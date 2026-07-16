# Craft Plugin

[![Documentation](https://img.shields.io/badge/docs-98%25%20complete-brightgreen.svg)](https://data-wise.github.io/craft/)
[![Docs Sync](https://github.com/Data-Wise/craft/actions/workflows/docs-sync.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-sync.yml)
[![Docs](https://github.com/Data-Wise/craft/actions/workflows/docs.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs.yml)
[![Homebrew Release](https://github.com/Data-Wise/craft/actions/workflows/homebrew-release.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/homebrew-release.yml)
[![Validate Dependencies](https://github.com/Data-Wise/craft/actions/workflows/validate-dependencies.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/validate-dependencies.yml)
[![Version](https://img.shields.io/badge/version-2.61.2-brightgreen.svg)](https://github.com/Data-Wise/craft/releases)

| Branch | CI | Docs |
|--------|----|----- |
| **main** | [![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=main)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml) | [![Deploy Docs](https://github.com/Data-Wise/craft/actions/workflows/docs.yml/badge.svg)](https://github.com/Data-Wise/craft/actions/workflows/docs.yml) |
| **dev** | [![Craft CI](https://github.com/Data-Wise/craft/actions/workflows/ci.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/ci.yml) | [![Documentation Quality](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml/badge.svg?branch=dev)](https://github.com/Data-Wise/craft/actions/workflows/docs-quality.yml) |

> **TL;DR** (30 seconds)
>
> - **What:** Full-stack developer toolkit with 46 commands, 2 AI agents, and 40 auto-triggered skills
> - **Why:** Automate documentation, testing, git workflows, CLAUDE.md management, and site creation with one command
> - **How:** Install via `claude plugin install craft@local-plugins`
> - **Next:** Run `/craft:do "your task"` and let AI route to the best workflow

> Full-stack developer toolkit for Claude Code — 46 commands, 2 agents, 40 skills with smart orchestration and ADHD-friendly workflows

## Features

<div class="grid cards" markdown>

- :rocket:{ .lg .middle } **46 Commands**

    Smart commands, docs, site management, CLAUDE.md maintenance, code, testing, git, CI, architecture, distribution (marketplace + Homebrew + PyPI), planning, and workflow automation - all in one toolkit

- :brain:{ .lg .middle } **8 Specialized Agents**

    Docs architect, mermaid expert, API documenter, tutorial engineer, demo engineer, reference builder, and 2 orchestrators (default + v2.1)

- :sparkles:{ .lg .middle } **40 Skills**

    Auto-triggered expertise for backend/frontend design, DevOps, testing, architecture, planning, distribution, insights, and documentation automation

- :zap:{ .lg .middle } **Smart Orchestration**

    Enhanced orchestrator v2.1 with mode-aware execution, subagent monitoring, and timeline tracking

- :art:{ .lg .middle } **8 ADHD-Friendly Presets**

    Documentation site designs optimized for focus, calm, and quick comprehension

- :books:{ .lg .middle } **Documentation Excellence**

    99% complete documentation with comprehensive guides, 17 Mermaid diagrams, complete version history, smart doc generation, TL;DR boxes, time estimates, mermaid validation pipeline with health score

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
    Run `/craft:hub` to see all 46 commands organized by category - takes 5 seconds and shows everything craft can do.

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

Complete OpenAPI-style documentation for all 115 Craft commands:

<div class="grid cards" markdown>

- :scroll:{ .lg .middle } **[API Reference - Commands](API-REFERENCE-COMMANDS.md)**

    Complete documentation for all 46 commands organized by category with parameters, usage examples, and output formats

- :gear:{ .lg .middle } **[Command Parameters](reference/COMMAND-PARAMETERS.md)**

    Detailed parameter reference, types, defaults, aliases, and environment variables for every command

- :warning:{ .lg .middle } **[Error Scenarios & Recovery](reference/ERROR-SCENARIOS.md)**

    Comprehensive error handling guide with 50+ error scenarios, codes, causes, and recovery steps

- :bulb:{ .lg .middle } **[Command Examples](reference/COMMAND-EXAMPLES.md)**

    Real-world usage patterns, workflows, and practical examples for all command categories

</div>

**Quick Links:**

- [All 46 Commands with Full Documentation](API-REFERENCE-COMMANDS.md)
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

    All 46 commands organized

- :sparkles:{ .lg .middle } **[Skills & Agents](skills-agents.md)**

    Understanding the AI system

- :page_facing_up:{ .lg .middle } **[Quick Reference](REFCARD.md)**

    Command cheat sheet

- :scroll:{ .lg .middle } **[API Reference](API-REFERENCE-COMMANDS.md)**

    Complete documentation for all 46 commands

</div>

## Key Command Categories

| Category          | Count   | Description                                                                                                                                                     |
| ------------------ | ------- | ---------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| **Smart**          | 9       | Universal command, orchestrator, checks, help, hub (root-level commands)                                                                                          |
| **Documentation**  | 21      | Smart docs with update, sync, check, website, API, changelog, guides, tutorial, workflow                                                                           |
| **Site**           | 16      | Full site wizard with 8 ADHD-friendly presets, theme, nav, audit                                                                                                   |
| **Code & Check**   | 17 + 1  | Code: linting, testing, debugging, refactoring, CI fixes, deps management; Check: pre-flight validation                                                            |
| **Git**            | 15      | Repository initialization, branch management, worktrees, sync, recap, clean, two-layer branch protection (local hook + GitHub-side baseline), learning guides     |
| **CI**             | 6       | Detection, generation, validation                                                                                                                                  |
| **Architecture**   | 4       | Analysis, diagrams, planning, reviews                                                                                                                              |
| **Distribution**   | 5       | Marketplace, Homebrew, PyPI, curl installers                                                                                                                       |
| **Planning**       | 3       | Feature planning, sprints, roadmaps                                                                                                                                |
| **Orchestrate**    | 4       | Multi-agent dispatch, drive loops, swarm levels                                                                                                                    |
| **Workflow**       | 14      | Brainstorming, task management, spec capture, getting unstuck                                                                                                      |
| **Utils**          | 2       | Misc helpers                                                                                                                                                       |
| **Total**          | **115** | **Complete development workflow coverage**                                                                                                                         |

!!! info "Latest: v2.61.2 — Guard Suite Consolidation"
    [PR #272](https://github.com/Data-Wise/craft/pull/272) consolidates the branch-guard and
    no-switch-guard into a skill-driven operations layer under `skills/dev/git/`, adds
    `--classify`/`GUARD_DRY_RUN=1` ground-truth mode, a portable `sedi()` wrapper, and 62 new
    tests. Four stale shims thinned, 3 orphan docs archived. [PR #270](https://github.com/Data-Wise/craft/pull/270) removes
    dead agent-dispatch from `/craft:do` and `/release`, adds `verify-surfaces.sh --report-only`/`--version`,
    and ships a [`release-rollback`](runbooks/release-rollback.md) manual-undo runbook.
    See the [full changelog](CHANGELOG.md) for all releases, or visit the [News](NEWS.md) page for release highlights.

## Links

- [GitHub Repository](https://github.com/Data-Wise/craft)
- [Issue Tracker](https://github.com/Data-Wise/craft/issues)
- [Changelog](CHANGELOG.md)
- [ROADMAP](https://github.com/Data-Wise/craft/blob/main/docs/archive/ROADMAP.md)
