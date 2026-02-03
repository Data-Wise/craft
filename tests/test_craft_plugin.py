#!/usr/bin/env python3
"""
Craft Plugin Automated Test Suite
==================================
Validates the craft plugin structure, commands, skills, and agents.

Run with: python tests/test_craft_plugin.py
"""

import json
import os
import re
import sys
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from typing import Optional

# Add utils directory to path for linkcheck_ignore_parser
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))


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


# ─── Plugin Structure Tests ──────────────────────────────────────────────────


def _check_plugin_json_exists() -> CheckResult:
    """Test that plugin.json exists and is valid."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"

    if not plugin_json.exists():
        return CheckResult(
            "Plugin JSON Exists", False, 0,
            f"Missing: {plugin_json}", "structure"
        )

    try:
        with open(plugin_json) as f:
            data = json.load(f)

        # Check required fields
        required = ["name", "version", "description", "author"]
        missing = [f for f in required if f not in data]

        duration = (time.time() - start) * 1000

        if missing:
            return CheckResult(
                "Plugin JSON Valid", False, duration,
                f"Missing fields: {missing}", "structure"
            )

        # Check author is object
        if not isinstance(data.get("author"), dict):
            return CheckResult(
                "Plugin JSON Valid", False, duration,
                "author must be an object with 'name' field", "structure"
            )

        return CheckResult(
            "Plugin JSON Valid", True, duration,
            f"name={data['name']}, version={data['version']}", "structure"
        )

    except json.JSONDecodeError as e:
        return CheckResult(
            "Plugin JSON Valid", False, 0,
            f"Invalid JSON: {e}", "structure"
        )


def test_plugin_json_exists():
    """Test that plugin.json exists and is valid."""
    result = _check_plugin_json_exists()
    assert result.passed, result.details


def _check_directory_structure() -> CheckResult:
    """Test that required directories exist."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    required_dirs = ["commands", "skills", "agents", ".claude-plugin"]

    missing = []
    for d in required_dirs:
        if not (plugin_dir / d).is_dir():
            missing.append(d)

    duration = (time.time() - start) * 1000

    if missing:
        return CheckResult(
            "Directory Structure", False, duration,
            f"Missing directories: {missing}", "structure"
        )

    return CheckResult(
        "Directory Structure", True, duration,
        f"All {len(required_dirs)} directories present", "structure"
    )


def test_directory_structure():
    """Test that required directories exist."""
    result = _check_directory_structure()
    assert result.passed, result.details


