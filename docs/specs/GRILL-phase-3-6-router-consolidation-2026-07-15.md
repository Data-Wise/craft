# GRILL — Phase 3.6 Router Consolidation (feature/folio-split)

**Date:** 2026-07-15
**Target:** `tasks/todo.md` Phase 3.6 (T3.6.0–T3.6.7) + `docs/plans/ORCHESTRATE-folio-split.md` Phase 3.5 rider section, on `feature/folio-split`
**Prior spec:** none (Phase 3.6 was split out of the T3.5.3 handoff note, no dedicated brainstorm/SPEC)
**Outcome:** Phase 3.6 scope substantially re-shaped — smaller and reframed vs. the original plan.

## Context

Phase 3.6 (router consolidations: `plan:feature`, `orch:drive`/`orch:workflow`, `arch` ×4,
`code:audit` ×5 → 4 new/absorbing routers, craft 46→~26 commands) was deferred at Phase 3.5
close (2026-07-13) pending a re-grill (T3.6.0), explicitly because 5 target families turned out
to be live non-deprecated commands — real architecture work, not shim deletion. T3.6.0 itself
(deprecated-frontmatter re-check, D2-lock re-verification) was re-run this session and confirmed
nothing has drifted since the plan was written. This GRILL is the adversarial pass on what to
actually build, run before implementation per the plan's own caution ("do not execute under
time/token pressure").

## Locked Decisions

### D1 — `orch.md` is the router, not a fresh build

`commands/orch.md` (369 lines, "Launch orchestrator mode") already exists and already has
embedded coupling to the two commands T3.6.2 planned to "absorb": it dispatches to
`/craft:orch:drive` (line 365) and auto-detects + proposes `--engine=workflow` (lines 250–301,
`orch:workflow`'s territory). T3.6.2's premise (drive/workflow as independent leaves folding
into a fresh router) is wrong — orch.md is already a half-formed router.

**Decision:** refactor `orch.md` itself into the formal router. Its existing
task/mode/swarm/engine surface + embedded drive/workflow dispatch logic become the router body.
`drive.md`/`workflow.md` bodies move to skill references (see D7 for where the launch logic
itself goes).

### D2 — code:audit shared flags dispatch per-subcommand

`command-audit.md` and `skill-standards.md` both define `format`+`fix`; `deps-audit.md` adds
`dry-run`; `deps-check.md`/`docs-check.md` have independent surfaces.

**Decision:** `format`/`fix` become one shared vocabulary across the `code:audit` router
(verified compatible — see below); subcommand-specific extras (`--ignore`/`--fail-on` on
deps-audit, etc.) stay per-reference-doc, not promoted to the shared set.

**Verification (session, not deferred):** read both `command-audit.md` and `skill-standards.md`
in full — `format` means output rendering (terminal/json/markdown) in both; `fix` means "auto-fix
safe mechanical issues" in both (command-audit: frontmatter/deprecated-marker fixes;
skill-standards: version-tag strip, frontmatter normalize, TOC stub — never prose in either).
Semantics genuinely compatible; D2 holds without revision.

### D3 — preserve direct slash-invocability

8 test files + 21 doc-site files reference the 9 target commands by literal path
(`/craft:orch:drive`, `commands/arch/analyze.md`, etc.).

**Decision:** every absorbed subcommand stays individually slash-invocable
(`/craft:orch:drive` keeps working) — the router is an *additional* discovery layer, not a
replacement. Matches the T3.5.1 salvage precedent (dist/claude-md/git families kept invocable
via skill, not deleted). Avoids silently breaking the 8 test files' literal-path assertions.

### D4 — reframe around organization, not command count

Direct consequence of D3: since every subcommand stays as a real invocable file, the "46 → ~26
commands" target in the original plan is **not reachable** this way — count barely moves (maybe
a handful from de-duplicated bodies). The real win is organizational: shared reference bodies,
a discovery router, less duplicated flag documentation.

**Decision:** drop the count-reduction framing entirely. `ci.yml`'s command floor stays near
current (46-ish) — T3.5.4's planned `-lt 18` re-baseline does NOT apply to this phase.

### D5 — split into independent PRs, one per workstream

Given D1 turned out to be a bigger refactor than planned and D4 downgraded the win, one bundled
CP-3.6 PR (as originally scoped) over-couples a risky refactor (orch.md) to a lower-risk one
(code:audit).

**Decision:** each surviving workstream (post D6: 2, not 3) lands as its own independently
reviewed, mergeable PR/gate. No `CP-3.6` single bundled gate.

### D6 — drop the `arch` router entirely

Weakest-recommendation check: `arch`'s 4 commands total 519 lines (analyze 147, diagram 130,
plan 133, review 109) — smallest family, and unlike code:audit's genuinely overlapping
audit-shaped commands, arch's 4 are independent design activities (analyze / diagram / plan /
review) with no real duplication or flag overlap to consolidate.

