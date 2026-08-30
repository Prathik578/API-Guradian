"""Guarded APIs routes."""
from typing import cast
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select, func

from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import GuardedAPIModel
from api_guardian.api.schemas import GuardedAPIResponse, PaginatedResponse, CreateGuardedAPIRequest
import uuid

from api_guardian.api.dependencies import require_viewer, require_member

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[GuardedAPIResponse])
async def list_guarded_apis(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    ctx: TenantContext = Depends(require_viewer)
) -> PaginatedResponse[GuardedAPIResponse]:
    with db_manager.get_tenant_session(ctx) as session:
        total = session.execute(select(func.count()).select_from(GuardedAPIModel)).scalar() or 0
        stmt = select(GuardedAPIModel).order_by(GuardedAPIModel.created_at.desc()).offset((page - 1) * size).limit(size)
        apis = session.execute(stmt).scalars().all()
        
        items = [
            GuardedAPIResponse(
                id=a.id,
                integration_id=a.integration_id,
                name=a.name,
                version=a.version,
                status=a.status,
                risk_level=a.risk_level,
                created_at=str(a.created_at) if a.created_at else None
            )
            for a in apis
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)

@router.post("/", response_model=GuardedAPIResponse)
async def create_guarded_api(
    request_data: CreateGuardedAPIRequest,
    ctx: TenantContext = Depends(require_member)
) -> GuardedAPIResponse:
    """Create a new guarded API for the tenant."""
    from api_guardian.persistence.models.tables import OrganizationPlanModel
    with db_manager.get_tenant_session(ctx) as session:
        # Check quota
        apis_count = session.execute(select(func.count()).select_from(GuardedAPIModel)).scalar() or 0
        plan = session.execute(
            select(OrganizationPlanModel).where(OrganizationPlanModel.organization_id == ctx.tenant_id)
        ).scalars().first()
        tier = plan.plan_tier if plan else "FREE"
        if tier == "FREE":
            limit = 5
        elif tier == "PRO":
            limit = 50
        else:
            limit = 5000
            
        if apis_count >= limit:
            raise HTTPException(status_code=402, detail="Guarded API quota exceeded for your current plan.")
            
        api = GuardedAPIModel(
            id=uuid.uuid4(),
            integration_id=request_data.integration_id,
            name=request_data.name,
            version=request_data.version,
            risk_level=request_data.risk_level,
            status="ACTIVE"
        )
        session.add(api)
        session.commit()
        session.refresh(api)
        
        return GuardedAPIResponse(
            id=api.id,
            integration_id=api.integration_id,
            name=api.name,
            version=api.version,
            status=api.status,
            risk_level=api.risk_level,
            created_at=str(api.created_at) if api.created_at else None
        )
