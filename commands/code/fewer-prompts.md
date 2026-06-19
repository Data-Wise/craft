---
description: Install curated read-only Bash allowlist to eliminate permission prompts
category: code
arguments:
  - name: flags
    description: "Optional: --dry-run | --global | --reset"
    required: false
---

# /craft:code:fewer-prompts — Curated Bash Allowlist

Writes a craft-curated, security-reviewed read-only Bash allowlist to `.claude/settings.json`
in one shot. Eliminates permission prompts for `git status`, `git log`, `grep`, `ls`, `find .`,
`wc`, `head`, `tail`, and craft-specific read operations across all sessions.

## Flags

| Flag | Effect |
|---|---|
| _(none)_ | Write to `.claude/settings.json` in project root |
| `--dry-run` | Preview entries; no writes |
| `--global` | Write to `~/.claude/settings.json` instead |
| `--reset` | Remove craft-managed entries (undo) |

## When invoked

### Step 1: Parse flags

Check the user's invocation for `--dry-run`, `--global`, and `--reset`.
These are independent: `--dry-run` and `--reset` can combine to preview a reset.

### Step 2: Determine settings path

- Default: `.claude/settings.json` (project root — create `.claude/` dir if absent)
- `--global`: `~/.claude/settings.json`

Run: `python3 utils/allowlist_manager.py --settings-path <path> [--dry-run] [--reset]`

Print the command output verbatim.

### Step 3: Confirm and hint

After a successful default run (not dry-run, not reset), add:

```
✓ Restart Claude Code (or open a new session) for the allowlist to take effect.
  Run /craft:code:fewer-prompts --reset to undo.
```

After `--reset`:

```
✓ Craft-managed allowlist removed. Restart Claude Code for the change to take effect.
```

## What gets added

**Tier 1 — always safe:** `git status/log/diff/branch/show/shortlog/worktree list/remote -v/rev-parse`,
`ls *`, `find . *`, `grep *`, `wc *`, `head *`, `tail *`, `pwd`, `echo *`, `which *`,
`python3 --version`, `node --version`

**Tier 3 — craft-specific:** `gh pr list/view`, `gh issue list/view`, `gh run list`,
`./scripts/validate-counts.sh`, `python3 tests/test_craft_plugin.py --list`, `mkdocs build --dry-run`

**Excluded:** `cat` (Read tool handles files safely), `grep -r /`, `find /`, `gh secret list`,
arbitrary `python3 *.py`

## Tracking

Craft writes entries to both `permissions.allow` (enforcement) and a parallel `craft_allowlist`
key (ownership tracking for `--reset`). User-added entries outside `craft_allowlist` are never
touched by `--reset`.
