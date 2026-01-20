---
name: stackfix-dev
description: StackFix development workflow for Codex: inspect repo, reproduce issues, apply minimal diffs, run tests, and update docs/changelog for StackFix CLI and TUI changes.
metadata:
  short-description: StackFix dev workflow
---

# StackFix Development Skill

## Triage and context
- Reproduce the issue or goal with the exact CLI/TUI command.
- Capture logs and errors; include exit code and stdout/stderr snippets.
- Inspect config inputs (env vars, `AGENTS.md`, `docs/` references).
- Read relevant files before changing anything.

## Safe edits
- Search for symbols before editing.
- Make minimal diffs; prefer `apply_patch` over full rewrites.
- Avoid touching files outside the stated scope.

## Validate
- Run targeted tests first, then the broader suite when needed.
- Default test command: `pytest tests/ -v`.
- If a test fails, fix and rerun until green.

## Docs and changelog
- Update `docs/` when behavior or CLI usage changes.
- Update `CHANGELOG.md` for user-facing changes.

## Finish
- Report: What changed, How verified, Remaining risks/next steps.