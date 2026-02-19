# /craft:hub - Command Discovery Hub

> **v2.5.0 Update**: Added `--orch` flag for quick orchestration across 5 key commands: `/craft:do`, `/craft:workflow:brainstorm`, `/craft:check`, `/craft:docs:sync`, `/craft:ci:generate`.
>
> **v2.4.0 Update**: Added brainstorm question control with colon notation (`d:5`, `m:12`, `q:3`) and categories flag (`-C req,tech,success`).

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
# - stats['total']: Total command count (e.g., 100)
# - stats['categories']: Dict of category counts (e.g., {'code': 12, 'test': 7, ...})
# - stats['with_modes']: Commands supporting modes
# - stats['with_dry_run']: Commands with dry-run support
# - commands: Full list of command objects with metadata
```

**Use this data** to populate the hub display below with accurate, auto-detected counts.

### Step 1: Detect Project Context

```
Detection Rules (check in order):
1. DESCRIPTION file → R Package
2. pyproject.toml → Python Package
3. package.json → Node.js Project
4. _quarto.yml → Quarto Project
5. mkdocs.yml → MkDocs Project
6. Otherwise → Generic Project
```

### Step 2: Display Hub (Layer 1 - Main Menu)

**Generate this display dynamically** using stats and commands data loaded in Step 0.

Replace placeholders:

- `[TOTAL]` → `stats['total']`
- `[CODE_COUNT]` → `stats['categories'].get('code', 0)`
- `[TEST_COUNT]` → `stats['categories'].get('test', 0)`
- `[DOCS_COUNT]` → `stats['categories'].get('docs', 0)`
- `[GIT_COUNT]` → `stats['categories'].get('git', 0)`
- `[SITE_COUNT]` → `stats['categories'].get('site', 0)`
- `[ARCH_COUNT]` → `stats['categories'].get('arch', 0)`
- `[PLAN_COUNT]` → `stats['categories'].get('plan', 0)`

Display template:

```
┌─────────────────────────────────────────────────────────────────────────┐
│  CRAFT - Full Stack Developer Toolkit v2.21.0                          │
│  [PROJECT_NAME] ([PROJECT_TYPE]) on [GIT_BRANCH]                       │
> **111 commands** | **25 skills** | **8 agents** | **~1575 tests passing**
├─────────────────────────────────────────────────────────────────────────┤
│ ⚡ SMART COMMANDS (Start Here):                                         │
│    /craft:do <task>     Universal command - AI routes to best workflow │
│    /craft:check         Pre-flight checks for commit/pr/release        │
│    /craft:smart-help    Context-aware help and suggestions             │
├─────────────────────────────────────────────────────────────────────────┤
│ 🎚️ MODES (default|debug|optimize|release):                             │
│    default  < 10s   Quick analysis, minimal output                     │
│    debug    < 120s  Verbose traces, detailed fixes                     │
│    optimize < 180s  Performance focus, parallel execution              │
│    release  < 300s  Comprehensive checks, full audit                   │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ 💻 CODE ([CODE_COUNT])              🧪 TEST ([TEST_COUNT])             │
│   /craft:code:debug                /craft:test:run [mode]               │
│   /craft:code:demo                 /craft:test:watch                    │
│   /craft:code:docs-check           /craft:test:coverage                 │
│   /craft:code:refactor             /craft:test:debug                    │
│   /craft:code:release                                                   │
│   /craft:code:test-gen           🏗️ ARCH ([ARCH_COUNT])                 │
│   /craft:code:lint [mode]          /craft:arch:analyze [mode]           │
│   /craft:code:coverage             /craft:arch:plan                     │
│   /craft:code:deps-check           /craft:arch:review                   │
│   /craft:code:deps-audit           /craft:arch:diagram                  │
│   /craft:code:ci-local                                                  │
│   /craft:code:ci-fix             📋 PLAN ([PLAN_COUNT])                 │
│                                    /craft:plan:feature                  │
│ 📄 DOCS ([DOCS_COUNT])             /craft:plan:sprint                   │
│   /craft:docs:sync                 /craft:plan:roadmap                  │
│   /craft:docs:changelog                                                 │
│   /craft:docs:claude-md          🔄 WORKFLOW ([WORKFLOW_COUNT])         │
│   /craft:docs:validate             /brainstorm [depth:count] "topic"    │
│   /craft:docs:nav-update           /brainstorm d:5 "auth" -C req,tech   │
│                                    /brainstorm m:12 "api" --categories  │
│ 🔀 GIT ([GIT_COUNT]+4 guides)      /workflow:focus                      │
│   /craft:git:init                  /workflow:next                       │
│   /craft:git:branch                /workflow:stuck                      │
│   /craft:git:sync                  /workflow:done                       │
│   /craft:git:clean                                                      │
│   /craft:git:recap               📦 DIST ([DIST_COUNT])                 │
│                                    /craft:dist:marketplace              │
│                                    /craft:dist:homebrew                 │
│                                    /craft:dist:curl-install             │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│  Quick Actions:                                                          │
│    /craft:do "fix bug"          /craft:check --for pr                    │
│    /craft:do "add auth" --orch=optimize  NEW (v2.5.0) Quick orchestration│
│    /brainstorm d:5 "auth"       /craft:help testing                      │
│    /craft:test:run debug        /craft:arch:analyze                      │
│    /craft:git:sync                                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**How to generate:**

