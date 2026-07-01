---
description: Adversarially interrogate a plan, spec, or topic one question at a time — convergent counterpart to brainstorm
arguments:
  - name: target
    description: "Spec/plan path, a topic in quotes, or empty to detect from context"
    required: false
  - name: bound
    description: "Limit interrogation to N decision branches (used by orchestrate Step 0.5 for a quick gate)"
    required: false
    default: null
  - name: no-capture
    description: "Skip writing a GRILL spec file; return decisions inline (used by embedded callers like orchestrate Step 0.5)"
    required: false
    default: false
  - name: yes
    description: "Non-interactive: auto-accept every Recommended answer, emit zero AskUserQuestion prompts (alias --non-interactive)"
    required: false
  - name: refine
    description: "Refine the topic via prompt-refiner BEFORE grilling. Default-ON for a quoted/bare topic; SKIPPED when the argument is a path (a spec/plan file — nothing to refine). --no-refine to disable."
    required: false
  - name: no-tests
    description: "Skip the auto-emitted test-plan section (on by default)"
    required: false
  - name: no-docs
    description: "Skip the auto-emitted Documentation section (on by default)"
    required: false
---

# /craft:grill — Interrogate Before Building

> **This command is a thin shim.** The canonical behavior lives in the
> [`grill` skill](../skills/workflow/grill/SKILL.md). This file preserves the
> explicit `/craft:grill` slash entry point and owns the argument surface.

Convergent counterpart to `/craft:workflow:brainstorm`: brainstorm is **divergent** (generates
options); grill is **convergent** (interrogates a position to find gaps, contradictions, and
unresolved dependencies before you implement).

## When Invoked

1. **Load the canonical procedure:** read
   [`skills/workflow/grill/SKILL.md`](../skills/workflow/grill/SKILL.md) and follow it exactly —
   resolve target, codebase-first pre-answer sweep, select attack angles, the deliberate
   one-question-at-a-time grill loop (Recommended-first + per-option consequence), milestone
   checkpoints, durable `GRILL-*.md` capture via `commands/utils/grill_ledger.py`, and the
   one-directional handoff into `/craft:plan`.
2. **Do not reimplement here.** Any change to grill behavior must be made in the skill, never
   duplicated into this shim.

The flags above (`--bound`, `--no-capture`, `--yes`/`--non-interactive`, `--refine`/`--no-refine`,
`--no-tests`/`--no-docs`) are parsed here and passed through to the skill.
