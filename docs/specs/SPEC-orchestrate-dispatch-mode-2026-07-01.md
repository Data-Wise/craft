# SPEC: `orchestrate-dispatch` — Background-Agent Dispatch Mode for plan-orchestrator

**Source grill (decisions locked):** [GRILL-plan-orchestrator-dispatch-mode-2026-07-01.md](GRILL-plan-orchestrator-dispatch-mode-2026-07-01.md) — 15 branches resolved, 0 open questions.
**Date synthesized:** 2026-07-01
**Status:** Ready for `/craft:orchestrate:plan` (this file).

---

## 1. Problem

`skills/orchestration/plan-orchestrator/SKILL.md` Mode 1 (Spec → ORCHESTRATE) has exactly one
execution path today: generate `ORCHESTRATE-<topic>.md`, create a worktree, then instruct the
user to **STOP** and start a fresh session in that worktree to implement it. That's safe (a new
session structurally cannot depend on live-conversation-only context) but costly: N backlog
items means N cold-started sessions, each reloading `CLAUDE.md`/system-prompt, each requiring the
user to personally babysit N terminals.

This session used an ad hoc alternative for two independent backlog items (linear-plan tasks #3
and #4): create the worktree, then dispatch a background `Agent` call that reads the ORCHESTRATE
file and executes it, instead of a fresh human session. It won on token cost (no reload) and
attention cost (notification-driven, not babysitting) — but did so ad hoc, without the safety
gap-closing this spec formalizes.

## 2. Goal

Add a third `--output` mode, `orchestrate-dispatch`, to `plan-orchestrator`'s Mode 1, that
formalizes this pattern: same ORCHESTRATE-file self-containment guarantee as the STOP mode, but
execution happens via a dispatched background `Agent` from the live planning session instead of a
new human session — with explicit handling for the failure modes a background agent introduces
that a human session doesn't (stuck/ambiguous work, hangs, silent failures, resumability,
concurrency).

## 3. Design (from the Decision Ledger)

### 3.1 Attachment point (branch 1)

New flag value on **Mode 1 only** (Spec → ORCHESTRATE). Not on brainstorm (wrong layer — divergent,
ends in a SPEC, never touches code) and not a separate 5th mode (would duplicate Mode 1's
spec-parsing/ORCHESTRATE-generation logic).

### 3.2 Flag shape (branch 2)

Third enum value on the existing `output` frontmatter arg:

```yaml
output: orchestrate-worktree | orchestrate-only | orchestrate-dispatch
```

Not a separate boolean `--dispatch` flag (avoids nonsensical combos like
`--output orchestrate-only --dispatch`).

### 3.3 Self-containment (branch 3)

The dispatched `Agent`'s entire prompt is: *"read `ORCHESTRATE-<topic>.md` in full, then execute
it."* Self-containment is structural — inherited from the ORCHESTRATE file's own completeness,
already required by Mode 1 — not a separate checklist or lint script.

### 3.4 Multiplicity (branch 4)

