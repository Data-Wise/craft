# Tutorial: Orchestrator Modes Compared

> **Learn when to use each orchestrator mode** — See the same task executed in all 4 modes with performance metrics, output comparisons, and decision guidance.

**Level:** Intermediate
**Time:** 20-30 minutes
**Prerequisites:** Basic understanding of `/craft:orchestrate`

---

## What You'll Learn

1. How the same task executes differently across 4 modes
2. Performance and token usage trade-offs
3. When to use each mode
4. How to read orchestrator output
5. Mode selection decision trees

---

## The Reference Task

We'll execute this task in all 4 modes to compare behavior:

**Task:** "Implement user authentication with OAuth 2.0"

**Expected complexity:**

- 5 subtasks (design, backend, frontend, tests, docs)
- Estimated time: 8-15 minutes depending on mode
- Involves: architecture decisions, code implementation, test generation

---

## Mode 1: Default (Balanced)

### Execution

```bash
/craft:orchestrate "implement user authentication with OAuth 2.0" default
```

### Step-by-Step Output

**Step 1: Mode Selection (skipped — specified in command)**

**Step 2: Task Analysis**

```
## TASK ANALYSIS

Request: Implement user authentication with OAuth 2.0
Complexity: complex
Mode: default (2 agents max)
Estimated subtasks: 5
Delegation strategy: hybrid (parallel + sequential)

| # | Task                    | Agent      | Priority | Dependencies | Wave |
|---|-------------------------|------------|----------|--------------|------|
| 1 | Design OAuth flow       | arch-1     | P0       | none         | 1    |
| 2 | Implement backend auth  | code-1     | P0       | 1            | 2    |
| 3 | Create login UI         | code-2     | P1       | 1            | 2    |
| 4 | Generate test suite     | test-1     | P1       | 2,3          | 3    |
| 5 | Update documentation    | doc-1      | P2       | 2,3          | 3    |
```

**Step 3: Confirmation**

```
? Proceed with this orchestration plan?
  > Yes - Start Wave 1 (Recommended)
    Modify steps
    Change mode
    Cancel
```

Choose: **Yes - Start Wave 1**

**Step 4: Wave 1 Execution**

```
Spawning Wave 1 agents...
  arch-1: Design OAuth flow (running)

[arch-1] Analyzing OAuth 2.0 requirements...
[arch-1] Designing authentication flow...
[arch-1] Completed (2.1 minutes)

Output:
  ✓ OAuth 2.0 flow diagram
  ✓ Security model documented
  ✓ Token strategy (JWT + refresh)
```

**Step 5: Wave 1 Checkpoint**

```
## WAVE 1 COMPLETE

| Agent  | Task             | Status  | Output                        |
|--------|------------------|---------|-------------------------------|
| arch-1 | OAuth flow       | Done    | Architecture design complete  |

Next: Wave 2
| Agent  | Task             | Dependencies |
|--------|------------------|--------------|
| code-1 | Backend auth     | arch-1       |
| code-2 | Login UI         | arch-1       |

? Wave 1 complete. Continue to Wave 2?
  > Yes - Continue (Recommended)
    Review results first
    Modify next wave
    Stop here
```

Choose: **Yes - Continue**

**Step 6: Wave 2 Execution**

```
Spawning Wave 2 agents...
  code-1: Implement backend auth (running)
  code-2: Create login UI (running)

[code-1] Implementing /auth/login endpoint...
[code-2] Creating Login.tsx component...

[code-1] Completed (4.3 minutes)
[code-2] Completed (3.8 minutes)

Output:
  code-1:
    ✓ 4 endpoints created (/auth/login, /logout, /refresh, /callback)
    ✓ JWT middleware implemented
    ✓ Session management

  code-2:
    ✓ Login component (React + TypeScript)
    ✓ OAuth redirect handling
    ✓ Token storage
```

**Step 7: Wave 2 Checkpoint**

```
## WAVE 2 COMPLETE

Continue to Wave 3? (test-1, doc-1)
  > Yes - Continue
```

**Step 8: Wave 3 Execution**

```
Spawning Wave 3 agents...
  test-1: Generate test suite (running)
  doc-1: Update documentation (running)

[test-1] Completed (2.7 minutes)
[doc-1] Completed (1.9 minutes)
```

**Step 9: Final Summary**

```
## ORCHESTRATION COMPLETE

Total time: 8.3 minutes
Agents spawned: 5
Waves executed: 3
Context used: ~15,000 tokens

Results:
  ✓ Wave 1: Architecture designed (1 agent)
  ✓ Wave 2: Backend + frontend implemented (2 agents)
  ✓ Wave 3: Tests + docs completed (2 agents)

Next steps:
  1. Review generated code
  2. Run tests: /craft:test:run
  3. Commit changes
```

