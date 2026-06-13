# ORCHESTRATE: Deterministic Workflow Engine

> **Working artifact** — lives on `feature/workflow-engine`, deleted at merge. Do NOT carry to `dev`.

**Spec:** `docs/specs/SPEC-workflow-engine-2026-06-12.md` (INTERROGATED, 8 decisions locked)
**Branch:** `feature/workflow-engine` (worktree: `~/.git-worktrees/craft/feature-workflow-engine`)
**Base:** `dev` @ `107ec13f`
**Goal:** Add a third orchestration mode `/craft:orchestrate:workflow` — code-driven `parallel`/`pipeline`/`loop`/`verify` control flow with stdlib-enforced structural schemas, data-driven fan-out, and cached/resumable replay.

---

## ⛔ START HERE (read before coding)

This plan was scaffolded from the planning session. **Implementation runs in THIS worktree session** (you are reading this because you `cd`'d here and started a fresh `claude`). Before increment 1:

1. Confirm CWD + branch: `pwd` → `.../feature-workflow-engine`, `git branch --show-current` → `feature/workflow-engine`.
2. Rebase on latest dev (worktree was branched at `107ec13f`): `git fetch origin && git rebase origin/dev`.
3. Read the spec end-to-end — the Resolved Decisions table (D1–D8) is binding; don't relitigate it.

---

## Locked decisions (binding — from spec interrogation 2026-06-12)

| # | Decision | Implementation consequence |
|---|----------|----------------------------|
| D1 | Conditional determinism | Wave plan reproducible *given identical upstream outputs*; agent outputs are NOT byte-stable. Don't over-claim. |
| D2 | Hybrid schema | Stdlib structural check = **gating**; LLM semantic check = **advisory, never blocks**. |
| D3 | Frozen shape-DSL | Whitelist only: `agent`/`parallel`/`pipeline` + `map`/`flatMap`/`flatten` over ONE bound array + `fan(N,...)`. No lambdas, no chaining, no arbitrary expressions. |
| D4 | Cache key | Content hash of `{resolved stage input + role-prompt version + definition stage block}`; change cascades downstream invalidation. |
| D5 | Run-wide semaphore | File-backed counter (`semaphore.count`), NOT context state — survives compression. |
| D6 | Empty fan-out | Hard error, names the upstream stage. |
| D7 | Mode discovery | task-analyzer routes known-shape phrasing to a **suggestion**, not a silent switch. |
| D8 | drive convergence | First-class `verify` gate; engine must stay a strict superset of drive-engine. |

**Dialect constraint:** v1 supports `required` keys, primitives (`string`/`number`/`boolean`), homogeneous arrays (`string[]`/`object[]`) only. NO `oneOf`, regex `pattern`, conditional subschemas (stdlib must validate without `jsonschema`).

---

## Increments (dependency-ordered, TDD per the test-driven-development skill)

### Increment 1 — Mechanical core (parser + schema) ⚡ highest-value TDD target

- `commands/orchestrate/_workflow_schema.json` — constrained dialect (D2 keys + primitives + homogeneous arrays).
- `scripts/workflow_parse.py` (**stdlib only** — no `jsonschema`, no node):
  - YAML form + shape-DSL form → identical wave-plan JSON given fixed inputs (D1, D3).
  - Structural validator (gating, D2 layer 1).
  - Cache-key hash (D4) with downstream cascade.
  - Semaphore-file arithmetic (D5).
- **Verify gate:** `tests/test_workflow_engine.py` red→green for: both forms→identical plan; structural miss hard-stops; empty `over:`→abort naming upstream (D6); cache-key invalidation cascades; semaphore ceiling math. **Run the FULL `pytest tests/`**, not a subset (CI runs ~1700).

### Increment 2 — Skill executor

- `skills/orchestration/workflow-engine/SKILL.md` — prompt-driven executor (no runtime dep, like `drive-engine`): consume wave plan → dispatch file-scoped agents → structural-gate + semantic-warn → cache/replay → semaphore increment/decrement → reconcile counter at each wave boundary (residual-risk mitigation).
- Must expose a first-class **`verify` gate** (D8): runs a real project command, exit status authoritative (green transcript insufficient).
- **Verify gate:** dry-run of the example workflow emits a sane wave plan; semantic-warn path proven non-blocking.

### Increment 3 — Thin command

- `commands/orchestrate/workflow.md` — `/craft:orchestrate:workflow`; owns args, `--dry-run`/`-n`, `--resume <run-id>`, `--refine` (FR6 parity); delegates to skill.
- `.gitignore` += `.craft/workflow-runs/`.
- **Verify gate:** `--dry-run` box matches existing `orchestrate` style; frontmatter valid (command-audit clean).

### Increment 4 — Router integration (D7)

- Edit `skills/orchestration/task-analyzer/SKILL.md`: detect decompose→cover→verify→synthesize phrasing → **suggest** `:workflow` (confirm-before-switch, per routing-false-positive mitigation). Do NOT silently hijack.
- **Verify gate:** routing suggestion fires on known shape, stays silent otherwise.

### Increment 5 — Example, convergence test, docs + counts

- `examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml` — the spec's runnable 5-dim review case.
- Contract test: drive-engine's verify-gate semantics reproducible via a `verify` stage (D8 convergence guard).
- Count bumps: `+1 command` (109→110), `+1 skill` (38→39) across `plugin.json` / `CLAUDE.md` — run `./scripts/validate-counts.sh` to confirm. **NOTE the parallel-branch count footgun:** if another feature lands counts first, rebase and re-derive — don't naive `+1`.
- Docs surface (spec **FR9**, ship-blocking — mirror the `orchestrate:drive` set): `docs/tutorials/TUTORIAL-orchestrate-workflow.md`; update `docs/tutorials/orchestrator-modes-compared.md` (2→3 modes); `docs/commands/orchestrate-workflow.md` + `docs/help/orchestrate-workflow.md`; REFCARD entry in `docs/REFCARD.md` + dedicated `docs/reference/REFCARD-WORKFLOW.md`; `docs/cookbook/recipes/run-a-coded-workflow.md`; new skill row in `docs/skills-agents.md`; `mkdocs.yml` nav; `commands/smart-help.md` entry (hub auto-discovers via frontmatter). CHANGELOG `[Unreleased]`. Run `./scripts/docs-staleness-check.sh`.
- **Verify gate:** `./scripts/validate-counts.sh` ✓ AND full `pytest tests/` green AND `/craft:check` clean before PR.

---

## File map (spec "Artifacts to Build")

| Artifact | Path | Increment |
|----------|------|-----------|
| Schema | `commands/orchestrate/_workflow_schema.json` | 1 |
| Parser | `scripts/workflow_parse.py` | 1 |
| Tests | `tests/test_workflow_engine.py` | 1 (grows through 5) |
| Skill | `skills/orchestration/workflow-engine/SKILL.md` | 2 |
| Command | `commands/orchestrate/workflow.md` | 3 |
| Router edit | `skills/orchestration/task-analyzer/SKILL.md` | 4 |
| Example | `examples/workflow-code-review/WORKFLOW-code-review-sweep.yaml` | 5 |

---

## Accepted residual risks (carry into implementation)

- **Semaphore fragility (D5):** mid-run crash between increment and dispatch leaks a count → reconcile against live-agent manifest at each wave boundary.
- **Convergence debt (D8):** `verify` primitive + phase model must stay a strict superset of drive-engine → contract test in increment 5.
- **Routing false positives (D7):** suggest, never silently switch.

---

## Done = all true

- [ ] All 7 artifacts built; full `pytest tests/` green (re-run after each fix).
- [ ] `validate-counts.sh` ✓ (110 cmds / 39 skills) and `/craft:check` clean.
- [ ] Both definition forms produce identical wave plans on fixed inputs (D1).
- [ ] Structural miss hard-stops; semantic warn does not block (D2).
- [ ] Empty fan-out hard-aborts naming upstream (D6); replay cache cascade proven (D4).
- [ ] drive-engine verify-gate convergence contract test passes (D8).
- [ ] CHANGELOG `[Unreleased]` + docs synced.
- [ ] **Delete this ORCHESTRATE file before merging to dev** (working artifact only).
