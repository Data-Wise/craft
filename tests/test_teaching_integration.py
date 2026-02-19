#!/usr/bin/env python3
"""
Teaching Workflow Integration Tests
====================================
Comprehensive end-to-end tests for the teaching workflow implementation.

Tests cover:
- End-to-end workflow scenarios
- Error scenarios and edge cases
- Cross-component integration
- Performance benchmarks
- Validation completeness

Run with: python tests/test_teaching_integration.py
"""

import json
import os
import shutil
import sys
import tempfile
import time
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Optional, Dict, Any

import pytest

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.utils.teach_config import load_teach_config, validate_config
from commands.utils.teaching_validation import validate_teaching_content
from commands.utils.semester_progress import calculate_current_week as _calculate_current_week
from utils.detect_teaching_mode import detect_teaching_mode

pytestmark = [pytest.mark.integration, pytest.mark.teaching]


# ─── Test Fixtures ────────────────────────────────────────────────────────────

def get_fixture_path(name: str) -> Path:
    """Get path to a test fixture."""
    return Path(__file__).parent / "fixtures" / "teaching" / name


def calculate_semester_progress(cwd: str) -> Optional[Dict[str, any]]:
    """
    Wrapper for calculate_current_week that loads config first.

    Args:
        cwd: Path to teaching project

    Returns:
        Progress dictionary or None if config not found
    """
    try:
        config = load_teach_config(cwd)
        if not config:
            return None
        return _calculate_current_week(config)
    except Exception:
        return None


# ─── End-to-End Workflow Tests ───────────────────────────────────────────────

def test_e2e_minimal_course():
    """Test complete workflow with minimal course configuration."""
    fixture = get_fixture_path("minimal")

    # Step 1: Detection
    is_teaching, method = detect_teaching_mode(str(fixture))
    assert is_teaching, "Failed to detect minimal teaching project"

    # Step 2: Load config
    config = load_teach_config(str(fixture))
    assert config, "Failed to load config"
    assert config['course']['number'] == "TEST 100", f"Wrong course code: {config['course']['number']}"

    # Step 3: Validate
    errors = validate_config(config)
    assert not errors, f"Validation errors: {errors}"

    # Step 4: Calculate progress
    progress = calculate_semester_progress(str(fixture))
    assert progress, "Failed to calculate progress"


def test_e2e_full_course():
    """Test complete workflow with full course configuration."""
    fixture = get_fixture_path("stat-545")

    # Step 1: Detection
    is_teaching, method = detect_teaching_mode(str(fixture))
    assert is_teaching, "Failed to detect full teaching project"

    # Step 2: Load config
    config = load_teach_config(str(fixture))
    assert config, "Failed to load config"

    # Check optional sections
    assert 'teaching_assistants' in config and len(config['teaching_assistants']) == 2, \
        f"Expected 2 TAs, got {len(config.get('teaching_assistants', []))}"

    # Step 3: Validate
    errors = validate_config(config)
    assert not errors, f"Validation errors: {errors}"

    # Step 4: Check break handling
    breaks = config['dates'].get('breaks', [])
    assert len(breaks) == 2, f"Expected 2 breaks, got {len(breaks)}"


def test_e2e_summer_session():
    """Test workflow with summer session (compressed, no breaks)."""
    fixture = get_fixture_path("summer")

    # Detection
    is_teaching, method = detect_teaching_mode(str(fixture))
    assert is_teaching, "Failed to detect summer teaching project"

    # Load config
    config = load_teach_config(str(fixture))
    assert config, "Failed to load config"

    # Verify no breaks
    breaks = config['dates'].get('breaks', [])
    assert not breaks, "Summer session should have no breaks"

    # Validate
    errors = validate_config(config)
    assert not errors, f"Validation errors: {errors}"


# ─── Error Scenario Tests ─────────────────────────────────────────────────────

def test_error_missing_config():
    """Test handling of missing teach-config.yml."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create teaching project without config
        (tmp_path / "syllabus.qmd").write_text("# Syllabus")
        (tmp_path / "schedule.qmd").write_text("# Schedule")

        # Should detect as teaching
        is_teaching, method = detect_teaching_mode(str(tmp_path))
        assert is_teaching, "Should detect teaching project even without config"

        # Config load should return None
        config = load_teach_config(str(tmp_path))
        assert config is None, "Should return None for missing config"


def test_error_invalid_yaml():
    """Test handling of invalid YAML syntax."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create config with truly invalid YAML syntax
        config_content = """---
course:
  number: "TEST 100"
  title: "Test Course
  semester: Spring
  year: 2026
  invalid_indent:
 broken: true
"""
        (tmp_path / "teach-config.yml").write_text(config_content)

        # Should fail to load due to malformed YAML
        config = load_teach_config(str(tmp_path))
        assert config is None, "Should return None for invalid YAML"


