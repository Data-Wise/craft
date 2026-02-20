---
description: "/craft:hub - Command Discovery Hub"
---

# /craft:hub - Command Discovery Hub

You are a command discovery assistant for the craft plugin. Help users find the right command.

## When Invoked (`/craft:hub`)

### Step 0: Load Command Data (Auto-Detection)

**IMPORTANT**: Before displaying the hub, load command data from the discovery engine:

```python
import sys
from pathlib import Path

# Add commands directory to path
plugin_dir = Path.cwd()
sys.path.insert(0, str(plugin_dir))

# Import discovery engine
from commands._discovery import get_command_stats, load_cached_commands

# Get current command statistics
stats = get_command_stats()
commands = load_cached_commands()

# Available data:
# - stats['total']: Total command count (e.g., 108)
# - stats['categories']: Dict of category counts (e.g., {'code': 12, 'test': 2, ...})
# - stats['with_modes']: Commands supporting modes
# - stats['with_dry_run']: Commands with dry-run support
# - commands: Full list of command objects with metadata
```

**Use this data** to populate the hub display below with accurate, auto-detected counts.

### Step 1: Detect Project Context

```
Detection Rules (check in order):
1. .claude-plugin/plugin.json → Claude Code Plugin
2. DESCRIPTION file → R Package
3. pyproject.toml → Python Package
4. package.json → Node.js Project
5. _quarto.yml → Quarto Project
6. mkdocs.yml → MkDocs Project
7. Otherwise → Generic Project
```

### Step 2: Display Hub (Layer 1 - Main Menu)

**Generate this display dynamically** using stats and commands data loaded in Step 0.

Replace placeholders with actual data from `stats`.

Display template:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CRAFT - Full Stack Developer Toolkit v2.23.1                          │
│  [PROJECT_NAME] ([PROJECT_TYPE]) on [GIT_BRANCH]                       │
│  108 commands | 25 skills | 8 agents | ~1472 tests passing             │
├─────────────────────────────────────────────────────────────────────────┤
│ SMART COMMANDS (Start Here):                                            │
│    /craft:do <task>     Universal command - AI routes to best workflow  │
│    /craft:check         Pre-flight checks for commit/pr/release         │
│    /craft:smart-help    Context-aware help and suggestions              │
├─────────────────────────────────────────────────────────────────────────┤
│ MODES (default|debug|optimize|release):                                 │
│    default  < 10s   Quick analysis, minimal output                      │
│    debug    < 120s  Verbose traces, detailed fixes                      │
│    optimize < 180s  Performance focus, parallel execution               │
│    release  < 300s  Comprehensive checks, full audit                    │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ CODE (12)                         TEST (2)                              │
│   /craft:code:lint [mode]          /craft:test [mode]                   │
│   /craft:code:coverage [mode]      /craft:test:gen                      │
│   /craft:code:debug                                                     │
│   /craft:code:refactor           ARCH (4)                               │
│   /craft:code:deps-audit           /craft:arch:analyze [mode]           │
│   /craft:code:ci-local             /craft:arch:plan                     │
│   /craft:code:ci-fix               /craft:arch:review                   │
│                                    /craft:arch:diagram                  │
│ DOCS (25)                                                               │
│   /craft:docs:update             PLAN (3)                               │
│   /craft:docs:sync                 /craft:plan:feature                  │
│   /craft:docs:lint                 /craft:plan:sprint                   │
│   /craft:docs:check                /craft:plan:roadmap                  │
│   /craft:docs:changelog                                                 │
│   /craft:docs:claude-md          CI (4)                                 │
│   /craft:docs:nav-update           /craft:ci:detect                    │
│   /craft:docs:demo                 /craft:ci:generate                  │
│   /craft:docs:mermaid              /craft:ci:validate                  │
│   /craft:docs:check-links          /craft:ci:status                    │
│                                                                         │
│ GIT (13 incl. 4 guides)          WORKFLOW (13)                          │
│   /craft:git:worktree              /brainstorm [d|f|s] "topic"         │
│   /craft:git:sync                  /workflow:focus                     │
│   /craft:git:branch                /workflow:done                      │
│   /craft:git:clean                 /workflow:spec-review               │
│   /craft:git:recap                 /craft:insights                     │
│   /craft:git:status                                                     │
│   /craft:git:protect             DIST (4)                               │
│   /craft:git:unprotect             /craft:dist:marketplace             │
│                                    /craft:dist:homebrew                 │
│ SITE (16)                          /craft:dist:curl-install             │
│   /craft:site:build                /craft:dist:pypi                    │
│   /craft:site:deploy                                                    │
│   /craft:site:check              ORCHESTRATE (2)                        │
│   /craft:site:update               /craft:orchestrate [mode]           │
│   /craft:site:publish              /craft:orchestrate:resume           │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Quick Actions:                                                          │
│    /craft:do "fix bug"          /craft:check --for pr                    │
│    /brainstorm d f s "auth"     /craft:git:worktree create feat/x       │
│    /craft:test debug            /release --dry-run                       │
│    /craft:git:sync              /craft:insights --since 7                │
└─────────────────────────────────────────────────────────────────────────┘
```

**Category Navigation:**

- User can say `/craft:hub <category>` to see all commands in that category (Layer 2)
- User can say `/craft:hub <category>:<command>` for command details (Layer 3)

---

## Layer 2: Category View

When invoked with `/craft:hub <category>` (e.g., `/craft:hub code`):

### Step 1: Parse Category Argument

```python
# Check if user provided a category argument
import sys
category_arg = None  # Extract from user input

