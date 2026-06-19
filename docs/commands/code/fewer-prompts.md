# /craft:code:fewer-prompts

> **Install curated read-only Bash allowlist to eliminate permission prompts**

---

## Synopsis

```bash
/craft:code:fewer-prompts [--dry-run] [--global] [--reset]
```

**Quick examples:**

```bash
# Preview what will be written
/craft:code:fewer-prompts --dry-run

# Install to project settings
/craft:code:fewer-prompts

# Install globally (all projects)
/craft:code:fewer-prompts --global

# Remove craft-managed entries
/craft:code:fewer-prompts --reset
```

---

## Description

Writes a craft-curated, security-reviewed Bash allowlist to `.claude/settings.json` in one
shot. Eliminates permission prompts for safe read-only operations — `git status/log/diff`,
`grep`, `ls`, `find .`, `wc`, `head`, `tail` — without exposing destructive commands.

Idempotent: running it twice produces identical output. Uses a `craft_allowlist` tracking
key so `--reset` removes only craft-owned entries, leaving user-added entries untouched.

---

## Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Preview entries; no writes |
| `--global` | Write to `~/.claude/settings.json` instead of project |
| `--reset` | Remove craft-managed entries (undo) |

---

## What Gets Added

**Tier 1 — always safe:**

| Pattern | Covers |
|---------|--------|
| `Bash(git status*)` | Status, branch info |
| `Bash(git log*)` | History, log formats |
| `Bash(git diff*)` | Diffs, staged changes |
| `Bash(git branch*)` | Branch listing |
| `Bash(git show*)` | Object inspection |
| `Bash(git shortlog*)` | Contribution summaries |
| `Bash(git worktree list*)` | Worktree listing |
| `Bash(git remote -v*)` | Remote listing |
| `Bash(git rev-parse*)` | Commit resolution |
| `Bash(ls *)` | Directory listing |
| `Bash(find . *)` | Project-local search |
| `Bash(grep *)` | Text search |
| `Bash(wc *)` | Line/word/byte counts |
| `Bash(head *)` | First N lines |
| `Bash(tail *)` | Last N lines |
| `Bash(pwd*)` | Working directory |
| `Bash(echo *)` | Output |
| `Bash(which *)` | Binary location |
| `Bash(python3 --version*)` | Python version |
| `Bash(node --version*)` | Node version |

**Tier 3 — craft-specific:**

| Pattern | Covers |
|---------|--------|
| `Bash(gh pr list*)` | PR listing |
| `Bash(gh issue list*)` | Issue listing |
| `Bash(gh run list*)` | CI run listing |
| `Bash(gh pr view*)` | PR detail |
| `Bash(gh issue view*)` | Issue detail |
| `Bash(./scripts/validate-counts.sh*)` | Count validation |
| `Bash(python3 tests/test_craft_plugin.py --list*)` | Test discovery |
| `Bash(mkdocs build --dry-run*)` | Docs dry-run |

**Excluded by design:** `cat` (Read tool handles files safely), `grep -r /`, `find /`,
`find ~`, `gh secret list`, arbitrary `python3 *.py`.

---

## See Also

- [Tutorial](../../tutorials/TUTORIAL-code-fewer-prompts.md) — Step-by-step walkthrough
- [/craft:code:lint](lint.md) — Code style checks
- [/craft:check](../check.md) — Pre-flight validation
