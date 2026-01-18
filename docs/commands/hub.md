# /craft:hub — Command Discovery Hub v2.0

> **Smart 3-layer navigation system with auto-detection and progressive disclosure.** v2.4.0 adds workflow commands with brainstorm question control.

---

## Synopsis

```bash
# Layer 1: Main menu (browse all categories)
/craft:hub

# Layer 2: Category view (browse commands in a category)
/craft:hub <category>

# Layer 3: Command detail (view full tutorial for a command)
/craft:hub <category>:<command>
```

**Quick examples:**
```bash
# Show full hub (Layer 1)
/craft:hub

# Browse CODE category (Layer 2)
/craft:hub code

# View code:lint tutorial (Layer 3)
/craft:hub code:lint

# v2.4.0 Brainstorm with colon notation
/brainstorm d:5 "auth" -C req,tech
```

---

## What's New in v2.4.0

### Brainstorm Question Control
- **Colon notation** - `d:5`, `m:12`, `q:3` for custom question counts
- **Categories flag** - Filter questions by type (`-C req,tech,success`)
- **8-category question bank** - 16 questions total
- **Milestone prompts** - Every 8 questions for unlimited exploration

```bash
# Examples
/brainstorm d:5 "auth"              # Deep with exactly 5 questions
/brainstorm m:12 "api"              # Max with 12 questions
/brainstorm q:0 "quick"             # Quick with 0 questions
/brainstorm d:5 "auth" -C req,tech  # Filter to requirements + technical
/brainstorm d:20 "complex"          # Unlimited with milestones
```

### Hub v2.0 Core Features

Hub v2.0 introduces **intelligent auto-detection** and **3-layer progressive disclosure**:

### Auto-Detection Engine
- **Dynamic discovery** - Scans `commands/` directory automatically
- **Always accurate** - No hardcoded counts that drift out of sync
- **Fast caching** - JSON cache with auto-invalidation (<2ms cached, 12ms uncached)
- **100 commands** detected across 17 categories (v2.4.0)

### 3-Layer Navigation
1. **Layer 1 (Main Menu)** - Browse categories with counts
2. **Layer 2 (Category View)** - Browse commands by subcategory
3. **Layer 3 (Command Detail)** - View full tutorials

### ADHD-Friendly Design
- **Progressive disclosure** - Start broad, drill down as needed
- **Visual hierarchy** - Clear sections, icons, and formatting
- **No overwhelm** - Never show all 100 commands at once
- **Smart breadcrumbs** - Always know where you are

---

## Description

Central command discovery hub that shows all available craft commands organized by category. The v2.0 hub uses an auto-detection engine to dynamically discover commands and provides a 3-layer navigation system for exploring the toolkit.

**Key Features:**
- **Auto-detection** - Discovers commands from filesystem, always accurate
- **3-layer navigation** - Main Menu → Category View → Command Detail
- **Subcategory grouping** - Commands organized by purpose within categories
- **Auto-generated tutorials** - Command details from frontmatter metadata
- **Smart navigation** - Breadcrumbs maintain hierarchy
- **Mode system** - Execution modes with time budgets
- **Related commands** - Discover similar/complementary commands

---

## Layer 1: Main Menu

**Invocation:** `/craft:hub`

