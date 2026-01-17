#!/usr/bin/env python3
"""
Test Suite for Hub v2.0 Layer 2 - Category View
================================================
Validates category navigation, command grouping, and display generation.

Run with: python tests/test_hub_layer2.py
"""

import sys
from pathlib import Path
from dataclasses import dataclass
from datetime import datetime

# Add plugin directory to path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

# Import discovery engine
from commands._discovery import (
    get_commands_by_category,
    group_commands_by_subcategory,
    get_category_info,
    get_command_stats
)


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "general"


def log(msg: str) -> None:
    """Print with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")


# ─── Layer 2 Tests ───────────────────────────────────────────────────────────


def test_get_commands_by_category():
    """Test filtering commands by category."""
    import time
    start = time.time()

    # Test with 'code' category (should have 12 commands)
    code_commands = get_commands_by_category('code')

    duration = (time.time() - start) * 1000

    if len(code_commands) != 12:
        return TestResult(
            "Get Commands By Category",
            False,
            duration,
            f"Expected 12 code commands, found {len(code_commands)}",
            "layer2"
        )

    # Verify all commands are in 'code' category
    non_code = [cmd for cmd in code_commands if cmd['category'] != 'code']
    if non_code:
        return TestResult(
            "Get Commands By Category",
            False,
            duration,
            f"Found {len(non_code)} commands not in 'code' category",
            "layer2"
        )

    return TestResult(
        "Get Commands By Category",
        True,
        duration,
        f"Found {len(code_commands)} code commands, all in correct category",
        "layer2"
    )


def test_all_categories_have_commands():
    """Test that all expected categories return commands."""
    import time
    start = time.time()

    stats = get_command_stats()
    expected_categories = list(stats['categories'].keys())

    errors = []
    for category in expected_categories:
        commands = get_commands_by_category(category)
        expected_count = stats['categories'][category]

        if len(commands) != expected_count:
            errors.append(
                f"{category}: expected {expected_count}, got {len(commands)}"
            )

    duration = (time.time() - start) * 1000

    if errors:
        return TestResult(
            "All Categories Have Commands",
            False,
            duration,
            f"Mismatches: {'; '.join(errors)}",
            "layer2"
        )

    return TestResult(
        "All Categories Have Commands",
        True,
        duration,
        f"Validated {len(expected_categories)} categories",
        "layer2"
    )


def test_group_commands_by_subcategory():
    """Test grouping commands by subcategory."""
    import time
    start = time.time()

    # Get code commands and group by subcategory
    code_commands = get_commands_by_category('code')
    grouped = group_commands_by_subcategory(code_commands)

    duration = (time.time() - start) * 1000

    # Should have at least 'general' group
    if not grouped:
        return TestResult(
            "Group By Subcategory",
            False,
            duration,
            "No groups created",
            "layer2"
        )

    # Verify all commands are in a group
    total_in_groups = sum(len(cmds) for cmds in grouped.values())
    if total_in_groups != len(code_commands):
        return TestResult(
            "Group By Subcategory",
            False,
            duration,
            f"Lost commands: {len(code_commands)} total, {total_in_groups} in groups",
            "layer2"
        )

    return TestResult(
        "Group By Subcategory",
        True,
        duration,
        f"Created {len(grouped)} groups with {total_in_groups} commands",
        "layer2"
    )


def test_get_category_info():
    """Test getting complete category information."""
    import time
    start = time.time()

    info = get_category_info('code')

    duration = (time.time() - start) * 1000

    # Verify required fields
    required_fields = ['name', 'count', 'commands', 'subcategories', 'icon']
    missing = [f for f in required_fields if f not in info]

    if missing:
        return TestResult(
            "Get Category Info",
            False,
            duration,
            f"Missing fields: {missing}",
            "layer2"
        )

    # Verify data
    if info['name'] != 'code':
        return TestResult(
            "Get Category Info",
            False,
            duration,
            f"Wrong name: {info['name']} != 'code'",
            "layer2"
        )

    if info['count'] != 12:
        return TestResult(
            "Get Category Info",
            False,
            duration,
            f"Wrong count: {info['count']} != 12",
            "layer2"
        )

    if not info['icon']:
        return TestResult(
            "Get Category Info",
            False,
            duration,
            "Missing icon",
            "layer2"
        )

    return TestResult(
        "Get Category Info",
        True,
        duration,
        f"Complete info: {info['count']} commands, {len(info['subcategories'])} groups, icon={info['icon']}",
        "layer2"
    )


def test_category_info_all_categories():
    """Test get_category_info for all categories."""
    import time
    start = time.time()

    stats = get_command_stats()
    categories = list(stats['categories'].keys())

    errors = []
    for category in categories:
        try:
            info = get_category_info(category)

            # Verify count matches
            if info['count'] != stats['categories'][category]:
                errors.append(
                    f"{category}: count mismatch ({info['count']} != {stats['categories'][category]})"
                )

            # Verify has icon
            if not info['icon']:
                errors.append(f"{category}: missing icon")

        except Exception as e:
            errors.append(f"{category}: {str(e)}")

    duration = (time.time() - start) * 1000

    if errors:
        return TestResult(
            "Category Info All Categories",
            False,
            duration,
            f"Errors: {'; '.join(errors[:3])}{'...' if len(errors) > 3 else ''}",
            "layer2"
        )

    return TestResult(
        "Category Info All Categories",
        True,
        duration,
        f"Validated {len(categories)} categories",
        "layer2"
    )


def test_invalid_category():
    """Test handling of invalid category."""
    import time
    start = time.time()

    # Test with non-existent category
    commands = get_commands_by_category('nonexistent')

    duration = (time.time() - start) * 1000

    # Should return empty list, not error
    if commands != []:
        return TestResult(
            "Invalid Category Handling",
            False,
            duration,
            f"Expected empty list, got {len(commands)} commands",
            "layer2"
        )

    # Test get_category_info with invalid category
    info = get_category_info('nonexistent')

    if info['count'] != 0:
        return TestResult(
            "Invalid Category Handling",
            False,
            duration,
            f"Expected count=0, got {info['count']}",
            "layer2"
        )

    return TestResult(
        "Invalid Category Handling",
        True,
        duration,
        "Gracefully returns empty results for invalid category",
        "layer2"
    )


def test_layer2_display_generation():
    """Test generating Layer 2 display for a category."""
    import time
    start = time.time()

    # Generate display for 'test' category (smaller than 'code')
    info = get_category_info('test')

    # Build display
    lines = []
    lines.append("┌" + "─" * 65 + "┐")
    lines.append(f"│ {info['icon']} {info['name'].upper()} COMMANDS ({info['count']} total)")
    lines.append("├" + "─" * 65 + "┤")

    # Group by subcategory
    cmd_num = 1
    for subcat, commands in info['subcategories'].items():
        if subcat != 'general':
            lines.append(f"│ {subcat.upper()} ({len(commands)} commands)")

        for cmd in commands:
            mode_indicator = " [mode]" if cmd.get('modes') else ""
            desc = cmd.get('description', 'No description')[:40]
            lines.append(f"│   {cmd_num}. /craft:{cmd['name']}{mode_indicator:10s} {desc}")
            cmd_num += 1

    lines.append("└" + "─" * 65 + "┘")

    display = "\n".join(lines)

    duration = (time.time() - start) * 1000

    # Verify display was generated
    if not display or len(lines) < 5:
        return TestResult(
            "Layer 2 Display Generation",
            False,
            duration,
            "Failed to generate display",
            "layer2"
        )

    # Verify all commands appear
    if cmd_num - 1 != info['count']:
        return TestResult(
            "Layer 2 Display Generation",
            False,
            duration,
            f"Display shows {cmd_num - 1} commands, expected {info['count']}",
            "layer2"
        )

    return TestResult(
        "Layer 2 Display Generation",
        True,
        duration,
        f"Generated display with {len(lines)} lines for {info['count']} commands",
        "layer2"
    )


# ─── Test Runner ──────────────────────────────────────────────────────────────


def run_all_tests():
    """Run all Layer 2 tests."""
    tests = [
        test_get_commands_by_category,
        test_all_categories_have_commands,
        test_group_commands_by_subcategory,
        test_get_category_info,
        test_category_info_all_categories,
        test_invalid_category,
        test_layer2_display_generation,
    ]

    results = []
    for test_fn in tests:
        log(f"Running: {test_fn.__doc__}")
        result = test_fn()
        results.append(result)

        status = "✅ PASS" if result.passed else "❌ FAIL"
        log(f"  {status} ({result.duration_ms:.1f}ms) - {result.details}")

    return results


def generate_report(results):
    """Generate test report."""
    total = len(results)
    passed = sum(1 for r in results if r.passed)
    failed = total - passed
    total_duration = sum(r.duration_ms for r in results)

    # Group by category
    by_category = {}
    for result in results:
        cat = result.category
        if cat not in by_category:
            by_category[cat] = []
        by_category[cat].append(result)

    # Generate report
    lines = []
    lines.append("=" * 70)
    lines.append("📊 Layer 2 Test Report")
    lines.append("=" * 70)
    lines.append("")
    lines.append(f"Total Tests: {total}")
    lines.append(f"Passed: {passed}/{total} ({100 * passed // total if total > 0 else 0}%)")

    if failed > 0:
        lines.append(f"Failed: {failed}/{total}")

    lines.append(f"Total Duration: {total_duration:.0f}ms")
    lines.append("")

    # Category breakdown
    lines.append("Category Breakdown:")
    for cat, cat_results in by_category.items():
        cat_passed = sum(1 for r in cat_results if r.passed)
        cat_total = len(cat_results)
        avg_duration = sum(r.duration_ms for r in cat_results) / cat_total if cat_total > 0 else 0
        lines.append(f"  {cat}: {cat_passed}/{cat_total} pass (~{avg_duration:.0f}ms avg)")

    lines.append("")

    if failed > 0:
        lines.append("Failed Tests:")
        for result in results:
            if not result.passed:
                lines.append(f"  ❌ {result.name}")
                lines.append(f"     {result.details}")
        lines.append("")

    if passed == total:
        lines.append("🎉 All tests passed! Layer 2 is ready.")
    else:
        lines.append("⚠️  Some tests failed. Review failures above.")

    report = "\n".join(lines)
    print("")
    print(report)

    # Save report
    report_file = Path(__file__).parent / "hub_layer2_test_report.md"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")

    return passed == total


def main():
    """Main test entry point."""
    print("=" * 70)
    print("🔧 Hub v2.0 Layer 2 Test Suite")
    print("=" * 70)
    print()

    results = run_all_tests()

    print()
    success = generate_report(results)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
