"""Rate limiting with Redis backing for multi-instance deployments."""
from __future__ import annotations

import time
from typing import Dict, Tuple

from fastapi import HTTPException

from .config import Settings
from .redis_client import get_redis


class RateLimiter:
    def __init__(self, settings: Settings) -> None:
        self._limit = settings.rate_limit_per_day
        self._buckets: Dict[str, Tuple[int, float]] = {}
        self._redis = get_redis(settings)

    def check(self, device_id: str) -> tuple[int, int]:
        now = time.time()
        if self._redis:
            key = f"rl:{device_id}"
            count = self._redis.incr(key)
            if count == 1:
                self._redis.expire(key, 86400)
            ttl = self._redis.ttl(key)
            if ttl <= 0:
                self._redis.expire(key, 86400)
                ttl = 86400
            if count > self._limit:
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            remaining = max(self._limit - count, 0)
            reset_at = int(now + ttl)
            return remaining, reset_at
        count, reset_at = self._buckets.get(device_id, (0, now + 86400))
        if now > reset_at:
            count, reset_at = 0, now + 86400
        count += 1
        self._buckets[device_id] = (count, reset_at)
        if count > self._limit:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        remaining = max(self._limit - count, 0)
        return remaining, int(reset_at)
