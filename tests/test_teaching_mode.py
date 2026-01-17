#!/usr/bin/env python3
"""
Unit tests for teaching mode detection utility.

Tests all three detection strategies with priority ordering:
1. Config file detection
2. Metadata detection
3. Structure detection

Run with: python3 -m pytest tests/test_teaching_mode.py -v
"""

import os
import sys
import tempfile
import shutil
from pathlib import Path

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.detect_teaching_mode import detect_teaching_mode


class TestTeachingModeDetection:
    """Test suite for teaching mode detection"""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_config_detection_priority_1(self, temp_project):
        """Test Priority 1: .flow/teach-config.yml detection"""
        # Create .flow/teach-config.yml
        flow_dir = temp_project / ".flow"
        flow_dir.mkdir()
        config_file = flow_dir / "teach-config.yml"
        config_file.write_text("course: STAT 440\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is True
        assert method == "config"

    def test_metadata_detection_priority_2(self, temp_project):
        """Test Priority 2: _quarto.yml teaching: true detection"""
        # Create _quarto.yml with teaching: true
        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("teaching: true\nproject:\n  type: website\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is True
        assert method == "metadata"

    def test_structure_detection_priority_3_with_dir(self, temp_project):
        """Test Priority 3: Structure detection with syllabus/ directory"""
        # Create syllabus/ directory
        syllabus_dir = temp_project / "syllabus"
        syllabus_dir.mkdir()

        # Create schedule.qmd
        schedule_file = temp_project / "schedule.qmd"
        schedule_file.write_text("# Course Schedule\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is True
        assert method == "structure"

    def test_structure_detection_priority_3_with_file(self, temp_project):
        """Test Priority 3: Structure detection with syllabus.qmd file"""
        # Create syllabus.qmd file
        syllabus_file = temp_project / "syllabus.qmd"
        syllabus_file.write_text("# Course Syllabus\n")

        # Create schedule.qmd
        schedule_file = temp_project / "schedule.qmd"
        schedule_file.write_text("# Course Schedule\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is True
        assert method == "structure"

    def test_priority_order_config_over_metadata(self, temp_project):
        """Test that config detection takes priority over metadata"""
        # Create both config and metadata
        flow_dir = temp_project / ".flow"
        flow_dir.mkdir()
        config_file = flow_dir / "teach-config.yml"
        config_file.write_text("course: STAT 440\n")

        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("teaching: true\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        # Should detect via config (Priority 1), not metadata
        assert is_teaching is True
        assert method == "config"

    def test_priority_order_config_over_structure(self, temp_project):
        """Test that config detection takes priority over structure"""
        # Create config, syllabus, and schedule
        flow_dir = temp_project / ".flow"
        flow_dir.mkdir()
        config_file = flow_dir / "teach-config.yml"
        config_file.write_text("course: STAT 440\n")

        syllabus_dir = temp_project / "syllabus"
        syllabus_dir.mkdir()

        schedule_file = temp_project / "schedule.qmd"
        schedule_file.write_text("# Schedule\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        # Should detect via config (Priority 1)
        assert is_teaching is True
        assert method == "config"

    def test_priority_order_metadata_over_structure(self, temp_project):
        """Test that metadata detection takes priority over structure"""
        # Create metadata, syllabus, and schedule
        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("teaching: true\n")

        syllabus_dir = temp_project / "syllabus"
        syllabus_dir.mkdir()

        schedule_file = temp_project / "schedule.qmd"
        schedule_file.write_text("# Schedule\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        # Should detect via metadata (Priority 2)
        assert is_teaching is True
        assert method == "metadata"

    def test_no_teaching_mode_detected(self, temp_project):
        """Test negative case: no teaching mode indicators"""
        # Create a non-teaching project (e.g., research project)
        readme = temp_project / "README.md"
        readme.write_text("# Research Project\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is False
        assert method is None

    def test_structure_missing_schedule(self, temp_project):
        """Test structure detection fails without schedule.qmd"""
        # Create only syllabus directory, no schedule
        syllabus_dir = temp_project / "syllabus"
        syllabus_dir.mkdir()

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is False
        assert method is None

    def test_structure_missing_syllabus(self, temp_project):
        """Test structure detection fails without syllabus"""
        # Create only schedule.qmd, no syllabus
        schedule_file = temp_project / "schedule.qmd"
        schedule_file.write_text("# Schedule\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is False
        assert method is None

    def test_metadata_teaching_false(self, temp_project):
        """Test that teaching: false in metadata is not detected"""
        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("teaching: false\nproject:\n  type: website\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is False
        assert method is None

    def test_metadata_teaching_string_true(self, temp_project):
        """Test that teaching: 'true' (string) is not detected as true"""
        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("teaching: 'true'\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        # YAML should parse 'true' as string, not boolean
        # Only boolean true should be detected
        assert is_teaching is False
        assert method is None

    def test_metadata_no_teaching_field(self, temp_project):
        """Test _quarto.yml without teaching field"""
        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("project:\n  type: website\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is False
        assert method is None

    def test_default_cwd(self, temp_project, monkeypatch):
        """Test that default cwd='.' uses current directory"""
        # Change to temp project directory
        monkeypatch.chdir(temp_project)

        # Create config file
        flow_dir = temp_project / ".flow"
        flow_dir.mkdir()
        config_file = flow_dir / "teach-config.yml"
        config_file.write_text("course: TEST\n")

        # Call without arguments (should use current directory)
        is_teaching, method = detect_teaching_mode()

        assert is_teaching is True
        assert method == "config"

    def test_invalid_yaml_in_quarto(self, temp_project):
        """Test graceful handling of invalid YAML in _quarto.yml"""
        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("teaching: true\n  invalid: yaml: structure:\n")

        # Should not crash, should return False
        is_teaching, method = detect_teaching_mode(str(temp_project))

        # Result depends on YAML parser behavior
        # Either detects or fails gracefully
        assert isinstance(is_teaching, bool)
        assert method in ["metadata", None]

    def test_empty_quarto_file(self, temp_project):
        """Test empty _quarto.yml file"""
        quarto_file = temp_project / "_quarto.yml"
        quarto_file.write_text("")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is False
        assert method is None

    def test_nonexistent_directory(self):
        """Test with nonexistent directory path"""
        nonexistent = "/tmp/nonexistent-project-xyz123"

        is_teaching, method = detect_teaching_mode(nonexistent)

        # Should handle gracefully
        assert is_teaching is False
        assert method is None


class TestEdgeCases:
    """Test edge cases and error handling"""

    @pytest.fixture
    def temp_project(self):
        """Create a temporary project directory"""
        temp_dir = tempfile.mkdtemp()
        yield Path(temp_dir)
        shutil.rmtree(temp_dir)

    def test_symlink_to_syllabus(self, temp_project):
        """Test that symlinks to syllabus directory work"""
        # Create actual syllabus directory elsewhere
        real_syllabus = temp_project / "real_syllabus"
        real_syllabus.mkdir()

        # Create symlink
        syllabus_link = temp_project / "syllabus"
        syllabus_link.symlink_to(real_syllabus)

        # Create schedule
        schedule_file = temp_project / "schedule.qmd"
        schedule_file.write_text("# Schedule\n")

        is_teaching, method = detect_teaching_mode(str(temp_project))

        assert is_teaching is True
        assert method == "structure"

    def test_relative_path_input(self, temp_project, monkeypatch):
        """Test with relative path input"""
        # Change to parent of temp_project
        parent = temp_project.parent
        monkeypatch.chdir(parent)

        # Create config
        flow_dir = temp_project / ".flow"
        flow_dir.mkdir()
        config_file = flow_dir / "teach-config.yml"
        config_file.write_text("course: TEST\n")

        # Use relative path
        rel_path = temp_project.name
        is_teaching, method = detect_teaching_mode(rel_path)

        assert is_teaching is True
        assert method == "config"


class TestIntegration:
    """Integration tests with realistic project structures"""

    @pytest.fixture
    def realistic_teaching_project(self):
        """Create a realistic teaching project"""
        temp_dir = tempfile.mkdtemp()
        project = Path(temp_dir)

        # Create typical teaching project structure
        (project / ".flow").mkdir()
        (project / ".flow" / "teach-config.yml").write_text("course: STAT 440\n")

        (project / "_quarto.yml").write_text(
            "project:\n"
            "  type: website\n"
            "teaching: true\n"
        )

        (project / "syllabus").mkdir()
        (project / "syllabus" / "index.qmd").write_text("# Syllabus\n")

        (project / "schedule.qmd").write_text("# Schedule\n")

        (project / "lectures").mkdir()
        (project / "assignments").mkdir()

        yield project
        shutil.rmtree(temp_dir)

    def test_realistic_teaching_project(self, realistic_teaching_project):
        """Test detection on realistic teaching project"""
        is_teaching, method = detect_teaching_mode(str(realistic_teaching_project))

        assert is_teaching is True
        # Should detect via config (highest priority)
        assert method == "config"


if __name__ == "__main__":
    # Run tests with pytest
    pytest.main([__file__, "-v", "--tb=short"])
