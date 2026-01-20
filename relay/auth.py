"""Token store with Redis backing for multi-instance deployments."""
from __future__ import annotations

import secrets
import time
from typing import Dict, Tuple

from .config import Settings
from .redis_client import get_redis


class TokenStore:
    def __init__(self, settings: Settings) -> None:
        self._ttl = settings.token_ttl_seconds
        self._tokens: Dict[str, Tuple[str, float]] = {}
        self._redis = get_redis(settings)

    def issue_token(self, device_id: str) -> Tuple[str, int]:
        token = secrets.token_urlsafe(32)
        expires_at = int(time.time()) + self._ttl
        if self._redis:
            key = f"token:{token}"
            self._redis.setex(key, self._ttl, device_id)
        else:
            self._tokens[token] = (device_id, float(expires_at))
        return token, expires_at

    def verify_token(self, token: str) -> str | None:
        if self._redis:
            key = f"token:{token}"
            device_id = self._redis.get(key)
            return device_id
        self._purge_expired()
        info = self._tokens.get(token)
        if not info:
            return None
        device_id, expires_at = info
        if time.time() > expires_at:
            self._tokens.pop(token, None)
            return None
        return device_id

    def _purge_expired(self) -> None:
        now = time.time()
        expired = [t for t, (_, exp) in self._tokens.items() if now > exp]
        for token in expired:
            self._tokens.pop(token, None)
