"""Redis helper for relay state."""
from __future__ import annotations

from typing import Optional

from .config import Settings

try:
    from redis import Redis
except Exception:  # pragma: no cover - optional dependency in dev
    Redis = None


def get_redis(settings: Settings) -> Optional["Redis"]:
    if not settings.redis_url:
        return None
    if Redis is None:
        raise RuntimeError("redis package not installed")
    return Redis.from_url(settings.redis_url, decode_responses=True)