# guards.json Write-Race Fix — Orchestration Plan

> **Branch:** `feature/guards-json-lock`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-guards-json-lock`
> **Spec:** `docs/specs/SPEC-guard-hardening-adversarial-review-2026-07-15.md` (PR B)

## Objective

Close a confirmed lost-update race in `~/.claude/guards.json`'s mutation path (empirically
verified this session: 40/80 concurrent writes lost under the documented `jq`-mutate pattern)
with a shared mkdir-based lock helper, used by BOTH of the file's two writers —
`skills/dev/git/SKILL.md` Operation 12 and `scripts/install-guards.sh` (the second writer found
during adversarial review, previously uncovered by the original fix scope).

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|---|---|---|---|---|
| 1 | Shared mkdir-lock helper (with staleness timeout) | High | Med | ✅ |
| 2 | Wire into Operation 12 (enable/disable/profile) | High | Low | ✅ |
| 3 | Wire into install-guards.sh (seed/merge path) | High | Low | ✅ |
| 4 | `tests/test_guards_registry_concurrency.sh` | High | Med | ✅ |
| 5 | Docs correction (SKILL.md sole-mutator claim) + CHANGELOG | Med | Low | ✅ |

## Phase 1: Shared mkdir-Lock Helper

**Scope:** `mkdir` is atomic on both macOS and Linux (confirmed this session: `flock` has no
CLI on this machine's macOS — only the syscall exists). Write a small, reusable lock
acquire/release helper with a staleness timeout so a crashed caller can't wedge the lock
permanently.

- [x] 1.1 Decided: **standalone script at `lib/guards-lock.sh`** (repo already has a root-level
      `lib/` used by `branch-guard.sh` for shared helpers — reused that location rather than
      introducing a new `scripts/lib/`). Verified Operation 12's enable/disable/profile has **no
      backing script** — `skills/dev/git/SKILL.md` documents it as inline `jq`-mutate bash issued
      per-turn by the LLM, confirmed by reading Operation 12's text (line ~275) and
      `commands/git/guard.md` (thin shim, defers to the skill, no script reference). A sourced
      function can't coordinate across that and `install-guards.sh`'s separate process, so the
      helper is invoked as `bash lib/guards-lock.sh acquire|release [lockdir] [timeout]`.
- [x] 1.2 Lock acquire: `mkdir "${LOCKDIR}"` (atomic — succeeds for exactly one racer). On
      failure (lock held), poll/retry (0.1s interval, ~20s hard cap) up to the staleness timeout.
- [x] 1.3 Staleness check: lock dir mtime older than timeout (default 10s, overridable per-call)
      → treat as abandoned (crashed holder), force-acquire, log a warning to stderr.
- [x] 1.4 Lock release: `rmdir "${LOCKDIR}"`; callers wrap acquire/release with their own
      trap/cleanup around the write so a mid-write error doesn't leak the lock (see Phase 2/3).
- [x] 1.5 Read-modify-write pattern (`jq` transform → temp file → `mv` into place, THEN release)
      is the caller's responsibility per Phase 2/3 — the helper only owns acquire/release.

**Key files:** `lib/guards-lock.sh` (new). Manually verified: normal acquire/release round-trip,
and a pre-staged stale lock dir (mtime forced to 2020) force-broken and re-acquired within the
timeout.

## Phase 2: Wire into Operation 12

**Scope:** `skills/dev/git/SKILL.md`, Operation 12's `enable <name|#>` / `disable <name|#>
[--permanent|--session]` / `profile <focus|yolo|spec>` sub-actions (documented at line 275) —
currently "`jq`-mutate `guards.json` ... never raw `cat >`" with no locking.

- [x] 2.1 Updated Operation 12's documented procedure (`enable`/`disable`/`profile` sub-actions)
      to call `lib/guards-lock.sh acquire|release` immediately around its `jq`-mutate step, with
      a `trap ... EXIT` cleanup so a mid-write failure can't leak the lock.
- [x] 2.2 The mute-expiry auto-sweep only writes when it actually clears an expired mute (a plain
      `list`/`status` with nothing expired never acquires the lock) — documented explicitly at
      line 249 that the sweep goes through the same lock helper when it writes.

**Key files:** `skills/dev/git/SKILL.md` (Operation 12, line 243-277)

## Phase 3: Wire into install-guards.sh

**Scope:** Lines 159-182 — the seed-if-absent and merge-missing-entries paths. This is the
second-writer finding from the adversarial review; without this phase, PR B only half-closes
the race (Operation 12 alone would coordinate with itself but still race against a concurrent
`install-guards.sh` run).

- [x] 3.1 Wrapped both the fresh-create branch and the per-guard merge loop with
      `guards_lock_acquire`/`guards_lock_release` (thin wrappers over `lib/guards-lock.sh`),
      each with a `trap ... EXIT` cleanup. The fresh-create branch also re-checks
      `[[ ! -f "$GUARDS_JSON" ]]` **after** acquiring the lock, in case a concurrent racer
      created the file while this process was waiting.
- [x] 3.2 Confirmed and preserved: the merge loop acquires/releases **per guard iteration**, not
      once across the whole loop — each `jq -e` existence-check + `jq ... > tmp && mv` write pair
      is its own lock-guarded unit, so a concurrent Operation 12 mutation isn't blocked for the
      full loop duration.

Manually verified: ran `install-guards.sh` twice against a scratch `$HOME` (fresh-create path,
then idempotent merge-path re-run) — both exit 0, `guards.json` well-formed, lock dir cleaned up
after each run.

**Key files:** `scripts/install-guards.sh` (line 159-182)

## Phase 4: Concurrency Regression Test

**Scope:** Formalize this session's ad hoc falsification test (2 concurrent `jq`-mutate loops,
40 writes each, against a scratch copy — confirmed 40/80 writes lost pre-fix) as a permanent
test. Per GRILL decision #4, this must exercise BOTH writers now (widened in the adversarial
addendum), not just Operation 12 alone.

- [x] 4.1 `tests/test_guards_registry_concurrency.sh`: every case operates on a `mktemp -d`
      scratch copy (never the real `~/.claude/guards.json` — a hard `assert_not_real` guard
      aborts the suite if any path ever matches it). Case 1: two concurrent writers each
      incrementing a distinct field 40 times; asserts both land at exactly 40 (zero lost
      updates) under `MODE=locked` (default).
- [x] 4.2 Case 2 exercises the Phase 1/Phase 3 combination directly: one writer runs the
      Operation-12-style increment loop, the other runs install-guards.sh's per-guard
      merge-loop pattern, concurrently against the SAME scratch file. Asserts the incrementing
      writer still lands at exactly 40 and the merge writer's new guard entry survives — proves
      the shared lock, not just each writer's internal self-consistency.
- [x] 4.3 Case 3: pre-stages a lock dir with its mtime forced to 2020, then acquires with a 1s
      timeout — asserts the acquire succeeds promptly (<5s, not a hang), and that the "breaking
      stale lock" warning is actually logged.
- [x] 4.4 Red-first confirmed: `MODE=unlocked` (skips the lock entirely, reproducing the
      pre-fix code path) reliably shows lost updates in Case 1 across repeated runs (e.g.
      17/40 + 23/40, 13/40 + 27/40 — never 40/40+40/40), matching this session's earlier ad hoc
      40/80-lost finding. `MODE=locked` (post-fix, the default CI invocation) passes 7/7 across
      repeated runs with zero lost updates. Fixed one bug found along the way: `lib/guards-lock.sh`
      logged a spurious "breaking stale lock" warning when a lock dir vanished between its
      existence check and its `stat` call (the holder releasing normally, not a crash) — treated
      as an immediate-retry now instead of a false staleness signal.

**Key files:** new `tests/test_guards_registry_concurrency.sh`

## Phase 5: Docs Correction + CHANGELOG

**Scope:** `skills/dev/git/SKILL.md` line 245 currently states Operation 12 is "the sole
sanctioned mutator of `guards.json` (descriptive, not test-enforced — matches current practice,
revisit only if a second writer appears)." A second writer DID appear (install-guards.sh,
found this session) — this line needs correcting to reflect the shared-lock reality, not
deleted (the underlying convention — don't add a THIRD ad hoc writer — still holds).

- [x] 5.1 Updated `skills/dev/git/SKILL.md` line 245: "sole sanctioned mutator" claim replaced
      with "TWO sanctioned mutators ... coordinated through a shared lock," naming both Operation
      12 and `install-guards.sh`, pointing at `lib/guards-lock.sh` and the new test suite, and
      keeping the underlying convention ("don't add a third ad hoc writer without the lock").
- [x] 5.2 `CHANGELOG.md` + `docs/CHANGELOG.md` `[Unreleased]` — mirrored `### Fixed` entries
      added (verified identical wording in both files).

