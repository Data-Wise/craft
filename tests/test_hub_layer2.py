#!/usr/bin/env python3
"""
Test Suite for Hub v2.0 Layer 2 - Category View
================================================
Validates category navigation, command grouping, and display generation.

Run with: python tests/test_hub_layer2.py
"""

import sys
from pathlib import Path

import pytest

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

pytestmark = [pytest.mark.integration, pytest.mark.hub]


# ─── Layer 2 Tests ───────────────────────────────────────────────────────────


def test_get_commands_by_category():
    """Test filtering commands by category."""
    stats = get_command_stats()
    expected_code_count = stats['categories'].get('code', 0)
    code_commands = get_commands_by_category('code')

    assert len(code_commands) == expected_code_count, \
        f"Expected {expected_code_count} code commands, found {len(code_commands)}"

    # Verify all commands are in 'code' category
    non_code = [cmd for cmd in code_commands if cmd['category'] != 'code']
    assert not non_code, \
        f"Found {len(non_code)} commands not in 'code' category"


def test_all_categories_have_commands():
    """Test that all expected categories return commands."""
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

    assert not errors, f"Mismatches: {'; '.join(errors)}"


def test_group_commands_by_subcategory():
    """Test grouping commands by subcategory."""
    # Get code commands and group by subcategory
    code_commands = get_commands_by_category('code')
    grouped = group_commands_by_subcategory(code_commands)

    # Should have at least 'general' group
    assert grouped, "No groups created"

    # Verify all commands are in a group
    total_in_groups = sum(len(cmds) for cmds in grouped.values())
    assert total_in_groups == len(code_commands), \
        f"Lost commands: {len(code_commands)} total, {total_in_groups} in groups"


def test_get_category_info():
    """Test getting complete category information."""
    info = get_category_info('code')

    # Verify required fields
    required_fields = ['name', 'count', 'commands', 'subcategories', 'icon']
    missing = [f for f in required_fields if f not in info]
    assert not missing, f"Missing fields: {missing}"

    # Verify data
    stats = get_command_stats()
    expected_code_count = stats['categories'].get('code', 0)
    assert info['name'] == 'code', f"Wrong name: {info['name']} != 'code'"
    assert info['count'] == expected_code_count, f"Wrong count: {info['count']} != {expected_code_count}"
    assert info['icon'], "Missing icon"


def test_category_info_all_categories():
    """Test get_category_info for all categories."""
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

    assert not errors, \
        f"Errors: {'; '.join(errors[:3])}{'...' if len(errors) > 3 else ''}"


def test_invalid_category():
    """Test handling of invalid category."""
    # Test with non-existent category
    commands = get_commands_by_category('nonexistent')

    # Should return empty list, not error
    assert commands == [], \
        f"Expected empty list, got {len(commands)} commands"

    # Test get_category_info with invalid category
    info = get_category_info('nonexistent')

    assert info['count'] == 0, \
        f"Expected count=0, got {info['count']}"


def test_layer2_display_generation():
    """Test generating Layer 2 display for a category."""
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

    # Verify display was generated
    assert display and len(lines) >= 5, "Failed to generate display"

    # Verify all commands appear
    assert cmd_num - 1 == info['count'], \
        f"Display shows {cmd_num - 1} commands, expected {info['count']}"
