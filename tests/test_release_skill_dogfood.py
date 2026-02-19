#!/usr/bin/env python3
"""
Dogfooding Tests: Release Skill
================================
Tests /craft:release skill against the REAL craft repo.
Validates skill registration, version detection, reference files,
and trigger phrase coverage.

Run with: python3 tests/test_release_skill_dogfood.py
"""

import os
import re
import subprocess
import unittest
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.release]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CRAFT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SKILL_DIR = os.path.join(CRAFT_ROOT, "skills", "release")
SKILL_FILE = os.path.join(SKILL_DIR, "SKILL.md")
REFS_DIR = os.path.join(SKILL_DIR, "references")
CHECKLIST_FILE = os.path.join(REFS_DIR, "release-checklist.md")
PRE_RELEASE_SCRIPT = os.path.join(CRAFT_ROOT, "scripts", "pre-release-check.sh")


def _read_skill_frontmatter() -> dict:
    """Parse YAML frontmatter from SKILL.md (simple parser, no deps)."""
    if not os.path.isfile(SKILL_FILE):
        return {}
    with open(SKILL_FILE) as f:
        lines = f.readlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def _detect_version() -> str:
    """Detect version using the same priority as the release skill."""
    # 1. plugin.json
    plugin_json = os.path.join(CRAFT_ROOT, ".claude-plugin", "plugin.json")
    if os.path.isfile(plugin_json):
        import json
        with open(plugin_json) as f:
            data = json.load(f)
        v = data.get("version")
        if v and v != "?":
            return v
    # 2. package.json
    pkg_json = os.path.join(CRAFT_ROOT, "package.json")
    if os.path.isfile(pkg_json):
        import json
        with open(pkg_json) as f:
            data = json.load(f)
        v = data.get("version")
        if v and v != "?":
            return v
    # 3. git tag
    result = subprocess.run(
        ["git", "-C", CRAFT_ROOT, "describe", "--tags", "--abbrev=0"],
        capture_output=True, text=True,
    )
    if result.returncode == 0 and result.stdout.strip():
        return result.stdout.strip()
    return "unknown"


# ============================================================================
# Group 1: Skill Registration
# ============================================================================
class TestSkillRegistration(unittest.TestCase):
    """Verify skill is properly structured and discoverable."""

    def test_skill_file_exists(self):
        """SKILL.md exists in skills/release/."""
        self.assertTrue(os.path.isfile(SKILL_FILE))

    def test_skill_frontmatter_parseable(self):
        """Frontmatter is valid YAML with name and description."""
        fm = _read_skill_frontmatter()
        self.assertIn("name", fm, "Frontmatter should have 'name'")
        self.assertIn("description", fm, "Frontmatter should have 'description'")

    def test_skill_name_is_release(self):
        """Frontmatter name field is 'release'."""
        fm = _read_skill_frontmatter()
        self.assertEqual(fm.get("name"), "release")

    def test_skill_description_not_empty(self):
        """Description is non-empty and substantial."""
        fm = _read_skill_frontmatter()
        desc = fm.get("description", "")
        self.assertGreater(len(desc), 20, "Description should be substantial")

    def test_references_directory_exists(self):
        """references/ subdirectory exists."""
        self.assertTrue(os.path.isdir(REFS_DIR))

    def test_skill_has_pipeline_section(self):
        """SKILL.md contains a Release Pipeline section."""
        with open(SKILL_FILE) as f:
            content = f.read()
        self.assertIn("## Release Pipeline", content)

    def test_skill_has_dry_run_section(self):
        """SKILL.md contains a Dry-Run Mode section."""
        with open(SKILL_FILE) as f:
            content = f.read()
        self.assertIn("## Dry-Run Mode", content)

    def test_skill_has_error_recovery(self):
        """SKILL.md contains an Error Recovery section."""
        with open(SKILL_FILE) as f:
            content = f.read()
        self.assertIn("## Error Recovery", content)


