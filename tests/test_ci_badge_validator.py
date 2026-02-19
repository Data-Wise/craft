#!/usr/bin/env python3
"""
Unit Tests for CIBadgeValidator

Tests CI-specific badge validation for GitHub Actions workflows.

Coverage target: 90%+
"""

import unittest
from pathlib import Path
import tempfile
import shutil
import subprocess
import sys

import pytest

# Add utils directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

from ci_badge_validator import CIBadgeValidator, CIBadgeIssue, format_issues_report

pytestmark = [pytest.mark.integration, pytest.mark.badge]


class TestCIBadgeValidator(unittest.TestCase):
    """Test suite for CIBadgeValidator class."""

    def setUp(self):
        """Create temporary test directory with git repo and workflows."""
        self.test_dir = Path(tempfile.mkdtemp())
        self.validator = CIBadgeValidator(self.test_dir)

        # Initialize git repo
        subprocess.run(['git', 'init'], cwd=self.test_dir, capture_output=True)
        subprocess.run(['git', 'checkout', '-b', 'dev'], cwd=self.test_dir, capture_output=True)
        subprocess.run(
            ['git', 'remote', 'add', 'origin', 'https://github.com/test-user/test-repo'],
            cwd=self.test_dir,
            capture_output=True
        )

        # Create workflows directory
        workflows_dir = self.test_dir / ".github" / "workflows"
        workflows_dir.mkdir(parents=True, exist_ok=True)

        # Create sample workflow
        ci_workflow = workflows_dir / "ci.yml"
        ci_workflow.write_text("name: CI\non: [push]\njobs:\n  test:\n    runs-on: ubuntu-latest\n")

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.test_dir)

    def test_validate_correct_badge(self):
        """Test validation passes for correct CI badge."""
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![CI](https://github.com/test-user/test-repo/actions/workflows/ci.yml/badge.svg?branch=dev)]"
            "(https://github.com/test-user/test-repo/actions/workflows/ci.yml)\n"
        )

        issues = self.validator.validate_badges(branch='dev')

        self.assertEqual(len(issues), 0)

    def test_validate_missing_workflow(self):
        """Test detection of badge pointing to non-existent workflow."""
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![CI](https://github.com/test-user/test-repo/actions/workflows/nonexistent.yml/badge.svg)]"
            "(https://github.com/test-user/test-repo/actions)\n"
        )

        issues = self.validator.validate_badges()

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, 'error')
        self.assertEqual(issues[0].badge_type, 'missing_workflow')
        self.assertIn("nonexistent.yml", issues[0].message)

    def test_validate_wrong_branch(self):
        """Test detection of badge with wrong branch parameter."""
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![CI](https://github.com/test-user/test-repo/actions/workflows/ci.yml/badge.svg?branch=main)]"
            "(https://github.com/test-user/test-repo/actions)\n"
        )

        issues = self.validator.validate_badges(branch='dev')

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, 'warning')
        self.assertEqual(issues[0].badge_type, 'wrong_branch')
        self.assertIn("main", issues[0].message)
        self.assertIn("dev", issues[0].message)

        # Check expected badge is provided
        self.assertIsNotNone(issues[0].expected_badge)
        self.assertIn("branch=dev", issues[0].expected_badge)

    def test_validate_invalid_url_format(self):
        """Test detection of invalid CI badge URL format."""
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![CI](https://invalid-url/badge.svg)](https://actions)\n"
        )

        issues = self.validator.validate_badges()

        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].severity, 'warning')
        self.assertEqual(issues[0].badge_type, 'invalid_format')

    def test_is_ci_badge_by_url(self):
        """Test CI badge detection by GitHub Actions URL."""
        is_ci = self.validator._is_ci_badge(
            "Build",
            "https://github.com/user/repo/actions/workflows/build.yml/badge.svg"
        )
        self.assertTrue(is_ci)

    def test_is_ci_badge_by_label(self):
        """Test CI badge detection by label keywords."""
        test_cases = [
            ("CI Status", "https://example.com/badge.svg", True),
            ("Build Status", "https://example.com/badge.svg", True),
            ("Test Coverage", "https://example.com/badge.svg", True),
            ("Version", "https://example.com/badge.svg", False),
            ("Documentation", "https://example.com/badge.svg", False),
        ]

        for label, url, expected in test_cases:
            with self.subTest(label=label):
                result = self.validator._is_ci_badge(label, url)
                self.assertEqual(result, expected)

    def test_is_valid_ci_badge_url(self):
        """Test CI badge URL format validation."""
        valid_urls = [
            "https://github.com/user/repo/actions/workflows/ci.yml/badge.svg",
            "https://github.com/org/project/actions/workflows/test.yml/badge.svg?branch=dev",
        ]
        invalid_urls = [
            "https://shields.io/badge/ci-passing-green",
            "https://github.com/user/repo/badge.svg",
            "http://github.com/user/repo/actions/workflows/ci.yml/badge.svg",  # HTTP
        ]

        for url in valid_urls:
            with self.subTest(url=url):
                self.assertTrue(self.validator._is_valid_ci_badge_url(url))

        for url in invalid_urls:
            with self.subTest(url=url):
                self.assertFalse(self.validator._is_valid_ci_badge_url(url))

    def test_get_workflow_files(self):
        """Test workflow file discovery."""
        workflows = self.validator._get_workflow_files()

        self.assertIn('ci.yml', workflows)
        self.assertEqual(workflows['ci.yml'].name, 'ci.yml')

    def test_get_workflow_files_yaml_extension(self):
        """Test workflow discovery with .yaml extension."""
        workflows_dir = self.test_dir / ".github" / "workflows"
        test_workflow = workflows_dir / "test.yaml"
        test_workflow.write_text("name: Test\n")

        workflows = self.validator._get_workflow_files()

        self.assertIn('test.yaml', workflows)

    def test_detect_current_branch(self):
        """Test current branch detection."""
        branch = self.validator._detect_current_branch()
        self.assertEqual(branch, 'dev')

    def test_validate_multiple_issues(self):
        """Test validation with multiple issues in one file."""
        readme = self.test_dir / "README.md"
        readme.write_text(
            "# Test\n"
            "[![CI](https://github.com/test-user/test-repo/actions/workflows/missing.yml/badge.svg)](https://actions)\n"
            "[![Build](https://github.com/test-user/test-repo/actions/workflows/ci.yml/badge.svg?branch=main)](https://actions)\n"
        )

        issues = self.validator.validate_badges(branch='dev')

        self.assertEqual(len(issues), 2)
        # First issue: missing workflow (error)
        self.assertEqual(issues[0].severity, 'error')
        # Second issue: wrong branch (warning)
        self.assertEqual(issues[1].severity, 'warning')

    def test_validate_no_badges(self):
        """Test validation with no CI badges."""
        readme = self.test_dir / "README.md"
        readme.write_text("# Test\n\nNo badges here.\n")

        issues = self.validator.validate_badges()

        self.assertEqual(len(issues), 0)

    def test_ci_badge_issue_repr(self):
        """Test CIBadgeIssue __repr__ method."""
        issue = CIBadgeIssue(
            severity='error',
            badge_type='missing_workflow',
            file_path=Path("/tmp/README.md"),
            line_number=5,
            current_badge="[![CI](...)](...)",
            expected_badge=None,
            message="Workflow not found"
        )

        repr_str = repr(issue)
        self.assertIn("error", repr_str)
        self.assertIn("missing_workflow", repr_str)
        self.assertIn("README.md:5", repr_str)


