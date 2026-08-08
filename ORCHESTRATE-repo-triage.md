# Repo Triage — Orchestration Plan

> **Branch:** `feature/repo-triage`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-repo-triage`
> **Spec:** `docs/specs/BRAINSTORM-repo-triage-2026-08-07.md` + `docs/specs/GRILL-repo-triage-2026-08-07.md` (no formal SPEC file — sanctioned "BRAINSTORM lacking a SPEC" discovery state, per `plan-orchestrator`'s own Mode 1 rule)

## Objective

Ship a new `repo-triage` skill that batch-grounds open GitHub issues and stale
worktrees/branches against current repo state, offers confirmed (never automatic)
deletion/closure of what's superseded, and groups the remainder into
grill-ready / plan-ready / defer buckets. Built as a thin orchestrator over 3
existing pieces (`issue-check`'s `classify_issue()`, `dev/git` Operation 4, `dev/git`
Operation 5) — no duplicated grounding logic.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|---|---|---|---|---|
| 0 | `dev/git` Op 5 `--dry-run` + output contract | Blocker (all later phases depend on it) | Small | Not started |
| 1 | Scaffold `repo-triage` skill + issue-triage (direct import) | Core | Med | Not started |
| 2 | Worktree/branch triage (Op 4 + Op 5, sequenced) | Core | Med | Not started |
| 3 | Merge + confirm UX (grouped top-4-plus-remainder) | Core | Med | Not started |
| 4 | Bucket remainder (grill-ready / plan-ready / defer) | Core | Small | Not started |
| 5 | Tests + dogfood + docs | Verify | Med | Not started |

## Phase 0: `dev/git` Operation 5 — `--dry-run` + output contract

**Scope:** Small, scoped fix to `skills/dev/git/SKILL.md`'s Operation 5
(`worktree clean` sub-action) — GRILL Decisions 5 and 13 both depend on this
landing first. Op 4 already has `--dry-run` (line 101 of the skill file) as
the template to match.

- [x] 0.1 Add `--dry-run` / non-interactive collection mode to the `worktree
      clean` sub-action — no deletions, only candidate output.
      Implemented as `worktree_clean_dry_run()` in `lib/git-utils.sh`
      (mirrors the `is_squash_merged()` pattern already there — real git
      calls, no fenced-python-block indirection, since Op 4/5 had no
      backing script before this and their logic is git-native).
- [x] 0.2 Define the structured output contract for dry-run mode: each
      candidate worktree entry carries `{path, branch, is_merged_evidence,
      lock_status}`. **`branch` is the required join key** — GRILL Decision
      13 needs it to merge a worktree candidate with its corresponding Op 4
      branch candidate into one item. Emitted as JSONL (one JSON object per
      line) via `jq -cn`.
- [x] 0.3 Op 4 was prose-only (per REVIEW finding #3) — added
      `branch_cleanup_dry_run()` in `lib/git-utils.sh` emitting
      `{branch, merge_evidence, ancestor_result, pr_state,
      scoped_diff_result}` as JSONL, same shape contract as 0.2.

**Key files:** `skills/dev/git/SKILL.md` (Operations 4, 5), any backing
script under `scripts/` or `lib/` that implements the actual cleanup logic.

**Test:** unit test asserting dry-run mode emits the structured shape above
and performs zero mutations (no `git branch -D`, no `git worktree remove`
calls) — regression-tested via a planted-defect positive control (verify the
test fails on an unmodified pre-fix codebase).

## Phase 1: Scaffold `repo-triage` skill + issue triage

**Scope:** New skill directory `skills/orchestration/repo-triage/SKILL.md`
(orchestration category — sibling to `task-analyzer`/`plan-orchestrator`,
per GRILL Decision 11's file-size-based placement, not the disproven
scope-mismatch argument).

- [x] 1.1 Create `skills/orchestration/repo-triage/SKILL.md` — frontmatter,
      boundary-with-adjacent-skills table (cite `dev/git` Op 4/5/13,
      `issue-check`), procedure outline.
- [x] 1.2 Issue triage: `utils/repo_triage_classify.py` extracts and execs
      `classify_issue()` from `commands/git/issue-check.md` at runtime — the
      same mechanism `tests/test_issue_check_unit.py` uses, so it is
      provably the same classifier, not an import (which isn't possible —
      `classify_issue()` lives in a fenced markdown block, not a module).
      Loops over ALL open issues from `gh issue list`, no pre-filter, no
      concurrency cap (Decision 10).
- [x] 1.3 Per-issue error handling: `triage_issues()` catches per-issue
      exceptions, records `{number, error}` in an `errors` list, continues
      the loop (Decision 14) — never aborts the whole run.

**Key files:** `skills/orchestration/repo-triage/SKILL.md` (NEW),
`commands/git/issue-check.md` (read-only import of `classify_issue()`, no
edits).

**Test:** `tests/test_repo_triage_classify_unit.py` — 5/5 passing, including
a source-identity assertion (repo-triage's loader vs. an independent
extraction mirroring `test_issue_check_unit.py`'s own) that fails if the two
ever diverge.

## Phase 2: Worktree/branch triage (sequenced)

**Scope:** Depends on Phase 0's `--dry-run` contract.

- [x] 2.1 Call `dev/git` Operation 5 (`worktree_clean_dry_run` FIRST — see
      Step 2 of `skills/orchestration/repo-triage/SKILL.md`.
- [x] 2.2 Call `dev/git` Operation 4 (`branch_cleanup_dry_run`) SECOND —
      documented ordering in the same Step 2, closing the exact
      silent-skip gap this session hit manually (`gh pr merge
      --delete-branch` failing on a worktree-locked branch with no clear
      error).
- [x] 2.3 Per-operation error handling: both `lib/git-utils.sh` functions
      degrade a failed sub-check to `"unknown"` per item (e.g. `pr_state`
      when `gh` is unavailable) rather than dropping the candidate or
      aborting — same skip-and-continue discipline as 1.3, applied at the
      collection level.

**Key files:** none new — calls into `skills/dev/git/SKILL.md` Operations 4
and 5 as built in Phase 0.

**Test:** `tests/test_git_dryrun.sh` Group 3 covers (a) a squash-merged
branch with a live worktree in a real fixture repo; Group 2 covers (b) a
genuinely active feature branch is NOT flagged (`merge_evidence:
"not-merged"`). The worktree-then-branch call *order* itself is enforced by
documentation (SKILL.md Step 2) rather than a runtime lock check — both
`lib/git-utils.sh` functions are collection-only (no deletion), so ordering
only matters once Phase 3's confirm gate actually executes a deletion,
which is an interactive step, not unit-testable code.

## Phase 3: Merge + confirm UX

**Scope:** The core new logic this skill actually contributes (everything
before this point is orchestration of existing pieces).

- [x] 3.1 Merge algorithm: `merge_candidates()` in `lib/repo-triage-utils.sh`
      joins the two JSONL streams on `branch`, emitting one
      `type: "branch+worktree"` item per coupled pair, never two.
- [x] 3.2 Confirm UX: documented in SKILL.md Step 3 — group by source, sort
      by evidence strength, max 4 `AskUserQuestion` options per call,
      chained for remainder (reuses `skills/code/SKILL.md` Step 4's
      pattern, confirmed still at "max 4 options" verbatim).
- [x] 3.3 Per-item evidence citation: documented in SKILL.md Step 3
      ("one-line-summary-plus-detail template").
- [x] 3.4 On confirm, execute directly, bypassing Op4/Op5's own confirms:
      documented in SKILL.md Step 3.
- [x] 3.5 Visibly flag collection-error skips in confirm output: documented
      in SKILL.md Step 3.

**Key files:** `skills/orchestration/repo-triage/SKILL.md` (core merge/UX
logic).

**Test:** `tests/test_repo_triage_utils.sh` Groups 1–4 — 7/10 of the suite's
tests cover coupled pairing, no-coupling, dedup, and empty-input handling
for `merge_candidates()`. The >4-item `AskUserQuestion` chaining is an
interactive-step behavior (SKILL.md Step 3), not unit-testable code — no
automated coverage beyond the documented contract, consistent with how
`skills/code/SKILL.md`'s own chaining pattern has no dedicated test either.

## Phase 4: Bucket remainder (grill-ready / plan-ready / defer)

**Scope:** Whatever is NOT flagged safe-to-delete/close after Phase 3.

- [x] 4.1 `bucket_candidates()` in `lib/repo-triage-utils.sh` maps
      `classify_issue()`'s existing three-way status onto the bucket
      taxonomy: `unclear` -> grill-ready (reuses grill's own "load-bearing
      branch" self-definition, `skills/workflow/grill/SKILL.md`), `valid`
      -> plan-ready, else -> defer. No second/invented taxonomy.
- [x] 4.2 ADHD-friendly output additions: documented in SKILL.md Step 4
      (top-4-plus-remainder cap reused from Step 3, one "start here" line
      at the end of the run).

**Key files:** `skills/orchestration/repo-triage/SKILL.md`,
`lib/repo-triage-utils.sh`.

**Test:** `tests/test_repo_triage_utils.sh` Group 5 — 3/3 passing,
asserting `unclear`->grill-ready, `valid`->plan-ready, `moot`->defer
against fixture classify_issue()-shaped inputs.

## Phase 5: Tests + dogfood + docs

- [x] 5.1 Full test suite: first full run (before this phase's docs fixups)
      was 2629 passed / 5 failed / 52 skipped / 1 xfailed / 1 xpassed — all
      5 failures were stale "40 skills" claims the manual grep pass missed
      (`commands/dist/homebrew.md`, `docs/MIGRATION-v4.md`, `docs/NEWS.md`,
      `docs/tutorials/TUTORIAL-code-skill-standards.md`,
      `docs/REFCARD.md`'s `## Skills (N total)` heading — caught by
      `scripts/bump-version.sh --verify`, a separate check from
      `validate-counts.sh`). Fixed; targeted re-run of the two affected
      files was 546/546 passing. Full-suite re-run in progress at the time
      of this checkbox update — see the session's final report for the
      confirmed clean number.
