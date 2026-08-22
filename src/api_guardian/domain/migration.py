"""Migration domain models."""
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class MigrationState(str, Enum):
    PENDING = "pending"
    GENERATING = "generating"
    VERIFYING = "verifying"
    PR_CREATED = "pr_created"
    BLOCKED = "blocked"
    GENERATION_FAILED = "generation_failed"
    VERIFICATION_FAILED = "verification_failed"
    INFRASTRUCTURE_FAILED = "infrastructure_failed"
    STALE = "stale"
    CANCELLED = "cancelled"
    HUMAN_INTERVENTION_REQUIRED = "human_intervention_required"


@dataclass
class PatchArtifact:
    """Immutable patch bound to a specific repository and commit."""
    id: uuid.UUID
    repository_id: uuid.UUID
    base_commit_sha: str
    archive_content_hash: str
    affected_files: list[str]
    patch_data: str
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class MigrationAttempt:
    """One generation/repair attempt by the migration system."""
    id: uuid.UUID
    campaign_id: uuid.UUID
    model_name: str
    prompt_tokens: int
    completion_tokens: int
    patch_artifact_id: uuid.UUID | None = None
    error_reason: str | None = None
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class MigrationCampaign:
    """Workflow for resolving an affected MaintenanceCase."""
    id: uuid.UUID
    case_id: uuid.UUID
    state: MigrationState = MigrationState.PENDING
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
