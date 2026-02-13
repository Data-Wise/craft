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

Re-enable branch protection, configure levels, view status.

```bash
/craft:git:protect              # Re-enable protection
/craft:git:protect --show       # Show current level + session counters
/craft:git:protect --level smart  # Set protection level
/craft:git:protect --reset      # Reset session counters (verbosity restarts)
```

**Protection levels:**

| Level | Behavior | Default For |
|-------|----------|-------------|
| `block-all` | Hard block everything | main, master |
| `smart` | 3-tier risk: LOW (allow) / MEDIUM (confirm) / HIGH (block) | dev, develop |

### /craft:git:unprotect

Session-wide bypass for branch protection with reason logging.

```bash
/craft:git:unprotect                 # Interactive (asks for reason)
/craft:git:unprotect merge-conflict  # Bypass for merge conflicts
/craft:git:unprotect ci-fix          # Bypass for CI fixes
/craft:git:unprotect maintenance     # Bypass for maintenance
```

**Two bypass mechanisms:**

| Mechanism | Scope | Duration |
|-----------|-------|----------|
| One-shot (approve `[CONFIRM]`) | Single action | Consumed immediately |
| `/craft:git:unprotect` | All actions | Until `/craft:git:protect` |

### /craft:git:status

Enhanced git status with branch guard indicator.

```bash
/craft:git:status           # Shows guard level, session confirms, one-shot status
/craft:git:status --verbose # Additional details
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
