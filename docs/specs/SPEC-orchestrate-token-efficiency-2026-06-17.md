# SPEC: Orchestrate Token-Efficiency (Measure-First)

**Status:** draft
**Created:** 2026-06-17
**From Brainstorm:** interactive `/workflow:refine` session — token-usage investigation (orchestrate vs. parallel worktrees vs. large context) → evidence-backed optimization design
**Author:** dt + Claude

---

## Overview

Review sessions flagged high token usage attributed to orchestrate, parallel
worktrees, and large context. A prior investigation (repo evidence + Anthropic's
published multi-agent numbers) found the true driver is a **structural multiplier** —
`agents × inherited-context × loop-turns` — that orchestrate *amplifies* but does not
uniquely create. Parallel **worktrees contribute zero token cost** (isolation only).
The silent tax underneath is the **~5,200-token context floor** (root `CLAUDE.md` +
`craft/CLAUDE.md` + `MEMORY.md`) that every subagent inherits.

This spec optimizes orchestrate's token usage under a strict **measure → apply →
re-measure → prove** discipline: instrument first, then apply only levers whose savings
are demonstrated against a baseline. No lever ships without a number.

### Goal & non-goals

- **Goal:** reduce orchestrate's token usage, with each change validated by measured deltas.
- **Out of scope (explicit):** loop/turn caps & budget cutoffs; agent/skill architecture
  consolidation (`orchestrator.md` vs `orchestrator-v2.md`); migrating orchestrate's
  dispatch engine to the `Workflow` tool; and `/done`-based CLAUDE.md/memory hygiene
  (→ `SPEC-context-floor-hygiene-2026-06-17.md`).

---

## Primary User Story

**As a** craft user running orchestrate workflows,
**I want** orchestrate to cost measurably fewer tokens without losing capability,
**so that** multi-agent runs stay affordable and I can *see* where tokens go and prove
each optimization actually helped.

### Acceptance Criteria

- A read-only token report exists that attributes real token usage (input/output/cache)
  to an individual orchestrate run and to each subagent.
- A documented baseline exists for one representative reference task.
- Each shipped lever (A, B, C) has a recorded, non-negative measured delta vs. baseline.
- No change couples into the LLM loop such that a parser failure breaks an orchestrate run.

---

## Phase Spine & Branch Routing

A strict measure-first loop. Phase 0 lands first; each lever is validated independently
against the Phase 0 baseline.

| Phase | Work | Branch | Why |
|---|---|---|---|
| **0 — Instrument** | `scripts/orchestrate-token-report.py` (read-only parser) + run-marker emission in `commands/orchestrate.md` / `commands/orchestrate/drive.md` | **worktree** | New script is a *new file* (blocked on `dev`); marker emission is feature behavior |
| **A — Context-floor trim** | Trim `MEMORY.md` (~21 KB / 105 entries), root `dev-tools/CLAUDE.md`, `craft/CLAUDE.md` | **`dev` / no-commit** | `MEMORY.md` + root CLAUDE.md are outside the craft git repo; `craft/CLAUDE.md` is an existing file → `dev`-safe. Ships immediately |
| **B — Prompt-level scoping** | Rewrite subagent prompt-builder: spec slice + summarized prior outputs + structured returns | **worktree** | Feature behavior change |
| **C — Cache + model routing** | Byte-stable tool set/prompt + batch turns (exploit 5-min cache TTL); Haiku for cheap file-scoped stages | **worktree** | Feature behavior change |

**Consequence:** Lever A can ship today on `dev` for an instant, measurable win. Phase 0 +
Levers B/C share one feature worktree (`feature/orchestrate-token-efficiency`).

---

## Phase 0 — Components & Data Flow (the heart)

### Run markers

Orchestrate writes a tiny JSON marker at run start, updates it at end:

```
.flow/orchestrate-runs/<run-id>.json
  { run_id, command, mode, agents, max_turns, cwd, start_ts, end_ts }
```

- `run-id` = `<start_ts>-<mode>`.
- Marker directory: **`.flow/orchestrate-runs/`** (decision; `.flow/` already used elsewhere
  in the ecosystem, e.g. `teach-config.yml`).

### Parser — `scripts/orchestrate-token-report.py`

Read-only. **Never writes to `~/.claude`.** Steps:

1. Resolve the session transcript dir from `cwd` (the `~/.claude/projects/<slug>/` mapping).
2. Slice session JSONL messages to the `[start_ts, end_ts]` window from the marker.
3. Sum ground-truth `usage` fields: `input_tokens`, `output_tokens`,
   `cache_creation_input_tokens`, `cache_read_input_tokens`.
4. Locate `agent-*.jsonl` in the transcript dir for **per-agent** attribution.
5. Emit a report: per-run totals, per-agent breakdown, and a **cache-hit ratio**
   (`cache_read / (input + cache_read)`) — the headline number for Lever C.
   `--json` for machine output.

### Data flow

```
orchestrate run → marker(start) → … agents … → marker(end)
  → orchestrate-token-report.py <run-id>  → reads JSONL (ground truth) → table
```

No coupling into the LLM loop; if the parser breaks, orchestrate is unaffected.

### Ground-truth basis

