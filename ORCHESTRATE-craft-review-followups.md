# Craft Review Follow-ups — Orchestration Plan

> **Branch:** `feature/craft-review-followups`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-craft-review-followups`
> **Spec:** `docs/specs/SPEC-craft-review-followups-2026-07-06.md`
> **Grill:** `docs/specs/GRILL-craft-review-followups-2026-07-06.md`

## Objective

Fix `do.md`'s dead agent-dispatch branch (H3) and its 24-file documentation blast radius,
add a `--report-only` release-state verify mode + rollback runbook (M1/M10), and remove a
stray root-level file (G1) — the 3 items from this session's craft review that needed a
design decision rather than a mechanical fix. All decisions are locked in the GRILL ledger;
this plan does not re-litigate them.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|---|---|---|---|---|
| 1 | H3: `do.md` dead-branch removal + 24-doc sweep | High | Med | ✅ Done (`68ba115b`) |
| 2 | M1/M10: release-state `--report-only` verify + runbook | Med | Med | Not started |
| 3 | G1: remove stray file | Low | XS | Not started |

## Phase 1: H3 — `do.md` Dead Agent-Dispatch Removal

**Scope:** `select_agent()` in `commands/do.md` names 4 `subagent_type` values
(`feature-dev`, `backend-architect`, `bug-detective`, `code-quality-reviewer`) with no
backing agent definition. Score 4-7 tasks crash on dispatch. Fix per GRILL decision 3:
test-first. Also closes M6 (two disagreeing classifiers) as a documented side effect.

- [x] 1.1 Write `test_do_score_4_7_no_agent_dispatch` (or equivalent) asserting Score 4-7
      routes via Step 1's `category`, never via a `subagent_type` dispatch call. Run it,
      confirm it FAILS against current `do.md` (red-first, proves the test is load-bearing).
- [x] 1.2 Remove `select_agent()`'s independent keyword-rescan and the 4 dead
      `subagent_type` branches. Route Score 4-7 through the same category-based
      command-sequencing fallback Score 1-3 and 8+ already use.
- [x] 1.3 Re-run 1.1's test, confirm it now PASSES.
- [x] 1.4 Sweep all 24 doc files referencing the 4 dead agent names as if real (GRILL
      decision 1 — full list from `grep -rln "feature-dev\|backend-architect\|bug-detective\|code-quality-reviewer" docs/`,
      re-run at implementation time since this list may have shifted):
      `docs/guide/orchestrator.md`, `docs/guide/complexity-scoring-algorithm.md`,
      `docs/guide/claude-code-2.1-integration.md`, `docs/orchestrator.md`,
      `docs/architecture.md`, `docs/brainstorm/BRAINSTORM-claude-code-integration-2026-02-20.md`,
      `docs/brainstorm/BRAINSTORM-homebrew-refactor-2026-02-15.md`,
      `docs/plans/2026-06-30-token-usage-reduction-handoff.md`,
      `docs/specs/SPEC-claude-code-integration-2026-02-20.md`,
      `docs/specs/SPEC-planning-refactor-2026-06-22.md`,
      `docs/specs/SPEC-planning-federation-2026-06-22.md`,
      `docs/specs/NEXT-SESSION-2026-07-03.md`, `docs/workflows/index.md`,
      `docs/cookbook/common/use-interactive-orchestration.md`,
      `docs/cookbook/common/memory-aware-routing.md`,
      `docs/tutorials/orchestrator-modes-compared.md`,
      `docs/tutorials/smart-routing-tutorial.md`,
      `docs/tutorials/TUTORIAL-claude-code-2.1-enhancements.md`,
      `docs/commands/orch.md`, `docs/commands/smart.md`, `docs/commands/brainstorm.md`,
      `docs/REFCARD.md`, `docs/reference/REFCARD-claude-code-2.1-enhancements.md`,
      `docs/reference/orchestrate-reference.md`.
      For each: replace the fictional-agent description with the actual command-sequencing
      fallback behavior, or remove the reference if it's purely illustrative. Historical
      BRAINSTORM/SPEC/plan docs describing past decisions may be left as historical record
      with a one-line "superseded" note instead of a full rewrite — use judgment per file,
      don't force every historical doc into present-tense accuracy.
- [x] 1.5 Re-run the grep from 1.4 repo-wide; confirm zero remaining non-historical
      references to the 4 dead agent names. (Also caught and fixed "feature-developer",
      a differently-spelled instance the original grep missed.)

**Key files:** `commands/do.md` (update), `tests/test_craft_plugin.py` or nearest fitting
test file (new test), 24 doc files listed above (update, selectively).

## Phase 2: M1/M10 — Release-State Verify + Rollback Runbook

**Scope:** per GRILL decisions 2 and 5 — extend `scripts/verify-surfaces.sh` with a
`--report-only` mode (never exits 1, prints ALIGNED/DRIFTED per surface) and 2 new legs
(GitHub release publication, docs-site version), then fold that into `/craft:dist:surfaces`
rather than building a new script or command. Write a manual rollback runbook alongside it.

- [ ] 2.1 Read `scripts/verify-surfaces.sh` in full (dependency from the SPEC — do this
      before writing any code). Confirm the existing 5-leg structure (marketplace.json,
      git tag, tap Formula, brew-installed, Code-registered) and its env-var override
      pattern (`SURFACES_GIT_TAG` etc.) to match conventions for the 2 new legs.
- [ ] 2.2 Add a `--report-only` flag: same checks, but never exits 1 — prints
      `ALIGNED`/`DRIFTED` per surface and always exits 0. Existing default (blocking,
      exit 1 on mismatch) stays unchanged for the release pipeline's own gate.
- [ ] 2.3 Add the GitHub-release-published leg (`gh release view vX.Y.Z` or equivalent).
- [ ] 2.4 Add the docs-site-version leg — reuse the existing live-site version-poll
      pattern already used elsewhere in this repo (release skill Step 13 / `docs.yml`'s
      post-deploy poll per `.STATUS` history) rather than inventing a new HTTP check.
- [ ] 2.5 Add a `--version <X>` override (promoting the existing env-var override pattern
      to a first-class flag) so `--report-only` can diagnose a specific past release, not
      only the current `plugin.json` version.
- [ ] 2.6 Fold into `commands/dist/surfaces.md`: add the `--version` and `--report-only`
      pass-through, extend its report table to the 2 new legs. No new command file.
- [ ] 2.7 Write `docs/runbooks/release-rollback.md`: manual per-surface undo steps for a
      bad release (revert/delete tag, delete/edit GitHub release, revert Homebrew formula
      commit + re-run tap CI, re-deploy docs site from the last-good commit).
- [ ] 2.8 Update `commands/code/release.md`'s existing "have a rollback plan" line to
      link the new runbook.

**Key files:** `scripts/verify-surfaces.sh` (update), `commands/dist/surfaces.md` (update),
`docs/runbooks/release-rollback.md` (NEW), `commands/code/release.md` (update).

## Phase 3: G1 — Remove Stray File

**Scope:** per GRILL decision 4 — plain delete, no history-preservation step (file was
never committed).

- [ ] 3.1 Confirm with the user immediately before this step (SPEC acceptance criteria
      marks this as "pending explicit confirmation at implementation time" — do not delete
      silently even though the decision is locked). On confirmation: `rm Chat-Instructions-v1.3.0.md`.

**Key files:** `Chat-Instructions-v1.3.0.md` (DELETE).

## Friction Prevention

- Context first: re-read `craft/CLAUDE.md` at the start of the implementation session.
- Verify CWD/branch before any git operation (`git branch --show-current`, `git worktree list`).
- No autonomous starts — this file ends with STOP-new-session mode; implementation begins
  in a fresh session opened at the worktree path.
- Test per phase: run the full suite after Phase 1 and Phase 2 before moving on, not only
  at the end.

## Acceptance Criteria

(mirrors `docs/specs/SPEC-craft-review-followups-2026-07-06.md`'s Acceptance Criteria — see
that file for the authoritative list; not duplicated here to avoid drift between the two.)

## Commit Strategy

Conventional commits, one per phase (`fix(do): remove dead agent-dispatch branch`,
`docs(do): sweep stale agent references`, `feat(release): verify-surfaces --report-only mode`,
`chore: remove stray Chat-Instructions file`) — matches this session's existing commit
granularity on `dev` (H1/H2/H4/etc. each landed separately).

## Verification

```bash
python3 -m pytest tests/ -q            # full suite, compare against dev's known baseline
                                        # (1 pre-existing unrelated failure:
                                        # test_roadmap_orchestrator_enhancements)
