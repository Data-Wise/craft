# Claude Code 2.1.0 Integration - API Reference

**Version**: 1.0.0
**Last Updated**: 2026-01-17

## Overview

The Claude Code 2.1.0 integration provides intelligent task routing, hot-reload validation, and agent orchestration capabilities for the Craft plugin. This reference documents all public APIs, utilities, and integration points.

---

## Complexity Scoring API

### Module: `utils.complexity_scorer`

Provides task complexity analysis and routing recommendations.

#### `calculate_complexity_score(task: str) -> int`

Calculate complexity score for a task description.

**Parameters:**

- `task` (str): Natural language task description

**Returns:**

- `int`: Complexity score (0-10)

**Scoring Algorithm:**

- **0-3**: Simple single-operation tasks → Route to specific commands
- **4-7**: Multi-step tasks → Delegate to specialized agent
- **8-10**: Complex multi-category tasks → Delegate to orchestrator

**Scoring Factors** (each +2 points):

1. **Multi-step**: Task requires 3+ distinct operations
2. **Cross-category**: Spans multiple categories (code, test, docs, etc.)
3. **Planning**: Requires design/architecture phase
4. **Research**: Needs investigation/exploration
5. **Multi-file**: Affects 5+ files

**Example:**

```python
from utils.complexity_scorer import calculate_complexity_score

# Simple task
score = calculate_complexity_score("lint code")
# Returns: 1 (single operation)

# Multi-step task
score = calculate_complexity_score("lint, test, and build")
# Returns: 4 (multi-step +2, multiple verbs +2)

# Complex task
score = calculate_complexity_scoring(
    "design authentication system with OAuth2, tests, and docs"
)
# Returns: 8 (multi-step +2, cross-category +2, planning +2, comprehensive +2)
```

---

#### `get_routing_decision(score: int) -> str`

Map complexity score to routing decision.

**Parameters:**

- `score` (int): Complexity score (0-10)

**Returns:**

- `str`: One of "commands", "agent", or "orchestrator"

**Routing Logic:**

- **0-3** → `"commands"`: Execute via specific Craft commands
- **4-7** → `"agent"`: Delegate to single specialized agent
- **8-10** → `"orchestrator"`: Multi-agent coordination required

**Example:**

```python
from utils.complexity_scorer import get_routing_decision

routing = get_routing_decision(2)
# Returns: "commands"

routing = get_routing_decision(5)
# Returns: "agent"

routing = get_routing_decision(9)
# Returns: "orchestrator"
```

---

#### `explain_score(task: str) -> dict`

Generate detailed score explanation with factors.

**Parameters:**

- `task` (str): Task description

**Returns:**

- `dict`: Score breakdown with keys:
  - `task` (str): Original task
  - `score` (int): Complexity score
  - `routing` (str): Routing decision
  - `factors` (List[str]): List of detected factors
  - `explanation` (str): Human-readable explanation

**Example:**

```python
from utils.complexity_scorer import explain_score

result = explain_score("implement auth with OAuth2 and tests")

print(result)
# {
#     'task': 'implement auth with OAuth2 and tests',
#     'score': 6,
#     'routing': 'agent',
#     'factors': [
#         'Multi-step task (+2)',
#         'Cross-category task (code, security, test) (+2)',
#         'Requires planning (+2)'
#     ],
#     'explanation': 'Score 6/10 → Route to agent (Multi-step task (+2), ...'
# }
```

---

## Test Suite APIs

### Complexity Scoring Tests

**Location**: `tests/test_complexity_scoring.py`
**Tests**: 15 unit tests
**Coverage**: 100%

#### Test Categories

1. **Boundary Testing** (4 tests)
   - `test_boundary_score_3_routes_to_commands()`
   - `test_boundary_score_4_routes_to_agent()`
   - `test_boundary_score_7_routes_to_single_agent()`
   - `test_boundary_score_8_routes_to_orchestrator()`

2. **Factor Detection** (5 tests)
   - `test_multi_step_factor_detection()`
   - `test_cross_category_factor_detection()`
   - `test_planning_factor_detection()`
   - `test_research_factor_detection()`
   - `test_multi_file_factor_detection()`

3. **Score Range Testing** (3 tests)
   - `test_simple_task_low_score()` - Expects 0-2
   - `test_multistep_task_medium_score()` - Expects 4-6
   - `test_complex_architecture_high_score()` - Expects 8-10

4. **Edge Cases** (3 tests)
   - `test_empty_task()` - Empty string → score 0
   - `test_score_capped_at_10()` - Max score validation
   - `test_explain_score_output()` - Output format validation

