# Claude Code 2.1.0 Integration Guide

⏱️ **25 minutes** • 🟠 Advanced • ✓ Complete guide

> **TL;DR** (30 seconds)
>
> - **What:** Claude Code 2.1.0 adds intelligent task routing with complexity scoring and hot-reload validators
> - **Why:** Automatically choose between commands, agents, and orchestration based on task difficulty
> - **How:** Use `/craft:do "task"` and the system scores (0-10) and routes intelligently
> - **Next:** Read about [Dependency Management](dependency-management-advanced.md) or [Integration Tests](integration-testing.md)

Claude Code 2.1.0 introduced smart task routing that automatically delegates work based on task complexity. This guide explains how it works and how to use it effectively.

## Quick Start

!!! abstract "Smart Task Routing"
    ```bash
    # Simple task - routes to specific command
    /craft:do "lint the code"

    # Moderate task - routes to specialized agent
    /craft:do "refactor authentication module with tests"

    # Complex task - routes to orchestrator for multi-agent coordination
    /craft:do "add OAuth authentication, database schema, tests, and documentation"
    ```

## System Overview

### The Problem It Solves

Before v2.1.0:

- User had to choose: use specific command, or orchestrator, or single agent
- No automatic decision based on task complexity
- "lint code" and "redesign architecture" treated the same way

After v2.1.0:

- System analyzes task automatically
- Routes to optimal handler (command → agent → orchestrator)
- Simple tasks stay fast, complex tasks get full coordination

### How It Works: Three Levels

```
User Task
    ↓
Complexity Scorer
    ↓
    ├─ Score 0-3: Route to Commands ─→ Specific command executes immediately
    ├─ Score 4-7: Route to Agent ───→ Single specialized agent handles it
    └─ Score 8-10: Route to Orchestrator → Multi-agent coordination
```

## Complexity Scoring Algorithm

### The 7 Factors

The system scores tasks on a 0-10 scale based on 7 factors. Each factor adds up to +2 points:

| Factor | Triggers When | Example | Points |
|--------|---------------|---------|--------|
| **Multi-step** | 2+ action verbs, "and", "then", "after" | "lint and test code" | +2 |
| **Cross-category** | Spans 2+ categories (code, test, docs, CI) | "fix code and update docs" | +2 |
| **Requires planning** | Design, architecture, strategy needed | "design authentication system" | +2 |
| **Requires research** | Investigation/exploration needed | "research OAuth best practices" | +2 |
| **Multi-file impact** | Affects 5+ files or mentions 'multiple', 'all', 'system' | "update all tests" | +2 |
| **Inherent complexity** | Keywords like "optimization", "microservice", "migration" | "optimize database queries" | +2 |
| **Architectural change** | Combines redesign/refactor with architecture/system | "redesign system architecture" | +2 |

**Maximum Score:** 14 (clamped to 10)

### Scoring Examples

#### Simple Tasks (Score 0-3)

```
Task: "lint the code"
  ✓ Single action verb: +0
  ✓ Single category (code): +0
  ✓ No planning needed: +0
  ✓ No research: +0
  ✓ Single file area: +0

Score: 0 → ROUTE TO COMMANDS (/craft:code:lint)
```

```
Task: "run tests"
  ✓ Single action: +0
  ✓ Single category (test): +0

Score: 0-1 → ROUTE TO COMMANDS (/craft:test:run)
```

```
Task: "add a new function"
  ✓ Single action (add): +0
  ✓ Single category (code): +0

Score: 1 → ROUTE TO COMMANDS (/craft:code:*:add)
```

#### Moderate Tasks (Score 4-7)

```
Task: "refactor authentication module with tests"
  ✓ Multi-step (refactor AND tests): +2
  ✓ Cross-category (code AND test): +2
  ✓ No architecture planning: +0

Score: 4 → ROUTE TO AGENT (agent-code-specialist)
```

```
Task: "optimize database queries and add monitoring"
  ✓ Multi-step (optimize AND add): +2
  ✓ Cross-category (code AND ops): +2
  ✓ Inherent complexity (optimize): +2

Score: 6 → ROUTE TO AGENT (agent-architect)
```

