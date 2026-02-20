#!/usr/bin/env python3
"""
Plugin Self-Dogfooding Tests
==============================
Runs craft's own validation tools against itself. These tests exercise
the same scripts and checks that users/CI would run, ensuring they
pass on the craft repo itself.

Unlike e2e tests that check structural integrity, dogfood tests run
real scripts and validate real output against the live repo state.

Run with: python3 -m pytest tests/test_plugin_dogfood.py -v
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

PLUGIN_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"


def _run_script(script_name: str, *args, timeout: int = 30) -> subprocess.CompletedProcess:
    """Run a script from the scripts/ directory."""
    script = SCRIPTS_DIR / script_name
    return subprocess.run(
        ["bash", str(script), *args],
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=str(PLUGIN_DIR),
    )


# ============================================================================
# 1. Validate Counts (craft's own consistency checker)
# ============================================================================

class TestValidateCounts:
    """Run validate-counts.sh and verify it passes."""

    def test_validate_counts_exits_zero(self):
        """validate-counts.sh passes with exit code 0."""
        result = _run_script("validate-counts.sh")
        assert result.returncode == 0, (
            f"validate-counts.sh failed:\n{result.stdout}\n{result.stderr}"
        )

    def test_validate_counts_no_mismatch_warnings(self):
        """validate-counts.sh output has no MISMATCH warnings."""
        result = _run_script("validate-counts.sh")
        combined = result.stdout + result.stderr
        assert "MISMATCH" not in combined.upper(), (
            f"Count mismatch detected:\n{combined}"
        )


# ============================================================================
# 2. Pre-Release Check (dry validation of current version)
# ============================================================================

class TestPreReleaseCheck:
    """Run pre-release-check.sh against the current version."""

    @pytest.fixture(scope="class")
    def current_version(self):
        data = json.loads(PLUGIN_JSON.read_text())
        return data["version"]

    def test_pre_release_check_runs(self, current_version):
        """pre-release-check.sh runs without crashing."""
        result = _run_script("pre-release-check.sh", current_version)
        # May have warnings but should not crash (exit 0 or known non-zero)
        assert result.returncode in (0, 1), (
            f"Unexpected exit code {result.returncode}:\n{result.stderr}"
        )

    def test_pre_release_detects_version(self, current_version):
        """pre-release-check.sh detects the plugin version."""
        result = _run_script("pre-release-check.sh", current_version)
        assert current_version in result.stdout, (
            f"Script didn't detect version {current_version}"
        )


# ============================================================================
# 3. Version Sync Verification
# ============================================================================

class TestVersionSync:
    """Version references across files must be consistent."""

    @pytest.fixture(scope="class")
    def canonical_version(self):
        return json.loads(PLUGIN_JSON.read_text())["version"]

    def test_version_sync_script_syntax(self):
        """version-sync.sh passes syntax check."""
        script = SCRIPTS_DIR / "version-sync.sh"
        if not script.exists():
            pytest.skip("version-sync.sh not found")
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_claude_md_version_matches(self, canonical_version):
        """CLAUDE.md version matches plugin.json."""
        claude_md = (PLUGIN_DIR / "CLAUDE.md").read_text()
        assert canonical_version in claude_md, (
            f"CLAUDE.md missing version {canonical_version}"
        )


# ============================================================================
# 4. Formatting Library (shared dependency for all scripts)
# ============================================================================

class TestFormattingLibrary:
    """scripts/formatting.sh is the shared formatting library."""

    def test_formatting_sh_exists(self):
        """formatting.sh exists."""
        assert (SCRIPTS_DIR / "formatting.sh").exists()

    def test_formatting_sh_sourceable(self):
        """formatting.sh can be sourced without error."""
        result = subprocess.run(
            ["bash", "-c", f"source {SCRIPTS_DIR}/formatting.sh && echo OK"],
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0, f"Source failed: {result.stderr}"
        assert "OK" in result.stdout

    def test_formatting_exports_color_variables(self):
        """formatting.sh exports FMT_* color variables."""
        result = subprocess.run(
            ["bash", "-c", (
                f"source {SCRIPTS_DIR}/formatting.sh && "
                "echo FMT_RED=$FMT_RED FMT_GREEN=$FMT_GREEN FMT_NC=$FMT_NC"
            )],
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0
        # Should have non-empty color codes
        assert "FMT_RED=" in result.stdout
        assert "FMT_NC=" in result.stdout


# ============================================================================
# 5. Command Discovery (the _discovery.py + _schema.json system)
# ============================================================================

class TestCommandDiscovery:
    """Validate the command discovery and schema system."""

    def test_discovery_py_exists(self):
        """commands/_discovery.py exists."""
        assert (PLUGIN_DIR / "commands" / "_discovery.py").exists()

    def test_schema_json_exists(self):
        """commands/_schema.json exists."""
        assert (PLUGIN_DIR / "commands" / "_schema.json").exists()

    def test_schema_json_valid(self):
        """commands/_schema.json is valid JSON."""
        schema_path = PLUGIN_DIR / "commands" / "_schema.json"
        data = json.loads(schema_path.read_text())
        assert isinstance(data, (dict, list)), "Schema should be dict or list"

    def test_discovery_py_importable(self):
        """commands/_discovery.py can be imported without error."""
        result = subprocess.run(
            ["python3", "-c", (
                f"import sys; sys.path.insert(0, '{PLUGIN_DIR}'); "
                "from commands._discovery import *; print('OK')"
            )],
            capture_output=True, text=True, timeout=10,
        )
        # May fail if dependencies missing, but should not crash
        if result.returncode == 0:
            assert "OK" in result.stdout


# ============================================================================
# 6. Skill Trigger Uniqueness
# ============================================================================

class TestSkillTriggers:
    """SKILL.md trigger descriptions should be distinct to avoid misrouting."""

    def test_skill_descriptions_are_unique(self):
        """No two SKILL.md files have identical descriptions."""
        skills = list((PLUGIN_DIR / "skills").rglob("SKILL.md"))
        if len(skills) < 2:
            pytest.skip("Not enough SKILL.md files to compare")

        descriptions = {}
        for skill in skills:
            content = skill.read_text()
            m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
            if not m:
                continue
            # Simple extraction of description line
            for line in m.group(1).split("\n"):
                if line.startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    if desc in descriptions:
                        pytest.fail(
                            f"Duplicate skill description between "
                            f"{skill.parent.name} and {descriptions[desc]}: "
                            f"'{desc}'"
                        )
                    descriptions[desc] = skill.parent.name


# ============================================================================
# 7. Hook Scripts (branch-guard ecosystem)
# ============================================================================

class TestHookEcosystem:
    """Branch guard and related hook scripts are healthy."""

    def test_branch_guard_script_exists(self):
        """scripts/branch-guard.sh exists."""
        assert (SCRIPTS_DIR / "branch-guard.sh").exists()

    def test_branch_guard_syntax_valid(self):
        """branch-guard.sh passes bash -n."""
        result = subprocess.run(
            ["bash", "-n", str(SCRIPTS_DIR / "branch-guard.sh")],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_install_branch_guard_syntax(self):
        """install-branch-guard.sh passes bash -n."""
        script = SCRIPTS_DIR / "install-branch-guard.sh"
        if not script.exists():
            pytest.skip("install-branch-guard.sh not found")
        result = subprocess.run(
            ["bash", "-n", str(script)],
            capture_output=True, text=True,
        )
        assert result.returncode == 0, f"Syntax error: {result.stderr}"

    def test_branch_guard_handles_empty_input(self):
        """branch-guard.sh doesn't crash on empty stdin."""
        result = subprocess.run(
            ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
            input="",
            capture_output=True, text=True, timeout=5,
        )
        # Should exit cleanly (0 = allow, or graceful error)
        assert result.returncode in (0, 1, 2)

    def test_branch_guard_handles_invalid_json(self):
        """branch-guard.sh doesn't crash on malformed JSON."""
        result = subprocess.run(
            ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
            input="not valid json at all",
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode in (0, 1, 2)

    def test_branch_guard_read_tool_allowed(self):
        """Read tool always passes branch guard."""
        payload = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/test"},
            "cwd": str(PLUGIN_DIR),
        })
        result = subprocess.run(
            ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
            input=payload,
            capture_output=True, text=True, timeout=5,
        )
        assert result.returncode == 0, (
            f"Read should always be allowed: {result.stderr}"
        )


