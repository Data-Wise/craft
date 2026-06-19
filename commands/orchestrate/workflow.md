---
description: Execute a coded, fixed-control-flow workflow (parallel/pipeline/loop/verify) with schema-gated agents, data-driven fan-out, and cached/resumable replay
category: orchestrate
arguments:
  - name: workflow
    description: "Path to a WORKFLOW-*.yaml (or shape-DSL) file (default: newest WORKFLOW-*.yaml in the worktree root)"
    required: false
  - name: dry-run
    description: Print the wave plan (stages, fan-out, concurrency, schemas) without spawning agents
    required: false
    default: false
    alias: -n
  - name: resume
    description: "Replay run <run-id> from cache, re-running only stages whose cache key changed (and their downstream)"
    required: false
  - name: refine
    description: Pre-process a natural-language workflow request through prompt-refiner before synthesizing a definition
    required: false
    default: false
related_commands: orchestrate, orchestrate:drive
tutorial_file: docs/cookbook/recipes/run-a-coded-workflow.md
tags: workflow, orchestration, parallel, fan-out, yaml
---

# /craft:orchestrate:workflow — Coded Orchestration

Executes a **fixed control-flow program** — `parallel` / `pipeline` / `loop` /
`verify` — where only the *count* of agents in a `parallel` stage flexes to
upstream data. Thin wrapper: it owns args and the dry-run/resume surface, and
delegates compilation + dispatch + the verify gate to the `workflow-engine`
skill.

> **Which orchestration mode?**
>
> | Mode | Control model | Best for |
> |------|---------------|----------|
> | `/craft:orchestrate` | LLM improvises each turn | exploratory work |
> | `/craft:orchestrate:drive` | drive an approved SPEC to green | spec → done |
> | `/craft:orchestrate:workflow` | **fixed coded program** | known shapes: decompose → cover N → verify M → synthesize |

## Execution Behavior (MANDATORY)

Follow these steps in order. Do NOT skip any step.

### Step 1: Resolve the definition

Use the `workflow` arg; else the newest `WORKFLOW-*.yaml` in the worktree root.
With `--refine`, first pass a natural-language request through the
`prompt-refiner` skill, synthesize a `WORKFLOW-*.yaml`, and show it for
confirmation before running. Report which definition was chosen.

### Step 2: Compile the wave plan (delegate — never eyeball)

Run `python3 scripts/workflow_parse.py <file>` to obtain the canonical wave
plan. The YAML and shape-DSL forms compile to an identical plan given identical
upstream outputs (D1). A malformed definition exits non-zero with a structured
error — surface it and STOP.

### Step 3: `--dry-run` (zero side effects)

If `--dry-run`, render the wave plan as a dry-run box using the shared
`utils/dry_run_output.render_dry_run_preview` renderer (same style as
`orchestrate`), fed by `python3 scripts/workflow_parse.py --dry-run <file>`.
Show stages, fan-out width *if statically known* (else `xN`), the run-wide
ceiling, and per-stage schemas. Spawn no agents; STOP.

### Step 4: Execute via the workflow-engine skill

Invoke the `workflow-engine` skill. It dispatches file-scoped agents wave by
wave under the run-wide semaphore, structurally gates every output (advisory
semantic warnings never block), caches each output under
`.craft/workflow-runs/<run-id>/`, and reconciles the live-agent counter at each
wave boundary.

### Step 5: `--resume <run-id>` (cached replay)

With `--resume`, the skill recomputes cache keys, reuses unchanged stages, and
cascades invalidation downstream of any changed stage. Replay reuses cached
outputs — it does not re-invoke the model for unchanged stages.

### Step 6: Verify gate (authoritative, if present)

A `verify` stage runs the project's **real** verification command; its **exit
status** is the authoritative pass/fail — a green transcript alone is NOT
sufficient.

## Failure semantics

- A single agent's **structural** schema miss fails just that branch (a
  structured error marker); the run continues and `synthesize` receives
  partials.
- An **empty fan-out** (`over` resolves to `[]`) is a **hard error** naming the
  upstream stage — never a silently-skipped stage.

## Run substrate

`.craft/workflow-runs/<run-id>/` (gitignored) holds per-agent output JSON, a
human-readable `manifest.json`, and `semaphore.count`.

The `manifest.json` records the full run identity and is the primary source for
token attribution. It includes:

```json
{
  "run_id": "<ISO8601-start>-workflow",
  "command": "orchestrate:workflow",
  "mode": "workflow",
  "engine": "workflow",
  "agents": ["<agent-label-1>", "<agent-label-2>"],
  "max_turns": <run-wide-ceiling>,
  "cwd": "<absolute-cwd>",
  "start_ts": "<ISO8601>",
  "end_ts": "<ISO8601-or-null>"
}
```

`agents` is populated in dispatch order as agents are spawned. `end_ts` is
written at run completion (success, verify-fail, or hard error).

## See Also

- `/craft:orchestrate` — free-form multi-agent orchestration
- `/craft:orchestrate:drive` — drive an approved SPEC to green
- `workflow-engine` skill — the compile + dispatch + verify body this command calls
- [Run a coded workflow](../../docs/cookbook/recipes/run-a-coded-workflow.md) — cookbook: write a `WORKFLOW-*.yaml`, dry-run preview, execute, resume
- [Fan a workflow across files](../../docs/cookbook/recipes/fan-a-workflow-across-files.md) — cookbook: list → parallel-per-file → gate → summarize pattern
