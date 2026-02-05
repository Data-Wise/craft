# Commands Overview

> **TL;DR** (30 seconds)
>
> - **What:** 106 commands organized into 10 categories (Smart, Docs, Site, Code, Testing, Git, CI, Architecture, Distribution, Planning, Workflow)
> - **Why:** One plugin handles your entire development workflow from docs to deployment
> - **How:** Use `/craft:hub` to discover all commands by category
> - **Next:** Start with `/craft:do` for AI-powered task routing or `/craft:check` for pre-flight validation

Craft provides **106 commands** across 10 categories for full-stack development workflows.

## Command Categories

### 🎯 Smart Commands (4)

Universal commands with AI-powered routing:

- `/craft:do <task>` - Universal task router
- `/craft:orchestrate <task> [mode]` - Enhanced orchestrator v2.1
- `/craft:check [--for]` - Pre-flight checks
- `/craft:help [topic]` - Context-aware help

[Learn more →](smart.md)

### 📚 Documentation Commands (13)

Smart documentation generation and validation:

- Super Commands: `update`, `sync`, `check`
- **NEW:** `/craft:docs:website` - ADHD-friendly enhancement
- Specialized: `api`, `changelog`, `guide`, `demo`, `mermaid`

[Learn more →](docs.md)

### 🌐 Site Commands (12)

Full documentation site management:

- `/craft:site:create` - Wizard with 8 ADHD-friendly presets
- Navigation & audit: `nav`, `audit`, `consolidate`
- Management: `status`, `update`, `deploy`

[Learn more →](site.md)

### 💻 Code & Testing Commands (12)

Development workflow tools:

- Linting: `/craft:code:lint [mode]`
- Testing: `/craft:test:run [mode]`
- Debugging: `/craft:code:debug`
- Refactoring: `/craft:code:refactor`

[Learn more →](code.md)

### 🔀 Git & CI Commands (12)

Version control and continuous integration:

- Git: `worktree`, `sync`, `clean`, `recap`, `branch`
- CI: `detect`, `generate`, `validate`

[Learn more →](git.md)

### 📦 Other Categories

- **Architecture** (7): System design, tech stack analysis
- **Distribution** (2): Homebrew formulas, curl installers
- **Planning** (3): Feature planning, sprints, roadmaps
- **Discovery** (1): Command hub

## Mode System

Many commands support execution modes:

| Mode | Time | Description |
|------|------|-------------|
| `default` | <10s | Quick checks |
| `debug` | <120s | Verbose output with suggestions |
| `optimize` | <180s | Parallel execution, performance focused |
| `release` | <300s | Comprehensive audit |

**Example:**

```bash
/craft:code:lint optimize    # Fast parallel linting
/craft:test:run debug        # Verbose test output
```

## Quick Navigation

| I want to... | Use this command |
|--------------|------------------|
| Generate docs | `/craft:docs:update` |
| Create a site | `/craft:site:create` |
| Run tests | `/craft:test:run` |
| Manage git worktrees | `/craft:git:worktree` |
| Check before commit | `/craft:check` |
| Get help | `/craft:help` |
| Discover commands | `/craft:hub` |

---

## NEW in v2.9.0: Interactive Command Behavior

Four key commands now use the **"Show Steps First" pattern**:

### /craft:check - Pre-Flight Validation

```bash
/craft:check

# Shows plan → Asks to proceed → Runs checks
# NEW: --dry-run flag, --mode selection, --skip flags
```

[Learn more →](check.md) | [Cookbook recipe](../cookbook/common/check-code-quality-before-commit.md) | [Quick reference](../reference/REFCARD-CHECK.md)

### /craft:orchestrate - Multi-Agent Coordination

```bash
/craft:orchestrate "complex task"

# Shows plan → Asks for mode → Confirms → Runs with checkpoints
# NEW: Interactive mode selection (default/wave/phase)
```

[Learn more →](orchestrate.md) | [Tutorial](../tutorials/interactive-orchestration.md) | [Modes compared](../tutorials/orchestrator-modes-compared.md)

### /craft:git:worktree - Parallel Development

```bash
/craft:git:worktree feature/new-feature

# Creates worktree → Auto-generates ORCHESTRATE.md + SPEC.md
# NEW: Scope detection and auto-setup
```

[Learn more →](git/worktree.md) | [Tutorial](../tutorials/TUTORIAL-worktree-setup.md) | [Quick reference](../reference/REFCARD-GIT-WORKTREE.md)

### /craft:docs:update - Documentation Generator

```bash
/craft:docs:update

# Detects changes → Shows plan → Confirms → Generates → Validates
# NEW: --post-merge flag for automated 5-phase pipeline
```

[Learn more →](docs/update.md) | [Tutorial](../tutorials/TUTORIAL-post-merge-pipeline.md) | [Quick reference](../reference/REFCARD-DOCS-UPDATE.md)

---

## Quick Wins for New Users

**⚡ 30 seconds:**

```bash
/craft:hub        # Discover all commands by category
```

**⚡ 2 minutes:**

```bash
/craft:check      # Validate your project before commit
```

[Cookbook recipe →](../cookbook/common/check-code-quality-before-commit.md)

**⚡ 3-5 minutes:**

```bash
/craft:docs:update --post-merge    # Update docs after merging
```

[Cookbook recipe →](../cookbook/common/post-merge-documentation.md)

**⚡ 5-7 minutes:**

```bash
/craft:orchestrate "your task"     # Multi-step workflow with mode selection
```

[Cookbook recipe →](../cookbook/common/use-interactive-orchestration.md)

**⚡ 8-10 minutes:**

```bash
/craft:git:worktree feature/name   # Setup parallel development
```

[Cookbook recipe →](../cookbook/common/setup-parallel-worktrees.md)

---

## Learning Path

### Level 1: Essentials (First 30 minutes)

1. **Discover commands:** `/craft:hub`
2. **Get help:** `/craft:help`
3. **Quick check:** `/craft:check`
4. **Smart routing:** `/craft:do "simple task"`

### Level 2: Workflows (Next 2 hours)

1. **Documentation:** `/craft:docs:update`
2. **Testing:** `/craft:test:run`
3. **Git worktrees:** `/craft:git:worktree setup`
4. **Orchestration:** `/craft:orchestrate "multi-step task"`

### Level 3: Advanced (Ongoing)

1. **Site creation:** `/craft:site:create`
2. **CI/CD setup:** `/craft:ci:generate`
3. **Architecture analysis:** `/craft:arch:analyze`
4. **Distribution:** `/craft:dist:homebrew`

**Resources:**

- [Cookbook & Examples](../cookbook/index.md) - Task-focused recipes
- [Tutorials](../tutorials/) - Step-by-step guides
- [Guides](../guide/) - Comprehensive documentation

---
