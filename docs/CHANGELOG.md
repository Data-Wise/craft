# Changelog

All notable changes to the Craft plugin are documented here.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [2.23.0] - 2026-02-19: Extended Version Sync & Test Suite

### Added

- **bump-version.sh:** Extended from 9 to 11 files — now covers `docs/DEPENDENCY-ARCHITECTURE.md`, `docs/reference/configuration.md`, REFCARD box interior lines, and `docs/index.md` info box
- **test_bump_version.sh:** Comprehensive 45-test bash test suite with sandbox isolation (CLI args, dry-run, verify, per-file integration tests)
- **Release skill Step 3b:** Semantic doc updates for CHANGELOG, VERSION-HISTORY, README title, index.md info box, and REFCARD summary line

### Changed

- `FILE_COUNT` variable replaces hardcoded file count in configuration.md handler
- `.gitignore` no longer ignores `ORCHESTRATE-*.md` files (they should be tracked on feature branches)

---

## [2.22.2] - 2026-02-19: Bump-Version Feature & Documentation Overhaul

### Added

- **bump-version.sh:** Automated version bumping across all 11 project files with `--dry-run`, `--verify`, and `--counts-only` modes
- **CI status dashboard:** New command page and reference card for cross-repo CI monitoring

### Fixed

- CLAUDE.md stale ORCHESTRATE reference removed, spec/test counts corrected
- Stale doc pages fixed (config, dependency arch, choose-path, doc-quality)

### Changed

- Archived implemented spec, removed stale brainstorm
- Updated REFCARD, A-Z reference, and CHANGELOG with new features
- Rebuilt skills-agents pages with correct version/count refs

---

## [2.22.1] - 2026-02-19: Documentation Overhaul & Test Fixes

### Fixed

- **Dogfood test assertions:** Branch guard verbosity levels (full/brief/minimal) caused test failures in full suite — accept either "BRANCH GUARD" or "[CONFIRM]" format
- **Tutorials index:** Rebuilt from 1 listed tutorial to all 23, organized by category
- **REFCARD.md tables:** Expanded tutorials table (5→15) and refcards table (5→14)
- **Stale footers:** Fixed version labels in claude-md-workflows.md, pipeline-orchestrate-guide.md, insights guide
- **mkdocs nav:** Added REFCARD-CHECK and REFCARD-INSIGHTS to navigation
- **QUICK-START.md:** Fixed worktree command syntax (`add`→`create`)
- **REFCARD.md command count:** Code & Testing 17→14 (accurate)

### Added

- **bump-version.sh:** Atomic version + count sync across all 11 project files — prevents version drift between releases
- **bump-version-helper.py:** Python helper for JSON file updates (plugin.json, marketplace.json, package.json)
- **/craft:ci:status:** Cross-repo CI status dashboard — see all workflow statuses in one view with `--json` and `--repo` filters
- **REFCARD-BUMP-VERSION.md:** Quick reference card for bump-version.sh
- **docs/commands/ci/status.md:** Command help page for /craft:ci:status
- **Version sync Layer 4:** Added atomic version bump documentation to architecture/version-sync.md
- **REFCARD-INSIGHTS.md:** New consolidated quick-reference for insights, friction prevention, and version sync
- **CLAUDE.md layered architecture:** Expanded REFCARD-CLAUDE-MD with per-layer token budget, loading triggers, budget enforcement

### Changed

- **Release skill (SKILL.md):** Step 3 now uses `bump-version.sh` instead of manual file-by-file edits; Step 8.5 adds Homebrew post-update verification
- **skills-agents.md:** Rebuilt both reference and guide pages from actual filesystem inventory (removed 17 phantom skills, 7 phantom agents)
- **Command count:** 107→108 across 19 documentation files
- **bump-version.sh mkdocs.yml pattern:** Fixed sed to handle drifted versions (not just current→target replacement)

---

## [2.22.0] - 2026-02-19: Unified Test System, CLAUDE.md Refactor & Insights Prevention

### Added (Unified Test System)

### Added