1. Load stats and commands data (Step 0)
2. Replace all `[PLACEHOLDER]` values with actual data from stats
3. Display the completed hub menu
4. Optionally list top commands per category (first 5-6 from each)

**Category Navigation:**

- User can say `/craft:hub <category>` to see all commands in that category (Layer 2)
- User can say `/craft:hub <category>:<command>` for command details (Layer 3 - future)

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
        print(f"❌ Category '{category_arg}' not found or has no commands.")
        print(f"💡 Try: /craft:hub to see all categories")
    else:
        # Display Layer 2: Category View
        display_category_view(category_info)
else:
    # No category specified, show Layer 1 (Main Menu)
    display_main_menu()
```

### Step 2: Display Category View

**Generate this display using category_info data:**

Replace placeholders:

- `[CATEGORY]` → `category_info['name'].upper()`
- `[ICON]` → `category_info['icon']`
- `[COUNT]` → `category_info['count']`
- `[COMMANDS]` → Loop through `category_info['subcategories']`

Display template:

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
│ [SUBCATEGORY 2] ([count] commands)                              │
│   N. /craft:[category]:[commandN]          [description]       │
│   ...                                                           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 💡 Common Workflows:                                            │
│   • [Workflow 1 name]: [steps]                                  │
│   • [Workflow 2 name]: [steps]                                  │
│                                                                 │
│ 🔙 Back to hub: /craft:hub                                      │
│ 📚 Learn more: /craft:hub [category]:[command]                  │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation notes:**

1. Group commands by subcategory using `category_info['subcategories']`
2. For commands without subcategory, use 'general' group
3. Show mode indicator `[mode]` for commands that support modes
4. Keep descriptions under 40 characters
5. Number commands sequentially across all subcategories

**Example - CODE Category:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 💻 CODE COMMANDS (12 total)                                     │
│ Code Quality & Development Tools                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 ANALYSIS (6 commands)                                        │
│   1. /craft:code:lint [mode]        Code style & quality       │
│   2. /craft:code:coverage [mode]    Test coverage analysis     │
│   3. /craft:code:deps-check         Dependency health          │
│   4. /craft:code:deps-audit         Security vulnerabilities   │
│   5. /craft:code:ci-local           Run CI checks locally      │
│   6. /craft:code:ci-fix             Fix CI failures            │
│                                                                 │
│ 🏗️ DEVELOPMENT (6 commands)                                     │
│   7. /craft:code:debug              Systematic debugging       │
│   8. /craft:code:demo               Create demonstrations      │
│   9. /craft:code:test-gen           Generate test files        │
│  10. /craft:code:refactor           Refactoring guidance       │
│  11. /craft:code:release            Release workflow           │
│  12. /craft:code:docs-check         Pre-flight doc check       │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 💡 Common Workflows:                                            │
│   • Pre-commit: lint → test:run → ci-local                     │
│   • Debug: debug → test:debug → coverage                       │
│   • Release: deps-audit → test:run release → release           │
│                                                                 │
│ 🔙 Back to hub: /craft:hub                                      │
│ 📚 Learn more: /craft:hub code:[command]                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## Layer 3: Command Detail + Tutorial

When invoked with `/craft:hub <category>:<command>` (e.g., `/craft:hub code:lint`):

### Step 1: Parse Command Argument

```python
# Check if user provided command argument (category:command format)
import sys
command_arg = None  # Extract from user input (e.g., "code:lint")

