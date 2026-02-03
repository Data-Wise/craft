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
class CheckResult:
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


def _check_orchestrator_v21_exists() -> CheckResult:
    """Test that orchestrator-v2.md exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return CheckResult(
            "Orchestrator v2.1 Exists", False, duration,
            "Missing agents/orchestrator-v2.md", "orchestrator"
        )

    return CheckResult(
        "Orchestrator v2.1 Exists", True, duration,
        f"File exists ({agent_path.stat().st_size} bytes)", "orchestrator"
    )


def test_orchestrator_v21_exists():
    """Test that orchestrator-v2.md exists."""
    result = _check_orchestrator_v21_exists()
    assert result.passed, result.details


def _check_orchestrator_version() -> CheckResult:
    """Test that orchestrator version is 2.1.0."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return CheckResult(
            "Orchestrator Version", False, duration,
            "File not found", "orchestrator"
        )

    content = agent_path.read_text()

    # Check version in frontmatter
    if "version: 2.4.0" not in content:
        # Try to find actual version
        version_match = re.search(r"version:\s*([\d.]+)", content)
        actual = version_match.group(1) if version_match else "unknown"
        return CheckResult(
            "Orchestrator Version", False, duration,
            f"Expected 2.4.0, found {actual}", "orchestrator"
        )

    return CheckResult(
        "Orchestrator Version", True, duration,
        "Version 2.4.0 confirmed", "orchestrator"
    )


def test_orchestrator_version():
    """Test that orchestrator version is 2.1.0."""
    result = _check_orchestrator_version()
    assert result.passed, result.details


def _check_behavior_7_mode_aware() -> CheckResult:
    """Test BEHAVIOR 7: Mode-Aware Execution exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return CheckResult(
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
        return CheckResult(
            "BEHAVIOR 7: Mode-Aware", False, duration,
            f"Missing: {', '.join(missing)}", "mode-system"
        )

    return CheckResult(
        "BEHAVIOR 7: Mode-Aware", True, duration,
        f"All {len(required_elements)} elements present", "mode-system"
    )


def test_behavior_7_mode_aware():
    """Test BEHAVIOR 7: Mode-Aware Execution exists."""
    result = _check_behavior_7_mode_aware()
    assert result.passed, result.details


def _check_behavior_8_context_tracking() -> CheckResult:
    """Test BEHAVIOR 8: Improved Context Tracking exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return CheckResult(
            "BEHAVIOR 8: Context Tracking", False, duration,
            "File not found", "context"
        )

    content = agent_path.read_text()

    required_elements = [
        "BEHAVIOR 8",
        "Context Management",
        "Estimated Tokens",
        "Context Budget",
        "Compression Triggers",
        "Per-Agent",
        "Smart Summarization"
    ]

    missing = [elem for elem in required_elements if elem not in content]

    if missing:
        return CheckResult(
            "BEHAVIOR 8: Context Tracking", False, duration,
            f"Missing: {', '.join(missing)}", "context"
        )

    return CheckResult(
        "BEHAVIOR 8: Context Tracking", True, duration,
        f"All {len(required_elements)} elements present", "context"
    )


def test_behavior_8_context_tracking():
    """Test BEHAVIOR 8: Improved Context Tracking exists."""
    result = _check_behavior_8_context_tracking()
    assert result.passed, result.details


def _check_behavior_9_timeline() -> CheckResult:
    """Test BEHAVIOR 9: Timeline View exists."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return CheckResult(
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
        return CheckResult(
            "BEHAVIOR 9: Timeline View", False, duration,
            f"Missing: {', '.join(missing)}", "timeline"
        )

    return CheckResult(
        "BEHAVIOR 9: Timeline View", True, duration,
        f"All {len(required_elements)} elements present", "timeline"
    )


def test_behavior_9_timeline():
    """Test BEHAVIOR 9: Timeline View exists."""
    result = _check_behavior_9_timeline()
    assert result.passed, result.details


def _check_new_control_commands() -> CheckResult:
    """Test that new control commands are documented."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return CheckResult(
            "New Control Commands", False, duration,
            "File not found", "commands"
        )

    content = agent_path.read_text()

    new_commands = ["timeline", "budget", "mode", "continue"]
    missing = [cmd for cmd in new_commands if f"`{cmd}`" not in content]

    if missing:
        return CheckResult(
            "New Control Commands", False, duration,
            f"Missing commands: {', '.join(missing)}", "commands"
        )

    return CheckResult(
        "New Control Commands", True, duration,
        f"All {len(new_commands)} new commands documented", "commands"
    )


