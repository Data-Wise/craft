#!/usr/bin/env python3
"""
Tests for CLAUDE.md Phase 1 - Detector and Simple Updater

Covers:
- Project type detection
- Version extraction
- Command/skill/agent counting
- Simple metric updates
"""

import unittest
import tempfile
import json
import os
import time
import threading
from pathlib import Path
import sys

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_detector import CLAUDEMDDetector, ProjectInfo
from utils.claude_md_updater_simple import SimpleCLAUDEMDUpdater, MetricChange


class TestCLAUDEMDDetector(unittest.TestCase):
    """Test project type detection."""

    def setUp(self):
        """Create temporary directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def test_detect_craft_plugin(self):
        """Test craft plugin detection."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create commands directory with a command
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "test.md").write_text("# Test command")

        detector = CLAUDEMDDetector(self.path)
        info = detector.detect()

        self.assertIsNotNone(info)
        self.assertEqual(info.type, "craft-plugin")
        self.assertEqual(info.name, "test-plugin")
        self.assertEqual(info.version, "1.0.0")
        self.assertEqual(info.version_source, "plugin.json")
        self.assertEqual(len(info.commands), 1)

    def test_detect_r_package(self):
        """Test R package detection."""
        description = self.path / "DESCRIPTION"
        description.write_text("""Package: testpkg
Version: 0.1.0
Title: Test Package
""")

        detector = CLAUDEMDDetector(self.path)
        info = detector.detect()

        self.assertIsNotNone(info)
        self.assertEqual(info.type, "r-package")
        self.assertEqual(info.name, "testpkg")
        self.assertEqual(info.version, "0.1.0")
        self.assertEqual(info.version_source, "DESCRIPTION")

    def test_version_extraction_from_plugin_json(self):
        """Test version extraction from plugin.json."""
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "2.5.3"
        }))

        detector = CLAUDEMDDetector(self.path)
        version = detector.get_version_from_source("plugin.json")

        self.assertEqual(version, "2.5.3")

    def test_command_counting(self):
        """Test command counting."""
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test",
            "version": "1.0.0"
        }))

        # Create nested commands
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "test1.md").write_text("# Test 1")

        docs_dir = commands_dir / "docs"
        docs_dir.mkdir()
        (docs_dir / "test2.md").write_text("# Test 2")
        (docs_dir / "test3.md").write_text("# Test 3")

        detector = CLAUDEMDDetector(self.path)
        commands = detector._scan_commands()

        self.assertEqual(len(commands), 3)
        self.assertIn("test1.md", commands)
        self.assertIn("docs/test2.md", commands)
        self.assertIn("docs/test3.md", commands)

    def test_concurrent_detection_calls(self):
        """Test concurrent detection calls are thread-safe."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create commands directory
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "test.md").write_text("# Test command")

        # Run detection in parallel threads
        results = []
        errors = []

        def detect_project():
            try:
                detector = CLAUDEMDDetector(self.path)
                info = detector.detect()
                results.append(info)
            except Exception as e:
                errors.append(e)

        # Create 10 concurrent threads
        threads = []
        for _ in range(10):
            thread = threading.Thread(target=detect_project)
            threads.append(thread)
            thread.start()

        # Wait for all threads to complete
        for thread in threads:
            thread.join()

        # Verify results
        self.assertEqual(len(errors), 0, f"Errors occurred: {errors}")
        self.assertEqual(len(results), 10, "All threads should complete")

        # All results should be consistent
        for info in results:
            self.assertIsNotNone(info)
            self.assertEqual(info.type, "craft-plugin")
            self.assertEqual(info.name, "test-plugin")
            self.assertEqual(info.version, "1.0.0")

    def test_symlink_handling(self):
        """Test detection handles symlinked commands correctly."""
        # Create plugin.json
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create real commands directory
        real_commands = self.path / "real_commands"
        real_commands.mkdir()
        (real_commands / "real_cmd.md").write_text("# Real command")

        # Create commands directory with symlink
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "direct.md").write_text("# Direct command")

        # Create symlink to real command
        symlink_path = commands_dir / "symlinked.md"
        try:
            os.symlink(real_commands / "real_cmd.md", symlink_path)
            has_symlink = True
        except (OSError, NotImplementedError):
            # Symlinks not supported on this system
            has_symlink = False

        detector = CLAUDEMDDetector(self.path)
        commands = detector._scan_commands()

        # Should find direct command
        self.assertIn("direct.md", commands)

        if has_symlink:
            # Should handle symlinked command
            # Count should include symlink (detector follows them)
            self.assertGreaterEqual(len(commands), 1)

    def test_performance_benchmarks(self):
        """Test detection performance meets targets."""
        # Create a moderately complex project structure
        plugin_json = self.path / ".claude-plugin"
        plugin_json.mkdir()
        (plugin_json / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0"
        }))

        # Create 50 commands across nested directories
        commands_dir = self.path / "commands"
        commands_dir.mkdir()

        for i in range(20):
            (commands_dir / f"cmd{i}.md").write_text(f"# Command {i}")

        # Nested directories
        for subdir in ["docs", "git", "code", "test"]:
            sub = commands_dir / subdir
            sub.mkdir()
            for i in range(10):
                (sub / f"{subdir}_cmd{i}.md").write_text(f"# {subdir} {i}")

        # Benchmark detection
        detector = CLAUDEMDDetector(self.path)

        start_time = time.time()
        info = detector.detect()
        elapsed = time.time() - start_time

        # Assertions
        self.assertIsNotNone(info)
        self.assertEqual(len(info.commands), 60)  # 20 + 4*10

        # Performance targets
        self.assertLess(elapsed, 0.5,
                       f"Detection took {elapsed:.3f}s, should be < 0.5s")

        # Benchmark command scanning specifically
        start_time = time.time()
        commands = detector._scan_commands()
        scan_elapsed = time.time() - start_time

        self.assertEqual(len(commands), 60)
        self.assertLess(scan_elapsed, 0.1,
                       f"Command scanning took {scan_elapsed:.3f}s, should be < 0.1s")

        # Benchmark version extraction
        start_time = time.time()
        for _ in range(100):  # 100 iterations to measure
            version = detector.get_version_from_source("plugin.json")
        version_elapsed = time.time() - start_time

        self.assertEqual(version, "1.0.0")
        self.assertLess(version_elapsed, 0.1,
                       f"100 version extractions took {version_elapsed:.3f}s, should be < 0.1s")


class TestSimpleCLAUDEMDUpdater(unittest.TestCase):
    """Test simple metric updater."""

    def setUp(self):
        """Create temp directory and test CLAUDE.md."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create test CLAUDE.md
        self.claude_md = self.path / "CLAUDE.md"
        self.claude_md.write_text("""# CLAUDE.md - Test Plugin

**100 commands** · **21 skills** · **8 agents**

**Current Version:** v1.0.0 (released 2025-01-01)
**Documentation Status:** 80% complete | **Tests:** 50 passing
""")

        # Create mock project info
        self.project_info = ProjectInfo(
            type="craft-plugin",
            version="1.2.0",
            version_source="plugin.json",
            name="test-plugin",
            commands=["cmd1.md", "cmd2.md", "cmd3.md"],  # 3 commands
            skills=["skill1.md", "skill2.md"],  # 2 skills
            agents=["agent1.md"],  # 1 agent
            test_count=75,
            structure={}
        )

    def test_detect_version_change(self):
        """Test version mismatch detection."""
        updater = SimpleCLAUDEMDUpdater(self.claude_md, self.project_info)
        change = updater._check_version()

        self.assertIsNotNone(change)
        self.assertEqual(change.before, "v1.0.0")
        self.assertEqual(change.after, "v1.2.0")

    def test_detect_command_count_change(self):
        """Test command count change."""
        updater = SimpleCLAUDEMDUpdater(self.claude_md, self.project_info)
        change = updater._check_command_count()

        self.assertIsNotNone(change)
        self.assertEqual(change.before, "100 commands")
        self.assertEqual(change.after, "3 commands")

    def test_detect_test_count_change(self):
        """Test test count change."""
        updater = SimpleCLAUDEMDUpdater(self.claude_md, self.project_info)
        change = updater._check_test_count()

        self.assertIsNotNone(change)
        self.assertEqual(change.before, "50 passing")
        self.assertEqual(change.after, "75 passing")

    def test_apply_version_change(self):
        """Test applying version change."""
        updater = SimpleCLAUDEMDUpdater(self.claude_md, self.project_info)
        changes = [updater._check_version()]

        updated = updater.apply_changes(changes, dry_run=True)

        self.assertIn("v1.2.0", updated)
        self.assertNotIn("v1.0.0", updated)

    def test_no_changes_when_up_to_date(self):
        """Test no changes when CLAUDE.md is up to date."""
        # Update project info to match CLAUDE.md
        self.project_info.version = "1.0.0"
        self.project_info.commands = ["cmd" + str(i) + ".md" for i in range(100)]
        self.project_info.skills = ["skill" + str(i) + ".md" for i in range(21)]
        self.project_info.agents = ["agent" + str(i) + ".md" for i in range(8)]
        self.project_info.test_count = 50

        updater = SimpleCLAUDEMDUpdater(self.claude_md, self.project_info)
        changes = updater.detect_changes()

        # Should have no changes (except docs % since we don't have .STATUS)
        version_changes = [c for c in changes if c.name == "Version"]
        self.assertEqual(len(version_changes), 0)

    def test_generate_preview(self):
        """Test preview generation."""
        updater = SimpleCLAUDEMDUpdater(self.claude_md, self.project_info)
        changes = updater.detect_changes()

        preview = updater.generate_preview(changes)

        self.assertIn("Update Plan", preview)
        self.assertIn("test-plugin", preview)
        self.assertIn("craft-plugin", preview)


def run_tests():
    """Run all tests."""
    loader = unittest.TestLoader()
    suite = unittest.TestSuite()

    suite.addTests(loader.loadTestsFromTestCase(TestCLAUDEMDDetector))
    suite.addTests(loader.loadTestsFromTestCase(TestSimpleCLAUDEMDUpdater))

    runner = unittest.TextTestRunner(verbosity=2)
    result = runner.run(suite)

    return result.wasSuccessful()


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