### Metrics

| Metric | Value |
|--------|-------|
| **Total time** | 8.3 minutes |
| **Max parallel agents** | 2 |
| **Checkpoints** | 3 (per wave) |
| **Token usage** | ~15,000 tokens |
| **User interactions** | 4 prompts (confirmation + 3 wave checkpoints) |

### When to Use Default Mode

- ✅ Most tasks (balanced speed and oversight)
- ✅ Unknown complexity (mode auto-adjusts)
- ✅ Want checkpoints between major phases
- ✅ Budget-conscious (moderate token usage)

---

## Mode 2: Debug (Verbose)

### Execution

```bash
/craft:orchestrate "implement user authentication with OAuth 2.0" debug
```

### Key Differences

**Step 4: Wave 1 Execution (Verbose)**

```
Spawning Wave 1 agents...
  arch-1: Design OAuth flow (running)

[arch-1] DEBUG: Starting architecture analysis...
[arch-1] DEBUG: Analyzing OAuth 2.0 specification...
[arch-1] DEBUG: Reading RFC 6749...
[arch-1] DEBUG: Evaluating security models...
[arch-1] DEBUG: Comparing authorization code vs implicit flow...
[arch-1] DEBUG: Decision: Authorization code + PKCE recommended
[arch-1] DEBUG: Designing token refresh strategy...
[arch-1] DEBUG: Generating architecture diagram...
[arch-1] DEBUG: Validating design against OWASP guidelines...
[arch-1] Completed (2.8 minutes)

Detailed output:
  ✓ OAuth 2.0 flow diagram (see docs/arch/oauth-flow.md)
  ✓ Security model:
    - Authorization code flow with PKCE
    - State parameter for CSRF protection
    - Secure token storage (httpOnly cookies)
  ✓ Token strategy:
    - Access token: JWT (15 min expiry)
    - Refresh token: Opaque (30 day expiry)
  ✓ Error handling: 401/403 responses documented

[arch-1] Full trace (187 lines):
  [Click to expand detailed execution log]
```

**Step 5: Wave 1 Checkpoint (Every Step)**

```
## WAVE 1 STEP 1 COMPLETE

Agent arch-1 has completed design.

? Review arch-1 output and proceed?
  > Yes - Continue to Wave 2
    Show full trace
    Pause orchestration
    Abort
```

### Metrics

| Metric | Value |
|--------|-------|
| **Total time** | 12.1 minutes |
| **Max parallel agents** | 1 (sequential only) |
| **Checkpoints** | 5 (every agent) |
| **Token usage** | ~22,000 tokens |
| **User interactions** | 6 prompts (confirmation + 5 step checkpoints) |
| **Output verbosity** | Maximum (full traces) |

### When to Use Debug Mode

- ✅ Debugging a failing orchestration
- ✅ Understanding how decisions are made
- ✅ Learning orchestrator behavior
- ✅ Troubleshooting agent coordination issues
- ❌ Time-sensitive tasks (slowest mode)
- ❌ Simple tasks (overkill)

---

## Mode 3: Optimize (Fast)

### Execution

```bash
/craft:orchestrate "implement user authentication with OAuth 2.0" optimize
```

### Key Differences

**Step 4: Wave 1-3 Execution (Parallel)**

```
Spawning ALL agents in parallel...
  arch-1: Design OAuth flow (running)
  code-1: Implement backend (waiting for arch-1)
  code-2: Create login UI (waiting for arch-1)
  test-1: Generate tests (waiting for code-1, code-2)
  doc-1: Update docs (waiting for code-1, code-2)

[arch-1] Completed (2.0 minutes)
  ↓ Dependency resolved for code-1, code-2

[code-1] Started (waiting released)
[code-2] Started (waiting released)

[code-1] Completed (3.9 minutes)
[code-2] Completed (3.4 minutes)
  ↓ Dependency resolved for test-1, doc-1

[test-1] Started
[doc-1] Started

[test-1] Completed (2.3 minutes)
[doc-1] Completed (1.6 minutes)

All agents complete.
```

**Step 5: Wave-End Checkpoint Only**

```
## WAVE 1-3 COMPLETE (NO INTERMEDIATE CHECKPOINTS)

All 5 agents completed successfully.

Results summary:
  ✓ arch-1: Architecture designed
  ✓ code-1: Backend implemented
  ✓ code-2: Frontend implemented
  ✓ test-1: Tests generated
  ✓ doc-1: Docs updated

? Review results?
  > Yes - Show summary
    No - Finish orchestration
```

### Metrics

| Metric | Value |
|--------|-------|
| **Total time** | 5.2 minutes |
| **Max parallel agents** | 4 |
| **Checkpoints** | 1 (wave-end only) |
| **Token usage** | ~18,000 tokens |
| **User interactions** | 2 prompts (confirmation + final review) |
| **Output verbosity** | Low (summaries only) |

