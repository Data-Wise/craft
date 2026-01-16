# BRAINSTORM: Deep Update to /craft:hub

**Generated:** 2026-01-15
**Context:** Craft Plugin - Command Discovery Hub Enhancement
**Mode:** Deep (10 questions + comprehensive analysis)
**Duration:** ~10 minutes

---

## 📊 Current State Analysis

### Metrics
- **Commands:** 89 actual (hub shows outdated 47)
- **Skills:** 21 auto-activated
- **Agents:** 8 specialized
- **Categories:** 11+ (code, test, docs, git, site, arch, plan, ci, dist, workflow, orchestrate)

### Pain Points Identified
1. **Poor Discoverability** (Primary) - Users can't find the right command for their task
2. **Information Overload** - 89 commands shown at once overwhelms new users
3. **Outdated Information** - Manual counts drift (47 vs 89), maintenance burden
4. **No Learning Path** - Flat hierarchy doesn't guide beginners
5. **No Failed Search Tracking** - Can't improve when users struggle to find commands

### User Insights (From Questions)
- **Target User:** New users (first-time, learning Craft)
- **Preferred UX:** Category browsing with hierarchical multi-level menu
- **Hub Role:** Pure discovery/help (NOT execution - keep separate from `/craft:do`)
- **Learning:** Capture failed searches for continuous improvement
- **Value Enhancement:** Interactive tutorials showing how to use commands
- **Auto-Detection:** Parse frontmatter YAML from command `.md` files
- **Tutorial Format:** Step-by-step text walkthrough

---

## 💡 Solution Architecture

### Three-Layer Hub System

```
┌─────────────────────────────────────────────────────────────────┐
│ Layer 1: SMART ENTRY POINT                                      │
│ /craft:hub [query]                                              │
│                                                                 │
│ - No args     → Show main menu (10 categories)                 │
│ - With query  → Smart search + filter                          │
│ - --tutorial  → Show interactive learning mode                 │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 2: CATEGORY DRILL-DOWN                                    │
│ /craft:hub <category>                                           │
│                                                                 │
│ - Shows all commands in category                               │
│ - Grouped by subcategory (if any)                              │
│ - Displays: name, description, modes, tutorial link            │
└─────────────────────────────────────────────────────────────────┘
         ↓
┌─────────────────────────────────────────────────────────────────┐
│ Layer 3: COMMAND DETAIL + TUTORIAL                              │
│ /craft:hub <category>:<command>                                 │
│                                                                 │
│ - Full command documentation                                   │
│ - Step-by-step tutorial (if available)                         │
│ - Related commands                                             │
│ - Example workflows                                            │
└─────────────────────────────────────────────────────────────────┘
```

---

## 🎯 Quick Wins (< 2 hours each)

### 1. ⚡ Auto-Detection System
**Benefit:** Eliminate manual count updates, always accurate

**Implementation:**
```python
# Step 1: Scan commands directory
def discover_commands():
    commands = []
    for file in glob("commands/**/*.md"):
        # Parse YAML frontmatter
        metadata = parse_frontmatter(file)
        commands.append({
            "name": metadata.get("name"),
            "category": infer_category(file),
            "description": metadata.get("description"),
            "modes": metadata.get("modes", []),
            "tutorial": metadata.get("tutorial", None)
        })
    return commands

# Step 2: Cache results (rebuild on command change)
# Step 3: Display accurate counts
```

**Files to Create:**
- `commands/_discovery.py` - Auto-detection logic
- `commands/_cache.json` - Generated command registry

---

### 2. ⚡ Hierarchical Main Menu
**Benefit:** Reduce cognitive load, guide new users

