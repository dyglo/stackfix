import os
import subprocess
from typing import Dict

from .util import truncate_text, is_git_repo
from .safety import is_forbidden_path
from .agents import load_agents_instructions

MAX_STDIO_CHARS = 20000
MAX_GIT_CHARS = 20000
MAX_FILE_CHARS = 12000
MAX_FILE_BYTES = 200000

MANIFESTS = [
    "package.json",
    "pnpm-lock.yaml",
    "yarn.lock",
    "pyproject.toml",
    "requirements.txt",
    "poetry.lock",
]


def _read_file(path: str) -> str:
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        return f.read()


def collect_context(cwd: str, command: list, exit_code: int, stdout: str, stderr: str) -> Dict:
    ctx = {
        "command": command,
        "cwd": cwd,
        "exit_code": exit_code,
        "stdout": truncate_text(stdout, MAX_STDIO_CHARS),
        "stderr": truncate_text(stderr, MAX_STDIO_CHARS),
    }

    agents = load_agents_instructions(cwd)
    if agents:
        ctx["agent_instructions"] = truncate_text(agents, MAX_FILE_CHARS)

    if is_git_repo(cwd):
        try:
            status = subprocess.check_output(["git", "status", "--porcelain"], cwd=cwd, text=True)
        except Exception:
            status = ""
        try:
            diff = subprocess.check_output(["git", "diff"], cwd=cwd, text=True)
        except Exception:
            diff = ""
        ctx["git_status"] = truncate_text(status, MAX_GIT_CHARS)
        ctx["git_diff"] = truncate_text(diff, MAX_GIT_CHARS)

    files = {}
    for name in MANIFESTS:
        path = os.path.join(cwd, name)
        if not os.path.isfile(path):
            continue
        if is_forbidden_path(path, cwd):
            continue
        size = os.path.getsize(path)
        if size > MAX_FILE_BYTES:
            continue
        try:
            content = _read_file(path)
        except Exception:
            continue
        files[name] = truncate_text(content, MAX_FILE_CHARS)

    if files:
        ctx["manifests"] = files

    return ctx
