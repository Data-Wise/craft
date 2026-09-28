---
name: craft-restore
description: Restore project context after a break. Use when the user asks where they left off, requests a repository recap, or wants the current status and next action.
---

Restore the current repository's working context. This operation is read-only.

1. Read the repository's AGENTS.md and .STATUS when present. Treat project instructions as authoritative for repository-specific workflow.
2. Inspect the current branch and working tree, recent commits from the last 48 hours, and unpushed local commits when the repository's upstream is available.
3. If gh is installed and authenticated, check open pull requests and assigned open issues. If it is unavailable, report that rather than guessing.
4. Combine overlapping Git facts into one short section. Keep project status, blockers, and planning-file context in a separate section.
5. End with the next action from .STATUS, or identify the most direct next step if no status file exists.

Do not edit files, stage changes, commit, push, or synchronize external state during restore. Do not assume Obsidian, Claude, or Craft-specific commands are installed.
