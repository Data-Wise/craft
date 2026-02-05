#!/usr/bin/env python3
"""
Tests for CLAUDE.md Auditor

Covers:
- Version sync detection
- Command coverage (missing/stale)
- Broken link detection
- Required sections check
- Status file sync
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_auditor import CLAUDEMDAuditor, Issue, Severity


class TestVersionSync(unittest.TestCase):
    """Test version mismatch detection."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_version_mismatch_detected(self):
        """Verify version mismatch detection."""
        # Create plugin.json with version 2.0.0
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "2.0.0"
        }))

        # Create CLAUDE.md with version 1.0.0
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

**Current Version:** v1.0.0

Test content.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_version_sync()

        # Verify
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].category, "version_mismatch")
        self.assertEqual(issues[0].severity, Severity.WARNING)
        self.assertTrue(issues[0].fixable)
        self.assertIn("1.0.0", issues[0].message)
        self.assertIn("2.0.0", issues[0].message)

    def test_version_match_no_issue(self):
        """Verify no issue when versions match."""
        # Create plugin.json with version 2.0.0
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "2.0.0"
        }))

        # Create CLAUDE.md with matching version
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

**Current Version:** v2.0.0

Test content.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_version_sync()

        # Verify no issues
        self.assertEqual(len(issues), 0)


class TestCommandCoverage(unittest.TestCase):
    """Test command coverage detection."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_stale_command_detected(self):
        """Verify stale command detection."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create commands directory with one command
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "check.md").write_text("# Check command")

        # Create CLAUDE.md referencing deleted command
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

Commands:
- /craft:check - Check command
- /craft:deploy - Deploy command (DELETED)

""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_command_coverage()

        # Verify stale command found
        stale = [i for i in issues if i.category == "stale_command"]
        self.assertEqual(len(stale), 1)
        self.assertEqual(stale[0].severity, Severity.ERROR)
        self.assertIn("/craft:deploy", stale[0].message)
        self.assertTrue(stale[0].fixable)

    def test_missing_command_detected(self):
        """Verify missing command detection."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create commands directory with two commands
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "check.md").write_text("# Check command")
        (commands_dir / "test.md").write_text("# Test command")

        # Create CLAUDE.md only referencing one command
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

Commands:
- /craft:check - Check command

""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_command_coverage()

        # Verify missing command found
        missing = [i for i in issues if i.category == "missing_command"]
        self.assertEqual(len(missing), 1)
        self.assertEqual(missing[0].severity, Severity.INFO)
        self.assertIn("/craft:test", missing[0].message)
        self.assertFalse(missing[0].fixable)


class TestBrokenLinks(unittest.TestCase):
    """Test broken link detection."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_broken_internal_link_detected(self):
        """Verify broken link detection."""
        # Create CLAUDE.md with link to non-existent file
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

See [architecture guide](docs/architecture.md) for details.

External link is OK: [GitHub](https://github.com)
""")

        # Run audit (docs/architecture.md doesn't exist)
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_broken_links()

        # Verify broken link found
        broken = [i for i in issues if i.category == "broken_link"]
        self.assertEqual(len(broken), 1)
        self.assertEqual(broken[0].severity, Severity.ERROR)
        self.assertIn("docs/architecture.md", broken[0].message)
        self.assertTrue(broken[0].fixable)

    def test_valid_link_no_issue(self):
        """Verify valid links don't trigger issues."""
        # Create target file
        docs_dir = self.path / "docs"
        docs_dir.mkdir()
        (docs_dir / "guide.md").write_text("# Guide")

        # Create CLAUDE.md with valid link
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

See [guide](docs/guide.md) for details.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_broken_links()

        # Verify no issues
        self.assertEqual(len(issues), 0)


class TestRequiredSections(unittest.TestCase):
    """Test required sections check."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_missing_section_detected(self):
        """Verify missing section detection."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create CLAUDE.md without required sections
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

## Overview

Some content here.
""")

        # Run audit (expects "Quick Commands", "Project Structure", "Testing")
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_required_sections()

        # Verify missing sections found
        missing = [i for i in issues if i.category == "missing_section"]
        self.assertGreater(len(missing), 0)
        self.assertEqual(missing[0].severity, Severity.WARNING)
        self.assertFalse(missing[0].fixable)

    def test_all_sections_present_no_issue(self):
        """Verify no issue when all sections present."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create CLAUDE.md with all required sections
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

## Quick Commands

Commands here.

## Project Structure

Structure here.

## Testing

Testing info.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_required_sections()

        # Verify no issues
        self.assertEqual(len(issues), 0)


class TestStatusSync(unittest.TestCase):
    """Test status file sync check."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_progress_mismatch_detected(self):
        """Verify progress mismatch detection."""
        # Create .STATUS file
        status_file = self.path / ".STATUS"
        status_file.write_text("""status: WIP
version: 1.0.0
progress: 85% (Phase 2)
""")

        # Create CLAUDE.md with different progress
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

**Progress:** 60%

Some content.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_status_sync()

        # Verify mismatch found
        self.assertEqual(len(issues), 1)
        self.assertEqual(issues[0].category, "status_sync")
        self.assertEqual(issues[0].severity, Severity.WARNING)
        self.assertIn("60%", issues[0].message)
        self.assertIn("85%", issues[0].message)
        self.assertTrue(issues[0].fixable)

    def test_progress_match_no_issue(self):
        """Verify no issue when progress matches."""
        # Create .STATUS file
        status_file = self.path / ".STATUS"
        status_file.write_text("""status: WIP
progress: 85% (Phase 2)
""")

        # Create CLAUDE.md with matching progress
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

progress: 85%

Some content.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_status_sync()

        # Verify no issues
        self.assertEqual(len(issues), 0)


class TestReportGeneration(unittest.TestCase):
    """Test audit report generation."""

    def test_report_format(self):
        """Verify report formatting."""
        issues = [
            Issue(
                severity=Severity.ERROR,
                category="stale_command",
                message="Command /craft:old removed",
                line_number=45,
                fixable=True,
                fix_method="remove_command"
            ),
            Issue(
                severity=Severity.WARNING,
                category="version_mismatch",
                message="Version 1.0.0 doesn't match 2.0.0",
                line_number=12,
                fixable=True,
                fix_method="update_version"
            ),
            Issue(
                severity=Severity.INFO,
                category="missing_command",
                message="Command /craft:new not documented",
                fixable=False
            ),
        ]

        # Generate report
        auditor = CLAUDEMDAuditor(Path("CLAUDE.md"))
        report = auditor.generate_report(issues)

        # Verify report contains expected sections
        self.assertIn("🔴 Errors (1)", report)
        self.assertIn("⚠️  Warnings (1)", report)
        self.assertIn("📝 Info (1)", report)
        self.assertIn("Summary:", report)
        self.assertIn("/craft:docs:claude-md:sync --fix", report)


if __name__ == "__main__":
    unittest.main()
