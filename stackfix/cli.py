import argparse
import json
import os
import sys
from typing import List

from .agent import call_agent
from .context import collect_context
from .history import write_history, read_last
from .patching import apply_patch
from .util import run_command_stream
from .agents import load_agents_instructions
from .tui import run_tui


def _print_last(cwd: str) -> int:
    last = read_last(cwd)
    if not last:
        print("No history found.")
        return 1
    print("Last run summary:")
    print(last.get("summary", ""))
    print("\nPatch:")
    print(last.get("patch", ""))
    return 0


def _normalize_command(cmd: List[str]) -> List[str]:
    if cmd and cmd[0] == "--":
        return cmd[1:]
    return cmd


def main() -> None:
    parser = argparse.ArgumentParser(description="StackFix command wrapper")
    parser.add_argument("--last", action="store_true", help="Show last run summary and patch")
    parser.add_argument("--prompt", type=str, help="Run a single prompt non-interactively")
    parser.add_argument("command", nargs=argparse.REMAINDER, help="Command to run after --")
    args = parser.parse_args()

    cwd = os.getcwd()

    if args.last:
        sys.exit(_print_last(cwd))

    if args.prompt:
        context = {
            "mode": "prompt",
            "prompt": args.prompt,
            "cwd": cwd,
        }
        agents = load_agents_instructions(cwd)
        if agents:
            context["agent_instructions"] = agents
        try:
            agent_result = call_agent(context)
        except Exception as exc:
            print(f"Agent call failed: {exc}", file=sys.stderr)
            sys.exit(1)
        summary = agent_result.get("summary", "")
        warning = agent_result.get("_warning")
        if warning:
            print(f"Warning: {warning}", file=sys.stderr)
        print(summary)
        record = {
            "command": None,
            "exit_code": 0,
            "summary": summary,
            "patch": agent_result.get("patch_unified_diff", ""),
            "rerun_exit_code": None,
        }
        write_history(cwd, record)
        sys.exit(0)

    cmd = _normalize_command(args.command)
    if not cmd:
        run_tui()
        return

    exit_code, stdout, stderr = run_command_stream(cmd, cwd)

    if exit_code == 0:
        record = {
            "command": cmd,
            "exit_code": exit_code,
            "summary": "Command succeeded; no patch applied.",
            "patch": "",
            "rerun_exit_code": None,
        }
        write_history(cwd, record)
        sys.exit(exit_code)

    context = collect_context(cwd, cmd, exit_code, stdout, stderr)

    try:
        agent_result = call_agent(context)
    except Exception as exc:
        print(f"Agent call failed: {exc}", file=sys.stderr)
        sys.exit(exit_code)

    warning = agent_result.get("_warning")
    if warning:
        print(f"Warning: {warning}", file=sys.stderr)

    patch = agent_result.get("patch_unified_diff", "")
    summary = agent_result.get("summary", "")

    print("\nProposed fix:")
    print(summary)
    print("\nPatch preview:\n")
    print(patch)

    if not patch.strip():
        record = {
            "command": cmd,
            "exit_code": exit_code,
            "summary": summary,
            "patch": patch,
            "rerun_exit_code": None,
            "applied": False,
        }
        write_history(cwd, record)
        print("No patch provided by agent.")
        sys.exit(exit_code)

    confirm = input("Apply patch? [y/N]: ").strip().lower()
    if confirm != "y":
        record = {
            "command": cmd,
            "exit_code": exit_code,
            "summary": summary,
            "patch": patch,
            "rerun_exit_code": None,
            "applied": False,
        }
        write_history(cwd, record)
        print("Patch not applied.")
        sys.exit(exit_code)

    try:
        apply_patch(patch, cwd)
    except Exception as exc:
        print(f"Failed to apply patch: {exc}", file=sys.stderr)
        sys.exit(exit_code)

    rerun_cmd = agent_result.get("rerun_command") or cmd
    print("\nRerunning command...")
    rerun_exit, rerun_stdout, rerun_stderr = run_command_stream(rerun_cmd, cwd)

    record = {
        "command": cmd,
        "exit_code": exit_code,
        "summary": summary,
        "patch": patch,
        "rerun_command": rerun_cmd,
        "rerun_exit_code": rerun_exit,
        "rerun_stdout": rerun_stdout,
        "rerun_stderr": rerun_stderr,
        "applied": True,
    }
    write_history(cwd, record)

    print("\nRun summary:")
    print(json.dumps({"before": exit_code, "after": rerun_exit}, indent=2))
    sys.exit(rerun_exit)


if __name__ == "__main__":
    main()
