---
title: "Recipe: Update a Single Documentation Section"
description: "Refresh documentation for one specific area using the docs update command"
category: "cookbook"
level: "beginner"
time_estimate: "3 minutes"
related:
  - ../../commands/docs.md
  - ../../guide/documentation-quality.md
---

# Recipe: Update a Single Documentation Section

**Time:** 3 minutes
**Level:** Beginner
**Prerequisites:** Craft installed, MkDocs project with existing docs

## Problem

I want to update the documentation for one specific area of my project without regenerating everything.

## Solution

1. **Check which docs are outdated**

   ```bash
   /craft:docs:lint
   ```

   Why: Scans all documentation files and reports stale content, broken links, and formatting issues so you know where to focus

2. **Update a specific documentation category**

   ```bash
   /craft:docs:update commands
   ```

   Why: Targets only the `commands` docs directory, leaving other sections untouched. You can substitute any category name (e.g., `guide`, `tutorials`, `reference`)

3. **Review the proposed changes**

   The command shows a diff of what will change before applying:

   ```
   Changes to apply:
     docs/commands/overview.md  - Updated command count (104 -> 106)
     docs/commands/code.md      - Added new flag documentation
   Accept changes? (y/n)
   ```

   Why: You confirm before anything is written, so you stay in control

4. **Verify the result**

   ```bash
   /craft:docs:lint
   ```

   Why: Re-running the linter confirms the issues are resolved and no new problems were introduced

## Explanation

`/craft:docs:update` detects your project type and scans the specified section for outdated content. It checks command counts, version references, feature lists, and cross-references against the current codebase. Changes are always shown for review before being applied, so nothing is overwritten without your approval.

## What's Next

- [Docs Commands Reference](../../commands/docs.md) -- Full documentation command suite
- [Documentation Quality Guide](../../guide/documentation-quality.md) -- Best practices for project docs
- [Check Code Quality Before Commit](check-code-quality-before-commit.md) -- Validate everything before committing