Shows all categories with auto-detected command counts:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT - Full Stack Developer Toolkit v2.4.0                          │
│ 📍 craft (Claude Plugin) on feature/brainstorm-question-control         │
│ 📊 100 Commands | 21 Skills | 8 Agents | 4 Modes                         │
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
│ 💻 CODE (12)              🧪 TEST (7)              📄 DOCS (19)         │
│   /craft:code:lint          /craft:test:run          /craft:docs:sync   │
│   /craft:code:coverage      /craft:test:watch        /craft:docs:check  │
│   /craft:code:deps-audit    /craft:test:coverage     /craft:docs:lint   │
│   /craft:code:ci-local      /craft:test:debug        ...                │
│                                                                         │
│ 🔀 GIT (11)               📖 SITE (16)             🏗️ ARCH (1)          │
│   /craft:git:worktree       /craft:site:build        /craft:arch:analyze│
│   /craft:git:sync           /craft:site:publish      ...                │
│   /craft:git:clean          /craft:site:deploy                          │
│   ...                       ...                                         │
│                                                                         │
│ 🚀 CI (3)                 📦 DIST (1)              📋 PLAN (3)          │
│ 🔄 WORKFLOW (2)           🎯 MORE...                                    │
│                                                                         │
│ 💡 TIP: Say "/craft:hub <category>" to explore a category              │
│         Example: /craft:hub code                                        │
└─────────────────────────────────────────────────────────────────────────┘
```

**Navigation:**
- Select any category to view Layer 2 (Category View)
- Example: `/craft:hub code` → Browse all CODE commands

---

## Layer 2: Category View

**Invocation:** `/craft:hub <category>`

Shows all commands in a category, grouped by subcategory:

### Example: `/craft:hub code`

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 💻 CODE COMMANDS (12 total)                                             │
│ Code Quality & Development Tools                                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ 🔍 ANALYSIS (6 commands)                                                │
│   1. /craft:code:lint [mode]        Code style & quality checks        │
│   2. /craft:code:coverage [mode]    Test coverage analysis             │
│   3. /craft:code:deps-check         Dependency health checks           │
│   4. /craft:code:deps-audit         Security vulnerability scan        │
│   5. /craft:code:ci-local           Run CI checks locally              │
│   6. /craft:code:ci-fix             Fix CI failures                    │
│                                                                         │
│ 🏗️ DEVELOPMENT (6 commands)                                             │
│   7. /craft:code:debug              Systematic debugging               │
│   8. /craft:code:demo               Create demonstrations              │
│   9. /craft:code:test-gen           Generate test files                │
│  10. /craft:code:refactor           Refactoring guidance               │
│  11. /craft:code:release            Release workflow                   │
│  12. /craft:code:docs-check         Documentation pre-flight           │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ 💡 Common Workflows:                                                    │
│   • Pre-commit: lint → test:run → ci-local                             │
│   • Debug: debug → test:debug → coverage                               │
│   • Release: deps-audit → test:run release → release                   │
│                                                                         │
│ 🔙 Back to hub: /craft:hub                                              │
│ 📚 Learn more: /craft:hub code:[command]                                │
└─────────────────────────────────────────────────────────────────────────┘
```

**Features:**
- **Subcategory grouping** - Commands organized by purpose
- **Mode indicators** - `[mode]` shows mode support
- **Command descriptions** - Short summaries for quick scanning
- **Common workflows** - Real-world usage patterns
- **Navigation breadcrumbs** - Back to hub, drill down to command detail

**All Categories:**
- `code` (12) - Code quality, linting, debugging, CI/CD
- `test` (7) - Testing, coverage, debugging
- `docs` (19) - Documentation generation, sync, validation
- `git` (11) - Branch management, worktree, sync
- `site` (16) - Documentation sites (MkDocs, Quarto, pkgdown)
- `arch` (1) - Architecture analysis
- `ci` (3) - CI/CD workflow generation
- `dist` (1) - Distribution and packaging
- `plan` (3) - Planning and project management
- `workflow` (4) - Workflow automation, brainstorming (v2.4.0)

---

## Layer 2: WORKFLOW Category (NEW v2.4.0)

**Invocation:** `/craft:hub workflow`

The WORKFLOW category contains commands for ADHD-friendly workflow management and brainstorming:

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 🔄 WORKFLOW COMMANDS (4)                                                │
│ ADHD-Friendly Workflow Management & Brainstorming                       │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ 🧠 BRAINSTORMING (3 commands)                                           │
│   1. /brainstorm [depth:count] "topic"  Brainstorm with question control│
│   2. /brainstorm d:5 "auth"             Deep mode with 5 questions      │
│   3. /brainstorm m:12 "api"             Max mode with 12 questions      │
│                                                                         │
│ 🎯 WORKFLOW MANAGEMENT (1 command)                                      │
│   4. /workflow:focus                     Start focused work session     │
│                                                                         │
├─────────────────────────────────────────────────────────────────────────┤
│ 💡 v2.4.0 Brainstorm Features:                                         │
│   • Colon notation: d:5, m:12, q:3 for custom question counts          │
│   • Categories flag: -C req,tech,success to filter question types      │
│   • 8 categories: requirements, users, scope, technical, timeline,     │
│     risks, existing, success (16 questions total)                       │
│   • Milestone prompts every 8 questions for unlimited exploration       │
│                                                                         │
│ 💡 Common Workflows:                                                    │
│   • Quick context: brainstorm q "topic"                                │
│   • Deep analysis: brainstorm d:8 "topic"                              │
│   • Focused categories: brainstorm d:5 "topic" -C req,tech             │
│   • Unlimited: brainstorm d:20 "topic"                                 │
│                                                                         │
│ 🔙 Back to hub: /craft:hub                                              │
│ 📚 Learn more: /craft:hub workflow:brainstorm                           │
└─────────────────────────────────────────────────────────────────────────┘
```

### Example: `/craft:hub workflow`

```
🔄 WORKFLOW COMMANDS (4)
🧠 BRAINSTORMING (3 commands):
  1. /brainstorm d:5 "auth"           Deep with 5 questions
  2. /brainstorm m:12 "api"           Max with 12 questions
  3. /brainstorm q:0 "quick"          Quick with 0 questions

