"""Provider Changes routes."""
import uuid

from fastapi import APIRouter, HTTPException, Query
from sqlalchemy import func, select

from api_guardian.api.schemas import (
    PaginatedResponse,
    ProviderChangeDetailResponse,
    ProviderChangeResponse,
)
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import ProviderChangeModel

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[ProviderChangeResponse])
async def list_provider_changes(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
) -> PaginatedResponse[ProviderChangeResponse]:
    """List all detected provider changes."""
    # Note: ProviderChangeModel is not tenant-scoped in MVP
    with db_manager.SessionLocal() as session:
        total = session.execute(select(func.count()).select_from(ProviderChangeModel)).scalar() or 0
        
        stmt = select(ProviderChangeModel).order_by(ProviderChangeModel.created_at.desc()).offset((page - 1) * size).limit(size)
        changes = session.execute(stmt).scalars().all()
        
        items = [
            ProviderChangeResponse(
                id=c.id,
                provider=c.provider,
                classification=c.classification,
                summary=c.summary,
                effective_date=c.effective_date,
                sunset_date=c.sunset_date,
                created_at=str(c.created_at) if c.created_at else None
            )
            for c in changes
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)

@router.get("/{change_id}", response_model=ProviderChangeDetailResponse)
async def get_provider_change(change_id: uuid.UUID) -> ProviderChangeDetailResponse:
    """Get provider change details."""
    with db_manager.SessionLocal() as session:
        change = session.get(ProviderChangeModel, change_id)
        if not change:
            raise HTTPException(status_code=404, detail="Provider change not found")
        return ProviderChangeDetailResponse(
            id=change.id,
            provider=change.provider,
            classification=change.classification,
            summary=change.summary,
            affected_entities=change.affected_entities,
            effective_date=change.effective_date,
            sunset_date=change.sunset_date,
            revision=change.revision,
            created_at=str(change.created_at) if change.created_at else None
        )
