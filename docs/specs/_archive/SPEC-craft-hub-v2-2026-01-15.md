# SPEC: /craft:hub v2.0 - Hierarchical Command Discovery System

**Status:** done
**Created:** 2026-01-15
**Completed:** 2026-01-18 (v1.24.0)
**Implementation:** PR #17, #20
**From Brainstorm:** BRAINSTORM-craft-hub-update-2026-01-15.md (deleted)

---

## Overview

Transform `/craft:hub` from a flat command list (89 commands overwhelming users) into an intelligent hierarchical discovery system with auto-detection, interactive tutorials, and progressive disclosure. Target new users who struggle to find the right command for their task.

**Key Innovation:** Three-layer hub system (main → category → command) with auto-generated metadata and step-by-step tutorials.

---

## Primary User Story

**As a** new Craft user
**I want** to easily discover and learn commands through guided navigation
**So that** I can accomplish tasks without memorizing 89 commands or asking for help

**Acceptance Criteria:**

1. ✅ I can find any command in ≤ 3 clicks from hub entry
2. ✅ Command counts are always accurate (no manual updates)
3. ✅ Each command shows description, modes, and tutorial link
4. ✅ Failed searches are tracked for continuous improvement
5. ✅ Tutorials teach me how to use commands step-by-step

---

## Secondary User Stories

### US-2: Power User Quick Navigation

**As a** power user
**I want** to jump directly to categories or search commands
**So that** I can find commands quickly without extra navigation

**Acceptance Criteria:**

- ✅ Can invoke `/craft:hub <category>` to skip main menu
- ✅ Can search with `/craft:hub search <query>`
- ✅ Hub remembers my frequent commands (future)

---

### US-3: Maintainer Auto-Updates

**As a** Craft maintainer
**I want** command counts and metadata auto-detected from files
**So that** I don't manually update hub when commands change

**Acceptance Criteria:**

- ✅ Hub scans `commands/` directory on invocation
- ✅ Parses YAML frontmatter for metadata
- ✅ Displays accurate counts without hardcoded numbers
- ✅ Caches results for performance

---

### US-4: Tutorial Author Contributions

**As a** tutorial author
**I want** a standard template for writing command tutorials
**So that** I can create consistent, helpful learning content

**Acceptance Criteria:**

- ✅ Tutorial template exists with sections (What, Steps, Workflows, Related)
- ✅ Tutorials are markdown files in `commands/tutorials/`
- ✅ Hub auto-detects tutorials linked in command frontmatter
- ✅ Tutorial format is beginner-friendly (step-by-step text)

---

## Technical Requirements

### Architecture

#### Three-Layer Hub System

```
Layer 1: Main Menu
├── Entry point: /craft:hub
├── Display: 10 categories + smart commands
├── Navigation: AskUserQuestion (4 options max)
└── Output: Minimal (200 chars)

Layer 2: Category View
├── Entry point: /craft:hub <category>
├── Display: All commands in category (grouped by subcategory)
├── Navigation: AskUserQuestion OR direct command selection
└── Output: Moderate (500 chars)

Layer 3: Command Detail + Tutorial
├── Entry point: /craft:hub <category>:<command>
├── Display: Full docs + tutorial + examples
├── Navigation: Links to related commands, back to category
└── Output: Maximum (2000 chars)
```

---

### Auto-Detection System

#### Component: Command Discovery Engine

**File:** `commands/_discovery.py`

**Responsibilities:**

1. Scan `commands/` directory recursively for `*.md` files
2. Parse YAML frontmatter from each file
3. Extract metadata: name, category, description, modes, tutorial
4. Cache results in `commands/_cache.json`
5. Rebuild cache when command files change

**Pseudocode:**