```
Task: "add comprehensive error handling across modules"
  ✓ Multi-step pattern: +2
  ✓ Cross-category (code AND test): +2
  ✓ Multi-file (across modules): +2

Score: 6 → ROUTE TO AGENT
```

#### Complex Tasks (Score 8-10)

```
Task: "add OAuth authentication with database migrations and tests"
  ✓ Multi-step (add AND migrations AND tests): +2
  ✓ Cross-category (code, database, test, security): +2
  ✓ Requires planning (architecture): +2
  ✓ Multi-file impact (auth, db, test, docs): +2
  ✓ Inherent complexity (authentication): +2

Score: 10 → ROUTE TO ORCHESTRATOR (multi-agent coordination)
```

```
Task: "redesign API architecture to support microservices"
  ✓ Planning needed (redesign): +2
  ✓ Architectural change (redesign + architecture): +2
  ✓ Cross-category (code, architecture, test): +2
  ✓ Inherent complexity (microservice): +2
  ✓ Multi-file impact (system-wide): +2

Score: 10 → ROUTE TO ORCHESTRATOR
```

```
Task: "implement CI/CD pipeline with testing, security scans, and deployment"
  ✓ Multi-step (implement AND testing AND security AND deployment): +2
  ✓ Cross-category (CI, test, security, ops): +2
  ✓ Requires planning (pipeline design): +2
  ✓ Multi-file impact (entire CI system): +2

Score: 8 → ROUTE TO ORCHESTRATOR
```

## Routing Decisions

### Routing Table

```
Score 0-3: COMMANDS
  └─ Direct command execution
  └─ No agent overhead
  └─ Fast (< 1 second)
  └─ Examples: lint, test, format, commit

Score 4-7: AGENT
  └─ Single specialized agent
  └─ Agent can break task into subtasks
  └─ Moderate complexity (1-5 minutes)
  └─ Examples: refactor, optimize, add features

Score 8-10: ORCHESTRATOR
  └─ Multi-agent coordination
  └─ Task decomposition
  └─ Parallel execution
  └─ Complex work (5-30 minutes)
  └─ Examples: major features, system redesigns
```

### Routing Decision Flowchart

```
START: /craft:do "task"
  ↓
Score complexity (0-10)
  ↓
  ├─ 0-3 → Commands
  │  └─ Execute single command
  │  └─ Return immediately
  │
  ├─ 4-7 → Agent
  │  ├─ Analyze task
  │  ├─ Create subtasks
  │  └─ Execute sequentially
  │
  └─ 8-10 → Orchestrator
     ├─ Decompose into subtasks
     ├─ Identify agent types needed
     ├─ Spawn agents in parallel
     ├─ Monitor progress
     ├─ Coordinate results
     └─ Return aggregated result
```

## Hot-Reload Validators

### What They Do

Validators are checks that run automatically after tool execution. They validate:

- ✅ Test coverage (via `test-coverage` validator)
- ✅ Broken links (via `broken-links` validator)
- ✅ Code quality (via `lint-check` validator)

If validation fails, the orchestrator can:

1. Show results to user
2. Auto-fix if possible
3. Request user intervention
4. Rerun with fixes

### Validator Lifecycle

```
1. Tool Execution
   ↓
2. Hot-Reload Trigger
   ├─ File modified? Yes
   ├─ Test affected? Yes
   ├─ Docs changed? Yes
   ↓
3. Run Validators
   ├─ test-coverage validator
   │  └─ Run tests, measure coverage
   │  └─ Check if > 80%
   │
   ├─ broken-links validator
   │  └─ Find all markdown links
   │  └─ Check if links work
   │
   └─ lint-check validator
      └─ Run linter
      └─ Check exit code
   ↓
4. Collect Results
   ├─ Coverage: 87% ✅
   ├─ Links: 0 broken ✅
   ├─ Linting: 0 errors ✅
   ↓
5. Report
   └─ All validators passed
   └─ Ready to commit/PR
```

### Using Validators

#### Enable Validators

```bash
# Automatic with orchestrator (score 8+)
/craft:do "add comprehensive authentication"

# Explicit validation before commit
/craft:check --with-validators

# Specific validators only
/craft:check --validators test-coverage,broken-links
```

#### Validator Configuration

Validators are declared in command frontmatter:

```yaml
---
name: do
description: Smart task routing
validators:
  - test-coverage:
      minimum: 80
      fail_on_low: true
  - broken-links:
      ignore_external: false
  - lint-check:
      strict: true
---
```

**Validator Options:**

- `test-coverage:minimum` - Minimum coverage percentage
- `broken-links:ignore_external` - Ignore external URLs
- `lint-check:strict` - Fail on warnings

#### Creating Custom Validators

Create `.claude-plugin/skills/validation/my-validator.md`:

```yaml
---
name: my-validator
description: Custom validation skill
trigger:
  - post-tool-use
  - any-file-modified
validation:
  type: custom
  command: bash scripts/my-validation.sh
  expect_exit: 0
---
# Validator documentation and logic
```

Then reference in command:

```yaml
validators:
  - my-validator:
      threshold: 90
```

### Built-in Validators

#### test-coverage Validator

**Purpose:** Ensure new code has test coverage

**Triggers after:** Code changes, test additions

**Checks:**

- Run tests on modified files
- Measure coverage percentage
- Compare against minimum (default: 80%)
- Suggest tests if coverage low

**Output:**

```
Coverage Analysis:
  Total: 87%
  New code: 92%
  Status: ✅ OK (>= 80%)
```

#### broken-links Validator

**Purpose:** Find dead links in documentation

**Triggers after:** Markdown file changes

**Checks:**

- Parse all markdown files
- Extract links (internal and external)
- Verify links work
- Report broken links

**Output:**

```
Link Validation:
  Total checked: 45
  Working: 43
  Broken: 2

  ❌ docs/guide/nonexistent.md
  ❌ https://invalid-url-123.example.com
```

#### lint-check Validator

**Purpose:** Ensure code quality

**Triggers after:** Code file changes

**Checks:**

- Run linter on changed files
- Check exit code (0 = pass)
- Report violations

**Output:**

```
Lint Check:
  Files checked: 8
  Status: ✅ OK (0 errors, 0 warnings)
```

## Hot-Reload System

### What It Does

The hot-reload system monitors file changes during execution:

```
1. Agent executes task
   ├─ Modifies files
   ├─ Runs tests
   ├─ Updates docs
   ↓
2. Hot-reload triggers on file change
   ├─ Detected: utils/new_function.py
   ├─ Detected: tests/test_new_function.py
   ├─ Detected: docs/guide/new_function.md
   ↓
3. Auto-run validators
   ├─ test-coverage: ✅ 87%
   ├─ broken-links: ✅ None
   ├─ lint-check: ✅ Pass
   ↓
4. Report results immediately
   └─ Continue execution or report issue
```

### Enabling Hot-Reload

```bash
# Automatic with agents (score 4+)
/craft:do "refactor authentication"

# Explicit enable
/craft:code:refactor --with-hot-reload

# Disable if needed
/craft:code:refactor --no-hot-reload
```

### Hot-Reload Configuration

In `.claude/settings.json`:

```json
{
  "hotReload": {
    "enabled": true,
    "validators": ["test-coverage", "broken-links", "lint-check"],
    "debounceMs": 1000,
    "ignorePaths": [".git", "node_modules", ".env"]
  }
}
```

## Agent Hooks

### What They Are

Agent hooks allow you to run custom code at orchestration lifecycle points:

```
PreToolUse   → Before agent runs command
PostToolUse  → After agent completes command
Stop         → On orchestrator shutdown
```

### Hook Lifecycle

```
START: Orchestrator spawned
  ↓
PreToolUse
  └─ Setup environment
  └─ Initialize logging
  └─ Check prerequisites
  ↓
Agent executes task
  ├─ Run tests
  ├─ Build code
  ├─ Update docs
  ↓
PostToolUse
  ├─ Run validators
  ├─ Cleanup temp files
  └─ Report results
  ↓
Stop
  ├─ Archive session
  ├─ Save state
  └─ Cleanup
```

### Creating Hooks

Create `.claude-plugin/hooks/my-hook.sh`:

```bash
#!/bin/bash
# PreToolUse hook

event_type="$1"  # "PreToolUse" | "PostToolUse" | "Stop"
agent_id="$2"    # orchestrator-v2, agent-code-specialist, etc.
task="$3"        # Task being executed

case "$event_type" in
  PreToolUse)
    echo "[HOOK] Starting task: $task"
    # Set up environment
    export CRAFT_SESSION_ID=$(date +%s)
    ;;
  PostToolUse)
    echo "[HOOK] Completed task: $task"
    # Run validators
    /craft:check --validators test-coverage,lint-check
    ;;
  Stop)
    echo "[HOOK] Cleaning up"
    # Archive logs
    tar -czf "logs-$CRAFT_SESSION_ID.tar.gz" /tmp/craft-logs/
    ;;
esac
```

Then register in command frontmatter:

```yaml
---
name: do
hooks:
  - orchestrate-hooks.sh:
      events: ["PreToolUse", "PostToolUse", "Stop"]
---
```

## Session State Management

### Session Persistence

Sessions capture the state of work for resumption:

**Session Schema (JSON v1.0.0):**

```json
{
  "schema_version": "1.0.0",
  "session_id": "2026-01-18-abc123",
  "status": "in_progress",
  "goal": "Add OAuth authentication",
  "started_at": "2026-01-18T14:30:00Z",
  "agents": [
    {
      "id": "arch-1",
      "type": "docs-architect",
      "status": "completed",
      "output": "..."
    },
    {
      "id": "code-1",
      "type": "code-specialist",
      "status": "in_progress",
      "progress": 0.60
    }
  ],
  "completed_work": [
    {
      "task": "Design authentication system",
      "status": "completed",
      "output": "Created architecture.md"
    }
  ],
  "pending_tasks": [
    {
      "task": "Implement OAuth endpoints",
      "status": "pending"
    }
  ],
  "context_usage": {
    "tokens_used": 25000,
    "percentage": 19.5
  }
}
```

### Session Teleportation

Resume sessions on different devices:

```bash
# Device 1: Start work
/craft:do "add authentication" optimize

# System creates session file
# → ~/.claude/sessions/2026-01-18-abc123.json

# Device 2: Resume same session
/craft:continue 2026-01-18-abc123

# System loads session
# → Resumes from where you left off
# → Reuses context from previous device
# → Continues execution
```

### Session Commands

```bash
# Continue interrupted session
/craft:continue SESSION_ID

# List recent sessions
/craft:sessions --list

# View session details
/craft:sessions --show SESSION_ID

# Archive completed session
/craft:sessions --archive SESSION_ID

# Delete old sessions
/craft:sessions --cleanup 7d
```

## Agent Resilience

### 9 Recovery Strategies

When agents encounter errors, they use these strategies:

| Strategy | When Used | Example |
|----------|-----------|---------|
| **Retry** | Temporary error | Network timeout → wait 2s → retry |
| **Fallback** | Tool unavailable | Missing `npm` → try `yarn` |
| **Decompose** | Blocked by complexity | Too many changes → split into smaller tasks |
| **Escalate** | User decision needed | Delete file? → ask user |
| **Rollback** | Change caused issue | Revert to previous version |
| **Skip** | Optional task | No tests? → skip test coverage check |
| **Alternative** | Blocked approach | Can't use tool A → use tool B |
| **Pause** | Manual intervention | Need env var → pause and ask |
| **Checkpoint** | Session recovery | Save progress → can resume later |

### Resilience in Action

```
Task: "Add authentication with OAuth"
  ↓
Agent starts
  ↓
Error: Missing `openssl`
  ├─ Strategy: Fallback
  ├─ Alternative: Use system openssl
  ├─ Success! ✅
  ↓
Continue task
  ↓
Error: Network timeout checking OAuth provider
  ├─ Strategy: Retry (attempt 1)
  ├─ Failed, wait 2s
  ├─ Strategy: Retry (attempt 2)
  ├─ Success! ✅
  ↓
Error: Test fails - missing mock data
  ├─ Strategy: Decompose
  ├─ Split into: add OAuth + add tests
  ├─ Add OAuth first
  ├─ Success! ✅
  ├─ Create separate task for tests
  ↓
Task complete
```

## Performance Characteristics

### Scoring Performance

| Operation | Time |
|-----------|------|
| Score single task | 50-100ms |
| Score + routing decision | 150-250ms |
| Agent spawn | 500ms-1s |
| Orchestrator startup | 1-2s |

### Routing Overhead

