---
description: Roadmap Generation
category: plan
deprecated: true
replaced-by: "skills/orchestration/plan-orchestrator/"
---

# Roadmap Generation

> **This command is a thin shim.** The canonical behavior lives in the
> `plan-orchestrator` skill (Mode 4: Roadmap). This file exists only to preserve the
> explicit `/craft:plan:roadmap` slash entry point.

## When invoked

1. **Load the canonical procedure:** read
   [`skills/orchestration/plan-orchestrator/SKILL.md`](../../skills/orchestration/plan-orchestrator/SKILL.md)
   and follow its "4. Roadmap (`plan:roadmap`)" section exactly — phased milestones with
   progress bars, dependency callouts, timeline gantt-style strip.
2. **Do not reimplement here.** Any change to roadmap-generation behavior — output
   format, options (`--horizon`, `--format`, `--output`, `--update`), or flow — must be
   made in the skill, never duplicated into this shim.

## Why this is a shim

`plan-orchestrator` consolidated four planning commands (feature/sprint/roadmap +
spec→ORCHESTRATE) into one skill. This file is kept only as a deprecated alias so
existing muscle-memory (`/craft:plan:roadmap`) keeps working during the deprecation
horizon; the real logic lives in the skill.
