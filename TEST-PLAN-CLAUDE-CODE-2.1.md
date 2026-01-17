# Test Plan: Claude Code 2.1.0 Integration

**Date**: 2026-01-17
**Features**: Wave 1-3 implementation (Complexity scoring, Hot-reload validators, Agent hooks, Agent delegation, Forked context, Agent resilience, Validator ecosystem, Session teleportation)
**Test Types**: Unit, E2E, Dogfooding

---

## Overview

This test plan covers comprehensive testing for the Claude Code 2.1.0 integration features implemented across three waves.

### Test Pyramid

```
        Dogfooding (3 tests)
              /\
             /  \
            /E2E \  (12 tests)
           /      \
          /  Unit  \ (25 tests)
         /          \
        /____________\
```

**Total Tests**: 40 tests across 3 categories

---

## Unit Tests (25 tests)

### 1. Complexity Scoring (7 tests)

**File**: `tests/test_complexity_scoring.py` (new)

#### Test Cases

| Test | Input | Expected Score | Reason |
|------|-------|----------------|--------|
| `test_simple_task_low_score` | "lint code" | 1-2 | Single operation, no planning |
| `test_multistep_task_medium_score` | "lint, test, build" | 4-6 | Multi-step (+2), multi-category (+2) |
| `test_complex_architecture_high_score` | "design auth system with OAuth2, PKCE, and session management" | 8-10 | Multi-step (+2), planning (+2), research (+2), multi-file (+2) |
| `test_boundary_score_3_routes_to_commands` | "format code and commit" | 3 | Just below agent threshold |
| `test_boundary_score_4_routes_to_agent` | "format code, test, and fix errors" | 4 | At agent threshold |
| `test_boundary_score_7_routes_to_single_agent` | "refactor auth module with tests" | 7 | Just below orchestrator threshold |
| `test_boundary_score_8_routes_to_orchestrator` | "add feature with tests, docs, CI" | 8 | At orchestrator threshold |

#### Implementation

```python
#!/usr/bin/env python3
"""
Test complexity scoring algorithm for /craft:do routing.
"""

import pytest
from pathlib import Path
import sys

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.complexity_scorer import calculate_complexity_score

class TestComplexityScoring:
    """Tests for complexity scoring algorithm."""

    def test_simple_task_low_score(self):
        """Simple single-operation tasks should score 1-2."""
        task = "lint code"
        score = calculate_complexity_score(task)
        assert 1 <= score <= 2, f"Expected 1-2, got {score}"

    def test_multistep_task_medium_score(self):
        """Multi-step tasks should score 4-6."""
        task = "lint code, run tests, and build project"
        score = calculate_complexity_score(task)
        assert 4 <= score <= 6, f"Expected 4-6, got {score}"

    def test_complex_architecture_high_score(self):
        """Complex architectural tasks should score 8-10."""
        task = "design authentication system with OAuth2, PKCE flow, session management, and refresh token rotation"
        score = calculate_complexity_score(task)
        assert 8 <= score <= 10, f"Expected 8-10, got {score}"

    def test_boundary_score_3_routes_to_commands(self):
        """Score of 3 should route to commands."""
        task = "format code and commit changes"
        score = calculate_complexity_score(task)
        assert score == 3, f"Expected 3, got {score}"

        routing = get_routing_decision(score)
        assert routing == "commands", f"Expected 'commands', got '{routing}'"

    def test_boundary_score_4_routes_to_agent(self):
        """Score of 4 should route to single agent."""
        task = "format code, run tests, and fix any errors"
        score = calculate_complexity_score(task)
        assert score == 4, f"Expected 4, got {score}"

        routing = get_routing_decision(score)
        assert routing == "agent", f"Expected 'agent', got '{routing}'"

    def test_boundary_score_7_routes_to_single_agent(self):
        """Score of 7 should still route to single agent."""
        task = "refactor authentication module and add comprehensive tests"
        score = calculate_complexity_score(task)
        assert score == 7, f"Expected 7, got {score}"

        routing = get_routing_decision(score)
        assert routing == "agent", f"Expected 'agent', got '{routing}'"

    def test_boundary_score_8_routes_to_orchestrator(self):
        """Score of 8 should route to orchestrator."""
        task = "add new feature with unit tests, integration tests, documentation, and CI pipeline"
        score = calculate_complexity_score(task)
        assert score == 8, f"Expected 8, got {score}"

        routing = get_routing_decision(score)
        assert routing == "orchestrator", f"Expected 'orchestrator', got '{routing}'"


def get_routing_decision(score: int) -> str:
    """Map score to routing decision."""
    if score <= 3:
        return "commands"
    elif score <= 7:
        return "agent"
    else:
        return "orchestrator"
```

