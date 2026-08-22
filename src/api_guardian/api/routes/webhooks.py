"""GitHub Webhook routes."""
from fastapi import APIRouter, Request, HTTPException
import hmac
import hashlib

router = APIRouter()

@router.post("/github")
async def github_webhook(request: Request):
    """Receives and queues GitHub webhooks."""
    # TODO: Implement HMAC signature validation and dispatch to workers
    payload = await request.json()
    return {"status": "received"}
