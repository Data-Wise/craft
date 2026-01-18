# Claude Code 2.1.0 Integration Guide

> **Intelligent Task Routing & Multi-Agent Orchestration**: Leverage Claude Code 2.1.0 capabilities for smart task handling

**Available Since:** v1.23.0 (Claude Code 2.1.0 Integration)
**Commands:** /craft:do, /craft:check, /craft:orchestrate
**Features:** Complexity scoring, hot-reload validators, agent delegation, session teleportation

---

## Overview

Craft integrates Claude Code 2.1.0 advanced features to provide intelligent task routing and multi-agent orchestration:

1. **Complexity Scoring** - Automatic task classification (0-10 scale)
2. **Smart Routing** - Command vs Agent vs Orchestrator routing
3. **Hot-Reload Validators** - Dynamic validation skills without restart
4. **Agent Delegation** - Specialized agents for different task types
5. **Forked Context** - Isolated execution to keep chat clean
6. **Session Teleportation** - Resume work across devices

---

## Quick Start

### 1. Use Smart Routing

```bash
# Simple task → Routes to commands
/craft:do "lint code"

# Moderate task → Routes to agent
/craft:do "add feature with tests and documentation"

# Complex task → Routes to orchestrator
/craft:do "design comprehensive authentication system with OAuth2, sessions, error handling, tests, and docs"
```

### 2. Pre-Flight Validation

```bash
# Auto-discover validators and validate
/craft:check
```

### 3. Orchestrate Multi-Step Work

```bash
# Multi-agent coordination
/craft:orchestrate "implement teaching workflow feature"
```

---

## Complexity Scoring Algorithm

The heart of smart routing is the 7-factor complexity scoring system.

### Algorithm at a Glance

```mermaid
flowchart TD
    A["Task Input<br/>e.g. 'add feature with tests and docs'"] -->|Analyze| B["Score: 0-10"]
    B -->|0-3| C["Commands<br/>Specific tools<br/>< 30 sec"]
    B -->|4-7| D["Agent<br/>Specialist agent<br/>5-30 min"]
    B -->|8-10| E["Orchestrator<br/>Multi-agent<br/>30 min+"]

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#c8e6c9
    style D fill:#b3e5fc
    style E fill:#ffccbc
```

### The 7 Factors (each +2 points, max 10)

| Factor | Detects | Examples |
|--------|---------|----------|
| **1. Multi-Step** | 2+ operations | "add AND test", "build THEN deploy" |
| **2. Cross-Category** | 2+ work areas | code + testing, code + docs |
| **3. Planning** | Design/architecture | "design system", "optimize performance" |
| **4. Research** | Investigation needed | "investigate issue", "analyze patterns" |
| **5. Multi-File** | Large scope | 5+ files or "system-wide", "entire" |
| **6. Complex Keywords** | Recognized complexity | "comprehensive", "redesign", "microservice" |
| **7. Architecture** | System-wide changes | "redesign architecture", "migrate to microservices" |

### Scoring Examples

#### Example 1: Simple Task (0 points)

```
Task: "Fix typo in README"
Score: 0/10 → Commands
Time: < 30 sec
```

**Analysis:**
```mermaid
graph LR
    A["Fix typo"] -->|Multi-step?| B["No"]
    A -->|Cross-category?| C["No"]
    A -->|Planning?| D["No"]
    A -->|Research?| E["No"]
    A -->|Multi-file?| F["No"]
    A -->|Complex KW?| G["No"]
    A -->|Architecture?| H["No"]

    B --> I["Score: 0/10"]
    C --> I
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J["→ /craft:docs:update"]

    style A fill:#e1f5ff
    style I fill:#fff3e0
    style J fill:#c8e6c9
```

#### Example 2: Moderate Task (6 points)

```
Task: "Add feature with comprehensive tests and documentation"
Score: 6/10 → Agent
Time: 5-30 min
```

**Analysis:**
```mermaid
graph LR
    A["Add feature with<br/>comprehensive tests<br/>and documentation"]
    A -->|Multi-step?| B["✓ Yes +2"]
    A -->|Cross-category?| C["✓ 3 areas +2"]
    A -->|Planning?| D["No"]
    A -->|Research?| E["No"]
    A -->|Multi-file?| F["No"]
    A -->|Complex KW?| G["✓ 'comprehensive' +2"]
    A -->|Architecture?| H["No"]

    B --> I["Score: 6/10"]
    C --> I
    G --> I

    I --> J["→ feature-developer agent"]

    style A fill:#e1f5ff
    style B fill:#fff9c4
    style C fill:#fff9c4
    style G fill:#fff9c4
    style I fill:#fff3e0
    style J fill:#b3e5fc
```