if command_arg and ':' in command_arg:
    # User wants to see specific command detail
    from commands._discovery import get_command_detail, generate_command_tutorial

    command_info = get_command_detail(command_arg)

    if not command_info:
        print(f"❌ Command '{command_arg}' not found.")
        print(f"💡 Try: /craft:hub to browse all commands")
    else:
        # Display Layer 3: Command Detail + Tutorial
        tutorial = generate_command_tutorial(command_info)
        print(tutorial)
else:
    # No command specified, show Layer 2 or Layer 1
    # (logic for Layer 1/2 navigation)
    pass
```

### Step 2: Display Command Detail

The `generate_command_tutorial()` function creates a formatted display with:

1. **Header** - Command name and short description
2. **Description** - Detailed explanation of what the command does
3. **Modes** - Execution modes with time budgets (if applicable)
4. **Basic Usage** - Syntax examples with mode variations
5. **Common Workflows** - Real-world usage patterns
6. **Related Commands** - Similar/complementary commands for navigation
7. **Navigation Footer** - Links back to category and hub

**Example - CODE:LINT Command:**

```
┌─────────────────────────────────────────────────────────────────┐
│ 📚 COMMAND: /craft:code:lint                                    │
│ Code style and quality checks                                  │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ DESCRIPTION                                                     │
│ ───────────                                                     │
│ Runs project-specific linters (ruff, flake8, eslint, etc.)     │
│ to check code style and quality. Supports 4 execution modes    │
│ for different use cases.                                       │
│                                                                 │
│ MODES                                                           │
│ ─────                                                           │
│   default    (< 10s)      Quick checks, minimal output         │
│   debug      (< 120s)     Verbose with fix suggestions         │
│   optimize   (< 180s)     Performance focus, parallel execution│
│   release    (< 300s)     Comprehensive with security audit    │
│                                                                 │
│ BASIC USAGE                                                     │
│ ───────────                                                     │
│   /craft:code:lint                 # Default mode              │
│   /craft:code:lint debug           # Debug mode                │
│   /craft:code:lint release         # Release mode              │
│                                                                 │
│ COMMON WORKFLOWS                                                │
│ ────────────────                                                │
│                                                                 │
│ Pre-Commit:                                                     │
│   1. /craft:code:lint                                           │
│   2. /craft:test:run                                            │
│   3. git commit                                                 │
│                                                                 │
│ Debug Workflow:                                                 │
│   1. /craft:code:lint debug                                     │
│   2. Fix issues based on suggestions                           │
│   3. /craft:code:lint  (verify fixes)                           │
│                                                                 │
│ RELATED COMMANDS                                                │
│ ────────────────                                                │
│   /craft:test:run        Run tests                             │
│   /craft:code:ci-local   Full CI checks                        │
│   /craft:check           Universal validation                  │
│                                                                 │
│ 🔙 Back to CODE: /craft:hub code                                │
│ 🏠 Back to Hub: /craft:hub                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Implementation Notes:**

1. Command detail is generated dynamically from frontmatter metadata
2. Tutorial sections are auto-generated but can be enriched with custom tutorial files
3. Related commands are looked up to show their descriptions
4. Navigation links maintain the 3-layer hierarchy (Hub → Category → Command)