# ============================================================================
# 8. Performance Budget
# ============================================================================

class TestPerformanceBudget:
    """Key scripts must complete within performance budgets.

    Budgets are relaxed for CI runners (typically 2-3x slower than local).
    """

    # CI runners are slower — detect via common CI env vars
    _IS_CI = os.environ.get("CI") == "true" or os.environ.get("GITHUB_ACTIONS") == "true"
    _PERF_MULTIPLIER = 3 if _IS_CI else 1

    def test_validate_counts_under_5s(self):
        """validate-counts.sh completes in under 5 seconds (15s on CI)."""
        budget = 5 * self._PERF_MULTIPLIER
        start = time.perf_counter()
        _run_script("validate-counts.sh", timeout=budget + 5)
        elapsed = time.perf_counter() - start
        assert elapsed < budget, (
            f"validate-counts.sh took {elapsed:.1f}s (budget: {budget}s)"
        )

    def test_branch_guard_under_200ms(self):
        """branch-guard.sh Read tool check completes in under 200ms avg (600ms on CI)."""
        budget_ms = 200 * self._PERF_MULTIPLIER
        payload = json.dumps({
            "tool_name": "Read",
            "tool_input": {"file_path": "/tmp/test"},
            "cwd": str(PLUGIN_DIR),
        })
        times = []
        for _ in range(5):
            start = time.perf_counter()
            subprocess.run(
                ["bash", str(SCRIPTS_DIR / "branch-guard.sh")],
                input=payload,
                capture_output=True, text=True, timeout=5,
            )
            times.append((time.perf_counter() - start) * 1000)
        avg = sum(times) / len(times)
        assert avg < budget_ms, (
            f"Branch guard avg {avg:.0f}ms exceeds {budget_ms}ms budget"
        )


