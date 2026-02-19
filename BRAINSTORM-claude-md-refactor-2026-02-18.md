# CLAUDE.md & Memory System Refactor - Brainstorm

**Generated:** 2026-02-18
**Context:** Craft Plugin + Global Claude Code Config
**Mode:** max (deep + 2 agents) | Focus: feature | Action: save

---

## The Problem

Your Claude Code instruction system has grown organically across **6 file types** totaling ~819 lines (~8,300 tokens per session):

| Source | Lines | Purpose | Issue |
|--------|-------|---------|-------|
| Global `CLAUDE.md` | 205 | Behavioral rules + reference | ~50% is reference material (MCP servers, keybinds, plugins) |
| Craft `CLAUDE.md` | 161 | Project instructions | 5 stale counts, git workflow duplicated from global |
| `MEMORY.md` | 36 | Learnings | 4 entries are behavioral rules, not learnings |
| `claude-code-instruction-enforcement.md` | 189 | One-time reference | Loaded every session, ~0 ongoing value |
| `brainstorm-mode.md` (rule) | 167 | Brainstorm formatting | 50 lines of AppleScript workaround |
| `feature-branch-workflow.md` (rule) | 61 | PR behavior | Clean, well-scoped |

**Key findings from agent analysis:**

1. **Git workflow stated 3x** (global CLAUDE.md, craft CLAUDE.md, memory) -- same content, three maintenance points
2. **Memory contains behavioral rules** -- "create a spec = STOP" and "user overrides > plan approval" are imperatives, not learnings
3. **Craft CLAUDE.md has 5 stale counts** -- skills (22 vs 25), specs (26 vs 31), tests (1504 vs 1575), version history range
4. **189-line reference doc** loaded every session for near-zero ongoing value
5. **15 orphan memory files** from old worktrees -- user doesn't know if they're used (answer: they ARE loaded when you're in those worktree paths, but NOT when you're in the main repo)
6. **.STATUS is stale** (last updated 2026-02-16) and doesn't auto-update

---

## How Memory Actually Works (Your Q2 Answer)

Your auto-memory IS being used. Here's what happens:

| What | When | How |
|------|------|-----|
| `MEMORY.md` (first 200 lines) | **Every session start** | Injected into system prompt automatically |
| Topic files (e.g., `claude-code-instruction-enforcement.md`) | **On demand** | Claude reads them when `MEMORY.md` references them |
| Worktree memory files | **Only in that worktree** | Each worktree path maps to a separate memory dir |
| Writing | **Claude's judgment** | When it discovers patterns, solves tricky problems, or you say "remember X" |

**Your 15 worktree memory files** are only loaded when Claude Code is running inside those specific worktree directories. When you're in `~/projects/dev-tools/craft`, only the craft memory is loaded. The worktree memories are effectively dormant unless you revisit those worktrees.

---

## How Tasks API Works (Your .STATUS Question)

Claude Code now has a **persistent task system** (since v2.1.16):

| Feature | TodoWrite (Legacy) | Tasks API (Current) |
|---------|-------------------|---------------------|
| Storage | Context window (RAM) | Disk (`~/.claude/tasks/`) |
| Survives session restart | No | Yes |
| Dependencies | None | `blockedBy` / `blocks` chains |
| Cross-terminal | No | Yes (shared via `CLAUDE_CODE_TASK_LIST_ID`) |

You have **138 task list directories** in `~/.claude/tasks/`. The Tasks API could replace your `.STATUS` file for planning and tracking, or complement it.

**Suggestion:** Use `.STATUS` as a living dashboard (auto-updated) with branch status, version, and next action. Use Tasks API for granular planning within sessions. Use ORCHESTRATE files for cross-session implementation plans.

---

## Options

### Option A: Layered CLAUDE.md (Your Preference)

Split both global and project CLAUDE.md into **core instructions** (always loaded) + **reference files** (read on demand).

**Global:**

```
~/.claude/
├── CLAUDE.md              # ~80 lines: behavioral rules ONLY
├── reference/
│   ├── mcp-servers.md     # MCP server table
│   ├── plugins.md         # Plugin list
│   ├── shell-aliases.md   # Workflow/teaching/research commands
│   ├── email-keybinds.md  # Himalaya + Neovim integration
│   └── release-automation.md  # Homebrew/PyPI pipelines
├── rules/
│   ├── brainstorm-mode.md # (keep, but trim AppleScript to 10 lines)
│   ├── feature-branch-workflow.md  # (keep as-is)
│   └── spec-only-mode.md  # NEW: promoted from memory
└── projects/*/memory/     # (keep, but prune)
```

