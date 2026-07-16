# Report: Branch Guard Target-Resolution — Grill Ledger

> Restructured from [`GRILL-branch-guard-target-resolution-2026-07-14.md`](GRILL-branch-guard-target-resolution-2026-07-14.md), cross-linked with [`BRAINSTORM-branch-guard-target-resolution-2026-07-14.md`](../../BRAINSTORM-branch-guard-target-resolution-2026-07-14.md) and [`REPORT-branch-guard-2026-07-14.md`](REPORT-branch-guard-2026-07-14.md).

## tl;dr

| Metric | Value |
|---|---|
| Branches interrogated | 6 |
| In-scope fixes locked | 3 (A, B, C) |
| Scoped out to a follow-on | 1 |
| Open questions (unresolved) | 2 |
| Companion docs | 2 (brainstorm, rule reference) |

## Decision Ledger

**Finding / Problem / Fix**

| Finding | Problem | Fix |
|---|---|---|
| Scope pivot | Was the fix purely a parsing bug, or does it touch protection policy too? | Policy ruled in scope — widened beyond target-resolution parsing |
| `rm -rf .git` on same-repo dev | Hard-blocked with no confirm option, even for legitimate same-repo dev work | User wants confirm-not-block, in principle |
| hard_deny "same-repo" carve-out | Classifier enforces hard_deny on command *text* only, no git execution context — can't verify "same repo" | **Rejected** — the carve-out is unverifiable, so scoping the rule text doesn't work |
| Implementation of the confirm-ability | Given the carve-out is impossible, how does `rm -rf .git` become confirm-able at all? | **Remove `delete-git-dir` from the hard_deny catalog**; branch-guard.sh's HIGH tier becomes the sole gate — confirm on dev/draft, block only on `main` |
| Orchestrate/swarm concurrency | Workflow-dispatched agents may race on shared guard state (`.claude/allow-once`, `guards.json`) | **Out of scope** — separate follow-on brainstorm/grill; investigate whether the race is even real before designing a fix |
| cd/-C resolver mechanics | Does the per-clause resolver need cumulative cwd-tracking to fix the worktree-push false positive? | **Left unresolved** — dismissed twice; deferred to build time |

## Open Questions

- Whether the resolver needs cumulative cwd tracking (`cd <path> &&` updating every later clause) — without it, the worktree-push false positive only downgrades to confirm rather than resolving correctly.
- Rollout blast radius of removing `delete-git-dir` from hard_deny — affects every craft install with hard_deny enabled, not sized during the grill.

## Scope for Implementation

**In scope:**

1. Per-clause target resolution for compound Bash commands — fixes worktree-push, cross-repo-main, compound-string-match, and worktree-cleanup false positives.
2. Cross-repo `main` case → `[CONFIRM]`, not hard block.
3. Remove `delete-git-dir` from `scripts/hard-deny-rules.json` + the `/craft:git:protect` install list; branch-guard.sh's HIGH tier owns `rm -rf .git`.

**Deferred:**

- Concurrency-safety for guard state under Workflow/orchestrate parallel dispatch.

**Unresolved, needs a build-time call:**

- cd/-C cumulative-state tracking mechanics.

## Next Steps

1. Run `/craft:plan` to turn this ledger + the brainstorm into an `ORCHESTRATE-*.md` covering items 1–3.
2. Decide the cd/-C tracking mechanics before writing the parser.
3. Size the hard_deny removal's blast radius across other craft installs before shipping item 3.
4. Open a separate brainstorm/grill for orchestrate/swarm guard-state concurrency when ready to pursue it.
