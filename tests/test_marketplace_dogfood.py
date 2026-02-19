#!/usr/bin/env python3
"""
Dogfooding Tests: Marketplace Distribution
============================================
Tests marketplace distribution feature against the REAL craft repo.
Validates marketplace.json, version consistency, command documentation,
and integration with release skill and pre-release checks.

Run with: python3 tests/test_marketplace_dogfood.py
"""

import json
import os
import re
import unittest
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.marketplace]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CRAFT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MARKETPLACE_JSON = os.path.join(CRAFT_ROOT, ".claude-plugin", "marketplace.json")
PLUGIN_JSON = os.path.join(CRAFT_ROOT, ".claude-plugin", "plugin.json")
MKT_COMMAND = os.path.join(CRAFT_ROOT, "commands", "dist", "marketplace.md")
HOMEBREW_COMMAND = os.path.join(CRAFT_ROOT, "commands", "dist", "homebrew.md")
RELEASE_SKILL = os.path.join(CRAFT_ROOT, "skills", "release", "SKILL.md")
PRE_RELEASE_SCRIPT = os.path.join(CRAFT_ROOT, "scripts", "pre-release-check.sh")
README = os.path.join(CRAFT_ROOT, "README.md")


def _read_marketplace_json() -> dict:
    """Parse marketplace.json and return as dict."""
    if not os.path.isfile(MARKETPLACE_JSON):
        return {}
    with open(MARKETPLACE_JSON) as f:
        return json.load(f)


def _read_plugin_json() -> dict:
    """Parse plugin.json and return as dict."""
    if not os.path.isfile(PLUGIN_JSON):
        return {}
    with open(PLUGIN_JSON) as f:
        return json.load(f)


def _read_frontmatter(filepath: str) -> dict:
    """Parse YAML frontmatter from a markdown file (simple parser, no deps)."""
    if not os.path.isfile(filepath):
        return {}
    with open(filepath) as f:
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


def _read_file(filepath: str) -> str:
    """Read a file and return its content, or empty string if missing."""
    if not os.path.isfile(filepath):
        return ""
    with open(filepath) as f:
        return f.read()


# ============================================================================
# Group 1: Marketplace JSON
# ============================================================================
class TestMarketplaceJson(unittest.TestCase):
    """Validate marketplace.json structure and fields."""

    @classmethod
    def setUpClass(cls):
        cls.data = _read_marketplace_json()

    def test_marketplace_json_exists(self):
        """marketplace.json exists in .claude-plugin/."""
        self.assertTrue(os.path.isfile(MARKETPLACE_JSON))

    def test_marketplace_json_valid(self):
        """marketplace.json parses as valid JSON."""
        self.assertIsInstance(self.data, dict)
        self.assertGreater(len(self.data), 0, "marketplace.json should not be empty")

    def test_has_name(self):
        """name field is present and kebab-case."""
        name = self.data.get("name", "")
        self.assertTrue(len(name) > 0, "name field should be present")
        self.assertRegex(name, r"^[a-z0-9]+(-[a-z0-9]+)*$",
                         f"name should be kebab-case, got: {name}")

    def test_has_owner(self):
        """owner.name is present and non-empty."""
        owner = self.data.get("owner", {})
        self.assertIn("name", owner, "owner should have a name field")
        self.assertGreater(len(owner["name"]), 0, "owner.name should be non-empty")

    def test_has_metadata(self):
        """metadata.description and metadata.version are present."""
        meta = self.data.get("metadata", {})
        self.assertIn("description", meta, "metadata should have description")
        self.assertIn("version", meta, "metadata should have version")
        self.assertGreater(len(meta["description"]), 0)
        self.assertGreater(len(meta["version"]), 0)

    def test_has_plugins(self):
        """plugins array is non-empty."""
        plugins = self.data.get("plugins", [])
        self.assertIsInstance(plugins, list)
        self.assertGreater(len(plugins), 0, "plugins array should not be empty")

    def test_plugin_has_source(self):
        """plugins[0].source is a dict with source='github'."""
        plugins = self.data.get("plugins", [])
        if not plugins:
            self.skipTest("No plugins found")
        source = plugins[0].get("source", {})
        self.assertIsInstance(source, dict, "source should be an object, not a string")
        self.assertEqual(source.get("source"), "github",
                         "source.source should be 'github'")

    def test_plugin_has_repo(self):
        """plugins[0].source.repo is non-empty."""
        plugins = self.data.get("plugins", [])
        if not plugins:
            self.skipTest("No plugins found")
        source = plugins[0].get("source", {})
        repo = source.get("repo", "")
        self.assertGreater(len(repo), 0, "source.repo should be non-empty")

    def test_description_length(self):
        """metadata.description is under 100 characters."""
        meta = self.data.get("metadata", {})
        desc = meta.get("description", "")
        self.assertLess(len(desc), 100,
                        f"Description too long ({len(desc)} chars): {desc[:50]}...")

    def test_no_relative_source(self):
        """source is NOT a string (should be object for marketplace)."""
        plugins = self.data.get("plugins", [])
        if not plugins:
            self.skipTest("No plugins found")
        source = plugins[0].get("source")
        self.assertNotIsInstance(source, str,
                                 "source should be an object, not a relative path string")


