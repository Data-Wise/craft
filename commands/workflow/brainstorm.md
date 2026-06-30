---
name: brainstorm
description: Enhanced brainstorming with smart detection, design modes, time budgets, context-aware questions, and spec capture
category: workflow
arguments:
  - name: depth
    description: "Analysis depth: q|quick|d|deep (default: balanced, shows menu if omitted)"
    required: false
  - name: focus
    description: "Focus area: f|feat|a|arch|x|ux|b|api|u|ui|o|ops (optional, auto-detect if omitted)"
    required: false
  - name: action
    description: "Action: s|save (capture as spec) - replaces --save-spec"
    required: false
  - name: topic
    description: "Topic to brainstorm (quoted string, uses conversation context if omitted)"
    required: false
  - name: format
    description: "Output format: terminal|json|markdown (default: terminal)"
    required: false
  - name: categories
    description: "Question categories: req,users,scope,tech,timeline,risks,existing,success (comma-separated, use 'all' for default)"
    required: false
  - name: orch
    description: "Enable orchestration mode (delegates to orchestrator-v2; replaces the old in-skill max-depth agent delegation)"
    required: false
  - name: orch-mode
    description: "Orchestration mode: default|debug|optimize|release"
    required: false
  - name: no-tests
    description: "Skip the auto-emitted test-plan section (on by default)"
    required: false
  - name: no-docs
    description: "Skip the auto-emitted Documentation section (on by default)"
    required: false
  - name: refine
    description: "Runs the prompt-refiner by default; pass --no-refine to skip"
    required: false
    default: true
  - name: no-refine
    description: Skip the prompt-refiner (opt out of the default refinement step)
    required: false
    default: false
deprecated: true
replaced-by: "skills/workflow/brainstorm/"
---

# /brainstorm - ADHD-friendly Ideation

> **This command is a thin shim.** The canonical behavior lives in the
> `brainstorm` skill (a sibling of `brainstorm-insights`, which now holds
> only the session-insights operation — see "Why this is a redesign" below).
> This file exists only to preserve the explicit `/craft:workflow:brainstorm`
> slash entry point through the v2.34.0 → v3.0.0 migration.

## --refine / --no-refine (prompt pre-processing)

Runs the prompt-refiner **by default** to pre-process your input. Pass `--no-refine` to skip.
Under `--yes`, the refiner auto-accepts (no Accept/Edit prompt).

Do NOT act on the raw argument. First invoke the `prompt-refiner` skill with
the argument and project context. Follow that skill's canonical flow
(before/after → Accept/Edit/Use-original; `--yes` or auto mode
auto-accepts). Then proceed using the prompt the skill returns. On
no-argument interactive commands, refine AFTER the topic is captured.

## When invoked

1. **Load the canonical procedure:** read
   [`skills/workflow/brainstorm/SKILL.md`](../../skills/workflow/brainstorm/SKILL.md)
   and follow it exactly — parse args, pick depth+focus, context scan,
   expert questions, one follow-up offer, generate output, optional spec
   capture, optional `--orch` handoff.
2. **Do not reimplement here.** Any change to `/brainstorm` behavior must be
   made in the skill, never duplicated into this shim.

## Why this is a redesign, not just a shim

The pre-redesign command and the `brainstorm-insights` skill it pointed to
both carried full, diverging implementations of brainstorming — see the
deprecated-commands audit. This redesign:

- **Splits brainstorm from insights.** `brainstorm-insights` bundled two
  operations sharing no input or output: ideation (topic + context →
  BRAINSTORM/SPEC) and session-facet friction analysis
  (`~/.claude/usage-data/facets/` → report). Insights now lives alone at
  `skills/workflow/brainstorm-insights/` (directory name kept for path
  stability — tests and `commands/workflow/insights.md` reference it).
  Brainstorm moved to its own `skills/workflow/brainstorm/`.
- **Cut decision points from four to two.** The old flow had separate depth
  and focus menus, a per-depth "ask more?" escape hatch with different
  options at each depth, and milestone re-prompts every N questions at high
  counts. Now: one combined depth+focus prompt, one follow-up offer after
  the expert questions.
- **Removed in-skill agent delegation.** The old "max" depth spawned 1-2
  background subagents directly, using agent type names that didn't exist
  (silently falling back to `general-purpose` with no model pin — fixed
  earlier in this branch). That duplicated what `orchestrator-v2` already
  does correctly (wave checkpoints, file-based results, explicit model
  routing, confirmation before spawning). Brainstorm no longer spawns agents
  itself — deep analysis needing multiple agents goes through `--orch`
  (routes to `orchestrator-v2`, unaffected by this redesign) after a spec is
  captured. One delegation mechanism, not two. There is no more `max` depth;
  use `deep` for the full question set, then `--orch` if multi-agent
  implementation planning is wanted.

## Test-plan / Documentation scaffolding (unchanged, on by default)

`--no-tests` / `--no-docs` still suppress the auto-emitted sections, per the
arguments above. The tier-inference table and doc-scorer reuse are
documented in the skill, not here — see
[`skills/workflow/brainstorm/SKILL.md`](../../skills/workflow/brainstorm/SKILL.md#test-plan-and-documentation-scaffolding-default-on).
