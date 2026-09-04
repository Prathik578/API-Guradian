"""Integrations routes."""
import uuid

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select

from api_guardian.api.dependencies import require_member, require_viewer
from api_guardian.api.schemas import (
    ActionResponse,
    CreateIntegrationRequest,
    IntegrationResponse,
    PaginatedResponse,
)
from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import IntegrationModel

router = APIRouter()

@router.get("/", response_model=PaginatedResponse[IntegrationResponse])
async def list_integrations(
    page: int = Query(1, ge=1),
    size: int = Query(20, ge=1, le=100),
    ctx: TenantContext = Depends(require_viewer)
) -> PaginatedResponse[IntegrationResponse]:
    with db_manager.get_tenant_session(ctx) as session:
        total = session.execute(select(func.count()).select_from(IntegrationModel)).scalar() or 0
        stmt = select(IntegrationModel).order_by(IntegrationModel.created_at.desc()).offset((page - 1) * size).limit(size)
        integrations = session.execute(stmt).scalars().all()
        
        items = [
            IntegrationResponse(
                id=i.id,
                provider=i.provider,
                status=i.status,
                last_synced_at=str(i.last_synced_at) if i.last_synced_at else None,
                created_at=str(i.created_at) if i.created_at else None
            )
            for i in integrations
        ]
        return PaginatedResponse(items=items, total=total, page=page, size=size)

@router.post("/", response_model=IntegrationResponse)
async def create_integration(
    request_data: CreateIntegrationRequest,
    ctx: TenantContext = Depends(require_member)
) -> IntegrationResponse:
    """Create a new integration for the tenant."""
    with db_manager.get_tenant_session(ctx) as session:
        integration = IntegrationModel(
            id=uuid.uuid4(),
            provider=request_data.provider,
            configuration=request_data.configuration,
            status="CONNECTED"
        )
        session.add(integration)
        session.commit()
        session.refresh(integration)
        
        return IntegrationResponse(
            id=integration.id,
            provider=integration.provider,
            status=integration.status,
            last_synced_at=str(integration.last_synced_at) if integration.last_synced_at else None,
            created_at=str(integration.created_at) if integration.created_at else None
        )

@router.post("/{integration_id}/sync", response_model=ActionResponse)
async def sync_integration(
    integration_id: uuid.UUID,
    ctx: TenantContext = Depends(require_member)
) -> ActionResponse:
    """Trigger a sync for the integration."""
    with db_manager.get_tenant_session(ctx) as session:
        integration = session.get(IntegrationModel, integration_id)
        if not integration:
            raise HTTPException(status_code=404, detail="Integration not found")
            
        from api_guardian.persistence.outbox import OutboxManager
        # Assuming provider name maps to task name loosely
        if integration.provider.lower() == "stripe":
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.provider.sync_stripe_task",
                {"tenant_id": str(ctx.tenant_id)}
            )
        else:
            OutboxManager.schedule_task(
                session,
                "api_guardian.workers.tasks.provider.sync_provider_task",
                {"tenant_id": str(ctx.tenant_id), "provider": integration.provider}
            )
        return ActionResponse(status="sync_queued")

import os

from pydantic import BaseModel


class OAuthLoginResponse(BaseModel):
    url: str

@router.get("/github/oauth/login", response_model=OAuthLoginResponse)
async def github_oauth_login(ctx: TenantContext = Depends(require_member)) -> OAuthLoginResponse:
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    if not client_id:
        raise HTTPException(status_code=501, detail="GitHub OAuth is not configured. External configuration required.")
    
    # State parameter should ideally contain a secure nonce and tenant context
    state = str(ctx.tenant_id)
    redirect_uri = f"https://github.com/login/oauth/authorize?client_id={client_id}&scope=repo&state={state}"
    return OAuthLoginResponse(url=redirect_uri)

@router.get("/github/oauth/callback", response_model=IntegrationResponse)
async def github_oauth_callback(code: str, state: str, ctx: TenantContext = Depends(require_member)) -> IntegrationResponse:
    client_id = os.environ.get("GITHUB_CLIENT_ID")
    client_secret = os.environ.get("GITHUB_CLIENT_SECRET")
    
    if not client_id or not client_secret:
        raise HTTPException(status_code=501, detail="GitHub OAuth is not configured. External configuration required.")
        
    # Real implementation exchanges code for token using httpx
    import httpx
    async with httpx.AsyncClient() as client:
        token_res = await client.post(
            "https://github.com/login/oauth/access_token",
            headers={"Accept": "application/json"},
            data={
                "client_id": client_id,
                "client_secret": client_secret,
                "code": code
            }
        )
        token_res.raise_for_status()
        token_data = token_res.json()
        
    access_token = token_data.get("access_token")
    if not access_token:
        raise HTTPException(status_code=400, detail="Failed to retrieve access token from GitHub")
        
    # Store token securely
    with db_manager.get_tenant_session(ctx) as session:
        integration = IntegrationModel(
            id=uuid.uuid4(),
            provider="github",
            configuration={"access_token": access_token},  # Should be encrypted in prod
            status="CONNECTED"
        )
        session.add(integration)
        session.commit()
        session.refresh(integration)
        
        return IntegrationResponse(
            id=integration.id,
            provider=integration.provider,
            status=integration.status,
            last_synced_at=str(integration.last_synced_at) if integration.last_synced_at else None,
            created_at=str(integration.created_at) if integration.created_at else None
        )

from typing import Any


@router.get("/{integration_id}/github/repositories")
async def github_discover_repositories(integration_id: uuid.UUID, ctx: TenantContext = Depends(require_member)) -> list[dict[str, Any]]:
    with db_manager.get_tenant_session(ctx) as session:
        integration = session.get(IntegrationModel, integration_id)
        if not integration or integration.provider != "github":
            raise HTTPException(status_code=404, detail="Integration not found or not a GitHub integration")
            
        access_token = integration.configuration.get("access_token") if integration.configuration else None
        if not access_token:
            raise HTTPException(status_code=400, detail="Integration is missing access token")
            
    import httpx
    async with httpx.AsyncClient() as client:
        res = await client.get(
            "https://api.github.com/user/repos",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/vnd.github.v3+json",
                "X-GitHub-Api-Version": "2022-11-28",
            },
            params={"visibility": "all", "per_page": 100}
        )
        if res.status_code == 401:
            raise HTTPException(status_code=401, detail="GitHub access token is invalid or expired")
        res.raise_for_status()
        repos = res.json()
        
    return [{"id": r["id"], "name": r["name"], "full_name": r["full_name"], "default_branch": r["default_branch"]} for r in repos]
