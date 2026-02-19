# Craft Plugin

[![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml)
[![Documentation Quality](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml)
[![Documentation](https://img.shields.io/badge/docs-99%25%20complete-brightgreen.svg)](https://data-wise.github.io/craft/)

> **TL;DR** (30 seconds)
>
> - **What:** Full-stack developer toolkit with 111 commands, 8 AI agents, and 25 auto-triggered skills
> - **Why:** Automate documentation, testing, git workflows, CLAUDE.md management, and site creation with one command
> - **How:** Install via `claude plugin install craft@local-plugins`
> - **Next:** Run `/craft:do "your task"` and let AI route to the best workflow

> Full-stack developer toolkit for Claude Code — 111 commands, 8 agents, 25 skills with smart orchestration and ADHD-friendly workflows

## Features

<div class="grid cards" markdown>

- :rocket:{ .lg .middle } **111 Commands**

    Smart commands, docs, site management, CLAUDE.md maintenance, code, testing, git, CI, architecture, distribution (marketplace + Homebrew + PyPI), planning, and workflow automation - all in one toolkit

- :brain:{ .lg .middle } **8 Specialized Agents**

    Backend architect, docs architect, mermaid expert, API documenter, tutorial engineer, demo engineer, reference builder, and orchestrators

- :sparkles:{ .lg .middle } **25 Skills**

    Auto-triggered expertise for backend/frontend design, DevOps, testing, architecture, planning, distribution, insights, and documentation automation

- :zap:{ .lg .middle } **Smart Orchestration**

    Enhanced orchestrator v2.1 with mode-aware execution, subagent monitoring, and timeline tracking

- :art:{ .lg .middle } **8 ADHD-Friendly Presets**

    Documentation site designs optimized for focus, calm, and quick comprehension

- :books:{ .lg .middle } **Documentation Excellence**

    99% complete documentation with comprehensive guides, 17 Mermaid diagrams, complete version history, smart doc generation, TL;DR boxes, time estimates, mermaid validation

</div>

## Quick Start

```bash
# Install via Claude Code
claude plugin install craft@local-plugins

# Or create symlink
ln -s ~/projects/dev-tools/claude-plugins/craft ~/.claude/plugins/craft
```

**First command:**

```bash
/craft:do "add user authentication"
```

The universal `/craft:do` command routes your task to the best workflow automatically.

!!! success "Quick Win: Try It Now"
    Run `/craft:hub` to see all 111 commands organized by category - takes 5 seconds and shows everything craft can do.

## Feature Highlights

<div class="grid cards" markdown>

- :dart:{ .lg .middle } **Smart Command Routing**

    `/craft:do` analyzes task complexity (0-10 scale), routes to the right commands or delegates to specialized agents. Simple tasks run instantly, complex ones get full orchestration.

    → [How it works](commands/smart.md)

- :page_facing_up:{ .lg .middle } **CLAUDE.md Lifecycle Management**

    3-command suite (`init`, `sync`, `edit`) with budget enforcement (< 150 lines), pointer architecture, and 4-phase sync pipeline. Keeps your CLAUDE.md lean and accurate.

    → [Command reference](commands/docs/claude-md.md)

- :performing_arts:{ .lg .middle } **Interactive Orchestration**

    "Show Steps First" pattern across key commands — preview execution plans, confirm before running, wave checkpoints between agent groups. 4 orchestration modes for different needs.

    → [Orchestrator guide](guide/interactive-commands.md)

- :mag:{ .lg .middle } **Documentation Automation**

    9-category detection finds stale docs automatically. Interactive prompts for category-level approval. Auto-fix with `--post-merge` pipeline after PR merges.

    → [Docs update tutorial](tutorials/interactive-docs-update-tutorial.md)

- :shield:{ .lg .middle } **Branch Guard v2: Smart Protection**

    3-tier risk classification replaces binary block/allow. Fade-to-brief learning reduces noise over your session. One-shot approvals with 5-minute TTL, destructive command detection, and critical file protection.

    → [Smart mode guide](guide/branch-guard-smart-mode.md)

</div>

## API Reference

Complete OpenAPI-style documentation for all 111 Craft commands:

<div class="grid cards" markdown>

- :scroll:{ .lg .middle } **[API Reference - Commands](API-REFERENCE-COMMANDS.md)**

    Complete documentation for all 111 commands organized by category with parameters, usage examples, and output formats

- :gear:{ .lg .middle } **[Command Parameters](reference/COMMAND-PARAMETERS.md)**

    Detailed parameter reference, types, defaults, aliases, and environment variables for every command

- :warning:{ .lg .middle } **[Error Scenarios & Recovery](reference/ERROR-SCENARIOS.md)**

    Comprehensive error handling guide with 50+ error scenarios, codes, causes, and recovery steps

- :bulb:{ .lg .middle } **[Command Examples](reference/COMMAND-EXAMPLES.md)**

    Real-world usage patterns, workflows, and practical examples for all command categories

</div>

**Quick Links:**

- [All 111 Commands with Full Documentation](API-REFERENCE-COMMANDS.md)
- [Parameters Quick Reference](reference/COMMAND-PARAMETERS.md)
- [Error Recovery Guide](reference/ERROR-SCENARIOS.md)
- [Real-World Examples](reference/COMMAND-EXAMPLES.md)

## Popular Workflows

<div class="grid cards" markdown>

- :memo:{ .lg .middle } **Documentation Automation**

    Update all docs from code changes in one command

    → [Learn more](workflows/index.md#documentation-workflow)

- :globe_with_meridians:{ .lg .middle } **Site Creation**

    Zero to deployed docs site in < 5 minutes

    → [Learn more](workflows/index.md#site-creation-workflow)

- :rocket:{ .lg .middle } **Release Management**

    Pre-release checks to published in one flow

    → [Learn more](workflows/index.md#release-workflow)

- :computer:{ .lg .middle } **Development Workflow**

    Feature branches with git worktrees

    → [Learn more](workflows/index.md#development-workflow)

</div>

## Documentation

<div class="grid cards" markdown>

- :rocket:{ .lg .middle } **[Quick Start](QUICK-START.md)**

    Get running in 30 seconds

- :brain:{ .lg .middle } **[ADHD Guide](ADHD-QUICK-START.md)**

    Under 2 minutes, zero cognitive load

- :bar_chart:{ .lg .middle } **[Visual Workflows](workflows/index.md)**

    5 diagrams showing complete flows

- :books:{ .lg .middle } **[Commands Overview](commands/overview.md)**

    All 111 commands organized

- :sparkles:{ .lg .middle } **[Skills & Agents](guide/skills-agents.md)**

    Understanding the AI system

- :page_facing_up:{ .lg .middle } **[Quick Reference](REFCARD.md)**

    Command cheat sheet

- :scroll:{ .lg .middle } **[API Reference](API-REFERENCE-COMMANDS.md)**

    Complete documentation for all 111 commands

</div>

## Key Command Categories

| Category           | Count  | Description                                                                                                               |
| ------------------ | ------ | ------------------------------------------------------------------------------------------------------------------------- |
| **Smart**          | 4      | Universal command, orchestrator, checks, help, hub                                                                        |
| **Documentation**  | 19     | Smart docs with update, sync, check, website, API, changelog, guides, tutorial, workflow                                  |
| **Site**           | 16     | Full site wizard with 8 ADHD-friendly presets, theme, nav, audit                                                          |
| **Code & Testing** | 12 + 7 | Code: linting, testing, debugging, refactoring, CI fixes, deps management; Tests: run, debug, watch, coverage, generation |
| **Git**            | 13     | Repository initialization, branch management, worktrees, sync, recap, clean, smart branch protection (3-tier risk), learning guides |
| **CI**             | 3      | Detection, generation, validation                                                                                         |
| **Architecture**   | 4      | Analysis, diagrams, planning, reviews                                                                                     |
| **Distribution**   | 4      | Marketplace, Homebrew, PyPI, curl installers                                                                              |
| **Planning**       | 3      | Feature planning, sprints, roadmaps                                                                                       |
| **Workflow**       | 12     | Brainstorming, task management, spec capture, getting unstuck                                                             |
| **Total**          | **111** | **Complete development workflow coverage**                                                                                |

!!! info "Latest: v2.22.0 — CLAUDE.md Layered Instruction System"
    Layered CLAUDE.md architecture (~4000 tokens/session), instruction health check in `/craft:check`, session-end auto-sync in `/workflow:done`, `--generate-reference` for `.claude/reference/` files. 111 commands, ~1575 tests passing. See the [full changelog](CHANGELOG.md) for all releases.

## Links

- [GitHub Repository](https://github.com/Data-Wise/craft)
- [Issue Tracker](https://github.com/Data-Wise/craft/issues)
- [Changelog](CHANGELOG.md)
- [ROADMAP](https://github.com/Data-Wise/craft/blob/main/ROADMAP.md)
