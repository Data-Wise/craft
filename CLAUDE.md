# CLAUDE.md - Craft Plugin

> **TL;DR**: Use `/craft:do <task>` for smart routing, `/craft:check` before commits, `/craft:git:worktree` for feature branches. **Always start work from `dev` branch** - never commit to `main` directly.

**100 commands** · **21 skills** · **8 agents** · **14 specs** · [Documentation](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

**Current Version:** v2.6.0 (released 2026-01-20)
**Documentation Status:** 96% complete (v2.7.0 planning phase)

## Git Workflow

```text
main (protected) ← PR only, never direct commits
  ↑
dev (integration) ← Plan here, branch from here
  ↑
feature/* (worktrees) ← All implementation work
```

### Workflow Steps

| Step | Action | Command |
|------|--------|---------|
| 1. Plan | Analyze on `dev`, wait for approval | `git checkout dev` |
| 2. Branch | Create worktree for isolation | `/craft:git:worktree feature/<name>` |
| 3. Develop | Conventional commits (`feat:`, `fix:`, etc.) | Small, atomic commits |
| 4. Integrate | Test → rebase → PR to dev | `gh pr create --base dev` |
| 5. Release | PR from dev to main | `gh pr create --base main --head dev` |

### Constraints

- **CRITICAL**: Always start work from `dev` branch (`git checkout dev`)
- **Never** commit directly to `main`
- **Never** write feature code on `dev`
- **Always** verify branch: `git branch --show-current`

## Quick Commands

| Task | Shell | Craft |
|------|-------|-------|
| Run unit tests | `python3 tests/test_craft_plugin.py` | `/craft:test:run` |
| Integration tests | `python3 tests/test_integration_*.py` | - |
| Dependency tests | `bash tests/test_dependency_management.sh` | - |
| Validate | `./scripts/validate-counts.sh` | `/craft:check` |
| Build docs | `mkdocs build` | - |
| Lint code | - | `/craft:code:lint` |
| Architecture | - | `/craft:arch:analyze` |
| Git status | `git status` | `/craft:git:status` |
| Worktree | `git worktree add ...` | `/craft:git:worktree <branch>` |
| Clean branches | - | `/craft:git:clean` |
| CI workflow | - | `/craft:ci:generate` |
| Smart routing | - | `/craft:do <task>` |
| Brainstorm | - | `/craft:workflow:brainstorm` |
| Orchestrate | - | `/craft:orchestrate` |
| Orchestrate task | - | `/craft:do "task" --orch=<mode>` |

## Execution Modes

| Mode | Budget | Use Case | Example |
|------|--------|----------|---------|
| **default** | < 10s | Quick tasks | `/craft:code:lint` |
| **debug** | < 120s | Verbose traces | `/craft:code:lint debug` |
| **optimize** | < 180s | Performance | `/craft:code:lint optimize` |
| **release** | < 300s | Thorough validation | `/craft:code:lint release` |

Auto-selection: debug (errors), optimize (performance), release (deploy), else default.

## Agents

| Agent | Model | Use For |
|-------|-------|---------|
| **orchestrator-v2** | sonnet | Complex multi-step tasks, parallel execution (v2.3.0) |
| **orchestrator** | sonnet | Basic workflow automation |
| **docs-architect** | sonnet | System documentation, architecture guides |
| **api-documenter** | sonnet | OpenAPI specs, API docs, SDKs |
| **tutorial-engineer** | sonnet | Step-by-step tutorials, onboarding |
| **reference-builder** | haiku | Parameter listings, config references |
| **mermaid-expert** | haiku | Flowcharts, sequence diagrams, ERDs |
| **demo-engineer** | - | Terminal GIF demos (asciinema workflow) |

## Project Structure

```text
craft/
├── .claude-plugin/     # Plugin manifest, hooks, validators
├── commands/           # 100 commands (arch, ci, code, docs, git, site, test, workflow)
├── skills/             # 21 specialized skills
├── agents/             # 8 agents
├── scripts/            # 20+ utility scripts (dependency management, converters, installers)
├── utils/              # Python utilities (complexity scorer, validators, parsers)
├── tests/              # Comprehensive test suite (581+ tests, 90%+ coverage)
├── docs/
│   ├── specs/          # Implementation specs (14 total)
│   ├── guide/          # User guides (complexity scoring, teaching, Claude Code 2.1)
│   ├── tutorials/      # Step-by-step guides
│   └── brainstorm/     # Working drafts (gitignored)
└── .STATUS             # Current milestone and progress
```

## Recent Major Features

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

| Category | Tests | Purpose | Guide |
|----------|-------|---------|-------|
| **Dependency System** | 9 | Tool detection, installation, repair | [Dependency Management Advanced](docs/guide/dependency-management-advanced.md) |
| **Orchestrator Workflows** | 13 | Complexity scoring, routing, agent coordination | [Claude Code 2.1.0 Guide](docs/guide/claude-code-2.1-integration.md) |
| **Teaching Workflow** | 8 | Course detection, validation, publishing | [Teaching Workflow Guide](docs/guide/teaching-workflow.md) |
| **Total** | **27** | **End-to-end system validation** | [Integration Testing Guide](docs/guide/integration-testing.md) |

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

### Implementation & Documentation Completeness (v2.6.0)

| Feature | Commands | Implementation | Documentation | Status |
|---------|----------|---|---|---|
| **Brainstorm Question Control (v2.4.0)** | 1 | 100% | 95% | Complete ✅ |
| **Hub v2.0** | 1 | 100% | 95% | Complete ✅ |
| **Claude Code 2.1.0** | 3 | 100% | 90% | Complete ✅ |
| **Dependency Management** | 1 | 100% | 85% | Complete ✅ |
| **Teaching Workflow** | 5 | 100% | 90% | Complete ✅ |
| **Website Organization** | 6 | 100% | 100% | Complete ✅ |
| **Broken Link Validation** | 2 | 100% | 95% | Complete ✅ |
| **Code Quality Commands** | 8 | 100% | 85% | Complete ✅ |
| **Testing Commands** | 10 | 100% | 80% | Complete ✅ |
| **Architecture Commands** | 12 | 100% | 75% | Complete ✅ |
| **Remaining Commands** | 51 | 100% | 40% | Baseline ✅ |
| **TOTAL** | **100** | **100%** | **95%** | v2.6.0 ✅ |

**Legend:**

- 100% Implementation: All planned features completed
- 90-100% Docs: Comprehensive guides with examples
- 80-89% Docs: Good documentation, minor gaps
- 70-79% Docs: Basic documentation, could expand
- <70% Docs: Minimal documentation

### Documentation Guides

| Guide | Content | Location |
|-------|---------|----------|
| **Version History** | Evolution from v1.0.0 → v2.4.0, feature timeline | `docs/VERSION-HISTORY.md` |
| **Complexity Scoring** | 7-factor algorithm, routing zones, examples | `docs/guide/complexity-scoring-algorithm.md` |
| **Claude Code 2.1** | Integration overview, agent delegation, session teleportation | `docs/guide/claude-code-2.1-integration.md` |
| **Teaching Workflow** | Preview-before-publish, semester tracking, validation | `docs/guide/teaching-workflow.md` |
| **Dependency Management** | Checking, installation, batch conversion workflow | Tutorial docs (in development) |
| **Integration Testing** | Test patterns, validation, debugging | Tutorial docs (in development) |

## Active Development

### Current Worktree (v2.7.0 Planning)

| Branch | Location | Status |
|--------|----------|--------|
| `dev` | `/Users/dt/projects/dev-tools/craft` | Main repo (clean) |
| `feature/docs-update-interactive` | `~/.git-worktrees/craft/feature-docs-update-interactive` | **WIP: Phase 1 Starting** |

### v2.7.0 - Interactive Documentation & Enhanced Linting (Planning)

| Feature | Priority | Effort | Status |
|---------|----------|--------|--------|
| Interactive docs:update specs | Critical | 4h | ✅ Complete (1,634 lines) |
| docs:sync merge specs | Critical | 2h | ✅ Complete (947 lines) |
| Markdownlint expansion (24 rules) | Critical | 1h | ✅ Complete |
| Worktree setup | High | 30m | ✅ Complete |
| Phase 1: Core workflow | High | 8-10h | ⏳ Starting |
| Phase 2: GIF integration | Medium | 6-8h | 📝 Planned |
| Phase 3: Lint & tutorial | Medium | 8-10h | 📝 Planned |
| Phase 4: Help files | High | 10-12h | 📝 Planned |

**Specs:** `docs/specs/SPEC-docs-update-interactive-2026-01-22.md`, `docs/specs/SPEC-docs-sync-update-integration-2026-01-22.md`

### Completed Features (v2.6.0)

| Feature | Priority | Effort | Status |
|---------|----------|--------|--------|
| Test fixes (706/706 passing) | Critical | 4h | ✅ Complete |
| Markdownlint expansion (3 → 24 rules) | High | 2h | ✅ Complete |
| Release notes | High | 1h | ✅ Complete |
| CI/CD fixes | Medium | 1h | ✅ Complete |

See `docs/specs/` for detailed specifications (14 total).

## Key Files

| File | Purpose |
|------|---------|
| `.STATUS` | Current milestone, progress, session history |
| `commands/do.md` | Universal smart routing with complexity scoring |
| `commands/check.md` | Pre-flight validation |
| `commands/orchestrate.md` | Multi-agent coordination |
| `commands/hub.md` | Zero-maintenance command discovery (v2.0) |
| `commands/workflow/brainstorm.md` | ADHD-friendly brainstorming (v2.4.0 - Question control) |
| `docs/guide/orch-flag-usage.md` | --orch flag usage guide (v2.5.0, improved v2.5.1) |
| `docs/VERSION-HISTORY.md` | Complete version evolution (NEW) |
| `docs/guide/complexity-scoring-algorithm.md` | Complexity algorithm guide (NEW) |
| `docs/guide/claude-code-2.1-integration.md` | Claude Code 2.1 integration guide (NEW) |
| `docs/orch/ORCH-brainstorm-phase1-2026-01-18.md` | Phase 1 implementation plan |
| `docs/specs/SPEC-teaching-workflow-2026-01-16.md` | Teaching mode implementation spec |
| `docs/specs/SPEC-craft-hub-v2-2026-01-15.md` | Hub v2.0 architecture spec |
| `.linkcheck-ignore` | Expected broken links (test files, brainstorm refs) |
| `utils/complexity_scorer.py` | Task complexity scoring (0-10 scale) |
| `utils/linkcheck_ignore_parser.py` | Parser for .linkcheck-ignore patterns |
| `scripts/dependency-manager.sh` | Dependency checking and installation |
| `tests/test_brainstorm_phase1.py` | Phase 1 unit tests (53 tests) |
| `tests/test_integration_brainstorm_phase1.py` | Phase 1 integration tests (24 tests) |

## Test Suite

| Test File | Tests | Coverage | Purpose |
|-----------|-------|----------|---------|
| **Unit & Feature Tests** | | | |
| `tests/test_craft_plugin.py` | 370 | 84% | Core functionality |
| `tests/test_brainstorm_phase1.py` | 53 | 100% | Question control (v2.4.0) |
| `tests/test_complexity_scoring.py` | 15 | 100% | Complexity scorer |
| `tests/test_hot_reload_validators.py` | 9 | 95% | Hot-reload validators |
| `tests/test_agent_hooks.py` | 13 | 100% | Agent hooks |
| **Integration Tests** | | | |
| `tests/test_integration_brainstorm_phase1.py` | 24 | 100% | Question control integration |
| `tests/test_integration_dependency_system.py` | 9 | 100% | Dependency workflow |
| `tests/test_integration_orchestrator_workflows.py` | 13 | 100% | Task routing & scoring |
| `tests/test_integration_teaching_workflow.py` | 8 | 100% | Teaching mode (3 skipped) |
| **System Tests** | | | |
| `tests/test_dependency_management.sh` | 79 | 100% | Dependency system |
| **Total** | **581+** | **~90%** | **All systems** |

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Unit tests failing | `python3 tests/test_craft_plugin.py` |
| Integration tests failing | `python3 tests/test_integration_<name>.py` |
| Dependency tests failing | `bash tests/test_dependency_management.sh` |
| Broken links | `python3 tests/test_craft_plugin.py -k "broken_links"` |
| Outdated counts | `./scripts/validate-counts.sh` |
| Stale worktree | `git worktree remove <path> --force` |
| Orphaned worktrees | `git worktree prune` |
| Rebase conflicts | `git rebase --abort && git merge origin/dev` |
| Plugin not loading | Check `.claude-plugin/plugin.json` frontmatter |
| Command not found | Verify file in `commands/` with valid frontmatter |
| Agent not triggering | Check triggers list in agent frontmatter |
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
