# Craft - Full Stack Developer Toolkit Plugin

[![Documentation](https://img.shields.io/badge/docs-98%25%20complete-brightgreen.svg)](https://data-wise.github.io/craft/)
[![Docs Sync](https://github.com/Data-Wise/craft/actions/workflows/docs-sync.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-sync.yml)
[![Docs](https://github.com/Data-Wise/craft/actions/workflows/docs.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs.yml)
[![Homebrew Release](https://github.com/Data-Wise/craft/actions/workflows/homebrew-release.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/homebrew-release.yml)
[![Validate Dependencies](https://github.com/Data-Wise/craft/actions/workflows/validate-dependencies.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/validate-dependencies.yml)

**main:** [![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml) [![Deploy Docs](https://github.com/Data-Wise/craft/actions/workflows/docs.yml/badge.svg)](https://github.com/Data-Wise/craft/actions/workflows/docs.yml)
**dev:** [![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml) [![Documentation Quality](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml)
[![Version](https://img.shields.io/badge/version-4.6.0-brightgreen.svg)](https://github.com/Data-Wise/craft/releases)

> **Docs/publishing commands moved to [`folio`](https://github.com/Data-Wise/folio)** — see
> [MIGRATION-v4.md](docs/MIGRATION-v4.md) for the old-command → new-location table.
>
> **v4.6.0 — prose-staleness checks, hardened same day** 🚀
> **48 commands** | **41 skills** | **2 agents**
> New release-date consistency and count-prose checks in `docs-staleness-check.sh` Phase 7, closing a blind spot where stale counts read GREEN for multiple releases — then hardened the same day after a high-effort review found 9 defects (2 HIGH) in the initial ship. Also: Teaching Mode feature removed. See [NEWS.md](docs/NEWS.md).

A comprehensive production-ready toolkit for Claude Code featuring smart orchestration, ADHD-friendly workflows, multi-agent coordination, and complete documentation coverage.

## Installation

Craft works in both Claude Code CLI and Claude Desktop app. No MCP server dependencies required.

### Option 1: Marketplace (Recommended)

```bash
# Install from the Claude Code plugin marketplace
claude plugin add github:Data-Wise/craft
```

Works on **all platforms** (macOS, Linux, Windows). No additional tools required.

### Option 2: Homebrew (macOS)

```bash
# Add the Data-Wise tap
brew tap data-wise/tap

# Install craft plugin
brew install craft
```

The Homebrew formula automatically:

- Installs the plugin to `~/.claude/plugins/craft`
- Makes it available in Claude Code CLI and Claude Desktop
- No additional configuration needed

### Option 3: Quick Install (curl)

```bash
# One-command installation
curl -fsSL https://raw.githubusercontent.com/Data-Wise/craft/main/install.sh | bash
```

**Then restart Claude Code to load the plugin.**

### Option 4: npm (When published)

```bash
# Install from npm (after publishing)
npm install -g @data-wise/claude-craft-plugin

# Plugin will auto-install to ~/.claude/plugins/craft
```

### Option 5: Manual Installation (Local Development)

**For Claude Code CLI and Claude Desktop:**

```bash
# Clone the repository
git clone https://github.com/Data-Wise/craft.git
cd craft

# Install in development mode (symlink - changes reflected immediately)
ln -s $(pwd) ~/.claude/plugins/craft

# Or install in production mode (copy - stable)
cp -r . ~/.claude/plugins/craft
```

**Installation locations:**

- Plugin directory: `~/.claude/plugins/craft`
- Commands: `~/.claude/plugins/craft/commands/`
- Skills: `~/.claude/plugins/craft/skills/`
- Agents: `~/.claude/plugins/craft/agents/`

### Verify Installation

```bash
# Check plugin directory exists
ls -la ~/.claude/plugins/craft

# Verify plugin.json
cat ~/.claude/plugins/craft/.claude-plugin/plugin.json

# Test a command
claude
/craft:help
```

**Expected output:**

```
Craft v4.0.0 loaded
48 commands available
```

### Using in Claude Code CLI

After installation, commands are immediately available:

```bash
# Start Claude Code in any directory
claude

# Use craft commands
/craft:do "add user authentication"
/craft:check
/craft:test unit
```

### Using in Claude Desktop App

Craft automatically loads when you open Claude Desktop. Commands work the same way:

1. Open Claude Desktop app
2. Start a new conversation
3. Use slash commands: `/craft:do`, `/brainstorm`, etc.

### MCP Server Setup

**Craft does NOT require any MCP server configuration.**

Craft is a pure plugin that uses built-in Claude Code capabilities. No external servers needed.

**Benefits:**

- ✅ Instant startup (no server overhead)
- ✅ Simple installation (no server config)
- ✅ Works offline
- ✅ Self-contained

## 📚 Documentation

**Full documentation:** <https://data-wise.github.io/craft/> (99% complete)

- [Quick Start](https://data-wise.github.io/craft/QUICK-START/) (30 seconds)
- [ADHD Guide](https://data-wise.github.io/craft/ADHD-QUICK-START/) (neurodivergent-friendly)
- [Visual Workflows](https://data-wise.github.io/craft/workflows/) (10 GIF demonstrations)

> Full-stack developer toolkit for Claude Code — 48 commands, 2 agents, 41 skills with smart orchestration and ADHD-friendly workflows

- [Claude Code 2.1 Integration](https://data-wise.github.io/craft/guide/claude-code-2.1-integration/) (comprehensive guide with 9 diagrams)
- [Complexity Scoring Algorithm](https://data-wise.github.io/craft/guide/complexity-scoring-algorithm/) (complete technical documentation with 8 diagrams)
- [Version History](https://data-wise.github.io/craft/VERSION-HISTORY/) (v1.0.0 → v1.24.0 timeline)
- [Dependency Management](https://data-wise.github.io/craft/DEPENDENCY-MANAGEMENT/) (API, Architecture, Developer Guide)

## Quick Start - Smart Commands

```bash
# Universal command - AI routes to best workflow
/craft:do "add user authentication"

# Pre-flight checks
/craft:check                    # Quick validation
/craft:check --for release      # Full release audit

# Context-aware help
/craft:help                     # Suggestions for your project
/craft:help testing             # Deep dive into testing

# Discover all commands
/craft:hub
```

## Mode System

Commands support execution modes for different use cases:

| Mode         | Time   | Use Case               |
| ------------ | ------ | ---------------------- |
| **default**  | < 10s  | Quick checks           |
| **debug**    | < 120s | Verbose output, traces |
| **optimize** | < 180s | Parallel, performance  |
| **release**  | < 300s | Comprehensive audit    |

```bash
/craft:code:lint                # Quick check
/craft:code:lint debug          # Verbose with suggestions
/craft:test release             # Full suite with coverage
/craft:arch:analyze optimize    # Performance analysis
```

## Commands (48)

Every command is `/craft:<name>`. Four root commands (`brainstorm`, `check`, `next`, `refine`) are
thin shims: the command still works, and its logic lives in the skill named in its
`replaced-by:` frontmatter.

### Workflow & discovery (14)

| Command | What it does |
|---|---|
| `/craft:do <task>` | Universal entry point — scores the task and routes to the right commands |
| `/craft:plan <topic>` | Universal planning entry — routes to brainstorm, grill, plan-orchestrator, or feature planning |
| `/craft:brainstorm` | Brainstorming with design modes, time budgets, and spec capture (shim → `brainstorm` skill) |
| `/craft:grill` | Adversarially interrogate a plan or spec, one question at a time |
| `/craft:check` | Pre-flight readiness check before commit / PR / release (shim → `preflight-check` skill) |
| `/craft:test` | Unified test runner with category filtering and modes |
| `/craft:orch` | Orchestrator mode — subagent delegation, monitoring, mode-aware execution |
| `/craft:finish` | Session completion and context capture (renamed from `/craft:done` in v4.2.0) |
| `/craft:restore` | Restore git + `.STATUS` context when returning to a project |
| `/craft:next` | Decision support — what to work on next (shim → `adhd-workflow` skill) |
| `/craft:brief` | 3-line action block: next step / watch out for / connects to |
| `/craft:refine` | Prompt optimizer (shim → `prompt-refiner` skill) |
| `/craft:hub` · `/craft:smart-help` | Browse all commands · context-aware command suggestions |

### Code (13)

| Command | What it does |
|---|---|
| `/craft:code:lint` | Style and quality checks, with modes |
| `/craft:code:debug` | Guided bug diagnosis |
| `/craft:code:refactor` | Refactoring guidance |
| `/craft:code:test-gen` | Generate tests |
| `/craft:code:demo` | Code demonstration |
| `/craft:code:deps-check` · `/craft:code:deps-audit` | Dependency health · security audit for known vulnerabilities |
| `/craft:code:docs-check` | Documentation and website pre-flight check |
| `/craft:code:release` | Release workflow (delegates to the `release` skill for plugins) |
| `/craft:code:release-watch` | Track Claude Code + Desktop releases for plugin-relevant changes |
| `/craft:code:command-audit` | Validate command frontmatter and report a health score |
| `/craft:code:skill-standards` | Audit `SKILL.md` files against Anthropic's authoring standards |
| `/craft:code:fewer-prompts` | Install a curated read-only Bash allowlist |

### CI (8)

| Command | What it does |
|---|---|
| `/craft:ci:detect` · `/craft:ci:generate` · `/craft:ci:validate` | Detect project/CI needs · generate a GitHub Actions workflow · validate an existing one |
| `/craft:ci:local` | Run CI checks locally before pushing |
| `/craft:ci:status` | Cross-repo CI status dashboard |
| `/craft:ci:watch` | Poll a run to completion, then route: merge if green, triage if red |
| `/craft:ci:triage` | Classify a failing check as diff-caused vs pre-existing/infra |
| `/craft:ci:fix` | Fix CI failures |

### Architecture & planning (5)

| Command | What it does |
|---|---|
| `/craft:arch:analyze` · `/craft:arch:review` | Analyze architecture (with modes) · review it |
| `/craft:arch:plan` · `/craft:arch:diagram` | Plan architecture · generate diagrams |
| `/craft:plan:feature` | Feature planning, with test and doc plans on by default (`--no-tests` / `--no-docs`) |

### Orchestration (2)

| Command | What it does |
|---|---|
| `/craft:orch:drive` | Drive an approved SPEC to completion via the `/goal` loop, with a real verify gate |
| `/craft:orch:workflow` | Run a coded, fixed-control-flow workflow with schema-gated agents |

### Docs, site & distribution (6)

| Command | What it does |
|---|---|
| `/craft:docs:update` · `/craft:docs:changelog` | Smart doc updates · CHANGELOG from commits |
| `/craft:site:deploy` | Deploy the docs site to GitHub Pages |
| `/craft:dist:homebrew` · `/craft:dist:surfaces` | Homebrew automation · read-only multi-surface release registry |
| `/craft:git:issue-check <N>` | Check whether an open issue's premise still holds before fixing it |

The rest of the docs-authoring surface (`docs:sync`, `docs:mermaid`, `docs:tutorial`, `docs:site`,
…) moved to the separate **[folio](https://github.com/Data-Wise/folio)** plugin in v4.0.0 as
`/folio:docs:*`. Git workflow operations (branches, worktrees, sync, protection) are the
**`dev/git` skill** — ask in plain language ("create a worktree for X"); only
`/craft:git:issue-check` remains a command.

## Skills (41)

Skills trigger from plain-language requests; no slash command needed.

| Area | Skills |
|---|---|
| Workflow | `brainstorm`, `brainstorm-insights`, `grill`, `prompt-refiner`, `adhd-workflow`, `background-task-manager` |
| Orchestration | `task-analyzer`, `plan-orchestrator`, `drive-engine`, `workflow-engine`, `session-state`, `repo-triage`, `orchestrator-resilience` |
| Code & quality | `audit-router`, `plugin-audit`, `command-skill-token-efficiency`, `sync-features`, `preflight-check`, `guard-audit`, `hooks`, `insights-apply` |
| Design & architecture | `system-architect`, `backend-designer`, `frontend-designer`, `devops-helper`, `project-planner` |
| Testing | `test-generator`, `test-strategist` |
| Git & release | `git-workflow` (`dev/git`), `release`, `changelog-automation` |
| Distribution | `distribution-strategist`, `dist-extras`, `homebrew-formula-expert`, `homebrew-multi-formula`, `homebrew-setup-wizard`, `homebrew-workflow-expert` |
| Docs | `architecture-decision-records`, `claude-md-lifecycle` |
| CI & modes | `project-detector`, `mode-controller` |

## Agents (2)

| Agent | Purpose |
|---|---|
| `orchestrator-v2` | Multi-step orchestration with subagent monitoring and mode-aware execution — what `/craft:do` delegates to for complex tasks |
| `workflow-orchestrator` | Background agent delegation, task parallelization, and result synthesis |

The documentation agents (`docs-architect`, `api-documenter`, `tutorial-engineer`, …) ship with
folio.

## Workflows

### Daily development

```bash
/craft:do "add input validation to the signup form"   # routed to the right commands
/craft:code:lint && /craft:test                        # quick quality pass
/craft:finish                                          # capture session context
```

### Returning to a project

```bash
/craft:restore        # where did I leave off? (git + .STATUS)
/craft:next           # what to work on next
```

### Planning a feature

```bash
/craft:plan "redesign the auth flow"   # picks brainstorm / grill / feature plan
/craft:grill                            # stress-test the resulting spec
```

### Release preparation

```bash
/craft:check --for release   # pre-flight
/craft:test release          # full suite
/craft:code:release          # release workflow
```

### Documentation & site

```bash
/craft:docs:update           # detect and apply doc updates
/craft:docs:changelog        # CHANGELOG from commits
/craft:site:deploy           # publish to GitHub Pages
```

## Version

- **Version:** 4.6.0
- **Author:** DT (Data-Wise)
- **License:** MIT

## Development

**For plugin development and contributions:**

- 📖 **[Architecture Guide](docs/architecture.md)** - How Craft works internally
- 📖 **[Commands Reference](docs/commands.md)** - All 48 commands documented
- 📖 **[Skills & Agents](docs/skills-agents.md)** - 41 skills, 2 agents
- Development commands (testing, validation, documentation)
- Architecture patterns and plugin structure
- CI/CD workflows and quality standards
- Documentation staleness detection (4-phase checks with traffic light output)

See the [documentation site](https://data-wise.github.io/craft/) for comprehensive guides.

## Changelog

### [1.11.0] - 2025-12-30

#### Changed

- **Documentation Commands Consolidation** (16→12 commands):
  - **Super Commands (3)**: `update`, `sync`, `check` - smart defaults, do everything useful
  - **Specialized Commands (8)**: `api`, `changelog`, `site`, `mermaid`, `nav-update`, `prompt`, `demo`, `guide`
  - **Internal (1)**: `claude-md`
- **`update`**: Smart-Full default - detect → generate all needed → check → changelog
- **`sync`**: Merged `analyze` logic - detection + classification + stale report
- **`check`**: Renamed from `validate`, Version C full-by-default (links + stale + nav + auto-fix)

#### Added

- `/craft:docs:demo` - Terminal recorder for GIF demos (asciinema default, VHS optional)
- `/craft:docs:guide` - Feature guide + demo + refcard generator

#### Removed

- `/craft:docs:validate` → renamed to `/craft:docs:check`
- `/craft:docs:done` → merged into `sync` (default is quick)
- `/craft:docs:generate` → merged into `update`
- `/craft:docs:feature` → use `update "name"` instead
- `/craft:docs:analyze` → merged into `sync`

#### Philosophy

> "Just run the command. It figures out what's needed, then does it."

- Total: 68 commands, 17 skills, 7 agents

### [1.10.0] - 2025-12-28

#### Added

- **CI Toolkit** (3 commands):
  - `/craft:ci:detect` - Smart detection of project type, build tools, and CI requirements
  - `/craft:ci:generate` - Generate GitHub Actions workflow from detection (Python, Node, R, Rust, Go templates)
  - `/craft:ci:validate` - Validate existing CI workflow against project configuration
- **Project Detector Skill**:
  - Core detection logic for Python (uv/poetry/pip), Node (npm/pnpm/yarn), R, Rust, Go, Claude plugins
  - Detects test frameworks (pytest, jest, vitest, testthat, cargo test)
  - Identifies linting configs (ruff, eslint, lintr, clippy)
  - Recommends appropriate CI templates based on project type
- Total: 67 commands, 17 skills, 7 agents

### [1.9.0] - 2025-12-28

#### Added

- **Site Navigation Command**:
  - `/craft:site:nav` - ADHD-friendly navigation reorganization
  - Interactive mode selection menu (analyze, adhd, apply, preview)
  - Enforces max 7 top-level sections
  - Generates reorganization proposals
- **Site Audit Command**:
  - `/craft:site:audit` - Content inventory & quality audit
  - Modes: full, outdated, duplicates, gaps
  - Generates AUDIT-CONTENT-INVENTORY.md
  - Detects version mismatches, duplicate files, missing docs
- **Site Consolidate Command**:
  - `/craft:site:consolidate` - Merge duplicate documentation files
  - Auto-detect duplicates or merge specific files
  - Preview mode, safety backups, link updates
  - Archive option instead of delete
- **Docs Prompt Command**:
  - `/craft:docs:prompt` - Generate reusable maintenance prompts
  - Types: full, reorganize, audit, edit
  - Pre-filled with project context
  - ADHD-friendly design principles included
- **Sub-command UX Pattern**:
  - Standard menu pattern for commands with modes
  - Argument bypass for power users
  - Keyboard: ↑↓ Navigate, ⏎ Select, "cancel" to exit
  - Consistent footer with tips and related commands
- Total: 63 commands, 16 skills, 7 agents

### [1.8.0] - 2025-12-28

#### Added

- **Git Worktrees**: `/craft:git:worktree` for parallel development
- **Mermaid Diagrams**: `/craft:docs:mermaid` with 6 diagram templates
- **New Skills**: `mermaid-linter`, `worktree-expert`
- Total: 60 commands, 16 skills, 7 agents

### [1.7.0] - 2025-12-27

#### Added

- **Site Commands Redesign** (5 new commands):
  - `/craft:site:create` - Full documentation site wizard with design presets
  - `/craft:site:update` - Smart content sync from code changes
  - `/craft:site:status` - Site dashboard and health check
  - `/craft:site:theme` - Quick theme changes (colors, presets, fonts)
  - `/craft:site:add` - Add new documentation pages with templates
- **8 Design Presets**:
  - Standard: `data-wise`, `minimal`, `open-source`, `corporate`
  - ADHD-Friendly: `adhd-focus`, `adhd-calm`, `adhd-dark`, `adhd-light`
- **ADHD-Friendly Features**:
  - Reduced animations, larger click targets
  - Calm color palettes, clear hierarchy
  - Warm backgrounds (no harsh white/black)
- **Design System**: Templates, presets, color palettes
- **Preset Gallery**: Visual reference for all 8 presets
- Total: 61 commands, 15 skills, 7 agents

### [1.6.0] - 2025-12-27

#### Added

- **Docs Workflow Commands** (4 new commands):
  - `/craft:docs:update [full]` - Smart universal documentation updater
  - `/craft:docs:feature [name]` - Comprehensive feature documentation
  - `/craft:docs:done [summary]` - End-of-session doc updates
  - `/craft:docs:site [--deploy]` - Website-focused updates with deploy
- **Documentation Workflow Section** in README
- Total: 58 commands, 15 skills, 7 agents

### [1.5.0] - 2025-12-27

#### Added

- **Distribution Commands** (2 new commands):
  - `/craft:dist:homebrew` - Generate/update Homebrew formulas
  - `/craft:dist:curl-install` - Create curl-based installation scripts
- **Distribution Skills** (2 new skills):
  - `distribution-strategist` - Recommend optimal distribution channels
  - `homebrew-formula-expert` - Homebrew formula best practices
- Total: 54 commands, 15 skills, 7 agents

### [1.4.0] - 2025-12-27

#### Enhanced

- **Orchestrator v2.1** with major improvements:
  - Mode-aware execution (default, debug, optimize, release)
  - Improved context tracking with token estimation heuristics
  - Timeline view for visual execution progress
  - Session persistence with auto-save and resume
  - Per-agent context budgets (~15% each)
  - Smart summarization for large agent responses
  - New commands: `timeline`, `budget`, `mode`, `continue`, `save`, `history`, `new`
- Total: 51 commands, 12 skills, 7 agents

### [1.3.0] - 2025-12-26

#### Added

- 5 documentation agents (ported from documentation-generation plugin)
  - `docs-architect` - Long-form technical documentation
  - `tutorial-engineer` - Step-by-step tutorials
  - `api-documenter` - OpenAPI/Swagger documentation
  - `reference-builder` - Technical reference guides
  - `mermaid-expert` - Mermaid diagram generation
- 3 documentation skills
  - `changelog-automation` - Changelog patterns
  - `architecture-decision-records` - ADR generation
  - `openapi-spec-generation` - OpenAPI specs
- 4 new commands
  - `/craft:docs:generate` - Full documentation generation
  - `/craft:docs:api` - OpenAPI/Swagger documentation
  - `/craft:test:cli-gen` - Generate CLI test suites
  - `/craft:test:cli-run` - Run CLI test suites
- Total: 50 commands, 11 skills, 6 agents

### [1.2.0] - 2025-12-26

#### Added

- Mode system (default, debug, optimize, release)
- 3 smart commands (do, check, help)
- 2 new skills (mode-controller, task-analyzer)
- Mode support for lint, test:run, arch:analyze, coverage
- Total: 46 commands, 8 skills, 1 agent

### [1.1.0] - 2025-12-26

#### Added

- 6 new code commands (lint, coverage, deps-check, deps-audit, ci-local, ci-fix)
- 4 new test commands (run, watch, coverage, debug)
- 4 new architecture commands (analyze, plan, review, diagram)
- 3 new planning commands (feature, sprint, roadmap)
- 3 new skills (test-strategist, system-architect, project-planner)
- Total: 42 commands, 6 skills, 1 agent

### [1.0.0] - 2025-12-26

#### Added

- Initial release with 26 commands
- 6 code, 6 site, 8 git, 5 docs commands
- 3 skills (backend, frontend, devops)
- 1 orchestrator agent
- Hub command for discovery
