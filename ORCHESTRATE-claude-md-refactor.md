# CLAUDE.md & Memory System Refactor - Orchestration Plan

> **Branch:** `feature/claude-md-refactor`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-claude-md-refactor`
> **Spec:** `docs/specs/SPEC-claude-md-refactor-2026-02-18.md`

## Objective

Restructure the Claude Code instruction hierarchy from a flat, scattered
819-line system (~8300 tokens/session) into a layered architecture (~4000
tokens/session). Lean behavioral CLAUDE.md files + reference files loaded on
demand + per-project rules + auto-updated .STATUS dashboard.

## Phase Overview

| Phase | Task | Priority | Status |
| ----- | ---- | -------- | ------ |
| 1 | Quick Wins (stale counts, archive, promote rules) | HIGH | Pending |
| 2 | Global CLAUDE.md Layering | HIGH | Pending |
| 3 | Craft CLAUDE.md Layering | HIGH | Pending |
| 4 | Workflow Integration (/workflow:done + /craft:check) | MEDIUM | Pending |
| 5 | Per-Project Rules | LOW | Pending |

---

## Phase 1: Quick Wins (< 30 min)

> **Goal:** Fix immediate data accuracy issues and reduce token waste.
> **Why first:** Zero risk, immediate ROI. Saves ~2000 tokens/session just
> by archiving one file.

### Tasks

- [ ] **1.1 Fix 5 stale counts in craft CLAUDE.md**
  - Skills: 22 -> actual count (run `find commands/ -name "*.md" | wc -l`)
  - Specs: 26 -> actual count (run `find docs/specs -name "SPEC-*.md" | wc -l`)
  - Tests: ~1504 -> actual count (run test suite, capture pass count)
  - Version history range needs updating
  - Recent versions list needs updating
  <!-- COMMENT: These counts drift every few sessions. After this fix,
       Phase 4 will add auto-sync so they never go stale again. -->

- [ ] **1.2 Archive `claude-code-instruction-enforcement.md`**
  - Move from `~/.claude/projects/-Users-dt-projects-dev-tools-craft/memory/`
    to `docs/reference/claude-code-instruction-enforcement.md`
  - Remove the reference link from MEMORY.md
  - This 189-line file loads on-demand every session for near-zero value
  <!-- COMMENT: This was a one-time research document about how hooks,
       rules, and memory work. The knowledge is now internalized in the
       spec and brainstorm files. Archive, don't delete — it's good
       reference material if someone needs to understand the system. -->

- [ ] **1.3 Promote memory behavioral rules to `~/.claude/rules/spec-only-mode.md`**
  - Extract from MEMORY.md "User Workflow Rules" section:
    - "Create a spec file means SPEC ONLY, STOP"
    - "Always ask before editing code on any branch"
    - "Never write feature code on dev"
    - "User overrides beat plan-mode approval"
  - Create new rule file at `~/.claude/rules/spec-only-mode.md`
  - Remove the promoted rules from MEMORY.md (keep reference to new location)
  <!-- COMMENT: These are imperatives, not learnings. Rules files are the
       right home — they load every session and are explicitly labeled as
       behavioral constraints. Memory should be for patterns and insights. -->

- [ ] **1.4 Remove `--delete-branch` duplication from MEMORY.md**
  - This rule already exists in global CLAUDE.md (Pre-PR checklist)
  - Keep the audit note (2026-02-13) as a memory entry — it's a genuine learning
  - Remove the duplicated rule text
  <!-- COMMENT: The rule itself belongs in CLAUDE.md. The audit finding
       ("checked all plugins, no --delete-branch in automated paths")
       is a genuine learning worth keeping in memory. -->

- [ ] **1.5 Update .STATUS with current session info**
  - Refresh branch status, version, last_session date
  - Add this brainstorm/refactor work to recent activity
  <!-- COMMENT: Quick win, sets the stage for Phase 4 auto-updating. -->

### Phase 1 Acceptance Criteria

- [ ] All counts in craft CLAUDE.md match filesystem
- [ ] `claude-code-instruction-enforcement.md` no longer in memory/
- [ ] MEMORY.md contains only learnings, not behavioral rules
- [ ] No duplicated content between MEMORY.md and CLAUDE.md
- [ ] .STATUS reflects current session

---

## Phase 2: Global CLAUDE.md Layering

> **Goal:** Extract ~120 lines of reference material from global CLAUDE.md,
> leaving ~80 lines of behavioral rules only.
> **Why:** Reference material (MCP server tables, plugin lists, keybinds)
> consumes context budget every session but is rarely needed.

### Tasks

- [ ] **2.1 Create `~/.claude/reference/` directory**
  <!-- COMMENT: This is the new home for on-demand reference material.
       Claude reads these files only when the user asks about MCP servers,
       plugins, keybinds, etc. Not loaded into system prompt. -->

- [ ] **2.2 Extract MCP server table to `~/.claude/reference/mcp-servers.md`**
  - Source: global CLAUDE.md lines ~75-89 (MCP Servers section)
  - Include the full server table with runtime, purpose columns
  <!-- COMMENT: 8 servers × 3 columns = ~15 lines. Rarely referenced
       during normal coding sessions. Perfect candidate for on-demand. -->

- [ ] **2.3 Extract plugin list to `~/.claude/reference/plugins.md`**
  - Source: global CLAUDE.md lines ~93-97 (Local Plugins section)
  - Include Homebrew, Symlinked, and Marketplace categories
  <!-- COMMENT: The plugin list changes rarely (only on install/uninstall).
       No need to load it every session. -->

- [ ] **2.4 Extract shell workflow to `~/.claude/reference/shell-workflow.md`**
  - Source: global CLAUDE.md lines ~60-71 (ADHD commands, teaching, research)
  - Include core commands, teaching commands, research commands
  <!-- COMMENT: These are reference lookups — "what's the command for X?"
       Not behavioral rules that Claude needs to follow. -->

- [ ] **2.5 Extract email/neovim to `~/.claude/reference/email-neovim.md`**
  - Source: global CLAUDE.md lines ~126-144 (Himalaya + keybinds)
  - Include the keybind table and backend info
  <!-- COMMENT: Email integration is used ~1 in 10 sessions. No reason
       to load 20 lines of keybind tables every time. -->

- [ ] **2.6 Extract release automation to `~/.claude/reference/release-automation.md`**
  - Source: global CLAUDE.md lines ~108-115 (Homebrew/PyPI pipelines)
  - Include tap info, formula list, PyPI publishing details
  <!-- COMMENT: Release automation is used ~1 in 20 sessions. -->

- [ ] **2.7 Rewrite global CLAUDE.md as behavioral rules only (~80 lines)**
  - Keep: Git workflow, safety rules, commit standards, branch guard rules
  - Keep: Edit safety rules, debugging rules, shell escaping notes
  - Add: "For reference material, see `~/.claude/reference/`" pointer
  - Remove: All extracted reference sections
  <!-- COMMENT: The rewritten CLAUDE.md should answer "how should Claude
       behave?" not "what tools does the user have?" Behavioral rules
       are the ones Claude needs every session. -->

- [ ] **2.8 Trim brainstorm-mode.md AppleScript section (50 -> 10 lines)**
  - Keep: The AppleScript examples for iA Writer + explanation of why
  - Remove: Redundant examples for TextEdit, VS Code, Finder, Obsidian
  - Remove: The "Why This Works" explanation (already understood)
  <!-- COMMENT: The AppleScript workaround is important (open command
       doesn't work from Claude Code), but 50 lines of examples is
       excessive. Keep iA Writer (primary use) and a generic pattern. -->

- [ ] **2.9 Verify no behavioral rules lost in extraction**
  - Diff old vs new global CLAUDE.md
  - Check each extracted line: is it a rule or reference?
  - Run a session with new CLAUDE.md, verify no missing guidance
  <!-- COMMENT: This is the critical safety check. If we accidentally
       extract a behavioral rule into reference/, Claude won't follow
       it unless explicitly asked to read the file. -->

### Phase 2 Acceptance Criteria

- [ ] Global CLAUDE.md < 100 lines
- [ ] 5 reference files created in `~/.claude/reference/`
- [ ] brainstorm-mode.md < 130 lines (from 167)
- [ ] No behavioral rules moved to reference/ (only reference material)
- [ ] "See reference/" pointer in CLAUDE.md

---

## Phase 3: Craft CLAUDE.md Layering

> **Goal:** Extract project-specific reference material from craft CLAUDE.md,
> leaving ~80 lines of workflow + commands + troubleshooting.
> **Why:** Agent tables, test file lists, and project structure trees are
> reference material that Claude can look up on demand.

### Tasks

- [ ] **3.1 Create `.claude/reference/` directory in craft project**
  <!-- COMMENT: Project-level reference files, auto-generated from
       filesystem state. These complement the global reference/. -->

- [ ] **3.2 Extract agent table to `.claude/reference/agents.md`**
  - Source: craft CLAUDE.md "Agents" section
  - Include agent name, model, use-for description
  - Auto-generate from `agents/` directory listing
  <!-- COMMENT: Agent table changes only when agents are added/removed.
       Auto-generation means it stays accurate without manual maintenance. -->

- [ ] **3.3 Extract test suite to `.claude/reference/test-suite.md`**
  - Source: craft CLAUDE.md "Test Suite" section
  - Include test commands, key test files, pass counts
  - Auto-generate counts from test runner output
  <!-- COMMENT: Test counts are the #1 source of staleness. Auto-generating
       from the actual test runner eliminates this problem entirely. -->

- [ ] **3.4 Extract project structure to `.claude/reference/project-structure.md`**
  - Source: craft CLAUDE.md "Project Structure" and "Key Files" sections
  - Include directory tree, key files table, version history
  - Auto-generate tree from filesystem
  <!-- COMMENT: The project structure section is pure reference. Claude
       can explore the filesystem directly when needed. -->

- [ ] **3.5 Enhance `claude_md_sync.py` to populate reference files**
  - Add reference file generation to the sync pipeline
  - Generate agents.md from `agents/` directory
  - Generate test-suite.md from test runner output
  - Generate project-structure.md from filesystem
  <!-- COMMENT: This is the key automation piece. The sync utility
       already knows how to count commands, skills, etc. Extending it
       to generate reference files is a natural evolution. -->

- [ ] **3.6 Rewrite craft CLAUDE.md (~80 lines)**
  - Keep: Active Work, Git Workflow, Quick Commands, Execution Modes
  - Keep: Troubleshooting section
  - Add: "For details, see `.claude/reference/`" pointer
  - Remove: Agents, Test Suite, Project Structure, Key Files, Version History
  <!-- COMMENT: The rewritten craft CLAUDE.md should answer "how do I
       work in this project?" — workflow, commands, modes, troubleshooting.
       Not "what files exist?" or "what agents are available?" -->

### Phase 3 Acceptance Criteria

- [ ] Craft CLAUDE.md < 100 lines
- [ ] 3 reference files in `.claude/reference/`
- [ ] `claude_md_sync.py` generates reference files
- [ ] Reference files match current filesystem state
- [ ] "See .claude/reference/" pointer in CLAUDE.md

---

## Phase 4: Workflow Integration

> **Goal:** Wire CLAUDE.md maintenance into existing triggers so the system
> stays accurate automatically.
> **Why:** Manual sync is the reason counts go stale. Automating via
> `/workflow:done` means every session ends with fresh data.

### Tasks

- [ ] **4.1 Add CLAUDE.md staleness check to `/workflow:done`**
  - After existing done steps, run `claude_md_sync.py`
  - Report any stale counts or outdated sections
  - Auto-fix counts (update in-place)
  <!-- COMMENT: /workflow:done is already the "end of session" trigger.
       Adding a staleness check here means every productive session
       ends with accurate instruction files. -->

- [ ] **4.2 Add .STATUS auto-refresh to `/workflow:done`**
  - Update branch status from `git branch --show-current`
  - Update version from source of truth (package.json, etc.)
  - Update last_session timestamp
  - Update next_action from context
  <!-- COMMENT: .STATUS becomes a living dashboard that's always current.
       No more manually editing it at the start of each session. -->

- [ ] **4.3 Add instruction health check to `/craft:check`**
  - Check CLAUDE.md line counts (global < 100, project < 100)
  - Verify count accuracy (commands, skills, agents, specs, tests)
  - Flag memories older than 30 days with no updates
  - Detect contradictions between global + project + memory
  <!-- COMMENT: /craft:check is the pre-flight validation command.
       Adding instruction health means you catch stale data before
       commits, not after. -->

- [ ] **4.4 Add staleness report UI**
  - Show health check results in the format from spec UI/UX section
  - Color-coded: green (ok), yellow (warning), red (error)
  - Actionable: suggest fixes for each issue found
  <!-- COMMENT: The report should be ADHD-friendly — scannable at a
       glance with clear action items. No walls of text. -->

### Phase 4 Acceptance Criteria

- [ ] `/workflow:done` runs CLAUDE.md sync automatically
- [ ] `/workflow:done` updates .STATUS automatically
- [ ] `/craft:check` validates instruction health
- [ ] Staleness report shows green/yellow/red status
- [ ] No manual intervention needed to keep counts accurate

---

## Phase 5: Per-Project Rules (LOW Priority)

> **Goal:** Support project-scoped rules that load alongside global rules.
> **Why:** Different projects need different rules. Brainstorm formatting
> shouldn't load for R packages; spec-only rules should apply everywhere.

### Tasks

- [ ] **5.1 Support `.claude/rules/` in project directories**
  - Claude Code already supports this natively (gitignored by default)
  - Document the loading order: global rules + project rules
  <!-- COMMENT: This may already work out of the box with Claude Code's
       native .claude/rules/ support. Main task is documenting and
       testing, not implementing. -->

- [ ] **5.2 Move project-specific rules from global to project scope**
  - Identify which global rules are project-specific
  - Move them to appropriate `.claude/rules/` directories
  <!-- COMMENT: The brainstorm identified that brainstorm-mode.md
       shouldn't load for R packages. Per-project rules solve this. -->

- [ ] **5.3 Document rule loading order**
  - Global `~/.claude/rules/` + project `.claude/rules/`
  - Precedence: project rules override global rules?
  - Test with conflicting rules to verify behavior
  <!-- COMMENT: Need to verify Claude Code's actual behavior when
       the same topic is covered by both global and project rules. -->

- [ ] **5.4 Create rule templates for common project types**
  - R packages: no brainstorm formatting, CRAN compliance
  - Node.js: npm conventions, ESLint preferences
  - Python: PEP 8, pytest conventions
  <!-- COMMENT: Optional nice-to-have. Templates make it easy to
       bootstrap rules for new projects. -->

### Phase 5 Acceptance Criteria

- [ ] `.claude/rules/` works in project directories
- [ ] Rules load alongside global rules (not replacing)
- [ ] Loading order documented
- [ ] At least one project has project-specific rules

---

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-claude-md-refactor
claude
```

Start with Phase 1 (Quick Wins) — all tasks are low-risk and provide
immediate value. Each phase can be committed independently.

## Notes

- **Do not implement.** This ORCHESTRATE file is the plan. Implementation
  happens when the user says "start Phase 1" or similar.
- Phases 1-3 are the core value (HIGH priority). Phase 4 is the automation
  layer (MEDIUM). Phase 5 is optional future work (LOW).
- Each phase should be committed as a logical unit with its own PR or
  commit set.
- The spec (`docs/specs/SPEC-claude-md-refactor-2026-02-18.md`) is the
  source of truth for acceptance criteria and architecture decisions.
