"""Circuit breaker for external dependencies (GitHub, LLM)."""

import time
from collections.abc import Callable
from enum import Enum
from typing import Any


class CircuitState(Enum):
    CLOSED = "closed"
    OPEN = "open"
    HALF_OPEN = "half_open"


class CircuitBreakerOpenError(Exception):
    """Raised when attempting to execute through an open circuit breaker."""


class CircuitBreaker:
    """Prevents cascading failures by short-circuiting failing downstream services."""

    def __init__(self, failure_threshold: int = 5, recovery_timeout_sec: int = 60) -> None:
        self.failure_threshold = failure_threshold
        self.recovery_timeout_sec = recovery_timeout_sec

        self.state = CircuitState.CLOSED
        self.failure_count = 0
        self.last_failure_time = 0.0

    def call(self, func: Callable[..., Any], *args: Any, **kwargs: Any) -> Any:
        """Executes the function if the circuit is not open."""
        self._check_state()

        if self.state == CircuitState.OPEN:
            raise CircuitBreakerOpenError("Circuit is OPEN.")

        try:
            result = func(*args, **kwargs)
            self._on_success()
            return result
        except Exception:
            self._on_failure()
            raise

    def _check_state(self) -> None:
        if (
            self.state == CircuitState.OPEN
            and time.time() - self.last_failure_time >= self.recovery_timeout_sec
        ):
            self.state = CircuitState.HALF_OPEN

    def _on_success(self) -> None:
        if self.state == CircuitState.HALF_OPEN:
            self.state = CircuitState.CLOSED
            self.failure_count = 0

    def _on_failure(self) -> None:
        self.failure_count += 1
        self.last_failure_time = time.time()

        if self.state == CircuitState.HALF_OPEN or self.failure_count >= self.failure_threshold:
            self.state = CircuitState.OPEN