# ============================================================================
# Group 2: Version Consistency
# ============================================================================
class TestVersionConsistency(unittest.TestCase):
    """Verify versions stay in sync across all files."""

    @classmethod
    def setUpClass(cls):
        cls.mkt = _read_marketplace_json()
        cls.plugin = _read_plugin_json()

    def test_marketplace_matches_plugin(self):
        """metadata.version matches plugin.json version."""
        mkt_version = self.mkt.get("metadata", {}).get("version", "")
        plugin_version = self.plugin.get("version", "")
        self.assertEqual(mkt_version, plugin_version,
                         f"marketplace.json ({mkt_version}) != plugin.json ({plugin_version})")

    def test_plugin_entry_matches(self):
        """plugins[0].version matches plugin.json version."""
        plugins = self.mkt.get("plugins", [])
        if not plugins:
            self.skipTest("No plugins found")
        entry_version = plugins[0].get("version", "")
        plugin_version = self.plugin.get("version", "")
        self.assertEqual(entry_version, plugin_version,
                         f"plugins[0].version ({entry_version}) != plugin.json ({plugin_version})")

    def test_version_in_claude_md(self):
        """Version appears in CLAUDE.md."""
        version = self.plugin.get("version", "")
        if not version:
            self.skipTest("No version in plugin.json")
        claude_md = os.path.join(CRAFT_ROOT, "CLAUDE.md")
        content = _read_file(claude_md)
        if not content:
            self.skipTest("CLAUDE.md not found")
        self.assertIn(version, content,
                      f"Version {version} not found in CLAUDE.md")

    def test_version_in_readme(self):
        """Version appears in README.md."""
        version = self.plugin.get("version", "")
        if not version:
            self.skipTest("No version in plugin.json")
        content = _read_file(README)
        if not content:
            self.skipTest("README.md not found")
        self.assertIn(version, content,
                      f"Version {version} not found in README.md")

    def test_command_count_consistent(self):
        """Count of .md files in commands/ approximates plugin.json description count."""
        desc = self.plugin.get("description", "")
        # Extract number from "109 commands" or similar
        match = re.search(r"(\d+)\s+commands", desc)
        if not match:
            self.skipTest("No command count found in plugin.json description")
        claimed = int(match.group(1))
        # Count actual command files
        commands_dir = os.path.join(CRAFT_ROOT, "commands")
        if not os.path.isdir(commands_dir):
            self.skipTest("commands/ directory not found")
        count = 0
        for root, dirs, files in os.walk(commands_dir):
            for f in files:
                if f.endswith(".md"):
                    count += 1
        # Allow some tolerance (within 20%)
        self.assertGreater(count, claimed * 0.8,
                           f"Too few commands: {count} vs claimed {claimed}")
        self.assertLess(count, claimed * 1.2,
                        f"Too many commands: {count} vs claimed {claimed}")