class TestFormatIssuesReport(unittest.TestCase):
    """Test formatted report generation."""

    def test_format_empty_issues(self):
        """Test formatting with no issues."""
        report = format_issues_report([])
        self.assertEqual(report, "✅ All CI badges valid")

    def test_format_single_error(self):
        """Test formatting with single error."""
        issues = [
            CIBadgeIssue(
                severity='error',
                badge_type='missing_workflow',
                file_path=Path("README.md"),
                line_number=3,
                current_badge="[![CI](...)](...)",
                expected_badge=None,
                message="Badge points to non-existent workflow"
            )
        ]

        report = format_issues_report(issues)

        self.assertIn("CI Badge Validation", report)
        self.assertIn("README.md", report)
        self.assertIn("❌", report)
        self.assertIn("Line 3", report)
        self.assertIn("missing_workflow", report)
        self.assertIn("1 error", report)

    def test_format_multiple_issues(self):
        """Test formatting with multiple errors and warnings."""
        issues = [
            CIBadgeIssue(
                severity='error',
                badge_type='missing_workflow',
                file_path=Path("README.md"),
                line_number=3,
                current_badge="",
                expected_badge=None,
                message="Workflow missing"
            ),
            CIBadgeIssue(
                severity='warning',
                badge_type='wrong_branch',
                file_path=Path("README.md"),
                line_number=4,
                current_badge="",
                expected_badge="fixed",
                message="Wrong branch parameter"
            )
        ]

        report = format_issues_report(issues)

        self.assertIn("1 error", report)
        self.assertIn("1 warning", report)
        self.assertIn("--fix", report)


if __name__ == '__main__':
    unittest.main()
