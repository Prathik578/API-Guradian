"""Provider change domain models."""
import uuid
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum


class ChangeClassification(str, Enum):
    DEPRECATION = "deprecation"
    BREAKING_BEHAVIOR = "breaking_behavior"
    SIGNATURE_CHANGE = "signature_change"
    SUNSET = "sunset"
    SECURITY = "security"
    UNKNOWN = "unknown"


@dataclass
class VersionGraph:
    """Represents version relationships for an API/SDK."""
    versions: list[str]
    compatibility_edges: dict[str, list[str]]
    deprecations: dict[str, datetime | None]


@dataclass
class RawArtifact:
    """Immutable representation of provider source used for interpretation."""
    id: uuid.UUID
    provider: str
    content: str
    content_hash: str
    source_url: str | None = None
    fetched_at: datetime = field(default_factory=datetime.utcnow)


@dataclass
class CandidateChange:
    """Intermediate extraction before it becomes a canonical ProviderChange."""
    id: uuid.UUID
    raw_artifact_id: uuid.UUID
    provider: str
    extracted_summary: str


@dataclass
class ProviderChange:
    """Canonical immutable interpretation of a provider change."""
    id: uuid.UUID
    provider: str
    provider_native_id: str | None
    classification: ChangeClassification
    summary: str
    affected_entities: list[str]
    effective_date: datetime | None
    sunset_date: datetime | None
    created_at: datetime = field(default_factory=datetime.utcnow)
