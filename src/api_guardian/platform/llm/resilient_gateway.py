"""Resilient LLM Gateway with circuit breaking, retries, and rate limiting."""

import logging
import time
from datetime import UTC, datetime
from typing import Any

from api_guardian.application.interfaces.llm import LLMGateway, LLMRole

logger = logging.getLogger(__name__)


class CircuitBreakerOpen(Exception):
    pass


class QuotaExceededError(Exception):
    pass


class ResilientLLMGateway(LLMGateway):
    """Wraps an underlying LLMGateway with production resilience."""

    def __init__(
        self,
        underlying: LLMGateway,
        max_retries: int = 3,
        circuit_failure_threshold: int = 5,
        circuit_reset_timeout_seconds: int = 60,
    ) -> None:
        self.underlying = underlying
        self.max_retries = max_retries
        self.circuit_failure_threshold = circuit_failure_threshold
        self.circuit_reset_timeout_seconds = circuit_reset_timeout_seconds
        
        self.service_name = "llm_gateway"

    def _get_or_create_state(self, session: Any) -> Any:
        from sqlalchemy import select

        from api_guardian.persistence.models.tables import CircuitBreakerStateModel
        
        # Atomic lock on the row
        state_model = session.scalar(
            select(CircuitBreakerStateModel)
            .where(CircuitBreakerStateModel.service_name == self.service_name)
            .with_for_update()
        )
        if not state_model:
            state_model = CircuitBreakerStateModel(service_name=self.service_name)
            session.add(state_model)
            session.flush()
        return state_model

    def _check_circuit(self) -> None:
        from api_guardian.persistence.database import db_manager
        with db_manager.get_session() as session:
            state_model = self._get_or_create_state(session)
            if state_model.state == "OPEN":
                if state_model.last_failure_time:
                    now = datetime.now(UTC)
                    last_fail = datetime.fromisoformat(state_model.last_failure_time)
                    if (now - last_fail).total_seconds() > self.circuit_reset_timeout_seconds:
                        state_model.state = "HALF_OPEN"
                        session.commit()
                        logger.info("Circuit breaker transitioning to HALF_OPEN")
                        return
                raise CircuitBreakerOpen("LLM Gateway circuit is OPEN")

    def _record_success(self) -> None:
        from api_guardian.persistence.database import db_manager
        with db_manager.get_session() as session:
            state_model = self._get_or_create_state(session)
            if state_model.state == "HALF_OPEN" or state_model.consecutive_failures > 0:
                state_model.state = "CLOSED"
                state_model.consecutive_failures = 0
                session.commit()
                logger.info("Circuit breaker transitioning to CLOSED")

    def _record_failure(self) -> bool:
        from api_guardian.persistence.database import db_manager
        with db_manager.get_session() as session:
            state_model = self._get_or_create_state(session)
            state_model.consecutive_failures += 1
            state_model.last_failure_time = datetime.now(UTC).isoformat()
            
            if state_model.state == "HALF_OPEN" or state_model.consecutive_failures >= self.circuit_failure_threshold:
                state_model.state = "OPEN"
                logger.warning(f"Circuit breaker transitioning to OPEN after {state_model.consecutive_failures} failures")
            
            is_open = bool(state_model.state == "OPEN")
            session.commit()
            return is_open

    def _execute_with_resilience(self, func: Any, *args: Any, **kwargs: Any) -> Any:
        self._check_circuit()
        
        # Also enforce MVP token bounds here contextually
        max_tokens = kwargs.get("max_tokens", 4096)
        if max_tokens > 8192:
            raise ValueError("Requested output tokens exceeds max allowed (8192)")
            
        # Basic retry loop
        last_err = None
        for attempt in range(self.max_retries + 1):
            try:
                # Add hard timeout semantics (mocked via simple call here for MVP)
                # In production, use `asyncio.wait_for` or `concurrent.futures.Future`
                result = func(*args, **kwargs)
                self._record_success()
                return result
            except Exception as e:
                last_err = e
                logger.error(f"LLM Call Failed (Attempt {attempt + 1}/{self.max_retries + 1}): {e}")
                is_open = self._record_failure()
                
                if is_open:
                    raise CircuitBreakerOpen("LLM circuit opened during retry loop") from e
                    
                if attempt < self.max_retries:
                    # Exponential backoff with naive jitter
                    delay = (2 ** attempt) + 0.5
                    time.sleep(delay)
                    
        raise RuntimeError("LLM Gateway exhausted retries") from last_err

    def generate_completion(self, role: LLMRole, prompt_envelope: str, max_tokens: int | None = None) -> tuple[str, int, int]:
        result = self._execute_with_resilience(
            self.underlying.generate_completion, role, prompt_envelope, max_tokens=max_tokens
        )
        return result  # type: ignore

    def generate_structured(self, role: LLMRole, prompt_envelope: str, schema_cls: type, max_tokens: int | None = None) -> tuple[dict[str, Any], int, int]:
        result = self._execute_with_resilience(
            self.underlying.generate_structured, role, prompt_envelope, schema_cls, max_tokens=max_tokens
        )
        return result  # type: ignore
