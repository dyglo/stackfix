# Slash Commands Reference

When inside the StackFix TUI, you can use slash commands to control the agent and manage your session.

## Core Commands

| Command | Description |
|---------|-------------|
| `/help` | List all available commands. |
| `/exit` | Exit StackFix and return to your shell. |
| `/clear` | Clear the current log history in the TUI view. |
| `/status` | Show current configuration (CWD, Model, Session ID). |

## Agent Control

| Command | Description |
|---------|-------------|
| `/model <name>` | Temporarily switch the model for the current session. |
| `/approvals <mode>` | Toggle how patches are applied: `suggest` (default), `auto-edit`, or `full-auto`. |
| `/diff` | Show pending git changes in the current directory. |
| `/history` | Show the summary and patch of the last attempted fix. |

## Session Management

| Command | Description |
|---------|-------------|
| `/new` | Start a fresh session with a new ID. |
| `/sessions` | List recent saved sessions. |
| `/resume <id>` | Resume a specific session from history. |

## Shell Integration
You can run any shell command directly from the TUI by prefixing it with an exclamation mark:
`!ls -la` or `!git status`