---

### 2. Hot-Reload Validators (6 tests)

**File**: `tests/test_hot_reload_validators.py` (new)

#### Test Cases

| Test | Validator | Check |
|------|-----------|-------|
| `test_validator_frontmatter_valid` | All 3 | Valid YAML frontmatter |
| `test_validator_has_hot_reload_flag` | All 3 | `hot_reload: true` present |
| `test_validator_uses_fork_context` | All 3 | `context: fork` present |
| `test_coverage_validator_mode_aware` | test-coverage | Different thresholds per mode |
| `test_lint_validator_multi_language` | lint-check | Supports 6 languages |
| `test_broken_links_validator_integration` | broken-links | Uses existing test |

#### Implementation

```python
#!/usr/bin/env python3
"""
Test hot-reload validators in .claude-plugin/skills/validation/.
"""

import pytest
import yaml
from pathlib import Path

VALIDATORS = [
    "test-coverage.md",
    "broken-links.md",
    "lint-check.md"
]

class TestHotReloadValidators:
    """Tests for hot-reload validator infrastructure."""

    @pytest.fixture
    def plugin_dir(self):
        """Get plugin directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def validators_dir(self, plugin_dir):
        """Get validators directory."""
        return plugin_dir / ".claude-plugin" / "skills" / "validation"

    def test_validator_frontmatter_valid(self, validators_dir):
        """All validators should have valid YAML frontmatter."""
        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            assert path.exists(), f"Validator not found: {validator_file}"

            content = path.read_text()

            # Extract frontmatter
            parts = content.split("---")
            assert len(parts) >= 3, f"Invalid frontmatter in {validator_file}"

            frontmatter = parts[1]

            # Parse YAML
            try:
                data = yaml.safe_load(frontmatter)
            except yaml.YAMLError as e:
                pytest.fail(f"Invalid YAML in {validator_file}: {e}")

            # Check required fields
            required_fields = ["name", "description", "category", "version"]
            for field in required_fields:
                assert field in data, f"Missing '{field}' in {validator_file}"

    def test_validator_has_hot_reload_flag(self, validators_dir):
        """All validators should have hot_reload: true."""
        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            content = path.read_text()

            # Extract frontmatter
            parts = content.split("---")
            frontmatter = parts[1]
            data = yaml.safe_load(frontmatter)

            assert "hot_reload" in data, f"Missing hot_reload in {validator_file}"
            assert data["hot_reload"] is True, f"hot_reload must be true in {validator_file}"

    def test_validator_uses_fork_context(self, validators_dir):
        """All validators should use context: fork."""
        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            content = path.read_text()

            # Extract frontmatter
            parts = content.split("---")
            frontmatter = parts[1]
            data = yaml.safe_load(frontmatter)

            assert "context" in data, f"Missing context in {validator_file}"
            assert data["context"] == "fork", f"context must be 'fork' in {validator_file}"

    def test_coverage_validator_mode_aware(self, validators_dir):
        """Coverage validator should have mode-specific thresholds."""
        path = validators_dir / "test-coverage.md"
        content = path.read_text()

        # Check for mode-aware thresholds
        modes = ["debug", "default", "optimize", "release"]
        thresholds = {
            "debug": "60",
            "default": "70",
            "optimize": "75",
            "release": "90"
        }

        for mode in modes:
            assert mode in content, f"Missing mode '{mode}' in coverage validator"
            threshold = thresholds[mode]
            assert threshold in content, f"Missing threshold '{threshold}%' for {mode} mode"

    def test_lint_validator_multi_language(self, validators_dir):
        """Lint validator should support multiple languages."""
        path = validators_dir / "lint-check.md"
        content = path.read_text()

        languages = ["Python", "JavaScript", "TypeScript", "R", "Go", "Rust"]
        tools = ["ruff", "eslint", "lintr", "golangci-lint", "clippy"]

        for lang in languages:
            assert lang in content, f"Missing language support: {lang}"

        for tool in tools:
            assert tool in content, f"Missing tool reference: {tool}"

    def test_broken_links_validator_integration(self, validators_dir):
        """Broken links validator should reference existing test."""
        path = validators_dir / "broken-links.md"
        content = path.read_text()

        # Should reference the existing test
        assert "test_craft_plugin.py" in content, "Should reference existing test suite"
        assert "test_no_broken_links" in content, "Should reference specific test function"
```

