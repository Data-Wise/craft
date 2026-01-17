#!/usr/bin/env python3
"""
Test complexity scoring algorithm for /craft:do routing.

Tests the scoring logic that determines whether tasks should be:
- Routed to specific commands (score 0-3)
- Delegated to single agent (score 4-7)
- Delegated to orchestrator (score 8-10)
"""

import sys
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.complexity_scorer import (
    calculate_complexity_score,
    get_routing_decision,
    explain_score
)


class TestComplexityScoring:
    """Tests for complexity scoring algorithm."""

    def test_simple_task_low_score(self):
        """Simple single-operation tasks should score 1-2."""
        task = "lint code"
        score = calculate_complexity_score(task)
        assert 0 <= score <= 2, f"Expected 0-2 for simple task, got {score}"

        routing = get_routing_decision(score)
        assert routing == "commands", f"Simple task should route to commands, got {routing}"

    def test_multistep_task_medium_score(self):
        """Multi-step tasks should score 4-6."""
        task = "lint code, run tests, and build project"
        score = calculate_complexity_score(task)
        assert 4 <= score <= 6, f"Expected 4-6 for multi-step task, got {score}"

        routing = get_routing_decision(score)
        assert routing == "agent", f"Multi-step task should route to agent, got {routing}"

    def test_complex_architecture_high_score(self):
        """Complex architectural tasks should score 8-10."""
        task = "design authentication system with OAuth2, PKCE flow, session management, and refresh token rotation"
        score = calculate_complexity_score(task)
        assert 8 <= score <= 10, f"Expected 8-10 for complex architecture, got {score}"

        routing = get_routing_decision(score)
        assert routing == "orchestrator", f"Complex task should route to orchestrator, got {routing}"

    def test_boundary_score_3_routes_to_commands(self):
        """Score of 3 should route to commands."""
        task = "format code and commit changes"
        score = calculate_complexity_score(task)

        # Should be at or below boundary
        assert score <= 3, f"Expected ≤3 for simple two-step task, got {score}"

        routing = get_routing_decision(score)
        assert routing == "commands", f"Score {score} should route to commands, got {routing}"

    def test_boundary_score_4_routes_to_agent(self):
        """Score of 4 should route to single agent."""
        task = "format code, run tests, and fix any errors"
        score = calculate_complexity_score(task)

        # Should be at or above boundary
        assert score >= 4, f"Expected ≥4 for three-step task, got {score}"

        routing = get_routing_decision(score)
        assert routing == "agent", f"Score {score} should route to agent, got {routing}"

    def test_boundary_score_7_routes_to_single_agent(self):
        """Score of 7 should still route to single agent."""
        task = "refactor authentication module and add comprehensive tests"
        score = calculate_complexity_score(task)

        # Should be between 4-7
        assert 4 <= score <= 7, f"Expected 4-7 for refactor with tests, got {score}"

        routing = get_routing_decision(score)
        assert routing == "agent", f"Score {score} should route to agent, got {routing}"

    def test_boundary_score_8_routes_to_orchestrator(self):
        """Score of 8 should route to orchestrator."""
        # Task with all factors: multi-step, cross-category (4+), planning, multi-file
        task = "design and implement entire authentication system with unit tests, integration tests, documentation, and CI pipeline"
        score = calculate_complexity_score(task)

        # Should be 8 or higher
        assert score >= 8, f"Expected ≥8 for comprehensive feature task, got {score}"

        routing = get_routing_decision(score)
        assert routing == "orchestrator", f"Score {score} should route to orchestrator, got {routing}"

    def test_multi_step_factor_detection(self):
        """Tasks with multiple steps should get +2."""
        # Task with commas (clear multi-step)
        task1 = "lint, test, build"
        result1 = explain_score(task1)
        assert any("Multi-step" in factor for factor in result1['factors']), \
            f"Should detect multi-step in comma-separated task"

        # Task with 'and'
        task2 = "run tests and check coverage"
        result2 = explain_score(task2)
        assert any("Multi-step" in factor for factor in result2['factors']), \
            f"Should detect multi-step in 'and' conjunction"

    def test_cross_category_factor_detection(self):
        """Tasks spanning multiple categories should get +2."""
        task = "implement feature and add tests"
        result = explain_score(task)

        # Should detect both 'code' and 'test' categories
        assert any("Cross-category" in factor for factor in result['factors']), \
            f"Should detect cross-category task (code + test)"

    def test_planning_factor_detection(self):
        """Tasks requiring planning should get +2."""
        task = "design API architecture for authentication"
        result = explain_score(task)

        assert any("planning" in factor.lower() for factor in result['factors']), \
            f"Should detect planning requirement in design task"

    def test_research_factor_detection(self):
        """Tasks requiring research should get +2."""
        task = "investigate performance bottleneck"
        result = explain_score(task)

        assert any("research" in factor.lower() for factor in result['factors']), \
            f"Should detect research requirement in investigate task"

    def test_multi_file_factor_detection(self):
        """Tasks affecting multiple files should get +2."""
        task = "refactor entire authentication module"
        result = explain_score(task)

        assert any("Multi-file" in factor for factor in result['factors']), \
            f"Should detect multi-file impact in 'entire module' task"

    def test_explain_score_output(self):
        """explain_score() should return detailed breakdown."""
        task = "design auth system with OAuth2 and tests"
        result = explain_score(task)

        # Check required fields
        assert 'task' in result
        assert 'score' in result
        assert 'routing' in result
        assert 'factors' in result
        assert 'explanation' in result

        # Should have multiple factors
        assert len(result['factors']) >= 2, \
            f"Complex task should have multiple factors, got {result['factors']}"

    def test_score_capped_at_10(self):
        """Score should never exceed 10."""
        # Create task with all possible factors
        task = "design and implement entire authentication system with OAuth2, PKCE, " \
               "session management, refresh tokens, investigate security best practices, " \
               "add comprehensive tests, documentation, and CI pipeline across multiple modules"

        score = calculate_complexity_score(task)
        assert score <= 10, f"Score should be capped at 10, got {score}"

    def test_empty_task(self):
        """Empty task should score 0."""
        task = ""
        score = calculate_complexity_score(task)
        assert score == 0, f"Empty task should score 0, got {score}"

        routing = get_routing_decision(score)
        assert routing == "commands", f"Empty task should route to commands, got {routing}"


def run_tests():
    """Run all tests and report results."""
    import time

    test_class = TestComplexityScoring()
    test_methods = [
        method for method in dir(test_class)
        if method.startswith('test_')
    ]

    print("=" * 80)
    print("Complexity Scoring Unit Tests")
    print("=" * 80)

    passed = 0
    failed = 0
    total_time = 0

    for method_name in test_methods:
        method = getattr(test_class, method_name)
        test_name = method_name.replace('test_', '').replace('_', ' ').title()

        try:
            start = time.time()
            method()
            duration = (time.time() - start) * 1000
            total_time += duration

            print(f"✓ {test_name:60} ({duration:.1f}ms)")
            passed += 1

        except AssertionError as e:
            print(f"✗ {test_name:60} FAILED")
            print(f"  {str(e)}")
            failed += 1

        except Exception as e:
            print(f"✗ {test_name:60} ERROR")
            print(f"  {type(e).__name__}: {str(e)}")
            failed += 1

    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed ({total_time:.1f}ms total)")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
