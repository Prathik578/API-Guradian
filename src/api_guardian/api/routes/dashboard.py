"""Dashboard analytics routes."""

from fastapi import APIRouter, Depends
from sqlalchemy import func, select

from api_guardian.api.dependencies import require_viewer
from api_guardian.api.schemas import DashboardOverviewResponse
from api_guardian.domain import (
    MaintenanceCaseState,
    MigrationState,
    TenantContext,
    VerificationState,
)
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import (
    MaintenanceCaseModel,
    MigrationCampaignModel,
    ProviderChangeModel,
    PullRequestModel,
    RepositoryModel,
    VerificationRunModel,
)

router = APIRouter()

@router.get("/overview", response_model=DashboardOverviewResponse)
async def get_dashboard_overview(ctx: TenantContext = Depends(require_viewer)) -> DashboardOverviewResponse:
    """Get high-level dashboard statistics."""
    with db_manager.get_tenant_session(ctx) as session:
        active_repos_count = session.execute(select(func.count()).select_from(RepositoryModel)).scalar() or 0
        active_cases_count = session.execute(
            select(func.count()).select_from(MaintenanceCaseModel).where(
                MaintenanceCaseModel.state != MaintenanceCaseState.RESOLVED
            )
        ).scalar() or 0
        
        migrations_in_progress = session.execute(
            select(func.count()).select_from(MigrationCampaignModel).where(
                MigrationCampaignModel.state.in_([MigrationState.PENDING, MigrationState.GENERATING])
            )
        ).scalar() or 0
        
        open_prs_count = session.execute(
            select(func.count()).select_from(PullRequestModel).where(
                PullRequestModel.state != "CLOSED"
            )
        ).scalar() or 0
        
        failed_verifications = session.execute(
            select(func.count()).select_from(VerificationRunModel).where(
                VerificationRunModel.state.in_([
                    VerificationState.BASELINE_FAILED,
                    VerificationState.PATCH_CONFLICT,
                    VerificationState.TESTS_FAILED,
                    VerificationState.VERIFICATION_INTEGRITY_FAILED,
                    VerificationState.INFRASTRUCTURE_FAILED,
                    VerificationState.TIMEOUT
                ])
            )
        ).scalar() or 0
        
        with db_manager.SessionLocal() as unscoped_session:
            pending_changes_count = unscoped_session.execute(select(func.count()).select_from(ProviderChangeModel)).scalar() or 0
            from api_guardian.persistence.models.tables import ProviderNoticeModel
            recent_notices_count = unscoped_session.execute(select(func.count()).select_from(ProviderNoticeModel)).scalar() or 0
        
        return DashboardOverviewResponse(
            active_repositories=active_repos_count,
            active_cases=active_cases_count,
            pending_api_changes=pending_changes_count,
            migrations_in_progress=migrations_in_progress,
            open_prs=open_prs_count,
            failed_verifications=failed_verifications,
            recent_notices=recent_notices_count
        )