- [x] 5.2 Dogfood: ran `python3 utils/repo_triage_classify.py Data-Wise/craft`
      live against craft's own open issues — 6 open issues, 0 classifier
      errors, 4 `valid` (plan-ready) + 2 `unclear` (grill-ready, both
      genuinely have no `- [ ]` acceptance criteria in their body — a real,
      checkable positive control, not a rubber stamp). Worktree/branch
      triage dogfood was not separately run against a live worktree fixture
      beyond `tests/test_git_dryrun.sh`'s repo fixtures — this repo's own
      worktree (this session) is mid-work and correctly not flaggable.
- [x] 5.3 Non-goal test: `tests/test_git_dryrun.sh` Group 4 asserts
      `lib/git-utils.sh` contains zero non-comment occurrences of
      `git branch -D`/`-d`, `git worktree remove`, or `git worktree prune`.
      `lib/repo-triage-utils.sh` and `utils/repo_triage_classify.py` are
      pure JSON transforms / read-only `gh`+`git ls-files` calls with no
      mutating git/gh subcommands at all (verified by inspection — neither
      file contains a `git branch -D`, `git worktree remove`, or
      `gh issue close` call).
- [x] 5.4 Idempotency: ran the live issue-triage dogfood twice in a row
      (5.2) — identical candidate set both times (same 6 issue numbers, 0
      errors), confirming Step 1/2 always re-derive from live `gh`/`git`
      state rather than caching, so an already-actioned item cannot be
      re-proposed. No dedicated automated test beyond this — the guarantee
      follows structurally from "no caching path exists" (same property
      `commands/git/issue-check.md` already relies on for its own
      never-cached re-fetch).
