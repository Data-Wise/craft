# Help: /craft:orchestrate:drive

## What it does

Drives an approved SPEC to completion using Claude Code's built-in `/goal`
turn-loop. It synthesizes a measurable `/goal` condition from the spec,
iterates until the condition holds, then runs a **real verify gate** (the
project's actual tests + `git status`) as the authoritative "done" check —
stopping at verified green and printing the PR command for you to run.

## When to use — and when not

**Use it when** you have an approved spec and want autonomous completion
in an isolated `feature/*` worktree.

**Don't use it for** free-form, parallel, independent work with no single
spec — reach for `/craft:orchestrate --swarm` instead (fan-out-and-converge
across isolated worktrees).

## Quick start

```bash
# 1. Always preview first — zero side effects
/craft:orchestrate:drive --dry-run

# 2. Review the derived /goal condition + precondition report, then run for real
/craft:orchestrate:drive
```

## Precondition failures + remedies

If any precondition fails, `drive` blocks before setting a goal and shows
the remedy. Every blocker:

| Check | Block reason | Remedy |
|-------|--------------|--------|
| Worktree on `feature/*` | Not isolated — drive won't run on `dev`/`main` | `git worktree add … -b feature/<topic> dev` |
| `/goal` available (Claude Code ≥ v2.1.139) | Turn-loop engine missing | Upgrade Claude Code to ≥ v2.1.139 |
| Hooks not blocking `/goal` (`disableAllHooks` / `allowManagedHooksOnly`) | `/goal` disabled by hook policy | Adjust the hook policy in settings to allow `/goal` |
| Workspace trust accepted | `/goal` requires an accepted-trust workspace | Accept workspace trust when prompted |
| Auto mode on (unless `--no-auto`) | Loop can't run unattended | Accept the offer to enable auto mode at the confirm gate, or pass `--no-auto` to approve tools per turn |

## Reading the verify gate

When the `/goal` condition clears, the verify gate runs the project's real
verify command:

- **Green** → done. `drive` stops and prints `gh pr create --base dev`.
  Open the PR yourself.
- **Red** → not done. The loop continues — a green-looking transcript is
  never accepted in place of an actual passing run.

## See also

- `/craft:orchestrate:drive` command reference
- `/craft:orchestrate` — free-form orchestration (`--swarm`)
- Tutorial: `TUTORIAL-orchestrate-drive.md`
