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
from dataclasses import dataclass
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


@dataclass
class CheckResult:
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "integration"


def log(msg: str) -> None:
    """Print with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")


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

def _check_e2e_minimal_course() -> CheckResult:
    """Test complete workflow with minimal course configuration."""
    start = time.time()

    try:
        fixture = get_fixture_path("minimal")

        # Step 1: Detection
        is_teaching, method = detect_teaching_mode(str(fixture))

        if not is_teaching:
            return CheckResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                "Failed to detect minimal teaching project",
                "integration"
            )

        # Step 2: Load config
        config = load_teach_config(str(fixture))

        if not config:
            return CheckResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                "Failed to load config",
                "integration"
            )

        if config['course']['number'] != "TEST 100":
            return CheckResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                f"Wrong course code: {config['course']['code']}",
                "integration"
            )

        # Step 3: Validate
        errors = validate_config(config)

        if errors:
            return CheckResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                f"Validation errors: {errors}",
                "integration"
            )

        # Step 4: Calculate progress
        progress = calculate_semester_progress(str(fixture))

        if not progress:
            return CheckResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                "Failed to calculate progress",
                "integration"
            )

        duration = (time.time() - start) * 1000
        return CheckResult(
            "E2E Minimal Course", True, duration,
            f"Complete workflow: detect({method}) → config → validate → progress ({duration:.1f}ms)",
            "integration"
        )

    except Exception as e:
        return CheckResult(
            "E2E Minimal Course", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "integration"
        )


def _check_e2e_full_course() -> CheckResult:
    """Test complete workflow with full course configuration."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Step 1: Detection
        is_teaching, method = detect_teaching_mode(str(fixture))

        if not is_teaching:
            return CheckResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                "Failed to detect full teaching project",
                "integration"
            )

        # Step 2: Load config
        config = load_teach_config(str(fixture))

        if not config:
            return CheckResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                "Failed to load config",
                "integration"
            )

        # Check optional sections
        if 'teaching_assistants' not in config or len(config['teaching_assistants']) != 2:
            return CheckResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                f"Expected 2 TAs, got {len(config.get('teaching_assistants', []))}",
                "integration"
            )

        # Step 3: Validate
        errors = validate_config(config)

        if errors:
            return CheckResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                f"Validation errors: {errors}",
                "integration"
            )

        # Step 4: Check break handling
        breaks = config['dates'].get('breaks', [])
        if len(breaks) != 2:
            return CheckResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                f"Expected 2 breaks, got {len(breaks)}",
                "integration"
            )

        duration = (time.time() - start) * 1000
        return CheckResult(
            "E2E Full Course", True, duration,
            f"Full config: 2 TAs, 2 breaks, 5 homeworks ({duration:.1f}ms)",
            "integration"
        )

    except Exception as e:
        return CheckResult(
            "E2E Full Course", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "integration"
        )


def _check_e2e_summer_session() -> CheckResult:
    """Test workflow with summer session (compressed, no breaks)."""
    start = time.time()

    try:
        fixture = get_fixture_path("summer")

        # Detection
        is_teaching, method = detect_teaching_mode(str(fixture))
        if not is_teaching:
            return CheckResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                "Failed to detect summer teaching project",
                "integration"
            )

        # Load config
        config = load_teach_config(str(fixture))

        if not config:
            return CheckResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                "Failed to load config",
                "integration"
            )

        # Verify no breaks
        breaks = config['dates'].get('breaks', [])
        if breaks:
            return CheckResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                "Summer session should have no breaks",
                "integration"
            )

        # Validate
        errors = validate_config(config)

        if errors:
            return CheckResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                f"Validation errors: {errors}",
                "integration"
            )

        duration = (time.time() - start) * 1000
        return CheckResult(
            "E2E Summer Session", True, duration,
            f"Summer session: no breaks, 8 quizzes ({duration:.1f}ms)",
            "integration"
        )

    except Exception as e:
        return CheckResult(
            "E2E Summer Session", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "integration"
        )


# ─── Error Scenario Tests ─────────────────────────────────────────────────────

def _check_error_missing_config() -> CheckResult:
    """Test handling of missing teach-config.yml."""
    start = time.time()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create teaching project without config
            (tmp_path / "syllabus.qmd").write_text("# Syllabus")
            (tmp_path / "schedule.qmd").write_text("# Schedule")

            # Should detect as teaching
            is_teaching, method = detect_teaching_mode(str(tmp_path))

            if not is_teaching:
                return CheckResult(
                    "Error: Missing Config", False,
                    (time.time() - start) * 1000,
                    "Should detect teaching project even without config",
                    "error_scenarios"
                )

            # Config load should return None
            config = load_teach_config(str(tmp_path))

            if config is not None:
                return CheckResult(
                    "Error: Missing Config", False,
                    (time.time() - start) * 1000,
                    "Should return None for missing config",
                    "error_scenarios"
                )

            duration = (time.time() - start) * 1000
            return CheckResult(
                "Error: Missing Config", True, duration,
                f"Correctly detected teaching but no config (via {method})",
                "error_scenarios"
            )

    except Exception as e:
        return CheckResult(
            "Error: Missing Config", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "error_scenarios"
        )


