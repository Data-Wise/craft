# Craft Plugin

[![Documentation](https://img.shields.io/badge/docs-comprehensive-brightgreen.svg)](https://data-wise.github.io/craft/)
[![Docs Sync](https://github.com/Data-Wise/craft/actions/workflows/docs-sync.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-sync.yml)
[![Docs](https://github.com/Data-Wise/craft/actions/workflows/docs.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs.yml)
[![Homebrew Release](https://github.com/Data-Wise/craft/actions/workflows/homebrew-release.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/homebrew-release.yml)
[![Validate Dependencies](https://github.com/Data-Wise/craft/actions/workflows/validate-dependencies.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/validate-dependencies.yml)
[![Version](https://img.shields.io/badge/version-4.4.0-brightgreen.svg)](https://github.com/Data-Wise/craft/releases)

| Branch | CI | Docs |
|--------|----|----- |
| **main** | [![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml) | [![Deploy Docs](https://github.com/Data-Wise/craft/actions/workflows/docs.yml/badge.svg)](https://github.com/Data-Wise/craft/actions/workflows/docs.yml) |
| **dev** | [![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml) | [![Documentation Quality](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml) |

> **TL;DR** (30 seconds)
>
> - **What:** Full-stack developer toolkit with 48 commands, 2 AI agents, and 40 auto-triggered skills
> - **Why:** Automate documentation, testing, git workflows, CLAUDE.md management, and site creation with one command
> - **How:** Install via `claude plugin install craft@local-plugins`
> - **Next:** Run `/craft:do "your task"` and let AI route to the best workflow

> Full-stack developer toolkit for Claude Code — 48 commands, 2 agents, 40 skills with smart orchestration and ADHD-friendly workflows

## Features

<div class="grid cards" markdown>

- :rocket:{ .lg .middle } **47 Commands**

    Smart commands, docs, code, testing, git, CI, architecture, distribution (Homebrew), planning, and workflow automation — all in one toolkit. Docs-authoring/site-publishing commands live in the sibling [`folio`](https://github.com/Data-Wise/folio) plugin.

- :brain:{ .lg .middle } **2 Agents**

    `orchestrator` and `orchestrator-v2` (mode-aware, subagent-monitoring multi-step orchestration). The docs-focused agents (mermaid expert, API documenter, tutorial engineer, demo engineer, reference builder) moved to `folio`.

- :sparkles:{ .lg .middle } **40 Skills**

    Auto-triggered expertise for backend/frontend design, DevOps, testing, architecture, planning, distribution, insights, and documentation automation

- :zap:{ .lg .middle } **Smart Orchestration**

    Enhanced orchestrator v2.1 with mode-aware execution, subagent monitoring, and timeline tracking

- :art:{ .lg .middle } **8 ADHD-Friendly Presets**

    Documentation site designs optimized for focus, calm, and quick comprehension

- :books:{ .lg .middle } **Documentation Excellence**

    Comprehensive guides, 80+ Mermaid diagrams, complete version history, smart doc generation, TL;DR boxes, time estimates, mermaid validation pipeline with health score

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
    Run `/craft:hub` to see all 47 commands organized by category - takes 5 seconds and shows everything craft can do.

## Feature Highlights

<div class="grid cards" markdown>

- :dart:{ .lg .middle } **Smart Command Routing**

    `/craft:do` analyzes task complexity (0-10 scale), routes to the right commands or delegates to specialized agents. Simple tasks run instantly, complex ones get full orchestration.

    → [How it works](commands/smart.md)

- :page_facing_up:{ .lg .middle } **CLAUDE.md Lifecycle Management**

    Skill-driven lifecycle management (`init`, `sync`, `edit` folded into the `docs/claude-md` skill in the v4 consolidation) with budget enforcement (< 150 lines), pointer architecture, and 4-phase sync pipeline. Keeps your CLAUDE.md lean and accurate.

    → [Tutorial guide](tutorials/claude-md-workflows.md)

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

Reference documentation for all 47 Craft commands:

<div class="grid cards" markdown>

- :scroll:{ .lg .middle } **[API Reference - Commands](API-REFERENCE-COMMANDS.md)**

    Index into per-command pages ([docs/commands/](commands/overview.md)) and the [REFCARD](REFCARD.md) cheat sheet, organized by category

- :gear:{ .lg .middle } **[Command Parameters](reference/COMMAND-PARAMETERS.md)**

    Detailed parameter reference, types, defaults, aliases, and environment variables for every command

- :warning:{ .lg .middle } **[Error Scenarios & Recovery](reference/ERROR-SCENARIOS.md)**

    Comprehensive error handling guide with 50+ error scenarios, codes, causes, and recovery steps

- :bulb:{ .lg .middle } **[Command Examples](reference/COMMAND-EXAMPLES.md)**

    Real-world usage patterns, workflows, and practical examples for all command categories

</div>

**Quick Links:**

- [All 47 Commands, Indexed by Category](API-REFERENCE-COMMANDS.md)
- [Parameters Quick Reference](reference/COMMAND-PARAMETERS.md)
- [Error Recovery Guide](reference/ERROR-SCENARIOS.md)
- [Real-World Examples](reference/COMMAND-EXAMPLES.md)

## Popular Workflows

<div class="grid cards" markdown>

- :memo:{ .lg .middle } **Documentation Automation**

    Update all docs from code changes in one command

    → [Learn more](workflows/index.md#documentation-workflow)

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

    All 47 commands organized

- :sparkles:{ .lg .middle } **[Skills & Agents](skills-agents.md)**

    Understanding the AI system

- :page_facing_up:{ .lg .middle } **[Quick Reference](REFCARD.md)**

    Command cheat sheet

- :scroll:{ .lg .middle } **[API Reference](API-REFERENCE-COMMANDS.md)**

    Index into per-command documentation for all 48 commands

</div>

## Key Command Categories

| Category          | Count  | Description                                                                                                    |
| ------------------ | ------ | ---------------------------------------------------------------------------------------------------------------- |
| **Root-level**     | 14     | Universal command (`/craft:do`), orchestrator, checks, hub, next, finish, refine, brief, brainstorm, grill, plan, restore, smart-help, test |
| **Code**           | 13     | Linting, testing, debugging, refactoring, CI-fix helpers, deps management                                       |
| **CI**             | 8      | Detection, generation, validation, triage, watch, local/fix runners                                             |
| **Architecture**   | 4      | Analysis, diagrams, planning, reviews                                                                           |
| **Distribution**   | 2      | Homebrew, cross-surface distribution status                                                                     |
| **Docs**           | 2      | Doc-set update, changelog generation (docs authoring itself lives in the `folio` plugin since v4.0.0)           |
| **Orchestrate**    | 2      | Drive loops, multi-agent dispatch workflow                                                                      |
| **Git**            | 1      | Issue-check triage (branch/worktree/guard ops live in the `dev/git` skill, not a command, since the guard-suite consolidation) |
| **Planning**       | 1      | Feature planning                                                                                                |
| **Site**           | 1      | Deploy to GitHub Pages (site build/status/check moved to `folio` in v4.0.0)                                     |
| **Total**          | **48** | **Complete development workflow coverage**                                                                      |

!!! info "Latest: v4.4.0 — Guard-Bypass Escape Hatch + Reference-Scope Guard"
    [`CRAFT_GUARD_ALLOW_DEV_EDIT`](https://github.com/Data-Wise/craft/pull/305) closes a
    self-referential deadlock where creating the branch-guard bypass marker was itself blocked by
    the guard it was meant to bypass. New advisory-only
    [`reference-scope-guard.sh`](https://github.com/Data-Wise/craft/pull/306) hook warns (never
    blocks) on non-conforming filenames written under `~/.claude/reference/`.
    See the [full changelog](CHANGELOG.md) for all releases, or visit the [News](NEWS.md) page for release highlights.

## Links

- [GitHub Repository](https://github.com/Data-Wise/craft)
- [Issue Tracker](https://github.com/Data-Wise/craft/issues)
- [Changelog](CHANGELOG.md)
- [ROADMAP](https://github.com/Data-Wise/craft/blob/main/docs/archive/ROADMAP.md)
