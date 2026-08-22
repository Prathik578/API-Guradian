"""SQLAlchemy ORM tables for domain entities."""
import uuid
from typing import Any

from sqlalchemy import JSON, ForeignKey, Integer, String, Uuid
from sqlalchemy import Enum as SQLEnum
from sqlalchemy.orm import Mapped, mapped_column

from api_guardian.domain import (
    MaintenanceCaseState,
    MigrationState,
    VerificationState,
)

from .base import Base, TenantMixin, TimestampMixin


class OrganizationModel(Base, TimestampMixin):
    __tablename__ = "organizations"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    github_installation_id: Mapped[int | None] = mapped_column(Integer, nullable=True)


class RepositoryModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "repositories"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    github_full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    default_branch: Mapped[str] = mapped_column(String(255), nullable=False, default="main")


class MaintenanceCaseModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "maintenance_cases"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("repositories.id"), nullable=False)
    provider_change_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    base_revision_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    state: Mapped[MaintenanceCaseState] = mapped_column(SQLEnum(MaintenanceCaseState), nullable=False)


class MigrationCampaignModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "migration_campaigns"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("maintenance_cases.id"), nullable=False)
    state: Mapped[MigrationState] = mapped_column(SQLEnum(MigrationState), nullable=False)


class VerificationRunModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "verification_runs"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(Uuid, ForeignKey("migration_campaigns.id"), nullable=False)
    patch_artifact_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    sandbox_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[VerificationState] = mapped_column(SQLEnum(VerificationState), nullable=False)
    # the rest of fields could be stored in a JSON column or separate columns
    result_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