def _check_readme_exists() -> CheckResult:
    """Test that README.md exists."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    readme = plugin_dir / "README.md"

    duration = (time.time() - start) * 1000

    if not readme.exists():
        return CheckResult(
            "README Exists", False, duration,
            "Missing README.md", "structure"
        )

    size = readme.stat().st_size
    return CheckResult(
        "README Exists", True, duration,
        f"README.md ({size} bytes)", "structure"
    )


def test_readme_exists():
    """Test that README.md exists."""
    result = _check_readme_exists()
    assert result.passed, result.details


# ─── Command Tests ───────────────────────────────────────────────────────────


def find_all_commands() -> list[Path]:
    """Find all command markdown files."""
    plugin_dir = Path(__file__).parent.parent
    commands_dir = plugin_dir / "commands"
    return list(commands_dir.rglob("*.md"))


def _check_command_count() -> CheckResult:
    """Test that we have expected number of commands."""
    import time
    start = time.time()

    commands = find_all_commands()
    duration = (time.time() - start) * 1000

    # We expect at least 15 commands based on the structure
    min_expected = 15

    if len(commands) < min_expected:
        return CheckResult(
            "Command Count", False, duration,
            f"Found {len(commands)} commands, expected at least {min_expected}",
            "commands"
        )

    return CheckResult(
        "Command Count", True, duration,
        f"Found {len(commands)} commands", "commands"
    )


def test_command_count():
    """Test that we have expected number of commands."""
    result = _check_command_count()
    assert result.passed, result.details


def validate_command_file(cmd_path: Path) -> tuple[bool, str]:
    """Validate a single command file."""
    try:
        content = cmd_path.read_text()

        # Check it's not empty
        if len(content.strip()) < 10:
            return False, "File is empty or too short"

        # Check for basic markdown structure
        if not content.startswith("#"):
            # Some commands might not start with # but should have content
            if len(content) < 50:
                return False, "Missing header or insufficient content"

        return True, "Valid"

    except Exception as e:
        return False, f"Error reading: {e}"


def _check_all_commands_valid() -> CheckResult:
    """Test that all command files are valid."""
    import time
    start = time.time()

    commands = find_all_commands()
    invalid = []

    for cmd in commands:
        valid, msg = validate_command_file(cmd)
        if not valid:
            relative = cmd.relative_to(Path(__file__).parent.parent)
            invalid.append(f"{relative}: {msg}")

    duration = (time.time() - start) * 1000

    if invalid:
        return CheckResult(
            "Commands Valid", False, duration,
            f"Invalid commands: {invalid[:3]}{'...' if len(invalid) > 3 else ''}",
            "commands"
        )

    return CheckResult(
        "Commands Valid", True, duration,
        f"All {len(commands)} commands are valid", "commands"
    )


def test_all_commands_valid():
    """Test that all command files are valid."""
    result = _check_all_commands_valid()
    assert result.passed, result.details


def _check_command_categories() -> CheckResult:
    """Test that commands are organized in categories."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    commands_dir = plugin_dir / "commands"

    # Expected categories
    expected = ["code", "docs", "git", "site"]
    found = []
    missing = []

    for cat in expected:
        cat_dir = commands_dir / cat
        if cat_dir.is_dir():
            found.append(cat)
        else:
            missing.append(cat)

    duration = (time.time() - start) * 1000

    if missing:
        return CheckResult(
            "Command Categories", False, duration,
            f"Missing categories: {missing}", "commands"
        )

    return CheckResult(
        "Command Categories", True, duration,
        f"Found categories: {found}", "commands"
    )


def test_command_categories():
    """Test that commands are organized in categories."""
    result = _check_command_categories()
    assert result.passed, result.details


def _check_hub_command_exists() -> CheckResult:
    """Test that the main hub command exists."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    hub = plugin_dir / "commands" / "hub.md"

    duration = (time.time() - start) * 1000

    if not hub.exists():
        return CheckResult(
            "Hub Command", False, duration,
            "Missing commands/hub.md", "commands"
        )

    content = hub.read_text()
    size = len(content)

    return CheckResult(
        "Hub Command", True, duration,
        f"hub.md exists ({size} chars)", "commands"
    )


def test_hub_command_exists():
    """Test that the main hub command exists."""
    result = _check_hub_command_exists()
    assert result.passed, result.details


# ─── Skills Tests ────────────────────────────────────────────────────────────


def find_all_skills() -> list[Path]:
    """Find all skill markdown files."""
    plugin_dir = Path(__file__).parent.parent
    skills_dir = plugin_dir / "skills"
    return list(skills_dir.rglob("*.md"))


def _check_skills_exist() -> CheckResult:
    """Test that skills are defined."""
    import time
    start = time.time()

    skills = find_all_skills()
    duration = (time.time() - start) * 1000

    if len(skills) == 0:
        return CheckResult(
            "Skills Exist", False, duration,
            "No skills found", "skills"
        )

    skill_names = [s.stem for s in skills]
    return CheckResult(
        "Skills Exist", True, duration,
        f"Found {len(skills)} skills: {skill_names[:5]}", "skills"
    )


def test_skills_exist():
    """Test that skills are defined."""
    result = _check_skills_exist()
    assert result.passed, result.details


def _check_design_skills() -> CheckResult:
    """Test that design skills are present."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    design_dir = plugin_dir / "skills" / "design"

    expected = ["backend-designer.md", "frontend-designer.md", "devops-helper.md"]
    found = []
    missing = []

    for skill in expected:
        if (design_dir / skill).exists():
            found.append(skill)
        else:
            missing.append(skill)

    duration = (time.time() - start) * 1000

    if missing:
        return CheckResult(
            "Design Skills", False, duration,
            f"Missing: {missing}", "skills"
        )

    return CheckResult(
        "Design Skills", True, duration,
        f"All design skills present: {found}", "skills"
    )


