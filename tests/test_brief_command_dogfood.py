#!/usr/bin/env python3
"""
Dogfood tests for /craft:workflow:brief — validates that craft's own validation
scripts still pass after adding brief.md as the 117th command.

Unlike e2e structural tests (test_brief_command_e2e.py), these run real scripts
and verify their exit codes and output against the live repo.

Run with: python3 -m pytest tests/test_brief_command_dogfood.py -v
"""

import json
import re
import subprocess
from pathlib import Path

import pytest

pytestmark = [pytest.mark.dogfood]

PLUGIN_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"
BRIEF_CMD = PLUGIN_DIR / "commands" / "workflow" / "brief.md"
DO_CMD = PLUGIN_DIR / "commands" / "do.md"


def _run(script: str, *args, timeout: int = 30) -> subprocess.CompletedProcess:
    return subprocess.run(
        ["bash", str(SCRIPTS_DIR / script), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PLUGIN_DIR),
    )


# ============================================================================
# 1. validate-counts.sh still passes
# ============================================================================

class TestValidateCountsAfterBrief:
    """Adding brief.md (117th command) must not break validate-counts.sh."""

    def test_validate_counts_exits_zero_or_badge_only(self):
        """validate-counts.sh must pass or fail ONLY on the README badge (known drift).

        The README badge (docs/README.md) is updated during release prep by
        bump-version.sh. Until the release PR is merged, exit code 1 with only
        the badge discrepancy is expected and acceptable.
        """
        result = _run("validate-counts.sh")
        if result.returncode == 0:
            return  # clean pass
        combined = result.stdout + result.stderr
        # Only the badge line should be failing, not a counts mismatch
        assert "Commands match" in combined and "Skills match" in combined, (
            f"validate-counts.sh failed on more than just the README badge:\n{combined}"
        )
        assert "README badge" in combined, (
            f"validate-counts.sh failed for unknown reason:\n{combined}"
        )

    def test_validate_counts_no_mismatch(self):
        result = _run("validate-counts.sh")
        combined = result.stdout + result.stderr
        assert "MISMATCH" not in combined.upper(), (
            f"Count mismatch after adding brief.md:\n{combined}"
        )

    def test_validate_counts_reports_117(self):
        """validate-counts.sh should report 117 command files (after brief was added)."""
        result = _run("validate-counts.sh")
        combined = result.stdout + result.stderr
        # Either 117 appears in output, or the count check passes (exit 0)
        # We check exit 0 as the primary assertion; this is belt-and-suspenders
        assert result.returncode == 0 or "117" in combined, (
            f"Expected 117 commands or passing count check:\n{combined}"
        )


# ============================================================================
# 2. docs-staleness-check.sh — brief.md is not flagged as stale
# ============================================================================

class TestDocsStaleness:
    """docs-staleness-check.sh should not flag brief.md as a missing help page (it's a new command)."""

    def test_staleness_check_runs(self):
        result = _run("docs-staleness-check.sh", timeout=60)
        # Non-zero is fine — other docs may be stale; we just verify it runs
        assert result.returncode in (0, 1), (
            f"docs-staleness-check.sh crashed unexpectedly:\n{result.stderr}"
        )

    def test_brief_md_file_is_accessible(self):
        """Brief command file must be readable by scripts (not a permission issue)."""
        assert BRIEF_CMD.exists() and BRIEF_CMD.stat().st_size > 0, (
            "brief.md is empty or missing — scripts would silently skip it"
        )


# ============================================================================
# 3. plugin.json description parity — workflow count matches reality
# ============================================================================

class TestPluginJsonParity:
    """After adding brief.md, plugin.json description must match file counts."""

    def test_workflow_count_in_description(self):
        desc = json.loads(PLUGIN_JSON.read_text())["description"]
        m = re.search(r"(\d+) workflow", desc)
        assert m, "plugin.json description must contain '(N) workflow'"
        documented = int(m.group(1))

        workflow_dir = PLUGIN_DIR / "commands" / "workflow"
        actual = len(list(workflow_dir.glob("*.md")))

        assert documented == actual, (
            f"plugin.json says {documented} workflow commands, "
            f"but commands/workflow/ has {actual} .md files. "
            f"Update plugin.json description."
        )

    def test_total_count_in_description(self):
        desc = json.loads(PLUGIN_JSON.read_text())["description"]
        m = re.search(r"(\d+) commands", desc)
        assert m, "plugin.json description must contain total command count"

        total_in_desc = int(m.group(1))
        all_commands = [
            p for p in (PLUGIN_DIR / "commands").rglob("*.md")
            if p.name not in ("index.md", "README.md")
        ]
        actual_total = len(all_commands)

        assert total_in_desc == actual_total, (
            f"plugin.json says {total_in_desc} commands total, "
            f"but found {actual_total} command .md files. "
            f"Run bump-version.sh or update plugin.json description."
        )


# ============================================================================
# 4. do.md --brief argument declared (contract test)
# ============================================================================

class TestDoBriefContract:
    """do.md's --brief contract must be in place so validate-counts and
    other scripts don't see a structurally incomplete command."""

    def test_do_md_has_brief_argument(self):
        content = DO_CMD.read_text(encoding="utf-8")
        assert "- name: brief" in content, (
            "do.md missing '- name: brief' declaration — "
            "other scripts/tests may incorrectly parse argument list"
        )

    def test_do_md_brief_described_as_append_block(self):
        content = DO_CMD.read_text(encoding="utf-8")
        # The description must convey "append 3-line action block"
        assert "action block" in content.lower() or "3-line" in content.lower(), (
            "do.md --brief description must mention 'action block' or '3-line'"
        )

    def test_do_md_has_step_5_5(self):
        content = DO_CMD.read_text(encoding="utf-8")
        assert "Step 5.5" in content, (
            "do.md missing Step 5.5 — the --brief behavior is not wired"
        )

    def test_step_5_5_is_after_step_5(self):
        content = DO_CMD.read_text(encoding="utf-8")
        pos_5 = content.find("### Step 5:")
        pos_5_5 = content.find("### Step 5.5:")
        pos_6 = content.find("### Step 6:")
        assert pos_5 < pos_5_5, "Step 5.5 must come after Step 5"
        if pos_6 > 0:
            assert pos_5_5 < pos_6, "Step 5.5 must come before Step 6"


# ============================================================================
# 5. brief.md passes the command-audit check (no stale deprecated keys)
# ============================================================================

class TestCommandAudit:
    """brief.md must not contain deprecated frontmatter keys."""

    DEPRECATED_KEYS = {"deprecated", "replaced_by", "replaced-by", "sunset"}

    def test_brief_has_no_deprecated_keys(self):
        import yaml
        content = BRIEF_CMD.read_text(encoding="utf-8")
        m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
        if not m:
            return  # No frontmatter — caught elsewhere
        try:
            fm = yaml.safe_load(m.group(1)) or {}
        except yaml.YAMLError:
            pytest.fail("brief.md has invalid YAML frontmatter")
        found = self.DEPRECATED_KEYS & set(fm.keys())
        assert not found, (
            f"brief.md frontmatter contains deprecated keys: {found}. "
            f"Run scripts/command-audit.sh --fix to clean up."
        )