🎯 WORKFLOW MANAGEMENT (1 command):
  4. /workflow:focus                  Start focused work session

💡 Common:
  /brainstorm d:5 "auth" -C req,tech  # Filtered categories
  /brainstorm d:20 "complex"          # Unlimited with milestones
```

---

## Layer 3: Command Detail + Tutorial

**Invocation:** `/craft:hub <category>:<command>`

Shows detailed documentation for a specific command:

### Example: `/craft:hub workflow:brainstorm`

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📚 COMMAND: /brainstorm                                                 │
│ ADHD-friendly brainstorming with question control (v2.4.0)             │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ SYNTAX                                                                 │
│ ──────                                                                 │
│   /brainstorm [depth:count] [focus] [action] [-C|--categories] "topic"│
│                                                                         │
│ ARGUMENTS                                                              │
│ ──────────                                                             │
│   depth:count  Question count (q:0, d:5, m:12, etc.)                   │
│   focus       feat|arch|api|ux|ops (default: auto-detect)              │
│   action      save|s (capture as spec)                                 │
│   -C categories  req,users,scope,technical,timeline,risks,existing,success│
│   topic       What to brainstorm (quoted string)                       │
│                                                                         │
│ MODES                                                                 │
│ ─────                                                                 │
│   default  2 questions + "ask more?"                                   │
│   quick    0 questions + "ask more?"                                   │
│   deep     8 questions + "ask more?"                                   │
│   max      8 questions + agents + "ask more?"                          │
│   custom   d:5, m:12, etc. (v2.4.0)                                    │
│                                                                         │
│ EXAMPLES                                                               │
│ ─────────                                                              │
│   /brainstorm "auth"                           Default mode            │
│   /brainstorm d:5 "auth"                       Deep with 5 questions   │
│   /brainstorm m:12 "api"                       Max with 12 questions   │
│   /brainstorm q:0 "quick"                      Quick with 0 questions  │
│   /brainstorm d:5 "auth" -C req,tech           Filtered categories     │
│   /brainstorm d:20 "complex"                   Unlimited with milestones│
│   /brainstorm d:5 f s "auth"                   Deep + feature + spec   │
│                                                                         │
│ QUESTIONS BANK (v2.4.0)                                                │
│ ────────────────                                                       │
│   8 categories × 2 questions = 16 total                                │
│   requirements, users, scope, technical, timeline, risks, existing,    │
│   success                                                               │
│                                                                         │
│ 🔙 Back to WORKFLOW: /craft:hub workflow                               │
│ 🏠 Back to Hub: /craft:hub                                             │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## Layer 3: Command Detail + Tutorial

**Invocation:** `/craft:hub <category>:<command>`

Shows full command tutorial with step-by-step instructions:

### Example: `/craft:hub code:lint`

```
┌─────────────────────────────────────────────────────────────────────────┐
│ 📚 COMMAND: /craft:code:lint                                            │
│ Code style and quality checks with mode support                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                         │
│ DESCRIPTION                                                             │
│ ───────────                                                             │
│ Runs project-specific linters (ruff, flake8, eslint, etc.) to check    │
│ code style and quality. Supports 4 execution modes for different use   │
│ cases from quick checks to comprehensive audits.                       │
│                                                                         │
│ MODES                                                                   │
│ ─────                                                                   │
│   default    (< 10s)      Quick checks, minimal output                 │
│   debug      (< 120s)     Verbose with fix suggestions                 │
│   optimize   (< 180s)     Performance focus, parallel execution        │
│   release    (< 300s)     Comprehensive with security audit            │
│                                                                         │
│ BASIC USAGE                                                             │
│ ───────────                                                             │
│   /craft:code:lint                 # Default mode (quick)              │
│   /craft:code:lint debug           # Debug mode (verbose)              │
│   /craft:code:lint release         # Release mode (thorough)           │
│                                                                         │
│ COMMON WORKFLOWS                                                        │
│ ────────────────                                                        │
│                                                                         │
│ Pre-Commit Workflow:                                                    │
│   1. /craft:code:lint                                                   │
│   2. /craft:test:run                                                    │
│   3. git commit -m "..."                                                │
│                                                                         │
│ Debug Workflow:                                                         │
│   1. /craft:code:lint debug                                             │
│   2. Fix issues based on suggestions                                   │
│   3. /craft:code:lint  (verify fixes)                                   │
│                                                                         │
│ RELATED COMMANDS                                                        │
│ ────────────────                                                        │
│   /craft:test:run        Run tests                                     │
│   /craft:code:ci-local   Full CI checks locally                        │
│   /craft:check           Universal validation                          │
│                                                                         │
│ 💡 TIP: Use /craft:check for automated lint + test + CI workflow       │
│                                                                         │
│ 🔙 Back to CODE: /craft:hub code                                        │
│ 🏠 Back to Hub: /craft:hub                                              │
└─────────────────────────────────────────────────────────────────────────┘
```

**Tutorial Sections:**
1. **Description** - Detailed explanation of what the command does
2. **Modes** - Execution modes with time budgets (if applicable)
3. **Basic Usage** - Syntax examples with mode variations
4. **Common Workflows** - Real-world usage patterns
5. **Related Commands** - Similar/complementary commands
6. **Tips** - Pro user hints
7. **Navigation** - Breadcrumbs back to category and hub

---

## Navigation Examples

### Browsing by Category

```bash
# Start at main menu
/craft:hub

