# Configuration Guide

StackFix is provider-agnostic and supports a zero-config relay by default.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `STACKFIX_PROVIDER` | Provider mode (`stackfix` or `direct`) | `stackfix` |
| `STACKFIX_RELAY_URL` | StackFix relay base URL | `https://api.stackfix.ai/v1` |
| `STACKFIX_REDIS_URL` | Relay Redis URL (server-side) | `redis://localhost:6379/0` |
| `MODEL_BASE_URL` | The API endpoint | `https://api.openai.com/v1` |
| `MODEL_API_KEY` | Your secret API key | `sk-xxxx...` |
| `MODEL_NAME` | The model identifier | `gpt-4o`, `openai/gpt-oss-120b` |
| `STACKFIX_DEBUG` | Enable verbose logging | `1` |
| `MODEL_MAX_TOKENS` | Max output tokens | `2000` |
| `STACKFIX_USE_DIRECT` | Force direct provider mode | `1` |

## Provider Examples

### StackFix Relay (default)
```bash
export STACKFIX_PROVIDER="stackfix"
export STACKFIX_RELAY_URL="https://api.stackfix.ai/v1"
```

Server-side relay config (for self-hosting):
```bash
export STACKFIX_UPSTREAM_BASE_URL="https://api.tokenfactory.nebius.com/v1"
export STACKFIX_UPSTREAM_API_KEY="..."
export STACKFIX_UPSTREAM_MODEL="openai/gpt-oss-120b"
export STACKFIX_REDIS_URL="redis://localhost:6379/0"
```

### OpenAI
```bash
export MODEL_BASE_URL="https://api.openai.com/v1"
export MODEL_API_KEY="sk-..."
export MODEL_NAME="gpt-4o"
export STACKFIX_PROVIDER="direct"
```

### Nebius
```bash
export MODEL_BASE_URL="https://api.tokenfactory.nebius.com/v1"
export MODEL_API_KEY="..."
export MODEL_NAME="openai/gpt-oss-120b"
export STACKFIX_PROVIDER="direct"
```

### Ollama (Local)
```bash
export MODEL_BASE_URL="http://localhost:11434/v1"
export MODEL_API_KEY="ollama"
export MODEL_NAME="codellama"
export STACKFIX_PROVIDER="direct"
```

## Persisting Settings

To avoid typing these every time:

- **Windows:** Search for "Edit the system environment variables" in the Start menu.
- **macOS/Linux:** Add the `export` lines to your `~/.bashrc` or `~/.zshrc`.
