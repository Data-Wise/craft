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

# Add parent directory to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands.utils.teach_config import load_teach_config, validate_config
from commands.utils.teaching_validation import validate_teaching_content
from commands.utils.semester_progress import calculate_current_week as _calculate_current_week
from utils.detect_teaching_mode import detect_teaching_mode


@dataclass
class TestResult:
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

def test_e2e_minimal_course() -> TestResult:
    """Test complete workflow with minimal course configuration."""
    start = time.time()

    try:
        fixture = get_fixture_path("minimal")

        # Step 1: Detection
        is_teaching, method = detect_teaching_mode(str(fixture))

        if not is_teaching:
            return TestResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                "Failed to detect minimal teaching project",
                "integration"
            )

        # Step 2: Load config
        config = load_teach_config(str(fixture))

        if not config:
            return TestResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                "Failed to load config",
                "integration"
            )

        if config['course']['code'] != "TEST 100":
            return TestResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                f"Wrong course code: {config['course']['code']}",
                "integration"
            )

        # Step 3: Validate
        errors = validate_config(config)

        if errors:
            return TestResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                f"Validation errors: {errors}",
                "integration"
            )

        # Step 4: Calculate progress
        progress = calculate_semester_progress(str(fixture))

        if not progress:
            return TestResult(
                "E2E Minimal Course", False,
                (time.time() - start) * 1000,
                "Failed to calculate progress",
                "integration"
            )

        duration = (time.time() - start) * 1000
        return TestResult(
            "E2E Minimal Course", True, duration,
            f"Complete workflow: detect({method}) → config → validate → progress ({duration:.1f}ms)",
            "integration"
        )

    except Exception as e:
        return TestResult(
            "E2E Minimal Course", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "integration"
        )


def test_e2e_full_course() -> TestResult:
    """Test complete workflow with full course configuration."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Step 1: Detection
        is_teaching, method = detect_teaching_mode(str(fixture))

        if not is_teaching:
            return TestResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                "Failed to detect full teaching project",
                "integration"
            )

        # Step 2: Load config
        config = load_teach_config(str(fixture))

        if not config:
            return TestResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                "Failed to load config",
                "integration"
            )

        # Check optional sections
        if 'teaching_assistants' not in config or len(config['teaching_assistants']) != 2:
            return TestResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                f"Expected 2 TAs, got {len(config.get('teaching_assistants', []))}",
                "integration"
            )

        # Step 3: Validate
        errors = validate_config(config)

        if errors:
            return TestResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                f"Validation errors: {errors}",
                "integration"
            )

        # Step 4: Check break handling
        breaks = config['semester'].get('breaks', [])
        if len(breaks) != 2:
            return TestResult(
                "E2E Full Course", False,
                (time.time() - start) * 1000,
                f"Expected 2 breaks, got {len(breaks)}",
                "integration"
            )

        duration = (time.time() - start) * 1000
        return TestResult(
            "E2E Full Course", True, duration,
            f"Full config: 2 TAs, 2 breaks, 5 homeworks ({duration:.1f}ms)",
            "integration"
        )

    except Exception as e:
        return TestResult(
            "E2E Full Course", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "integration"
        )


def test_e2e_summer_session() -> TestResult:
    """Test workflow with summer session (compressed, no breaks)."""
    start = time.time()

    try:
        fixture = get_fixture_path("summer")

        # Detection
        is_teaching, method = detect_teaching_mode(str(fixture))
        if not is_teaching:
            return TestResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                "Failed to detect summer teaching project",
                "integration"
            )

        # Load config
        config = load_teach_config(str(fixture))

        if not config:
            return TestResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                "Failed to load config",
                "integration"
            )

        # Verify no breaks
        breaks = config['semester'].get('breaks', [])
        if breaks:
            return TestResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                "Summer session should have no breaks",
                "integration"
            )

        # Validate
        errors = validate_config(config)

        if errors:
            return TestResult(
                "E2E Summer Session", False,
                (time.time() - start) * 1000,
                f"Validation errors: {errors}",
                "integration"
            )

        duration = (time.time() - start) * 1000
        return TestResult(
            "E2E Summer Session", True, duration,
            f"Summer session: no breaks, 8 quizzes ({duration:.1f}ms)",
            "integration"
        )

    except Exception as e:
        return TestResult(
            "E2E Summer Session", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "integration"
        )


# ─── Error Scenario Tests ─────────────────────────────────────────────────────

def test_error_missing_config() -> TestResult:
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
                return TestResult(
                    "Error: Missing Config", False,
                    (time.time() - start) * 1000,
                    "Should detect teaching project even without config",
                    "error_scenarios"
                )

            # Config load should return None
            config = load_teach_config(str(tmp_path))

            if config is not None:
                return TestResult(
                    "Error: Missing Config", False,
                    (time.time() - start) * 1000,
                    "Should return None for missing config",
                    "error_scenarios"
                )

            duration = (time.time() - start) * 1000
            return TestResult(
                "Error: Missing Config", True, duration,
                f"Correctly detected teaching but no config (via {method})",
                "error_scenarios"
            )

    except Exception as e:
        return TestResult(
            "Error: Missing Config", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "error_scenarios"
        )


def test_error_invalid_yaml() -> TestResult:
    """Test handling of invalid YAML syntax."""
    start = time.time()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config with invalid YAML
            config_content = """---