### When to Use Optimize Mode

- ✅ Time-sensitive tasks
- ✅ High trust in orchestrator
- ✅ Bulk operations (refactoring, test generation)
- ✅ CI/CD automation
- ❌ Complex tasks requiring oversight
- ❌ Unknown requirements (might spawn incorrect agents)

---

## Mode 4: Release (Thorough)

### Execution

```bash
/craft:orchestrate "implement user authentication with OAuth 2.0" release
```

### Key Differences

**Step 4: Wave 1 Execution (Full Audit)**

```
Spawning Wave 1 agents...
  arch-1: Design OAuth flow (running)

[arch-1] Starting architecture analysis...
[arch-1] Completed (2.5 minutes)

Output:
  ✓ OAuth 2.0 flow diagram
  ✓ Security model documented
  ✓ Token strategy (JWT + refresh)

Diff from baseline:
  + docs/arch/oauth-flow.md (247 lines)
  + docs/arch/security-model.md (183 lines)

Audit trail:
  [2026-01-29 18:42:15] arch-1 started
  [2026-01-29 18:42:17] Analyzing OAuth 2.0 spec
  [2026-01-29 18:43:22] Security model designed
  [2026-01-29 18:44:38] Architecture diagram generated
  [2026-01-29 18:44:45] arch-1 completed
```

**Step 5: Wave 1 Checkpoint (Every Step with Audit)**

```
## WAVE 1 STEP 1 COMPLETE

Agent arch-1 completed.

Files created:
  + docs/arch/oauth-flow.md (247 lines)
  + docs/arch/security-model.md (183 lines)

Audit log (47 entries):
  [Click to view full execution timeline]

? Review arch-1 output and proceed?
  > Yes - Continue to Wave 2
    Show full diff
    Show audit log
    Pause orchestration
    Abort
```

### Metrics

| Metric | Value |
|--------|-------|
| **Total time** | 14.7 minutes |
| **Max parallel agents** | 4 |
| **Checkpoints** | 5 (every agent + full audit) |
| **Token usage** | ~28,000 tokens |
| **User interactions** | 6 prompts (confirmation + 5 step checkpoints with audit) |
| **Output verbosity** | Maximum (full traces + diffs + audit) |

### When to Use Release Mode

- ✅ Pre-release validation
- ✅ Critical production changes
- ✅ Compliance requirements (audit trail needed)
- ✅ Complex multi-team coordination
- ❌ Rapid prototyping
- ❌ Daily development tasks

---

## Side-by-Side Comparison

### Execution Timeline

```
Mode      0m   2m   4m   6m   8m   10m  12m  14m
────────  ────┼────┼────┼────┼────┼────┼────┼────┤
default   ████████████████░░░░░░░░░░░░░░░░░░░░  8.3m
debug     ████████████████████████░░░░░░░░░░░░  12.1m
optimize  ██████████░░░░░░░░░░░░░░░░░░░░░░░░░░  5.2m
release   ██████████████████████████████░░░░░░  14.7m
```

### Output Comparison (Same Agent, 4 Modes)

**Agent:** arch-1 (Design OAuth flow)

| Mode | Output Detail | Lines |
|------|---------------|-------|
| **default** | Summary + key decisions | 23 lines |
| **debug** | Full trace + reasoning | 187 lines |
| **optimize** | Summary only | 8 lines |
| **release** | Summary + diff + audit trail | 94 lines |

### Token Budget Analysis

```
Mode        Total Tokens   Per Agent Avg   Compression Impact
──────────  ─────────────  ──────────────  ──────────────────
default     ~15,000        ~3,000          Low (70% threshold)
debug       ~22,000        ~4,400          High (90% threshold)
optimize    ~18,000        ~3,600          Medium (60% threshold)
release     ~28,000        ~5,600          High (85% threshold)
```

### User Interaction Points

| Mode | Confirmation | Wave Checkpoints | Total Prompts |
|------|-------------|------------------|---------------|
| **default** | 1 | 3 (per wave) | 4 |
| **debug** | 1 | 5 (per agent) | 6 |
| **optimize** | 1 | 1 (wave-end only) | 2 |
| **release** | 1 | 5 (per agent + audit) | 6 |

---

## Mode Selection Decision Tree

```
Start: Need to orchestrate a task

├─ Is this for production release?
│   └─ YES → Use release mode
│       (Full audit trail required)
│
├─ Is time critical? (< 10 minutes needed)
│   └─ YES → Use optimize mode
│       (Fast parallel execution)
│
├─ Are you debugging a failed orchestration?
│   └─ YES → Use debug mode
│       (Verbose traces, sequential execution)
│
└─ Everything else?
    └─ Use default mode
        (Balanced speed and oversight)
```

