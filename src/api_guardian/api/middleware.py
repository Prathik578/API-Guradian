"""Middleware for tenant isolation."""
import uuid
from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from api_guardian.domain import TenantContext


class TenantIdentificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # Simplistic implementation for MVP.
        # In reality, this would decode a JWT or verify a GitHub App installation ID.
        tenant_header = request.headers.get("X-Tenant-ID")
        
        if tenant_header:
            try:
                tenant_id = uuid.UUID(tenant_header)
                request.state.tenant = TenantContext(tenant_id=tenant_id)
            except ValueError:
                request.state.tenant = None
        else:
            request.state.tenant = None
            
        response = await call_next(request)
        return response
