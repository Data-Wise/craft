# /workflow:done

> **Session completion and context capture - never lose progress at session boundaries.**

---

## Synopsis

```bash
/workflow:done
```

---

## Description

ADHD-friendly session completion command that captures what you accomplished before you forget. Analyzes git changes, updates `.STATUS`, generates commit messages, and preserves context for next session.

**Key features:**

1. **Gather Activity** - Detect commits, changed files, current .STATUS
2. **Spec Check** - Find implementing specs for archival
3. **Doc Health** - Run documentation detectors for staleness
4. **CLAUDE.md Sync** - Auto-update counts and version (v2.30.0)
5. **Memory Capture** - Save session learnings to MEMORY.md (v2.30.0)
6. **Insights Capture** - Write friction facet JSON for analysis (v2.30.0)
7. **Worktree Status** - Show branch ahead/behind, ORCHESTRATE progress (v2.30.0)
8. **Interactive Summary** - Present findings, confirm with user
9. **Auto-Git** - Commit + push after confirmation (v2.30.0)

**ADHD Insight:** Most context loss happens at session boundaries. This command prevents that.

---

## Interactive Summary

```
+---------------------------------------------------------+
| SESSION SUMMARY                                         |
|---------------------------------------------------------|
|                                                         |
| COMPLETED:                                              |
|    - [Inferred from commits/changes]                    |
|                                                         |
| IN PROGRESS:                                            |
|    - [Uncommitted changes detected]                     |
|                                                         |
| SYNCED: [if CLAUDE.md counts changed]                   |
|    - CLAUDE.md: commands 106->107, tests 109->112       |
|                                                         |
| MEMORY: [if learnings captured]                         |
|    - Saved 2 learnings to MEMORY.md                     |
|                                                         |
| FRICTION: [if 3+ events]                                |
|    - wrong_approach (2), buggy_code (1)                 |
|    -> Run /craft:workflow:insights for full analysis     |
|                                                         |
| WORKTREE: [if in worktree]                              |
|    - Branch: feature/my-feature (+12 ahead, -0 behind)  |
|    - ORCHESTRATE: 8/15 increments complete               |
|                                                         |
| FILES CHANGED:                                          |
|    - [file1.py] - [brief description]                   |
|                                                         |
|---------------------------------------------------------|
| A) Yes - Full auto: .STATUS + commit + push + sync      |
| B) Let me edit what was completed                        |
| C) Skip .STATUS update (just suggest commit)             |
| D) Cancel (don't save anything)                          |
+---------------------------------------------------------+
```

---

## Options

| Option | What It Does |
|--------|-------------|
| **A) Full auto** | Update .STATUS, commit all changes, push to remote |
| **B) Edit** | Manually describe accomplishments, then auto-update |
| **C) Skip .STATUS** | Only generate commit message suggestion |
| **D) Cancel** | Exit without changes |

---

## Auto-Git (v2.30.0)

After Option A, automatically commits and pushes:

- Stages specific changed files (never `git add -A`)
- Generates commit message from session summary
- Pushes to current branch with `-u` flag
- If behind remote: attempts `git pull --rebase` first

**Safety constraints:**

- Never force-pushes
- Skips entirely on `main` branch
- Only pushes current branch
- Reports errors gracefully without blocking .STATUS update

---

## Learning Loop (v2.30.0)

### Memory Capture (Step 1.11)

Scans the session for learnings worth persisting:

- Errors with workarounds
- Repeated friction (2+ occurrences)
- User-stated learnings ("remember", "always", "never")

Deduplicates against existing MEMORY.md entries (60% word overlap). User confirms which learnings to save via multiSelect prompt.

### Insights Capture (Step 1.13)

Writes session metadata to `~/.claude/usage-data/facets/session-<timestamp>.json`:

- Friction events (wrong branch, undo-redo, test-fix cycles)
- Session outcome and duration
- Goal category and file count

If 3+ friction events: shows summary and suggests `/craft:workflow:insights`.

---

## Env Var Opt-Outs

| Variable | Default | Effect |
|----------|---------|--------|
| `SKIP_DOC_CHECK` | unset (runs) | Skip documentation health check |
| `SKIP_DOC_DRIFT` | unset (runs) | Skip doc drift detection |
| `SKIP_CLAUDE_MD_SYNC` | unset (runs) | Skip CLAUDE.md count sync |
| `SKIP_MEMORY_UPDATE` | unset (runs) | Skip memory capture |
| `SKIP_INSIGHTS` | unset (runs) | Skip insights facet write |
| `SKIP_WORKTREE_STATUS` | unset (runs) | Skip worktree status |
| `SKIP_GIT_SYNC` | unset (runs) | Skip auto-commit and push |

---

## Special Cases

| Scenario | Behavior |
|----------|----------|
| No .STATUS file | Suggest commit only, offer to create .STATUS |
| No git changes | Ask what was accomplished, update .STATUS only |
| No git repo | Update .STATUS only, note missing repo |
| On main branch | Skip auto-git (protected) |
| Implementing specs found | Offer to archive as complete |

---

## Typical Session Flow

```
START:  /workflow:recap      # "Where was I?"
        [work happens]
END:    /workflow:done       # "Save context"
```

**Emergency exit (30 seconds):**

```
/workflow:done → A (accept auto-summary) → done
```

---

## See Also

- **Start session:** `/workflow:recap` - Restore context
- **Decision support:** `/workflow:next` - What to do next
- **Insights:** `/craft:workflow:insights` - Friction analysis
- **Git sync:** `/craft:git:sync` - Manual push
