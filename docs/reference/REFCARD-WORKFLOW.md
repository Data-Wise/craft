# Quick Reference: /craft:orchestrate:workflow

**Execute a coded, fixed-control-flow workflow** — schema-gated agents,
data-driven fan-out, cached/resumable replay.

**Status:** Production Ready | **NEW:** third orchestration mode (alongside `orchestrate` and `drive`)

---

## Quick Start

```bash
/craft:orchestrate:workflow --dry-run        # preview wave plan, no agents
/craft:orchestrate:workflow                   # run newest WORKFLOW-*.yaml
/craft:orchestrate:workflow <file>            # run a specific definition
/craft:orchestrate:workflow --resume <run-id> # cached replay of changed stages
/craft:orchestrate:workflow --refine          # refine an NL request first
```

---

## Decision Tree: Which orchestration mode?

```
┌─ How well-defined is the work? ────────────────────────┐
│                                                         │
│  Fixed, repeatable shape                                │
│  (decompose → cover → verify → synthesize)?             │
│    └─> /craft:orchestrate:workflow                      │
│                                                         │
│  One approved spec → drive to green?                    │
│    └─> /craft:orchestrate:drive                         │
│                                                         │
│  Exploratory, can't predict the steps?                  │
│    └─> /craft:orchestrate                               │
│                                                         │
│  Not sure what it will run?                             │
│    └─> /craft:orchestrate:workflow --dry-run            │
│                                                         │
└─────────────────────────────────────────────────────────┘
```

---

## Control-flow primitives

| Primitive | Semantics |
|-----------|-----------|
| `agent` | One subagent, one role, schema-validated JSON out |
| `parallel` | Fan-out; `over` binds an upstream array → N agents; empty → **hard error** |
| `pipeline` | Sequential stages; each output feeds the next |
| `loop` | Repeat a stage until a condition clears (`max_iter` bound) |
| `verify` | First-class gate: runs a real command, **exit status authoritative** |

---

## Schema dialect (v1)

Constrained on purpose so a stdlib validator checks it without `jsonschema`:

| Allowed | Example |
|---------|---------|
| primitives | `string`, `number`, `boolean` |
| homogeneous arrays | `string[]`, `number[]`, `boolean[]`, `object[]` |
| required keys | every declared key is required |

**Not in v1:** `oneOf`, regex `pattern`, conditional subschemas.

---

## Two-layer validation

| Layer | Who | Gating? |
|-------|-----|---------|
| **Structural** | Python stdlib | **Yes** — a miss fails that branch |
| **Semantic** | the model | No — advisory warning only |

---

## Run cache (`.craft/workflow-runs/<run-id>/`, gitignored)

| File | Purpose |
|------|---------|
| `<agent>.json` | per-agent output, cache-keyed |
| `manifest.json` | human-readable wave-by-wave progress + warnings |
| `semaphore.count` | run-wide live-agent counter (survives compression) |

Cache key = hash of `{resolved input + role-prompt version + definition block}`;
a change cascades downstream invalidation. `--resume` re-runs only what changed.

---

## See Also

- Command: [/craft:orchestrate:workflow](../commands/orchestrate-workflow.md)
- Tutorial: [TUTORIAL-orchestrate-workflow](../tutorials/TUTORIAL-orchestrate-workflow.md)
- Compared: [Orchestrator Modes Compared](../tutorials/orchestrator-modes-compared.md)
