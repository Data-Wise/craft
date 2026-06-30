# Craft Skills & Agents

> **TL;DR**: 42 skills auto-activate from conversation context (no command to memorize) and 8 specialized agents handle deep work. Browse by category below; use [`/craft:hub`](commands/hub.md) to discover commands.

Craft includes 42 auto-activating skills and 8 specialized agents for comprehensive development support.

## Skills (42 total)

Skills automatically activate based on conversation context, providing just-in-time expertise.

### Architecture (1)

| Name | Description | Path |
|------|-------------|------|
| system-architect | Software architecture, system design, and technical decision-making | `skills/architecture/SKILL.md` |

### Check (1)

| Name | Description | Path |
|------|-------------|------|
| preflight-check | Context-aware pre-flight validation (commit/PR/release/deploy) — orchestrates lint, tests, types, version sync, stale refs, docs, hook conflicts | `skills/check/SKILL.md` |

### CI (1)

| Name | Description | Path |
|------|-------------|------|
| project-detector | Smart detection of project types, build tools, and CI requirements | `skills/ci/SKILL.md` |

### Code (2)

| Name | Description | Path |
|------|-------------|------|
| sync-features | Chain command-audit, release-watch, and desktop-watch into a prioritized action plan | `skills/code/SKILL.md` |
| demonstration-builder | Designs progressive runnable code examples for tutorials, vignettes, presentations, and documentation | `skills/code/demonstration-builder/SKILL.md` |

### Design (3)

| Name | Description | Path |
|------|-------------|------|
| backend-designer | Backend architecture, API design, database decisions, and authentication patterns | `skills/design/backend-designer/SKILL.md` |
| devops-helper | CI/CD, deployment, Docker, testing automation, and infrastructure decisions | `skills/design/devops-helper/SKILL.md` |
| frontend-designer | UI/UX design, component architecture, accessibility, and frontend performance | `skills/design/frontend-designer/SKILL.md` |

### Dev (1)

| Name | Description | Path |
|------|-------------|------|
| git-workflow | Full git lifecycle — repo init, branches, worktrees, remote sync, status/recap, local + GitHub-side branch protection, undo/safety reference docs | `skills/dev/git/SKILL.md` |

### Distribution (6)

| Name | Description | Path |
|------|-------------|------|
| dist-extras | Non-Homebrew distribution channels — PyPI publishing, GitHub-release curl installers, Claude Code plugin marketplace listings | `skills/distribution/dist-extras/SKILL.md` |
| distribution-strategist | Recommends optimal distribution channels based on project type and target audience | `skills/distribution/distribution-strategist/SKILL.md` |
| homebrew-formula-expert | Homebrew formula creation, best practices, and troubleshooting | `skills/distribution/homebrew-formula-expert/SKILL.md` |
| homebrew-multi-formula | Coordinate releases across multiple Homebrew formulas with dependency ordering | `skills/distribution/homebrew-multi-formula/SKILL.md` |
| homebrew-setup-wizard | Implementation logic for the Homebrew automation setup wizard | `skills/distribution/homebrew-setup-wizard/SKILL.md` |
| homebrew-workflow-expert | GitHub Actions workflows for automated Homebrew formula updates and releases | `skills/distribution/homebrew-workflow-expert/SKILL.md` |

### Documentation (8)

| Name | Description | Path |
|------|-------------|------|
| architecture-decision-records | Write and maintain ADRs following best practices for technical decision documentation | `skills/docs/architecture-decision-records/SKILL.md` |
| changelog-automation | Automate changelog generation from commits, PRs, and releases (Keep a Changelog format) | `skills/docs/changelog-automation/SKILL.md` |
| claude-md-lifecycle | Manage CLAUDE.md lifecycle (init, sync, audit, fix, optimize, edit) — project-local and global `~/.claude/CLAUDE.md` | `skills/docs/claude-md/SKILL.md` |
| doc-classifier | Classify documentation needs based on code changes | `skills/docs/doc-classifier/SKILL.md` |
| mermaid-linter | Mermaid validation, auto-fix, health score with MCP-powered syntax checking | `skills/docs/mermaid-linter/SKILL.md` |
| nav-sync | Keep mkdocs.yml in sync with docs/ — directory-driven nav updates, new-page scaffolding, ADHD-friendly nav reorganization | `skills/docs/navigation/SKILL.md` |
| openapi-spec-generation | Generate and maintain OpenAPI 3.1 specifications from code and design-first specs | `skills/docs/openapi-spec-generation/SKILL.md` |
| site-lifecycle | Manage docs site lifecycle (MkDocs, Quarto, pkgdown) — init/create/theme through build/preview/audit through deploy/publish/update | `skills/docs/site-management/SKILL.md` |

### Guard & Insights (2)

| Name | Description | Path |
|------|-------------|------|
| guard-audit | Analyze branch-guard.sh rules and propose config changes to reduce false positives | `skills/guard-audit/SKILL.md` |
| insights-apply | Extract suggestions from insights report and apply them to global CLAUDE.md via sync pipeline | `skills/insights-apply/SKILL.md` |

### Hooks (1)

| Name | Description | Path |
|------|-------------|------|
| hooks | Common PostToolUse/PreToolUse hook templates for quality gates. Provides ready-to-install JSON blocks for MkDocs strict mode, linting, and other automated checks, with setup instructions for each. | `skills/hooks/SKILL.md` |

### Modes (1)

| Name | Description | Path |
|------|-------------|------|
| mode-controller | Manages craft plugin execution modes (default, debug, optimize, release) | `skills/modes/SKILL.md` |

### Orchestration (5)

