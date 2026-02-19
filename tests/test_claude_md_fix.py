#!/usr/bin/env python3
"""
Tests for CLAUDE.md Fixer

Covers:
- Version mismatch fixing
- Stale command removal
- Broken link fixing
- Progress sync fixing
- Dry-run mode
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

import pytest

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

pytestmark = [pytest.mark.unit, pytest.mark.claude_md]

from utils.claude_md_fixer import CLAUDEMDFixer, FixResult
from utils.claude_md_auditor import CLAUDEMDAuditor, Issue, Severity


class TestVersionFix(unittest.TestCase):
    """Test version mismatch fixing."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_fix_version_mismatch(self):
        """Verify version fix."""
        # Create plugin.json with version 2.0.0
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "2.0.0"
        }))

        # Create CLAUDE.md with old version
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

**Current Version:** v1.0.0

Test content.
""")

        # Create issue
        issue = Issue(
            severity=Severity.WARNING,
            category="version_mismatch",
            message="Version 1.0.0 doesn't match 2.0.0",
            line_number=3,
            fixable=True,
            fix_method="update_version"
        )

        # Fix
        fixer = CLAUDEMDFixer(claude_md)
        result = fixer.fix_version_mismatch(issue)

        # Verify
        self.assertTrue(result.success)
        self.assertIn("2.0.0", fixer.content)
        self.assertNotIn("1.0.0", fixer.content)

    def test_version_fix_alternative_format(self):
        """Verify version fix with alternative format."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "3.5.1"
        }))

        # Create CLAUDE.md with version: format
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test

version: 2.1.0

Content.
""")

        # Create issue
        issue = Issue(
            severity=Severity.WARNING,
            category="version_mismatch",
            message="Version 2.1.0 doesn't match 3.5.1",
            fixable=True,
            fix_method="update_version"
        )

        # Fix
        fixer = CLAUDEMDFixer(claude_md)
        result = fixer.fix_version_mismatch(issue)

        # Verify
        self.assertTrue(result.success)
        self.assertIn("3.5.1", fixer.content)


class TestStaleCommandFix(unittest.TestCase):
    """Test stale command removal."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_remove_stale_command(self):
        """Verify stale command removal."""
        # Create CLAUDE.md with stale command
        claude_md = self.path / "CLAUDE.md"
        original_content = """# Test Plugin

Commands:
- /craft:check - Check command
- /craft:deploy - Deploy (removed)
- /craft:test - Test command

Content.
"""
        claude_md.write_text(original_content)

        # Create issue
        issue = Issue(
            severity=Severity.ERROR,
            category="stale_command",
            message="Command /craft:deploy documented but file deleted",
            line_number=5,
            fixable=True,
            fix_method="remove_command"
        )

        # Fix
        fixer = CLAUDEMDFixer(claude_md)
        result = fixer.fix_stale_command(issue)

        # Verify
        self.assertTrue(result.success)
        self.assertNotIn("/craft:deploy", fixer.content)
        self.assertIn("/craft:check", fixer.content)
        self.assertIn("/craft:test", fixer.content)
        self.assertEqual(result.lines_changed, 1)


class TestBrokenLinkFix(unittest.TestCase):
    """Test broken link fixing."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_comment_out_broken_link(self):
        """Verify broken link is commented out."""
        # Create CLAUDE.md with broken link
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

See [architecture](docs/architecture.md) for details.

More content.
""")

        # Create issue
        issue = Issue(
            severity=Severity.ERROR,
            category="broken_link",
            message="Link points to non-existent file: docs/architecture.md",
            line_number=3,
            fixable=True,
            fix_method="remove_link"
        )

        # Fix
        fixer = CLAUDEMDFixer(claude_md)
        result = fixer.fix_broken_link(issue)

        # Verify
        self.assertTrue(result.success)
        self.assertIn("<!-- ", fixer.content)
        self.assertIn("(link broken)", fixer.content)
        self.assertIn("docs/architecture.md", fixer.content)  # Still present in comment


class TestProgressFix(unittest.TestCase):
    """Test progress sync fixing."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_fix_progress_mismatch(self):
        """Verify progress fix."""
        # Create .STATUS file
        status_file = self.path / ".STATUS"
        status_file.write_text("""status: WIP
progress: 85%
""")

        # Create CLAUDE.md with old progress
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

progress: 60%

Content.
""")

        # Create issue
        issue = Issue(
            severity=Severity.WARNING,
            category="status_sync",
            message="Progress mismatch: CLAUDE.md=60%, .STATUS=85%",
            line_number=3,
            fixable=True,
            fix_method="update_progress"
        )

        # Fix
        fixer = CLAUDEMDFixer(claude_md)
        result = fixer.fix_status_sync(issue)

        # Verify
        self.assertTrue(result.success)
        self.assertIn("85%", fixer.content)
        self.assertNotIn("60%", fixer.content)

    def test_fix_progress_alternative_format(self):
        """Verify progress fix with alternative format."""
        # Create CLAUDE.md with **Progress:** format
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test

**Progress:** 45%

Content.
""")

        # Create issue
        issue = Issue(
            severity=Severity.WARNING,
            category="status_sync",
            message="Progress mismatch: CLAUDE.md=45%, .STATUS=90%",
            fixable=True,
            fix_method="update_progress"
        )

        # Fix
        fixer = CLAUDEMDFixer(claude_md)
        result = fixer.fix_status_sync(issue)

        # Verify
        self.assertTrue(result.success)
        self.assertIn("90%", fixer.content)


class TestDryRun(unittest.TestCase):
    """Test dry-run mode."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_dry_run_no_changes(self):
        """Verify dry-run doesn't modify files."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "2.0.0"
        }))

        # Create CLAUDE.md
        claude_md = self.path / "CLAUDE.md"
        original_content = """# Test

**Current Version:** v1.0.0
"""
        claude_md.write_text(original_content)

        # Create fixer
        fixer = CLAUDEMDFixer(claude_md)

        # Run fixes in dry-run mode
        results = fixer.fix_all(scope="all", dry_run=True)

        # Verify file wasn't modified
        current_content = claude_md.read_text()
        self.assertEqual(original_content, current_content)

        # But fixer.content should have changes
        if results:
            self.assertIn("2.0.0", fixer.content)


class TestFixAll(unittest.TestCase):
    """Test fix_all method."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_fix_multiple_issues(self):
        """Verify multiple issues can be fixed."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "2.0.0"
        }))

        # Create .STATUS
        status_file = self.path / ".STATUS"
        status_file.write_text("progress: 90%")

        # Create CLAUDE.md with multiple issues
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test

**Current Version:** v1.0.0

progress: 75%

- /craft:old - Old command
""")

        # Fix all
        fixer = CLAUDEMDFixer(claude_md)
        results = fixer.fix_all(scope="all", dry_run=False)

        # Verify fixes applied
        self.assertGreater(len(results), 0)

        # Read updated content
        updated_content = claude_md.read_text()
        self.assertIn("2.0.0", updated_content)
        self.assertIn("90%", updated_content)


if __name__ == "__main__":
    unittest.main()
