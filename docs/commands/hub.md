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
# - stats['total']: Total command count (e.g., 109)
# - stats['categories']: Dict of category counts (e.g., {'code': 15, 'test': 3, ...})
# - stats['with_modes']: Commands supporting modes
# - stats['with_dry_run']: Commands with dry-run support
# - commands: Full list of command objects with metadata

# Count skills, agents, and tests for banner
from pathlib import Path
skill_count = len(list((plugin_dir / 'skills').glob('*.md'))) if (plugin_dir / 'skills').exists() else 0
agent_count = len(list((plugin_dir / 'agents').glob('*.md'))) if (plugin_dir / 'agents').exists() else 0

# Read test count from CLAUDE.md or .STATUS (extract number from "N tests passing")
import re
test_count = "?"
for source in [plugin_dir / 'CLAUDE.md', plugin_dir / '.STATUS']:
    if source.exists():
        content = source.read_text()
        m = re.search(r'(\d+)\s+tests?\s+pass', content)
        if m:
            test_count = m.group(1)
            break
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

### Step 1.5: Read .STATUS Next Action

If a `.STATUS` file exists in the project root, extract the "Next Action" section:

```python
status_path = plugin_dir / '.STATUS'
next_action_lines = []

if status_path.exists():
    in_next_action = False
    for line in status_path.read_text().splitlines():
        if '🎯 Next Action' in line or 'Next Action' in line:
            in_next_action = True
            continue
        elif in_next_action:
            if line.strip() and (line.strip()[0] in '🔴✅🔄📋⚠️' or line.startswith('##')):
                break
            if line.strip():
                next_action_lines.append(line.strip())
```

**Display**: If `next_action_lines` is non-empty, show a `NEXT ACTION` section at the top of the hub. If `.STATUS` doesn't exist or has no Next Action, skip silently.

### Step 1.6: Detect Active Worktrees (NEW in v2.31.0)

Parse `git worktree list` to detect active worktrees for the WORKTREES section:

```bash
# Get all worktrees (porcelain format for reliable parsing)
worktree_data=$(git worktree list --porcelain 2>/dev/null)

# For each worktree (skip main working tree):
#   - branch name and ahead/behind dev
#   - uncommitted file count (git status --short | wc -l)
#   - staleness flag (no commits in 3+ days)
```

**If no worktrees exist:** Skip the WORKTREES section entirely.

### Step 2: Display Hub (Layer 1 - Main Menu)

**Generate this display dynamically** using stats and commands data loaded in Step 0.

Replace placeholders with actual data from `stats`.