./scripts/validate-counts.sh           # confirm no new commands/skills/agents drift
```

Before opening a PR: `/code-review` and `/craft:arch:review` per the SPEC's Review
Checklist — both are merge gates, not optional.

## Session Instructions

```
cd ~/.git-worktrees/craft/feature-craft-review-followups && claude
```

> "Read ORCHESTRATE-craft-review-followups.md and start Phase 1."

## Test-Plan Scaffolding

| Item | Tiers | Rationale |
|---|---|---|
| Phase 1 (`do.md` fix) | `e2e` + `dogfood` | Flag/prose-shaped change to existing routing logic, no new parser. |
| Phase 1 (docs sweep) | N/A — no code path | Prose-only change across 24 files. |
| Phase 2 (verify script) | `e2e` + `dogfood` + `unit` | Extends an existing script (`+ new parser or script` tier) — unit-testable per new leg. |
| Phase 3 (G1) | N/A — no code path, pure file removal | |

```bash
# TODO(author): delete if not contract-bearing
test_do_score_4_7_no_agent_dispatch() {
  # Phase 1.1 — plant a Score-4 task, assert no Task(subagent_type=<dead-name>)
  # call occurs, assert the category-based command fallback ran instead.
  :
}
```

```bash
# TODO(author): delete if not contract-bearing
test_verify_surfaces_report_only_never_blocks() {
  # Phase 2.2 — plant a mismatched surface, assert --report-only prints DRIFTED
  # but exits 0 (never 1), while the default mode still exits 1 for the same input.
  :
}
```

## Documentation Scaffolding

Per the doc-scorer rubric (`commands/docs/sync.md`, threshold ≥3):

- [x] **Guide/runbook** — `docs/runbooks/release-rollback.md` is itself the required guide
      artifact for Phase 2 (score: new operational capability needing a documented procedure).
- [ ] Refcard — N/A, score < 3 (`/craft:dist:surfaces` gains flags, not a new command;
      update its existing refcard entry inline rather than scoring a new one).
- [ ] Demo — N/A, score < 3 (internal tooling/bugfix, not a user-facing feature demo).
- [x] **CHANGELOG `[Unreleased]`** — both Phase 1 (bugfix) and Phase 2 (feat) entries.

### Site Consistency Checklist

- [ ] `docs/commands/dist/surfaces.md` mirrors the new `--version`/`--report-only` flags
      (satellite docs tree, separate from `commands/dist/surfaces.md`).
- [ ] `docs/REFCARD.md` — no new command row needed (no new command file), but verify no
      stale row references the 4 removed agent names either (Phase 1 overlap).
