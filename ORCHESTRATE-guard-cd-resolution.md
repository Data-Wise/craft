# Guard cd-Target Resolution — Orchestration Plan

> **Branch:** `feature/guard-cd-resolution`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-guard-cd-resolution`
> **Spec:** `docs/specs/SPEC-guard-hardening-adversarial-review-2026-07-15.md` (PR A)

## Objective

Give `no-switch-guard.sh` the same leading-`cd`-target resolution `branch-guard.sh` got in
PR #284, then extend BOTH hooks to cumulative-cwd tracking (a bare `cd <path> &&` retargets
every clause after it, not just the first) — closing a gap in #284's own resolver, which is
confirmed single-hop only.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|---|---|---|---|---|
| 1 | Cumulative-cwd resolver helper (shared logic) | High | Med | ✅ |
| 2 | Wire into `no-switch-guard.sh` | High | Low | ✅ |
| 3 | Retrofit `branch-guard.sh`'s §8d0 resolver | High | Med | ✅ |
| 4 | Test coverage (both hooks, multi-hop cases) | High | Med | ✅ |
| 5 | Docs (REFCARD-BRANCH-GUARD.md) + CHANGELOG | Med | Low | ✅ |

> **Completed 2026-07-15.** Phase 1.1 judgment call resolved: **parallel-inline**
> logic in each hook (not a shared sourced file) — the hooks derive base cwd
> differently (no-switch `$PWD`, branch-guard JSON `.cwd`) and a shared file would
> force both install scripts to deploy+source it. Phase 5 note: the REFCARD had no
> pre-existing cd-resolution section to "extend" (only a `GRILL-…-target-resolution`
> reference re: `rm -rf .git`), so a new "Cross-Context Target Resolution" section
> was added. Commits: `d1b95c4` (P1), `4027dfd` (P2), `d08202` (P3), `989f492` (P4),
> `0a3d716` (P5). Tests: branch-guard 124/124, no-switch 39/39 (repo-copy, enabled
> HOME). Not pushed / no PR opened per session instructions.

## Phase 1: Cumulative-cwd Resolver Helper

**Scope:** Design the shared resolution logic once, since decision #2 in the GRILL locked
"resolve once, apply to both hooks." Walk a compound command's clauses in order; each `cd
<path>` (bare, or via `-C <path>` on a `git` invocation) updates the *effective* target
directory for every subsequent clause, not just the immediately following one.

- [x] 1.1 Decide implementation shape: a shared shell function sourced by both scripts, or
      parallel (near-identical) inline logic in each — given `no-switch-guard.sh` and
      `branch-guard.sh` don't currently share any code (verified: no `source` of a common file
      in either), duplicated-but-synced inline logic is likely simpler than introducing a new
      shared-file dependency. **Judgment call — pick the lower-friction option, document the
      choice in this file's commit message.**
- [x] 1.2 Handle the two path forms already supported by branch-guard.sh's existing (single-hop)
      resolver: bare leading `cd <path> &&`/`;` and `-C <path>` on a `git` invocation. Extend
      matching to non-leading occurrences (currently `branch-guard.sh` line 579 anchors `^cd`,
      which structurally cannot match a second `cd`).
- [x] 1.3 Guard against `$`/backtick in the cd path (branch-guard.sh's existing resolver already
      excludes these — line 581 — to avoid resolving a shell-expansion target; carry this
      exclusion into the cumulative version).

**Key files:** `scripts/branch-guard.sh` (reference existing single-hop logic ~line 552-600),
`scripts/no-switch-guard.sh` (NEW resolver, currently only handles `-C` at line 64)

## Phase 2: Wire into no-switch-guard.sh

**Scope:** Replace the `-C`-only `git_dir` extraction (line 64) with the cumulative resolver
from Phase 1. `is_dirty()` and `switch_target()` must both use the resolved target directory,
not session `$CWD`.

- [x] 2.1 Replace `git_dir=$(printf '%s' "$cmd" | grep -oE 'git[[:space:]]+-C[[:space:]]+...')`
      with a call into the Phase 1 resolver.
- [x] 2.2 Verify `is_dirty()` (line 65-69) runs `git status --porcelain` against the resolved
      dir, not `$CWD`.
- [x] 2.3 Verify `switch_target()` and the RED-tier checks (§3a-3d) still work correctly when
      the resolved target differs from session CWD — e.g. does the dirty-tree confirm message
      (line 118) need to name which repo it's talking about, given cross-context is now possible
      here (mirrors the "name the resolved repo/branch explicitly" review-checklist item from
      #284's SPEC)?

**Key files:** `scripts/no-switch-guard.sh`

## Phase 3: Retrofit branch-guard.sh's §8d0 Resolver

**Scope:** This is a re-opening of already-merged #284 code, not new-file scope. The existing
§8d0 block (line 552-600) resolves only ONE leading `cd`/`-C` (confirmed by direct read this
session: line 579's regex is anchored `^cd`). Extend it to cumulative tracking using the same
Phase 1 logic/shape.

- [x] 3.1 Extend the `_bg_cd_path` extraction (line 579-585) to walk multiple `cd`/`-C`
      occurrences across the compound command, updating `_BG_TARGET_DIR` at each step.
- [x] 3.2 Confirm `IS_CROSS_REPO_TARGET`, `BRANCH`, `PROJECT_ROOT`, `PROJECT_NAME`, and the
      `INTEGRATION_BRANCH`/`PROTECTION` re-derivation (line 587-600ish) still fire correctly
      against the LAST resolved target in a multi-hop chain, not an intermediate one.
- [x] 3.3 Regression check: every existing single-hop cross-context test
      (`tests/test_branch_guard.sh`'s "Cross-Context Target Resolution" group, added in #284)
      must still pass unmodified — cumulative tracking is a superset behavior, not a rewrite.

**Key files:** `scripts/branch-guard.sh` (§8d0, ~line 552-600)

## Phase 4: Test Coverage

**Scope:** Multi-hop `cd` chain cases in both test files. Both already have compatible
scaffolding (confirmed this session — `init_repo`/`make_tmpdir`/`json_bash`/`run_green` in
`test_no_switch_guard.sh`; the analogous helpers already used by #284's cross-context group in
`test_branch_guard.sh`). No new test-harness infrastructure needed.

- [x] 4.1 `test_branch_guard.sh`: add cases for `cd a && cd b && git push` (target should resolve
      to repo `b`, not `a` or session CWD) and `cd a && git -C b push` (mixed cd + -C, `b` wins).
- [x] 4.2 `test_no_switch_guard.sh`: add the equivalent cases for `git switch`/`checkout`, plus
      the specific scenario from the BRAINSTORM's Context Scan: `cd <worktree> && git switch
      <branch>` with a dirty session repo and a clean worktree target (should NOT block) and the
      inverse (clean session, dirty worktree target — SHOULD block).
- [x] 4.3 Run both full suites (`bash tests/test_branch_guard.sh`, `bash tests/test_no_switch_guard.sh`)
      and confirm zero regressions against the pre-change baseline.

**Key files:** `tests/test_branch_guard.sh`, `tests/test_no_switch_guard.sh`

## Phase 5: Docs + CHANGELOG

**Scope:** Small, mechanical.

- [x] 5.1 `docs/reference/REFCARD-BRANCH-GUARD.md` — note cumulative cd-target resolution now
      applies to both hooks (extends the #284-era note already there for the single-hop case).
- [x] 5.2 `CHANGELOG.md` + `docs/CHANGELOG.md` `[Unreleased]` — mirrored `### Fixed` entries
      (both files must match — this repo maintains both, per project convention).

