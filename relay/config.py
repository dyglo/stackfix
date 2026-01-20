"""Configuration loader for the StackFix relay."""
from __future__ import annotations

import os
from dataclasses import dataclass


def _env(name: str, default: str = "") -> str:
    value = os.environ.get(name, default)
    return value.strip() if isinstance(value, str) else value


@dataclass(frozen=True)
class Settings:
    relay_host: str
    relay_port: int
    relay_secret: str
    token_ttl_seconds: int
    rate_limit_per_day: int
    redis_url: str
    upstream_base_url: str
    upstream_api_key: str
    upstream_model: str


def load_settings() -> Settings:
    env = _env("STACKFIX_ENV", "dev")
    relay_secret = _env("STACKFIX_RELAY_SECRET")
    if not relay_secret:
        if env == "dev":
            relay_secret = "dev-insecure"
        else:
            raise RuntimeError("STACKFIX_RELAY_SECRET is required in production")

    upstream_base_url = _env("STACKFIX_UPSTREAM_BASE_URL") or _env("NEBIUS_BASE_URL")
    upstream_api_key = _env("STACKFIX_UPSTREAM_API_KEY") or _env("NEBIUS_API_KEY")
    upstream_model = _env("STACKFIX_UPSTREAM_MODEL") or _env("NEBIUS_MODEL")

    if not upstream_base_url:
        raise RuntimeError("STACKFIX_UPSTREAM_BASE_URL (or NEBIUS_BASE_URL) is required")
    if not upstream_api_key:
        raise RuntimeError("STACKFIX_UPSTREAM_API_KEY (or NEBIUS_API_KEY) is required")
    if not upstream_model:
        upstream_model = "openai/gpt-oss-120b"

    return Settings(
        relay_host=_env("STACKFIX_RELAY_HOST", "0.0.0.0"),
        relay_port=int(_env("STACKFIX_RELAY_PORT", "8000")),
        relay_secret=relay_secret,
        token_ttl_seconds=int(_env("STACKFIX_TOKEN_TTL_SECONDS", "86400")),
        rate_limit_per_day=int(_env("STACKFIX_RATE_LIMIT_PER_DAY", "500")),
        redis_url=_env("STACKFIX_REDIS_URL"),
        upstream_base_url=upstream_base_url,
        upstream_api_key=upstream_api_key,
        upstream_model=upstream_model,
    )
