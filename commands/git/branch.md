---
description: Interactive git branch management assistant
category: git
arguments:
  - name: action
    description: Action to perform (new|switch|delete|sync) or empty to show status
    required: false
  - name: name
    description: Branch name (for new/switch/delete actions)
    required: false
  - name: dry-run
    description: Preview branch operations without executing
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:branch - Branch Management

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 2: Branch
> Management, with delete-safety shared via Operation 4 / Cross-Operation
> Patterns). This file exists only to preserve the explicit
> `/craft:git:branch` slash entry point through the v2.34.0 → v3.0.0
> migration.

## Actions

```bash
/craft:git:branch                              # Show branch overview
/craft:git:branch new <name> [--dry-run|-n]    # Create new branch
/craft:git:branch switch <name>                # Switch branches
/craft:git:branch delete <name> [--dry-run|-n]  # Delete branch safely
/craft:git:branch sync                         # Sync with remote (alias to Operation 6)
```

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 2
   (Branch Management), and follow it exactly — `new`/`switch`/`delete`/
   `sync` sub-actions, the safety rules (never delete current/protected
   branches, refuse dirty-tree switches), and default-base selection
   (`dev` if it exists, else `main`).
2. **Delete-safety checks** (merged-check via `is_squash_merged`,
   confirm-before-delete) are shared with Operation 4 — see that Operation
   and the skill's Cross-Operation Patterns section; do not restate them
   here, same pattern as `clean.md`.
3. **Branch-naming conventions** (`feature/*`, `fix/*`, `docs/*`,
   `experiment/*`, etc.) are generic reference material, not per-command
   prose — see the skill's Cross-Operation Patterns / branch-architecture
   section rather than duplicating a naming-pattern table in this shim.
4. **Do not reimplement here.** Any change to branch-management behavior
   must be made in the skill, never duplicated into this shim.

## Why this is a shim

`/craft:git:branch` was a standalone 483-line command that already claimed
`replaced-by: "skills/dev/git/"` in its frontmatter without actually being
thinned — a stale-shim drift found and fixed by
`SPEC-branch-protection-consolidation-2026-07-07` §4.7. Both entry paths —
the explicit `/craft:git:branch` slash command and natural-language triggers
("new branch", "switch branch", "delete branch") — route to the same skill
Operation.

## See Also

- `/craft:git:clean` - Clean merged branches
- `/craft:git:worktree` - Worktree management
- `/craft:git:status` - Enhanced git status with teaching-specific context
- `/craft:git:sync` - Smart git synchronization with remote repositories
- `/craft:git:unprotect` - Session-scoped bypass for branch protection with reason logging
- `/craft:git:protect-baseline` - Apply GitHub-side branch protection (PR required, no force-push, no delete) to any repo