Display template:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CRAFT - Full Stack Developer Toolkit v2.61.2                          │
│  [PROJECT_NAME] ([PROJECT_TYPE]) on [GIT_BRANCH]                       │
│  {stats['total']} commands | {skill_count} skills | {agent_count} agents | {test_count} tests passing │
├─────────────────────────────────────────────────────────────────────────┤
│ NEXT ACTION:  (from .STATUS — omit section if no .STATUS or no action) │
│    {next_action_lines[0]}                                              │
│    {next_action_lines[1]}  (show all parsed A/B/C entries)             │
├─────────────────────────────────────────────────────────────────────────┤
│ WORKTREES:  (omit section if no worktrees besides main working tree)   │
│    feature/auth    +5/-0 dev  2 uncommitted  3 hours ago              │
│    feature/docs    +12/-3 dev  0 uncommitted  ⚠ STALE (5 days)        │
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
│ CODE (13)                         TEST (0)                              │
│   /craft:code:lint [mode]          /craft:test [mode]                   │
│   /craft:test --coverage [mode]      /craft:test:gen                      │
│   /craft:code:debug                                                     │
│   /craft:code:refactor           ARCH (4)                               │
│   /craft:code:deps-audit           /craft:arch:analyze [mode]           │
│   /craft:ci:local             /craft:arch:plan                     │
│   /craft:ci:fix               /craft:arch:review                   │
│                                    /craft:arch:diagram                  │
│ DOCS (2)                                                               │
│   /craft:docs:update             PLAN (1)                               │
│   /folio:docs:sync                 /craft:plan:feature                  │
│   /folio:docs:lint                                                      │
│   /folio:docs:check                                                     │
│   /craft:docs:changelog                                                 │
│   /craft:docs:claude-md          CI (8)                                 │
│   /folio:docs:nav-update           /craft:ci:detect                    │
│   /folio:docs:demo                 /craft:ci:generate                  │
│   /folio:docs:mermaid              /craft:ci:validate                  │
│   /folio:docs:check-links          /craft:ci:status                    │
│                                                                         │
│ GIT (0, folded into dev/git skill) WORKFLOW (0)                       │
│   worktree/sync/recap/init/            /brainstorm [depth|focus] "topic"   │
│   protect/unprotect/status/            /workflow:done                      │
│   clean/branch/guard: ask              /craft:insights                     │
│   dev/git skill                                                          │
│                                   DIST (2)                               │
│                                     /craft:dist:marketplace             │
│                                    /craft:dist:homebrew                 │
│ SITE (1)                          /craft:dist:curl-install             │
│   /folio:site:build                /craft:dist:pypi                    │
│   /craft:site:deploy                                                    │
│   /folio:site:check              ORCHESTRATE (2)                        │
│   /folio:site:update               /craft:orch [mode]           │
│   /folio:site:publish                                                  │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Quick Actions:                                                          │
│    /craft:do "fix bug"          /craft:check --for pr                    │
│    /brainstorm deep feat "auth" ask "create a worktree for feat/x"      │
│    /craft:test debug            /release --dry-run                       │
│    ask "sync with remote"       /craft:insights --since 7                │
│                                                                         │
│  Recently Used: [if facets data exists — omit section if no data]       │
│    /craft:do (3x) · /craft:check (2x) · /workflow:done (2x)           │
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
CODE COMMANDS (13) - Code Quality & Development
─────────────────────────────────────────────────────────────────────────
Command                  | Description                    | Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:code:lint         | Code style & quality checks    | yes
/craft:test --coverage     | Test coverage report           | yes
/craft:code:deps-check   | Check dependency health        | -
/craft:code:deps-audit   | Security vulnerability scan    | -
/craft:ci:local     | Run CI checks locally          | -
/craft:ci:fix       | Fix CI failures                | -
/craft:code:debug        | Systematic debugging           | -
/craft:code:demo         | Create demonstrations          | -
/craft:code:test-gen     | Generate test files            | -
/craft:code:refactor     | Refactoring guidance           | -
/craft:code:release      | Release workflow               | -
/craft:code:docs-check   | Pre-flight doc check           | -
/craft:code:command-audit| Audit command frontmatter      | -
/craft:code:release-watch| Track Claude Code/Desktop rels | -
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub test`

```
TEST COMMANDS (0) - Unified Testing
─────────────────────────────────────────────────────────────────────────
Command                  | Description                    | Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:test [mode]       | Unified test runner            | yes
/craft:test:gen          | Generate test suites (Jinja2)  | -
/craft:test:template     | Manage Jinja2 test templates   | -
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
DOCS COMMANDS (2) - Documentation Automation (most moved to folio)
─────────────────────────────────────────────────────────────────────────
Command                        | Description
───────────────────────────────┼─────────────────────────────────────
/craft:docs:update             | Smart doc generator (detect + generate)
/folio:docs:sync               | Detect changes, classify doc needs
/folio:docs:lint               | Markdown quality checks
/folio:docs:check              | Documentation health check (links, stale, nav, mermaid)
/folio:docs:check-links        | Internal link validation
/craft:docs:changelog          | Auto-update CHANGELOG.md
/folio:docs:nav-update         | Update mkdocs.yml navigation
/folio:docs:demo               | Terminal recording & GIF generator
/folio:docs:mermaid            | Mermaid diagrams: templates, NL creation, MCP validation
/folio:docs:guide              | Generate feature guides
/folio:docs:tutorial           | Generate step-by-step tutorials
/folio:docs:api                | Generate API documentation
/folio:docs:quickstart         | Generate quickstart guides
/folio:docs:help               | Generate help pages
/folio:docs:prompt             | Generate documentation prompts
/folio:docs:site               | Website documentation focus
/folio:docs:website            | ADHD-friendly website enhancement
/folio:docs:workflow           | Workflow documentation generator

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
GIT COMMANDS (0: all folded into the dev/git skill, 2026-07 v4 consolidation)
────────────────────────────────────────────────────────────────────────
Worktree, sync, recap, init, branch protection, unprotect, status,
cleanup, quick-branch, and guard management: ask naturally or see
skills/dev/git/SKILL.md.

