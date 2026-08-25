"""GitHub Webhook routes."""

import uuid

import hashlib
import json
from sqlalchemy.exc import IntegrityError
from fastapi import APIRouter, Request, Header, HTTPException
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.outbox import OutboxManager
from api_guardian.persistence.models.tables import WebhookDeliveryModel

router = APIRouter()


@router.post("/github")
async def github_webhook(
    request: Request,
    x_github_delivery: str = Header(None),
    x_github_event: str = Header(None)
) -> dict[str, str]:
    """Receives and queues GitHub webhooks."""
    if not x_github_delivery or not x_github_event:
        raise HTTPException(status_code=400, detail="Missing GitHub Headers")

    payload_bytes = await request.body()
    payload = json.loads(payload_bytes)
    payload_hash = hashlib.sha256(payload_bytes).hexdigest()

    tenant_id_str = str(uuid.uuid4()) # In real app, derived from auth/webhook secret

    with db_manager.get_session() as session:
        # Check deduplication
        delivery = WebhookDeliveryModel(
            delivery_id=x_github_delivery,
            event_type=x_github_event,
            payload_hash=payload_hash
        )
        session.add(delivery)
        try:
            session.flush()
        except IntegrityError:
            session.rollback()
            return {"status": "already_processed"}

        if x_github_event == "push":
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.repository.handle_push_task",
                {"tenant_id_str": tenant_id_str, "payload": payload}
            )
        else:
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.provider.sync_provider_task",
                {"tenant_id_str": tenant_id_str, "payload": payload}
            )

    return {"status": "received"}
