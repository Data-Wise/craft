#!/usr/bin/env python3
"""
Dogfooding Tests: Branch Guard Hook
=====================================
Tests branch-guard.sh against the REAL craft repo — not temp repos.
Validates hook registration, config format, extension coverage,
real payload handling, error formatting, and performance.

Run with: python3 tests/test_branch_guard_dogfood.py
"""

import json
import os
import subprocess
import tempfile
import time
import unittest
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.branch_guard]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
HOOK_PATH = os.path.expanduser("~/.claude/hooks/branch-guard.sh")
SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")
CRAFT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INSTALL_SCRIPT = os.path.join(CRAFT_ROOT, "scripts", "install-branch-guard.sh")


def _run_hook(json_payload: dict, timeout: int = 10) -> subprocess.CompletedProcess:
    """Pipe JSON to the branch-guard hook and return the result."""
    return subprocess.run(
        ["bash", HOOK_PATH],
        input=json.dumps(json_payload),
        capture_output=True,
        text=True,
        timeout=timeout,
    )


def _get_current_branch() -> str:
    """Return the current branch of the craft repo."""
    result = subprocess.run(
        ["git", "-C", CRAFT_ROOT, "branch", "--show-current"],
        capture_output=True, text=True,
    )
    return result.stdout.strip()


# ============================================================================
# Group 1: Hook Installation & Registration
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestHookInstallation(unittest.TestCase):
    """Verify hook is properly installed and registered."""

    def test_hook_file_exists(self):
        """Hook script exists at ~/.claude/hooks/branch-guard.sh."""
        self.assertTrue(os.path.isfile(HOOK_PATH))

    def test_hook_is_executable_bash(self):
        """Hook starts with a valid bash shebang."""
        with open(HOOK_PATH) as f:
            first_line = f.readline().strip()
        self.assertIn("bash", first_line, "Hook should have bash shebang")

    def test_hook_registered_in_settings(self):
        """Hook is registered as a PreToolUse hook in settings.json."""
        if not os.path.isfile(SETTINGS_PATH):
            self.skipTest("settings.json not found")
        with open(SETTINGS_PATH) as f:
            settings = json.load(f)
        hooks = settings.get("hooks", {})
        pre_tool = hooks.get("PreToolUse", [])
        # Find our hook in the list
        found = any("branch-guard" in str(h) for h in pre_tool)
        self.assertTrue(found, "branch-guard should be in PreToolUse hooks")

    def test_install_script_exists(self):
        """Standalone installer script exists."""
        self.assertTrue(os.path.isfile(INSTALL_SCRIPT))

    def test_install_script_syntax_valid(self):
        """Install script passes bash -n syntax check."""
        result = subprocess.run(
            ["bash", "-n", INSTALL_SCRIPT],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, f"Syntax error: {result.stderr}")

    def test_hook_script_syntax_valid(self):
        """Hook script passes bash -n syntax check."""
        result = subprocess.run(
            ["bash", "-n", HOOK_PATH],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, f"Syntax error: {result.stderr}")

    def test_repo_copy_matches_installed(self):
        """scripts/branch-guard.sh matches the installed hook."""
        repo_script = os.path.join(CRAFT_ROOT, "scripts", "branch-guard.sh")
        if not os.path.isfile(repo_script):
            self.skipTest("Repo copy not found")
        with open(repo_script) as f:
            repo_content = f.read()
        with open(HOOK_PATH) as f:
            installed_content = f.read()
        self.assertEqual(
            repo_content, installed_content,
            "Installed hook should match repo copy. Run install-branch-guard.sh to sync.",
        )


