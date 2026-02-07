# Git & CI Commands

Version control and continuous integration - 14 commands total.

## Worktree vs Branch: When to Use What

| Scenario | Command | Why |
|----------|---------|-----|
| Start a new feature | `/craft:git:worktree` | Isolated directory, no branch switching |
| Quick one-file fix | `/craft:git:branch` | Lightweight, stays in same directory |
| Work on 2+ features at once | `/craft:git:worktree` | Each feature gets its own directory |
| Sync with remote | `/craft:git:sync` | Fetch + merge + push intelligently |
| Clean up after merge | `/craft:git:clean` | Removes merged branches safely |
| See what's going on | `/craft:git:status` | Enhanced status with teaching mode support |
| Review recent activity | `/craft:git:recap` | Commit summary across branches |

**Decision rule:** If the change takes more than one commit or you need to context-switch, use **worktree**. For quick fixes you'll commit immediately, use **branch**.

**CI commands:**

| Scenario | Command |
|----------|---------|
| What CI does my project need? | `/craft:ci:detect` |
| Generate GitHub Actions workflow | `/craft:ci:generate` |
| Validate existing CI config | `/craft:ci:validate` |

---

## Git Commands (11)

### /craft:git:worktree

**Purpose:** Parallel development with git worktrees.

```bash
/craft:git:worktree add feature-auth
/craft:git:worktree list
/craft:git:worktree remove feature-auth
```

### /craft:git:protect

Re-enable branch protection after a temporary bypass.

```bash
/craft:git:protect
```

### /craft:git:unprotect

Temporarily bypass branch protection for the current branch (creates `.claude/allow-dev-edit` marker).

```bash
/craft:git:unprotect
```

### /craft:git:sync

Smart git sync (fetch, merge, push)

### /craft:git:clean

Clean merged branches

### /craft:git:recap

Activity summary

### Other Git Commands

- `/craft:git:branch` - Branch management
- Git guides: refcard, undo-guide, safety-rails, learning-guide

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
