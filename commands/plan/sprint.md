---
description: Sprint Planning
category: plan
deprecated: true
replaced-by: "skills/orchestration/plan-orchestrator/"
---

# Sprint Planning

> **This command is a thin shim.** The canonical behavior lives in the
> `plan-orchestrator` skill (Mode 3: Sprint Plan). This file exists only to preserve the
> explicit `/craft:plan:sprint` slash entry point.

## When invoked

1. **Load the canonical procedure:** read
   [`skills/orchestration/plan-orchestrator/SKILL.md`](../../skills/orchestration/plan-orchestrator/SKILL.md)
   and follow its "3. Sprint Plan (`plan:sprint`)" section exactly — gather backlog,
   prioritize, fit to capacity, name a sprint goal, commit + stretch items, highlight
   dependencies and risks.
2. **Do not reimplement here.** Any change to sprint-planning behavior — output format,
   options (`--duration`, `--capacity`, `--goal`, `--from`), or flow — must be made in the
   skill, never duplicated into this shim.

## Why this is a shim

`plan-orchestrator` consolidated four planning commands (feature/sprint/roadmap +
spec→ORCHESTRATE) into one skill. This file is kept only as a deprecated alias so
existing muscle-memory (`/craft:plan:sprint`) keeps working during the deprecation
horizon; the real logic lives in the skill.
