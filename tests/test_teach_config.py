#!/usr/bin/env python3
"""
Unit tests for teaching configuration parser.

Tests cover:
- Valid configurations (complete and minimal)
- Invalid YAML syntax
- Missing required fields
- Date validation (format, logical order)
- Break validation (dates, overlaps, semester bounds)
- Config path detection (.flow/ vs root)
- Default value application
- Edge cases and error handling

Run:
    python3 -m pytest tests/test_teach_config.py -v
    python3 tests/test_teach_config.py  # Direct execution
"""

import os
import sys
import tempfile
import unittest
from datetime import datetime
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.utils.teach_config import (
    get_config_path,
    validate_date,
    parse_date,
    validate_breaks,
    apply_defaults,
    validate_config,
    load_teach_config,
    DEFAULTS,
    VALID_SEMESTERS,
)


class TestValidateDate(unittest.TestCase):
    """Test date validation function"""

    def test_valid_dates(self):
        """Valid YYYY-MM-DD dates should pass"""
        valid_dates = [
            "2026-01-19",
            "2025-12-31",
            "2000-01-01",
            "2099-12-31",
        ]
        for date_str in valid_dates:
            with self.subTest(date=date_str):
                self.assertTrue(validate_date(date_str))

    def test_invalid_format(self):
        """Invalid date formats should fail"""
        invalid_dates = [
            "2026/01/19",  # Wrong separator
            "01-19-2026",  # Wrong order
            "2026-1-19",   # Missing zero padding
            "2026-13-01",  # Invalid month
            "2026-01-32",  # Invalid day
            "not-a-date",  # Text
            "",            # Empty
            None,          # None type
        ]
        for date_str in invalid_dates:
            with self.subTest(date=date_str):
                self.assertFalse(validate_date(date_str))


class TestParseDate(unittest.TestCase):
    """Test date parsing function"""

    def test_parse_valid_date(self):
        """Valid dates should parse to datetime objects"""
        result = parse_date("2026-01-19")
        self.assertIsInstance(result, datetime)
        self.assertEqual(result.year, 2026)
        self.assertEqual(result.month, 1)
        self.assertEqual(result.day, 19)

    def test_parse_invalid_date(self):
        """Invalid dates should return None"""
        self.assertIsNone(parse_date("invalid"))
        self.assertIsNone(parse_date("2026/01/19"))
        self.assertIsNone(parse_date(None))


class TestValidateBreaks(unittest.TestCase):
    """Test break validation function"""

    def test_empty_breaks(self):
        """Empty breaks list should be valid"""
        errors = validate_breaks([], "2026-01-19", "2026-05-08")
        self.assertEqual(errors, [])

    def test_valid_break(self):
        """Valid break should pass validation"""
        breaks = [
            {
                "name": "Spring Break",
                "start": "2026-03-16",
                "end": "2026-03-20",
            }
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertEqual(errors, [])

    def test_multiple_valid_breaks(self):
        """Multiple non-overlapping breaks should be valid"""
        breaks = [
            {
                "name": "Spring Break",
                "start": "2026-03-16",
                "end": "2026-03-20",
            },
            {
                "name": "Reading Week",
                "start": "2026-04-13",
                "end": "2026-04-14",
            },
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertEqual(errors, [])

    def test_missing_name(self):
        """Break missing name should fail"""
        breaks = [{"start": "2026-03-16", "end": "2026-03-20"}]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("missing 'name'" in e for e in errors))

    def test_missing_start(self):
        """Break missing start should fail"""
        breaks = [{"name": "Spring Break", "end": "2026-03-20"}]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("missing 'start'" in e for e in errors))

    def test_missing_end(self):
        """Break missing end should fail"""
        breaks = [{"name": "Spring Break", "start": "2026-03-16"}]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("missing 'end'" in e for e in errors))

    def test_invalid_date_format(self):
        """Break with invalid date format should fail"""
        breaks = [
            {
                "name": "Spring Break",
                "start": "2026/03/16",
                "end": "2026-03-20",
            }
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("invalid start date format" in e for e in errors))

    def test_end_before_start(self):
        """Break with end before start should fail"""
        breaks = [
            {
                "name": "Spring Break",
                "start": "2026-03-20",
                "end": "2026-03-16",
            }
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("start date must be before end date" in e for e in errors))

    def test_break_before_semester(self):
        """Break starting before semester should fail"""
        breaks = [
            {
                "name": "Winter Break",
                "start": "2026-01-01",
                "end": "2026-01-18",
            }
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("starts before semester begins" in e for e in errors))

    def test_break_after_semester(self):
        """Break ending after semester should fail"""
        breaks = [
            {
                "name": "Summer Break",
                "start": "2026-05-07",
                "end": "2026-05-15",
            }
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("ends after semester ends" in e for e in errors))

    def test_overlapping_breaks(self):
        """Overlapping breaks should fail"""
        breaks = [
            {
                "name": "Break 1",
                "start": "2026-03-16",
                "end": "2026-03-20",
            },
            {
                "name": "Break 2",
                "start": "2026-03-19",  # Overlaps with Break 1
                "end": "2026-03-23",
            },
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("overlap" in e for e in errors))

    def test_invalid_semester_dates(self):
        """Invalid semester dates should fail gracefully"""
        breaks = [
            {
                "name": "Spring Break",
                "start": "2026-03-16",
                "end": "2026-03-20",
            }
        ]
        errors = validate_breaks(breaks, "invalid", "2026-05-08")
        self.assertTrue(any("invalid semester dates" in e for e in errors))