**Implementation:**
```markdown
┌─────────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT COMMAND HUB - Choose a Category                        │
│ 89 Commands | 21 Skills | 8 Agents                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🚀 GETTING STARTED (Recommended for new users)                 │
│    1. Quick Start Tutorial                                     │
│    2. Common Workflows                                         │
│    3. Smart Commands (do, check, help)                         │
│                                                                 │
│ 📂 BROWSE BY CATEGORY                                          │
│    4. 💻 CODE (11 commands)     - Lint, test, debug, CI       │
│    5. 🧪 TEST (3 commands)      - Run, watch, coverage        │
│    6. 📄 DOCS (10 commands)     - Sync, changelog, validate   │
│    7. 🔀 GIT (7 commands)       - Branch, sync, worktree      │
│    8. 📖 SITE (5 commands)      - Build, deploy, check        │
│    9. 🏗️ ARCH (1 command)       - Architecture analysis       │
│   10. 🔧 MORE... (CI, Dist, Plan, Workflow, Orchestrate)      │
│                                                                 │
│ 🔍 SEARCH & FILTER                                             │
│    /craft:hub search <keyword>                                 │
│    /craft:hub tutorial                                         │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

Choose a number or type a category name:
```

**AskUserQuestion Integration:**
```python
AskUserQuestion:
  question: "Which category would you like to explore?"
  header: "Category"
  multiSelect: false
  options:
    - label: "🚀 Getting Started (Recommended)"
      description: "Tutorials and common workflows for new users"
    - label: "💻 CODE (11 commands)"
      description: "Code quality, testing, debugging, CI/CD"
    - label: "🔀 GIT (7 commands)"
      description: "Git workflows, branching, worktrees"
    - label: "📄 DOCS (10 commands)"
      description: "Documentation automation and validation"
```

---

### 3. ⚡ Failed Search Tracking
**Benefit:** Continuous improvement, identify gaps

**Implementation:**
```python
# When user searches but finds nothing
def track_failed_search(query, context):
    # Append to log file
    with open("commands/_search_failures.jsonl", "a") as f:
        f.write(json.dumps({
            "timestamp": now(),
            "query": query,
            "context": context,
            "project_type": detect_project_type()
        }) + "\n")

    # Show helpful fallback
    print("❌ No commands found for:", query)
    print("💡 Try:")
    print("  - Browse by category: /craft:hub")
    print("  - Smart search: /craft:do", query)
    print("  - Get help: /craft:help", query)
```

**Files to Create:**
- `commands/_search_failures.jsonl` - Failed search log
- `commands/_analytics.py` - Analysis tools

---

## 🔧 Medium Effort (4-8 hours each)

### 4. Category Drill-Down Views
**Benefit:** Progressive disclosure, focused exploration

**Example: /craft:hub code**
```markdown
┌─────────────────────────────────────────────────────────────────┐
│ 💻 CODE COMMANDS (11 total)                                     │
│ Craft Plugin - Code Quality & Development Tools                │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ 🔍 ANALYSIS (5 commands)                                        │
│   /craft:code:lint [mode]           Code style & quality       │
│   /craft:code:coverage [mode]       Test coverage analysis     │
│   /craft:code:deps-check            Dependency health check    │
│   /craft:code:deps-audit            Security vulnerability scan│
│   /craft:code:debug                 Systematic debugging       │
│                                                                 │
│ 🏗️ DEVELOPMENT (3 commands)                                     │
│   /craft:code:test-gen              Generate test files        │
│   /craft:code:refactor              Refactoring guidance       │
│   /craft:code:demo                  Create demonstrations      │
│                                                                 │
│ 🚀 CI/CD (3 commands)                                           │
│   /craft:code:ci-local              Run CI checks locally      │
│   /craft:code:ci-fix                Fix CI failures            │
│   /craft:code:docs-check            Pre-flight doc check       │
│                                                                 │
│ 📦 RELEASE (1 command)                                          │
│   /craft:code:release               Release workflow           │
│                                                                 │
├─────────────────────────────────────────────────────────────────┤
│ 💡 Common Workflows:                                            │
│   • Pre-commit: lint → test:run → ci-local                     │
│   • Debug: debug → test:debug → coverage                       │
│   • Release: deps-audit → test:run release → release           │
│                                                                 │
│ 📚 Tutorials: /craft:hub code:tutorial                          │
│ 🔙 Back: /craft:hub                                             │
└─────────────────────────────────────────────────────────────────┘

Select a command number or type command name for details:
```

