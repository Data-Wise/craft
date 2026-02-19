"""Pytest configuration and shared fixtures for the Craft plugin test suite.

Adds project root AND tests/ directory to sys.path so test files can:
  - Import project modules: ``from utils.complexity_scorer import ...``
  - Import test helpers:    ``from helpers import CheckResult, read_file``
"""

import os
import shutil
import sys
import tempfile
from pathlib import Path

import pytest

# Add project root to sys.path (existing behavior)
_project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _project_root)

# Add tests/ directory so ``from helpers import ...`` works in all test files
_tests_dir = os.path.dirname(os.path.abspath(__file__))
if _tests_dir not in sys.path:
    sys.path.insert(0, _tests_dir)


# ---------------------------------------------------------------------------
# Path fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def craft_root() -> Path:
    """Path to the craft plugin root directory."""
    return Path(_project_root)


@pytest.fixture
def commands_dir(craft_root: Path) -> Path:
    """Path to the commands/ directory."""
    return craft_root / "commands"


@pytest.fixture
def scripts_dir(craft_root: Path) -> Path:
    """Path to the scripts/ directory."""
    return craft_root / "scripts"


# ---------------------------------------------------------------------------
# Temp directory fixtures
# ---------------------------------------------------------------------------

@pytest.fixture
def temp_dir(tmp_path: Path) -> Path:
    """Provide a clean temporary directory (pytest-managed, auto-cleaned)."""
    return tmp_path


@pytest.fixture
def temp_plugin_dir(tmp_path: Path) -> Path:
    """Temporary directory pre-populated with minimal plugin structure.

    Creates:
      - .claude-plugin/plugin.json (minimal valid manifest)
      - commands/ (empty)
      - CLAUDE.md (minimal)
    """
    plugin_dir = tmp_path / "test-plugin"
    plugin_dir.mkdir()
    (plugin_dir / ".claude-plugin").mkdir()
    (plugin_dir / ".claude-plugin" / "plugin.json").write_text(
        '{"name": "test-plugin", "description": "Test plugin", "version": "1.0.0"}'
    )
    (plugin_dir / "commands").mkdir()
    (plugin_dir / "CLAUDE.md").write_text("# Test Plugin\n")
    return plugin_dir


@pytest.fixture
def temp_git_repo(tmp_path: Path) -> Path:
    """Temporary git repository with initial commit on ``main`` branch.

    Ready for branch creation, commits, and hook testing.
    """
    import subprocess

    repo_dir = tmp_path / "test-repo"
    repo_dir.mkdir()
    env = {
        **os.environ,
        "GIT_AUTHOR_NAME": "test",
        "GIT_AUTHOR_EMAIL": "t@t",
        "GIT_COMMITTER_NAME": "test",
        "GIT_COMMITTER_EMAIL": "t@t",
    }
    subprocess.run(
        ["git", "init", "-b", "main", str(repo_dir)],
        capture_output=True, check=True,
    )
    (repo_dir / "README.md").write_text("# Test repo\n")
    subprocess.run(
        ["git", "-C", str(repo_dir), "add", "."],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", str(repo_dir), "commit", "-m", "Initial commit"],
        capture_output=True, check=True, env=env,
    )
    return repo_dir