---

### 3. Agent Hooks (5 tests)

**File**: `tests/test_agent_hooks.py` (new)

#### Test Cases

| Test | Hook Event | Check |
|------|------------|-------|
| `test_hook_script_exists` | - | Script exists and is executable |
| `test_hook_handles_pretooluse` | PreToolUse | Resource limit check works |
| `test_hook_handles_posttooluse` | PostToolUse | Logging works |
| `test_hook_handles_stop` | Stop | Cleanup works |
| `test_hook_mode_aware_limits` | PreToolUse | Different limits per mode |

#### Implementation

```python
#!/usr/bin/env python3
"""
Test agent hooks in .claude-plugin/hooks/.
"""

import pytest
import os
import subprocess
from pathlib import Path

class TestAgentHooks:
    """Tests for orchestration agent hooks."""

    @pytest.fixture
    def plugin_dir(self):
        """Get plugin directory."""
        return Path(__file__).parent.parent

    @pytest.fixture
    def hooks_dir(self, plugin_dir):
        """Get hooks directory."""
        return plugin_dir / ".claude-plugin" / "hooks"

    def test_hook_script_exists(self, hooks_dir):
        """Hook script should exist and be executable."""
        hook_script = hooks_dir / "orchestrate-hooks.sh"

        assert hook_script.exists(), "Hook script not found"
        assert os.access(hook_script, os.X_OK), "Hook script not executable"

    def test_hook_handles_pretooluse(self, hooks_dir):
        """Hook should handle PreToolUse event."""
        hook_script = hooks_dir / "orchestrate-hooks.sh"

        env = os.environ.copy()
        env["HOOK_EVENT"] = "PreToolUse"
        env["CRAFT_MODE"] = "default"

        result = subprocess.run(
            [str(hook_script)],
            env=env,
            capture_output=True,
            text=True
        )

        # Should exit 0 (allow)
        assert result.returncode == 0, f"PreToolUse check failed: {result.stderr}"

        # Should check resource limits
        assert "agents" in result.stdout.lower() or "resource" in result.stdout.lower()

    def test_hook_handles_posttooluse(self, hooks_dir):
        """Hook should handle PostToolUse event."""
        hook_script = hooks_dir / "orchestrate-hooks.sh"

        env = os.environ.copy()
        env["HOOK_EVENT"] = "PostToolUse"
        env["CRAFT_MODE"] = "default"

        result = subprocess.run(
            [str(hook_script)],
            env=env,
            capture_output=True,
            text=True
        )

        # Should exit 0 (success)
        assert result.returncode == 0, f"PostToolUse failed: {result.stderr}"

    def test_hook_handles_stop(self, hooks_dir):
        """Hook should handle Stop event."""
        hook_script = hooks_dir / "orchestrate-hooks.sh"

        env = os.environ.copy()
        env["HOOK_EVENT"] = "Stop"
        env["CRAFT_MODE"] = "default"

        result = subprocess.run(
            [str(hook_script)],
            env=env,
            capture_output=True,
            text=True
        )

        # Should exit 0 (success)
        assert result.returncode == 0, f"Stop failed: {result.stderr}"

    def test_hook_mode_aware_limits(self, hooks_dir):
        """Hook should enforce different limits per mode."""
        hook_script = hooks_dir / "orchestrate-hooks.sh"

        # Test debug mode (max 1 agent)
        env = os.environ.copy()
        env["HOOK_EVENT"] = "PreToolUse"
        env["CRAFT_MODE"] = "debug"

        result = subprocess.run(
            [str(hook_script)],
            env=env,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Debug mode check failed"

        # Test optimize mode (max 4 agents)
        env["CRAFT_MODE"] = "optimize"

        result = subprocess.run(
            [str(hook_script)],
            env=env,
            capture_output=True,
            text=True
        )

        assert result.returncode == 0, "Optimize mode check failed"
```