**Running Tests:**

```bash
# Run all complexity scoring tests
python3 tests/test_complexity_scoring.py

# Expected output:
# ✓ 15/15 tests passing (0.5ms)
```

---

### Hot-Reload Validator Tests

**Location**: `tests/test_hot_reload_validators.py`
**Tests**: 9 unit tests
**Coverage**: 95%

#### Validator Files Tested

1. **test-coverage.md** - Test coverage validation
2. **broken-links.md** - Link validation integration
3. **lint-check.md** - Multi-language linting

#### Test Categories

1. **Structure Validation** (3 tests)
   - `test_validator_files_exist()`
   - `test_validator_frontmatter_valid()`
   - `test_validator_version_format()`

2. **Hot-Reload Configuration** (2 tests)
   - `test_validator_has_hot_reload_flag()`
   - `test_validator_uses_fork_context()`

3. **Mode-Aware Behavior** (1 test)
   - `test_coverage_validator_mode_aware()`
   - Validates 4 modes: debug (60%), default (70%), optimize (75%), release (90%)

4. **Multi-Language Support** (1 test)
   - `test_lint_validator_multi_language()`
   - Languages: Python, JavaScript, TypeScript, R, Go, Rust
   - Tools: ruff, eslint, lintr, golangci-lint, clippy

5. **Integration** (2 tests)
   - `test_broken_links_validator_integration()`
   - `test_validator_category_is_validation()`

**Running Tests:**

```bash
# Run all hot-reload validator tests
python3 tests/test_hot_reload_validators.py

# Expected output:
# ✓ 9/9 tests passing (7.0ms)
```

---

### Agent Hooks Tests

**Location**: `tests/test_agent_hooks.py`
**Tests**: 13 unit tests
**Coverage**: 100%

#### Hook Script

**Location**: `.claude-plugin/hooks/orchestrate-hooks.sh`

#### Test Categories

1. **Script Structure** (3 tests)
   - `test_hook_script_exists()` - File existence and permissions
   - `test_hook_syntax_valid()` - Bash syntax validation
   - `test_hook_has_shebang()` - Proper `#!/bin/bash` header

2. **Event Handlers** (3 tests)
   - `test_hook_handles_pretooluse_event()`
   - `test_hook_handles_posttooluse_event()`
   - `test_hook_handles_stop_event()`

3. **Mode-Aware Logic** (1 test)
   - `test_hook_mode_aware_limits()`
   - Modes: debug (1 agent), default (2), optimize (4), release (4)

4. **Infrastructure** (3 tests)
   - `test_hook_creates_directories()` - `.craft/logs`, `.craft/cache`
   - `test_hook_uses_logging()` - Timestamp logging
   - `test_hook_archives_old_logs()` - Log retention (last 10 sessions)

5. **Error Handling** (3 tests)
   - `test_hook_handles_errors_gracefully()` - `set -e` usage
   - `test_hook_uses_status_cache()` - Agent status tracking
   - `test_hook_saves_session_state()` - JSON session persistence

**Running Tests:**

```bash
# Run all agent hooks tests
python3 tests/test_agent_hooks.py

# Expected output:
# ✓ 13/13 tests passing (11.9ms)
```

---

## Integration Points

### Command Integration

#### `/craft:do` - Smart Task Routing

**Enhancement**: Complexity scoring integration

**Flow:**

```
User task → complexity_scorer.calculate_complexity_score()
         → get_routing_decision()
         → Route to: commands | agent | orchestrator
```

**Example Integration:**

```bash
# Simple task (score 2)
/craft:do lint code
# → Routes to /craft:code:lint

# Medium task (score 5)
/craft:do lint code and run tests
# → Delegates to code-quality agent

# Complex task (score 9)
/craft:do design auth system with OAuth2, tests, and docs
# → Delegates to orchestrator-v2
```

---

#### `/craft:check` - Validation Discovery

**Enhancement**: Hot-reload validator discovery

**Flow:**

```
User invokes /craft:check
→ Scan .claude-plugin/skills/validation/
→ Find skills with hot_reload: true
→ Execute validators in forked context
→ Return aggregated results
```

**Validators Discovered:**

- `test-coverage.md` - Mode-aware coverage thresholds
- `broken-links.md` - Internal link validation
- `lint-check.md` - Multi-language linting

**Example:**

```bash
/craft:check

# Output:
# ✓ Test coverage: 96% (meets 70% threshold for default mode)
# ✓ No broken links detected
# ✓ Lint check: All files pass
```

---

### Agent Integration