One spec per invocation, matching every existing plan-orchestrator mode. For N independent
backlog items, call the command N times in one message. Explicitly **not** batch multi-spec
dispatch (would overlap with `orchestrate:workflow`'s `parallel()` fan-out — duplicate capability).

### 3.5 Review gate before merge (branch 5)

The dispatched agent updates the ORCHESTRATE file's own `- [ ] 1.1 <task>` checkboxes and Phase
Overview status column as it completes each phase. Review gate = the dispatching session
re-reads the updated file + runs its own Verification section's test command before offering
merge. Never rely solely on the Agent tool's ephemeral final-message summary.

### 3.6 GRILL-file precondition (branches 6, 11)

**Warn-only** (advisory, not a hard block) — matches this repo's ADR-003 gentle-ramp precedent.
Recommend (don't require) a `GRILL-*.md` for the underlying spec, since grilling is the step that
resolves judgment calls *before* dispatch (background agents are one-shot, cannot pause to ask).
Backstop regardless of GRILL presence: an agent that hits genuine unresolved ambiguity must leave
that phase's checkbox unchecked, add a one-line blocker note to the ORCHESTRATE file, and stop —
never guess.

### 3.7 Confirm-before-dispatch gate (branch 7)

Explicit `AskUserQuestion` confirm step mirroring Mode 1's existing step 4: show the generated
ORCHESTRATE summary + worktree path, ask **dispatch-now / review-first / cancel** before calling
`Agent`.

### 3.8 Resumability (branch 8)

Idempotent resume: re-dispatching against the SAME ORCHESTRATE file must detect already-checked
`- [ ] 1.1` phases and instruct the new agent to skip them, starting from the first unchecked
phase. Reuses the tracking data branch 5 already produces. Never always-restart-from-Phase-1.

### 3.9 Concurrency cap (branches 9, 13)

Soft cap of **2 concurrent `orchestrate-dispatch` dispatches per session**; an explicit
`AskUserQuestion` confirmation gates any 3rd+ concurrent dispatch. **Scope:** the cap counts ONLY
`orchestrate-dispatch` dispatches, not unrelated background `Agent` calls the session may also
have running — avoids both undercounting (blocking a legitimate 2nd dispatch because of an
unrelated agent) and overcounting (never triggering the confirm because an orchestrate-dispatch
agent isn't recognized as such). Not a hard block — a deliberate larger fan-out is still possible,
just confirmed.

### 3.10 Failure/hang detection (branches 10, 14)

Cross-check the Agent tool's completion notification against the ORCHESTRATE file itself:

- **Notification fires but no checkboxes moved** → flag as suspected silent failure, do not
  offer merge.
- **No notification within the hang-detection window** → surface the crash/hang case explicitly,
  do not wait silently.

**Window definition:** tied to the dispatched ORCHESTRATE file's own stated phase-effort
estimate — flag as possibly-hung at **2× that estimate** with no notification. Not a fixed
wall-clock value; reuses data the design already requires (every ORCHESTRATE file has effort
estimates per Mode 1's template).

### 3.11 Confirmed-failure disposition (branch 15)

On a confirmed silent-failure or hang: leave the worktree and branch in place for inspection —
**never auto-delete**. Add a `.STATUS` note in the same HELD style already used for PR #237 this
session, so a failed dispatch doesn't vanish from tracking.

### 3.12 `.STATUS` write mode (branch 12)

Auto-write only the **factual fields** (branch, path, PR link once opened) at dispatch time — that
data already exists then, no new logic needed. The narrative/purpose prose stays **manual**
(auto-generated prose reads worse than hand-written, per every `.STATUS` entry from this session).

## 4. Explicitly rejected (do not re-litigate)

- Bolting this onto `brainstorm` (wrong layer).
- A separate 5th plan-orchestrator mode (duplicate-body risk).
- A boolean `--dispatch` flag instead of a third enum value (validation complexity).
- Batch multi-spec dispatch in one call (overlaps `orchestrate:workflow`).
- Relying solely on the Agent tool's final-message summary as the review gate.
- A hard block on missing `GRILL-*.md` (too much friction for low-ambiguity specs).
- Always-restart-from-Phase-1 on resume (redoes completed work, risks conflicting edits).
- A fixed wall-clock hang-detection constant (arbitrary; effort-estimate-relative is better-grounded).
- Auto-deleting worktree/branch on confirmed failure (destroys evidence needed to debug).
- Sequential-thinking MCP (investigated, rejected — costs more tokens than native extended
  thinking; its value requires a human present mid-reasoning, unavailable in unsupervised
  background dispatch; redundant with the grill-gate, branch 6).

## 5. Acceptance Criteria

- [ ] `plan-orchestrator/SKILL.md` Mode 1 documents `orchestrate-dispatch` as a third `output`
      value, with the confirm-before-dispatch gate (3.7) and self-containment prompt shape (3.3).
- [ ] Concurrency-cap logic (3.9) is scoped to `orchestrate-dispatch` calls only, not all
      background agents.
- [ ] Failure/hang detection (3.10) cross-checks notification against ORCHESTRATE checkboxes,
      with the 2×-effort-estimate window (3.10) — not a fixed constant.
- [ ] Confirmed-failure disposition (3.11) leaves worktree/branch in place + adds a HELD-style
      `.STATUS` note.
- [ ] Resumability (3.8): re-dispatch against a partially-complete ORCHESTRATE file skips
      already-checked phases.
- [ ] `.STATUS` auto-write (3.12) covers only factual fields (branch/path/PR link); narrative
      prose stays manual.
- [ ] Documentation & Discoverability phase complete (tutorial/guide update, REFCARD, hub
      surfacing, CHANGELOG, `validate-counts.sh` clean — no new command/skill, so counts should be
      unaffected unless the flag enum itself needs documenting in existing surfaces).

## 6. Test Plan (default-on)

- **e2e:**
  - `--output orchestrate-dispatch` on a spec with no `GRILL-*.md` present → warns (not blocks),
    proceeds to confirm gate.
  - Confirm gate presents dispatch-now/review-first/cancel; `--yes` still requires this gate per
    branch 7 (it's a design decision, not a suppressible prompt-refiner echo — confirm the skill
    docs state this explicitly).
  - Re-dispatch against an ORCHESTRATE file with Phase 1 already checked → the new agent's prompt
    instructs skipping Phase 1.
- **dogfood:**
  - Concurrency-cap counter only increments/decrements on `orchestrate-dispatch`-labeled agent
    calls, verified against a mixed session with unrelated background agents running.
  - Hang-detection window math: given an ORCHESTRATE file with a stated phase effort estimate of
    `X`, the documented flag-as-hung threshold is `2X`, not a hardcoded number.

## 7. Documentation

- Update `skills/orchestration/plan-orchestrator/SKILL.md` Mode 1 section with the new output
  value and its full flow (confirm gate, self-containment prompt, resumability, concurrency cap,
  hang detection, failure disposition).
- Update `docs/guide/pipeline-orchestrate-guide.md` (already documents Mode 1) with a subsection
  on `orchestrate-dispatch` vs. the existing STOP-new-session mode — when to use which.
- No count-cascade expected (flag enum value, not a new command/skill/agent) — confirm with
  `validate-counts.sh` after implementation regardless.