---

## Smart Commands (v2.5.0 Enhanced)

### `/craft:do <task>` - Universal Command with --orch (NEW v2.5.0)

```
Intelligently routes your task to the right workflow:

# Traditional routing (complexity-based)
 /craft:do initialize project    → git:init (interactive wizard)
 /craft:do add authentication    → arch:plan + code:test-gen + git:branch
 /craft:do fix login bug         → code:debug + test:run + test:debug
 /craft:do improve quality       → code:lint + test:coverage + code:refactor
 /craft:do prepare release       → deps-audit + test:run release + code:release

# NEW (v2.5.0) - Quick orchestration with --orch flag
/craft:do "add feature X" --orch           # Orchestrate with mode prompt
/craft:do "implement auth" --orch=optimize # Fast parallel orchestration
/craft:do "debug issue" --orch=debug       # Sequential troubleshooting
/craft:do "prep release" --orch=release    # Comprehensive audit
/craft:do "task" --orch --dry-run          # Preview orchestration plan
```

### `/craft:check` - Universal Pre-flight (v2.5.0 Enhanced)

```
Auto-detects project type and runs appropriate checks:

# Traditional validation
/craft:check                   Quick validation (lint + tests + types)
/craft:check --for commit      Pre-commit checks
/craft:check --for pr          Pre-PR validation (+ coverage + conflicts)
/craft:check --for release     Full release audit (+ security + docs)

# NEW (v2.5.0) - Orchestrated validation
/craft:check --orch            Orchestrated checks with mode prompt
/craft:check --orch=optimize   Fast parallel validation
/craft:check --orch=release    Comprehensive pre-release audit
```

### `/craft:help` - Context-Aware Help

```
/craft:help                    Shows relevant commands for your project
/craft:help testing            Deep dive into testing commands
/craft:help "how do I..."      Answer workflow questions
```

## Mode System (NEW!)

Many commands support modes for different use cases:

| Mode | Time Budget | Use Case |
|------|-------------|----------|
| **default** | < 10-30s | Day-to-day quick checks |
| **debug** | < 120s | Investigating issues, verbose output |
| **optimize** | < 180s | Performance focus, parallel execution |
| **release** | < 300s | Pre-release comprehensive checks |

### Mode Examples

```bash
/craft:code:lint                # default mode - quick
/craft:code:lint debug          # verbose with fix suggestions
/craft:code:lint release        # comprehensive with security

/craft:test:run                 # quick smoke tests
/craft:test:run debug           # verbose with traces
/craft:test:run optimize        # parallel execution
/craft:test:run release         # full suite with coverage

/craft:arch:analyze             # quick overview
/craft:arch:analyze debug       # deep pattern analysis
/craft:arch:analyze release     # full architectural audit
```

## Category Deep Dive

### `/craft:hub code`

```
💻 CODE COMMANDS (12)
─────────────────────────────────────────────────────────────────────────
Command                  │ Description                    │ Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:code:debug        │ Systematic debugging           │ -
/craft:code:demo         │ Create demonstrations          │ -
/craft:code:docs-check   │ Pre-flight doc check           │ -
/craft:code:refactor     │ Refactoring guidance           │ -
/craft:code:release      │ Release workflow               │ -
/craft:code:test-gen     │ Generate test files            │ -
/craft:code:lint         │ Code style & quality checks    │ ✓
/craft:code:coverage     │ Test coverage report           │ ✓
/craft:code:deps-check   │ Check dependency health        │ -
/craft:code:deps-audit   │ Security vulnerability scan    │ -
/craft:code:ci-local     │ Run CI checks locally          │ -
/craft:code:ci-fix       │ Fix CI failures                │ -
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub test`

```
🧪 TEST COMMANDS (4) - Testing & Quality
─────────────────────────────────────────────────────────────────────────
Command                  │ Description                    │ Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:test:run          │ Unified test runner            │ ✓
/craft:test:watch        │ Watch mode (re-run on change)  │ -
/craft:test:coverage     │ Coverage analysis              │ ✓
/craft:test:debug        │ Debug failing tests            │ -
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub arch`

