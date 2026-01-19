# Changelog

All notable changes to StackFix will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.2.0] - 2026-01-19

### Added

- **npm installation support** — Install globally via `npm install -g stackfix`
- **Syntax-highlighted diffs** — Patch previews now show colored additions (green), deletions (red), and headers (cyan)
- **`/diff` command** — View pending git changes in the TUI
- **`/help` command** — List all available slash commands with descriptions
- **Test suite** — Comprehensive pytest coverage for CLI and TUI components
- **Slash command registry** — Centralized `SLASH_COMMANDS` list for easy extension

### Changed

- Improved TUI error messages with command suggestions
- Updated project description for clarity
- Version bump from 0.1.0 to 0.2.0

### Fixed

- Improved diff highlighting to handle all unified diff line types

## [0.1.0] - 2026-01-18

### Added

- Initial release
- Terminal-first CLI with `stackfix` command
- Natural language prompt mode (`--prompt`)
- Command wrapping and failure detection (`stackfix -- <cmd>`)
- LLM integration (provider-agnostic: OpenAI, Nebius, Modal)
- Patch preview and approval workflow
- Interactive TUI with Textual
- Slash commands: `/exit`, `/clear`, `/model`, `/approvals`, `/status`, `/history`, `/plan`, `/skills`, `/compact`, `/new`, `/resume`, `/sessions`
- Session persistence
- AGENTS.md support for project-specific guidance
- Run history storage in `.stackfix/history/`
