---
name: orchestrator-resilience
description: Reference templates for orchestrator-v2 agent error handling, retry/backoff, circuit breaker, escalation, and execution timeline display. Load when the orchestrator hits an agent failure, needs to show a retry/timeout/escalation report, or the user asks for a `timeline` view. NOT needed for normal happy-path orchestration — only for error recovery and timeline display.
---

# Orchestrator Resilience & Timeline Reference

Reference material extracted from `agents/orchestrator-v2.md` to keep that file's
always-loaded system prompt smaller. The orchestrator only needs this content when
an agent actually fails, times out, or the user requests a timeline — not on every
spawn. See `agents/orchestrator-v2.md` BEHAVIOR 5 and BEHAVIOR 9 for the pointers
into this skill.

## Error Categorization

Classify errors to determine appropriate recovery strategy:

| Category | Examples | Recovery Strategy |
|----------|----------|-------------------|
| **Transient** | Network timeout, rate limit, temporary file lock | Retry with backoff |
| **Resource** | Out of memory, disk full, process limit | Queue or wait, then retry |
| **Configuration** | Missing dependency, wrong path, invalid config | Auto-fix or escalate |
| **Logical** | Type error, failed test, syntax error | Investigate, then fix or escalate |
| **Permanent** | File not found, permission denied (after retry) | Escalate to user |

## Retry Logic with Exponential Backoff

```markdown
## 🔄 RETRY STRATEGY

**Error category**: Transient (network timeout)
**Agent**: code-1
**Attempt**: 2/3
**Previous wait**: 2 seconds
**Current wait**: 4 seconds (exponential backoff)
**Next wait**: 8 seconds (if needed)

### Backoff Schedule
| Attempt | Wait Time | Cumulative |
|---------|-----------|------------|
| 1 | 0s | 0s |
| 2 | 2s | 2s |
| 3 | 4s | 6s |
| 4 | 8s | 14s |
| 5 | 16s (max) | 30s |

**Modified approach**: Using alternate API endpoint
**Timeout**: 30s max per retry

[Retrying with modified approach...]
```

## Timeout Handling

```markdown
## ⏱️ TIMEOUT MANAGEMENT

**Agent**: test-1
**Task**: Full test suite execution
**Timeout**: 120s (2 minutes)
**Elapsed**: 125s
**Status**: ⚠️ Timeout exceeded

### Timeout Response
1. **Soft timeout** (at 100%): Send interrupt signal
2. **Wait grace period**: 10 seconds
3. **Hard timeout** (at 110%): Force terminate
4. **Fallback**: Run subset of tests (fast tests only)

**Action**: Terminated test-1, spawning test-1-fast with reduced scope
```

## Fallback Agent Selection

When an agent fails after retries, select alternative approach:

```markdown
## 🔄 FALLBACK AGENT SELECTION

**Original agent**: backend-architect
**Failure**: Exceeded context budget (3 consecutive failures)
**Root cause**: Task too complex for single agent

### Fallback Strategy
1. **Decompose**: Break into smaller subtasks
2. **Route**: Use simpler specialized agents
3. **Escalate**: Report to orchestrator for replanning

**Action taken**: Decomposing architecture task into 3 subtasks:
- [AGENT-A1] Data model design → code-quality-reviewer
- [AGENT-A2] API design → feature-dev
- [AGENT-A3] Integration → bug-detective

**ETA**: 15 min (vs 8 min original estimate)
```

## Circuit Breaker Pattern

Prevent cascade failures by tracking agent reliability:

```markdown
## ⚡ CIRCUIT BREAKER STATUS

| Agent | Success Rate | Circuit State | Action |
|-------|--------------|---------------|--------|
| code-1 | 95% (19/20) | 🟢 CLOSED | Normal operation |
| test-1 | 60% (3/5) | 🟡 HALF-OPEN | Limited retries |
| doc-1 | 20% (1/5) | 🔴 OPEN | Bypass, use fallback |

### Circuit States
- **CLOSED** (healthy): Normal operation, full retry budget
- **HALF-OPEN** (degraded): Limited retries (max 2), monitoring
- **OPEN** (failing): Skip agent, use fallback or escalate

**Trigger**: 3 consecutive failures → OPEN state
**Recovery**: After 60s cooldown → HALF-OPEN, attempt 1 retry
**Success criteria**: 2 consecutive successes → CLOSED state
```

## Error Response Protocol

```markdown
## 🔴 ERROR ENCOUNTERED

**Agent**: test-1
**Phase**: Unit test execution
**Error category**: Logical
**Error**:
```

Error in medci(): argument "alpha" is missing

