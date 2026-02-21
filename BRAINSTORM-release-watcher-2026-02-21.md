# BRAINSTORM: Release Watcher & Command Sync System

**Date:** 2026-02-21
**Depth:** max | **Focus:** feature + architecture
**Duration:** ~4 min (3 agents)

---

## Problem Statement

Claude Code and Claude Desktop evolve rapidly. Craft's 108 commands, 25 skills, and 8 agents need to stay aligned with:

- New plugin capabilities (hooks, agent features, environment variables)
- Deprecated features (models, APIs, CLI flags)
- New integration points (MCP, worktree isolation, desktop extensions)

Currently this is manual — someone reads changelogs and cross-references craft commands. This should be automated.

---

## Research Findings (3 Agents)

### Claude Code v2.1.50 — Plugin-Relevant Changes

| Change | Impact on Craft |
|--------|-----------------|
| `isolation: worktree` for agents | Craft agents could use isolated execution |
| `memory` frontmatter (user/project/local scope) | Agents can persist state across sessions |
| `background: true` agent config | Declare always-background agents |
| New hooks: `WorktreeCreate`, `WorktreeRemove`, `ConfigChange`, `TeammateIdle`, `TaskCompleted` | New hook triggers for craft hooks |
| `last_assistant_message` in hook inputs | Richer hook context |
| `settings.json` for plugins | Craft can ship default settings |
| Sonnet 4.5 (1M) deprecated → Sonnet 4.6 | Check for hardcoded model refs |
| `CLAUDE_CODE_SIMPLE` env var disables plugins | Document this limitation |

### Claude Desktop — New Capabilities

| Feature | Relevance |
|---------|-----------|
| Cowork (agentic runtime in VM) | Craft orchestration could integrate |
| Desktop Extensions (.mcpb) | New distribution channel for craft |
| Remote MCP servers | Team-shared craft instances |
| Built-in Node.js for MCP | No dependency issues |

### Craft Command Inventory — Current State

| Metric | Value |
|--------|-------|
| Total commands | 108 |
| Deprecated (need removal) | 4 (`docs/claude-md/{audit,fix,scaffold,update}`) |
| With mode support | 8 |
| With dry-run | 29 |
| Categories | 18 |
| External tool dependencies | 7 tools across 15 commands |

---

## Proposed Solution: 3 New Commands + 1 Skill

### 1. `/craft:code:release-watch` (Command)

**Purpose:** Fetch and analyze latest Claude Code releases for craft-relevant changes.

**What it does:**

1. Fetches latest releases from `gh api repos/anthropics/claude-code/releases`
2. Parses changelog for plugin-relevant keywords: `plugin`, `hook`, `agent`, `skill`, `command`, `frontmatter`, `schema`, `deprecated`, `breaking`
3. Cross-references against current craft implementation
4. Outputs actionable report: what to update, what's new, what's deprecated

**Output:**

```
╭─ Release Watch: Claude Code ──────────────────────────────╮
│ Latest: v2.1.50 (2026-02-20)                              │
│ Your craft: v2.24.0                                       │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ 🆕 NEW CAPABILITIES (not yet used by craft):              │
│   • Agent memory frontmatter (scope: user/project/local)  │
│   • isolation: worktree for agents                        │
│   • 5 new hook events available                           │
│                                                           │
│ ⚠️  DEPRECATIONS (check your code):                       │
│   • Sonnet 4.5 references → use Sonnet 4.6               │
│                                                           │
│ ✅ ALREADY ALIGNED:                                       │
│   • Plugin settings.json: supported                       │
│   • Background agents: supported                          │
│                                                           │
│ 📋 SUGGESTED ACTIONS:                                     │
│   1. Add memory to key agents (orchestrator-v2)           │
│   2. Add worktree isolation to safe agents                │
│   3. Register new hook events in hook configs             │
│                                                           │
╰───────────────────────────────────────────────────────────╯
```

### 2. `/craft:code:desktop-watch` (Command)

**Purpose:** Fetch and analyze latest Claude Desktop releases.

**Similar to release-watch but focused on:**

- MCP capabilities changes
- Desktop extension format changes
- New integration points
- Cowork runtime features

### 3. `/craft:code:command-audit` (Command)

**Purpose:** Audit all craft commands against current Claude Code capabilities.

**What it does:**

1. Reads all command frontmatter (108 files)
2. Validates against `_schema.json`
3. Checks for deprecated patterns (like the `trigger:` field we just found)
4. Checks for unknown frontmatter fields
5. Checks for hardcoded model names, deprecated features
6. Reports commands referencing removed/changed APIs
7. Suggests new capabilities not yet adopted

