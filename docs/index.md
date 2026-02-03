# Craft Plugin

[![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml)
[![Documentation Quality](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml)
[![Documentation](https://img.shields.io/badge/docs-98%25%20complete-brightgreen.svg)](https://data-wise.github.io/craft/)

> **TL;DR** (30 seconds)
>
> - **What:** Full-stack developer toolkit with 105 commands, 8 AI agents, and 21 auto-triggered skills
> - **Why:** Automate documentation, testing, git workflows, CLAUDE.md management, and site creation with one command
> - **How:** Install via `claude plugin install craft@local-plugins`
> - **Next:** Run `/craft:do "your task"` and let AI route to the best workflow

> Full-stack developer toolkit for Claude Code - 105 commands, 8 agents, 21 skills with smart orchestration and ADHD-friendly workflows
>
> **NEW in v2.10.0-dev:** Claude-MD command suite (5 commands), 81 comprehensive tests, 3,304 lines of documentation. Performance: 166x faster than targets. See [what's new](#whats-new-in-v2100-dev)

## Features

<div class="grid cards" markdown>

- :rocket:{ .lg .middle } **105 Commands**

    Smart commands, docs, site management, CLAUDE.md maintenance, code, testing, git, CI, architecture, distribution, planning, and workflow automation (brainstorming, task management, spec capture) - all in one toolkit

- :brain:{ .lg .middle } **8 Specialized Agents**

    Backend architect, docs architect, mermaid expert, API documenter, tutorial engineer, demo engineer, reference builder, and orchestrators

- :sparkles:{ .lg .middle } **21 Skills**

    Auto-triggered expertise for backend/frontend design, DevOps, testing, architecture, planning, distribution, and documentation automation

- :zap:{ .lg .middle } **Smart Orchestration**

    Enhanced orchestrator v2.1 with mode-aware execution, subagent monitoring, and timeline tracking

- :art:{ .lg .middle } **8 ADHD-Friendly Presets**

    Documentation site designs optimized for focus, calm, and quick comprehension

- :books:{ .lg .middle } **Documentation Excellence**

    98% complete documentation with comprehensive guides, 17 Mermaid diagrams, complete version history, smart doc generation (16→13 commands), TL;DR boxes, time estimates, mermaid validation

</div>

## Quick Start

```bash
# Install via Claude Code
claude plugin install craft@local-plugins

# Or create symlink
ln -s ~/projects/dev-tools/claude-plugins/craft ~/.claude/plugins/craft
```

**First command:**

```bash
/craft:do "add user authentication"
```

The universal `/craft:do` command routes your task to the best workflow automatically.

!!! success "Quick Win: Try It Now"
    Run `/craft:hub` to see all 97 commands organized by category - takes 5 seconds and shows everything craft can do.

## API Reference - NEW in v1.24.0

Complete OpenAPI-style documentation for all 97 Craft commands:

<div class="grid cards" markdown>

- :scroll:{ .lg .middle } **[API Reference - Commands](API-REFERENCE-COMMANDS.md)**

    Complete documentation for all 97 commands organized by category with parameters, usage examples, and output formats

- :gear:{ .lg .middle } **[Command Parameters](reference/COMMAND-PARAMETERS.md)**

    Detailed parameter reference, types, defaults, aliases, and environment variables for every command

- :warning:{ .lg .middle } **[Error Scenarios & Recovery](reference/ERROR-SCENARIOS.md)**

    Comprehensive error handling guide with 50+ error scenarios, codes, causes, and recovery steps

- :bulb:{ .lg .middle } **[Command Examples](reference/COMMAND-EXAMPLES.md)**

    Real-world usage patterns, workflows, and practical examples for all command categories

</div>

**Quick Links:**

- [All 97 Commands with Full Documentation](API-REFERENCE-COMMANDS.md)
- [Parameters Quick Reference](reference/COMMAND-PARAMETERS.md)
- [Error Recovery Guide](reference/ERROR-SCENARIOS.md)
- [Real-World Examples](reference/COMMAND-EXAMPLES.md)

## What's New in v2.9.0

**Command Behavior Enhancements** 🚀

Major interactive workflow improvements and comprehensive test infrastructure fixes:

- **"Show Steps First" Pattern**: 4 most-used commands now preview execution plan before running
  - `/craft:orchestrate` - Mode selection, plan confirmation, wave checkpoints
  - `/craft:check` - Step preview with mode-specific check lists
  - `/craft:docs:update` - `--post-merge` flag with 5-phase safe pipeline
  - `/craft:git:worktree` - Scope detection, auto-creates ORCHESTRATE/SPEC files

- **Interactive Orchestration**:
  - Mode selection via `AskUserQuestion` when mode not specified
  - Plan confirmation shows task analysis before spawning agents
  - Wave checkpoints pause between agent groups for review
  - Decision points with structured prompts for design choices

- **Git Worktree Auto-Setup**:
  - Automatically detects scope from branch patterns (fix/*→ feature/* → v* → multi-phase)
  - Auto-creates workflow files (ORCHESTRATE, SPEC, .STATUS, CLAUDE.md) based on scope

- **CI Test Infrastructure**:
  - Fixed 15 failing tests (hardcoded paths, pre-commit hooks, config validation, dependencies)
  - Updated orchestrator-v2 for Claude Code subagent constraints
  - 145 new tests (93 e2e + 52 orch handler)
  - **Total: 847 tests passing** (was 832)

**Documentation**: 3 new guides (guide, tutorial, reference - 650+ lines total)

**Release**: [v2.9.0 on GitHub](https://github.com/Data-Wise/craft/releases/tag/v2.9.0)

---

## What's New in v2.10.0-dev

**Claude-MD Command Suite** 🚀 (In Development)

Comprehensive CLAUDE.md management tools ported from local Claude Code (PR #39):

**5 New Commands:**

- `/craft:docs:claude-md:update` - Sync CLAUDE.md with project state
  - Detects version mismatches, new commands, test count changes
  - "Show Steps First" pattern with preview and confirmation
  - Supports dry-run, interactive, and section-specific modes
- `/craft:docs:claude-md:audit` - Validate completeness and accuracy
  - 5 validation checks: version sync, command coverage, broken links, required sections, status sync
  - 3 severity levels: ERROR, WARNING, INFO
- `/craft:docs:claude-md:fix` - Auto-fix common issues
  - 4 fix methods with dry-run support
- `/craft:docs:claude-md:scaffold` - Create from template
  - 3 project templates: craft-plugin, teaching-site, r-package
  - 18+ template variables with auto-population
- `/craft:docs:claude-md:edit` - Interactive section editing

**Implementation:**

- **7 utility modules** (2,713 lines Python)
  - Project type detection (6 types)
  - Validation (5 checks)
  - Auto-fix (4 methods)
  - Template population (18+ variables)
- **3 project templates**
- **81 comprehensive tests** (100% passing, 0.024s)
- **3,304 lines of documentation**

**Performance:**

- Full detection: **0.003s** (166x faster than 0.5s target)
- Command scanning: **0.002s** (50x faster than 0.1s target)
- Version extraction: **0.001s** per 100 calls (100x faster)
- Thread-safe concurrent detection verified (10 parallel threads)

**Test Enhancements:**

- Concurrent detection testing
- Symlink handling with fallback
- Performance benchmarking with targets

**Try it:**

```bash
/craft:docs:claude-md:update                # Sync CLAUDE.md
/craft:docs:claude-md:audit                 # Validate
/craft:docs:claude-md:fix --dry-run         # Preview fixes
/craft:docs:claude-md:scaffold              # Create new
```

**Documentation:**

- [Command Reference](commands/docs/claude-md.md)
- [Quick Reference Card](reference/REFCARD-CLAUDE-MD.md)
- [Tutorial Guide](tutorials/claude-md-workflows.md)

---

## What's New in v2.8.1

**Markdown Lint Style Fixes** 🎨

Comprehensive cleanup of markdown formatting across the codebase:

- **Auto-Fixed 191 Files**: Applied markdownlint-cli2 --fix
  - MD031: Blank lines around fenced code blocks
  - MD032: Blank lines around lists
  - MD034: Bare URLs wrapped with angle brackets
  - MD003: Setext headings converted to ATX style

- **MD025 Fixes (Duplicate H1 Headings)**:
  - Fixed 6 files with multiple top-level headings
  - Added `front_matter_title` config to ignore YAML titles

- **MD060 Fixes (Table Alignment)**:
  - Formatted tables in CLAUDE.md, README.md, commands/do.md
  - Created emoji-aware table formatter for proper padding

**Testing**: All 770+ tests passing (100%)

**Release**: [v2.8.1 on GitHub](https://github.com/Data-Wise/craft/releases/tag/v2.8.1)

---

## What's New in v2.8.0

**Markdown Linting Execution Layer** ✨

Implementation of the execution layer for `/craft:docs:lint` (PR #34):

- **`scripts/docs-lint.sh`**: Bash execution script for markdown linting
- **MVP Features**: Basic linting (30+ rules), auto-fix, path targeting, pre-commit integration

**Documentation**: [RELEASE-v2.8.0.md](RELEASE-v2.8.0.md) for comprehensive details

---

## What's New in v2.7.0

**Interactive Documentation Update System** 🎯

Smart documentation maintenance with 9-category detection and interactive prompts (PR #32):

- **9-category detection**: Version refs, command counts, broken links, stale examples, missing help, outdated status, inconsistent terminology, missing cross-references, outdated diagrams
- **Interactive prompts**: Category-level approval with AskUserQuestion integration
- **Real issues found**: 1,331 documentation problems detected across the project
- **Production-ready error handling**: 22 tests for corrupted files, unicode, edge cases
- **Comprehensive testing**: 29/29 tests passing (7 integration + 22 error handling)
- **Dry-run preview**: See what would change before applying updates
- **Category-specific mode**: Update only specific categories with `--category=NAME`

**Key Utilities:**

- `utils/docs_detector.py` (690 lines) - 9-category detection system
- `utils/help_file_validator.py` (457 lines) - 8-type help validation
- Production-ready error handling (handles binary files, unicode, corrupted data)

**Try it:**

```bash
/craft:docs:update --interactive              # Category-level prompts
/craft:docs:update --interactive --dry-run    # Preview without changes
/craft:docs:update --category=version_refs    # Update only version references
/craft:docs:update --auto-yes                 # Batch mode (no prompts)
```

**Documentation:**

- [Interactive Docs Update Tutorial](tutorials/interactive-docs-update-tutorial.md) - Step-by-step guide
- [Docs Update Reference Card](reference/REFCARD-DOCS-UPDATE.md) - Quick reference
- [Interactive Example](examples/docs-update-interactive-example.md) - Real-world walkthrough

## What's New in v2.5.1

**User Experience Enhancements for --orch Flag**

Enhanced orchestration with better prompts, error handling, and guidance (PR #28):

- **Interactive mode prompt**: Smart prompt with fallback behavior
- **Graceful error handling**: Proper error flow and recovery
- **Mode recommendations**: Based on complexity (0-10 scale)
- **Test coverage**: 15 new tests, 100% coverage

**Try it:** `/craft:do "task" --orch` for interactive mode selection

**Documentation:** [--orch Flag Usage Guide](guide/orch-flag-usage.md)

## What's New in v1.24.0

**Hub v2.0 - Zero-Maintenance Command Discovery** 🚀

Smart command discovery with 3-layer progressive disclosure (PR #17, #20):

- **Auto-detection engine**: Scans filesystem for commands, zero manual maintenance (680 lines)
- **3-layer navigation**: Main Menu → Category View (16 categories) → Command Detail + Tutorial
- **Performance**: 94% faster than target (12ms uncached, <2ms cached vs 200ms/10ms targets)
- **Test coverage**: 52 comprehensive tests (98% coverage), all passing in ~1 second
- **Pure Python**: Custom YAML parser, no external dependencies
- **Always accurate**: Auto-updates when commands added/changed

**Try it:**

```bash
/craft:hub              # Browse all 97 commands by category
/craft:hub code         # View code category (12 commands)
/craft:hub code:lint    # Get detailed tutorial for code:lint
```

**Enhanced testing** (PR #20):

- 18 new tests: YAML edge cases (12) + E2E workflows (6)
- Unified test runner (`tests/run_hub_tests.sh`)
- Coverage: 95% → 98%

See [Hub v2.0 Architecture](architecture/HUB-V2-ARCHITECTURE.md) for implementation details.

## What's New in v1.23.0

**Documentation Link Validation Enhancement** 🎉

`.linkcheck-ignore` parser system eliminates CI noise from expected broken links:

- **100% reduction in CI false positives** (30 expected links → 0 failures)
- **Smart categorization**: Critical vs Expected broken links
- **Parser utility**: `utils/linkcheck_ignore_parser.py` with glob pattern support
- **Enhanced commands**: `/craft:docs:check-links` and `/craft:docs:check` now categorize output
- **Zero manual filtering**: Expected links documented, auto-ignored
- **CI-friendly**: Exit code 0 for expected links, 1 for critical only

**Create `.linkcheck-ignore` to document expected broken links:**

```markdown
# Known Broken Links

### Test Files
File: `docs/test-violations.md`
- Purpose: Test data for validation

### Brainstorm References
Files: `docs/specs/*.md`
Targets: `docs/brainstorm/*.md`
- Reason: Gitignored, not published
```

**Testing**: 21/21 tests passing (13 unit + 8 integration), backward compatible (opt-in)

See [commands/docs documentation](commands/docs.md#craftdocscheck-links) for details.

---

## What's New in v1.20.0

**Standardized Dry-Run Feature** 🎉 TARGET EXCEEDED

27 commands now support `--dry-run` / `-n` preview mode (57% of target commands):

- **Phase 1** ✅: Git infrastructure (4 commands) - `git:clean`, `git:worktree`, `git:branch`, `git:sync`
- **Phase 2** ✅: CI/Site/Docs (9 commands) - `ci:detect`, `ci:validate`, `site:check`, `site:update`, `docs:sync`, and more
- **Phase 3** ✅: Smart routing + Code/Test (10 commands) - `do`, `orchestrate`, `check`, `code:lint`, `test:run`, and more
- **Coverage**: All CRITICAL, HIGH, P0, and Smart Routing priorities complete (100%)
- **Infrastructure**: Shared utilities (`utils/dry_run_output.py`), templates, 30 passing tests

**Preview before executing:**

```bash
/craft:git:clean --dry-run      # Preview branch cleanup
/craft:code:lint release -n     # Preview comprehensive linting
/craft:do "add auth" --dry-run  # Preview smart routing plan
```

See [DRY-RUN-SUMMARY.md](https://github.com/Data-Wise/craft/blob/dev/DRY-RUN-SUMMARY.md) for complete command list.

## What's New in v1.19.0

**Git Repository Initialization** ⭐

The `/craft:git:init` command bootstraps repositories with craft workflow patterns:

- **Interactive 9-step wizard**: Repository check, remote setup, branch structure, protection, CI, files, commit, push, validation
- **3 workflow patterns**: Main+Dev (collaborative), Simple (solo), GitFlow (complex releases)
- **Template system**: .STATUS, CLAUDE.md, PR template with smart placeholder replacement
- **GitHub integration**: Create repos, enable branch protection, generate CI workflows
- **Rollback on error**: Transaction-based operations with automatic cleanup
- **Dry-run mode**: Preview all changes before executing

See the [git:init reference](commands/git-init-reference.md), [architecture guide](architecture/git-init-flow.md), and [tutorial](guide/git-init-tutorial.md).

## What's New in v1.17.0

**Workflow Automation Integration** ⭐ NEW

Integrated 12 ADHD-friendly workflow commands from the standalone workflow plugin:

- **Brainstorming**: `/brainstorm` with smart delegation and mode detection
- **Task Management**: `/focus`, `/next`, `/done`, `/recap` for ADHD-friendly workflows
- **Getting Unstuck**: `/stuck` with guided problem solving
- **Background Tasks**: `/task-status`, `/task-output`, `/task-cancel` for monitoring
- **Documentation**: `/adhd-guide` for workflow best practices

All workflow commands work identically to the standalone plugin.

**Migration**: Users of the standalone `workflow` plugin can migrate seamlessly with `scripts/migrate-from-workflow.sh`

## What's New in v1.15.0

**ADHD-Friendly Website Enhancement**

New `/craft:docs:website` command with ADHD scoring algorithm (0-100) across 5 categories:

- Visual Hierarchy (25%): TL;DR boxes, emojis, heading structure
- Time Estimates (20%): Tutorial duration info
- Workflow Diagrams (20%): Mermaid diagrams without errors
- Mobile Responsive (15%): Overflow fixes, touch targets
- Content Density (20%): Paragraph length, callout boxes

3-phase enhancement: Quick Wins (<2h), Structure (<4h), Polish (<8h)

## Popular Workflows

<div class="grid cards" markdown>

- :memo:{ .lg .middle } **Documentation Automation**

    Update all docs from code changes in one command

    → [Learn more](workflows/index.md#documentation-workflow)

- :globe_with_meridians:{ .lg .middle } **Site Creation**

    Zero to deployed docs site in < 5 minutes

    → [Learn more](workflows/index.md#site-creation-workflow)

- :rocket:{ .lg .middle } **Release Management**

    Pre-release checks to published in one flow

    → [Learn more](workflows/index.md#release-workflow)

- :computer:{ .lg .middle } **Development Workflow**

    Feature branches with git worktrees

    → [Learn more](workflows/index.md#development-workflow)

</div>

## Documentation

<div class="grid cards" markdown>

- :rocket:{ .lg .middle } **[Quick Start](QUICK-START.md)**

    Get running in 30 seconds

- :brain:{ .lg .middle } **[ADHD Guide](ADHD-QUICK-START.md)**

    Under 2 minutes, zero cognitive load

- :bar_chart:{ .lg .middle } **[Visual Workflows](workflows/index.md)**

    5 diagrams showing complete flows

- :books:{ .lg .middle } **[Commands Overview](commands/overview.md)**

    All 97 commands organized

- :sparkles:{ .lg .middle } **[Skills & Agents](guide/skills-agents.md)**

    Understanding the AI system

- :page_facing_up:{ .lg .middle } **[Quick Reference](REFCARD.md)**

    Command cheat sheet

- :scroll:{ .lg .middle } **[API Reference](API-REFERENCE-COMMANDS.md)** ⭐ NEW

    Complete documentation for all 97 commands

</div>

## Key Command Categories

| Category           | Count  | Description                                                                                                               |
| ------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| **Smart**          | 4      | Universal command, orchestrator, checks, help, hub                                                                        |
| **Documentation**  | 19     | Smart docs with update, sync, check, website, API, changelog, guides, tutorial, workflow                                  |
| **Site**           | 16     | Full site wizard with 8 ADHD-friendly presets, theme, nav, audit                                                          |
| **Code & Testing** | 12 + 7 | Code: linting, testing, debugging, refactoring, CI fixes, deps management; Tests: run, debug, watch, coverage, generation |
| **Git**            | 11     | Repository initialization, branch management, worktrees, sync, recap, clean, learning guides                              |
| **CI**             | 3      | Detection, generation, validation                                                                                         |
| **Architecture**   | 4      | Analysis, diagrams, planning, reviews                                                                                     |
| **Distribution**   | 3      | Homebrew, PyPI, curl installers                                                                                           |
| **Planning**       | 3      | Feature planning, sprints, roadmaps                                                                                       |
| **Workflow**       | 12     | Brainstorming, task management, spec capture, getting unstuck                                                             |
| **Total**          | **97** | **Complete development workflow coverage**                                                                                |

## Links

- [GitHub Repository](https://github.com/Data-Wise/claude-plugins)
- [Issue Tracker](https://github.com/Data-Wise/claude-plugins/issues)
- [ROADMAP](https://github.com/Data-Wise/claude-plugins/blob/main/craft/ROADMAP.md)
