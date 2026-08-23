"""SQLAlchemy Declarative Base and mixins."""

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    pass


class TimestampMixin:
    created_at: Mapped[datetime] = mapped_column(DateTime, default=func.now(), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime, default=func.now(), onupdate=func.now(), nullable=False
    )


class TenantMixin:
    """Mixin for models that belong to a specific tenant (organization)."""

    organization_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False, index=True)