# ============================================================================
# Group 2: Craft Repo Dogfooding (real repo, real branch)
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestCraftRepoDogfood(unittest.TestCase):
    """Test branch-guard against the actual craft repo on its current branch."""

    @classmethod
    def setUpClass(cls):
        cls.branch = _get_current_branch()
        cls.cwd = CRAFT_ROOT

    def _payload(self, tool_name: str, **tool_input) -> dict:
        return {
            "tool_name": tool_name,
            "tool_input": tool_input,
            "cwd": self.cwd,
        }

    # --- dev branch tests ---
    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_edit_existing_allowed(self):
        """Editing an existing file on dev is allowed (block-new-code permits this)."""
        result = _run_hook(self._payload(
            "Edit",
            file_path=os.path.join(self.cwd, "CLAUDE.md"),
            old_string="x", new_string="y",
        ))
        self.assertEqual(result.returncode, 0, "Edit existing file on dev should be allowed")

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_write_new_md_allowed(self):
        """Writing a new .md file on dev is allowed."""
        result = _run_hook(self._payload(
            "Write",
            file_path=os.path.join(self.cwd, "docs", "NEW-DOC.md"),
            content="# New doc\n",
        ))
        self.assertEqual(result.returncode, 0, "New .md on dev should be allowed")

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_write_new_py_blocked(self):
        """Writing a new .py file on dev is blocked."""
        result = _run_hook(self._payload(
            "Write",
            file_path=os.path.join(self.cwd, "utils", "brand_new_module.py"),
            content="# new\n",
        ))
        self.assertEqual(result.returncode, 2, "New .py on dev should be blocked")
        self.assertTrue(
            "BRANCH GUARD" in result.stderr or "[CONFIRM]" in result.stderr,
            f"Expected guard output, got: {result.stderr!r}",
        )

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_write_new_sh_blocked(self):
        """Writing a new .sh file on dev is blocked."""
        result = _run_hook(self._payload(
            "Write",
            file_path=os.path.join(self.cwd, "scripts", "brand_new_script.sh"),
            content="#!/bin/bash\n",
        ))
        self.assertEqual(result.returncode, 2, "New .sh on dev should be blocked")

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_write_existing_py_allowed(self):
        """Overwriting an existing .py file on dev is allowed (fixup)."""
        existing = os.path.join(self.cwd, "utils", "complexity_scorer.py")
        if not os.path.isfile(existing):
            self.skipTest("Expected file not found")
        result = _run_hook(self._payload(
            "Write", file_path=existing, content="# updated\n",
        ))
        self.assertEqual(result.returncode, 0, "Overwrite existing .py on dev should be allowed")

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_write_status_file_allowed(self):
        """Writing .STATUS (dot-prefixed, extension-less) on dev is allowed."""
        result = _run_hook(self._payload(
            "Write",
            file_path=os.path.join(self.cwd, ".STATUS"),
            content="status: Active\n",
        ))
        self.assertEqual(result.returncode, 0, ".STATUS should be allowed on dev")

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_write_test_file_allowed(self):
        """Writing new files in tests/ directory on dev is allowed."""
        result = _run_hook(self._payload(
            "Write",
            file_path=os.path.join(self.cwd, "tests", "test_new_feature.py"),
            content="# test\n",
        ))
        self.assertEqual(result.returncode, 0, "New test file on dev should be allowed")

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_bash_git_status_allowed(self):
        """Read-only git commands on dev are allowed."""
        result = _run_hook(self._payload(
            "Bash", command="git status",
        ))
        self.assertEqual(result.returncode, 0, "git status on dev should be allowed")

    @unittest.skipUnless(_get_current_branch() == "dev", "Not on dev branch")
    def test_dev_bash_force_push_blocked(self):
        """Force push on dev is blocked."""
        result = _run_hook(self._payload(
            "Bash", command="git push --force origin dev",
        ))
        self.assertEqual(result.returncode, 2, "Force push on dev should be blocked")
        self.assertTrue(
            "BRANCH GUARD" in result.stderr or "[CONFIRM]" in result.stderr,
            f"Expected guard output, got: {result.stderr!r}",
        )

    # --- feature branch tests (always pass if on feature/*) ---
    @unittest.skipUnless(
        _get_current_branch().startswith("feature/"), "Not on feature branch"
    )
    def test_feature_write_new_py_allowed(self):
        """Writing new .py on a feature branch is always allowed."""
        result = _run_hook(self._payload(
            "Write",
            file_path=os.path.join(self.cwd, "utils", "brand_new.py"),
            content="# new\n",
        ))
        self.assertEqual(result.returncode, 0, "New .py on feature branch should be allowed")


