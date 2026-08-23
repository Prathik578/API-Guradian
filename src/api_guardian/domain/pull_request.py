"""Pull Request domain models."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum


class PullRequestState(str, Enum):
    PLANNED = "planned"
    CREATING = "creating"
    OPEN = "open"
    MERGED = "merged"
    CLOSED = "closed"
    STALE = "stale"
    CREATION_FAILED = "creation_failed"


@dataclass
class PullRequest:
    """GitHub PR created from a verified patch."""

    id: uuid.UUID
    case_id: uuid.UUID
    patch_artifact_id: uuid.UUID
    repository_id: uuid.UUID
    github_pr_number: int | None = None
    github_pr_url: str | None = None
    head_branch: str | None = None
    base_branch: str | None = None
    state: PullRequestState = PullRequestState.PLANNED
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
