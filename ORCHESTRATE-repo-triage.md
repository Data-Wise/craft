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

- [ ] 1.1 Create `skills/orchestration/repo-triage/SKILL.md` — frontmatter,
      boundary-with-adjacent-skills table (cite `dev/git` Op 4/5/13,
      `issue-check`), procedure outline.
- [ ] 1.2 Issue triage: direct-import `classify_issue()` from
      `commands/git/issue-check.md` (GRILL Decision 9) — loop over ALL open
      issues from `gh issue list`, **no pre-filter, no concurrency cap**
      (Decision 10 — the cost the cap hedged against doesn't exist at
      direct-import speed).
- [ ] 1.3 Per-issue error handling: on a `gh issue view` failure for one
      issue, skip and record it, continue the loop (Decision 14) — never
      abort the whole run on one failure.

**Key files:** `skills/orchestration/repo-triage/SKILL.md` (NEW),
`commands/git/issue-check.md` (read-only import of `classify_issue()`, no
edits).

**Test:** integration test asserting repo-triage's issue-triage step calls
the SAME `classify_issue()` function `tests/test_issue_check_unit.py`
already tests — a regression test should fail if the two diverge (i.e. if
repo-triage ever grows its own parallel classifier).

## Phase 2: Worktree/branch triage (sequenced)

**Scope:** Depends on Phase 0's `--dry-run` contract.

- [ ] 2.1 Call `dev/git` Operation 5 (`worktree clean --dry-run`) FIRST.
- [ ] 2.2 Call `dev/git` Operation 4 (`branch cleanup --dry-run`) SECOND —
      this ordering (GRILL Decision 3) ensures no branch is locked by a
      worktree when the branch-deletion candidate is generated, closing the
      exact silent-skip gap this session hit manually (`gh pr merge
      --delete-branch` failing on a worktree-locked branch with no clear
      error).
- [ ] 2.3 Per-operation error handling: same skip-and-continue discipline as
      1.3, applied to Op 4/Op 5 collection errors.

**Key files:** none new — calls into `skills/dev/git/SKILL.md` Operations 4
and 5 as built in Phase 0.

**Test:** e2e test against a fixture repo with (a) a squash-merged branch
with a live worktree — asserts the branch/worktree candidate pair is
generated in worktree-then-branch order, not the reverse; (b) a genuinely
active feature branch — asserts it is NOT flagged.

## Phase 3: Merge + confirm UX

**Scope:** The core new logic this skill actually contributes (everything
before this point is orchestration of existing pieces).

- [ ] 3.1 Merge algorithm: join Op 4 and Op 5 candidates on `branch` (Phase
      0.2's contract) into ONE candidate item per branch when a worktree is
      coupled to it (GRILL Decision 13) — never two independent opt-outs on
      a coupled pair.
- [ ] 3.2 Confirm UX: group merged candidates by source (issues / branches /
      worktrees), show the top 4 highest-confidence items per
      `AskUserQuestion` call (sort key: evidence strength — e.g. a squash-
      merge with both ancestor-check AND scoped-diff-clean ranks above one
      with only ancestor-check), chain additional calls for remaining items
      (GRILL Decision 12 — reuses the existing pattern documented in
      `skills/code/SKILL.md` ~line 113).
- [ ] 3.3 Per-item evidence citation: issue items show the `classify_issue()`
      reasoning string; branch/worktree items show the structured evidence
      fields from Phase 0.2's contract — render both under a consistent
      one-line-summary-plus-detail template (addresses REVIEW finding #10;
      not separately GRILL-locked, design call for this phase).
- [ ] 3.4 On confirm, execute approved deletions/closures directly (skip
      Op4/Op5's own interactive confirms — already bypassed via dry-run mode
      in Phase 0/2).
- [ ] 3.5 Visibly flag any items skipped due to a collection error (Phase
      1.3/2.3) in the confirm output — "N items skipped due to error: ..."
      — never silently present a partial list as complete (GRILL Decision
      14).

**Key files:** `skills/orchestration/repo-triage/SKILL.md` (core merge/UX
logic).

**Test:** unit test for the merge/join function (worktree+branch pairing,
no coupling case, dedup); e2e test simulating a >4-item candidate set,
asserting the grouped-top-4-plus-remainder chaining fires correctly.

## Phase 4: Bucket remainder (grill-ready / plan-ready / defer)

**Scope:** Whatever is NOT flagged safe-to-delete/close after Phase 3.

- [ ] 4.1 Apply grill's own self-definition (GRILL Decision 8, reused not
      reinvented): grill-ready = genuinely unresolved load-bearing design
      branch present; plan-ready = single clear next-action, no open design
      question; defer = neither, no near-term owner/deadline.
- [ ] 4.2 ADHD-friendly output additions (not separately GRILL-locked —
      REVIEW findings #7/#8/#9, folded in here per the GRILL Handoff note):
      cap each bucket's displayed items (reuse the same top-4-plus-remainder
      pattern from 3.2, don't invent a second display mechanism), and print
      ONE explicit "start here" next action at the end of the run (highest-
      priority grill-ready item, or plan-ready if grill-ready is empty).

**Key files:** `skills/orchestration/repo-triage/SKILL.md`.

**Test:** unit test for the bucket-assignment function against fixture
issues/branches with known-correct bucket expectations.

## Phase 5: Tests + dogfood + docs

- [ ] 5.1 Full test suite per the Test-Plan Scaffold below.
- [ ] 5.2 Dogfood: run `repo-triage` against craft's own current open issues
      + worktrees as a real-world smoke test before merge (mirrors the
      2026-07-14 `github-attention-triage` brainstorm's dogfood approach).
- [ ] 5.3 Non-goal test: confirm the skill NEVER calls `git branch -D`,
      `git worktree remove`, or `gh issue close` without a preceding
      explicit confirmation captured in the same run.
- [ ] 5.4 Idempotency test (REVIEW finding #14): re-running repo-triage
      twice in a row against the same repo state produces an empty or
      shrinking candidate set, never re-proposes already-actioned items.
- [ ] 5.5 Documentation — see Documentation section below.

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

- [ ] `repo-triage` skill exists at `skills/orchestration/repo-triage/SKILL.md`.
- [ ] Issue triage reuses `classify_issue()` directly — no parallel classifier.
- [ ] Worktree cleanup always sequenced before branch cleanup within a run.
- [ ] A coupled branch+worktree pair renders as ONE confirm-list item.
- [ ] Confirm UX never attempts more than 4 `AskUserQuestion` options in a
      single call.
- [ ] A collection-step error on one item never aborts the whole run, and is
      visibly flagged in the final output.
- [ ] Nothing is deleted/closed without an explicit confirm captured in the
      same run.
- [ ] Remainder buckets (grill-ready/plan-ready/defer) use grill's own
      membership test, not an invented second taxonomy.
- [ ] One explicit "start here" next action is printed at the end of every
      run.
- [ ] Full test suite green; dogfood run against craft's own repo completes
      cleanly.

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