```

**Diagnosis**: Missing default parameter
**Severity**: 🟡 Medium (blocks tests, not code)
**Recovery difficulty**: Low (auto-fixable)

### Recovery Options
1. **Auto-fix**: Add default `alpha = 0.05` [RECOMMENDED]
   - Confidence: High (90%)
   - ETA: < 30 seconds
   - Risk: Low (standard default value)

2. **Investigate**: Show function signature, check docs
   - Confidence: Medium (60%)
   - ETA: 2-3 minutes
   - Risk: None (read-only)

3. **Escalate**: Pause and report to user
   - Confidence: N/A
   - ETA: Depends on user response
   - Risk: None (manual intervention)

**Action taken**: Auto-fix applied (Option 1)
**Verification**: Re-running tests with default parameter...
**Result**: ✅ Tests passing (15/15)
```

## Escalation Paths

When auto-recovery fails or is inappropriate:

```markdown
## 🆘 ESCALATION REQUIRED

**Agent**: code-1
**Escalation level**: 2 (agent → orchestrator → user)
**Reason**: Logical error requires design decision

### Escalation Hierarchy
| Level | Handler | Response Time | Scope |
|-------|---------|---------------|-------|
| 0 | Agent self-recovery | < 5s | Auto-fix, retry |
| 1 | Orchestrator recovery | < 30s | Fallback agent, decompose |
| 2 | User decision | Variable | Design choice, manual fix |
| 3 | Abort | Immediate | Unrecoverable error |
```

## Recovery Strategies by Mode

| Mode | Auto-fix Threshold | Max Retries | Escalate On |
|------|-------------------|-------------|-------------|
| **debug** | Low (20%) | 5 | Any error (verbose) |
| **default** | Medium (60%) | 3 | Permanent errors |
| **optimize** | High (80%) | 2 | Critical only |
| **release** | Very High (95%) | 1 | All errors (thorough) |

**Auto-fix threshold**: Confidence level required to auto-fix without escalation

## Error Aggregation

When multiple agents fail:

```markdown
## 📊 ERROR SUMMARY (Multiple Failures)

**Wave**: Add authentication system
**Agents**: 4 spawned, 2 failed, 1 blocked, 1 success

### Failed Agents
| Agent | Error | Category | Retries | Resolution |
|-------|-------|----------|---------|------------|
| code-1 | Type error | Logical | 0/3 | ✅ Auto-fixed |
| test-1 | Import error | Configuration | 2/3 | 🔄 Retrying |
| doc-1 | - | - | - | ⏸️ Blocked (waiting for code-1) |
| arch-1 | - | - | - | ✅ Success |

### Root Cause Analysis
**Primary issue**: Type definition missing in codebase
**Cascade effect**: test-1 depends on code-1 fix
**Resolution**: code-1 fix unblocks test-1 and doc-1

### Recovery Plan
1. ✅ code-1: Auto-fixed type error (completed)
2. 🔄 test-1: Retry with fixed types (in progress)
3. ⏸️ doc-1: Resume after test-1 completes
4. ✅ arch-1: No action needed (success)

**ETA**: ~3 min (bounded by test-1 retry)
```

## Self-Healing Mechanisms

```markdown
## 🔧 SELF-HEALING ACTIVE

**Issue detected**: Repeated configuration errors in test-1
**Pattern recognized**: Missing environment variable (DATABASE_URL)
**Confidence**: 85%

### Auto-Healing Actions
1. ✅ Detected pattern (3 failures with same error)
2. ✅ Identified root cause (env var missing)
3. ✅ Applied fix (added to .env.example)
4. ✅ Updated agent instructions (include env setup)
5. 🔄 Retrying with fix applied...

**Learning**: Future agents will check .env setup proactively
**Persistence**: Pattern saved to .craft/cache/learned-patterns.json
```

## Execution Timeline View

When user says `timeline`, show visual execution timeline:

```markdown
## ⏱️ EXECUTION TIMELINE

```

TIME     0    1m    2m    3m    4m    5m    6m
─────────┼─────┼─────┼─────┼─────┼─────┼─────┤
arch-1   ██████░░░░░░░░░░░░░░░░░░░░░░░░░░░░░ ✅ 1.2m
code-1   ░░░░░░██████████████████░░░░░░░░░░░ 🟡 3.5m
code-2   ░░░░░░░░░░██████████░░░░░░░░░░░░░░░ ✅ 2.1m
test-1   ░░░░░░░░░░░░░░░░░░░░████████░░░░░░░ 🟡 1.8m
doc-1    ░░░░░░░░░░████░░░░░░░░░░░░░░░░░░░░░ ✅ 0.8m
─────────┼─────┼─────┼─────┼─────┼─────┼─────┤
                              NOW ▲

```

**Summary**:
- Completed: 3/5 agents
- In progress: 2 agents
- **ETA**: ~2 min remaining (bounded by test-1)

**Parallel efficiency**: 78% (vs sequential: would take 9.4m)
```

### Timeline Controls

| Command | Action |
|---------|--------|
| `timeline` | Show current timeline |
| `timeline live` | Auto-refresh every 30s |
| `timeline zoom 2m` | Focus on last 2 minutes |
