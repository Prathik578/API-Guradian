"""Provider change domain models."""

import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from typing import Any


class ChangeClassification(str, Enum):
    DEPRECATION = "deprecation"
    BREAKING_BEHAVIOR = "breaking_behavior"
    SIGNATURE_CHANGE = "signature_change"
    SUNSET = "sunset"
    SECURITY = "security"
    UNKNOWN = "unknown"


class EvidenceSource(str, Enum):
    OBSERVED_SCHEMA_CHANGE = "observed_schema_change"
    OFFICIAL_CHANGELOG = "official_changelog"
    OFFICIAL_MIGRATION_GUIDE = "official_migration_guide"
    OFFICIAL_VERSION_METADATA = "official_version_metadata"


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
    source_key: str
    content_hash: str
    source_url: str | None = None
    source_revision: str | None = None
    content_type: str | None = None
    storage_ref: str | None = None
    content: str | None = None
    fetched_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class CandidateChange:
    """Intermediate extraction before it becomes a canonical ProviderChange."""

    id: uuid.UUID
    raw_artifact_id: uuid.UUID
    previous_artifact_id: uuid.UUID | None
    provider: str
    change_type: str
    target_entity: str
    extracted_summary: str
    evidence_source: EvidenceSource
    evidence: dict[str, Any] | None = None


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
    source_artifact_hash: str | None = None
    revision: int = 1
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))


@dataclass
class ProviderChangeRevision:
    """Immutable append-only history of canonical change revisions."""

    id: uuid.UUID
    provider_change_id: uuid.UUID
    revision_number: int
    source_artifact_hash: str
    evidence: dict[str, Any]
    classification: ChangeClassification
    summary: str
    evidence_source: EvidenceSource
    created_at: datetime = field(default_factory=lambda: datetime.now(UTC))