**Output:**

```
╭─ Command Audit ───────────────────────────────────────────╮
│ Scanned: 108 commands, 25 skills, 8 agents                │
├───────────────────────────────────────────────────────────┤
│                                                           │
│ 🔴 ERRORS (3):                                            │
│   • docs/lint.md: invalid frontmatter field 'trigger'     │
│   • orchestrate.md: invalid fields 'agent', 'triggers'    │
│   • brainstorm.md: 'args' should be 'arguments'           │
│                                                           │
│ 🟡 WARNINGS (4):                                          │
│   • 4 deprecated commands still present                   │
│   • docs/claude-md/{audit,fix,scaffold,update}            │
│                                                           │
│ 🟢 SUGGESTIONS (6):                                       │
│   • 0/8 agents use memory frontmatter (new feature)       │
│   • 0/8 agents use isolation: worktree (new feature)      │
│   • No settings.json shipped (new capability)             │
│   • 5 new hook events not registered                      │
│                                                           │
│ 📊 HEALTH: 95/100 (3 errors, 4 warnings)                  │
│                                                           │
╰───────────────────────────────────────────────────────────╯
```

### 4. `/craft:code:sync-features` (Skill — interactive)

**Purpose:** Interactive wizard to adopt new Claude Code features.

**What it does:**

1. Runs release-watch + command-audit internally
2. Presents actionable items via AskUserQuestion
3. For each suggestion, offers to generate the code/config
4. Creates worktree for implementation if changes are non-trivial

---

## Quick Wins (< 30 min each)

1. **`/craft:code:command-audit`** — We literally just did this manually (invalid frontmatter). Automate it.
   - Validate all frontmatter against `_schema.json`
   - Check for deprecated commands still present
   - Report health score

2. **Remove 4 deprecated commands** — `docs/claude-md/{audit,fix,scaffold,update}` are marked deprecated, remove them.

3. **Ship `settings.json`** — New plugin capability, move budget config there.

## Medium Effort (1-2 hours each)

4. **`/craft:code:release-watch`** — Fetch releases via `gh api`, parse for plugin keywords, cross-reference.

5. **Add `memory` to orchestrator-v2 agent** — New capability, persist orchestration state across sessions.

6. **Add `isolation: worktree` to safe agents** — code-reviewer, test-automator could benefit.

7. **Register new hook events** — `WorktreeCreate`, `ConfigChange` etc.

## Long-term (Future sessions)

8. **`/craft:code:desktop-watch`** — Desktop releases are harder to parse (no GitHub API).

9. **`/craft:code:sync-features`** — Interactive wizard, depends on release-watch + command-audit.

10. **MCP Desktop Extension (.mcpb)** — Package craft for one-click Claude Desktop install.

11. **Automated CI release checking** — GitHub Action that runs release-watch on schedule and opens issues.

---

## Architecture Decision: Where to Put the Logic

### Option A: Pure Shell Scripts (like `docs-lint.sh`)

- **Pro:** Fast, no dependencies, works offline
- **Con:** Parsing GitHub API JSON in bash is painful
- **Verdict:** Good for command-audit (local files only)

### Option B: Python Scripts (like `claude_md_sync.py`)

- **Pro:** JSON parsing, rich output, existing pattern in craft
- **Con:** Python dependency
- **Verdict:** Good for release-watch (API calls + parsing)

### Option C: Instruction-Driven Commands (no script)

- **Pro:** Claude does the work, flexible
- **Con:** Depends on Claude's ability to fetch + parse
- **Verdict:** Good for sync-features (interactive)

### Recommendation: Mix

| Command | Implementation |
|---------|---------------|
| `command-audit` | Shell script (local file validation) |
| `release-watch` | Python script (GitHub API + parsing) |
| `desktop-watch` | Instruction-driven (web search) |
| `sync-features` | Skill (interactive, uses other commands) |

---

## Recommended Path

→ **Start with `/craft:code:command-audit`** — highest value, lowest effort. We just manually found 3 frontmatter errors and a broken trigger. This command would have caught them all. Plus it validates the 4 deprecated commands are still lingering.

Then build `release-watch` to make the audit data-driven (comparing against actual releases rather than just schema validation).

---

## Related Commands

- `/craft:check` — Pre-flight validation (could integrate command-audit)
- `/craft:code:deps-check` — Dependency checking (similar pattern)
- `/craft:docs:claude-md:sync` — CLAUDE.md sync (similar audit pattern)
