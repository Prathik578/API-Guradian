"""Storage interfaces and implementations."""

from abc import ABC, abstractmethod


class ArtifactStoragePort(ABC):
    """Abstract interface for storing large raw artifacts."""

    @abstractmethod
    def store_artifact(self, key: str, content: bytes) -> str:
        """Stores artifact and returns a storage reference."""

    @abstractmethod
    def retrieve_artifact(self, key: str) -> bytes:
        """Retrieves artifact by its storage reference."""
