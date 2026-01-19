# Craft Plugin - Version History

> **Evolution of Craft**: From command automation tool to intelligent orchestration platform

**Latest Release:** v2.5.1 (2026-01-19)
**Total Releases:** 28 versions | **Development Time:** 2+ years
**Community:** 100+ commands documented, 615+ tests, 90%+ coverage

---

## Release Timeline

### v2.5.1 (2026-01-19) - User Experience Enhancements

**Status:** Released ✅

**Highlights:**
- **Interactive Mode Prompt**: Enhanced `prompt_user_for_mode()` with fallback behavior
- **Error Handling**: Graceful orchestrator spawn failures with actionable suggestions
- **Mode Recommendations**: Smart mode selection based on complexity scores (0-10 scale)
- **Manual Testing**: Comprehensive 10-scenario testing checklist
- **Troubleshooting**: 6 detailed troubleshooting scenarios with solutions

**Gap Coverage:**
Addresses 4 of 12 gaps identified in v2.5.0 gap analysis:
- ✅ Gap #1 (HIGH): Interactive mode prompt stub implementation
- ✅ Gap #4 (MED): Error handling for orchestrator spawn failures
- ✅ Gap #10 (LOW): Manual testing checklist for interactive features
- ✅ Gap #5 (MED): User guidance for prompt failures

**Stats:**
- Enhanced file: `utils/orch_flag_handler.py` (complete rewrite with error handling)
- New tests: 15 tests (6 prompt + 5 error + 4 recommendation)
- Total tests: 51 (18 existing + 15 new + 18 integration)
- New checklist: `TESTING-CHECKLIST.md` (10 manual test scenarios)
- Documentation updates: troubleshooting section + VERSION-HISTORY + CLAUDE.md

**Key Files:**
- `utils/orch_flag_handler.py` - Enhanced with error handling and recommendations
- `tests/test_orch_flag_handler.py` - Added 15 new tests (51 total)
- `TESTING-CHECKLIST.md` - 10-scenario manual testing guide
- `docs/guide/orch-flag-usage.md` - Added comprehensive troubleshooting
- `CLAUDE.md` - Added orch guide reference

**Implementation:**
- `prompt_user_for_mode()`: Documents expected Claude Code behavior with fallback
- `spawn_orchestrator()`: Returns bool for error handling, try/except wrapper
- `handle_orchestrator_failure()`: User-friendly error messages with 4 suggestions
- `recommend_orchestration_mode()`: Complexity-based recommendations (0-3→default, 4-7→optimize, 8-10→release)
- Test coverage: 100% for new functions, maintains 95%+ overall

**Deferred to v2.6.0:**
- 8 remaining gaps (all low priority)
- Website documentation sync
- Integration with /craft:hub for mode recommendations
- Performance metrics for mode selection

---

### v2.5.0 (2026-01-19) - --orch Flag Integration

**Status:** Released ✅

**Highlights:**
- **--orch Flag**: Explicit orchestration mode for 5 commands
  - `/craft:do`, `/craft:workflow:brainstorm`, `/craft:check`
  - `/craft:docs:sync`, `/craft:ci:generate`
- **Mode Selection**: Interactive prompts when mode not specified
- **Dry-Run Support**: Preview orchestration without spawning agents
- **4 Orchestration Modes**: default, debug, optimize, release

**Stats:**
- New file: utils/orch_flag_handler.py (core handler)
- New tests: 36 tests (15 unit + 21 integration), 95% coverage
- Updated: 5 command files with --orch flag support
- Documentation: User guide + updates to CLAUDE.md and VERSION-HISTORY.md

**Key Files:**
- utils/orch_flag_handler.py (core orchestration logic)
- tests/test_orch_flag_handler.py (15 unit tests)
- tests/test_integration_orch_flag.py (21 integration tests)
- docs/guide/orch-flag-usage.md (user guide)
- commands/do.md, brainstorm.md, check.md, docs/sync.md, ci/generate.md

**Implementation:**
- Core handler: `utils/orch_flag_handler.py`
- 58 tests (unit + integration), 95% coverage
- Backward compatible (opt-in flag)
- No breaking changes to existing commands

---

### v2.4.0 (2026-01-18) - Brainstorm Question Control (Phase 1)

**Status:** Released ✅

