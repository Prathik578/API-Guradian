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

    @abstractmethod
    def put_snapshot(self, tenant_id: str, repository_id: str, commit_sha: str, archive_path: str) -> str:
        """Stores a snapshot archive and returns its SHA-256 hash."""

    @abstractmethod
    def get_snapshot(self, tenant_id: str, repository_id: str, commit_sha: str, expected_hash: str) -> str:
        """Retrieves the snapshot archive to a local path, verifying its hash."""

    @abstractmethod
    def put_patch(self, tenant_id: str, patch_id: str, patch_data: str) -> str:
        """Stores a patch and returns its SHA-256 hash."""

    @abstractmethod
    def get_patch(self, tenant_id: str, patch_id: str, expected_hash: str) -> str:
        """Retrieves the patch data as a string, verifying its hash."""

    @abstractmethod
    def generate_consumable_input_capability(self, tenant_id: str, artifact_type: str, artifact_id: str) -> str:
        """Generates a short-lived capability URL (e.g., presigned S3 URL or local HTTP mock URL)."""