**Craft project:**

```
craft/
├── CLAUDE.md              # ~80 lines: workflow + key commands + troubleshooting
├── .claude/
│   └── reference/
│       ├── agents.md      # Agent table (auto-generated)
│       ├── test-suite.md  # Test commands + file list (auto-generated)
│       └── project-structure.md  # Tree + key files (auto-generated)
└── .STATUS                # Living dashboard (auto-updated)
```

**Effort:** Medium (1-2 sessions)
**Pros:** Cuts context budget by ~50%, eliminates duplication, auto-generated sections stay fresh
**Cons:** More files to maintain, need to update `/craft:docs:claude-md:sync` to understand the new structure

### Option B: Smart Sync Only (Minimal Change)

Keep current structure but make `/craft:docs:claude-md:sync` smarter:

- Auto-update counts from filesystem
- Detect and warn about duplicates across files
- Trim stale version history
- Run as part of `/workflow:done`

**Effort:** Quick (< 1 session)
**Pros:** No structural change, immediate wins
**Cons:** Doesn't fix the root cause (reference material in CLAUDE.md)

### Option C: Per-Project Rules (Your Preference)

Move behavioral rules into project-scoped config files instead of global rules/:

```
craft/.claude/rules/
├── git-workflow.md        # Branch protection, worktree rules
├── spec-only-mode.md     # "Create spec = STOP"
└── brainstorm-format.md  # ADHD-friendly output rules
```

**Effort:** Quick
**Pros:** Rules travel with the project, different projects get different rules
**Cons:** Claude Code's `.claude/` in project root is gitignored by default; rules wouldn't be shared across team

### Option D: Combined (A + C + Workflow Integration)

The full package:

1. Layer CLAUDE.md (Option A)
2. Per-project rules (Option C)
3. `/workflow:done` triggers sync + staleness check
4. `.STATUS` becomes auto-updated living dashboard
5. Tasks API integration for session planning

**Effort:** Large (2-3 sessions)
**Pros:** Comprehensive, eliminates all pain points
**Cons:** Most work, most risk of breaking existing workflows

---

## Quick Wins (< 30 min each)

1. **Fix 5 stale counts in craft CLAUDE.md** -- skills 22->25, specs 26->31, tests 1504->1575, version history range, recent versions list
2. **Archive `claude-code-instruction-enforcement.md`** -- move out of memory/ to `docs/reference/` (saves ~2000 tokens/session)
3. **Promote 2 memory rules to `~/.claude/rules/spec-only-mode.md`** -- "create spec = STOP" and "user overrides > plan approval"
4. **Remove `--delete-branch` duplication** -- keep in global CLAUDE.md only, remove from MEMORY.md
5. **Update .STATUS** -- refresh branch status, update last_session, add today's brainstorm work

## Medium Effort (1-2 hours)

- [ ] Split global CLAUDE.md reference material into `~/.claude/reference/` files
- [ ] Add sync trigger to `/workflow:done` (or `/craft:check`)
- [ ] Auto-generate project structure section in craft CLAUDE.md
- [ ] Trim brainstorm-mode.md AppleScript section (50 -> 10 lines)
- [ ] Prune 15 orphan worktree memory files

## Long-term (Future sessions)

- [ ] Per-project rules directory support
- [ ] Tasks API integration for session planning
- [ ] Auto-dashboard .STATUS (branch status, test counts, version from source of truth)
- [ ] `/craft:docs:claude-md:layer` command -- generates layered CLAUDE.md from project state
- [ ] Config dashboard prototype showing all instruction sources

---

## Recommended Path

Start with **Quick Wins** (fix the 5 counts + archive the 189-line reference doc). That alone saves ~2000 tokens/session and fixes data accuracy.

Then do **Option D** as a proper feature branch -- it's the full solution that addresses scattering (your main pain point), integrates with `/workflow:done` (your trigger preference), and moves toward per-project rules (your architecture preference).

---

## Next Steps

1. [ ] Fix quick wins now (no worktree needed, these are doc changes on dev)
2. [ ] Create spec from this brainstorm (save action)
3. [ ] Create worktree for Option D implementation
4. [ ] Start with global CLAUDE.md layering
