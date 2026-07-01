# GRILL: craft Bloat Strategy — Phase Agents/Commands vs. Refactor to Skills?

**Target:** strategic question (no prior spec) — "should craft phase out agents & commands, or
rewire/refactor commands into skills, for token saving? craft is very bloated."
**Date:** 2026-07-01
**Outcome:** 3 load-bearing branches resolved. Headline: the premise ("convert commands→skills to
save tokens") is refuted by measurement — skill descriptions already out-cost command descriptions
at rest. Strategy pivots to delete + trim, with form-conversion gated on real `/usage` data.

## Measurement (grounding, not assumed)

Surface token cost, measured on `dev` (`~chars/4`; description = always-loaded proxy, body =
on-demand):

| Surface | Count | Always-loaded (desc) | On-demand (body) |
|---|---|---|---|
| Commands | 115 | ~1,613 tok | ~270,000 tok |
| Skills | 43 | **~3,858 tok** | ~79,000 tok |
| Agents | 8 | small | per-spawn |

**Counterintuitive finding:** 43 skills' descriptions already cost MORE at rest than 115
commands' descriptions — skills need verbose auto-fire triggers, commands have terse one-liners.
So command→skill conversion likely INCREASES always-loaded cost, not decreases it.

**Uncertainty flagged:** what actually preloads (fat agent bodies?) is unconfirmed — the
~2026-07-14 `/usage` checkpoint is the real measurement. A big form-conversion before that data
is betting blind.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Strategy: convert vs. delete vs. defer | **Measured two-track.** Track A (now): delete/consolidate low-value commands (117 is the resting surface) + trim descriptions — safe resting-token wins independent of unknowns. Track B: HOLD any commands↔skills form-conversion until the `/usage` checkpoint (~2026-07-14). Rejected mass-conversion (measurement shows it likely INCREASES resting cost) and blind aggressive cull. |
| 2 | Trim safety (the skill-description trap) | **Trim commands + agents freely** (terse descriptions, no activation dependency). **Skill descriptions are auto-fire triggers** — trim only with before/after activation checks; blind shortening silently degrades skill firing. **Front-load deleting known-dead surface** (deprecated-command consolidation, issue #233) — pure risk-free resting savings. Rejected aggressive all-descriptions trim (breaks auto-fire) and deletion-only (leaves the ~5.5k description surface). |
| 3 | Deferred-conversion go/no-go | **Pre-commit the criterion now** so 2026-07-14 is decisive: pursue commands↔skills conversion ONLY if `/usage` shows command **bodies** contribute to always-loaded cost (not just descriptions). If only descriptions preload (as this session's measurement suggests), form-conversion is **permanently off-table** — strategy stays delete + trim, no re-litigation. |

## Open Questions

- [ ] **Which commands to cull first.** Start with the 18 deprecated commands already tracked in issue #233 (known dead/duplicate). A broader 117-command value-audit is expensive/judgment-heavy — defer or scope carefully.
- [ ] **Instrument the safe-track wins.** Use `scripts/token-probe.py` (built this session) to measure the description surface before/after a trim pass — don't claim savings, measure them.
- [ ] **Skill-activation test method.** Define how to verify a skill still auto-fires after a description trim (the branch-2 gate) before trimming any skill description.
- [ ] **Feeds the `/usage` checkpoint (task #6).** Branch 3 adds a concrete decision to that checkpoint: does `/usage` show command bodies preloading? Record the answer there.
