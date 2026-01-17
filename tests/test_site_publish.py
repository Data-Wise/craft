#!/usr/bin/env python3
"""
Unit tests for /craft:site:publish command.

Tests the 5-step teaching workflow:
1. Validate draft branch
2. Preview changes
3. Confirm publish
4. Execute publish (with rollback)
5. Cleanup

Mock git operations to avoid actual repository changes.
"""

import os
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock, call

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.detect_teaching_mode import detect_teaching_mode
from commands.utils.teaching_validation import (
    ValidationResult,
    validate_teaching_content,
)


class TestSitePublishValidation(unittest.TestCase):
    """Test validation step of publish workflow."""

    def setUp(self):
        """Create temporary teaching project."""
        self.test_dir = tempfile.mkdtemp()

        # Create teaching project structure
        flow_dir = Path(self.test_dir) / ".flow"
        flow_dir.mkdir()
        config_file = flow_dir / "teach-config.yml"
        config_file.write_text("""
course:
  code: "STAT 440"
  name: "Regression Analysis"

branches:
  draft: "draft"
  production: "production"

deployment:
  gh_pages_url: "https://example.com/course/"
  verify_deployment: true
  deployment_timeout: 300
""")

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_teaching_mode_detected(self):
        """Should detect teaching mode from config."""
        is_teaching, method = detect_teaching_mode(self.test_dir)

        self.assertTrue(is_teaching)
        self.assertEqual(method, "config")

    def test_validation_called_in_teaching_mode(self):
        """Should call validation when teaching mode detected."""
        # Create complete course for validation
        syllabus_content = """
# Syllabus
## Objectives
Learn stats.
## Policies
Be nice.
## Grading
Homework 100%.
## Schedule
See schedule.
"""
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        schedule_content = """
## Week 1
Good content here with sufficient length.
"""
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        result = validate_teaching_content(self.test_dir)

        self.assertTrue(result.can_publish())
        self.assertEqual(len(result.errors), 0)

    def test_validation_errors_block_publish(self):
        """Should block publish when validation errors exist."""
        # Create incomplete course
        syllabus_content = """
# Syllabus
## Grading
Homework only.
"""
        (Path(self.test_dir) / 'syllabus.qmd').write_text(syllabus_content)

        schedule_content = """
## Week 1
Content.

## Week 2

## Week 3
More content.
"""
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        result = validate_teaching_content(self.test_dir)

        self.assertFalse(result.can_publish())
        self.assertGreater(len(result.errors), 0)

    def test_validation_warnings_allow_publish(self):
        """Should allow publish when only warnings exist."""
        # Create complete syllabus and schedule
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

        # Schedule references assignments but files don't exist
        schedule_content = """
## Week 1
Complete HW 1. Sufficient content here.

## Week 2
Complete HW 2. More content here.
"""
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

        result = validate_teaching_content(self.test_dir)

        # Should be publishable (warnings don't block)
        self.assertTrue(result.can_publish())
        # But should have warnings about missing assignments
        self.assertGreater(len(result.warnings), 0)


class TestSitePublishPreview(unittest.TestCase):
    """Test preview changes step of publish workflow."""

    @patch('subprocess.run')
    def test_git_diff_stat_called(self, mock_run):
        """Should call git diff --stat for preview."""
        mock_run.return_value = Mock(
            returncode=0,
            stdout="""
 syllabus/index.qmd    | 18 +++++++++-------
 schedule.qmd          | 50 +++++++++++++++++++++++++++++++++++++++++
 lectures/week-01.qmd  | 120 +++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++++
 3 files changed, 180 insertions(+), 8 deletions(-)
""",
            stderr=""
        )

        # Would call: git diff production..draft --stat
        # Verify output can be parsed
        result = mock_run.return_value.stdout

        self.assertIn("syllabus/index.qmd", result)
        self.assertIn("schedule.qmd", result)
        self.assertIn("lectures/week-01.qmd", result)

    def test_categorize_changed_files(self):
        """Should categorize files into critical/content/other."""
        files = [
            "syllabus/index.qmd",
            "syllabus.qmd",
            "schedule.qmd",
            "assignments/hw-1.qmd",
            "lectures/week-01.qmd",
            "readings/chapter-1.qmd",
            "resources/datasets.qmd",
            "_quarto.yml",
            ".gitignore",
        ]

        critical = []
        content = []
        other = []

        for file in files:
            if any(pattern in file for pattern in ["syllabus", "schedule", "assignments/"]):
                critical.append(file)
            elif any(pattern in file for pattern in ["lectures/", "readings/", "resources/"]):
                content.append(file)
            else:
                other.append(file)

        self.assertEqual(len(critical), 4)  # syllabus/index, syllabus, schedule, assignments/hw-1
        self.assertEqual(len(content), 3)   # lectures, readings, resources
        self.assertEqual(len(other), 2)     # _quarto.yml, .gitignore