**Key files:** `docs/reference/REFCARD-BRANCH-GUARD.md`, `CHANGELOG.md`, `docs/CHANGELOG.md`

## Friction Prevention

- Verify CWD before any git operation: `pwd` should show this worktree, not the main repo.
- No autonomous starts — this file is written for a fresh session to read and confirm before
  touching code (STOP-new-session mode; no `orchestrate-dispatch` requested this session).
- Test after each phase, not just at the end — Phase 3 in particular touches already-merged
  code and must not regress #284's existing passing tests.
- If genuine ambiguity is hit (e.g. Phase 1.1's shared-helper-vs-duplicated-logic call), leave
  the checkbox unchecked, add a one-line blocker note in this file, and stop rather than guess.

## Acceptance Criteria

(From `SPEC-guard-hardening-adversarial-review-2026-07-15.md`, PR A subset)

- [x] `cd <worktree> && git switch <branch>` in `no-switch-guard.sh` resolves dirtiness/target
      from the worktree, not session CWD.
- [x] A multi-hop `cd a && cd b && git switch x` resolves to `b` as the target in both
      `no-switch-guard.sh` and `branch-guard.sh` — cumulative tracking, not single-hop.
- [x] `branch-guard.sh`'s existing #284 single-hop cross-context tests stay green after the
      cumulative-tracking retrofit (no regression).
- [x] CHANGELOG `[Unreleased]` entry added (fix, not feat).

## Commit Strategy

Conventional commits per phase (`fix(guard): ...`), squash-merged into `dev` via PR.

## Verification

```bash
bash tests/test_branch_guard.sh
bash tests/test_no_switch_guard.sh
python3 -m pytest tests/ -x   # full suite, confirm no unrelated regression
```

## Test-Plan Scaffolding

| Tier | Scope |
|---|---|
| unit | N/A — the resolver logic is exercised end-to-end via the e2e hook-invocation tests below, not isolated unit tests (matches how #284's single-hop resolver was tested) |
| e2e | Phase 4 — full hook invocation for multi-hop `cd`/`-C` chains, both hooks |
| dogfood | Existing `tests/test_branch_guard_dogfood.py`-equivalent and any no-switch-guard dogfood suite stay green |
| integration | N/A — single-hook scope per file, no cross-command data flow |
| dependency | N/A — no new external dependency |
| count-cascade | N/A — not a new command/skill/agent |

## Documentation

- [x] `docs/reference/REFCARD-BRANCH-GUARD.md` — score ≥3 (existing #284-era section directly
      extended by this change)
- [ ] Guide/tutorial prose — N/A, internal hook behavior, not user-facing workflow change

## Session Instructions

```
cd ~/.git-worktrees/craft/feature-guard-cd-resolution && claude
```

> "Read ORCHESTRATE-guard-cd-resolution.md and start Phase 1."
