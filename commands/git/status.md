---
description: Enhanced git status with teaching-specific context
category: git
arguments:
  - name: verbose
    description: Show full git status output
    required: false
    default: false
    alias: -v
  - name: compact
    description: Show compact teaching context only
    required: false
    default: false
    alias: -c
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:status - Enhanced Git Status

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 3: Enhanced
> Status). This file exists only to preserve the explicit
> `/craft:git:status` slash entry point through the v2.34.0 → v3.0.0
> migration.

## Flags

```bash
/craft:git:status             # Standard status with teaching context
/craft:git:status --verbose   # Full git status output below the summary
/craft:git:status -v
/craft:git:status --compact   # Teaching context (or one-line summary) only
/craft:git:status -c
```

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 3
   (Enhanced Status), and follow it exactly — current branch, ahead/behind,
   worktree-aware path, teaching-mode detection and critical-file
   highlighting, and the guard-status display (protection level, session
   confirm count, one-shot-pending, bypass state — sourced from Operation 8's
   config, not restated here).
2. **Do not reimplement here.** Box-drawing output, teaching-mode critical
   file patterns (`syllabus/`, `schedule.qmd`, `assignments/`), and the
   protection-indicator logic all live in the skill's Operation 3 prose (and
   `utils/detect_teaching_mode.py`) — do not hardcode a second copy of the
   status box format in this shim.

## Why this is a shim

`/craft:git:status` was a standalone 453-line command that already claimed
`replaced-by: "skills/dev/git/"` in its frontmatter without actually being
thinned — a stale-shim drift found and fixed by
`SPEC-branch-protection-consolidation-2026-07-07` §4.7. Both entry paths —
the explicit `/craft:git:status` slash command and natural-language triggers
("git status", "what's the state of this repo") — route to the same skill
Operation.

## See Also

- `/craft:git:branch` - Branch management
- `/craft:git:sync` - Sync with remote
- `/craft:git:unprotect` - Session-scoped bypass for branch protection with reason logging
- `/craft:git:worktree` - Git worktree management for parallel development workflows
- Utility: `utils/detect_teaching_mode.py`
- `/craft:git:protect-baseline` - Apply GitHub-side branch protection (PR required, no force-push, no delete) to any repo
