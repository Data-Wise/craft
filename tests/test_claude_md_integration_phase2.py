#!/usr/bin/env python3
"""
Integration Tests for CLAUDE.md Phase 2 - Audit & Fix

Tests end-to-end workflows:
- Audit → Fix workflow
- Multiple issue types in same file
- Real-world scenarios
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

import pytest

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_auditor import CLAUDEMDAuditor, Severity
from utils.claude_md_fixer import CLAUDEMDFixer

pytestmark = [pytest.mark.integration, pytest.mark.claude_md]


class TestAuditFixWorkflow(unittest.TestCase):
    """Test complete audit → fix workflow."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_audit_then_fix_resolves_issues(self):
        """Verify fix resolves audit issues."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "2.0.0"
        }))

        # Create .STATUS
        status_file = self.path / ".STATUS"
        status_file.write_text("progress: 95%")

        # Create commands directory
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "check.md").write_text("# Check")

        # Create CLAUDE.md with multiple issues
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

**Current Version:** v1.0.0

## Quick Commands

- /craft:check - Validation
- /craft:deploy - Deploy (removed)

progress: 75%
""")

        # Step 1: Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues_before = auditor.audit()

        # Verify issues found
        errors = [i for i in issues_before if i.severity == Severity.ERROR]
        warnings = [i for i in issues_before if i.severity == Severity.WARNING]
        self.assertGreater(len(errors), 0, "Should find errors")
        self.assertGreater(len(warnings), 0, "Should find warnings")

        # Step 2: Run fix
        fixer = CLAUDEMDFixer(claude_md)
        results = fixer.fix_all(scope="all", dry_run=False)

        # Verify fixes applied
        self.assertGreater(len(results), 0, "Should apply fixes")
        successful = [r for r in results if r.success]
        self.assertGreater(len(successful), 0, "Should have successful fixes")

        # Step 3: Run audit again
        auditor2 = CLAUDEMDAuditor(claude_md)
        issues_after = auditor2.audit()

        # Verify fewer issues
        errors_after = [i for i in issues_after if i.severity == Severity.ERROR]
        warnings_after = [i for i in issues_after if i.severity == Severity.WARNING]

        self.assertLess(len(errors_after), len(errors), "Should have fewer errors")
        self.assertLess(len(warnings_after), len(warnings), "Should have fewer warnings")


class TestRealWorldScenarios(unittest.TestCase):
    """Test real-world scenarios."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_craft_plugin_audit_fix(self):
        """Test complete workflow for craft plugin."""
        # Setup realistic craft plugin structure
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-craft-plugin",
            "version": "2.5.0",
            "description": "Test plugin"
        }))

        # Create commands structure
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "check.md").write_text("# Check command")
        (commands_dir / "test.md").write_text("# Test command")

        # Create docs structure
        docs_dir = self.path / "docs"
        docs_dir.mkdir()
        (docs_dir / "guide.md").write_text("# Guide")

        # Create .STATUS
        (self.path / ".STATUS").write_text("""status: WIP
version: 2.5.0
progress: 92%
""")

        # Create CLAUDE.md with issues
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Craft Plugin

**Current Version:** v2.4.0

## Quick Commands

| Command | Purpose |
|---------|---------|
| /craft:check | Validation |
| /craft:test | Testing |
| /craft:old | Legacy (removed) |

## Project Structure

See [architecture](docs/architecture.md) for details.

## Testing

progress: 85%

Content here.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.audit()

        # Should find:
        # - Version mismatch (2.4.0 vs 2.5.0)
        # - Stale command (/craft:old)
        # - Broken link (docs/architecture.md doesn't exist)
        # - Progress mismatch (85% vs 92%)

        version_issues = [i for i in issues if i.category == "version_mismatch"]
        stale_issues = [i for i in issues if i.category == "stale_command"]
        broken_link_issues = [i for i in issues if i.category == "broken_link"]
        progress_issues = [i for i in issues if i.category == "status_sync"]

        self.assertEqual(len(version_issues), 1)
        self.assertEqual(len(stale_issues), 1)
        self.assertEqual(len(broken_link_issues), 1)
        self.assertEqual(len(progress_issues), 1)

        # Run fix
        fixer = CLAUDEMDFixer(claude_md)
        results = fixer.fix_all(scope="all", dry_run=False)

        # Verify fixes
        self.assertEqual(len(results), 4)
        self.assertTrue(all(r.success for r in results))

        # Read fixed content
        fixed_content = claude_md.read_text()
        self.assertIn("2.5.0", fixed_content)
        self.assertNotIn("/craft:old", fixed_content)
        self.assertIn("<!-- ", fixed_content)  # Commented out link
        self.assertIn("92%", fixed_content)

    def test_r_package_audit(self):
        """Test audit for R package."""
        # Setup R package structure
        description = self.path / "DESCRIPTION"
        description.write_text("""Package: testpkg
Version: 1.2.3
Title: Test Package
""")

        # Create CLAUDE.md
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# testpkg R Package

**Version:** 1.2.2

## Quick Reference

## Development

## Testing
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.audit()

        # Should find version mismatch
        version_issues = [i for i in issues if i.category == "version_mismatch"]
        self.assertEqual(len(version_issues), 1)

        # Should NOT find missing section issues (all required sections present)
        missing_sections = [i for i in issues if i.category == "missing_section"]
        self.assertEqual(len(missing_sections), 0)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error handling."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_no_issues_found(self):
        """Test when no issues are found."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "1.0.0"
        }))

        # Create perfect CLAUDE.md
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text("""# Test Plugin

**Current Version:** v1.0.0

## Quick Commands

None yet.

## Project Structure

Standard layout.

## Testing

No tests.
""")

        # Run audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.audit()

        # Run fix
        fixer = CLAUDEMDFixer(claude_md)
        results = fixer.fix_all(scope="all", dry_run=False)

        # Verify no fixes needed
        self.assertEqual(len(results), 0)

    def test_dry_run_preserves_file(self):
        """Verify dry-run doesn't modify file."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "2.0.0"
        }))

        # Create CLAUDE.md
        claude_md = self.path / "CLAUDE.md"
        original = """# Test

**Current Version:** v1.0.0
"""
        claude_md.write_text(original)

        # Get original modification time
        original_mtime = claude_md.stat().st_mtime

        # Run fix in dry-run mode
        fixer = CLAUDEMDFixer(claude_md)
        results = fixer.fix_all(scope="all", dry_run=True)

        # Verify file unchanged
        self.assertEqual(claude_md.read_text(), original)
        self.assertEqual(claude_md.stat().st_mtime, original_mtime)

    def test_backup_created(self):
        """Verify backup is created before fixing."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "2.0.0"
        }))

        # Create CLAUDE.md
        claude_md = self.path / "CLAUDE.md"
        original = """# Test

**Current Version:** v1.0.0
"""
        claude_md.write_text(original)

        # Run fix
        fixer = CLAUDEMDFixer(claude_md)
        results = fixer.fix_all(scope="all", dry_run=False)

        # Verify backup created
        backup_path = self.path / ".CLAUDE.md.backup"
        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.read_text(), original)


if __name__ == "__main__":
    unittest.main()
