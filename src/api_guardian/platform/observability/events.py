"""Structured observability and event tracing."""

import json
import logging
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from typing import Any


@dataclass
class StructuredEvent:
    event_type: str
    tenant_id: str | None = None
    repository_id: str | None = None
    case_id: str | None = None
    campaign_id: str | None = None
    attempt_id: str | None = None
    job_id: str | None = None
    timestamp: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    payload: dict[str, Any] = field(default_factory=dict)

    def to_json(self) -> str:
        return json.dumps(asdict(self))


class Observability:
    """Central entrypoint for structured metrics and traces."""
    
    _logger = logging.getLogger("api_guardian.structured")

    @classmethod
    def emit(cls, event: StructuredEvent) -> None:
        # In MVP we emit to stdout/logger. In prod, this goes to Datadog/CloudWatch JSON intake
        cls._logger.info(event.to_json())

    @classmethod
    def record_job_started(cls, job_id: str, job_type: str, tenant_id: str) -> None:
        cls.emit(StructuredEvent(
            event_type="JOB_STARTED",
            job_id=job_id,
            tenant_id=tenant_id,
            payload={"job_type": job_type}
        ))

    @classmethod
    def record_job_completed(cls, job_id: str, job_type: str, duration_sec: float) -> None:
        cls.emit(StructuredEvent(
            event_type="JOB_COMPLETED",
            job_id=job_id,
            payload={"job_type": job_type, "duration_sec": duration_sec}
        ))

    @classmethod
    def record_llm_usage(
        cls, attempt_id: str, tenant_id: str, prompt_tokens: int, completion_tokens: int
    ) -> None:
        estimated_cost_cents = ((prompt_tokens * 1.5) + (completion_tokens * 2.0)) / 1000
        cls.emit(StructuredEvent(
            event_type="LLM_USAGE",
            attempt_id=attempt_id,
            tenant_id=tenant_id,
            payload={
                "prompt_tokens": prompt_tokens,
                "completion_tokens": completion_tokens,
                "estimated_cost_cents": estimated_cost_cents
            }
        ))

    @classmethod
    def record_verification_result(
        cls, attempt_id: str, case_id: str, tenant_id: str, success: bool, duration_sec: float
    ) -> None:
        cls.emit(StructuredEvent(
            event_type="VERIFICATION_RESULT",
            attempt_id=attempt_id,
            case_id=case_id,
            tenant_id=tenant_id,
            payload={
                "success": success,
                "duration_sec": duration_sec
            }
        ))