```
🏗️ ARCH COMMANDS (4) - Architecture & Design
─────────────────────────────────────────────────────────────────────────
Command                  │ Description                    │ Modes
─────────────────────────┼────────────────────────────────┼─────────────
/craft:arch:analyze      │ Analyze architecture patterns  │ ✓
/craft:arch:plan         │ Design architecture            │ -
/craft:arch:review       │ Review architecture changes    │ -
/craft:arch:diagram      │ Generate Mermaid diagrams      │ -
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub plan`

```
📋 PLAN COMMANDS (3) - Planning & Project Management
─────────────────────────────────────────────────────────────────────────
Command                  │ Description
────────────────────────┼────────────────────────────────────────────
/craft:plan:feature      │ Plan features with tasks and estimates
/craft:plan:sprint       │ Sprint planning with capacity
/craft:plan:roadmap      │ Generate project roadmaps
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub workflow` (v2.5.0 Enhanced)

```
 WORKFLOW COMMANDS (4) - ADHD-Friendly Workflow Management
────────────────────────────────────────────────────────────────────────
Command                           │ Description
──────────────────────────────────┼────────────────────────────────────
/brainstorm [depth:count] "topic" │ Brainstorm with custom question counts
/brainstorm d:5 "auth"            │ Deep mode with exactly 5 questions
/brainstorm m:12 "api"            │ Max mode with 12 questions
/brainstorm q:0 "quick"           │ Quick with 0 questions (straight to brainstorming)
/brainstorm d:5 "auth" -C req,tech │ Filter to requirements + technical categories
/brainstorm d:20 "complex"        │ Unlimited mode with milestone prompts

# NEW (v2.5.0) - Orchestrated Brainstorming
/brainstorm "auth system" --orch           │ Orchestrated with mode prompt
/brainstorm "API design" --orch=optimize   │ Fast parallel context gathering
/brainstorm "complex feature" --orch=release │ Comprehensive analysis

/craft:insights                   │ Generate session insights report (v2.21.0)
/craft:insights --format html    │ HTML report for sharing
/craft:insights --since 7        │ Last 7 days only

/workflow:focus                   │ Start focused work session
/workflow:next                    │ Get next step
/workflow:stuck                   │ Get unstuck help
/workflow:done                    │ Complete session

**v2.5.0 Brainstorm Orchestration:**
- --orch flag for orchestrated brainstorming with multiple agents
- Combines question-based context gathering with agent analysis
- Optimized for comprehensive feature planning

**v2.4.0 Brainstorm Features:**
- Colon notation: d:5, m:12, q:3 for custom question counts
- Categories flag: -C req,tech,success to filter question types
- 8 categories: requirements, users, scope, technical, timeline, risks, existing, success
- Milestone prompts every 8 questions for unlimited exploration
────────────────────────────────────────────────────────────────────────
```

### `/craft:hub docs`

```
📄 DOCS COMMANDS (5) - Documentation Automation
─────────────────────────────────────────────────────────────────────────
Command                  │ Description
─────────────────────────┼────────────────────────────────────────────
/craft:docs:sync         │ Sync docs with code changes
/craft:docs:changelog    │ Auto-update CHANGELOG.md
/craft:docs:claude-md    │ CLAUDE.md management (init, sync, edit)
/craft:docs:validate     │ Validate links, code, structure
/craft:docs:nav-update   │ Update mkdocs.yml navigation
─────────────────────────────────────────────────────────────────────────

Reference Files (v2.22.0):
  .claude/reference/agents.md           │ Agent inventory (model, description)
  .claude/reference/test-suite.md       │ Test files with type classification
  .claude/reference/project-structure.md │ Directory tree, counts, version

  Generate/refresh: PYTHONPATH=. python3 utils/claude_md_sync.py --generate-reference
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub site`

