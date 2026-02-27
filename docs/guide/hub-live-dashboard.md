# Hub Live Dashboard

> Understanding the dynamic sections of `/craft:hub` — live counts, next actions, worktree status, and recently used commands.

---

## Overview

Since v2.30.0, `/craft:hub` displays a live dashboard that pulls data from multiple sources. No hardcoded numbers — everything is computed at display time.

---

## Dashboard Sections

### Banner Line (Live Counts)

```
CRAFT - Full Stack Developer Toolkit v2.29.0
{stats['total']} commands | {skill_count} skills | {agent_count} agents | {test_count} tests passing
```

**Data sources:**

| Count | Source | How It's Loaded |
|-------|--------|-----------------|
| Commands | `commands/_discovery.py` | `get_command_stats()['total']` |
| Skills | `skills/*.md` | Glob count of `.md` files |
| Agents | `agents/*.md` | Glob count of `.md` files |
| Tests | `CLAUDE.md` or `.STATUS` | Regex: `(\d+)\s+tests?\s+pass` |

If test count can't be determined, displays `?`.

### Next Action

```
NEXT ACTION:
   A) Implement Phase 3 learning loop (recommended)
   B) Review PR #42
   C) Update documentation
```

**Data source:** `.STATUS` file, `Next Action` section.

Parses multi-option format (A/B/C entries with descriptions). If `.STATUS` doesn't exist or has no Next Action section, this row is omitted entirely.

### Worktree Status

```
WORKTREES:
   ~/.git-worktrees/craft/feature-auth  feature/auth  +8 ahead  3 uncommitted  2d ago
   ~/.git-worktrees/craft/feature-ui    feature/ui    +2 ahead  0 uncommitted  5h ago
```

**Data source:** `git worktree list --porcelain`

For each worktree (excluding main working tree):

| Column | Source |
|--------|--------|
| Path | Worktree path from porcelain output |
| Branch | `git -C <path> branch --show-current` |
| Ahead/behind | `git rev-list --count dev..HEAD` / `HEAD..dev` |
| Uncommitted | `git -C <path> status --short \| wc -l` |
| Staleness | Last commit date — flagged if 3+ days old |

If no worktrees exist besides the main working tree, this section is hidden.

### Recently Used

```
Recently Used:
   /craft:do (3x) - /craft:check (2x) - /workflow:done (2x)
```

**Data source:** `~/.claude/usage-data/facets/session-*.json`

Reads the last 10 facet files, extracts `commands_used` arrays, and shows the top 5 commands by frequency. If no facets directory or files exist, this row is hidden.

---

## Smart Commands Grid

The main hub body shows categorized commands in a two-column grid:

```
SMART COMMANDS (Start Here):
   /craft:do "task"           Route any task intelligently
   /craft:check               Pre-flight validation
   /craft:hub                 You are here

CODE (12)                   DOCS (22)
   /craft:code:lint            /craft:docs:update
   ...                         ...
```

Command counts next to category names are live from `stats['categories']`.

---

## Quick Actions Footer

```
Quick Actions:
   /craft:do "fix bug"          /craft:check --for pr
   /brainstorm d f s "auth"     /craft:git:worktree create feat/x
   /craft:test debug            /release --dry-run
   /craft:git:sync              /craft:insights --since 7
```

These are static suggestions — curated examples of common workflows.

---

## Reading the Dashboard

### Typical Healthy State

```
107 commands | 26 skills | 8 agents | 112 tests passing

NEXT ACTION:
   A) Start Phase 3 implementation

WORKTREES:
   feature/workflow-enhancements  +4 ahead  0 uncommitted  1h ago

Recently Used:
   /craft:do (5x) - /workflow:done (3x) - /craft:check (2x)
```

Everything populated, no staleness warnings.

### Degraded State (Missing Data)

```
107 commands | 26 skills | 8 agents | ? tests passing
```

Only the banner line shows — no Next Action (no .STATUS), no Worktrees (none exist), no Recently Used (no facets). The hub still works; sections appear as data becomes available.

### Stale Worktree Warning

```
WORKTREES:
   feature/old-experiment  +0 ahead  0 uncommitted  5d ago  [STALE]
```

Worktrees with no commits in 3+ days are flagged. Consider cleaning up with `git worktree remove`.

---

## Graceful Degradation

Every dashboard section degrades independently:

| Section | Missing Data | Behavior |
|---------|-------------|----------|
| Banner counts | Discovery engine fails | Falls back to `?` |
| Next Action | No .STATUS file | Section hidden |
| Worktrees | No worktrees | Section hidden |
| Recently Used | No facets directory | Section hidden |

The hub always displays the command grid — dynamic sections are additive.

---

## See Also

- [Learning Loop Guide](learning-loop-session-completion.md) — How `/done` produces the data hub displays
- [/craft:hub Reference](../commands/hub.md) — Full command reference
- [Memory-Aware Routing](../cookbook/common/memory-aware-routing.md) — How `/do` uses the same data
