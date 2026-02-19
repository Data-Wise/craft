#!/usr/bin/env python3
"""
Craft Plugin v1.2.0 Feature Tests
==================================
Validates the new features added in v1.2.0:
- Mode System (Option B)
- Smart Orchestrator (Option C)

Run with: python tests/test_v120_features.py
"""

import re
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.structure]


PLUGIN_DIR = Path(__file__).parent.parent


# ─── Mode System Tests (Option B) ─────────────────────────────────────────────


def test_mode_controller_skill_exists():
    """Check that mode-controller skill exists."""
    skill_path = PLUGIN_DIR / "skills" / "modes" / "mode-controller.md"
    assert skill_path.exists(), "Missing skills/modes/mode-controller.md"

    content = skill_path.read_text()

    # Check for required mode definitions
    modes = ["default", "debug", "optimize", "release"]
    missing_modes = [m for m in modes if m not in content.lower()]
    assert not missing_modes, f"Missing mode definitions: {missing_modes}"


def test_lint_command_has_mode_support():
    """Check that lint command supports modes."""
    lint_path = PLUGIN_DIR / "commands" / "code" / "lint.md"
    assert lint_path.exists(), "Missing commands/code/lint.md"

    content = lint_path.read_text()

    # Check for mode argument in YAML frontmatter
    has_frontmatter = content.startswith("---")
    has_mode_arg = "mode" in content.lower() and "argument" in content.lower()
    has_mode_behaviors = "Mode Behavior" in content or "mode behavior" in content.lower()

    issues = []
    if not has_frontmatter:
        issues.append("missing YAML frontmatter")
    if not has_mode_arg:
        issues.append("missing mode argument")
    if not has_mode_behaviors:
        issues.append("missing mode behaviors")

    assert not issues, f"Issues: {', '.join(issues)}"


def test_test_run_command_has_mode_support():
    """Check that test:run command supports modes."""
    test_path = PLUGIN_DIR / "commands" / "test" / "run.md"
    assert test_path.exists(), "Missing commands/test/run.md"

    content = test_path.read_text()

    # Check for mode support
    has_mode_arg = "mode" in content.lower()
    has_all_modes = all(m in content.lower() for m in ["default", "debug", "optimize", "release"])

    assert has_mode_arg and has_all_modes, "Missing mode argument or mode definitions"


def test_arch_analyze_command_has_mode_support():
    """Check that arch:analyze command supports modes."""
    arch_path = PLUGIN_DIR / "commands" / "arch" / "analyze.md"
    assert arch_path.exists(), "Missing commands/arch/analyze.md"

    content = arch_path.read_text()

    # Check for mode support
    has_mode_support = "mode" in content.lower() and ("default" in content.lower() or "debug" in content.lower())
    assert has_mode_support, "Missing mode support"


# ─── Smart Orchestrator Tests (Option C) ──────────────────────────────────────


def test_do_command_exists():
    """Check that /craft:do universal command exists."""
    do_path = PLUGIN_DIR / "commands" / "do.md"
    assert do_path.exists(), "Missing commands/do.md"

    content = do_path.read_text()

    # Check for task routing logic
    has_task_arg = "task" in content.lower()
    has_routing = "route" in content.lower() or "workflow" in content.lower()
    has_categories = sum(1 for c in ["feature", "bug", "quality", "test", "release"] if c in content.lower()) >= 3

    issues = []
    if not has_task_arg:
        issues.append("missing task argument")
    if not has_routing:
        issues.append("missing routing logic")
    if not has_categories:
        issues.append("missing task categories")

    assert not issues, f"Issues: {', '.join(issues)}"


def test_check_command_exists():
    """Check that /craft:check universal pre-flight command exists."""
    check_path = PLUGIN_DIR / "commands" / "check.md"
    assert check_path.exists(), "Missing commands/check.md"

    content = check_path.read_text()

    # Check for pre-flight functionality
    has_commit_mode = "commit" in content.lower()
    has_pr_mode = "pr" in content.lower()
    has_release_mode = "release" in content.lower()
    has_project_detection = "detect" in content.lower() or "python" in content.lower()

    features = []
    if has_commit_mode:
        features.append("commit")
    if has_pr_mode:
        features.append("pr")
    if has_release_mode:
        features.append("release")
    if has_project_detection:
        features.append("detection")

    assert len(features) >= 3, f"Missing features, only found: {features}"


