# GRILL: Documentation-Impact Scaffolding

**Target:** [BRAINSTORM-doc-impact-scaffolding-2026-07-01.md](BRAINSTORM-doc-impact-scaffolding-2026-07-01.md)
**Date:** 2026-07-01
**Outcome:** 3 load-bearing branches resolved, design locked. Option C confirmed under a
token-efficiency lens. Hand off to `/craft:plan`.

Convergent interrogation of the brainstorm, with an explicit token-efficiency lens (agents vs
skills vs commands, grounded in 2026 Anthropic/community guidance).

**Established before grilling (not re-litigated):** Option C (extend rubric + reference existing
doc agents, no new skills) is token-efficient because (1) it adds ~0 permanent resting cost vs.
skill-per-type which taxes every session's startup context forever, and (2) doc authoring is
heavy + occasional → agent *isolation* (separate window, summary return) is the correct pattern,
which craft's 5 existing doc agents already commit to. The efficiency is conditional on tight
rubric-threshold tuning (branch 1).

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Rubric threshold / agent-spawn gating | **Tiered thresholds keyed to spawn cost.** Cheap in-context types (refcard, mermaid, index/nav tweak) stay at score ≥3. Heavy agent-authored types (tutorial, API, cookbook, architecture doc) need a higher bar (≥5) OR a concrete "new user-facing surface" trigger — so an expensive doc agent spawns only when authoring is genuinely needed, not for edits. This is what keeps Option C token-efficient (agents cost real tokens per spawn). |
| 2 | Scope / propagation | **Propagate to all spec-producers** (brainstorm / plan:feature / grill / orchestrate). They all read the same doc-scorer, so extending the scorer once gives every spec the fuller coverage for free. "Orchestrate-only" was rejected: it would require ADDING per-consumer gating logic to fork the scorer's output — more surface, breaks the single-source rule. Satisfies "every orchestrate spec" and more. |
| 3 | Site-consistency gate (mkdocs nav / index / site-update) | **Advisory-but-wired.** Render as ORCHESTRATE checkboxes that invoke the EXISTING `site:update` / docs-staleness tooling (a real check, not manual recall), but not a per-spec hard block. The release pipeline already hard-gates docs-staleness (`docs-staleness-check.sh --non-interactive`, Step 3b) — a per-spec hard gate would double-gate and add blocking friction to every feature. |

## Open Questions

- [ ] **Arch-doc double-count.** "Architecture change" is currently a scoring *factor* (+3 Mermaid). Promoting "Architecture doc" to an output *type* risks double-triggering (one arch change boosts Mermaid AND fires the arch-doc type). Adjust the factor weights during `/plan` so an arch change doesn't over-recommend both.
- [ ] **Single-source drift guard.** The expanded types MUST live only in `commands/docs/sync.md` (the scorer). The scaffold template + plan-orchestrator body must READ the scorer, never hardcode a parallel type list. Add the dogfood test proposed in the brainstorm (assert no parallel rubric).
- [ ] Not implemented — this ledger + brainstorm are the handoff artifacts for `/craft:plan`.