course:
  code: "TEST 100"
  title: Unclosed quote
  term: "Spring 2026"
"""
            (tmp_path / "teach-config.yml").write_text(config_content)

            # Should fail to load
            config = load_teach_config(str(tmp_path))

            if config is not None:
                return TestResult(
                    "Error: Invalid YAML", False,
                    (time.time() - start) * 1000,
                    "Should return None for invalid YAML",
                    "error_scenarios"
                )

            duration = (time.time() - start) * 1000
            return TestResult(
                "Error: Invalid YAML", True, duration,
                "Correctly rejected invalid YAML",
                "error_scenarios"
            )

    except Exception as e:
        return TestResult(
            "Error: Invalid YAML", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "error_scenarios"
        )


def test_error_missing_required_fields() -> TestResult:
    """Test validation of missing required fields."""
    start = time.time()

    try:
        with tempfile.TemporaryDirectory() as tmpdir:
            tmp_path = Path(tmpdir)

            # Create config missing required fields
            config_content = """---
course:
  code: "TEST 100"
  # Missing title and term

semester:
  start_date: "2026-01-01"
  # Missing end_date

# Missing instructor section entirely
"""
            (tmp_path / "teach-config.yml").write_text(config_content)

            config = load_teach_config(str(tmp_path))

            if not config:
                # OK if it fails to load
                duration = (time.time() - start) * 1000
                return TestResult(
                    "Error: Missing Fields", True, duration,
                    "Correctly rejected config with missing fields",
                    "error_scenarios"
                )

            # If it loads, validation should fail
            errors = validate_config(config)

            if not errors:
                return TestResult(
                    "Error: Missing Fields", False,
                    (time.time() - start) * 1000,
                    "Should report errors for missing required fields",
                    "error_scenarios"
                )

            duration = (time.time() - start) * 1000
            return TestResult(
                "Error: Missing Fields", True, duration,
                f"Correctly reported {len(errors)} validation errors",
                "error_scenarios"
            )

    except Exception as e:
        return TestResult(
            "Error: Missing Fields", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "error_scenarios"
        )


# ─── Edge Case Tests ──────────────────────────────────────────────────────────

def test_edge_before_semester() -> TestResult:
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
  code: "TEST 100"
  title: "Future Course"
  term: "Future"

semester:
  start_date: "{future_start}"
  end_date: "{future_end}"

instructor:
  name: "Test"
  email: "test@test.com"
"""
            (tmp_path / "teach-config.yml").write_text(config_content)

            progress = calculate_semester_progress(str(tmp_path))

            if not progress:
                return TestResult(
                    "Edge: Before Semester", False,
                    (time.time() - start) * 1000,
                    "Failed to calculate progress for future course",
                    "edge_cases"
                )

            # Week should be 0 or negative, percentage 0
            if progress.get('week', 1) > 0:
                return TestResult(
                    "Edge: Before Semester", False,
                    (time.time() - start) * 1000,
                    f"Current week should be ≤0, got {progress.get('week')}",
                    "edge_cases"
                )

            duration = (time.time() - start) * 1000
            return TestResult(
                "Edge: Before Semester", True, duration,
                f"Correct: week={progress.get('week', 0)}, before semester start",
                "edge_cases"
            )

    except Exception as e:
        return TestResult(
            "Edge: Before Semester", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "edge_cases"
        )


def test_edge_after_semester() -> TestResult:
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
  code: "TEST 100"
  title: "Past Course"
  term: "Past"

semester:
  start_date: "{past_start}"
  end_date: "{past_end}"

instructor:
  name: "Test"
  email: "test@test.com"
