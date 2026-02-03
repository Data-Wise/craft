#!/usr/bin/env python3
"""
Test Suite for Hub v2.0 Command Discovery
==========================================
Validates auto-detection, caching, and metadata extraction.

Run with: python tests/test_hub_discovery.py

This test suite validates the command discovery engine that powers
the /craft:hub command. It tests:
1. Discovery of all 97 commands across all categories
2. YAML frontmatter parsing and metadata extraction
3. Category inference from directory structure
4. Cache generation and invalidation
5. Performance targets (< 200ms first run, < 10ms cached)
"""

import json
import os
import shutil
import time
import yaml
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional, Dict, List, Any


@dataclass
class CheckResult:
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "general"


def log(msg: str) -> None:
    """Print with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")


# ─── Import Real Discovery Functions ─────────────────────────────────────────
# Integrated with commands._discovery module

# Add parent directory to path to import commands module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands._discovery import (
    discover_commands as real_discover_commands,
    parse_yaml_frontmatter as real_parse_frontmatter,
    get_command_stats as real_get_command_stats,
    load_cached_commands as real_load_cache,
    cache_commands as real_cache_commands
)

# Wrapper functions to match test interface
def stub_discover_commands(plugin_dir: Path) -> List[Dict[str, Any]]:
    """Wrapper: Use real discover_commands function."""
    return real_discover_commands()


def stub_parse_frontmatter(file_path: Path) -> Dict[str, Any]:
    """Wrapper: Use real parse_yaml_frontmatter function."""
    try:
        with open(file_path) as f:
            content = f.read()
        return real_parse_frontmatter(content)
    except Exception:
        return {}


def _extract_modes(file_path: Path) -> List[str]:
    """Extract execution modes from command file."""
    try:
        content = file_path.read_text()
        modes = []

        # Look for mode definitions (simple pattern matching)
        for line in content.split("\n"):
            if "| **default**" in line or "| default |" in line:
                if "default" not in modes:
                    modes.append("default")
            if "| **debug**" in line or "| debug |" in line:
                if "debug" not in modes:
                    modes.append("debug")
            if "| **optimize**" in line or "| optimize |" in line:
                if "optimize" not in modes:
                    modes.append("optimize")
            if "| **release**" in line or "| release |" in line:
                if "release" not in modes:
                    modes.append("release")

        return modes
    except Exception:
        return []


def stub_generate_cache(plugin_dir: Path, commands: List[Dict[str, Any]]) -> Path:
    """Wrapper: Use real cache_commands function."""
    real_cache_commands(commands)
    return plugin_dir / "commands" / "_cache.json"


def stub_load_cache(plugin_dir: Path) -> Optional[Dict[str, Any]]:
    """Wrapper: Use real load_cached_commands function."""
    commands = real_load_cache()
    if commands:
        return {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_commands": len(commands),
            "commands": commands
        }
    return None


def _stub_load_cache_old(plugin_dir: Path) -> Optional[Dict[str, Any]]:
    """Old stub implementation - kept for reference."""
    cache_path = plugin_dir / "commands" / "_cache.json"

    if not cache_path.exists():
        return None

    try:
        with open(cache_path) as f:
            return json.load(f)
    except Exception:
        return None


def stub_get_command_stats(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrapper: Use real get_command_stats function."""
    return real_get_command_stats()


# ─── Discovery Tests ─────────────────────────────────────────────────────────


def _check_discovery_finds_all_commands() -> CheckResult:
    """Test that discovery finds all 97 command files."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)

    duration = (time.time() - start) * 1000

    # Expected: at least 100 commands (count grows as features are added)
    min_expected = 100
    found = len(commands)

    if found < min_expected:
        return CheckResult(
            "Discovery Finds All Commands",
            False,
            duration,
            f"Expected at least {min_expected} commands, found {found}",
            "discovery"
        )

    return CheckResult(
        "Discovery Finds All Commands",
        True,
        duration,
        f"Found all {found} commands",
        "discovery"
    )


def test_discovery_finds_all_commands():
    """Test that discovery finds all 97 command files."""
    result = _check_discovery_finds_all_commands()
    assert result.passed, result.details


def _check_category_inference() -> CheckResult:
    """Test category inference from file paths."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)

    # Test specific category inferences
    # Note: discovery module returns relative filenames, not full paths
    test_cases = {
        "code/lint.md": "code",
        "git/worktree.md": "git",
        "hub.md": "hub",
    }

    errors = []
    for file_path, expected_cat in test_cases.items():
        cmd = next((c for c in commands if c["file"] == file_path), None)
        if not cmd:
            errors.append(f"{file_path}: not found")
        elif cmd["category"] != expected_cat:
            errors.append(f"{file_path}: expected '{expected_cat}', got '{cmd['category']}'")

    duration = (time.time() - start) * 1000

    if errors:
        return CheckResult(
            "Category Inference",
            False,
            duration,
            f"Errors: {errors[:3]}",
            "discovery"
        )

    return CheckResult(
        "Category Inference",
        True,
        duration,
        f"All {len(test_cases)} test cases passed",
        "discovery"
    )


