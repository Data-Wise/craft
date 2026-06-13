# /craft:orchestrate:workflow

> **Execute a coded, fixed-control-flow workflow — `parallel` / `pipeline` / `loop` / `verify` with schema-gated agents, data-driven fan-out, and cached/resumable replay.**

---

## Synopsis

```bash
/craft:orchestrate:workflow [workflow] [flags]
```

**Quick examples:**

```bash
# Preview the wave plan (stages, fan-out, ceiling) — zero side effects
/craft:orchestrate:workflow --dry-run

# Run the newest WORKFLOW-*.yaml in the worktree root
/craft:orchestrate:workflow

# Run a specific definition
/craft:orchestrate:workflow examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml

# Replay a prior run from cache, re-running only changed stages
/craft:orchestrate:workflow --resume 2026-06-13-a1b2
```

---

## Which orchestration mode?

| Mode | Control model | Best for |
|------|---------------|----------|
| `/craft:orchestrate` | LLM improvises each turn | exploratory work |
| `/craft:orchestrate:drive` | drive an approved SPEC to green | spec → done |
| **`/craft:orchestrate:workflow`** | **fixed coded program** | known shapes: decompose → cover N → verify M → synthesize |

`workflow` fixes the control flow in the definition; only the *count* of agents
in a `parallel` stage flexes to upstream data.

---

## Flags

| Argument / Flag | Required | Default | Purpose |
|---|---|---|---|
| `workflow` (positional) | no | newest `WORKFLOW-*.yaml` in worktree root | Definition to run (YAML or shape-DSL). |
| `--dry-run` / `-n` | no | false | Print the wave plan without spawning agents. |
| `--resume <run-id>` | no | — | Replay from cache; re-run only stages whose cache key changed (and downstream). |
| `--refine` | no | false | Pre-process a natural-language request through `prompt-refiner` before synthesizing a definition. |

---

## Definition forms

A workflow is defined either as declarative **YAML** (`WORKFLOW-*.yaml`) or as a
frozen **shape-DSL** for fan-out shapes YAML can't express cleanly. Both compile
to an **identical wave plan** given identical upstream outputs.

```yaml
# YAML form
stages:
  - id: decompose
    type: agent
    role: task-analyzer
    output_schema: { dimensions: "string[]" }
  - id: cover
    type: parallel
    over: ${decompose.dimensions}      # data-driven fan-out
    agent: { role: reviewer, output_schema: { findings: "object[]" } }
```

```js
// shape-DSL form (whitelisted vocabulary only — not arbitrary JS)
pipeline(
  agent("decompose", { role: "task-analyzer" }),
  parallel(map("decompose.dimensions", agent("cover", { role: "reviewer" })))
);
```

The shape-DSL permits only `agent`/`parallel`/`pipeline` + `map`/`flatMap`/`flatten`
over **one** bound array, plus `fan(N, …)`. No lambdas, no chaining, no arbitrary
expressions — a stdlib parser reads it to a wave plan deterministically.

---

## Schema-gated output (hybrid)

Each agent stage declares an `output_schema`. Validation is two-layer:

- **Structural (gating, deterministic):** a stdlib check of required keys,
  primitive types, and homogeneous array types. A miss **fails just that
  branch** with a structured error — never a silent parse-guess.
- **Semantic (advisory, non-gating):** the model judges plausibility and may
  emit a **warning that never blocks**.

An **empty fan-out** (`over` resolves to `[]`) is a **hard error** naming the
upstream stage that produced it.

---

## Conditional-deterministic replay

Each run gets a `run-id`; per-agent outputs are cached under
`.craft/workflow-runs/<run-id>/`. The cache key is a content hash of
`{resolved stage input + agent role-prompt version + definition stage block}`;
any change invalidates that stage and cascades downstream. `--resume` reuses
unchanged stages and re-runs only what changed. Replay reuses cached outputs —
it does **not** re-invoke the model for unchanged stages.

---

## v1 limitations

- **Concurrency is enforced at runtime, not predicted.** The run-wide semaphore
  (D5) throttles live agents during execution; the dry-run does **not** yet warn
  when a statically-knowable max could exceed the ceiling (v1 fan-out is always
  data-driven, so width is unknown until runtime).
- **`loop` is represented, not yet executed.** A `loop` stage compiles and
  carries its `max_iter`, but iterate-until-condition semantics live in the
  skill prose; full loop execution is future work.
- **Shape-DSL `agent("id")` requires an options object** (e.g.
  `agent("id", { role: "…" })`); a bare `agent("id")` is a grammar error.

## See Also

- `/craft:orchestrate` — free-form multi-agent orchestration
- `/craft:orchestrate:drive` — drive an approved SPEC to green
- `workflow-engine` skill — the compile + dispatch + verify body this command calls
- Tutorial: `TUTORIAL-orchestrate-workflow.md`
