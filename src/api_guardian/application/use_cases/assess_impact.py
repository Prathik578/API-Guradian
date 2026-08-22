"""Use case for assessing impact of a provider change on a repository."""
import uuid
from typing import Any


class AssessImpactUseCase:
    """Runs impact funnel for a ProviderChange against a snapshot."""
    def __init__(self, case_repo: Any) -> None:
        self.case_repo = case_repo

    def execute(self, ctx: Any, case_id: uuid.UUID) -> None:
        # TODO: Implement impact assessment logic
        pass
