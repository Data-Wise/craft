# ORCHESTRATE: Test Generation & Execution Refactor

**Branch:** `feature/test-gen-refactor`
**Spec:** `docs/specs/SPEC-test-gen-refactor-2026-02-18.md`
**Worktree:** `~/.git-worktrees/craft/feature-test-gen-refactor`

---

## What This Refactor Does

Craft currently has **7 overlapping test commands** (`test:cli-gen`, `test:cli-run`, `test:coverage`, `test:debug`, `test:watch`, `test:generate`, `test:run`) that grew organically. Each handles a slice of testing but with inconsistent patterns, no project-type awareness, and duplicated utilities across 63 test files.

This refactor consolidates everything into **3 commands**:

| New Command | Replaces | Purpose |
|-------------|----------|---------|
| `/craft:test` | `test:run`, `test:coverage`, `test:debug`, `test:watch` | Unified runner with category filtering + modes |
| `/craft:test:gen` | `test:cli-gen`, `test:generate` | Auto-detect project type, generate full test suite |
| `/craft:test:template` | *(new)* | Manage Jinja2 templates that power test generation |

### Why It Matters

- **One command to remember** instead of 7
- **Project-type awareness** — plugin, ZSH, CLI, MCP each get tailored tests
- **Tiered execution** — smoke (2 min) through e2e (30 min) with pytest markers
- **Template-driven** — Jinja2 templates make test generation maintainable and extensible
- **Shared helpers** — `tests/helpers.py` eliminates duplicated utilities

---

## Implementation Increments

### Increment 1: Foundation (Phase 1)

**Goal:** Modernize existing test infrastructure without changing commands yet

- [ ] Add `[tool.pytest.ini_options]` to `pyproject.toml` with all marker definitions
- [ ] Create `tests/helpers.py` — extract shared utilities from existing test files
- [ ] Enrich `tests/conftest.py` with reusable fixtures (`craft_root`, `temp_plugin_dir`, `temp_git_repo`)
- [ ] Add `@pytest.mark.*` markers to all 63 existing test files
- [ ] Migrate 10 CheckResult-pattern files to native pytest assertions

**Tests:** Run existing suite — all ~1575 tests must still pass after marker migration
**Commit pattern:** One commit per sub-task (markers, helpers, conftest, migrations)

### Increment 2: Command Consolidation (Phase 2)

**Goal:** Create the 3 new commands, wire up template infrastructure

- [ ] Create `commands/test.md` — unified runner (replaces run/coverage/debug/watch)
- [ ] Create `commands/test/gen.md` — unified generator (replaces cli-gen/generate)
- [ ] Create `commands/test/template.md` — template lifecycle manager (7 actions)
- [ ] Create `templates/` directory structure:

  ```
  templates/
  ├── _base/           # Shared partials (conftest, helpers, bash boilerplate)
  ├── plugin/          # Claude Code plugin templates (7 files)
  ├── zsh/             # ZSH plugin templates (5 files)
  ├── cli/             # Python/Node CLI templates (7 files)
  ├── mcp/             # MCP server templates (5 files)
  └── registry.json    # Type metadata, detection rules, required variables
  ```

- [ ] Create `templates/registry.json` with schema for all 4 project types
- [ ] Remove deprecated commands: `test:cli-gen`, `test:cli-run`, `test:coverage`, `test:debug`, `test:watch`
- [ ] Update `test-generator` skill to delegate to `test:gen`
- [ ] Update `validate-counts.sh` and CLAUDE.md for new command count

**Tests:** New commands validate, old commands removed, count validation passes

### Increment 3: Documentation (Phase 2.5)

**Goal:** Ship docs alongside the commands — not after

- [ ] `docs/guide/test-commands.md` — full argument/flag reference
- [ ] `docs/tutorials/testing-quickstart.md` — step-by-step getting started
- [ ] `docs/guide/test-architecture.md` — template system, detection, tiers, CI
- [ ] `docs/guide/test-migration.md` — old commands → new commands migration
- [ ] Update CLAUDE.md Quick Commands table
- [ ] Update mkdocs.yml nav

**Tests:** `test_craft_plugin.py -k broken_links` passes

### Increment 4: Project Type Templates (Phase 3)

**Goal:** Write the actual Jinja2 templates for all 4 project types

- [ ] `templates/plugin/` — Claude Code plugin (most complex: lifecycle e2e, dogfood)
- [ ] `templates/zsh/` — ZSH plugin (sourcing, functions, completions, ShellSpec e2e)
- [ ] `templates/cli/` — Python/Node CLI (enhanced from current, snapshot tests)
- [ ] `templates/mcp/` — MCP server (protocol compliance, tool execution)
- [ ] `templates/_base/` — Shared partials (conftest, helpers, bash boilerplate)
- [ ] Validate all templates: Jinja2 syntax, required vars, rendered output parseable
- [ ] Dogfood: run `/craft:test:gen` against craft itself, verify output

**Tests:** `/craft:test:template validate` passes, generated tests run successfully

### Increment 5: Advanced Features (Phase 4 — future)

**Goal:** Optional enhancements, not blocking release

- [ ] Snapshot testing with syrupy
- [ ] Property-based testing with Hypothesis
- [ ] Contract tests for plugin.json strict schema
- [ ] CI workflow YAML generation

---

## Dependencies

| Dependency | When Needed | Install |
|------------|-------------|---------|
| `jinja2` | Increment 2 | `pip install jinja2` |
| `shellspec` | Increment 4 (ZSH) | `brew install shellspec` |
| `pytest-xdist` | Optional | `pip install pytest-xdist` |
| `pytest-watch` | Optional | `pip install pytest-watch` |
| `pytest-cov` | Optional | `pip install pytest-cov` |

---

## Risk Notes

- **Increment 1 is the riskiest** — touching 63 test files with marker additions. Run full suite after each batch.
- **Command count changes** in Increment 2 — removing 5, adding 3 = net -2. Update validate-counts.sh early.
- **Template rendering** in Increment 4 must produce valid Python/Bash. The `/craft:test:template validate` command exists specifically for this.

---

## How to Use This File

```
/craft:orchestrate    # Load this file, execute increments
```

Each increment is a self-contained unit. Complete one, commit, then move to the next. Increments 1-3 are HIGH priority and ship together. Increment 4 is MEDIUM. Increment 5 is FUTURE.
