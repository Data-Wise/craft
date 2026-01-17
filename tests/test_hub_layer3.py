#!/usr/bin/env python3
"""
Test Suite for Hub v2.0 Layer 3 - Command Detail View
======================================================
Validates command lookup, tutorial generation, and detail display.

Run with: python tests/test_hub_layer3.py
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
    get_command_detail,
    generate_command_tutorial,
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


# ─── Layer 3 Tests ───────────────────────────────────────────────────────────


def test_get_command_detail_exact_match():
    """Test getting command detail with exact match."""
    import time
    start = time.time()

    # Test with exact command name
    command = get_command_detail('code:lint')

    duration = (time.time() - start) * 1000

    if not command:
        return TestResult(
            "Get Command Detail - Exact Match",
            False,
            duration,
            "Failed to find 'code:lint' command",
            "layer3"
        )

    # Verify required fields
    required_fields = ['name', 'category', 'description', 'file']
    missing = [f for f in required_fields if f not in command]

    if missing:
        return TestResult(
            "Get Command Detail - Exact Match",
            False,
            duration,
            f"Missing fields: {missing}",
            "layer3"
        )

    # Verify data
    if command['name'] != 'code:lint':
        return TestResult(
            "Get Command Detail - Exact Match",
            False,
            duration,
            f"Wrong name: {command['name']} != 'code:lint'",
            "layer3"
        )

    if command['category'] != 'code':
        return TestResult(
            "Get Command Detail - Exact Match",
            False,
            duration,
            f"Wrong category: {command['category']} != 'code'",
            "layer3"
        )

    return TestResult(
        "Get Command Detail - Exact Match",
        True,
        duration,
        f"Found command: {command['name']} in {command['category']}",
        "layer3"
    )


def test_get_command_detail_not_found():
    """Test handling of non-existent command."""
    import time
    start = time.time()

    command = get_command_detail('nonexistent:command')

    duration = (time.time() - start) * 1000

    if command is not None:
        return TestResult(
            "Get Command Detail - Not Found",
            False,
            duration,
            f"Expected None, got command: {command.get('name')}",
            "layer3"
        )

    return TestResult(
        "Get Command Detail - Not Found",
        True,
        duration,
        "Correctly returns None for non-existent command",
        "layer3"
    )


def test_get_command_detail_all_categories():
    """Test get_command_detail for commands across all categories."""
    import time
    start = time.time()

    # Test one command from each major category
    test_commands = [
        'code:lint',
        'test:run',
        'docs:sync',
        'git:worktree',
        'site:build'
    ]

    errors = []
    for cmd_name in test_commands:
        cmd = get_command_detail(cmd_name)
        if not cmd:
            errors.append(f"{cmd_name}: not found")
            continue

        # Verify name matches
        if cmd['name'] != cmd_name:
            errors.append(f"{cmd_name}: name mismatch ({cmd['name']})")

        # Verify has description
        if not cmd.get('description'):
            errors.append(f"{cmd_name}: missing description")

    duration = (time.time() - start) * 1000

    if errors:
        return TestResult(
            "Get Command Detail All Categories",
            False,
            duration,
            f"Errors: {'; '.join(errors)}",
            "layer3"
        )

    return TestResult(
        "Get Command Detail All Categories",
        True,
        duration,
        f"Validated {len(test_commands)} commands across categories",
        "layer3"
    )


def test_generate_command_tutorial_basic():
    """Test generating basic tutorial for a command."""
    import time
    start = time.time()

    # Get a command
    command = get_command_detail('code:lint')

    if not command:
        return TestResult(
            "Generate Tutorial - Basic",
            False,
            0,
            "Failed to find test command",
            "layer3"
        )

    # Generate tutorial
    tutorial = generate_command_tutorial(command)

    duration = (time.time() - start) * 1000

    # Verify tutorial has content
    if not tutorial or len(tutorial) < 100:
        return TestResult(
            "Generate Tutorial - Basic",
            False,
            duration,
            f"Tutorial too short: {len(tutorial)} chars",
            "layer3"
        )

    # Verify contains key sections
    required_sections = [
        '📚 COMMAND:',
        'DESCRIPTION',
        'BASIC USAGE',
        'Back to',
        'Back to Hub'
    ]

    missing = [s for s in required_sections if s not in tutorial]

    if missing:
        return TestResult(
            "Generate Tutorial - Basic",
            False,
            duration,
            f"Missing sections: {missing}",
            "layer3"
        )

    return TestResult(
        "Generate Tutorial - Basic",
        True,
        duration,
        f"Generated {len(tutorial)} char tutorial with all sections",
        "layer3"
    )


def test_generate_command_tutorial_with_modes():
    """Test tutorial generation for command with modes."""
    import time
    start = time.time()

    # Get a command with modes
    command = get_command_detail('code:lint')

    if not command:
        return TestResult(
            "Generate Tutorial - With Modes",
            False,
            0,
            "Failed to find test command",
            "layer3"
        )

    # Generate tutorial
    tutorial = generate_command_tutorial(command)

    duration = (time.time() - start) * 1000

    # If command has modes, tutorial should show them
    if command.get('modes'):
        if 'MODES' not in tutorial:
            return TestResult(
                "Generate Tutorial - With Modes",
                False,
                duration,
                "Command has modes but tutorial doesn't show MODES section",
                "layer3"
            )

        # Check for mode names
        modes_shown = sum(1 for mode in command['modes'] if mode in tutorial)
        if modes_shown == 0:
            return TestResult(
                "Generate Tutorial - With Modes",
                False,
                duration,
                "MODES section present but no mode names found",
                "layer3"
            )

    return TestResult(
        "Generate Tutorial - With Modes",
        True,
        duration,
        f"Tutorial correctly shows {len(command.get('modes', []))} modes",
        "layer3"
    )


def test_generate_tutorial_multiple_commands():
    """Test generating tutorials for multiple commands."""
    import time
    start = time.time()

    test_commands = ['code:lint', 'test:run', 'docs:sync']
    errors = []

    for cmd_name in test_commands:
        cmd = get_command_detail(cmd_name)
        if not cmd:
            errors.append(f"{cmd_name}: not found")
            continue

        tutorial = generate_command_tutorial(cmd)

        # Verify tutorial is generated
        if not tutorial or len(tutorial) < 100:
            errors.append(f"{cmd_name}: tutorial too short")
            continue

        # Verify command name appears
        if f'/craft:{cmd_name}' not in tutorial:
            errors.append(f"{cmd_name}: command name not in tutorial")

        # Verify description appears
        if cmd.get('description') and cmd['description'] not in tutorial:
            errors.append(f"{cmd_name}: description not in tutorial")

    duration = (time.time() - start) * 1000

    if errors:
        return TestResult(
            "Generate Tutorial Multiple Commands",
            False,
            duration,
            f"Errors: {'; '.join(errors[:3])}{'...' if len(errors) > 3 else ''}",
            "layer3"
        )

    return TestResult(
        "Generate Tutorial Multiple Commands",
        True,
        duration,
        f"Generated tutorials for {len(test_commands)} commands",
        "layer3"
    )


def test_layer3_display_format():
    """Test that tutorial display follows correct format."""
    import time
    start = time.time()

    command = get_command_detail('code:lint')

    if not command:
        return TestResult(
            "Layer 3 Display Format",
            False,
            0,
            "Failed to find test command",
            "layer3"
        )

    tutorial = generate_command_tutorial(command)

    duration = (time.time() - start) * 1000

    # Verify box drawing characters (ASCII art border)
    if not tutorial.startswith('┌'):
        return TestResult(
            "Layer 3 Display Format",
            False,
            duration,
            "Tutorial doesn't start with box border",
            "layer3"
        )

    if not tutorial.endswith('┘'):
        return TestResult(
            "Layer 3 Display Format",
            False,
            duration,
            "Tutorial doesn't end with box border",
            "layer3"
        )

    # Count lines
    lines = tutorial.split('\n')
    if len(lines) < 10:
        return TestResult(
            "Layer 3 Display Format",
            False,
            duration,
            f"Tutorial too short: {len(lines)} lines",
            "layer3"
        )

    # Verify navigation footer exists
    footer_found = False
    for line in lines[-5:]:  # Check last 5 lines
        if 'Back to' in line or 'Hub' in line:
            footer_found = True
            break

    if not footer_found:
        return TestResult(
            "Layer 3 Display Format",
            False,
            duration,
            "Navigation footer not found",
            "layer3"
        )

    return TestResult(
        "Layer 3 Display Format",
        True,
        duration,
        f"Tutorial follows format: {len(lines)} lines, proper borders, navigation",
        "layer3"
    )


def test_related_commands_lookup():
    """Test that related commands are looked up correctly."""
    import time
    start = time.time()

    # Find a command with related_commands field
    stats = get_command_stats()
    command = None

    # Try to find a command with related commands
    # For now, test with code:lint (we'll add related_commands to frontmatter)
    command = get_command_detail('code:lint')

    if not command:
        return TestResult(
            "Related Commands Lookup",
            False,
            0,
            "Failed to find test command",
            "layer3"
        )

    tutorial = generate_command_tutorial(command)

    duration = (time.time() - start) * 1000

    # If command has related_commands, they should appear in tutorial
    related = command.get('related_commands', [])

    if related:
        # Check if RELATED COMMANDS section exists
        if 'RELATED COMMANDS' not in tutorial:
            return TestResult(
                "Related Commands Lookup",
                False,
                duration,
                "Command has related_commands but section not in tutorial",
                "layer3"
            )

        # Check if at least one related command appears
        found_count = sum(1 for rel in related if rel in tutorial)

        if found_count == 0:
            return TestResult(
                "Related Commands Lookup",
                False,
                duration,
                "RELATED COMMANDS section exists but no commands found",
                "layer3"
            )

        return TestResult(
            "Related Commands Lookup",
            True,
            duration,
            f"Found {found_count}/{len(related)} related commands in tutorial",
            "layer3"
        )
    else:
        # No related commands, tutorial shouldn't have section
        if 'RELATED COMMANDS' in tutorial:
            return TestResult(
                "Related Commands Lookup",
                False,
                duration,
                "Command has no related_commands but section appears",
                "layer3"
            )

        return TestResult(
            "Related Commands Lookup",
            True,
            duration,
            "Command has no related_commands, section correctly omitted",
            "layer3"
        )


# ─── Test Runner ──────────────────────────────────────────────────────────────


def run_all_tests():
    """Run all Layer 3 tests."""
    tests = [
        test_get_command_detail_exact_match,
        test_get_command_detail_not_found,
        test_get_command_detail_all_categories,
        test_generate_command_tutorial_basic,
        test_generate_command_tutorial_with_modes,
        test_generate_tutorial_multiple_commands,
        test_layer3_display_format,
        test_related_commands_lookup,
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
    lines.append("📊 Layer 3 Test Report")
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
        lines.append("🎉 All tests passed! Layer 3 is ready.")
    else:
        lines.append("⚠️  Some tests failed. Review failures above.")

    report = "\n".join(lines)
    print("")
    print(report)

    # Save report
    report_file = Path(__file__).parent / "hub_layer3_test_report.md"
    with open(report_file, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_file}")

    return passed == total


def main():
    """Main test entry point."""
    print("=" * 70)
    print("🔧 Hub v2.0 Layer 3 Test Suite")
    print("=" * 70)
    print()

    results = run_all_tests()

    print()
    success = generate_report(results)

    return 0 if success else 1


if __name__ == "__main__":
    exit(main())
