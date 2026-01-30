# CLAUDE.md - Craft Plugin

> **TL;DR**: Use `/craft:do <task>` for smart routing, `/craft:check` before commits, `/craft:git:worktree` for feature branches. **Always start work from `dev` branch** - never commit to `main` directly.

**105 commands** · **21 skills** · **8 agents** · **15 specs** · [Documentation](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

**Current Version:** v2.10.0-dev (in development) | **Latest Release:** v2.9.1 (2026-01-29)
**Documentation Status:** 98% complete | **Tests:** 847 passing (81 claude-md + 766 core)

## Git Workflow

```text
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

### Workflow Steps

| Step         | Action                                       | Command                               |
| ------------ | -------------------------------------------- | ------------------------------------- |
| 1. Plan      | Analyze on `dev`, wait for approval          | `git checkout dev`                    |
| 2. Branch    | Create worktree for isolation                | `/craft:git:worktree feature/<name>`  |
| 3. Develop   | Conventional commits (`feat:`, `fix:`, etc.) | Small, atomic commits                 |
| 4. Integrate | Test → rebase → PR to dev                    | `gh pr create --base dev`             |
| 5. Release   | PR from dev to main                          | `gh pr create --base main --head dev` |

### Constraints

- **CRITICAL**: Always start work from `dev` branch (`git checkout dev`)
- **Never** commit directly to `main`
- **Never** write feature code on `dev`
- **Always** verify branch: `git branch --show-current`

## Quick Commands

| Task              | Shell                                      | Craft                            |
| ----------------- | ------------------------------------------ | -------------------------------- |
| Run unit tests    | `python3 tests/test_craft_plugin.py`       | `/craft:test:run`                |
| Integration tests | `python3 tests/test_integration_*.py`      | -------------------------------- |
| Dependency tests  | `bash tests/test_dependency_management.sh` | -------------------------------- |
| Validate          | `./scripts/validate-counts.sh`             | `/craft:check`                   |
| Build docs        | `mkdocs build`                             | -------------------------------- |
| Lint code         | ------------------------------------------ | `/craft:code:lint`               |
| Lint markdown     | `npx markdownlint-cli2 "**/*.md"`          | `/craft:docs:lint`               |
| Architecture      | ------------------------------------------ | `/craft:arch:analyze`            |
| Git status        | `git status`                               | `/craft:git:status`              |
| Worktree          | `git worktree add ...`                     | `/craft:git:worktree <branch>`   |
| Clean branches    | ------------------------------------------ | `/craft:git:clean`               |
| CI workflow       | ------------------------------------------ | `/craft:ci:generate`             |
| Smart routing     | ------------------------------------------ | `/craft:do <task>`               |
| Brainstorm        | ------------------------------------------ | `/craft:workflow:brainstorm`     |
| Orchestrate       | ------------------------------------------ | `/craft:orchestrate`             |
| Orchestrate task  | ------------------------------------------ | `/craft:do "task" --orch=<mode>` |
| CLAUDE.md update  | ------------------------------------------ | `/craft:docs:claude-md:update`   |
| CLAUDE.md audit   | ------------------------------------------ | `/craft:docs:claude-md:audit`    |
| CLAUDE.md fix     | ------------------------------------------ | `/craft:docs:claude-md:fix`      |
| Badge sync        | ------------------------------------------ | `/craft:site:update` (Step 3.5)  |
| CI badge validate | ------------------------------------------ | `/craft:ci:validate`             |

## Execution Modes

| Mode         | Budget | Use Case            | Example                     |
| ------------ | ------ | ------------------- | --------------------------- |
| **default**  | < 10s  | Quick tasks         | `/craft:code:lint`          |
| **debug**    | < 120s | Verbose traces      | `/craft:code:lint debug`    |
| **optimize** | < 180s | Performance         | `/craft:code:lint optimize` |
| **release**  | < 300s | Thorough validation | `/craft:code:lint release`  |

Auto-selection: debug (errors), optimize (performance), release (deploy), else default.

## Agents

| Agent                 | Model  | Use For                                               |
| --------------------- | ------ | ----------------------------------------------------- |
| **orchestrator-v2**   | sonnet | Complex multi-step tasks, parallel execution (v2.3.0) |
| **orchestrator**      | sonnet | Basic workflow automation                             |
| **docs-architect**    | sonnet | System documentation, architecture guides             |
| **api-documenter**    | sonnet | OpenAPI specs, API docs, SDKs                         |
| **tutorial-engineer** | sonnet | Step-by-step tutorials, onboarding                    |
| **reference-builder** | haiku  | Parameter listings, config references                 |
| **mermaid-expert**    | haiku  | Flowcharts, sequence diagrams, ERDs                   |
| **demo-engineer**     | ------ | Terminal GIF demos (asciinema workflow)               |

## Project Structure

```text
craft/
├── .claude-plugin/     # Plugin manifest, hooks, validators
├── commands/           # 100 commands (arch, ci, code, docs, git, site, test, workflow)
├── skills/             # 21 specialized skills
├── agents/             # 8 agents
├── scripts/            # 20+ utility scripts (dependency management, converters, installers)
├── utils/              # Python utilities (complexity scorer, validators, parsers)
├── tests/              # Comprehensive test suite (770+ tests, 90%+ coverage)
├── docs/
│   ├── specs/          # Implementation specs (14 total)
│   ├── guide/          # User guides (complexity scoring, teaching, Claude Code 2.1)
│   ├── tutorials/      # Step-by-step guides
│   └── brainstorm/     # Working drafts (gitignored)
└── .STATUS             # Current milestone and progress
```

## Recent Major Features

### v2.10.0 - Claude-MD Command Suite (In Development) 🚧

**Merged:** PR #39 (2026-01-30)

**Commands Added (5):**

- `/craft:docs:claude-md:update` - Sync CLAUDE.md with project state
- `/craft:docs:claude-md:audit` - Validate completeness and accuracy (5 checks)
- `/craft:docs:claude-md:fix` - Auto-fix common issues (4 fix methods)
- `/craft:docs:claude-md:scaffold` - Create from template (3 project types)
- `/craft:docs:claude-md:edit` - Interactive section editing

**Implementation:**

- 7 utility modules (2,713 lines Python)
  - `claude_md_detector.py` - 6 project types, version extraction
  - `claude_md_auditor.py` - 5 validation checks, 3 severity levels
  - `claude_md_fixer.py` - 4 auto-fix methods
  - `claude_md_template_populator.py` - 18+ template variables
  - `claude_md_section_editor.py` - Interactive editing
  - `claude_md_updater.py` - Metric-based updates
  - `claude_md_updater_simple.py` - Simple metric updates
- 3 project templates (plugin, teaching, r-package)
- 81 comprehensive tests (100% passing, 0.024s)
- 3,304 lines documentation

**Performance:**

- Full detection: 0.003s (166x faster than 0.5s target)
- Command scanning: 0.002s (50x faster than 0.1s target)
- Version extraction: 0.001s per 100 calls
- Thread-safe concurrent detection verified

**Test Enhancements:**

- Concurrent detection (10 parallel threads)
- Symlink handling with fallback
- Performance benchmarking with targets

**Files Changed:** 38 (+15,997/-271)

**Release:** Target v2.10.0 (pending)

---

### v2.9.0 - Command Behavior Enhancements (Released 2026-01-29) ✅

**Command Enhancements:**

- **"Show Steps First" Pattern**: All 4 most-used commands show plan before executing, ask for confirmation
- **Interactive Orchestration**: Mode selection via AskUserQuestion, wave checkpoints, plan confirmation
- **Worktree Auto-Setup**: Scope detection from branch patterns, auto-creates ORCHESTRATE/SPEC files
- **Post-Merge Pipeline**: `--post-merge` flag for docs:update with 5-phase auto-fix
- **Check Step Preview**: Mode-specific check lists with skip/dry-run options
- **Orchestrator-v2 Alignment**: Updated agent with Claude Code subagent constraints

**Documentation Expansion (2026-01-29):**

- 6 comprehensive files created (3,880 lines total)
- Documentation completeness: 95% → 98% (+3%)
- Tutorial coverage: 25% → 75% (+50%)
- New guides: Check Command Mastery (460 lines), Worktree Advanced Patterns (575 lines)
- New tutorials: Post-Merge Pipeline (542 lines), Worktree Setup (795 lines), Orchestrator Modes (446 lines)
- New reference: Git Worktree Quick Reference (484 lines)
- Coverage improvements: Check command (+55%), Git worktree (+38%), Orchestrator modes (+45%)

**Testing:**

- 145 new tests (93 e2e + 52 orch handler), 847 total tests passing
- CI Test Fixes: Resolved 15 failing tests (hardcoded paths, pre-commit hooks, config validation, dependencies)

**Release:**

- Merged via PR #36 (command enhancements) + PR #37 (test fixes) + documentation expansion
- Release: <https://github.com/Data-Wise/craft/releases/tag/v2.9.0>
- Documentation site: <https://data-wise.github.io/craft/>

### v2.6.0 - Documentation Quality Improvements (Released 2026-01-20) ✅

- Fixed all failing tests → 706/706 passing (100% pass rate)
- Expanded markdownlint pre-commit hook (3 → 24 rules)
  - Lists: MD004, MD005, MD007, MD029, MD030, MD031, MD032
  - Headings: MD003, MD022, MD023, MD036
  - Code: MD040, MD046, MD048
  - Links/Images: MD042, MD045, MD052, MD056
  - Whitespace: MD009, MD010, MD012
  - Inline: MD034, MD049, MD050
- Created comprehensive release notes (RELEASE-v2.6.0.md)
- CI/CD fixes: Added PyYAML dependency, removed hardcoded paths
- Merged PR #30 (markdownlint feature) + 6 follow-up fixes

### v2.5.0-v2.5.1 - Orchestration & List Spacing ✅

- **--orch Flag Integration (v2.5.0)**: Explicit orchestration mode for 5 key commands
- **Markdownlint List Spacing (v2.5.1)**: MD030/MD004/MD032 enforcement with pre-commit hook
- 36 tests (15 unit + 21 integration), 95% coverage
- 78 comprehensive tests (21 unit + 42 validation + 15 e2e), 100% passing

### v2.4.0 - Command Discovery & ADHD Features ✅

#### Hub v2.0 - Zero-Maintenance Command Discovery ✅

- 3-layer progressive disclosure (Main → Category → Detail + Tutorial)
- Auto-discovery from YAML frontmatter (no manual maintenance)
- 52 tests, 98% coverage, <2ms cached performance
- 94% faster than target (12ms uncached vs 200ms goal)

#### Claude Code 2.1.0 Integration ✅

- Complexity scoring system (0-10 scale) for smart task routing
- 3 hot-reload validators (test-coverage, broken-links, lint-check)
- Orchestration hooks (PreToolUse, PostToolUse, Stop)
- Agent delegation with 5 specialized agents
- 37 unit tests, 100% passing, 96% coverage

#### Dependency Management System ✅

- Full dependency checking/installation for demo command
- 10 scripts: manager, installer, health-check, repair, converters
- 4 installer adapters: brew, cargo, binary, consent-prompt
- 79 tests (unit, validation, e2e), 100% passing
- CI workflow for automated validation

#### Teaching Workflow System ✅

- Teaching mode auto-detection (`.flow/teach-config.yml`)
- Safe publish workflow (draft → preview → validate → deploy)
- Semester progress tracking
- Content validation (syllabus, schedule, assignments)
- 5 teaching-aware commands

## Integration Features (v1.24.0)

The v1.24.0 release includes 27 integration tests validating three critical systems:

### Integration Test Categories

| Category                   | Tests  | Purpose                                         | Guide                                                                          |
| -------------------------- | ------ | ----------------------------------------------- | ------------------------------------------------------------------------------ |
| **Dependency System**      | 9      | Tool detection, installation, repair            | [Dependency Management Advanced](docs/guide/dependency-management-advanced.md) |
| **Orchestrator Workflows** | 13     | Complexity scoring, routing, agent coordination | [Claude Code 2.1.0 Guide](docs/guide/claude-code-2.1-integration.md)           |
| **Teaching Workflow**      | 8      | Course detection, validation, publishing        | [Teaching Workflow Guide](docs/guide/teaching-workflow.md)                     |
| **Total**                  | **27** | **End-to-end system validation**                | [Integration Testing Guide](docs/guide/integration-testing.md)                 |

### Running Integration Tests

```bash
# Run all integration tests
python3 tests/test_integration_*.py

# Run specific category
python3 tests/test_integration_dependency_system.py
python3 tests/test_integration_orchestrator_workflows.py
python3 tests/test_integration_teaching_workflow.py
```

### Key Integration Features

1. **Dependency System** - Automatic tool detection (4 methods), health validation, intelligent installation
2. **Complexity Scoring** - 7-factor algorithm (0-10 scale) for smart task routing
3. **Agent Hooks** - Lifecycle integration points (PreToolUse, PostToolUse, Stop)
4. **Hot-Reload Validators** - Automatic validation on file changes (test-coverage, broken-links, lint-check)
5. **Session State** - Persistent session management with teleportation support

## Feature Status Matrix

### Implementation & Documentation Completeness (v2.9.0)

| Feature                                  | Commands | Implementation | Documentation | Status      |
| ---------------------------------------- | -------- | -------------- | ------------- | ----------- |
| **Command Enhancements (v2.9.0)**        | 4        | 100%           | 98%           | Released ✅ |
| **Check Command Mastery**                | 1        | 100%           | 95%           | Released ✅ |
| **Git Worktree Advanced**                | 1        | 100%           | 98%           | Released ✅ |
| **Orchestrator Modes**                   | 1        | 100%           | 95%           | Released ✅ |
| **Brainstorm Question Control (v2.4.0)** | 1        | 100%           | 95%           | Complete ✅ |
| **Hub v2.0**                             | 1        | 100%           | 95%           | Complete ✅ |
| **Claude Code 2.1.0**                    | 3        | 100%           | 90%           | Complete ✅ |
| **Dependency Management**                | 1        | 100%           | 85%           | Complete ✅ |
| **Teaching Workflow**                    | 5        | 100%           | 90%           | Complete ✅ |
| **Website Organization**                 | 6        | 100%           | 100%          | Complete ✅ |
| **Broken Link Validation**               | 2        | 100%           | 95%           | Complete ✅ |
| **Code Quality Commands**                | 8        | 100%           | 85%           | Complete ✅ |
| **Testing Commands**                     | 10       | 100%           | 80%           | Complete ✅ |
| **Architecture Commands**                | 12       | 100%           | 75%           | Complete ✅ |
| **Remaining Commands**                   | 51       | 100%           | 40%           | Baseline ✅ |
| **TOTAL**                                | **100**  | **100%**       | **98%**       | v2.9.0 ✅   |

**Legend:**

- 100% Implementation: All planned features completed
- 90-100% Docs: Comprehensive guides with examples
- 80-89% Docs: Good documentation, minor gaps
- 70-79% Docs: Basic documentation, could expand
- <70% Docs: Minimal documentation

### Documentation Guides

| Guide                        | Content                                                       | Location                                        |
| ---------------------------- | ------------------------------------------------------------- | ----------------------------------------------- |
| **Version History**          | Evolution from v1.0.0 → v2.9.0, feature timeline              | `docs/VERSION-HISTORY.md`                       |
| **Check Command Mastery**    | Decision framework, scenarios, performance trade-offs (NEW)   | `docs/guide/check-command-mastery.md`           |
| **Worktree Advanced**        | Multi-worktree management, team collaboration (NEW)           | `docs/guide/worktree-advanced-patterns.md`      |
| **Interactive Commands**     | "Show Steps First" pattern across all commands (NEW)          | `docs/guide/interactive-commands.md`            |
| **Complexity Scoring**       | 7-factor algorithm, routing zones, examples                   | `docs/guide/complexity-scoring-algorithm.md`    |
| **Claude Code 2.1**          | Integration overview, agent delegation, session teleportation | `docs/guide/claude-code-2.1-integration.md`     |
| **Teaching Workflow**        | Preview-before-publish, semester tracking, validation         | `docs/guide/teaching-workflow.md`               |
| **Post-Merge Pipeline**      | 5-phase auto-fix workflow after PR merge (NEW)                | `docs/tutorials/TUTORIAL-post-merge-pipeline.md` |
| **Worktree Setup**           | Beginner to intermediate guide with auto-setup (NEW)          | `docs/tutorials/TUTORIAL-worktree-setup.md`     |
| **Orchestrator Modes**       | Same task in 4 modes with performance metrics (NEW)           | `docs/tutorials/orchestrator-modes-compared.md` |
| **Interactive Orchestration**| Wave checkpoints, mode selection tutorial                    | `docs/tutorials/interactive-orchestration.md`   |
| **Dependency Management**    | Checking, installation, batch conversion workflow             | Tutorial docs (in development)                  |
| **Integration Testing**      | Test patterns, validation, debugging                          | Tutorial docs (in development)                  |

## Active Development

### Current Status

**Branch:** `dev` (synced with main @ v2.9.0)
**Location:** `/Users/dt/projects/dev-tools/craft`
**Status:** ✅ All releases merged, ready for new features

| Branch | Commit | Status |
|--------|--------|--------|
| **main** | `93a10ad` | ✅ v2.9.0 released |
| **dev** | `93a10ad` | ✅ Synced with main |
| **Worktrees** | None active | Clean state |

### Recent Releases

#### v2.9.0 - Command Behavior Enhancements (2026-01-29) ✅

**Merged PRs:**

- PR #36: Command enhancements (feature → dev)
- PR #37: v2.9.0 release + CI test fixes (dev → main)

**What Shipped:**

- "Show Steps First" pattern across 4 commands
- Interactive orchestration with mode selection
- Git worktree auto-setup with scope detection
- Post-merge documentation pipeline
- Check step preview with mode-specific lists
- 15 CI test fixes (paths, hooks, config, dependencies)

**Release:** <https://github.com/Data-Wise/craft/releases/tag/v2.9.0>

#### v2.8.1 - Markdown Lint Style Fixes (2026-01-28) ✅

- Auto-fix 191 files
- MD025 duplicate H1 fixes (6 files)
- MD060 table alignment (5 files)
- Emoji-aware table formatter

**Release:** <https://github.com/Data-Wise/craft/releases/tag/v2.8.1>

### Future Features (v2.10.0+)

**Ideas for Next Release:**

- Styled output boxes for better UX
- Enhanced execution modes
- Language detection for multi-lang projects
- Rule expansion (30 → 42 markdownlint rules)

### Completed Features (v2.8.0)

| Feature                               | Status      |
| ------------------------------------- | ----------- |
| Execution layer (docs-lint.sh)        | ✅ Complete |
| Basic linting command                 | ✅ Complete |
| Auto-fix support                      | ✅ Complete |
| Pre-commit hook                       | ✅ Complete |
| Test fixes (706/706 passing)          | ✅ Complete |
| Markdownlint expansion (3 → 24 rules) | ✅ Complete |

See `docs/specs/` for detailed specifications (14 total).

## Key Files

| File                                              | Purpose                                                 |
| ------------------------------------------------- | ------------------------------------------------------- |
| `.STATUS`                                         | Current milestone, progress, session history            |
| `commands/do.md`                                  | Universal smart routing with complexity scoring         |
| `commands/check.md`                               | Pre-flight validation                                   |
| `commands/orchestrate.md`                         | Multi-agent coordination                                |
| `commands/hub.md`                                 | Zero-maintenance command discovery (v2.0)               |
| `commands/workflow/brainstorm.md`                 | ADHD-friendly brainstorming (v2.4.0 - Question control) |
| `docs/guide/orch-flag-usage.md`                   | --orch flag usage guide (v2.5.0, improved v2.5.1)       |
| `docs/VERSION-HISTORY.md`                         | Complete version evolution (NEW)                        |
| `docs/guide/complexity-scoring-algorithm.md`      | Complexity algorithm guide (NEW)                        |
| `docs/guide/claude-code-2.1-integration.md`       | Claude Code 2.1 integration guide (NEW)                 |
| `docs/orch/ORCH-brainstorm-phase1-2026-01-18.md`  | Phase 1 implementation plan                             |
| `docs/specs/SPEC-teaching-workflow-2026-01-16.md` | Teaching mode implementation spec                       |
| `docs/specs/SPEC-craft-hub-v2-2026-01-15.md`      | Hub v2.0 architecture spec                              |
| `.linkcheck-ignore`                               | Expected broken links (test files, brainstorm refs)     |
| `utils/complexity_scorer.py`                      | Task complexity scoring (0-10 scale)                    |
| `utils/linkcheck_ignore_parser.py`                | Parser for .linkcheck-ignore patterns                   |
| `scripts/dependency-manager.sh`                   | Dependency checking and installation                    |
| `tests/test_brainstorm_phase1.py`                 | Phase 1 unit tests (53 tests)                           |
| `tests/test_integration_brainstorm_phase1.py`     | Phase 1 integration tests (24 tests)                    |
| `docs/guide/interactive-commands.md`              | "Show Steps First" pattern guide (v2.9.0)               |
| `docs/tutorials/interactive-orchestration.md`     | Interactive orchestration tutorial (v2.9.0)             |
| `docs/reference/REFCARD-INTERACTIVE-COMMANDS.md`  | Interactive commands quick reference (v2.9.0)           |
| `tests/test_command_enhancements_e2e.py`          | Command enhancements e2e tests (93 tests)               |
| `tests/test_orch_flag_handler.py`                 | Orch flag handler tests (52 tests)                      |

## Test Suite

| Test File                                          | Tests    | Coverage | Purpose                      |
| -------------------------------------------------- | -------- | -------- | ---------------------------- |
| **Unit & Feature Tests**                           |          |          |                              |
| `tests/test_craft_plugin.py`                       | 370      | 84%      | Core functionality           |
| `tests/test_brainstorm_phase1.py`                  | 53       | 100%     | Question control (v2.4.0)    |
| `tests/test_complexity_scoring.py`                 | 15       | 100%     | Complexity scorer            |
| `tests/test_hot_reload_validators.py`              | 9        | 95%      | Hot-reload validators        |
| `tests/test_agent_hooks.py`                        | 13       | 100%     | Agent hooks                  |
| `tests/test_orch_flag_handler.py`                  | 52       | 100%     | Orch flag handler (v2.9.0)   |
| **Integration & E2E Tests**                        |          |          |                              |
| `tests/test_command_enhancements_e2e.py`           | 93       | 100%     | Command enhancements (v2.9.0)|
| `tests/test_integration_brainstorm_phase1.py`      | 24       | 100%     | Question control integration |
| `tests/test_integration_dependency_system.py`      | 9        | 100%     | Dependency workflow          |
| `tests/test_integration_orchestrator_workflows.py` | 13       | 100%     | Task routing & scoring       |
| `tests/test_integration_teaching_workflow.py`      | 8        | 100%     | Teaching mode (3 skipped)    |
| **System Tests**                                   |          |          |                              |
| `tests/test_dependency_management.sh`              | 79       | 100%     | Dependency system            |
| **Total**                                          | **847**  | **~90%** | **All systems**              |

## Troubleshooting

| Issue                       | Fix                                                                                |
| --------------------------- | ---------------------------------------------------------------------------------- |
| Unit tests failing          | `python3 tests/test_craft_plugin.py`                                               |
| Integration tests failing   | `python3 tests/test_integration_<name>.py`                                         |
| Dependency tests failing    | `bash tests/test_dependency_management.sh`                                         |
| Broken links                | `python3 tests/test_craft_plugin.py -k "broken_links"`                             |
| Outdated counts             | `./scripts/validate-counts.sh`                                                     |
| Stale worktree              | `git worktree remove <path> --force`                                               |
| Orphaned worktrees          | `git worktree prune`                                                               |
| Rebase conflicts            | `git rebase --abort && git merge origin/dev`                                       |
| Plugin not loading          | Check `.claude-plugin/plugin.json` frontmatter                                     |
| Command not found           | Verify file in `commands/` with valid frontmatter                                  |
| Agent not triggering        | Check triggers list in agent frontmatter                                           |
| GIF showing broken commands | **CRITICAL:** Test commands FIRST with Bash tool, verify output, THEN generate GIF |

## Phase 3 Documentation Enhancements

**Status:** Completed (87% → 95% target)

**New Documentation:**

- VERSION-HISTORY.md - Complete version evolution from v1.0.0 → v1.24.0
- Complexity Scoring Algorithm Guide - 7-factor system with visual decision flows
- Claude Code 2.1.0 Integration Guide - Smart routing, agents, validators, session teleportation
- Feature Status Matrix - Implementation and documentation completeness by feature

**Deliverables:**

- 3 new guide documents (1,609 lines)
- 17 Mermaid diagrams (task routing, complexity scoring, agent delegation, orchestration)
- Feature completeness matrix showing 100 commands with 95% documentation
- Version history timeline with 24+ releases documented

**Success Criteria Met:**

- ✅ VERSION-HISTORY.md created with comprehensive timeline
- ✅ Mermaid visualizations for complexity scoring and orchestration (17 diagrams)
- ✅ Feature status matrix in CLAUDE.md showing documentation completeness
- ✅ All internal links verified and working
- ✅ Documentation builds without errors (mkdocs: 3.83s)
- ✅ Guides properly referenced with links to guides/ directory

## Links

- [Documentation Site](https://data-wise.github.io/craft/) — Full guides and references
- [Commands Reference](https://data-wise.github.io/craft/commands/) — All 100 commands
- [Architecture Guide](https://data-wise.github.io/craft/architecture/) — How Craft works
- [Specifications](docs/specs/) — Implementation specs (14 total)
- [Version History](docs/VERSION-HISTORY.md) — Complete release timeline (NEW)
- [Complexity Scoring](docs/guide/complexity-scoring-algorithm.md) — Algorithm & routing (NEW)
- [Claude Code 2.1](docs/guide/claude-code-2.1-integration.md) — Integration guide (NEW)
- [GitHub Repository](https://github.com/Data-Wise/craft) — Source code and issues