```python
def discover_commands():
    """Auto-detect all commands from filesystem."""
    commands = []

    for filepath in glob("commands/**/*.md", recursive=True):
        # Skip private/helper files
        if filepath.startswith("commands/_"):
            continue

        # Parse frontmatter
        with open(filepath) as f:
            content = f.read()
            metadata = parse_yaml_frontmatter(content)

        # Infer category from directory structure
        category = infer_category(filepath)

        commands.append({
            "name": metadata.get("name"),
            "category": category,
            "subcategory": metadata.get("subcategory"),
            "description": metadata.get("description"),
            "modes": metadata.get("modes", []),
            "tutorial": metadata.get("tutorial", False),
            "tutorial_level": metadata.get("tutorial_level"),
            "related_commands": metadata.get("related_commands", []),
            "tags": metadata.get("tags", []),
            "file": filepath
        })

    return commands

def infer_category(filepath):
    """Extract category from file path."""
    # commands/code/lint.md → "code"
    # commands/git/worktree.md → "git"
    # commands/hub.md → "hub" (special case)
    parts = filepath.split("/")
    if len(parts) >= 2:
        return parts[1]
    return "misc"

def cache_commands(commands):
    """Save to cache file for performance."""
    with open("commands/_cache.json", "w") as f:
        json.dump({
            "generated": datetime.now().isoformat(),
            "count": len(commands),
            "commands": commands
        }, f, indent=2)

def load_cached_commands():
    """Load from cache if fresh, else regenerate."""
    cache_file = "commands/_cache.json"

    if os.path.exists(cache_file):
        # Check if cache is stale (any .md file newer than cache)
        cache_mtime = os.path.getmtime(cache_file)
        commands_mtime = max(
            os.path.getmtime(f)
            for f in glob("commands/**/*.md", recursive=True)
        )

        if cache_mtime >= commands_mtime:
            # Cache is fresh
            with open(cache_file) as f:
                return json.load(f)["commands"]

    # Cache is stale or missing, regenerate
    commands = discover_commands()
    cache_commands(commands)
    return commands
```

**Performance:**

- First run: ~200ms (scan + parse + cache)
- Subsequent runs: ~10ms (load from cache)
- Auto-invalidates when command files change

---

### Command Metadata Schema

#### Enhanced Frontmatter

**File:** `commands/_schema.json` (documentation only, not enforced)

**Required Fields:**

```yaml
---
name: "code:lint"                    # Command identifier
category: "code"                     # Primary category
description: "Code style & quality"  # One-line summary (< 60 chars)
---
```

**Optional Fields:**

```yaml
---
subcategory: "analysis"              # Subcategory for grouping
modes: ["default", "debug", "release"]  # Supported execution modes
time_budgets:                        # Time estimates per mode
  default: "< 10s"
  debug: "< 120s"
  release: "< 300s"
tutorial: true                       # Has tutorial available?
tutorial_level: "beginner"           # beginner|intermediate|advanced
tutorial_file: "tutorials/code-lint.md"  # Path to tutorial
related_commands:                    # Related commands for navigation
  - "test:run"
  - "code:ci-local"
  - "check"
common_workflows:                    # Real-world usage patterns
  - name: "Pre-commit"
    steps: ["code:lint", "test:run", "git commit"]
  - name: "Debug"
    steps: ["code:lint debug", "fix issues", "code:lint"]
tags: ["quality", "style", "linting"]  # Searchable tags
project_types: ["python", "node", "r"]  # Applicable project types
examples:                            # Usage examples
  - command: "/craft:code:lint"
    description: "Quick validation"
  - command: "/craft:code:lint debug"
    description: "Verbose with fix suggestions"
---
```

**Migration Plan:**

- Phase 1: Add required fields to all 89 commands
- Phase 2: Add tutorials to top 10 commands
- Phase 3: Add workflows to top 20 commands
- Phase 4: Complete all optional fields

---

### UI Design

#### Layer 1: Main Menu

**Invocation:** `/craft:hub`

**Display:**

```markdown
┌─────────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT COMMAND HUB - Choose a Category                        │
│ 89 Commands | 21 Skills | 8 Agents                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🚀 GETTING STARTED (Recommended for new users)                 │
│    Quick Start Tutorial                                        │
│    Common Workflows                                            │
│    Smart Commands (do, check, help)                            │
│                                                                 │
│ 📂 BROWSE BY CATEGORY                                          │
│    💻 CODE (11)      🧪 TEST (3)      📄 DOCS (10)             │
│    🔀 GIT (7)        📖 SITE (5)      🏗️ ARCH (1)              │
│    🚀 CI (3)         📦 DIST (1)      📋 PLAN (3)              │
│    🔄 WORKFLOW (2)   🎯 ORCHESTRATE (1)                        │
│                                                                 │
│ 🔍 SEARCH & FILTER                                             │
│    /craft:hub search <keyword>                                 │
│    /craft:hub tutorial                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

**AskUserQuestion:**

```python
AskUserQuestion:
  question: "Which category would you like to explore?"
  header: "Category"
  multiSelect: false
  options:
    - label: "🚀 Getting Started (Recommended)"
      description: "Tutorials and common workflows for new users"
    - label: "💻 CODE (11 commands)"
      description: "Lint, test, debug, CI/CD, release"
    - label: "🔀 GIT (7 commands)"
      description: "Branch, sync, worktree, clean, recap"
    - label: "📄 DOCS (10 commands)"
      description: "Sync, changelog, validation, tutorials"