Guides:
  /craft:git:refcard        Quick reference card

Branch Protection (v2.16.0):
  main   = block all (code + docs + commits)
  dev    = block new code files, allow edits + docs
  feat/* = unrestricted
────────────────────────────────────────────────────────────────────────
```

### `/craft:hub workflow`

```
WORKFLOW COMMANDS (0) - ADHD-Friendly Workflow Management
────────────────────────────────────────────────────────────────────────
Brainstorming:
  /brainstorm "topic"                | Default depth (2 questions)
  /brainstorm deep feat s "auth"     | Deep + feature + save as spec
  /brainstorm quick "quick idea"     | Quick (< 1 min, no questions)
  /brainstorm "API" --orch           | Hand off to orchestrator after spec

  Depth: quick | default | deep (no max — deep work hands off to --orch)
  Focus: f(eat) | a(rch) | x(ux) | b(api) | u(i) | o(ps)
  Action: s(ave) — capture as SPEC file

Session Management:
  /workflow:next                     | Get next step
  /workflow:done                     | Complete session + capture context

Insights (v2.21.0):
  /craft:insights                    | Generate session insights report
  /craft:insights --format html      | HTML report for sharing
  /craft:insights --since 7          | Last 7 days only
────────────────────────────────────────────────────────────────────────
```

### `/craft:hub site`

```
SITE COMMANDS (1) - Documentation Sites (most moved to folio)
─────────────────────────────────────────────────────────────────────────
Command                  | R Package        | Other (MkDocs)
─────────────────────────┼──────────────────┼─────────────────────
/folio:site:build        | pkgdown::build   | mkdocs build
/craft:site:deploy       | gh-pages push    | mkdocs gh-deploy
/folio:site:check        | validate site    | validate site
/folio:site:update       | sync code->docs  | sync code->docs
/folio:site:publish      | teaching site    | teaching site
/folio:site:status       | site health      | site health
/folio:site:progress     | semester dash    | semester dash
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
CI COMMANDS (8) - CI/CD Management
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
DIST COMMANDS (2) - Distribution & Packaging
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
PLAN COMMANDS (1) - Planning & Project Management
─────────────────────────────────────────────────────────────────────────
Command                  | Description
─────────────────────────┼────────────────────────────────────────────
/craft:plan:feature      | Plan features with tasks and estimates
─────────────────────────────────────────────────────────────────────────
```

Sprint planning and roadmap generation moved into the `plan-orchestrator`
skill (Modes 3–4) — invoke `/craft:plan` and describe the need.

### `/craft:hub orchestrate`

```
ORCHESTRATE COMMANDS (2) - Multi-Agent Coordination
────────────────────────────────────────────────────────────────────────
/craft:orch "task" [mode]     | Launch orchestrator (free-form, fan-out)
/craft:orch:drive [spec]      | Spec-driven autonomous /goal loop → verified green
/craft:orch:plan              | (deprecated → plan-orchestrator skill)

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

## Skills (38 Auto-Activated)

Skills activate automatically from conversation context — no command needed.
Full catalog with trigger phrases: **[Skills & Agents](../skills-agents.md)**.

| Category | Count | Notable skills |
|----------|-------|----------------|
| Documentation | 8 | doc-classifier, mermaid-linter, changelog-automation, openapi-spec |
| Distribution | 6 | homebrew-formula/workflow/multi-formula/setup, pypi, marketplace |
| Orchestration | 4 | **drive-engine** (NEW), plan-orchestrator, task-analyzer, session-state |
| Workflow | 5 | **prompt-refiner** (NEW — `--refine`), adhd-workflow, **brainstorm**, **brainstorm-insights** (split from brainstorm), task-management |
| Design | 3 | backend / frontend / devops designers |
| Code · Testing · Guard&Insights | 2 each | lint/refactor, test-strategist/generator, guard-audit/insights-apply |
| Architecture · Check · CI · Dev · Modes · Planning · Release | 1 each | architecture, preflight-check, project-detector, git-workflow, mode-controller, project-planner, release |

> Newest: `drive-engine` (powers `/craft:orch:drive`) and `prompt-refiner`
> (powers the `--refine` flag, replacing the deprecated `/refine`).

## Agents (8 Specialized)

| Agent | Specialty | Triggers |
|-------|-----------|----------|
| `orchestrator-v2` | Complex multi-step tasks with parallel execution | `/craft:orch` |
| `orchestrator` | Legacy orchestrator | Direct invocation |
| `docs-architect` | Technical documentation, architecture guides | Docs requests |
| `api-documenter` | OpenAPI specs, developer portals | API documentation |
| `reference-builder` | Exhaustive technical references | Reference docs |
| `tutorial-engineer` | Step-by-step tutorials | Tutorial creation |
| `demo-engineer` | Interactive demos | Demo creation |
| `mermaid-expert` | Flowcharts, diagrams, MCP validation + rendering | Diagram requests |

---

## Release Pipeline

```
/release                  Interactive release pipeline (13 steps)
/release --dry-run        Preview release plan without executing
/release --autonomous     Fully automated (no prompts, auto-admin)

Pipeline: pre-flight -> bump -> commit -> PR -> CI monitor -> merge ->
          GitHub release -> docs deploy -> Homebrew tap -> sync dev ->
          verify CI on main -> downstream verification

Version bump: bump-version.sh syncs version across 13 files atomically
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
  /craft:ci:local        Pre-push validation
  /craft:code:release         PyPI release workflow
```

### R Package (DESCRIPTION detected)

```
SUGGESTED FOR R PACKAGE:

  /craft:do "check package"   Smart workflow
  /craft:test                 Run testthat
  /craft:code:release         CRAN submission prep
  /folio:site:build           Build pkgdown/altdoc site
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
│ {stats['total']} commands | {skill_count} skills | {agent_count} agents | {test_count} tests passing │
├────────────────────────────────────────────────────────────────────────┤
│ Start Here:                                                            │
│   /craft:do <task>   -> AI routes to best workflow                     │
│   /craft:check       -> Quick validation                               │
│   /craft:smart-help  -> Context-aware suggestions                      │
│                                                                        │
│ Development Workflow:                                                  │
│   /craft:code:lint [mode] -> /craft:test [mode] ->                     │
│   /craft:test --coverage -> /craft:ci:local -> ask "sync with remote"  │
│                                                                        │
│ Feature Development (dev/git skill — ask naturally):                  │
│   "create a worktree for feat/x" -> [develop] ->                       │
│   "finish worktree" -> "clean up worktree"                             │
│                                                                        │
│ Branch Protection (dev/git skill — ask naturally):                    │
│   "protect this branch"    -> Re-enable guard                         │
│   "unprotect"               -> Temporary bypass (auto-expires)         │
│   "show git status"        -> Show protection level                   │
│                                                                        │
│ Release Pipeline:                                                      │
│   /release                 -> Full 13-step pipeline                   │
│   /release --dry-run       -> Preview without executing               │
│   /release --autonomous    -> Fully automated release                 │
│                                                                        │
│ Orchestration:                                                         │
│   /craft:orch "task" optimize -> 4 parallel agents              │
│   /craft:do "task" --orch=optimize   -> Quick orchestration            │
│                                                                        │
│ Documentation:                                                         │
│   /craft:docs:update       -> Smart detection + generation             │
│   /craft:docs:claude-md:sync -> 4-phase CLAUDE.md pipeline            │
│   /folio:docs:lint         -> Markdown quality checks                  │
│   /folio:docs:check-links  -> Internal link validation                 │
│                                                                        │
│ Brainstorming:                                                         │
│   /brainstorm "topic"              -> Default depth                   │
│   /brainstorm deep feat s "auth"   -> Deep + feature + save spec      │
│   /brainstorm "API" --orch         -> Hand off to orchestrator        │
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
│   ask "git status" -> /craft:check -> ask "sync with remote"           │
└────────────────────────────────────────────────────────────────────────┘
```
