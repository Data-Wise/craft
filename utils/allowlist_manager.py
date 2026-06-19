#!/usr/bin/env python3
"""
Craft Allowlist Manager

Manages the curated read-only Bash allowlist in .claude/settings.json.
Called by /craft:code:fewer-prompts.

Usage:
    python3 utils/allowlist_manager.py --settings-path .claude/settings.json
    python3 utils/allowlist_manager.py --settings-path .claude/settings.json --dry-run
    python3 utils/allowlist_manager.py --settings-path .claude/settings.json --reset
"""

import argparse
import json
from pathlib import Path

CRAFT_ALLOWLIST_KEY = "craft_allowlist"

# Tier 1: unconditionally safe read-only operations
TIER1 = [
    "Bash(git status*)",
    "Bash(git log*)",
    "Bash(git diff*)",
    "Bash(git branch*)",
    "Bash(git show*)",
    "Bash(git shortlog*)",
    "Bash(git worktree list*)",
    "Bash(git remote -v*)",
    "Bash(git rev-parse*)",
    "Bash(ls *)",
    "Bash(find . *)",
    "Bash(grep *)",
    "Bash(wc *)",
    "Bash(head *)",
    "Bash(tail *)",
    "Bash(pwd*)",
    "Bash(echo *)",
    "Bash(which *)",
    "Bash(python3 --version*)",
    "Bash(node --version*)",
]

# Tier 3: craft-specific read-only operations
TIER3 = [
    "Bash(gh pr list*)",
    "Bash(gh issue list*)",
    "Bash(gh run list*)",
    "Bash(gh pr view*)",
    "Bash(gh issue view*)",
    "Bash(./scripts/validate-counts.sh*)",
    "Bash(python3 tests/test_craft_plugin.py --list*)",
    "Bash(mkdocs build --dry-run*)",
]

CURATED = TIER1 + TIER3


def load_settings(path: Path) -> dict:
    if path.exists():
        with open(path) as f:
            return json.load(f)
    return {}


def save_settings(path: Path, settings: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w") as f:
        json.dump(settings, f, indent=2)
        f.write("\n")


def _get_allow(settings: dict) -> list:
    return list(settings.get("permissions", {}).get("allow", []))


def _get_craft_list(settings: dict) -> list:
    return list(settings.get(CRAFT_ALLOWLIST_KEY, []))


def add_entries(settings: dict, entries: list) -> tuple:
    """Merge entries into permissions.allow and craft_allowlist. Returns (added_count, new_settings)."""
    existing_allow = _get_allow(settings)
    existing_craft = _get_craft_list(settings)

    new_entries = [e for e in entries if e not in existing_craft]

    merged_allow = existing_allow + [e for e in new_entries if e not in existing_allow]
    merged_craft = existing_craft + new_entries

    new_settings = {**settings}
    new_settings["permissions"] = {**settings.get("permissions", {}), "allow": merged_allow}
    new_settings[CRAFT_ALLOWLIST_KEY] = merged_craft

    return len(new_entries), new_settings


def reset_entries(settings: dict) -> tuple:
    """Remove craft-managed entries. Returns (removed_count, new_settings)."""
    craft_entries = set(_get_craft_list(settings))
    current_allow = _get_allow(settings)

    new_allow = [e for e in current_allow if e not in craft_entries]
    removed = len(current_allow) - len(new_allow)

    new_settings = {**settings}
    new_settings["permissions"] = {**settings.get("permissions", {}), "allow": new_allow}
    new_settings[CRAFT_ALLOWLIST_KEY] = []

    return removed, new_settings


def dry_run_output(settings: dict, entries: list) -> str:
    existing_craft = set(_get_craft_list(settings))
    tier_map = {e: "Tier 1" for e in TIER1}
    tier_map.update({e: "Tier 3" for e in TIER3})

    lines = ["Dry run — no changes will be written.", ""]
    lines.append(f"{'Entry':<50} {'Tier':<8} {'Status'}")
    lines.append("-" * 75)
    for entry in entries:
        tier = tier_map.get(entry, "?")
        status = "already present" if entry in existing_craft else "new"
        lines.append(f"{entry:<50} {tier:<8} {status}")

    new_count = sum(1 for e in entries if e not in existing_craft)
    lines.append("")
    lines.append(f"Would add {new_count} new entries to permissions.allow.")
    lines.append("Run without --dry-run to apply.")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Manage craft curated Bash allowlist")
    parser.add_argument("--settings-path", required=True, help="Path to settings.json")
    parser.add_argument("--dry-run", action="store_true", help="Preview without writing")
    parser.add_argument("--reset", action="store_true", help="Remove craft-managed entries")
    args = parser.parse_args()

    path = Path(args.settings_path)
    settings = load_settings(path)

    if args.reset:
        removed, new_settings = reset_entries(settings)
        save_settings(path, new_settings)
        print(f"Removed {removed} craft-managed entries from {path}.")
        print(f"craft_allowlist cleared. Your own entries are untouched.")
        return

    if args.dry_run:
        print(dry_run_output(settings, CURATED))
        return

    added, new_settings = add_entries(settings, CURATED)
    save_settings(path, new_settings)
    if added:
        print(f"Added {added} entries to {path}.")
    else:
        print(f"Already up to date — no new entries added to {path}.")
    print(f"Run with --reset to undo.")


if __name__ == "__main__":
    main()
