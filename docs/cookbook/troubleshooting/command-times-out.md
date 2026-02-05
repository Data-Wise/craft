---
title: "Troubleshooting: Command Times Out"
description: "Fix commands that run too long or exceed their time budget"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - ../../commands/overview.md
  - ../../guide/interactive-commands.md
---

# Troubleshooting: Command Times Out

**Level:** Beginner

## Problem

A Craft command runs too long and exceeds its time budget:

```
/craft:code:lint release
⏳ Running comprehensive lint checks...
ERROR: Command exceeded 300s budget. Aborting.
```

## Common Causes & Solutions

### 1. Wrong Execution Mode for the Task

**Issue:** Using a heavy mode like `release` on a task that only needs the default.

**Solution:** Match the mode to the task:

| Mode       | Budget  | Use When                       |
|------------|---------|--------------------------------|
| default    | < 10s   | Day-to-day tasks, quick checks |
| debug      | < 120s  | Diagnosing unexpected behavior |
| optimize   | < 180s  | Large codebases, deep scans   |
| release    | < 300s  | Pre-release validation only    |

```bash
/craft:code:lint            # default — handles 90% of tasks
/craft:code:lint release    # overkill for a quick check
```

**Why:** The default mode handles most tasks. Reserve `release` for actual releases.

### 2. Complex Task in Default Mode

**Issue:** A genuinely complex task (large codebase, many files) times out at the 10-second default budget.

**Solution:** Upgrade the mode or use smart routing:

```bash
/craft:arch:analyze optimize         # More time for large codebases
/craft:do "analyze architecture"     # Auto-selects appropriate mode
```

**Why:** `/craft:do` uses the complexity scorer to automatically pick the right mode.

### 3. Network Issues for Site Commands

**Issue:** Site commands (`site:update`, link-check) stall on HTTP requests.

**Solution:**

1. Check your network connection
2. Use local-only checks if offline: `/craft:docs:lint`
3. Retry with a longer budget: `/craft:site:update optimize`

**Why:** External link validation requires HTTP requests that can be slow on poor connections.

### 4. Stale Process or Cached State

**Issue:** A previous failed command left partial state that blocks the current run.

**Solution:**

1. Cancel the stuck command (Ctrl+C)
2. Run `/craft:check` to verify health
3. Restart your Claude Code session if the problem persists

## Verification Steps

```bash
# Quick default-mode check (should complete in <10s)
/craft:check

# Verify mode selection works
/craft:code:lint debug
# Expected: completes within 120s with verbose output
```

## Related

- [Commands Overview](../../commands/overview.md) — Execution modes explained
- [Interactive Commands Guide](../../guide/interactive-commands.md) — "Show Steps First" pattern
- [Do Command](../../commands/do.md) — Smart routing with automatic mode selection
