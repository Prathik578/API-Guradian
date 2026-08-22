"""Maintenance Cases routes."""
import uuid
from fastapi import APIRouter, Depends, HTTPException, Request

from api_guardian.domain import TenantContext

router = APIRouter()

def get_tenant_context(request: Request) -> TenantContext:
    if not hasattr(request.state, "tenant") or not request.state.tenant:
        raise HTTPException(status_code=401, detail="Tenant context required")
    return request.state.tenant

@router.get("/")
async def list_cases(ctx: TenantContext = Depends(get_tenant_context)):
    """List active cases for the tenant."""
    # TODO: Implement listing via use case
    return {"cases": []}

@router.get("/{case_id}")
async def get_case(case_id: uuid.UUID, ctx: TenantContext = Depends(get_tenant_context)):
    """Get a specific case."""
    # TODO: Implement retrieval via use case
    return {"id": str(case_id)}