#### Orchestrator-v2 Enhancement

**Version**: 2.1.0 → 2.3.0

**New Capabilities:**

1. **Forked Context Execution** - Isolated validator runs
2. **Agent Resilience** - 9 recovery patterns
3. **Session Teleportation** - Cross-device resume

**Hook Events:**

- `PreToolUse`: Resource limit checking (mode-aware)
- `PostToolUse`: Status tracking, duration logging
- `Stop`: Session state persistence

---

## Configuration

### Environment Variables

| Variable | Description | Default | Required |
|----------|-------------|---------|----------|
| `CRAFT_MODE` | Execution mode | `default` | No |
| `MAX_AGENTS` | Max concurrent agents | Mode-dependent | No |

### Mode Configuration

| Mode | Max Agents | Coverage Threshold | Use Case |
|------|------------|-------------------|----------|
| `debug` | 1 | 60% | Development, verbose logging |
| `default` | 2 | 70% | Standard operation |
| `optimize` | 4 | 75% | Performance optimization |
| `release` | 4 | 90% | Production deployment |

---

## Error Handling

### Complexity Scorer

**Empty Task:**

```python
score = calculate_complexity_score("")
# Returns: 0 (routes to commands)
```

**Invalid Input:**

```python
score = calculate_complexity_score(None)
# Raises: TypeError
```

### Validators

**Missing Frontmatter:**

- Validator skipped with warning
- Does not fail entire check

**Invalid YAML:**

- Parser error logged
- Validator marked as invalid

---

## Performance Metrics

### Test Execution Times

| Test Suite | Tests | Duration | Avg/Test |
|------------|-------|----------|----------|
| Complexity Scoring | 15 | 0.5ms | 0.03ms |
| Hot-Reload Validators | 9 | 7.0ms | 0.78ms |
| Agent Hooks | 13 | 11.9ms | 0.92ms |
| **Total** | **37** | **19.4ms** | **0.52ms** |

### Coverage Metrics

| Component | Lines | Tested | Coverage |
|-----------|-------|--------|----------|
| Complexity Scorer | 210 | 210 | 100% |
| Hot-Reload Validators | 950 | 902 | 95% |
| Agent Hooks Script | 169 | 169 | 100% |
| **Total** | **1,329** | **1,281** | **96%** |

---

## Migration Guide

### From Manual Routing to Complexity Scoring

**Before:**

```bash
# Manual decision required
/craft:code:lint  # User decides which command
```

**After:**

```bash
# Automatic routing based on complexity
/craft:do lint code  # Routes to /craft:code:lint
/craft:do lint and test  # Routes to agent
```

### From Static Validators to Hot-Reload

**Before:**

```bash
# Validators hardcoded in /craft:check
# Required plugin restart for changes
```

**After:**

```bash
# Validators auto-discovered from .claude-plugin/skills/validation/
# Changes take effect immediately (hot-reload)
```

---

## Troubleshooting

### Tests Failing

**Issue**: `python3 tests/test_complexity_scoring.py` fails

**Solution:**

```bash
# Verify utility exists
ls -la utils/complexity_scorer.py

# Check Python syntax
python3 -m py_compile utils/complexity_scorer.py

# Run with verbose output
python3 -v tests/test_complexity_scoring.py
```

### Validators Not Discovered

**Issue**: `/craft:check` doesn't find new validators

**Solution:**

```bash
# Verify frontmatter
head -20 .claude-plugin/skills/validation/my-validator.md

# Check for hot_reload: true flag
grep "hot_reload" .claude-plugin/skills/validation/my-validator.md

# Verify context: fork setting
grep "context: fork" .claude-plugin/skills/validation/my-validator.md
```

### Hook Script Not Executing

**Issue**: Orchestrator hooks not running

**Solution:**

```bash
# Verify script exists
ls -la .claude-plugin/hooks/orchestrate-hooks.sh

# Check executable permissions
chmod +x .claude-plugin/hooks/orchestrate-hooks.sh

# Validate bash syntax
bash -n .claude-plugin/hooks/orchestrate-hooks.sh
```

---

## Related Documentation

- [Testing Guide](./TESTING-CLAUDE-CODE-2.1.md) - Comprehensive test suite documentation
- [.STATUS](../.STATUS) - Implementation status and Wave 1-4 details
- [CLAUDE.md](https://github.com/Data-Wise/craft/blob/main/CLAUDE.md) - Project overview and quick reference

---

**Last Updated**: 2026-01-17
**Integration Version**: Claude Code 2.1.0
**Test Coverage**: 96% (37/37 tests passing)
