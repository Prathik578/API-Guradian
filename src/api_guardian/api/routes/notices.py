"""Provider Notices routes."""
from typing import cast
from fastapi import APIRouter, Depends, HTTPException, Request, Query
from sqlalchemy import select, func
import uuid

from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import ProviderNoticeModel
from api_guardian.api.schemas import ProviderNoticeResponse, PaginatedResponse

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[ProviderNoticeResponse])
async def list_notices(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100)
) -> PaginatedResponse[ProviderNoticeResponse]:
    # Notices are global, like ProviderChange
    with db_manager.SessionLocal() as session:
        total = session.execute(select(func.count()).select_from(ProviderNoticeModel)).scalar() or 0
        stmt = select(ProviderNoticeModel).order_by(ProviderNoticeModel.created_at.desc()).offset((page - 1) * size).limit(size)
        notices = session.execute(stmt).scalars().all()
        
        items = [
            ProviderNoticeResponse(
                id=n.id,
                provider=n.provider,
                title=n.title,
                description=n.description,
                published_at=str(n.published_at) if n.published_at else None,
                effective_at=str(n.effective_at) if n.effective_at else None,
                severity=n.severity,
                affected_api=n.affected_api,
                notice_type=n.notice_type,
                status=n.status,
                created_at=str(n.created_at) if n.created_at else None
            )
            for n in notices
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)

@router.get("/{notice_id}", response_model=ProviderNoticeResponse)
async def get_notice(notice_id: uuid.UUID) -> ProviderNoticeResponse:
    with db_manager.SessionLocal() as session:
        n = session.get(ProviderNoticeModel, notice_id)
        if not n:
            raise HTTPException(status_code=404, detail="Notice not found")
        return ProviderNoticeResponse(
            id=n.id,
            provider=n.provider,
            title=n.title,
            description=n.description,
            published_at=str(n.published_at) if n.published_at else None,
            effective_at=str(n.effective_at) if n.effective_at else None,
            severity=n.severity,
            affected_api=n.affected_api,
            notice_type=n.notice_type,
            status=n.status,
            created_at=str(n.created_at) if n.created_at else None
        )