---

### 4. Agent Delegation (4 tests)

**File**: `tests/test_agent_delegation.py` (new)

#### Test Cases

| Test | Task Type | Expected Agent |
|------|-----------|----------------|
| `test_keyword_routing_to_feature_dev` | "implement login" | feature-dev |
| `test_keyword_routing_to_backend_architect` | "design API" | backend-architect |
| `test_keyword_routing_to_bug_detective` | "debug error" | bug-detective |
| `test_fallback_to_orchestrator` | "complex multi-step task" | orchestrator-v2 |

---

### 5. Session State Schema (3 tests)

**File**: `tests/test_session_state_schema.py` (new)

#### Test Cases

| Test | Check |
|------|-------|
| `test_session_schema_json_valid` | JSON schema validates correctly |
| `test_session_required_fields` | All required fields present |
| `test_session_agent_tracking` | Agent state tracking complete |

---

## E2E Tests (12 tests)

### 6. Complexity Scoring Integration (3 tests)

**File**: `tests/e2e/test_do_command_routing.py` (new)

#### Test Cases

| Test | Command | Expected Outcome |
|------|---------|------------------|
| `test_do_routes_simple_to_commands` | `/craft:do "lint code"` | Executes `/craft:code:lint` |
| `test_do_routes_medium_to_agent` | `/craft:do "refactor auth module"` | Delegates to agent |
| `test_do_routes_complex_to_orchestrator` | `/craft:do "add feature with tests and docs"` | Delegates to orchestrator |

---

### 7. Validator Discovery (3 tests)

**File**: `tests/e2e/test_check_validator_discovery.py` (new)

#### Test Cases

| Test | Check |
|------|-------|
| `test_check_discovers_validators` | `/craft:check` finds all 3 validators |
| `test_check_runs_validators_in_fork` | Validators execute in forked context |
| `test_check_mode_aware_execution` | `CRAFT_MODE=release` runs stricter checks |

---

### 8. Orchestrator Resilience (3 tests)

**File**: `tests/e2e/test_orchestrator_resilience.py` (new)

#### Test Cases

| Test | Scenario | Expected Outcome |
|------|----------|------------------|
| `test_transient_error_retry` | Network timeout | Retries with backoff |
| `test_circuit_breaker_opens` | 3 consecutive failures | Opens circuit, uses fallback |
| `test_escalation_to_user` | Permanent error | Escalates with clear context |

---

### 9. Session Teleportation (3 tests)

**File**: `tests/e2e/test_session_teleportation.py` (new)

#### Test Cases

| Test | Scenario | Expected Outcome |
|------|----------|------------------|
| `test_session_save_and_load` | Start session, save, resume | State preserved |
| `test_cross_device_resume` | Save on device A, resume on B | Sync works |
| `test_conflict_resolution` | Concurrent edits | Prompts user for decision |

---

## Dogfooding Tests (3 tests)

### 10. Real-World Workflow Tests

**File**: `tests/dogfood/test_real_workflows.py` (new)

#### Test Cases

| Test | Workflow | Success Criteria |
|------|----------|------------------|
| `test_add_feature_end_to_end` | Use `/craft:do` to add a small feature | Complexity scored correctly, routed to agent, feature implemented |
| `test_pre_commit_validation` | Use `/craft:check` before committing | All validators run, pass/fail reported correctly |
| `test_orchestrate_complex_task` | Use `/craft:orchestrate` for multi-step task | Agents spawn, resilience works, session persists |

#### Implementation

