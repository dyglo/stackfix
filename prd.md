# StackFix — Product Requirements Document

> **Version:** 1.0.0-transition  
> **Date:** January 2026  
> **Status:** Strategic Transition to Codex/Claude Code-grade CLI Agent

---

## 1. Project Overview

### What is StackFix?

**StackFix** is a terminal-first **agentic developer CLI** that uses large language models to help developers fix failing commands, write code, and automate repetitive tasks through natural language.

Unlike traditional CLI tools that require memorizing flags and syntax, StackFix lets developers **describe what they want** and receives intelligent, contextual assistance directly in their terminal.

### The Problem StackFix Solves

Developers encounter friction daily:
- Commands fail with cryptic errors
- Debugging requires context-switching between terminals, browsers, and documentation  
- Repetitive tasks demand boilerplate code or shell scripts
- AI coding assistants typically require leaving the terminal for web interfaces or IDEs

**StackFix eliminates this friction** by bringing AI-powered development assistance directly into the terminal where developers already work.

### Comparison to Codex CLI / Claude Code

| Capability | OpenAI Codex CLI | Anthropic Claude Code | StackFix |
|------------|------------------|----------------------|----------|
| Terminal-native | ✅ | ✅ | ✅ |
| Natural language input | ✅ | ✅ | ✅ |
| Provider-agnostic | ❌ (OpenAI only) | ❌ (Anthropic only) | ✅ |
| Command wrapping & auto-fix | Limited | Limited | ✅ Core feature |
| Interactive TUI | ✅ | ✅ | ✅ |
| Slash commands | ✅ | ✅ | ✅ |
| Session persistence | ✅ | ✅ | ✅ |
| Project context (AGENTS.md) | ✅ | ✅ | ✅ |
| Approval modes | ✅ | ✅ | ✅ |

StackFix differentiates by being **provider-agnostic** (OpenAI, Nebius, Modal, or any OpenAI-compatible endpoint) and by focusing on **command failure diagnosis and automatic patching**.

---

## 2. What Has Already Been Achieved

### Core CLI Implementation ✅

- **Entry point:** `stackfix` command via `pyproject.toml` script
- **Command wrapping:** `stackfix -- <command>` captures failures and streams output
- **Natural language prompts:** `stackfix --prompt "<question>"` for non-interactive queries
- **History:** Run records stored in `.stackfix/history/` with `--last` retrieval

### LLM Integration ✅

- **Provider-agnostic:** Works with any OpenAI-compatible API endpoint
- **Configuration:** Environment variables (`MODEL_BASE_URL`, `MODEL_API_KEY`, `MODEL_NAME`)
- **Modal support:** Optional `STACKFIX_ENDPOINT` for serverless deployment
- **Structured parsing:** JSON response extraction with fallback handling

### Agent Response Parsing ✅

- JSON schema validation for agent responses
- Unified diff extraction and validation
- Confidence scoring and rerun command normalization
- Fallback mode for plain-text responses

### Interactive TUI ✅

- **Framework:** Textual-based terminal UI
- **Layout:** Splash header, log panel, input line, status bar
- **Phases:** Planning → Exploring → Proposed Fix → Validation/Summary

### Slash Commands (Implemented)

| Command | Description |
|---------|-------------|
| `/exit` | Exit the TUI |
| `/clear` | Clear the log panel |
| `/model <name>` | View or switch model |
| `/approvals <mode>` | Set approval mode (suggest, auto-edit, full-auto) |
| `/status` | Show current configuration |
| `/history` | Show last run summary |
| `/plan` | Show current execution plan |
| `/skills` | List available skills (stub) |
| `/compact` | Summarize session (stub) |
| `/new` | Start new session |
| `/resume <id>` | Resume saved session |
| `/sessions` | List saved sessions |

### Project Context ✅

- `AGENTS.md` file loading for project-specific instructions
- Context injection into agent prompts

### Current Limitations

- **Sandbox security:** Not implemented (command execution is unrestricted)
- **Patch reliability:** Basic `git apply` with fallback; edge cases may fail
- **TUI stability:** Some rendering inconsistencies under heavy output
- **Skills system:** Stubs only; no actual skill execution
- **Cost tracking:** No token usage monitoring
- **CI integration:** No pipeline-specific features

