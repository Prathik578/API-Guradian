"""Use case for generating a migration using the LLM gateway."""
import uuid
from typing import Any

from api_guardian.domain import MaintenanceCaseState, TenantContext
from api_guardian.reasoning.patch_generator import PatchGenerator


class GenerateMigrationUseCase:
    """Constructs LLM context & produces candidate PatchArtifact."""
    def __init__(self, case_repo: Any, patch_generator: PatchGenerator) -> None:
        self.case_repo = case_repo
        self.patch_generator = patch_generator

    def execute(self, ctx: TenantContext, case_id: uuid.UUID) -> None:
        """Generates a patch artifact using the LLM patch generator."""
        
        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError("Case not found")
            
        case.transition_to(MaintenanceCaseState.MIGRATING)
        self.case_repo.save(ctx, case)
        
        artifact = self.patch_generator.generate_patch(
            repository_id=case.repository_id,
            commit_sha=case.base_revision_sha,
            provider_name="Stripe",
            change_description="Deprecating `card` param in Charges API.",
            affected_files=["src/payments.py"],
            graph=None, # type: ignore
            source_files={"src/payments.py": "stripe.Charge.create(card='tok_123')"}
        )
        
        print(f"Generated patch artifact: {artifact.id} with {len(artifact.diff_blocks)} blocks.")