```
📖 SITE COMMANDS (6) - Documentation Sites
─────────────────────────────────────────────────────────────────────────
Command                  │ R Package        │ Other (MkDocs)
─────────────────────────┼──────────────────┼─────────────────────
/craft:site:init         │ pkgdown/altdoc   │ mkdocs init
/craft:site:build        │ pkgdown::build   │ mkdocs build
/craft:site:preview      │ preview locally  │ mkdocs serve
/craft:site:deploy       │ gh-pages push    │ mkdocs gh-deploy
/craft:site:check        │ validate site    │ validate site
/craft:site:frameworks   │ compare options  │ compare options
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub git`

```
🔀 GIT COMMANDS (5 commands + 4 guides)
────────────────────────────────────────────────────────────────────────
Commands:
  /craft:git:init       Initialize repo with craft workflow
  /craft:git:branch     Branch management (create, switch, delete)
  /craft:git:sync       Smart sync with remote (pull, rebase, push)
  /craft:git:clean      Clean up merged branches safely
  /craft:git:recap      Git activity summary (what changed?)

Guides:
  /craft:git:refcard    Quick reference card
  /craft:git:undo-guide Emergency undo guide
  /craft:git:safety-rails Safety rails guide
  /craft:git:learning-guide Learning guide
────────────────────────────────────────────────────────────────────────
```

### `/craft:hub dist`

```
📦 DIST COMMANDS (7) - Distribution & Packaging
─────────────────────────────────────────────────────────────────────────
Command                  │ Description
─────────────────────────┼────────────────────────────────────────────
/craft:dist:marketplace  │ Marketplace init, validate, test, publish
/craft:dist:package      │ Package for distribution
/craft:dist:homebrew     │ Generate Homebrew formula
/craft:dist:pypi         │ Package for PyPI
/craft:dist:npm          │ Package for npm
/craft:dist:curl-install │ Generate curl installer

Recommended Install Hierarchy:
  1. Marketplace (Recommended) — works everywhere, one command
  2. Homebrew — macOS power users, auto-updates
  3. Manual — contributors and developers

Quick Examples:
  /craft:dist:marketplace validate   # Check marketplace config
  /craft:dist:marketplace init       # Generate marketplace.json
  /craft:dist:homebrew               # Generate Homebrew formula
─────────────────────────────────────────────────────────────────────────
```

### `/craft:hub workflow` (NEW v2.4.0)

```
🔄 WORKFLOW COMMANDS (4) - ADHD-Friendly Workflow Management
────────────────────────────────────────────────────────────────────────
Command                           │ Description
──────────────────────────────────┼────────────────────────────────────
/brainstorm [depth:count] "topic" │ Brainstorm with custom question counts
/brainstorm d:5 "auth"            │ Deep mode with exactly 5 questions
/brainstorm m:12 "api"            │ Max mode with 12 questions
/brainstorm q:0 "quick"           │ Quick with 0 questions
/brainstorm d:5 "auth" -C req,tech │ Filter to requirements + technical
/brainstorm d:20 "complex"        │ Unlimited mode with milestone prompts
/workflow:focus                   │ Start focused work session
/workflow:next                    │ Get next step
/workflow:stuck                   │ Get unstuck help
/workflow:done                    │ Complete session

**v2.4.0 Brainstorm Features:**
- Colon notation: d:5, m:12, q:3 for custom question counts
- Categories flag: -C req,tech,success to filter question types
- 8 categories: requirements, users, scope, technical, timeline, risks, existing, success
- Milestone prompts every 8 questions for unlimited exploration

**Quick Examples:**
/brainstorm d:5 "auth" -C req,tech     # 5 questions, filtered categories
/brainstorm m:10 f s "api"              # Max mode, feature, spec capture
/brainstorm d:20 "complex" -C all      # Unlimited with all categories
────────────────────────────────────────────────────────────────────────
```

## Skills (11 Auto-Activated)

