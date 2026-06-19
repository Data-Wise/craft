---
name: workflow-engine
description: This skill should be used when executing a coded, fixed-control-flow workflow — "run the workflow engine", "execute this WORKFLOW yaml", "run the coded orchestration", decompose→cover→verify→synthesize shapes. Owns the reusable body behind /craft:orchestrate:workflow — compile a WORKFLOW definition to a deterministic wave plan, dispatch file-scoped agents wave by wave under a run-wide semaphore, structurally gate every output, and run a first-class verify gate.
---

# Workflow Engine

The reusable execution body behind `/craft:orchestrate:workflow`. The command
owns args (`--dry-run`, `--resume`, `--refine`); this skill owns the work.

Unlike `drive-engine` (improvises "what next" each turn) the control flow here
is **fixed in the definition** — only the *count* of agents in a `parallel`
stage flexes to upstream data. That determinism is real only because the
mechanical steps are **delegated to `scripts/workflow_parse.py`**, never
improvised. You orchestrate and judge the advisory semantic layer; the Python
core decides everything that must be reproducible.

## Hard rule — delegate the deterministic mechanics

Never eyeball these. Always shell out to the core:

| Mechanic | Call | Decision it owns |
|----------|------|------------------|
| Compile plan | `python3 scripts/workflow_parse.py <file>` | wave order + fan-out shape (D1/D3) |
| Structural gate | `gate_output(data, schema, stage)` | pass/fail per agent output (D2 layer 1) |
| Cache key | `cache_key(stage_block, resolved_input, role_version)` | replay vs re-run (D4) |
| Cascade | `cascade_invalidate(stages, changed, build_deps(plan))` | downstream invalidation (D4) |
| Fan-out | `resolve_fanout(over, upstream_outputs)` | bound items; empty → hard abort (D6) |
| Semaphore | `sem_acquire/sem_release/sem_reconcile` | live-agent ceiling (D5) |

## Agent Prompt Composition (Lever B — prompt-trim)

Every subagent prompt MUST contain exactly three parts — nothing more:

1. **Spec slice** — only the portion of the WORKFLOW definition scoped to THIS
   agent's files/phase. Do NOT pass the entire WORKFLOW-*.yaml to every agent.
   Extract and pass only the stage block(s) the agent needs to execute.

2. **Summarized prior outputs** — a brief structured summary of earlier stage
   results (~200 tokens max per stage). Do NOT include full transcripts or raw
   prior-agent outputs. Derive the summary from the structured return values
   cached in `.craft/workflow-runs/<run-id>/`.

3. **Structured-return instruction** — end every prompt with exactly:

   ```
   Return a concise structured summary:
   { files_changed: [...], tests_run: bool, tests_passed: bool, issues: [...] }
   Do NOT include full file contents or verbose explanations in your response.
   ```

### Anti-patterns (explicitly forbidden)

- **Passing full WORKFLOW-*.yaml to every subagent** — use spec slice instead.
  A 300-line workflow YAML passed to 8 parallel agents = 2400 lines of wasted
  context; the agent needs only its own stage block.
- **Passing raw prior-agent transcripts** — use structured summary instead.
  Transcripts can be 10–50× larger than the information they carry; always
  compress to the structured-return schema before forwarding.
- **Asking for long narrative responses** — use the structured-return instruction
  instead. Narrative responses are unstructured, hard to gate, and inflate
  downstream context for every subsequent agent in the wave.

## Responsibilities

1. **Compile** — run the parser on the `WORKFLOW-*.yaml` (or shape-DSL) file to
   get the canonical wave plan. The YAML and shape-DSL forms compile to an
   identical plan given identical upstream outputs (D1).
2. **Per wave, resolve fan-out** — for a `parallel` stage, call `resolve_fanout`
   against the real upstream outputs. An empty bound array **hard-aborts the
   run** naming the upstream stage (D6/FR8) — never silently skip it.
3. **Dispatch under the semaphore** — for each bound item, `sem_acquire` against
   the run-wide ceiling before launching a file-scoped subagent; refuse (queue)
   when at the ceiling; `sem_release` on completion. The counter is the file
   `semaphore.count`, not context state, so it survives compression (D5).
