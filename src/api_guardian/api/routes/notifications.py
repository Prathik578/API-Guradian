"""Notifications routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlalchemy import desc, select

from api_guardian.api.dependencies import require_member
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import NotificationModel

router = APIRouter()

class NotificationResponse(BaseModel):
    id: uuid.UUID
    title: str
    message: str
    event_type: str
    resource_url: str | None
    is_read: bool
    created_at: str

@router.get("/", response_model=list[NotificationResponse])
def get_notifications(ctx: TenantContext = Depends(require_member)) -> list[NotificationResponse]:
    with db_manager.get_tenant_session(ctx) as session:
        # Also filter by user_id if present, but for now organization level or both
        query = select(NotificationModel).where(
            NotificationModel.organization_id == ctx.tenant_id
        ).order_by(desc(NotificationModel.created_at))
        
        notifs = session.execute(query).scalars().all()
        
        return [
            NotificationResponse(
                id=n.id,
                title=n.title,
                message=n.message,
                event_type=n.event_type,
                resource_url=n.resource_url,
                is_read=n.is_read,
                created_at=str(n.created_at) if n.created_at else ""
            ) for n in notifs
        ]

@router.post("/{notification_id}/read")
def mark_read(notification_id: uuid.UUID, ctx: TenantContext = Depends(require_member)) -> dict[str, str]:
    with db_manager.get_tenant_session(ctx) as session:
        notif = session.execute(
            select(NotificationModel).where(
                NotificationModel.id == notification_id,
                NotificationModel.organization_id == ctx.tenant_id
            )
        ).scalars().first()
        if not notif:
            raise HTTPException(status_code=404, detail="Notification not found")
        
        notif.is_read = True
        session.commit()
        return {"status": "success"}

@router.post("/read-all")
def mark_all_read(ctx: TenantContext = Depends(require_member)) -> dict[str, str]:
    with db_manager.get_tenant_session(ctx) as session:
        notifs = session.execute(
            select(NotificationModel).where(
                NotificationModel.organization_id == ctx.tenant_id,
                NotificationModel.is_read == False
            )
        ).scalars().all()
        
        for n in notifs:
            n.is_read = True
        session.commit()
        return {"status": "success"}
