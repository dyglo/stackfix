# StackFix plan

## Architecture
- CLI entrypoint (Python) that wraps a user command, streams output live, and preserves exit codes.
- Context collector with strict safety denylist and size limits (stdout/stderr, git status/diff, key manifests).
- Agent client for OpenAI-compatible API (direct provider now; Modal endpoint later via STACKFIX_ENDPOINT).
- Patch validator and applier (git apply in repo, git apply --no-index otherwise), with human approval gate.
- History store in .stackfix/history/ for run records; --last reads last run summary + patch.

## TUI (CLI Interface v1)
- UI architecture: Textual-based single-screen TUI with a main log panel for phased agent output and a bottom input line.
- Interaction flow: user enters prompts or commands; commands prefixed with "!" run in project cwd; results flow through phases (Planning, Exploring, Proposed Fix, Validation/Summary).
- Milestones:
  - TUI-1: scaffolding (layout + input + /exit, /clear). [done]
  - TUI-2: command execution + streaming output in phases. [done]
  - TUI-3: agent integration + patch preview + approval + summary; history and /history. [pending]

## Codex-inspired integration plan
- Slash-command registry in TUI (/model, /approvals, /status, /history, /plan, /compact, /skills, /new, /resume, /sessions).
- Session state persistence for long-running chats (save/load sessions).
- Approval modes (suggest/auto-edit/full-auto) to control patch apply behavior.
- AGENTS.md loader to inject project guidance into agent context.
- Non-interactive prompt mode for scripting/CI (CLI flag).
Milestones:
- Integrate-1: slash commands + approvals + status (TUI).
- Integrate-2: sessions + AGENTS.md context (TUI + core context).
- Integrate-3: non-interactive prompt mode and docs.

## Risks
- Missing MODEL_* env vars prevent real model calls; fail loudly and block agent workflow.
- Patch application differences across platforms if git/patch is absent; rely on git apply and surface errors.
- Context leakage risk; mitigate with denylist + size bounds and avoid reading arbitrary files.
- Non-JSON model output; enforce strict parsing and reject on schema mismatch.

## Milestones
- Milestone A: CLI works end-to-end using direct provider model call.
  - Command wrapper + failure gate
  - Safe context collection
  - Real model call + JSON validation
  - Patch preview + approval + apply
  - Rerun once + history
  - Tests executed and passing
- Milestone B: Modal endpoint added and CLI can use it via STACKFIX_ENDPOINT.
- Milestone C: Safety hardening + denylist verified + size limits enforced (explicit tests).
- Milestone D: End-to-end demo scripts included + README instructions verified.

## Status
- Milestone A: in progress (direct model call not validated; missing MODEL_API_KEY)
- Milestone B: pending
- Milestone C: pending
- Milestone D: pending
- CLI Interface v1: in progress (TUI-1 and TUI-2 complete; TUI-3 pending)
- Codex-inspired integration: in progress (Integrate-1/2 complete; Integrate-3 pending)

## Validation notes
- 2026-01-19: Ran `python -m stackfix -- python -c "import sys; print('fail'); sys.exit(1)"` with MODEL_BASE_URL=https://api.tokenfactory.nebius.com/v1 and MODEL_NAME=openai/gpt-oss-120b; agent call failed due to missing MODEL_API_KEY.
- 2026-01-19: Agent call reached Token Factory endpoint but failed parsing JSON because the response content was None. Added robust content extraction (content list/text/tool_calls/text field) and will re-validate with real API key.
- 2026-01-19: Created deterministic demo failure in `demo/calc.py` + `demo/test_calc.py`. Command: `python demo\\test_calc.py`. Output: `FAIL: add(2,3) returned -1, expected 5`.
- 2026-01-19: Command: `STACKFIX_DEBUG=1 python -m stackfix -- python demo\\test_calc.py`. Output: `FAIL: add(2,3) returned -1, expected 5` then `Agent call failed: Missing required env var: MODEL_BASE_URL`.
- 2026-01-19: Added fallback patch applier for single-file diffs with invalid hunk headers and Begin Patch format. Re-validation required with real model output.
- 2026-01-19: TUI-1 manual test: launched `python -m stackfix`, verified header + prompt visible, `/exit` closes session.
- 2026-01-19: TUI-2 manual test: launched `python -m stackfix`, ran `! python -c "print('ok')"`, then `/exit`; no crashes observed in TUI session.
- 2026-01-19: TUI styling update: launched `python -m stackfix` and verified splash box + tip line render and `/exit` closes session.
- 2026-01-19: Codex-inspired TUI commands: launched `python -m stackfix`, ran `/status` (showed cwd/model/endpoint/approvals/session), then `/exit`.
- 2026-01-19: Parsing self-test: ran `python scripts\\parse_selftest.py` and verified coercion of rerun_command and fallback for plain text.
