"""Stripe OpenAPI acquisition adapter."""

import logging
import uuid
from typing import Any

import httpx

from api_guardian.domain import CandidateChange, ProviderChange
from api_guardian.providers.base import AcquiredSource, ProviderAdapter
from api_guardian.providers.stripe.detector import StripeChangeDetector
from api_guardian.providers.stripe.errors import StripeRateLimitError, StripeSyncError
from api_guardian.providers.stripe.interpreter import StripeChangeInterpreter

logger = logging.getLogger(__name__)


class StripeOpenAPIAdapter(ProviderAdapter):
    """
    Adapter for acquiring and processing Stripe's OpenAPI spec.
    Current-snapshot limitation: uses the master branch spec3.json as a point-in-time
    observation source, not a complete historical changelog.
    """

    SPEC_URL = "https://raw.githubusercontent.com/stripe/openapi/master/openapi/spec3.json"
    MAX_RESPONSE_SIZE = 10 * 1024 * 1024  # 10MB

    @property
    def provider_id(self) -> str:
        return "stripe"

    def acquire_source(self) -> AcquiredSource:
        """Fetches the OpenAPI spec3.json from GitHub."""
        # We use explicit limits to prevent hanging or memory exhaustion
        limits = httpx.Limits(max_keepalive_connections=1, max_connections=1)
        timeout = httpx.Timeout(30.0, read=60.0)

        with (
            httpx.Client(limits=limits, timeout=timeout) as client,
            client.stream("GET", self.SPEC_URL) as response,
        ):
            if response.status_code == 429:
                retry_after = response.headers.get("Retry-After")
                delay = int(retry_after) if retry_after and retry_after.isdigit() else 60
                raise StripeRateLimitError("Rate limited by GitHub raw content", retry_after=delay)
            
            if 500 <= response.status_code < 600:
                # Will be caught by Celery as transient via httpx.HTTPStatusError
                response.raise_for_status()
            
            if 400 <= response.status_code < 500:
                # Permanent failure for things like 404
                logger.error(f"Failed to fetch Stripe OpenAPI spec: {response.status_code}")
                raise StripeSyncError(f"Permanent HTTP error: {response.status_code}")

            content_type = response.headers.get("content-type", "")
            if "application/json" not in content_type and "text/plain" not in content_type:
                raise StripeSyncError(f"Unexpected content type: {content_type}")

            content_chunks = []
            size = 0
            for chunk in response.iter_bytes():
                size += len(chunk)
                if size > self.MAX_RESPONSE_SIZE:
                    raise StripeSyncError("Response exceeded 10MB maximum size")
                content_chunks.append(chunk)

            content = b"".join(content_chunks)
            
            source_revision = response.headers.get("ETag") or response.headers.get("Last-Modified")

            return AcquiredSource(
                content=content,
                source_url=self.SPEC_URL,
                content_type="application/json",
                source_key="openapi/spec3",
                source_revision=source_revision,
            )

    def detect_changes(
        self,
        current_spec: dict[str, Any],
        previous_spec: dict[str, Any] | None,
        current_artifact_id: uuid.UUID,
        previous_artifact_id: uuid.UUID | None,
    ) -> list[CandidateChange]:
        detector = StripeChangeDetector()
        return detector.detect_changes(
            current_spec, previous_spec, current_artifact_id, previous_artifact_id
        )

    def interpret_change(self, candidate: CandidateChange) -> ProviderChange:
        interpreter = StripeChangeInterpreter()
        return interpreter.interpret_change(candidate)
