#!/usr/bin/env python3
"""
Integration Tests: Branch Guard Hook
======================================
Tests the full branch-guard.sh PreToolUse hook end-to-end
including protection, bypass, config loading, and auto-detection.

Hook under test: ~/.claude/hooks/branch-guard.sh
Protocol: reads JSON from stdin, exits 0 (allow) or 2 (block)

Run with: python3 tests/test_integration_branch_guard.py
"""

import json
import os
import shutil
import subprocess
import tempfile
import unittest
from pathlib import Path


# Hook path
HOOK_PATH = os.path.expanduser("~/.claude/hooks/branch-guard.sh")


def _run_hook(json_payload: dict, timeout: int = 10) -> subprocess.CompletedProcess:
    """Pipe JSON to the branch-guard hook and return the result."""
    return subprocess.run(
        ["bash", HOOK_PATH],
        input=json.dumps(json_payload),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _init_repo(path: str, branches: list[str] | None = None) -> None:
    """Initialize a git repo at path with main branch and optional extras.

    Creates an initial commit so branches can be created.
    """
    subprocess.run(
        ["git", "init", "-b", "main", path],
        capture_output=True, check=True,
    )
    # Initial commit so branches work
    readme = os.path.join(path, "README.md")
    with open(readme, "w") as f:
        f.write("# Test repo\n")
    subprocess.run(
        ["git", "-C", path, "add", "."],
        capture_output=True, check=True,
    )
    subprocess.run(
        ["git", "-C", path, "commit", "-m", "Initial commit"],
        capture_output=True, check=True,
        env={**os.environ, "GIT_AUTHOR_NAME": "test", "GIT_AUTHOR_EMAIL": "t@t",
             "GIT_COMMITTER_NAME": "test", "GIT_COMMITTER_EMAIL": "t@t"},
    )
    for branch in (branches or []):
        subprocess.run(
            ["git", "-C", path, "branch", branch],
            capture_output=True, check=True,
        )


def _checkout(path: str, branch: str) -> None:
    """Switch to branch in the repo at path."""
    subprocess.run(
        ["git", "-C", path, "checkout", branch],
        capture_output=True, check=True,
    )


def _make_write_json(file_path: str, cwd: str) -> dict:
    """Build a Write tool JSON payload for a new .py file."""
    return {
        "tool_name": "Write",
        "tool_input": {
            "file_path": file_path,
            "content": "# new code\n",
        },
        "cwd": cwd,
    }


def _make_edit_json(file_path: str, cwd: str) -> dict:
    """Build an Edit tool JSON payload."""
    return {
        "tool_name": "Edit",
        "tool_input": {
            "file_path": file_path,
            "old_string": "x",
            "new_string": "y",
        },
        "cwd": cwd,
    }


@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestBranchGuardFullWorkflow(unittest.TestCase):
    """Test the full protection workflow: dev blocks new code, feature allows it."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="bg-workflow-")
        _init_repo(self.repo, branches=["dev"])

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_dev_new_code_blocked_then_worktree_allowed(self):
        """New .py on dev is blocked; same file on feature branch is allowed."""
        payload = _make_write_json("src/feature.py", self.repo)

        # On dev: should be blocked
        _checkout(self.repo, "dev")
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 2, "New .py should be blocked on dev")
        self.assertIn("BRANCH GUARD", result.stderr)

        # Create a feature branch and switch to it
        subprocess.run(
            ["git", "-C", self.repo, "checkout", "-b", "feature/new-thing"],
            capture_output=True, check=True,
        )

        # On feature branch: should be allowed
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0, "New .py should be allowed on feature branch")


@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestBranchGuardBypassFlow(unittest.TestCase):
    """Test the .claude/allow-dev-edit bypass marker."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="bg-bypass-")
        _init_repo(self.repo, branches=["dev"])
        _checkout(self.repo, "dev")

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_bypass_enables_and_disables(self):
        """Bypass marker toggles protection on and off."""
        payload = _make_write_json("lib/new_module.py", self.repo)
        marker = os.path.join(self.repo, ".claude", "allow-dev-edit")

        # Step 1: blocked by default
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 2, "Should be blocked without bypass marker")

        # Step 2: create bypass marker -> allowed
        os.makedirs(os.path.dirname(marker), exist_ok=True)
        Path(marker).touch()
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0, "Should be allowed with bypass marker")

        # Step 3: remove marker -> blocked again
        os.remove(marker)
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 2, "Should be blocked after marker removal")


