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
from pathlib import Path
from typing import Optional

import pytest

# Add utils directory to path for linkcheck_ignore_parser
sys.path.insert(0, str(Path(__file__).parent.parent / "utils"))

pytestmark = [pytest.mark.integration, pytest.mark.structure]


# ─── Plugin Structure Tests ──────────────────────────────────────────────────


def test_plugin_json_exists():
    """Test that plugin.json exists and is valid."""
    plugin_dir = Path(__file__).parent.parent
    plugin_json = plugin_dir / ".claude-plugin" / "plugin.json"

    assert plugin_json.exists(), f"Missing: {plugin_json}"

    data = json.load(open(plugin_json))

    # Check required fields
    required = ["name", "version", "description", "author"]
    missing = [f for f in required if f not in data]
    assert not missing, f"Missing fields: {missing}"

    # Check author is object
    assert isinstance(data.get("author"), dict), \
        "author must be an object with 'name' field"


def test_directory_structure():
    """Test that required directories exist."""
    plugin_dir = Path(__file__).parent.parent
    required_dirs = ["commands", "skills", "agents", ".claude-plugin"]

    missing = []
    for d in required_dirs:
        if not (plugin_dir / d).is_dir():
            missing.append(d)

    assert not missing, f"Missing directories: {missing}"


def test_readme_exists():
    """Test that README.md exists."""
    plugin_dir = Path(__file__).parent.parent
    readme = plugin_dir / "README.md"

    assert readme.exists(), "Missing README.md"


# ─── Command Tests ───────────────────────────────────────────────────────────


def find_all_commands() -> list[Path]:
    """Find all command markdown files."""
    plugin_dir = Path(__file__).parent.parent
    commands_dir = plugin_dir / "commands"
    return list(commands_dir.rglob("*.md"))


def test_command_count():
    """Test that we have expected number of commands."""
    commands = find_all_commands()

    # We expect at least 15 commands based on the structure
    min_expected = 15

    assert len(commands) >= min_expected, \
        f"Found {len(commands)} commands, expected at least {min_expected}"


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


def test_all_commands_valid():
    """Test that all command files are valid."""
    commands = find_all_commands()
    invalid = []

    for cmd in commands:
        valid, msg = validate_command_file(cmd)
        if not valid:
            relative = cmd.relative_to(Path(__file__).parent.parent)
            invalid.append(f"{relative}: {msg}")

    assert not invalid, \
        f"Invalid commands: {invalid[:3]}{'...' if len(invalid) > 3 else ''}"


def test_command_categories():
    """Test that commands are organized in categories."""
    plugin_dir = Path(__file__).parent.parent
    commands_dir = plugin_dir / "commands"

    # Expected categories
    expected = ["code", "docs", "git", "site"]
    missing = []

    for cat in expected:
        cat_dir = commands_dir / cat
        if not cat_dir.is_dir():
            missing.append(cat)

    assert not missing, f"Missing categories: {missing}"


def test_hub_command_exists():
    """Test that the main hub command exists."""
    plugin_dir = Path(__file__).parent.parent
    hub = plugin_dir / "commands" / "hub.md"

    assert hub.exists(), "Missing commands/hub.md"


# ─── Skills Tests ────────────────────────────────────────────────────────────


def find_all_skills() -> list[Path]:
    """Find all skill markdown files."""
    plugin_dir = Path(__file__).parent.parent
    skills_dir = plugin_dir / "skills"
    return list(skills_dir.rglob("*.md"))


def test_skills_exist():
    """Test that skills are defined."""
    skills = find_all_skills()

    assert len(skills) > 0, "No skills found"


def test_design_skills():
    """Test that design skills are present."""
    plugin_dir = Path(__file__).parent.parent
    design_dir = plugin_dir / "skills" / "design"

    expected = ["backend-designer.md", "frontend-designer.md", "devops-helper.md"]
    missing = []

    for skill in expected:
        if not (design_dir / skill).exists():
            missing.append(skill)

    assert not missing, f"Missing: {missing}"


# ─── Agents Tests ────────────────────────────────────────────────────────────


def find_all_agents() -> list[Path]:
    """Find all agent markdown files."""
    plugin_dir = Path(__file__).parent.parent
    agents_dir = plugin_dir / "agents"
    return list(agents_dir.rglob("*.md"))


def test_agents_exist():
    """Test that agents are defined."""
    agents = find_all_agents()

    assert len(agents) > 0, "No agents found"


def test_orchestrator_agent():
    """Test that the orchestrator agent exists."""
    plugin_dir = Path(__file__).parent.parent
    orchestrator = plugin_dir / "agents" / "orchestrator.md"

    assert orchestrator.exists(), "Missing agents/orchestrator.md"


# ─── Integration Tests ───────────────────────────────────────────────────────


def test_no_broken_links():
    """Test for broken internal links in markdown files.

    NOTE: docs/test-violations.md is intentionally excluded from this test.
    That file contains broken links used to test the .linkcheck-ignore parser
    and link validation system. See .linkcheck-ignore for the list of expected
    broken links.

    Uses .linkcheck-ignore file to filter out documented/expected broken links.
    """
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

    assert not broken, \
        f"Broken links: {broken[:3]}{'...' if len(broken) > 3 else ''}"


def test_consistent_naming():
    """Test that files follow naming conventions."""
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

    assert not bad_names, f"Non-kebab-case names: {bad_names[:3]}"
