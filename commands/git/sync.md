---
description: Smart git synchronization with remote repositories
category: git
arguments:
  - name: dry-run
    description: Preview sync operations without executing
    required: false
    default: false
    alias: -n
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:sync - Smart Git Sync

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 6: Remote Sync).
> This file exists only to preserve the explicit `/craft:git:sync` slash
> entry point through the v2.34.0 → v3.0.0 migration.

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 6
   (Remote Sync), and follow it exactly — detect ahead/behind divergence,
   fast-forward when possible, prompt rebase vs. merge on true divergence,
   never force-push to protected branches.
2. **Do not reimplement here.** Any change to `/craft:git:sync` behavior —
   conflict handling, sync strategy selection, stash handling — must be made
   in the skill, never duplicated into this shim.

## Why this is a shim

`/craft:git:sync` is one of the 10 `commands/git/*.md` commands (plus 4
`commands/git/docs/*.md` reference docs) consolidated into `skills/dev/git/`
under the v2.34.0 → v3.0.0 migration (ADR-002's pattern, generalized). Both
entry paths — the explicit `/craft:git:sync` slash command and natural-language
triggers ("sync with remote", "pull and push") — route to the same skill. At
v3.0.0 this shim may be retired; the canonical body in the skill survives.
