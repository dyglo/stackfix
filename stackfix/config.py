import json
import os
import time
import uuid
from typing import Any, Dict

CONFIG_DIR = ".stackfix"
CONFIG_FILE = "config.json"


def _config_path(cwd: str) -> str:
    os.makedirs(os.path.join(cwd, CONFIG_DIR), exist_ok=True)
    return os.path.join(cwd, CONFIG_DIR, CONFIG_FILE)


def load_config(cwd: str) -> Dict[str, Any]:
    path = _config_path(cwd)
    if not os.path.isfile(path):
        return {}
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_config(cwd: str, data: Dict[str, Any]) -> None:
    path = _config_path(cwd)
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


def get_or_create_device_fingerprint(cwd: str) -> str:
    cfg = load_config(cwd)
    relay = cfg.get("relay", {})
    fingerprint = relay.get("device_fingerprint")
    if fingerprint:
        return fingerprint
    fingerprint = str(uuid.uuid4())
    relay["device_fingerprint"] = fingerprint
    cfg["relay"] = relay
    save_config(cwd, cfg)
    return fingerprint


def get_relay_token(cwd: str) -> Dict[str, Any]:
    cfg = load_config(cwd)
    relay = cfg.get("relay", {})
    return {
        "token": relay.get("token"),
        "expires_at": relay.get("expires_at"),
    }


def set_relay_token(cwd: str, token: str, expires_at: int) -> None:
    cfg = load_config(cwd)
    relay = cfg.get("relay", {})
    relay["token"] = token
    relay["expires_at"] = expires_at
    cfg["relay"] = relay
    save_config(cwd, cfg)


def is_token_valid(expires_at: Any, skew_seconds: int = 60) -> bool:
    try:
        expires_at_int = int(expires_at)
    except Exception:
        return False
    return time.time() + skew_seconds < expires_at_int