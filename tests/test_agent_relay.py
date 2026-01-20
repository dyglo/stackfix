import json as jsonlib
from typing import Any

import pytest

import stackfix.agent as agent


class _FakeResponse:
    def __init__(self, payload: dict) -> None:
        self._payload = payload
        self.status_code = payload.get("status_code", 200)
        self.text = jsonlib.dumps(payload.get("body", {}))

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RuntimeError(f"HTTP {self.status_code}")

    def json(self) -> dict:
        return self._payload.get("body", {})


class _FakeRequests:
    def __init__(self) -> None:
        self.calls = []

    def post(self, url: str, json: Any = None, headers: Any = None, timeout: int = 60):
        self.calls.append((url, json, headers))
        if url.endswith("/anon-token"):
            return _FakeResponse({"body": {"token": "tok", "expires_at": 9999999999}})
        if url.endswith("/chat/completions"):
            return _FakeResponse(
                {
                    "body": {
                        "choices": [
                            {
                                "message": {
                                    "content": jsonlib.dumps(
                                        {
                                            "summary": "ok",
                                            "confidence": 1,
                                            "patch_unified_diff": "",
                                            "rerun_command": [],
                                        }
                                    )
                                }
                            }
                        ]
                    }
                }
            )
        return _FakeResponse({"status_code": 404, "body": {}})


def test_relay_default_path(monkeypatch: pytest.MonkeyPatch, temp_cwd) -> None:
    fake = _FakeRequests()
    monkeypatch.setattr(agent, "requests", fake)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.setenv("STACKFIX_PROVIDER", "stackfix")
    monkeypatch.setenv("STACKFIX_RELAY_URL", "https://api.stackfix.ai/v1")

    context = {"mode": "prompt", "prompt": "hello", "cwd": str(temp_cwd)}
    result = agent.call_agent(context)
    assert result.get("summary") == "ok"
    assert any(call[0].endswith("/anon-token") for call in fake.calls)
    assert any(call[0].endswith("/chat/completions") for call in fake.calls)