# ============================================================================
# Group 3: Real Claude Code Payload Formats
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestRealPayloadFormats(unittest.TestCase):
    """Test with payload formats matching actual Claude Code tool calls."""

    @classmethod
    def setUpClass(cls):
        cls.cwd = CRAFT_ROOT

    def test_write_payload_with_all_fields(self):
        """Full Write payload with content field (as Claude Code sends it)."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": os.path.join(self.cwd, "CLAUDE.md"),
                "content": "# Updated CLAUDE.md\n",
            },
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        # On dev: overwriting existing .md -> allowed
        self.assertEqual(result.returncode, 0)

    def test_edit_payload_with_replace_all(self):
        """Edit payload with replace_all field (optional parameter)."""
        payload = {
            "tool_name": "Edit",
            "tool_input": {
                "file_path": os.path.join(self.cwd, "CLAUDE.md"),
                "old_string": "old",
                "new_string": "new",
                "replace_all": True,
            },
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_bash_payload_with_description(self):
        """Bash payload includes optional description field."""
        payload = {
            "tool_name": "Bash",
            "tool_input": {
                "command": "ls -la",
                "description": "List files",
            },
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_read_tool_always_allowed(self):
        """Read tool is always allowed (no file modification)."""
        payload = {
            "tool_name": "Read",
            "tool_input": {
                "file_path": os.path.join(self.cwd, "CLAUDE.md"),
            },
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_glob_tool_always_allowed(self):
        """Glob tool is always allowed."""
        payload = {
            "tool_name": "Glob",
            "tool_input": {"pattern": "**/*.py"},
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_grep_tool_always_allowed(self):
        """Grep tool is always allowed."""
        payload = {
            "tool_name": "Grep",
            "tool_input": {"pattern": "def test_", "path": self.cwd},
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_task_tool_always_allowed(self):
        """Task tool is always allowed (spawns subagent)."""
        payload = {
            "tool_name": "Task",
            "tool_input": {"prompt": "Analyze code", "subagent_type": "Explore"},
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0)

    def test_empty_file_path_handled(self):
        """Payload with empty file_path doesn't crash."""
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": "", "content": "x"},
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        # Should not crash (returncode 0 or 2, not 1)
        self.assertIn(result.returncode, [0, 2])

    def test_missing_tool_input_handled(self):
        """Payload without tool_input doesn't crash."""
        payload = {
            "tool_name": "Bash",
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        self.assertIn(result.returncode, [0, 2])

    def test_filePath_camelcase_variant(self):
        """Claude Code sometimes sends filePath instead of file_path."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "filePath": os.path.join(self.cwd, "CLAUDE.md"),
                "content": "# test\n",
            },
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        # Should resolve filePath and allow (existing .md)
        self.assertEqual(result.returncode, 0)


# ============================================================================
# Group 4: Extension Classification (Craft's own file types)
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
@unittest.skipUnless(_get_current_branch() == "dev", "Extension tests need dev branch")
class TestExtensionClassification(unittest.TestCase):
    """Verify code vs non-code classification for craft's actual file extensions."""

    @classmethod
    def setUpClass(cls):
        cls.cwd = CRAFT_ROOT

    def _write_new_file(self, filename: str) -> subprocess.CompletedProcess:
        """Attempt to write a new file that doesn't exist."""
        path = os.path.join(self.cwd, "tmp_test_dir", filename)
        payload = {
            "tool_name": "Write",
            "tool_input": {"file_path": path, "content": "test"},
            "cwd": self.cwd,
        }
        return _run_hook(payload)

    # Code extensions → blocked
    def test_new_py_blocked(self):
        self.assertEqual(self._write_new_file("new.py").returncode, 2)

    def test_new_sh_blocked(self):
        self.assertEqual(self._write_new_file("new.sh").returncode, 2)

    def test_new_js_blocked(self):
        self.assertEqual(self._write_new_file("new.js").returncode, 2)

    def test_new_ts_blocked(self):
        self.assertEqual(self._write_new_file("new.ts").returncode, 2)

    def test_new_json_blocked(self):
        self.assertEqual(self._write_new_file("new.json").returncode, 2)

    def test_new_yml_blocked(self):
        self.assertEqual(self._write_new_file("new.yml").returncode, 2)

    def test_new_yaml_blocked(self):
        self.assertEqual(self._write_new_file("new.yaml").returncode, 2)

    def test_new_toml_blocked(self):
        self.assertEqual(self._write_new_file("new.toml").returncode, 2)

    def test_new_r_blocked(self):
        self.assertEqual(self._write_new_file("new.R").returncode, 2)

    def test_new_zsh_blocked(self):
        self.assertEqual(self._write_new_file("new.zsh").returncode, 2)

    # Non-code extensions → allowed
    def test_new_md_allowed(self):
        self.assertEqual(self._write_new_file("new.md").returncode, 0)

    def test_new_txt_allowed(self):
        self.assertEqual(self._write_new_file("new.txt").returncode, 0)

    def test_new_css_allowed(self):
        self.assertEqual(self._write_new_file("new.css").returncode, 0)

    def test_new_html_allowed(self):
        self.assertEqual(self._write_new_file("new.html").returncode, 0)

    def test_extensionless_allowed(self):
        self.assertEqual(self._write_new_file("Makefile").returncode, 0)

    def test_dotfile_allowed(self):
        self.assertEqual(self._write_new_file(".gitignore").returncode, 0)


# ============================================================================
# Group 5: Error Message Formatting
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
@unittest.skipUnless(_get_current_branch() == "dev", "Error format tests need dev branch")
class TestErrorFormatting(unittest.TestCase):
    """Verify error messages use box-drawing and include actionable guidance."""

    @classmethod
    def setUpClass(cls):
        cls.cwd = CRAFT_ROOT

    def setUp(self):
        # Clear session counter before each test to ensure full verbosity
        session_file = os.path.join(CRAFT_ROOT, ".claude", "guard-session-counts")
        if os.path.isfile(session_file):
            os.remove(session_file)

    def _trigger_block(self) -> str:
        """Trigger a block and return the stderr message."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": os.path.join(self.cwd, "utils", "evil.py"),
                "content": "# bad\n",
            },
            "cwd": self.cwd,
        }
        result = _run_hook(payload)
        # Smart mode v2: blocks with teaching box + [CONFIRM]
        self.assertNotEqual(result.returncode, 0, "New .py on dev should be blocked")
        return result.stderr

    def test_error_has_box_drawing(self):
        """Error messages use Unicode box-drawing characters."""
        msg = self._trigger_block()
        # Check for double-line box corners
        self.assertTrue(
            any(c in msg for c in "╔╗╚╝║═"),
            "Error should use box-drawing characters",
        )

    def test_error_shows_branch_name(self):
        """Error shows which branch triggered the block."""
        msg = self._trigger_block()
        branch = _get_current_branch()
        self.assertIn(branch, msg, "Error should show the branch name")

    def test_error_shows_protection_level(self):
        """Error shows the protection level (smart mode on dev)."""
        msg = self._trigger_block()
        self.assertIn("smart", msg.lower(), "Error should show protection level")

    def test_error_shows_file_path(self):
        """Error shows the file path that was blocked."""
        msg = self._trigger_block()
        self.assertIn("evil.py", msg, "Error should show the blocked file")

    def test_error_shows_remediation(self):
        """Error suggests how to fix the issue."""
        msg = self._trigger_block()
        # Should mention worktree or unprotect as options
        self.assertTrue(
            "worktree" in msg.lower() or "unprotect" in msg.lower(),
            "Error should suggest remediation",
        )


# ============================================================================
# Group 6: Performance
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
class TestPerformance(unittest.TestCase):
    """Hook must be fast — it runs on EVERY tool call."""

    def test_hook_completes_under_200ms(self):
        """Hook should complete in under 200ms for an allow decision."""
        payload = {
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/anything"},
            "cwd": CRAFT_ROOT,
        }
        times = []
        for _ in range(5):
            start = time.perf_counter()
            _run_hook(payload, timeout=5)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg = sum(times) / len(times)
        self.assertLess(avg, 200, f"Average {avg:.0f}ms exceeds 200ms budget")

    def test_block_decision_under_200ms(self):
        """Block decisions should also be fast."""
        branch = _get_current_branch()
        if branch not in ("dev", "main", "master"):
            self.skipTest("Need protected branch for block timing")

        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": os.path.join(CRAFT_ROOT, "tmp_perf", "new.py"),
                "content": "x",
            },
            "cwd": CRAFT_ROOT,
        }
        times = []
        for _ in range(5):
            start = time.perf_counter()
            _run_hook(payload, timeout=5)
            elapsed = (time.perf_counter() - start) * 1000
            times.append(elapsed)

        avg = sum(times) / len(times)
        self.assertLess(avg, 200, f"Block avg {avg:.0f}ms exceeds 200ms budget")


# ============================================================================
# Group 7: Bypass Marker Dogfooding
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
@unittest.skipUnless(_get_current_branch() == "dev", "Bypass tests need dev branch")
class TestBypassDogfood(unittest.TestCase):
    """Test bypass marker in the actual craft repo (creates and cleans up)."""

    def setUp(self):
        self.marker = os.path.join(CRAFT_ROOT, ".claude", "allow-dev-edit")
        self.marker_existed = os.path.isfile(self.marker)

    def tearDown(self):
        # Restore original state
        if not self.marker_existed and os.path.isfile(self.marker):
            os.remove(self.marker)
        elif self.marker_existed and not os.path.isfile(self.marker):
            Path(self.marker).touch()

    def test_bypass_allows_then_block_restores(self):
        """Create marker -> allowed, remove marker -> blocked again."""
        payload = {
            "tool_name": "Write",
            "tool_input": {
                "file_path": os.path.join(CRAFT_ROOT, "utils", "nonexistent.py"),
                "content": "x",
            },
            "cwd": CRAFT_ROOT,
        }

        # Ensure marker does NOT exist
        if os.path.isfile(self.marker):
            os.remove(self.marker)

        # Step 1: blocked
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 2, "Should be blocked without marker")

        # Step 2: create marker -> allowed
        os.makedirs(os.path.dirname(self.marker), exist_ok=True)
        Path(self.marker).touch()
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 0, "Should be allowed with marker")

        # Step 3: remove marker -> blocked again
        os.remove(self.marker)
        result = _run_hook(payload)
        self.assertEqual(result.returncode, 2, "Should be blocked after marker removal")


# ============================================================================
# Group 8: Dry-Run Mode Dogfooding
# ============================================================================
@unittest.skipUnless(os.path.isfile(HOOK_PATH), f"Hook not found: {HOOK_PATH}")
@unittest.skipUnless(_get_current_branch() == "dev", "Dry-run tests need dev branch")
class TestDryRunDogfood(unittest.TestCase):
    """Test dry-run mode in the actual craft repo."""

    def setUp(self):
        self.dryrun_marker = os.path.join(CRAFT_ROOT, ".claude", "branch-guard-dryrun")
        self.existed = os.path.isfile(self.dryrun_marker)

    def tearDown(self):
        if not self.existed and os.path.isfile(self.dryrun_marker):
            os.remove(self.dryrun_marker)
        elif self.existed and not os.path.isfile(self.dryrun_marker):
            os.makedirs(os.path.dirname(self.dryrun_marker), exist_ok=True)
            Path(self.dryrun_marker).touch()

    def test_dryrun_logs_but_allows(self):
        """Dry-run mode logs the block but exits 0 (allow)."""
        # Ensure no bypass marker exists
        bypass = os.path.join(CRAFT_ROOT, ".claude", "allow-dev-edit")
        bypass_existed = os.path.isfile(bypass)
        if bypass_existed:
            os.remove(bypass)

        try:
            # Create dry-run marker
            os.makedirs(os.path.dirname(self.dryrun_marker), exist_ok=True)
            Path(self.dryrun_marker).touch()

            payload = {
                "tool_name": "Write",
                "tool_input": {
                    "file_path": os.path.join(CRAFT_ROOT, "utils", "nonexistent.py"),
                    "content": "x",
                },
                "cwd": CRAFT_ROOT,
            }
            result = _run_hook(payload)
            self.assertEqual(result.returncode, 0, "Dry-run should allow (exit 0)")
            self.assertIn("[DRY-RUN]", result.stderr, "Should log dry-run message")
        finally:
            if bypass_existed:
                Path(bypass).touch()


if __name__ == "__main__":
    unittest.main(verbosity=2)
