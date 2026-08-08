---
title: "Troubleshooting: CLAUDE.md Out of Sync"
description: "Fix outdated command counts, missing features, or stale versions in CLAUDE.md"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - ../../reference/REFCARD-CLAUDE-MD.md
---

# Troubleshooting: CLAUDE.md Out of Sync

> **Note (v4 consolidation):** `/craft:docs:claude-md:sync` was folded into the `claude-md-lifecycle` skill — the command itself no longer exists. Replace any `/craft:docs:claude-md:sync` example below with a natural request (e.g. "sync CLAUDE.md") and the skill runs the same detect → audit → fix → optimize pipeline. See [`skills/docs/claude-md/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/docs/claude-md/SKILL.md) for the current reference.

**Level:** Beginner

## Problem

Your `CLAUDE.md` contains outdated information -- wrong command counts, missing features, or stale version numbers:

```markdown
# Example of stale CLAUDE.md header
**115 commands** · **45 skills** · **8 agents**
**Current Version:** v2.61.0
```

When the project is actually at v2.61.0 with 115 commands, 45 skills, and 8 agents.

## Common Causes & Solutions

### 1. New Commands Added Without Syncing

**Issue:** Commands were added to `commands/` but CLAUDE.md was not updated.

**Solution:**

```text
Ask: "sync CLAUDE.md"
```

This runs the 4-phase pipeline: **detect** (scan project metrics) -> **audit** (compare against CLAUDE.md) -> **fix** (update stale values) -> **optimize** (enforce line budget and section priorities).

**Why:** CLAUDE.md references project metrics that change with every feature addition.

### 2. Version Bumped Without Sync

**Issue:** A release was tagged but CLAUDE.md still shows the old version.

**Solution:**

```bash
# Ask "sync CLAUDE.md", then:
grep "Current Version" CLAUDE.md   # verify fix
```

**Why:** The sync pipeline extracts the version from git tags and `CHANGELOG.md`, then updates the CLAUDE.md header.

### 3. Manual Edits That Drifted

**Issue:** Hand edits introduced inconsistencies -- duplicate sections, wrong counts, or broken links.

**Solution:**

```text
Ask: "sync CLAUDE.md"
# Watch for optimizer warnings about bloated or duplicate sections
```

**Why:** The optimizer classifies sections by priority (P0/P1/P2) and flags sections that push the file over budget.

### 4. File Exceeds Line Budget

**Issue:** CLAUDE.md has grown beyond the recommended size, slowing down Claude's parsing.

**Solution:**

```bash
wc -l CLAUDE.md                          # check current size
# Ask "sync CLAUDE.md" — optimizer trims low-priority content
bash scripts/claude-md-budget-check.sh   # pre-commit budget check
```

**Why:** CLAUDE.md is read at the start of every conversation. Lean files (< 150 lines for new projects) improve response quality and reduce token usage.

## Verification Steps

```bash
./scripts/validate-counts.sh             # verify command count matches reality
# Ask "sync CLAUDE.md" — should report "0 issues found"
bash scripts/claude-md-budget-check.sh   # should pass without warnings
```

## Related

- `skills/docs/claude-md/` -- init, sync, and edit folded into this skill (v4 consolidation)
- [CLAUDE.md Quick Reference](../../reference/REFCARD-CLAUDE-MD.md) -- Cheat sheet for CLAUDE.md management
