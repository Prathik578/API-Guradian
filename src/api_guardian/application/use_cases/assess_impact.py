"""Use case for assessing impact of a provider change on a repository."""

import uuid
from typing import Any

from api_guardian.application.interfaces import (
    ImpactAssessmentRepository,
    MaintenanceCaseRepository,
    ProviderChangeRepository,
    SnapshotRepository,
)
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.domain.maintenance import EvidenceLevel, ImpactAssessment, ImpactClassification


class AssessImpactUseCase:
    """Runs impact funnel for a ProviderChange against a snapshot."""

    def __init__(
        self,
        case_repo: MaintenanceCaseRepository,
        change_repo: ProviderChangeRepository,
        snapshot_repo: SnapshotRepository,
        assessment_repo: ImpactAssessmentRepository,
    ) -> None:
        self.case_repo = case_repo
        self.change_repo = change_repo
        self.snapshot_repo = snapshot_repo
        self.assessment_repo = assessment_repo

    def execute(self, ctx: TenantContext, case_id: uuid.UUID, snapshot_id: uuid.UUID) -> None:
        """Analyzes the dependency graph against the provider change."""
        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError("Case not found")

        change = self.change_repo.get_by_id(case.provider_change_id)
        if not change:
            raise ValueError("Provider change not found")

        snapshot = self.snapshot_repo.get_by_id(ctx, snapshot_id)
        if not snapshot:
            raise ValueError("Snapshot not found")

        case.transition_to(MaintenanceCaseState.IMPACT_ANALYZING)
        self.case_repo.save(ctx, case)

        affected_files: list[str] = []
        evidence_payload: dict[str, Any] = {}
        
        # Intersect provider entities with call sites in the module graph
        if snapshot.dependency_graph and "modules" in snapshot.dependency_graph:
            modules = snapshot.dependency_graph["modules"]
            for path, mod_data in modules.items():
                file_affected = False
                for sym_data in mod_data.get("symbols", []):
                    for call_site in sym_data.get("call_sites", []):
                        target_name = call_site.get("target_name")
                        for entity in change.affected_entities:
                            # Direct match or alias match logic
                            if target_name and target_name.endswith(entity):
                                file_affected = True
                                evidence_payload.setdefault(path, []).append({
                                    "symbol": sym_data.get("name"),
                                    "call_site": target_name,
                                    "matched_entity": entity,
                                    "location": call_site.get("location")
                                })
                if file_affected:
                    affected_files.append(path)
        
        is_affected = len(affected_files) > 0
        
        assessment = ImpactAssessment(
            id=uuid.uuid4(),
            case_id=case.id,
            snapshot_id=snapshot.id,
            classification=ImpactClassification.CONFIRMED_AFFECTED if is_affected else ImpactClassification.NOT_AFFECTED,
            evidence_level=EvidenceLevel.DIRECT_MATCH if is_affected else EvidenceLevel.NONE,
            affected_files=affected_files,
            evidence_payload=evidence_payload
        )
        self.assessment_repo.save(ctx, assessment)

        if is_affected:
            new_state = MaintenanceCaseState.AFFECTED_ACTION_REQUIRED
        else:
            # If it was previously affected, and now it isn't, the user resolved it!
            # Since the state might be IMPACT_ANALYZING currently (we transitioned it earlier), 
            # we don't have the original state unless we check the case before transitioning.
            # But wait, case.transition_to(IMPACT_ANALYZING) was called above. 
            # So let's look at the baseline base_revision_sha. If it's a re-analysis, 
            # meaning it was STALE, PR_OPEN, etc. then we should mark it MANUALLY_RESOLVED.
            # For simplicity, if we are doing a re-analysis (we can tell if we look at whether there was a previous assessment, but we don't have that).
            # Actually, `case` has a history or we can just say if the `case.base_revision_sha` changed (which it would have, if it's a new push), then it's MANUALLY_RESOLVED.
            # But the use case doesn't know if this is the first analysis or a re-analysis.
            # Let's just use UNAFFECTED for now, or check if it was previously NOT UNAFFECTED.
            # To be completely safe and meet MVP requirements:
            # "If the triggering API usage no longer exists: MANUALLY_RESOLVED"
            # I will query the DB to see if a previous assessment existed with CONFIRMED_AFFECTED.
            previous_assessments = self.assessment_repo.get_by_case_id(ctx, case.id)
            # assessment_repo.get_by_case_id returns a single assessment right now.
            if previous_assessments and previous_assessments.classification == ImpactClassification.CONFIRMED_AFFECTED:
                new_state = MaintenanceCaseState.MANUALLY_RESOLVED
            else:
                new_state = MaintenanceCaseState.UNAFFECTED

        case.transition_to(new_state)
        self.case_repo.save(ctx, case)
