# ORCHESTRATE: Release Watcher & Command Sync System

> **Branch:** `feature/release-watcher`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-release-watcher`
> **Spec:** `docs/specs/SPEC-release-watcher-2026-02-21.md`
> **Brainstorm:** `BRAINSTORM-release-watcher-2026-02-21.md`

## Objective

Build 4 new commands that automate tracking Claude Code/Desktop releases, auditing craft commands for compliance, and interactively adopting new capabilities. Also remove 4 deprecated commands and create documentation.

## Phase Overview

| Phase | Task | Priority | Effort | Status |
|-------|------|----------|--------|--------|
| 1 | `/craft:code:command-audit` (shell script) | High | 2-3h | Pending |
| 2 | Remove deprecated commands + cleanup | High | 30min | Pending |
| 3 | `/craft:code:release-watch` (Python script) | Medium | 3-4h | Pending |
| 4 | `/craft:code:desktop-watch` (instruction-driven) | Medium | 1h | Pending |
| 5 | `/craft:code:sync-features` (skill) | Low | 2h | Pending |
| 6 | Documentation (docs site pages) | Medium | 1-2h | Pending |
| 7 | Tests + CI integration | Medium | 1-2h | Pending |

---

## Phase 1: `/craft:code:command-audit` (Shell Script)

**Deliverables:**

- `scripts/command-audit.sh` — shell script
- `commands/code/command-audit.md` — command file

**Implementation:**

### 1.1 Create `scripts/command-audit.sh`

The script validates all command/skill/agent frontmatter against the schema.

**Checks to implement:**

| # | Check | Severity | Logic |
|---|-------|----------|-------|
| 1 | Invalid frontmatter fields | ERROR | Parse YAML, compare keys against `_schema.json` valid fields list |
| 2 | Missing `description` field | ERROR | Required per schema |
| 3 | Deprecated commands still present | WARNING | Scan for `DEPRECATED` in file content |
| 4 | Hardcoded model names | WARNING | Grep for `sonnet 4.5`, `opus 4.0`, etc. |
| 5 | YAML parse errors | ERROR | Validate frontmatter YAML syntax |
| 6 | Orphaned scripts | WARNING | Scripts in `scripts/` not referenced by any command |
| 7 | External tool availability | INFO | Check `command -v` for ruff, mkdocs, etc. |
| 8 | Schema compliance | ERROR | Required fields per schema: `description` is the only hard requirement |

**Valid frontmatter fields** (from `_schema.json`):

```
name, category, subcategory, description, file, modes, arguments,
tutorial, tutorial_level, tutorial_file, related_commands, tags,
project_types, common_workflows, time_budgets, examples
```

**Arguments:**

- `--format terminal|json|markdown` (default: terminal)
- `--fix` — auto-fix safe issues (remove invalid fields, rename `args` → `arguments`)
- `--strict` — treat warnings as errors (for CI)

**Exit codes:** 0 = pass, 1 = warnings only, 2 = errors found

**Output format:** Use craft standard box format (see `/craft:check` for reference).

**Health score calculation:**

```
score = 100
score -= (errors * 5)
score -= (warnings * 2)
score -= (suggestions * 0)  # suggestions don't reduce score
score = max(0, score)
```

### 1.2 Create `commands/code/command-audit.md`

Standard command file with frontmatter:

```yaml
---
description: Validate command frontmatter, find deprecated patterns, report health score
category: code
arguments:
  - name: format
    description: "Output format: terminal, json, markdown"
    required: false
    default: terminal
  - name: fix
    description: Auto-fix safe issues
    required: false
    default: false
    alias: --fix
  - name: strict
    description: Treat warnings as errors (for CI)
    required: false
    default: false
    alias: --strict