# ============================================================================
# Group 3: Marketplace Command
# ============================================================================
class TestMarketplaceCommand(unittest.TestCase):
    """Validate the dist:marketplace command file."""

    @classmethod
    def setUpClass(cls):
        cls.content = _read_file(MKT_COMMAND)
        cls.frontmatter = _read_frontmatter(MKT_COMMAND)

    def test_command_file_exists(self):
        """commands/dist/marketplace.md exists."""
        self.assertTrue(os.path.isfile(MKT_COMMAND))

    def test_has_frontmatter(self):
        """Command file starts with --- frontmatter delimiter."""
        self.assertTrue(self.content.startswith("---"),
                        "Command file should start with --- frontmatter")

    def test_frontmatter_has_description(self):
        """Frontmatter contains a description field."""
        self.assertIn("description", self.frontmatter,
                      "Frontmatter should have 'description'")

    def test_frontmatter_has_arguments(self):
        """Frontmatter contains an arguments field."""
        self.assertIn("arguments", self.frontmatter,
                      "Frontmatter should have 'arguments'")

    def test_documents_init(self):
        """Command documents the 'init' subcommand."""
        self.assertIn("init", self.content,
                      "Command should document 'init' subcommand")

    def test_documents_validate(self):
        """Command documents the 'validate' subcommand."""
        self.assertIn("validate", self.content,
                      "Command should document 'validate' subcommand")

    def test_documents_test(self):
        """Command documents the 'test' subcommand."""
        self.assertIn("test", self.content,
                      "Command should document 'test' subcommand")

    def test_documents_publish(self):
        """Command documents the 'publish' subcommand."""
        self.assertIn("publish", self.content,
                      "Command should document 'publish' subcommand")


# ============================================================================
# Group 4: Integration
# ============================================================================
class TestIntegration(unittest.TestCase):
    """Cross-cutting integration checks across distribution features."""

    def test_homebrew_has_plugin_autodetect(self):
        """Homebrew command mentions Claude Code Plugin detection."""
        content = _read_file(HOMEBREW_COMMAND)
        if not content:
            self.skipTest("commands/dist/homebrew.md not found")
        self.assertIn("Claude Code Plugin", content,
                      "Homebrew command should reference Claude Code Plugin")

    def test_release_skill_has_marketplace_step(self):
        """Release skill mentions marketplace in its pipeline."""
        content = _read_file(RELEASE_SKILL)
        if not content:
            self.skipTest("skills/release/SKILL.md not found")
        self.assertIn("marketplace", content.lower(),
                      "Release skill should mention marketplace step")

    def test_release_skill_has_tap_update(self):
        """Release skill references Homebrew tap update step."""
        content = _read_file(RELEASE_SKILL)
        if not content:
            self.skipTest("skills/release/SKILL.md not found")
        has_step = "8.5" in content or "tap" in content.lower()
        self.assertTrue(has_step,
                        "Release skill should reference tap update (step 8.5 or 'tap')")

    def test_pre_release_checks_marketplace(self):
        """Pre-release script validates marketplace.json."""
        content = _read_file(PRE_RELEASE_SCRIPT)
        if not content:
            self.skipTest("scripts/pre-release-check.sh not found")
        self.assertIn("marketplace", content.lower(),
                      "Pre-release script should check marketplace.json")

    def test_readme_recommends_marketplace(self):
        """README recommends Marketplace as an installation option."""
        content = _read_file(README)
        if not content:
            self.skipTest("README.md not found")
        self.assertIn("Marketplace", content,
                      "README should recommend Marketplace installation")


if __name__ == "__main__":
    unittest.main(verbosity=2)