**Key files:** `skills/dev/git/SKILL.md`, `CHANGELOG.md`, `docs/CHANGELOG.md`

## Friction Prevention

- Verify CWD before any operation: `pwd` should show this worktree, not the main repo.
- No autonomous starts — STOP-new-session mode, no `orchestrate-dispatch` requested this session.
- Test after each phase. Phase 4's tests are the actual proof this fix works — do not skip or
  defer them to "later."
- **Never test against `~/.claude/guards.json` directly** — always a scratch copy, per this
  session's own established discipline. A bug in test setup that touches the real file would be
  a genuinely destructive mistake (could disable a guard on the live system mid-test).
- If genuine ambiguity is hit (e.g. Phase 1.1's standalone-script-vs-sourced-function shape,
  which depends on how Operation 12 is actually implemented under the hood — verify before
  assuming), leave the checkbox unchecked, add a one-line blocker note, and stop rather than
  guess.

## Acceptance Criteria

(From `SPEC-guard-hardening-adversarial-review-2026-07-15.md`, PR B subset)

- [x] Two concurrent `/craft:git:guard disable` calls (or the formalized concurrency test)
      against a scratch `guards.json` produce zero lost updates. (Case 1)
- [x] Two concurrent writes — one via Operation 12, one via `install-guards.sh`'s seed/merge
      path — against the same scratch file also produce zero lost updates. (Case 2)
