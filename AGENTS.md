# StackFix Agent Guide

## Project summary
StackFix is a terminal-first agentic CLI that fixes failing commands using AI.
Key entry points:
- TUI: `stackfix`
- Prompt mode: `stackfix --prompt "<question>"`
- Wrap a failing command: `stackfix -- <command>`

## Repo map
- `stackfix/` core runtime (agent, context, patching, safety, TUI)
- `tests/` pytest suite
- `docs/` user documentation
- `scripts/` install helpers
- `demo/` example files
- `public/` static assets

## Setup
- Install (dev): `pip install -e ".[dev]"`
- Install (runtime): `pip install -e .`
- Run TUI: `stackfix`
- Run prompt: `stackfix --prompt "..."`
- Wrap command: `stackfix -- <cmd>`
- Tests: `pytest tests/ -v`
- Lint/format: no configured lint/format command

## Execution loop (mandatory)
1) Read relevant files first (don’t guess)
2) Search code for symbols before editing
3) Make minimal diffs
4) Run the most relevant test(s) after changes
5) If tests fail, fix and rerun
6) Repeat until green + requirements satisfied

## Safety / change-control
- Prefer diffs; don’t delete files unless required
- Never commit secrets; never print env secrets; redact keys in logs
- Respect approval modes (suggest vs auto-edit vs full-auto if applicable)

## Quality gates
- Keep formatting/lint clean
- Update docs when behavior changes

## Output format (end of task)
- What changed
- How verified
- Remaining risks/next steps