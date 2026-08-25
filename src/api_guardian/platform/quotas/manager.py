"""Distributed Quota Management."""

import uuid
from datetime import UTC, datetime, timedelta

from sqlalchemy import func, select

from api_guardian.domain.quotas import ResourcePolicy
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.models.tables import ResourceLeaseModel


class QuotaManager:
    """Manages distributed atomic quotas using PostgreSQL locking."""

    @classmethod
    def acquire_tenant_lease(cls, tenant_id: uuid.UUID, resource_type: str, worker_id: str, duration_sec: int = 1800) -> uuid.UUID:
        """Atomically acquires a lease if the quota is not exceeded."""
        policy = ResourcePolicy.get_default()
        
        limit = getattr(policy.tenant, f"max_{resource_type}", None)
        if limit is None:
            raise ValueError(f"Unknown tenant resource type {resource_type}")

        from api_guardian.domain import TenantContext
        ctx = TenantContext(tenant_id=tenant_id)

        with db_manager.get_tenant_session(ctx) as session:
            # Clean up expired leases first
            now = datetime.now(UTC)
            session.query(ResourceLeaseModel).filter(
                ResourceLeaseModel.resource_type == resource_type,
                ResourceLeaseModel.organization_id == tenant_id,
                ResourceLeaseModel.expires_at < now.isoformat()
            ).delete(synchronize_session=False)
            
            # Count active leases under lock
            # We use an advisory lock or a simpler FOR UPDATE on a dummy row, but counting with FOR UPDATE is complex.
            # In PostgreSQL, we can use an advisory lock per tenant+resource to serialize this check.
            lock_id = (int(tenant_id.int) ^ hash(resource_type)) % (2**63 - 1)
            session.execute(select(func.pg_advisory_xact_lock(lock_id)))
            
            active_count = session.scalar(
                select(func.count(ResourceLeaseModel.id)).where(
                    ResourceLeaseModel.resource_type == resource_type,
                    ResourceLeaseModel.organization_id == tenant_id
                )
            )

            if active_count is not None and active_count >= limit:
                raise RuntimeError(f"Quota exceeded for tenant {tenant_id} on {resource_type}")

            lease = ResourceLeaseModel(
                organization_id=tenant_id,
                resource_type=resource_type,
                worker_id=worker_id,
                expires_at=(now + timedelta(seconds=duration_sec)).isoformat()
            )
            session.add(lease)
            session.commit()
            return lease.id

    @classmethod
    def release_lease(cls, tenant_id: uuid.UUID, lease_id: uuid.UUID) -> None:
        """Releases a previously acquired lease."""
        from api_guardian.domain import TenantContext
        ctx = TenantContext(tenant_id=tenant_id)
        with db_manager.get_tenant_session(ctx) as session:
            session.query(ResourceLeaseModel).filter(
                ResourceLeaseModel.id == lease_id,
                ResourceLeaseModel.organization_id == tenant_id
            ).delete(synchronize_session=False)
            session.commit()
