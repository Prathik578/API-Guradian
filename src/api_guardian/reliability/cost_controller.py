"""Cost controls to prevent runaway LLM consumption."""

from api_guardian.persistence.redis_client import RedisClient


class TokenBudgetExceededError(Exception):
    """Raised when a tenant exhausts their allocated LLM token budget."""


class CostController:
    """Tracks and enforces LLM token limits per tenant/campaign."""

    def __init__(self, redis_client: RedisClient) -> None:
        self.redis = redis_client

    def check_and_deduct(self, tenant_id: str, estimated_tokens: int) -> None:
        """Atomically checks and deducts budget. Raises if exceeded."""
        key = f"budget:tenant:{tenant_id}"

        # MVP Mock implementation of an atomic operation
        val = self.redis.get_val(key)
        budget = int(val) if val else 100000  # default budget for MVP

        if budget < estimated_tokens:
            raise TokenBudgetExceededError(f"Tenant {tenant_id} exceeded token budget.")

        self.redis.client.decrby(key, estimated_tokens)
