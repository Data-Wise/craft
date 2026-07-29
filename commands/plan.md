---
description: Universal planning entry point — routes to the right deliberation tier (brainstorm/grill/plan-orchestrator/project-planner) via deterministic repo-state detection, never phrase matching
category: plan
arguments:
  - name: topic
    description: "The topic/feature to plan. Optional — inferred from .STATUS/git branch/recent commits if omitted."
    required: false
  - name: dry-run
    description: Preview which tier would be selected, without invoking it
    required: false
    default: false
  - name: refine
    description: "Runs the prompt-refiner by default (deliberation-entry command — see prompt-refiner SKILL.md Default Policy); pass --no-refine to skip"
    required: false
    default: true
  - name: no-refine
    description: Skip the prompt-refiner (opt out of the default refinement step)
    required: false
    default: false
---

# Plan

Single entry point for craft's planning tiers (brainstorm → spec → strategy →
artifact). Decides which tier to invoke via **deterministic repo-state detection** —
never phrase/keyword classification. That distinction is the entire reason this
command exists safely: phrase classification is the exact mechanism that caused the
`project-planner` ↔ `plan-orchestrator` collision (C1,
`SPEC-planning-refactor-2026-06-22.md`) — a second phrase classifier one layer up
would relocate that risk, not eliminate it. See
[`GRILL-planning-refactor-a2-2026-07-04.md`](../docs/specs/GRILL-planning-refactor-a2-2026-07-04.md)
G-2 for the full reasoning.

## Scope

This command is a **router only** — it invokes exactly one of craft's existing
planning surfaces and then stops. It never re-implements brainstorm/grill/
plan-orchestrator/project-planner logic itself, and it never invokes `/craft:do` or
`/craft:orch` directly: the seam is one-directional (`plan` produces an
artifact; `do`/`orchestrate` consume it in a later, separate invocation — see
`SPEC-planning-refactor-2026-06-22.md` §4).

## Tier Detection (deterministic)

### Step 1: Resolve topic

Explicit `topic` argument, or infer in order from: `.STATUS` current-task field →
current git branch name → most recent commit subject. This is the same inference
order `plan-orchestrator`'s own "Inputs" section already documents — reused here, not
reinvented.

If no topic can be resolved (no argument, no `.STATUS` task, an unhelpful branch name
like `dev`/`main`), ask via `AskUserQuestion` rather than guessing.

### Step 2: Check repo state for that topic

```bash
spec=$(find docs/specs -iname "SPEC-*${topic}*.md" 2>/dev/null | grep -v _archive | head -1)
grill=$(find docs/specs -iname "GRILL-*${topic}*.md" 2>/dev/null | head -1)
orch=$(find . -maxdepth 1 -iname "ORCHESTRATE-*${topic}*.md" 2>/dev/null | head -1)
```

| Repo state | Route to | Tier |
|---|---|---|
| No SPEC found | `/craft:brainstorm` (renamed from `workflow:brainstorm`, v4) | 1 — divergent ideation → SPEC |
| SPEC exists, no GRILL | Offer `/craft:grill` (ask, don't force — a well-scoped, low-ambiguity spec doesn't strictly need one) | 2 — convergent interrogation |
| GRILL exists (or user declined it), no ORCHESTRATE | `plan-orchestrator` skill | 4 — artifact generation |
| SPEC + GRILL + ORCHESTRATE all exist | `project-planner` skill (strategy advice — the only case needing interpretation, since there's no further artifact-presence state left to detect against) | 3 — strategy |

### Step 3: Known limitation — staleness is not checked

This detection is pure presence/absence. It does not verify a SPEC is current
relative to the codebase, or that a GRILL predates later SPEC edits. Not built now —
gentle-ramp: add a mtime/git-log staleness check only if this actually causes
confusion in practice, not preemptively.

## `--dry-run`

Show which tier would be selected and why, without invoking it:

```
┌──────────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: /craft:plan routing                                   │
├────────────────────────────────────────────────────────────────── │
│ Topic: "orchestrator-consolidation" (inferred: git branch)        │
│ SPEC found:        docs/specs/SPEC-orchestrator-consolidation-... │
│ GRILL found:       none                                           │
│ ORCHESTRATE found: none                                           │
│ → Route: offer /craft:grill (tier 2)                              │
├──────────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                                  │
└──────────────────────────────────────────────────────────────────┘
```

## Integration

- `/craft:brainstorm` (renamed from `workflow:brainstorm`, v4), `grill`, `plan-orchestrator`, `project-planner` — the four
  tiers this router dispatches to. This command owns none of their internal logic.
- `/craft:do --plan <topic>` — pure sugar forwarding to `/craft:plan <topic>` (an
  alias, not a separate mode) — see `commands/do.md`.
- `/craft:do` / `/craft:orch` — the one-directional seam this hands off to once
  an artifact exists; never invoked directly by this command.
