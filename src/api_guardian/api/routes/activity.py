"""Activity logs routes."""
from typing import cast
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select, func

from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import ActivityLogModel
from api_guardian.api.schemas import ActivityEventResponse, PaginatedResponse

router = APIRouter()

def get_tenant_context(request: Request) -> TenantContext:
    if not hasattr(request.state, "tenant") or not request.state.tenant:
        raise HTTPException(status_code=401, detail="Tenant context required")
    return cast(TenantContext, request.state.tenant)

@router.get("/", response_model=PaginatedResponse[ActivityEventResponse])
async def list_activity_logs(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    ctx: TenantContext = Depends(get_tenant_context)
) -> PaginatedResponse[ActivityEventResponse]:
    with db_manager.get_tenant_session(ctx) as session:
        total = session.execute(select(func.count()).select_from(ActivityLogModel)).scalar() or 0
        stmt = select(ActivityLogModel).order_by(ActivityLogModel.created_at.desc()).offset((page - 1) * size).limit(size)
        logs = session.execute(stmt).scalars().all()
        
        items = [
            ActivityEventResponse(
                id=log.id,
                actor=log.actor,
                event_type=log.event_type,
                entity=log.entity,
                entity_id=log.entity_id,
                result=log.result,
                metadata_payload=log.metadata_payload,
                created_at=str(log.created_at) if log.created_at else None
            )
            for log in logs
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)
