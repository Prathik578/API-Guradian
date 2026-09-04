"""Pull Requests routes."""
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select

from api_guardian.api.schemas import PaginatedResponse, PullRequestResponse
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import PullRequestModel

router = APIRouter()

def get_tenant_context(request: Request) -> TenantContext:
    if not hasattr(request.state, "tenant") or not request.state.tenant:
        raise HTTPException(status_code=401, detail="Tenant context required")
    return cast(TenantContext, request.state.tenant)

@router.get("/", response_model=PaginatedResponse[PullRequestResponse])
async def list_pull_requests(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    ctx: TenantContext = Depends(get_tenant_context)
) -> PaginatedResponse[PullRequestResponse]:
    with db_manager.get_tenant_session(ctx) as session:
        total = session.execute(select(func.count()).select_from(PullRequestModel)).scalar() or 0
        stmt = select(PullRequestModel).order_by(PullRequestModel.created_at.desc()).offset((page - 1) * size).limit(size)
        prs = session.execute(stmt).scalars().all()
        
        items = [
            PullRequestResponse(
                id=pr.id,
                case_id=pr.case_id,
                repository_id=pr.repository_id,
                patch_artifact_id=pr.patch_artifact_id,
                github_pr_number=pr.github_pr_number,
                github_pr_url=pr.github_pr_url,
                state=pr.state,
                created_at=str(pr.created_at) if pr.created_at else None
            )
            for pr in prs
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)
