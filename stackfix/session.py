import os
import json
from datetime import datetime
from typing import Dict, Any, Optional

SESSION_DIR = ".stackfix/sessions"


def _session_dir(cwd: str) -> str:
    path = os.path.join(cwd, SESSION_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def new_session_id() -> str:
    return datetime.utcnow().strftime("%Y%m%d_%H%M%S")


def save_session(cwd: str, session_id: str, state: Dict[str, Any]) -> str:
    path = os.path.join(_session_dir(cwd), f"{session_id}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
    return path


def load_session(cwd: str, session_id: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(_session_dir(cwd), f"{session_id}.json")
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)


def list_sessions(cwd: str) -> list:
    path = _session_dir(cwd)
    items = []
    for name in os.listdir(path):
        if name.endswith(".json"):
            items.append(name[:-5])
    return sorted(items)