---

### 5. Interactive Step-by-Step Tutorials
**Benefit:** Guide new users through actual usage

**Example: /craft:hub code:lint tutorial**
```markdown
┌─────────────────────────────────────────────────────────────────┐
│ 📚 TUTORIAL: /craft:code:lint                                   │
│ Learn how to use code linting in your workflow                 │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│ WHAT IT DOES                                                    │
│ ────────────                                                    │
│ Runs code style and quality checks using project-specific      │
│ linters (ruff, flake8, eslint, etc.). Supports 4 modes for     │
│ different use cases.                                            │
│                                                                 │
│ STEP-BY-STEP GUIDE                                              │
│ ──────────────────                                              │
│                                                                 │
│ Step 1: Basic Usage (Quick Check)                              │
│ ────────────────────────────────────                            │
│   $ /craft:code:lint                                            │
│                                                                 │
│   This runs in default mode (< 10s) with quick checks.         │
│   Perfect for: Daily development, quick validation             │
│                                                                 │
│ Step 2: Debug Mode (When You Have Issues)                      │
│ ──────────────────────────────────────────                      │
│   $ /craft:code:lint debug                                      │
│                                                                 │
│   This runs verbose analysis (< 120s) with fix suggestions.    │
│   Perfect for: Investigating errors, learning best practices   │
│                                                                 │
│ Step 3: Release Mode (Before Deployment)                       │
│ ─────────────────────────────────────────                       │
│   $ /craft:code:lint release                                    │
│                                                                 │
│   This runs comprehensive checks (< 300s) with security audit. │
│   Perfect for: Pre-release validation, production readiness    │
│                                                                 │
│ COMMON WORKFLOWS                                                │
│ ────────────────                                                │
│                                                                 │
│ Pre-Commit Workflow:                                            │
│   1. /craft:code:lint                                           │
│   2. /craft:test:run                                            │
│   3. git commit                                                 │
│                                                                 │
│ Debug Workflow:                                                 │
│   1. /craft:code:lint debug                                     │
│   2. Fix issues based on suggestions                           │
│   3. /craft:code:lint (verify fixes)                            │
│                                                                 │
│ RELATED COMMANDS                                                │
│ ────────────────                                                │
│   /craft:test:run       - Run tests                            │
│   /craft:code:ci-local  - Full CI checks                       │
│   /craft:check          - Universal validation                 │
│                                                                 │
│ 💡 TIP: Use /craft:check for automated lint + test + CI checks │
│                                                                 │
│ 🔙 Back to CODE: /craft:hub code                                │
│ 🏠 Back to Hub: /craft:hub                                      │
└─────────────────────────────────────────────────────────────────┘
```

**Tutorial Template Structure:**
1. **What it does** (1-2 sentences)
2. **Step-by-step guide** (3-5 steps with examples)
3. **Common workflows** (real-world usage patterns)
4. **Related commands** (navigation)
5. **Tips** (pro user hints)

---

### 6. Command Metadata Enhancement
**Benefit:** Rich information for better discovery

**Enhanced Frontmatter Schema:**
```yaml
---
name: "code:lint"
category: "code"
subcategory: "analysis"
description: "Code style & quality checks"
modes: ["default", "debug", "optimize", "release"]
time_budgets:
  default: "< 10s"
  debug: "< 120s"
  release: "< 300s"
tutorial: true
tutorial_level: "beginner"
related_commands:
  - "test:run"
  - "code:ci-local"
  - "check"
common_workflows:
  - name: "Pre-commit"
    steps: ["code:lint", "test:run", "git commit"]
  - name: "Debug"
    steps: ["code:lint debug", "fix issues", "code:lint"]
tags: ["quality", "style", "linting", "analysis"]
project_types: ["python", "node", "r"]
---
```

**Files to Update:**
- All `commands/**/*.md` files with enhanced frontmatter
- `commands/_schema.json` - Metadata schema definition

---

## 🏗️ Long-term Enhancements (Future Sessions)

### 7. Smart Search & Filtering
**Benefit:** Natural language command discovery