### Task Complexity → Recommended Mode

| Complexity | Characteristics | Recommended Mode |
|------------|----------------|------------------|
| **Simple** | 1-2 agents, < 5 min | `optimize` |
| **Moderate** | 3-4 agents, 5-10 min | `default` |
| **Complex** | 5+ agents, 10-15 min | `default` or `release` |
| **Critical** | Any complexity, production impact | `release` |

---

## Advanced: Mid-Task Mode Switching

**Current limitation:** You cannot switch modes mid-task.

**Workaround:** Abort and restart with different mode.

```bash
# Start with default
/craft:orchestrate "complex task" default

# Wave 1 completes successfully
# Wave 2 fails with unclear error

# Abort
/craft:orchestrate abort

# Restart in debug mode to see traces
/craft:orchestrate "complex task" debug
```

**Future feature request:** Mid-task mode switching

```bash
# Hypothetical future feature
/craft:orchestrate mode debug  # Switch current session to debug mode
```

---

## Performance Tips

### Pre-Select Mode to Skip Prompt

```bash
# Default: Shows mode selection prompt
/craft:orchestrate "task"

# Explicit: Skips mode selection, faster
/craft:orchestrate "task" default
```

### Use --dry-run to Preview

```bash
# See orchestration plan without spawning agents
/craft:orchestrate "task" default --dry-run

Output:
  ✓ Task analysis
  ✓ Agent allocation
  ✓ Parallelization strategy
  ✓ Estimated time: ~8 minutes

  (No agents spawned, no token usage)
```

### Budget Allocation Strategies

| Budget Available | Mode Choice | Reasoning |
|-----------------|-------------|-----------|
| **< 50% context** | `optimize` | Fast execution, lower token overhead |
| **50-70% context** | `default` | Balanced usage |
| **70-90% context** | `debug` (if needed) | High compression threshold |
| **> 90% context** | Compress first | Run `/craft:orchestrate compress` before starting |

### When to Use Each Mode by Project Phase

| Phase | Typical Mode | Reasoning |
|-------|--------------|-----------|
| **Prototyping** | `optimize` | Speed over oversight |
| **Development** | `default` | Balanced workflow |
| **Code review** | `default` | Need checkpoints |
| **Pre-release** | `release` | Full audit required |
| **Debugging** | `debug` | Need verbose traces |

---

## Troubleshooting by Mode

### Default Mode Failures

**Symptom:** Wave checkpoint shows unexpected agent output.

**Solution:**

```bash
# Re-run in debug mode to see full traces
/craft:orchestrate abort
/craft:orchestrate "same task" debug
```

### Debug Mode: Reading Verbose Output

**Symptom:** Too much output, hard to find key information.

**Solution:**

```bash
# Use grep to filter agent output
/craft:orchestrate status | grep "ERROR"

# Or redirect to file for later review
/craft:orchestrate "task" debug > orchestration-log.txt 2>&1
```

### Optimize Mode: Parallel Conflicts

**Symptom:** Agents modify the same file simultaneously, causing conflicts.

**Solution:**

```bash
# Switch to default mode (limits parallelization)
/craft:orchestrate "same task" default

# Or manually coordinate agent dependencies
# (Not currently supported — future feature)
```

### Release Mode: Performance Issues

**Symptom:** Release mode takes too long (> 15 minutes).

**Solution:**

```bash
# Use default mode for most of orchestration
/craft:orchestrate "task" default

# Then switch to release mode for final validation
/craft:check thorough --for release
```

---

## Summary

### Mode Recommendation Matrix

| Scenario | Mode | Time | Tokens | Oversight |
|----------|------|------|--------|-----------|
| **Daily development** | `default` | 8-10m | ~15k | Medium |
| **Debugging issues** | `debug` | 12-15m | ~22k | High |
| **Time-sensitive** | `optimize` | 5-8m | ~18k | Low |
| **Pre-release** | `release` | 14-18m | ~28k | Maximum |

### Quick Reference Table

| Need | Mode |
|------|------|
| **Fastest execution** | `optimize` |
| **Most oversight** | `release` |
| **Most verbose traces** | `debug` |
| **Best balance** | `default` |
| **Lowest token usage** | `default` |
| **Audit trail** | `release` |

---

## Next Steps

- **Guide:** [Orchestrator Deep Dive](../guide/orchestrator.md) — Full reference
- **Tutorial:** [Interactive Orchestration](interactive-orchestration.md) — Basic flow
- **Pattern guide:** [Interactive Commands](../guide/interactive-commands.md) — How the pattern works
- **Command:** [/craft:orchestrate](../commands/orchestrate.md) — All flags and options
