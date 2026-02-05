---
title: "Recipe: Find the Right Command"
description: "Use the Hub to discover the exact Craft command for any task"
category: "cookbook"
level: "beginner"
time_estimate: "2 minutes"
related:
  - ../../commands/hub.md
  - ../../commands/overview.md
---

# Recipe: Find the Right Command

**Time:** 2 minutes
**Level:** Beginner
**Prerequisites:** Craft installed

## Problem

I want to find the right Craft command for a task without memorizing all 106 commands.

## Solution

1. **Open the Hub**

   ```bash
   /craft:hub
   ```

   Why: The Hub is a zero-maintenance command directory that auto-discovers all available commands

2. **Browse categories**

   The Hub shows top-level categories first:

   ```
   Available Categories:
     arch      Architecture analysis (12 commands)
     ci        CI/CD automation (6 commands)
     code      Code quality (8 commands)
     docs      Documentation (14 commands)
     git       Git workflow (9 commands)
     site      Website management (6 commands)
     test      Testing (10 commands)
     workflow  Workflow tools (5 commands)
   ```

   Why: Progressive disclosure keeps the list manageable instead of showing all 106 commands at once

3. **Drill into a category**

   ```bash
   /craft:hub code
   ```

   Why: Shows just the commands in that category with short descriptions

   ```
   Code Commands:
     code:lint       Run code quality checks
     code:format     Auto-format code files
     code:coverage   Generate coverage report
     code:ci-local   Run CI checks locally
     ...
   ```

4. **View command details**

   ```bash
   /craft:hub code:lint
   ```

   Why: Shows full usage, flags, examples, and execution modes for that specific command

## Explanation

The Hub uses 3-layer progressive disclosure: **Main** (all categories) then **Category** (commands in one group) then **Detail** (full docs for one command). It reads command metadata directly from YAML frontmatter in the command files, so new commands appear automatically without any manual registry updates.

## What's Next

- [Hub Command Reference](../../commands/hub.md) -- Full Hub documentation
- [Commands Overview](../../commands/overview.md) -- All commands listed by category
- [Quick Code Checks](quick-code-checks.md) -- Run your first lint check