class TestApplyDefaults(unittest.TestCase):
    """Test default value application"""

    def test_apply_all_defaults(self):
        """Empty config should get all defaults"""
        config = {"course": {}, "dates": {}}
        result = apply_defaults(config)

        # Check deployment defaults
        self.assertIn("deployment", result)
        self.assertEqual(result["deployment"]["production_branch"], "production")
        self.assertEqual(result["deployment"]["draft_branch"], "draft")

        # Check progress defaults
        self.assertIn("progress", result)
        self.assertEqual(result["progress"]["current_week"], "auto")

        # Check validation defaults
        self.assertIn("validation", result)
        self.assertEqual(result["validation"]["strict_mode"], True)
        self.assertIn("grading", result["validation"]["required_sections"])

        # Check dates defaults
        self.assertIn("breaks", result["dates"])
        self.assertEqual(result["dates"]["breaks"], [])

    def test_preserve_existing_values(self):
        """Existing values should not be overwritten"""
        config = {
            "course": {},
            "dates": {"breaks": [{"name": "test"}]},
            "deployment": {"production_branch": "prod"},
            "progress": {"current_week": 5},
            "validation": {"strict_mode": False},
        }
        result = apply_defaults(config)

        self.assertEqual(result["deployment"]["production_branch"], "prod")
        self.assertEqual(result["progress"]["current_week"], 5)
        self.assertEqual(result["validation"]["strict_mode"], False)
        self.assertEqual(len(result["dates"]["breaks"]), 1)


