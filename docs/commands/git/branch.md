# /craft:git:branch

> **Interactive assistant for branch management**

---

## Synopsis

```bash
/craft:git:branch [action] [name] [options]
```

**Quick examples:**

```bash
# Show branch status
/craft:git:branch

# Create new feature branch
/craft:git:branch new feature/auth

# Switch to existing branch
/craft:git:branch switch dev

# Delete branch (with confirmation)
/craft:git:branch delete old-feature
```

---

## Description

Interactive assistant for creating, switching, and managing git branches. Provides guided workflows for common branch operations with built-in safety checks and protection for critical branches.

When called without arguments, shows the current branch and lists all local branches. With actions, provides step-by-step guidance for branch operations.

---

## Actions

| Action   | Description                              | Args Required |
|----------|------------------------------------------|---------------|
| (none)   | Show current branch and list all         | No            |
| `new`    | Create and switch to new branch          | `name`        |
| `switch` | Switch to existing branch                | `name`        |
| `delete` | Delete branch (with confirmation)        | `name`        |
| `sync`   | Sync current branch with remote          | No            |

---

## Options

| Option        | Description                           | Default |
|---------------|---------------------------------------|---------|
| `--dry-run`   | Preview operations without executing  | `false` |
| `-n`          | Alias for `--dry-run`                 | `false` |

---

## Protected Branches

The following branches **cannot** be deleted:

- `main`, `master` — Production branches
- `dev` — Integration branch
- Current branch (wherever HEAD points)

Attempting to delete protected branches results in an error with explanation.

---

## Safety Features

- Confirms before deletion (unless `--force` specified)
- Never deletes protected branches
- Checks for uncommitted changes before switching
- Validates branch names (no spaces, special chars)
- Warns if switching would lose uncommitted work

---

## Branch Naming Conventions

Recommended patterns:

- `feature/*` — New features (e.g., `feature/auth`)
- `fix/*` — Bug fixes (e.g., `fix/login-error`)
- `docs/*` — Documentation (e.g., `docs/api-guide`)
- `refactor/*` — Code refactoring
- `test/*` — Test additions/fixes

---

## Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | Operation completed successfully     |
| 1    | Operation failed (invalid name, etc.)|
| 2    | User canceled operation              |
| 3    | Protected branch operation blocked   |

---

## See Also

- [/craft:git:worktree](worktree.md) — Worktree management (recommended for features)
- [/craft:git:status](status.md) — Enhanced git status
- [/craft:git:clean](clean.md) — Remove merged branches
- [/craft:git:sync](sync.md) — Smart git synchronization
- [Git Workflow Guide](../../guide/worktree-advanced-patterns.md) — Branch workflow patterns