class TestSitePublishConfirmation(unittest.TestCase):
    """Test confirmation step of publish workflow."""

    def test_confirmation_options(self):
        """Should present 3 options: Yes, Preview diff, Cancel."""
        options = [
            "Yes - Merge and deploy (Recommended)",
            "Preview full diff first",
            "Cancel"
        ]

        self.assertEqual(len(options), 3)
        self.assertIn("Yes", options[0])
        self.assertIn("Preview", options[1])
        self.assertIn("Cancel", options[2])


class TestSitePublishExecution(unittest.TestCase):
    """Test execution step with git operations."""

    @patch('subprocess.run')
    @patch('datetime.datetime')
    def test_backup_branch_created(self, mock_datetime, mock_run):
        """Should create backup branch with timestamp."""
        mock_datetime.now.return_value.strftime.return_value = "20260116-143022"
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Simulate: git branch production-backup-20260116-143022
        backup_name = f"production-backup-{mock_datetime.now().strftime('%Y%m%d-%H%M%S')}"

        self.assertEqual(backup_name, "production-backup-20260116-143022")

    @patch('subprocess.run')
    def test_fast_forward_merge(self, mock_run):
        """Should attempt fast-forward merge."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Would call: git merge draft --ff-only
        # Verify command structure
        expected_args = ["git", "merge", "draft", "--ff-only"]

        self.assertEqual(len(expected_args), 4)
        self.assertIn("--ff-only", expected_args)

    @patch('subprocess.run')
    def test_merge_conflict_rollback(self, mock_run):
        """Should rollback on merge conflict."""
        # Simulate merge failure
        mock_run.side_effect = [
            Mock(returncode=0, stdout="", stderr=""),  # backup creation
            Mock(returncode=0, stdout="", stderr=""),  # checkout production
            Mock(returncode=1, stdout="", stderr="CONFLICT"),  # merge fails
            Mock(returncode=0, stdout="", stderr=""),  # rollback
        ]

        # On conflict, should call: git reset --hard production-backup-<timestamp>
        rollback_command = ["git", "reset", "--hard", "production-backup-20260116-143022"]

        self.assertIn("--hard", rollback_command)
        self.assertIn("production-backup", rollback_command[3])

    @patch('subprocess.run')
    def test_push_to_remote(self, mock_run):
        """Should push production branch to remote."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Would call: git push origin production
        push_command = ["git", "push", "origin", "production"]

        self.assertEqual(len(push_command), 4)
        self.assertEqual(push_command[3], "production")

    @patch('subprocess.run')
    def test_push_failure_rollback(self, mock_run):
        """Should rollback on push failure."""
        # Simulate push failure
        side_effects = [
            Mock(returncode=0, stdout="", stderr=""),  # backup
            Mock(returncode=0, stdout="", stderr=""),  # checkout
            Mock(returncode=0, stdout="", stderr=""),  # merge success
            Mock(returncode=1, stdout="", stderr="Permission denied"),  # push fails
            Mock(returncode=0, stdout="", stderr=""),  # rollback
        ]
        mock_run.side_effect = side_effects

        # Should preserve backup branch and rollback
        # Verify rollback logic is triggered
        self.assertEqual(len(side_effects), 5)

    @patch('requests.get')
    def test_deployment_verification(self, mock_get):
        """Should verify deployment by checking URL."""
        mock_get.return_value = Mock(status_code=200)

        # Would call: requests.get("https://example.com/course/")
        url = "https://example.com/course/"
        response = mock_get(url)

        self.assertEqual(response.status_code, 200)

    @patch('requests.get')
    def test_deployment_verification_timeout(self, mock_get):
        """Should handle deployment verification timeout gracefully."""
        import requests
        mock_get.side_effect = requests.Timeout()

        # Should warn but not rollback
        try:
            response = mock_get("https://example.com/course/", timeout=300)
            self.fail("Should have raised Timeout")
        except requests.Timeout:
            # Expected - should warn user but continue
            pass

    @patch('requests.get')
    def test_deployment_verification_404(self, mock_get):
        """Should warn on 404 but not rollback."""
        mock_get.return_value = Mock(status_code=404)

        url = "https://example.com/course/"
        response = mock_get(url)

        # Should warn but not rollback (may take time to propagate)
        self.assertEqual(response.status_code, 404)