- [x] `tests/test_guards_registry_concurrency.sh` exists, passes, and never touches the real
      `~/.claude/guards.json`.
- [x] `skills/dev/git/SKILL.md` Operation 12's sole-mutator claim is corrected to reflect the
      shared lock.
- [x] CHANGELOG `[Unreleased]` entry added (fix, not feat) — mirrored in `CHANGELOG.md` and
      `docs/CHANGELOG.md`.

## Commit Strategy

Conventional commits per phase (`fix(guard): ...`), squash-merged into `dev` via PR.

## Verification

```bash
bash tests/test_guards_registry_concurrency.sh
python3 -m pytest tests/ -x   # full suite, confirm no unrelated regression
```

## Test-Plan Scaffolding

| Tier | Scope |
|---|---|
| unit | N/A — lock helper is exercised via the concurrency e2e tests below, which are a more meaningful contract check than isolated unit tests for a timing-sensitive primitive |
| e2e | Phase 4 — full concurrent-writer scenarios against a scratch `guards.json` copy |
| dogfood | N/A — this is new coverage, not an existing dogfood suite to keep green |
| integration | N/A — single-file, two-caller scope, no cross-command data flow beyond the two already-identified writers |
| dependency | N/A — `mkdir`/`jq` are already-available primitives |
| count-cascade | N/A — not a new command/skill/agent |

## Documentation

- [x] `skills/dev/git/SKILL.md` — score ≥3 (existing Operation 12 section directly corrected by
      this change)
- [ ] Guide/tutorial prose — N/A, internal locking mechanism, not user-facing workflow change

## Session Instructions

```
cd ~/.git-worktrees/craft/feature-guards-json-lock && claude
```

> "Read ORCHESTRATE-guards-json-lock.md and start Phase 1."