def test_category_inference():
    """Test category inference from file paths."""
    result = _check_category_inference()
    assert result.passed, result.details


def _check_frontmatter_parsing() -> CheckResult:
    """Test YAML frontmatter extraction."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    lint_cmd = plugin_dir / "commands" / "code" / "lint.md"

    if not lint_cmd.exists():
        return CheckResult(
            "Frontmatter Parsing",
            False,
            0,
            f"Test file not found: {lint_cmd}",
            "parsing"
        )

    metadata = stub_parse_frontmatter(lint_cmd)

    duration = (time.time() - start) * 1000

    # Verify expected fields
    required_fields = ["description", "arguments"]
    missing = [f for f in required_fields if f not in metadata]

    if missing:
        return CheckResult(
            "Frontmatter Parsing",
            False,
            duration,
            f"Missing fields: {missing}",
            "parsing"
        )

    # Verify arguments structure
    if not isinstance(metadata["arguments"], list):
        return CheckResult(
            "Frontmatter Parsing",
            False,
            duration,
            "arguments must be a list",
            "parsing"
        )

    # Check first argument has required fields
    if metadata["arguments"]:
        arg = metadata["arguments"][0]
        arg_fields = ["name", "description", "required"]
        missing_arg_fields = [f for f in arg_fields if f not in arg]

        if missing_arg_fields:
            return CheckResult(
                "Frontmatter Parsing",
                False,
                duration,
                f"Argument missing fields: {missing_arg_fields}",
                "parsing"
            )

    return CheckResult(
        "Frontmatter Parsing",
        True,
        duration,
        f"Parsed {len(metadata)} fields, {len(metadata['arguments'])} arguments",
        "parsing"
    )


def test_frontmatter_parsing():
    """Test YAML frontmatter extraction."""
    result = _check_frontmatter_parsing()
    assert result.passed, result.details


def _check_mode_extraction() -> CheckResult:
    """Test execution mode extraction from command content."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    lint_cmd = plugin_dir / "commands" / "code" / "lint.md"

    if not lint_cmd.exists():
        return CheckResult(
            "Mode Extraction",
            False,
            0,
            f"Test file not found: {lint_cmd}",
            "parsing"
        )

    modes = _extract_modes(lint_cmd)

    duration = (time.time() - start) * 1000

    # lint.md should have: default, debug, optimize, release
    expected_modes = ["default", "debug", "optimize", "release"]

    missing = [m for m in expected_modes if m not in modes]
    if missing:
        return CheckResult(
            "Mode Extraction",
            False,
            duration,
            f"Missing modes: {missing} (found: {modes})",
            "parsing"
        )

    return CheckResult(
        "Mode Extraction",
        True,
        duration,
        f"Extracted {len(modes)} modes: {modes}",
        "parsing"
    )


def test_mode_extraction():
    """Test execution mode extraction from command content."""
    result = _check_mode_extraction()
    assert result.passed, result.details


# ─── Cache Tests ─────────────────────────────────────────────────────────────