def test_design_skills():
    """Test that design skills are present."""
    result = _check_design_skills()
    assert result.passed, result.details


# ─── Agents Tests ────────────────────────────────────────────────────────────


def find_all_agents() -> list[Path]:
    """Find all agent markdown files."""
    plugin_dir = Path(__file__).parent.parent
    agents_dir = plugin_dir / "agents"
    return list(agents_dir.rglob("*.md"))


def _check_agents_exist() -> CheckResult:
    """Test that agents are defined."""
    import time
    start = time.time()

    agents = find_all_agents()
    duration = (time.time() - start) * 1000

    if len(agents) == 0:
        return CheckResult(
            "Agents Exist", False, duration,
            "No agents found", "agents"
        )

    agent_names = [a.stem for a in agents]
    return CheckResult(
        "Agents Exist", True, duration,
        f"Found {len(agents)} agents: {agent_names}", "agents"
    )


def test_agents_exist():
    """Test that agents are defined."""
    result = _check_agents_exist()
    assert result.passed, result.details


def _check_orchestrator_agent() -> CheckResult:
    """Test that the orchestrator agent exists."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent
    orchestrator = plugin_dir / "agents" / "orchestrator.md"

    duration = (time.time() - start) * 1000

    if not orchestrator.exists():
        return CheckResult(
            "Orchestrator Agent", False, duration,
            "Missing agents/orchestrator.md", "agents"
        )

    content = orchestrator.read_text()
    size = len(content)

    return CheckResult(
        "Orchestrator Agent", True, duration,
        f"orchestrator.md exists ({size} chars)", "agents"
    )


def test_orchestrator_agent():
    """Test that the orchestrator agent exists."""
    result = _check_orchestrator_agent()
    assert result.passed, result.details


# ─── Integration Tests ───────────────────────────────────────────────────────


def _check_no_broken_links() -> CheckResult:
    """Test for broken internal links in markdown files.

    NOTE: docs/test-violations.md is intentionally excluded from this test.
    That file contains broken links used to test the .linkcheck-ignore parser
    and link validation system. See .linkcheck-ignore for the list of expected
    broken links.

    Uses .linkcheck-ignore file to filter out documented/expected broken links.
    """
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent

    # Load ignore rules from .linkcheck-ignore
    try:
        from linkcheck_ignore_parser import parse_linkcheck_ignore
        ignore_rules = parse_linkcheck_ignore(str(plugin_dir / ".linkcheck-ignore"))
    except ImportError:
        ignore_rules = None

    all_md = list(plugin_dir.rglob("*.md"))

    broken = []
    ignored = []
    link_pattern = re.compile(r'\[([^\]]+)\]\(([^)]+)\)')
    code_block_pattern = re.compile(r'```[\s\S]*?```', re.MULTILINE)

    for md_file in all_md:
        # Skip test files, node_modules, and test-violations.md (intentional broken links)
        if "node_modules" in str(md_file) or "tests" in str(md_file) or "test-violations" in str(md_file):
            continue

        try:
            content = md_file.read_text()

            # Remove code blocks to avoid matching example links
            content_no_code = code_block_pattern.sub('', content)

            matches = link_pattern.findall(content_no_code)

            for text, link in matches:
                # Skip external links
                if link.startswith(("http://", "https://", "#")):
                    continue

                # Skip example/placeholder links (common in docs)
                if any(x in link.lower() for x in ["example", "missing", "path", "page.md", "anchor"]):
                    continue

                # Skip template placeholder links (e.g., {docs_url}, {repo_url})
                if '{' in link and '}' in link:
                    continue

                # Check relative links
                link_path = md_file.parent / link.split("#")[0]
                if not link_path.exists() and not link.startswith("/"):
                    relative = str(md_file.relative_to(plugin_dir))

                    # Check if this link should be ignored (documented in .linkcheck-ignore)
                    if ignore_rules:
                        should_ignore, category = ignore_rules.should_ignore(relative, link)
                        if should_ignore:
                            ignored.append(f"{relative}: {link} ({category})")
                            continue

                    broken.append(f"{relative}: {link}")

        except Exception:
            pass

    duration = (time.time() - start) * 1000

    if broken:
        return CheckResult(
            "No Broken Links", False, duration,
            f"Broken links: {broken[:3]}{'...' if len(broken) > 3 else ''}",
            "integration"
        )

    ignored_msg = f", {len(ignored)} ignored" if ignored else ""
    return CheckResult(
        "No Broken Links", True, duration,
        f"Checked {len(all_md)} files, no broken links{ignored_msg}", "integration"
    )


def test_no_broken_links():
    """Test for broken internal links in markdown files."""
    result = _check_no_broken_links()
    assert result.passed, result.details


def _check_consistent_naming() -> CheckResult:
    """Test that files follow naming conventions."""
    import time
    start = time.time()

    plugin_dir = Path(__file__).parent.parent

    # Check for kebab-case in command names
    commands = find_all_commands()
    bad_names = []

    for cmd in commands:
        name = cmd.stem
        # Should be lowercase with hyphens
        if name != name.lower() or "_" in name:
            relative = cmd.relative_to(plugin_dir)
            bad_names.append(str(relative))

    duration = (time.time() - start) * 1000

    if bad_names:
        return CheckResult(
            "Consistent Naming", False, duration,
            f"Non-kebab-case names: {bad_names[:3]}", "integration"
        )

    return CheckResult(
        "Consistent Naming", True, duration,
        f"All {len(commands)} command names follow conventions", "integration"
    )


def test_consistent_naming():
    """Test that files follow naming conventions."""
    result = _check_consistent_naming()
    assert result.passed, result.details


# ─── Test Runner ─────────────────────────────────────────────────────────────


def run_all_tests() -> list[CheckResult]:
    """Run all validation tests."""
    tests = [
        # Structure tests
        _check_plugin_json_exists,
        _check_directory_structure,
        _check_readme_exists,
        # Command tests
        _check_command_count,
        _check_all_commands_valid,
        _check_command_categories,
        _check_hub_command_exists,
        # Skills tests
        _check_skills_exist,
        _check_design_skills,
        # Agents tests
        _check_agents_exist,
        _check_orchestrator_agent,
        # Integration tests
        _check_no_broken_links,
        _check_consistent_naming,
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

    report = f"""# Craft Plugin Test Report

