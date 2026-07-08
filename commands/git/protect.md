---
description: Re-enable branch protection after bypass, configure protection level
category: git
tags: [git, branch-protection]
arguments:
  - name: level
    description: Set protection level (smart|block-all|block-new-code)
    required: false
  - name: show
    description: Display current protection config without changes
    required: false
    default: false
  - name: reset
    description: Remove branch from config (revert to auto-detect)
    required: false
    default: false
  - name: no-hard-deny
    description: Skip the hard_deny layer detection step (v2.33.0)
    required: false
    default: false
  - name: audit
    description: Run the gap-diff-then-ask baseline audit wizard (also the default when protection is already active and no other flag is given)
    required: false
    default: false
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:protect - Branch Protection Management

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 8: Local Branch
> Protection). This file exists only to preserve the explicit
> `/craft:git:protect` slash entry point through the v2.34.0 → v3.0.0
> migration.

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 8
   (Local Branch Protection), and follow it exactly — bypass-marker removal,
   hard_deny detection, `--show`/`--level`/`--reset`, and the `--audit`
   gap-diff wizard (diffs against `docs/specs/baseline.json`, reuses
   Operation 9's GitHub-side check, walks gaps one `AskUserQuestion` at a
   time).
2. **Do not reimplement here.** Any change to level detection, hard_deny
   install flow, or the audit wizard must be made in the skill, never
   duplicated into this shim. Use `CONFIG_FILE` as the sole variable name for
   `.claude/branch-guard.json` — do not reintroduce the `$CONFIG`/
   `$CONFIG_FILE` naming drift this fold fixed.

## Why this is a shim

`/craft:git:protect` was a standalone 212-line command folded into
`skills/dev/git/` as an extension of the existing Operation 8 by
`SPEC-branch-protection-consolidation-2026-07-07`. Both entry paths — the
explicit `/craft:git:protect` slash command and natural-language triggers
("protect main", "enable branch protection") — route to the same skill
Operation.

## See Also

- `/craft:git:protect-baseline` — Apply GitHub-side branch protection (PR
  required, no force-push, no delete) to any repo. Companion command —
  `/craft:git:protect` manages the local hook, `protect-baseline` manages
  GitHub-side rules. Unchanged by this consolidation.
- `/craft:git:unprotect` — Bypass branch protection
- `/craft:git:guard` — Guard registry CLI (enable/disable/explain)
- `/craft:git:status` — Shows protection indicator
