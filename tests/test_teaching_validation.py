"""Unit tests for teaching content validation.

Tests all validation functions with mock course structures:
- Syllabus validation (complete and incomplete)
- Schedule validation (complete and with gaps)
- Assignment validation (all exist and some missing)
- ValidationResult logic and formatting
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.utils.teaching_validation import (
    ValidationResult,
    validate_syllabus,
    validate_schedule,
    validate_assignments,
    validate_teaching_content,
)


class TestValidationResult(unittest.TestCase):
    """Test ValidationResult dataclass."""

    def test_can_publish_no_errors(self):
        """Should allow publish when no errors."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=["Some warning"],
            checks={"test": True}
        )
        self.assertTrue(result.can_publish())

    def test_can_publish_with_errors(self):
        """Should block publish when errors exist."""
        result = ValidationResult(
            valid=False,
            errors=["Critical error"],
            warnings=[],
            checks={"test": False}
        )
        self.assertFalse(result.can_publish())

    def test_format_report_success(self):
        """Should format success report correctly."""
        result = ValidationResult(
            valid=True,
            errors=[],
            warnings=["Minor issue"],
            checks={
                "Check 1": True,
                "Check 2": True,
            }
        )
        report = result.format_report()

        self.assertIn("READY TO PUBLISH", report)
        self.assertIn("2/2 checks passed", report)
        self.assertIn("Minor issue", report)
        self.assertIn("✓", report)

    def test_format_report_errors(self):
        """Should format error report correctly."""
        result = ValidationResult(
            valid=False,
            errors=["Error 1", "Error 2"],
            warnings=["Warning 1"],
            checks={
                "Check 1": True,
                "Check 2": False,
            }
        )
        report = result.format_report()

        self.assertIn("BLOCKED", report)
        self.assertIn("Error 1", report)
        self.assertIn("Error 2", report)
        self.assertIn("Warning 1", report)
        self.assertIn("2 error(s) blocking", report)


class TestValidateSyllabus(unittest.TestCase):
    """Test syllabus validation."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_no_syllabus(self):
        """Should return all False when no syllabus exists."""
        result = validate_syllabus(self.test_dir)

        self.assertFalse(result['grading'])
        self.assertFalse(result['policies'])
        self.assertFalse(result['objectives'])
        self.assertFalse(result['schedule'])

    def test_complete_syllabus(self):
        """Should find all sections in complete syllabus."""
        syllabus_content = """
# Course Syllabus

## Learning Objectives
Students will learn statistical methods.

## Course Policies
Attendance is required.

## Grading
- Homework: 40%
- Exams: 60%

## Schedule
Week 1: Introduction
        """

        syllabus_path = Path(self.test_dir) / 'syllabus.qmd'
        syllabus_path.write_text(syllabus_content)

        result = validate_syllabus(self.test_dir)

        self.assertTrue(result['grading'])
        self.assertTrue(result['policies'])
        self.assertTrue(result['objectives'])
        self.assertTrue(result['schedule'])

    def test_partial_syllabus(self):
        """Should detect missing sections."""
        syllabus_content = """
# Course Syllabus

## Grading Policy
Homework counts for everything.

## Learning Goals
Learn statistics.
        """

        syllabus_path = Path(self.test_dir) / 'syllabus.qmd'
        syllabus_path.write_text(syllabus_content)

        result = validate_syllabus(self.test_dir)

        self.assertTrue(result['grading'])
        self.assertTrue(result['objectives'])
        self.assertFalse(result['policies'])
        self.assertFalse(result['schedule'])

    def test_syllabus_subdirectory(self):
        """Should find syllabus in subdirectory."""
        syllabus_dir = Path(self.test_dir) / 'syllabus'
        syllabus_dir.mkdir()

        syllabus_content = """
# Syllabus

## Assessment
Graded on participation.
        """

        (syllabus_dir / 'index.qmd').write_text(syllabus_content)

        result = validate_syllabus(self.test_dir)

        self.assertTrue(result['grading'])

    def test_case_insensitive_matching(self):
        """Should match section headers case-insensitively."""
        syllabus_content = """
# SYLLABUS

## GRADING POLICY
All caps should work.