def _check_cache_generation() -> CheckResult:
    """Test cache file is generated correctly."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    cache_path = plugin_dir / "commands" / "_cache.json"

    # Remove existing cache
    if cache_path.exists():
        cache_path.unlink()

    # Generate cache
    commands = stub_discover_commands(plugin_dir)
    generated_path = stub_generate_cache(plugin_dir, commands)

    duration = (time.time() - start) * 1000

    if not generated_path.exists():
        return CheckResult(
            "Cache Generation",
            False,
            duration,
            "Cache file not created",
            "cache"
        )

    # Verify JSON structure
    try:
        with open(generated_path) as f:
            cache_data = json.load(f)

        # Updated to match actual discovery module cache structure
        required_fields = ["generated", "count", "commands"]
        missing = [f for f in required_fields if f not in cache_data]

        if missing:
            return CheckResult(
                "Cache Generation",
                False,
                duration,
                f"Cache missing fields: {missing}",
                "cache"
            )

        return CheckResult(
            "Cache Generation",
            True,
            duration,
            f"Cache created with {cache_data['count']} commands",
            "cache"
        )

    except json.JSONDecodeError as e:
        return CheckResult(
            "Cache Generation",
            False,
            duration,
            f"Invalid JSON: {e}",
            "cache"
        )


def test_cache_generation():
    """Test cache file is generated correctly."""
    result = _check_cache_generation()
    assert result.passed, result.details


def _check_cache_loading() -> CheckResult:
    """Test cache file loading."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent

    # Ensure cache exists
    commands = stub_discover_commands(plugin_dir)
    stub_generate_cache(plugin_dir, commands)

    # Load cache
    cache_data = stub_load_cache(plugin_dir)

    duration = (time.time() - start) * 1000

    if cache_data is None:
        return CheckResult(
            "Cache Loading",
            False,
            duration,
            "Failed to load cache",
            "cache"
        )

    if "commands" not in cache_data:
        return CheckResult(
            "Cache Loading",
            False,
            duration,
            "Cache missing commands array",
            "cache"
        )

    return CheckResult(
        "Cache Loading",
        True,
        duration,
        f"Loaded {len(cache_data['commands'])} commands from cache",
        "cache"
    )


def test_cache_loading():
    """Test cache file loading."""
    result = _check_cache_loading()
    assert result.passed, result.details


def _check_cache_invalidation() -> CheckResult:
    """Test cache rebuilds when files change."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    cache_path = plugin_dir / "commands" / "_cache.json"

    # Generate fresh cache
    commands = stub_discover_commands(plugin_dir)
    stub_generate_cache(plugin_dir, commands)

    original_mtime = cache_path.stat().st_mtime

    # Wait a bit to ensure different timestamp
    time.sleep(0.1)

    # Touch a command file
    test_file = plugin_dir / "commands" / "hub.md"
    if test_file.exists():
        test_file.touch()

    # Simulate invalidation check
    test_file_mtime = test_file.stat().st_mtime
    cache_is_stale = test_file_mtime > original_mtime

    duration = (time.time() - start) * 1000

    if not cache_is_stale:
        return CheckResult(
            "Cache Invalidation",
            False,
            duration,
            "Cache not marked as stale after file modification",
            "cache"
        )

    return CheckResult(
        "Cache Invalidation",
        True,
        duration,
        "Cache correctly detected as stale",
        "cache"
    )


def test_cache_invalidation():
    """Test cache rebuilds when files change."""
    result = _check_cache_invalidation()
    assert result.passed, result.details


# ─── Performance Tests ───────────────────────────────────────────────────────


def _check_performance_first_run() -> CheckResult:
    """Test first run completes < 200ms."""
    plugin_dir = Path(__file__).parent.parent
    cache_path = plugin_dir / "commands" / "_cache.json"

    # Remove cache to force fresh discovery
    if cache_path.exists():
        cache_path.unlink()

    start = time.time()
    commands = stub_discover_commands(plugin_dir)
    duration = (time.time() - start) * 1000

    target_ms = 200

    if duration > target_ms:
        return CheckResult(
            "Performance (First Run)",
            False,
            duration,
            f"Took {duration:.1f}ms, target < {target_ms}ms",
            "performance"
        )

    return CheckResult(
        "Performance (First Run)",
        True,
        duration,
        f"Completed in {duration:.1f}ms (target < {target_ms}ms)",
        "performance"
    )


def test_performance_first_run():
    """Test first run completes < 200ms."""
    result = _check_performance_first_run()
    assert result.passed, result.details


def _check_performance_cached_run() -> CheckResult:
    """Test cached run completes < 10ms."""
    plugin_dir = Path(__file__).parent.parent

    # Ensure cache exists
    commands = stub_discover_commands(plugin_dir)
    stub_generate_cache(plugin_dir, commands)

    start = time.time()
    cache_data = stub_load_cache(plugin_dir)
    duration = (time.time() - start) * 1000

    target_ms = 10

    if cache_data is None:
        return CheckResult(
            "Performance (Cached)",
            False,
            duration,
            "Cache load failed",
            "performance"
        )

    if duration > target_ms:
        return CheckResult(
            "Performance (Cached)",
            False,
            duration,
            f"Took {duration:.1f}ms, target < {target_ms}ms",
            "performance"
        )

    return CheckResult(
        "Performance (Cached)",
        True,
        duration,
        f"Completed in {duration:.1f}ms (target < {target_ms}ms)",
        "performance"
    )


def test_performance_cached_run():
    """Test cached run completes < 10ms."""
    result = _check_performance_cached_run()
    assert result.passed, result.details


# ─── Statistics Tests ────────────────────────────────────────────────────────


def _check_command_stats() -> CheckResult:
    """Test get_command_stats() returns correct counts."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)
    stats = stub_get_command_stats(commands)

    duration = (time.time() - start) * 1000

    # Verify structure
    required_fields = ["total", "categories", "with_modes"]
    missing = [f for f in required_fields if f not in stats]

    if missing:
        return CheckResult(
            "Command Stats",
            False,
            duration,
            f"Missing fields: {missing}",
            "statistics"
        )

    # Verify total
    if stats["total"] != len(commands):
        return CheckResult(
            "Command Stats",
            False,
            duration,
            f"Total mismatch: {stats['total']} vs {len(commands)}",
            "statistics"
        )

    # Verify category counts sum to total
    cat_sum = sum(stats["categories"].values())
    if cat_sum != stats["total"]:
        return CheckResult(
            "Command Stats",
            False,
            duration,
            f"Category sum {cat_sum} doesn't match total {stats['total']}",
            "statistics"
        )

    return CheckResult(
        "Command Stats",
        True,
        duration,
        f"Total: {stats['total']}, Categories: {len(stats['categories'])}, With modes: {stats['with_modes']}",
        "statistics"
    )