---

## 3. Transition Statement

> **StackFix is officially transitioning from an early agentic CLI prototype into a full Codex/Claude Code-grade developer agent.**

This transition prioritizes:

1. **Natural language workflows** — Making prompts the primary interaction mode
2. **Interactive CLI/TUI UX** — Polished, terminal-native experience
3. **Developer productivity** — Reducing time from error to fix
4. **Extensibility** — Skills, plugins, and IDE bridges (future phases)

The goal is to make StackFix a **serious, production-ready developer tool** comparable to OpenAI Codex CLI and Anthropic Claude Code.

---

## 4. Near-Term Product Direction

### 4.1 Codex/Claude Code-like CLI Interface

**Priority Features:**

- **Rich input handling:** Tab completion, message editing, multi-line input
- **Diff visualization:** Syntax-highlighted patch previews
- **Progress indicators:** Spinners, streaming output, phase transitions
- **Keyboard shortcuts:** Esc to edit, Ctrl+C to interrupt, ? for help

### 4.2 Structured Agent Output

The agent should produce clear, phased output:

```
• Planning
  → Read project structure
  → Analyze error context

• Exploring  
  → Identified: TypeError in utils.py:42
  → Root cause: Missing null check

• Proposed Fix
  ┌─────────────────────────────────────
  │ utils.py: Add null check before access
  └─────────────────────────────────────
  
  @@ -41,3 +41,5 @@
  -    return obj.value
  +    if obj is None:
  +        return None
  +    return obj.value

• Validation
  ✓ Patch applied successfully
  ✓ Tests pass (exit code 0)
```

### 4.3 Natural Language + Commands

Both interaction styles supported:

```bash
# Natural language (primary)
> fix the failing test in utils.py
> explain what this function does
> refactor to use async/await

# Shell commands (prefixed)
> ! pytest -v
> ! git diff HEAD~1

# Slash commands (configuration)
> /model gpt-4
> /approvals auto-edit
```

### 4.4 Provider-Agnostic Design

Maintain support for multiple LLM providers:

```bash
# OpenAI
export MODEL_BASE_URL="https://api.openai.com/v1"
export MODEL_API_KEY="sk-..."
export MODEL_NAME="gpt-4"

# Nebius
export MODEL_BASE_URL="https://api.tokenfactory.nebius.com/v1"
export MODEL_API_KEY="..."
export MODEL_NAME="openai/gpt-oss-120b"

# Local (Ollama)
export MODEL_BASE_URL="http://localhost:11434/v1"
export MODEL_NAME="codellama:13b"
```

---

## 5. Installation & Distribution

### 5.1 Global Install Method

**Primary: npm wrapper (recommended)**

```bash
npm install -g stackfix
# or
npx stackfix
```

The npm package will:
1. Check for Python 3.9+
2. Create an isolated virtualenv
3. Install the Python package
4. Provide a `stackfix` shell wrapper

**Alternative: pip install**

```bash
pip install stackfix
```

**Alternative: pipx (isolated)**

```bash
pipx install stackfix
```

### 5.2 Package Structure

```
stackfix/
├── package.json          # npm wrapper
├── bin/
│   └── stackfix          # Shell wrapper script
├── pyproject.toml        # Python package
├── stackfix/
│   ├── __init__.py
│   ├── cli.py           # Entry point
│   ├── agent.py         # LLM integration
│   ├── tui.py           # Interactive TUI
│   └── ...
└── README.md
```

### 5.3 Versioning Strategy

- **Semantic versioning:** `MAJOR.MINOR.PATCH`
- **Current:** `0.1.0` (pre-release)
- **Target:** `1.0.0` for production-ready release

**Version milestones:**
- `0.2.0` — Stable TUI with all slash commands
- `0.3.0` — npm packaging complete
- `0.4.0` — Skills system functional
- `1.0.0` — Production-ready, fully documented

### 5.4 Simple Entrypoint

After installation, the user runs:

```bash
stackfix                    # Launch interactive TUI
stackfix --prompt "..."     # Single prompt, non-interactive
stackfix -- pytest -v       # Wrap and fix failing command
stackfix --help             # Show usage
```

---

## 6. Feature Roadmap (Codex CLI Alignment)

