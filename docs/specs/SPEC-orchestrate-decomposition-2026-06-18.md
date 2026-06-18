# SPEC: Orchestrate Task Decomposition — Bound the Agent×Turn Multiplier

**Status:** design resolved (spec-only; implementation deferred to a worktree)
**Created:** 2026-06-18
**From:** revision note in `SPEC-orchestrate-token-efficiency-2026-06-17.md` (Finding 3, deferred item)
**Author:** dt + Claude
**Relationship:** complements (does not supersede) the token-efficiency spec. That spec picks
the *engine*; this spec governs *how a task is broken into subtasks* before any engine runs.

---

## Why

Token usage is `agents × inherited-context × loop-turns`. The token-efficiency spec attacks the
*context* and *engine* factors. It explicitly defers the **agent-count factor**: loose fan-out
that spawns too many agents, or agents whose subtasks are too large (many loop-turns each),
inflates the multiplier regardless of engine or model routing. Worktrees and `:workflow` don't
fix an over-decomposed (or under-decomposed) plan — they just isolate or sequence it.

**Goal:** make the default orchestrate path produce **bounded, right-sized subtasks** so the
agent×turn product is controlled *before* engine selection.

**Non-goals:** model routing (done in orchestrator-v2), engine default flip (token-efficiency
spec Phase 1), budget primitives (craft has none; out of scope here too).

---

## Primary User Story

**As a** craft user running `/craft:orchestrate` on a non-trivial task,
**I want** the orchestrator to decompose it into a bounded set of appropriately-scoped
subtasks (not one giant agent, not 30 tiny ones),
**so that** the run stays cheap and legible without me hand-tuning the breakdown.

---

## Resolved Design (decisions, 2026-06-18)

1. **Agent-count ceiling — mode-scaled soft cap.** Scale the cap to craft's existing mode
   system; over-cap **warns and asks to confirm**, never hard-blocks (a hard block frustrates
   legitimate large tasks; no cap defeats the purpose).

   | Mode | Soft cap (concurrent subtask agents) |
   |---|---|
   | `default` | ~4 (warn + confirm above) |
   | `optimize` | ~4 (fast parallel) |
   | `release` | ~8 (thorough) |

   Caps are tunable; `--swarm` worktree count follows the same ceiling (one worktree per agent).

2. **Subtask sizing — single-concern + file-count guard.** A right-sized subtask covers **one
   module/concern** and touches **≤ K files** (K ≈ 5, tunable). Subtasks touching **> K files →
   suggest split**; **trivial single-file** subtasks → **collapse/merge**. Deterministic and
   observable — **no LLM pre-pass** (the token-efficiency spec rejected derivation pre-passes
   for the same token reason).

3. **Decompose-then-confirm — reuse craft's confirm/auto pattern.** Default: **show the
   breakdown and confirm** before spawning. `--yes`/auto-mode: **auto-run**. `--dry-run`:
   **preview only** (already the preview surface). No new gate — reuse the existing one.

4. **Mid-run adjustment — one-shot at planning time (v1).** Decomposition is decided **once
   before spawning**; **no dynamic merge/split**. Mid-run re-planning adds orchestrator
   turns/tokens — the opposite of this spec's goal. Revisit only if real runs show a need.

5. **Scope — fan-out path ONLY.** When a SPEC/plan yields a derivable `:workflow`, **its phases
   ARE the decomposition** (the workflow engine already bounds agents/turns by construction).
   This spec's heuristics apply **only to the free-form fan-out path**. No competing decomposer,
   no redundant re-check of workflow phases.

---

## Implementation Shape (from resolved design)

- A decomposition step in `agents/orchestrator-v2.md` planning phase (fan-out path only) that
  emits a **bounded subtask list** with per-subtask scope (concern + files) under the
  mode-scaled soft cap.
- Cheap heuristic, **no LLM pre-pass**: mode-scaled agent cap (warn+confirm over); flag > K-file
  subtasks to split; collapse trivial single-file subtasks; single-concern per subtask.
- Surface the breakdown in `--dry-run` and the default confirm gate; `--yes` auto-runs.
- Guard: skip entirely when the `:workflow` engine is selected (phases supply decomposition).
- Tests: fixture tasks → assert mode-scaled agent cap, > K-file split suggestion, trivial-merge,
  and that `:workflow`-derivable tasks bypass the heuristic.

---

## Branch Routing

- **This spec:** `.md` on `dev` (dev-safe).
- **Implementation:** orchestrator behavior = **feature code → worktree**
  (`feature/orchestrate-decomposition`), not `dev`. Not started.

---

## Sequencing

After (or alongside) the token-efficiency spec's Phase 0/Phase 1 — decomposition is most
valuable once token attribution exists to measure its effect on agent count and turns.