Claude Code already writes per-message `usage` to `~/.claude/projects/**/*.jsonl`
(verified): `input_tokens`, `output_tokens`, `cache_creation_input_tokens`,
`cache_read_input_tokens`, plus `server_tool_use` web counts. Worktrees get their own
project transcript dirs; subagents write `agent-*.jsonl`. So Phase 0 is a **read-only
parser over existing logs**, not in-loop telemetry. No OTEL is configured.

---

## Levers (each: apply → re-measure → prove)

### Lever A — Context-floor trim (docs)

Trim the ~5,200-token floor inherited by every subagent: curate `MEMORY.md` (105 entries
→ leaner index), de-duplicate the root `dev-tools/CLAUDE.md`, tighten `craft/CLAUDE.md`.
**Validate:** measured drop in inherited context size and in per-agent input tokens on the
reference task.

### Lever B — Prompt-level scoping (chosen approach)

Rewrite how orchestrate builds each subagent prompt: pass a **spec slice** (not the whole
spec), **summaries** of prior agent outputs (not full transcripts), and require concise /
structured returns. Stays within harness constraints (cannot suppress auto-loaded
`CLAUDE.md` — that is Lever A's job). **Validate:** per-agent input tokens drop; net run
tokens down.

> Alternatives considered and rejected for this spec: *cwd-aware dispatch* (fights
> documented harness behavior — subagents inherit session cwd, don't re-walk) and
> *migrate fan-out to the `Workflow` tool* (engine rewrite; belongs to the deferred
> architecture-consolidation goal — see `SPEC-workflow-as-default-engine-2026-06-17.md`).

### Lever C — Cache + model routing

Keep the tool set and system prompt **byte-stable** across a run and **batch turns** to
exploit prompt caching (cache hits cost ~90% less; Claude Code's cache TTL is now 5 min,
so long interactive pauses blow it). Route cheap file-scoped stages to **Haiku** (~5×
cheaper). **Validate:** cache-read ratio increases; cheap stages show Haiku usage; cost down.

---

## Relationship to Dynamic Workflows & Worktrees

This is an explicit boundary note so future readers don't assume these specs already chose
an engine.

- **These plans do NOT make the `Workflow` tool the default.** Lever B uses prompt-level
  scoping, not engine migration. However, **Phase 0 measurement is engine-agnostic** (the
  parser reads `usage` from Task agents *and* `Workflow` agents alike), so it is the
  prerequisite that makes a future, **evidence-based** "Workflow-as-default" decision
  possible. Levers B and C also backport advantages the `Workflow` tool has natively
  (per-agent scoped context, `schema` summaries, `model` routing, `budget`). That future
  decision is **out of scope here** → `SPEC-workflow-as-default-engine-2026-06-17.md`.
- **Execution worktrees are orthogonal to this spec's goal.** `--swarm` / the `Workflow`
  tool's `isolation:'worktree'` provide *file-write isolation*, not token savings (worktrees
  cost zero tokens). They scale with **parallel writes**, not with using dynamic workflows.
- **Worktrees are NOT necessary for dynamic workflows.** In the `Workflow` tool, worktree
  isolation is opt-in per-agent, needed only when multiple agents write the same files in
  parallel; read-only/sequential fan-out needs none.
- **Dev worktrees** (for *implementing* this spec's code) are still required by craft's
  branch rules for Phase 0 + Levers B/C, unchanged by the above.

---

## Validation Protocol & Success Criteria

- **Baseline:** choose one representative "reference task," run it under orchestrate,
  capture the Phase 0 report → baseline (total in/out, cache-hit ratio, per-agent).
- **Per lever:** apply → re-run the *same* reference task → diff the report → record the
  delta in this spec + CHANGELOG.
- **Success (discovered, not pre-set):**
  - **A** — drop in inherited context size *and* per-agent input tokens.
  - **B** — per-agent input tokens drop (summaries vs. full transcripts); net run tokens down.
  - **C** — cache-read ratio up; cheap stages on Haiku; cost down.
  - **Overall** — every shipped lever has a proven, documented, non-negative delta.

---

## Testing & Risk

### Tests

- Parser unit tests against a committed **fixture JSONL** (deterministic, offline).
- Marker-schema test.
- Assert parser is **read-only** (no writes outside the repo).
- Wire into craft's pytest suite.

### Risks & mitigations

| Risk | Mitigation |
|---|---|
| Time-window attribution fuzzy if concurrent sessions share a project dir | Correlate by `run-id` where possible; document the limitation |
| JSONL schema is Claude-Code-internal and may change | Parser **fails soft** on missing fields; pins nothing |
| Worktree transcript dirs differ from main | Resolve dir from `cwd`; test both paths |
| Lever C cache discipline degraded by tool-set changes mid-run | Treat byte-stable tool set as a run invariant; note in docs |

---

## Documentation & Discoverability

- CHANGELOG entry per shipped lever with its measured delta.
- `scripts/orchestrate-token-report.py --help` usage; reference from orchestrate docs.
- Update `commands/orchestrate.md` / `drive.md` to mention the marker + report.

---

## Dependencies & Sequencing

1. **This spec ships first** (clean measurement baseline).
2. Then `SPEC-context-floor-hygiene-2026-06-17.md` (sustains Lever A via `/done`; depends on
   this spec's Phase 0 parser to trend floor size).
3. Later (optional) `SPEC-workflow-as-default-engine-2026-06-17.md` (evidence-based engine
   decision, enabled by Phase 0).
