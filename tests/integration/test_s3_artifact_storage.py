"""Phase 20A: Real AWS Artifact Lifecycle Proof."""

import hashlib
import os
import tempfile
import uuid

import pytest

from api_guardian.platform.storage.s3_storage import S3ArtifactStorage


@pytest.fixture
def s3_storage(monkeypatch):
    """Provides a mocked S3 storage for integration testing.
    
    In a true AWS-connected integration test, we'd use a real bucket or moto.
    Here we use moto to mock the AWS S3 endpoint entirely but run the real boto3 code.
    """
    try:
        import boto3
        from moto import mock_aws
    except ImportError:
        pytest.skip("moto not installed")

    with mock_aws():
        client = boto3.client("s3", region_name="us-east-1")
        bucket_name = "api-guardian-artifacts-test"
        client.create_bucket(Bucket=bucket_name)
        yield S3ArtifactStorage(bucket_name=bucket_name, region_name="us-east-1")


def test_s3_snapshot_lifecycle(s3_storage):
    tenant_id = str(uuid.uuid4())
    repo_id = str(uuid.uuid4())
    commit_sha = "abcd1234efgh5678"
    
    # Create fake archive
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(b"fake archive content")
        archive_path = f.name
        
    try:
        # Calculate expected hash
        expected_hash = hashlib.sha256(b"fake archive content").hexdigest()
        
        # 1. Put Snapshot
        returned_hash = s3_storage.put_snapshot(tenant_id, repo_id, commit_sha, archive_path)
        assert returned_hash == expected_hash
        
        # 2. Get Snapshot with verification
        downloaded_path = s3_storage.get_snapshot(tenant_id, repo_id, commit_sha, expected_hash=expected_hash)
        with open(downloaded_path, "rb") as d:
            assert d.read() == b"fake archive content"
        os.remove(downloaded_path)
        
        # 3. Corrupt artifact and verify it fails
        # Manually overwrite the S3 object
        s3_storage.s3_client.put_object(
            Bucket=s3_storage.bucket_name,
            Key=f"{tenant_id}/{repo_id}/snapshots/{commit_sha}.tar.gz",
            Body=b"corrupted content"
        )
        
        with pytest.raises(ValueError, match="Artifact corruption detected"):
            s3_storage.get_snapshot(tenant_id, repo_id, commit_sha, expected_hash=expected_hash)
            
    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)


def test_s3_patch_lifecycle(s3_storage):
    tenant_id = str(uuid.uuid4())
    patch_id = str(uuid.uuid4())
    patch_data = "diff --git a/test.py b/test.py\n..."
    
    expected_hash = hashlib.sha256(patch_data.encode("utf-8")).hexdigest()
    
    returned_hash = s3_storage.put_patch(tenant_id, patch_id, patch_data)
    assert returned_hash == expected_hash
    
    retrieved_patch = s3_storage.get_patch(tenant_id, patch_id, expected_hash=expected_hash)
    assert retrieved_patch == patch_data
    
    # Corrupt patch
    s3_storage.s3_client.put_object(
        Bucket=s3_storage.bucket_name,
        Key=f"{tenant_id}/patches/{patch_id}.diff",
        Body=b"corrupted patch data"
    )
    
    with pytest.raises(ValueError, match="Artifact corruption detected"):
        s3_storage.get_patch(tenant_id, patch_id, expected_hash=expected_hash)
