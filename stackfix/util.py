import os
import subprocess
import threading
import sys
from typing import Tuple, List


def is_git_repo(cwd: str) -> bool:
    return os.path.isdir(os.path.join(cwd, ".git"))


def run_command_stream(cmd: List[str], cwd: str) -> Tuple[int, str, str]:
    proc = subprocess.Popen(
        cmd,
        cwd=cwd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        text=True,
        bufsize=1,
        universal_newlines=True,
    )

    stdout_chunks = []
    stderr_chunks = []

    def _pump(stream, sink, out_stream):
        for line in iter(stream.readline, ""):
            sink.append(line)
            out_stream.write(line)
            out_stream.flush()
        stream.close()

    t_out = threading.Thread(target=_pump, args=(proc.stdout, stdout_chunks, sys.stdout))
    t_err = threading.Thread(target=_pump, args=(proc.stderr, stderr_chunks, sys.stderr))
    t_out.start()
    t_err.start()
    proc.wait()
    t_out.join()
    t_err.join()

    return proc.returncode, "".join(stdout_chunks), "".join(stderr_chunks)


def truncate_text(text: str, max_chars: int) -> str:
    if len(text) <= max_chars:
        return text
    return text[:max_chars] + f"\n... [truncated to {max_chars} chars]\n"


def env_required(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise RuntimeError(f"Missing required env var: {name}")
    return value
