"""Use case for orchestrating MaintenanceCase transitions."""

import uuid

from api_guardian.application.interfaces import MaintenanceCaseRepository
from api_guardian.domain import MaintenanceCaseState, TenantContext


class OrchestrateCaseUseCase:
    """Central orchestrator for the autonomous migration loop."""

    def __init__(self, case_repo: MaintenanceCaseRepository) -> None:
        self.case_repo = case_repo

    def execute(self, ctx: TenantContext, case_id: uuid.UUID) -> MaintenanceCaseState:
        """Evaluates current case state and dispatches next action."""
        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError(f"Case {case_id} not found")

        # In a real system, this would queue Celery tasks securely using outbox pattern.
        # For MVP, we just return the state so the Celery task can trigger the next step.
        return case.state