**Highlights:**
- Phase 1 MVP: Question Control for brainstorming
- Colon notation: `d:5`, `m:12`, `q:3` for custom question counts
- Categories flag: `--categories` or `-C` to filter question types
- 8-category question bank (16 questions total)
- Unlimited questions with milestone prompts every 8 questions
- 53 unit tests, 24 integration tests, 100% coverage

**Stats:**
- Commands: 100 (100% implementation)
- Tests: 581+ (90%+ coverage)
- Question categories: 8 (requirements, users, scope, technical, timeline, risks, existing, success)

**Key Files:**
- commands/workflow/brainstorm.md (v2.4.0)
- tests/test_brainstorm_phase1.py (53 tests)
- tests/test_integration_brainstorm_phase1.py (24 tests)

---

### v1.24.0 (2026-01-18) - Hub v2.0: Zero-Maintenance Command Discovery

**Status:** Released ✅

**Highlights:**
- Hub v2.0 Zero-Maintenance Command Discovery system
- 3-layer progressive disclosure (Main → Category → Detail + Tutorial)
- Auto-detection from YAML frontmatter (eliminates manual maintenance)
- 52 tests (98% coverage), <2ms cached performance, 94% faster than target
- Dependency Management System (79 tests, 100% passing)
- Claude Code 2.1.0 Integration support
- Integration tests for 27 workflows (100% passing)

**Stats:**
- Commands: 99 (100% implementation)
- Documentation: 87% complete (3 gaps identified)
- Tests: 516+ (90%+ coverage)
- Hub v2.0 performance: 12ms uncached (vs 200ms target)

**Key Files:**
- commands/_discovery.py (680 lines)
- tests/test_hub_*.py (52 tests)
- docs/GAP-ANALYSIS-2026-01-18.md (comprehensive)

---

### v1.23.1 (2026-01-17) - Test Coverage & Build Cleanup

**Status:** Released ✅

**Highlights:**
- Test Coverage & Build Cleanup merge from dev to main
- 253 files changed, +30,857/-151,299 lines
- 92% test pass rate
- Website organization Phase 1 & 2 merged
- Broken link validation integration
- Teaching workflow system complete
- asciinema default GIF recording method

**Stats:**
- Commands: 97 (up from 92)
- New validators: 3 (test-coverage, broken-links, lint-check)
- Tests added: 160 (139 teaching + 21 linkcheck)
- Navigation reduced: 14+ → 6 sections (50% reduction)

---

### v1.23.0 (2026-01-17) - Documentation Quality Automation

**Status:** Released ✅

**Highlights:**
- /craft:docs:check-links with internal link validation
- /craft:docs:lint with markdown linting + auto-fix
- Broken link validation system with .linkcheck-ignore parser
- CI pre-commit hooks for document validation
- 21 comprehensive link validation tests

**New Commands:**
- /craft:docs:check-links (4 modes: quick, thorough, interactive, ci)
- /craft:docs:lint (markdown formatting, embedded rules)

**Files Changed:**
- 21 files, +4,609 lines
- Dependencies: markdown-link-check, markdownlint-cli2
- Test coverage: 100% of new code

**Impact:**
- Prevents broken links in production
- Auto-fixes 90% of formatting issues
- Eliminates manual documentation validation

---

### v1.22.0 (2026-01-17) - Teaching Workflow System

**Status:** Released ✅

**Highlights:**
- Teaching mode auto-detection (.flow/teach-config.yml)
- Preview-before-publish safe deployment workflow
- Semester progress tracking dashboard
- Content validation (syllabus, schedule, assignments)
- 5 new teaching-aware commands
- 139 teaching-specific tests

**New Commands:**
- /craft:site:publish (preview + validation workflow)
- /craft:site:progress (semester tracking)
- Enhanced: /craft:git:status, /craft:site:build

**New Utilities:**
- detect_teaching_mode.py
- teaching_validation.py
- teach_config.py
- semester_progress.py

**Impact:**
- 80% time reduction: 15 min → 3 min
- Zero production bugs from deployments
- Safe preview-before-publish workflow

**Stats:**
- 44 files changed, +12,241 lines
- 139 tests (100% passing)
- 8 documentation guides

---

### v1.21.0 (2026-01-17) - Hub v2.0 Smart Discovery (Foundation)

**Status:** Released ✅

**Highlights:**
- Zero-maintenance command discovery engine
- Auto-detection from YAML frontmatter
- 3-layer progressive disclosure UI
- JSON caching with auto-invalidation
- Auto-generated tutorials
- 16 categories, 97 commands, always accurate

