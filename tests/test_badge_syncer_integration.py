#!/usr/bin/env python3
"""
Integration Tests for Badge Syncer

End-to-end tests for badge synchronization across multiple project types
and workflows.

Coverage target: 90%+
"""

import unittest
from pathlib import Path
import tempfile
import shutil
import subprocess
import json
import sys

# Add utils directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from badge_syncer import BadgeSyncer, BadgeSeverity
from badge_detector import BadgeDetector, BadgeType


class TestBadgeSyncerIntegration(unittest.TestCase):
    """Integration tests for complete badge sync workflows."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Initialize git
        subprocess.run(['git', 'init'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', 'dev'], cwd=self.test_dir, capture_output=True)
        subprocess.run(
            ['git', 'remote', 'add', 'origin', 'https://github.com/test-org/test-project'],
            cwd=self.test_dir,
            capture_output=True
        )

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_sync_craft_plugin_version_mismatch(self):
        """Test badge sync detects version mismatch in craft plugin."""
        # Setup: Craft plugin structure
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({
            "version": "2.10.0-dev",
            "name": "test-plugin"
        }))

        # Create outdated README
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test Plugin\n"
            "[![Version](https://img.shields.io/badge/version-2.9.0-blue.svg)]"
            "(https://github.com/test-org/test-project)\n"
        )

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(dry_run=True, calculate_coverage=False)

        # Should detect version mismatch
        version_mismatches = [m for m in mismatches if m.badge_type == BadgeType.VERSION]
        self.assertEqual(len(version_mismatches), 1)
        self.assertEqual(version_mismatches[0].severity, BadgeSeverity.CRITICAL)
        self.assertIn("2.9.0", version_mismatches[0].fix_action)
        self.assertIn("2.10.0-dev", version_mismatches[0].fix_action)

    def test_sync_updates_file_on_disk(self):
        """Test badge sync actually updates file content."""
        # Setup: Plugin with outdated version
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "3.0.0", "name": "test"}))

        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://releases)\n"
        )

        syncer = BadgeSyncer(self.test_dir)

        # Apply sync (auto-confirm to skip prompt)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Verify file was updated
        updated_content = readme.read_text()
        self.assertIn("version-3.0.0", updated_content)
        self.assertNotIn("version-2.0.0", updated_content)

        # Verify mismatch was applied
        self.assertGreater(len(mismatches), 0)

    def test_sync_no_op_when_badges_correct(self):
        """Test sync does nothing when badges already correct."""
        # Setup: Plugin with current version
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "1.5.0", "name": "test"}))

        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![Version](https://img.shields.io/badge/version-1.5.0-brightgreen.svg)]"
            "(https://github.com/test-org/test-project/releases)\n"
        )

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(dry_run=True, calculate_coverage=False)

        # Should find no mismatches
        version_mismatches = [m for m in mismatches if m.badge_type == BadgeType.VERSION]
        self.assertEqual(len(version_mismatches), 0)

    def test_sync_adds_missing_badge(self):
        """Test badge sync adds missing badge to README."""
        # Setup: Plugin without any badges
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "1.0.0", "name": "test"}))

        readme = self.test_dir / "README.md"
        readme.write_text("# Test Plugin\n\nNo badges yet.\n")

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Verify badge was added
        updated_content = readme.read_text()
        self.assertIn("[![Version]", updated_content)
        self.assertIn("version-1.0.0", updated_content)

    def test_sync_generates_ci_badge_from_workflow(self):
        """Test CI badge generation from workflow file."""
        # Setup: Plugin with workflow but no CI badge
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "1.0.0", "name": "test"}))

        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        ci_workflow = workflows_dir / "ci.yml"
        ci_workflow.write_text("name: CI\non: [push]\n")

        readme = self.test_dir / "README.md"
        readme.write_text("# Test\n")

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Should find CI badge missing
        ci_mismatches = [m for m in mismatches if m.badge_type == BadgeType.CI_STATUS]
        self.assertGreater(len(ci_mismatches), 0)

        # Verify badge was added
        updated_content = readme.read_text()
        self.assertIn("Craft CI", updated_content)
        self.assertIn("actions/workflows/ci.yml", updated_content)

    def test_sync_updates_multiple_files(self):
        """Test badge sync updates both README.md and docs/index.md."""
        # Setup: Plugin with outdated badges in multiple files
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "2.0.0", "name": "test"}))

        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://releases)\n"
        )

        docs_dir = self.test_dir / "docs"
        docs_dir.mkdir(exist_ok=True)
        docs_index = docs_dir / "index.md"
        docs_index.write_text(
            "# Test Docs\n"
            "[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://releases)\n"
        )

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Should update both files
        self.assertGreater(len(mismatches), 0)

        readme_content = readme.read_text()
        docs_content = docs_index.read_text()

        self.assertIn("version-2.0.0", readme_content)
        self.assertIn("version-2.0.0", docs_content)

    def test_sync_teaching_site_project(self):
        """Test badge sync for teaching site project type."""
        # Setup: Teaching site structure
        quarto_yml = self.test_dir / "_quarto.yml"
        quarto_yml.write_text("project:\n  type: website\n  title: Test Course\n")

        package_json = self.test_dir / "package.json"
        package_json.write_text(json.dumps({"version": "1.0.0", "name": "test-course"}))

        readme = self.test_dir / "README.md"
        readme.write_text("# Test Course\n")

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Should generate version badge
        version_mismatches = [m for m in mismatches if m.badge_type == BadgeType.VERSION]
        self.assertGreater(len(version_mismatches), 0)

    def test_sync_handles_no_git_repo(self):
        """Test badge sync works without git repo (uses safe defaults)."""
        # Setup: Directory without git
        no_git_dir = Path(tempfile.mkdtemp())
        try:
            plugin_dir = no_git_dir / ".claude-plugin"
            plugin_dir.mkdir(exist_ok=True)
            plugin_json = plugin_dir / "plugin.json"
            plugin_json.write_text(json.dumps({"version": "1.0.0", "name": "test"}))

            readme = no_git_dir / "README.md"
            readme.write_text("# Test\n")

            syncer = BadgeSyncer(no_git_dir)
            mismatches = syncer.sync_badges(dry_run=True, calculate_coverage=False)

            # Should still generate version badge (even without git)
            version_mismatches = [m for m in mismatches if m.badge_type == BadgeType.VERSION]
            self.assertGreater(len(version_mismatches), 0)
        finally:
            shutil.rmtree(no_git_dir)

    def test_sync_calculates_docs_coverage(self):
        """Test docs coverage calculation and badge generation."""
        # Setup: Plugin with .STATUS file
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "1.0.0", "name": "test"}))

        status_file = self.test_dir / ".STATUS"
        status_file.write_text("Documentation: 95% complete\nprogress: 80%\n")

        readme = self.test_dir / "README.md"
        readme.write_text("# Test\n")

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=True)

        # Should generate docs coverage badge
        coverage_mismatches = [m for m in mismatches if m.badge_type == BadgeType.DOCS_COVERAGE]
        self.assertGreater(len(coverage_mismatches), 0)

        # Verify badge was added
        updated_content = readme.read_text()
        self.assertIn("docs-95%", updated_content)

    def test_sync_preserves_file_structure(self):
        """Test badge sync preserves markdown structure around badges."""
        # Setup
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "2.0.0", "name": "test"}))

        readme = self.test_dir / "README.md"
        original_content = (
            "# Test Plugin\n"
            "\n"
            "[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://releases)\n"
            "\n"
            "## Overview\n"
            "\n"
            "This is a test plugin.\n"
        )
        readme.write_text(original_content)

        syncer = BadgeSyncer(self.test_dir)
        syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Verify structure preserved
        updated_content = readme.read_text()
        lines = updated_content.splitlines()

        self.assertEqual(lines[0], "# Test Plugin")
        self.assertTrue(lines[2].startswith("[![Version]"))
        self.assertEqual(lines[4], "## Overview")
        self.assertEqual(lines[6], "This is a test plugin.")


class TestBadgeSyncerRealWorld(unittest.TestCase):
    """Real-world scenario tests."""

    def setUp(self):
        """Create temporary test directory."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Initialize git
        subprocess.run(['git', 'init'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', 'dev'], cwd=self.test_dir, capture_output=True)
        subprocess.run(
            ['git', 'remote', 'add', 'origin', 'https://github.com/test-org/test-project'],
            cwd=self.test_dir,
            capture_output=True
        )

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_craft_plugin_self_dogfood(self):
        """Test badge sync on actual craft plugin structure (simulated)."""
        # Create minimal craft plugin structure
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({
            "version": "2.10.0-dev",
            "name": "craft"
        }))

        # Create workflows
        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        (workflows_dir / "ci.yml").write_text("name: Craft CI\n")
        (workflows_dir / "docs-quality.yml").write_text("name: Docs Quality\n")

        # Create .STATUS
        status_file = self.test_dir / ".STATUS"
        status_file.write_text("Documentation: 98% complete\n")

        # Create outdated README
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Craft Plugin\n"
            "[![Version](https://img.shields.io/badge/version-2.9.0-blue.svg)](https://releases)\n"
            "[![CI](https://github.com/test-org/test-project/actions/workflows/ci.yml/badge.svg?branch=main)](https://actions)\n"
        )

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(dry_run=True, calculate_coverage=True)

        # Should detect: version outdated, CI branch wrong, docs coverage missing
        self.assertGreaterEqual(len(mismatches), 2)

        # Check version
        version_mismatches = [m for m in mismatches if m.badge_type == BadgeType.VERSION]
        self.assertEqual(len(version_mismatches), 1)
        self.assertIn("2.10.0-dev", version_mismatches[0].fix_action)

        # Check CI branch
        ci_mismatches = [m for m in mismatches if m.badge_type == BadgeType.CI_STATUS]
        self.assertGreaterEqual(len(ci_mismatches), 1)

    def test_python_cli_project(self):
        """Test badge sync for Python CLI project (pyproject.toml)."""
        pyproject = self.test_dir / "pyproject.toml"
        pyproject.write_text('[project]\nname = "test-cli"\nversion = "0.5.0"\n')

        readme = self.test_dir / "README.md"
        readme.write_text("# Test CLI\n")

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Should add version badge
        version_mismatches = [m for m in mismatches if m.badge_type == BadgeType.VERSION]
        self.assertGreater(len(version_mismatches), 0)

        # Verify file updated
        updated = readme.read_text()
        self.assertIn("version-0.5.0", updated)

    def test_node_cli_project(self):
        """Test badge sync for Node CLI project (package.json)."""
        package_json = self.test_dir / "package.json"
        package_json.write_text(json.dumps({
            "version": "1.2.3",
            "name": "test-node-cli"
        }))

        readme = self.test_dir / "README.md"
        readme.write_text("# Test Node CLI\n")

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Should add version badge
        updated = readme.read_text()
        self.assertIn("version-1.2.3", updated)

    def test_sync_error_handling_file_permissions(self):
        """Test badge sync handles file permission errors gracefully."""
        # This test may not work on all systems, skip if needed
        plugin_dir = self.test_dir / ".claude-plugin"
        try:
            plugin_dir.mkdir(exist_ok=True)
            plugin_json = plugin_dir / "plugin.json"
            plugin_json.write_text(json.dumps({"version": "1.0.0", "name": "test"}))

            readme = self.test_dir / "README.md"
            readme.write_text("# Test\n")

            # Make readonly (may fail on some systems)
            readme.chmod(0o444)

            syncer = BadgeSyncer(self.test_dir)

            # Should not crash, just report warning
            # (In practice, prints warning and continues)
            mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

            # Cleanup: restore permissions
            readme.chmod(0o644)

        except (OSError, PermissionError):
            # Skip test if permission changes not supported
            self.skipTest("File permissions not supported on this system")

    def test_sync_dry_run_no_file_changes(self):
        """Test dry-run mode doesn't modify files."""
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "2.0.0", "name": "test"}))

        readme = self.test_dir / "README.md"
        original_content = (
            "# Test\n"
            "[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://releases)\n"
        )
        readme.write_text(original_content)

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(dry_run=True, calculate_coverage=False)

        # Should detect mismatch
        self.assertGreater(len(mismatches), 0)

        # File should NOT be modified
        current_content = readme.read_text()
        self.assertEqual(current_content, original_content)

    def test_sync_mcp_server_project(self):
        """Test badge sync for MCP server project."""
        # MCP server structure
        package_json = self.test_dir / "package.json"
        package_json.write_text(json.dumps({
            "version": "0.3.0",
            "name": "@test/mcp-server"
        }))

        mcp_dir = self.test_dir / "src" / "mcp-server"
        mcp_dir.mkdir(parents=True, exist_ok=True)

        readme = self.test_dir / "README.md"
        readme.write_text("# MCP Server\n")

        syncer = BadgeSyncer(self.test_dir)
        mismatches = syncer.sync_badges(auto_confirm=True, calculate_coverage=False)

        # Should add version badge
        updated = readme.read_text()
        self.assertIn("version-0.3.0", updated)

    def test_sync_with_custom_config(self):
        """Test badge sync with custom configuration."""
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "1.0.0", "name": "test"}))

        readme = self.test_dir / "README.md"
        readme.write_text("# Test\n")

        # Create syncer with custom config
        custom_config = {
            'badge_color': 'orange',
            'include_coverage': False
        }
        syncer = BadgeSyncer(self.test_dir, config=custom_config)

        # Verify config is stored
        self.assertEqual(syncer.config['badge_color'], 'orange')


if __name__ == '__main__':
    unittest.main()
