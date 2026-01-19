import os
from typing import Optional

MAX_AGENT_BYTES = 12000


def find_agents_file(cwd: str) -> Optional[str]:
    current = os.path.abspath(cwd)
    root = os.path.abspath(os.sep)
    while True:
        candidate = os.path.join(current, "AGENTS.md")
        if os.path.isfile(candidate):
            return candidate
        if current == root:
            return None
        current = os.path.dirname(current)


def load_agents_instructions(cwd: str) -> Optional[str]:
    path = find_agents_file(cwd)
    if not path:
        return None
    try:
        if os.path.getsize(path) > MAX_AGENT_BYTES:
            return None
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            return f.read()
    except Exception:
        return None
