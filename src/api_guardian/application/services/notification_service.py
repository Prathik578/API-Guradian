import uuid
from typing import Optional
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import NotificationModel
from api_guardian.domain import TenantContext

class NotificationService:
    @staticmethod
    def create_notification(
        ctx: TenantContext,
        title: str,
        message: str,
        event_type: str,
        resource_url: Optional[str] = None
    ) -> None:
        with db_manager.get_tenant_session(ctx) as session:
            notif = NotificationModel(
                organization_id=ctx.tenant_id,
                title=title,
                message=message,
                event_type=event_type,
                resource_url=resource_url
            )
            session.add(notif)
            session.commit()
