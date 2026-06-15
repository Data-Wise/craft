# Deterministic Workflow Engine — Spec

**Generated:** 2026-06-12
**Context:** Craft Plugin v2.35.0 — adds a third orchestration mode
**Sources:** Codebase analysis (`commands/orchestrate/`, `skills/orchestration/`), session comparison doc (Workflow tool vs. `/craft:orchestrate`)
**Status:** done — SHIPPED in v2.36.0 (PR #148 → main `eb7e143d`, 2026-06-13); includes B1/B2 review hardening

---

## Resolved Decisions (interrogation 2026-06-12)

| # | Question | Decision |
|---|----------|----------|
| D1 | What does "deterministic" mean? | **Conditional determinism** — wave plan is reproducible *given identical upstream outputs*; agent outputs are not. Determinism is a property of the plan + cache, not the executor. |
| D2 | Schema enforcement | **Hybrid** — Python stdlib enforces structure (keys + primitive types + arrays-of), deterministic and **gating**. LLM judges semantic plausibility, **advisory only, never blocks**. |
| D3 | JS escape-hatch | **Frozen shape-DSL** — whitelisted vocabulary only (`agent`/`parallel`/`pipeline` + `map`/`flatMap`/`flatten` over a single bound array). Stdlib-parseable. No arbitrary expressions. Preserves D1. |
| D4 | Cache key | **Full content hash** of `{resolved stage input + agent role-prompt version + definition stage block}`. Any change cascades downstream invalidation. |
| D5 | Concurrency | **Run-wide semaphore**, materialized as a **counter file** under the run dir (not held in executor's context — survives compression). |
| D6 | Empty fan-out | **Hard error** — empty `over:` array aborts the run. |
| D7 | Mode discovery | **task-analyzer auto-routes** known-shape phrasing (decompose→cover→verify→synthesize) to `:workflow`. |
| D8 | drive-engine relationship | **Design for convergence** — workflow-engine is a superset; drive-engine eventually expressible as a workflow definition. Requires a first-class `verify` gate stage. |

---

## Executive Summary

**BLUF:** Craft has two orchestration modes, both **model-driven**. This spec adds a third, **code-driven** mode: deterministic `parallel`/`pipeline`/`loop` control flow with schema-validated JSON per agent, data-driven fan-out, and cached/resumable replay by run-ID.

**The three modes after this lands:**

- **`/craft:orchestrate`** — LLM improvises the orchestration (reasons "what next" each turn). Best for exploratory work.
- **`/craft:orchestrate:drive`** — drives an approved SPEC to done via `drive-engine`. Best for spec → green.
- **`/craft:orchestrate:workflow`** *(NEW)* — executes a **fixed control-flow program**; only fan-out *volume* flexes to data. Best for known-shape work: decompose → cover N → verify M → synthesize.

**Why a separate mode, not a flag:** improvised vs. coded orchestration are different control models. A `--workflow` flag on `orchestrate` would collide with its `status`/`continue`/`compress` verbs and muddy the conceptual line. This mirrors how `drive` already branched off as its own subcommand + skill.

**Design choices (locked):**

- **Definition:** hybrid — declarative `WORKFLOW-*.yaml` for simple shapes; **frozen shape-DSL** (`agent`/`parallel`/`pipeline` + `map`/`flatMap`/`flatten` over one bound array) for dynamic fan-out. Whitelisted vocabulary, stdlib-parseable — *not* arbitrary JS (D3).
- **Executor:** pure prompt/markdown — the skill instructs Claude to act as the deterministic executor (no runtime dependency), consistent with `drive-engine`.
- **Split:** thin command `commands/orchestrate/workflow.md` → reusable skill `skills/orchestration/workflow-engine/SKILL.md`.

---

## Open Questions (resolved — see Resolved Decisions table)

All five original open questions plus three interrogation targets were
resolved in the 2026-06-12 interrogation. Residual implementation notes:

- **Cache substrate:** `.craft/workflow-runs/<run-id>/` — per-agent JSON, a
  human-readable `manifest.json`, and `semaphore.count` (D5). Add
  `.craft/workflow-runs/` to `.gitignore`.
- **Schema dialect (D2):** constrained subset only — `required` keys,
  primitive types (`string`/`number`/`boolean`), and homogeneous arrays
  (`string[]`, `object[]`). **No** `oneOf`, regex `pattern`, or conditional
  subschemas in v1 (stdlib must check it without `jsonschema`).

---

## Functional Requirements

### FR1 — Workflow definition (hybrid)

**YAML form** (`WORKFLOW-<name>.yaml` in worktree root):

```yaml
name: code-review-sweep
version: 1
inputs:
  target: { type: string, required: true }
stages:
  - id: decompose
    type: agent
    role: task-analyzer
    output_schema: { dimensions: "string[]" }
  - id: cover
    type: parallel
    over: ${decompose.dimensions}      # data-driven fan-out
    max_concurrent: 16
    agent: { role: reviewer, output_schema: { findings: "object[]" } }
  - id: verify
    type: parallel
    over: ${cover.*.findings}           # fan-out flexes to N findings
    fan: 2                              # 2 verifiers per finding
    agent: { role: verifier, output_schema: { confirmed: boolean } }
  - id: synthesize
    type: agent
    role: docs-architect
    input: ${verify.*}
```

**Shape-DSL form** (D3 — whitelisted vocabulary, *not* arbitrary JS; for fan-out shapes YAML can't express cleanly):

```js
pipeline(
  agent("decompose", { role: "task-analyzer" }),
  parallel(
    map("decompose.dimensions",        // bind ONE upstream array
        agent("cover", { role: "reviewer" }))),
  parallel(
    flatMap("cover[].findings",        // flatten one level, then fan
            fan(2, agent("verify", { role: "verifier" })))),
  agent("synthesize", { role: "docs-architect" })
);
```

Only `map`/`flatMap`/`flatten` over a **single named array path** plus `fan(N, ...)` are permitted. No method chaining, no lambdas, no arbitrary expressions — a stdlib parser reads it to a wave plan deterministically.

**Acceptance:** the executor reads either form and emits an identical wave plan **given identical upstream outputs** (D1 — conditional determinism; statically-known shapes are unconditionally identical, data-driven shapes are identical only when the upstream array is held fixed).

### FR2 — Control-flow primitives

| Primitive | Semantics |
|-----------|-----------|
| `agent` | One subagent, one role, schema-validated JSON out |
| `parallel` | Fan-out; `over` binds to upstream array → N agents; `max_concurrent` caps wave width. Empty `over` → **hard error** (D6) |
| `pipeline` | Sequential stages; each stage's output is the next's input |
| `loop` | Repeat a stage until a `/goal`-style condition clears (bounded by `max_iter`) |
| `verify` | **(D8)** First-class gate: runs a real project command, treats exit status as authoritative pass/fail. A green transcript is not sufficient. This is the drive-engine gate lifted into the engine so `drive` is eventually expressible as a workflow definition. |

Control flow is **fixed in the definition**; only the *count* of agents in a `parallel` stage is determined at runtime from upstream data.

### FR3 — Schema-enforced output (hybrid, D2)

Each agent stage declares `output_schema`. Validation is **two-layer**:

1. **Structural (gating, deterministic):** a Python stdlib check verifies `required` keys, primitive types, and homogeneous array types. A structural miss is a **hard stop** with a structured error — no silent parse-guessing. This is the layer that makes the stage-to-stage contract real and D1 holdable.
2. **Semantic (advisory, non-gating):** the LLM judges plausibility (e.g. "does this `findings` array actually describe findings?"). It may emit a warning but **must not block** — blocking on LLM judgment would reintroduce the non-determinism D1/D2 designed out.

Schema dialect is constrained (see Open Questions note): no `oneOf`, regex, or conditional subschemas in v1.

### FR4 — Conditional-deterministic replay (D1, D4)

- Each run gets a `run-id`. Per-agent outputs cached under `.craft/workflow-runs/<run-id>/`.
- **Cache key (D4):** content hash of `{resolved stage input + agent role-prompt version + definition stage block}`. A change to any of the three invalidates that stage **and cascades to all downstream stages**.
- `--resume <run-id>` replays from cache, re-running only stages whose key changed.
- **Determinism claim (precise):** replay reuses cached outputs (so a resumed run does not re-invoke the model for unchanged stages); the **wave plan** is reproducible given identical upstream outputs. Fresh re-execution of an `agent` stage is **not** byte-identical — agent outputs are non-deterministic by construction. The spec does not claim otherwise.

### FR7 — Run-wide concurrency semaphore (D5)

- A single run-wide ceiling caps total simultaneously-live agents across all waves (not merely within one stage).
- The counter is materialized as a file (`.craft/workflow-runs/<run-id>/semaphore.count`) that the executor increments before dispatch and decrements on completion — **not** a number held in the executor's context, so it survives chat compression mid-run.
- At `--dry-run`, if a plan's *statically-known* maximum live-agent count could exceed the ceiling, warn; data-driven fan-out that can only be known at runtime is throttled by the live counter.

### FR8 — Empty fan-out is a hard error (D6)

A `parallel`/`map`/`flatMap` whose bound array resolves to empty **aborts the run** with a structured error identifying the upstream stage that produced the empty array. Empty fan-out is treated as an upstream bug, not a silently-skipped stage.

### FR5 — Dry-run

`--dry-run` / `-n` prints the wave plan (stages, fan-out width *if statically known*, concurrency, schemas) without spawning agents — matching the existing `orchestrate` dry-run box style.

### FR6 — `--refine` parity

Support `--refine` to pre-process a natural-language workflow request through `prompt-refiner` before synthesizing a definition, consistent with other craft commands.

### FR9 — Documentation & discoverability (ship-blocking)

The mode is **not "done" until discoverable and documented** across craft's standard surface, mirroring exactly what `/craft:orchestrate:drive` shipped. Each item below is required, not optional:

- **Help hub / discovery:** command auto-appears in `/craft:hub` via valid frontmatter (`_discovery.py`) — verify it surfaces; add a curated entry to `commands/smart-help.md` so context-aware help suggests it.
- **Modes comparison (REQUIRED update):** `docs/tutorials/orchestrator-modes-compared.md` goes from **two modes to three** (`orchestrate` / `drive` / `workflow`) with a "when to use which" table. Also touch `docs/orchestrator.md`, `docs/guide/orchestrator.md`, `docs/guide/pipeline-orchestrate-guide.md`.
- **Tutorial:** `docs/tutorials/TUTORIAL-orchestrate-workflow.md` — hands-on walkthrough (YAML + shape-DSL forms, `--dry-run`, `--resume`).
- **Command + help reference pages:** `docs/commands/orchestrate-workflow.md` and `docs/help/orchestrate-workflow.md` (mirror the `orchestrate-drive` pair).
- **REFCARD:** add `/craft:orchestrate:workflow` to the command tables in `docs/REFCARD.md`; add a dedicated `docs/reference/REFCARD-WORKFLOW.md` (precedent: `REFCARD-CHECK.md`, `REFCARD-BRAINSTORM.md`).
- **Cookbook recipe:** `docs/cookbook/recipes/run-a-coded-workflow.md` (precedent: `drive-a-spec-to-green.md`).
- **Catalog + nav:** add the new skill row to `docs/skills-agents.md`; add new pages to `mkdocs.yml` nav.
- **CHANGELOG + counts:** `[Unreleased]` entry; bump command/skill counts (`plugin.json`, `CLAUDE.md`) and confirm `validate-counts.sh` ✓.

**Acceptance:** `/craft:hub` lists the command; modes-compared shows three modes; tutorial + command/help pages + REFCARD entry exist; `docs-staleness-check.sh` and `/craft:check` are clean.

---

## Non-Functional Requirements

- **No new *hard* runtime deps** — executor is markdown-prompt-driven; the only mechanical pieces are Python **stdlib** (structural schema check D2, hash/cache D4, semaphore-file arithmetic D5). No `jsonschema`, no node.
- **Concurrency safety** — run-wide live-agent ceiling enforced via semaphore file (FR7); refuse plans whose static max exceeds it.
- **Observability** — wave-by-wave progress; `manifest.json` + `semaphore.count` are human-readable.
- **Failure isolation** — one agent's *structural* schema miss or error fails its branch with a structured result, not the whole run; synthesize stage receives partials + error markers. (Empty fan-out is the exception — hard-aborts per FR8.)

---

## Artifacts to Build (post-review)

| Artifact | Path | Role |
|----------|------|------|
| Skill | `skills/orchestration/workflow-engine/SKILL.md` | Reusable executor: parse YAML/shape-DSL → wave plan → dispatch file-scoped agents → structural-validate (gating) + semantic-warn → cache/replay → semaphore. Must expose a `verify` gate (D8). |
| Command | `commands/orchestrate/workflow.md` | Thin entry `/craft:orchestrate:workflow`; owns args, `--dry-run`, `--resume <run-id>`, `--refine`; delegates to skill |
| Schema | `commands/orchestrate/_workflow_schema.json` | Constrained dialect for `WORKFLOW-*.yaml` (required keys + primitives + homogeneous arrays only, D2) |
| Parser | `scripts/workflow_parse.py` (stdlib only) | YAML/shape-DSL → wave-plan JSON; structural validator; hash/cache key; semaphore arithmetic |
| Router edit | `skills/orchestration/task-analyzer/SKILL.md` | Add known-shape detection → route to `:workflow` (D7) |
| Tests | `tests/test_workflow_engine.py` | Both forms → identical plan (fixed inputs); structural miss hard-stops; semantic warn does NOT block; empty fan-out aborts; replay cache-key invalidation cascade; dry-run output; semaphore ceiling |
| Example | `examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml` | The doc's 5-dim review case, runnable |

---

## Residual Risks (accepted, post-interrogation)

- **Semaphore fragility (D5):** a prompt-driven executor maintaining a file-backed global counter across waves is the highest-risk mechanism. Mitigated by making it a file, not context state, but a mid-run crash between increment and dispatch can leak a count. *Mitigation: reconcile counter against live-agent manifest at each wave boundary.*
- **Convergence debt (D8):** committing now to "drive becomes a workflow definition" means the `verify` primitive and phase model must stay a strict superset of drive-engine. If they drift, the convergence promise silently breaks. *Mitigation: a contract test asserting drive-engine's verify-gate semantics are reproducible via a `verify` stage.*
- **Routing false positives (D7):** auto-routing "decompose/cover/verify/synthesize" phrasing to `:workflow` may hijack tasks better served by improvised `orchestrate`. *Mitigation: route to a suggestion, not a silent switch — confirm before committing to the coded path.*