if category_arg:
    # User wants to see specific category
    from commands._discovery import get_category_info

    category_info = get_category_info(category_arg)

    if category_info['count'] == 0:
        print(f"Category '{category_arg}' not found or has no commands.")
        print(f"Try: /craft:hub to see all categories")
    else:
        # Display Layer 2: Category View
        display_category_view(category_info)
else:
    # No category specified, show Layer 1 (Main Menu)
    display_main_menu()
```

### Step 2: Display Category View

**Generate this display using category_info data:**

```
┌─────────────────────────────────────────────────────────────────┐
│ [ICON] [CATEGORY] COMMANDS ([COUNT] total)                      │
│ [Category Description]                                          │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ [SUBCATEGORY 1] ([count] commands)                              │
│   1. /craft:[category]:[command1] [mode]   [description]       │
│   2. /craft:[category]:[command2]          [description]       │
│   ...                                                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ Common Workflows:                                               │
│   [Workflow 1 name]: [steps]                                    │
│   [Workflow 2 name]: [steps]                                    │
│                                                                 │
│ Back to hub: /craft:hub                                         │
│ Learn more: /craft:hub [category]:[command]                     │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation notes:**

1. Group commands by subcategory using `category_info['subcategories']`
2. For commands without subcategory, use 'general' group
3. Show mode indicator `[mode]` for commands that support modes
4. Keep descriptions under 40 characters
5. Number commands sequentially across all subcategories

---

## Layer 3: Command Detail + Tutorial

When invoked with `/craft:hub <category>:<command>` (e.g., `/craft:hub code:lint`):

Display:

1. **Header** - Command name and short description
2. **Description** - Detailed explanation of what the command does
3. **Modes** - Execution modes with time budgets (if applicable)
4. **Basic Usage** - Syntax examples with mode variations
5. **Common Workflows** - Real-world usage patterns
6. **Related Commands** - Similar/complementary commands for navigation
7. **Navigation Footer** - Links back to category and hub

---

## Smart Commands

### `/craft:do <task>` - Universal Command

```
Intelligently routes your task to the right workflow:

 /craft:do initialize project    -> git:init (interactive wizard)
 /craft:do add authentication    -> arch:plan + code:test-gen + git:branch
 /craft:do fix login bug         -> code:debug + test + test debug
 /craft:do improve quality       -> code:lint + test --coverage + code:refactor
 /craft:do prepare release       -> deps-audit + test release + code:release

With orchestration:
 /craft:do "add feature X" --orch           # Orchestrate with mode prompt
 /craft:do "implement auth" --orch=optimize # Fast parallel orchestration
 /craft:do "debug issue" --orch=debug       # Sequential troubleshooting
 /craft:do "task" --orch --dry-run          # Preview orchestration plan
```

### `/craft:check` - Universal Pre-flight

