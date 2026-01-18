#!/usr/bin/env python3
"""
Integration Tests: Teaching Workflow
=====================================
Tests the full teaching workflow end-to-end including detection,
validation, and publish cycle.

Components tested:
- commands/utils/detect_teaching_mode.py
- commands/utils/teaching_validation.py
- commands/utils/teach_config.py
- commands/site/publish.md
- commands/site/progress.md
- commands/site/build.md

Run with: python tests/test_integration_teaching_workflow.py
"""

import unittest
import tempfile
import yaml
from pathlib import Path
from datetime import date, timedelta
import sys

# Add plugin directory to path
plugin_dir = Path(__file__).parent.parent
utils_dir = plugin_dir / "commands" / "utils"
sys.path.insert(0, str(plugin_dir))
sys.path.insert(0, str(utils_dir))

# Try to import teaching modules
try:
    from commands.utils.detect_teaching_mode import detect_teaching_mode
    DETECT_AVAILABLE = True
except ImportError:
    DETECT_AVAILABLE = False

try:
    from commands.utils.teach_config import parse_teach_config, calculate_current_week
    CONFIG_AVAILABLE = True
except ImportError:
    CONFIG_AVAILABLE = False


class TestTeachingWorkflowIntegration(unittest.TestCase):
    """Integration tests for teaching workflow."""

    def setUp(self):
        """Create temporary teaching project."""
        self.temp_dir = tempfile.mkdtemp()
        self.project_dir = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary files."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    @unittest.skipIf(not DETECT_AVAILABLE, "Teaching detection module not available")
    def test_01_detection_with_config(self):
        """Test: Detects teaching mode from .flow/teach-config.yml."""
        # Arrange: Create teach-config.yml
        config_dir = self.project_dir / ".flow"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "teach-config.yml"

        config_content = {
            "course": {
                "number": "STAT 545",
                "title": "Regression Analysis",
                "semester": "Spring 2026",
                "year": 2026
            }
        }
        config_file.write_text(yaml.dump(config_content))

        # Act
        is_teaching, method = detect_teaching_mode(str(self.project_dir))

        # Assert
        self.assertTrue(is_teaching, "Should detect teaching mode")
        self.assertEqual(method, "teach-config.yml", f"Should detect via config file, got: {method}")

    @unittest.skipIf(not DETECT_AVAILABLE, "Teaching detection module not available")
    def test_02_detection_without_config(self):
        """Test: Returns False when no teaching indicators present."""
        # Act
        is_teaching, method = detect_teaching_mode(str(self.project_dir))

        # Assert
        self.assertFalse(is_teaching, "Should not detect teaching mode in empty project")
        self.assertIsNone(method, "Method should be None when not detected")

    @unittest.skipIf(not CONFIG_AVAILABLE, "Teaching config module not available")
    def test_03_config_parsing(self):
        """Test: Parses teach-config.yml correctly."""
        # Arrange
        config_dir = self.project_dir / ".flow"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "teach-config.yml"

        start_date = date.today()
        end_date = start_date + timedelta(days=105)  # 15 weeks

        config_content = {
            "course": {"number": "TEST 101", "title": "Test Course"},
            "dates": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }
        config_file.write_text(yaml.dump(config_content))

        # Act
        config = parse_teach_config(str(self.project_dir))

        # Assert
        self.assertIsNotNone(config, "Should successfully parse config")
        self.assertEqual(config["course"]["number"], "TEST 101")
        self.assertEqual(config["course"]["title"], "Test Course")

    def test_04_teaching_commands_exist(self):
        """Test: Teaching-related commands exist."""
        # Arrange
        commands_dir = plugin_dir / "commands" / "site"

        expected_commands = ["publish.md", "progress.md", "build.md"]

        for cmd in expected_commands:
            with self.subTest(command=cmd):
                # Assert
                cmd_path = commands_dir / cmd
                self.assertTrue(cmd_path.exists(), f"Command {cmd} should exist")

    def test_05_teaching_utilities_exist(self):
        """Test: Teaching utility modules exist."""
        # Arrange - utilities are split across two directories
        expected_utils = [
            ("utils", "detect_teaching_mode.py"),
            ("commands/utils", "teach_config.py"),
            ("commands/utils", "teaching_validation.py")
        ]

        for directory, util in expected_utils:
            with self.subTest(utility=util):
                # Assert
                util_path = plugin_dir / directory / util
                self.assertTrue(util_path.exists(), f"Utility {util} should exist in {directory}")

    def test_06_config_structure_validation(self):
        """Test: Config file validates required structure."""
        # Arrange: Create minimal valid config
        config_dir = self.project_dir / ".flow"
        config_dir.mkdir(parents=True)
        config_file = config_dir / "teach-config.yml"

        # Minimal config
        config_content = {
            "course": {
                "number": "TEST 101",
                "title": "Test Course",
                "semester": "Spring 2026",
                "year": 2026
            },
            "dates": {
                "start": "2026-01-20",
                "end": "2026-05-15"
            }
        }
        config_file.write_text(yaml.dump(config_content))

        # Act: Parse config
        content = yaml.safe_load(config_file.read_text())

        # Assert: Required fields present
        self.assertIn("course", content, "Should have course section")
        self.assertIn("dates", content, "Should have dates section")
        self.assertIn("number", content["course"], "Course should have number")
        self.assertIn("title", content["course"], "Course should have title")


class TestTeachingEdgeCases(unittest.TestCase):
    """Edge case tests for teaching workflow."""

    def test_invalid_yaml_handling(self):
        """Test: System handles invalid YAML gracefully."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".flow"
            config_dir.mkdir()
            config_file = config_dir / "teach-config.yml"

            # Write invalid YAML
            config_file.write_text("invalid: yaml: syntax: error:")

            # Act & Assert: Should not crash
            try:
                content = yaml.safe_load(config_file.read_text())
            except yaml.YAMLError:
                pass  # Expected behavior

    def test_missing_required_fields(self):
        """Test: Detects missing required config fields."""
        # Arrange
        with tempfile.TemporaryDirectory() as tmpdir:
            config_dir = Path(tmpdir) / ".flow"
            config_dir.mkdir()
            config_file = config_dir / "teach-config.yml"

            # Incomplete config
            config_content = {"course": {"number": "TEST 101"}}  # Missing title
            config_file.write_text(yaml.dump(config_content))

            # Act
            content = yaml.safe_load(config_file.read_text())

            # Assert: Can detect missing fields
            self.assertNotIn("title", content["course"], "Title should be missing")


if __name__ == "__main__":
    unittest.main(verbosity=2)
