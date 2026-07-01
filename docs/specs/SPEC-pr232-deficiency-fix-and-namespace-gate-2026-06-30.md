# craft: PR #232 Deficiency Fix + Namespace-Refactor Go/No-Go Gate

**Date:** 2026-06-30
**Status:** Planning
**Source:** Adversarial review of PR #232 (`feature/token-usage-reduction`) + research question
about whether `SPEC-refactor-namespace-2026-06-29.md` would help token reduction
**Distinct from:** `SPEC-refactor-namespace-2026-06-29.md` (this spec produces a recommendation
*for* that spec; it does not implement it), `SPEC-flat-command-ownership-2026-06-29.md`

---

## Context

An 8-angle finder + verifier review of PR #232 (token-usage-reduction: orchestrator model
routing, `/refine` + `/brainstorm` redesign) surfaced 8 confirmed/plausible findings, all
doc/count-drift or undocumented-behavior issues — none correctness-breaking, all fixable in the
existing `craft-review` worktree before merge. A follow-up adversarial pass on the PR's actual
token-reduction claims found the structural mechanism is sound (3 of 4 changes produce real,
verified savings on the common path) but **zero actual token measurement was run** — the PR's own
`SPEC-token-efficiency-research-2026-06-30.md` admits the headline "48% reduction" is a `wc -l`
line-count diff, not a token count, and that `/usage` validation "has not yet happened." The new
`command-skill-token-efficiency/SKILL.md` overstates this further, claiming "measured token cost"
where its own cited source explicitly disclaims that.

Separately: `docs/specs/SPEC-refactor-namespace-2026-06-29.md` (written the day before, status
Planning, not yet implemented) proposes consolidating craft's 117 commands into ~40 with
sub-actions, justified on structural-bloat/routing-ambiguity grounds — not token cost. Whether
consolidation actually reduces session-start token cost is unverified there too, and
`token-reduction-plan.md` (from PR #232) explicitly argues the opposite: commands are already
lazy-loaded (frontmatter-only until invoked), so command *count* may not be the primary cost
driver consolidation assumes it is.

Both gaps share a root cause: assertions stand in for measurement. This spec plans the fix for
both, scoped tightly so Track B stays a recommendation, not an implementation.

---

## Track A — Fix PR #232 before merge

**Where:** `craft-review` worktree, on `feature/token-usage-reduction`, before the PR merges to
`dev`.

### A1. Mechanical doc fixes (6 items, ~45 min total)

| File | Fix |
|---|---|
| `commands/hub.md` + `docs/commands/hub.md` | Workflow skill-category row: `7` → `5`, add missing `task-management` to the named list |
| `docs/REFCARD.md:8` | `Commands: 112` → `Commands: 117` |
| `docs/skills-agents.md:94` | `### Orchestration (5)` → `### Orchestration (6)` |
| `commands/workflow/refine.md` | Fix ADR-002 citation — either correct the citation or correct ADR-002's routing table, whichever is actually true (verify before editing: ADR-002 currently routes `/refine` → `adhd-workflow`, the shim routes to `prompt-refiner`) |
| `tests/test_scaffold_defaults_dogfood.py` | Add `brainstorm-insights/SKILL.md` back to the `SKILLS` list alongside `brainstorm/SKILL.md` — both carry the scaffold-default contract |
| `docs/CHANGELOG.md` / `CHANGELOG.md` | Add an `[Unreleased]` entry covering this branch's actual work (model pinning, `/refine` shim, `/brainstorm` split, `orchestrator-resilience` extraction, new `command-skill-token-efficiency` skill) |

### A2. Claim-accuracy fixes

- `skills/code/command-skill-token-efficiency/SKILL.md:8` — change "found and fixed real, **measured** token cost" to language consistent with what's actually been measured (line count, not tokens), matching the caveat already present in `SPEC-token-efficiency-research-2026-06-30.md:65`.
- Audit other PR-touched docs for the same overclaim pattern (commit titles like "631→42 lines" framed as token savings without the "line count ≠ token count" caveat nearby) and add the caveat where it's missing.

### A3. Resolve the two PLAUSIBLE (not CONFIRMED) findings

- **Depth-count colon notation** (`d:5`, `m:12`) — dropped with no migration note. Decide: restore the override mechanism in `skills/workflow/brainstorm/SKILL.md`, or add an explicit "intentionally removed, here's why" note. Do not leave it silently absent.
- **`-C`/`--categories` flag** — declared in `commands/workflow/brainstorm.md` frontmatter but its value table is only reachable via a link into `docs/specs/_archive/SPEC-brainstorm-question-bank.md`. Surface the category-value table directly in `skills/workflow/brainstorm/SKILL.md`.

### A4. Update the PR description

PR #232's description currently documents 6 commits ending at `1974ffeb`; the branch HEAD is 6
commits ahead (`d80daa5f` through `f615f3fb`), including the entire
`command-skill-token-efficiency` skill and both new research docs — none of which the description
mentions. Rewrite the description to cover all 12 commits.

### A5. Commit to a real post-merge measurement checkpoint

Not prose ("watch `/usage` for a week") — a concrete, dated follow-up: add a `.STATUS` next-action
item or a scheduled trigger (`send_later`/`create_trigger`) to actually come back in ~1-2 weeks
and check real `/usage` data against the pre-merge baseline, closing the validation gap the PR's
own SPEC flags as still open.

**Verification:** full `pytest tests/`, `validate-counts.sh`, `bump-version.sh --verify`, plus the
three regression tests already named in the PR's own commit history
(`test_skill_trigger_phrases_unique`, `test_refine_flag_documented`, `test_behavior_9_timeline`).

---

## Track B — Namespace-refactor go/no-go (empirical, recommendation-only)

**Where:** scratchpad / disposable test plugin — explicitly **not** the live `commands/` tree.

**Question:** does consolidating craft's 117 flat commands into ~40 with sub-actions (per
`SPEC-refactor-namespace-2026-06-29.md`) measurably reduce session-start token cost, or is
`token-reduction-plan.md`'s lazy-loading argument correct that command count isn't the primary
cost driver?

