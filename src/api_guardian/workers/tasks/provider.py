import logging
import os
from typing import Any

import httpx
from sqlalchemy.exc import OperationalError

from api_guardian.application.interfaces.storage import ArtifactStoragePort
from api_guardian.application.use_cases.sync_provider import SyncProviderUseCase
from api_guardian.persistence.database import db_manager
from api_guardian.persistence.repositories.maintenance_case_repo import SQLMaintenanceCaseRepository
from api_guardian.persistence.repositories.provider_change_repo import SQLProviderChangeRepository
from api_guardian.persistence.repositories.raw_artifact_repo import SQLRawArtifactRepository
from api_guardian.persistence.s3_storage import S3StorageAdapter
from api_guardian.providers.stripe.adapter import StripeOpenAPIAdapter
from api_guardian.providers.stripe.errors import StripeRateLimitError
from api_guardian.workers.celery_app import app

logger = logging.getLogger(__name__)

class S3ArtifactStorage(S3StorageAdapter, ArtifactStoragePort):
    """Adapter for the ArtifactStoragePort using the existing S3StorageAdapter."""
    def store_artifact(self, key: str, content: bytes) -> str:
        # We need a file-like object for upload_fileobj, but we have bytes
        import io
        self.upload_artifact(key, io.BytesIO(content))
        return key

    def retrieve_artifact(self, key: str) -> bytes:
        # S3StorageAdapter doesn't have a direct download method, so we use boto3 directly
        response = self.s3_client.get_object(Bucket=self.bucket_name, Key=key)
        return response['Body'].read()


@app.task(bind=True, max_retries=3)  # type: ignore[untyped-decorator]
def sync_provider_task(self: Any, tenant_id_str: str, payload: dict[str, Any]) -> None:
    try:
        pass
    except Exception as e:
        logger.error(f"Failed to sync provider payload: {e}")
        raise


@app.task(bind=True, max_retries=5)  # type: ignore[untyped-decorator]
def sync_stripe_task(self: Any) -> None:
    """Periodic Stripe OpenAPI sync."""
    try:
        adapter = StripeOpenAPIAdapter()
        
        # Determine S3 bucket from env or use a default test bucket
        bucket = os.environ.get("S3_ARTIFACT_BUCKET", "api-guardian-artifacts")
        region = os.environ.get("AWS_REGION", "us-east-1")
        artifact_storage = S3ArtifactStorage(bucket_name=bucket, region_name=region)
        
        use_case = SyncProviderUseCase(
            provider_adapter=adapter,
            raw_artifact_repo=SQLRawArtifactRepository(db_manager),
            provider_repo=SQLProviderChangeRepository(db_manager),
            case_repo=SQLMaintenanceCaseRepository(db_manager),
            artifact_storage=artifact_storage,
        )
        use_case.execute()
    except (httpx.TimeoutException, httpx.ConnectError, OperationalError) as e:
        # Transient — retry
        logger.warning(f"Transient error in sync_stripe_task: {e}")
        raise self.retry(exc=e, countdown=2 ** self.request.retries)
    except StripeRateLimitError as e:
        # Transient — retry with provider-specified delay
        delay = e.retry_after or 60
        logger.warning(f"Rate limited in sync_stripe_task. Retrying in {delay}s")
        raise self.retry(exc=e, countdown=delay)
    except Exception as e:
        # Permanent — log and fail
        logger.error(f"Failed sync_stripe_task: {e}")
        raise
