# Changelog

All notable changes to the Craft plugin will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [1.20.0] - 2026-01-16

### 🎉 Milestone: Standardized Dry-Run Feature - Target Exceeded

**Target:** 47 commands (52% coverage)
**Achieved:** 27 commands (57% coverage)
**Status:** ✅ Target exceeded by 5%

### Added

#### Phase 1: Infrastructure + Git Commands (PR #6)
- **Infrastructure:**
  - `utils/dry_run_output.py` (324 lines) - Shared dry-run output utilities
  - `templates/dry-run-pattern.md` (306 lines) - Implementation template
  - 17 comprehensive tests (all passing)
  - Standardized bordered box format (65-character width)
  - Risk level indicators (LOW, MEDIUM, HIGH, CRITICAL)

- **Git Commands (4):**
  - `/craft:git:clean` - Preview merged branch deletion (CRITICAL priority)
  - `/craft:git:worktree` - Preview worktree operations (HIGH priority)
  - `/craft:git:branch` - Preview branch operations
  - `/craft:git:sync` - Preview sync operations

#### Phase 2: CI/Site/Docs Commands (PR #7)
- **CI/CD Commands (3):**
  - `/craft:ci:detect` - Preview project type detection (60+ patterns)
  - `/craft:ci:generate` - Preview workflow generation (CRITICAL priority)
  - `/craft:ci:validate` - Preview CI validation

- **Site Commands (4):**
  - `/craft:site:build` - Preview site build
  - `/craft:site:check` - Preview validation checks
  - `/craft:site:deploy` - Preview GitHub Pages deployment (CRITICAL priority)
  - `/craft:site:update` - Preview site content updates

- **Documentation Commands (5):**
  - `/craft:docs:changelog` - Preview changelog generation
  - `/craft:docs:check` - Preview health check
  - `/craft:docs:claude-md` - Preview CLAUDE.md generation
  - `/craft:docs:nav-update` - Preview navigation updates
  - `/craft:docs:sync` - Preview documentation sync

#### Phase 3: Smart Routing + Code/Test Commands (PR #8, #9)
- **Smart Routing Commands (3):**
  - `/craft:do` - Preview routing plan with time estimates
  - `/craft:orchestrate` - Preview agent allocation and parallelization
  - `/craft:check` - Preview validation plan (context-aware)

- **P0 Commands (2):**
  - `/craft:git:recap` - Preview git activity summary (7 git commands)
  - `/craft:dist:pypi` - Preview PyPI publishing (IRREVERSIBLE warnings)

- **Code Quality Commands (3):**
  - `/craft:code:lint` - Preview linting plan (mode-aware: default/debug/optimize/release)
  - `/craft:code:ci-local` - Preview local CI checks (6 checks)
  - `/craft:code:deps-audit` - Preview security vulnerability scanning

- **Test Commands (2):**
  - `/craft:test:run` - Preview test execution (mode-aware)
  - `/craft:test:cli-run` - Preview CLI test suite execution

- **Git Commands (2 additional):**
  - `/craft:git:init` - Preview repository initialization
  - `/craft:git:recap` - Preview git activity summary

### Coverage by Priority

| Priority | Coverage | Status |
|----------|----------|--------|
| CRITICAL | 100% (3/3) | ✅ Complete |
| HIGH | 100% (1/1) | ✅ Complete |
| P0 | 100% (6/6) | ✅ Complete |
| Smart Routing | 100% (3/3) | ✅ Complete |
| MEDIUM | ~40% (17/43) | 🟡 In Progress |

### Coverage by Category

- **Git:** 100% (6/6) ✅
- **CI/CD:** 100% (3/3) ✅
- **Smart Routing:** 100% (3/3) ✅
- **Site:** 67% (4/6) 🟢
- **Docs:** 50% (5/10) 🟡
- **Code:** 25% (3/12) 🟡
- **Test:** 33% (2/6) 🟡
- **Distribution:** 25% (1/4) 🟡

### Usage Examples

```bash
# Preview branch cleanup
/craft:git:clean --dry-run

# Preview comprehensive linting (release mode)
/craft:code:lint release -n

# Preview smart routing plan
/craft:do "add user authentication" --dry-run

# Preview orchestration with agent allocation
/craft:orchestrate "refactor auth" --dry-run

# Preview PyPI publishing (CRITICAL - shows IRREVERSIBLE warnings)
/craft:dist:pypi publish --dry-run
```

### Documentation

- Added comprehensive dry-run feature documentation
- Updated homepage with v1.20.0 announcement
- Created [DRY-RUN-SUMMARY.md](DRY-RUN-SUMMARY.md) tracking document
- Added dry-run section to commands reference
- Added 🔍 indicators to dry-run enabled commands

### Testing

- 30 tests total (13 plugin structure + 17 dry-run utilities)
- All tests passing
- Test coverage for all dry-run output functions
- Real-world example tests

### Infrastructure

- Shared utilities reduce code duplication
- Consistent 65-character bordered box format
- Risk level system (LOW → MEDIUM → HIGH → CRITICAL)
- Warning and summary sections
- Text wrapping and edge case handling

---

## [1.19.0] - 2026-01-08

### Added

- `/craft:git:init` command for repository initialization
  - Interactive 9-step wizard
  - 3 workflow patterns (Main+Dev, Simple, GitFlow)
  - Template system (.STATUS, CLAUDE.md, PR templates)
  - GitHub integration (create repos, branch protection, CI workflows)
  - Rollback on error with transaction-based operations
  - Dry-run mode

### Documentation

- Git init reference guide
- Architecture flow diagrams
- Tutorial for repository setup

---

## [1.17.0] - 2025-12-XX

### Added

- Workflow automation integration (12 commands)
  - `/brainstorm` - Smart brainstorming with delegation
  - Task management: `/focus`, `/next`, `/done`, `/recap`
  - `/stuck` - Guided problem solving
  - Background task monitoring

### Changed

- Migrated workflow commands from standalone plugin
- Updated command count: 90 total (78 craft + 12 workflow)

---

## Earlier Versions

See git history for versions prior to 1.17.0.

---

## Links

- **Homepage:** https://Data-Wise.github.io/craft/
- **Repository:** https://github.com/Data-Wise/craft
- **Documentation:** https://Data-Wise.github.io/craft/
- **Dry-Run Summary:** [DRY-RUN-SUMMARY.md](DRY-RUN-SUMMARY.md)