#### Example 3: Complex Task (10 points, capped)

```
Task: "Design and implement comprehensive authentication system with OAuth2,
       PKCE, session management, error handling, extensive tests, and full docs"
Score: 10/10 → Orchestrator
Time: 30 min - several hours
```

**Analysis:**
```mermaid
graph LR
    A["Design & implement<br/>comprehensive auth<br/>with OAuth2, sessions,<br/>errors, tests, docs"]

    A -->|Multi-step?| B["✓ Yes +2"]
    A -->|Cross-category?| C["✓ 5 areas +4"]
    A -->|Planning?| D["✓ 'design' +2"]
    A -->|Research?| E["No"]
    A -->|Multi-file?| F["✓ Multi +2"]
    A -->|Complex KW?| G["✓ 'comprehensive' +2"]
    A -->|Architecture?| H["✓ 'design system' +2"]

    B --> I["Score: 10/10<br/>CAPPED"]
    C --> I
    D --> I
    F --> I
    G --> I
    H --> I

    I --> J["→ Orchestrator v2<br/>Multi-Agent Coordination"]

    style A fill:#e1f5ff
    style B fill:#fff9c4
    style C fill:#fff9c4
    style D fill:#fff9c4
    style F fill:#fff9c4
    style G fill:#fff9c4
    style H fill:#fff9c4
    style I fill:#fff3e0
    style J fill:#ffccbc
```

---

## Routing Decision Flow

### Full Decision Tree

```mermaid
flowchart TD
    A["Start"] --> B{{"Analyze task<br/>Calculate score"}}

    B -->|0-3 Points| C["Route: Commands"]
    B -->|4-7 Points| D["Route: Single Agent"]
    B -->|8-10 Points| E["Route: Orchestrator v2"]

    C --> F["Find matching<br/>specific command"]
    D --> G["Select best agent<br/>from 5 specialists"]
    E --> H["Plan multi-phase<br/>work with agents"]

    F --> I["Execute<br/>< 30 seconds"]
    G --> J["Execute<br/>5-30 minutes"]
    H --> K["Execute<br/>30+ minutes"]

    I --> L["Return<br/>Output"]
    J --> L
    K --> L

    style A fill:#e1f5ff
    style B fill:#fff3e0
    style C fill:#c8e6c9
    style D fill:#b3e5fc
    style E fill:#ffccbc
    style F fill:#dcedc8
    style G fill:#b2dfdb
    style H fill:#f0f4c3
    style I fill:#f1f8e9
    style J fill:#f1f8e9
    style K fill:#f1f8e9
    style L fill:#f1f8e9
```

---

## Agent Delegation System

When a task scores 4-7 points, /craft:do delegates to a specialist agent.

### Available Agents

| Agent | Specialization | Best For | Model |
|-------|---|---|---|
| **feature-developer** | Feature implementation | "add new feature with tests" | Sonnet |
| **bug-detective** | Bug investigation & fixing | "investigate and fix slow queries" | Sonnet |
| **docs-architect** | Documentation & guides | "write comprehensive migration guide" | Sonnet |
| **api-documenter** | API specification & SDKs | "document REST API with OpenAPI" | Sonnet |
| **tutorial-engineer** | Step-by-step tutorials | "create setup tutorial" | Sonnet |

### Agent Selection Logic

```mermaid
graph TD
    A["Task Routed to Agent<br/>Score 4-7"] --> B{{"Analyze keywords<br/>and task type"}}

    B -->|"add", "feature", "implement"| C["→ feature-developer"]
    B -->|"fix", "bug", "issue", "investigate"| D["→ bug-detective"]
    B -->|"doc", "guide", "tutorial", "architecture"| E["→ docs-architect"]
    B -->|"API", "OpenAPI", "SDK", "client"| F["→ api-documenter"]
    B -->|"tutorial", "step-by-step", "onboarding"| G["→ tutorial-engineer"]
    B -->|No match| H["→ feature-developer<br/>default"]

    C --> I["Agent executes<br/>in forked context<br/>Clean chat history"]
    D --> I
    E --> I
    F --> I
    G --> I
    H --> I

    I --> J["Summary returned<br/>to user"]

    style A fill:#b3e5fc
    style B fill:#fff3e0
    style C fill:#dcedc8
    style D fill:#dcedc8
    style E fill:#dcedc8
    style F fill:#dcedc8
    style G fill:#dcedc8
    style H fill:#dcedc8
    style I fill:#c8e6c9
    style J fill:#f1f8e9
```