### B1. Design a minimal empirical probe

Build two small, disposable layouts outside the main command tree:

- **Layout 1 (flat):** N standalone command `.md` files (e.g. 10), each with realistic frontmatter
  (`name`, `description`, `argument-hint`).
- **Layout 2 (consolidated):** the same N pieces of content as one command file with N documented
  sub-actions, matching the namespace spec's proposed `/craft:docs <sub-action>` pattern.

### B2. Observe and record actual numbers

Start a fresh session against each layout and capture what's actually surfaced at session start
(the system-reminder command/skill listing, or transcript token accounting) — not an estimate.
Record frontmatter-token cost per layout.

### B3. Write the recommendation as an addendum

Append the result to `SPEC-refactor-namespace-2026-06-29.md`'s existing structure (new dated
addendum section, not a new file) — `proceed as-is` / `proceed with modification` / `shelve` —
citing the measured numbers against that spec's current unmeasured structural-bloat rationale.

### B4. Explicit stop condition

No file moves, no `namespace.json` generation, no command consolidation happens in this track.
That work stays scoped to `SPEC-refactor-namespace-2026-06-29.md`'s own dedicated worktree, per
its existing Implementation Note #1 ("Do not run this in the same session as any other craft
feature work").

---

## Done Signal

- [ ] Track A: all 6 mechanical fixes applied and verified
- [ ] Track A: SKILL.md / commit-title overclaim language corrected
- [ ] Track A: depth-count notation and `-C`/`--categories` decided and resolved (not silently dropped)
- [ ] Track A: PR #232 description updated to cover all 12 commits
- [ ] Track A: dated post-merge `/usage` checkpoint scheduled
- [ ] Track A: full test suite + validate-counts + bump-version --verify green
- [ ] Track A: PR #232 merged to `dev`
- [ ] Track B: empirical probe built and run (disposable, not committed to `commands/`)
- [ ] Track B: recommendation addendum written to `SPEC-refactor-namespace-2026-06-29.md`
- [ ] Track B: explicitly did NOT implement any part of the namespace refactor itself

---

## Cross-references

- `docs/specs/SPEC-refactor-namespace-2026-06-29.md` — the namespace refactor this gates
- `docs/specs/SPEC-flat-command-ownership-2026-06-29.md` — separate, already-scoped hub-contract work
- `docs/specs/SPEC-token-efficiency-research-2026-06-30.md` — PR #232's own research, source of the
  line-count-vs-token-count caveat this spec enforces consistently
- `docs/internal/TOKEN-EFFICIENCY-craft.md` — PR #232's implementation record
- `token-reduction-plan.md` — original research, source of the lazy-loading counter-argument Track B tests
