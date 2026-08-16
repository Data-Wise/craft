# Recipe: Triage your repo

Open issues piling up, worktrees you forgot about, branches you're not sure are safe to
delete. Ground all of it against current repo state before acting on any of it.

1. Ask naturally — "triage the repo" or "what needs attention here" — or invoke the
   `repo-triage` skill directly.
2. It batch-checks:
   - **Open GitHub issues** — still valid, or moot against current code?
   - **Worktrees** — stale (no commits in N days) or already merged?
   - **Branches** — merged-and-safe-to-delete, or still live work?
3. Read the buckets:
   - **Confirmed-safe** → offered for deletion/closure, but never automatic — you
     confirm each one.
   - **Grill-ready** → issues/ideas with enough shape to take straight into
     `/craft:grill`.
   - **Plan-ready** → already scoped enough for `/craft:plan`.
   - **Defer** → needs more context before any of the above.
4. Confirm only what you actually want gone. Nothing is deleted or closed without your
   explicit yes.

> **Why grounded, not just listed:** a plain `gh issue list` or `git worktree list`
> tells you what exists — it doesn't tell you what's still true. repo-triage checks
> each item against the current branch/commit state before bucketing it, so "closed as
> moot" and "still valid" are evidence-backed, not a guess.

See [`skills/orchestration/repo-triage/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/orchestration/repo-triage/SKILL.md).