---

## Hot-Reload Validators

`/craft:check` discovers and runs validation skills dynamically without restart.

### Available Validators

| Validator | Purpose | Trigger |
|-----------|---------|---------|
| **test-coverage** | Verify test coverage thresholds | When code changes detected |
| **broken-links** | Check for broken documentation links | Before site deploy |
| **lint-check** | Run language-specific linting | Code commit checks |

### How Hot-Reload Works

```mermaid
flowchart TD
    A["/craft:check command"] --> B["Scan for validators<br/>with hot_reload: true"]
    B --> C["Load validator metadata<br/>from frontmatter YAML"]
    C --> D["Discover 3 validators"]
    D --> E["Run all validators<br/>in parallel"]
    E --> F["Return results<br/>without restart needed"]

    style A fill:#b3e5fc
    style B fill:#fff3e0
    style C fill:#fff3e0
    style D fill:#fff3e0
    style E fill:#c8e6c9
    style F fill:#f1f8e9
```

### Creating Custom Validators

```bash
# Generate validator template
/craft:check:gen-validator my-validator

# Edit and customize
vim .claude-plugin/skills/validators/my-validator.md

# Run to test (no restart needed!)
/craft:check
```

**Validator Template Structure:**

```yaml
---
name: my-validator
type: skill
hot_reload: true        # Enable dynamic loading
description: "Check custom requirements"
categories: [validation]
---

# Your validator implementation
```

---

## Orchestrator v2 Features

When a task scores 8-10 points, /craft:orchestrate v2 coordinates multiple agents.

### Multi-Agent Coordination

```mermaid
graph TD
    A["Complex Task<br/>Score: 8-10"] -->|"Plan phases"| B["Wave 1<br/>Architecture<br/>Planning"]

    B --> C["Spawn parallel<br/>agents"]
    C --> D["Agent 1<br/>Backend<br/>Design"]
    C --> E["Agent 2<br/>Frontend<br/>Design"]

    D --> F["Wave 2<br/>Implementation<br/>Sequential"]
    E --> F

    F --> G["Agent 3<br/>Backend<br/>Code"]
    F --> H["Agent 4<br/>Frontend<br/>Code"]

    G --> I["Wave 3<br/>Testing &<br/>Integration"]
    H --> I

    I --> J["Agent 5<br/>Test<br/>Suite"]
    I --> K["Agent 6<br/>Integration<br/>Tests"]

    J --> L["Wave 4<br/>Documentation<br/>& Deployment"]
    K --> L

    L --> M["Agent 7<br/>Docs<br/>Writer"]
    L --> N["Agent 8<br/>Deployment<br/>Guide"]

    M --> O["Final Output<br/>Multi-agent<br/>results"]
    N --> O

    style A fill:#ffccbc
    style B fill:#f0f4c3
    style C fill:#fff3e0
    style D fill:#b2dfdb
    style E fill:#b2dfdb
    style F fill:#f0f4c3
    style G fill:#b2dfdb
    style H fill:#b2dfdb
    style I fill:#f0f4c3
    style J fill:#b2dfdb
    style K fill:#b2dfdb
    style L fill:#f0f4c3
    style M fill:#b2dfdb
    style N fill:#b2dfdb
    style O fill:#f1f8e9
```

### Resilience Patterns

Orchestrator v2 handles failures with 9 recovery strategies:

| Pattern | Use Case | Strategy |
|---------|----------|----------|
| **Retry** | Transient failures | Exponential backoff 2-16 sec |
| **Timeout** | Slow agents | Cancel after threshold, fallback |
| **Circuit Breaker** | Repeated failures | CLOSED → HALF-OPEN → OPEN |
| **Fallback** | Primary fails | Use secondary approach |
| **Cascade** | Multi-step failures | Pause, assess, adapt |
| **Logging** | Debugging | Structured event logs |
| **Monitoring** | Health check | Periodic validation |
| **Escalation** | Unrecoverable | Promote to higher-level agent |
| **Abort** | Blocking issues | Clean shutdown & recovery |

---

## Session Teleportation

Resume work across devices with `/craft:orchestrate:resume`

### Session State Tracking