# Select GIT category
/craft:hub git

# View worktree command tutorial
/craft:hub git:worktree
```

### Quick Command Lookup

```bash
# Jump directly to command detail
/craft:hub test:run
/craft:hub docs:sync
/craft:hub code:lint
```

### Category Deep Dive

```bash
# Explore all TEST commands
/craft:hub test

# Learn about specific test command
/craft:hub test:coverage

# Check related command
/craft:hub test:debug
```

---

## Mode System

Many commands support execution modes for different use cases:

| Mode | Time Budget | Use Case | Example |
|------|-------------|----------|---------|
| **default** | < 10s | Day-to-day quick checks | `/craft:code:lint` |
| **debug** | < 120s | Investigating issues | `/craft:code:lint debug` |
| **optimize** | < 180s | Performance focus | `/craft:code:lint optimize` |
| **release** | < 300s | Pre-release comprehensive | `/craft:code:lint release` |

**Mode indicators in hub:**
- Commands supporting modes show `[mode]` in Layer 2 (Category View)
- Layer 3 (Command Detail) shows all available modes with time budgets
- Use modes to balance speed vs. thoroughness

---

## Auto-Detection System

### How It Works

Hub v2.0 uses an auto-detection engine to discover commands:

1. **Scan** - Recursively scans `commands/` directory for `*.md` files
2. **Parse** - Extracts YAML frontmatter metadata from each file
3. **Infer** - Derives category from directory structure (`code/lint.md` → "code")
4. **Cache** - Stores discovered commands in JSON cache
5. **Invalidate** - Auto-invalidates cache when files change

### Performance

- **First run:** ~12ms (well under 200ms target, 94% faster)
- **Cached run:** <2ms (well under 10ms target, 80% faster)
- **Cache location:** `commands/_cache.json` (gitignored)

### Benefits

- **Always accurate** - Counts auto-update when commands added/removed
- **No maintenance** - No hardcoded lists to keep in sync
- **Fast** - JSON cache provides instant results
- **Reliable** - Auto-invalidation ensures freshness

---

## Command Frontmatter

Commands use YAML frontmatter for metadata discovery:

```yaml
---
name: "code:lint"                    # Command identifier
category: "code"                     # Primary category
subcategory: "analysis"              # Subcategory for grouping
description: "Code style & quality"  # One-line summary
modes: ["default", "debug", "optimize", "release"]  # Supported modes
time_budgets:                        # Time estimates per mode
  default: "< 10s"
  debug: "< 120s"
  release: "< 300s"
