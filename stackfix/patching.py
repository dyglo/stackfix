import os
import re
import subprocess
from typing import List, Tuple

from .safety import is_forbidden_path
from .util import is_git_repo


def _extract_paths_from_diff(diff_text: str) -> List[str]:
    paths = []
    for line in diff_text.splitlines():
        if line.startswith("+++ ") or line.startswith("--- "):
            path = line[4:].strip()
            if path.startswith("a/") or path.startswith("b/"):
                path = path[2:]
            if path == "/dev/null":
                continue
            paths.append(path)
    return paths


def _extract_paths_from_begin_patch(diff_text: str) -> List[str]:
    paths = []
    for line in diff_text.splitlines():
        if line.startswith("*** Update File: "):
            paths.append(line.replace("*** Update File: ", "").strip())
        if line.startswith("*** Add File: "):
            paths.append(line.replace("*** Add File: ", "").strip())
        if line.startswith("*** Delete File: "):
            paths.append(line.replace("*** Delete File: ", "").strip())
    return paths


def _is_begin_patch(diff_text: str) -> bool:
    for line in diff_text.splitlines():
        if line.strip():
            return line.startswith("*** Begin Patch")
    return False


def _is_valid_hunk_header(line: str) -> bool:
    return re.match(r"^@@ -\d+(,\d+)? \+\d+(,\d+)? @@", line) is not None


def _is_valid_unified_diff(diff_text: str) -> bool:
    if "diff --git " not in diff_text or "+++" not in diff_text or "---" not in diff_text:
        return False
    has_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("@@"):
            if not _is_valid_hunk_header(line):
                return False
            has_hunk = True
    return has_hunk


def validate_patch_paths(diff_text: str, cwd: str) -> List[str]:
    if _is_begin_patch(diff_text):
        paths = _extract_paths_from_begin_patch(diff_text)
    else:
        paths = _extract_paths_from_diff(diff_text)
    if not paths:
        raise RuntimeError("Patch contains no file paths")
    for rel in paths:
        abs_path = os.path.abspath(os.path.join(cwd, rel))
        if is_forbidden_path(abs_path, cwd):
            raise RuntimeError(f"Patch touches forbidden path: {rel}")
    return paths


def _parse_simple_blocks(diff_text: str) -> Tuple[List[str], List[str]]:
    old_lines: List[str] = []
    new_lines: List[str] = []
    in_hunk = False
    for line in diff_text.splitlines():
        if line.startswith("diff --git ") or line.startswith("--- ") or line.startswith("+++ "):
            in_hunk = True
            continue
        if line.startswith("*** Begin Patch") or line.startswith("*** End Patch"):
            in_hunk = True
            continue
        if line.startswith("*** Update File: ") or line.startswith("*** Add File: ") or line.startswith("*** Delete File: "):
            in_hunk = True
            continue
        if line.startswith("@@"):
            in_hunk = True
            continue
        if not in_hunk:
            continue
        if line.startswith("+") and not line.startswith("+++ "):
            new_lines.append(line[1:])
            continue
        if line.startswith("-") and not line.startswith("--- "):
            old_lines.append(line[1:])
            continue
        if line.startswith(" "):
            old_lines.append(line[1:])
            new_lines.append(line[1:])
            continue
    return old_lines, new_lines


def _apply_simple_replace(path: str, old_lines: List[str], new_lines: List[str]) -> None:
    if not old_lines and not new_lines:
        raise RuntimeError("Fallback patch has no changes to apply")
    old_block = "\n".join(old_lines)
    new_block = "\n".join(new_lines)
    with open(path, "r", encoding="utf-8", errors="replace") as f:
        content = f.read()
    count = content.count(old_block)
    if count != 1:
        raise RuntimeError("Fallback patch failed; old block not found exactly once")
    content = content.replace(old_block, new_block, 1)
    with open(path, "w", encoding="utf-8") as f:
        f.write(content)


def apply_patch(diff_text: str, cwd: str) -> None:
    paths = validate_patch_paths(diff_text, cwd)

    if _is_valid_unified_diff(diff_text):
        if is_git_repo(cwd):
            cmd = ["git", "apply", "--whitespace=nowarn", "-"]
        else:
            cmd = ["git", "apply", "--no-index", "--whitespace=nowarn", "-"]
        proc = subprocess.Popen(cmd, cwd=cwd, stdin=subprocess.PIPE, text=True)
        proc.communicate(diff_text)
        if proc.returncode == 0:
            return

    if len(paths) != 1:
        raise RuntimeError("Fallback patch only supports single-file edits")

    rel = paths[0]
    abs_path = os.path.abspath(os.path.join(cwd, rel))
    old_lines, new_lines = _parse_simple_blocks(diff_text)
    _apply_simple_replace(abs_path, old_lines, new_lines)
