# Skills & Agents

⏱️ **6 minutes** • 🟡 Intermediate • ✓ Understanding AI automation

> **TL;DR** (30 seconds)
>
> - **What:** 25 auto-triggered skills + 8 specialized agents for backend, docs, testing, distribution, and architecture
> - **Why:** AI automatically selects the right expertise for your task without manual intervention
> - **How:** Skills trigger on context (e.g., "API" activates backend-designer), agents handle long-running tasks
> - **Next:** Read [Orchestrator](orchestrator.md) to learn how they work together

## Skills (25 total)

Skills are auto-triggered expertise modules that activate based on conversation context.

### Architecture

| Name | Description | Path |
|------|-------------|------|
| system-architect | Software architecture, system design, technical decisions | `skills/architecture/system-architect.md` |

### CI

| Name | Description | Path |
|------|-------------|------|
| project-detector | Auto-detect project type, build tools, and CI requirements | `skills/ci/project-detector.md` |

### Design

| Name | Description | Path |
|------|-------------|------|
| backend-designer | API design, database decisions, authentication patterns | `skills/design/backend-designer.md` |
| devops-helper | CI/CD, deployment, Docker, infrastructure decisions | `skills/design/devops-helper.md` |
| frontend-designer | UI/UX design, component architecture, accessibility | `skills/design/frontend-designer.md` |

### Distribution

| Name | Description | Path |
|------|-------------|------|
| distribution-strategist | Multi-channel distribution planning (Homebrew, PyPI, npm) | `skills/distribution/distribution-strategist.md` |
| homebrew-formula-expert | Homebrew formula syntax and best practices | `skills/distribution/homebrew-formula-expert.md` |
| homebrew-multi-formula | Managing multiple formulas in a tap | `skills/distribution/homebrew-multi-formula.md` |
| homebrew-setup-wizard | Guided Homebrew setup implementation | `skills/distribution/homebrew-setup-wizard.md` |
| homebrew-workflow-expert | GitHub Actions automation for tap releases | `skills/distribution/homebrew-workflow-expert.md` |

### Documentation

| Name | Description | Path |
|------|-------------|------|
| architecture-decision-records | ADR generation and maintenance | `skills/docs/architecture-decision-records/SKILL.md` |
| changelog-automation | Changelog generation from commits and PRs | `skills/docs/changelog-automation/SKILL.md` |
| doc-classifier | Documentation type detection (guide, reference, tutorial, etc.) | `skills/docs/doc-classifier/skill.md` |
| mermaid-linter | Mermaid diagram syntax validation and fixing | `skills/docs/mermaid-linter/skill.md` |
| openapi-spec-generation | OpenAPI 3.1 spec generation and maintenance | `skills/docs/openapi-spec-generation/SKILL.md` |

### Guard & Insights

| Name | Description | Path |
|------|-------------|------|
| guard-audit | Analyze branch-guard rules, reduce false positives | `skills/guard-audit/SKILL.md` |
| insights-apply | Apply insights suggestions to CLAUDE.md via sync pipeline | `skills/insights-apply/SKILL.md` |

### Modes

| Name | Description | Path |
|------|-------------|------|
| mode-controller | Manages execution modes (default, debug, optimize, release) | `skills/modes/mode-controller.md` |

### Orchestration

| Name | Description | Path |
|------|-------------|------|
| session-state | Orchestrator state tracking and session management | `skills/orchestration/session-state.md` |
| task-analyzer | Routes tasks to appropriate tools and commands | `skills/orchestration/task-analyzer.md` |

### Planning

| Name | Description | Path |
|------|-------------|------|
| project-planner | Project planning, estimation, and delivery management | `skills/planning/project-planner.md` |

### Release

| Name | Description | Path |
|------|-------------|------|
| release | Full release pipeline orchestration | `skills/release/SKILL.md` |

### Testing

| Name | Description | Path |
|------|-------------|------|
| test-generator | Dogfooding test suite generation (automated + interactive) | `skills/testing/test-generator.md` |
| test-strategist | Test strategy, coverage optimization, QA | `skills/testing/test-strategist.md` |

## Agents (8 total)

Agents are long-running AI assistants for complex, multi-step tasks.

### Documentation Agents

| Name | Description | Path |
|------|-------------|------|
| api-documenter | OpenAPI 3.1 docs, SDK generation, developer portals | `agents/docs/api-documenter.md` |
| demo-engineer | VHS tape file generation for terminal GIF demos | `agents/docs/demo-engineer.md` |
| docs-architect | Technical documentation, architecture guides, manuals | `agents/docs/docs-architect.md` |
| mermaid-expert | Flowcharts, sequence diagrams, ERDs, architecture diagrams | `agents/docs/mermaid-expert.md` |
| reference-builder | API references, configuration guides, searchable docs | `agents/docs/reference-builder.md` |
| tutorial-engineer | Step-by-step tutorials, progressive learning experiences | `agents/docs/tutorial-engineer.md` |

### Orchestration Agents

| Name | Description | Path |
|------|-------------|------|
| orchestrator | Background agent delegation, task parallelization, result synthesis | `agents/orchestrator.md` |
| orchestrator-v2 | Enhanced orchestrator with subagent monitoring, mode-aware execution, ADHD-optimized tracking | `agents/orchestrator-v2.md` |

*Note: `orchestrator-v2` is the recommended version (v1.1.0+). The original `orchestrator` exists for backward compatibility.*

## How They Work Together

When you run `/craft:do "add authentication"`:

1. **task-analyzer** skill routes the task
2. **backend-designer** skill provides expertise
3. **test-strategist** skill suggests testing approach
4. Agents are invoked if the task requires long-running work

## Triggering Specific Agents

Use the Task tool directly:

```bash
# In your prompt to Claude
"Use the docs-architect agent to document the system"
```

## Next Steps

- [Orchestrator](orchestrator.md) - Advanced orchestration
- [Getting Started](getting-started.md) - Basic usage
