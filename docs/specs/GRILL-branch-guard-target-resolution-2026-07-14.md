# GRILL: Branch Guard Target-Resolution Fix

**Date:** 2026-07-14 · **Target:** [`BRAINSTORM-branch-guard-target-resolution-2026-07-14.md`](../../BRAINSTORM-branch-guard-target-resolution-2026-07-14.md) (repo root)
**Related:** [`REPORT-branch-guard-2026-07-14.md`](REPORT-branch-guard-2026-07-14.md)

## Decision Ledger

| # | Branch | Decision | Consequence |
|---|---|---|---|
| 1 | Scope pivot: is the fix purely technical or does it touch policy? | **Policy is in scope.** The grill surfaced that the brainstorm's locked confirm-not-block stance (for cross-repo `main`) implies a broader question: should HIGH-tier catastrophic ops also prefer confirm over hard-block when same-repo? | Widened this session beyond pure target-resolution parsing into a hard_deny policy question — see decisions 2–3. |
| 2 | Should `rm -rf .git` be confirm-able (not hard-blocked) when run against the session's own repo on dev/draft? | **Yes, in principle** — user does not want a hard gate disrupting legitimate same-repo dev work, even for catastrophic ops. | Requires moving `delete-git-dir` out of the classifier-level hard_deny layer, since... |
| 3 | Can hard_deny's rule text be scoped to "same-repo only" so cross-repo/cross-context `rm -rf .git` stays bypass-proof while same-repo dev gets confirm? | **No — rejected on adversarial review.** hard_deny is enforced by the Claude Code classifier against command *text*, with no git execution context (no cwd resolution, no repo identity check). A "same-repo" carve-out is something the classifier structurally cannot verify — it would either not apply (rule still blocks unconditionally) or over-apply (drops protection whenever no `-C`/`cd` is textually present, which is exactly what an accidental same-directory `rm -rf .git` looks like too, i.e. no way to discriminate). | Ruled out the "scope hard_deny" path explored in decision 2's first pass. |
| 4 | Given decision 3, how does `rm -rf .git` confirm-ability actually get implemented? | **Remove `delete-git-dir` from the hard_deny catalog entirely; branch-guard.sh's own HIGH tier (which has real git context — session cwd, resolved branch) becomes the sole gate: `[CONFIRM]` on dev/draft, hard block only on `main`.** | **Global trade-off, not a same-repo-only one**: the "survives forgotten session bypass" guarantee is lost everywhere `delete-git-dir` previously applied — including cross-repo and main-adjacent cases — because hard_deny cannot partially apply. This is the real cost of decision 2's ask; the user chose it knowingly after the adversarial finding. |
| 5 | Concurrent Workflow-dispatched agents racing on shared guard state (`.claude/allow-once`, `guards.json`) during orchestrate/swarm dispatch | **Out of scope for this fix — separate follow-on brainstorm/grill.** Genuinely distinct failure class (concurrency-safety vs. target-resolution); bundling risks an under-tested design and violates the brainstorm's own decision #5 (scope discipline). | This fix stays limited to: the 4 original target-resolution false positives (brainstorm decisions 1–4) + the hard_deny `delete-git-dir` removal (this ledger's decisions 2–4). A concurrency-safety GRILL/BRAINSTORM is a distinct next initiative — first step there should be *investigating* whether markers are already session/worktree-scoped before assuming a race exists. |
| — | cd/-C stateful-vs-stateless clause resolution (mechanics of decision 1 in the brainstorm) | **Deliberately left unresolved** — dismissed twice during the grill loop. Signal read as: this is implementation-detail territory better resolved during build, not further interrogation rounds. | Flagged as an **open question** below; the eventual implementer must still decide cumulative-cwd-tracking vs. per-clause-only before writing the parser, since it materially changes whether problem #1 (worktree push) actually gets fixed or only downgraded to confirm. |

## Open Questions (not locked — carry into implementation)

- **cd vs. -C state tracking**: does the per-clause resolver need cumulative-cwd tracking (a bare `cd <path> &&` updates all subsequent clauses) to correctly fix problem #1, or is a downgrade-to-confirm fallback acceptable for that specific pattern? Three options were on the table (cumulative tracking / independent-per-clause / cd-always-confirms) — none was selected.
- **hard_deny removal blast radius**: removing `delete-git-dir` from the catalog affects *all* craft installs that ran `/craft:git:protect` with hard_deny enabled, not just this repo. Before implementing decision 4, check how many active installs currently rely on it (git-grep other repos' `~/.claude/settings.json` equivalents, or at minimum flag this prominently in the PR description) — this wasn't explored in the grill and is a real rollout-risk gap.
- **Does branch-guard.sh's HIGH tier, once it's the sole gate, need its own bypass-proofing** (e.g. does `[CONFIRM]` on a catastrophic op need a stronger confirmation UX than the existing one-shot MEDIUM-tier flow, given the removed hard_deny guarantee)? Not discussed.

## Scope Summary for `/craft:plan`

**In scope for the next implementation pass:**

1. Per-clause target resolution for compound Bash commands (brainstorm decisions 1–4: fixes worktree-push, cross-repo-main, compound-string-match, worktree-cleanup false positives).
2. Cross-repo `main` case → `[CONFIRM]`, not hard block (brainstorm decision 2).
3. Remove `delete-git-dir` from `scripts/hard-deny-rules.json` + `/craft:git:protect` install list; let branch-guard.sh's HIGH tier own `rm -rf .git` (confirm on dev/draft, block on main) (this ledger's decisions 2–4).

> **2026-07-15 correction:** item 1's "compound-string-match, worktree-cleanup false
> positives" claim for `no-switch-guard.sh` did not hold up under a follow-up adversarial
> re-check — neither scenario reproduces in that file (verified by direct code read; see
> [`BRAINSTORM-guard-hardening-adversarial-review-2026-07-15.md`](../../BRAINSTORM-guard-hardening-adversarial-review-2026-07-15.md)
> Context Scan). The real bug found instead — `no-switch-guard.sh`'s `git_dir` resolution
> only honored `-C`, never a leading `cd` — was fixed in
> [#287](https://github.com/Data-Wise/craft/pull/287), together with a retrofit of
> `branch-guard.sh`'s own single-hop #284 resolver to cumulative-cwd tracking.

**Explicitly out of scope, deferred to a separate initiative:**

- Concurrency-safety for guard state under Workflow/orchestrate parallel dispatch (this ledger's decision 5).

> **2026-07-15 update:** addressed, broader than originally scoped. The 2026-07-15
> adversarial review found and fixed a real, empirically-confirmed lost-update race in
> `~/.claude/guards.json`'s write path — not scoped to Workflow/orchestrate dispatch
> specifically, but the same class of concurrent-write hazard this decision anticipated.
> Fixed in [#288](https://github.com/Data-Wise/craft/pull/288) (shared mkdir-lock helper,
> both writers). See
> [`GRILL-guard-hardening-adversarial-review-2026-07-15.md`](GRILL-guard-hardening-adversarial-review-2026-07-15.md).

**Unresolved, needs a build-time decision (not re-grilled):**

- cd/-C cumulative-state tracking mechanics.

> **2026-07-15 resolution:** locked as **cumulative-cwd tracking** (not per-clause-only or
> cd-always-confirms) during the 2026-07-15 grill, and implemented in both
> `no-switch-guard.sh` and a retrofit of `branch-guard.sh`'s #284-era single-hop resolver.
> Shipped in [#287](https://github.com/Data-Wise/craft/pull/287).
