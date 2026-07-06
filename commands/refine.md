---
description: /refine - Prompt Optimizer
deprecated: true
replaced-by: "skills/workflow/prompt-refiner/"
---

# /refine - Prompt Optimizer

> **This command is a thin shim.** The canonical behavior lives in the
> `prompt-refiner` skill. This file exists only to preserve the explicit
> `/craft:refine` slash entry point through the v2.34.0 → v3.0.0
> migration (see [ADR-002](../docs/adr/ADR-002-done-command-skill-consolidation.md),
> which treats `/refine` as a separate consolidation into `prompt-refiner`,
> distinct from the six `adhd-workflow` commands).

## When invoked

1. **Load the canonical procedure:** read
   [`skills/workflow/prompt-refiner/SKILL.md`](../skills/workflow/prompt-refiner/SKILL.md)
   and follow it exactly — read context, rewrite, show before/after, confirm
   via AskUserQuestion, return the chosen prompt. With no downstream command
   (standalone `/refine "..."` ), stop after the before/after + confirm step
   and print the refined prompt.
2. **Do not reimplement here.** Any change to `/refine` behavior — including
   the optional `--explain` rationale mode — must be made in the skill, never
   duplicated into this shim.

## Why this is a shim

`/refine` is consolidated into a skill under the v2.34.0 → v3.0.0 migration
(ADR-002) — a separate consolidation from the six `commands/workflow/*.md`
commands (`done`/`recap`/`next`/`focus`/`stuck`/`spec-review`) that route into
the `adhd-workflow` skill. Both entry paths — the explicit
`/craft:refine` slash command and the `--refine` flag on
brainstorm/do/orchestrate/plan:feature/arch:plan — now route to the same
`prompt-refiner` skill. The canonical body lives in the skill, not here.

**Scope note:** the pre-consolidation version of this command also had
clipboard-copy and background-task-execution ("execute in background, check
status via task-status/task-output") features. Those are command-routing
concerns, not prompt-refining, and were intentionally dropped rather than
ported — the skill's job is to rewrite the prompt and hand it back, not to
execute or manage it. If background execution of a refined prompt is wanted,
that belongs in the calling command (e.g. `/craft:do --refine`), not here.