def test_smart_help_command_exists():
    """Check that /craft:help smart help command exists."""
    help_path = PLUGIN_DIR / "commands" / "smart-help.md"
    assert help_path.exists(), "Missing commands/smart-help.md"

    content = help_path.read_text()

    # Check for context-awareness
    has_context = "context" in content.lower()
    assert has_context, "Missing context-awareness"


def test_task_analyzer_skill_exists():
    """Check that task-analyzer skill exists."""
    skill_path = PLUGIN_DIR / "skills" / "orchestration" / "task-analyzer.md"
    assert skill_path.exists(), "Missing skills/orchestration/task-analyzer.md"

    content = skill_path.read_text()

    # Check for required capabilities
    has_intent = "intent" in content.lower()
    has_domain = "domain" in content.lower()
    has_workflow = "workflow" in content.lower()
    has_complexity = "complexity" in content.lower()

    capabilities = []
    if has_intent:
        capabilities.append("intent")
    if has_domain:
        capabilities.append("domain")
    if has_workflow:
        capabilities.append("workflow")
    if has_complexity:
        capabilities.append("complexity")

    assert len(capabilities) >= 3, f"Missing capabilities, only found: {capabilities}"


# ─── Hub & README Tests ───────────────────────────────────────────────────────


def test_hub_reflects_v120():
    """Check that hub.md reflects v1.2.0 features."""
    hub_path = PLUGIN_DIR / "commands" / "hub.md"
    assert hub_path.exists(), "Missing commands/hub.md"

    content = hub_path.read_text()

    # Check for v1.2.0 features
    has_46_commands = "46" in content
    has_8_skills = "8" in content
    has_modes = "mode" in content.lower()
    has_smart_commands = "smart" in content.lower() or "/craft:do" in content

    features = []
    if has_46_commands:
        features.append("46 commands")
    if has_8_skills:
        features.append("8 skills")
    if has_modes:
        features.append("modes")
    if has_smart_commands:
        features.append("smart commands")

    assert len(features) >= 3, f"Missing v1.2.0 features: {features}"


def test_readme_reflects_v120():
    """Check that README.md reflects v1.2.0."""
    readme_path = PLUGIN_DIR / "README.md"
    assert readme_path.exists(), "Missing README.md"

    content = readme_path.read_text()

    # Check for version
    assert "1.2.0" in content, "Missing version 1.2.0"
    assert "46" in content, "Missing 46 commands count"


# ─── Count Validation Tests ───────────────────────────────────────────────────


def test_total_command_count():
    """Check that we have at least 43 commands."""
    commands_dir = PLUGIN_DIR / "commands"
    commands = list(commands_dir.rglob("*.md"))

    expected_min = 43
    assert len(commands) >= expected_min, f"Found {len(commands)} commands, expected at least {expected_min}"


def test_total_skill_count():
    """Check that we have at least 8 skills."""
    skills_dir = PLUGIN_DIR / "skills"
    skills = list(skills_dir.rglob("*.md"))

    expected_min = 8
    if len(skills) < expected_min:
        skill_names = [s.stem for s in skills]
        assert False, f"Found {len(skills)} skills, expected at least {expected_min}: {skill_names}"


def test_skills_directory_structure():
    """Check that skills are organized correctly."""
    skills_dir = PLUGIN_DIR / "skills"

    expected_subdirs = ["design", "modes", "orchestration", "testing", "architecture", "planning"]
    found = []
    missing = []

    for subdir in expected_subdirs:
        if (skills_dir / subdir).is_dir():
            found.append(subdir)
        else:
            missing.append(subdir)

    assert len(found) >= 4, f"Missing subdirs: {missing}"
