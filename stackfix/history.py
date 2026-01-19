import json
import os
from datetime import datetime
from typing import Dict, Any, Optional

HISTORY_DIR = ".stackfix/history"
LAST_FILE = os.path.join(HISTORY_DIR, "last.json")


def ensure_history_dir(cwd: str) -> str:
    path = os.path.join(cwd, HISTORY_DIR)
    os.makedirs(path, exist_ok=True)
    return path


def write_history(cwd: str, record: Dict[str, Any]) -> str:
    history_dir = ensure_history_dir(cwd)
    ts = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
    path = os.path.join(history_dir, f"{ts}.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    with open(os.path.join(cwd, LAST_FILE), "w", encoding="utf-8") as f:
        json.dump(record, f, indent=2)
    return path


def read_last(cwd: str) -> Optional[Dict[str, Any]]:
    path = os.path.join(cwd, LAST_FILE)
    if not os.path.isfile(path):
        return None
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)
