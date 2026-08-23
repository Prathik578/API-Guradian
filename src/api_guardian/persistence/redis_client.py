"""Redis Client."""

import redis


class RedisClient:
    def __init__(self, redis_url: str):
        self.client = redis.from_url(redis_url)

    def set_val(self, key: str, value: str, ex: int | None = None) -> None:
        self.client.set(key, value, ex=ex)

    def get_val(self, key: str) -> str | None:
        val = self.client.get(key)
        if val is not None:
            return val.decode("utf-8") if isinstance(val, bytes) else str(val)
        return None