```

**Interaction Flow:**

1. Show main menu (auto-detected counts)
2. User selects category (via AskUserQuestion)
3. Navigate to Layer 2 (category view)

---

#### Layer 2: Category View

**Invocation:** `/craft:hub <category>` (e.g., `/craft:hub code`)

**Display:**

```markdown
┌─────────────────────────────────────────────────────────────────┐
│ 💻 CODE COMMANDS (11 total)                                     │
│ Code Quality & Development Tools                               │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 ANALYSIS (5 commands)                                        │
│   1. /craft:code:lint [mode]        Code style & quality       │
│   2. /craft:code:coverage [mode]    Test coverage analysis     │
│   3. /craft:code:deps-check         Dependency health          │
│   4. /craft:code:deps-audit         Security vulnerabilities   │
│   5. /craft:code:debug              Systematic debugging       │
│                                                                 │
│ 🏗️ DEVELOPMENT (3 commands)                                     │
│   6. /craft:code:test-gen           Generate test files        │
│   7. /craft:code:refactor           Refactoring guidance       │
│   8. /craft:code:demo               Create demonstrations      │
│                                                                 │
│ 🚀 CI/CD (2 commands)                                           │
│   9. /craft:code:ci-local           Run CI checks locally      │
│  10. /craft:code:ci-fix             Fix CI failures            │
│                                                                 │
│ 📦 RELEASE (1 command)                                          │
│  11. /craft:code:release            Release workflow           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 💡 Common Workflows:                                            │
│   • Pre-commit: lint → test:run → ci-local                     │
│   • Debug: debug → test:debug → coverage                       │
│   • Release: deps-audit → test:run release → release           │
│                                                                 │
│ 📚 View tutorials: /craft:hub code:tutorial                     │
│ 🔙 Back to hub: /craft:hub                                      │
└─────────────────────────────────────────────────────────────────┘
```

**AskUserQuestion:**

```python
AskUserQuestion:
  question: "Select a command to learn more (or choose an option below)"
  header: "Command"
  multiSelect: false
  options:
    - label: "1. /craft:code:lint [mode]"
      description: "Code style & quality checks (tutorial available)"
    - label: "2. /craft:code:coverage [mode]"
      description: "Test coverage analysis"
    - label: "3. /craft:code:deps-check"
      description: "Check dependency health"
    - label: "📚 View all CODE tutorials"
      description: "Interactive learning for all CODE commands"
```

**Interaction Flow:**

1. Show category commands (grouped by subcategory)
2. User selects command number (via AskUserQuestion)
3. Navigate to Layer 3 (command detail)

---

#### Layer 3: Command Detail + Tutorial

**Invocation:** `/craft:hub <category>:<command>` (e.g., `/craft:hub code:lint`)

**Display:**

```markdown
┌─────────────────────────────────────────────────────────────────┐
│ 📚 COMMAND: /craft:code:lint                                    │
│ Code style & quality checks                                    │
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
│   default  (< 10s)    Quick checks, minimal output             │
│   debug    (< 120s)   Verbose with fix suggestions             │
│   optimize (< 180s)   Performance focus, parallel execution    │
│   release  (< 300s)   Comprehensive with security audit        │
│                                                                 │
│ BASIC USAGE                                                     │
│ ───────────                                                     │
│   /craft:code:lint                  # Default mode             │
│   /craft:code:lint debug            # Debug mode               │
│   /craft:code:lint release          # Release mode             │
│                                                                 │
│ TUTORIAL (STEP-BY-STEP)                                         │
│ ───────────────────────                                         │
│                                                                 │
│ Step 1: Quick Check (Daily Development)                        │
│ ───────────────────────────────────                             │
│   $ /craft:code:lint                                            │
│                                                                 │
│   Runs fast validation (< 10s) with essential checks.          │
│   Perfect for quick validation during development.             │
│                                                                 │
│ Step 2: Debug Mode (When You Have Issues)                      │
│ ──────────────────────────────────────                          │
│   $ /craft:code:lint debug                                      │
│                                                                 │
│   Runs verbose analysis (< 120s) with detailed fix             │
│   suggestions. Use when investigating errors or learning       │
│   best practices.                                              │
│                                                                 │
│ Step 3: Release Mode (Before Deployment)                       │
│ ─────────────────────────────────────                           │
│   $ /craft:code:lint release                                    │
│                                                                 │
│   Runs comprehensive checks (< 300s) including security        │
│   audit. Use before releases for production readiness.         │
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
│   /craft:test:run       Run tests                              │
│   /craft:code:ci-local  Full CI checks                         │
│   /craft:check          Universal validation                   │
│                                                                 │
│ 💡 TIP: Use /craft:check for automated lint + test + CI        │
│                                                                 │
│ 🔙 Back to CODE: /craft:hub code                                │
│ 🏠 Back to Hub: /craft:hub                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Tutorial Template Structure:**