class TestValidateConfig(unittest.TestCase):
    """Test configuration validation"""

    def get_minimal_valid_config(self):
        """Return minimal valid configuration"""
        return {
            "course": {
                "number": "STAT 545",
                "title": "Regression Analysis",
                "semester": "Spring",
                "year": 2026,
            },
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08",
                "breaks": [],
            },
        }

    def test_valid_minimal_config(self):
        """Minimal valid config should pass"""
        config = self.get_minimal_valid_config()
        errors = validate_config(config)
        self.assertEqual(errors, [])

    def test_missing_course_section(self):
        """Missing course section should fail"""
        config = {"dates": {"start": "2026-01-19", "end": "2026-05-08"}}
        errors = validate_config(config)
        self.assertTrue(any("Missing required section: 'course'" in e for e in errors))

    def test_missing_dates_section(self):
        """Missing dates section should fail"""
        config = {
            "course": {
                "number": "STAT 545",
                "title": "Test",
                "semester": "Spring",
                "year": 2026,
            }
        }
        errors = validate_config(config)
        self.assertTrue(any("Missing required section: 'dates'" in e for e in errors))

    def test_missing_course_fields(self):
        """Missing required course fields should fail"""
        config = self.get_minimal_valid_config()
        del config["course"]["number"]
        errors = validate_config(config)
        self.assertTrue(any("course.number" in e for e in errors))

    def test_invalid_semester(self):
        """Invalid semester value should fail"""
        config = self.get_minimal_valid_config()
        config["course"]["semester"] = "Invalid"
        errors = validate_config(config)
        self.assertTrue(any("Invalid semester" in e for e in errors))

    def test_invalid_year_type(self):
        """Non-integer year should fail"""
        config = self.get_minimal_valid_config()
        config["course"]["year"] = "2026"
        errors = validate_config(config)
        self.assertTrue(any("Invalid year" in e for e in errors))

    def test_invalid_year_range(self):
        """Year out of range should fail"""
        config = self.get_minimal_valid_config()
        config["course"]["year"] = 1999
        errors = validate_config(config)
        self.assertTrue(any("must be between 2000 and 2100" in e for e in errors))

    def test_invalid_start_date(self):
        """Invalid start date format should fail"""
        config = self.get_minimal_valid_config()
        config["dates"]["start"] = "2026/01/19"
        errors = validate_config(config)
        self.assertTrue(any("Invalid start date format" in e for e in errors))

    def test_end_before_start(self):
        """End date before start should fail"""
        config = self.get_minimal_valid_config()
        config["dates"]["start"] = "2026-05-08"
        config["dates"]["end"] = "2026-01-19"
        errors = validate_config(config)
        self.assertTrue(any("end date must be after start date" in e for e in errors))

    def test_invalid_current_week_type(self):
        """Invalid current_week type should fail"""
        config = self.get_minimal_valid_config()
        config["progress"] = {"current_week": "five"}
        errors = validate_config(config)
        self.assertTrue(any("Invalid current_week" in e for e in errors))

    def test_invalid_current_week_range(self):
        """current_week out of range should fail"""
        config = self.get_minimal_valid_config()
        config["progress"] = {"current_week": 100}
        errors = validate_config(config)
        self.assertTrue(any("must be between 1 and 52" in e for e in errors))

    def test_invalid_strict_mode_type(self):
        """Non-boolean strict_mode should fail"""
        config = self.get_minimal_valid_config()
        config["validation"] = {"strict_mode": "yes"}
        errors = validate_config(config)
        self.assertTrue(any("Invalid strict_mode" in e for e in errors))


class TestGetConfigPath(unittest.TestCase):
    """Test config file path detection"""

    def test_flow_config_priority(self):
        """Should prefer .flow/teach-config.yml over root"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create both files
            flow_dir = Path(tmpdir) / ".flow"
            flow_dir.mkdir()
            flow_config = flow_dir / "teach-config.yml"
            flow_config.write_text("test: flow")

            root_config = Path(tmpdir) / "teach-config.yml"
            root_config.write_text("test: root")

            # Should return .flow version (resolve both paths for comparison)
            result = get_config_path(tmpdir)
            self.assertEqual(Path(result).resolve(), flow_config.resolve())

    def test_root_config_fallback(self):
        """Should use root config if .flow doesn't exist"""
        with tempfile.TemporaryDirectory() as tmpdir:
            root_config = Path(tmpdir) / "teach-config.yml"
            root_config.write_text("test: root")

            result = get_config_path(tmpdir)
            self.assertEqual(Path(result).resolve(), root_config.resolve())

    def test_no_config_found(self):
        """Should return None if no config exists"""
        with tempfile.TemporaryDirectory() as tmpdir:
            result = get_config_path(tmpdir)
            self.assertIsNone(result)


