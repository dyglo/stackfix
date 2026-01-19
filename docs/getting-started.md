# Getting Started with StackFix

StackFix is a terminal-native agentic loop that helps you fix failing commands using AI.

## Installation

### Via npm (Recommended)
The easiest way to use StackFix is to install it globally via npm:

```bash
npm install -g stackfix
```

### Via pip
You can also install it as a Python package:

```bash
pip install stackfix
```

## Your First Run

1. **Configure Your Model:**
   Before running StackFix, you need to tell it which LLM to use. Set these environment variables (using your favorite provider like OpenAI, Nebius, or Anthropic):

   ```bash
   export MODEL_BASE_URL="https://api.openai.com/v1"
   export MODEL_API_KEY="your-api-key"
   export MODEL_NAME="gpt-4o"
   ```

2. **Launch the TUI:**
   Simply type `stackfix` in any terminal.

3. **Wrap a Command:**
   If you have a command that is failing, wrap it to get an automated fix:
   ```bash
   stackfix -- pytest tests/test_math.py
   ```

## Next Steps
- Learn about [Configuration](./configuration.md)
- Explore [Slash Commands](./slash-commands.md)
- Add [Project Context](./agents-md.md)
