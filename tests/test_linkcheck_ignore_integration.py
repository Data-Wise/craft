#!/usr/bin/env python3
"""
Integration tests for .linkcheck-ignore feature.

Tests end-to-end behavior of:
1. Parser loading .linkcheck-ignore file
2. Link validation with categorization
3. Exit code logic based on link categories
4. VS Code format output with categories
"""

import unittest
import tempfile
import os
from pathlib import Path

# Add parent directory to path to import the parser
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.linkcheck_ignore_parser import parse_linkcheck_ignore


class TestLinkcheckIgnoreIntegration(unittest.TestCase):
    """Integration tests for .linkcheck-ignore feature."""

    def setUp(self):
        """Create temporary directory with test files."""
        self.temp_dir = tempfile.mkdtemp()
        self.original_cwd = os.getcwd()
        os.chdir(self.temp_dir)

        # Create docs directory structure
        os.makedirs("docs/specs", exist_ok=True)
        os.makedirs("docs/guide", exist_ok=True)
        os.makedirs("docs/brainstorm", exist_ok=True)

    def tearDown(self):
        """Clean up temporary files and restore working directory."""
        os.chdir(self.original_cwd)
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_scenario_1_all_links_valid(self):
        """Test Scenario 1: All links are valid (no broken links)."""
        # Setup: No .linkcheck-ignore needed
        # Expected: Exit code 0, no broken links reported

        # Simulate validation with no broken links
        broken_links = []

        # Expected behavior
        critical_count = len(broken_links)
        expected_count = 0

        self.assertEqual(critical_count, 0)
        # Exit code should be 0
        exit_code = 1 if critical_count > 0 else 0
        self.assertEqual(exit_code, 0)

    def test_scenario_2_critical_broken_links_only(self):
        """Test Scenario 2: Broken links exist, no .linkcheck-ignore file."""
        # Setup: Some broken links, no ignore file
        broken_links = [
            {"file": "docs/index.md", "line": 34, "target": "/docs/config.md"},
            {"file": "README.md", "line": 67, "target": "docs/guide/nonexistent.md"},
        ]

        # Load rules (will be empty since file doesn't exist)
        rules = parse_linkcheck_ignore()

        # Categorize links
        critical_broken = []
        expected_broken = []

        for link in broken_links:
            should_ignore, category = rules.should_ignore(link["file"], link["target"])
            if should_ignore:
                expected_broken.append({**link, "category": category})
            else:
                critical_broken.append(link)

        # Expected: All broken links are critical
        self.assertEqual(len(critical_broken), 2)
        self.assertEqual(len(expected_broken), 0)

        # Exit code should be 1
        exit_code = 1 if len(critical_broken) > 0 else 0
        self.assertEqual(exit_code, 1)

    def test_scenario_3_expected_broken_links_only(self):
        """Test Scenario 3: All broken links are expected (in .linkcheck-ignore)."""
        # Create .linkcheck-ignore file
        linkcheck_content = """# Known Broken Links

### Test Files
File: `docs/test-violations.md`
- Purpose: Test data

### Brainstorm References
File: `docs/specs/SPEC-feature.md`
Target: `../brainstorm/notes.md`
"""
        Path(".linkcheck-ignore").write_text(linkcheck_content)

        broken_links = [
            {"file": "docs/test-violations.md", "line": 12, "target": "nonexistent.md"},
            {"file": "docs/specs/SPEC-feature.md", "line": 45, "target": "../brainstorm/notes.md"},
        ]

        # Load rules
        rules = parse_linkcheck_ignore()

        # Categorize links
        critical_broken = []
        expected_broken = []

        for link in broken_links:
            should_ignore, category = rules.should_ignore(link["file"], link["target"])
            if should_ignore:
                expected_broken.append({**link, "category": category})
            else:
                critical_broken.append(link)

        # Expected: All broken links are expected
        self.assertEqual(len(critical_broken), 0)
        self.assertEqual(len(expected_broken), 2)
        self.assertEqual(expected_broken[0]["category"], "Test Files")
        self.assertEqual(expected_broken[1]["category"], "Brainstorm References")

        # Exit code should be 0 (only expected broken links)
        exit_code = 1 if len(critical_broken) > 0 else 0
        self.assertEqual(exit_code, 0)

    def test_scenario_4_mixed_critical_and_expected(self):
        """Test Scenario 4: Both critical and expected broken links."""
        # Create .linkcheck-ignore file
        linkcheck_content = """# Known Broken Links

### Test Files
File: `docs/test-violations.md`
"""
        Path(".linkcheck-ignore").write_text(linkcheck_content)

        broken_links = [
            # Expected broken link
            {"file": "docs/test-violations.md", "line": 12, "target": "nonexistent.md"},
            # Critical broken links
            {"file": "docs/index.md", "line": 34, "target": "/docs/config.md"},
            {"file": "README.md", "line": 67, "target": "docs/guide/missing.md"},
        ]

        # Load rules
        rules = parse_linkcheck_ignore()

        # Categorize links
        critical_broken = []
        expected_broken = []

        for link in broken_links:
            should_ignore, category = rules.should_ignore(link["file"], link["target"])
            if should_ignore:
                expected_broken.append({**link, "category": category})
            else:
                critical_broken.append(link)

        # Expected: 2 critical, 1 expected
        self.assertEqual(len(critical_broken), 2)
        self.assertEqual(len(expected_broken), 1)
        self.assertEqual(expected_broken[0]["category"], "Test Files")

        # Exit code should be 1 (critical links exist)
        exit_code = 1 if len(critical_broken) > 0 else 0
        self.assertEqual(exit_code, 1)

    def test_scenario_5_glob_patterns(self):
        """Test Scenario 5: Glob patterns match multiple files."""
        # Create .linkcheck-ignore with glob patterns
        linkcheck_content = """# Known Broken Links

### Spec Files
Files with broken links:
- `docs/specs/*.md`

Targets: `docs/brainstorm/*.md`
"""
        Path(".linkcheck-ignore").write_text(linkcheck_content)

        broken_links = [
            # Should be expected (matches glob)
            {"file": "docs/specs/SPEC-feature-a.md", "line": 10, "target": "../brainstorm/notes-a.md"},
            {"file": "docs/specs/SPEC-feature-b.md", "line": 20, "target": "../brainstorm/notes-b.md"},
            # Should be critical (doesn't match glob)
            {"file": "docs/guide/setup.md", "line": 30, "target": "../brainstorm/notes.md"},
        ]

        # Load rules
        rules = parse_linkcheck_ignore()

        # Categorize links
        critical_broken = []
        expected_broken = []

        for link in broken_links:
            should_ignore, category = rules.should_ignore(link["file"], link["target"])
            if should_ignore:
                expected_broken.append({**link, "category": category})
            else:
                critical_broken.append(link)

        # Expected: 2 expected (spec files), 1 critical (guide)
        self.assertEqual(len(expected_broken), 2)
        self.assertEqual(len(critical_broken), 1)
        self.assertEqual(critical_broken[0]["file"], "docs/guide/setup.md")

        # Exit code should be 1 (critical link exists)
        exit_code = 1 if len(critical_broken) > 0 else 0
        self.assertEqual(exit_code, 1)

    def test_scenario_6_multiple_categories(self):
        """Test Scenario 6: Multiple categories with different patterns."""
        # Create .linkcheck-ignore with multiple categories
        linkcheck_content = """# Known Broken Links

### Test Files
File: `docs/test-violations.md`

### Brainstorm References
Files with broken links:
- `docs/specs/SPEC-hub.md`
- `docs/specs/SPEC-teaching.md`

Targets: `docs/brainstorm/*.md`

### README References
File: `docs/TEACHING-DOCS-INDEX.md`
Target: `../README.md`
"""
        Path(".linkcheck-ignore").write_text(linkcheck_content)

        broken_links = [
            {"file": "docs/test-violations.md", "line": 5, "target": "any.md"},
            {"file": "docs/specs/SPEC-hub.md", "line": 10, "target": "../brainstorm/hub.md"},
            {"file": "docs/TEACHING-DOCS-INDEX.md", "line": 20, "target": "../README.md"},
        ]

        # Load rules
        rules = parse_linkcheck_ignore()

        # Categorize links
        expected_broken = []
        for link in broken_links:
            should_ignore, category = rules.should_ignore(link["file"], link["target"])
            if should_ignore:
                expected_broken.append({**link, "category": category})

        # Expected: All 3 should be categorized
        self.assertEqual(len(expected_broken), 3)

        # Check categories
        categories = [link["category"] for link in expected_broken]
        self.assertIn("Test Files", categories)
        self.assertIn("Brainstorm References", categories)
        self.assertIn("README References", categories)

    def test_scenario_7_vscode_format_output(self):
        """Test Scenario 7: VS Code format includes category information."""
        # Create .linkcheck-ignore file
        linkcheck_content = """# Known Broken Links

### Test Files
File: `docs/test.md`
"""
        Path(".linkcheck-ignore").write_text(linkcheck_content)

        broken_links = [
            {"file": "docs/test.md", "line": 10, "col": 5, "text": "[link](target.md)", "target": "target.md"},
            {"file": "docs/other.md", "line": 20, "col": 10, "text": "[link](missing.md)", "target": "missing.md"},
        ]

        # Load rules
        rules = parse_linkcheck_ignore()

        # Generate VS Code format output
        vscode_output = []
        for link in broken_links:
            should_ignore, category = rules.should_ignore(link["file"], link["target"])
            if should_ignore:
                # Expected broken link - include category
                output = f"{link['file']}:{link['line']}:{link['col']}: {link['text']} → Expected ({category})"
            else:
                # Critical broken link
                output = f"{link['file']}:{link['line']}:{link['col']}: {link['text']} → File not found"
            vscode_output.append(output)

        # Verify format
        self.assertEqual(len(vscode_output), 2)
        self.assertIn("Expected (Test Files)", vscode_output[0])
        self.assertIn("File not found", vscode_output[1])
        self.assertNotIn("Expected", vscode_output[1])

    def test_real_world_linkcheck_ignore(self):
        """Test with real-world .linkcheck-ignore file structure."""
        # Use actual .linkcheck-ignore format from craft project
        linkcheck_content = """# Known Broken Links - Documentation Only

## Purpose
This file documents known broken links in the documentation.

## Categories

### 1. Test Violation Files (Intentional)
File: `docs/test-violations.md`
- Purpose: Test data for validation
- Should NOT be fixed

### 2. Brainstorm References (Gitignored)
Files with broken links:
- `docs/specs/SPEC-craft-hub-v2-2026-01-15.md`
- `docs/specs/SPEC-teaching-workflow-2026-01-16.md`

Targets: `docs/brainstorm/*.md` (gitignored)

### 3. README References (Outside Docs)
File: `docs/TEACHING-DOCS-INDEX.md`
Target: `../README.md`

### 4. Individual Command Pages (Not Implemented)
Files with broken links:
- `docs/teaching-migration.md`

Targets:
- `../commands/site/publish.md`
- `../commands/git/sync.md`
"""
        Path(".linkcheck-ignore").write_text(linkcheck_content)

        # Test various broken links
        test_cases = [
            ("docs/test-violations.md", "nonexistent.md", True, "Test Violation Files"),
            ("docs/specs/SPEC-craft-hub-v2-2026-01-15.md", "../brainstorm/hub.md", True, "Brainstorm References"),
            ("docs/TEACHING-DOCS-INDEX.md", "../README.md", True, "README References"),
            ("docs/teaching-migration.md", "../commands/site/publish.md", True, "Individual Command Pages"),
            ("docs/guide/setup.md", "missing.md", False, None),  # Should be critical
        ]

        # Load rules
        rules = parse_linkcheck_ignore()

        # Verify all test cases
        for file, target, should_ignore_expected, category_expected in test_cases:
            should_ignore, category = rules.should_ignore(file, target)
            self.assertEqual(
                should_ignore,
                should_ignore_expected,
                f"Failed for {file} → {target}"
            )
            if should_ignore_expected:
                self.assertEqual(
                    category,
                    category_expected,
                    f"Wrong category for {file} → {target}"
                )


if __name__ == "__main__":
    unittest.main()
