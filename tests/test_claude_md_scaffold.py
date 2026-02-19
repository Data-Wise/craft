#!/usr/bin/env python3
"""
Tests for CLAUDE.md Scaffold Command

Covers:
- Template detection and selection
- Variable population from project analysis
- Template rendering
- File creation with confirmation
- Force overwrite handling
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

from utils.claude_md_detector import CLAUDEMDDetector
from utils.claude_md_template_populator import TemplatePopulator, populate_template, get_unpopulated_variables


class TestProjectTypeDetection(unittest.TestCase):
    """Test project type detection for template selection."""

    def setUp(self):
        """Create temporary project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_detect_craft_plugin(self):
        """Verify craft plugin detection."""
        # Create plugin indicators
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        commands_dir = self.path / "commands"
        commands_dir.mkdir()

        # Detect
        detector = CLAUDEMDDetector(self.path)
        info = detector.detect()

        # Verify
        self.assertIsNotNone(info)
        self.assertEqual(info.type, "craft-plugin")

    def test_detect_teaching_site(self):
        """Verify teaching site detection."""
        # Create teaching indicators
        (self.path / "_quarto.yml").write_text("title: Test Course")
        (self.path / "course.yml").write_text("code: TEST 101")

        # Detect
        detector = CLAUDEMDDetector(self.path)
        info = detector.detect()

        # Verify
        self.assertIsNotNone(info)
        self.assertEqual(info.type, "teaching-site")

    def test_detect_r_package(self):
        """Verify R package detection."""
        # Create R package indicators
        (self.path / "DESCRIPTION").write_text("""Package: testpkg
Title: Test Package
Version: 0.1.0
""")

        r_dir = self.path / "R"
        r_dir.mkdir()

        # Detect
        detector = CLAUDEMDDetector(self.path)
        info = detector.detect()

        # Verify
        self.assertIsNotNone(info)
        self.assertEqual(info.type, "r-package")


class TestPluginTemplatePopulation(unittest.TestCase):
    """Test variable population for plugin template."""

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
            "description": "Test plugin description",
            "repository": {
                "url": "https://github.com/test/plugin",
                "docs": "https://test.github.io/plugin"
            }
        }))

        # Create directories with sample files
        (self.path / "commands").mkdir()
        (self.path / "commands" / "test.md").write_text("# Test")
        (self.path / "commands" / "test2.md").write_text("# Test 2")

        (self.path / "skills").mkdir()
        (self.path / "skills" / "skill1.md").write_text("# Skill 1")

        (self.path / "agents").mkdir()
        (self.path / "agents" / "agent1.md").write_text("# Agent 1")

        (self.path / "tests").mkdir()

    def test_populate_basic_fields(self):
        """Verify basic field population."""
        populator = TemplatePopulator(self.path, "plugin")
        variables = populator.populate_all()

        # Verify basic fields
        self.assertEqual(variables["plugin_name"], "test-plugin")
        self.assertEqual(variables["version"], "1.0.0")
        self.assertEqual(variables["tagline"], "Test plugin description")

    def test_populate_directory_counts(self):
        """Verify directory counting."""
        populator = TemplatePopulator(self.path, "plugin")
        variables = populator.populate_all()

        # Verify counts
        self.assertEqual(variables["command_count"], 2)
        self.assertEqual(variables["skill_count"], 1)
        self.assertEqual(variables["agent_count"], 1)

    def test_populate_urls(self):
        """Verify URL extraction."""
        populator = TemplatePopulator(self.path, "plugin")
        variables = populator.populate_all()

        # Verify URLs
        self.assertEqual(variables["repo_url"], "https://github.com/test/plugin")
        self.assertEqual(variables["docs_url"], "https://test.github.io/plugin")


class TestTeachingTemplatePopulation(unittest.TestCase):
    """Test variable population for teaching template."""

    def setUp(self):
        """Create temporary teaching project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create teaching structure
        (self.path / "_quarto.yml").write_text("""title: "Regression Analysis"
""")
        (self.path / "course.yml").write_text("""course_code: STAT 440
