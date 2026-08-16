<!-- markdownlint-disable MD046 -->
# Integration Testing Guide

⏱️ **15 minutes** • 🟢 Beginner • ✓ Complete guide

> **TL;DR** (30 seconds)
>
> - **What:** Craft includes 28 integration tests across 3 categories (dependency system, orchestrator workflows, branch guard)
> - **Why:** Ensure new features work end-to-end with all dependencies
> - **How:** Run `python3 tests/test_integration_*.py` to test each category
> - **Next:** Read about [Dependency Management](dependency-management-advanced.md) or [Claude Code 2.1.0 Integration](claude-code-2.1-guide.md)

Craft has comprehensive integration tests that validate the entire system end-to-end. This guide explains what they test and how to run them.

## Quick Start

!!! abstract "Run All Integration Tests"
    ```bash
    # Run all integration tests
    python3 tests/test_integration_*.py

    # Run specific category
    python3 tests/test_integration_dependency_system.py
    python3 tests/test_integration_orchestrator_workflows.py
    python3 tests/test_integration_branch_guard.py
    ```

## Test Categories

### Category 1: Dependency Management System (9 tests)

**File:** `tests/test_integration_dependency_system.py`

**Purpose:** Validates the complete dependency detection and installation workflow.

**What It Tests:**

- ✅ Full dependency check workflow (`/folio:docs:demo --check`)
- ✅ Health check validation of installed tools
- ✅ Tool detection across multiple methods (PATH, homebrew, npm, cargo)
- ✅ Version comparison logic for upgrade decisions
- ✅ Installer fallback chains (homebrew → cargo → binary)
- ✅ Session caching system for performance
- ✅ Dependency conflict detection
- ✅ Batch installation across multiple tools
- ✅ Repair workflow for broken dependencies

**Components Tested:**

- `commands/docs/demo.md` - Dependency declarations in demo command
- `scripts/dependency-manager.sh` - Main orchestration script
- `scripts/tool-detector.sh` - Multi-method tool detection
- `scripts/health-check.sh` - Installation validation
- `scripts/installers/` - Platform-specific installers (brew, cargo, binary, consent)

**Run It:**

```bash
python3 tests/test_integration_dependency_system.py
```

**Expected Output:**

```
test_01_full_check_workflow ... ok
test_02_health_check_integration ... ok
test_03_tool_detector_all_methods ... ok
test_04_version_check_comparison ... ok
test_05_installer_fallback_chain ... ok
test_06_session_cache_workflow ... ok
test_07_conflict_detection ... ok
test_08_batch_installation ... ok
test_09_repair_workflow ... ok

Ran 9 tests in ~2-5 seconds
```

### Category 2: Orchestrator Workflows (13 tests)

**File:** `tests/test_integration_orchestrator_workflows.py`

**Purpose:** Validates the smart task routing system with complexity scoring and agent delegation.

**What It Tests:**

- ✅ Simple tasks (score 0-3) route to direct commands
- ✅ Moderate tasks (score 4-7) route to single agents
- ✅ Complex tasks (score 8-10) route to orchestrator with multi-agent coordination
- ✅ Complexity scoring algorithm with 7 factors
- ✅ Hot-reload validators (test-coverage, broken-links, lint-check)
- ✅ Validator ecosystem integration
- ✅ Orchestration hooks (PreToolUse, PostToolUse, Stop)
- ✅ Agent resilience with 9 recovery strategies
- ✅ Session state schema (JSON v1.0.0)
- ✅ Session teleportation (cross-device resume)
- ✅ Task decomposition for complex work
- ✅ Parallel agent execution
- ✅ Agent coordination and result aggregation

**Components Tested:**

- `utils/complexity_scorer.py` - Task complexity calculation (0-10 scale)
- `commands/do.md` - Universal task routing
- `commands/orchestrate.md` - Multi-agent coordination
- `.claude-plugin/skills/validation/` - Validator ecosystem
- `.claude-plugin/hooks/orchestrate-hooks.sh` - Orchestration lifecycle
- `agents/orchestrator-v2.md` - v2.3.0 agent with improved coordination