related_commands:                    # Navigation suggestions
  - "test:run"
  - "code:ci-local"
  - "check"
common_workflows:                    # Usage patterns
  - name: "Pre-commit"
    steps: ["code:lint", "test:run", "git commit"]
---
```

**Required fields:**
- `name` - Command identifier
- `category` - Primary category
- `description` - One-line summary

**Optional fields:**
- `subcategory` - For Layer 2 grouping
- `modes` - Execution modes
- `time_budgets` - Time estimates
- `related_commands` - Navigation
- `common_workflows` - Usage patterns
- `examples` - Usage examples

---

## Implementation Details

### Discovery Engine

**Location:** `commands/_discovery.py`

**Key Functions:**
```python
discover_commands()              # Scan and discover all commands
load_cached_commands()           # Load with auto-invalidation
get_command_stats()              # Get statistics

# Layer 2
get_commands_by_category(cat)    # Filter by category
group_commands_by_subcategory()  # Group by subcategory
get_category_info(cat)           # Complete category info

# Layer 3
get_command_detail(name)         # Lookup command by name
generate_command_tutorial(cmd)   # Auto-generate tutorial
```

### Cache Format

```json
{
  "generated": "2026-01-17T11:30:00Z",
  "count": 97,
  "commands": [
    {
      "name": "code:lint",
      "category": "code",
      "subcategory": "analysis",
      "description": "Code style & quality checks",
      "file": "code/lint.md",
      "modes": ["default", "debug", "optimize", "release"],
      "time_budgets": { "default": "< 10s", "debug": "< 120s" }
    }
  ]
}
```

### Test Coverage

- **34 tests** across 4 test suites
- **100% passing** (207ms total duration)
- Tests: discovery, integration, Layer 2, Layer 3
- Validation: accuracy, performance, format, navigation

---

## Tips & Best Practices

### For Quick Tasks
- Start with `/craft:do <task>` for smart routing
- Use default mode for fast checks
- Use `/craft:check` for comprehensive validation

### For Learning
- Start at Layer 1 (Main Menu) to browse categories
- Use Layer 2 (Category View) to scan available commands
- Use Layer 3 (Command Detail) for step-by-step tutorials

### For Power Users
- Jump directly to Layer 3: `/craft:hub code:lint`
- Use debug mode for verbose output
- Use release mode before deployments
- Check related commands for complementary tools

### For Plugin Developers
- Add frontmatter to new commands
- Run `python3 commands/_discovery.py` to regenerate cache
- Test with `python3 tests/test_hub_*.py`

---

## Troubleshooting

### Cache Issues

**Problem:** Counts seem wrong or outdated
**Solution:** Delete cache and regenerate:
```bash
rm commands/_cache.json
python3 commands/_discovery.py
```

### Command Not Found

**Problem:** `/craft:hub code:lint` says "not found"
**Solution:** Check command name format:
- Use `category:command` format (e.g., `code:lint`)
- Browse Layer 2 to find correct name: `/craft:hub code`

### Performance Issues

**Problem:** Hub seems slow
**Solution:** Check cache file exists:
```bash
ls -lh commands/_cache.json
# Should be < 100KB and recent timestamp
```

---

## Migration from v1.x

### Breaking Changes
- None - Hub v2.0 is fully backward compatible
- Old usage (`/craft:hub`, `/craft:hub code`) still works

### New Features
- Layer 3 command detail views
- Auto-detection (no hardcoded counts)
- Subcategory grouping
- Auto-generated tutorials
- Related commands navigation

### What to Update
- Add frontmatter to custom commands
- Regenerate cache after upgrade
- Update documentation if referencing command counts

---

## See Also

- **Smart routing:** `/craft:do` - Universal task command
- **Pre-flight:** `/craft:check` - Validation before commit/PR/release
- **Help:** `/craft:smart-help` - Context-aware suggestions
- **Orchestrator:** `/craft:orchestrate` - Multi-agent workflows
- **Discovery engine:** `commands/_discovery.py` - Implementation details
- **Test suite:** `tests/test_hub_*.py` - Validation tests