```
Auto-detects project type and runs appropriate checks:

/craft:check                   Quick validation (lint + tests + types)
/craft:check --for commit      Pre-commit checks
/craft:check --for pr          Pre-PR validation (+ coverage + conflicts)
/craft:check --for release     Full release audit (+ security + docs)
/craft:check --context         Output session context only (no checks)
/craft:check --dry-run         Preview which checks will run

Orchestrated:
/craft:check --orch=optimize   Fast parallel validation
/craft:check --orch=release    Comprehensive pre-release audit
```

### `/craft:smart-help` - Context-Aware Help

```
/craft:smart-help              Shows relevant commands for your project
/craft:smart-help testing      Deep dive into testing commands
/craft:smart-help "how do I..."  Answer workflow questions
```

## Mode System

Many commands support modes for different use cases:

| Mode | Time Budget | Use Case |
|------|-------------|----------|
| **default** | < 10-30s | Day-to-day quick checks |
| **debug** | < 120s | Investigating issues, verbose output |
| **optimize** | < 180s | Performance focus, parallel execution |
| **release** | < 300s | Pre-release comprehensive checks |

---

## Category Deep Dive

### `/craft:hub code`

```
CODE COMMANDS (12) - Code Quality & Development
─────────────────────────────────────────────────────────────────────────
Command                  | Description                    | Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:code:lint         | Code style & quality checks    | yes
/craft:code:coverage     | Test coverage report           | yes
/craft:code:deps-check   | Check dependency health        | -
/craft:code:deps-audit   | Security vulnerability scan    | -
/craft:code:ci-local     | Run CI checks locally          | -
/craft:code:ci-fix       | Fix CI failures                | -
/craft:code:debug        | Systematic debugging           | -
/craft:code:demo         | Create demonstrations          | -
/craft:code:test-gen     | Generate test files            | -
/craft:code:refactor     | Refactoring guidance           | -
/craft:code:release      | Release workflow               | -
/craft:code:docs-check   | Pre-flight doc check           | -
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub test`

```
TEST COMMANDS (2) - Unified Testing
─────────────────────────────────────────────────────────────────────────
Command                  | Description                    | Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:test [mode]       | Unified test runner            | yes
/craft:test:gen          | Generate test suites (Jinja2)  | -
─────────────────────────────────────────────────────────────────────────

Usage:
  /craft:test                     # Quick smoke tests
  /craft:test debug               # Verbose with traces
  /craft:test --coverage          # Coverage analysis
  /craft:test release             # Full suite + coverage report
  /craft:test:gen                 # Auto-detect project, generate tests
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub docs`

```
DOCS COMMANDS (25) - Documentation Automation
─────────────────────────────────────────────────────────────────────────
Command                        | Description
───────────────────────────────┼─────────────────────────────────────
/craft:docs:update             | Smart doc generator (detect + generate)
/craft:docs:sync               | Detect changes, classify doc needs
/craft:docs:lint               | Markdown quality checks
/craft:docs:check              | Documentation health check
/craft:docs:check-links        | Internal link validation
/craft:docs:changelog          | Auto-update CHANGELOG.md
/craft:docs:nav-update         | Update mkdocs.yml navigation
/craft:docs:demo               | Terminal recording & GIF generator
/craft:docs:mermaid            | Generate Mermaid diagram templates
/craft:docs:guide              | Generate feature guides
/craft:docs:tutorial           | Generate step-by-step tutorials
/craft:docs:api                | Generate API documentation
/craft:docs:quickstart         | Generate quickstart guides

CLAUDE.md Management:
  /craft:docs:claude-md:init   | Create from lean template (< 150 lines)
  /craft:docs:claude-md:sync   | 4-phase pipeline (detect/audit/fix/optimize)
  /craft:docs:claude-md:edit   | Interactive section editing

Reference Files (.claude/reference/):
  agents.md              | Agent inventory (model, description)
  test-suite.md          | Test files with type classification
  project-structure.md   | Directory tree, counts, version

  Refresh: PYTHONPATH=. python3 utils/claude_md_sync.py --generate-reference
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub git`