---
```

Body should document: what it checks, output format, CI usage, examples.

### 1.3 Test Phase 1

- Run against current codebase — should report 0 errors (we already fixed them)
- Introduce a test violation, verify it catches it
- Test `--fix` mode
- Test `--format json` output

**Commit:** `feat: add /craft:code:command-audit for frontmatter validation`

---

## Phase 2: Remove Deprecated Commands

**Deliverables:**

- Delete 4 deprecated command files
- Update hub.md references
- Update any cross-references

### 2.1 Delete files

```
commands/docs/claude-md/audit.md   → DEPRECATED, use sync
commands/docs/claude-md/fix.md     → DEPRECATED, use sync --fix
commands/docs/claude-md/scaffold.md → DEPRECATED, use init
commands/docs/claude-md/update.md  → DEPRECATED, use sync
```

### 2.2 Update references

- `commands/hub.md` — remove deprecated entries from command tables
- `CLAUDE.md` — update command count (108 → 104)
- `docs/` site pages — remove references to deprecated commands
- Run `./scripts/validate-counts.sh` to verify

### 2.3 Test Phase 2

- Run `command-audit` — should show 0 deprecation warnings
- Run `validate-counts.sh` — counts should match
- Run broken links test

**Commit:** `chore: remove 4 deprecated claude-md commands`

---

## Phase 3: `/craft:code:release-watch` (Python Script)

**Deliverables:**

- `scripts/release-watch.py` — Python script
- `commands/code/release-watch.md` — command file

### 3.1 Create `scripts/release-watch.py`

**Logic:**

1. Run `gh api repos/anthropics/claude-code/releases --paginate` via subprocess
2. Parse JSON response, take latest N releases
3. For each release body, search for plugin keywords:
   - Plugin system: `plugin`, `skill`, `command`, `agent`, `hook`, `frontmatter`
   - Schema: `schema`, `field`, `property`, `validation`
   - Deprecation: `deprecated`, `removed`, `breaking`, `migration`
   - New features: `new`, `added`, `support`, `feature`, `capability`
   - Models: `sonnet`, `opus`, `haiku`, `model`
   - Environment: `environment`, `variable`, `CLAUDE_`
4. Categorize findings: NEW / DEPRECATED / BREAKING / FIXED
5. Cross-reference against craft state:
   - Read `agents/*.md` for `memory`, `isolation`, `background` fields
   - Check registered hook events
   - Grep for hardcoded model names
6. Output delta report

**Arguments:**

- `--count N` — number of releases (default: 3)
- `--since vX.Y.Z` — only show releases after version
- `--format terminal|json|markdown` (default: terminal)

**Requires:** `gh` CLI authenticated. Check with `gh auth status`.

### 3.2 Create `commands/code/release-watch.md`

Document: purpose, requirements (`gh` CLI), output format, examples, CI usage.

### 3.3 Test Phase 3

- Run against real GitHub API
- Verify keyword detection catches known changes
- Test `--format json` for CI consumption
- Test `--since` filtering

**Commit:** `feat: add /craft:code:release-watch for tracking Claude Code changes`

---

## Phase 4: `/craft:code:desktop-watch` (Instruction-Driven)

**Deliverables:**

- `commands/code/desktop-watch.md` — command file (no script needed)

### 4.1 Create command file

This is an instruction-driven command. The command body tells Claude to:

1. WebSearch for "Claude Desktop release notes 2026"
2. WebFetch the Anthropic support page
3. Parse for developer-relevant features (MCP, extensions, file system)
4. Compare against craft's distribution channels
5. Output report with integration opportunities

**Arguments:**

- `--format terminal|markdown` (default: terminal)

No script needed — Claude handles the web research.

### 4.2 Test Phase 4

- Invoke the command, verify it produces useful output
- Check that output format is consistent with other commands

**Commit:** `feat: add /craft:code:desktop-watch for tracking Claude Desktop changes`

---

## Phase 5: `/craft:code:sync-features` (Skill)

**Deliverables:**

- `skills/code/sync-features.md` — skill file

### 5.1 Create skill file

The skill:

1. Runs `command-audit` internally
2. Runs `release-watch` internally
3. Optionally runs `desktop-watch`
4. Merges findings into prioritized action list
5. Presents via AskUserQuestion (multiSelect)
6. For selected items, generates implementation code or creates worktree

### 5.2 Test Phase 5

- Run the skill end-to-end
- Verify it correctly chains the other commands
- Test that AskUserQuestion options make sense

**Commit:** `feat: add /craft:code:sync-features interactive wizard`

---

## Phase 6: Documentation

**Deliverables:**

- Docs site pages for each new command
- Updated hub.md
- Updated CLAUDE.md counts

### 6.1 Create docs pages

For each new command, create a docs page at `docs/commands/code/`:

- `command-audit.md` — usage, checks, CI integration
- `release-watch.md` — usage, requirements, output examples
- `desktop-watch.md` — usage, output examples
- `sync-features.md` — usage, workflow, examples

### 6.2 Update navigation

- `mkdocs.yml` — add new pages to nav
- `commands/hub.md` — add entries to CODE category table
- `CLAUDE.md` — update counts (commands: 108 → 108 net: +4 new, -4 deprecated)

### 6.3 Run docs checks

```bash
/craft:docs:lint
/craft:docs:check-links
mkdocs build
```

**Commit:** `docs: add documentation for release watcher commands`

---

## Phase 7: Tests + CI

**Deliverables:**

- Unit tests for `command-audit.sh`
- Integration test for `release-watch.py`
- CI workflow addition

### 7.1 Unit tests for command-audit

Add to `tests/test_craft_plugin.py` or create `tests/test_command_audit.py`:

- Test: valid commands pass
- Test: invalid frontmatter field detected
- Test: deprecated command detected
- Test: missing description detected
- Test: `--fix` mode works
- Test: `--format json` output valid JSON
- Test: health score calculation

### 7.2 Integration test for release-watch

Add to `tests/test_plugin_e2e.py`:

- Test: script runs without error (requires `gh`)
- Test: `--format json` produces valid JSON
- Test: `--count 1` limits output

### 7.3 CI integration

Add `command-audit --strict --format json` to `.github/workflows/ci.yml`:

- Run on PRs that touch `commands/`, `skills/`, `agents/`
- Fail PR if errors found

**Commit:** `test: add tests for release watcher commands`

---

## Acceptance Criteria

From spec — all must pass before PR:

- [ ] `command-audit` validates all frontmatter against `_schema.json` and reports errors
- [ ] `command-audit` detects deprecated commands still present
- [ ] `command-audit` reports a health score (0-100)
- [ ] `release-watch` fetches latest Claude Code releases via GitHub API
- [ ] `release-watch` identifies plugin-relevant changes
- [ ] `release-watch` cross-references findings against current craft state
- [ ] `desktop-watch` reports latest Claude Desktop features relevant to plugins
- [ ] `sync-features` presents actionable items interactively
- [ ] 4 deprecated claude-md commands removed
- [ ] Documentation pages created for all new commands
- [ ] Tests pass, CI integration works
- [ ] `validate-counts.sh` passes with updated counts

## How to Start

```bash
cd ~/.git-worktrees/craft/feature-release-watcher
claude
# Then: "Implement Phase 1 from the ORCHESTRATE plan"
```
