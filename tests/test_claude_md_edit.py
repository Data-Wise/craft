#!/usr/bin/env python3
"""
Tests for CLAUDE.md Edit Command

Covers:
- Section parsing
- Section editing
- Preview generation
- Change statistics
- Backup/restore
"""

import unittest
import tempfile
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_section_editor import (
    SectionParser, SectionEditor, Section,
    format_section_list, get_section_diff, calculate_change_stats
)


class TestSectionParsing(unittest.TestCase):
    """Test section parsing from CLAUDE.md."""

    def setUp(self):
        """Create temporary CLAUDE.md."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir) / "CLAUDE.md"

        # Create sample CLAUDE.md
        self.path.write_text("""# CLAUDE.md - Test Project

## Quick Commands

| Task | Command |
|------|---------|
| Test | `/craft:test` |

## Project Structure

```
test/
├── src/
└── tests/
```

## Development Workflow

1. Write code
2. Test
3. Commit
""")

    def test_parse_sections_count(self):
        """Verify correct number of sections parsed."""
        parser = SectionParser(self.path)
        sections = parser.parse_sections()

        # Should have: title, quick commands, project structure, development workflow
        self.assertEqual(len(sections), 4)

    def test_parse_section_names(self):
        """Verify section names parsed correctly."""
        parser = SectionParser(self.path)
        sections = parser.parse_sections()

        names = [s.name for s in sections]
        self.assertIn("CLAUDE.md - Test Project", names)
        self.assertIn("Quick Commands", names)
        self.assertIn("Project Structure", names)
        self.assertIn("Development Workflow", names)

    def test_parse_section_levels(self):
        """Verify header levels detected correctly."""
        parser = SectionParser(self.path)
        sections = parser.parse_sections()

        # Title should be level 1
        title_section = [s for s in sections if "Test Project" in s.name][0]
        self.assertEqual(title_section.level, 1)

        # Other sections should be level 2
        quick_commands = [s for s in sections if s.name == "Quick Commands"][0]
        self.assertEqual(quick_commands.level, 2)

    def test_get_section_by_name(self):
        """Verify getting section by exact name."""
        parser = SectionParser(self.path)
        section = parser.get_section("Quick Commands")

        self.assertIsNotNone(section)
        self.assertEqual(section.name, "Quick Commands")
        self.assertIn("| Task | Command |", section.content)

    def test_get_section_case_insensitive(self):
        """Verify case-insensitive section lookup."""
        parser = SectionParser(self.path)
        section = parser.get_section("quick commands")

        self.assertIsNotNone(section)
        self.assertEqual(section.name, "Quick Commands")

    def test_fuzzy_section_match(self):
        """Verify fuzzy section matching."""
        parser = SectionParser(self.path)
        section = parser.find_section_fuzzy("workflow")

        self.assertIsNotNone(section)
        self.assertEqual(section.name, "Development Workflow")


class TestSectionEditing(unittest.TestCase):
    """Test section editing operations."""

    def setUp(self):
        """Create temporary CLAUDE.md."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir) / "CLAUDE.md"

        # Create sample CLAUDE.md
        self.path.write_text("""# Test Project

## Quick Commands

Old content here.

## Testing

Test content.
""")

    def test_replace_section(self):
        """Verify section replacement."""
        editor = SectionEditor(self.path)

        new_content = """## Quick Commands

New content here.
"""

        success = editor.replace_section("Quick Commands", new_content)

        self.assertTrue(success)

        # Verify content changed
        updated_content = self.path.read_text()
        self.assertIn("New content here.", updated_content)
        self.assertNotIn("Old content here.", updated_content)

    def test_delete_section(self):
        """Verify section deletion."""
        editor = SectionEditor(self.path)

        success = editor.delete_section("Testing")

        self.assertTrue(success)

        # Verify section removed
        updated_content = self.path.read_text()
        self.assertNotIn("## Testing", updated_content)
        self.assertNotIn("Test content.", updated_content)

    def test_preview_change(self):
        """Verify change preview generation."""
        editor = SectionEditor(self.path)

        new_content = "## Quick Commands\n\nNew content."

        before, after = editor.preview_change("Quick Commands", new_content)

        self.assertIn("Old content here.", before)
        self.assertIn("New content.", after)

    def test_backup_creation(self):
        """Verify backup file creation."""
        editor = SectionEditor(self.path)

        backup_path = editor.backup()

        self.assertTrue(backup_path.exists())
        self.assertEqual(backup_path.read_text(), self.path.read_text())

    def test_restore_from_backup(self):
        """Verify restore from backup."""
        editor = SectionEditor(self.path)

        # Create backup
        original_content = self.path.read_text()
        editor.backup()

        # Make change
        self.path.write_text("Modified content")

        # Restore
        success = editor.restore_backup()

        self.assertTrue(success)
        self.assertEqual(self.path.read_text(), original_content)


class TestDiffGeneration(unittest.TestCase):
    """Test diff and change stat generation."""

    def test_section_diff(self):
        """Verify unified diff generation."""
        before = "Line 1\nLine 2\nLine 3"
        after = "Line 1\nModified Line 2\nLine 3"

        diff = get_section_diff(before, after)

        self.assertIn("-Line 2", diff)
        self.assertIn("+Modified Line 2", diff)

    def test_change_stats(self):
        """Verify change statistics calculation."""
        before = "Line 1\nLine 2\nLine 3"
        after = "Line 1\nLine 2\nLine 3\nLine 4\nLine 5"

        stats = calculate_change_stats(before, after)

        self.assertEqual(stats["before_lines"], 3)
        self.assertEqual(stats["after_lines"], 5)
        self.assertEqual(stats["diff_lines"], 2)
        self.assertAlmostEqual(stats["diff_percent"], 66.7, places=1)


class TestSectionFormatting(unittest.TestCase):
    """Test section list formatting."""

    def test_format_section_list(self):
        """Verify section list formatting."""
        sections = [
            Section("Quick Commands", 0, 10, "content1", 2),
            Section("Testing", 10, 20, "content2", 2),
            Section("Workflow", 20, 30, "content3", 2),
        ]

        formatted = format_section_list(sections)

        self.assertIn("1. Quick Commands", formatted)
        self.assertIn("2. Testing", formatted)
        self.assertIn("3. Workflow", formatted)
        self.assertIn("lines", formatted)


if __name__ == "__main__":
    unittest.main()
