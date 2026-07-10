# GRILL — craft v4 Roster (Phase 3.5 rider: the exact surviving command set + salvage list)

> **Target:** pin the exact v4 command roster + per-shim salvage list for the Phase 3.5 rider
> of `ORCHESTRATE-folio-split.md`, per
> `BRAINSTORM-craft-v4-skills-first-surface-2026-07-09.md`.
> **Date:** 2026-07-09 · **Evidence base:** per-file classification of all 69 post-split
> commands (Explore agent, repo-verified: 27 deprecated shims / 2 shims / 6 routers /
> 2 references / 32 rich).

## Decision Ledger

### R1 — hot shims: kill all 27 or keep the heavy-use 4?  ✅ LOCKED

**Decision:** **Keep `/next`, `/done`, `/refine`, `/brainstorm` as ≤5-line micro-shims; kill
the other 23.** Roster = **26**, not 22.

**Why:** the 4 were root-promoted in v2.60 explicitly for heavy real-world use; skill
slash-invocation binds to the SKILL name (`adhd-workflow`, `prompt-refiner`) — killing the
shims would replace the highest-frequency short verbs with longer or NL-probabilistic entries.
The micro-shims cost ~20 lines total and duplicate zero behavior (skills stay canonical).
Rejected kill-all-27 (UX regression on the most-used surface) and usage-audit-first (the v2.60
promotion rationale is already the usage evidence).

**Consequence accepted:** the roster is 26; the "22" in prior docs becomes 26 everywhere
(ci.yml floor target unchanged at `-lt 18` — still comfortably below).

### R2 — salvage gate for the 23 dying shims  ✅ LOCKED

**Decision:** **Mechanical rule — every dying shim >150 lines gets a body-vs-skill(+references)
diff; unique logic migrates to the skill's `references/` BEFORE deletion.** Smaller shims die
on the existing test tripwires (`test_skill_referenced_commands_exist` + bash suites).

**The ~9 salvage jobs this catches:** `dist:pypi` (492L) · `check:gen-validator` (447L) ·
`dist:marketplace` (409L) · `git:docs:refcard` (363L) · `docs:claude-md:edit` (635L) ·
`docs:claude-md:sync` (362L) · `docs:claude-md:init` (320L) · `dist:curl-install` (252L) ·
`workflow:insights` (194L). Includes all 3 PR #279 restorations and the dist-extras trio
(409–492L each labeled "shim" into ONE skill — exactly the profile that bit before).

**Why:** deterministic, no mid-execution judgment calls; ~9 jobs vs 23 (diff-all = low-yield
day) vs 6 (trust-the-rest = repeats the PR #279 miss on the dist trio).

**Consequence accepted:** salvage work is front-loaded into Phase 3.5's first increment.

### R3 — consolidation shape: where do ~4,400 lines of rich bodies go?  ✅ LOCKED

**Decision:** **Thin router (~60L: subcommand parse + dispatch table) + verbatim body migration
to the backing skill's `references/<subcommand>.md`** — e.g. `ci:generate`'s 730 lines →
`skills/ci/references/generate.md`. The proven ADR-002/savant pattern.

**Why:** progressive disclosure — tokens load only for the invoked subcommand; references are
excluded from skill counts (no cascade). Rejected mega-files (every invocation loads all 8
bodies — the bloat v2.56 killed) and SKILL.md-inlining (blows the 300-line skill-standards
gate + auto-fire loads everything).

**Consequence accepted:** ~5 new `references/` dirs; ADR-002 line-conservation diff per
migration; router dispatch tables become the new per-family test surface.

### R4 — the roster  ✅ LOCKED (26)

**Decision:** locked as tabled in `ROSTER-craft-v4-disposition-2026-07-09.md`:
**18 keep-as-is + 5 micro-shims (next, done, refine, brainstorm, check — check added during
table review: it's a 315L deprecated shim serving as the daily pre-commit entry) + 3 new
consolidation routers (ci, arch, code:audit) = 26.** 20 files consolidated, 22 shims + 2
teaching utils killed, discovery-usage demoted, **12 salvage jobs** (R2 gate). hub.md
regenerates against the 26 during the Phase 3.5 cascade.

**Tolerance:** ±2 for execution-time discoveries (e.g. a salvage diff proving a shim must
survive) — each deviation recorded here.

## Handoff

R1–R4 locked → Phase 3.5 of `ORCHESTRATE-folio-split.md` is spec-complete. Execution order
inside 3.5: (1) the 12 salvage diffs, (2) shim/util kills, (3) the 5 consolidations
(router + references), (4) cascade (bump-version, hub regen, ci.yml floor → `-lt 18`),
(5) suites + MIGRATION-v4 rows for every killed/consolidated name.
