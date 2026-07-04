# GRILL: A2 — `/craft:plan` Dispatcher Command

- **Date:** 2026-07-04
- **Target:** [`SPEC-planning-refactor-2026-06-22.md`](SPEC-planning-refactor-2026-06-22.md) §6 (A2)
- **Mode:** grill (convergent) — 5 branches resolved
- **Sweep evidence:** no bare `commands/plan.md` dispatcher exists today, only
  `commands/plan/{feature,sprint,roadmap}.md` (2 of 3 flagged `deprecated: true` per A3,
  not yet shrunk to thin stubs); `/craft:do` already has a mature complexity-score router
  (0–10 scale, `commands/do.md`) for the execution axis — A2 is the analogous router for
  the deliberation axis, not a duplicate of it.

## Locked decisions

| # | Branch | Decision | Why |
|---|--------|----------|-----|
| G-1 | **Real gap?** | **Yes** — users don't know craft's 5-tier vocabulary (brainstorm/grill/project-planner/plan-orchestrator/orchestrate) by name. `/craft:plan <topic>` as a single memorable entry point is the value-add, mirroring `/craft:do`'s role for execution. **Scope: router only** — no new planning logic, just decides which existing skill/command to call. | Confirms A2 isn't redundant with skill auto-activation; also bounds scope so it doesn't grow into a 6th planning surface. |
| G-2 | **Tier-detection mechanism** | **Deterministic repo-state signals, NOT phrase/keyword classification.** No SPEC for the topic → brainstorm. SPEC exists, no GRILL → offer grill. GRILL exists, no ORCHESTRATE → plan-orchestrator. Otherwise → project-planner (strategy advice, the only case needing any interpretation, and A1 already disambiguated its own triggers). | Phrase-based classification is the EXACT mechanism that caused C1. Building another phrase classifier one layer up would relocate the same ambiguity risk instead of eliminating it — deterministic file-existence checks have no such risk. |
| G-3 | **Namespace (D-ns)** | **Trust as decided** — `/craft:plan`, not bare `/plan`. Not re-verified against the live platform this grill. | Re-litigating an already-locked spec decision (§1 D-ns) is scope creep on A2's own grill; if D-ns needs revisiting, that's a separate, explicit decision to reopen — not incidental to this pass. |
| G-4 | **Blast radius vs. `commands/plan/*`** | **Real overlap found — A2 is now sequenced AFTER A3, not before.** A bare `/craft:plan` router next to `commands/plan/{feature,sprint,roadmap}.md` — 2 of which are still full-length despite being flagged deprecated — is confusing regardless of tier semantics; A3 (shrink to thin stubs) must land first so there's no window where a router and stale full-length subcommands coexist under the same path prefix. | Reorders the priority list in `docs/specs/NEXT-SESSION-2026-07-03.md` (had A2 ahead of A3) — a genuine sequencing dependency the original plan didn't flag. |
| G-5 | **Build now?** | **Defer.** Do A3 next instead; A2 is blocked on it per G-4, and there's no concrete friction case yet (no user has actually been confused about which skill to invoke) — the gap (G-1) is real but not urgent. | Cheapest, lowest-risk path: unblock A2 by finishing what's already scoped and small (A3, 15min), rather than starting A2's design against a namespace it can't cleanly land in yet. |

## Open questions (resolve at plan/build, if A2 is picked up later)

1. **Exact repo-state check implementation** — where does the deterministic detection (G-2) live? Likely a small Python helper (`commands/_plan_dispatch.py`?) mirroring `commands/do.md`'s existing complexity-scorer pattern, not inline command prose.
2. **What happens on ambiguous repo state** — e.g. a SPEC exists but is stale/abandoned; a GRILL exists but predates spec edits. G-2's happy-path logic doesn't yet cover staleness detection.
3. **Bare invocation with no topic** — G-2's detection requires a topic/spec-path argument to check repo state against. What does `/craft:plan` (zero args) do? Likely: fall back to `.STATUS`/git-branch topic inference, same as `brainstorm`'s own Step 1 — not yet confirmed.

## Handoff

**Deferred, not planned.** Per G-5, do NOT proceed to `/craft:plan` (tier 4) for A2 yet — A3
(`commands/plan/sprint.md` + `roadmap.md` → thin stubs) is the next actionable item instead.
Revisit A2 after A3 lands, or when a concrete user-confusion case for tier-routing appears,
whichever comes first.