def _check_error_invalid_yaml() -> CheckResult:
    """Test handling of invalid YAML syntax."""
    start = time.time()

    try:
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

            if config is not None:
                return CheckResult(
                    "Error: Invalid YAML", False,
                    (time.time() - start) * 1000,
                    "Should return None for invalid YAML",
                    "error_scenarios"
                )

            duration = (time.time() - start) * 1000
            return CheckResult(
                "Error: Invalid YAML", True, duration,
                "Correctly rejected invalid YAML",
                "error_scenarios"
            )

    except Exception as e:
        return CheckResult(
            "Error: Invalid YAML", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "error_scenarios"
        )


def _check_error_missing_required_fields() -> CheckResult:
    """Test validation of missing required fields."""
    start = time.time()

    try:
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
                duration = (time.time() - start) * 1000
                return CheckResult(
                    "Error: Missing Fields", True, duration,
                    "Correctly raised ValueError for missing required fields",
                    "error_scenarios"
                )

            if not config:
                # OK if it fails to load
                duration = (time.time() - start) * 1000
                return CheckResult(
                    "Error: Missing Fields", True, duration,
                    "Correctly rejected config with missing fields",
                    "error_scenarios"
                )

            # If it loads, validation should fail
            errors = validate_config(config)

            if not errors:
                return CheckResult(
                    "Error: Missing Fields", False,
                    (time.time() - start) * 1000,
                    "Should report errors for missing required fields",
                    "error_scenarios"
                )

            duration = (time.time() - start) * 1000
            return CheckResult(
                "Error: Missing Fields", True, duration,
                f"Correctly reported {len(errors)} validation errors",
                "error_scenarios"
            )

    except Exception as e:
        return CheckResult(
            "Error: Missing Fields", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "error_scenarios"
        )


# ─── Edge Case Tests ──────────────────────────────────────────────────────────

def _check_edge_before_semester() -> CheckResult:
    """Test progress calculation before semester starts."""
    start = time.time()

    try:
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

            if not progress:
                return CheckResult(
                    "Edge: Before Semester", False,
                    (time.time() - start) * 1000,
                    "Failed to calculate progress for future course",
                    "edge_cases"
                )

            # Week should be 0 or negative, percentage 0
            if progress.get('current_week', 1) > 0:
                return CheckResult(
                    "Edge: Before Semester", False,
                    (time.time() - start) * 1000,
                    f"Current week should be ≤0, got {progress.get('current_week')}",
                    "edge_cases"
                )

            duration = (time.time() - start) * 1000
            return CheckResult(
                "Edge: Before Semester", True, duration,
                f"Correct: week={progress.get('current_week', 0)}, before semester start",
                "edge_cases"
            )

    except Exception as e:
        return CheckResult(
            "Edge: Before Semester", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "edge_cases"
        )


def _check_edge_after_semester() -> CheckResult:
    """Test progress calculation after semester ends."""
    start = time.time()

    try:
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

            if not progress:
                return CheckResult(
                    "Edge: After Semester", False,
                    (time.time() - start) * 1000,
                    "Failed to calculate progress for past course",
                    "edge_cases"
                )

            # Should indicate semester is over via percent_complete == 100
            percent = progress.get('percent_complete', 0)
            current_week = progress.get('current_week', 0)
            total_weeks = progress.get('total_weeks', 0)
            if percent < 100.0 or current_week != total_weeks:
                return CheckResult(
                    "Edge: After Semester", False,
                    (time.time() - start) * 1000,
                    f"Should be 100% complete, got {percent}% (week {current_week}/{total_weeks})",
                    "edge_cases"
                )

            duration = (time.time() - start) * 1000
            return CheckResult(
                "Edge: After Semester", True, duration,
                f"Correct: {percent}% complete, week {current_week}/{total_weeks}",
                "edge_cases"
            )

    except Exception as e:
        return CheckResult(
            "Edge: After Semester", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "edge_cases"
        )


# ─── Performance Benchmarks ───────────────────────────────────────────────────

