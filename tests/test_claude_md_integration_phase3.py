#!/usr/bin/env python3
"""
Integration Tests for Phase 3 - Scaffold & Edit Commands

Tests complete workflows:
- Scaffold → Edit → Validate
- Template selection → Population → Rendering
- Section editing → Preview → Apply
- Cross-command integration
"""

import unittest
import tempfile
import json
from pathlib import Path
import sys

import pytest

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_detector import CLAUDEMDDetector
from utils.claude_md_template_populator import TemplatePopulator, populate_template
from utils.claude_md_section_editor import SectionParser, SectionEditor
from utils.claude_md_auditor import CLAUDEMDAuditor

pytestmark = [pytest.mark.integration, pytest.mark.claude_md]


class TestScaffoldEditWorkflow(unittest.TestCase):
    """Test scaffold → edit workflow."""

    def setUp(self):
        """Create temporary plugin project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create plugin structure
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0",
            "description": "Test plugin"
        }))

        (self.path / "commands").mkdir()
        (self.path / "skills").mkdir()
        (self.path / "agents").mkdir()

    def test_full_scaffold_edit_workflow(self):
        """Test complete scaffold → edit → validate workflow."""
        # Step 1: Detect project type
        detector = CLAUDEMDDetector(self.path)
        info = detector.detect()
        self.assertEqual(info.type, "craft-plugin")

        # Step 2: Populate variables
        populator = TemplatePopulator(self.path, "craft-plugin")
        variables = populator.populate_all()
        self.assertEqual(variables["plugin_name"], "test-plugin")

        # Step 3: Load and render template
        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "plugin-template.md"
        template = template_path.read_text()
        content = populate_template(template, variables)

        # Step 4: Write CLAUDE.md
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)

        # Step 5: Parse sections
        parser = SectionParser(claude_md)
        sections = parser.parse_sections()
        self.assertGreater(len(sections), 3)

        # Step 6: Edit a section
        editor = SectionEditor(claude_md)
        quick_commands_section = parser.get_section("Quick Commands")
        self.assertIsNotNone(quick_commands_section)

        new_content = """## Quick Commands

| Task | Command |
|------|---------|
| Test | `/craft:test:run` |
| Check | `/craft:check` |
"""

        success = editor.replace_section("Quick Commands", new_content)
        self.assertTrue(success)

        # Step 7: Verify changes
        updated_parser = SectionParser(claude_md)
        updated_section = updated_parser.get_section("Quick Commands")
        self.assertIn("/craft:test:run", updated_section.content)
        self.assertIn("/craft:check", updated_section.content)


class TestTemplateValidation(unittest.TestCase):
    """Test template generation and validation."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_plugin_template_generates_valid_markdown(self):
        """Verify plugin template generates valid markdown."""
        # Create plugin
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "1.0.0"
        }))

        (self.path / "commands").mkdir()

        # Generate
        populator = TemplatePopulator(self.path, "craft-plugin")
        variables = populator.populate_all()

        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "plugin-template.md"
        template = template_path.read_text()
        content = populate_template(template, variables)

        # Validate structure
        self.assertIn("# CLAUDE.md", content)
        self.assertIn("## Quick Commands", content)
        self.assertIn("## Project Structure", content)
        self.assertIn("v1.0.0", content)

    def test_teaching_template_generates_valid_markdown(self):
        """Verify teaching template generates valid markdown."""
        # Create teaching site
        (self.path / "_quarto.yml").write_text("title: Test Course")
        (self.path / "course.yml").write_text("course_code: TEST 101")

        weeks_dir = self.path / "weeks"
        weeks_dir.mkdir()

        # Generate
        populator = TemplatePopulator(self.path, "teaching")
        variables = populator.populate_all()

        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "teaching-template.md"
        template = template_path.read_text()
        content = populate_template(template, variables)

        # Validate structure
        self.assertIn("# CLAUDE.md", content)
        self.assertIn("Test Course", content)
        self.assertIn("TEST 101", content)

    def test_r_package_template_generates_valid_markdown(self):
        """Verify R package template generates valid markdown."""
        # Create R package
        (self.path / "DESCRIPTION").write_text("""Package: testpkg
Title: Test Package
Version: 0.1.0
""")

        r_dir = self.path / "R"
        r_dir.mkdir()

        # Generate
        populator = TemplatePopulator(self.path, "r-package")
        variables = populator.populate_all()

        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "r-package-template.md"
        template = template_path.read_text()
        content = populate_template(template, variables)

        # Validate structure
        self.assertIn("# CLAUDE.md", content)
        self.assertIn("testpkg", content)
        self.assertIn("devtools", content)


