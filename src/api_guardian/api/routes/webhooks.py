"""GitHub Webhook routes."""

import uuid

from fastapi import APIRouter, Request

router = APIRouter()


@router.post("/github")
async def github_webhook(request: Request) -> dict[str, str]:
    """Receives and queues GitHub webhooks."""
    payload = await request.json()

    from api_guardian.workers.tasks.provider import sync_provider_task
    
    tenant_id_str = str(uuid.uuid4()) # In real app, derived from auth/webhook secret
    sync_provider_task.delay(tenant_id_str, payload)

    return {"status": "received"}