class TestLoadTeachConfig(unittest.TestCase):
    """Test full config loading and validation"""

    def test_load_complete_valid_config(self):
        """Complete valid config should load successfully"""
        config_yaml = """
course:
  number: "STAT 545"
  title: "Regression Analysis"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"
  breaks:
    - name: "Spring Break"
      start: "2026-03-16"
      end: "2026-03-20"

instructor:
  name: "Dr. Jane Smith"
  email: "jsmith@university.edu"
  office_hours: "Tu/Th 2-3pm"

deployment:
  production_branch: "production"
  draft_branch: "draft"
  gh_pages_url: "https://example.com"

progress:
  current_week: auto

validation:
  required_sections:
    - grading
    - policies
  strict_mode: true
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / ".flow" / "teach-config.yml"
            config_path.parent.mkdir()
            config_path.write_text(config_yaml)

            config = load_teach_config(tmpdir)
            self.assertIsNotNone(config)
            self.assertEqual(config["course"]["number"], "STAT 545")
            self.assertEqual(config["dates"]["start"], "2026-01-19")
            self.assertEqual(len(config["dates"]["breaks"]), 1)

    def test_load_minimal_config_with_defaults(self):
        """Minimal config should load with defaults applied"""
        config_yaml = """
course:
  number: "STAT 545"
  title: "Regression Analysis"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            config = load_teach_config(tmpdir)
            self.assertIsNotNone(config)

            # Check defaults applied
            self.assertEqual(config["deployment"]["production_branch"], "production")
            self.assertEqual(config["progress"]["current_week"], "auto")
            self.assertTrue(config["validation"]["strict_mode"])
            self.assertEqual(config["dates"]["breaks"], [])

    def test_no_config_returns_none(self):
        """Missing config should return None (not an error)"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config = load_teach_config(tmpdir)
            self.assertIsNone(config)

    def test_malformed_yaml_returns_none(self):
        """Malformed YAML should return None with warning"""
        config_yaml = """
course:
  number: "STAT 545"
  - invalid yaml structure
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            config = load_teach_config(tmpdir)
            self.assertIsNone(config)

    def test_invalid_config_raises_error(self):
        """Invalid config should raise ValueError"""
        config_yaml = """
course:
  number: "STAT 545"
  # Missing required fields
dates:
  start: "2026-01-19"
  end: "2026-05-08"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            with self.assertRaises(ValueError) as cm:
                load_teach_config(tmpdir)

            self.assertIn("validation failed", str(cm.exception))

    def test_non_dict_config_returns_none(self):
        """Non-dictionary YAML should return None"""
        config_yaml = "just a string"

        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            config = load_teach_config(tmpdir)
            self.assertIsNone(config)

    def test_invalid_breaks_raises_error(self):
        """Config with invalid breaks should raise ValueError"""
        config_yaml = """
course:
  number: "STAT 545"
  title: "Test"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"
  breaks:
    - name: "Spring Break"
      start: "2026-03-20"
      end: "2026-03-16"  # End before start
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            with self.assertRaises(ValueError) as cm:
                load_teach_config(tmpdir)

            self.assertIn("validation failed", str(cm.exception))


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions"""

    def test_leap_year_date(self):
        """Leap year dates should be valid"""
        self.assertTrue(validate_date("2024-02-29"))

    def test_non_leap_year_invalid(self):
        """Non-leap year Feb 29 should be invalid"""
        self.assertFalse(validate_date("2023-02-29"))

    def test_all_valid_semesters(self):
        """All valid semester values should pass"""
        for semester in VALID_SEMESTERS:
            config = {
                "course": {
                    "number": "TEST",
                    "title": "Test",
                    "semester": semester,
                    "year": 2026,
                },
                "dates": {
                    "start": "2026-01-19",
                    "end": "2026-05-08",
                },
            }
            errors = validate_config(config)
            self.assertEqual(errors, [])

    def test_current_week_auto_string(self):
        """current_week: auto should be valid"""
        config = {
            "course": {
                "number": "TEST",
                "title": "Test",
                "semester": "Spring",
                "year": 2026,
            },
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08",
            },
            "progress": {
                "current_week": "auto",
            },
        }
        errors = validate_config(config)
        self.assertEqual(errors, [])

    def test_current_week_integer(self):
        """current_week as integer should be valid"""
        config = {
            "course": {
                "number": "TEST",
                "title": "Test",
                "semester": "Spring",
                "year": 2026,
            },
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08",
            },
            "progress": {
                "current_week": 8,
            },
        }
        errors = validate_config(config)
        self.assertEqual(errors, [])

    def test_file_read_error(self):
        """File read errors should return None with warning"""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a directory instead of a file
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.mkdir()  # This will fail to read as YAML

            config = load_teach_config(tmpdir)
            self.assertIsNone(config)

    def test_validation_required_sections_optional(self):
        """validation.required_sections should be optional"""
        config_yaml = """
