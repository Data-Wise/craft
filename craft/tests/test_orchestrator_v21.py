#!/usr/bin/env python3
"""
Craft Plugin Orchestrator v2.1 Tests
====================================
Validates the orchestrator enhancements added in v1.4.0:
- Mode-aware execution (BEHAVIOR 7)
- Improved context tracking (BEHAVIOR 8)
- Timeline view (BEHAVIOR 9)

Run with: python tests/test_orchestrator_v21.py
"""

import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional
import time


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    details: str
    category: str = "orchestrator"


def log(msg: str) -> None:
    """Print with timestamp."""
    ts = datetime.now().strftime("%H:%M:%S.%f")[:-3]
    print(f"[{ts}] {msg}")


PLUGIN_DIR = Path(__file__).parent.parent


# ─── Orchestrator v2.1 Agent Tests ───────────────────────────────────────────


def test_orchestrator_v21_exists() -> TestResult:
    """Test that orchestrator-v2.md exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return TestResult(
            "Orchestrator v2.1 Exists", False, duration,
            "Missing agents/orchestrator-v2.md", "orchestrator"
        )

    return TestResult(
        "Orchestrator v2.1 Exists", True, duration,
        f"File exists ({agent_path.stat().st_size} bytes)", "orchestrator"
    )


def test_orchestrator_version() -> TestResult:
    """Test that orchestrator version is 2.1.0."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return TestResult(
            "Orchestrator Version", False, duration,
            "File not found", "orchestrator"
        )

    content = agent_path.read_text()

    # Check version in frontmatter
    if "version: 2.1.0" not in content:
        # Try to find actual version
        version_match = re.search(r"version:\s*([\d.]+)", content)
        actual = version_match.group(1) if version_match else "unknown"
        return TestResult(
            "Orchestrator Version", False, duration,
            f"Expected 2.1.0, found {actual}", "orchestrator"
        )

    return TestResult(
        "Orchestrator Version", True, duration,
        "Version 2.1.0 confirmed", "orchestrator"
    )


def test_behavior_7_mode_aware() -> TestResult:
    """Test BEHAVIOR 7: Mode-Aware Execution exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return TestResult(
            "BEHAVIOR 7: Mode-Aware", False, duration,
            "File not found", "mode-system"
        )

    content = agent_path.read_text()

    required_elements = [
        "BEHAVIOR 7",
        "Mode-Aware Execution",
        "default",
        "debug",
        "optimize",
        "release",
        "Max Agents",
        "Compression"
    ]

    missing = [elem for elem in required_elements if elem not in content]

    if missing:
        return TestResult(
            "BEHAVIOR 7: Mode-Aware", False, duration,
            f"Missing: {', '.join(missing)}", "mode-system"
        )

    return TestResult(
        "BEHAVIOR 7: Mode-Aware", True, duration,
        f"All {len(required_elements)} elements present", "mode-system"
    )


def test_behavior_8_context_tracking() -> TestResult:
    """Test BEHAVIOR 8: Improved Context Tracking exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return TestResult(
            "BEHAVIOR 8: Context Tracking", False, duration,
            "File not found", "context"
        )

    content = agent_path.read_text()

    required_elements = [
        "BEHAVIOR 8",
        "Context Tracking",
        "Estimated Tokens",
        "Context Budget",
        "Compression Triggers",
        "Per-Agent",
        "Smart Summarization"
    ]

    missing = [elem for elem in required_elements if elem not in content]

    if missing:
        return TestResult(
            "BEHAVIOR 8: Context Tracking", False, duration,
            f"Missing: {', '.join(missing)}", "context"
        )

    return TestResult(
        "BEHAVIOR 8: Context Tracking", True, duration,
        f"All {len(required_elements)} elements present", "context"
    )


def test_behavior_9_timeline() -> TestResult:
    """Test BEHAVIOR 9: Timeline View exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return TestResult(
            "BEHAVIOR 9: Timeline View", False, duration,
            "File not found", "timeline"
        )

    content = agent_path.read_text()

    required_elements = [
        "BEHAVIOR 9",
        "Timeline View",
        "EXECUTION TIMELINE",
        "ETA",
        "timeline"
    ]

    missing = [elem for elem in required_elements if elem not in content]

    if missing:
        return TestResult(
            "BEHAVIOR 9: Timeline View", False, duration,
            f"Missing: {', '.join(missing)}", "timeline"
        )

    return TestResult(
        "BEHAVIOR 9: Timeline View", True, duration,
        f"All {len(required_elements)} elements present", "timeline"
    )


def test_new_control_commands() -> TestResult:
    """Test that new control commands are documented."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return TestResult(
            "New Control Commands", False, duration,
            "File not found", "commands"
        )

    content = agent_path.read_text()

    new_commands = ["timeline", "budget", "mode", "continue"]
    missing = [cmd for cmd in new_commands if f"`{cmd}`" not in content]

    if missing:
        return TestResult(
            "New Control Commands", False, duration,
            f"Missing commands: {', '.join(missing)}", "commands"
        )

    return TestResult(
        "New Control Commands", True, duration,
        f"All {len(new_commands)} new commands documented", "commands"
    )


