import json
from typing import Any, Dict

import pytest

try:
    from fastapi.testclient import TestClient
except Exception:  # pragma: no cover - optional dependency
    TestClient = None

import relay.app as relay_app

pytestmark = pytest.mark.skipif(TestClient is None, reason="fastapi not installed")


class _FakeResp:
    def __init__(self, payload: Dict[str, Any]) -> None:
        self._payload = payload

    def model_dump(self) -> Dict[str, Any]:
        return self._payload


class _FakeOpenAI:
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        self.chat = self
        self.completions = self

    def create(self, **payload: Any) -> _FakeResp:
        return _FakeResp({"choices": [{"message": {"content": json.dumps({"ok": True})}}]})


@pytest.fixture(autouse=True)
def _relay_env(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STACKFIX_ENV", "test")
    monkeypatch.setenv("STACKFIX_RELAY_SECRET", "test-secret")
    monkeypatch.setenv("STACKFIX_UPSTREAM_BASE_URL", "http://example.com/v1")
    monkeypatch.setenv("STACKFIX_UPSTREAM_API_KEY", "test")
    monkeypatch.setenv("STACKFIX_UPSTREAM_MODEL", "stackfix-test")
    monkeypatch.delenv("STACKFIX_REDIS_URL", raising=False)
    relay_app._reset_state_for_tests()


def _client(monkeypatch: pytest.MonkeyPatch) -> TestClient:
    monkeypatch.setattr(relay_app, "OpenAI", _FakeOpenAI)
    relay_app._reset_state_for_tests()
    return TestClient(relay_app.app)


def test_anon_token_and_chat(monkeypatch: pytest.MonkeyPatch) -> None:
    client = _client(monkeypatch)
    resp = client.post("/v1/anon-token", json={"device_fingerprint": "abc"})
    assert resp.status_code == 200
    token = resp.json().get("token")
    assert token

    payload = {"model": "stackfix-test", "messages": [{"role": "user", "content": "hi"}]}
    chat = client.post(
        "/v1/chat/completions",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert chat.status_code == 200
    assert "choices" in chat.json()
    assert "X-RateLimit-Remaining" in chat.headers


def test_rate_limit(monkeypatch: pytest.MonkeyPatch) -> None:
    monkeypatch.setenv("STACKFIX_RATE_LIMIT_PER_DAY", "1")
    client = _client(monkeypatch)
    resp = client.post("/v1/anon-token", json={"device_fingerprint": "abc"})
    token = resp.json().get("token")

    payload = {"model": "stackfix-test", "messages": [{"role": "user", "content": "hi"}]}
    ok = client.post(
        "/v1/chat/completions",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert ok.status_code == 200

    blocked = client.post(
        "/v1/chat/completions",
        json=payload,
        headers={"Authorization": f"Bearer {token}"},
    )
    assert blocked.status_code == 429
