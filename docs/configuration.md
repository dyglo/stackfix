# Configuration Guide

StackFix is provider-agnostic, meaning it works with any OpenAI-compatible API.

## Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `MODEL_BASE_URL` | The API endpoint | `https://api.openai.com/v1` |
| `MODEL_API_KEY` | Your secret API key | `sk-xxxx...` |
| `MODEL_NAME` | The model identifier | `gpt-4o`, `openai/gpt-oss-120b` |
| `STACKFIX_DEBUG` | Enable verbose logging | `1` |
| `MODEL_MAX_TOKENS` | Max output tokens | `2000` |

## Provider Examples

### OpenAI
```bash
export MODEL_BASE_URL="https://api.openai.com/v1"
export MODEL_API_KEY="sk-..."
export MODEL_NAME="gpt-4o"
```

### Nebius
```bash
export MODEL_BASE_URL="https://api.tokenfactory.nebius.com/v1"
export MODEL_API_KEY="..."
export MODEL_NAME="openai/gpt-oss-120b"
```

### Ollama (Local)
```bash
export MODEL_BASE_URL="http://localhost:11434/v1"
export MODEL_API_KEY="ollama"
export MODEL_NAME="codellama"
```

## Persisting Settings

To avoid typing these every time:

- **Windows:** Search for "Edit the system environment variables" in the Start menu.
- **macOS/Linux:** Add the `export` lines to your `~/.bashrc` or `~/.zshrc`.
