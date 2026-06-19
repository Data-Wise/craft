#!/usr/bin/env python3
"""
Tests for /craft:code:fewer-prompts — curated read-only Bash allowlist command.

Tests the utils/allowlist_manager.py utility that the command calls.
Run with: python3 -m pytest tests/test_fewer_prompts.py -v
"""

import json
import subprocess
import sys
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit]

PLUGIN_DIR = Path(__file__).parent.parent
UTILITY = PLUGIN_DIR / "utils" / "allowlist_manager.py"


def run_utility(settings_path, *flags):
    """Run allowlist_manager.py with given flags; return (returncode, stdout, stderr)."""
    cmd = [sys.executable, str(UTILITY), "--settings-path", str(settings_path)] + list(flags)
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.returncode, result.stdout, result.stderr


def load_settings(path):
    with open(path) as f:
        return json.load(f)


# ─── Utility existence ────────────────────────────────────────────────────────


def test_utility_exists():
    assert UTILITY.exists(), f"Missing: {UTILITY}"


# ─── Dry-run ──────────────────────────────────────────────────────────────────


def test_dry_run_does_not_create_settings_file(tmp_path):
    settings_path = tmp_path / ".claude" / "settings.json"
    rc, out, err = run_utility(settings_path, "--dry-run")
    assert rc == 0, err
    assert not settings_path.exists(), "--dry-run must not write the settings file"


def test_dry_run_shows_tier1_entries(tmp_path):
    settings_path = tmp_path / "settings.json"
    rc, out, _ = run_utility(settings_path, "--dry-run")
    assert rc == 0
    assert "git status" in out
    assert "git log" in out
    assert "grep" in out
    assert "find ." in out


def test_dry_run_shows_tier3_entries(tmp_path):
    settings_path = tmp_path / "settings.json"
    rc, out, _ = run_utility(settings_path, "--dry-run")
    assert rc == 0
    assert "gh pr list" in out
    assert "validate-counts" in out


# ─── Default run ──────────────────────────────────────────────────────────────


def test_default_writes_permissions_allow(tmp_path):
    settings_path = tmp_path / "settings.json"
    rc, _, err = run_utility(settings_path)
    assert rc == 0, err
    settings = load_settings(settings_path)
    allow = settings.get("permissions", {}).get("allow", [])
    assert any("git status" in e for e in allow)
    assert any("git log" in e for e in allow)
    assert any("grep" in e for e in allow)


def test_default_writes_craft_allowlist(tmp_path):
    settings_path = tmp_path / "settings.json"
    rc, _, err = run_utility(settings_path)
    assert rc == 0, err
    settings = load_settings(settings_path)
    assert "craft_allowlist" in settings
    assert len(settings["craft_allowlist"]) > 0


def test_permissions_allow_and_craft_allowlist_match(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    settings = load_settings(settings_path)
    craft = set(settings["craft_allowlist"])
    allow = set(settings["permissions"]["allow"])
    assert craft.issubset(allow), "All craft_allowlist entries must be in permissions.allow"


def test_preserves_existing_user_entries(tmp_path):
    settings_path = tmp_path / "settings.json"
    existing = {"permissions": {"allow": ["Bash(mkdocs build:*)", "Bash(git restore:*)"]}}
    settings_path.write_text(json.dumps(existing))

    run_utility(settings_path)
    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert "Bash(mkdocs build:*)" in allow
    assert "Bash(git restore:*)" in allow


# ─── Idempotency ──────────────────────────────────────────────────────────────


def test_idempotent(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    settings_after_first = load_settings(settings_path)

    run_utility(settings_path)
    settings_after_second = load_settings(settings_path)

    assert settings_after_first == settings_after_second, "Running twice must produce identical settings"


def test_no_duplicate_entries_after_double_run(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    run_utility(settings_path)
    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert len(allow) == len(set(allow)), "Duplicate entries found in permissions.allow"


# ─── Reset ────────────────────────────────────────────────────────────────────


def test_reset_removes_craft_entries(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)

    rc, _, err = run_utility(settings_path, "--reset")
    assert rc == 0, err

    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert not any("git status" in e for e in allow)
    assert not any("git log" in e for e in allow)


def test_reset_clears_craft_allowlist(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    run_utility(settings_path, "--reset")
    settings = load_settings(settings_path)
    assert settings.get("craft_allowlist", []) == []


def test_reset_preserves_user_entries(tmp_path):
    settings_path = tmp_path / "settings.json"
    existing = {"permissions": {"allow": ["Bash(mkdocs build:*)", "Bash(git restore:*)"]}}
    settings_path.write_text(json.dumps(existing))

    run_utility(settings_path)
    run_utility(settings_path, "--reset")

    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert "Bash(mkdocs build:*)" in allow, "User entry must survive --reset"
    assert "Bash(git restore:*)" in allow, "User entry must survive --reset"


def test_reset_then_readd_restores_full_set(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    original = load_settings(settings_path)

    run_utility(settings_path, "--reset")
    run_utility(settings_path)
    restored = load_settings(settings_path)

    assert set(original["permissions"]["allow"]) == set(restored["permissions"]["allow"])
    assert set(original["craft_allowlist"]) == set(restored["craft_allowlist"])


# ─── Security: excluded patterns ─────────────────────────────────────────────


def test_cat_not_in_allowlist(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert not any(e.lower().startswith("bash(cat") for e in allow), \
        "cat must not appear in the allowlist"


def test_grep_r_slash_not_in_allowlist(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert not any("grep -r /" in e for e in allow)
    assert not any("grep -r ~" in e for e in allow)


def test_find_slash_not_in_allowlist(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert not any("find /" in e for e in allow)
    assert not any("find ~" in e for e in allow)


def test_gh_secret_list_not_in_allowlist(tmp_path):
    settings_path = tmp_path / "settings.json"
    run_utility(settings_path)
    settings = load_settings(settings_path)
    allow = settings["permissions"]["allow"]
    assert not any("secret" in e for e in allow)
