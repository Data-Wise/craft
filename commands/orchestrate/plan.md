---
description: Generate ORCHESTRATE file from spec, with optional worktree creation and cross-repo detection
category: orchestrate
arguments:
  - name: spec-path
    description: Path to SPEC-*.md file (if omitted, scans docs/specs/ for available specs)
    required: false
  - name: output
    description: "Output mode: orchestrate-worktree (default), orchestrate-only"
    required: false
    default: orchestrate-worktree
deprecated: true
replaced-by: "skills/orchestration/plan-orchestrator/"
---

# /craft:orchestrate:plan — Spec → ORCHESTRATE → Worktree Pipeline

> **This command is a thin shim.** The canonical behavior lives in the
> [`plan-orchestrator` skill](../../skills/orchestration/plan-orchestrator/SKILL.md). This file
> preserves the explicit `/craft:orchestrate:plan` slash entry point and owns the argument surface.

Generate an ORCHESTRATE file from a spec document, optionally creating a worktree for isolated
development.

## Usage

```bash
# Interactive: scan for specs and choose
/craft:orchestrate:plan

# Direct: specify spec path
/craft:orchestrate:plan docs/specs/SPEC-auth-2026-02-15.md

# ORCHESTRATE only (no worktree)
/craft:orchestrate:plan docs/specs/SPEC-auth.md --output orchestrate-only
```

## When Invoked

1. **Load the canonical procedure:** read
   [`skills/orchestration/plan-orchestrator/SKILL.md`](../../skills/orchestration/plan-orchestrator/SKILL.md)
   and follow its "Spec → ORCHESTRATE (`orchestrate:plan`)" mode exactly — spec discovery, spec
   parsing, cross-repo detection, plan confirmation, ORCHESTRATE file generation (canonical
   template), worktree creation, `.STATUS`/`.gitignore` tracking, and the rebase-strategy check.
2. **Do not reimplement here.** Any change to this command's behavior must be made in the skill,
   never duplicated into this shim.

The `spec-path` and `output` arguments above are parsed here and passed through to the skill.

## See Also

- [/craft:orchestrate](../orchestrate.md) — Launch orchestrator mode
- [/craft:git:worktree](../git/worktree.md) — Manual worktree management
- [Worktree Tutorial](../../docs/tutorials/TUTORIAL-worktree-setup.md) — Step-by-step guide