# ============================================================================
# Group 2: Real Repo Validation
# ============================================================================
class TestRealRepoValidation(unittest.TestCase):
    """Test version detection and pre-release on the real craft repo."""

    def test_version_detection_returns_valid_semver(self):
        """Version detection returns a valid semver string."""
        version = _detect_version()
        self.assertNotEqual(version, "unknown", "Should detect a version")
        # Strip leading 'v' for semver check
        v = version.lstrip("v")
        self.assertRegex(v, r"^\d+\.\d+\.\d+", f"Not semver: {version}")

    def test_plugin_json_exists(self):
        """plugin.json exists (primary version source for craft)."""
        path = os.path.join(CRAFT_ROOT, ".claude-plugin", "plugin.json")
        self.assertTrue(os.path.isfile(path))

    def test_plugin_json_has_version(self):
        """plugin.json has a version field."""
        import json
        path = os.path.join(CRAFT_ROOT, ".claude-plugin", "plugin.json")
        with open(path) as f:
            data = json.load(f)
        self.assertIn("version", data)
        self.assertRegex(data["version"], r"^\d+\.\d+\.\d+")

    def test_pre_release_script_exists(self):
        """pre-release-check.sh exists."""
        self.assertTrue(os.path.isfile(PRE_RELEASE_SCRIPT))

    def test_pre_release_script_syntax(self):
        """pre-release-check.sh passes bash -n syntax check."""
        result = subprocess.run(
            ["bash", "-n", PRE_RELEASE_SCRIPT],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, f"Syntax error: {result.stderr}")

    def test_version_matches_claude_md(self):
        """Detected version appears in CLAUDE.md."""
        version = _detect_version().lstrip("v")
        claude_md = os.path.join(CRAFT_ROOT, "CLAUDE.md")
        if not os.path.isfile(claude_md):
            self.skipTest("CLAUDE.md not found")
        with open(claude_md) as f:
            content = f.read()
        self.assertIn(version, content, f"Version {version} not found in CLAUDE.md")


# ============================================================================
# Group 3: Reference File Integrity
# ============================================================================
class TestReferenceFiles(unittest.TestCase):
    """Validate release-checklist.md structure and completeness."""

    def test_checklist_exists(self):
        """release-checklist.md exists in references/."""
        self.assertTrue(os.path.isfile(CHECKLIST_FILE))

    def test_checklist_has_craft_section(self):
        """Checklist has Craft Plugin section."""
        with open(CHECKLIST_FILE) as f:
            content = f.read()
        self.assertIn("Craft Plugin", content)

    def test_checklist_has_python_section(self):
        """Checklist has Python Package section."""
        with open(CHECKLIST_FILE) as f:
            content = f.read()
        self.assertIn("Python Package", content)

    def test_checklist_has_node_section(self):
        """Checklist has Node Package section."""
        with open(CHECKLIST_FILE) as f:
            content = f.read()
        self.assertIn("Node Package", content)

    def test_checklist_has_edge_cases(self):
        """Checklist has edge cases section."""
        with open(CHECKLIST_FILE) as f:
            content = f.read()
        self.assertIn("Edge Cases", content)

    def test_checklist_warns_delete_branch(self):
        """Checklist warns about --delete-branch danger."""
        with open(CHECKLIST_FILE) as f:
            content = f.read()
        self.assertIn("--delete-branch", content)

    def test_checklist_has_version_priority(self):
        """Checklist documents version detection priority."""
        with open(CHECKLIST_FILE) as f:
            content = f.read()
        self.assertIn("Version Detection Priority", content)


# ============================================================================
# Group 4: Trigger Phrase Coverage
# ============================================================================
class TestTriggerPhrases(unittest.TestCase):
    """Verify description contains expected trigger phrases."""

    @classmethod
    def setUpClass(cls):
        cls.description = _read_skill_frontmatter().get("description", "")

    def test_trigger_release(self):
        """Description contains 'release'."""
        self.assertIn("release", self.description.lower())

    def test_trigger_ship_it(self):
        """Description contains 'ship it'."""
        self.assertIn("ship it", self.description.lower())

    def test_trigger_publish(self):
        """Description contains 'publish'."""
        self.assertIn("publish", self.description.lower())

    def test_trigger_bump_version(self):
        """Description contains 'bump version'."""
        self.assertIn("bump version", self.description.lower())

    def test_trigger_cut_a_release(self):
        """Description contains 'cut a release'."""
        self.assertIn("cut a release", self.description.lower())

    def test_trigger_github(self):
        """Description mentions GitHub."""
        self.assertIn("github", self.description.lower())

    def test_description_length(self):
        """Description is at least 50 characters (enough for effective matching)."""
        self.assertGreater(len(self.description), 50)


if __name__ == "__main__":
    unittest.main(verbosity=2)