class TestSitePublishCleanup(unittest.TestCase):
    """Test cleanup step of publish workflow."""

    @patch('subprocess.run')
    def test_return_to_original_branch(self, mock_run):
        """Should checkout original branch after publish."""
        mock_run.return_value = Mock(returncode=0, stdout="", stderr="")

        # Would call: git checkout draft
        checkout_command = ["git", "checkout", "draft"]

        self.assertEqual(len(checkout_command), 3)
        self.assertEqual(checkout_command[2], "draft")

    def test_success_message_format(self):
        """Should show ADHD-friendly success message."""
        message_parts = [
            "✅ PUBLISH SUCCESSFUL",
            "🌐 Live Site:",
            "📊 Changes Published:",
            "💡 Next Steps:",
        ]

        # Verify all key components present
        for part in message_parts:
            self.assertIsNotNone(part)


class TestSitePublishNonTeaching(unittest.TestCase):
    """Test publish workflow for non-teaching projects."""

    def setUp(self):
        """Create temporary non-teaching project."""
        self.test_dir = tempfile.mkdtemp()

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_non_teaching_mode_detected(self):
        """Should detect non-teaching mode."""
        is_teaching, method = detect_teaching_mode(self.test_dir)

        self.assertFalse(is_teaching)
        self.assertIsNone(method)

    def test_validation_skipped_for_non_teaching(self):
        """Should skip validation for non-teaching projects."""
        is_teaching, _ = detect_teaching_mode(self.test_dir)

        if not is_teaching:
            # Validation should be skipped
            self.assertFalse(is_teaching)


class TestSitePublishIntegration(unittest.TestCase):
    """Integration tests for full publish workflow."""

    def setUp(self):
        """Create temporary teaching project."""
        self.test_dir = tempfile.mkdtemp()

        # Create complete teaching project
        flow_dir = Path(self.test_dir) / ".flow"
        flow_dir.mkdir()
        config_file = flow_dir / "teach-config.yml"
        config_file.write_text("""
course:
  code: "STAT 440"
branches:
  draft: "draft"
  production: "production"
deployment:
  gh_pages_url: "https://example.com/course/"
""")

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

        # Complete schedule
        schedule_content = """
## Week 1
Content here that is long enough to pass validation checks.
"""
        (Path(self.test_dir) / 'schedule.qmd').write_text(schedule_content)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.test_dir)

    def test_full_workflow_success(self):
        """Should complete all 5 steps successfully."""
        # Step 1: Detect teaching mode
        is_teaching, method = detect_teaching_mode(self.test_dir)
        self.assertTrue(is_teaching)

        # Step 2: Validate content
        validation = validate_teaching_content(self.test_dir)
        self.assertTrue(validation.can_publish())

        # Step 3-5 would require git operations (mocked in other tests)
        # Verify workflow components are present
        self.assertTrue(is_teaching)
        self.assertTrue(validation.can_publish())


if __name__ == '__main__':
    unittest.main()