**Implementation:**
- Discovery engine: commands/_discovery.py (680 lines)
- Cache system: timestamp-based invalidation
- YAML parser: pure Python, no dependencies

**Performance:**
- Uncached: 12ms (target: <200ms) - 94% faster
- Cached: <2ms (target: <10ms) - 80% faster
- Scales to 500+ commands with no degradation

**Test Coverage:**
- 34 comprehensive tests (100% coverage)
- 12 discovery tests
- 7 layer 2 tests (category view)
- 8 layer 3 tests (command detail)
- 7 integration tests

**Enhanced:**
- 18 additional YAML edge case tests (v1.21.1)
- E2E workflow tests (6 tests)
- Total: 52 tests, 98% coverage

**Stats:**
- 26 files changed, +9,149 lines
- 3,527 lines documentation
- 4 Mermaid diagrams
- 15 API functions documented

---

### v1.20.0 (2026-01-15) - Phase 3 Dry-Run Completion

**Status:** Released ✅

**Target Exceeded:** 57% vs 52% target (Target: +5%)

**Phases:**
- Phase 1: /craft:git:clean, /craft:git:worktree, /craft:git:branch, /craft:git:sync (4 commands)
- Phase 2: CI detection, validation, docs quality (9 commands)
- Phase 3: Smart routing, task detection, code/test utilities (10 commands)

**New Features:**
- Complexity scoring system (0-10 scale)
- Task router with agent delegation
- Hot-reload validators
- Orchestration hooks

**Stats:**
- 27 of 47 target commands (57%)
- 17 of 90 total commands (19% dry-run coverage)
- All P0 commands: 100% complete
- All P1 commands: 100% complete

---

### v1.19.0 (2025-12-27) - Phase 2 Dry-Run Implementation

**Status:** Released ✅

**Highlights:**
- 9 new dry-run capable commands
- CI detection & validation system
- Documentation quality automation
- Site building & updating
- Navigation updates

**Commands Added:**
- /craft:ci:detect
- /craft:ci:validate
- /craft:docs:sync
- /craft:docs:changelog
- /craft:docs:check
- /craft:docs:update
- /craft:site:check
- /craft:site:update
- /craft:docs:claude-md

**Impact:**
- Full documentation workflow support
- CI/CD integration readiness
- Site building automation

---

### v1.18.0 (2025-12-20) - Phase 1 Dry-Run Implementation

**Status:** Released ✅

**Highlights:**
- 4 new dry-run capable commands
- Git workflow utilities
- Worktree management
- Branch cleanup & syncing

**Commands Added:**
- /craft:git:clean
- /craft:git:worktree
- /craft:git:branch
- /craft:git:sync

**Infrastructure:**
- utils/dry_run_output.py (dry-run output rendering)
- templates/dry-run-pattern.md (reusable template)
- 17 comprehensive tests

---

### v1.17.0 (2025-12-15) - Smart Routing Foundation

**Status:** Released ✅

**Highlights:**
- /craft:do smart routing command
- Complexity scoring system
- Task type detection
- Agent delegation framework
- Command vs agent vs orchestrator routing

**Features:**
- 0-10 complexity scale
- 5 classification factors
- 5 specialized agents
- Mode-aware routing

---

### v1.16.0 (2025-12-10) - Orchestrator v2 Enhancement

**Status:** Released ✅

**Highlights:**
- Orchestrator v2 improved
- Multi-agent coordination
- Context management
- Agent monitoring

**Versions:**
- orchestrator-v2: 2.0 → 2.1 → 2.3.0

---

### v1.15.0 - v1.1.0 (2025-06-01 - 2025-09-15)

**Foundation Releases:**

| Version | Focus | Status |
|---------|-------|--------|
| v1.15.0 | Command coverage expansion | Released |
| v1.14.0 | Documentation framework | Released |
| v1.13.0 | Site building system | Released |
| v1.12.0 | CI/CD workflow | Released |
| v1.11.0 | Git workflow commands | Released |
| v1.10.0 | Testing framework | Released |
| v1.9.0 | Architecture analysis | Released |
| v1.8.0 | Brainstorming workflow | Released |
| v1.7.0 | Code quality tools | Released |
| v1.6.0 | Plugin system | Released |
| v1.5.0 | Agent framework | Released |
| v1.4.0 | Skills system | Released |
| v1.3.0 | Documentation system | Released |
| v1.2.0 | Command framework | Released |
| v1.1.0 | Initial release | Released |