```
GIT COMMANDS (13: 9 commands + 4 guides)
────────────────────────────────────────────────────────────────────────
Commands:
  /craft:git:worktree     Parallel development (create/move/finish/clean)
  /craft:git:sync         Smart sync with remote (pull, rebase, push)
  /craft:git:branch       Branch management (create, switch, delete)
  /craft:git:clean        Clean up merged branches safely
  /craft:git:recap        Git activity summary (what changed?)
  /craft:git:status       Enhanced status with protection level
  /craft:git:protect      Re-enable branch protection
  /craft:git:unprotect    Session-scoped bypass (auto-expires)
  /craft:git:init         Initialize repo with craft workflow

Guides:
  /craft:git:refcard        Quick reference card
  /craft:git:undo-guide     Emergency undo guide
  /craft:git:safety-rails   Safety rails guide
  /craft:git:learning-guide Learning guide

Branch Protection (v2.16.0):
  main   = block all (code + docs + commits)
  dev    = block new code files, allow edits + docs
  feat/* = unrestricted
────────────────────────────────────────────────────────────────────────
```

### `/craft:hub workflow`

```
WORKFLOW COMMANDS (13) - ADHD-Friendly Workflow Management
────────────────────────────────────────────────────────────────────────
Brainstorming:
  /brainstorm "topic"                | Quick brainstorm (default depth)
  /brainstorm d f s "auth"           | Deep + feature + save as spec
  /brainstorm q "quick idea"         | Quick (< 1 min, no questions)
  /brainstorm m a "architecture"     | Max depth + architecture focus

  Depth: q(uick) | d(eep) | m(ax)
  Focus: f(eat) | a(rch) | x(ux) | b(api) | u(i) | o(ps)
  Action: s(ave) — capture as SPEC file

Session Management:
  /workflow:focus                    | Start focused work session
  /workflow:next                     | Get next step
  /workflow:stuck                    | Get unstuck help
  /workflow:done                     | Complete session + capture context

Spec Management:
  /workflow:spec-review              | List, review, approve, archive specs
  /workflow:spec-review approve X    | Quick approval

Insights (v2.21.0):
  /craft:insights                    | Generate session insights report
  /craft:insights --format html      | HTML report for sharing
  /craft:insights --since 7          | Last 7 days only
────────────────────────────────────────────────────────────────────────
```

### `/craft:hub site`

```
SITE COMMANDS (16) - Documentation Sites
─────────────────────────────────────────────────────────────────────────
Command                  | R Package        | Other (MkDocs)
─────────────────────────┼──────────────────┼─────────────────────
/craft:site:build        | pkgdown::build   | mkdocs build
/craft:site:deploy       | gh-pages push    | mkdocs gh-deploy
/craft:site:check        | validate site    | validate site
/craft:site:update       | sync code->docs  | sync code->docs
/craft:site:preview      | preview locally  | mkdocs serve
/craft:site:publish      | teaching site    | teaching site
/craft:site:init         | pkgdown/altdoc   | mkdocs init
/craft:site:create       | new site wizard  | new site wizard
/craft:site:status       | site health      | site health
/craft:site:progress     | semester dash    | semester dash
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub arch`

```
ARCH COMMANDS (4) - Architecture & Design
─────────────────────────────────────────────────────────────────────────
Command                  | Description                    | Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:arch:analyze      | Analyze architecture patterns  | yes
/craft:arch:plan         | Design architecture            | -
/craft:arch:review       | Review architecture changes    | -
/craft:arch:diagram      | Generate Mermaid diagrams      | -
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub ci`

```
CI COMMANDS (4) - CI/CD Management
─────────────────────────────────────────────────────────────────────────
Command                  | Description
─────────────────────────┼────────────────────────────────────────────
/craft:ci:detect         | Detect project type and build tools
/craft:ci:generate       | Generate GitHub Actions workflow
/craft:ci:validate       | Validate existing CI workflow
/craft:ci:status         | Cross-repo CI status dashboard
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub dist`

```
DIST COMMANDS (4) - Distribution & Packaging
─────────────────────────────────────────────────────────────────────────
Command                  | Description
─────────────────────────┼────────────────────────────────────────────
/craft:dist:marketplace  | Marketplace init, validate, test, publish
/craft:dist:homebrew     | Generate Homebrew formula
/craft:dist:curl-install | Generate curl installer
/craft:dist:pypi         | Package for PyPI

Recommended Install Hierarchy:
  1. Marketplace (Recommended) — works everywhere, one command
  2. Homebrew — macOS power users, auto-updates
  3. Manual — contributors and developers
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub plan`

