"""Usage and Quotas routes."""
from typing import cast
from fastapi import APIRouter, Depends
from sqlalchemy import select, func

from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import (
    RepositoryModel, GuardedAPIModel, ProviderChangeModel, 
    MigrationAttemptModel, VerificationRunModel, OrganizationPlanModel
)
from api_guardian.api.dependencies import require_member
from pydantic import BaseModel

router = APIRouter()

class UsageResponse(BaseModel):
    repositories_monitored: int
    guarded_apis: int
    api_changes_detected: int
    maintenance_cases: int
    migration_attempts: int
    verification_runs: int
    repositories_limit: int
    guarded_apis_limit: int

@router.get("/", response_model=UsageResponse)
def get_usage(ctx: TenantContext = Depends(require_member)) -> UsageResponse:
    from api_guardian.persistence.models.tables import MaintenanceCaseModel
    with db_manager.get_tenant_session(ctx) as session:
        repos_count = session.execute(select(func.count()).select_from(RepositoryModel)).scalar() or 0
        apis_count = session.execute(select(func.count()).select_from(GuardedAPIModel)).scalar() or 0
        # For provider changes, they are global, we just show total detected
        changes_count = session.execute(select(func.count()).select_from(ProviderChangeModel)).scalar() or 0
        cases_count = session.execute(select(func.count()).select_from(MaintenanceCaseModel)).scalar() or 0
        migrations_count = session.execute(select(func.count()).select_from(MigrationAttemptModel)).scalar() or 0
        verifications_count = session.execute(select(func.count()).select_from(VerificationRunModel)).scalar() or 0
        
        plan = session.execute(
            select(OrganizationPlanModel).where(OrganizationPlanModel.organization_id == ctx.tenant_id)
        ).scalars().first()
        
        # Define limits based on plan
        tier = plan.plan_tier if plan else "FREE"
        if tier == "FREE":
            repo_limit = 1
            api_limit = 5
        elif tier == "PRO":
            repo_limit = 10
            api_limit = 50
        else: # ENTERPRISE
            repo_limit = 1000
            api_limit = 5000
            
        return UsageResponse(
            repositories_monitored=repos_count,
            guarded_apis=apis_count,
            api_changes_detected=changes_count,
            maintenance_cases=cases_count,
            migration_attempts=migrations_count,
            verification_runs=verifications_count,
            repositories_limit=repo_limit,
            guarded_apis_limit=api_limit
        )