@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestBranchGuardConfigLoading(unittest.TestCase):
    """Test custom .claude/branch-guard.json config loading."""

    def setUp(self):
        self.repo = tempfile.mkdtemp(prefix="bg-config-")
        _init_repo(self.repo, branches=["production", "staging"])
        # Write custom config
        config_dir = os.path.join(self.repo, ".claude")
        os.makedirs(config_dir, exist_ok=True)
        # The hook reads branch names as top-level keys using jq:
        #   _json_get '."production"' reads the protection level directly.
        # Write branch name as top-level key to match the hook's config format.
        config_file = os.path.join(config_dir, "branch-guard.json")
        with open(config_file, "w") as f:
            json.dump({"production": "block-all"}, f)

    def tearDown(self):
        shutil.rmtree(self.repo, ignore_errors=True)

    def test_custom_config_production_blocked(self):
        """Production branch with block-all config rejects edits."""
        _checkout(self.repo, "production")
        payload = _make_edit_json("README.md", self.repo)
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 2, "Edit should be blocked on production (block-all)")
        self.assertIn("BRANCH PROTECTION", result.stderr)

    def test_custom_config_unlisted_branch_allowed(self):
        """Branch not listed in config is unprotected."""
        _checkout(self.repo, "staging")
        payload = _make_edit_json("README.md", self.repo)
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0, "Edit should be allowed on staging (not in config)")


@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestBranchGuardAutoDetect(unittest.TestCase):
    """Test auto-detection of protection rules based on repo structure."""

    def setUp(self):
        self.repos = []

    def tearDown(self):
        for repo in self.repos:
            shutil.rmtree(repo, ignore_errors=True)

    def _make_repo(self, branches=None):
        repo = tempfile.mkdtemp(prefix="bg-autodetect-")
        _init_repo(repo, branches=branches)
        self.repos.append(repo)
        return repo

    def test_repo_with_dev_protects_both(self):
        """Repo with dev branch: main=block-all, dev=block-new-code."""
        repo = self._make_repo(branches=["dev"])

        # On main: Edit is blocked (block-all)
        _checkout(repo, "main")
        edit_payload = _make_edit_json("README.md", repo)
        result = _run_hook(edit_payload)
        self.assertEqual(result.returncode, 2, "Edit on main should be blocked (block-all)")

        # On dev: Write new .py is blocked (block-new-code)
        _checkout(repo, "dev")
        write_payload = _make_write_json("app/server.py", repo)
        result = _run_hook(write_payload)
        self.assertEqual(result.returncode, 2, "New .py on dev should be blocked (block-new-code)")

    def test_repo_without_dev_only_protects_main(self):
        """Repo without dev branch: main=block-all, other branches unprotected."""
        repo = self._make_repo(branches=[])

        # On main: Edit is blocked
        _checkout(repo, "main")
        edit_payload = _make_edit_json("README.md", repo)
        result = _run_hook(edit_payload)
        self.assertEqual(result.returncode, 2, "Edit on main should be blocked")

        # Create and switch to a working branch
        subprocess.run(
            ["git", "-C", repo, "checkout", "-b", "working"],
            capture_output=True, check=True,
        )

        # On working: Write new .py is allowed
        write_payload = _make_write_json("lib/utils.py", repo)
        result = _run_hook(write_payload)
        self.assertEqual(result.returncode, 0, "New .py on 'working' branch should be allowed")


if __name__ == "__main__":
    unittest.main()