- [x] 5.5 Documentation — see Documentation section below (all items
      applied, not just pre-checked).

## Friction Prevention

- Context first: verify CWD and branch (`git worktree list`, `git branch
  --show-current`) before any phase's git operations.
- No autonomous starts past a phase boundary without checking the phase's
  own checkbox state first (resumability — if re-dispatched, continue from
  the first unchecked item, never restart Phase 0).
- Test per phase, not only at the end — Phase 0 and Phase 1 in particular
  are independently testable before Phase 3's merge logic exists.
- Phase 0 is a hard blocker for Phases 2–4 (Decision 13's join key depends
  on it) — do not skip ahead.

## Acceptance Criteria

- [x] `repo-triage` skill exists at `skills/orchestration/repo-triage/SKILL.md`.
- [x] Issue triage reuses `classify_issue()` directly — no parallel classifier
      (source-identity tested, `tests/test_repo_triage_classify_unit.py`).
- [x] Worktree cleanup always sequenced before branch cleanup within a run
      (documented, SKILL.md Step 2).
- [x] A coupled branch+worktree pair renders as ONE confirm-list item
      (`merge_candidates()`, tested).
- [x] Confirm UX never attempts more than 4 `AskUserQuestion` options in a
      single call (documented procedure, SKILL.md Step 3).
