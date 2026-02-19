---
description: Clean up merged branches safely
category: git
arguments:
  - name: dry-run
    description: Preview branches that would be deleted without executing
    required: false
    default: false
    alias: -n
---

# Git Clean - Remove merged branches

This command safely removes branches that have been merged.

## What I'll do

1. **Analyze merged branches** - Identify branches that have been merged
2. **Check for ORCHESTRATE files** - Warn if any `ORCHESTRATE-*.md` files remain on `dev` after merge (working artifacts that should have been removed by `/craft:git:worktree finish`)
3. **Check for issues** - Detect uncommitted changes or other blockers
4. **Preview or execute** - Show what will be deleted (dry-run) or delete branches
5. **Confirm deletion** - Ask before deleting (unless --dry-run)

## Safety

- Never deletes current branch
- Never deletes protected branches (main/master/dev/develop)
- Skips branches with uncommitted changes
- Always confirms before deletion
- Supports `--dry-run` to preview without executing

## Usage

```bash
# Preview what would be deleted
/craft:git:clean --dry-run
/craft:git:clean -n

# Actually delete merged branches (with confirmation)
/craft:git:clean
```

## Implementation

The command:

1. Lists all local branches using `git branch --merged`
2. Filters out protected branches and current branch
3. Checks each branch for uncommitted changes
4. In dry-run mode: Displays preview with warnings
5. In normal mode: Asks for confirmation, then deletes branches

## Dry-Run Output Example

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Clean Merged Branches                              │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Delete 3 local branches (merged to dev):                    │
│   - feature/auth-system                                       │
│   - fix/login-bug                                             │
│   - refactor/api-cleanup                                      │
│                                                               │
│ ⊘ Skip 1 branch:                                              │
│   - feature/wip (uncommitted changes)                         │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • Branch feature/wip has uncommitted changes                 │
│                                                               │
│ 📊 Summary: 3 branches to delete, 1 skipped                    │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

## See Also

- Template: `templates/dry-run-pattern.md`
- Utility: `utils/dry_run_output.py`
- Specification: `docs/specs/_archive/SPEC-dry-run-feature-2026-01-15.md`
