"""Pytest fixtures for StackFix tests."""

import os
import pytest
from pathlib import Path
from unittest.mock import patch


@pytest.fixture
def temp_cwd(tmp_path):
    """Create a temporary directory and change to it."""
    original_cwd = os.getcwd()
    os.chdir(tmp_path)
    yield tmp_path
    os.chdir(original_cwd)


@pytest.fixture
def mock_env_vars():
    """Mock environment variables for testing."""
    env_vars = {
        "MODEL_BASE_URL": "http://localhost:8000/v1",
        "MODEL_API_KEY": "test-key",
        "MODEL_NAME": "test-model",
    }
    with patch.dict(os.environ, env_vars):
        yield env_vars


@pytest.fixture
def mock_agent_response():
    """Sample agent response for testing."""
    return {
        "summary": "Fixed the bug in utils.py",
        "confidence": 0.9,
        "patch_unified_diff": """diff --git a/utils.py b/utils.py
--- a/utils.py
+++ b/utils.py
@@ -1,3 +1,4 @@
+# Fixed version
 def add(a, b):
-    return a - b
+    return a + b
""",
        "rerun_command": ["python", "-m", "pytest"],
    }


@pytest.fixture
def sample_diff():
    """Sample unified diff for testing highlighting."""
    return """diff --git a/example.py b/example.py
--- a/example.py
+++ b/example.py
@@ -1,5 +1,6 @@
 def hello():
-    print("old")
+    print("new")
+    return True
"""