course:
  number: "STAT 545"
  title: "Test"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"

validation:
  strict_mode: false
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            config = load_teach_config(tmpdir)
            self.assertIsNotNone(config)
            # Should have default required_sections
            self.assertIn("required_sections", config["validation"])

    def test_instructor_section_optional(self):
        """Instructor section is completely optional"""
        config = {
            "course": {
                "number": "TEST",
                "title": "Test",
                "semester": "Spring",
                "year": 2026,
            },
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08",
            },
        }
        errors = validate_config(config)
        self.assertEqual(errors, [])

    def test_deployment_gh_pages_url_optional(self):
        """deployment.gh_pages_url is optional"""
        config_yaml = """
course:
  number: "STAT 545"
  title: "Test"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"

deployment:
  production_branch: "prod"
  draft_branch: "draft"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            config = load_teach_config(tmpdir)
            self.assertIsNotNone(config)
            self.assertEqual(config["deployment"]["production_branch"], "prod")
            self.assertNotIn("gh_pages_url", config["deployment"])

    def test_breaks_validation_with_multiple_errors(self):
        """Break validation should collect all errors"""
        breaks = [
            {
                "name": "Bad Break 1",
                "start": "2026-03-20",
                "end": "2026-03-16",  # End before start
            },
            {
                "name": "Bad Break 2",
                "start": "2026-01-01",  # Before semester
                "end": "2026-01-05",
            },
        ]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        # Should have multiple errors
        self.assertGreater(len(errors), 1)

    def test_breaks_not_a_dict(self):
        """Break that's not a dictionary should fail"""
        breaks = ["not a dict"]
        errors = validate_breaks(breaks, "2026-01-19", "2026-05-08")
        self.assertTrue(any("must be a dictionary" in e for e in errors))

    def test_config_without_instructor_section(self):
        """Config without instructor section should work"""
        config_yaml = """
course:
  number: "STAT 545"
  title: "Test"
  semester: "Spring"
  year: 2026

dates:
  start: "2026-01-19"
  end: "2026-05-08"
"""
        with tempfile.TemporaryDirectory() as tmpdir:
            config_path = Path(tmpdir) / "teach-config.yml"
            config_path.write_text(config_yaml)

            config = load_teach_config(tmpdir)
            self.assertIsNotNone(config)
            self.assertNotIn("instructor", config)

    def test_validation_section_partial(self):
        """Partial validation section should merge with defaults"""
        config = {
            "course": {
                "number": "TEST",
                "title": "Test",
                "semester": "Spring",
                "year": 2026,
            },
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08",
            },
            "validation": {
                "strict_mode": False,
                # required_sections should get default
            },
        }
        result = apply_defaults(config)
        self.assertIn("required_sections", result["validation"])
        self.assertEqual(result["validation"]["strict_mode"], False)

    def test_progress_section_partial(self):
        """Partial progress section should merge with defaults"""
        config = {
            "course": {"number": "TEST"},
            "dates": {"start": "2026-01-19"},
            "progress": {},  # Empty progress section
        }
        result = apply_defaults(config)
        self.assertEqual(result["progress"]["current_week"], "auto")

    def test_deployment_section_partial(self):
        """Partial deployment section should merge with defaults"""
        config = {
            "course": {"number": "TEST"},
            "dates": {"start": "2026-01-19"},
            "deployment": {
                "production_branch": "custom-prod",
                # draft_branch should get default
            },
        }
        result = apply_defaults(config)
        self.assertEqual(result["deployment"]["production_branch"], "custom-prod")
        self.assertEqual(result["deployment"]["draft_branch"], "draft")


if __name__ == "__main__":
    unittest.main()
