import os
import uuid
import hashlib
import pytest
import boto3
from botocore.exceptions import ClientError
from api_guardian.platform.storage.s3_storage import S3ArtifactStorage

@pytest.fixture(scope="module")
def run_id():
    return f"phase25x-{uuid.uuid4().hex[:8]}"

@pytest.fixture(scope="module")
def real_s3_storage(run_id):
    region = os.environ.get("AWS_REGION", "us-east-1")
    s3_client = boto3.client("s3", region_name=region)
    bucket_name = f"api-guardian-test-{run_id}"
    
    # We only create the bucket if AWS credentials exist and we're opted in
    # This fixture should technically only execute if the test runs.
    try:
        if region == "us-east-1":
            s3_client.create_bucket(Bucket=bucket_name)
        else:
            s3_client.create_bucket(
                Bucket=bucket_name,
                CreateBucketConfiguration={'LocationConstraint': region}
            )
    except Exception as e:
        pytest.skip(f"Failed to create bucket: {e}")
        
    yield S3ArtifactStorage(bucket_name=bucket_name, region_name=region)
    
    # Cleanup
    try:
        objects = s3_client.list_objects_v2(Bucket=bucket_name)
        if 'Contents' in objects:
            for obj in objects['Contents']:
                s3_client.delete_object(Bucket=bucket_name, Key=obj['Key'])
        s3_client.delete_bucket(Bucket=bucket_name)
    except Exception as e:
        print(f"Failed to cleanup test bucket {bucket_name}: {e}")

@pytest.mark.real_aws
def test_s3_positive_flow(real_s3_storage):
    tenant_id = "tenant-a"
    repo_id = str(uuid.uuid4())
    commit_sha = "abcd1234efgh5678"
    
    content = b"real aws runtime content"
    expected_hash = hashlib.sha256(content).hexdigest()
    
    import tempfile
    with tempfile.NamedTemporaryFile(delete=False) as f:
        f.write(content)
        archive_path = f.name
        
    try:
        returned_hash = real_s3_storage.put_snapshot(tenant_id, repo_id, commit_sha, archive_path)
        assert returned_hash == expected_hash
        
        dl_path = real_s3_storage.get_snapshot(tenant_id, repo_id, commit_sha, expected_hash=expected_hash)
        with open(dl_path, "rb") as d:
            assert d.read() == content
    finally:
        if os.path.exists(archive_path):
            os.remove(archive_path)

@pytest.mark.real_aws
def test_s3_hash_integrity_negative(real_s3_storage):
    tenant_id = "tenant-a"
    patch_id = str(uuid.uuid4())
    content = "real patch data"
    expected_hash = hashlib.sha256(content.encode()).hexdigest()
    
    real_s3_storage.put_patch(tenant_id, patch_id, content)
    
    with pytest.raises(ValueError, match="Artifact corruption"):
        real_s3_storage.get_patch(tenant_id, patch_id, expected_hash="wronghash")