1. **Description** (1-2 sentences, what it does)
2. **Modes** (table of execution modes with time budgets)
3. **Basic Usage** (syntax examples)
4. **Tutorial** (3-5 step-by-step instructions with real examples)
5. **Common Workflows** (real-world usage patterns)
6. **Related Commands** (navigation to similar/complementary commands)
7. **Tips** (pro user hints)

---

### Failed Search Tracking

#### Component: Search Analytics Engine

**File:** `commands/_search_failures.jsonl`

**Format:**

```json
{"timestamp": "2026-01-15T14:30:00Z", "query": "deploy website", "context": "mkdocs project", "project_type": "mkdocs"}
{"timestamp": "2026-01-15T14:35:00Z", "query": "run ci", "context": "python package", "project_type": "python"}
```

**Usage:**

```python
def track_failed_search(query, context):
    """Log when user searches but finds nothing."""
    with open("commands/_search_failures.jsonl", "a") as f:
        f.write(json.dumps({
            "timestamp": datetime.now().isoformat(),
            "query": query,
            "context": context,
            "project_type": detect_project_type()
        }) + "\n")

    # Show helpful fallback
    print("❌ No commands found for:", query)
    print()
    print("💡 Try:")
    print("  - Browse by category: /craft:hub")
    print("  - Smart command: /craft:do", query)
    print("  - Get help: /craft:smart-help", query)
```

**Analytics:**

```bash
# Monthly review of failed searches
$ python3 commands/_analytics.py report --month 2026-01

Top 10 Failed Searches:
  1. "deploy website" (12 occurrences) → Need /craft:site:deploy tutorial
  2. "run ci" (8 occurrences) → Need CI category in main menu
  3. "fix tests" (6 occurrences) → Need /craft:test:debug tutorial
  ...

Suggested Improvements:
  - Add "deploy" as synonym for "site:deploy"
  - Promote CI commands to main menu
  - Create troubleshooting tutorials for top 5 queries
```

---

## Data Models

### Command Metadata (JSON Schema)

```json
{
  "$schema": "http://json-schema.org/draft-07/schema#",
  "type": "object",
  "required": ["name", "category", "description"],
  "properties": {
    "name": {
      "type": "string",
      "pattern": "^[a-z0-9:_-]+$",
      "description": "Command identifier (e.g., 'code:lint')"
    },
    "category": {
      "type": "string",
      "enum": ["code", "test", "docs", "git", "site", "arch", "plan", "ci", "dist", "workflow", "orchestrate"],
      "description": "Primary category"
    },
    "subcategory": {
      "type": "string",
      "description": "Optional subcategory for grouping"
    },
    "description": {
      "type": "string",
      "maxLength": 60,
      "description": "One-line summary"
    },
    "modes": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["default", "debug", "optimize", "release"]
      },
      "description": "Supported execution modes"
    },
    "time_budgets": {
      "type": "object",
      "properties": {
        "default": {"type": "string"},
        "debug": {"type": "string"},
        "optimize": {"type": "string"},
        "release": {"type": "string"}
      }
    },
    "tutorial": {
      "type": "boolean",
      "description": "Has tutorial available?"
    },
    "tutorial_level": {
      "type": "string",
      "enum": ["beginner", "intermediate", "advanced"]
    },
    "tutorial_file": {
      "type": "string",
      "description": "Path to tutorial markdown"
    },
    "related_commands": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Related command names"
    },
    "common_workflows": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["name", "steps"],
        "properties": {
          "name": {"type": "string"},
          "steps": {
            "type": "array",
            "items": {"type": "string"}
          }
        }
      }
    },
    "tags": {
      "type": "array",
      "items": {"type": "string"},
      "description": "Searchable tags"
    },
    "project_types": {
      "type": "array",
      "items": {
        "type": "string",
        "enum": ["python", "node", "r", "quarto", "mkdocs", "generic"]
      }
    },
    "examples": {
      "type": "array",
      "items": {
        "type": "object",
        "required": ["command", "description"],
        "properties": {
          "command": {"type": "string"},
          "description": {"type": "string"}
        }
      }
    },
    "file": {
      "type": "string",
      "description": "Source file path (auto-generated)"
    }
  }
}
```