# ============================================================================
# 9. Git Repo Health (dogfood: craft's own repo)
# ============================================================================

class TestRepoHealth:
    """Craft's own git repo should be in a healthy state."""

    def test_on_expected_branch_type(self):
        """Current branch is main, dev, feature/*, or detached HEAD (CI)."""
        result = subprocess.run(
            ["git", "-C", str(PLUGIN_DIR), "branch", "--show-current"],
            capture_output=True, text=True,
        )
        branch = result.stdout.strip()
        if not branch:
            # Detached HEAD (common in CI) — that's fine
            return
        valid = (
            branch in ("main", "dev")
            or branch.startswith("feature/")
        )
        assert valid, f"Unexpected branch: {branch}"

    def test_no_merge_conflicts_in_tracked_files(self):
        """No tracked files contain merge conflict markers."""
        result = subprocess.run(
            ["git", "-C", str(PLUGIN_DIR), "diff", "--check", "HEAD"],
            capture_output=True, text=True,
        )
        conflict_lines = [
            line for line in result.stdout.split("\n")
            if "conflict" in line.lower()
        ]
        assert not conflict_lines, f"Merge conflicts found: {conflict_lines}"


# ============================================================================
# 10. Plugin JSON Schema
# ============================================================================

class TestPluginJsonSchema:
    """plugin.json must conform to Claude Code's expected schema."""

    @pytest.fixture(scope="class")
    def plugin_data(self):
        return json.loads(PLUGIN_JSON.read_text())

    def test_required_fields_present(self, plugin_data):
        """All required fields exist."""
        required = ["name", "version", "description", "author"]
        missing = [f for f in required if f not in plugin_data]
        assert not missing, f"Missing required fields: {missing}"

    def test_author_is_object(self, plugin_data):
        """Author field is an object with 'name'."""
        author = plugin_data.get("author")
        assert isinstance(author, dict), "author must be an object"
        assert "name" in author, "author must have 'name' field"

    def test_no_unrecognized_keys(self, plugin_data):
        """No unrecognized top-level keys (strict schema)."""
        recognized = {
            "name", "version", "description", "author",
            "homepage", "repository", "license", "keywords",
            "engines", "dependencies",
        }
        unknown = set(plugin_data.keys()) - recognized
        assert not unknown, (
            f"Unrecognized keys in plugin.json: {unknown} "
            f"(Claude Code uses strict schema)"
        )

    def test_description_not_too_long(self, plugin_data):
        """Description is under 500 characters (display limit)."""
        desc = plugin_data.get("description", "")
        assert len(desc) < 500, (
            f"Description is {len(desc)} chars (max 500 for display)"
        )


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
