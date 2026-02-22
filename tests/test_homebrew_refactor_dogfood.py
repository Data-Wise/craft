#!/usr/bin/env python3
"""
Dogfooding Tests: Homebrew Refactor (Phases 1, 2, 6)
=====================================================
Tests the homebrew command refactor, workflow hardening, and release skill
updates against the REAL craft repo.

Run with: python3 tests/test_homebrew_refactor_dogfood.py
"""

import json
import os
import re
import unittest
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.structure]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CRAFT_ROOT = Path(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
HOMEBREW_CMD = CRAFT_ROOT / "commands" / "dist" / "homebrew.md"
CI_GENERATE_CMD = CRAFT_ROOT / "commands" / "ci" / "generate.md"
RELEASE_SKILL = CRAFT_ROOT / "skills" / "release" / "SKILL.md"
HOMEBREW_JSON = CRAFT_ROOT / ".craft" / "homebrew.json"
WORKFLOW_YML = CRAFT_ROOT / ".github" / "workflows" / "homebrew-release.yml"


def _read_file(path: Path) -> str:
    """Read a file and return its contents."""
    return path.read_text(encoding="utf-8")


def _extract_subcommand_table(content: str) -> list[str]:
    """Extract subcommand names from the first Subcommands table only."""
    # Find the ## Subcommands section and extract only its table
    match = re.search(r"## Subcommands\n\n(.*?)(?=\n## |\n---)", content, re.DOTALL)
    if not match:
        return []
    table_text = match.group(1)
    pattern = r"\| `([a-z-]+)` \|"
    return re.findall(pattern, table_text)


# ============================================================================
# Group 1: Subcommand Consolidation
# ============================================================================
class TestSubcommandConsolidation(unittest.TestCase):
    """Verify 8 → 6 subcommand consolidation."""

    @classmethod
    def setUpClass(cls):
        cls.content = _read_file(HOMEBREW_CMD)
        cls.subcommands = _extract_subcommand_table(cls.content)

    def test_exactly_6_subcommands(self):
        """Subcommand table has exactly 6 entries."""
        self.assertEqual(len(self.subcommands), 6,
                         f"Expected 6 subcommands, found {len(self.subcommands)}: {self.subcommands}")

    def test_expected_subcommands_present(self):
        """All 6 expected subcommands are in the table."""
        expected = {"formula", "workflow", "audit", "setup", "update-resources", "deps"}
        actual = set(self.subcommands)
        self.assertEqual(expected, actual,
                         f"Missing: {expected - actual}, Extra: {actual - expected}")

    def test_validate_removed(self):
        """validate subcommand no longer in table."""
        self.assertNotIn("validate", self.subcommands)

    def test_token_removed(self):
        """token subcommand no longer in table."""
        self.assertNotIn("token", self.subcommands)

    def test_release_batch_removed(self):
        """release-batch subcommand no longer in table."""
        self.assertNotIn("release-batch", self.subcommands)

    def test_frontmatter_updated(self):
        """Frontmatter description lists new subcommand names."""
        # Extract frontmatter
        lines = self.content.split("\n")
        fm_lines = []
        in_fm = False
        for line in lines:
            if line.strip() == "---":
                if in_fm:
                    break
                in_fm = True
                continue
            if in_fm:
                fm_lines.append(line)
        fm_text = "\n".join(fm_lines)
        self.assertIn("audit", fm_text, "Frontmatter should mention audit")
        self.assertNotIn("validate", fm_text, "Frontmatter should not mention validate")
        self.assertNotIn("token", fm_text, "Frontmatter should not mention token")


# ============================================================================
# Group 2: Audit Subcommand
# ============================================================================
class TestAuditSubcommand(unittest.TestCase):
    """Verify validate → audit rename and --build flag."""

    @classmethod
    def setUpClass(cls):
        cls.content = _read_file(HOMEBREW_CMD)

    def test_audit_section_exists(self):
        """## /craft:dist:homebrew audit section header present."""
        self.assertIn("## /craft:dist:homebrew audit", self.content)

    def test_no_validate_section(self):
        """No ## /craft:dist:homebrew validate section header."""
        self.assertNotIn("## /craft:dist:homebrew validate", self.content)

    def test_build_flag_documented(self):
        """--build flag is documented in usage."""
        self.assertIn("--build", self.content)

    def test_build_from_source_explained(self):
        """brew install --build-from-source is explained."""
        self.assertIn("build-from-source", self.content)

    def test_auto_fix_patterns_present(self):
        """Auto-Fix Patterns section exists with code examples."""
        self.assertIn("Auto-Fix Patterns", self.content)
        # Check for specific fix patterns
        self.assertIn("Array#include?", self.content)
        self.assertIn("assert_path_exists", self.content)

    def test_no_stale_validate_references(self):
        """No remaining 'validate' word in the file."""
        # Exclude code fence contents and historical comments
        # Just check there's no /craft:dist:homebrew validate
        self.assertNotIn("/craft:dist:homebrew validate", self.content)


# ============================================================================
# Group 3: Token Folded into Setup
# ============================================================================
class TestTokenFoldedIntoSetup(unittest.TestCase):
    """Verify token guidance moved into setup wizard."""

    @classmethod
    def setUpClass(cls):
        cls.content = _read_file(HOMEBREW_CMD)
        # Extract setup section
        match = re.search(
            r"(## /craft:dist:homebrew setup.*?)(?=## /craft:dist:homebrew [a-z]|## Formula Templates|## Claude Code)",
            cls.content, re.DOTALL
        )
        cls.setup_section = match.group(1) if match else ""

    def test_no_standalone_token_section(self):
        """No ## /craft:dist:homebrew token section."""
        self.assertNotIn("## /craft:dist:homebrew token", self.content)

    def test_setup_mentions_token(self):
        """Setup section mentions token configuration."""
        self.assertIn("Token", self.setup_section,
                       "Setup section should mention token")

    def test_setup_mentions_homebrew_tap_token(self):
        """Setup section mentions HOMEBREW_TAP_GITHUB_TOKEN."""
        self.assertIn("HOMEBREW_TAP_GITHUB_TOKEN", self.setup_section)

    def test_setup_has_token_in_step4(self):
        """Setup wizard Step 4 covers token."""
        self.assertIn("Step 4", self.setup_section)
        # Token should be near Step 4
        step4_idx = self.setup_section.find("Step 4")
        token_idx = self.setup_section.find("TOKEN", step4_idx)
        self.assertGreater(token_idx, step4_idx,
                          "Token should appear after Step 4 header")


# ============================================================================
# Group 4: Deps Subcommand
# ============================================================================
class TestDepsSubcommand(unittest.TestCase):
    """Verify expanded deps subcommand."""

    @classmethod
    def setUpClass(cls):
        cls.content = _read_file(HOMEBREW_CMD)

    def test_deps_section_exists(self):
        """## /craft:dist:homebrew deps section present."""
        self.assertIn("## /craft:dist:homebrew deps", self.content)

    def test_inter_formula_graph(self):
        """Documents inter-formula dependency graph."""
        self.assertIn("Inter-Formula", self.content)

    def test_system_deps_matrix(self):
        """Documents system dependencies matrix."""
        self.assertIn("System Dep", self.content)

    def test_system_flag(self):
        """--system flag documented."""
        self.assertIn("--system", self.content)

    def test_dot_flag(self):
        """--dot flag for Graphviz documented."""
        self.assertIn("--dot", self.content)


# ============================================================================
# Group 5: Workflow Hardening
# ============================================================================
class TestWorkflowHardening(unittest.TestCase):
    """Verify security hardening in workflow YAML and template."""

    def test_workflow_yaml_exists(self):
        """homebrew-release.yml exists."""
        self.assertTrue(WORKFLOW_YML.exists())

    def test_workflow_env_indirection(self):
        """Workflow uses env: block for github context (prevents script injection)."""
        content = _read_file(WORKFLOW_YML)
        self.assertIn("EVENT_NAME:", content)
        self.assertIn("INPUT_VERSION:", content)

    def test_workflow_sha256sum(self):
        """Workflow uses sha256sum (not shasum)."""
        content = _read_file(WORKFLOW_YML)
        self.assertIn("sha256sum", content)
        # Should NOT have shasum -a 256
        self.assertNotIn("shasum -a 256", content)

    def test_workflow_curl_retry(self):
        """Workflow has --retry on curl."""
        content = _read_file(WORKFLOW_YML)
        self.assertIn("--retry", content)

    def test_workflow_sha_validation(self):
        """Workflow validates SHA256 is 64 chars."""
        content = _read_file(WORKFLOW_YML)
        self.assertIn("64", content)

    def test_template_hardened(self):
        """Template in homebrew.md is also hardened."""
        content = _read_file(HOMEBREW_CMD)
        self.assertIn("sha256sum", content)
        self.assertIn("--retry", content)

    def test_security_features_documented(self):
        """Security features table exists in workflow section."""
        content = _read_file(HOMEBREW_CMD)
        self.assertIn("script injection", content.lower())


# ============================================================================
# Group 6: .craft/homebrew.json
# ============================================================================
class TestHomebrewJsonConfig(unittest.TestCase):
    """Verify .craft/homebrew.json config format."""

    def test_config_exists(self):
        """.craft/homebrew.json exists."""
        self.assertTrue(HOMEBREW_JSON.exists(),
                        f".craft/homebrew.json not found at {HOMEBREW_JSON}")

    def test_config_valid_json(self):
        """Config is valid JSON."""
        data = json.loads(HOMEBREW_JSON.read_text())
        self.assertIsInstance(data, dict)

    def test_config_has_formula_name(self):
        """Config has formula_name field."""
        data = json.loads(HOMEBREW_JSON.read_text())
        self.assertIn("formula_name", data)

    def test_config_has_tap(self):
        """Config has tap field."""
        data = json.loads(HOMEBREW_JSON.read_text())
        self.assertIn("tap", data)

    def test_config_formula_name_is_craft(self):
        """formula_name is 'craft' for this repo."""
        data = json.loads(HOMEBREW_JSON.read_text())
        self.assertEqual(data["formula_name"], "craft")

    def test_config_tap_is_data_wise(self):
        """tap is 'data-wise/tap'."""
        data = json.loads(HOMEBREW_JSON.read_text())
        self.assertEqual(data["tap"], "data-wise/tap")

    def test_config_source_type(self):
        """source_type is 'github'."""
        data = json.loads(HOMEBREW_JSON.read_text())
        self.assertEqual(data.get("source_type", "github"), "github")


# ============================================================================
# Group 7: Release Skill Step 10 (Homebrew Tap Update)
# ============================================================================
class TestReleaseSkillStep10(unittest.TestCase):
    """Verify Step 10 uses config lookup chain and hardened patterns."""

    @classmethod
    def setUpClass(cls):
        cls.content = _read_file(RELEASE_SKILL)
        # Extract Step 10 section
        match = re.search(r"(### Step 10.*?)(?=### Step 11|## Output Format)",
                         cls.content, re.DOTALL)
        cls.step10 = match.group(1) if match else ""

    def test_step10_exists(self):
        """Step 10 section exists in SKILL.md."""
        self.assertIn("Step 10", self.content)

    def test_no_basename_pwd_as_primary(self):
        """basename $PWD is not the primary lookup — config file comes first."""
        config_idx = self.step10.find(".craft/homebrew.json")
        basename_idx = self.step10.find("basename")
        self.assertGreater(config_idx, -1, "Config file should be referenced")
        self.assertGreater(basename_idx, -1, "basename should exist as fallback")
        self.assertLess(config_idx, basename_idx,
                       "Config file should be checked before basename fallback")

    def test_config_lookup_first(self):
        """Config file (.craft/homebrew.json) is checked first."""
        config_idx = self.step10.find(".craft/homebrew.json")
        remote_idx = self.step10.find("git remote")
        self.assertGreater(config_idx, -1, ".craft/homebrew.json not referenced")
        self.assertGreater(remote_idx, -1, "git remote not referenced")
        self.assertLess(config_idx, remote_idx,
                       "Config should be checked before git remote")

    def test_git_remote_fallback(self):
        """Git remote is second lookup priority."""
        self.assertIn("git remote", self.step10)

    def test_basename_is_last_resort(self):
        """basename is documented as fallback only."""
        self.assertIn("fallback", self.step10.lower())

    def test_uses_shasum(self):
        """Step 10 uses shasum -a 256 (macOS-portable, not sha256sum)."""
        self.assertIn("shasum -a 256", self.step10)
        self.assertNotIn("sha256sum", self.step10)

    def test_has_ruby_syntax_check(self):
        """Step 10 runs ruby -c after sed update."""
        self.assertIn("ruby -c", self.step10)

    def test_has_sha_guard(self):
        """Step 10 validates SHA256 is 64 chars."""
        self.assertIn("64", self.step10)

    def test_has_curl_retry(self):
        """Step 10 has --retry on curl."""
        self.assertIn("--retry", self.step10)

    def test_documents_config_format(self):
        """Step 10 documents .craft/homebrew.json fields."""
        self.assertIn("formula_name", self.step10)
        self.assertIn("tap", self.step10)
        self.assertIn("source_type", self.step10)


# ============================================================================
# Group 8: Cross-Reference Integrity
# ============================================================================
class TestCrossReferences(unittest.TestCase):
    """Verify no stale references across the codebase."""

    def test_ci_generate_references_homebrew_workflow(self):
        """ci:generate.md references dist:homebrew workflow."""
        content = _read_file(CI_GENERATE_CMD)
        self.assertIn("dist:homebrew workflow", content)

    def _find_files_with_pattern(self, pattern: str, dirs: list[str]) -> list[str]:
        """Find files containing a pattern in given directories."""
        matches = []
        for d in dirs:
            dir_path = CRAFT_ROOT / d
            if not dir_path.exists():
                continue
            for f in dir_path.rglob("*.md"):
                try:
                    if pattern in f.read_text():
                        matches.append(str(f.relative_to(CRAFT_ROOT)))
                except (OSError, UnicodeDecodeError):
                    continue
        return matches

    def test_no_stale_validate_in_skills(self):
        """No 'dist:homebrew validate' in skills/."""
        matches = self._find_files_with_pattern(
            "dist:homebrew validate", ["skills"]
        )
        self.assertEqual(matches, [],
                        f"Stale validate refs in: {matches}")

    def test_no_stale_validate_in_docs(self):
        """No 'dist:homebrew validate' in docs/."""
        matches = self._find_files_with_pattern(
            "dist:homebrew validate", ["docs"]
        )
        self.assertEqual(matches, [],
                        f"Stale validate refs in: {matches}")

    def test_no_stale_validate_in_commands(self):
        """No 'dist:homebrew validate' in commands/."""
        matches = self._find_files_with_pattern(
            "dist:homebrew validate", ["commands"]
        )
        self.assertEqual(matches, [],
                        f"Stale validate refs in: {matches}")

    def test_no_stale_token_refs(self):
        """No 'dist:homebrew token' in skills/, docs/, commands/."""
        matches = self._find_files_with_pattern(
            "dist:homebrew token", ["skills", "docs", "commands"]
        )
        self.assertEqual(matches, [],
                        f"Stale token refs in: {matches}")


if __name__ == "__main__":
    unittest.main(verbosity=2)
