"""Organization and Tenant context domain models."""

import uuid
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True)
class TenantContext:
    """Represents the current tenant context.

    Used to enforce tenant isolation throughout the application stack.
    """

    tenant_id: uuid.UUID


@dataclass
class Organization:
    """An organization that uses API Guardian."""

    id: uuid.UUID
    name: str
    github_installation_id: int | None = None
    created_at: datetime = field(default_factory=datetime.utcnow)
    updated_at: datetime = field(default_factory=datetime.utcnow)

    def is_github_connected(self) -> bool:
        """Check if the organization has an active GitHub App installation."""
        return self.github_installation_id is not None