def test_mode_configuration_table() -> TestResult:
    """Test that mode configuration table is complete."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return TestResult(
            "Mode Configuration Table", False, duration,
            "File not found", "mode-system"
        )

    content = agent_path.read_text()

    # Check for mode configurations
    mode_configs = [
        ("`default`", "2", "70%"),
        ("`debug`", "1", "90%"),
        ("`optimize`", "4", "60%"),
        ("`release`", "4", "85%")
    ]

    issues = []
    for mode, agents, threshold in mode_configs:
        if mode not in content:
            issues.append(f"missing {mode}")
        elif threshold not in content:
            issues.append(f"{mode} missing threshold {threshold}")

    if issues:
        return TestResult(
            "Mode Configuration Table", False, duration,
            f"Issues: {', '.join(issues)}", "mode-system"
        )

    return TestResult(
        "Mode Configuration Table", True, duration,
        "All 4 modes properly configured", "mode-system"
    )


# ─── Orchestrate Command Tests ───────────────────────────────────────────────


def test_orchestrate_command_exists() -> TestResult:
    """Test that orchestrate.md command exists."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return TestResult(
            "Orchestrate Command Exists", False, duration,
            "Missing commands/orchestrate.md", "command"
        )

    return TestResult(
        "Orchestrate Command Exists", True, duration,
        f"File exists ({cmd_path.stat().st_size} bytes)", "command"
    )


def test_orchestrate_command_version() -> TestResult:
    """Test orchestrate command version is 1.1.0."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return TestResult(
            "Orchestrate Command Version", False, duration,
            "File not found", "command"
        )

    content = cmd_path.read_text()

    if "version: 1.1.0" not in content:
        version_match = re.search(r"version:\s*([\d.]+)", content)
        actual = version_match.group(1) if version_match else "unknown"
        return TestResult(
            "Orchestrate Command Version", False, duration,
            f"Expected 1.1.0, found {actual}", "command"
        )

    return TestResult(
        "Orchestrate Command Version", True, duration,
        "Version 1.1.0 confirmed", "command"
    )


def test_orchestrate_mode_syntax() -> TestResult:
    """Test that mode syntax is documented in command."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return TestResult(
            "Orchestrate Mode Syntax", False, duration,
            "File not found", "command"
        )

    content = cmd_path.read_text()

    required = [
        "<task> <mode>",
        "optimize",
        "release",
        "debug"
    ]

    missing = [r for r in required if r not in content]

    if missing:
        return TestResult(
            "Orchestrate Mode Syntax", False, duration,
            f"Missing: {', '.join(missing)}", "command"
        )

    return TestResult(
        "Orchestrate Mode Syntax", True, duration,
        "Mode syntax documented", "command"
    )


