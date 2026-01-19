"""Tests for StackFix CLI."""

import subprocess
import sys
from pathlib import Path


def test_cli_help():
    """Test that --help flag works correctly."""
    result = subprocess.run(
        [sys.executable, "-m", "stackfix", "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "StackFix command wrapper" in result.stdout
    assert "--prompt" in result.stdout
    assert "--last" in result.stdout


def test_cli_last_no_history(temp_cwd):
    """Test --last with no history returns appropriate message."""
    result = subprocess.run(
        [sys.executable, "-m", "stackfix", "--last"],
        capture_output=True,
        text=True,
        cwd=temp_cwd,
    )
    assert result.returncode == 1
    assert "No history found" in result.stdout


def test_cli_prompt_mode_without_model(temp_cwd, monkeypatch):
    """Test prompt mode fails gracefully without model config."""
    # Remove any model env vars
    monkeypatch.delenv("MODEL_BASE_URL", raising=False)
    monkeypatch.delenv("MODEL_API_KEY", raising=False)
    monkeypatch.delenv("MODEL_NAME", raising=False)
    
    result = subprocess.run(
        [sys.executable, "-m", "stackfix", "--prompt", "hello"],
        capture_output=True,
        text=True,
        cwd=temp_cwd,
    )
    # Should fail because model is not configured
    assert result.returncode != 0
    assert "MODEL_BASE_URL" in result.stderr or "Agent call failed" in result.stderr


def test_npm_wrapper_help():
    """Test that the npm wrapper invokes stackfix correctly."""
    result = subprocess.run(
        ["node", str(Path(__file__).parent.parent / "bin" / "stackfix"), "--help"],
        capture_output=True,
        text=True,
    )
    assert result.returncode == 0
    assert "StackFix" in result.stdout