- **Unified test commands:** 7 old commands (`test:run`, `test:watch`, `test:coverage`, `test:debug`, `test:cli-gen`, `test:cli-run`, `test:generate`) consolidated into 3: `/craft:test`, `/craft:test:gen`, `/craft:test:template`
- **Jinja2 template engine:** `utils/test_generator.py` (865 lines) — auto-detects project type (plugin, zsh, cli, mcp) and renders test suites from 27 templates
- **Template registry:** `templates/registry.json` with detection rules, variable schemas, and tier assignments for all 4 project types
- **27 Jinja2 templates:** `templates/` directory covering `_base/` (shared), `plugin/` (7), `zsh/` (5), `cli/` (7), `mcp/` (5) with conftest + helpers
- **Pytest infrastructure:** `pyproject.toml` markers (25 total), `tests/conftest.py` shared fixtures, `tests/helpers.py` shared utilities
- **Advanced testing markers:** `snapshot`, `property`, `contract` markers with optional dependency groups
- **Testing documentation:** REFCARD-TESTING.md, test-architecture.md (3 Mermaid diagrams), test-commands.md, test-migration.md, testing-quickstart.md
- **Cookbook recipes:** "Generate Tests for a Project" and "Run Tests by Category"
- **YAML frontmatter:** Added to 52 command files that were missing metadata

### Changed

- **Command count:** 111 → 107 (removed 7 old test commands, added 3 unified, net -4)
- **All test files:** 66 test files now have module-level `pytestmark` assignments for tier + domain filtering
- **9 test files:** Migrated from `CheckResult` dataclass to native pytest assertions
- **40+ files:** Updated old test command references (`test:run` → `test`, `test:coverage` → `test --coverage`, etc.)
- **mkdocs.yml:** Fixed 3 duplicate nav entries, updated site description to v2.21.0

### Documentation

- [Testing Quick Reference](reference/REFCARD-TESTING.md) · [Test Architecture](guide/test-architecture.md) · [Migration Guide](guide/test-migration.md) · [Testing Quickstart](tutorials/testing-quickstart.md)

---

### Added (Marketplace Distribution)

- **Marketplace distribution:** `/craft:dist:marketplace` command with 4 subcommands (init, validate, test, publish) for Claude Code marketplace listing management
- **marketplace.json:** New `.claude-plugin/marketplace.json` manifest for marketplace distribution with GitHub source object format
- **Release pipeline marketplace steps:** Step 2c (marketplace validation), Step 3 (marketplace version bump), Step 8.5 (Homebrew tap auto-update)
- **Pre-release marketplace check:** `pre-release-check.sh` expanded to 6 checks (added marketplace version consistency)
- **Homebrew auto-detection:** Claude Code Plugin added as highest-priority entry in auto-detect table
- **115 marketplace tests:** 57 CLI tests, 30 e2e tests, 28 dogfood tests (all passing)
- **Documentation:** Marketplace distribution guide, updated dist commands reference, release workflow updates

### Changed (Marketplace Distribution)

- **Command count:** 108 → 109 (added dist:marketplace)
- **Install hierarchy:** README and docs now recommend Marketplace as Option 1 (Recommended), Homebrew as Option 2
- **Distribution commands:** 3 → 4 (added marketplace)

**Documentation:** [Marketplace Guide](guide/marketplace-distribution.md) · [Distribution Commands](commands/dist.md) · [Release Reference](reference/REFCARD-RELEASE.md)

---

## [2.16.0] - 2026-02-07: Teaching Ecosystem + Branch Protection

### Added

- **Branch protection hooks:** `scripts/branch-guard.sh` — PreToolUse hook that prevents edits on protected branches (main=block-all, dev=block-new-code)
- **New commands:** `/craft:git:protect` (re-enable protection) and `/craft:git:unprotect` (temporary bypass via marker file)
- **Standalone installer:** `scripts/install-branch-guard.sh` — works outside Craft plugin
- **138 branch guard tests:** 49 unit + 31 e2e + 6 integration + 52 dogfooding (jq-based JSON parsing with Python/grep fallback)
- **Config normalizer:** `_normalize_config()` in `commands/utils/teach_config.py` — adapter that maps flow-cli schema (`semester_info`, `course.name`, `branches`) to Craft-native format
- **Single-day break support:** Break validation now accepts `start == end` for holidays like MLK Day
- **8 normalization tests** in `tests/test_integration_teaching_workflow.py` (all passing)
- **Teaching tab:** Dedicated top-level "Teaching" tab in documentation site nav (`docs/teaching/index.md`)
- **Ecosystem spec:** `docs/specs/SPEC-teaching-ecosystem-coordination-2026-02-06.md`

