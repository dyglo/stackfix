# StackFix

> Terminal-first agentic CLI that fixes failing commands using AI

StackFix is a developer productivity tool that brings AI-powered assistance directly to your terminal. Describe what you want in natural language, wrap failing commands to get automated fixes, or use the interactive TUI for complex workflows.

## Features

- 🤖 **Natural language prompts** — Ask questions, get code suggestions
- 🔧 **Command wrapping** — Automatically diagnose and fix failing commands
- 🎨 **Syntax-highlighted diffs** — Clear visualization of proposed changes
- 💬 **Interactive TUI** — Rich terminal interface with slash commands
- 🔌 **Provider-agnostic** — Works with OpenAI, Nebius, or any compatible API
- 📝 **Session persistence** — Resume previous conversations

## Documentation

- [Getting Started](./docs/getting-started.md)
- [Configuration Guide](./docs/configuration.md)
- [Slash Commands Reference](./docs/slash-commands.md)
- [Project Context (AGENTS.md)](./docs/agents-md.md)
- [Changelog](./CHANGELOG.md)

## Installation

### npm (recommended)

```bash
npm install -g stackfix
```

### pip

```bash
pip install stackfix
```

### From source

```bash
git clone https://github.com/stackfix/stackfix.git
cd stackfix
pip install -e .
```

## Quick Start

```bash
# Launch interactive TUI
stackfix

# Single prompt (non-interactive)
stackfix --prompt "explain this error: ImportError: No module named 'foo'"

# Wrap a failing command
stackfix -- pytest -q
```

## Configuration

Set environment variables for your LLM provider:

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

## TUI Commands

| Command | Description |
|---------|-------------|
| `/help` | Show all available commands |
| `/exit` | Exit the TUI |
| `/model <name>` | View or switch the model |
| `/approvals <mode>` | Set approval mode (suggest, auto-edit, full-auto) |
| `/status` | Show current configuration |
| `/diff` | Show pending git changes |
| `/history` | Show last run summary |
| `/new` | Start a new session |
| `/resume <id>` | Resume a saved session |

Use `!command` to run shell commands directly.

## Project Context

Create an `AGENTS.md` file in your project root to provide persistent context:

```markdown
# Project Guidelines

- Use pytest for testing
- Follow PEP 8 style
- Prefer type hints
```

## Development

```bash
# Install with dev dependencies
pip install -e ".[dev]"

# Run tests
pytest tests/ -v
```

## License

MIT