| Name | Description | Path |
|------|-------------|------|
| drive-engine | Reusable execution body behind `/craft:orchestrate:drive` — parse-or-derive ORCHESTRATE phases, dispatch file-scoped subagents, and run the authoritative real verify gate | `skills/orchestration/drive-engine/SKILL.md` |
| plan-orchestrator | Produce concrete planning artifacts (ORCHESTRATE files, feature breakdowns, sprint backlogs, roadmaps) from specs | `skills/orchestration/plan-orchestrator/SKILL.md` |
| session-state | Manages orchestrator session state persistence — save, load, resume, and history | `skills/orchestration/session-state/SKILL.md` |
| task-analyzer | Analyzes natural language task descriptions and routes to appropriate craft commands | `skills/orchestration/task-analyzer/SKILL.md` |
| orchestrator-resilience | Reference templates for orchestrator-v2 agent error handling (retry/backoff, circuit breaker, escalation) and execution timeline display — loaded on agent failure or `timeline` request, not on the happy path | `skills/orchestrator-resilience/SKILL.md` |
| workflow-engine | Reusable execution body behind `/craft:orchestrate:workflow` — compile a WORKFLOW definition to a deterministic wave plan, dispatch file-scoped agents under a run-wide semaphore, structurally gate every output, and run a first-class verify gate | `skills/orchestration/workflow-engine/SKILL.md` |

### Planning (1)

| Name | Description | Path |
|------|-------------|------|
| project-planner | Project planning, estimation, and delivery management | `skills/planning/SKILL.md` |

### Release (1)

| Name | Description | Path |
|------|-------------|------|
| release | Orchestrates the full release pipeline from pre-flight checks through GitHub release creation | `skills/release/SKILL.md` |

### Testing (2)

| Name | Description | Path |
|------|-------------|------|
| test-generator | Generates dogfooding test suites (automated + interactive) for any project type | `skills/testing/test-generator/SKILL.md` |
| test-strategist | Test strategy, coverage optimization, and quality assurance | `skills/testing/test-strategist/SKILL.md` |

### Workflow (4)

| Name | Description | Path |
|------|-------------|------|
| adhd-workflow | Session and task workflow support — done/recap/next/focus/stuck/spec-review/refine for ADHD-friendly flow | `skills/workflow/adhd-workflow/SKILL.md` |
| brainstorm | Generate BRAINSTORM/SPEC documents from topic + project/git context (2 decision points: depth+focus, one follow-up); deep multi-agent work hands off to `--orch` | `skills/workflow/brainstorm/SKILL.md` |
| brainstorm-insights | Aggregate session facet history into a friction/goals report (directory name kept for path stability; ideation moved to the `brainstorm` skill above) | `skills/workflow/brainstorm-insights/SKILL.md` |
| background-task-manager | Manage already-launched background tasks — status inspection, output retrieval, cancellation | `skills/workflow/task-management/SKILL.md` |
| prompt-refiner | Refine a vague request into a sharp prompt using project context (before/after + Accept/Edit/Use-original) — the engine behind the `--refine` flag; replaces the deprecated `/refine` | `skills/workflow/prompt-refiner/SKILL.md` |

## Agents (8 total)

Specialized agents can be invoked explicitly or delegated to by the orchestrator.

### Documentation Agents (6)

| Name | Description | Path |
|------|-------------|------|
| api-documenter | OpenAPI 3.1 documentation, SDK generation, and developer portal creation | `agents/docs/api-documenter.md` |
| demo-engineer | VHS tape file generation for terminal GIF demos | `agents/docs/demo-engineer.md` |
| docs-architect | Comprehensive technical documentation from existing codebases - architecture guides and technical manuals | `agents/docs/docs-architect.md` |
| mermaid-expert | Flowcharts, diagrams, MCP validation + SVG rendering | `agents/docs/mermaid-expert.md` |
| reference-builder | Exhaustive technical references, API documentation, and configuration guides | `agents/docs/reference-builder.md` |
| tutorial-engineer | Step-by-step tutorials and progressive learning experiences from code | `agents/docs/tutorial-engineer.md` |

### Orchestration Agents (2)

| Name | Description | Path |
|------|-------------|------|
| orchestrator | Manages background agent delegation, task parallelization, and result synthesis | `agents/orchestrator.md` |
| orchestrator-v2 | Enhanced orchestrator with subagent monitoring, mode-aware execution, and ADHD-optimized status tracking | `agents/orchestrator-v2.md` |

*Note: `orchestrator-v2` is the recommended version. The original `orchestrator` exists for backward compatibility.*

### Agent Platform Features

Some agents use Claude Code platform features for enhanced behavior:

| Feature | Agents | Effect |
|---------|--------|--------|
| `background: true` | docs-architect, reference-builder, tutorial-engineer | Run as non-blocking background tasks |
| `memory: project` | orchestrator-v2 | Persistent project-scoped memory across sessions |
| `skills` | orchestrator-v2 (session-state, task-analyzer) | Preloaded skill context at agent startup |

## Skill Activation

Skills trigger automatically based on keywords in conversation context. For example:

- Mention "API design" or "database" to activate **backend-designer**
- Mention "CI/CD" or "deployment" to activate **devops-helper**
- Mention "release" or "ship it" to activate **release**
- Mention "test strategy" to activate **test-strategist**

## Mode-Aware Behavior

Both skills and agents adapt behavior based on execution mode:

| Mode | Behavior |
|------|----------|
| **default** | Quick analysis, high-level recommendations |
| **debug** | Verbose output, detailed traces, step-by-step |
| **optimize** | Parallel execution, focus on performance |
| **release** | Comprehensive audit, production-ready checks |

## See Also

- **[Commands Reference](commands.md)** - All available commands
- **[Architecture Guide](architecture.md)** - How Craft works
- **[Orchestrator Guide](orchestrator.md)** - Multi-agent coordination
