# Git & CI Commands

Version control and continuous integration.

> **Note (2026-07 v4 consolidation):** All git commands — worktree, sync, recap,
> init, branch protection, guard management, status, cleanup, and quick-branch
> creation — were folded into the `dev/git` skill; there are no longer separate
> slash commands under `/craft:git:*`. Ask naturally ("create a worktree for
> feature-auth", "protect this branch", "check guard status", "clean up merged
> branches") or see
> [`skills/dev/git/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/dev/git/SKILL.md)
> directly.

## Worktree vs Branch: When to Use What

| Scenario | Ask | Why |
|----------|-----|-----|
| Start a new feature | "create a worktree for feature-x" | Isolated directory, no branch switching |
| Quick one-file fix | "create feature branch x" | Lightweight, stays in same directory |
| Work on 2+ features at once | "create a worktree for feature-x" | Each feature gets its own directory |
| Clean up after merge | "clean up merged branches" | Removes merged branches safely |
| See what's going on | "show git status" | Enhanced status with teaching mode support |

**Decision rule:** If the change takes more than one commit or you need to context-switch, use **worktree**. For quick fixes you'll commit immediately, use **branch**.

**CI commands:**

| Scenario | Command |
|----------|---------|
| What CI does my project need? | `/craft:ci:detect` |
| Generate GitHub Actions workflow | `/craft:ci:generate` |
| Validate existing CI config | `/craft:ci:validate` |

---

## Git Commands (0)

Worktree, sync, recap, init, protect, unprotect, status, clean, branch, and
guard were all folded into the `dev/git` skill (2026-07 v4 consolidation) —
ask naturally ("create a worktree for feature-auth", "protect this branch",
"unprotect for a merge conflict", "check guard status", "clean up merged
branches", "create feature branch x") or see
[`skills/dev/git/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/dev/git/SKILL.md).

## CI Commands (3)

### /craft:ci:detect

Smart detection of project type, build tools, and CI requirements

```bash
/craft:ci:detect
```

### /craft:ci:generate

Generate GitHub Actions workflow from detection

```bash
/craft:ci:generate
```

### /craft:ci:validate

Validate existing CI workflow against project configuration

```bash
/craft:ci:validate
```
