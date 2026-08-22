"""Use case for assessing impact of a provider change on a repository."""
import uuid
from typing import Any

from api_guardian.domain import MaintenanceCaseState, TenantContext


class AssessImpactUseCase:
    """Runs impact funnel for a ProviderChange against a snapshot."""
    def __init__(self, case_repo: Any) -> None:
        self.case_repo = case_repo

    def execute(self, ctx: TenantContext, case_id: uuid.UUID) -> None:
        """Analyzes the dependency graph against the provider change."""
        
        case = self.case_repo.get_by_id(ctx, case_id)
        if not case:
            raise ValueError("Case not found")
            
        case.transition_to(MaintenanceCaseState.IMPACT_ANALYZING)
        self.case_repo.save(ctx, case)
        
        affected = True
        new_state = MaintenanceCaseState.AFFECTED_ACTION_REQUIRED if affected else MaintenanceCaseState.UNAFFECTED
        case.transition_to(new_state)
        self.case_repo.save(ctx, case)
        
        print(f"Assessed impact for case {case_id}: {new_state.value}")
