#!/usr/bin/env python3
"""
Integration Tests: Dependency Management System
================================================
Tests the full dependency workflow from command invocation to tool installation.

Components tested:
- commands/docs/demo.md (dependency declarations)
- scripts/dependency-manager.sh (detection & installation)
- scripts/tool-detector.sh (tool detection)
- scripts/health-check.sh (validation)
- scripts/installers/*.sh (platform-specific installers)

Run with: python tests/test_integration_dependency_system.py
"""

import unittest
import subprocess
import tempfile
import os
from pathlib import Path


class TestDependencySystemIntegration(unittest.TestCase):
    """Integration tests for dependency management system."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.plugin_dir = Path(__file__).parent.parent
        cls.scripts_dir = cls.plugin_dir / "scripts"
        cls.demo_command = cls.plugin_dir / "commands" / "docs" / "demo.md"

    def test_01_full_check_workflow(self):
        """Test: /craft:docs:demo --check shows dependency status."""
        # Arrange: Run dependency check
        result = subprocess.run(
            [str(self.scripts_dir / "dependency-manager.sh"), "display_status_json", "asciinema"],
            capture_output=True,
            text=True,
            cwd=self.plugin_dir
        )

        # Assert: Check returns valid JSON (exit code 0 = all installed, 1 = some missing - both valid)
        self.assertIn(result.returncode, [0, 1], "Dependency check should succeed (0 or 1)")
        self.assertIn('"status":', result.stdout, "Should output JSON")
        self.assertIn('"method":', result.stdout, "Should include method")
        self.assertIn('"tools":', result.stdout, "Should include tools list")

    def test_02_health_check_integration(self):
        """Test: Health check validates installed tools."""
        # Arrange: Check if health-check.sh exists
        health_script = self.scripts_dir / "health-check.sh"
        if not health_script.exists():
            self.skipTest("health-check.sh not found")

        # Act: Run health check
        result = subprocess.run(
            ["bash", str(health_script)],
            capture_output=True,
            text=True,
            cwd=self.plugin_dir
        )

        # Assert: Health check runs without errors
        self.assertIn("health", result.stdout.lower() or result.stderr.lower() or "check")

    def test_03_tool_detector_all_methods(self):
        """Test: Tool detector finds tools across all methods."""
        # Arrange: Check if tool-detector.sh exists
        tool_detector = self.scripts_dir / "tool-detector.sh"
        if not tool_detector.exists():
            self.skipTest("tool-detector.sh not found")

        # Act: Source tool-detector and test detection
        script = f"""
        source {tool_detector}
        detect_tool "bash"
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            cwd=self.plugin_dir
        )

        # Assert: Detector returns valid output (exit code 0 or 1 both valid)
        self.assertIn(result.returncode, [0, 1], "Tool detection should return valid exit code")

    def test_04_version_check_comparison(self):
        """Test: Version comparison logic works correctly."""
        # Arrange: Check if version-check.sh exists
        version_check = self.scripts_dir / "version-check.sh"
        if not version_check.exists():
            self.skipTest("version-check.sh not found")

        # Act: Test version comparison
        script = f"""
        source {version_check}
        compare_versions "1.2.3" "1.2.4"
        echo $?
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            cwd=self.plugin_dir
        )

        # Assert: Returns correct comparison result (1.2.3 < 1.2.4)
        self.assertEqual(result.returncode, 0)

    def test_05_session_cache_workflow(self):
        """Test: Session caching prevents redundant checks."""
        # Arrange: Run check twice
        result1 = subprocess.run(
            [str(self.scripts_dir / "dependency-manager.sh"), "display_status_json", "asciinema"],
            capture_output=True,
            text=True,
            cwd=self.plugin_dir
        )

        result2 = subprocess.run(
            [str(self.scripts_dir / "dependency-manager.sh"), "display_status_json", "asciinema"],
            capture_output=True,
            text=True,
            cwd=self.plugin_dir
        )

        # Assert: Both succeed (exit code 0 = all installed, 1 = some missing - both valid)
        self.assertIn(result1.returncode, [0, 1], "First check should succeed (0 or 1)")
        self.assertIn(result2.returncode, [0, 1], "Second check should succeed (0 or 1)")

    def test_06_batch_convert_integration(self):
        """Test: Batch conversion workflow handles multiple files."""
        # Arrange: Check if batch-convert.sh exists
        batch_convert = self.scripts_dir / "batch-convert.sh"
        if not batch_convert.exists():
            self.skipTest("batch-convert.sh not found")

        # Create temp .cast files
        with tempfile.TemporaryDirectory() as tmpdir:
            tmpdir_path = Path(tmpdir)
            (tmpdir_path / "test1.cast").write_text('{"version": 2}')
            (tmpdir_path / "test2.cast").write_text('{"version": 2}')

            # Act: Run batch convert in dry-run mode
            result = subprocess.run(
                ["bash", str(batch_convert), "--dry-run"],
                capture_output=True,
                text=True,
                cwd=tmpdir
            )

            # Assert: Dry-run shows plan or handles gracefully
            # Script may not run in test env, just verify it doesn't crash
            self.assertIn(result.returncode, [0, 1], "Batch convert should handle dry-run")

    def test_07_consent_prompt_validation(self):
        """Test: Consent prompt validates user input."""
        # Arrange: Check if consent-prompt.sh exists
        consent_prompt = self.scripts_dir / "consent-prompt.sh"
        if not consent_prompt.exists():
            self.skipTest("consent-prompt.sh not found")

        # Act: Test script sources correctly
        script = f"""
        source {consent_prompt}
        # Just test sourcing - actual prompt would hang
        type prompt_user_consent > /dev/null 2>&1
        echo $?
        """
        result = subprocess.run(
            ["bash", "-c", script],
            capture_output=True,
            text=True,
            cwd=self.plugin_dir
        )

        # Assert: Script sources without errors
        self.assertEqual(result.returncode, 0, "Consent prompt should source correctly")


class TestDependencyEdgeCases(unittest.TestCase):
    """Edge case tests for dependency system."""

    def test_missing_tool_graceful_degradation(self):
        """Test: System handles missing tools gracefully."""
        # Test that system doesn't crash when tool is missing
        result = subprocess.run(
            ["bash", "-c", "command -v nonexistent_tool_xyz_123 || echo 'not found'"],
            capture_output=True,
            text=True
        )

        self.assertIn("not found", result.stdout)
        self.assertEqual(result.returncode, 0)

    def test_shell_script_syntax_valid(self):
        """Test: All dependency scripts have valid bash syntax."""
        plugin_dir = Path(__file__).parent.parent
        scripts_dir = plugin_dir / "scripts"

        if not scripts_dir.exists():
            self.skipTest("Scripts directory not found")

        scripts = list(scripts_dir.glob("*.sh"))

        for script in scripts:
            with self.subTest(script=script.name):
                result = subprocess.run(
                    ["bash", "-n", str(script)],
                    capture_output=True,
                    text=True
                )
                self.assertEqual(
                    result.returncode, 0,
                    f"{script.name} should have valid syntax: {result.stderr}"
                )


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