```mermaid
graph LR
    A["Session Start<br/>Device A"] --> B["Auto-save<br/>Session State"]
    B --> C["Encrypted Cloud<br/>Sync"]
    C --> D["Device B<br/>Available"]
    D --> E["Resume Session<br/>/craft:orchestrate:resume"]
    E --> F["Load State<br/>Continue Work"]
    F --> G["Resume from<br/>Checkpoint"]

    style A fill:#b3e5fc
    style B fill:#fff3e0
    style C fill:#f0f4c3
    style D fill:#b3e5fc
    style E fill:#c8e6c9
    style F fill:#dcedc8
    style G fill:#f1f8e9
```

### Using Session Teleportation

```bash
# Start work on Device A
/craft:do "implement feature X"
# ... work in progress ...
# State auto-saved

# Switch to Device B
/craft:orchestrate:resume
# Continues exactly where you left off!
```

---

## Integration Testing

Craft includes 27+ integration tests validating Claude Code 2.1.0 features:

### Test Coverage

```bash
# Run all integration tests
python3 tests/test_integration_orchestrator_workflows.py

# Test complexity scoring
python3 tests/test_complexity_scoring.py

# Test hot-reload validators
python3 tests/test_hot_reload_validators.py

# Test agent hooks
python3 tests/test_agent_hooks.py
```

### Test Results

| Test Suite | Tests | Pass | Coverage |
|-----------|-------|------|----------|
| Complexity Scoring | 15 | 15 | 100% |
| Hot-Reload Validators | 9 | 9 | 95% |
| Agent Hooks | 13 | 13 | 100% |
| Integration Orchestrator | 13 | 13 | 100% |
| **Total** | **37+** | **37+** | **98%+** |

---

## Mode-Aware Execution

Configure execution mode based on task requirements:

| Mode | Max Agents | Compression | Use When |
|------|-----------|-------------|----------|
| **default** | 2 | 70% | Balanced tasks |
| **debug** | 1 (sequential) | 90% | Troubleshooting |
| **optimize** | 4 (parallel) | 60% | Need speed |
| **release** | 4 + validation | 85% | Pre-release |

```bash
# Explicit mode selection
/craft:do "add feature" optimize
/craft:do "debug issue" debug
/craft:orchestrate "complex task" release
```

---

## Best Practices

### 1. Leverage Complexity Scoring

Good: "Add feature with tests" (lets router choose)
Bad: "Use agent to add feature" (constrains routing)

### 2. Be Specific About Requirements

Good: "Add feature with unit tests, integration tests, and documentation"
Better: "Add OAuth2 authentication with PKCE flow, session management, extensive unit/integration tests, and security docs"

### 3. Use Hot-Reload Validators

```bash
# Check all validators without restart
/craft:check

# Run specific validator
/craft:check test-coverage
```

### 4. Monitor Agent Execution

```bash
# See agent delegation happening
/craft:do "complex task" --verbose

# Check session state
/craft:orchestrate:status
```

### 5. Resume Across Sessions

```bash
# Continue previous work
/craft:orchestrate:resume

# Or start new
/craft:do "new task"
```

---

## Troubleshooting

| Issue | Cause | Fix |
|-------|-------|-----|
| Task routes to command but seems complex | Low keyword match | Use more specific task description |
| Agent takes too long | Task too complex for agent | Break into smaller tasks or use orchestrator |
| Validator not running | Not marked with hot_reload: true | Add to validator frontmatter |
| Session not resuming | Device not synced | Check cloud sync status |

---

## Performance Metrics

### Complexity Scoring

```
Pure scoring: < 2ms
With routing decision: < 5ms
```

### Agent Delegation

```
Single agent: 5-30 minutes
Discovery: < 100ms
Execution: variable by task
```

### Orchestrator v2

```
Planning phase: 1-5 minutes
Multi-agent parallel: 5-30 minutes
Result aggregation: < 1 minute
```

---

## See Also

- [Complexity Scoring Algorithm](complexity-scoring-algorithm.md) - Deep dive into 7 factors
- [Teaching Workflow Guide](teaching-workflow.md) - Specialized workflow for courses
- [Orchestrator Documentation](orchestrator.md) - Advanced multi-agent features
- [Commands Reference](../commands/) - All 99 commands

---

## Release History

- **v1.24.0** - Full integration, 516+ tests, 87% documentation
- **v1.23.1** - Integration tests (27+ tests passing)
- **v1.23.0** - Initial release (Waves 1-4)

---

*Last Updated: 2026-01-18*