class TestScaffoldAuditIntegration(unittest.TestCase):
    """Test scaffold → audit integration."""

    def setUp(self):
        """Create temporary plugin project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create plugin
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "2.0.0"
        }))

        (self.path / "commands").mkdir()

    def test_scaffolded_file_passes_audit(self):
        """Verify scaffolded CLAUDE.md passes audit."""
        # Scaffold
        populator = TemplatePopulator(self.path, "craft-plugin")
        variables = populator.populate_all()

        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "plugin-template.md"
        template = template_path.read_text()
        content = populate_template(template, variables)

        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)

        # Audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_version_sync()

        # Should have no version issues (both should be 2.0.0)
        version_issues = [i for i in issues if i.category == "version_mismatch"]
        self.assertEqual(len(version_issues), 0)


class TestEditPreviewApply(unittest.TestCase):
    """Test edit → preview → apply workflow."""

    def setUp(self):
        """Create temporary CLAUDE.md."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir) / "CLAUDE.md"

        self.path.write_text("""# Test Project

## Quick Commands

Original commands here.

## Testing

Original testing info.
""")

    def test_preview_before_apply(self):
        """Verify preview shows changes before applying."""
        editor = SectionEditor(self.path)

        new_content = "## Quick Commands\n\nNew commands here."

        # Preview
        before, after = editor.preview_change("Quick Commands", new_content)

        # Verify preview content
        self.assertIn("Original commands here.", before)
        self.assertIn("New commands here.", after)

        # Verify file unchanged
        current_content = self.path.read_text()
        self.assertIn("Original commands here.", current_content)
        self.assertNotIn("New commands here.", current_content)

    def test_apply_after_preview(self):
        """Verify changes applied after preview confirmation."""
        editor = SectionEditor(self.path)

        new_content = "## Quick Commands\n\nNew commands here."

        # Preview (simulating user sees changes)
        before, after = editor.preview_change("Quick Commands", new_content)

        # Apply
        success = editor.replace_section("Quick Commands", new_content)
        self.assertTrue(success)

        # Verify file changed
        current_content = self.path.read_text()
        self.assertNotIn("Original commands here.", current_content)
        self.assertIn("New commands here.", current_content)


class TestBackupRestore(unittest.TestCase):
    """Test backup/restore workflow."""

    def setUp(self):
        """Create temporary CLAUDE.md."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir) / "CLAUDE.md"

        self.original_content = """# Test Project

## Quick Commands

Original content.
"""

        self.path.write_text(self.original_content)

    def test_backup_before_edit(self):
        """Verify backup created before editing."""
        editor = SectionEditor(self.path)

        # Create backup
        backup_path = editor.backup()

        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.read_text(), self.original_content)

    def test_restore_after_bad_edit(self):
        """Verify restore works after problematic edit."""
        editor = SectionEditor(self.path)

        # Backup
        editor.backup()

        # Make bad edit
        self.path.write_text("Corrupted content")

        # Restore
        success = editor.restore_backup()

        self.assertTrue(success)
        self.assertEqual(self.path.read_text(), self.original_content)


class TestCrossCommandIntegration(unittest.TestCase):
    """Test integration between scaffold, edit, audit commands."""

    def setUp(self):
        """Create temporary plugin project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create plugin
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "integration-test",
            "version": "1.5.0"
        }))

        (self.path / "commands").mkdir()

    def test_scaffold_edit_audit_workflow(self):
        """Test complete workflow: scaffold → edit → audit."""
        # 1. Scaffold
        populator = TemplatePopulator(self.path, "craft-plugin")
        variables = populator.populate_all()

        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "plugin-template.md"
        template = template_path.read_text()
        content = populate_template(template, variables)

        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)

        # 2. Edit (add custom content)
        editor = SectionEditor(claude_md)
        new_quick_commands = """## Quick Commands

| Task | Command |
|------|---------|
| Test | `/craft:test:run` |
| Validate | `/craft:check` |
| Build | `/craft:build` |
"""

        editor.replace_section("Quick Commands", new_quick_commands)

        # 3. Audit
        auditor = CLAUDEMDAuditor(claude_md)
        issues = auditor.check_version_sync()

        # Should pass version check
        version_issues = [i for i in issues if i.category == "version_mismatch"]
        self.assertEqual(len(version_issues), 0)

        # Verify custom content preserved
        final_content = claude_md.read_text()
        self.assertIn("/craft:test:run", final_content)
        self.assertIn("/craft:check", final_content)
        self.assertIn("/craft:build", final_content)


if __name__ == "__main__":
    unittest.main()
