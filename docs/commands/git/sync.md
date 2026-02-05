# /craft:git:sync

> **Smart git synchronization with remote repositories**

---

## Synopsis

```bash
/craft:git:sync [options]
```

**Quick examples:**

```bash
# Sync current branch with remote
/craft:git:sync

# Preview sync operations without executing
/craft:git:sync --dry-run
```

---

## Description

Safely synchronizes your local branch with its remote counterpart using an intelligent pull-rebase-push workflow. The command pulls the latest changes with rebase to maintain a clean history, then pushes your local commits to the remote.

This is safer than manual git operations because it validates the state before syncing, ensures you're not in a detached HEAD state, and aborts on conflicts rather than leaving your repository in an uncertain state.

---

## Options

| Option        | Description                           | Default |
|---------------|---------------------------------------|---------|
| `--dry-run`   | Preview operations without executing  | `false` |
| `-n`          | Alias for `--dry-run`                 | `false` |

---

## Behavior

- Validates current branch has a remote tracking branch
- Pulls with rebase (`git pull --rebase`) to avoid merge commits
- Pushes local commits to remote
- Aborts on conflicts and provides clear error messages
- Skips if no remote tracking branch is configured

---

## Safety Features

- Checks for uncommitted changes before syncing
- Validates repository state (not detached HEAD)
- Aborts on rebase conflicts with recovery instructions
- Never forces pushes (respects remote history)

---

## Exit Codes

| Code | Meaning                              |
|------|--------------------------------------|
| 0    | Sync completed successfully          |
| 1    | Sync failed (conflicts, no remote)   |
| 2    | Invalid repository state             |

---

## See Also

- [/craft:git:status](status.md) — Enhanced git status
- [/craft:git:branch](branch.md) — Branch management
- [/craft:git:worktree](worktree.md) — Worktree management
- [/craft:git:clean](clean.md) — Remove merged branches