## course POLICIES
Mixed case too.
        """

        syllabus_path = Path(self.test_dir) / 'syllabus.qmd'
        syllabus_path.write_text(syllabus_content)

        result = validate_syllabus(self.test_dir)

        self.assertTrue(result['grading'])
        self.assertTrue(result['policies'])


class TestValidateSchedule(unittest.TestCase):
    """Test schedule validation."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_no_schedule(self):
        """Should return empty result when no schedule exists."""
        result = validate_schedule(self.test_dir)

        self.assertEqual(result['total_weeks'], 0)
        self.assertEqual(result['complete_weeks'], 0)
        self.assertEqual(result['gaps'], [])

    def test_complete_schedule(self):
        """Should validate complete schedule with no gaps."""
        schedule_content = """
# Course Schedule

## Week 1
Introduction to statistics. Read Chapter 1.
Assignment: HW 1 due Friday.

## Week 2
Descriptive statistics. Read Chapter 2.
Assignment: HW 2 due next Friday.

## Week 3
Probability basics. Read Chapter 3.
Quiz on Friday covering Weeks 1-2.
        """

        schedule_path = Path(self.test_dir) / 'schedule.qmd'
        schedule_path.write_text(schedule_content)

        result = validate_schedule(self.test_dir)

        self.assertEqual(result['total_weeks'], 3)
        self.assertEqual(result['complete_weeks'], 3)
        self.assertEqual(result['gaps'], [])

    def test_schedule_with_gaps(self):
        """Should detect weeks with missing content."""
        schedule_content = """
# Course Schedule

## Week 1
Introduction to statistics. Read Chapter 1.

## Week 2

## Week 3
Probability basics. Read Chapter 3.

## Week 4
        """

        schedule_path = Path(self.test_dir) / 'schedule.qmd'
        schedule_path.write_text(schedule_content)

        result = validate_schedule(self.test_dir)

        self.assertEqual(result['total_weeks'], 4)
        self.assertEqual(result['complete_weeks'], 2)
        self.assertIn(2, result['gaps'])
        self.assertIn(4, result['gaps'])

    def test_flexible_week_headers(self):
        """Should match various week header formats."""
        schedule_content = """
# Schedule

## Week 1
Content here that is long enough to pass validation.

### Week 2:
More content that is also long enough to pass.

#### Week 3 - Topic Name
Even more content with sufficient length to pass validation.
        """

        schedule_path = Path(self.test_dir) / 'schedule.qmd'
        schedule_path.write_text(schedule_content)

        result = validate_schedule(self.test_dir)

        self.assertEqual(result['total_weeks'], 3)
        self.assertEqual(result['complete_weeks'], 3)

    def test_schedule_subdirectory(self):
        """Should find schedule in subdirectory."""
        schedule_dir = Path(self.test_dir) / 'schedule'
        schedule_dir.mkdir()

        schedule_content = """
## Week 1
Some content here that is long enough to count.
        """

        (schedule_dir / 'index.qmd').write_text(schedule_content)

        result = validate_schedule(self.test_dir)

        self.assertEqual(result['total_weeks'], 1)
        self.assertEqual(result['complete_weeks'], 1)


class TestValidateAssignments(unittest.TestCase):
    """Test assignment validation."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_no_schedule(self):
        """Should return empty result when no schedule exists."""
        result = validate_assignments(self.test_dir)

        self.assertEqual(result['referenced'], [])
        self.assertEqual(result['missing'], [])
        self.assertEqual(result['found'], [])

    def test_all_assignments_exist(self):
        """Should find all referenced assignments."""
        schedule_content = """
# Schedule

## Week 1
Complete HW 1 by Friday.

## Week 2
Submit Assignment 2 next week.

## Week 3
Homework 3 due soon.
        """

        schedule_path = Path(self.test_dir) / 'schedule.qmd'
        schedule_path.write_text(schedule_content)

        # Create assignment files
        assignments_dir = Path(self.test_dir) / 'assignments'
        assignments_dir.mkdir()

        (assignments_dir / 'hw-1.qmd').write_text("# HW 1")
        (assignments_dir / 'hw-2.qmd').write_text("# HW 2")
        (assignments_dir / 'hw-3.qmd').write_text("# HW 3")

        result = validate_assignments(self.test_dir)

        self.assertEqual(len(result['referenced']), 3)
        self.assertIn("HW 1", result['referenced'])
        self.assertIn("HW 2", result['referenced'])
        self.assertIn("HW 3", result['referenced'])
        self.assertEqual(len(result['found']), 3)
        self.assertEqual(len(result['missing']), 0)

    def test_some_assignments_missing(self):
        """Should detect missing assignment files."""
        schedule_content = """
# Schedule

## Week 1
HW 1 due Friday.

## Week 2
HW 2 due Friday.

## Week 3
HW 3 due Friday.
        """

        schedule_path = Path(self.test_dir) / 'schedule.qmd'
        schedule_path.write_text(schedule_content)

        # Create only HW 1 and HW 3
        assignments_dir = Path(self.test_dir) / 'assignments'
        assignments_dir.mkdir()

        (assignments_dir / 'hw-1.qmd').write_text("# HW 1")
        (assignments_dir / 'hw-3.qmd').write_text("# HW 3")

        result = validate_assignments(self.test_dir)

        self.assertEqual(len(result['referenced']), 3)
        self.assertEqual(len(result['found']), 2)
        self.assertIn("HW 2", result['missing'])

    def test_various_assignment_formats(self):
        """Should match different assignment reference formats."""
        schedule_content = """
# Schedule

Week 1: HW1 due
Week 2: HW 2 due
Week 3: Assignment 3 due
Week 4: Homework 4 due
        """

        schedule_path = Path(self.test_dir) / 'schedule.qmd'
        schedule_path.write_text(schedule_content)

        result = validate_assignments(self.test_dir)

        self.assertEqual(len(result['referenced']), 4)
        # All should be missing since we didn't create files
        self.assertEqual(len(result['missing']), 4)

    def test_assignment_subdirectories(self):
        """Should find assignments in subdirectories."""
        schedule_content = """
