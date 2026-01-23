#!/usr/bin/env python3
"""
Integration tests for docs_detector.py and help_file_validator.py

Ensures both utilities work correctly before building interactive workflow.
"""

import unittest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.docs_detector import DocsDetector
from utils.help_file_validator import HelpFileValidator, IssueType


class TestDocsUtilities(unittest.TestCase):
    """Test both documentation utilities"""

    def setUp(self):
        """Set up test fixtures"""
        self.project_root = Path(__file__).parent.parent
        self.detector = DocsDetector(str(self.project_root))
        self.validator = HelpFileValidator(str(self.project_root))

    def test_docs_detector_returns_results(self):
        """Test that docs detector returns results for all categories"""
        results = self.detector.detect_all("v2.5.1")

        # Should have 9 categories (using snake_case keys)
        expected_keys = [
            "version_refs",
            "command_counts",
            "broken_links",
            "stale_examples",
            "missing_help",
            "outdated_status",
            "inconsistent_terms",
            "missing_xrefs",
            "outdated_diagrams"
        ]

        self.assertEqual(len(results), 9, "Should detect 9 categories")

        for key in expected_keys:
            self.assertIn(key, results, f"Missing category key: {key}")
            result = results[key]

            # Check result structure
            self.assertTrue(hasattr(result, 'category'))
            self.assertTrue(hasattr(result, 'found'))
            self.assertTrue(hasattr(result, 'count'))
            self.assertTrue(hasattr(result, 'items'))
            self.assertTrue(hasattr(result, 'details'))

    def test_docs_detector_finds_issues(self):
        """Test that detector finds known issues in project"""
        results = self.detector.detect_all("v2.5.1")

        # We know there are issues in the project
        version_refs = results["version_refs"]
        self.assertTrue(version_refs.found, "Should find version reference issues")
        self.assertGreater(version_refs.count, 0, "Should have version refs to update")

    def test_help_validator_returns_results(self):
        """Test that help validator returns grouped results"""
        issues = self.validator.validate_all()

        # Should return dict with IssueType keys
        self.assertIsInstance(issues, dict)

        # Should have all issue types
        for issue_type in IssueType:
            self.assertIn(issue_type, issues)
            self.assertIsInstance(issues[issue_type], list)

    def test_help_validator_finds_missing_help(self):
        """Test that validator finds missing help files"""
        issues = self.validator.validate_all()

        missing_help = issues[IssueType.MISSING_HELP]

        # We know there are 60 missing help files
        self.assertGreater(len(missing_help), 0, "Should find missing help files")

    def test_utilities_agree_on_missing_help(self):
        """Test that both utilities agree on missing help count"""
        detector_results = self.detector.detect_all("v2.5.1")
        validator_issues = self.validator.validate_all()

        # Both should find similar number of missing help files
        detector_count = detector_results["missing_help"].count
        validator_count = len(validator_issues[IssueType.MISSING_HELP])

        # They should match closely (within 10% tolerance for different detection methods)
        diff_percentage = abs(detector_count - validator_count) / max(detector_count, validator_count)
        self.assertLess(diff_percentage, 0.1,
                       f"Utilities disagree on missing help: detector={detector_count}, validator={validator_count}")

    def test_detector_result_items_have_required_fields(self):
        """Test that detector result items have required fields"""
        results = self.detector.detect_all("v2.5.1")

        for category, result in results.items():
            if result.found and result.items:
                first_item = result.items[0]

                # Each item should be a dict with at least 'file' key
                self.assertIsInstance(first_item, dict, f"{category} items should be dicts")
                self.assertIn('file', first_item, f"{category} items should have 'file' key")

    def test_validator_issues_have_required_fields(self):
        """Test that validator issues have required fields"""
        issues = self.validator.validate_all()

        for issue_type, issue_list in issues.items():
            if issue_list:
                first_issue = issue_list[0]

                # Each issue should have required attributes
                self.assertTrue(hasattr(first_issue, 'issue_type'))
                self.assertTrue(hasattr(first_issue, 'file_path'))
                self.assertTrue(hasattr(first_issue, 'severity'))
                self.assertTrue(hasattr(first_issue, 'description'))

                # Test summary method
                summary = first_issue.summary()
                self.assertIsInstance(summary, str)
                self.assertGreater(len(summary), 0)


def run_tests():
    """Run the test suite"""
    loader = unittest.TestLoader()
    suite = loader.loadTestsFromTestCase(TestDocsUtilities)
    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
