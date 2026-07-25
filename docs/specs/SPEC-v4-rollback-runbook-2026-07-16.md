# SPEC: v4.0.0 Train — Cross-Repo Rollback Runbook (T4.2)

**Date:** 2026-07-16 · **Status:** Approved for the drivable portion; ONE open question
explicitly blocks full completion — see Problem
**Plan of record:** `docs/plans/ORCHESTRATE-folio-split.md` (moved from repo root 2026-07-24) · `tasks/todo.md` T4.2 ·
`tasks/plan.md` Risks table
**Repo:** `craft` (this runbook lives in craft, the parent-session-owned repo, even though it
covers both craft and folio)

## Problem

The v4.0.0 train ships two coupled releases in a specific order (folio v1.0.0 first, craft
v4.0.0 tag last). If either release goes bad, there's no written runbook for how to undo it —
today that knowledge exists only in this session's transcript and the plan docs' Risks table.
Most of the runbook is mechanical (which commit/PR to revert, how to re-point Homebrew/tap, how
to yank a bad tag) and fully specifiable now. **One sub-question is NOT mechanical and has no
answer yet**: if folio ships v1.0.0 successfully and craft's v4.0.0 release then fails or stalls
for an extended period, is that a stable, acceptable end-state on its own, or does folio need
some signal/flag that craft hasn't caught up yet? This needs a human decision, not an assumption.

## Scope

### In scope

- Full revert map for craft: which commit/PR to revert if v4.0.0 is bad, how to re-point
  Homebrew/tap back to `2.61.2`.
- Full revert map for folio: how to yank a bad `v1.0.0` tag/release and unpublish from
  tap/marketplace.
- The cross-repo sequencing risk this phase's own ordering creates: explicit statement that
  craft must NOT tag v4.0.0 if folio's release fails partway.

### Explicitly out of scope / stop condition

- **Do not answer the partial-rollback question yourself.** If the drive loop reaches the point
  of writing that section, it must present the question verbatim (as phrased in Problem above)
  and stop — treat it the same as any other precondition failure requiring human input, not
  something to resolve via a plausible-sounding default. A runbook that silently picks an answer
  here is worse than an incomplete one.

## Acceptance Criteria

- [ ] `docs/RUNBOOK-v4-release-rollback.md` exists with a craft revert map: exact `git revert`
      target (the `dev→main` merge commit once it exists, or the last-known-good tag
      `v2.61.2`), the Homebrew formula re-point procedure, and which secrets/App installation
      steps (if any) need no action (idempotent) vs. reversal.
- [ ] Same file has a folio revert map: how to delete/re-tag a bad GitHub release, how to remove
      or downgrade the `homebrew-tap` formula entry, how to pull a bad marketplace manifest
      entry.
- [ ] An explicit "sequencing invariant" statement: craft's `dev→main` PR (T4.4) must not be
      opened until folio's T4.3 is confirmed fully released (tag + GH release + brew install
      verified) — prove this is stated, not just implied, by quoting the exact sentence in the
      transcript.
- [ ] The partial-rollback question (Problem, second paragraph) is either (a) answered by the
      user mid-loop and the answer is recorded verbatim in the runbook, or (b) the loop stops
      and reports the question rather than guessing. Either outcome satisfies this criterion —
      guessing does not.
- [ ] A human can execute either rollback (craft or folio) from the runbook alone, with no
      further research — verified by a dry read-through naming every command that would need to
      be run, in order, for at least one of the two rollback paths.

## Review Checklist

- [ ] Runbook is written BEFORE any tag exists for v4.0.0 or folio v1.0.0 (this task has no
      dependency on T4.1/T4.1b/T4.1c/T4.0 — it can and should run in parallel, ahead of T4.3).
- [ ] No destructive command in the runbook is phrased as a plain executable one-liner without
      a confirm step noted alongside it (`git push --force`, `gh release delete`, etc. all need
      an explicit "confirm with user first" annotation, consistent with this session's standing
      git-safety rules).
- [ ] The runbook cross-references `tasks/plan.md`'s Risks table rather than duplicating its
      prose (per this project's memory-write-dedup-guard pattern — one home per fact).

## Key Files

- `docs/RUNBOOK-v4-release-rollback.md` (new)
- `tasks/plan.md` (Risks and Mitigations table — cross-link only, don't duplicate)
- `ORCHESTRATE-folio-split.md` (Phase 4 section — add a one-line pointer once the runbook exists)

## Test Plan

No code changes — this is a docs-only deliverable. Verification is a read-through: can a human
who has never seen this session execute either rollback path using only the runbook? No
pytest/CI tier applies; do not invent one.

## How to drive this

```
# craft repo, feature worktree (docs-only work is otherwise dev-eligible per spec-only-mode.md,
# but drive requires a feature/* worktree per its own Step 3 precondition)
git worktree add ~/.git-worktrees/craft/feature-v4-rollback-runbook -b feature/v4-rollback-runbook dev
cd ~/.git-worktrees/craft/feature-v4-rollback-runbook
/craft:orch:drive --spec docs/specs/SPEC-v4-rollback-runbook-2026-07-16.md
```

If the loop hits the partial-rollback question and you want to answer it inline rather than
waiting for the loop to stop, answer it before invoking `drive` by adding your decision as a
one-line addendum to this SPEC's Problem section — the condition synthesis (drive Step 4) will
then treat it as already-resolved instead of a blocker.
