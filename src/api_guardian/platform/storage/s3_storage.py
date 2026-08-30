"""S3 Artifact Storage implementation."""

import hashlib
import os
import re
import uuid

import boto3
from botocore.exceptions import ClientError

from api_guardian.application.interfaces.storage import ArtifactStoragePort


class S3ArtifactStorage(ArtifactStoragePort):
    """Production S3-backed artifact storage."""

    def __init__(self, bucket_name: str, region_name: str = "us-east-1"):
        self.bucket_name = bucket_name
        self.s3_client = boto3.client("s3", region_name=region_name)

    def _validate_identifier(self, identifier: str) -> None:
        if not re.match(r"^[a-zA-Z0-9\-_]+$", identifier):
            raise ValueError(f"Invalid identifier format: {identifier}")

    def _get_key(self, *parts: str) -> str:
        for part in parts:
            if "/" in part or ".." in part:
                raise ValueError("Path traversal detected")
        return "/".join(parts)

    def store_artifact(self, key: str, content: bytes) -> str:
        full_key = self._get_key("raw", key)
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=full_key,
            Body=content,
        )
        return f"s3://{self.bucket_name}/{full_key}"

    def retrieve_artifact(self, key: str) -> bytes:
        full_key = self._get_key("raw", key)
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=full_key)
            return response["Body"].read()
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Artifact {key} not found in S3")
            raise

    def put_snapshot(self, tenant_id: str, repository_id: str, commit_sha: str, archive_path: str) -> str:
        self._validate_identifier(tenant_id)
        self._validate_identifier(repository_id)
        key = self._get_key(tenant_id, repository_id, "snapshots", f"{commit_sha}.tar.gz")
        
        hasher = hashlib.sha256()
        file_size = os.path.getsize(archive_path)
        
        # Calculate hash first
        with open(archive_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
                
        # Upload
        with open(archive_path, "rb") as f:
            self.s3_client.put_object(
                Bucket=self.bucket_name,
                Key=key,
                Body=f,
                ContentLength=file_size,
                Metadata={"sha256": hasher.hexdigest()}
            )
            
        return hasher.hexdigest()

    def get_snapshot(self, tenant_id: str, repository_id: str, commit_sha: str, expected_hash: str) -> str:
        self._validate_identifier(tenant_id)
        self._validate_identifier(repository_id)
        if not expected_hash:
            raise ValueError("expected_hash is required for artifact integrity")
        key = self._get_key(tenant_id, repository_id, "snapshots", f"{commit_sha}.tar.gz")
        
        import tempfile
        tmp_path = os.path.join(tempfile.gettempdir(), f"{uuid.uuid4()}_{commit_sha}.tar.gz")
        try:
            self.s3_client.download_file(self.bucket_name, key, tmp_path)
        except ClientError as e:
            if e.response["Error"]["Code"] == "404" or e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError("Snapshot not found in S3")
            raise
            
        hasher = hashlib.sha256()
        with open(tmp_path, "rb") as f:
            for chunk in iter(lambda: f.read(4096), b""):
                hasher.update(chunk)
        if hasher.hexdigest() != expected_hash:
            os.remove(tmp_path)
            raise ValueError("Artifact corruption detected: SHA-256 hash mismatch")
                
        return tmp_path

    def put_patch(self, tenant_id: str, patch_id: str, patch_data: str) -> str:
        self._validate_identifier(tenant_id)
        self._validate_identifier(patch_id)
        key = self._get_key(tenant_id, "patches", f"{patch_id}.diff")
        content_bytes = patch_data.encode("utf-8")
        patch_hash = hashlib.sha256(content_bytes).hexdigest()
        
        self.s3_client.put_object(
            Bucket=self.bucket_name,
            Key=key,
            Body=content_bytes,
            Metadata={"sha256": patch_hash}
        )
        return patch_hash

    def get_patch(self, tenant_id: str, patch_id: str, expected_hash: str) -> str:
        self._validate_identifier(tenant_id)
        self._validate_identifier(patch_id)
        if not expected_hash:
            raise ValueError("expected_hash is required for artifact integrity")
        key = self._get_key(tenant_id, "patches", f"{patch_id}.diff")
        try:
            response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
            content = response["Body"].read()
            actual_hash = hashlib.sha256(content).hexdigest()
            if actual_hash != expected_hash:
                raise ValueError("Artifact corruption detected: SHA-256 hash mismatch")
            return content.decode("utf-8")
        except ClientError as e:
            if e.response["Error"]["Code"] == "NoSuchKey":
                raise FileNotFoundError(f"Patch {patch_id} not found in S3")
            raise

    def generate_consumable_input_capability(self, tenant_id: str, artifact_type: str, artifact_id: str) -> str:
        """Returns a pre-signed URL for the sandbox to consume."""
        self._validate_identifier(tenant_id)
        if artifact_type == "snapshot":
            repo_id, commit_sha = artifact_id.split("/")
            self._validate_identifier(repo_id)
            key = self._get_key(tenant_id, repo_id, "snapshots", f"{commit_sha}.tar.gz")
        elif artifact_type == "patch":
            self._validate_identifier(artifact_id)
            key = self._get_key(tenant_id, "patches", f"{artifact_id}.diff")
        else:
            raise ValueError(f"Unknown artifact type {artifact_type}")
            
        try:
            url = self.s3_client.generate_presigned_url(
                "get_object",
                Params={"Bucket": self.bucket_name, "Key": key},
                ExpiresIn=3600
            )
            return url
        except ClientError as e:
            raise RuntimeError(f"Failed to generate pre-signed URL: {e}")
