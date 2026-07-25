# GRILL: Guard-Hardening Follow-Ups — Adversarial Review

**Date:** 2026-07-15 · **Target:** [`BRAINSTORM-guard-hardening-adversarial-review-2026-07-15.md`](BRAINSTORM-guard-hardening-adversarial-review-2026-07-15.md) (repo root)

## Decision Ledger

| # | Branch | Decision | Consequence |
|---|---|---|---|
| 1 | Fix approach for the confirmed `guards.json` lost-update race | **mkdir-based lock dir**, wrapping enable/disable/profile's read-modify-write, with a staleness timeout (~5s) so a crashed `/craft:git:guard` can't wedge the lock forever. Rejected: CAS-retry (more code, more subtle-bug surface) and do-nothing (rejected in branch 5, below). | `mkdir` is atomic on both macOS and Linux (unlike `flock`, which isn't guaranteed on macOS — same portability class as the `stat -f` gotcha already documented in `~/.claude/CLAUDE.md`). Implementation must include the staleness/timeout check as part of this decision, not as an afterthought — a bare lock-wait with no timeout was explicitly rejected. |
| 2 | Whether the leading-`cd` target resolver (shared by no-switch-guard.sh's new fix and branch-guard.sh's #284-deferred open question) needs cumulative-cwd tracking | **Yes — cumulative-cwd tracking**, resolved once and applied to both hooks. Rejected: per-clause-only (under-resolves multi-hop `cd a && cd b && ...` chains) and cd-always-confirms fallback (would regress #284's own fix for branch-guard.sh, which specifically moved away from over-confirming). | This is a **retroactive change to branch-guard.sh**, not just new-file scope for no-switch-guard.sh — branch-guard.sh's #284-era resolver currently does NOT do cumulative tracking (it only resolves the FIRST leading cd/-C, treating the whole command as targeting that one repo). Implementing this decision means revisiting `scripts/branch-guard.sh`'s §8d0 resolver as part of this work, not just `no-switch-guard.sh`. |
| 3 | PR bundling for item 1 (no-switch-guard cd/cumulative-cwd fix) vs. item 2 (guards.json locking) | **Two separate PRs.** Unrelated files, unrelated risk profiles (item 2 touches shared global state across all sessions on the machine; item 1 is scoped to a single hook's target resolution). | Matches the #284 precedent of calling out a risky/global-scope change (there: hard_deny catalog removal) prominently rather than burying it in a mixed diff. Two PR-review round-trips instead of one — accepted tradeoff. |
| 4 | Should the concurrency falsification test (2 background `jq`-mutate loops, 40 writes each, against a scratch `guards.json` copy — run ad hoc this session, confirmed 40/80 writes lost) become a permanent test? | **Yes — formalize as `tests/test_guards_registry_concurrency.sh`.** | Must run against a scratch copy, never the real `~/.claude/guards.json` (matches this session's own test discipline — see BRAINSTORM Context Scan). This is the regression guard for decision #1's fix; without it, a future refactor of Operation 12 could silently reintroduce the race. |
| 5 | Given the real-world trigger for the guards.json race (two sessions manually invoking `/craft:git:guard` at the literal same instant) is rare — does the fix's scope still hold, including the staleness-timeout edge case from decision #1? | **Ship the full fix as scoped, including the staleness timeout.** Rejected: lock-only-no-timeout (risks a permanently wedged lock from a crashed invocation) and document-only/no-code (rejected — a silently-lost guard-state write is security-relevant: a guard could end up disabled when the user believes it's still on, not merely an annoyance). | Confirms decision #1 stands as originally scoped — this branch was a deliberate "did we over-scope" check, not a new direction; the answer closes the loop rather than opening a new one. |

## Adversarial Review Addendum (post-lock verification pass, same session)

After the 5 branches above locked, a verification pass re-checked the load-bearing claims
against the actual code rather than trusting the just-written ledger at face value:

- **`flock` unavailability confirmed empirically** (not just asserted): `which flock` → not
  found on this machine's macOS 26.5.2; only the `flock(2)` syscall man page exists, no CLI.
  Validates decision #1's rejection of flock.
- **Branch-guard.sh's single-hop-only resolver confirmed by direct read** (`scripts/branch-guard.sh`
  line 579): the leading-`cd` regex is anchored `^[[:space:]]*cd[[:space:]]+...` — matches only a
  `cd` at the very start of the command string, structurally incapable of matching a second `cd`
  later in the chain. Validates decision #2's premise that cumulative tracking is genuinely new
  work, not already partially present.
- **`tests/test_no_switch_guard.sh` structure checked — no scaffolding gap.** It already has
  `init_repo`/`make_tmpdir`/`json_bash`/`run_green` helpers with `cwd`-override support directly
  comparable to `test_branch_guard.sh`'s cross-context group. **Resolves open question 3 below:**
  compatible, no new scaffolding needed before adding cross-context/multi-hop cases.
- **New finding: `guards.json` has a second, unguarded writer.** `skills/dev/git/SKILL.md`
  Operation 12 is documented as "the sole sanctioned mutator" of `guards.json`, but
  `scripts/install-guards.sh` (lines 164-181) also writes it directly — identical unsafe
  `jq ... > tmp && mv tmp file` pattern, no lock — when seeding a fresh registry or merging in
  missing guard entries on reinstall. Decision #1's mkdir-lock as scoped only wraps Operation
  12's `enable`/`disable`/`profile` path; `install-guards.sh`'s write is a second race surface the
  original decision didn't cover.
  - **Resolution (Recommended, auto-picked — no override given):** extract a shared lock helper
    (a small `_guards_json_locked_write()` function or a sourced script) and have
    `install-guards.sh` call it too, not just Operation 12. This also makes the "sole sanctioned
    mutator" doc claim literally true instead of aspirational — worth folding into the same
    doc-update task already scoped for PR B.
  - **PR B scope, updated:** now includes `scripts/install-guards.sh`'s seed/merge write path,
    not just `skills/dev/git/SKILL.md` Operation 12.

## Open Questions (not locked — carry into implementation)

- **Exact staleness-timeout value** for the mkdir-lock (decision #1/#5 named "~5s" as an illustrative figure, not a locked number) — left to implementation judgment, matching how #284's GRILL left some mechanics ("cd/-C tracking" itself, at the time) to the builder.
- **Whether branch-guard.sh's cumulative-cwd retrofit (decision #2) needs its own test-plan update** beyond what's already scaffolded in the BRAINSTORM's Test-Plan section — the existing `tests/test_branch_guard.sh` cross-context group (added in #284) tests single-hop `cd`/`-C` only; multi-hop cases are new coverage, not just a re-run of existing cases.
- ~~Does `tests/test_no_switch_guard.sh` have a structure compatible with adding cross-context cases?~~ **Resolved in the Adversarial Review Addendum above** — yes, compatible, no scaffolding gap.

## Scope Summary for `/craft:plan`

**In scope for the next implementation pass (two PRs, per decision #3):**

**PR A — no-switch-guard.sh + branch-guard.sh cd-target resolution:**

1. Give `no-switch-guard.sh`'s `git_dir` resolution the same leading-`cd` handling branch-guard.sh got in #284, PLUS cumulative-cwd tracking (decision #2) — applies to both files, so branch-guard.sh's §8d0 resolver also needs the cumulative-tracking retrofit, not just no-switch-guard.sh's new code.
2. New/extended test coverage for multi-hop `cd` chains in both `tests/test_branch_guard.sh` and `tests/test_no_switch_guard.sh` (confirmed compatible, no scaffolding gap — see addendum).

**PR B — guards.json write-race fix:**

1. Shared mkdir-based lock helper with a staleness timeout (decision #1/#5), used by BOTH `skills/dev/git/SKILL.md` Operation 12's `enable`/`disable`/`profile` mutation AND `scripts/install-guards.sh`'s seed/merge write path (widened in the Adversarial Review Addendum — install-guards.sh is a second, previously-uncovered writer).
2. New `tests/test_guards_registry_concurrency.sh` (decision #4), scratch-copy-only — should exercise the shared helper from both call sites, not just Operation 12.
3. Doc update: `skills/dev/git/SKILL.md` Operation 12's "sole sanctioned mutator ... descriptive, not test-enforced" line needs correcting once real locking exists AND install-guards.sh is folded in — it currently overstates informality where a real, shared guarantee will now exist.

**Explicitly re-scoped out of the original two deferred items (per the BRAINSTORM's Context Scan, not re-grilled here since it was a factual disproof, not a decision):**

- The "compound `main` substring" and "worktree-cleanup blocked as a unit" framing for no-switch-guard.sh — does not reproduce; dropped.

## Next Steps

1. Run `/craft:plan` on this ledger + the BRAINSTORM to route into `plan-orchestrator` for PR A and PR B (likely as two separate `ORCHESTRATE-*.md` artifacts, given decision #3).
2. Before implementation, verify `tests/test_no_switch_guard.sh`'s structure (open question above) — informs whether PR A's test work is "extend existing" or "add new scaffolding."
3. One-line correction to `docs/specs/GRILL-branch-guard-target-resolution-2026-07-14.md`'s "Scope Summary" noting decision #5 there ("no-switch-guard same pattern") was re-investigated and found not to reproduce as originally described — still outstanding from the BRAINSTORM's own Next Steps, not yet done.
