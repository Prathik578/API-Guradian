from fastapi import Depends, HTTPException, Request
from typing import cast
from api_guardian.domain import TenantContext

def get_tenant_context(request: Request) -> TenantContext:
    if not hasattr(request.state, "tenant") or not request.state.tenant:
        raise HTTPException(status_code=401, detail="Authentication required")
    return cast(TenantContext, request.state.tenant)

class RoleChecker:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, ctx: TenantContext = Depends(get_tenant_context)) -> TenantContext:
        if not ctx.role:
            raise HTTPException(status_code=403, detail="No role found for this organization")
        if ctx.role not in self.allowed_roles:
            raise HTTPException(status_code=403, detail="Insufficient permissions")
        return ctx

require_owner = RoleChecker(["OWNER"])
require_admin = RoleChecker(["OWNER", "ADMIN"])
require_member = RoleChecker(["OWNER", "ADMIN", "MEMBER"])
require_viewer = RoleChecker(["OWNER", "ADMIN", "MEMBER", "VIEWER"])
