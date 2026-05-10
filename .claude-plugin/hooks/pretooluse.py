#!/usr/bin/env python3
"""PreToolUse hook: Warn when Write/Edit targets files outside the current worktree.

Non-blocking (stderr warning only, exit 0). Runs on every Write/Edit call.
"""

import json
import os
import subprocess
import sys


def get_git_toplevel():
    """Get the git toplevel directory for the current working directory."""
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--show-toplevel"],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            return result.stdout.strip()
    except (subprocess.TimeoutExpired, FileNotFoundError):
        pass
    return None


def main():
    # Claude Code passes the hook payload as JSON on stdin:
    #   { "session_id": "...", "tool_name": "Write",
    #     "tool_input": { "file_path": "...", "content": "..." }, "cwd": "..." }
    # See ~/.claude/hooks/branch-guard.sh:6 for the canonical contract
    # documentation. Earlier versions of this hook read CLAUDE_TOOL_NAME
    # / CLAUDE_TOOL_INPUT from os.environ — that's not the actual API,
    # so the hook silently no-op'd in production (every Write/Edit hit
    # the early return because the env vars were never set).
    try:
        payload = json.load(sys.stdin)
    except (json.JSONDecodeError, ValueError):
        return

    tool_name = payload.get("tool_name", "")

    # Only check Write and Edit operations
    if tool_name not in ("Write", "Edit"):
        return

    # Only check if we're in a worktree
    cwd = os.getcwd()
    if "/.git-worktrees/" not in cwd:
        return

    # Get the file path from tool input
    parsed = payload.get("tool_input", {}) or {}

    file_path = parsed.get("file_path", "")
    if not file_path:
        return

    # Resolve to absolute path
    file_path = os.path.abspath(file_path)

    # Get git toplevel for this worktree
    toplevel = get_git_toplevel()
    if not toplevel:
        return

    toplevel = os.path.abspath(toplevel)

    # Check if the file is inside the worktree
    if not file_path.startswith(toplevel + os.sep) and file_path != toplevel:
        print(
            f"⚠️  WARNING: Writing outside worktree",
            file=sys.stderr
        )
        print(
            f"   File:     {file_path}",
            file=sys.stderr
        )
        print(
            f"   Worktree: {toplevel}",
            file=sys.stderr
        )
        print(
            f"   Consider: cd {toplevel}",
            file=sys.stderr
        )


if __name__ == "__main__":
    main()