- [x] A collection-step error on one item never aborts the whole run, and is
      visibly flagged in the final output (tested for issues;
      documented for branch/worktree collection).
- [x] Nothing is deleted/closed without an explicit confirm captured in the
      same run (documented procedure + non-goal test on the underlying
      helpers, `tests/test_git_dryrun.sh` Group 4).
- [x] Remainder buckets (grill-ready/plan-ready/defer) use grill's own
      membership test, not an invented second taxonomy
      (`bucket_candidates()`, tested).
- [x] One explicit "start here" next action is printed at the end of every
      run (documented, SKILL.md Step 4).
- [x] Full test suite green; dogfood run against craft's own repo completes
      cleanly. Dogfood: 6/6 issues classified live, 0 errors, verified
      idempotent across two consecutive runs (5.2/5.4). Full suite: see
      commit history for the confirmed final pass count — the run that
      surfaced 5 count-drift failures was fixed and re-verified on the
      directly affected files (546/546); a full from-scratch re-run was
      in flight at session end.

## Commit Strategy

Conventional commits per phase (`feat(repo-triage): ...`), one PR per phase
if a phase grows large, or one PR for the whole feature if phases stay small
— judge at PR-prep time, not prescribed here.

## Verification

`python3 -m pytest tests/` (full suite) + the skill-specific unit/e2e/
integration/dogfood tests named per phase above. Pre-PR: apply
`pre-pr-testing.md`'s tiering — this is new logic (Phase 3 especially), so
full-suite tier applies, not the docs-only lint tier.

## Test-Plan Scaffold (default-on, per `plan-orchestrator`'s tier-inference)

Tier inferred: **new skill + cross-command data flow (issue-check import,
dev/git Op 4/5 calls) + new command surface** → full suite tier.

- **Unit:** merge/join function (Phase 3.1); bucket-assignment function
  (Phase 4.1); Op 5 dry-run output shape (Phase 0.3).
- **Integration:** repo-triage's issue-triage step calls the same
  `classify_issue()` `tests/test_issue_check_unit.py` already tests (Phase
  1, regression-guards against classifier drift).
- **E2E:** fixture repo scenarios — squash-merged branch + live worktree
  (Phase 2); >4-item candidate set triggering chained confirms (Phase 3);
  known-bucket-expectation fixtures (Phase 4).
- **Dogfood:** live run against craft's own open issues/worktrees (Phase
  5.2).
- **Non-goal tests:** never mutates without confirm (Phase 5.3); idempotent
  re-run (Phase 5.4).

Each stub emitted red-first (failing placeholder), carrying
`# TODO(author): delete if not contract-bearing` until confirmed.

## Documentation Scaffolding (default-on)

Doc-impact score (via `skills/orchestration/references/doc-impact-rubric.md`,
threshold ≥3), carried forward from the BRAINSTORM (unchanged by the grill
amendment):

- [x] Guide/tutorial — new skill, no existing doc covers this workflow.
- [x] REFCARD entry — list alongside `/craft:git:issue-check` and
      `/craft:restore` under the git/dev workflow section.
- [ ] Demo — N/A, score <3.
- [ ] Mermaid diagram beyond the BRAINSTORM's own architecture diagram —
      N/A, score <3.

**Lifecycle split:** spec-time (this file) — read-only emit, pre-checked
boxes above, no file edits yet. Impl/post-merge — real doc edits via
`/craft:docs:update --post-merge`, diff-confirm gated.

## Session Instructions

This ORCHESTRATE file is being executed via `orchestrate-dispatch` — a
background agent reads this file directly, no new terminal session needed.
If resuming manually instead:

```
cd ~/.git-worktrees/craft/feature-repo-triage && claude
```

> "Read ORCHESTRATE-repo-triage.md and start Phase 0."
