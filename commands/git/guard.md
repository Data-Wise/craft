---
description: Manage and inspect craft PreToolUse guards (branch-guard, no-switch-guard)
category: git
arguments:
  - name: action
    description: "Action: list | status | explain | test | enable | disable | profile"
    required: true
  - name: target
    description: "Guard name or number (for enable/disable/explain); profile name (focus|yolo|spec)"
    required: false
  - name: permanent
    description: "Permanent disable (vs 30-min mute)"
    required: false
    default: false
    alias: --permanent
  - name: session
    description: "Session-scoped mute (expires after mute_window_min)"
    required: false
    default: false
    alias: --session
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:guard - Manage Craft PreToolUse Guards

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 12: Guard
> Registry CLI). This file exists only to preserve the explicit
> `/craft:git:guard` slash entry point through the v2.34.0 → v3.0.0
> migration.

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 12
   (Guard Registry CLI), and follow it exactly — `list`/`status`/`explain`/
   `test`/`enable`/`disable`/`profile`, the mute-expiry sweep, and the
   `guards.json` sole-mutator contract.
2. **`explain <cmd>` uses the real classify mode.** Run the command text
   through `GUARD_DRY_RUN=1 bash scripts/branch-guard.sh` and
   `GUARD_DRY_RUN=1 bash scripts/no-switch-guard.sh` (both scripts' additive
   dry-run mode), then present the two lines as one unified table — do not
   reason about what the guards "would" do from memory of their logic.
3. **Do not reimplement here.** Any change to registry mutation, profile
   presets, or the guard table's rendering must be made in the skill, never
   duplicated into this shim. The registry table is generated from
   `~/.claude/guards.json` at render time — it is never a static list in
   this file.

## Why this is a shim

`/craft:git:guard` was a standalone 446-line command folded into
`skills/dev/git/` as Operation 12 by
`SPEC-branch-protection-consolidation-2026-07-07` (both scripts hardcode
`/craft:git:guard disable <name>` as a remediation string, so the command
stays a thin shim rather than being deleted outright — deleting it would
require a coordinated same-PR update to those hardcoded strings). Both entry
paths — the explicit `/craft:git:guard` slash command and natural-language
triggers ("list guards", "explain what this command would do") — route to
the same skill Operation.

## See Also

- `/craft:git:protect` — Local branch-guard config (Operation 8)
- `/craft:git:unprotect` — Session-scoped bypass for branch protection
- `docs/guide/guard-suite.md` — Guard suite user guide