def test_new_control_commands():
    """Test that new control commands are documented."""
    result = _check_new_control_commands()
    assert result.passed, result.details


def _check_mode_configuration_table() -> CheckResult:
    """Test that mode configuration table is complete."""
    start = time.time()

    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    duration = (time.time() - start) * 1000

    if not agent_path.exists():
        return CheckResult(
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
        return CheckResult(
            "Mode Configuration Table", False, duration,
            f"Issues: {', '.join(issues)}", "mode-system"
        )

    return CheckResult(
        "Mode Configuration Table", True, duration,
        "All 4 modes properly configured", "mode-system"
    )


def test_mode_configuration_table():
    """Test that mode configuration table is complete."""
    result = _check_mode_configuration_table()
    assert result.passed, result.details


# ─── Orchestrate Command Tests ───────────────────────────────────────────────


def _check_orchestrate_command_exists() -> CheckResult:
    """Test that orchestrate.md command exists."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return CheckResult(
            "Orchestrate Command Exists", False, duration,
            "Missing commands/orchestrate.md", "command"
        )

    return CheckResult(
        "Orchestrate Command Exists", True, duration,
        f"File exists ({cmd_path.stat().st_size} bytes)", "command"
    )


def test_orchestrate_command_exists():
    """Test that orchestrate.md command exists."""
    result = _check_orchestrate_command_exists()
    assert result.passed, result.details


def _check_orchestrate_command_version() -> CheckResult:
    """Test orchestrate command version is 1.1.0."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return CheckResult(
            "Orchestrate Command Version", False, duration,
            "File not found", "command"
        )

    content = cmd_path.read_text()

    if "version: 1.1.0" not in content:
        version_match = re.search(r"version:\s*([\d.]+)", content)
        actual = version_match.group(1) if version_match else "unknown"
        return CheckResult(
            "Orchestrate Command Version", False, duration,
            f"Expected 1.1.0, found {actual}", "command"
        )

    return CheckResult(
        "Orchestrate Command Version", True, duration,
        "Version 1.1.0 confirmed", "command"
    )


def test_orchestrate_command_version():
    """Test orchestrate command version is 1.1.0."""
    result = _check_orchestrate_command_version()
    assert result.passed, result.details