def test_error_missing_required_fields():
    """Test validation of missing required fields."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create config missing required fields
        # Has 'course' but missing 'number', 'semester', 'year'
        # Has 'dates' but missing 'end'
        config_content = """---
course:
  title: "Incomplete Course"
  # Missing number, semester, year

dates:
  start: "2026-01-01"
  # Missing end
"""
        (tmp_path / "teach-config.yml").write_text(config_content)

        try:
            config = load_teach_config(str(tmp_path))
        except ValueError:
            # load_teach_config raises ValueError on validation failure
            return  # Test passes

        if not config:
            # OK if it fails to load
            return  # Test passes

        # If it loads, validation should fail
        errors = validate_config(config)
        assert errors, "Should report errors for missing required fields"


# ─── Edge Case Tests ──────────────────────────────────────────────────────────

def test_edge_before_semester():
    """Test progress calculation before semester starts."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create future course
        future_start = (datetime.now() + timedelta(days=30)).strftime("%Y-%m-%d")
        future_end = (datetime.now() + timedelta(days=150)).strftime("%Y-%m-%d")

        config_content = f"""---
course:
  number: "TEST 100"
  title: "Future Course"
  semester: "Spring"
  year: 2027

dates:
  start: "{future_start}"
  end: "{future_end}"
"""
        (tmp_path / "teach-config.yml").write_text(config_content)

        progress = calculate_semester_progress(str(tmp_path))
        assert progress, "Failed to calculate progress for future course"

        # Week should be 0 or negative, percentage 0
        assert progress.get('current_week', 1) <= 0, \
            f"Current week should be <=0, got {progress.get('current_week')}"


def test_edge_after_semester():
    """Test progress calculation after semester ends."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmp_path = Path(tmpdir)

        # Create past course
        past_start = (datetime.now() - timedelta(days=150)).strftime("%Y-%m-%d")
        past_end = (datetime.now() - timedelta(days=30)).strftime("%Y-%m-%d")

        config_content = f"""---
course:
  number: "TEST 100"
  title: "Past Course"
  semester: "Fall"
  year: 2025

dates:
  start: "{past_start}"
  end: "{past_end}"
"""
        (tmp_path / "teach-config.yml").write_text(config_content)

        progress = calculate_semester_progress(str(tmp_path))
        assert progress, "Failed to calculate progress for past course"

        # Should indicate semester is over via percent_complete == 100
        percent = progress.get('percent_complete', 0)
        current_week = progress.get('current_week', 0)
        total_weeks = progress.get('total_weeks', 0)
        assert percent >= 100.0 and current_week == total_weeks, \
            f"Should be 100% complete, got {percent}% (week {current_week}/{total_weeks})"


# ─── Performance Benchmarks ───────────────────────────────────────────────────

def test_benchmark_detection():
    """Benchmark: Teaching mode detection should be < 100ms."""
    fixture = get_fixture_path("stat-545")

    start = time.time()
    is_teaching, method = detect_teaching_mode(str(fixture))
    duration = (time.time() - start) * 1000

    assert is_teaching, "Failed to detect teaching project"

    target_ms = 100
    assert duration < target_ms, f"{duration:.2f}ms (target: <{target_ms}ms)"


def test_benchmark_config_parsing():
    """Benchmark: Config parsing should be < 200ms."""
    fixture = get_fixture_path("stat-545")

    start = time.time()
    config = load_teach_config(str(fixture))
    duration = (time.time() - start) * 1000

    assert config, "Failed to load config"

    target_ms = 200
    assert duration < target_ms, f"{duration:.2f}ms (target: <{target_ms}ms)"


def test_benchmark_validation():
    """Benchmark: Full validation should be < 5s."""
    fixture = get_fixture_path("stat-545")

    start = time.time()
    results = validate_teaching_content(str(fixture))
    duration = (time.time() - start) * 1000

    assert results, "Validation failed to return results"

    target_ms = 5000
    assert duration < target_ms, f"{duration:.2f}ms (target: <{target_ms}ms)"


def test_benchmark_progress():
    """Benchmark: Progress calculation should be < 100ms."""
    fixture = get_fixture_path("stat-545")

    start = time.time()
    progress = calculate_semester_progress(str(fixture))
    duration = (time.time() - start) * 1000

    assert progress, "Failed to calculate progress"

    target_ms = 100
    assert duration < target_ms, f"{duration:.2f}ms (target: <{target_ms}ms)"
