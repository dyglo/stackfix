import json
import os
import shlex
import subprocess
import threading
from typing import List, Optional

from textual.app import App, ComposeResult
from textual.containers import Horizontal, Vertical, VerticalScroll
from textual.widgets import Input, RichLog, Static

from .agent import call_agent
from .context import collect_context
from .history import read_last, write_history
from .session import new_session_id, save_session, load_session, list_sessions
from .agents import load_agents_instructions
from .patching import apply_patch


# Slash command definitions for /help
SLASH_COMMANDS = [
    ("/exit", "Exit the TUI"),
    ("/clear", "Clear the log panel"),
    ("/model <name>", "View or switch the model"),
    ("/approvals <mode>", "Set approval mode (suggest, auto-edit, full-auto)"),
    ("/status", "Show current configuration"),
    ("/history", "Show last run summary and patch"),
    ("/plan", "Show current execution plan"),
    ("/diff", "Show pending git changes"),
    ("/help", "Show this help message"),
    ("/skills", "List available skills"),
    ("/compact", "Summarize session (stub)"),
    ("/new", "Start a new session"),
    ("/resume <id>", "Resume a saved session"),
    ("/sessions", "List saved sessions"),
]


def _highlight_diff(diff_text: str) -> str:
    """Apply syntax highlighting to a unified diff."""
    lines = []
    for line in diff_text.split("\n"):
        if line.startswith("+++ ") or line.startswith("--- "):
            lines.append(f"[bold cyan]{line}[/bold cyan]")
        elif line.startswith("@@"):
            lines.append(f"[magenta]{line}[/magenta]")
        elif line.startswith("+"):
            lines.append(f"[green]{line}[/green]")
        elif line.startswith("-"):
            lines.append(f"[red]{line}[/red]")
        elif line.startswith("diff --git"):
            lines.append(f"[bold blue]{line}[/bold blue]")
        else:
            lines.append(f"[dim]{line}[/dim]")
    return "\n".join(lines)