**Decision:** T3.6.3 is dropped. `commands/arch/{analyze,diagram,plan,review}.md` stay exactly
as they are — no router built.

### D7 — orch.md's launch logic moves to a skill

D1 requires disentangling orch.md's own orchestrator-v2-launch logic (task/mode/swarm/engine
execution) from its drive/workflow routing logic.

**Decision:** launch logic moves to a new skill (e.g.
`skills/orchestration/orchestrator-launch/`), matching the pattern already used by
check.md/dist-extras/claude-md in this same refactor arc. `orch.md` shrinks to a pure router:
bare-mode dispatch table (drive / workflow / direct launch) + a thin call into the new skill.

### D8 — code:audit router survives its own weakest-recommendation check

Applying D6's same skepticism: code:audit is 804 lines / 5 commands (larger than arch's
519/4, which was dropped). But unlike arch's 4 unrelated activities, code:audit's 5 commands
are structurally identical in shape (audit → report → optional `--fix`) with **verified**
shared flag semantics (D2).

**Decision:** distinction holds — code:audit router proceeds as the sole remaining workstream
alongside the orch.md refactor (D1/D7). Final Phase 3.6 scope: **2 workstreams, not 4.**

### D9 — explicit discovery-cache regen step

`commands/_cache.json` (61KB, gitignored per `.gitignore:42`) exists in this worktree. If stale
relative to the new router structure during dev/testing, discovery-based tests/dogfood could
silently read pre-refactor routing data.

**Decision:** add an explicit cache-regen step (`rm commands/_cache.json` or the regen script,
whichever the repo uses) to each workstream's task list, before the final verification pass —
cheap insurance beyond what the full suite already catches incidentally.

### D10 — `ci` router: build it as a 3rd workstream (correction)

**Process note:** the original Phase 3.6 plan had **5** target families
(`plan:feature`, `orch:drive`/`workflow`, `arch`, `code:audit`, `ci`) — this grill's first pass
covered only 4 and omitted `ci` entirely (8 commands: detect/fix/generate/local/status/triage/
validate/watch, 2117 lines, the largest family). Caught and corrected during plan-handoff, before
any implementation started.

Verified same as D2/D8: `dry-run`/`fix`/`json` mean the same thing everywhere they appear across
the 8 commands (preview / auto-fix / structured-output, respectively). One real mismatch found:
`repo` accepts short names ("craft", "homebrew-tap") in `status.md` but requires `OWNER/NAME`
format in `triage.md`/`watch.md` — same flag name, incompatible input contract. Structurally, the
8 commands form a cohesive CI lifecycle (detect→fix→generate→run→status→triage→validate→watch),
closer to code:audit's structural-similarity case than arch's independent-activities case (D6).

**Decision:** build the `ci` router as a 3rd independent workstream/PR, alongside the orch.md
refactor and the code:audit router. `repo` must be normalized to `OWNER/NAME` everywhere as part
of the build (status.md's short-name acceptance becomes an explicit alias/expansion, not silently
dropped) — not left as a latent inconsistency. Largest and highest-line-count of the 3 — do it
last, per the original plan's own sequencing note for this family.

## Net Effect on Phase 3.6 Scope

| | Original plan | Post-grill |
|---|---|---|
| Workstreams | 5 (plan:feature excluded, orch, arch, code:audit, ci) | 3 (orch.md refactor, code:audit router, ci router) |
| `plan:feature` | excluded (D2 lock, pre-existing) | unchanged — still excluded |
| `arch` router | planned (T3.6.3) | **dropped** (D6) |
| `ci` router | planned (T3.6.5), initially omitted from this grill | **kept**, re-verified (D10) |
| Command count goal | 46 → ~26 | **not a goal** — organizational only (D4) |
| Invocability | unspecified | preserved for every subcommand (D3) |
| PR batching | 1 bundled (CP-3.6) | 3 independent PRs (D5 + D10) |
| orch.md treatment | build fresh router alongside orch.md | **orch.md itself becomes the router** (D1, D7) |

## Open Questions (deferred to /craft:plan)

- Sequencing: ci router last (per D10); no design dependency between orch-refactor and
  code:audit — pure scheduling between those two.
- Exact reference-file layout for the new orchestrator-launch skill, the code:audit references,
  and the ci references (per-subcommand file naming, ADR-002 line-conservation diff targets).
- Whether `tasks/todo.md`'s Phase 3.6 section (T3.6.1–T3.6.7) should be rewritten in place to
  match this scope, or superseded by a fresh task breakdown scoped to the 3 workstreams.

## Handoff

Ready for `/craft:plan` (plan-orchestrator tier) to turn this into task breakdowns for the 3
workstreams. Grill interrogates and hands the artifact forward — no execution here.
