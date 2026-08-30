"""Repositories routes."""
import uuid
from typing import cast

from fastapi import APIRouter, Depends, HTTPException, Query, Request
from sqlalchemy import func, select

from api_guardian.api.schemas import PaginatedResponse, RepositoryResponse, CreateRepositoryRequest
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import RepositoryModel

from api_guardian.api.dependencies import require_viewer, require_member

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[RepositoryResponse])
async def list_repositories(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    ctx: TenantContext = Depends(require_viewer)
) -> PaginatedResponse[RepositoryResponse]:
    """List all repositories for the tenant."""
    with db_manager.get_tenant_session(ctx) as session:
        total = session.execute(select(func.count()).select_from(RepositoryModel)).scalar() or 0
        
        stmt = select(RepositoryModel).order_by(RepositoryModel.created_at.desc()).offset((page - 1) * size).limit(size)
        repos = session.execute(stmt).scalars().all()
        
        items = [
            RepositoryResponse(
                id=repo.id,
                name=repo.name,
                github_full_name=repo.github_full_name,
                default_branch=repo.default_branch,
                created_at=str(repo.created_at) if repo.created_at else None
            )
            for repo in repos
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)

@router.post("/", response_model=RepositoryResponse)
async def create_repository(
    request_data: CreateRepositoryRequest,
    ctx: TenantContext = Depends(require_member)
) -> RepositoryResponse:
    """Create a new repository for the tenant."""
    from api_guardian.persistence.models.tables import OrganizationPlanModel
    with db_manager.get_tenant_session(ctx) as session:
        # Check quota
        repos_count = session.execute(select(func.count()).select_from(RepositoryModel)).scalar() or 0
        plan = session.execute(
            select(OrganizationPlanModel).where(OrganizationPlanModel.organization_id == ctx.tenant_id)
        ).scalars().first()
        tier = plan.plan_tier if plan else "FREE"
        if tier == "FREE":
            limit = 1
        elif tier == "PRO":
            limit = 10
        else:
            limit = 1000
        
        if repos_count >= limit:
            raise HTTPException(status_code=402, detail="Repository quota exceeded for your current plan.")
            
        repo = RepositoryModel(
            id=uuid.uuid4(),
            name=request_data.name,
            github_full_name=request_data.github_full_name,
            default_branch=request_data.default_branch,
        )
        session.add(repo)
        session.commit()
        session.refresh(repo)
        
        return RepositoryResponse(
            id=repo.id,
            name=repo.name,
            github_full_name=repo.github_full_name,
            default_branch=repo.default_branch,
            created_at=str(repo.created_at) if repo.created_at else None
        )

@router.get("/{repo_id}", response_model=RepositoryResponse)
async def get_repository(
    repo_id: uuid.UUID, ctx: TenantContext = Depends(require_viewer)
) -> RepositoryResponse:
    """Get repository details."""
    with db_manager.get_tenant_session(ctx) as session:
        repo = session.get(RepositoryModel, repo_id)
        if not repo:
            raise HTTPException(status_code=404, detail="Repository not found")
        return RepositoryResponse(
            id=repo.id,
            name=repo.name,
            github_full_name=repo.github_full_name,
            default_branch=repo.default_branch,
            created_at=str(repo.created_at) if repo.created_at else None
        )
