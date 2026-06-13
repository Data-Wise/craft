# Tutorial: Coded Workflows with /craft:orchestrate:workflow

> **Run a fixed, schema-gated, resumable orchestration** — define it once in YAML (or the shape-DSL), preview the wave plan, execute it, and resume after an edit.

**Level:** Intermediate
**Time:** 15-20 minutes
**Prerequisites:** Familiarity with `/craft:orchestrate`; a `feature/*` worktree

---

## What You'll Learn

1. When a *coded* workflow beats improvised orchestration
2. The two definition forms (YAML and the frozen shape-DSL)
3. Reading a `--dry-run` wave plan
4. How schema gating and empty-fan-out errors behave
5. Resuming a run from cache after editing one stage

---

## 1. Why a coded workflow?

`/craft:orchestrate` improvises "what next" each turn — great for exploration.
`/craft:orchestrate:workflow` runs a **fixed program**: the control flow is
pinned in the definition, and only the *count* of agents in a `parallel` stage
flexes to upstream data. You get a reproducible wave plan, structural contracts
between stages, and resumable replay.

Reach for it on **known shapes** — the canonical one being a multi-dimensional
review: **decompose → cover each dimension → verify each finding → synthesize**.

---

## 2. The reference workflow

Copy the runnable example:

```bash
cp examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml WORKFLOW-mine.yaml
```

```yaml
name: code-review-sweep
max_concurrent: 16
stages:
  - id: decompose
    type: agent
    role: task-analyzer
    output_schema: { dimensions: "string[]" }
  - id: cover
    type: parallel
    over: ${decompose.dimensions}      # one reviewer per dimension
    agent: { role: reviewer, output_schema: { findings: "object[]" } }
  - id: verify
    type: parallel
    over: ${cover.*.findings}           # flatten findings across reviewers
    fan: 2                              # 2 verifiers per finding
    agent: { role: verifier, output_schema: { confirmed: "boolean" } }
  - id: synthesize
    type: agent
    role: docs-architect
    input: ${verify.*}
```

The same shape in the **frozen shape-DSL** (for fan-out shapes YAML can't
express cleanly) compiles to an identical wave plan:

```js
pipeline(
  agent("decompose", { role: "task-analyzer" }),
  parallel(map("decompose.dimensions", agent("cover", { role: "reviewer" }))),
  parallel(flatMap("cover[].findings", fan(2, agent("verify", { role: "verifier" })))),
  agent("synthesize", { role: "docs-architect" })
);
```

Only `agent`/`parallel`/`pipeline` + `map`/`flatMap`/`flatten` over one bound
array + `fan(N, …)` are allowed — no lambdas, no arbitrary expressions.

---

## 3. Preview the wave plan (always first)

```bash
/craft:orchestrate:workflow --dry-run WORKFLOW-mine.yaml
```

```
DRY RUN: code-review-sweep  (run-wide ceiling: 16)
  1. decompose: agent -> task-analyzer
  2. cover: parallel xN over ${decompose.dimensions} -> reviewer
  3. verify: parallel xN over ${cover[].findings}, fan 2 -> verifier
  4. synthesize: agent -> docs-architect
```

`xN` means the fan-out width is **only known at runtime** (it depends on how
many dimensions `decompose` returns). The dry-run never fabricates a number and
never spawns an agent.

---

## 4. Run it

```bash
/craft:orchestrate:workflow WORKFLOW-mine.yaml
```

The engine executes wave by wave under the run-wide semaphore. For each agent
output it runs the **structural gate** (required keys + types). Two things to
know:

- A **structural miss** fails just that branch (a structured marker) — the run
  continues and `synthesize` receives the partials.
- A **semantic** concern (the model judging "these findings look like TODOs")
  is an advisory **warning that never blocks**.

If a `parallel` stage's `over` resolves to an **empty array**, the run
**hard-aborts**, naming the upstream stage — empty fan-out is treated as an
upstream bug, not a silently-skipped stage.

---

## 5. Resume after an edit

Say you tweak the `verify` stage's role. Re-run from cache:

```bash
/craft:orchestrate:workflow --resume <run-id>
```

The engine recomputes each stage's cache key (a hash of its resolved input +
role-prompt version + definition block). `decompose` and `cover` are unchanged,
so their cached outputs are reused — the model is **not** re-invoked for them.
`verify` changed, so it and everything downstream (`synthesize`) re-run. That's
the cascade: a change to any stage invalidates it and all of its dependents.

---

## 6. Verify gates (optional)

Add a `verify` stage to make a real command the authoritative pass/fail:

```yaml
  - id: gate
    type: verify
    command: python3 tests/test_craft_plugin.py
```

Its **exit status** decides done — a green-looking transcript is never enough.
This is the same gate `/craft:orchestrate:drive` uses, lifted into the engine.

---

## Next Steps

- **Reference:** [/craft:orchestrate:workflow](../commands/orchestrate-workflow.md)
- **Refcard:** [REFCARD-WORKFLOW](../reference/REFCARD-WORKFLOW.md)
- **Compared:** [Orchestrator Modes Compared](orchestrator-modes-compared.md)
- **Recipe:** [Run a coded workflow](../cookbook/recipes/run-a-coded-workflow.md)
