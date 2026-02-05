# /craft:git:clean

> **Safely remove merged branches**

---

## Synopsis

```bash
/craft:git:clean [options]
```

**Quick examples:**

```bash
# Remove all merged branches
/craft:git:clean

# Preview which branches would be removed
/craft:git:clean --dry-run
```

---

## Description

Safely removes local branches that have been merged into the current branch. This helps maintain a clean repository by removing obsolete feature branches after they've been integrated.

The command includes multiple safety checks to prevent accidental deletion of important branches, including protection for current branch, main/master/dev branches, and branches with uncommitted changes.

---

## Options

| Option        | Description                           | Default |
|---------------|---------------------------------------|---------|
| `--dry-run`   | Preview deletions without executing   | `false` |
| `-n`          | Alias for `--dry-run`                 | `false` |

---

## Protected Branches

The following branches are **never** deleted:

- Current branch (wherever HEAD points)
- `main`, `master`, `dev` (protected branches)
- Branches with uncommitted changes
- Branches not yet merged

---

## Behavior

1. Lists all local branches
2. Checks each branch for merge status
3. Skips protected branches
4. Verifies no uncommitted changes
5. Deletes only fully-merged, non-protected branches
6. Reports number of branches removed

---

## Safety Features

- Multiple protection layers prevent accidental deletions
- Always checks merge status before deletion
- Never deletes branches with uncommitted work
- Provides clear summary of actions taken
- Dry-run mode for safe preview

---

## Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | Clean completed successfully         |
| 1    | Clean failed (permission, locked)    |
| 2    | Invalid repository state             |

---

## See Also

- [/craft:git:branch](branch.md) — Branch management
- [/craft:git:status](status.md) — Enhanced git status
- [/craft:git:sync](sync.md) — Smart git synchronization
- [/craft:git:worktree](worktree.md) — Worktree management
