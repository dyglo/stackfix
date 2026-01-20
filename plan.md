# StackFix plan

## Vision
Ship a production-ready, terminal-first agentic CLI with a zero-config default model backed by a StackFix relay, and a professional safety/approval system comparable to Codex CLI.

## Architecture (target)
- **CLI runtime (Python)**: TUI + prompt mode + command wrap; local tool execution; diff/approval UX.
- **Relay (FastAPI)**: OpenAI-compatible `/v1/chat/completions` with anonymous device tokens and rate limiting.
- **Provider layer**: OpenAI SDK with configurable upstream base URL (Nebius/Token Factory).
- **Safety & policy**: command denylist, path allowlist, and approval modes.
- **Session & history**: stored in `.stackfix/` with summaries and patches.

## Phase plan

### Phase 1 — Relay + zero-config default model
- FastAPI relay scaffold with OpenAI-compatible endpoints.
- Anonymous token issuance and verification.
- Per-device rate limiting and quota headers.
- Health check and model listing endpoints.

### Phase 2 — Tool calling loop
- Add OpenAI tool schema + local execution loop.
- Support file read/write/patch, search, and command execution.
- Structured tool result return to model.

### Phase 3 — Safety + approvals polish
- Approval modes: suggest / auto-edit / full-auto.
- Command safety denylist and confirmation gates.
- Clear diff preview + apply/reject flow.

### Phase 4 — UX and docs hardening
- `/status`, `/history`, `/diff`, `/sessions` refinements.
- Updated docs and configuration guide.
- Changelog entries for user-facing behavior.

## Deliverables (near-term)
- Relay scaffold (FastAPI app + auth + rate limiting).
- CLI config defaults for relay usage.
- Specs for tool schema and approval workflow.

## Risks & mitigations
- **Upstream outages**: add retry/backoff and clear error messages.
- **Cost spikes**: enforce daily quotas and device/IP throttling.
- **Security**: never expose provider keys; redact sensitive logs.
- **Tool misuse**: strict path allowlist and command approvals.

## Definition of Done for each milestone
- Relevant tests passing (`pytest tests/ -v`).
- Updated docs for behavior changes.
- No regressions in CLI flows.

## Status
- Phase 1: in progress (relay scaffold pending).
- Phase 2: pending.
- Phase 3: pending.
- Phase 4: pending.
