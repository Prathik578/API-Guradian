"""GitHub Webhook routes."""

from fastapi import APIRouter, Request

from api_guardian.application.use_cases.sync_provider import SyncProviderUseCase

router = APIRouter()

@router.post("/github")
async def github_webhook(request: Request) -> dict[str, str]:
    """Receives and queues GitHub webhooks."""
    payload = await request.json()  # noqa: F841
    
    use_case = SyncProviderUseCase(provider_repo=None, case_repo=None)  # noqa: F841
    # We would execute the usecase here with actual tenant context
    # use_case.execute(ctx, payload.get("provider", "GitHub"))
    
    return {"status": "received"}
