"""Repository and Snapshot domain models."""
import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass(frozen=True)
class RepositoryRevision:
    """A specific point in a repository's git history.
    
    This is the logical identity of the code at a point in time.
    """
    repository_id: uuid.UUID
    branch: str
    commit_sha: str


@dataclass
class RepositorySnapshot:
    """Immutable analysis context representing the physical archive of a repository.
    
    The architecture proves that the exact repository state analyzed is the 
    exact state verified by comparing the commit SHA and archive_content_hash.
    """
    id: uuid.UUID
    revision: RepositoryRevision
    archive_content_hash: str
    code_model_version: str
    dependency_graph: dict[str, Any] | None = None
    analyzed_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class Repository:
    """Customer-managed codebase registered with API Guardian."""
    id: uuid.UUID
    organization_id: uuid.UUID
    name: str
    github_full_name: str
    default_branch: str = "main"
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = field(default_factory=lambda: datetime.now(UTC))