**Run It:**

```bash
python3 tests/test_integration_orchestrator_workflows.py
```

**Expected Output:**

```
test_01_simple_task_routes_to_command ... ok
test_02_moderate_task_routes_to_agent ... ok
test_03_complex_task_routes_to_orchestrator ... ok
test_04_complexity_scoring_factors ... ok
test_05_hot_reload_validators ... ok
test_06_validator_ecosystem ... ok
test_07_orchestration_hooks_lifecycle ... ok
test_08_agent_resilience ... ok
test_09_session_state_schema ... ok
test_10_session_teleportation ... ok
test_11_task_decomposition ... ok
test_12_parallel_execution ... ok
test_13_agent_coordination ... ok

Ran 13 tests in ~3-8 seconds
```

### Category 3: Branch Guard (6 tests)

**File:** `tests/test_integration_branch_guard.py`

**Purpose:** Validates the branch protection hook system including config loading, protection levels, and jq-based JSON parsing.

**What It Tests:**

- ✅ Config file loading and validation (`.claude/branch-guard.json`)
- ✅ Auto-detection fallback when no config exists
- ✅ Protection level assignment (block-all vs block-new-code)
- ✅ File extension classification (code vs docs)
- ✅ Bypass marker detection (`.claude/allow-dev-edit`)
- ✅ JSON parsing with jq (primary), Python (fallback), grep/sed (last resort)

**Components Tested:**

- `scripts/branch-guard.sh` - PreToolUse hook with `_json_get` function
- `.claude/branch-guard.json` - Per-project config
- `skills/dev/git/SKILL.md` - Protect/unprotect operations (folded from
  `commands/git/protect.md`/`unprotect.md`, 2026-07 v4 consolidation)

**Run It:**

```bash
python3 tests/test_integration_branch_guard.py
```

**Also: Bash test suites** (49 unit + 31 e2e) **and dogfooding** (52 tests):

```bash
bash tests/test_branch_guard.sh            # Unit tests
bash tests/test_branch_guard_e2e.sh        # End-to-end tests
python3 tests/test_branch_guard_dogfood.py # Dogfooding tests (real repo)
```

## Running Integration Tests

### Run Everything

```bash
# Run all tests (all categories)
cd /path/to/craft
python3 -m pytest tests/test_integration_*.py -v

# Or individual runner
for test in tests/test_integration_*.py; do
  python3 "$test"
done
```

### Run Specific Category

```bash
# Dependency system tests only
python3 tests/test_integration_dependency_system.py

# Orchestrator tests only
python3 tests/test_integration_orchestrator_workflows.py

# Branch guard tests only
python3 tests/test_integration_branch_guard.py
```

### With Verbose Output

```bash
python3 tests/test_integration_dependency_system.py -v
```

## Understanding Test Structure

Each test file follows a standard pattern:

```python
#!/usr/bin/env python3
"""
Integration Tests: [Category Name]
==================================
Tests the full [system] end-to-end...

Components tested:
- File 1
- File 2
- File 3

Run with: python tests/test_integration_[category].py
"""

class Test[Category]Integration(unittest.TestCase):
    """Integration tests for [category]."""

    @classmethod
    def setUpClass(cls):
        # Set up test environment once

    def test_01_feature_name(self):
        # Arrange: Set up test data
        # Act: Run the feature
        # Assert: Verify results
```

## What Each Category Validates

### Dependency System Tests Validate

The dependency management system is critical for the `/folio:docs:demo` command. Tests verify:

1. **Detection** - Finding installed tools using 4 methods (PATH, homebrew, npm, cargo)
2. **Health** - Validating tool functionality
3. **Versioning** - Comparing versions correctly for upgrade decisions
4. **Installation** - Using correct installers for each platform
5. **Fallbacks** - Trying alternative installers if primary fails
6. **Caching** - Performance optimization with session cache
7. **Conflicts** - Detecting version incompatibilities
8. **Batch Work** - Installing multiple tools efficiently
9. **Repair** - Fixing broken dependencies