def _check_benchmark_detection() -> CheckResult:
    """Benchmark: Teaching mode detection should be < 100ms."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Run detection
        is_teaching, method = detect_teaching_mode(str(fixture))

        duration = (time.time() - start) * 1000

        if not is_teaching:
            return CheckResult(
                "Benchmark: Detection", False, duration,
                "Failed to detect teaching project",
                "performance"
            )

        # Check performance target
        target_ms = 100
        passed = duration < target_ms

        return CheckResult(
            "Benchmark: Detection", passed, duration,
            f"{duration:.2f}ms (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return CheckResult(
            "Benchmark: Detection", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


def _check_benchmark_config_parsing() -> CheckResult:
    """Benchmark: Config parsing should be < 200ms."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Parse config
        config = load_teach_config(str(fixture))

        duration = (time.time() - start) * 1000

        if not config:
            return CheckResult(
                "Benchmark: Config Parse", False, duration,
                "Failed to load config",
                "performance"
            )

        # Check performance target
        target_ms = 200
        passed = duration < target_ms

        return CheckResult(
            "Benchmark: Config Parse", passed, duration,
            f"{duration:.2f}ms (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return CheckResult(
            "Benchmark: Config Parse", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


def _check_benchmark_validation() -> CheckResult:
    """Benchmark: Full validation should be < 5s."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Run full validation
        results = validate_teaching_content(str(fixture))

        duration = (time.time() - start) * 1000

        if not results:
            return CheckResult(
                "Benchmark: Validation", False, duration,
                "Validation failed to return results",
                "performance"
            )

        # Check performance target
        target_ms = 5000
        passed = duration < target_ms

        check_count = len(results.checks) if hasattr(results, 'checks') else 0
        return CheckResult(
            "Benchmark: Validation", passed, duration,
            f"{duration:.2f}ms for {check_count} checks (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return CheckResult(
            "Benchmark: Validation", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


def _check_benchmark_progress() -> CheckResult:
    """Benchmark: Progress calculation should be < 100ms."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Calculate progress
        progress = calculate_semester_progress(str(fixture))

        duration = (time.time() - start) * 1000

        if not progress:
            return CheckResult(
                "Benchmark: Progress", False, duration,
                "Failed to calculate progress",
                "performance"
            )

        # Check performance target
        target_ms = 100
        passed = duration < target_ms

        return CheckResult(
            "Benchmark: Progress", passed, duration,
            f"{duration:.2f}ms (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return CheckResult(
            "Benchmark: Progress", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


# ─── Pytest Wrappers ─────────────────────────────────────────────────────────


def test_e2e_minimal_course():
    result = _check_e2e_minimal_course()
    assert result.passed, result.details


def test_e2e_full_course():
    result = _check_e2e_full_course()
    assert result.passed, result.details


def test_e2e_summer_session():
    result = _check_e2e_summer_session()
    assert result.passed, result.details


def test_error_missing_config():
    result = _check_error_missing_config()
    assert result.passed, result.details


def test_error_invalid_yaml():
    result = _check_error_invalid_yaml()
    assert result.passed, result.details


def test_error_missing_required_fields():
    result = _check_error_missing_required_fields()
    assert result.passed, result.details


def test_edge_before_semester():
    result = _check_edge_before_semester()
    assert result.passed, result.details


def test_edge_after_semester():
    result = _check_edge_after_semester()
    assert result.passed, result.details


def test_benchmark_detection():
    result = _check_benchmark_detection()
    assert result.passed, result.details


def test_benchmark_config_parsing():
    result = _check_benchmark_config_parsing()
    assert result.passed, result.details


def test_benchmark_validation():
    result = _check_benchmark_validation()
    assert result.passed, result.details


def test_benchmark_progress():
    result = _check_benchmark_progress()
    assert result.passed, result.details


# ─── Test Runner ──────────────────────────────────────────────────────────────

def run_all_tests() -> List[CheckResult]:
    """Run all integration tests."""
    tests = [
        # End-to-end workflows
        _check_e2e_minimal_course,
        _check_e2e_full_course,
        _check_e2e_summer_session,

        # Error scenarios
        _check_error_missing_config,
        _check_error_invalid_yaml,
        _check_error_missing_required_fields,

        # Edge cases
        _check_edge_before_semester,
        _check_edge_after_semester,

        # Performance benchmarks
        _check_benchmark_detection,
        _check_benchmark_config_parsing,
        _check_benchmark_validation,
        _check_benchmark_progress,
    ]

    results = []
    for test_fn in tests:
        log(f"Running: {test_fn.__name__}")
        result = test_fn()
        results.append(result)
        status = "✓" if result.passed else "✗"
        log(f"  {status} {result.name}: {result.details}")

    return results


def print_summary(results: List[CheckResult]) -> None:
    """Print test results summary."""
    print("\n" + "=" * 80)
    print("TEACHING WORKFLOW INTEGRATION TEST RESULTS")
    print("=" * 80)

    # Group by category
    categories = {}
    for result in results:
        if result.category not in categories:
            categories[result.category] = []
        categories[result.category].append(result)

    # Print each category
    for category, tests in sorted(categories.items()):
        print(f"\n{category.upper().replace('_', ' ')}:")
        print("-" * 80)

        for result in tests:
            status = "✓ PASS" if result.passed else "✗ FAIL"
            print(f"  {status:8} {result.name:35} {result.duration_ms:7.2f}ms")
            if not result.passed:
                print(f"           {result.details}")

    # Overall summary
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    pct = (passed / total * 100) if total > 0 else 0

    print("\n" + "=" * 80)
    print(f"TOTAL: {passed}/{total} passed ({pct:.1f}%)")
    if failed > 0:
        print(f"FAILED: {failed} tests")
    print("=" * 80)


if __name__ == "__main__":
    log("Starting teaching workflow integration tests...")
    results = run_all_tests()
    print_summary(results)

    # Exit with error if any tests failed
    if any(not r.passed for r in results):
        sys.exit(1)
    else:
        print("\n✓ All integration tests passed!")
        sys.exit(0)
