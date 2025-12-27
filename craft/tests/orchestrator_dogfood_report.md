# Orchestrator v2.1 Dogfooding Test Report

**Generated:** 2025-12-27 10:09:52
**Plugin:** Craft v1.4.0-dev
**Test Type:** Functional/Dogfooding
**Tests:** 18 total, 18 passed, 0 failed

## Summary

| Metric | Value |
|--------|-------|
| Total Tests | 18 |
| Passed | 18 (100%) |
| Failed | 0 (0%) |

## Results by Category

### Compression (2/2)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Compression Trigger Logic | ✓ PASS | All 6 trigger conditions correct | 0.0ms |
| Compression Ratio | ✓ PASS | All 3 compressions achieve ~60% reduction | 0.0ms |

### Estimation (2/2)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Token Estimation Heuristics | ✓ PASS | All 4 estimates within range | 0.0ms |
| Context Budget Calculation | ✓ PASS | Budget: 19200 tokens/agent (15% of 128K) | 0.0ms |

### Integration (3/3)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Agent Types Match Commands | ✓ PASS | All 6 command patterns mapped | 0.1ms |
| Craft Command Structure | ✓ PASS | All 4 sections present | 0.1ms |
| Agent-Skill Consistency | ✓ PASS | 6/6 agent types mapped | 0.1ms |

### Modes (2/2)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Mode Agent Limits | ✓ PASS | All 4 modes have valid limits | 0.0ms |
| Mode Verbosity Levels | ✓ PASS | All 3 verbosity levels documented | 0.3ms |

### Parsing (1/1)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Mode Regex Parsing | ✓ PASS | All 6 patterns parsed correctly | 0.1ms |

### Session (5/5)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Session State Schema | ✓ PASS | Schema valid with 4 required fields | 0.0ms |
| Session File Operations | ✓ PASS | Read/write/delete successful | 1.4ms |
| Session Persistence Skill | ✓ PASS | Skill valid with 4 sections | 0.1ms |
| Session State Lifecycle | ✓ PASS | All 7 transitions validated | 0.0ms |
| Session History Archiving | ✓ PASS | Archive create/verify successful | 1.2ms |

### Timeline (2/2)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Timeline ASCII Rendering | ✓ PASS | All 4 progress bars rendered | 0.0ms |
| Timeline Time Formatting | ✓ PASS | All 5 durations formatted | 0.0ms |

### Validation (1/1)

| Test | Status | Details | Time |
|------|--------|---------|------|
| Context Threshold Values | ✓ PASS | All 43 percentages valid (0-100) | 0.5ms |

