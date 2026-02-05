---
title: "Troubleshooting: Worktree Won't Create"
description: "Fix errors when /craft:git:worktree fails to create a new worktree"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - ../../commands/git/worktree.md
  - ../../guide/worktree-advanced-patterns.md
---

# Troubleshooting: Worktree Won't Create

**Level:** Beginner

## Problem

Running `/craft:git:worktree feature/<name>` fails instead of creating a new worktree:

```
fatal: 'feature/docs-revamp' already exists
```

or

```
fatal: '/Users/you/.git-worktrees/craft/feature-docs-revamp' already exists
```

## Common Causes & Solutions

### 1. Branch Already Exists

**Issue:** A local branch with the same name exists from a previous worktree.

**Solution:**

```bash
git branch --list 'feature/*'
git branch -d feature/docs-revamp   # safe if already merged
/craft:git:worktree feature/docs-revamp
```

**Why:** Git refuses to create a worktree for a branch that already exists locally.

### 2. Directory Path Conflict

**Issue:** The target directory exists on disk even though no worktree is registered.

**Solution:**

```bash
rm -rf ~/.git-worktrees/craft/feature-docs-revamp
git worktree prune
/craft:git:worktree feature/docs-revamp
```

**Why:** `git worktree prune` cleans internal references but does not delete orphaned directories.

### 3. Not on the `dev` Branch

**Issue:** Worktrees must be created from `dev` to branch from the correct base.

**Solution:**

```bash
git branch --show-current        # check current branch
git checkout dev && git pull origin dev
/craft:git:worktree feature/docs-revamp
```

**Why:** Craft requires `main <- dev <- feature/*`. Branching from `main` or another feature branch breaks the integration flow.

### 4. Uncommitted Changes

**Issue:** A dirty working tree blocks the branch operation.

**Solution:**

```bash
git stash push -m "stash before worktree"
/craft:git:worktree feature/docs-revamp
```

**Why:** Worktree creation involves checkout operations that conflict with uncommitted changes.

## Verification Steps

```bash
git worktree list
cd ~/.git-worktrees/craft/feature-docs-revamp
git branch --show-current
# Expected: feature/docs-revamp
```

## Related

- [Worktree Command Reference](../../commands/git/worktree.md) -- Full command documentation
- [Worktree Advanced Patterns](../../guide/worktree-advanced-patterns.md) -- Multi-worktree management
- [Git Worktree Quick Reference](../../reference/REFCARD-GIT-WORKTREE.md) -- Cheat sheet
