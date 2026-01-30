#!/usr/bin/env python3
"""
Unit Tests for BadgeSyncer

Tests badge synchronization orchestration, mismatch detection, diff display,
and file updates.

Coverage target: 90%+
"""

import unittest
from pathlib import Path
import tempfile
import shutil
import sys
import json
import subprocess

# Add utils directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from badge_syncer import BadgeSyncer, BadgeMismatch, BadgeSeverity
from badge_detector import Badge, BadgeType


class TestBadgeSyncer(unittest.TestCase):
    """Test suite for BadgeSyncer class."""

    def setUp(self):
        """Create temporary test directory with git repo."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.syncer = BadgeSyncer(self.test_dir)

        # Create mock plugin.json for version detection
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "2.10.0-dev", "name": "test-plugin"}))

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', 'dev'], cwd=self.test_dir, capture_output=True)
        subprocess.run(
            ['git', 'remote', 'add', 'origin', 'https://github.com/test-user/test-repo'],
            cwd=self.test_dir,
            capture_output=True
        )

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_generate_version_badge(self):
        """Test version badge generation from plugin.json."""
        badge = self.syncer._generate_version_badge()

        self.assertIsNotNone(badge)
        self.assertEqual(badge.type, BadgeType.VERSION)
        self.assertEqual(badge.label, "Version")
        self.assertIn("2.10.0--dev", badge.url)  # Escaped for shields.io
        self.assertIn("blue", badge.url)  # Dev version color

    def test_generate_version_badge_release(self):
        """Test version badge color for release version."""
        # Update to release version
        plugin_json = self.test_dir / ".claude-plugin" / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "1.0.0", "name": "test-plugin"}))

        syncer = BadgeSyncer(self.test_dir)
        badge = syncer._generate_version_badge()

        self.assertIn("brightgreen", badge.url)  # Release version color

    def test_generate_ci_badges(self):
        """Test CI badge generation from workflow files."""
        # Create workflow file
        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        ci_workflow = workflows_dir / "ci.yml"
        ci_workflow.write_text("name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n")

        ci_badges = self.syncer._generate_ci_badges()

        self.assertIn('ci_ci', ci_badges)
        ci_badge = ci_badges['ci_ci']
        self.assertEqual(ci_badge.type, BadgeType.CI_STATUS)
        self.assertIn("actions/workflows/ci.yml", ci_badge.url)
        self.assertIn("branch=dev", ci_badge.url)

    def test_generate_ci_badges_multiple_workflows(self):
        """Test CI badge generation with multiple workflow files."""
        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        (workflows_dir / "ci.yml").write_text("name: CI\n")
        (workflows_dir / "docs-quality.yml").write_text("name: Docs Quality\n")

        ci_badges = self.syncer._generate_ci_badges()

        self.assertEqual(len(ci_badges), 2)
        self.assertIn('ci_ci', ci_badges)
        self.assertIn('ci_docs-quality', ci_badges)  # Uses stem directly (with dash)

    def test_badges_match_identical(self):
        """Test badge matching with identical badges."""
        current = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-1.0.0-blue.svg",
            link_url="https://releases",
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-1.0.0-blue.svg",
            link_url="https://releases",
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        self.assertTrue(self.syncer._badges_match(current, expected))

    def test_badges_match_different_version(self):
        """Test badge matching with different versions."""
        current = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-1.0.0-blue.svg",
            link_url="https://releases",
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-2.0.0-blue.svg",
            link_url="https://releases",
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        self.assertFalse(self.syncer._badges_match(current, expected))

    def test_badges_match_different_branch(self):
        """Test badge matching with different branch parameters."""
        current = Badge(
            type=BadgeType.CI_STATUS,
            label="CI",
            url="https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=main",
            link_url="https://actions",
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.CI_STATUS,
            label="CI",
            url="https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=dev",
            link_url="https://actions",
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        self.assertFalse(self.syncer._badges_match(current, expected))

    def test_determine_severity_version_mismatch(self):
        """Test severity determination for version mismatch (CRITICAL)."""
        current = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-1.0.0-blue.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-2.0.0-blue.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        severity = self.syncer._determine_severity(current, expected)
        self.assertEqual(severity, BadgeSeverity.CRITICAL)

    def test_determine_severity_branch_mismatch(self):
        """Test severity determination for branch mismatch (WARNING)."""
        current = Badge(
            type=BadgeType.CI_STATUS,
            label="CI",
            url="https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=main",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.CI_STATUS,
            label="CI",
            url="https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=dev",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        severity = self.syncer._determine_severity(current, expected)
        self.assertEqual(severity, BadgeSeverity.WARNING)

    def test_determine_severity_coverage_change(self):
        """Test severity determination for coverage change (INFO)."""
        current = Badge(
            type=BadgeType.DOCS_COVERAGE,
            label="Docs",
            url="https://img.shields.io/badge/docs-95%25-green.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.DOCS_COVERAGE,
            label="Docs",
            url="https://img.shields.io/badge/docs-98%25-brightgreen.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        severity = self.syncer._determine_severity(current, expected)
        self.assertEqual(severity, BadgeSeverity.INFO)

    def test_describe_fix_version(self):
        """Test fix description for version update."""
        current = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-1.0.0-blue.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-2.0.0-blue.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        description = self.syncer._describe_fix(current, expected)
        self.assertIn("1.0.0", description)
        self.assertIn("2.0.0", description)

    def test_describe_fix_branch(self):
        """Test fix description for branch parameter update."""
        current = Badge(
            type=BadgeType.CI_STATUS,
            label="CI",
            url="https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=main",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.CI_STATUS,
            label="CI",
            url="https://github.com/user/repo/actions/workflows/ci.yml/badge.svg?branch=dev",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        description = self.syncer._describe_fix(current, expected)
        self.assertIn("branch", description.lower())
        self.assertIn("main", description)
        self.assertIn("dev", description)

    def test_describe_fix_coverage(self):
        """Test fix description for coverage percentage update."""
        current = Badge(
            type=BadgeType.DOCS_COVERAGE,
            label="Docs",
            url="https://img.shields.io/badge/docs-95%25-green.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=1
        )
        expected = Badge(
            type=BadgeType.DOCS_COVERAGE,
            label="Docs",
            url="https://img.shields.io/badge/docs-98%25-brightgreen.svg",
            link_url=None,
            raw_markdown="",
            file_path=Path("README.md"),
            line_number=0
        )

        description = self.syncer._describe_fix(current, expected)
        self.assertIn("95%", description)
        self.assertIn("98%", description)

    def test_find_current_badge(self):
        """Test finding current badge by type and label."""
        readme_badges = [
            Badge(
                type=BadgeType.VERSION,
                label="Version",
                url="https://img.shields.io/badge/version-1.0.0-blue.svg",
                link_url=None,
                raw_markdown="",
                file_path=self.test_dir / "README.md",
                line_number=1
            ),
            Badge(
                type=BadgeType.CI_STATUS,
                label="CI",
                url="https://github.com/user/repo/actions/workflows/ci.yml/badge.svg",
                link_url=None,
                raw_markdown="",
                file_path=self.test_dir / "README.md",
                line_number=2
            )
        ]

        current = {self.test_dir / "README.md": readme_badges}

        found = self.syncer._find_current_badge(current, BadgeType.VERSION, "Version")
        self.assertIsNotNone(found)
        self.assertEqual(found.label, "Version")

        not_found = self.syncer._find_current_badge(current, BadgeType.VERSION, "NonExistent")
        self.assertIsNone(not_found)

    def test_insert_badge_after_title(self):
        """Test badge insertion after markdown title."""
        content = "# Test Project\n\nSome content here.\n"
        badge = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-1.0.0-blue.svg",
            link_url="https://releases",
            raw_markdown="[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://releases)",
            file_path=Path("README.md"),
            line_number=0
        )

        updated = self.syncer._insert_badge(content, badge)

        lines = updated.splitlines()
        self.assertEqual(lines[0], "# Test Project")
        self.assertTrue(lines[1].startswith("[![Version]"))
        self.assertEqual(lines[2], "")
        self.assertEqual(lines[3], "Some content here.")

    def test_insert_badge_empty_file(self):
        """Test badge insertion in empty file."""
        content = ""
        badge = Badge(
            type=BadgeType.VERSION,
            label="Version",
            url="https://img.shields.io/badge/version-1.0.0-blue.svg",
            link_url=None,
            raw_markdown="![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)",
            file_path=Path("README.md"),
            line_number=0
        )

        updated = self.syncer._insert_badge(content, badge)

        self.assertTrue(updated.startswith("![Version]"))

    def test_detect_version_fallback_package_json(self):
        """Test fallback version detection from package.json."""
        # Create isolated directory without plugin.json
        isolated_dir = Path(tempfile.mkdtemp())
        try:
            package_json = isolated_dir / "package.json"
            package_json.write_text(json.dumps({"version": "3.5.7", "name": "test-package"}))

            syncer = BadgeSyncer(isolated_dir)
            version = syncer._detect_version_fallback()

            self.assertEqual(version, "3.5.7")
        finally:
            shutil.rmtree(isolated_dir)

    def test_detect_version_fallback_pyproject_toml(self):
        """Test fallback version detection from pyproject.toml."""
        # Create isolated directory without plugin.json
        isolated_dir = Path(tempfile.mkdtemp())
        try:
            pyproject = isolated_dir / "pyproject.toml"
            pyproject.write_text('[project]\nname = "test"\nversion = "1.2.3"\n')

            syncer = BadgeSyncer(isolated_dir)
            version = syncer._detect_version_fallback()

            self.assertEqual(version, "1.2.3")
        finally:
            shutil.rmtree(isolated_dir)

    def test_get_current_branch(self):
        """Test current branch detection."""
        branch = self.syncer._get_current_branch()
        self.assertEqual(branch, "dev")

    def test_get_repo_url_https(self):
        """Test repository URL extraction (HTTPS)."""
        url = self.syncer._get_repo_url()
        self.assertEqual(url, "https://github.com/test-user/test-repo")

    def test_get_docs_site_url(self):
        """Test documentation site URL generation."""
        url = self.syncer._get_docs_site_url()
        self.assertEqual(url, "https://test-user.github.io/test-repo/")

    def test_calculate_docs_coverage_from_status(self):
        """Test docs coverage calculation from .STATUS file."""
        status_file = self.test_dir / ".STATUS"
        status_file.write_text("progress: 85%\nDocumentation: 98% complete\n")

        coverage = self.syncer._calculate_docs_coverage()
        self.assertEqual(coverage, 98)

    def test_find_mismatches_missing_badge(self):
        """Test mismatch detection when badge is missing."""
        # Create empty README.md so it exists
        (self.test_dir / "README.md").write_text("# Test\n\nNo badges here.\n")

        current = {}  # No badges
        expected = {
            'version': Badge(
                type=BadgeType.VERSION,
                label="Version",
                url="https://img.shields.io/badge/version-1.0.0-blue.svg",
                link_url=None,
                raw_markdown="![Version](...)",
                file_path=Path("README.md"),
                line_number=0
            )
        }

        mismatches = self.syncer._find_mismatches(current, expected, ['README.md'])

        self.assertEqual(len(mismatches), 1)
        self.assertIsNone(mismatches[0].current)
        self.assertEqual(mismatches[0].severity, BadgeSeverity.CRITICAL)
        self.assertIn("Add", mismatches[0].fix_action)

    def test_find_mismatches_outdated_version(self):
        """Test mismatch detection for outdated version badge."""
        current = {
            self.test_dir / "README.md": [
                Badge(
                    type=BadgeType.VERSION,
                    label="Version",
                    url="https://img.shields.io/badge/version-1.0.0-blue.svg",
                    link_url=None,
                    raw_markdown="![Version](...)",
                    file_path=self.test_dir / "README.md",
                    line_number=3
                )
            ]
        }
        expected = {
            'version': Badge(
                type=BadgeType.VERSION,
                label="Version",
                url="https://img.shields.io/badge/version-2.0.0-blue.svg",
                link_url=None,
                raw_markdown="![Version](...)",
                file_path=Path("README.md"),
                line_number=0
            )
        }

        mismatches = self.syncer._find_mismatches(current, expected, ['README.md'])

        self.assertEqual(len(mismatches), 1)
        self.assertIsNotNone(mismatches[0].current)
        self.assertEqual(mismatches[0].severity, BadgeSeverity.CRITICAL)

    def test_sync_badges_dry_run(self):
        """Test badge sync in dry-run mode (no file changes)."""
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![Version](https://img.shields.io/badge/version-1.0.0-blue.svg)](https://releases)\n"
        )

        # Version is now 2.10.0-dev (from plugin.json)
        mismatches = self.syncer.sync_badges(dry_run=True)

        # Should detect version mismatch
        self.assertGreater(len(mismatches), 0)

        # File should not be modified
        content = readme.read_text()
        self.assertIn("version-1.0.0", content)

    def test_get_repo_url_ssh_format(self):
        """Test repository URL conversion from SSH to HTTPS."""
        # Change remote to SSH format
        subprocess.run(
            ['git', 'remote', 'set-url', 'origin', 'git@github.com:test-user/test-repo.git'],
            cwd=self.test_dir,
            capture_output=True
        )

        syncer = BadgeSyncer(self.test_dir)
        url = syncer._get_repo_url()

        self.assertEqual(url, "https://github.com/test-user/test-repo")

    def test_get_repo_url_no_git(self):
        """Test repository URL when not a git repo."""
        no_git_dir = Path(tempfile.mkdtemp())
        try:
            syncer = BadgeSyncer(no_git_dir)
            url = syncer._get_repo_url()
            self.assertIsNone(url)
        finally:
            shutil.rmtree(no_git_dir)

    def test_generate_expected_badges_no_coverage(self):
        """Test expected badge generation without coverage calculation."""
        # Create CI workflow
        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        (workflows_dir / "ci.yml").write_text("name: CI\n")

        expected = self.syncer._generate_expected_badges(calculate_coverage=False)

        # Should have version and CI, but not coverage
        self.assertIn('version', expected)
        self.assertIn('ci_ci', expected)
        self.assertNotIn('docs_coverage', expected)

    def test_badge_mismatch_repr(self):
        """Test BadgeMismatch __repr__ method."""
        mismatch = BadgeMismatch(
            file_path=Path("/tmp/README.md"),
            badge_type=BadgeType.VERSION,
            current=None,
            expected=Badge(
                type=BadgeType.VERSION,
                label="Version",
                url="https://img.shields.io/badge/version-1.0.0-blue.svg",
                link_url=None,
                raw_markdown="",
                file_path=Path("README.md"),
                line_number=0
            ),
            severity=BadgeSeverity.CRITICAL,
            fix_action="Add Version badge"
        )

        repr_str = repr(mismatch)
        self.assertIn("missing", repr_str)
        self.assertIn("version", repr_str)
        self.assertIn("README.md", repr_str)


class TestBadgeSyncerIntegration(unittest.TestCase):
    """Integration tests for badge sync workflow."""

    def setUp(self):
        """Create test directory with complete setup."""
        self.test_dir = Path(tempfile.mkdtemp())

        # Create plugin structure
        plugin_dir = self.test_dir / ".claude-plugin"
        plugin_dir.mkdir(exist_ok=True)
        plugin_json = plugin_dir / "plugin.json"
        plugin_json.write_text(json.dumps({"version": "2.5.0", "name": "test-plugin"}))

        # Create CI workflows
        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)
        (workflows_dir / "ci.yml").write_text("name: CI\non: [push]\n")

        # Create .STATUS file
        status_file = self.test_dir / ".STATUS"
        status_file.write_text("Documentation: 95% complete\n")

        # Initialize git
        subprocess.run(['git', 'init'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', 'dev'], cwd=self.test_dir, capture_output=True)
        subprocess.run(
            ['git', 'remote', 'add', 'origin', 'https://github.com/test/plugin'],
            cwd=self.test_dir,
            capture_output=True
        )

        # Create outdated README
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test Plugin\n"
            "[![Version](https://img.shields.io/badge/version-2.0.0-blue.svg)](https://github.com/test/plugin)\n"
            "[![CI](https://github.com/test/plugin/actions/workflows/ci.yml/badge.svg?branch=main)](https://actions)\n"
        )

        self.syncer = BadgeSyncer(self.test_dir)

    def tearDown(self):
        """Clean up test directory."""
        shutil.rmtree(self.test_dir)

    def test_full_sync_detects_all_mismatches(self):
        """Test full sync detects version, branch, and coverage mismatches."""
        mismatches = self.syncer.sync_badges(dry_run=True)

        # Should find: version outdated (2.0.0 → 2.5.0), branch wrong (main → dev), coverage missing
        self.assertGreaterEqual(len(mismatches), 2)

        # Check version mismatch
        version_mismatches = [m for m in mismatches if m.badge_type == BadgeType.VERSION]
        self.assertEqual(len(version_mismatches), 1)
        self.assertIn("2.0.0", version_mismatches[0].fix_action)
        self.assertIn("2.5.0", version_mismatches[0].fix_action)

        # Check branch mismatch
        ci_mismatches = [m for m in mismatches if m.badge_type == BadgeType.CI_STATUS]
        self.assertGreaterEqual(len(ci_mismatches), 1)


if __name__ == '__main__':
    # Import subprocess for tests
    import subprocess
    unittest.main()