**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}
**Total Tests:** {total}
**Passed:** {passed}/{total} ({100*passed//total}%)
**Total Duration:** {total_time:.1f}ms

## Summary

| Category | Passed | Total |
|----------|--------|-------|
"""

    for cat, cat_results in categories.items():
        cat_passed = sum(1 for r in cat_results if r.passed)
        report += f"| {cat.title()} | {cat_passed} | {len(cat_results)} |\n"

    report += "\n## Detailed Results\n\n"

    for cat, cat_results in categories.items():
        report += f"### {cat.title()}\n\n"
        report += "| Test | Status | Duration | Details |\n"
        report += "|------|--------|----------|--------|\n"

        for r in cat_results:
            status = "✅ Pass" if r.passed else "❌ Fail"
            report += f"| {r.name} | {status} | {r.duration_ms:.1f}ms | {r.details} |\n"

        report += "\n"

    if passed == total:
        report += "## Result\n\n🎉 **All tests passed!** The craft plugin is correctly structured.\n"
    else:
        report += f"## Result\n\n⚠️ **{total - passed} test(s) failed.** Review details above.\n"

    return report


def main():
    print("=" * 60)
    print("🔧 Craft Plugin Test Suite")
    print("=" * 60)
    print()

    results = run_all_tests()

    print()
    print("=" * 60)
    print("📊 Generating Report...")
    print("=" * 60)

    report = generate_report(results)

    # Save report
    report_path = Path(__file__).parent / "craft_test_report.md"
    with open(report_path, "w") as f:
        f.write(report)

    print(f"\n📄 Report saved to: {report_path}")

    # Print summary
    passed = sum(1 for r in results if r.passed)
    total = len(results)

    print()
    if passed == total:
        print("🎉 All tests passed! Craft plugin is ready.")
    else:
        print(f"⚠️  {total - passed}/{total} tests failed. See report for details.")

    return 0 if passed == total else 1


if __name__ == "__main__":
    exit(main())
