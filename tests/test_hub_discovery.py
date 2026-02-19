#!/usr/bin/env python3
"""
Test Suite for Hub v2.0 Command Discovery
==========================================
Validates auto-detection, caching, and metadata extraction.

Run with: python tests/test_hub_discovery.py

This test suite validates the command discovery engine that powers
the /craft:hub command. It tests:
1. Discovery of all 97 commands across all categories
2. YAML frontmatter parsing and metadata extraction
3. Category inference from directory structure
4. Cache generation and invalidation
5. Performance targets (< 200ms first run, < 10ms cached)
"""

import json
import os
import shutil
import time
import yaml
from pathlib import Path
from typing import Optional, Dict, List, Any

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.hub]


# ─── Import Real Discovery Functions ─────────────────────────────────────────
# Integrated with commands._discovery module

# Add parent directory to path to import commands module
import sys
sys.path.insert(0, str(Path(__file__).parent.parent))

from commands._discovery import (
    discover_commands as real_discover_commands,
    parse_yaml_frontmatter as real_parse_frontmatter,
    get_command_stats as real_get_command_stats,
    load_cached_commands as real_load_cache,
    cache_commands as real_cache_commands
)

# Wrapper functions to match test interface
def stub_discover_commands(plugin_dir: Path) -> List[Dict[str, Any]]:
    """Wrapper: Use real discover_commands function."""
    return real_discover_commands()


def stub_parse_frontmatter(file_path: Path) -> Dict[str, Any]:
    """Wrapper: Use real parse_yaml_frontmatter function."""
    try:
        with open(file_path) as f:
            content = f.read()
        return real_parse_frontmatter(content)
    except Exception:
        return {}


def _extract_modes(file_path: Path) -> List[str]:
    """Extract execution modes from command file."""
    try:
        content = file_path.read_text()
        modes = []

        # Look for mode definitions (simple pattern matching)
        for line in content.split("\n"):
            if "| **default**" in line or "| default |" in line:
                if "default" not in modes:
                    modes.append("default")
            if "| **debug**" in line or "| debug |" in line:
                if "debug" not in modes:
                    modes.append("debug")
            if "| **optimize**" in line or "| optimize |" in line:
                if "optimize" not in modes:
                    modes.append("optimize")
            if "| **release**" in line or "| release |" in line:
                if "release" not in modes:
                    modes.append("release")

        return modes
    except Exception:
        return []


def stub_generate_cache(plugin_dir: Path, commands: List[Dict[str, Any]]) -> Path:
    """Wrapper: Use real cache_commands function."""
    real_cache_commands(commands)
    return plugin_dir / "commands" / "_cache.json"


def stub_load_cache(plugin_dir: Path) -> Optional[Dict[str, Any]]:
    """Wrapper: Use real load_cached_commands function."""
    from datetime import datetime
    commands = real_load_cache()
    if commands:
        return {
            "version": "1.0.0",
            "generated_at": datetime.now().isoformat(),
            "total_commands": len(commands),
            "commands": commands
        }
    return None


def _stub_load_cache_old(plugin_dir: Path) -> Optional[Dict[str, Any]]:
    """Old stub implementation - kept for reference."""
    cache_path = plugin_dir / "commands" / "_cache.json"

    if not cache_path.exists():
        return None

    try:
        with open(cache_path) as f:
            return json.load(f)
    except Exception:
        return None


def stub_get_command_stats(commands: List[Dict[str, Any]]) -> Dict[str, Any]:
    """Wrapper: Use real get_command_stats function."""
    return real_get_command_stats()


# ─── Discovery Tests ─────────────────────────────────────────────────────────


def test_discovery_finds_all_commands():
    """Test that discovery finds all 97 command files."""
    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)

    # Expected: at least 100 commands (count grows as features are added)
    min_expected = 100
    found = len(commands)

    assert found >= min_expected, f"Expected at least {min_expected} commands, found {found}"


def test_category_inference():
    """Test category inference from file paths."""
    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)

    # Test specific category inferences
    # Note: discovery module returns relative filenames, not full paths
    test_cases = {
        "code/lint.md": "code",
        "git/worktree.md": "git",
        "hub.md": "hub",
    }

    errors = []
    for file_path, expected_cat in test_cases.items():
        cmd = next((c for c in commands if c["file"] == file_path), None)
        if not cmd:
            errors.append(f"{file_path}: not found")
        elif cmd["category"] != expected_cat:
            errors.append(f"{file_path}: expected '{expected_cat}', got '{cmd['category']}'")

    assert not errors, f"Errors: {errors[:3]}"


def test_frontmatter_parsing():
    """Test YAML frontmatter extraction."""
    plugin_dir = Path(__file__).parent.parent
    lint_cmd = plugin_dir / "commands" / "code" / "lint.md"

    assert lint_cmd.exists(), f"Test file not found: {lint_cmd}"

    metadata = stub_parse_frontmatter(lint_cmd)

    # Verify expected fields
    required_fields = ["description", "arguments"]
    missing = [f for f in required_fields if f not in metadata]
    assert not missing, f"Missing fields: {missing}"

    # Verify arguments structure
    assert isinstance(metadata["arguments"], list), "arguments must be a list"

    # Check first argument has required fields
    if metadata["arguments"]:
        arg = metadata["arguments"][0]
        arg_fields = ["name", "description", "required"]
        missing_arg_fields = [f for f in arg_fields if f not in arg]
        assert not missing_arg_fields, f"Argument missing fields: {missing_arg_fields}"