```python
#!/usr/bin/env python3
"""
Dogfooding tests - Real-world workflow validation.
"""

import pytest
import subprocess
import tempfile
from pathlib import Path

class TestRealWorldWorkflows:
    """Tests using actual craft commands in real scenarios."""

    @pytest.fixture
    def temp_project(self):
        """Create temporary project for testing."""
        with tempfile.TemporaryDirectory() as tmpdir:
            project = Path(tmpdir)

            # Create minimal project structure
            (project / "src").mkdir()
            (project / "src" / "main.py").write_text("print('hello')")
            (project / "tests").mkdir()

            yield project

    def test_add_feature_end_to_end(self, temp_project):
        """
        Test complete feature addition workflow:
        1. Use /craft:do with medium complexity task
        2. Verify routing decision
        3. Verify implementation
        """
        # This test would require Claude Code CLI integration
        # Placeholder for actual implementation
        pass

    def test_pre_commit_validation(self, temp_project):
        """
        Test pre-commit validation workflow:
        1. Make changes to code
        2. Run /craft:check
        3. Verify all validators execute
        4. Verify pass/fail reporting
        """
        # This test would require Claude Code CLI integration
        # Placeholder for actual implementation
        pass

    def test_orchestrate_complex_task(self, temp_project):
        """
        Test orchestration workflow:
        1. Start complex multi-step task
        2. Verify agents spawn correctly
        3. Verify resilience patterns work
        4. Verify session state persists
        """
        # This test would require Claude Code CLI integration
        # Placeholder for actual implementation
        pass
```

---

## Test Execution

### Running Tests

```bash
# Run all unit tests
python3 -m pytest tests/test_complexity_scoring.py -v
python3 -m pytest tests/test_hot_reload_validators.py -v
python3 -m pytest tests/test_agent_hooks.py -v

# Run all E2E tests
python3 -m pytest tests/e2e/ -v

# Run dogfooding tests (requires Claude Code CLI)
python3 -m pytest tests/dogfood/ -v

# Run all tests
python3 -m pytest tests/ -v

# Run with coverage
python3 -m pytest tests/ --cov=. --cov-report=term
```

### Expected Coverage

| Component | Target Coverage |
|-----------|----------------|
| Complexity scoring | 100% |
| Hot-reload validators | 95% |
| Agent hooks | 90% |
| Session state | 95% |
| Integration | 80% |

---

## Test Implementation Checklist

- [ ] Create `tests/test_complexity_scoring.py` (7 tests)
- [ ] Create `tests/test_hot_reload_validators.py` (6 tests)
- [ ] Create `tests/test_agent_hooks.py` (5 tests)
- [ ] Create `tests/test_agent_delegation.py` (4 tests)
- [ ] Create `tests/test_session_state_schema.py` (3 tests)
- [ ] Create `tests/e2e/test_do_command_routing.py` (3 tests)
- [ ] Create `tests/e2e/test_check_validator_discovery.py` (3 tests)
- [ ] Create `tests/e2e/test_orchestrator_resilience.py` (3 tests)
- [ ] Create `tests/e2e/test_session_teleportation.py` (3 tests)
- [ ] Create `tests/dogfood/test_real_workflows.py` (3 tests)
- [ ] Create `utils/complexity_scorer.py` (scoring logic)
- [ ] Add pytest to dependencies
- [ ] Add pytest-cov to dependencies
- [ ] Update `.gitignore` for pytest cache
- [ ] Document test execution in README

---

## Notes

### Critical Testing Requirements

1. **Unit tests** must not require Claude Code CLI - test logic in isolation
2. **E2E tests** may mock CLI interactions but test integration points
3. **Dogfooding tests** require actual Claude Code CLI and are optional

### Test Data

All test data should be:
- Minimal and focused
- Self-contained (no external dependencies)
- Deterministic (no flaky tests)
- Fast to execute (< 1s per unit test)

### Continuous Integration

Tests should run on:
- Every commit (unit tests only)
- Every PR (unit + E2E tests)
- Release builds (all tests including dogfooding)

---

## Success Metrics

| Metric | Target | Current |
|--------|--------|---------|
| Total tests | 40 | 0 (to be implemented) |
| Unit test coverage | 95% | - |
| E2E test coverage | 80% | - |
| All tests pass | Yes | - |
| Test execution time | < 30s (unit) | - |

---

**Next Steps**: Implement unit tests first, then E2E, then dogfooding.
