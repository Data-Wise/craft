#!/usr/bin/env python3
"""
Test Suite for Hub v2.0 Layer 3 - Command Detail View
======================================================
Validates command lookup, tutorial generation, and detail display.

Run with: python tests/test_hub_layer3.py
"""

import sys
from pathlib import Path

import pytest

# Add plugin directory to path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

# Import discovery engine
from commands._discovery import (
    get_command_detail,
    generate_command_tutorial,
    get_command_stats
)

pytestmark = [pytest.mark.integration, pytest.mark.hub]


# ─── Layer 3 Tests ───────────────────────────────────────────────────────────


def test_get_command_detail_exact_match():
    """Test getting command detail with exact match."""
    # Test with exact command name
    command = get_command_detail('code:lint')

    assert command, "Failed to find 'code:lint' command"

    # Verify required fields
    required_fields = ['name', 'category', 'description', 'file']
    missing = [f for f in required_fields if f not in command]
    assert not missing, f"Missing fields: {missing}"

    # Verify data
    assert command['name'] == 'code:lint', \
        f"Wrong name: {command['name']} != 'code:lint'"
    assert command['category'] == 'code', \
        f"Wrong category: {command['category']} != 'code'"


def test_get_command_detail_not_found():
    """Test handling of non-existent command."""
    command = get_command_detail('nonexistent:command')

    assert command is None, \
        f"Expected None, got command: {command.get('name') if command else None}"


def test_get_command_detail_all_categories():
    """Test get_command_detail for commands across all categories."""
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

    assert not errors, f"Errors: {'; '.join(errors)}"


def test_generate_command_tutorial_basic():
    """Test generating basic tutorial for a command."""
    # Get a command
    command = get_command_detail('code:lint')
    assert command, "Failed to find test command"

    # Generate tutorial
    tutorial = generate_command_tutorial(command)

    # Verify tutorial has content
    assert tutorial and len(tutorial) >= 100, \
        f"Tutorial too short: {len(tutorial) if tutorial else 0} chars"

    # Verify contains key sections
    required_sections = [
        '📚 COMMAND:',
        'DESCRIPTION',
        'BASIC USAGE',
        'Back to',
        'Back to Hub'
    ]

    missing = [s for s in required_sections if s not in tutorial]
    assert not missing, f"Missing sections: {missing}"


def test_generate_command_tutorial_with_modes():
    """Test tutorial generation for command with modes."""
    # Get a command with modes
    command = get_command_detail('code:lint')
    assert command, "Failed to find test command"

    # Generate tutorial
    tutorial = generate_command_tutorial(command)

    # If command has modes, tutorial should show them
    if command.get('modes'):
        assert 'MODES' in tutorial, \
            "Command has modes but tutorial doesn't show MODES section"

        # Check for mode names
        modes_shown = sum(1 for mode in command['modes'] if mode in tutorial)
        assert modes_shown > 0, \
            "MODES section present but no mode names found"


def test_generate_tutorial_multiple_commands():
    """Test generating tutorials for multiple commands."""
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

    assert not errors, \
        f"Errors: {'; '.join(errors[:3])}{'...' if len(errors) > 3 else ''}"


def test_layer3_display_format():
    """Test that tutorial display follows correct format."""
    command = get_command_detail('code:lint')
    assert command, "Failed to find test command"

    tutorial = generate_command_tutorial(command)

    # Verify box drawing characters (ASCII art border)
    assert tutorial.startswith('┌'), \
        "Tutorial doesn't start with box border"

    assert tutorial.endswith('┘'), \
        "Tutorial doesn't end with box border"

    # Count lines
    lines = tutorial.split('\n')
    assert len(lines) >= 10, f"Tutorial too short: {len(lines)} lines"

    # Verify navigation footer exists
    footer_found = False
    for line in lines[-5:]:  # Check last 5 lines
        if 'Back to' in line or 'Hub' in line:
            footer_found = True
            break

    assert footer_found, "Navigation footer not found"


def test_related_commands_lookup():
    """Test that related commands are looked up correctly."""
    command = get_command_detail('code:lint')
    assert command, "Failed to find test command"

    tutorial = generate_command_tutorial(command)

    # If command has related_commands, they should appear in tutorial
    related = command.get('related_commands', [])

    if related:
        # Check if RELATED COMMANDS section exists
        assert 'RELATED COMMANDS' in tutorial, \
            "Command has related_commands but section not in tutorial"

        # Check if at least one related command appears
        found_count = sum(1 for rel in related if rel in tutorial)
        assert found_count > 0, \
            "RELATED COMMANDS section exists but no commands found"
    else:
        # No related commands, tutorial shouldn't have section
        assert 'RELATED COMMANDS' not in tutorial, \
            "Command has no related_commands but section appears"
