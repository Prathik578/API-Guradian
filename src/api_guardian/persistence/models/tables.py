"""SQLAlchemy ORM tables for domain entities."""

import uuid
from typing import Any

from sqlalchemy import JSON, Boolean, ForeignKey, Integer, String, UniqueConstraint, Uuid, text
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


class SnapshotModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "snapshots"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("repositories.id"), nullable=False
    )
    branch: Mapped[str] = mapped_column(String(255), nullable=False)
    commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    archive_content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    code_model_version: Mapped[str] = mapped_column(String(50), nullable=False)
    dependency_graph: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class MaintenanceCaseModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "maintenance_cases"
    __table_args__ = (
        UniqueConstraint("repository_id", "provider_change_id", "base_revision_sha", name="uq_maintenance_case"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("repositories.id"), nullable=False
    )
    provider_change_id: Mapped[uuid.UUID] = mapped_column(Uuid, nullable=False)
    base_revision_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    state: Mapped[MaintenanceCaseState] = mapped_column(
        SQLEnum(MaintenanceCaseState), nullable=False
    )


class ImpactAssessmentModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "impact_assessments"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("maintenance_cases.id"), nullable=False
    )
    snapshot_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("snapshots.id"), nullable=False
    )
    classification: Mapped[str] = mapped_column(String(50), nullable=False)
    evidence_level: Mapped[str] = mapped_column(String(50), nullable=False)
    affected_files: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    evidence_payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)


class MigrationCampaignModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "migration_campaigns"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("maintenance_cases.id"), nullable=False
    )
    state: Mapped[MigrationState] = mapped_column(SQLEnum(MigrationState), nullable=False)


class ProviderChangeModel(Base, TimestampMixin):
    __tablename__ = "provider_changes"
    __table_args__ = (
        UniqueConstraint("provider", "provider_native_id", name="uq_provider_change"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    provider_native_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    classification: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(String(1024), nullable=False)
    affected_entities: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    effective_date: Mapped[Any | None] = mapped_column(
        String(50), nullable=True
    )  # ISO format date strings for MVP
    sunset_date: Mapped[Any | None] = mapped_column(String(50), nullable=True)
    source_artifact_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    revision: Mapped[int] = mapped_column(Integer, nullable=False, default=1, server_default=text("1"))


class ProviderChangeRevisionModel(Base, TimestampMixin):
    __tablename__ = "provider_change_revisions"
    __table_args__ = (
        UniqueConstraint("provider_change_id", "revision_number", name="uq_provider_change_revision"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    provider_change_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("provider_changes.id", ondelete="CASCADE"), nullable=False
    )
    revision_number: Mapped[int] = mapped_column(Integer, nullable=False)
    source_artifact_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    evidence: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    classification: Mapped[str] = mapped_column(String(50), nullable=False)
    summary: Mapped[str] = mapped_column(String(1024), nullable=False)
    evidence_source: Mapped[str] = mapped_column(String(100), nullable=False)


class RawArtifactModel(Base, TimestampMixin):
    __tablename__ = "raw_artifacts"
    __table_args__ = (
        UniqueConstraint("provider", "source_key", "content_hash", name="uq_raw_artifact"),
    )
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    provider: Mapped[str] = mapped_column(String(255), nullable=False)
    source_key: Mapped[str] = mapped_column(String(255), nullable=False)
    content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    source_url: Mapped[str | None] = mapped_column(String(1024), nullable=True)
    source_revision: Mapped[str | None] = mapped_column(String(255), nullable=True)
    content_type: Mapped[str | None] = mapped_column(String(100), nullable=True)
    storage_ref: Mapped[str | None] = mapped_column(String(512), nullable=True)
    fetched_at: Mapped[Any] = mapped_column(String(50), nullable=False)


class PatchArtifactModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "patch_artifacts"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("repositories.id"), nullable=False
    )
    base_commit_sha: Mapped[str] = mapped_column(String(40), nullable=False)
    archive_content_hash: Mapped[str] = mapped_column(String(64), nullable=False)
    affected_files: Mapped[list[str]] = mapped_column(JSON, nullable=False)
    patch_data: Mapped[str] = mapped_column(String, nullable=False)
    patch_hash: Mapped[str | None] = mapped_column(String(64), nullable=True)
    pre_image_hashes: Mapped[dict[str, str] | None] = mapped_column(JSON, nullable=True)


class MigrationAttemptModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "migration_attempts"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("migration_campaigns.id"), nullable=False
    )
    patch_artifact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("patch_artifacts.id"), nullable=False
    )
    model_name: Mapped[str] = mapped_column(String(255), nullable=False)
    prompt_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    completion_tokens: Mapped[int] = mapped_column(Integer, nullable=False)
    error_reason: Mapped[str | None] = mapped_column(String, nullable=True)


class VerificationRunModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "verification_runs"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    campaign_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("migration_campaigns.id"), nullable=False
    )
    patch_artifact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("patch_artifacts.id"), nullable=False
    )
    sandbox_task_id: Mapped[str | None] = mapped_column(String(255), nullable=True)
    state: Mapped[VerificationState] = mapped_column(SQLEnum(VerificationState), nullable=False)
    verification_plan: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    result_data: Mapped[dict[str, Any] | None] = mapped_column(JSON, nullable=True)
    audit_passed: Mapped[bool | None] = mapped_column(Boolean, nullable=True)
    signing_secret: Mapped[str | None] = mapped_column(String(128), nullable=True)
    nonce: Mapped[str | None] = mapped_column(String(64), nullable=True)


class PullRequestModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "pull_requests"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True)
    case_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("maintenance_cases.id"), nullable=False
    )
    patch_artifact_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("patch_artifacts.id"), nullable=False
    )
    repository_id: Mapped[uuid.UUID] = mapped_column(
        Uuid, ForeignKey("repositories.id"), nullable=False
    )
    github_pr_number: Mapped[int] = mapped_column(Integer, nullable=False)
    github_pr_url: Mapped[str] = mapped_column(String, nullable=False)
    head_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    base_branch: Mapped[str] = mapped_column(String(255), nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False)


class TaskOutboxModel(Base, TimestampMixin):
    __tablename__ = "task_outbox"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    task_name: Mapped[str] = mapped_column(String(255), nullable=False)
    payload: Mapped[dict[str, Any]] = mapped_column(JSON, nullable=False)
    dispatched_at: Mapped[Any | None] = mapped_column(String(50), nullable=True)


class WebhookDeliveryModel(Base, TimestampMixin):
    __tablename__ = "webhook_deliveries"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    delivery_id: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    event_type: Mapped[str] = mapped_column(String(100), nullable=False)
    payload_hash: Mapped[str] = mapped_column(String(64), nullable=False)


class CircuitBreakerStateModel(Base, TimestampMixin):
    __tablename__ = "circuit_breaker_states"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    service_name: Mapped[str] = mapped_column(String(255), unique=True, nullable=False)
    state: Mapped[str] = mapped_column(String(50), nullable=False, default="CLOSED")
    consecutive_failures: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    last_failure_time: Mapped[Any | None] = mapped_column(String(50), nullable=True)


class ResourceLeaseModel(Base, TimestampMixin, TenantMixin):
    __tablename__ = "resource_leases"
    id: Mapped[uuid.UUID] = mapped_column(Uuid, primary_key=True, default=uuid.uuid4)
    resource_type: Mapped[str] = mapped_column(String(255), nullable=False)
    worker_id: Mapped[str] = mapped_column(String(255), nullable=False)
    expires_at: Mapped[Any] = mapped_column(String(50), nullable=False)