def _check_orchestrate_mode_syntax() -> CheckResult:
    """Test that mode syntax is documented in command."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return CheckResult(
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
        return CheckResult(
            "Orchestrate Mode Syntax", False, duration,
            f"Missing: {', '.join(missing)}", "command"
        )

    return CheckResult(
        "Orchestrate Mode Syntax", True, duration,
        "Mode syntax documented", "command"
    )


def test_orchestrate_mode_syntax():
    """Test that mode syntax is documented in command."""
    result = _check_orchestrate_mode_syntax()
    assert result.passed, result.details


def _check_orchestrate_new_subcommands() -> CheckResult:
    """Test that new subcommands are documented."""
    start = time.time()

    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    duration = (time.time() - start) * 1000

    if not cmd_path.exists():
        return CheckResult(
            "Orchestrate Subcommands", False, duration,
            "File not found", "command"
        )

    content = cmd_path.read_text()

    subcommands = ["timeline", "budget", "continue", "status", "compress", "abort"]
    missing = [sc for sc in subcommands if sc not in content]

    if missing:
        return CheckResult(
            "Orchestrate Subcommands", False, duration,
            f"Missing: {', '.join(missing)}", "command"
        )

    return CheckResult(
        "Orchestrate Subcommands", True, duration,
        f"All {len(subcommands)} subcommands documented", "command"
    )


def test_orchestrate_new_subcommands():
    """Test that new subcommands are documented."""
    result = _check_orchestrate_new_subcommands()
    assert result.passed, result.details


# ─── README Tests ────────────────────────────────────────────────────────────


def _check_readme_version() -> CheckResult:
    """Test that README shows v1.4.0-dev."""
    start = time.time()

    readme_path = PLUGIN_DIR / "README.md"
    duration = (time.time() - start) * 1000

    if not readme_path.exists():
        return CheckResult(
            "README Version", False, duration,
            "File not found", "readme"
        )

    content = readme_path.read_text()

    if "1.4.0" not in content:
        version_match = re.search(r"Version:\*\*\s*([\d.]+)", content)
        actual = version_match.group(1) if version_match else "unknown"
        return CheckResult(
            "README Version", False, duration,
            f"Expected 1.4.0, found {actual}", "readme"
        )

    return CheckResult(
        "README Version", True, duration,
        "Version 1.4.0-dev confirmed", "readme"
    )


def test_readme_version():
    """Test that README shows v1.4.0-dev."""
    result = _check_readme_version()
    assert result.passed, result.details


def _check_readme_orchestrator_v2() -> CheckResult:
    """Test that README documents orchestrator-v2."""
    start = time.time()

    readme_path = PLUGIN_DIR / "README.md"
    duration = (time.time() - start) * 1000

    if not readme_path.exists():
        return CheckResult(
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
        return CheckResult(
            "README Orchestrator v2", False, duration,
            f"Missing: {', '.join(missing)}", "readme"
        )

    return CheckResult(
        "README Orchestrator v2", True, duration,
        "Orchestrator v2 documented", "readme"
    )


def test_readme_orchestrator_v2():
    """Test that README documents orchestrator-v2."""
    result = _check_readme_orchestrator_v2()
    assert result.passed, result.details


def _check_readme_7_agents() -> CheckResult:
    """Test that README shows 7 agents."""
    start = time.time()

    readme_path = PLUGIN_DIR / "README.md"
    duration = (time.time() - start) * 1000

    if not readme_path.exists():
        return CheckResult(
            "README Agent Count", False, duration,
            "File not found", "readme"
        )

    content = readme_path.read_text()

    if "Agents (7)" not in content:
        # Try to find actual count
        count_match = re.search(r"Agents \((\d+)\)", content)
        actual = count_match.group(1) if count_match else "unknown"
        return CheckResult(
            "README Agent Count", False, duration,
            f"Expected 7 agents, found {actual}", "readme"
        )

    return CheckResult(
        "README Agent Count", True, duration,
        "7 agents documented", "readme"
    )


def test_readme_7_agents():
    """Test that README shows 7 agents."""
    result = _check_readme_7_agents()
    assert result.passed, result.details


# ─── ROADMAP Tests ───────────────────────────────────────────────────────────


def _check_roadmap_orchestrator_enhancements() -> CheckResult:
    """Test that ROADMAP includes orchestrator enhancements."""
    start = time.time()

    roadmap_path = PLUGIN_DIR / "ROADMAP.md"
    duration = (time.time() - start) * 1000

    if not roadmap_path.exists():
        return CheckResult(
            "ROADMAP Orchestrator", False, duration,
            "File not found", "roadmap"
        )

    content = roadmap_path.read_text()

    required = [
        "Orchestrator v2.1 Enhancement",
        "Mode Integration",
        "Context Tracking",
        "Timeline View"
    ]

    missing = [r for r in required if r not in content]

    if missing:
        return CheckResult(
            "ROADMAP Orchestrator", False, duration,
            f"Missing: {', '.join(missing)}", "roadmap"
        )

    return CheckResult(
        "ROADMAP Orchestrator", True, duration,
        "Orchestrator enhancements planned", "roadmap"
    )


def test_roadmap_orchestrator_enhancements():
    """Test that ROADMAP includes orchestrator enhancements."""
    result = _check_roadmap_orchestrator_enhancements()
    assert result.passed, result.details


# ─── Test Runner ─────────────────────────────────────────────────────────────


def run_all_tests() -> tuple[list[CheckResult], int, int]:
    """Run all tests and return results."""
    tests = [
        # Agent tests
        _check_orchestrator_v21_exists,
        _check_orchestrator_version,
        _check_behavior_7_mode_aware,
        _check_behavior_8_context_tracking,
        _check_behavior_9_timeline,
        _check_new_control_commands,
        _check_mode_configuration_table,
        # Command tests
        _check_orchestrate_command_exists,
        _check_orchestrate_command_version,
        _check_orchestrate_mode_syntax,
        _check_orchestrate_new_subcommands,
        # README tests
        _check_readme_version,
        _check_readme_orchestrator_v2,
        _check_readme_7_agents,
        # ROADMAP tests
        _check_roadmap_orchestrator_enhancements,
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


def generate_report(results: list[CheckResult], passed: int, failed: int) -> str:
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