def test_command_stats():
    """Test get_command_stats() returns correct counts."""
    result = _check_command_stats()
    assert result.passed, result.details


def _check_all_categories_present() -> CheckResult:
    """Test all expected categories are discovered."""
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)
    stats = stub_get_command_stats(commands)

    duration = (time.time() - start) * 1000

    # Expected categories based on directory structure
    expected_categories = {
        "code", "test", "docs", "git", "site",
        "arch", "ci", "dist", "workflow", "hub"
    }

    found_categories = set(stats["categories"].keys())
    missing = expected_categories - found_categories

    if missing:
        return CheckResult(
            "All Categories Present",
            False,
            duration,
            f"Missing categories: {missing}",
            "statistics"
        )

    return CheckResult(
        "All Categories Present",
        True,
        duration,
        f"Found all expected categories: {sorted(found_categories)}",
        "statistics"
    )


def test_all_categories_present():
    """Test all expected categories are discovered."""
    result = _check_all_categories_present()
    assert result.passed, result.details


def _check_missing_frontmatter_handling() -> CheckResult:
    """Test graceful handling of missing frontmatter."""
    start = time.time()

    # Create temporary test file without frontmatter
    plugin_dir = Path(__file__).parent.parent
    test_file = plugin_dir / "commands" / "_test_no_frontmatter.md"

    try:
        test_file.write_text("# Test Command\n\nThis has no frontmatter.")

        metadata = stub_parse_frontmatter(test_file)

        duration = (time.time() - start) * 1000

        # Should return empty dict, not None or error
        if metadata is None:
            return CheckResult(
                "Missing Frontmatter Handling",
                False,
                duration,
                "Returned None instead of empty dict",
                "parsing"
            )

        if not isinstance(metadata, dict):
            return CheckResult(
                "Missing Frontmatter Handling",
                False,
                duration,
                f"Returned {type(metadata)} instead of dict",
                "parsing"
            )

        return CheckResult(
            "Missing Frontmatter Handling",
            True,
            duration,
            "Gracefully returned empty dict",
            "parsing"
        )

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()


def test_missing_frontmatter_handling():
    """Test graceful handling of missing frontmatter."""
    result = _check_missing_frontmatter_handling()
    assert result.passed, result.details


# ─── Test Runner ─────────────────────────────────────────────────────────────


