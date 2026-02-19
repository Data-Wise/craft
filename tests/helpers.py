"""Shared test utilities for the Craft plugin test suite.

Extracts duplicated patterns from across 60+ test files into a single
reusable module. Import what you need:

    from tests.helpers import CheckResult, log, read_file
    from tests.helpers import init_repo, run_hook, make_write_json
"""

from __future__ import annotations

import json
import os
import re
import subprocess
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Any, Optional


# ---------------------------------------------------------------------------
# Project paths
# ---------------------------------------------------------------------------

PLUGIN_DIR = Path(__file__).parent.parent
"""Root directory of the craft plugin (repo root)."""

SCRIPTS_DIR = PLUGIN_DIR / "scripts"
"""Location of shell scripts (formatting.sh, branch-guard.sh, etc.)."""

COMMANDS_DIR = PLUGIN_DIR / "commands"
"""Location of command markdown files."""

TESTS_DIR = PLUGIN_DIR / "tests"
"""Location of test files."""


# ---------------------------------------------------------------------------
# CheckResult — transitional pattern (will be replaced by native pytest)
# ---------------------------------------------------------------------------

@dataclass
class CheckResult:
    """Structured test result used by check-style test functions.

    This is a transitional pattern — new tests should use native pytest
    assertions instead. Existing tests will be migrated incrementally.
    """
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "general"


# ---------------------------------------------------------------------------
# Logging
# ---------------------------------------------------------------------------

def log(msg: str) -> None:
    """Print a message with HH:MM:SS.mmm timestamp prefix."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")


# ---------------------------------------------------------------------------
# File utilities
# ---------------------------------------------------------------------------

def read_file(path: str | Path, encoding: str = "utf-8") -> str:
    """Read file contents, return empty string if file not found.

    Accepts both str and Path objects. Safe to call on nonexistent paths.
    """
    p = Path(path) if isinstance(path, str) else path
    if not p.exists():
        return ""
    return p.read_text(encoding=encoding)


def extract_frontmatter(content: str) -> dict[str, Any]:
    """Extract YAML frontmatter from markdown content.

    Returns empty dict if no frontmatter found or YAML is invalid.
    Requires PyYAML (``import yaml``).
    """
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    try:
        import yaml
        return yaml.safe_load(match.group(1)) or {}
    except Exception:
        return {}


# ---------------------------------------------------------------------------
# Git helpers (for integration/e2e tests)
# ---------------------------------------------------------------------------

_GIT_ENV = {
    "GIT_AUTHOR_NAME": "test",
    "GIT_AUTHOR_EMAIL": "t@t",
    "GIT_COMMITTER_NAME": "test",
    "GIT_COMMITTER_EMAIL": "t@t",
}


def init_repo(
    path: str,
    branches: list[str] | None = None,
    initial_file: str = "README.md",
) -> None:
    """Initialize a git repo at *path* with ``main`` branch and optional extras.

    Creates an initial commit so branches can be created immediately.
    """
    env = {**os.environ, **_GIT_ENV}
    subprocess.run(
        ["git", "init", "-b", "main", path],
        capture_output=True, check=True,
    )
    readme = os.path.join(path, initial_file)
    with open(readme, "w") as f:
        f.write("# Test repo\n")
    subprocess.run(
        ["git", "-C", path, "add", "."],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", path, "commit", "-m", "Initial commit"],
        capture_output=True, check=True, env=env,
    )
    for branch in branches or []:
        subprocess.run(
            ["git", "-C", path, "branch", branch],
            capture_output=True, check=True,
        )


def checkout_branch(path: str, branch: str) -> None:
    """Switch to *branch* in the repo at *path*."""
    subprocess.run(
        ["git", "-C", path, "checkout", branch],
        capture_output=True, check=True,
    )


# ---------------------------------------------------------------------------
# Hook testing helpers
# ---------------------------------------------------------------------------

def run_hook(
    json_payload: dict[str, Any],
    hook_path: str | Path,
    timeout: int = 10,
) -> subprocess.CompletedProcess:
    """Pipe JSON to a hook script and return the result.

    Used for testing branch-guard and other PreToolUse/PostToolUse hooks.
    """
    return subprocess.run(
        ["bash", str(hook_path)],
        input=json.dumps(json_payload),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def make_write_json(file_path: str, cwd: str) -> dict[str, Any]:
    """Build a Write tool JSON payload for hook testing."""
    return {
        "tool_name": "Write",
        "tool_input": {
            "file_path": file_path,
            "content": "# new code\n",
        },
        "cwd": cwd,
    }


def make_edit_json(file_path: str, cwd: str) -> dict[str, Any]:
    """Build an Edit tool JSON payload for hook testing."""
    return {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": file_path,
            "old_string": "x",
            "new_string": "y",
        },
        "cwd": cwd,
    }
