"""Maintenance Cases routes."""

import uuid
from typing import Any, cast

from fastapi import APIRouter, Depends, HTTPException, Request

from api_guardian.domain import TenantContext
from api_guardian.workers.tasks.analysis import analyze_repository_task  # noqa: F401
from api_guardian.workers.tasks.migration import generate_migration_task
from api_guardian.workers.tasks.verification import execute_verification_task

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
    
    from api_guardian.workers.tasks.analysis import assess_impact_task
    assess_impact_task.delay(str(ctx.tenant_id), str(case_id), str(snapshot_id))
    
    return {"status": "queued"}


@router.post("/{case_id}/generate_migration")
async def trigger_migration(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> dict[str, str]:
    """Asynchronously triggers migration generation."""
    generate_migration_task.delay(str(ctx.tenant_id), str(case_id))
    return {"status": "queued"}


@router.post("/{case_id}/verify")
async def trigger_verification(
    case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)
) -> dict[str, str]:
    """Asynchronously triggers sandbox verification."""
    execute_verification_task.delay(str(ctx.tenant_id), str(case_id))
    return {"status": "queued"}