### Orchestrator Tests Validate

The orchestration system enables smart task routing and agent delegation. Tests verify:

1. **Routing** - Directing tasks to correct handler (command/agent/orchestrator)
2. **Scoring** - Calculating complexity from 7 factors
3. **Validation** - Hot-reload validators work correctly
4. **Hooks** - Orchestration lifecycle hooks trigger properly
5. **Resilience** - Agents recover from 9 types of failures
6. **State** - Session persistence works correctly
7. **Teleportation** - Sessions can resume on different devices
8. **Decomposition** - Complex tasks break into subtasks
9. **Parallelism** - Multiple agents run simultaneously
10. **Coordination** - Agents synchronize and aggregate results

## Troubleshooting Integration Tests

| Issue | Solution |
|-------|----------|
| Tests fail with "module not found" | `python3 -m pip install -e .` in craft root |
| Permission denied on scripts | `chmod +x scripts/*.sh` |
| Tests timeout | Some dependency tests may take 5-10 seconds if tools need checking |
| Dependency detection fails | Make sure tools being detected are in PATH or installed via homebrew/cargo |

## Key Files Reference

| Component | File | Purpose |
|-----------|------|---------|
| **Dependency System** | | |
| Main orchestrator | `scripts/dependency-manager.sh` | Coordinates detection, check, fix, batch |
| Tool detection | `scripts/tool-detector.sh` | Finds tools using 4 methods |
| Health validation | `scripts/health-check.sh` | Verifies tool functionality |
| Version checking | `scripts/version-check.sh` | Compares versions for upgrades |
| Brew installer | `scripts/installers/installer-brew.sh` | Homebrew installation |
| Cargo installer | `scripts/installers/installer-cargo.sh` | Rust package installation |
| Binary installer | `scripts/installers/installer-binary.sh` | Direct binary download |
| Consent installer | `scripts/installers/installer-consent.sh` | Interactive approval |
| Session cache | `scripts/session-cache.sh` | Performance caching |
| **Orchestrator** | | |
| Complexity scorer | `utils/complexity_scorer.py` | Calculates task complexity (0-10) |
| Task routing | `commands/do.md` | Routes tasks to correct handler |
| Orchestration | `commands/orchestrate.md` | Multi-agent coordination |
| Validators | `.claude-plugin/skills/validation/` | Hot-reload validators |
| Hooks | `.claude-plugin/hooks/orchestrate-hooks.sh` | Lifecycle hooks |
| Orchestrator v2 | `agents/orchestrator-v2.md` | v2.3.0 agent |
| **Branch Guard** | | |
| Hook script | `scripts/branch-guard.sh` | PreToolUse hook with jq parsing |
| Config | `.claude/branch-guard.json` | Per-project branch protection config |
| Protect/unprotect | `skills/dev/git/SKILL.md` | Re-enable protection / bypass (folded from commands/git/, 2026-07 v4) |
| Unit tests | `tests/test_branch_guard.sh` | 49 bash unit tests |
| E2E tests | `tests/test_branch_guard_e2e.sh` | 31 end-to-end tests |
| Dogfooding tests | `tests/test_branch_guard_dogfood.py` | 52 dogfooding tests (real repo) |

## Next Steps

1. **Run the tests** - `python3 tests/test_integration_dependency_system.py`
2. **Explore components** - Read files in the "Key Files Reference" table
3. **Learn related features:**
   - [Dependency Management Advanced Guide](dependency-management-advanced.md) - Detailed workflow
   - [Claude Code 2.1.0 Integration Guide](claude-code-2.1-guide.md) - Complexity scoring details

## Summary

Craft's 28 integration tests validate three critical systems:

- **Dependency System (9 tests)** - Tool detection, installation, and repair
- **Orchestrator (13 tests)** - Smart routing, complexity scoring, agent delegation
- **Branch Guard (6 tests)** - Branch protection hooks, config loading, JSON parsing

Run them regularly to ensure features continue working end-to-end. All tests pass with 100% success rate.
