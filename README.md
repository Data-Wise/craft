# Craft - Full Stack Developer Toolkit Plugin

[![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/craft-ci.yml/badge.svg)](https://github.com/Data-Wise/craft/actions/workflows/craft-ci.yml)
[![Validate Plugins](https://github.com/Data-Wise/craft/actions/workflows/validate-plugins.yml/badge.svg)](https://github.com/Data-Wise/craft/actions/workflows/validate-plugins.yml)
[![Version](https://img.shields.io/badge/version-1.23.1-blue.svg)](https://github.com/Data-Wise/craft/releases/tag/v1.23.1)
[![Documentation](https://img.shields.io/badge/docs-complete-green.svg)](https://data-wise.github.io/craft/)

> **v1.23.1 - Hub v2.0** 🚀
> **97 commands** | **21 skills** | **8 agents** | **Zero-maintenance discovery**
> Smart command discovery with auto-detection (94% faster), 3-layer navigation, 98% test coverage

A comprehensive production-ready toolkit for Claude Code featuring smart orchestration, ADHD-friendly workflows, multi-agent coordination, and complete documentation coverage.

## Installation

Craft works in both Claude Code CLI and Claude Desktop app. No MCP server dependencies required.

### Option 1: Homebrew (Recommended - macOS)

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

### Option 2: Quick Install (curl)

```bash
# One-command installation
curl -fsSL https://raw.githubusercontent.com/Data-Wise/craft/main/install.sh | bash
```

**Then restart Claude Code to load the plugin.**

### Option 3: npm (When published)

```bash
# Install from npm (after publishing)
npm install -g @data-wise/claude-craft-plugin

# Plugin will auto-install to ~/.claude/plugins/craft
```

### Option 4: Manual Installation (Local Development)

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
Craft v1.17.0 loaded
86 commands available
```

### Using in Claude Code CLI

After installation, commands are immediately available:

```bash
# Start Claude Code in any directory
claude

# Use craft commands
/craft:do "add user authentication"
/craft:check
/craft:test:run
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

**Full documentation:** https://data-wise.github.io/craft/

- [Quick Start](https://data-wise.github.io/craft/QUICK-START/) (30 seconds)
- [ADHD Guide](https://data-wise.github.io/craft/ADHD-QUICK-START/) (neurodivergent-friendly)
- [Visual Workflows](https://data-wise.github.io/craft/workflows/) (10 GIF demonstrations)
- [Command Reference](https://data-wise.github.io/craft/REFCARD/) (all 74 commands)
- [Skills & Agents](https://data-wise.github.io/craft/guide/skills-agents/) (21 skills, 8 agents)

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

## Mode System (NEW in v1.2.0)

Commands support execution modes for different use cases:

| Mode | Time | Use Case |
|------|------|----------|
| **default** | < 10s | Quick checks |
| **debug** | < 120s | Verbose output, traces |
| **optimize** | < 180s | Parallel, performance |
| **release** | < 300s | Comprehensive audit |

```bash
/craft:code:lint                # Quick check
/craft:code:lint debug          # Verbose with suggestions
/craft:test:run release         # Full suite with coverage
/craft:arch:analyze optimize    # Performance analysis
```

## Teaching Mode (NEW in v1.18.0)

Specialized workflows for teaching projects with automated validation, semester tracking, and safe publishing.

**Key Features:**
- Auto-detection via `.flow/teach-config.yml` configuration
- Content validation (syllabus sections, schedule completeness, assignment files)
- Preview-before-publish workflow (draft → production branches)
- Semester progress tracking with automatic week calculation
- ADHD-friendly dashboards and output

![Teaching Workflow Demo](docs/demos/teaching-workflow.gif)

**Quick Start:**
1. Create `.flow/teach-config.yml` with course info and semester dates
2. Run `/craft:site:validate` to check content completeness
3. Publish with confidence using `/craft:site:publish`

**Example workflow:**
```bash
# Check semester progress
/craft:site:progress

# Validate content before publishing
/craft:site:validate

# Publish draft → production (with preview)
/craft:site:publish
```

**[Full Tutorial](https://data-wise.github.io/craft/tutorials/teaching-mode-setup/)** • **[Config Schema](https://data-wise.github.io/craft/teaching-config-schema/)**

## Commands (86 total)

### Workflow Commands (12) - NEW in v1.17.0
| Command | Description |
|---------|-------------|
| `/brainstorm [depth] [focus] [action]` | Enhanced brainstorming with smart detection, design modes, time budgets, and agent delegation |
| `/spec-review <file>` | Interactive spec review with validation, status updates, and archival |
| `/focus [task]` | Enter focus mode for deep work on a specific task |
| `/next` | Get next task recommendation |
| `/done [message]` | Mark current task as complete |
| `/recap` | Generate session summary and progress report |
| `/stuck [description]` | Get help when blocked on a task |
| `/refine <spec-file>` | Refine and improve existing spec documents |
| `/task-status [task-id]` | Check status of background tasks |
| `/task-output <task-id>` | Get output from completed task |
| `/task-cancel <task-id>` | Cancel running background task |
| `/adhd-guide` | ADHD-friendly workflow guide and best practices |

**Brainstorming Modes:**
```bash
/brainstorm q feat        # Quick feature brainstorm
/brainstorm d arch        # Deep architecture analysis
/brainstorm max ux save   # Max depth UX design with spec capture
```

### Smart Commands (4) - ENHANCED
| Command | Description |
|---------|-------------|
| `/craft:do <task>` | Universal command - routes to appropriate workflow |
| `/craft:orchestrate <task> [mode]` | **ENHANCED v2.1** Launch orchestrator with mode-aware execution, context tracking, timeline view |
| `/craft:check` | Pre-flight checks (commit/pr/release) |
| `/craft:help` | Context-aware help and suggestions |

#### Orchestrator Modes (NEW in v1.4.0)
```bash
/craft:orchestrate "add auth" optimize    # Fast parallel (4 agents)
/craft:orchestrate "prep release" release # Thorough audit
/craft:orchestrate status                 # Agent dashboard
/craft:orchestrate timeline               # Execution timeline
/craft:orchestrate budget                 # Context tracking
/craft:orchestrate continue               # Resume session
```

### Code Commands (12)
| Command | Description | Modes |
|---------|-------------|-------|
| `/craft:code:debug` | Systematic debugging | - |
| `/craft:code:demo` | Create demonstrations | - |
| `/craft:code:docs-check` | Pre-flight doc check | - |
| `/craft:code:refactor` | Refactoring guidance | - |
| `/craft:code:release` | Release workflow | - |
| `/craft:code:test-gen` | Generate test files | - |
| `/craft:code:lint` | Code style checks | ✓ |
| `/craft:code:coverage` | Coverage report | ✓ |
| `/craft:code:deps-check` | Dependency health | - |
| `/craft:code:deps-audit` | Security scan | - |
| `/craft:code:ci-local` | CI checks locally | - |
| `/craft:code:ci-fix` | Fix CI failures | - |

### Test Commands (6)
| Command | Description | Modes |
|---------|-------------|-------|
| `/craft:test:run` | Unified test runner | ✓ |
| `/craft:test:watch` | Watch mode | - |
| `/craft:test:coverage` | Coverage analysis | ✓ |
| `/craft:test:debug` | Debug failing tests | - |
| `/craft:test:cli-gen` | Generate CLI test suites | - |
| `/craft:test:cli-run` | Run CLI test suites | - |

### Architecture Commands (4)
| Command | Description | Modes |
|---------|-------------|-------|
| `/craft:arch:analyze` | Architecture analysis | ✓ |
| `/craft:arch:plan` | Design architecture | - |
| `/craft:arch:review` | Review changes | - |
| `/craft:arch:diagram` | Generate diagrams | - |

### Planning Commands (3)
| Command | Description |
|---------|-------------|
| `/craft:plan:feature` | Plan features with tasks |
| `/craft:plan:sprint` | Sprint planning |
| `/craft:plan:roadmap` | Generate roadmaps |

### Documentation Commands (13) - CONSOLIDATED in v1.11.0

#### Super Commands (3) - Smart defaults, do everything useful
| Command | Description |
|---------|-------------|
| `/craft:docs:update` | **Smart-Full**: Detect → Generate all needed → Check → Changelog |
| `/craft:docs:sync` | **Detection**: Classify changes, report stale docs, recommend actions |
| `/craft:docs:check` | **Validation**: Links + stale + nav + auto-fix (Version C: full-by-default) |

```bash
# Just run it - figures out what's needed
/craft:docs:update                    # Smart detection → full execution
/craft:docs:update "sessions"         # Feature-specific full cycle
/craft:docs:sync                      # Quick: "3 stale, guide recommended"
/craft:docs:check                     # Full check cycle, auto-fixes issues
/craft:docs:check --report-only       # CI-safe mode (no modifications)

# ADHD-friendly website enhancement (NEW v1.15.0)
/craft:docs:website                   # Full enhancement (all 3 phases)
/craft:docs:website --analyze         # Show ADHD score only
/craft:docs:website --phase 1         # Quick wins: TL;DR, mermaid fixes, time estimates
/craft:docs:website --phase 2         # Structure: Visual workflows, navigation
/craft:docs:website --phase 3         # Polish: Mobile responsive, interactions
/craft:docs:website --dry-run         # Preview changes without writing
```

#### Specialized Commands (9)
| Command | Description |
|---------|-------------|
| `/craft:docs:api` | OpenAPI/Swagger documentation |
| `/craft:docs:changelog` | Auto-update CHANGELOG |
| `/craft:docs:site` | Website-focused updates with optional deploy |
| `/craft:docs:website` | **NEW v1.15.0** ADHD-friendly website enhancement (scoring, TL;DR, mermaid fixes) |
| `/craft:docs:mermaid` | Mermaid diagram templates (6 types) |
| `/craft:docs:nav-update` | Update mkdocs.yml navigation |
| `/craft:docs:prompt` | Generate reusable maintenance prompts |
| `/craft:docs:demo` | Terminal recorder for GIF demos (asciinema/VHS) |
| `/craft:docs:guide` | **NEW** Feature guide + demo + refcard generator |

#### Internal (1)
| Command | Description |
|---------|-------------|
| `/craft:docs:claude-md` | Update CLAUDE.md (called by other commands) |

### Site Commands (12) - ENHANCED in v1.9.0
| Command | Description |
|---------|-------------|
| `/craft:site:create` | Full documentation site wizard with 8 design presets |
| `/craft:site:nav` | **NEW v1.9.0** Navigation reorganization (ADHD-friendly, max 7 sections) |
| `/craft:site:audit` | **NEW v1.9.0** Content inventory & audit (outdated, duplicates, gaps) |
| `/craft:site:consolidate` | **NEW v1.9.0** Merge duplicate/overlapping documentation files |
| `/craft:site:update` | Update site content from code changes |
| `/craft:site:status` | Dashboard and health check |
| `/craft:site:theme` | Quick theme changes (colors, presets, fonts) |
| `/craft:site:add` | Add new documentation pages |
| `/craft:site:build` | Build site |
| `/craft:site:preview` | Preview locally |
| `/craft:site:deploy` | Deploy to GitHub Pages |
| `/craft:site:init` | Basic initialization (use `create` for full wizard) |

### Git Commands (5 + 4 guides)
| Command | Description |
|---------|-------------|
| `/craft:git:branch` | Branch management |
| `/craft:git:sync` | Smart git sync |
| `/craft:git:clean` | Clean merged branches |
| `/craft:git:recap` | Activity summary |
| `/craft:git:worktree` | **NEW v1.8.0** Parallel development with git worktrees |

**Git Guides:** refcard, undo-guide, safety-rails, learning-guide

### CI Commands (3) - NEW in v1.10.0
| Command | Description |
|---------|-------------|
| `/craft:ci:detect` | Smart detection of project type, build tools, and CI requirements |
| `/craft:ci:generate` | Generate GitHub Actions workflow from detection |
| `/craft:ci:validate` | Validate existing CI workflow against project configuration |

### Distribution Commands (2)
| Command | Description |
|---------|-------------|
| `/craft:dist:homebrew` | Generate/update Homebrew formula |
| `/craft:dist:curl-install` | Create curl-based install scripts |

### Discovery
| Command | Description |
|---------|-------------|
| `/craft:hub` | Command discovery hub |

## Skills (17)

| Skill | Category | Triggers |
|-------|----------|----------|
| `backend-designer` | Design | API, database, auth |
| `frontend-designer` | Design | UI/UX, components |
| `devops-helper` | Design | CI/CD, deployment |
| `test-strategist` | Testing | Test strategy |
| `cli-test-strategist` | Testing | CLI testing |
| `system-architect` | Architecture | System design |
| `project-planner` | Planning | Feature planning |
| `mode-controller` | Modes | Mode behavior |
| `task-analyzer` | Orchestration | Task routing |
| `changelog-automation` | Documentation | Changelog patterns |
| `architecture-decision-records` | Documentation | ADR generation |
| `openapi-spec-generation` | Documentation | OpenAPI specs |
| `mermaid-linter` | Documentation | Mermaid diagram validation |
| `project-detector` | CI | **NEW v1.10.0** Smart project type detection |
| `distribution-strategist` | Distribution | Release channels |
| `homebrew-formula-expert` | Distribution | Homebrew formulas |
| `worktree-expert` | Git | Git worktree workflows |

## Agents (7)

| Agent | Purpose |
|-------|---------|
| `orchestrator` | Smart delegation to skills |
| `orchestrator-v2` | **ENHANCED** Mode-aware execution, context tracking, timeline view |
| `docs-architect` | Long-form technical documentation |
| `tutorial-engineer` | Step-by-step tutorials |
| `api-documenter` | OpenAPI/Swagger documentation |
| `reference-builder` | Technical reference guides |
| `mermaid-expert` | Mermaid diagram generation |

## Workflows

### Daily Development
```
/craft:check → /craft:test:run → /craft:git:sync
```

### Release Preparation
```
/craft:check --for release
# OR
/craft:code:deps-audit → /craft:test:run release → /craft:code:release
```

### Feature Development
```
/craft:do "add feature name"
# Routes to: arch:plan → code:test-gen → git:branch
```

### Documentation Workflow (v1.11.0 - Consolidated)
```bash
# THE ONE COMMAND - detects what's needed, does it all
/craft:docs:update                    # Smart detection → full execution

# Feature-specific documentation
/craft:docs:update "auth"             # Full cycle for auth feature

# Check documentation health
/craft:docs:check                     # Full: links + stale + nav + auto-fix
/craft:docs:check --report-only       # CI mode (no changes)

# Quick status check
/craft:docs:sync                      # "3 stale, guide recommended (score: 7)"

# Deploy website
/craft:docs:site --deploy
```

### Site Workflow (NEW in v1.7.0)
```
# Create new documentation site with design preset
/craft:site:create --preset adhd-focus

# Change theme quickly
/craft:site:theme --preset adhd-calm
/craft:site:theme --primary "#1a73e8"

# Add new pages
/craft:site:add guide "Getting Started"

# Update content from code changes
/craft:site:update

# Check site health
/craft:site:status

# Build and deploy
/craft:site:build → /craft:site:deploy
```

## Version

- **Version:** 1.11.0
- **Author:** DT (Data-Wise)
- **License:** MIT

## Development

**For plugin development and contributions:**

- 📖 **[Architecture Guide](docs/architecture.md)** - How Craft works internally
- 📖 **[Commands Reference](docs/commands.md)** - All 86 commands documented
- 📖 **[Skills & Agents](docs/guide/skills-agents.md)** - 21 skills, 8 agents
- Development commands (testing, validation, documentation)
- Architecture patterns and plugin structure
- CI/CD workflows and quality standards

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