def test_orchestrate_new_subcommands() -> TestResult:
    """Test that new subcommands are documented."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return TestResult(
            "Orchestrate Subcommands", False, duration,
            "File not found", "command"
        )

    content = cmd_path.read_text()

    subcommands = ["timeline", "budget", "continue", "status", "compress", "abort"]
    missing = [sc for sc in subcommands if sc not in content]

    if missing:
        return TestResult(
            "Orchestrate Subcommands", False, duration,
            f"Missing: {', '.join(missing)}", "command"
        )

    return TestResult(
        "Orchestrate Subcommands", True, duration,
        f"All {len(subcommands)} subcommands documented", "command"
    )


# ─── README Tests ────────────────────────────────────────────────────────────


def test_readme_version() -> TestResult:
    """Test that README shows v1.4.0-dev."""
    start = time.time()

    readme_path = PLUGIN_DIR / "README.md"
    duration = (time.time() - start) * 1000

    if not readme_path.exists():
        return TestResult(
            "README Version", False, duration,
            "File not found", "readme"
        )

    content = readme_path.read_text()

    if "1.4.0" not in content:
        version_match = re.search(r"Version:\*\*\s*([\d.]+)", content)
        actual = version_match.group(1) if version_match else "unknown"
        return TestResult(
            "README Version", False, duration,
            f"Expected 1.4.0, found {actual}", "readme"
        )

    return TestResult(
        "README Version", True, duration,
        "Version 1.4.0-dev confirmed", "readme"
    )


def test_readme_orchestrator_v2() -> TestResult:
    """Test that README documents orchestrator-v2."""
    start = time.time()

    readme_path = PLUGIN_DIR / "README.md"
    duration = (time.time() - start) * 1000

    if not readme_path.exists():
        return TestResult(
            "README Orchestrator v2", False, duration,
            "File not found", "readme"
        )

    content = readme_path.read_text()

    required = [
        "orchestrator-v2",
        "Mode-aware",
        "context tracking",
        "timeline"
    ]

    missing = [r for r in required if r.lower() not in content.lower()]

    if missing:
        return TestResult(
            "README Orchestrator v2", False, duration,
            f"Missing: {', '.join(missing)}", "readme"
        )

    return TestResult(
        "README Orchestrator v2", True, duration,
        "Orchestrator v2 documented", "readme"
    )


def test_readme_7_agents() -> TestResult:
    """Test that README shows 7 agents."""
    start = time.time()

    readme_path = PLUGIN_DIR / "README.md"
    duration = (time.time() - start) * 1000

    if not readme_path.exists():
        return TestResult(
            "README Agent Count", False, duration,
            "File not found", "readme"
        )

    content = readme_path.read_text()

    if "Agents (7)" not in content:
        # Try to find actual count
        count_match = re.search(r"Agents \((\d+)\)", content)
        actual = count_match.group(1) if count_match else "unknown"
        return TestResult(
            "README Agent Count", False, duration,
            f"Expected 7 agents, found {actual}", "readme"
        )

    return TestResult(
        "README Agent Count", True, duration,
        "7 agents documented", "readme"
    )


# ─── ROADMAP Tests ───────────────────────────────────────────────────────────


def test_roadmap_orchestrator_enhancements() -> TestResult:
    """Test that ROADMAP includes orchestrator enhancements."""
    start = time.time()

    roadmap_path = PLUGIN_DIR / "ROADMAP.md"
    duration = (time.time() - start) * 1000

    if not roadmap_path.exists():
        return TestResult(
            "ROADMAP Orchestrator", False, duration,
            "File not found", "roadmap"
        )

    content = roadmap_path.read_text()

    required = [
        "Orchestrator v2 Enhancements",
        "Mode Integration",
        "Context Tracking",
        "Timeline View"
    ]

    missing = [r for r in required if r not in content]

    if missing:
        return TestResult(
            "ROADMAP Orchestrator", False, duration,
            f"Missing: {', '.join(missing)}", "roadmap"
        )

    return TestResult(
        "ROADMAP Orchestrator", True, duration,
        "Orchestrator enhancements planned", "roadmap"
    )


# ─── Test Runner ─────────────────────────────────────────────────────────────


def run_all_tests() -> tuple[list[TestResult], int, int]:
    """Run all tests and return results."""
    tests = [
        # Agent tests
        test_orchestrator_v21_exists,
        test_orchestrator_version,
        test_behavior_7_mode_aware,
        test_behavior_8_context_tracking,
        test_behavior_9_timeline,
        test_new_control_commands,
        test_mode_configuration_table,
        # Command tests
        test_orchestrate_command_exists,
        test_orchestrate_command_version,
        test_orchestrate_mode_syntax,
        test_orchestrate_new_subcommands,
        # README tests
        test_readme_version,
        test_readme_orchestrator_v2,
        test_readme_7_agents,
        # ROADMAP tests
        test_roadmap_orchestrator_enhancements,
    ]

    results = []
    passed = 0
    failed = 0

    print("\n" + "=" * 60)
    print("CRAFT ORCHESTRATOR v2.1 TEST SUITE")
    print("=" * 60 + "\n")

    for test_fn in tests:
        result = test_fn()
        results.append(result)

        status = "PASS" if result.passed else "FAIL"
        symbol = "✓" if result.passed else "✗"

        if result.passed:
            passed += 1
        else:
            failed += 1

        print(f"  {symbol} [{status}] {result.name}")
        print(f"         {result.details} ({result.duration_ms:.1f}ms)")

    return results, passed, failed


def generate_report(results: list[TestResult], passed: int, failed: int) -> str:
    """Generate markdown test report."""
    total = passed + failed

    report = f"""# Orchestrator v2.1 Test Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Plugin:** Craft v1.4.0-dev
**Tests:** {total} total, {passed} passed, {failed} failed

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | {total} |
| Passed | {passed} ({100*passed//total}%) |
| Failed | {failed} ({100*failed//total}%) |

## Results by Category

"""

    # Group by category
    categories = {}
    for r in results:
        if r.category not in categories:
            categories[r.category] = []
        categories[r.category].append(r)

    for cat, cat_results in categories.items():
        cat_passed = sum(1 for r in cat_results if r.passed)
        report += f"### {cat.title()} ({cat_passed}/{len(cat_results)})\n\n"
        report += "| Test | Status | Details | Time |\n"
        report += "|------|--------|---------|------|\n"

        for r in cat_results:
            status = "✓ PASS" if r.passed else "✗ FAIL"
            report += f"| {r.name} | {status} | {r.details} | {r.duration_ms:.1f}ms |\n"

        report += "\n"

    if failed > 0:
        report += "## Failed Tests\n\n"
        for r in results:
            if not r.passed:
                report += f"- **{r.name}**: {r.details}\n"

    return report


def main() -> int:
    """Main entry point."""
    log("Starting Orchestrator v2.1 test suite...")

    results, passed, failed = run_all_tests()

    total = passed + failed

    print("\n" + "=" * 60)
    print(f"RESULTS: {passed}/{total} passed ({100*passed//total}%)")
    print("=" * 60)

    # Generate report
    report = generate_report(results, passed, failed)
    report_path = PLUGIN_DIR / "tests" / "orchestrator_v21_report.md"
    report_path.write_text(report)
    log(f"Report saved to: {report_path}")

    if failed > 0:
        print(f"\n{failed} test(s) failed!")
        return 1
    else:
        print("\nAll tests passed!")
        return 0


if __name__ == "__main__":
    sys.exit(main())
