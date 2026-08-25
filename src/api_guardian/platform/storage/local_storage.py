import hashlib
import os
import shutil
import tempfile
import uuid
from pathlib import Path

from api_guardian.application.interfaces.storage import ArtifactStoragePort


class LocalArtifactStorage(ArtifactStoragePort):
    """Local file-based artifact storage for development and testing."""

    def __init__(self, base_dir: str | None = None) -> None:
        self.base_dir = Path(base_dir) if base_dir else Path(tempfile.gettempdir()) / "api_guardian_artifacts"
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _get_path(self, *parts: str) -> Path:
        target = self.base_dir.joinpath(*parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        return target

    def store_artifact(self, key: str, content: bytes) -> str:
        path = self._get_path("raw", key)
        path.write_bytes(content)
        return str(path)

    def retrieve_artifact(self, key: str) -> bytes:
        path = self._get_path("raw", key)
        if not path.exists():
            raise FileNotFoundError(f"Artifact {key} not found")
        return path.read_bytes()

    def put_snapshot(self, tenant_id: str, repository_id: str, commit_sha: str, archive_path: str) -> str:
        target = self._get_path(tenant_id, repository_id, "snapshots", f"{commit_sha}.tar.gz")
        shutil.copy2(archive_path, target)
        
        hasher = hashlib.sha256()
        with open(target, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        return hasher.hexdigest()

    def get_snapshot(self, tenant_id: str, repository_id: str, commit_sha: str, expected_hash: str | None = None) -> str:
        target = self._get_path(tenant_id, repository_id, "snapshots", f"{commit_sha}.tar.gz")
        if not target.exists():
            raise FileNotFoundError(f"Snapshot not found for commit {commit_sha}")
        
        if expected_hash:
            hasher = hashlib.sha256()
            with open(target, "rb") as f:
                for chunk in iter(lambda: f.read(4096), b""):
                    hasher.update(chunk)
            if hasher.hexdigest() != expected_hash:
                raise ValueError("Artifact corruption detected: SHA-256 hash mismatch")
                
        return str(target)

    def put_patch(self, tenant_id: str, patch_id: str, patch_data: str) -> str:
        target = self._get_path(tenant_id, "patches", f"{patch_id}.diff")
        target.write_text(patch_data, encoding="utf-8")
        return hashlib.sha256(patch_data.encode("utf-8")).hexdigest()

    def get_patch(self, tenant_id: str, patch_id: str, expected_hash: str | None = None) -> str:
        target = self._get_path(tenant_id, "patches", f"{patch_id}.diff")
        if not target.exists():
            raise FileNotFoundError(f"Patch {patch_id} not found")
            
        content = target.read_bytes()
        if expected_hash:
            if hashlib.sha256(content).hexdigest() != expected_hash:
                raise ValueError("Artifact corruption detected: SHA-256 hash mismatch")
                
        return content.decode("utf-8")

    def generate_consumable_input_capability(self, tenant_id: str, artifact_type: str, artifact_id: str) -> str:
        """Returns a local file:// URL for the sandbox to consume directly."""
        if artifact_type == "snapshot":
            # artifact_id is formatted as repo_id/commit_sha
            repo_id, commit_sha = artifact_id.split("/")
            path = self._get_path(tenant_id, repo_id, "snapshots", f"{commit_sha}.tar.gz")
        elif artifact_type == "patch":
            path = self._get_path(tenant_id, "patches", f"{artifact_id}.diff")
        else:
            raise ValueError(f"Unknown artifact type {artifact_type}")
            
        if not path.exists():
            raise FileNotFoundError(f"Capability generation failed: {path} does not exist.")
            
        return f"file://{path.absolute()}"
