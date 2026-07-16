# SPEC: folio Phase 4 — Behavioral Tests + Docs/Version Gap (T4.1b, T4.1c)

**Date:** 2026-07-16 · **Status:** Approved (derived from `ORCHESTRATE-folio-split.md` Phase 4,
`tasks/plan.md`/`tasks/todo.md` T4.1b/T4.1c — no new decisions, just reformatted for `/goal`)
**Plan of record:** `ORCHESTRATE-folio-split.md` (repo root) · `tasks/todo.md` T4.1b/T4.1c
**Repo:** `folio` (NOT craft — this spec's worktree/PR target is `Data-Wise/folio`)
**Predecessor:** folio PR [#2](https://github.com/Data-Wise/folio/pull/2) (`feature/folio-do`,
`/folio:do` dispatcher — merged or not, T4.1b/T4.1c should branch from its tip, since tests must
exercise the real `do.md`, not a stub)

## Problem

CP-2 (folio's Phase 2 extraction checkpoint) flagged two gaps that were never turned into
tracked tasks: folio has zero behavioral test coverage (`tests/test_structure.py` only checks
structural things — file counts, frontmatter presence — never that a command actually does
anything), and `plugin.json` is still the placeholder `0.1.0` with only 3 stub doc pages against
16 real commands. Both block a credible v1.0.0 release (T4.3) and were caught only by directly
inspecting the repo during the 2026-07-16 Phase 4 re-planning pass, not by any existing doc.

## Scope

### In scope — two independent tasks, can run in either order (both depend only on T4.1, not

### on each other)

1. **T4.1b — behavioral test coverage** (`folio/tests/*`)
2. **T4.1c — docs + version bump** (`folio/docs/*`, `folio/.claude-plugin/plugin.json`)

### Out of scope

- Anything in `T4.3` (the actual `dev→main` release) — that has 4 explicit human-ask gates
  (PR/merge/tag/release) and is NOT a `/goal`-drivable task; do not fold it into this spec.
- Re-litigating `do.md`'s routing table (T4.1, already shipped in PR #2).

## Acceptance Criteria

- [ ] Every one of folio's 16 commands (`commands/hub.md`, `commands/do.md`, 15×
      `commands/docs/*.md`) has at least one behavioral test — not just "the file exists and has
      frontmatter," but an assertion that exercises what the command actually claims to do (e.g.
      for `do.md`: a routing-trace test that a sample phrase for each of the 16 targets resolves
      to the right command, plus an ambiguous-input case resolving to the hub fallback).
- [ ] `python3 -m pytest tests/` passes, non-zero behavioral-test count (not just the existing
      structural suite) — prove via the actual pytest summary line in the transcript.
- [ ] `folio/.claude-plugin/plugin.json`'s `version` field moves off the placeholder `0.1.0`
      toward the real v1.0.0 release target (exact value: `0.9.0` — a pre-release marker, since
      the actual `1.0.0` tag itself belongs to T4.3, not this task) — prove via `git diff` showing
      the version line changed and `scripts/bump-version.sh` (not a hand-edit) as the mechanism.
- [ ] Doc coverage extends past the 3 stub pages flagged at CP-2 — one doc page per command
      family at minimum (not necessarily all 16 individually), covering `do.md`/`hub.md`
      discovery flow plus the `docs:*` command groups. Prove via `mkdocs build --strict` (if
      folio ships a docs site) or a manual page-count `git diff --stat` against `docs/`.
- [ ] `bash scripts/validate-counts.sh` stays clean (no count-cascade drift introduced by new
      test/doc files being mistaken for new commands).

## Review Checklist

- [ ] T4.1b and T4.1c land as **separate PRs** (independent concerns, per the original
      over-bundling finding that split them out of one M-sized task in the first place — don't
      re-bundle them now for convenience).
- [ ] Neither PR touches `commands/**/*.md` behavior — this spec is tests + docs + version only,
      not a re-implementation of any command.
- [ ] New tests never depend on network access or the real `~/.claude/` state (scratch
      fixtures/temp dirs only, same discipline as craft's own test suite).
- [ ] PR descriptions cite this SPEC and the CP-2 gap it closes.

## Key Files

- `folio/tests/test_structure.py` — existing structural suite, extend or add siblings
- `folio/tests/test_do_routing.py` (new, suggested) — behavioral coverage for `do.md`
- `folio/.claude-plugin/plugin.json` — version bump target
- `folio/docs/*.md` — doc coverage target
- `folio/scripts/bump-version.sh` — the only sanctioned mechanism for the version bump

## Test Plan

`python3 -m pytest tests/` (full suite, not a subset) + `bash scripts/validate-counts.sh` +
`mkdocs build --strict` (if applicable) — all three, in the worktree the PR ships from, before
opening either PR. No e2e/dogfood tier exists yet in folio beyond pytest; this spec is what
creates the first real behavioral layer, so there's no pre-existing tier to also run.

## How to drive this

```
cd ~/.git-worktrees/folio/<worktree-for-this-spec>   # feature/* off folio's dev (or feature/folio-do tip)
/craft:orch:drive --spec docs/specs/SPEC-folio-phase4-tests-docs-2026-07-16.md
```

Note: `/craft:orch:drive` lives in **craft**, but its Step 3 precondition check (worktree on
`feature/*`, hooks/auto-mode state) is harness-level, not repo-level — it can drive a loop whose
actual dispatch/verify happens in a different repo's worktree, as long as the session's CWD for
verify commands resolves into that worktree. If in doubt, run `T4.1b`/`T4.1c` as two separate
`drive` invocations (one spec-scope each) rather than one combined loop — smaller, more provable
increments, consistent with this spec's own "two independent tasks" framing.
