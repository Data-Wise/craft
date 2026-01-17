#!/usr/bin/env python3
"""
Unit tests for linkcheck_ignore_parser.py
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add parent directory to path to import the parser
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.linkcheck_ignore_parser import parse_linkcheck_ignore, IgnoreRules, IgnorePattern


class TestLinkcheckIgnoreParser(unittest.TestCase):
    """Test suite for .linkcheck-ignore parser."""

    def setUp(self):
        """Create temporary directory for test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files and restore working directory."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_parse_missing_file(self):
        """Test graceful handling of missing .linkcheck-ignore file."""
        rules = parse_linkcheck_ignore("nonexistent.md")
        self.assertIsInstance(rules, IgnoreRules)
        self.assertEqual(len(rules.patterns), 0)
        self.assertEqual(rules.get_categories(), [])

    def test_parse_single_category_single_file(self):
        """Test parsing a single category with one file pattern."""
        content = """# Known Broken Links

### Test Files
File: `docs/test-violations.md`
- Purpose: Test data for validation
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()
        self.assertEqual(len(rules.patterns), 1)
        self.assertEqual(rules.patterns[0].category, "Test Files")
        self.assertEqual(rules.patterns[0].files, ["docs/test-violations.md"])
        self.assertEqual(rules.patterns[0].targets, [])
        self.assertEqual(rules.patterns[0].reason, "Test data for validation")

    def test_parse_multiple_categories(self):
        """Test parsing multiple categories."""
        content = """# Known Broken Links

### 1. Test Files (Intentional)
File: `docs/test-violations.md`
- Purpose: Test data

### 2. Brainstorm References (Gitignored)
Files with broken links:
- `docs/specs/SPEC-one.md`
- `docs/specs/SPEC-two.md`

Targets: `docs/brainstorm/*.md` (gitignored)
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()
        self.assertEqual(len(rules.patterns), 2)

        # Check first category
        self.assertEqual(rules.patterns[0].category, "Test Files")
        self.assertEqual(rules.patterns[0].files, ["docs/test-violations.md"])

        # Check second category
        self.assertEqual(rules.patterns[1].category, "Brainstorm References")
        self.assertEqual(len(rules.patterns[1].files), 2)
        self.assertIn("docs/specs/SPEC-one.md", rules.patterns[1].files)
        self.assertIn("docs/specs/SPEC-two.md", rules.patterns[1].files)
        self.assertEqual(rules.patterns[1].targets, ["docs/brainstorm/*.md"])

    def test_should_ignore_exact_match(self):
        """Test exact file and target matching."""
        content = """# Known Broken Links

### Test Category
File: `docs/test.md`
Target: `nonexistent.md`
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()
        should_ignore, category = rules.should_ignore("docs/test.md", "nonexistent.md")
        self.assertTrue(should_ignore)
        self.assertEqual(category, "Test Category")

        # Test non-matching file
        should_ignore, category = rules.should_ignore("docs/other.md", "nonexistent.md")
        self.assertFalse(should_ignore)
        self.assertIsNone(category)

    def test_should_ignore_glob_patterns(self):
        """Test glob pattern matching for files and targets."""
        content = """# Known Broken Links

### Brainstorm Files
Files with broken links:
- `docs/specs/*.md`

Targets: `docs/brainstorm/*.md`
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()

        # Should match spec file linking to brainstorm
        should_ignore, category = rules.should_ignore(
            "docs/specs/SPEC-feature.md",
            "../brainstorm/notes.md"
        )
        self.assertTrue(should_ignore)
        self.assertEqual(category, "Brainstorm Files")

        # Should not match non-spec file
        should_ignore, _ = rules.should_ignore(
            "docs/guide/setup.md",
            "../brainstorm/notes.md"
        )
        self.assertFalse(should_ignore)

    def test_should_ignore_empty_targets(self):
        """Test that empty targets list ignores all links from file."""
        content = """# Known Broken Links

### Test Files
File: `docs/test-violations.md`
- Purpose: Intentionally broken
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()

        # Should ignore any target from this file
        should_ignore, category = rules.should_ignore(
            "docs/test-violations.md",
            "any-target.md"
        )
        self.assertTrue(should_ignore)
        self.assertEqual(category, "Test Files")

        should_ignore, _ = rules.should_ignore(
            "docs/test-violations.md",
            "another-target.md"
        )
        self.assertTrue(should_ignore)

    def test_path_normalization(self):
        """Test that docs/path and ../path are normalized correctly."""
        content = """# Known Broken Links

### External References
File: `docs/index.md`
Target: `../README.md`
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()

        # Both forms should match
        should_ignore, _ = rules.should_ignore("docs/index.md", "../README.md")
        self.assertTrue(should_ignore)

    def test_get_categories(self):
        """Test getting list of all categories."""
        content = """# Known Broken Links

### Category A
File: `a.md`

### Category B
File: `b.md`

### Category C
File: `c.md`
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()
        categories = rules.get_categories()
        self.assertEqual(len(categories), 3)
        self.assertIn("Category A", categories)
        self.assertIn("Category B", categories)
        self.assertIn("Category C", categories)

    def test_get_patterns_by_category(self):
        """Test filtering patterns by category."""
        content = """# Known Broken Links

### Test Files
File: `test1.md`

### Test Files
File: `test2.md`

### Other Category
File: `other.md`
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()
        test_patterns = rules.get_patterns_by_category("Test Files")
        self.assertEqual(len(test_patterns), 2)
        self.assertEqual(test_patterns[0].files, ["test1.md"])
        self.assertEqual(test_patterns[1].files, ["test2.md"])

    def test_skip_comment_sections(self):
        """Test that ## Purpose, ## Build Status sections are skipped."""
        content = """# Known Broken Links

## Purpose
This file documents known broken links.

## Build Status
Expected warnings: 30

### Real Category
File: `docs/test.md`
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()
        self.assertEqual(len(rules.patterns), 1)
        self.assertEqual(rules.patterns[0].category, "Real Category")

    def test_multiple_targets_on_separate_lines(self):
        """Test parsing multiple target lines in bullet list."""
        content = """# Known Broken Links

### Command Pages
Files with broken links:
- `docs/teaching.md`

Targets:
- `../commands/site/publish.md`
- `../commands/site/build.md`
- `../commands/git/sync.md`
"""
        Path(".linkcheck-ignore").write_text(content)

        rules = parse_linkcheck_ignore()
        self.assertEqual(len(rules.patterns), 1)
        self.assertEqual(len(rules.patterns[0].targets), 3)
        self.assertIn("../commands/site/publish.md", rules.patterns[0].targets)
        self.assertIn("../commands/site/build.md", rules.patterns[0].targets)
        self.assertIn("../commands/git/sync.md", rules.patterns[0].targets)


class TestIgnorePattern(unittest.TestCase):
    """Test IgnorePattern dataclass."""

    def test_create_pattern(self):
        """Test creating an IgnorePattern."""
        pattern = IgnorePattern(
            category="Test",
            files=["test.md"],
            targets=["target.md"],
            reason="Testing"
        )
        self.assertEqual(pattern.category, "Test")
        self.assertEqual(pattern.files, ["test.md"])
        self.assertEqual(pattern.targets, ["target.md"])
        self.assertEqual(pattern.reason, "Testing")

    def test_default_values(self):
        """Test default values for optional fields."""
        pattern = IgnorePattern(category="Test")
        self.assertEqual(pattern.files, [])
        self.assertEqual(pattern.targets, [])
        self.assertIsNone(pattern.reason)


if __name__ == "__main__":
    unittest.main()
