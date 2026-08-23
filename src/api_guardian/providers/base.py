"""Base provider adapter contract."""

import uuid
from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import Any

from api_guardian.domain import CandidateChange, ProviderChange


@dataclass
class AcquiredSource:
    """Represents a successfully acquired source artifact from a provider."""
    content: bytes
    source_url: str
    content_type: str
    source_key: str
    source_revision: str | None = None


class ProviderAdapter(ABC):
    """Abstract contract for provider-specific source acquisition and change detection."""

    @property
    @abstractmethod
    def provider_id(self) -> str:
        """The canonical ID of this provider (e.g. 'stripe')."""

    @abstractmethod
    def acquire_source(self) -> AcquiredSource:
        """Fetches the source material from the provider."""

    @abstractmethod
    def detect_changes(
        self,
        current_spec: dict[str, Any],
        previous_spec: dict[str, Any] | None,
        current_artifact_id: uuid.UUID,
        previous_artifact_id: uuid.UUID | None,
    ) -> list[CandidateChange]:
        """Detects logical changes between current and previous source states."""

    @abstractmethod
    def interpret_change(self, candidate: CandidateChange) -> ProviderChange:
        """Converts a detected change into a canonical ProviderChange."""
