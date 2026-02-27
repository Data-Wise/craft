# Session Wrap-Up Workflow

> Quick recipe: end your session without losing context.

---

## The 30-Second Path

```bash
/workflow:done
# --> Review auto-detected summary
# --> Press A (full auto)
# --> Done: .STATUS updated, committed, pushed
```

That's it. Everything else is automatic.

---

## What Gets Captured

| Item | Source | Automatic? |
|------|--------|------------|
| Accomplishments | Git commits + diff | Yes |
| In-progress work | Uncommitted changes | Yes |
| .STATUS update | Session context | Yes |
| CLAUDE.md counts | Discovery engine | Yes |
| Commit + push | Auto-git | Yes (Option A) |
| Memory learnings | Session friction scan | Prompted |
| Insights facet | Friction metadata | Yes (silent) |

---

## Common Patterns

### Feature Development Session

```bash
# After implementing a feature...
/workflow:done

# Summary shows:
#   COMPLETED: Implemented auth endpoints
#   WORKTREE: feature/auth (+8 ahead, -0 behind dev)
#   ORCHESTRATE: 5/10 increments complete
#
# --> A (auto)
# --> Committed: feat: implement auth endpoints (abc1234)
# --> Pushed: origin/feature/auth
```

### Bug Fix Session

```bash
# After fixing a bug...
/workflow:done

# Summary shows:
#   COMPLETED: Fixed login redirect loop
#   FILES: 2 changed
#
# --> A (auto)
# --> Committed: fix: login redirect loop (def5678)
```

### Documentation Session

```bash
# After writing docs...
/workflow:done

# Summary shows:
#   COMPLETED: Updated API docs, added tutorial
#   SYNCED: CLAUDE.md commands 106->107
#
# --> A (auto)
```

### Emergency Exit

```bash
# Must stop NOW
/workflow:done
# --> A
# 30 seconds total, context saved
```

---

## Opting Out of Steps

Skip any step independently:

```bash
# Skip auto-git (commit/push manually later)
SKIP_GIT_SYNC=1

# Skip memory prompts (no learning capture)
SKIP_MEMORY_UPDATE=1

# Skip everything except .STATUS
SKIP_DOC_CHECK=1 SKIP_CLAUDE_MD_SYNC=1 SKIP_INSIGHTS=1 SKIP_WORKTREE_STATUS=1
```

---

## Next Session

Start your next session with:

```bash
/workflow:recap    # Restores context from .STATUS
/craft:hub         # See next action + worktree status
```

---

## See Also

- [Learning Loop Guide](../../guide/learning-loop-session-completion.md)
- [/workflow:done Reference](../../commands/workflow/done.md)