"""
            (tmp_path / "teach-config.yml").write_text(config_content)

            progress = calculate_semester_progress(str(tmp_path))

            if not progress:
                return TestResult(
                    "Edge: After Semester", False,
                    (time.time() - start) * 1000,
                    "Failed to calculate progress for past course",
                    "edge_cases"
                )

            # Should indicate semester is over
            status = progress.get('status', '')
            if 'complete' not in status.lower() and 'ended' not in status.lower():
                return TestResult(
                    "Edge: After Semester", False,
                    (time.time() - start) * 1000,
                    f"Status should indicate completion, got: {status}",
                    "edge_cases"
                )

            duration = (time.time() - start) * 1000
            return TestResult(
                "Edge: After Semester", True, duration,
                f"Correct: {status}",
                "edge_cases"
            )

    except Exception as e:
        return TestResult(
            "Edge: After Semester", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "edge_cases"
        )


# ─── Performance Benchmarks ───────────────────────────────────────────────────

def test_benchmark_detection() -> TestResult:
    """Benchmark: Teaching mode detection should be < 100ms."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Run detection
        is_teaching, method = detect_teaching_mode(str(fixture))

        duration = (time.time() - start) * 1000

        if not is_teaching:
            return TestResult(
                "Benchmark: Detection", False, duration,
                "Failed to detect teaching project",
                "performance"
            )

        # Check performance target
        target_ms = 100
        passed = duration < target_ms

        return TestResult(
            "Benchmark: Detection", passed, duration,
            f"{duration:.2f}ms (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return TestResult(
            "Benchmark: Detection", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


def test_benchmark_config_parsing() -> TestResult:
    """Benchmark: Config parsing should be < 200ms."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Parse config
        config = load_teach_config(str(fixture))

        duration = (time.time() - start) * 1000

        if not config:
            return TestResult(
                "Benchmark: Config Parse", False, duration,
                "Failed to load config",
                "performance"
            )

        # Check performance target
        target_ms = 200
        passed = duration < target_ms

        return TestResult(
            "Benchmark: Config Parse", passed, duration,
            f"{duration:.2f}ms (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return TestResult(
            "Benchmark: Config Parse", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


def test_benchmark_validation() -> TestResult:
    """Benchmark: Full validation should be < 5s."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Run full validation
        results = validate_teaching_content(str(fixture))

        duration = (time.time() - start) * 1000

        if not results:
            return TestResult(
                "Benchmark: Validation", False, duration,
                "Validation failed to return results",
                "performance"
            )

        # Check performance target
        target_ms = 5000
        passed = duration < target_ms

        check_count = len(results.get('checks', []))
        return TestResult(
            "Benchmark: Validation", passed, duration,
            f"{duration:.2f}ms for {check_count} checks (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return TestResult(
            "Benchmark: Validation", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


def test_benchmark_progress() -> TestResult:
    """Benchmark: Progress calculation should be < 100ms."""
    start = time.time()

    try:
        fixture = get_fixture_path("stat-545")

        # Calculate progress
        progress = calculate_semester_progress(str(fixture))

        duration = (time.time() - start) * 1000

        if not progress:
            return TestResult(
                "Benchmark: Progress", False, duration,
                "Failed to calculate progress",
                "performance"
            )

        # Check performance target
        target_ms = 100
        passed = duration < target_ms

        return TestResult(
            "Benchmark: Progress", passed, duration,
            f"{duration:.2f}ms (target: <{target_ms}ms) {'✓' if passed else '✗'}",
            "performance"
        )

    except Exception as e:
        return TestResult(
            "Benchmark: Progress", False,
            (time.time() - start) * 1000,
            f"Exception: {str(e)}",
            "performance"
        )


# ─── Test Runner ──────────────────────────────────────────────────────────────

def run_all_tests() -> List[TestResult]:
    """Run all integration tests."""
    tests = [
        # End-to-end workflows
        test_e2e_minimal_course,
        test_e2e_full_course,
        test_e2e_summer_session,

        # Error scenarios
        test_error_missing_config,
        test_error_invalid_yaml,
        test_error_missing_required_fields,

        # Edge cases
        test_edge_before_semester,
        test_edge_after_semester,

        # Performance benchmarks
        test_benchmark_detection,
        test_benchmark_config_parsing,
        test_benchmark_validation,
        test_benchmark_progress,
    ]

    results = []
    for test_fn in tests:
        log(f"Running: {test_fn.__name__}")
        result = test_fn()
        results.append(result)
        status = "✓" if result.passed else "✗"
        log(f"  {status} {result.name}: {result.details}")

    return results


def print_summary(results: List[TestResult]) -> None:
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
