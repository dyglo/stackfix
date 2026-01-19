"""Tests for StackFix TUI components."""

import pytest
from stackfix.tui import _highlight_diff, SLASH_COMMANDS, StackFixTUI


class TestHighlightDiff:
    """Test diff highlighting function."""

    def test_highlight_additions(self):
        diff = "+ added line"
        result = _highlight_diff(diff)
        assert "[green]" in result
        assert "+ added line" in result

    def test_highlight_deletions(self):
        diff = "- removed line"
        result = _highlight_diff(diff)
        assert "[red]" in result
        assert "- removed line" in result

    def test_highlight_headers(self):
        diff = "@@ -1,3 +1,4 @@"
        result = _highlight_diff(diff)
        assert "[magenta]" in result

    def test_highlight_file_headers(self):
        diff = "--- a/file.py\n+++ b/file.py"
        result = _highlight_diff(diff)
        assert "[bold cyan]" in result

    def test_highlight_diff_git(self):
        diff = "diff --git a/file.py b/file.py"
        result = _highlight_diff(diff)
        assert "[bold blue]" in result

    def test_highlight_context_lines(self):
        diff = " unchanged line"
        result = _highlight_diff(diff)
        assert "[dim]" in result


class TestSlashCommands:
    """Test slash command registry."""

    def test_commands_defined(self):
        assert len(SLASH_COMMANDS) > 0

    def test_essential_commands_present(self):
        cmd_names = [cmd for cmd, _ in SLASH_COMMANDS]
        assert "/exit" in cmd_names
        assert "/help" in cmd_names
        assert "/status" in cmd_names
        assert "/diff" in cmd_names
        assert "/model <name>" in cmd_names

    def test_commands_have_descriptions(self):
        for cmd, desc in SLASH_COMMANDS:
            assert cmd.startswith("/")
            assert len(desc) > 0


class TestStackFixTUI:
    """Test TUI app initialization."""

    def test_tui_instantiates(self):
        """Test that TUI can be created."""
        app = StackFixTUI()
        assert app is not None
        assert app._approvals_mode == "suggest"

    def test_tui_has_bindings(self):
        """Test that TUI has expected key bindings."""
        app = StackFixTUI()
        binding_keys = [b[0] for b in app.BINDINGS]
        assert "ctrl+c" in binding_keys
        assert "ctrl+l" in binding_keys