4. **Gate every output (hybrid, D2)** — `gate_output` returns
   `{ok, structural_errors, semantic_warning}`. `ok=False` (a structural miss)
   **fails just that branch** with a structured marker (failure isolation); the
   run continues and `synthesize` receives partials + error markers. Then judge
   the output's *semantic* plausibility yourself and pass it as
   `semantic_warning` — it is **surfaced but never blocks** (blocking on LLM
   judgment would reintroduce the non-determinism D2 designed out).
5. **Cache / replay (D4)** — write each agent output under
   `.craft/workflow-runs/<run-id>/` keyed by `cache_key`. On `--resume`,
   recompute keys; reuse unchanged stages, and `cascade_invalidate` the
   downstream of any changed stage (derive the dependency graph from the plan
   with `build_deps(plan)` — never hand-trace it). Replay reuses cached outputs — it does
   **not** re-invoke the model for unchanged stages (a fresh `agent` run is not
   byte-identical; the spec never claims otherwise).
6. **Reconcile at each wave boundary** — before opening the next wave, count the
   actually-live agents and `sem_reconcile` the counter to it. This heals a
   leaked count from a mid-run crash between increment and dispatch (the
   accepted D5 residual risk).

## The verify gate (D8 — first class)

A `verify` stage runs the project's **actual** verification command and treats
its **exit status as the authoritative pass/fail**. A green transcript is NOT
sufficient — the command must really run. This is the drive-engine gate lifted
into the engine so `drive` stays expressible as a workflow definition; keep the
semantics a strict superset.

| Detection | Verify command |
|-----------|----------------|
| `tests/test_craft_plugin.py` | `python3 tests/test_craft_plugin.py` |
| `package.json` test script | `npm test` |
| `pyproject.toml` / `pytest.ini` | `pytest` |
| `Cargo.toml` | `cargo test` |
| `DESCRIPTION` (R) | `R CMD check` |

## Run substrate

`.craft/workflow-runs/<run-id>/` holds per-agent output JSON, a human-readable
`manifest.json` (wave-by-wave progress + any semantic warnings), and
`semaphore.count`. All are plain files — inspectable mid-run.

## Outputs

A structured run result: `{ run_id, waves: [...], warnings: [...], verify:
{command, exit_code, passed} | null }`. The skill never opens a PR; on a passing
`verify` it reports verified-green and hands back to the command.

## Cache Strategy and Model Routing (Lever C)

### Cache Strategy (5-min TTL)

Keep the tool set and system prompt **byte-stable** across all agents in a
single run. Claude's prompt cache has a 5-minute TTL; any change to the tool
list or system prompt between agent calls busts the cache and forces a full
re-tokenization of every prior turn.

**Rules:**

- Determine the tool list **once at run start** and hold it constant for the
  entire run. Do NOT add, remove, or reorder tools between agent dispatches.
- If two sequential agents share the same system context, **batch them in the
  same turn** rather than separate sessions. Separate sessions reset the cache
  clock even when the content is identical.
- Target `cache_hit_ratio > 0.5` for runs with more than 3 agents. This is
  measurable via `scripts/orchestrate-token-report.py` after the run completes.

**What busts the cache (avoid these mid-run):**

- Adding a tool that was not in the initial tool list
- Removing a tool from the initial tool list
- Reordering the tool list
- Changing the system prompt text (even whitespace)
- Starting a new session instead of a new turn

### Model Routing (Haiku for cheap stages)

Not every stage needs Sonnet. Route by stage cost:

**Cheap stages → `model: claude-haiku-4-5-20251001`** (10–20× cheaper):

- Grep a file for a pattern
- Count lines or tokens in a file
- Read and summarize a short section (< 200 lines)
- Emit structured JSON from a file under 200 lines

These stages require no reasoning — Haiku handles them correctly and at
dramatically lower cost.

**Reasoning-required stages → session-default model (do not specify `model`)**:

- Architecture decisions
- Multi-file synthesis
- Verify gate semantic judgment
- Any stage requiring cross-file reasoning or prose explanation

**Heuristic:** a stage is "cheap" if:

1. The prompt fits in under 500 tokens, AND
2. The output is simple structured JSON with no prose reasoning required.

When dispatching a cheap agent, add `model: "claude-haiku-4-5-20251001"` to
the agent call. When dispatching a reasoning-required agent, omit `model`
entirely and inherit the session default.

**Routing responsibility:** The workflow-engine skill is responsible for
model routing decisions. The WORKFLOW yaml does NOT specify models — routing
is a runtime concern, not a definition concern.
