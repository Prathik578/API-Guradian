"""Middleware for tenant isolation."""

import uuid

from fastapi import Request
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from starlette.responses import Response

from api_guardian.domain import TenantContext


class TenantIdentificationMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next: RequestResponseEndpoint) -> Response:
        # Simplistic implementation for MVP.
        # In reality, this would decode a JWT or verify a GitHub App installation ID.
        tenant_header = request.headers.get("X-Tenant-ID")
        auth_header = request.headers.get("Authorization")
        
        user_id = None
        role = None

        if auth_header and auth_header.startswith("Bearer "):
            token = auth_header.split(" ")[1]
            try:
                import jwt
                payload = jwt.decode(token, "dev_secret_key", algorithms=["HS256"])
                user_id = uuid.UUID(payload.get("sub"))
            except Exception:
                pass

        if tenant_header:
            try:
                tenant_id = uuid.UUID(tenant_header)
                if user_id:
                    from sqlalchemy import select

                    from api_guardian.persistence.database import db_manager
                    from api_guardian.persistence.models.tables import OrganizationMemberModel
                    
                    with db_manager.SessionLocal() as session:
                        member = session.execute(
                            select(OrganizationMemberModel).where(
                                OrganizationMemberModel.organization_id == tenant_id,
                                OrganizationMemberModel.user_id == user_id
                            )
                        ).scalars().first()
                        if member:
                            role = member.role

                request.state.tenant = TenantContext(tenant_id=tenant_id, user_id=user_id, role=role)
            except ValueError:
                request.state.tenant = None
        else:
            request.state.tenant = None

        response = await call_next(request)
        return response