---

## Major Feature Evolution Timeline

### Dry-Run Support (v1.18-v1.20)
- Phase 1 (4 commands): Git workflows
- Phase 2 (9 commands): Docs & CI
- Phase 3 (10 commands): Smart routing & orchestration
- **Progress:** 27 of 47 target commands (57%)

### Documentation Quality (v1.23)
- /craft:docs:check-links
- /craft:docs:lint
- .linkcheck-ignore parser
- CI pre-commit hooks

### Teaching Mode (v1.22)
- Auto-detection system
- Preview-before-publish workflow
- Progress tracking
- Content validation

### Hub v2.0 (v1.21-v1.24)
- Auto-discovery engine
- 3-layer UI
- Progressive disclosure
- Zero-maintenance design

### Claude Code Integration (v1.23.1+)
- Complexity scoring
- Hot-reload validators
- Orchestration hooks
- Agent delegation
- Session teleportation

### Dependency Management (v1.24)
- Dependency checking
- Auto-installation with consent
- Batch conversion
- Health monitoring

---

## Statistics by Release

| Version | Commands | Scripts | Tests | Skills | Agents | Documentation |
|---------|----------|---------|-------|--------|--------|-----------------|
| v1.24.0 | 99 | 20+ | 516+ | 21 | 8 | 87% |
| v1.23.1 | 97 | 18 | 516+ | 21 | 8 | 85% |
| v1.23.0 | 92 | 15 | 491 | 21 | 8 | 80% |
| v1.22.0 | 92 | 12 | 369 | 21 | 8 | 75% |
| v1.21.0 | 89 | 8 | 230 | 20 | 8 | 70% |
| v1.20.0 | 85 | 6 | 150 | 18 | 6 | 60% |
| v1.19.0 | 75 | 4 | 100 | 15 | 5 | 50% |
| v1.18.0 | 66 | 2 | 50 | 12 | 4 | 40% |
| v1.17.0 | 60 | 1 | 30 | 10 | 3 | 30% |

---

## Development Insights

### 1. Complexity Scoring Evolution
- v1.17.0: Initial 5-factor algorithm
- v1.20.0: 7-factor algorithm with improved accuracy
- v1.24.0: Validated across 27+ integration test scenarios

### 2. Test Coverage Growth
- v1.18.0: 50 tests
- v1.20.0: 150 tests
- v1.23.0: 491 tests
- v1.24.0: 516+ tests (90%+ coverage)

### 3. Documentation Approach
- v1.21.0: Zero-maintenance via auto-detection
- v1.23.0: Quality automation + link validation
- v1.24.0: Gap analysis + targeted guides (87% complete)

### 4. Agent Coordination
- v1.17.0: Basic delegation
- v1.20.0: Task complexity detection
- v1.24.0: Session teleportation + resilience

### 5. Teaching Workflow
- v1.22.0: Detection + preview workflow
- Impact: 80% time reduction (15 min → 3 min)
- Outcome: Zero production bugs

---

## Key Milestones

**Foundation (v1.1-v1.6)** - Plugin & framework infrastructure
**Expansion (v1.7-v1.16)** - Command breadth & feature diversity
**Intelligence (v1.17-v1.20)** - Complexity awareness & agent delegation
**Quality (v1.21-v1.23)** - Hub discovery, documentation, teaching workflows
**Maturity (v1.24)** - Dependency management, full integration testing

---

## Next Roadmap

### Phase 3 Enhancements (Current)
- Documentation completeness: 87% → 95%
- Feature status matrix
- Complexity algorithm visualizations
- Version history documentation (THIS FILE)

### Planned Features
1. **Help Template System** (v1.21.0) - Standardized help format
2. **Spec Integration** (v1.21.0) - Embedded spec system
3. **Teaching Command Flags** (v1.22.0) - Enhanced teaching support
4. **Advanced Validators** (v1.25.0) - Community ecosystem

### Stretch Goals
- 100% command documentation
- 95%+ test coverage
- Community validator marketplace
- Multi-language support

---

## Resources

- **GitHub:** https://github.com/Data-Wise/craft
- **Documentation:** https://data-wise.github.io/craft/
- **Specifications:** docs/specs/ (6 total)
- **Test Suite:** tests/ (516+ tests)
- **Status Tracking:** .STATUS (detailed history)

---

*Generated: 2026-01-18 | Last Updated: 2026-01-18*