**Features:**
- Fuzzy search across command names, descriptions, tags
- Filter by: category, mode support, project type, complexity
- Synonym mapping (e.g., "fix" → "debug", "deploy" → "release")
- Search suggestions based on common queries

**Example:**
```bash
$ /craft:hub search "run tests in watch mode"
Found 2 commands:
  1. /craft:test:run      - Unified test runner (supports modes)
  2. /craft:test:watch    - Watch mode (re-run on change)

Did you mean:
  • /craft:test:watch  ← Most relevant
```

---

### 8. Usage Analytics & Personalization
**Benefit:** Learn user preferences, improve recommendations

**Features:**
- Track most-used commands per user/project
- Show "Your frequent commands" section in hub
- Suggest commands based on project context + history
- Identify unused commands (candidates for better documentation)

**Example:**
```markdown
┌─────────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT COMMAND HUB                                            │
│                                                                 │
│ 🔥 YOUR FREQUENT COMMANDS (This Project)                        │
│    /craft:test:run debug    (used 15 times this week)          │
│    /craft:code:lint         (used 12 times)                     │
│    /craft:git:sync          (used 8 times)                      │
│                                                                 │
│ 💡 SUGGESTED FOR YOU                                            │
│    /craft:code:coverage     (pairs well with test:run)         │
│    /craft:git:worktree      (advanced git workflow)            │
│                                                                 │
│ 📂 BROWSE ALL CATEGORIES...                                     │
└─────────────────────────────────────────────────────────────────┘
```

---

### 9. Visual Workflow Maps
**Benefit:** Show command relationships & sequences

**Mermaid Diagrams:**
```mermaid
graph TD
    Start[New Feature] --> Branch[/craft:git:worktree]
    Branch --> Code[Write Code]
    Code --> Lint[/craft:code:lint]
    Lint --> Test[/craft:test:run]
    Test --> CI[/craft:code:ci-local]
    CI --> Check{All Pass?}
    Check -->|Yes| Commit[git commit]
    Check -->|No| Debug[/craft:code:debug]
    Debug --> Code
    Commit --> PR[gh pr create]
    PR --> Review[Code Review]
    Review --> Merge[Merge to dev]
```

**Interactive Navigation:**
- Click on command node → Show command details
- Highlight current position in workflow
- Show alternative paths (e.g., skip CI for quick commits)

---

### 10. Multi-Language Support
**Benefit:** Reach wider audience, global adoption

**Structure:**
```
commands/
  en/  (English - default)
  es/  (Spanish)
  fr/  (French)
  ja/  (Japanese)
```

**Detection:**
```bash
# Auto-detect from system locale
$ /craft:hub
┌─────────────────────────────────────────────────────────────────┐
│ 🛠️ CRAFT COMMAND HUB                                            │
│ Language: English (Change: /craft:hub --lang es)               │
```

---

## 🎨 UX Enhancements

### Progressive Disclosure Pattern

**Level 1: Main Hub (Minimal)**
```
10 categories + 3 smart commands
~200 characters of text
Choice: Pick category or search
```

**Level 2: Category View (Moderate)**
```
All commands in category
Grouped by subcategory
~500 characters of text
Choice: Pick command or go back
```

**Level 3: Command Detail (Maximum)**
```
Full documentation + tutorial
Examples, workflows, related commands
~2000 characters of text
Choice: Run command, tutorial, or back
```

**Key Principle:** Each level shows 3x more detail than previous

---

### Keyboard Navigation (Future)

```
In Hub Menu:
  ↑/↓     Navigate options
  Enter   Select
  /       Start search
  Esc     Go back
  h       Show help
  ?       Show keyboard shortcuts

In Category View:
  1-9     Quick select command by number
  /       Filter commands
  b       Back to hub
```

---

## 📊 Success Metrics

### Discoverability Improvements
- **Time to Find Command:** < 30s (from any starting point)
- **Search Success Rate:** > 90% (users find what they need)
- **Failed Searches:** < 5% (tracked for improvement)

