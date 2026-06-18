# SPEC: Orchestrate Task Decomposition — Bound the Agent×Turn Multiplier

**Status:** draft (spec-only; no code yet)
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

## Open Design Questions (resolve before implementation)

1. **Agent-count ceiling.** A hard cap (e.g. ≤ N concurrent), a soft warning, or mode-scaled
   (default vs release)? What N? How does it interact with `--swarm` worktree count?
2. **Subtask sizing heuristic.** What signals a subtask is "right-sized"? Candidates: file-count
   touched, single-responsibility (one module/concern), estimated turns. Avoid an expensive
   LLM pre-pass (the token-efficiency spec rejected derivation pre-passes for the same reason).
3. **Decompose-then-confirm.** Show the proposed breakdown and confirm before spawning (like
   `--dry-run` already does), or auto-run under auto-mode? Reuse the existing confirm-gate.
4. **Merge/split feedback.** If a subtask finishes trivially or balloons, should the orchestrator
   merge/split mid-run, or is decomposition one-shot at planning time?
5. **Interaction with `:workflow`.** When a workflow is derivable, does its phase structure
   already supply the decomposition (making this a no-op for that path), leaving this spec to
   govern only the fan-out path?

---

## Proposed Shape (tentative — pending Q's above)

- A decomposition step in `agents/orchestrator-v2.md` planning phase that emits a **bounded
  subtask list** with per-subtask scope (files/concern) and a count guard.
- Cheap heuristic, **no LLM pre-pass**: cap agent count; flag subtasks touching > K files for
  splitting; collapse single-file trivial subtasks.
- Surface the breakdown in `--dry-run` output (already the preview surface).
- Tests: fixture tasks → assert bounded agent count + scoped subtasks.

---

## Branch Routing

- **This spec:** `.md` on `dev` (dev-safe).
- **Implementation:** orchestrator behavior = **feature code → worktree**
  (`feature/orchestrate-decomposition`), not `dev`. Not started.

---

## Sequencing

After (or alongside) the token-efficiency spec's Phase 0/Phase 1 — decomposition is most
valuable once token attribution exists to measure its effect on agent count and turns.
