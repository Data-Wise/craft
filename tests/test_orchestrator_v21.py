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
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.orchestrator]


PLUGIN_DIR = Path(__file__).parent.parent


# ─── Orchestrator v2.1 Agent Tests ───────────────────────────────────────────


def test_orchestrator_v21_exists():
    """Test that orchestrator-v2.md exists."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    assert agent_path.exists(), "Missing agents/orchestrator-v2.md"


def test_orchestrator_version():
    """Test that orchestrator-v2 agent has required identity markers."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    assert agent_path.exists(), "File not found"

    content = agent_path.read_text()

    # Verify the agent identifies as orchestrator v2
    assert "orchestrator-v2" in content.lower() or "Orchestrator v2" in content, \
        "Agent file missing orchestrator v2 identity"
    assert "name: orchestrator-v2" in content, \
        "Agent frontmatter missing name: orchestrator-v2"


def test_behavior_7_mode_aware():
    """Test BEHAVIOR 7: Mode-Aware Execution exists."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    assert agent_path.exists(), "File not found"

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
    assert not missing, f"Missing: {', '.join(missing)}"


def test_behavior_8_context_tracking():
    """Test BEHAVIOR 8: Improved Context Tracking exists."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    assert agent_path.exists(), "File not found"

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
    assert not missing, f"Missing: {', '.join(missing)}"


def test_behavior_9_timeline():
    """Test BEHAVIOR 9: Timeline View exists."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    assert agent_path.exists(), "File not found"

    content = agent_path.read_text()

    required_elements = [
        "BEHAVIOR 9",
        "Timeline View",
        "EXECUTION TIMELINE",
        "ETA",
        "timeline"
    ]

    missing = [elem for elem in required_elements if elem not in content]
    assert not missing, f"Missing: {', '.join(missing)}"


def test_new_control_commands():
    """Test that new control commands are documented."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    assert agent_path.exists(), "File not found"

    content = agent_path.read_text()

    new_commands = ["timeline", "budget", "mode", "continue"]
    missing = [cmd for cmd in new_commands if f"`{cmd}`" not in content]
    assert not missing, f"Missing commands: {', '.join(missing)}"


def test_mode_configuration_table():
    """Test that mode configuration table is complete."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    assert agent_path.exists(), "File not found"

    content = agent_path.read_text()

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

    assert not issues, f"Issues: {', '.join(issues)}"


# ─── Orchestrate Command Tests ───────────────────────────────────────────────


def test_orchestrate_command_exists():
    """Test that orchestrate.md command exists."""
    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    assert cmd_path.exists(), "Missing commands/orchestrate.md"


def test_orchestrate_command_version():
    """Test orchestrate command exists and has required content."""
    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    assert cmd_path.exists(), "File not found"

    content = cmd_path.read_text()

    assert "name:" in content, "Command frontmatter missing name field"
    assert "orchestrate" in content.lower(), "Command missing orchestrate identity"


def test_orchestrate_mode_syntax():
    """Test that mode syntax is documented in command."""
    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    assert cmd_path.exists(), "File not found"

    content = cmd_path.read_text()

    required = [
        "<task> <mode>",
        "optimize",
        "release",
        "debug"
    ]

    missing = [r for r in required if r not in content]
    assert not missing, f"Missing: {', '.join(missing)}"


def test_orchestrate_new_subcommands():
    """Test that new subcommands are documented."""
    cmd_path = PLUGIN_DIR / "commands" / "orchestrate.md"
    assert cmd_path.exists(), "File not found"

    content = cmd_path.read_text()

    subcommands = ["timeline", "budget", "continue", "status", "compress", "abort"]
    missing = [sc for sc in subcommands if sc not in content]
    assert not missing, f"Missing: {', '.join(missing)}"


# ─── README Tests ────────────────────────────────────────────────────────────


def test_readme_version():
    """Test that README shows v1.4.0-dev."""
    readme_path = PLUGIN_DIR / "README.md"
    assert readme_path.exists(), "File not found"

    content = readme_path.read_text()

    if "1.4.0" not in content:
        version_match = re.search(r"Version:\*\*\s*([\d.]+)", content)
        actual = version_match.group(1) if version_match else "unknown"
        assert False, f"Expected 1.4.0, found {actual}"


def test_readme_orchestrator_v2():
    """Test that README documents orchestrator-v2."""
    readme_path = PLUGIN_DIR / "README.md"
    assert readme_path.exists(), "File not found"

    content = readme_path.read_text()

    required = [
        "orchestrator-v2",
        "Mode-aware",
        "context tracking",
        "timeline"
    ]

    missing = [r for r in required if r.lower() not in content.lower()]
    assert not missing, f"Missing: {', '.join(missing)}"


def test_readme_7_agents():
    """Test that README shows 7 agents."""
    readme_path = PLUGIN_DIR / "README.md"
    assert readme_path.exists(), "File not found"

    content = readme_path.read_text()

    if "Agents (7)" not in content:
        count_match = re.search(r"Agents \((\d+)\)", content)
        actual = count_match.group(1) if count_match else "unknown"
        assert False, f"Expected 7 agents, found {actual}"


# ─── ROADMAP Tests ───────────────────────────────────────────────────────────


def test_roadmap_orchestrator_enhancements():
    """Test that ROADMAP includes orchestrator enhancements."""
    roadmap_path = PLUGIN_DIR / "ROADMAP.md"
    assert roadmap_path.exists(), "File not found"

    content = roadmap_path.read_text()

    required = [
        "Orchestrator v2.1 Enhancement",
        "Mode Integration",
        "Context Tracking",
        "Timeline View"
    ]

    missing = [r for r in required if r not in content]
    assert not missing, f"Missing: {', '.join(missing)}"