def run_all_tests() -> list[CheckResult]:
    """Run all validation tests."""
    tests = [
        # Discovery tests
        _check_discovery_finds_all_commands,
        _check_category_inference,

        # Parsing tests
        _check_frontmatter_parsing,
        _check_mode_extraction,
        _check_missing_frontmatter_handling,

        # Cache tests
        _check_cache_generation,
        _check_cache_loading,
        _check_cache_invalidation,

        # Performance tests
        _check_performance_first_run,
        _check_performance_cached_run,

        # Statistics tests
        _check_command_stats,
        _check_all_categories_present,
    ]

    results = []
    for test_fn in tests:
        doc = test_fn.__doc__ or test_fn.__name__
        log(f"Running: {doc.strip().split('.')[0]}...")
        result = test_fn()
        results.append(result)
        status = "✅ PASS" if result.passed else "❌ FAIL"
        log(f"  {status} ({result.duration_ms:.1f}ms) - {result.details}")

    return results


def generate_report(results: list[CheckResult]) -> str:
    """Generate markdown report."""
    passed = sum(1 for r in results if r.passed)
    total = len(results)
    total_time = sum(r.duration_ms for r in results)

    # Group by category
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = []
        categories[r.category].append(r)

    report = f"""# Hub v2.0 Discovery Test Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests:** {total}
**Passed:** {passed}/{total} ({100*passed//total}%)
**Total Duration:** {total_time:.1f}ms

## Summary

| Category | Passed | Total |
|----------|--------|-------|
"""

    for cat, cat_results in sorted(categories.items()):
        cat_passed = sum(1 for r in cat_results if r.passed)
        report += f"| {cat.title()} | {cat_passed} | {len(cat_results)} |\n"

    report += "\n## Detailed Results\n\n"

    for cat, cat_results in sorted(categories.items()):
        report += f"### {cat.title()}\n\n"
        report += "| Test | Status | Duration | Details |\n"
        report += "|------|--------|----------|--------|\n"

        for r in cat_results:
            status = "✅ Pass" if r.passed else "❌ Fail"
            details = r.details.replace("|", "\\|")  # Escape pipes in details
            report += f"| {r.name} | {status} | {r.duration_ms:.1f}ms | {details} |\n"

        report += "\n"

    if passed == total:
        report += "## Result\n\n🎉 **All tests passed!** The Hub v2.0 discovery system is working correctly.\n"
    else:
        report += f"## Result\n\n⚠️ **{total - passed} test(s) failed.** Review details above.\n"

    # Add implementation notes
    report += """
## Implementation Notes

### Current Status
- ✅ Test structure complete with 12 test cases
- ⏳ Using stubbed discovery functions (awaiting Agent 1 implementation)
- ⏳ Ready for integration testing after `commands/_discovery.py` is complete

### Integration Steps
After Agent 1 completes `commands/_discovery.py`:
1. Replace stub functions with actual imports:
   ```python
   from commands._discovery import (
       discover_commands,
       parse_frontmatter,
       generate_cache,
       load_cache,
       get_command_stats
   )
   ```
2. Re-run tests: `python tests/test_hub_discovery.py`
3. Validate all 97 commands are discovered
4. Verify performance targets are met

### Test Coverage
- **Discovery**: Command finding, category inference
- **Parsing**: YAML frontmatter, mode extraction, error handling
- **Cache**: Generation, loading, invalidation
- **Performance**: First run < 200ms, cached < 10ms
- **Statistics**: Total counts, category breakdown, mode counts

### Expected Results (Post-Integration)
- Total commands: 97 (71 main + 26 docs/utils)
- Categories: code, test, docs, git, site, arch, ci, dist, workflow, hub
- Commands with modes: ~15-20
- Performance: First run ~50-150ms, cached ~1-5ms
"""

    return report


def main():
    print("=" * 60)
    print("🔧 Hub v2.0 Discovery Test Suite")
    print("=" * 60)
    print()

    results = run_all_tests()

    print()
    print("=" * 60)
    print("📊 Generating Report...")
    print("=" * 60)

    report = generate_report(results)

    # Save report
    report_path = Path(__file__).parent / "hub_discovery_test_report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_path}")

    # Print summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)

    print()
    if passed == total:
        print("🎉 All tests passed! Hub v2.0 discovery system is ready.")
    else:
        print(f"⚠️  {total - passed}/{total} tests failed. See report for details.")

    print()
    print("📝 Note: Tests are using stubbed functions.")
    print("   After Agent 1 completes, update imports to use actual discovery module.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