```
Direct command: 100ms baseline
  └─ /craft:do "lint" adds 150ms scoring overhead
  └─ Total: ~250ms

Agent delegation: 500ms baseline
  └─ /craft:do "refactor code" adds 150ms scoring + 500ms spawn overhead
  └─ Total: ~650ms (worth it for complex work)

Orchestrator: 2s baseline
  └─ /craft:do "add auth" adds 150ms scoring + 2s spawn overhead
  └─ Total: ~2.2s (worth it for multi-hour work)
```

## Best Practices

### 1. Let System Route Your Tasks

```bash
# Good - let system decide routing
/craft:do "add user authentication with tests"

# Avoid - forcing specific routing
/craft:code:add-auth  # Loses automatic decomposition

# Avoid - vague tasks
/craft:do "work on authentication"  # Unclear what's needed
```

### 2. Be Specific in Task Descriptions

```bash
# Good - clear and specific
/craft:do "add OAuth 2.0 authentication with Google provider, test coverage for 3 flows, and update README with setup instructions"

# Poor - vague
/craft:do "add auth"

# Poor - too broad
/craft:do "refactor everything"
```

### 3. Use Score to Understand Complexity

```bash
# Check how system scored your task
/craft:do "add feature" --show-score

# Output:
# Complexity Score: 4
# Routing: Agent
# Reasoning: Cross-category (code+test), multi-step
```

### 4. Enable Validators for Important Work

```bash
# Critical work - strict validation
/craft:do "add payment processing" --validators test-coverage:minimum=90,lint-check:strict

# Routine work - basic validation
/craft:do "update documentation" --validators broken-links

# Experimental - no validation
/craft:do "try new approach" --no-validators
```

### 5. Use Session Resumption for Long Tasks

```bash
# Start long task
/craft:do "redesign authentication system" optimize

# If interrupted - resume exactly where you left off
/craft:continue SESSION_ID

# System reloads context and continues
```

## Troubleshooting

### Issue: Simple Task Routes to Orchestrator

**Diagnosis:**

```bash
/craft:do "fix typo" --show-score
# Output: Score: 8 (unexpected!)
```

**Possible Causes:**

- Task description has architectural keywords
- Multiple categories detected incorrectly
- Complexity keywords trigger scoring

**Solution:**

```bash
# Be more specific
/craft:do "fix typo in README.md" --routing commands

# Or use direct command
/craft:docs:sync  # Simpler approach
```

### Issue: Complex Task Routes to Agent Only

**Diagnosis:**

```bash
/craft:do "add OAuth, database schema, tests" --show-score
# Output: Score: 6 (should be 8+)
```

**Possible Causes:**

- Keywords not recognized
- Categories not matched correctly

**Solution:**

```bash
# Add architectural language
/craft:do "implement OAuth authentication system with database schema design and comprehensive test coverage"

# Check scoring again
# Should now route to orchestrator
```

### Issue: Validator Fails, Blocking Work

**Diagnosis:**

```
Test coverage: 65% (minimum: 80%)
Cannot proceed.
```

**Solution:**

```bash
# Option 1: Add tests
/craft:do "add tests to reach 80% coverage"

# Option 2: Override for exploratory work
/craft:do "add feature" --skip-validators

# Option 3: Lower threshold temporarily
/craft:do "add feature" --validators test-coverage:minimum=60
```

## Next Steps

1. **Try routing:** Use `/craft:do "task"` instead of specific commands
2. **Check scores:** Add `--show-score` to understand routing decisions
3. **Enable validators:** Use `--validators` on important work
4. **Read related guides:**
   - [Integration Testing](integration-testing.md) - How tests validate the orchestration system
   - [Dependency Management](dependency-management-advanced.md) - Advanced tool management
   - [Orchestrator](orchestrator.md) - Detailed orchestrator documentation

## Summary

Claude Code 2.1.0 provides:

- **Automatic routing** - System chooses optimal handler (command/agent/orchestrator)
- **Complexity scoring** - 7 factors scored 0-10
- **Hot-reload validators** - Automatic validation after changes
- **Agent hooks** - Customize lifecycle
- **Session persistence** - Resume interrupted work
- **9 recovery strategies** - Resilience for error handling

The system simplifies your workflow: just use `/craft:do "task"` and let intelligence handle the complexity.