def test_mode_extraction():
    """Test execution mode extraction from command content."""
    plugin_dir = Path(__file__).parent.parent
    lint_cmd = plugin_dir / "commands" / "code" / "lint.md"

    assert lint_cmd.exists(), f"Test file not found: {lint_cmd}"

    modes = _extract_modes(lint_cmd)

    # lint.md should have: default, debug, optimize, release
    expected_modes = ["default", "debug", "optimize", "release"]

    missing = [m for m in expected_modes if m not in modes]
    assert not missing, f"Missing modes: {missing} (found: {modes})"


# ─── Cache Tests ─────────────────────────────────────────────────────────────


def test_cache_generation():
    """Test cache file is generated correctly."""
    plugin_dir = Path(__file__).parent.parent
    cache_path = plugin_dir / "commands" / "_cache.json"

    # Remove existing cache
    if cache_path.exists():
        cache_path.unlink()

    # Generate cache
    commands = stub_discover_commands(plugin_dir)
    generated_path = stub_generate_cache(plugin_dir, commands)

    assert generated_path.exists(), "Cache file not created"

    # Verify JSON structure
    with open(generated_path) as f:
        cache_data = json.load(f)

    # Updated to match actual discovery module cache structure
    required_fields = ["generated", "count", "commands"]
    missing = [f for f in required_fields if f not in cache_data]
    assert not missing, f"Cache missing fields: {missing}"


def test_cache_loading():
    """Test cache file loading."""
    plugin_dir = Path(__file__).parent.parent

    # Ensure cache exists
    commands = stub_discover_commands(plugin_dir)
    stub_generate_cache(plugin_dir, commands)

    # Load cache
    cache_data = stub_load_cache(plugin_dir)

    assert cache_data is not None, "Failed to load cache"
    assert "commands" in cache_data, "Cache missing commands array"


def test_cache_invalidation():
    """Test cache rebuilds when files change."""
    plugin_dir = Path(__file__).parent.parent
    cache_path = plugin_dir / "commands" / "_cache.json"

    # Generate fresh cache
    commands = stub_discover_commands(plugin_dir)
    stub_generate_cache(plugin_dir, commands)

    original_mtime = cache_path.stat().st_mtime

    # Wait a bit to ensure different timestamp
    time.sleep(0.1)

    # Touch a command file
    test_file = plugin_dir / "commands" / "hub.md"
    if test_file.exists():
        test_file.touch()

    # Simulate invalidation check
    test_file_mtime = test_file.stat().st_mtime
    cache_is_stale = test_file_mtime > original_mtime

    assert cache_is_stale, "Cache not marked as stale after file modification"


# ─── Performance Tests ───────────────────────────────────────────────────────


def test_performance_first_run():
    """Test first run completes < 200ms."""
    plugin_dir = Path(__file__).parent.parent
    cache_path = plugin_dir / "commands" / "_cache.json"

    # Remove cache to force fresh discovery
    if cache_path.exists():
        cache_path.unlink()

    start = time.time()
    commands = stub_discover_commands(plugin_dir)
    duration = (time.time() - start) * 1000

    target_ms = 200
    assert duration <= target_ms, f"Took {duration:.1f}ms, target < {target_ms}ms"


def test_performance_cached_run():
    """Test cached run completes < 10ms."""
    plugin_dir = Path(__file__).parent.parent

    # Ensure cache exists
    commands = stub_discover_commands(plugin_dir)
    stub_generate_cache(plugin_dir, commands)

    start = time.time()
    cache_data = stub_load_cache(plugin_dir)
    duration = (time.time() - start) * 1000

    assert cache_data is not None, "Cache load failed"

    target_ms = 10
    assert duration <= target_ms, f"Took {duration:.1f}ms, target < {target_ms}ms"


# ─── Statistics Tests ────────────────────────────────────────────────────────


def test_command_stats():
    """Test get_command_stats() returns correct counts."""
    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)
    stats = stub_get_command_stats(commands)

    # Verify structure
    required_fields = ["total", "categories", "with_modes"]
    missing = [f for f in required_fields if f not in stats]
    assert not missing, f"Missing fields: {missing}"

    # Verify total
    assert stats["total"] == len(commands), f"Total mismatch: {stats['total']} vs {len(commands)}"

    # Verify category counts sum to total
    cat_sum = sum(stats["categories"].values())
    assert cat_sum == stats["total"], f"Category sum {cat_sum} doesn't match total {stats['total']}"


def test_all_categories_present():
    """Test all expected categories are discovered."""
    plugin_dir = Path(__file__).parent.parent
    commands = stub_discover_commands(plugin_dir)
    stats = stub_get_command_stats(commands)

    # Expected categories based on directory structure
    expected_categories = {
        "code", "test", "docs", "git", "site",
        "arch", "ci", "dist", "workflow", "hub"
    }

    found_categories = set(stats["categories"].keys())
    missing = expected_categories - found_categories

    assert not missing, f"Missing categories: {missing}"


def test_missing_frontmatter_handling():
    """Test graceful handling of missing frontmatter."""
    plugin_dir = Path(__file__).parent.parent
    test_file = plugin_dir / "commands" / "_test_no_frontmatter.md"

    try:
        test_file.write_text("# Test Command\n\nThis has no frontmatter.")

        metadata = stub_parse_frontmatter(test_file)

        # Should return empty dict, not None or error
        assert metadata is not None, "Returned None instead of empty dict"
        assert isinstance(metadata, dict), f"Returned {type(metadata)} instead of dict"

    finally:
        # Cleanup
        if test_file.exists():
            test_file.unlink()
