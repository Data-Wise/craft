# Craft Skills & Agents

Craft includes 26 auto-activating skills and 8 specialized agents for comprehensive development support.

## Skills (26 total)

Skills automatically activate based on conversation context, providing just-in-time expertise.

### Architecture (1)

| Name | Description | Path |
|------|-------------|------|
| system-architect | Software architecture, system design, and technical decision-making | `skills/architecture/system-architect.md` |

### CI (1)

| Name | Description | Path |
|------|-------------|------|
| project-detector | Smart detection of project types, build tools, and CI requirements | `skills/ci/project-detector.md` |

### Design (3)

| Name | Description | Path |
|------|-------------|------|
| backend-designer | Backend architecture, API design, database decisions, and authentication patterns | `skills/design/backend-designer.md` |
| devops-helper | CI/CD, deployment, Docker, testing automation, and infrastructure decisions | `skills/design/devops-helper.md` |
| frontend-designer | UI/UX design, component architecture, accessibility, and frontend performance | `skills/design/frontend-designer.md` |

### Distribution (5)

| Name | Description | Path |
|------|-------------|------|
| distribution-strategist | Recommends optimal distribution channels based on project type and target audience | `skills/distribution/distribution-strategist.md` |
| homebrew-formula-expert | Homebrew formula creation, best practices, and troubleshooting | `skills/distribution/homebrew-formula-expert.md` |
| homebrew-multi-formula | Coordinate releases across multiple Homebrew formulas with dependency ordering | `skills/distribution/homebrew-multi-formula.md` |
| homebrew-setup-wizard | Implementation logic for the Homebrew automation setup wizard | `skills/distribution/homebrew-setup-wizard.md` |
| homebrew-workflow-expert | GitHub Actions workflows for automated Homebrew formula updates and releases | `skills/distribution/homebrew-workflow-expert.md` |

### Documentation (5)

| Name | Description | Path |
|------|-------------|------|
| architecture-decision-records | Write and maintain ADRs following best practices for technical decision documentation | `skills/docs/architecture-decision-records/SKILL.md` |
| changelog-automation | Automate changelog generation from commits, PRs, and releases (Keep a Changelog format) | `skills/docs/changelog-automation/SKILL.md` |
| doc-classifier | Classify documentation needs based on code changes | `skills/docs/doc-classifier/skill.md` |
| mermaid-linter | Mermaid validation, auto-fix, health score with MCP-powered syntax checking | `skills/docs/mermaid-linter/skill.md` |
| openapi-spec-generation | Generate and maintain OpenAPI 3.1 specifications from code and design-first specs | `skills/docs/openapi-spec-generation/SKILL.md` |

### Guard & Insights (2)

| Name | Description | Path |
|------|-------------|------|
| guard-audit | Analyze branch-guard.sh rules and propose config changes to reduce false positives | `skills/guard-audit/SKILL.md` |
| insights-apply | Extract suggestions from insights report and apply them to global CLAUDE.md via sync pipeline | `skills/insights-apply/SKILL.md` |

### Modes (1)

| Name | Description | Path |
|------|-------------|------|
| mode-controller | Manages craft plugin execution modes (default, debug, optimize, release) | `skills/modes/mode-controller.md` |

### Orchestration (2)

| Name | Description | Path |
|------|-------------|------|
| session-state | Manages orchestrator session state persistence - save, load, resume, and history | `skills/orchestration/session-state.md` |
| task-analyzer | Analyzes natural language task descriptions and routes to appropriate craft commands | `skills/orchestration/task-analyzer.md` |

### Planning (1)

| Name | Description | Path |
|------|-------------|------|
| project-planner | Project planning, estimation, and delivery management | `skills/planning/project-planner.md` |

### Release (1)

| Name | Description | Path |
|------|-------------|------|
| release | Orchestrates the full release pipeline from pre-flight checks through GitHub release creation | `skills/release/SKILL.md` |

### Testing (2)

| Name | Description | Path |
|------|-------------|------|
| test-generator | Generates dogfooding test suites (automated + interactive) for any project type | `skills/testing/test-generator.md` |
| test-strategist | Test strategy, coverage optimization, and quality assurance | `skills/testing/test-strategist.md` |

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
