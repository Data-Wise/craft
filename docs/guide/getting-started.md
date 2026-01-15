# Getting Started with Craft

⏱️ **10 minutes** • 🟡 Intermediate • ✓ Complete guide

> **TL;DR** (30 seconds)
> - **What:** Complete guide to installing and using craft's 89 commands, 21 skills, and 8 agents
> - **Why:** Master the full-stack toolkit to automate your entire development workflow
> - **How:** Install plugin → verify with `/craft:hub` → start with `/craft:do "task"`
> - **Next:** Read about [Skills & Agents](skills-agents.md) to understand AI automation

Complete guide to using the craft plugin for Claude Code.

## Installation

!!! abstract "Progress: Step 1/5"
    Installing craft - choose your method

### Method 1: Homebrew (Recommended)

```bash
brew tap data-wise/tap
brew install craft
```

See [Homebrew Installation Guide](homebrew-installation.md) for details on updates and troubleshooting.

### Method 2: Claude Code Plugin System

```bash
claude plugin install craft@local-plugins
```

### Method 3: Symlink (Development)

```bash
ln -s ~/projects/dev-tools/craft ~/.claude/plugins/craft
```

## Verify Installation

!!! abstract "Progress: Step 2/5"
    Verify everything works

```bash
/craft:hub
```

You should see all 89 commands listed.

## Initialize a New Project (Optional)

!!! tip "Starting from Scratch?"
    Skip this section if you already have a git repository. This is for brand new projects.

If you're starting a new project, use craft to set up the complete git workflow:

```bash
/craft:git:init
```

This interactive wizard will:

- Initialize git repository
- Create `main` + `dev` branch structure
- Enable branch protection on `main`
- Auto-detect and generate CI workflow
- Create project tracking files (`.STATUS`, `CLAUDE.md`)
- Add PR template
- Create initial commit
- Push to GitHub (if desired)

**Quick setup:**

```bash
# Interactive wizard
/craft:git:init

# Preview what would happen
/craft:git:init --dry-run

# Skip prompts, use defaults
/craft:git:init --yes --remote user/repo
```

After initialization, you'll have:
- ✅ Protected `main` branch (PR + CI required)
- ✅ `dev` branch ready for work
- ✅ CI workflow configured
- ✅ Project documentation

See [/craft:git:init](../../commands/git/init.md) for full details.

## Your First Commands

!!! abstract "Progress: Step 3/5"
    Try these essential commands

### 1. Universal Task Execution

```bash
/craft:do "add user authentication"
```

The AI routes your task automatically.

### 2. Pre-Flight Checks

Before committing code:

```bash
/craft:check
```

Before creating a PR:

```bash
/craft:check --for pr
```

Before releasing:

```bash
/craft:check --for release
```

### 3. Documentation

Update all documentation:

```bash
/craft:docs:update
```

Check for stale docs:

```bash
/craft:docs:sync
```

### 4. Create a Documentation Site

```bash
/craft:site:create --preset data-wise --quick
```

## Understanding the System

!!! abstract "Progress: Step 4/5"
    Learn the 3-layer architecture

Craft has three levels of automation:

1. **Commands** (89 total) - Direct actions
2. **Skills** (21 total) - Auto-triggered expertise
3. **Agents** (8 specialized) - Long-running tasks

When you use `/craft:do`, the system determines which combination to use.

## Next Steps

!!! abstract "Progress: Step 5/5 - Complete! 🎉"
    Continue your journey

- [Skills & Agents](skills-agents.md) - Understanding the AI system
- [Orchestrator](orchestrator.md) - Advanced mode-aware execution
- [Commands Overview](../commands/overview.md) - Explore all commands