### Changed

- **Command count:** 106 → 108 (added protect + unprotect)
- **Test count:** 1294 → 1432 (+138 branch guard tests)
- **Craft command enhancements:** `/craft:check` shows guard status, `/craft:do` respects protection, `/craft:git:worktree` validates branch, `/craft:git:status` shows protection level
- **Teaching config schema docs:** Added flow-cli compatibility section, single-day break docs, field mapping table
- **Teaching tutorial:** Added flow-cli note, single-day break example, ecosystem links
- **Teaching workflow guide:** Added ecosystem section with role boundaries and decision guide
- **Site navigation:** Restructured mkdocs.yml with dedicated Teaching tab (was buried in Guides)

### Fixed

- **Broken test import:** `test_integration_teaching_workflow.py` imported non-existent `parse_teach_config` — fixed to `load_teach_config`
- **Break validation:** `>=` → `>` comparison allowing single-day breaks (MLK Day, Veterans Day)

**Documentation:** [Teaching Home](teaching/index.md) · [Config Schema](teaching-config-schema.md) · [Ecosystem Spec](specs/_archive/SPEC-teaching-ecosystem-coordination-2026-02-06.md)

---

## [2.15.0] - 2026-02-06

### Added

- **Context-aware smart questions:** New `utils/brainstorm_context.py` (~280 lines) scans `.STATUS`, specs, git log, and CLAUDE.md to pre-fill brainstorm questions
- **Project-type question extensions:** 12 new questions across 6 project types (R, Python, Node.js, Quarto, Claude Plugin, Teaching)
- **Dynamic questions:** Auto-generated questions based on matching specs, prior brainstorms, and failing tests
- **38 new tests** in `tests/test_brainstorm_context.py` (all passing)
- **Documentation:** Power user tutorial (`docs/tutorials/TUTORIAL-brainstorm-power-user.md`), brainstorm reference card (`docs/reference/REFCARD-BRAINSTORM.md`), question bank spec (`docs/specs/_archive/SPEC-brainstorm-question-bank.md`)

### Changed

- **Brainstorm spec simplified:** `commands/workflow/brainstorm.md` reduced from 1,919 → 312 lines (84% reduction)
- **Version history updated:** Brainstorm evolution table added to `docs/VERSION-HISTORY.md`
- Total tests: 1248 → 1286

**Documentation:** [Power User Guide](tutorials/TUTORIAL-brainstorm-power-user.md) · [Quick Reference](reference/REFCARD-BRAINSTORM.md) · [Question Bank](specs/_archive/SPEC-brainstorm-question-bank.md)

---

## [2.14.0] - 2026-02-05

### Added

- **Formatting library:** `scripts/formatting.sh` — unified box-drawing, `FMT_` color constants, ANSI-aware padding, source guard
- **Box-drawing API:** `box_header`, `box_single`, `box_row`, `box_separator`, `box_footer`, `box_empty_row`, `box_table`
- **Utility functions:** `fmt_set_width`, `fmt_divider`, `_fmt_strip_ansi`, `_fmt_visible_len`
- **74 tests:** 28 unit + 30 integration + 16 edge cases in `tests/test_formatting.sh`
- **Documentation:** Guide (`docs/guide/bash-formatting-library.md`), tutorial (`docs/tutorials/TUTORIAL-formatting-migration.md`), reference card (`docs/reference/REFCARD-FORMATTING.md`)

### Changed

- **8 scripts migrated to box-drawing:** install.sh, migrate-from-workflow.sh, convert-cast.sh, health-check.sh, consent-prompt.sh, dependency-installer.sh, dependency-manager.sh
- **15 scripts migrated to shared colors:** validate-counts.sh, pre-release-check.sh, batch-convert.sh, repair-tools.sh, 3 installers, tool-detector.sh, version-check.sh, sync-version.sh, verify-phase1/2.sh, install-hooks.sh, test-fix-flag.sh, pre-commit-markdownlint hook
- **Box width standardized:** All boxes now render at exactly 63 visible characters (previously 61-63 inconsistently)

