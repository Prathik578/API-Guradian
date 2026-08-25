"""Maintenance Cases routes."""

import uuid
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request

from api_guardian.domain import TenantContext
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.outbox import OutboxManager
from api_guardian.workers.tasks.analysis import analyze_repository_task  # noqa: F401

router = APIRouter()


def get_tenant_context(request: Request) -> TenantContext:
    if not hasattr(request.state, "tenant") or not request.state.tenant:
        raise HTTPException(status_code=401, detail="Tenant context required")
    return cast(TenantContext, request.state.tenant)


@router.get("/")
async def list_cases(ctx: TenantContext = Depends(get_tenant_context)) -> dict[str, Any]:
    """List active cases for the tenant."""
    return {"cases": []}


@router.get("/{case_id}")
async def get_case(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> dict[str, Any]:
    """Get a specific case."""
    return {"id": str(case_id)}


@router.post("/{case_id}/assess_impact")
async def assess_impact(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> dict[str, str]:
    """Asynchronously triggers impact assessment."""
    # Assuming snapshot_id would come from the body, for MVP we'll just mock it if not present
    snapshot_id = uuid.uuid4()
    
    with db_manager.get_tenant_session(ctx) as session:
        OutboxManager.schedule_task(
            session,
            "api_guardian.workers.tasks.analysis.assess_impact_task",
            {"tenant_id": str(ctx.tenant_id), "case_id": str(case_id), "snapshot_id": str(snapshot_id)}
        )
    
    return {"status": "queued"}


@router.post("/{case_id}/generate_migration")
async def trigger_migration(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> dict[str, str]:
    """Asynchronously triggers migration generation."""
    with db_manager.get_tenant_session(ctx) as session:
        OutboxManager.schedule_task(
            session,
            "api_guardian.workers.tasks.migration.generate_migration_task",
            {"tenant_id": str(ctx.tenant_id), "case_id": str(case_id)}
        )
    return {"status": "queued"}


@router.post("/{case_id}/verify")
async def trigger_verification(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> dict[str, str]:
    """Asynchronously triggers sandbox verification."""
    with db_manager.get_tenant_session(ctx) as session:
        OutboxManager.schedule_task(
            session,
            "api_guardian.workers.tasks.verification.execute_verification_task",
            {"tenant_id": str(ctx.tenant_id), "case_id": str(case_id)}
        )
    return {"status": "queued"}
