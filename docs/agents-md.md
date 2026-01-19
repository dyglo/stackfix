# Project Context (AGENTS.md)

StackFix can read project-specific instructions from a file named `AGENTS.md` in your repository root. This is the best way to ensure the AI follows your team's coding standards.

## How it Works
When StackFix starts, it looks for an `AGENTS.md` file. The contents of this file are automatically added to every prompt sent to the LLM.

## Example AGENTS.md

Create a file at the root of your project:

```markdown
# Project Standards

- **Language:** Python 3.10+
- **Testing:** Use `pytest`. Never use `unittest`.
- **Styling:** Follow PEP 8. Use type hints for all functions.
- **Errors:** Don't just fix errors; add helpful logging where appropriate.
- **Security:** Never commit API keys or secrets.
```

## Why Use It?
- **Consistency:** Ensures the AI doesn't propose code that breaks your style guide.
- **Speed:** You don't have to repeat basic project requirements in your prompts.
- **Customization:** Tailor the agent's behavior to specific libraries your project uses.