**Documentation:** [Guide](guide/bash-formatting-library.md) · [Quick Reference](reference/REFCARD-FORMATTING.md) · [Migration Tutorial](tutorials/TUTORIAL-formatting-migration.md)

---

## [2.13.1] - 2026-02-05

### Fixed

- **Plugin loading:** Moved `claude_md_budget` from `plugin.json` to `.claude-plugin/config.json` — Claude Code's strict schema rejects unrecognized keys, silently breaking plugin loading ([#20415](https://github.com/anthropics/claude-code/issues/20415))
- **Budget utilities:** Updated `claude_md_optimizer.py`, `claude_md_sync.py`, and `claude-md-budget-check.sh` to read budget from `config.json` instead of `plugin.json`
- **Homebrew formula:** Added dual-protection JSON cleanup in `post_install` (Ruby allowlist + Python fallback) to strip unrecognized keys from immutable v2.13.0 tarball

### Changed

- Budget config fallback chain: `.claude-plugin/config.json` → `package.json` (`claudeMd.budget`) → default 150
- Updated docs, sync command, conventions, and troubleshooting to reference `config.json`

---

## [2.13.0] - 2026-02-05

### Documentation Gap-Fill & Release Automation

- 30 new documentation pages (PR #47)
- Documentation status: 98% → 99%
- Pre-release validation script (`scripts/pre-release-check.sh`)
- CI version-tag consistency check
- Dynamic formula metadata in homebrew-release workflow

---

## [2.12.0] - 2026-02-05

### CLAUDE.md v3 Command Refactoring

**PR #45** — 5 commands consolidated to 3 lean commands with budget enforcement and pointer architecture.

**Commands (3 — replaces 5):**

- `/craft:docs:claude-md:init` — Create from lean template (< 150 lines), replaces `scaffold`
- `/craft:docs:claude-md:sync` — 4-phase pipeline (detect → audit → fix → optimize), replaces `update`, `audit`, `fix`
- `/craft:docs:claude-md:edit` — Interactive editing with `--global` support

**Key Changes:**

- Budget enforcement: < 150 line target for new CLAUDE.md files
- Pointer architecture: reference detail files instead of duplicating content
- 4-phase sync pipeline with `--fix` and `--optimize` flags
- Deprecation aliases for old commands (available until v2.13.0)
- New utilities: `claude_md_common.py`, `claude_md_sync.py`, `claude_md_optimizer.py`
- Pre-commit budget check script

**Documentation:** [Command Reference](commands/docs/claude-md.md) · [Quick Reference](reference/REFCARD-CLAUDE-MD.md) · [Tutorial](tutorials/claude-md-workflows.md)

---

## [2.11.0] - 2026-02-03

### Test Suite Cleanup & CRAFT-001

- Eliminated all **236 pytest warnings** across 13 test files using `_check_*` + `test_*` wrapper pattern
- Fixed **21 hidden test failures** that were silently passing
- Added **CRAFT-001** emoji-attribute spacing lint rule with CI integration
- **50 new tests** for CRAFT-001 across 9 categories
- Test count: **847 → 1111 → 1171** (all passing, 0 warnings)

**Documentation:** [CRAFT-001 Tutorial](tutorials/TUTORIAL-craft-001-emoji-spacing.md) · [Test Wrapper Pattern Guide](guide/test-wrapper-pattern.md)

**Release:** [v2.11.0 on GitHub](https://github.com/Data-Wise/craft/releases/tag/v2.11.0)

---

## [2.10.0] - 2026-01-30

### Claude-MD Command Suite

Comprehensive CLAUDE.md management tools ported from local Claude Code (PR #39).

**Commands (5 new):**

- `/craft:docs:claude-md:update` — Sync CLAUDE.md with project state
- `/craft:docs:claude-md:audit` — Validate completeness and accuracy (5 checks, 3 severity levels)
- `/craft:docs:claude-md:fix` — Auto-fix common issues (4 fix methods)
- `/craft:docs:claude-md:scaffold` — Create from template (3 project types)
- `/craft:docs:claude-md:edit` — Interactive section editing

**Implementation:** 7 utility modules (2,713 lines Python), 3 project templates, 81 tests (100% passing, 0.024s), 3,304 lines documentation.

**Performance:**

- Full detection: **0.003s** (166x faster than 0.5s target)
- Command scanning: **0.002s** (50x faster than 0.1s target)
- Thread-safe concurrent detection verified (10 parallel threads)

**Release:** [v2.10.0 on GitHub](https://github.com/Data-Wise/craft/releases/tag/v2.10.0)

---

## [2.9.0] - 2026-01-29

### Command Behavior Enhancements

Major interactive workflow improvements and comprehensive test infrastructure fixes.

- **"Show Steps First" Pattern**: 4 most-used commands now preview execution plan before running
  - `/craft:orchestrate` — Mode selection, plan confirmation, wave checkpoints
  - `/craft:check` — Step preview with mode-specific check lists
  - `/craft:docs:update` — `--post-merge` flag with 5-phase safe pipeline
  - `/craft:git:worktree` — Scope detection, auto-creates ORCHESTRATE/SPEC files
- **Interactive Orchestration**: Mode selection via `AskUserQuestion`, wave checkpoints, decision points
- **Git Worktree Auto-Setup**: Detects scope from branch patterns, auto-creates workflow files
- **CI Test Infrastructure**: Fixed 15 failing tests, 145 new tests (93 e2e + 52 orch handler)
- **Total: 1171 tests passing** (was 847)

**Documentation:** 3 new guides (650+ lines total) · [Release on GitHub](https://github.com/Data-Wise/craft/releases/tag/v2.9.0)

---

## [2.8.1] - 2026-01-28

### Markdown Lint Style Fixes

Comprehensive cleanup of markdown formatting across 191 files.

- **Auto-Fixed**: MD031 (blank lines around code blocks), MD032 (blank lines around lists), MD034 (bare URLs), MD003 (setext → atx headings)
- **MD025 Fixes**: 6 files with duplicate H1 headings, added `front_matter_title` config
- **MD060 Fixes**: Table alignment in CLAUDE.md, README.md, commands/do.md

**Release:** [v2.8.1 on GitHub](https://github.com/Data-Wise/craft/releases/tag/v2.8.1)

---

## [2.8.0] - 2026-01-28

### Markdown Linting Execution Layer

Implementation of the execution layer for `/craft:docs:lint` (PR #34).

- `scripts/docs-lint.sh`: Bash execution script for markdown linting
- MVP features: Basic linting (30+ rules), auto-fix, path targeting, pre-commit integration

**Documentation:** [RELEASE-v2.8.0.md](RELEASE-v2.8.0.md)

---

## [2.7.0] - 2026-01-22

### Interactive Documentation Update System

Smart documentation maintenance with 9-category detection and interactive prompts (PR #32).

- **9-category detection**: Version refs, command counts, broken links, stale examples, missing help, outdated status, inconsistent terminology, missing cross-references, outdated diagrams
- **Interactive prompts**: Category-level approval with AskUserQuestion integration
- **Real issues found**: 1,331 documentation problems detected across the project
- **Production-ready error handling**: 22 tests for corrupted files, unicode, edge cases
- **29/29 tests passing** (7 integration + 22 error handling)

```bash
/craft:docs:update --interactive              # Category-level prompts
/craft:docs:update --interactive --dry-run    # Preview without changes
/craft:docs:update --category=version_refs    # Update only version references
```

**Documentation:** [Tutorial](tutorials/interactive-docs-update-tutorial.md) · [Reference Card](reference/REFCARD-DOCS-UPDATE.md)

---

## [2.5.1] - 2026-01-20

### UX Enhancements for --orch Flag

Enhanced orchestration with better prompts, error handling, and guidance (PR #28).

- Interactive mode prompt with fallback behavior
- Mode recommendations based on complexity (0-10 scale)
- 15 new tests, 100% coverage

**Documentation:** [--orch Flag Usage Guide](guide/orch-flag-usage.md)

---

## [2.5.0] - 2026-01-19

### Markdownlint List Spacing Enforcement

Strict enforcement of list formatting rules (MD030, MD004, MD032) for consistent rendering.

- 78 comprehensive tests (21 unit + 42 validation + 15 e2e)
- Pre-commit hook for staged `.md` files
- Baseline report: 6,398 violations cataloged for gradual migration

---

## [1.24.0] - 2026-01-18

### Hub v2.0 — Zero-Maintenance Command Discovery

Smart command discovery with 3-layer progressive disclosure (PR #17, #20).

- **Auto-detection engine**: Scans filesystem for commands, zero manual maintenance (680 lines)
- **3-layer navigation**: Main Menu → Category View (16 categories) → Command Detail + Tutorial
- **Performance**: 94% faster than target (12ms uncached, <2ms cached vs 200ms/10ms targets)
- **52 comprehensive tests** (98% coverage), all passing in ~1 second

```bash
/craft:hub              # Browse all commands by category
/craft:hub code         # View code category
/craft:hub code:lint    # Get detailed tutorial for code:lint
```

**Architecture:** [Hub v2.0 Architecture](architecture/HUB-V2-ARCHITECTURE.md)

---

## [1.23.0] - 2026-01-17

### Documentation Link Validation Enhancement

`.linkcheck-ignore` parser system eliminates CI noise from expected broken links.

- **100% reduction in CI false positives** (30 expected links → 0 failures)
- Smart categorization: Critical vs Expected broken links
- Parser utility: `utils/linkcheck_ignore_parser.py` with glob pattern support
- 21/21 tests passing (13 unit + 8 integration)

---

## [1.22.0] - 2026-01-17

### Teaching Workflow System

Comprehensive teaching workflow for course website management (PR #12).

- 5 new commands: `site:publish`, `site:progress`, enhanced `git:status`, `site:build`
- Preview-before-publish safety workflow
- Content validation (schedule, syllabus, assignments)
- Semester progress tracking
- 139 tests, 100% passing
- **Time savings:** 80% reduction in publish time (15 min → 3 min)

---

## [1.20.0] - 2026-01-16

### Standardized Dry-Run Feature

27 commands now support `--dry-run` / `-n` preview mode (57% of target commands).

- **Phase 1**: Git infrastructure (4 commands)
- **Phase 2**: CI/Site/Docs (9 commands)
- **Phase 3**: Smart routing + Code/Test (10 commands)
- All CRITICAL, HIGH, P0, and Smart Routing priorities complete (100%)
- Shared utilities (`utils/dry_run_output.py`), 30 passing tests

```bash
/craft:git:clean --dry-run      # Preview branch cleanup
/craft:code:lint release -n     # Preview comprehensive linting
/craft:do "add auth" --dry-run  # Preview smart routing plan
```

---

## [1.19.0] - 2026-01-08

### Git Repository Initialization

`/craft:git:init` command bootstraps repositories with craft workflow patterns.

- Interactive 9-step wizard
- 3 workflow patterns: Main+Dev (collaborative), Simple (solo), GitFlow (complex releases)
- Template system (.STATUS, CLAUDE.md, PR templates)
- GitHub integration (create repos, branch protection, CI workflows)
- Rollback on error, dry-run mode

---

## [1.17.0] - 2025-12

### Workflow Automation Integration

Integrated 12 ADHD-friendly workflow commands from standalone workflow plugin.

- `/brainstorm` — Smart brainstorming with delegation
- Task management: `/focus`, `/next`, `/done`, `/recap`
- `/stuck` — Guided problem solving
- Background task monitoring

---

## [1.15.0] - 2025-12

### ADHD-Friendly Website Enhancement

`/craft:docs:website` command with ADHD scoring algorithm (0-100) across 5 categories.

- Visual Hierarchy (25%), Time Estimates (20%), Workflow Diagrams (20%), Mobile Responsive (15%), Content Density (20%)
- 3-phase enhancement: Quick Wins (<2h), Structure (<4h), Polish (<8h)

---

## Earlier Versions

See [git history](https://github.com/Data-Wise/craft/commits/main) for versions prior to 1.15.0.

---

## Links

- [Documentation Site](https://data-wise.github.io/craft/)
- [GitHub Repository](https://github.com/Data-Wise/craft)
- [Version History](VERSION-HISTORY.md)
