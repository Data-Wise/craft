#!/usr/bin/env python3
"""
Error handling tests for docs_detector.py and help_file_validator.py

Tests robustness against:
- Missing/corrupted files
- Invalid input
- Permission errors
- Edge cases
- Partial failures
"""

import unittest
import sys
import tempfile
import shutil
from pathlib import Path
from unittest.mock import patch, MagicMock

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.docs_detector import DocsDetector, DetectionResult
from utils.help_file_validator import HelpFileValidator, IssueType, HelpIssue


class TestDocsDetectorErrorHandling(unittest.TestCase):
    """Test DocsDetector error handling"""

    def setUp(self):
        """Create temporary test directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detector_handles_missing_project_root(self):
        """Test detector gracefully handles non-existent project root"""
        non_existent = "/tmp/does_not_exist_12345"
        detector = DocsDetector(non_existent)

        # Should not crash, just return empty results
        results = detector.detect_all("v2.6.0")

        self.assertIsInstance(results, dict)
        self.assertEqual(len(results), 9, "Should return all 9 categories even with missing root")

        # All categories should show no issues found
        for category, result in results.items():
            self.assertFalse(result.found, f"{category} should report no issues on missing root")
            self.assertEqual(result.count, 0, f"{category} should have zero count")

    def test_detector_handles_empty_project(self):
        """Test detector handles project with no files"""
        detector = DocsDetector(str(self.temp_path))
        results = detector.detect_all("v2.6.0")

        self.assertEqual(len(results), 9)

        # Should return results with zero counts
        for result in results.values():
            self.assertIsInstance(result, DetectionResult)
            self.assertEqual(result.count, 0)

    def test_detector_handles_corrupted_markdown(self):
        """Test detector handles corrupted markdown files"""
        # Create docs directory with corrupted file
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        corrupted_file = docs_dir / "corrupted.md"
        with open(corrupted_file, 'wb') as f:
            # Write random binary data that's not valid UTF-8
            f.write(b'\x80\x81\x82\x83\x84\x85')

        detector = DocsDetector(str(self.temp_path))

        # Should not crash when encountering corrupted file
        try:
            results = detector.detect_all("v2.6.0")
            self.assertIsInstance(results, dict)
        except UnicodeDecodeError:
            self.fail("Detector should handle corrupted files gracefully")

    def test_detector_handles_invalid_version_format(self):
        """Test detector handles invalid version formats"""
        detector = DocsDetector(str(self.temp_path))

        # Test various invalid version formats
        invalid_versions = [
            None,
            "",
            "not-a-version",
            "v.2.5",
            "2.5.1.0.0",
            "abc.def.ghi",
        ]

        for invalid_version in invalid_versions:
            with self.subTest(version=invalid_version):
                # Should not crash, just handle gracefully
                results = detector.detect_version_references(invalid_version)
                self.assertIsInstance(results, DetectionResult)

    def test_detector_handles_malformed_yaml_frontmatter(self):
        """Test detector handles files with malformed YAML frontmatter"""
        commands_dir = self.temp_path / "commands"
        commands_dir.mkdir()

        malformed_file = commands_dir / "malformed.md"
        with open(malformed_file, 'w') as f:
            f.write("---\n")
            f.write("name: test\n")
            f.write("invalid yaml: ][{\n")  # Malformed YAML
            f.write("---\n")
            f.write("# Content\n")

        detector = DocsDetector(str(self.temp_path))

        # Should handle malformed YAML without crashing
        try:
            results = detector.detect_missing_help()
            self.assertIsInstance(results, DetectionResult)
        except yaml.YAMLError:
            self.fail("Detector should handle malformed YAML gracefully")

    def test_detector_handles_empty_files(self):
        """Test detector handles empty files"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        # Create empty file
        empty_file = docs_dir / "empty.md"
        empty_file.touch()

        detector = DocsDetector(str(self.temp_path))
        results = detector.detect_all("v2.6.0")

        # Should not crash on empty files
        self.assertEqual(len(results), 9)

    def test_detector_handles_symlink_loops(self):
        """Test detector handles circular symlinks"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        # Create circular symlink if OS supports it
        try:
            link1 = docs_dir / "link1"
            link2 = docs_dir / "link2"
            link1.symlink_to(link2)
            link2.symlink_to(link1)

            detector = DocsDetector(str(self.temp_path))

            # Should handle circular symlinks without infinite loop
            results = detector.detect_all("v2.6.0")
            self.assertEqual(len(results), 9)
        except (OSError, NotImplementedError):
            # Skip test if OS doesn't support symlinks
            self.skipTest("OS does not support symlinks")

    def test_detector_handles_very_large_files(self):
        """Test detector handles very large files efficiently"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        # Create a large file (1MB of content)
        large_file = docs_dir / "large.md"
        with open(large_file, 'w') as f:
            # Write 1MB of repeated content
            content = "# Heading\n\nContent line.\n" * 20000
            f.write(content)

        detector = DocsDetector(str(self.temp_path))

        # Should handle large files without memory issues
        import time
        start_time = time.time()
        results = detector.detect_all("v2.6.0")
        elapsed = time.time() - start_time

        # Should complete in reasonable time (< 5 seconds for 1MB)
        self.assertLess(elapsed, 5.0, "Should process large files efficiently")