```
PLAN COMMANDS (3) - Planning & Project Management
─────────────────────────────────────────────────────────────────────────
Command                  | Description
─────────────────────────┼────────────────────────────────────────────
/craft:plan:feature      | Plan features with tasks and estimates
/craft:plan:sprint       | Sprint planning with capacity
/craft:plan:roadmap      | Generate project roadmaps
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub orchestrate`

```
ORCHESTRATE COMMANDS (2) - Multi-Agent Coordination
────────────────────────────────────────────────────────────────────────
/craft:orchestrate "task" [mode]     | Launch orchestrator
/craft:orchestrate:resume            | Resume previous session
/craft:orchestrate:plan              | Generate ORCHESTRATE file from spec

Modes:
  default   — 2 agents max, quick tasks
  debug     — 1 agent, sequential troubleshooting
  optimize  — 4 agents, fast parallel work
  release   — 4 agents, comprehensive audit

Quick orchestration (--orch flag on any command):
  /craft:do "add auth" --orch=optimize
  /craft:check --orch=release
  /brainstorm "API" --orch
────────────────────────────────────────────────────────────────────────
```

---

## Skills (25 Auto-Activated)

| Skill | Category | Triggers On |
|-------|----------|-------------|
| `backend-designer` | Design | API design, database, auth discussions |
| `frontend-designer` | Design | UI/UX, components, accessibility |
| `devops-helper` | Design | CI/CD, deployment, Docker |
| `test-strategist` | Testing | Test strategy, coverage, flaky tests |
| `test-generator` | Testing | Test file generation |
| `system-architect` | Architecture | System design, patterns, trade-offs |
| `project-planner` | Planning | Feature planning, sprints, roadmaps |
| `mode-controller` | Modes | Mode selection and behavior |
| `task-analyzer` | Orchestration | Task routing for /craft:do |
| `session-state` | Orchestration | Session persistence and resumption |
| `release` | Release | Release pipeline, version bump, deploy |
| `guard-audit` | DevOps | Guard friction, false positives, tune guard |
| `insights-apply` | Workflow | Insights report, CLAUDE.md rules |
| `doc-classifier` | Docs | Documentation needs classification |
| `mermaid-linter` | Docs | Mermaid diagram validation |
| `distribution-strategist` | Distribution | Packaging strategy selection |
| `homebrew-formula-expert` | Distribution | Homebrew formula generation |
| `homebrew-workflow-expert` | Distribution | Homebrew tap management |
| `homebrew-multi-formula` | Distribution | Multi-formula taps |
| `homebrew-setup-wizard` | Distribution | First-time Homebrew setup |
| `project-detector` | CI | Project type detection |
| `architecture-decision-records` | Docs | ADR generation |
| `changelog-automation` | Docs | Changelog from commits |
| `openapi-spec-generation` | Docs | OpenAPI spec generation |

## Agents (8 Specialized)

| Agent | Specialty | Triggers |
|-------|-----------|----------|
| `orchestrator-v2` | Complex multi-step tasks with parallel execution | `/craft:orchestrate` |
| `orchestrator` | Legacy orchestrator | Direct invocation |
| `docs-architect` | Technical documentation, architecture guides | Docs requests |
| `api-documenter` | OpenAPI specs, developer portals | API documentation |
| `reference-builder` | Exhaustive technical references | Reference docs |
| `tutorial-engineer` | Step-by-step tutorials | Tutorial creation |
| `demo-engineer` | Interactive demos | Demo creation |
| `mermaid-expert` | Flowcharts, diagrams, visualizations | Diagram requests |

---

## Release Pipeline

```
/release                  Interactive release pipeline (10 steps)
/release --dry-run        Preview release plan without executing
/release --autonomous     Fully automated (no prompts, auto-admin)

Pipeline: pre-flight -> bump -> commit -> PR -> merge ->
          GitHub release -> Homebrew tap -> docs deploy -> sync dev

Version bump: bump-version.sh syncs version across 11 files atomically
```

---

## Context-Aware Suggestions

### Claude Code Plugin (.claude-plugin/plugin.json detected)