### User Engagement
- **Tutorial Completion:** > 60% of new users complete at least 1 tutorial
- **Hub Usage:** 30% of sessions start with `/craft:hub`
- **Command Reachability:** All 89 commands reachable in ≤ 3 clicks

### Maintenance
- **Auto-Detection Accuracy:** 100% (no manual count updates)
- **Metadata Completeness:** 100% of commands have category, description, modes
- **Tutorial Coverage:** > 80% of high-traffic commands have tutorials

---

## 🛠️ Implementation Strategy

### Phase 1: Foundation (Week 1)
**Goal:** Fix immediate pain points
1. ✅ Auto-detection system (`commands/_discovery.py`)
2. ✅ Hierarchical main menu (update `hub.md`)
3. ✅ Failed search tracking (`_search_failures.jsonl`)

**Deliverable:** `/craft:hub` shows accurate counts, organized categories

---

### Phase 2: Discovery (Week 2)
**Goal:** Improve command findability
1. ✅ Category drill-down views (`/craft:hub <category>`)
2. ✅ Enhanced metadata in all command files
3. ✅ Smart search prototype

**Deliverable:** Users can browse and find commands easily

---

### Phase 3: Learning (Week 3-4)
**Goal:** Guide new users
1. ✅ Tutorial template system
2. ✅ Write tutorials for top 10 commands
3. ✅ Common workflow documentation

**Deliverable:** New users can learn Craft through interactive tutorials

---

### Phase 4: Intelligence (Week 5-6)
**Goal:** Adaptive & personalized
1. ✅ Usage analytics tracking
2. ✅ Personalized suggestions
3. ✅ Visual workflow maps (Mermaid)

**Deliverable:** Hub learns and adapts to user preferences

---

## 🔍 Open Questions

1. **Tutorial Authoring:** Who writes tutorials? Auto-generate from examples or manual curation?
2. **Search Syntax:** Should search support filters like `mode:debug category:code`?
3. **Offline Mode:** Should hub work without internet (for auto-updates/analytics)?
4. **Command Aliases:** Should hub suggest shorter aliases for frequently used commands?
5. **Integration:** Should hub integrate with IDE autocomplete (VS Code, Cursor)?

---

## 📚 Related Commands

- `/craft:do` - Smart command execution (hub's complement)
- `/craft:check` - Universal validation
- `/craft:smart-help` - Context-aware help
- `/craft:orchestrate` - Multi-agent workflow coordination

---

## 🎯 Recommended Next Steps

### Immediate Actions (Today)
1. **Validate Approach:** Review this brainstorm, confirm direction
2. **Spike Auto-Detection:** Test YAML frontmatter parsing on 5 commands
3. **Design Main Menu:** Finalize category groupings and naming

### This Week
1. **Implement Phase 1:** Auto-detection + hierarchical menu + tracking
2. **Update 10 Commands:** Add enhanced metadata to top 10 commands
3. **Write 1 Tutorial:** Create tutorial for `/craft:code:lint` as template

### Next Sprint
1. **Complete Phase 2:** All category views + search prototype
2. **Expand Tutorials:** Cover top 20 commands
3. **User Testing:** Get feedback from 3 new users

---

## 💭 Design Principles

1. **Progressive Disclosure:** Show minimal → moderate → maximum detail
2. **Guided Discovery:** New users follow learning path, power users navigate freely
3. **Zero Maintenance:** Auto-detection eliminates manual updates
4. **Feedback Loops:** Track failures, learn from usage, improve continuously
5. **Separation of Concerns:** Hub = discovery, `/craft:do` = execution
6. **Accessibility:** Keyboard navigation, screen reader friendly, clear hierarchy

---

## ✅ Success Criteria

**This update succeeds if:**
- ✅ New users can find their first command in < 30 seconds
- ✅ Command counts are always accurate (auto-detected)
- ✅ Failed searches are tracked and analyzed monthly
- ✅ 80%+ of users prefer hierarchical menu over flat list
- ✅ Tutorials reduce "how do I...?" questions by 50%

---

**Brainstorm completed in ~12 minutes**
**Next:** Capture as implementation spec → `/craft:hub` v2.0