---

### Command Cache Format

```json
{
  "generated": "2026-01-15T14:30:00Z",
  "count": 89,
  "categories": {
    "code": 11,
    "test": 3,
    "docs": 10,
    "git": 7,
    "site": 5,
    "arch": 1,
    "plan": 3,
    "ci": 3,
    "dist": 1,
    "workflow": 2,
    "orchestrate": 1
  },
  "commands": [
    {
      "name": "code:lint",
      "category": "code",
      "subcategory": "analysis",
      "description": "Code style & quality checks",
      "modes": ["default", "debug", "optimize", "release"],
      "tutorial": true,
      "tutorial_level": "beginner",
      "tutorial_file": "commands/tutorials/code-lint.md",
      "related_commands": ["test:run", "code:ci-local", "check"],
      "tags": ["quality", "style", "linting"],
      "file": "commands/code/lint.md"
    }
  ]
}
```

---

## Dependencies

### External Libraries (None Required)

All functionality can be implemented with:

- **Python Standard Library:** `os`, `glob`, `json`, `yaml` (frontmatter parsing)
- **Existing Craft Tools:** `AskUserQuestion`, file I/O tools

### New Internal Components

| File | Purpose |
|------|---------|
| `commands/_discovery.py` | Auto-detect commands from filesystem |
| `commands/_cache.json` | Generated command metadata cache |
| `commands/_search_failures.jsonl` | Failed search log |
| `commands/_analytics.py` | Search analytics & reporting |
| `commands/_schema.json` | Metadata schema documentation |
| `commands/tutorials/*.md` | Command tutorial files |

---

## UI/UX Specifications

### User Flow: New User Finding a Command

```
User invokes: /craft:hub
  ↓
[Layer 1: Main Menu]
Shows: 11 categories + Getting Started + Search
User selects: "💻 CODE (11 commands)"
  ↓
[Layer 2: Category View]
Shows: 11 code commands grouped by subcategory
User selects: "1. /craft:code:lint [mode]"
  ↓
[Layer 3: Command Detail + Tutorial]
Shows: Full documentation with step-by-step tutorial
User learns: How to use code:lint in 3 scenarios
  ↓
User runs: /craft:code:lint debug
  ↓
Success! User learned and executed command in < 30s
```

---

### User Flow: Power User Quick Access

```
User invokes: /craft:hub code
  ↓
[Layer 2: Category View] (skipped Layer 1)
Shows: All CODE commands
User selects: Command number or name
  ↓
[Layer 3: Command Detail]
User reviews: Quick reference
  ↓
User runs: Command directly
```

---

### User Flow: Search Workflow

```
User invokes: /craft:hub search "deploy website"
  ↓
[Search Results]
Found: 2 matching commands
  1. /craft:site:deploy     - Deploy documentation site
  2. /craft:site:build      - Build documentation site
User selects: "1. /craft:site:deploy"
  ↓
[Layer 3: Command Detail + Tutorial]
Shows: Tutorial for deployment
User learns: How to deploy with mkdocs
  ↓
User runs: /craft:site:deploy
```

---

### Accessibility Checklist

- ✅ Clear hierarchy (3 levels max)
- ✅ Keyboard navigation (number selection)
- ✅ Screen reader friendly (no ASCII art tables)
- ✅ High contrast text (unicode symbols + text labels)
- ✅ Short descriptions (< 60 chars)
- ✅ Breadcrumb navigation (back links at each level)

---

## Open Questions

1. **Tutorial Authoring:**
   - Who writes tutorials? (Answer: Phase 1 = maintainers, Phase 2 = community contributions)
   - Should tutorials be auto-generated from command examples? (Answer: No, manual curation for quality)

2. **Search Syntax:**
   - Should search support filters like `mode:debug category:code`? (Answer: Phase 1 = simple text search, Phase 2 = advanced filters)
   - How to handle synonyms (e.g., "fix" → "debug")? (Answer: Create synonym map in `_discovery.py`)

