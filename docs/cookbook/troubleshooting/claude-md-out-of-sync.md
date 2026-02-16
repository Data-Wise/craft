---
title: "Troubleshooting: CLAUDE.md Out of Sync"
description: "Fix outdated command counts, missing features, or stale versions in CLAUDE.md"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - ../../commands/docs/claude-md.md
  - ../../reference/REFCARD-CLAUDE-MD.md
---

# Troubleshooting: CLAUDE.md Out of Sync

**Level:** Beginner

## Problem

Your `CLAUDE.md` contains outdated information -- wrong command counts, missing features, or stale version numbers:

```markdown
# Example of stale CLAUDE.md header
**94 commands** · **18 skills** · **6 agents**
**Current Version:** v2.8.0
```

When the project is actually at v2.18.0 with 110 commands, 25 skills, and 8 agents.

## Common Causes & Solutions

### 1. New Commands Added Without Syncing

**Issue:** Commands were added to `commands/` but CLAUDE.md was not updated.

**Solution:**

```bash
/craft:docs:claude-md:sync
```

This runs the 4-phase pipeline: **detect** (scan project metrics) -> **audit** (compare against CLAUDE.md) -> **fix** (update stale values) -> **optimize** (enforce line budget and section priorities).

**Why:** CLAUDE.md references project metrics that change with every feature addition.

### 2. Version Bumped Without Sync

**Issue:** A release was tagged but CLAUDE.md still shows the old version.

**Solution:**

```bash
/craft:docs:claude-md:sync
grep "Current Version" CLAUDE.md   # verify fix
```

**Why:** The sync pipeline extracts the version from git tags and `CHANGELOG.md`, then updates the CLAUDE.md header.

### 3. Manual Edits That Drifted

**Issue:** Hand edits introduced inconsistencies -- duplicate sections, wrong counts, or broken links.

**Solution:**

```bash
/craft:docs:claude-md:sync
# Watch for optimizer warnings about bloated or duplicate sections
```

**Why:** The optimizer classifies sections by priority (P0/P1/P2) and flags sections that push the file over budget.

### 4. File Exceeds Line Budget

**Issue:** CLAUDE.md has grown beyond the recommended size, slowing down Claude's parsing.

**Solution:**

```bash
wc -l CLAUDE.md                          # check current size
/craft:docs:claude-md:sync               # optimizer trims low-priority content
bash scripts/claude-md-budget-check.sh   # pre-commit budget check
```

**Why:** CLAUDE.md is read at the start of every conversation. Lean files (< 150 lines for new projects) improve response quality and reduce token usage.

## Verification Steps

```bash
./scripts/validate-counts.sh             # verify command count matches reality
/craft:docs:claude-md:sync               # should report "0 issues found"
bash scripts/claude-md-budget-check.sh   # should pass without warnings
```

## Related

- [CLAUDE.md Command Reference](../../commands/docs/claude-md.md) -- init, sync, and edit commands
- [CLAUDE.md Quick Reference](../../reference/REFCARD-CLAUDE-MD.md) -- Cheat sheet for CLAUDE.md management
