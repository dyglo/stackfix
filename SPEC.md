# StackFix Spec

## Scope
- Deliver a terminal-first AI CLI for fixing failing commands and answering developer prompts.
- Support TUI, prompt mode, and command wrapping flows.
- Provide safe local execution with clear diffs and approvals.

## Definition of Done
- Acceptance criteria checklist fully checked.
- Relevant tests pass (`pytest tests/ -v`).
- Docs updated for behavior changes.
- No new regressions; changes are minimal and scoped.

## Acceptance criteria checklist (template)
- [ ] Repro steps documented (or reason not reproducible)
- [ ] Root cause identified
- [ ] Minimal fix implemented
- [ ] Tests updated/added as needed
- [ ] Relevant tests pass
- [ ] Docs updated if behavior changes

## Loop until done
Codex must iterate: read -> search -> edit -> test -> fix -> retest until all checklist items are checked.
Do not stop early; continue until acceptance criteria are satisfied.

## Task board (near-term)
- [ ] TUI polish (keyboard shortcuts, clearer prompts, status line)
- [ ] Command wrapping reliability (better error parsing, rerun safety)
- [ ] Session persistence hardening (corruption handling, migrations)
- [ ] Provider config ergonomics (wizard, validation, clearer errors)