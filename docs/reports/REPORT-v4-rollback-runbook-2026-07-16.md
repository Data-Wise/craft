# Report: v4.0.0 Cross-Repo Rollback Runbook (T4.2)

> Source: [`SPEC-v4-rollback-runbook-2026-07-16.md`](../specs/SPEC-v4-rollback-runbook-2026-07-16.md)

**Status:** SHIPPED — `docs/RUNBOOK-v4-release-rollback.md` merged via PR #293
(`06a7b919a`, "docs(T4.2): v4.0.0 train rollback runbook")

## tl;dr

| Metric | Value |
|---|---|
| Deliverable | 1 (`docs/RUNBOOK-v4-release-rollback.md`) |
| Rollback maps covered | 2 (craft, folio) |
| Acceptance criteria | 5 |
| Review checklist items | 3 |
| Open question at spec time | 1 (partial-rollback end-state) |

## What it does

Writes a single runbook covering how to undo either half of the coupled v4.0.0 train
(folio v1.0.0 first, craft v4.0.0 tag last) if a release goes bad:

1. **Craft revert map** — exact `git revert` target (the `dev→main` merge commit, or
   fall back to last-known-good tag `v2.61.2`), the Homebrew formula re-point
   procedure, and which secrets/App-installation steps are idempotent vs. need
   reversal.
2. **Folio revert map** — how to delete/re-tag a bad GitHub release, remove or
   downgrade the `homebrew-tap` formula entry, pull a bad marketplace manifest entry.
3. **Sequencing invariant** — craft's `dev→main` PR must not open until folio's
   release is fully confirmed (tag + GH release + brew install verified).

**Explicitly out of scope:** answering the doc's own open question. If a partial
rollback happens — folio ships v1.0.0 successfully but craft's v4.0.0 then fails or
stalls — is that a stable end-state on its own, or does folio need a signal that
craft hasn't caught up? The spec required this to be surfaced to the human verbatim,
never guessed.

## How it's built

- **Repo home:** lives in `craft` (the parent-session-owned repo) even though it
  covers both craft and folio — a single cross-repo runbook, not one per repo.
- **Docs-only deliverable:** no code changes, no pytest/CI tier — verification is a
  read-through confirming a human who never saw the original session could execute
  either rollback path from the file alone.
- **Cross-referencing, not duplication:** the runbook points at `tasks/plan.md`'s
  Risks table rather than restating it (memory-write-dedup-guard pattern — one home
  per fact).

## Guardrails

- **Always do:** write the runbook before any v4.0.0/folio v1.0.0 tag exists — no
  dependency on the release tasks, so it can and should run ahead of them in
  parallel.
- **Ask first:** any destructive one-liner in the runbook (`git push --force`,
  `gh release delete`, etc.) — each needs an explicit "confirm with user first"
  annotation, not a bare executable command.
- **Never do:** answer the partial-rollback question with a plausible-sounding
  default — a runbook that silently picks an answer here is worse than an
  incomplete one.

## Acceptance Criteria

- [ ] Craft revert map: exact `git revert` target, Homebrew re-point procedure,
      secrets/App-install idempotent-vs-reversal breakdown.
- [ ] Folio revert map: bad-release delete/re-tag, formula downgrade/removal,
      marketplace manifest pull.
- [ ] Sequencing invariant quoted verbatim, not just implied.
- [ ] Partial-rollback question either answered by the user (recorded verbatim) or
      explicitly surfaced and left open — never guessed.
- [ ] A human can execute at least one full rollback path from the runbook alone,
      verified by a dry read-through naming every command in order.

## Open Question (from spec)

1. If folio ships v1.0.0 but craft's v4.0.0 then fails/stalls — is that a stable
   end-state, or does folio need a signal that craft hasn't caught up? Spec-time
   status: unresolved, human decision required, not this doc's call to make.
