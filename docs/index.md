# Craft Plugin

[![Craft CI](https://github.com/Data-Wise/claude-plugins/actions/workflows/craft-ci.yml/badge.svg)](https://github.com/Data-Wise/claude-plugins/actions/workflows/craft-ci.yml)
[![Validate Plugins](https://github.com/Data-Wise/claude-plugins/actions/workflows/validate-plugins.yml/badge.svg)](https://github.com/Data-Wise/claude-plugins/actions/workflows/validate-plugins.yml)

> **TL;DR** (30 seconds)
> - **What:** Full-stack developer toolkit with 97 commands, 8 AI agents, and 21 auto-triggered skills
> - **Why:** Automate documentation, testing, git workflows, and site creation with one command
> - **How:** Install via `claude plugin install craft@local-plugins`
> - **Next:** Run `/craft:do "your task"` and let AI route to the best workflow

> Full-stack developer toolkit for Claude Code - 97 commands, 8 agents, 21 skills with smart orchestration and ADHD-friendly workflows
>
> **NEW in v1.24.0 (Unreleased):** Hub v2.0 - Zero-maintenance command discovery with 3-layer progressive disclosure. Auto-detects all commands (94% faster than target). See [what's new](#whats-new-in-v1240-unreleased)

## Features

<div class="grid cards" markdown>

- :rocket: **97 Commands**

    Smart commands, docs, site management, code, testing, git, CI, architecture, distribution, planning, and workflow automation (brainstorming, task management, spec capture) - all in one toolkit

- :brain: **8 Specialized Agents**

    Backend architect, docs architect, mermaid expert, API documenter, tutorial engineer, demo engineer, reference builder, and orchestrators

- :sparkles: **21 Skills**

    Auto-triggered expertise for backend/frontend design, DevOps, testing, architecture, planning, distribution, and documentation automation

- :zap: **Smart Orchestration**

    Enhanced orchestrator v2.1 with mode-aware execution, subagent monitoring, and timeline tracking

- :art: **8 ADHD-Friendly Presets**

    Documentation site designs optimized for focus, calm, and quick comprehension

- :books: **Documentation Excellence**

    Smart doc generation, consolidation (16→13 commands), TL;DR boxes, time estimates, mermaid validation

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

## What's New in v1.23.0 (Unreleased)

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

## What's New in v1.24.0 (Unreleased)

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

- :memo: **Documentation Automation**

    Update all docs from code changes in one command

    → [Learn more](workflows/index.md#documentation-workflow)

- :globe_with_meridians: **Site Creation**

    Zero to deployed docs site in < 5 minutes

    → [Learn more](workflows/index.md#site-creation-workflow)

- :rocket: **Release Management**

    Pre-release checks to published in one flow

    → [Learn more](workflows/index.md#release-workflow)

- :computer: **Development Workflow**

    Feature branches with git worktrees

    → [Learn more](workflows/index.md#development-workflow)

</div>

## Documentation

<div class="grid cards" markdown>

- :rocket: **[Quick Start](QUICK-START.md)**

    Get running in 30 seconds

- :brain: **[ADHD Guide](ADHD-QUICK-START.md)**

    Under 2 minutes, zero cognitive load

- :bar_chart: **[Visual Workflows](workflows/index.md)**

    5 diagrams showing complete flows

- :books: **[Commands Overview](commands/overview.md)**

    All 69 commands organized

- :sparkles: **[Skills & Agents](guide/skills-agents.md)**

    Understanding the AI system

- :page_facing_up: **[Quick Reference](REFCARD.md)**

    Command cheat sheet

</div>

## Key Command Categories

| Category | Count | Description |
|----------|-------|-------------|
| **Smart** | 4 | Universal command, orchestrator, checks, help, hub |
| **Documentation** | 17 | Smart docs with update, sync, check, website, API, changelog, guides |
| **Site** | 15 | Full site wizard with 8 ADHD-friendly presets, theme, nav, audit |
| **Code & Testing** | 17 | Linting, testing, debugging, refactoring, CI fixes, deps management |
| **Git** | 5 | **NEW:** Repository initialization, branch management, worktrees, sync, recap, clean |
| **CI** | 3 | Detection, generation, validation |
| **Architecture** | 4 | Analysis, diagrams, planning, reviews |
| **Distribution** | 3 | Homebrew, PyPI, curl installers |
| **Planning** | 3 | Feature planning, sprints, roadmaps |
| **Workflow** | 12 | Brainstorming, task management, spec capture, getting unstuck |
| **Total** | **90** | **Complete development workflow coverage** |

## Links

- [GitHub Repository](https://github.com/Data-Wise/claude-plugins)
- [Issue Tracker](https://github.com/Data-Wise/claude-plugins/issues)
- [ROADMAP](https://github.com/Data-Wise/claude-plugins/blob/main/craft/ROADMAP.md)
