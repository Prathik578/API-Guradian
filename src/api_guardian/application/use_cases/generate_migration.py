"""Use case for generating a migration using the LLM gateway."""

import uuid

from api_guardian.application.interfaces import MaintenanceCaseRepository, MigrationRepository
from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.domain.migration import MigrationAttempt, MigrationCampaign, PatchArtifact
from api_guardian.reasoning.patch_generator import PatchGenerator


class GenerateMigrationUseCase:
    """Constructs LLM context & produces candidate PatchArtifact."""

    def __init__(
        self,
        case_repo: MaintenanceCaseRepository,
        migration_repo: MigrationRepository,
        patch_generator: PatchGenerator,
    ) -> None:
        self.case_repo = case_repo
        self.migration_repo = migration_repo
        self.patch_generator = patch_generator

    def execute(self, ctx: TenantContext, case_id: uuid.UUID) -> MigrationCampaign:
        """Generates a patch artifact using the LLM patch generator."""

        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError("Case not found")

        case.transition_to(MaintenanceCaseState.MIGRATING)
        self.case_repo.save(ctx, case)

        # 1. Create Campaign
        campaign = MigrationCampaign(
            id=uuid.uuid4(),
            case_id=case.id,
        )

        artifact = self.patch_generator.generate_patch(
            repository_id=case.repository_id,
            commit_sha=case.base_revision_sha,
            provider_name="Stripe",
            change_description="Deprecating `card` param in Charges API.",
            affected_files=["src/payments.py"],
            graph=None,  # type: ignore
            source_files={"src/payments.py": "stripe.Charge.create(card='tok_123')"},
        )

        print(f"Generated patch artifact: {artifact.id} with {len(artifact.diff_blocks)} blocks.")

        # 2. Create Artifact and Attempt Domain objects
        affected_files = list({block.file_path for block in artifact.diff_blocks})
        patch_data = ""
        for block in artifact.diff_blocks:
            patch_data += f"--- {block.file_path}\n+++ {block.file_path}\n{block.original_snippet}\n{block.modified_snippet}\n"

        patch_artifact = PatchArtifact(
            id=artifact.id,
            repository_id=case.repository_id,
            base_commit_sha=case.base_revision_sha,
            archive_content_hash="mock-hash",
            affected_files=affected_files,
            patch_data=patch_data,
        )

        attempt = MigrationAttempt(
            id=uuid.uuid4(),
            campaign_id=campaign.id,
            model_name="mock-model",
            prompt_tokens=100,
            completion_tokens=50,
            patch_artifact_id=patch_artifact.id,
        )

        # 3. Save domain objects
        self.migration_repo.save_campaign(ctx, campaign)
        self.migration_repo.save_patch(ctx, patch_artifact)
        self.migration_repo.save_attempt(ctx, attempt)

        return campaign