```
SUGGESTED FOR CLAUDE CODE PLUGIN:

  /craft:check --for release  Full pre-release audit
  /craft:test                 Run pytest suite
  /release --dry-run          Preview release plan
  /craft:dist:marketplace     Marketplace distribution
  /craft:docs:claude-md:sync  Sync CLAUDE.md with project state
```

### Python Package (pyproject.toml detected)

```
SUGGESTED FOR PYTHON PROJECT:

  /craft:do "run all checks"  Smart workflow
  /craft:code:lint            Run ruff/flake8
  /craft:test                 Run pytest
  /craft:code:ci-local        Pre-push validation
  /craft:code:release         PyPI release workflow
```

### R Package (DESCRIPTION detected)

```
SUGGESTED FOR R PACKAGE:

  /craft:do "check package"   Smart workflow
  /craft:test                 Run testthat
  /craft:code:release         CRAN submission prep
  /craft:site:init            Setup pkgdown/altdoc
  /craft:arch:analyze         Check package structure
```

### Node.js Project (package.json detected)

```
SUGGESTED FOR NODE PROJECT:

  /craft:do "validate all"    Smart workflow
  /craft:code:lint            Run ESLint/Prettier
  /craft:test                 Run Jest/Vitest
  /craft:code:deps-audit      Security scan
  /craft:code:release         npm publish workflow
```

## Quick Reference

```
┌────────────────────────────────────────────────────────────────────────┐
│ Full-stack developer toolkit for Claude Code                           │
│ 108 commands | 25 skills | 8 agents | ~1472 tests passing              │
├────────────────────────────────────────────────────────────────────────┤
│ Start Here:                                                            │
│   /craft:do <task>   -> AI routes to best workflow                     │
│   /craft:check       -> Quick validation                               │
│   /craft:smart-help  -> Context-aware suggestions                      │
│                                                                        │
│ Development Workflow:                                                  │
│   /craft:code:lint [mode] -> /craft:test [mode] ->                     │
│   /craft:code:coverage -> /craft:code:ci-local -> /craft:git:sync      │
│                                                                        │
│ Feature Development:                                                   │
│   /craft:git:worktree create feat/x -> [develop] ->                    │
│   /craft:git:worktree finish -> /craft:git:worktree clean              │
│                                                                        │
│ Branch Protection:                                                     │
│   /craft:git:protect       -> Re-enable guard                         │
│   /craft:git:unprotect     -> Temporary bypass (auto-expires)         │
│   /craft:git:status        -> Show protection level                   │
│                                                                        │
│ Release Pipeline:                                                      │
│   /release                 -> Full 10-step pipeline                   │
│   /release --dry-run       -> Preview without executing               │
│   /release --autonomous    -> Fully automated release                 │
│                                                                        │
│ Orchestration:                                                         │
│   /craft:orchestrate "task" optimize -> 4 parallel agents              │
│   /craft:do "task" --orch=optimize   -> Quick orchestration            │
│   /craft:orchestrate:resume          -> Resume previous session        │
│                                                                        │
│ Documentation:                                                         │
│   /craft:docs:update       -> Smart detection + generation             │
│   /craft:docs:claude-md:sync -> 4-phase CLAUDE.md pipeline            │
│   /craft:docs:lint         -> Markdown quality checks                  │
│   /craft:docs:check-links  -> Internal link validation                 │
│                                                                        │
│ Brainstorming:                                                         │
│   /brainstorm "topic"              -> Default depth                   │
│   /brainstorm d f s "auth"         -> Deep + feature + save spec      │
│   /brainstorm m a "architecture"   -> Max + architecture focus        │
│                                                                        │
│ Insights & Guard:                                                      │
│   /craft:insights          -> Session friction report                  │
│   /craft:guard:audit       -> Audit guard config                       │
│   /craft:insights:apply    -> Apply insights to CLAUDE.md              │
│   /craft:check --context   -> Front-load session context               │
│                                                                        │
│ CI/CD:                                                                 │
│   /craft:ci:status         -> Cross-repo CI dashboard                  │
│   /craft:ci:generate       -> Generate GitHub Actions workflow         │
│   /craft:ci:detect         -> Detect project type + build tools        │
│                                                                        │
│ Daily:                                                                 │
│   /craft:git:recap -> /craft:check -> /craft:git:sync                  │
└────────────────────────────────────────────────────────────────────────┘
```