### Phase 1: Core UX Polish (Current)
- [x] Basic TUI layout
- [x] Slash command framework
- [x] Session persistence
- [ ] Tab completion for commands
- [ ] Syntax-highlighted diffs
- [ ] Interrupt handling (Ctrl+C)

### Phase 2: Agent Loop Enhancement
- [ ] Multi-step planning display
- [ ] File exploration phases
- [ ] Streaming response rendering
- [ ] Error recovery and retry

### Phase 3: Skills System
- [ ] `/skills` with actual implementations
- [ ] `/review` — code review skill
- [ ] `/compact` — conversation summarization
- [ ] Custom skill loading

### Phase 4: Distribution
- [ ] npm wrapper package
- [ ] GitHub releases with binaries
- [ ] Homebrew formula (macOS)
- [ ] Documentation site

### Phase 5: Advanced Features (Deferred)
- [ ] Sandbox security
- [ ] Approval policies
- [ ] Token cost tracking
- [ ] CI/CD integration
- [ ] IDE extensions

---

## 7. Non-Goals (Explicitly Deferred)

The following are **out of scope** for the current phase:

- **Sandbox security:** Will use unrestricted execution for now
- **Approval policies:** Beyond basic suggest/auto-edit/full-auto modes
- **Patch correctness:** Will rely on git apply; edge cases accepted
- **Cost optimization:** No token tracking or budget limits
- **CI integration:** No GitHub Actions or pipeline features
- **IDE plugins:** Future phase after CLI maturity

---

## 8. Success Metrics

### User Experience
- Time from install to first successful prompt: < 2 minutes
- Interactive TUI startup time: < 500ms
- Agent response time (excluding LLM latency): < 100ms

### Reliability
- Command wrapping success rate: > 99%
- Patch application success rate: > 90%
- Session persistence reliability: 100%

### Adoption
- npm weekly downloads (target): 1,000+ within 3 months
- GitHub stars (target): 500+ within 3 months

---

## 9. Technical Requirements

### Runtime Dependencies
- Python 3.9+
- `requests` — HTTP client for LLM APIs
- `textual` — Terminal UI framework

### Development Dependencies
- `pytest` — Testing
- `ruff` — Linting
- `mypy` — Type checking

### Environment Variables
| Variable | Required | Description |
|----------|----------|-------------|
| `MODEL_BASE_URL` | Yes | LLM API endpoint |
| `MODEL_API_KEY` | Yes | API authentication key |
| `MODEL_NAME` | Yes | Model identifier |
| `STACKFIX_ENDPOINT` | No | Modal serverless endpoint |
| `STACKFIX_DEBUG` | No | Enable debug logging |

---

## 10. Appendix: Codex CLI Feature Reference

Features studied from OpenAI Codex CLI for adoption:

| Feature | Status in StackFix |
|---------|-------------------|
| Slash command framework | ✅ Implemented |
| `/model` switching | ✅ Implemented |
| `/approvals` modes | ✅ Implemented |
| `/status` display | ✅ Implemented |
| `/new` / `/resume` sessions | ✅ Implemented |
| `/skills` list | 🔄 Stub only |
| `/review` code review | 🔄 Stub only |
| `/compact` summarize | 🔄 Stub only |
| `/diff` show changes | ❌ Not implemented |
| `/mention` file context | ❌ Not implemented |
| `/mcp` multi-repo | ❌ Not implemented |
| Shell command prefix (`!`) | ✅ Implemented |
| Tab completion | ❌ Not implemented |
| Message editing (Esc) | ❌ Not implemented |
| Image paste (Ctrl+V) | ❌ Not implemented |
| AGENTS.md support | ✅ Implemented |
| Non-interactive mode | ✅ Implemented |
| Notification hooks | ❌ Not implemented |

---

## 11. Next Engineering Steps

1. **Polish TUI rendering** — Fix any whitespace/layout issues, improve diff display
2. **Implement `/diff`** — Show pending changes before apply
3. **Add Tab completion** — For slash commands and file paths
4. **Create npm wrapper** — `package.json` with install script
5. **Write end-to-end tests** — Automated verification of core flows
6. **Prepare GitHub release** — Tag v0.2.0 with changelog

---

*This PRD will be updated as the transition progresses. For implementation details, see `plan.md`.*