3. **Offline Mode:**
   - Should hub work without internet (for analytics)? (Answer: Yes, all local files, no network required)

4. **Command Aliases:**
   - Should hub suggest shorter aliases for frequent commands? (Answer: Phase 3 feature, personalization)

5. **IDE Integration:**
   - Should hub integrate with VS Code/Cursor autocomplete? (Answer: Future enhancement, out of scope for v2.0)

---

## Review Checklist

Before implementing, verify:

- ✅ **Auto-detection** works for all 89 commands
- ✅ **Frontmatter schema** is documented and examples exist
- ✅ **Tutorial template** is finalized and tested with 1 command
- ✅ **Main menu** categories are stable (no major reorganization planned)
- ✅ **Failed search tracking** doesn't violate privacy (local only, no external logging)
- ✅ **Performance** is acceptable (< 100ms for cached loads)
- ✅ **Navigation** is intuitive for new users (user testing with 3 people)

---

## Implementation Notes

### Phase 1: Foundation (Week 1)

**Files to Create:**

```
commands/
├── _discovery.py          # Auto-detection engine
├── _cache.json            # Generated metadata (gitignored)
├── _search_failures.jsonl # Failed search log (gitignored)
├── _analytics.py          # Analytics tools
└── _schema.json           # Metadata schema docs
```

**Files to Update:**

```
commands/hub.md            # Main hub command (Layer 1 + 2 + 3)
.gitignore                 # Ignore cache and log files
```

**Approach:**

1. Implement `_discovery.py` first (core auto-detection)
2. Test with 10 commands to validate parsing
3. Update `hub.md` to use auto-detected data
4. Add failed search tracking to search fallback
5. Verify counts are accurate (89 commands)

---

### Phase 2: Metadata Enhancement (Week 2)

**Tasks:**

1. Create `_schema.json` with full metadata schema
2. Update all 89 command files with enhanced frontmatter:
   - Required: `name`, `category`, `description`
   - Optional: `modes`, `tutorial`, `related_commands`, `tags`
3. Create category groupings (subcategories)
4. Add common workflows to top 20 commands

**Migration Script:**

```bash
# Bulk add required frontmatter to all commands
python3 scripts/migrate-frontmatter.py --add-required

# Validate all frontmatter
python3 scripts/validate-frontmatter.py
```

---

### Phase 3: Tutorials (Week 3-4)

**Tasks:**

1. Create tutorial template: `commands/tutorials/_TEMPLATE.md`
2. Write tutorials for top 10 commands:
   - `code:lint`, `test:run`, `git:worktree`, `site:deploy`
   - `check`, `do`, `arch:analyze`, `code:ci-local`
   - `docs:changelog`, `git:sync`
3. Link tutorials in command frontmatter
4. Add tutorial navigation to Layer 3

**Tutorial Template:**

```markdown
# Tutorial: /craft:<command>

## What It Does
[1-2 sentence summary]

## Step-by-Step Guide

### Step 1: [Scenario Name]
```bash
$ /craft:<command>
```

[Explanation of what happens and when to use]

### Step 2: [Scenario Name]

```bash
/craft:<command> <mode>
```

[Explanation of what happens and when to use]

## Common Workflows

### Workflow 1: [Name]

1. Step
2. Step
3. Step

## Related Commands

- [Command] - [Why related]

## Tips

💡 [Pro user hint]

```

---

### Phase 4: Testing & Refinement (Week 5)

**User Testing:**
1. Recruit 3 new Craft users (never used before)
2. Give task: "Find and run the command to check code quality"
3. Observe: How long? How many clicks? Did they succeed?
4. Iterate based on feedback

**Success Metrics:**
- Time to find command: < 30s (target: 15s)
- Clicks to command: ≤ 3 (target: 2)
- Success rate: 100% (all 3 users find it)

**Refinements:**
- Adjust category names based on user feedback
- Reorder categories by usage frequency
- Add missing tutorials based on user requests

---

## History

| Date | Change | Author |
|------|--------|--------|
| 2026-01-15 | Initial spec created from brainstorm | DT |

---

## Related Specifications

- `/craft:do` - Smart command execution (hub's complement)
- `/craft:check` - Universal validation
- `/craft:smart-help` - Context-aware help system

---

**Spec Status:** Ready for review
**Next Step:** Implement Phase 1 (Foundation) on `feature/hub-v2` branch