| Skill | Category | Triggers On |
|-------|----------|-------------|
| `backend-designer` | Design | API design, database, auth discussions |
| `frontend-designer` | Design | UI/UX, components, accessibility |
| `devops-helper` | Design | CI/CD, deployment, Docker |
| `test-strategist` | Testing | Test strategy, coverage, flaky tests |
| `system-architect` | Architecture | System design, patterns, trade-offs |
| `project-planner` | Planning | Feature planning, sprints, roadmaps |
| `mode-controller` | Modes | Mode selection and behavior |
| `task-analyzer` | Orchestration | Task routing for /craft:do |
| `release` | Release | Release pipeline, version bump, deploy |
| `guard-audit` | DevOps | Guard friction, false positives, tune guard |
| `insights-apply` | Workflow | Insights report, CLAUDE.md rules, apply suggestions |

## Context-Aware Suggestions

### Python Package (pyproject.toml detected)

```
💡 SUGGESTED FOR PYTHON PROJECT:

  /craft:do "run all checks"  Smart workflow
  /craft:code:lint            Run ruff/flake8
  /craft:test:run             Run pytest
  /craft:code:ci-local        Pre-push validation
  /craft:code:release         PyPI release workflow
```

### R Package (DESCRIPTION detected)

```
💡 SUGGESTED FOR R PACKAGE:

  /craft:do "check package"   Smart workflow
  /craft:test:run             Run testthat
  /craft:code:release         CRAN submission prep
  /craft:site:init            Setup pkgdown/altdoc
  /craft:arch:analyze         Check package structure
```

### Node.js Project (package.json detected)

```
💡 SUGGESTED FOR NODE PROJECT:

  /craft:do "validate all"    Smart workflow
  /craft:code:lint            Run ESLint/Prettier
  /craft:test:run             Run Jest/Vitest
  /craft:code:deps-audit      Security scan
  /craft:code:release         npm publish workflow
```

## Quick Reference (v2.5.0)

```
┌────────────────────────────────────────────────────────────────────────┐
> Full-stack developer toolkit for Claude Code — 111 commands, 8 agents, 25 skills
├────────────────────────────────────────────────────────────────────────┤
│ Start Here:                                                            │
│   /craft:do <task>   → AI routes to best workflow                     │
│   /craft:check       → Quick validation                               │
│   /craft:help        → Context-aware suggestions                      │
│                                                                        │
│ v2.5.0 Quick Orchestration (--orch flag):                             │
│   /craft:do "add auth" --orch=optimize  → Quick parallel orchestration│
│   /craft:check --orch=release           → Orchestrated validation     │
│   /brainstorm "API" --orch              → Orchestrated brainstorming  │
│   /craft:docs:sync --orch               → Orchestrated docs sync      │
│   /craft:ci:generate --orch=optimize    → Orchestrated CI generation  │
│                                                                        │
│ v2.4.0 Brainstorm Question Control:                                    │
│   /brainstorm d:5 "auth"           → Deep mode with 5 questions       │
│   /brainstorm m:12 "api"           → Max mode with 12 questions       │
│   /brainstorm d:5 "auth" -C req,tech → Filter to specific categories  │
│   /brainstorm d:20 "complex"       → Unlimited with milestone prompts │
│                                                                        │
│ Development Workflow:                                                  │
│   /craft:code:lint [mode] → /craft:test:run [mode] →                  │
│   /craft:code:coverage → /craft:code:ci-local → /craft:git:sync       │
│                                                                        │
│ Architecture:                                                          │
│   /craft:arch:analyze [mode] → /craft:arch:plan → /craft:arch:diagram │
│                                                                        │
│ Distribution:                                                          │
│   /craft:dist:marketplace validate  → Check marketplace config        │
│   /craft:dist:marketplace init      → Generate marketplace.json       │
│   /craft:dist:homebrew              → Generate Homebrew formula        │
│                                                                        │
│ Before Release:                                                        │
│   /craft:check --for release  OR                                       │
│   /craft:code:deps-audit → /craft:test:run release →                  │
│   /craft:docs:changelog → /craft:code:release                          │
│                                                                        │
│ Instruction System (v2.22.0):                                         │
│   /craft:check                    → Includes instruction health check │
│   /workflow:done                  → Auto-syncs CLAUDE.md counts       │
│   --generate-reference            → Refresh .claude/reference/ files  │
│                                                                        │
│ Insights-Driven:                                                      │
│   /craft:guard:audit              → Audit guard config                │
│   /craft:insights:apply           → Apply insights to CLAUDE.md       │
│   /craft:check --context          → Front-load session context        │
│   /release --autonomous           → Fully automated release           │
│   /craft:git:worktree validate    → Verify worktree path              │
│   /craft:orchestrate --swarm      → Parallel agents in worktrees      │
│                                                                        │
│ Daily:                                                                 │
│   /craft:git:recap → /craft:check → /craft:git:sync                   │
│                                                                        │
│ Orchestrate Complex Tasks (Traditional):                               │
│   /craft:orchestrate "add auth" optimize  → Parallel agent execution  │
│   /craft:orchestrate "debug issue" debug  → Sequential troubleshooting│
│   /craft:orchestrate "prep release" release → Comprehensive audit     │
│   /craft:orchestrate status               → Agent dashboard           │
│   /craft:orchestrate timeline             → Execution timeline        │
│   /craft:orchestrate continue             → Resume previous session   │
│                                                                        │
│ NEW (v2.5.0) Quick Orchestration with --orch Flag:                     │
│   /craft:do "add feature" --orch=optimize  → Same as orchestrate      │
│   /craft:do "fix bug" --orch=debug         → Sequential troubleshooting│
│   /craft:check --orch=release             → Comprehensive validation  │
└────────────────────────────────────────────────────────────────────────┘
```

