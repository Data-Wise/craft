# CLAUDE.md - Craft Plugin

> **TL;DR**: Use `/craft:do <task>` for smart routing, `/craft:check` before commits, `/craft:git:worktree` for feature branches. **Always start work from `dev` branch** - never commit to `main` directly.

**99 commands** · **21 skills** · **8 agents** · **6 specs** · **4 gap analysis docs** · [Documentation](https://data-wise.github.io/craft/) · [GitHub](https://github.com/Data-Wise/craft)

**Current Version:** v1.24.0 (released 2026-01-18)
**Documentation Status:** 60% complete (3 critical gaps identified - see DOCS-GAP-ANALYSIS-COMPLETE.md)

## Git Workflow

```
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

```
craft/
├── .claude-plugin/     # Plugin manifest, hooks, validators
├── commands/           # 99 commands (arch, ci, code, docs, git, site, test, workflow)
├── skills/             # 21 specialized skills
├── agents/             # 8 agents
├── scripts/            # 20+ utility scripts (dependency management, converters, installers)
├── utils/              # Python utilities (complexity scorer, validators, parsers)
├── tests/              # Comprehensive test suite (516+ tests, 90%+ coverage)
├── docs/
│   ├── specs/          # Implementation specs (6 total)
│   ├── tutorials/      # Step-by-step guides
│   └── brainstorm/     # Working drafts (gitignored)
└── .STATUS             # Current milestone and progress
```

## Recent Major Features (v1.24.0)

### Hub v2.0 - Zero-Maintenance Command Discovery ✅
- 3-layer progressive disclosure (Main → Category → Detail + Tutorial)
- Auto-discovery from YAML frontmatter (no manual maintenance)
- 52 tests, 98% coverage, <2ms cached performance
- 94% faster than target (12ms uncached vs 200ms goal)

### Claude Code 2.1.0 Integration ✅
- Complexity scoring system (0-10 scale) for smart task routing
- 3 hot-reload validators (test-coverage, broken-links, lint-check)
- Orchestration hooks (PreToolUse, PostToolUse, Stop)
- Agent delegation with 5 specialized agents
- 37 unit tests, 100% passing, 96% coverage

### Dependency Management System ✅
- Full dependency checking/installation for demo command
- 10 scripts: manager, installer, health-check, repair, converters
- 4 installer adapters: brew, cargo, binary, consent-prompt
- 79 tests (unit, validation, e2e), 100% passing
- CI workflow for automated validation

### Teaching Workflow System ✅
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
| **Orchestrator Workflows** | 13 | Complexity scoring, routing, agent coordination | [Claude Code 2.1.0 Guide](docs/guide/claude-code-2.1-guide.md) |
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

### Integration Guides

- **[Integration Testing Guide](docs/guide/integration-testing.md)** - Understand test structure and categories
- **[Dependency Management Advanced](docs/guide/dependency-management-advanced.md)** - Deep dive into dependency system architecture and workflows
- **[Claude Code 2.1.0 Guide](docs/guide/claude-code-2.1-guide.md)** - Complexity scoring, validators, hooks, and session management

## Active Development

### Current Worktree
| Branch | Location | Status |
|--------|----------|--------|
| `dev` | `/Users/dt/projects/dev-tools/craft` | Main repo (clean) |
| `feature/teaching-flags` | `~/.git-worktrees/craft/feature-teaching-flags` | Planned (add --teaching flags) |

### Planned Features
| Feature | Priority | Effort | Status |
|---------|----------|--------|--------|
| Teaching command flags | Medium | 2-4h | Planned |
| Help Template System | High | 30h | Spec ready |
| Spec Integration | High | 20h | Spec ready |

See `docs/specs/` for detailed specifications.

## Key Files

| File | Purpose |
|------|---------|
| `.STATUS` | Current milestone, progress, session history |
| `commands/do.md` | Universal smart routing with complexity scoring |
| `commands/check.md` | Pre-flight validation |
| `commands/orchestrate.md` | Multi-agent coordination |
| `commands/hub.md` | Zero-maintenance command discovery (v2.0) |
| `commands/workflow/brainstorm.md` | ADHD-friendly brainstorming |
| `docs/specs/SPEC-teaching-workflow-2026-01-16.md` | Teaching mode implementation spec |
| `docs/specs/SPEC-craft-hub-v2-2026-01-15.md` | Hub v2.0 architecture spec |
| `.linkcheck-ignore` | Expected broken links (test files, brainstorm refs) |
| `utils/complexity_scorer.py` | Task complexity scoring (0-10 scale) |
| `utils/linkcheck_ignore_parser.py` | Parser for .linkcheck-ignore patterns |
| `scripts/dependency-manager.sh` | Dependency checking and installation |

## Test Suite

| Test File | Tests | Coverage | Purpose |
|-----------|-------|----------|---------|
| **Unit & Feature Tests** |
| `tests/test_craft_plugin.py` | 370 | 84% | Core functionality |
| `tests/test_complexity_scoring.py` | 15 | 100% | Complexity scorer |
| `tests/test_hot_reload_validators.py` | 9 | 95% | Hot-reload validators |
| `tests/test_agent_hooks.py` | 13 | 100% | Agent hooks |
| **Integration Tests** |
| `tests/test_integration_dependency_system.py` | 9 | 100% | Dependency workflow |
| `tests/test_integration_orchestrator_workflows.py` | 13 | 100% | Task routing & scoring |
| `tests/test_integration_teaching_workflow.py` | 8 | 100% | Teaching mode (3 skipped) |
| **System Tests** |
| `tests/test_dependency_management.sh` | 79 | 100% | Dependency system |
| **Total** | **516+** | **~90%** | **All systems** |

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

## Documentation Gap Analysis (2026-01-18)

**Status:** Comprehensive analysis complete - Ready for Phase 1 implementation

**Key Findings:**
- 60% documentation complete (3 features under-documented)
- 3 critical gaps identified (4-5 hours to close)
- Worktree ready: `~/.git-worktrees/craft/feature/docs-gap-analysis`

**Critical Gaps:**
1. Integration Testing Guide (30 min) - 27 tests, no user docs
2. Dependency Management Guide (1.5h) - 16K LOC, incomplete guide
3. Claude Code 2.1.0 Integration Guide (1.5h) - 6K LOC, missing user docs

**Documentation Resources:**
- **DOCS-GAP-ANALYSIS-COMPLETE.md** — Gateway document (start here)
- **docs/GAP-ANALYSIS-2026-01-18.md** — Full 1,200+ line analysis
- **docs/README-DOCS-GAP-ANALYSIS.md** — Implementation guide with templates
- **docs/SESSION-SUMMARY-2026-01-18-DOCS-ANALYSIS.md** — Session overview
- **.STATUS** — Session details (session_2026_01_18_docs_gap_analysis)

**Next Steps:** Create critical guides in Phase 1 (4-5 hours total)

## Links

- [Documentation Site](https://data-wise.github.io/craft/) — Full guides and references
- [Commands Reference](https://data-wise.github.io/craft/commands/) — All 99 commands
- [Architecture Guide](https://data-wise.github.io/craft/architecture/) — How Craft works
- [Specifications](docs/specs/) — Implementation specs (6 total)
- [Gap Analysis](DOCS-GAP-ANALYSIS-COMPLETE.md) — Documentation gap analysis (2026-01-18)
- [GitHub Repository](https://github.com/Data-Wise/craft) — Source code and issues
