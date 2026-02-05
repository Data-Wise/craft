#!/usr/bin/env python3
"""
CLAUDE.md Common Utilities

Shared functions used by multiple claude_md_* modules.
"""

import os


# ---------------------------------------------------------------------------
# Path Resolution
# ---------------------------------------------------------------------------

def resolve_claude_md_path(global_flag=False, start_dir=None):
    """Resolve the path to CLAUDE.md.

    Args:
        global_flag: If True, return ~/.claude/CLAUDE.md
        start_dir: Directory to start searching from (default: cwd)

    Returns:
        Absolute path to CLAUDE.md

    Raises:
        FileNotFoundError: If no CLAUDE.md found
    """
    if global_flag:
        path = os.path.expanduser("~/.claude/CLAUDE.md")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Global CLAUDE.md not found at {path}")
        return path

    # Walk up from start_dir to find CLAUDE.md
    search_dir = start_dir or os.getcwd()
    while True:
        candidate = os.path.join(search_dir, "CLAUDE.md")
        if os.path.exists(candidate):
            return os.path.abspath(candidate)
        parent = os.path.dirname(search_dir)
        if parent == search_dir:  # Root reached
            raise FileNotFoundError("No CLAUDE.md found in directory tree")
        search_dir = parent