class StackFixTUI(App):
    CSS = """
    Screen {
        background: #000000;
        color: #e6e6e6;
    }

    VerticalScroll {
        padding: 0 4;
    }

    RichLog {
        background: #000000;
        color: #e6e6e6;
        border: none;
        height: auto;
        min-height: 1;
        max-height: 100%;
        padding: 0;
    }

    #splash {
        padding: 1 0 0 0;
        height: auto;
    }

    #tip {
        color: #e6e6e6;
        padding: 1 0 1 0;
        height: auto;
    }

    #prompt-row {
        height: 1;
        margin: 1 0 0 0;
    }

    #prompt-label {
        width: 2;
        color: #e6e6e6;
    }

    #prompt-input {
        border: none;
        background: transparent;
        color: #e6e6e6;
        padding: 0;
        height: 1;
    }

    #prompt-input:focus {
        border: none;
    }

    #status-line {
        color: #6b7280;
        padding: 0 0 1 0;
    }

    .accent {
        color: #3b82f6;
    }

    .dim {
        color: #6b7280;
    }

    .bold {
        text-style: bold;
    }

    .phase {
        color: #94a3b8;
    }
    """

    BINDINGS = [
        ("ctrl+c", "quit", "Quit"),
        ("ctrl+l", "clear", "Clear"),
    ]

    def __init__(self) -> None:
        super().__init__()
        self._log: Optional[RichLog] = None
        self._awaiting_confirm = False
        self._pending_cmd: Optional[List[str]] = None
        self._pending_agent = None
        self._last_plan: List[str] = []
        self._splash: Optional[Static] = None
        self._tip: Optional[Static] = None
        self._session_id = new_session_id()
        self._approvals_mode = "suggest"
        self._last_prompt: Optional[str] = None
        self._current_phase: str = "Ready"

    def compose(self) -> ComposeResult:
        with VerticalScroll():
            self._splash = Static(self._render_splash(), id="splash", markup=True)
            yield self._splash
            self._tip = Static(self._render_tip(), id="tip", markup=True)
            yield self._tip
            self._log = RichLog(highlight=False, wrap=True)
            yield self._log
            with Horizontal(id="prompt-row"):
                yield Static(">", id="prompt-label")
                yield Input(placeholder="Type a prompt, !cmd, or /command", id="prompt-input")
            self._status_bar = Static(self._render_status(), id="status-line", markup=True)
            yield self._status_bar

    def on_mount(self) -> None:
        self.query_one(Input).focus()

    def _render_splash(self) -> str:
        cwd = os.getcwd()
        if cwd == os.path.expanduser("~"):
            cwd = "~"
        model = os.environ.get("MODEL_NAME") or os.environ.get("STACKFIX_MODEL") or "stackfix-default"
        version = "v0.2.0"

        lines = [
            f"> StackFix ({version})",
            f"model: {model}",
            f"directory: {cwd}",
        ]
        width = max(len(line) for line in lines) + 2
        top = "+" + "-" * width + "+"
        body = "\n".join(f"| {line.ljust(width - 1)}|" for line in lines)
        bottom = "+" + "-" * width + "+"
        return f"\n{top}\n{body}\n{bottom}\n"

    def _render_tip(self) -> str:
        return "[bold]Tip:[/bold] Use [bold]/help[/bold] for commands or [bold]/skills[/bold] to list skills."

    def _render_status(self) -> str:
        phase_style = "[bold cyan]" if self._current_phase != "Ready" else "[dim]"
        return f" {phase_style}* {self._current_phase}[/]  -  [dim]100% context left[/dim]  -  [dim]? for shortcuts[/dim]"

    def action_clear(self) -> None:
        if self._log:
            self._log.clear()

    def _log_line(self, text: str) -> None:
        if self._log:
            self._log.write(text)

    def _phase(self, name: str) -> None:
        self._current_phase = name
        if hasattr(self, "_status_bar") and self._status_bar:
            self._status_bar.update(self._render_status())

    def _agent_error_hint(self, exc: Exception) -> Optional[str]:
        message = str(exc)
        if "Relay token request failed" in message or "Relay unreachable" in message:
            return "Hint: set STACKFIX_RELAY_URL=http://localhost:8000/v1 if your relay is local."
        return None

    def _set_plan(self, steps: List[str]) -> None:
        self._last_plan = steps

    def _show_plan(self) -> None:
        if not self._last_plan:
            self._log_line("[dim]No plan available.[/dim]")
            return
        self._log_line("[bold]Current plan:[/bold]")
        for step in self._last_plan:
            self._log_line(f" [dim]- {step}[/dim]")

    def _show_history(self) -> None:
        last = read_last(os.getcwd())
        if not last:
            self._log_line("No history found.")
            return
        self._log_line("Last run summary:")
        self._log_line(last.get("summary", ""))
        patch = last.get("patch", "")
        if patch:
            self._log_line("\nPatch:")
            self._log_line(patch)

    def _show_status(self) -> None:
        cwd = os.getcwd()
        model = os.environ.get("MODEL_NAME") or os.environ.get("STACKFIX_MODEL") or "unset"
        provider = os.environ.get("STACKFIX_PROVIDER", "auto")
        relay_url = os.environ.get("STACKFIX_RELAY_URL", "default")
        endpoint = os.environ.get("STACKFIX_ENDPOINT", "direct")
        self._log_line(f"cwd: {cwd}")
        self._log_line(f"model: {model}")
        self._log_line(f"provider: {provider}")
        self._log_line(f"relay_url: {relay_url}")
        self._log_line(f"endpoint: {endpoint}")
        self._log_line(f"approvals: {self._approvals_mode}")
        self._log_line(f"session: {self._session_id}")

    def _show_sessions(self) -> None:
        sessions = list_sessions(os.getcwd())
        if not sessions:
            self._log_line("No saved sessions.")
            return
        self._log_line("Sessions:")
        for sid in sessions[-10:]:
            self._log_line(f"- {sid}")

    def _show_diff(self) -> None:
        """Show pending git changes."""
        cwd = os.getcwd()
        try:
            result = subprocess.run(
                ["git", "diff", "HEAD"],
                cwd=cwd,
                capture_output=True,
                text=True,
                timeout=10,
            )
            diff = result.stdout.strip()
            if not diff:
                self._log_line("[dim]No pending changes.[/dim]")
                return
            self._log_line("[bold]Pending changes:[/bold]")
            self._log_line(_highlight_diff(diff))
        except FileNotFoundError:
            self._log_line("[red]git not found. /diff requires git.[/red]")
        except subprocess.TimeoutExpired:
            self._log_line("[red]git diff timed out.[/red]")
        except Exception as exc:
            self._log_line(f"[red]Error: {exc}[/red]")

    def _show_help(self) -> None:
        """Show available slash commands."""
        self._log_line("[bold]Available commands:[/bold]")
        for cmd, desc in SLASH_COMMANDS:
            self._log_line(f"  [accent]{cmd:<20}[/accent] {desc}")

    def on_input_submitted(self, event: Input.Submitted) -> None:
        text = event.value.strip()
        event.input.value = ""
        if not text:
            return

        if self._awaiting_confirm:
            self._handle_confirm(text)
            return

        if text.startswith("/"):
            self._handle_slash_command(text)
            return

        if text.startswith("!"):
            cmd = shlex.split(text[1:].strip())
            if not cmd:
                self._log_line("No command provided.")
                return
            self._run_command(cmd)
            return

        self._last_prompt = text
        self._run_prompt(text)

    def _handle_slash_command(self, text: str) -> None:
        raw = text.strip()
        cmd = raw.lower()
        if cmd == "/exit":
            self.exit()
            return
        if cmd == "/clear":
            self.action_clear()
            return
        if cmd == "/plan":
            self._show_plan()
            return
        if cmd == "/history":
            self._show_history()
            return
        if cmd == "/status":
            self._show_status()
            return
        if cmd.startswith("/model"):
            parts = raw.split(maxsplit=1)
            if len(parts) == 2:
                os.environ["MODEL_NAME"] = parts[1].strip()
                if self._splash:
                    self._splash.update(self._render_splash())
                self._log_line(f"Model set to {parts[1].strip()}")
            else:
                self._log_line(f"Current model: {os.environ.get('MODEL_NAME', 'unset')}")
            return
        if cmd.startswith("/approvals"):
            parts = raw.split(maxsplit=1)
            if len(parts) == 2:
                mode = parts[1].strip().lower()
                if mode not in ["suggest", "auto-edit", "full-auto"]:
                    self._log_line("Approvals mode must be: suggest | auto-edit | full-auto")
                else:
                    self._approvals_mode = mode
                    self._log_line(f"Approvals mode set to {mode}")
            else:
                self._log_line(f"Approvals mode: {self._approvals_mode}")
            return
        if cmd == "/skills":
            self._log_line("Skills: review (stub), compact (stub), mcp (stub)")
            return
        if cmd == "/compact":
            self._log_line("Compact: not implemented yet.")
            return
        if cmd == "/new":
            self._session_id = new_session_id()
            self._log_line(f"New session: {self._session_id}")
            return
        if cmd.startswith("/resume"):
            parts = raw.split(maxsplit=1)
            if len(parts) != 2:
                self._show_sessions()
                return
            sid = parts[1].strip()
            session = load_session(os.getcwd(), sid)
            if not session:
                self._log_line(f"Session not found: {sid}")
                return
            self._session_id = sid
            self._log_line(f"Resumed session: {sid}")
            return
        if cmd == "/sessions":
            self._show_sessions()
            return
        if cmd == "/diff":
            self._show_diff()
            return
        if cmd == "/help" or cmd == "/?":
            self._show_help()
            return
        self._log_line(f"Unknown command: {cmd}. Type /help for available commands.")

    def _handle_confirm(self, text: str) -> None:
        self._awaiting_confirm = False
        if text.strip().lower() != "y":
            self._log_line("Patch not applied.")
            record = {
                "command": self._pending_cmd,
                "exit_code": 1,
                "summary": self._pending_agent.get("summary", "") if self._pending_agent else "",
                "patch": self._pending_agent.get("patch_unified_diff", "") if self._pending_agent else "",
                "rerun_exit_code": None,
                "applied": False,
            }
            write_history(os.getcwd(), record)
            self._pending_cmd = None
            self._pending_agent = None
            return

        self._phase("Validation / Summary")
        self._log_line("Applying patch...")
        self.run_worker(self._apply_and_rerun, thread=True)

    def _run_command(self, cmd: List[str]) -> None:
        self._phase("Planning")
        self._log_line(f"[bold cyan]> {shlex.join(cmd)}[/bold cyan]")
        self._set_plan([
            "Run command",
            "Collect context",
            "Propose fix",
            "Validate outcome",
        ])
        self.run_worker(lambda: self._command_flow(cmd), thread=True)

    def _run_prompt(self, prompt: str) -> None:
        self._phase("Planning")
        self._log_line(f"[bold cyan]> {prompt}[/bold cyan]")
        self._set_plan(["Answer prompt", "Summarize response"])
        self.run_worker(lambda: self._prompt_flow(prompt), thread=True)

    def _command_flow(self, cmd: List[str]) -> None:
        cwd = os.getcwd()
        stdout_chunks: List[str] = []
        stderr_chunks: List[str] = []

        def _stream(pipe, sink, is_err: bool) -> None:
            for line in iter(pipe.readline, ""):
                sink.append(line)
                prefix = "stderr" if is_err else "stdout"
                self.call_from_thread(self._log_line, f"[{prefix}] {line.rstrip()}" if line.strip() else "")
            pipe.close()

        proc = subprocess.Popen(
            cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
            bufsize=1,
            universal_newlines=True,
        )
        t_out = threading.Thread(target=_stream, args=(proc.stdout, stdout_chunks, False))
        t_err = threading.Thread(target=_stream, args=(proc.stderr, stderr_chunks, True))
        t_out.start()
        t_err.start()
        proc.wait()
        t_out.join()
        t_err.join()

        exit_code = proc.returncode
        stdout = "".join(stdout_chunks)
        stderr = "".join(stderr_chunks)

        if exit_code == 0:
            record = {
                "command": cmd,
                "exit_code": exit_code,
                "summary": "Command succeeded; no patch applied.",
                "patch": "",
                "rerun_exit_code": None,
            }
            write_history(cwd, record)
            write_history(cwd, record)
            self.call_from_thread(self._phase, "Ready")
            self.call_from_thread(self._log_line, "[green]Command succeeded.[/green]")
            return

        self.call_from_thread(self._phase, "Exploring")
        context = collect_context(cwd, cmd, exit_code, stdout, stderr)
        agents = load_agents_instructions(cwd)
        if agents:
            context["agent_instructions"] = agents

        try:
            agent_result = call_agent(context)
        except Exception as exc:
            self.call_from_thread(self._log_line, f"Agent call failed: {exc}")
            hint = self._agent_error_hint(exc)
            if hint:
                self.call_from_thread(self._log_line, f"[dim]{hint}[/dim]")
            return

        warning = agent_result.get("_warning")
        if warning:
            self.call_from_thread(self._log_line, f"Warning: {warning}")

        self._pending_cmd = cmd
        self._pending_agent = agent_result

        summary = agent_result.get("summary", "")
        patch = agent_result.get("patch_unified_diff", "")

        self.call_from_thread(self._phase, "Review")
        self.call_from_thread(self._log_line, f"\n{summary}")
        
        if patch:
            self.call_from_thread(self._log_line, "\n[bold]Patch preview[/bold]\n")
            highlighted = _highlight_diff(patch)
            self.call_from_thread(self._log_line, highlighted)
        else:
            self.call_from_thread(self._log_line, "\n[dim]No patch provided by agent.[/dim]")
            return

        if self._approvals_mode == "full-auto":
            self._phase("Validation / Summary")
            self._log_line("Auto-apply enabled; applying patch...")
            self.run_worker(self._apply_and_rerun, thread=True)
        else:
            self.call_from_thread(self._log_line, "\nApply patch? [y/N]")
            self._awaiting_confirm = True

    def _apply_and_rerun(self) -> None:
        cwd = os.getcwd()
        agent = self._pending_agent or {}
        cmd = self._pending_cmd or []
        patch = agent.get("patch_unified_diff", "")
        summary = agent.get("summary", "")

        try:
            apply_patch(patch, cwd)
        except Exception as exc:
            self.call_from_thread(self._log_line, f"Failed to apply patch: {exc}")
            return

        rerun_cmd = agent.get("rerun_command") or cmd
        self.call_from_thread(self._log_line, "Rerunning command...")
        proc = subprocess.Popen(
            rerun_cmd,
            cwd=cwd,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True,
        )
        out, err = proc.communicate()
        rerun_exit = proc.returncode

        record = {
            "command": cmd,
            "exit_code": 1,
            "summary": summary,
            "patch": patch,
            "rerun_command": rerun_cmd,
            "rerun_exit_code": rerun_exit,
            "rerun_stdout": out,
            "rerun_stderr": err,
            "applied": True,
        }
        write_history(cwd, record)
        
        self.call_from_thread(self._phase, "Validation / Summary")
        self.call_from_thread(self._log_line, f"Rerun exit code: [bold]{rerun_exit}[/bold]")
        if out:
            self.call_from_thread(self._log_line, f"\n[bold]Output[/bold]\n{out.strip()}")
        if err:
            self.call_from_thread(self._log_line, f"\n[bold]Errors[/bold]\n{err.strip()}")

        self.call_from_thread(self._phase, "Ready")

        self._pending_cmd = None
        self._pending_agent = None
        state = {
            "session_id": self._session_id,
            "last_prompt": self._last_prompt,
            "last_command": cmd,
            "approvals_mode": self._approvals_mode,
        }
        save_session(cwd, self._session_id, state)

    def _prompt_flow(self, prompt: str) -> None:
        cwd = os.getcwd()
        context = {
            "mode": "prompt",
            "prompt": prompt,
            "cwd": cwd,
        }
        agents = load_agents_instructions(cwd)
        if agents:
            context["agent_instructions"] = agents
        try:
            agent_result = call_agent(context)
        except Exception as exc:
            self.call_from_thread(self._log_line, f"Agent call failed: {exc}")
            hint = self._agent_error_hint(exc)
            if hint:
                self.call_from_thread(self._log_line, f"[dim]{hint}[/dim]")
            return
        warning = agent_result.get("_warning")
        if warning:
            self.call_from_thread(self._log_line, f"Warning: {warning}")
        summary = agent_result.get("summary", "")
        if not summary:
            summary = agent_result.get("_raw_content", "")
        self.call_from_thread(self._phase, "Ready")
        self.call_from_thread(self._log_line, summary)
        state = {
            "session_id": self._session_id,
            "last_prompt": prompt,
            "approvals_mode": self._approvals_mode,
        }
        save_session(cwd, self._session_id, state)


def run_tui() -> None:
    app = StackFixTUI()
    app.run()