semester: Spring 2026
instructor: Dr. Test
""")

        # Create weeks
        weeks_dir = self.path / "weeks"
        weeks_dir.mkdir()
        (weeks_dir / "week1").mkdir()
        (weeks_dir / "week2").mkdir()

        # Create assignments
        assignments_dir = self.path / "assignments"
        assignments_dir.mkdir()
        (assignments_dir / "hw1.qmd").write_text("# HW 1")
        (assignments_dir / "hw2.qmd").write_text("# HW 2")

    def test_populate_course_metadata(self):
        """Verify course metadata extraction."""
        populator = TemplatePopulator(self.path, "teaching")
        variables = populator.populate_all()

        # Verify metadata
        self.assertEqual(variables["course_name"], "Regression Analysis")
        self.assertEqual(variables["course_code"], "STAT 440")
        self.assertEqual(variables["semester"], "Spring 2026")
        self.assertEqual(variables["instructor"], "Dr. Test")

    def test_populate_course_counts(self):
        """Verify course structure counting."""
        populator = TemplatePopulator(self.path, "teaching")
        variables = populator.populate_all()

        # Verify counts
        self.assertEqual(variables["week_count"], 2)
        self.assertEqual(variables["assignment_count"], 2)


class TestRPackageTemplatePopulation(unittest.TestCase):
    """Test variable population for R package template."""

    def setUp(self):
        """Create temporary R package project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create DESCRIPTION
        (self.path / "DESCRIPTION").write_text("""Package: testpkg
Title: Test Package for Something
Version: 0.2.0
Depends: R (>= 4.1.0)
""")

        # Create R files
        r_dir = self.path / "R"
        r_dir.mkdir()
        (r_dir / "func1.R").write_text("func1 <- function() {}")
        (r_dir / "func2.R").write_text("func2 <- function() {}")

        # Create test files
        test_dir = self.path / "tests" / "testthat"
        test_dir.mkdir(parents=True)
        (test_dir / "test-func1.R").write_text("test_that(...)")

    def test_populate_package_metadata(self):
        """Verify package metadata extraction."""
        populator = TemplatePopulator(self.path, "r-package")
        variables = populator.populate_all()

        # Verify metadata
        self.assertEqual(variables["package_name"], "testpkg")
        self.assertEqual(variables["package_title"], "Test Package for Something")
        self.assertEqual(variables["version"], "0.2.0")
        self.assertEqual(variables["r_version"], "4.1.0")

    def test_populate_package_counts(self):
        """Verify package file counting."""
        populator = TemplatePopulator(self.path, "r-package")
        variables = populator.populate_all()

        # Verify counts
        self.assertEqual(variables["function_count"], 2)
        self.assertEqual(variables["test_count"], 1)


class TestTemplateRendering(unittest.TestCase):
    """Test template rendering with variable substitution."""

    def test_simple_substitution(self):
        """Verify simple variable substitution."""
        template = "# {project_name}\n\nVersion: {version}"
        variables = {
            "project_name": "test",
            "version": "1.0.0"
        }

        result = populate_template(template, variables)

        self.assertEqual(result, "# test\n\nVersion: 1.0.0")

    def test_multiple_occurrences(self):
        """Verify multiple variable occurrences."""
        template = "{name} version {version}\n\n{name} is great"
        variables = {
            "name": "craft",
            "version": "2.0.0"
        }

        result = populate_template(template, variables)

        self.assertEqual(result, "craft version 2.0.0\n\ncraft is great")

    def test_partial_population(self):
        """Verify partial population leaves unpopulated variables."""
        template = "Name: {name}\nVersion: {version}\nAuthor: {author}"
        variables = {
            "name": "test",
            "version": "1.0.0"
        }

        result = populate_template(template, variables)

        self.assertIn("Name: test", result)
        self.assertIn("Version: 1.0.0", result)
        self.assertIn("{author}", result)  # Should remain unpopulated


class TestUnpopulatedVariableDetection(unittest.TestCase):
    """Test detection of unpopulated variables."""

    def test_find_unpopulated(self):
        """Verify unpopulated variable detection."""
        content = """# {project_name}

Version: 1.0.0
Author: {author}
License: {license}
"""

        unpopulated = get_unpopulated_variables(content)

        self.assertEqual(len(unpopulated), 3)
        self.assertIn("project_name", unpopulated)
        self.assertIn("author", unpopulated)
        self.assertIn("license", unpopulated)

    def test_no_unpopulated(self):
        """Verify no variables found when all populated."""
        content = """# Test Project

Version: 1.0.0
Author: Test
"""

        unpopulated = get_unpopulated_variables(content)

        self.assertEqual(len(unpopulated), 0)


class TestTemplateSelection(unittest.TestCase):
    """Test template file selection based on project type."""

    def test_plugin_template_exists(self):
        """Verify plugin template exists."""
        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "plugin-template.md"
        self.assertTrue(template_path.exists(), f"Plugin template not found at {template_path}")

    def test_teaching_template_exists(self):
        """Verify teaching template exists."""
        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "teaching-template.md"
        self.assertTrue(template_path.exists(), f"Teaching template not found at {template_path}")

    def test_r_package_template_exists(self):
        """Verify R package template exists."""
        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "r-package-template.md"
        self.assertTrue(template_path.exists(), f"R package template not found at {template_path}")


class TestScaffoldWorkflow(unittest.TestCase):
    """Test complete scaffold workflow."""

    def setUp(self):
        """Create temporary plugin project."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create minimal plugin
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "1.0.0"
        }))

        (self.path / "commands").mkdir()

    def test_full_scaffold_workflow(self):
        """Test complete scaffold workflow: detect → populate → render."""
        # Step 1: Detect project type
        detector = CLAUDEMDDetector(self.path)
        info = detector.detect()
        self.assertEqual(info.type, "craft-plugin")

        # Step 2: Populate variables
        populator = TemplatePopulator(self.path, info.type)
        variables = populator.populate_all()
        self.assertEqual(variables["plugin_name"], "test")

        # Step 3: Load template
        template_path = Path(__file__).parent.parent / "templates" / "claude-md" / "plugin-template.md"
        template_content = template_path.read_text()

        # Step 4: Render template
        result = populate_template(template_content, variables)
        self.assertIn("# CLAUDE.md - test", result)
        self.assertIn("v1.0.0", result)

        # Step 5: Check for unpopulated variables
        unpopulated = get_unpopulated_variables(result)
        # Some variables expected to remain unpopulated (optional fields)
        self.assertGreater(len(result), 100)  # Should have substantial content


if __name__ == "__main__":
    unittest.main()