## Agents (8 Specialized)

| Agent | Specialty | Triggers |
|-------|-----------|----------|
| `orchestrator-v2` | Complex multi-step tasks with parallel execution | `/craft:orchestrate` |
| `backend-architect` | Scalable APIs, microservices, database design | Architecture tasks |
| `frontend-specialist` | React, Vue, component architecture | UI/UX discussions |
| `devops-engineer` | CI/CD, Docker, Kubernetes, deployment | Ops tasks |
| `test-strategist` | Test strategy, coverage, flaky tests | Testing needs |
| `docs-architect` | Technical documentation, architecture guides | Docs requests |
| `api-documenter` | OpenAPI specs, developer portals | API documentation |
| `mermaid-expert` | Flowcharts, diagrams, visualizations | Diagram requests |

### Orchestrator v2.1 (v2.5.0 Enhanced)

The orchestrator coordinates multiple agents for complex tasks:

**Traditional Method:**

```bash
/craft:orchestrate "implement feature X"       # Start with default mode
/craft:orchestrate "complex task" optimize     # Parallel execution (4 agents)
/craft:orchestrate "debug issue" debug         # Sequential troubleshooting
/craft:orchestrate "prep release" release      # Comprehensive audit
/craft:orchestrate status                      # Check agent progress
/craft:orchestrate timeline                    # View execution timeline
/craft:orchestrate continue                    # Resume previous session
```

**NEW (v2.5.0) Quick Orchestration with --orch Flag:**

```bash
# Quick orchestration from any supported command
/craft:do "implement feature X" --orch         # Same as orchestrate (default mode)
/craft:do "complex task" --orch=optimize       # Same as orchestrate optimize
/craft:do "debug issue" --orch=debug           # Same as orchestrate debug
/craft:do "prep release" --orch=release        # Same as orchestrate release

# Works with other commands too
/craft:check --orch=optimize                   # Orchestrated validation
/craft:brainstorm "API design" --orch          # Orchestrated brainstorming
/craft:docs:sync --orch                        # Orchestrated docs sync
/craft:ci:generate --orch=release              # Orchestrated CI generation
```

**Key Features:**

- Mode-aware execution (default/debug/optimize/release)
- Up to 4 parallel agents in optimize/release modes
- Chat compression for long sessions
- Session persistence and resumption
- ADHD-friendly progress tracking
- **NEW (v2.5.0)** --orch flag for quick orchestration