HW 1 is available.
        """

        schedule_path = Path(self.test_dir) / 'schedule.qmd'
        schedule_path.write_text(schedule_content)

        # Create assignment in subdirectory
        assignments_dir = Path(self.test_dir) / 'assignments' / 'hw-1'
        assignments_dir.mkdir(parents=True)
        (assignments_dir / 'index.qmd').write_text("# HW 1")

        result = validate_assignments(self.test_dir)

        self.assertIn("HW 1", result['found'])


class TestValidateTeachingContent(unittest.TestCase):
    """Test comprehensive teaching content validation."""

    def setUp(self):
        """Create temporary directory for tests."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_complete_valid_course(self):
        """Should pass validation for complete course."""
        # Create complete syllabus
        syllabus_content = """
# Syllabus

## Learning Objectives
Students will master statistics.

## Course Policies
Be respectful and on time.

## Grading
Homework 50%, Exams 50%.

## Schedule
See full schedule page.
        """
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        # Create complete schedule
        schedule_content = """
## Week 1
Introduction. Read Chapter 1. HW 1 due Friday.

## Week 2
More content. Read Chapter 2. HW 2 due Friday.
        """
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        # Create assignments
        assignments_dir = Path(self.test_dir) / 'assignments'
        assignments_dir.mkdir()
        (assignments_dir / 'hw-1.qmd').write_text("# HW 1")
        (assignments_dir / 'hw-2.qmd').write_text("# HW 2")

        result = validate_teaching_content(self.test_dir)

        self.assertTrue(result.can_publish())
        self.assertEqual(len(result.errors), 0)
        # Warnings allowed (none in this case)
        self.assertTrue(result.valid)

    def test_missing_syllabus_sections(self):
        """Should error on missing syllabus sections."""
        # Incomplete syllabus
        syllabus_content = """
# Syllabus

## Grading
Homework counts.
        """
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        # Complete schedule
        schedule_content = """
## Week 1
Content here that is long enough.
        """
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        result = validate_teaching_content(self.test_dir)

        self.assertFalse(result.can_publish())
        self.assertGreater(len(result.errors), 0)
        self.assertIn("Syllabus missing required sections", result.errors[0])

    def test_incomplete_schedule(self):
        """Should error on incomplete schedule weeks."""
        # Complete syllabus
        syllabus_content = """
# Syllabus

## Objectives
Learn stats.

## Policies
Attendance required.

## Grading
Homework 100%.

## Schedule
See schedule page.
        """
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        # Incomplete schedule
        schedule_content = """
## Week 1
Good content here.

## Week 2

## Week 3
More good content.
        """
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        result = validate_teaching_content(self.test_dir)

        self.assertFalse(result.can_publish())
        self.assertGreater(len(result.errors), 0)
        self.assertTrue(any("incomplete weeks" in e for e in result.errors))

    def test_missing_assignments_warning(self):
        """Should warn (not error) on missing assignments."""
        # Complete syllabus
        syllabus_content = """
# Syllabus

## Objectives
Learn.

## Policies
Rules.

## Grading
Grades.

## Schedule
Times.
        """
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        # Schedule referencing assignments
        schedule_content = """
## Week 1
Complete HW 1 by Friday. Lots of content here.

## Week 2
Complete HW 2 by Friday. More content here.
        """
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        # Don't create assignment files

        result = validate_teaching_content(self.test_dir)

        # Should still be publishable (warnings don't block)
        self.assertTrue(result.can_publish())
        # But should have warnings
        self.assertGreater(len(result.warnings), 0)
        self.assertTrue(any("Missing assignment files" in w for w in result.warnings))

    def test_checks_populated(self):
        """Should populate detailed checks dict."""
        # Minimal valid course
        syllabus_content = """
# Syllabus
## Objectives
Learn.
## Policies
Rules.
## Grading
Grades.
## Schedule
Times.
        """
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        schedule_content = """
## Week 1
Content with sufficient length to pass validation.
        """
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        result = validate_teaching_content(self.test_dir)

        # Should have checks for syllabus sections
        self.assertIn('Syllabus: grading', result.checks)
        self.assertIn('Syllabus: policies', result.checks)
        self.assertIn('Syllabus: objectives', result.checks)
        self.assertIn('Syllabus: schedule', result.checks)

        # Should have schedule checks
        self.assertIn('Schedule: exists', result.checks)

    def test_format_report(self):
        """Should generate formatted report."""
        # Course with one error and one warning
        syllabus_content = """
# Syllabus
## Grading
Grades.
        """
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        schedule_content = """
## Week 1
HW 1 due Friday. Good content here.
        """
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        result = validate_teaching_content(self.test_dir)
        report = result.format_report()

        # Should be blocked
        self.assertIn("BLOCKED", report)

        # Should show errors
        self.assertIn("ERRORS", report)

        # Should show warnings
        self.assertIn("WARNINGS", report)

        # Should show checks
        self.assertIn("DETAILED CHECKS", report)


if __name__ == '__main__':
    unittest.main()
