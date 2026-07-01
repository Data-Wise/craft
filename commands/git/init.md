---
description: Initialize git repository with craft workflow patterns
category: git
arguments:
  - name: remote
    description: GitHub repository (user/repo or full URL)
    required: false
  - name: workflow
    description: Workflow pattern (main-dev|simple|gitflow)
    required: false
    default: main-dev
  - name: dry-run
    description: Preview changes without executing
    required: false
    default: false
  - name: yes
    description: Skip interactive prompts, use defaults
    required: false
    default: false
deprecated: true
replaced-by: "skills/dev/git/"
---

# /craft:git:init - Initialize Repository

> **This command is a thin shim.** The canonical behavior lives in the
> `git-workflow` skill (`skills/dev/git/SKILL.md`, Operation 1: Repo Init).
> This file exists only to preserve the explicit `/craft:git:init` slash
> entry point through the v2.34.0 → v3.0.0 migration.

## When invoked

1. **Load the canonical procedure:** read
   [`skills/dev/git/SKILL.md`](../../skills/dev/git/SKILL.md), Operation 1
   (Repo Init), and follow it exactly — bootstrap the repo, apply the
   `main-dev`/`simple`/`gitflow` workflow pattern, wire remote + branch
   protection, scaffold starter files.
2. **Do not reimplement here.** Any change to `/craft:git:init` behavior —
   wizard steps, workflow-pattern choices, rollback strategy, template
   contents — must be made in the skill, never duplicated into this shim.

## Why this is a shim

`/craft:git:init` is one of the 10 `commands/git/*.md` commands (plus 4
`commands/git/docs/*.md` reference docs) consolidated into `skills/dev/git/`
under the v2.34.0 → v3.0.0 migration (ADR-002's pattern, generalized). Both
entry paths — the explicit `/craft:git:init` slash command and natural-language
triggers ("init a repo", "bootstrap project") — route to the same skill. At
v3.0.0 this shim may be retired; the canonical body in the skill survives.
