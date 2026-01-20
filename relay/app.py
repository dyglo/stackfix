"""FastAPI relay scaffold for StackFix (OpenAI-compatible)."""
from __future__ import annotations

import hashlib
import time
from typing import Any, Dict, Optional

from fastapi import FastAPI, Header, HTTPException, Request
from fastapi.responses import JSONResponse

from .auth import TokenStore
from .config import Settings, load_settings
from .rate_limit import RateLimiter

try:
    from openai import OpenAI
except Exception:  # pragma: no cover - optional dependency in dev
    OpenAI = None

app = FastAPI(title="StackFix Relay", version="0.1.0")

_SETTINGS: Optional[Settings] = None
_TOKEN_STORE: Optional[TokenStore] = None
_RATE_LIMITER: Optional[RateLimiter] = None


@app.get("/healthz")
def healthz() -> Dict[str, str]:
    return {"status": "ok"}


def _get_settings() -> Settings:
    global _SETTINGS
    if _SETTINGS is None:
        _SETTINGS = load_settings()
    return _SETTINGS


def _get_token_store() -> TokenStore:
    global _TOKEN_STORE
    if _TOKEN_STORE is None:
        _TOKEN_STORE = TokenStore(_get_settings())
    return _TOKEN_STORE


def _get_rate_limiter() -> RateLimiter:
    global _RATE_LIMITER
    if _RATE_LIMITER is None:
        _RATE_LIMITER = RateLimiter(_get_settings())
    return _RATE_LIMITER


def _reset_state_for_tests() -> None:
    global _SETTINGS, _TOKEN_STORE, _RATE_LIMITER
    _SETTINGS = None
    _TOKEN_STORE = None
    _RATE_LIMITER = None


def _hash_device(value: str) -> str:
    return hashlib.sha256(value.encode("utf-8")).hexdigest()


def _derive_device_id(req: Request, device_fingerprint: Optional[str]) -> str:
    if device_fingerprint:
        return _hash_device(device_fingerprint)
    ua = req.headers.get("user-agent", "unknown")
    ip = req.client.host if req.client else "unknown"
    return _hash_device(f"{ua}|{ip}")


@app.post("/v1/anon-token")
async def anon_token(
    request: Request,
    payload: Dict[str, Any],
) -> Dict[str, Any]:
    device_fingerprint = payload.get("device_fingerprint")
    device_id = _derive_device_id(request, device_fingerprint)
    store = _get_token_store()
    token, expires_at = store.issue_token(device_id)
    return {"token": token, "device_id": device_id, "expires_at": expires_at}


@app.get("/v1/models")
def list_models() -> Dict[str, Any]:
    settings = _get_settings()
    return {
        "object": "list",
        "data": [
            {
                "id": settings.upstream_model,
                "object": "model",
                "owned_by": "stackfix",
            }
        ],
    }


def _auth_bearer(authorization: Optional[str]) -> str:
    if not authorization:
        raise HTTPException(status_code=401, detail="Missing Authorization header")
    if not authorization.startswith("Bearer "):
        raise HTTPException(status_code=401, detail="Invalid Authorization header")
    return authorization.split(" ", 1)[1]


def _require_token(
    authorization: Optional[str],
    settings: Settings,
    limiter: RateLimiter,
) -> str:
    token = _auth_bearer(authorization)
    store = _get_token_store()
    device_id = store.verify_token(token)
    if not device_id:
        raise HTTPException(status_code=401, detail="Invalid or expired token")
    remaining, reset_at = limiter.check(device_id)
    return device_id, remaining, reset_at


@app.post("/v1/chat/completions")
async def chat_completions(
    request: Request,
    authorization: Optional[str] = Header(default=None),
) -> JSONResponse:
    settings = _get_settings()
    limiter = _get_rate_limiter()
    _, remaining, reset_at = _require_token(authorization, settings, limiter)

    if OpenAI is None:
        raise HTTPException(
            status_code=500,
            detail="openai SDK not installed; install relay extras",
        )

    payload = await request.json()
    if not isinstance(payload, dict):
        raise HTTPException(status_code=400, detail="Invalid JSON payload")

    if not payload.get("model"):
        payload["model"] = settings.upstream_model

    client = OpenAI(base_url=settings.upstream_base_url, api_key=settings.upstream_api_key)
    try:
        resp = client.chat.completions.create(**payload)
    except Exception as exc:
        raise HTTPException(status_code=502, detail=f"Upstream error: {exc}") from exc

    data = resp.model_dump() if hasattr(resp, "model_dump") else resp
    headers = {
        "X-RateLimit-Remaining": str(remaining),
        "X-RateLimit-Reset": str(reset_at),
    }
    return JSONResponse(content=data, headers=headers)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "relay.app:app",
        host=load_settings().relay_host,
        port=load_settings().relay_port,
        reload=False,
    )
