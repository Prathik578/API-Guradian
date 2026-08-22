"""Use case for generating a migration using the LLM gateway."""
import uuid
from typing import Any


class GenerateMigrationUseCase:
    """Constructs LLM context & produces candidate PatchArtifact."""
    def __init__(self, migration_repo: Any, llm_gateway: Any) -> None:
        self.migration_repo = migration_repo
        self.llm_gateway = llm_gateway

    def execute(self, ctx: Any, campaign_id: uuid.UUID) -> None:
        # TODO: Implement migration generation logic
        pass