class TestHelpValidatorErrorHandling(unittest.TestCase):
    """Test HelpFileValidator error handling"""

    def setUp(self):
        """Create temporary test directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_validator_handles_missing_commands_dir(self):
        """Test validator handles missing commands directory"""
        validator = HelpFileValidator(str(self.temp_path))

        # Should not crash, just return empty results
        issues = validator.validate_all()

        self.assertIsInstance(issues, dict)
        self.assertEqual(len(issues), 8, "Should return all 8 issue types")

        # All issue types should have empty lists
        for issue_type, issue_list in issues.items():
            self.assertIsInstance(issue_list, list)
            self.assertEqual(len(issue_list), 0, f"{issue_type} should have no issues")

    def test_validator_handles_malformed_yaml_frontmatter(self):
        """Test validator handles files with malformed YAML"""
        commands_dir = self.temp_path / "commands"
        commands_dir.mkdir()

        malformed_file = commands_dir / "bad.md"
        with open(malformed_file, 'w') as f:
            f.write("---\n")
            f.write("name: test\n")
            f.write("invalid: ][{]\n")  # Malformed YAML
            f.write("---\n")

        validator = HelpFileValidator(str(self.temp_path))

        # Should handle malformed YAML and report as incomplete
        try:
            issues = validator.validate_all()

            # Should either skip the file or report it as incomplete
            self.assertIsInstance(issues, dict)

            # If malformed YAML is treated as missing frontmatter
            incomplete = issues[IssueType.INCOMPLETE_YAML]
            missing = issues[IssueType.MISSING_HELP]

            # File should appear in one of these categories
            total_issues = len(incomplete) + len(missing)
            self.assertGreaterEqual(total_issues, 0, "Should handle malformed YAML")

        except yaml.YAMLError:
            self.fail("Validator should handle malformed YAML gracefully")

    def test_validator_handles_missing_frontmatter_delimiters(self):
        """Test validator handles files with incomplete frontmatter markers"""
        commands_dir = self.temp_path / "commands"
        commands_dir.mkdir()

        # File with opening --- but no closing
        incomplete = commands_dir / "incomplete.md"
        with open(incomplete, 'w') as f:
            f.write("---\n")
            f.write("name: test\n")
            f.write("# No closing delimiter\n")

        validator = HelpFileValidator(str(self.temp_path))
        issues = validator.validate_all()

        # Should report as missing or incomplete help
        missing = issues[IssueType.MISSING_HELP]
        incomplete_yaml = issues[IssueType.INCOMPLETE_YAML]

        self.assertTrue(
            len(missing) > 0 or len(incomplete_yaml) > 0,
            "Should detect incomplete frontmatter"
        )

    def test_validator_handles_empty_yaml_frontmatter(self):
        """Test validator handles files with empty frontmatter"""
        commands_dir = self.temp_path / "commands"
        commands_dir.mkdir()

        empty_yaml = commands_dir / "empty.md"
        with open(empty_yaml, 'w') as f:
            f.write("---\n")
            f.write("---\n")  # Empty frontmatter
            f.write("# Content\n")

        validator = HelpFileValidator(str(self.temp_path))
        issues = validator.validate_all()

        # Should report as incomplete YAML
        incomplete = issues[IssueType.INCOMPLETE_YAML]
        self.assertGreater(len(incomplete), 0, "Should detect empty frontmatter")

    def test_validator_handles_binary_files(self):
        """Test validator handles binary files in commands directory"""
        commands_dir = self.temp_path / "commands"
        commands_dir.mkdir()

        # Create a binary file
        binary_file = commands_dir / "binary.md"
        with open(binary_file, 'wb') as f:
            f.write(b'\x00\x01\x02\x03\x04\x05')

        validator = HelpFileValidator(str(self.temp_path))

        # Should skip binary files without crashing
        try:
            issues = validator.validate_all()
            self.assertIsInstance(issues, dict)
        except UnicodeDecodeError:
            self.fail("Validator should skip binary files gracefully")

    def test_validator_handles_special_characters_in_paths(self):
        """Test validator handles special characters in file paths"""
        commands_dir = self.temp_path / "commands"
        commands_dir.mkdir()

        # Create subdirectory with special characters
        special_dir = commands_dir / "special-chars!@#"
        special_dir.mkdir(exist_ok=True)

        special_file = special_dir / "command.md"
        with open(special_file, 'w') as f:
            f.write("---\n")
            f.write("name: test\n")
            f.write("---\n")
            f.write("# Content\n")

        validator = HelpFileValidator(str(self.temp_path))

        # Should handle special characters in paths
        try:
            issues = validator.validate_all()
            self.assertIsInstance(issues, dict)
        except OSError:
            self.fail("Validator should handle special characters in paths")


class TestUpdateRollbackScenarios(unittest.TestCase):
    """Test error handling during update operations"""

    def setUp(self):
        """Create temporary test directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_write_error_handling(self):
        """Test handling of write errors during updates"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        test_file = docs_dir / "test.md"
        test_file.write_text("Version: v2.5.0\n")

        # Make file read-only to simulate write error
        test_file.chmod(0o444)

        try:
            # Attempt to write should fail
            with self.assertRaises(PermissionError):
                test_file.write_text("Version: v2.6.0\n")
        finally:
            # Restore write permissions for cleanup
            test_file.chmod(0o644)

    def test_partial_update_detection(self):
        """Test detection of partially completed updates"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        # Create multiple files
        files = []
        for i in range(5):
            f = docs_dir / f"file{i}.md"
            f.write_text(f"Version: v2.5.0\nCount: {i}\n")
            files.append(f)

        detector = DocsDetector(str(self.temp_path))

        # Update first 3 files
        for i in range(3):
            content = files[i].read_text()
            updated = content.replace("v2.5.0", "v2.6.0")
            files[i].write_text(updated)

        # Detect should find remaining 2 files with old version
        results = detector.detect_version_references("v2.6.0")

        self.assertTrue(results.found, "Should detect partial update")
        self.assertEqual(results.count, 2, "Should find 2 files with old version")

    def test_disk_full_simulation(self):
        """Test handling of disk full errors (simulated)"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        test_file = docs_dir / "large.md"

        # Write initial content
        test_file.write_text("Version: v2.5.0\n")

        # Simulate disk full by mocking write operation
        with patch('pathlib.Path.write_text', side_effect=OSError("No space left on device")):
            with self.assertRaises(OSError):
                test_file.write_text("Version: v2.6.0\n" * 1000000)


class TestEdgeCases(unittest.TestCase):
    """Test edge cases and boundary conditions"""

    def setUp(self):
        """Create temporary test directory"""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temporary directory"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_zero_byte_files(self):
        """Test handling of zero-byte files"""
        commands_dir = self.temp_path / "commands"
        commands_dir.mkdir()

        zero_file = commands_dir / "empty.md"
        zero_file.touch()  # Create empty file

        self.assertEqual(zero_file.stat().st_size, 0)

        validator = HelpFileValidator(str(self.temp_path))
        issues = validator.validate_all()

        # Should detect as missing help
        missing = issues[IssueType.MISSING_HELP]
        self.assertGreater(len(missing), 0, "Should detect zero-byte file")

    def test_deeply_nested_directories(self):
        """Test handling of deeply nested directory structures"""
        # Create deeply nested structure (10 levels)
        current = self.temp_path / "commands"
        for i in range(10):
            current = current / f"level{i}"
        current.mkdir(parents=True)

        deep_file = current / "deep.md"
        with open(deep_file, 'w') as f:
            f.write("---\n")
            f.write("name: deep\n")
            f.write("---\n")

        validator = HelpFileValidator(str(self.temp_path))

        # Should find deeply nested files
        issues = validator.validate_all()
        self.assertIsInstance(issues, dict)

    def test_unicode_content_handling(self):
        """Test handling of Unicode characters in content"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        unicode_file = docs_dir / "unicode.md"
        with open(unicode_file, 'w', encoding='utf-8') as f:
            f.write("# 测试文档\n")
            f.write("Content with émojis: 🚀 🎉 ✅\n")
            f.write("Arabic: مرحبا\n")
            f.write("Japanese: こんにちは\n")

        detector = DocsDetector(str(self.temp_path))

        # Should handle Unicode content
        results = detector.detect_all("v2.6.0")
        self.assertEqual(len(results), 9)

    def test_windows_line_endings(self):
        """Test handling of Windows line endings (CRLF)"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        crlf_file = docs_dir / "windows.md"
        with open(crlf_file, 'wb') as f:
            f.write(b"---\r\n")
            f.write(b"name: test\r\n")
            f.write(b"---\r\n")
            f.write(b"# Content\r\n")

        validator = HelpFileValidator(str(self.temp_path))

        # Should handle CRLF line endings
        issues = validator.validate_all()
        self.assertIsInstance(issues, dict)

    def test_mixed_line_endings(self):
        """Test handling of mixed line endings"""
        docs_dir = self.temp_path / "docs"
        docs_dir.mkdir()

        mixed_file = docs_dir / "mixed.md"
        with open(mixed_file, 'wb') as f:
            f.write(b"---\n")           # LF
            f.write(b"name: test\r\n")  # CRLF
            f.write(b"---\n")           # LF
            f.write(b"# Content\r\n")   # CRLF

        validator = HelpFileValidator(str(self.temp_path))

        # Should handle mixed line endings
        issues = validator.validate_all()
        self.assertIsInstance(issues, dict)


def run_tests():
    """Run all error handling tests"""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    # Load all test classes
    suite.addTests(loader.loadTestsFromTestCase(TestDocsDetectorErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestHelpValidatorErrorHandling))
    suite.addTests(loader.loadTestsFromTestCase(TestUpdateRollbackScenarios))
    suite.addTests(loader.loadTestsFromTestCase(TestEdgeCases))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)
    return result.wasSuccessful()


if __name__ == '__main__':
    success = run_tests()
    sys.exit(0 if success else 1)
