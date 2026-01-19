import os
import re
from typing import Iterable

DENYLIST_NAMES = {
    ".env",
    ".env.local",
    ".env.development",
    ".env.production",
    ".env.test",
}

DENYLIST_PATTERNS = [
    re.compile(r".*\.key$", re.IGNORECASE),
    re.compile(r".*\.pem$", re.IGNORECASE),
    re.compile(r".*\.p12$", re.IGNORECASE),
    re.compile(r".*\.pfx$", re.IGNORECASE),
    re.compile(r".*\.crt$", re.IGNORECASE),
    re.compile(r".*\.cer$", re.IGNORECASE),
    re.compile(r".*id_rsa$", re.IGNORECASE),
    re.compile(r".*id_ed25519$", re.IGNORECASE),
]

DENYLIST_DIRS = {
    ".git",
    "node_modules",
    "dist",
    "build",
    "__pycache__",
    ".venv",
    ".env",
    ".ssh",
    ".gnupg",
}


def is_forbidden_path(path: str, cwd: str) -> bool:
    abs_path = os.path.abspath(path)
    cwd_abs = os.path.abspath(cwd)
    if not abs_path.startswith(cwd_abs):
        return True

    parts = os.path.relpath(abs_path, cwd_abs).split(os.sep)
    for part in parts:
        if part in DENYLIST_DIRS:
            return True

    name = os.path.basename(abs_path)
    if name in DENYLIST_NAMES:
        return True

    for pat in DENYLIST_PATTERNS:
        if pat.match(name):
            return True

    return False


def filter_allowed_paths(paths: Iterable[str], cwd: str) -> list:
    return [p for p in paths if not is_forbidden_path(p, cwd)]
