"""Data models for LLM Reasoning."""
import uuid
from dataclasses import dataclass, field


@dataclass
class DiffBlock:
    """Represents a discrete code modification."""
    file_path: str
    original_snippet: str
    modified_snippet: str


@dataclass
class PatchArtifact:
    """The generated outcome of a migration reasoning attempt."""
    id: uuid.UUID
    repository_id: uuid.UUID
    commit_sha: str
    diff_blocks: list[DiffBlock] = field(default_factory=list)
    explanation: str = ""
