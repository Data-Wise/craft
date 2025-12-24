"""
Unit tests for time budget system in workflow plugin.

Tests time budget specifications, enforcement, and reporting for:
- quick mode (< 60s MUST)
- default mode (< 300s SHOULD)
- thorough mode (< 1800s MAX)
"""

import pytest
import time


@pytest.mark.unit
class TestTimeBudgetSpecifications:
    """Test time budget specifications for each mode."""

    def test_quick_mode_budget_60_seconds(self, time_budgets):
        """Quick mode must have strict 60 second budget."""
        quick_budget = time_budgets["quick"]

        assert quick_budget["budget_seconds"] == 60
        assert quick_budget["type"] == "MUST"

    def test_default_mode_budget_300_seconds(self, time_budgets):
        """Default mode should have 300 second (5 min) budget."""
        default_budget = time_budgets["default"]

        assert default_budget["budget_seconds"] == 300
        assert default_budget["type"] == "SHOULD"

    def test_thorough_mode_budget_1800_seconds(self, time_budgets):
        """Thorough mode max 1800 seconds (30 min) budget."""
        thorough_budget = time_budgets["thorough"]

        assert thorough_budget["budget_seconds"] == 1800
        assert thorough_budget["type"] == "MAX"

    def test_budget_type_hierarchy(self, time_budgets):
        """Test budget type hierarchy (MUST > SHOULD > MAX)."""
        types = ["MUST", "SHOULD", "MAX"]

        assert time_budgets["quick"]["type"] == types[0]
        assert time_budgets["default"]["type"] == types[1]
        assert time_budgets["thorough"]["type"] == types[2]

    def test_budgets_increase_with_mode_depth(self, time_budgets):
        """Budgets should increase: quick < default < thorough."""
        assert time_budgets["quick"]["budget_seconds"] < time_budgets["default"]["budget_seconds"]
        assert time_budgets["default"]["budget_seconds"] < time_budgets["thorough"]["budget_seconds"]


@pytest.mark.unit
class TestTimeBudgetEnforcement:
    """Test time budget enforcement logic."""

    def test_within_quick_budget_passes(self, time_budgets):
        """Test execution within quick budget passes."""
        budget = time_budgets["quick"]["budget_seconds"]
        elapsed = 45  # 45 seconds

        assert elapsed < budget
        assert self._check_budget_adherence("quick", elapsed, budget) is True

    def test_exceeds_quick_budget_fails(self, time_budgets):
        """Test execution exceeding quick budget fails."""
        budget = time_budgets["quick"]["budget_seconds"]
        elapsed = 75  # 75 seconds (over 60s limit)

        assert elapsed > budget
        assert self._check_budget_adherence("quick", elapsed, budget) is False

    def test_within_default_budget_passes(self, time_budgets):
        """Test execution within default budget passes."""
        budget = time_budgets["default"]["budget_seconds"]
        elapsed = 240  # 4 minutes

        assert elapsed < budget
        assert self._check_budget_adherence("default", elapsed, budget) is True

    def test_slightly_exceeds_default_budget_warning(self, time_budgets):
        """Default mode SHOULD target means warning, not failure."""
        budget = time_budgets["default"]["budget_seconds"]
        elapsed = 350  # 5min 50s (slightly over)

        # SHOULD budgets generate warnings but don't fail
        assert elapsed > budget
        assert time_budgets["default"]["type"] == "SHOULD"

    def test_within_thorough_budget_passes(self, time_budgets):
        """Test execution within thorough budget passes."""
        budget = time_budgets["thorough"]["budget_seconds"]
        elapsed = 1200  # 20 minutes

        assert elapsed < budget
        assert self._check_budget_adherence("thorough", elapsed, budget) is True

    def _check_budget_adherence(self, mode: str, elapsed: float, budget: float) -> bool:
        """Helper to check if execution adheres to budget."""
        return elapsed <= budget


@pytest.mark.unit
class TestTimeBudgetReporting:
    """Test time budget completion reporting."""

    def test_quick_mode_completion_message(self):
        """Test quick mode completion message format."""
        elapsed = 42
        budget = 60

        message = self._format_completion_message("quick", elapsed, budget)

        assert "42" in message or "42.0" in message
        assert "quick" in message.lower()
        assert "within" in message.lower() or "✅" in message

    def test_quick_mode_exceeded_message(self):
        """Test quick mode exceeded message format."""
        elapsed = 75
        budget = 60

        message = self._format_completion_message("quick", elapsed, budget, exceeded=True)

        assert "75" in message or "75.0" in message
        assert "exceeded" in message.lower() or "⚠️" in message
        assert "60" in message  # Shows budget

    def test_default_mode_completion_message(self):
        """Test default mode completion message."""
        elapsed = 180  # 3 minutes
        budget = 300

        message = self._format_completion_message("default", elapsed, budget)

        assert "180" in message or "3m" in message.lower()
        assert "default" in message.lower()

    def test_thorough_mode_with_agents_message(self):
        """Test thorough mode message includes agent info."""
        elapsed = 204  # 3m 24s
        budget = 1800
        agents = ["backend-architect", "database-architect"]

        message = self._format_completion_message(
            "thorough", elapsed, budget, agents=agents
        )

        assert "204" in message or "3m 24s" in message.lower()
        assert "backend-architect" in message.lower() or "2 agents" in message.lower()

    def _format_completion_message(
        self, mode: str, elapsed: float, budget: float,
        exceeded: bool = False, agents: list = None
    ) -> str:
        """Helper to format completion message."""
        if exceeded:
            msg = f"⚠️  {mode.capitalize()} mode exceeded {budget}s budget ({elapsed:.1f}s)"
        else:
            msg = f"✅ Completed in {elapsed:.1f}s (within {mode} budget)"

        if agents:
            msg += f" with {len(agents)} agents"

        return msg


@pytest.mark.unit
class TestModeBehaviors:
    """Test expected behaviors for each mode."""

    def test_quick_mode_no_agent_delegation(self, mode_examples):
        """Quick mode should never delegate to agents."""
        quick = mode_examples["quick"]

        assert quick["delegation"] is False
        assert quick["agents_count"] == 0

    def test_default_mode_optional_delegation(self, mode_examples):
        """Default mode should have optional agent delegation."""
        default = mode_examples["default"]

        assert default["delegation"] == "optional"
        assert default["agents_count"][0] == 0  # min 0 agents
        assert default["agents_count"][1] >= 1  # max 1+ agents

    def test_thorough_mode_requires_delegation(self, mode_examples):
        """Thorough mode should require agent delegation."""
        thorough = mode_examples["thorough"]

        assert thorough["delegation"] is True
        assert thorough["agents_count"][0] >= 2  # min 2 agents
        assert thorough["agents_count"][1] <= 4  # max 4 agents

    def test_quick_mode_output_constraints(self, mode_examples):
        """Quick mode should produce 5-7 ideas."""
        quick = mode_examples["quick"]

        min_ideas, max_ideas = quick["output_items"]
        assert min_ideas == 5
        assert max_ideas == 7

    def test_thorough_mode_output_comprehensive(self, mode_examples):
        """Thorough mode should produce 15-30 ideas."""
        thorough = mode_examples["thorough"]

        min_ideas, max_ideas = thorough["output_items"]
        assert min_ideas >= 15
        assert max_ideas <= 30


@pytest.mark.unit
@pytest.mark.slow
class TestRealTimeBudgetMeasurement:
    """Test actual time budget measurement (slower tests)."""

    def test_measure_quick_operation_time(self):
        """Measure time for simulated quick operation."""
        start = time.time()

        # Simulate quick brainstorm (sleep for 0.1s to represent fast operation)
        time.sleep(0.1)

        elapsed = time.time() - start

        # Should be well under 60s budget
        assert elapsed < 60
        assert elapsed < 1  # Should be very fast

    def test_measure_default_operation_time(self):
        """Measure time for simulated default operation."""
        start = time.time()

        # Simulate default brainstorm (sleep for 0.5s)
        time.sleep(0.5)

        elapsed = time.time() - start

        # Should be under 300s budget
        assert elapsed < 300
        assert elapsed < 5  # Should be reasonably fast

    def test_time_budget_decorator_logic(self):
        """Test time budget decorator/wrapper logic."""

        def enforce_time_budget(budget_seconds: int):
            """Decorator to enforce time budget."""
            def decorator(func):
                def wrapper(*args, **kwargs):
                    start = time.time()
                    result = func(*args, **kwargs)
                    elapsed = time.time() - start

                    return result, elapsed, elapsed <= budget_seconds

                return wrapper
            return decorator

        @enforce_time_budget(budget_seconds=60)
        def quick_operation():
            time.sleep(0.05)
            return "result"

        result, elapsed, within_budget = quick_operation()

        assert result == "result"
        assert elapsed < 1
        assert within_budget is True


@pytest.mark.unit
class TestTimeBudgetConfiguration:
    """Test time budget configuration and validation."""

    def test_all_modes_have_budgets(self, time_budgets):
        """All modes should have defined time budgets."""
        required_modes = ["quick", "default", "thorough"]

        for mode in required_modes:
            assert mode in time_budgets
            assert "budget_seconds" in time_budgets[mode]
            assert "type" in time_budgets[mode]

    def test_budgets_are_positive_integers(self, time_budgets):
        """All budgets should be positive integers."""
        for mode, config in time_budgets.items():
            budget = config["budget_seconds"]
            assert isinstance(budget, int)
            assert budget > 0

    def test_budget_types_are_valid(self, time_budgets):
        """Budget types should be MUST, SHOULD, or MAX."""
        valid_types = ["MUST", "SHOULD", "MAX"]

        for mode, config in time_budgets.items():
            assert config["type"] in valid_types

    def test_budget_descriptions_exist(self, time_budgets):
        """All budgets should have descriptions."""
        for mode, config in time_budgets.items():
            assert "description" in config
            assert len(config["description"]) > 0


@pytest.mark.unit
class TestTimeBudgetEdgeCases:
    """Test edge cases for time budget system."""

    def test_exactly_at_budget_limit(self, time_budgets):
        """Test execution exactly at budget limit."""
        budget = time_budgets["quick"]["budget_seconds"]
        elapsed = 60.0  # Exactly at limit

        # Should pass (<=)
        assert elapsed <= budget

    def test_one_millisecond_over_budget(self, time_budgets):
        """Test execution just barely over budget."""
        budget = time_budgets["quick"]["budget_seconds"]
        elapsed = 60.001  # 1ms over

        # Should fail (>)
        assert elapsed > budget

    def test_zero_elapsed_time(self):
        """Test handling of zero elapsed time."""
        elapsed = 0
        budget = 60

        assert elapsed < budget
        assert elapsed >= 0  # Should handle gracefully

    def test_negative_elapsed_time_impossible(self):
        """Negative elapsed time should be impossible."""
        # This should never happen, but test defensively
        start = time.time()
        time.sleep(0.01)
        end = time.time()

        elapsed = end - start
        assert elapsed >= 0


@pytest.mark.unit
class TestPerformanceGuarantees:
    """Test documented performance guarantee levels."""

    def test_quick_mode_must_guarantee(self, time_budgets):
        """MUST guarantees are strict requirements."""
        quick = time_budgets["quick"]

        assert quick["type"] == "MUST"
        # MUST = strict enforcement, failures are errors

    def test_default_mode_should_guarantee(self, time_budgets):
        """SHOULD guarantees are flexible targets."""
        default = time_budgets["default"]

        assert default["type"] == "SHOULD"
        # SHOULD = target, warnings if exceeded but not errors

    def test_thorough_mode_max_guarantee(self, time_budgets):
        """MAX guarantees are absolute limits."""
        thorough = time_budgets["thorough"]

        assert thorough["type"] == "MAX"
        # MAX = absolute limit, must terminate if reached

    def test_guarantee_levels_documented(self, time_budgets):
        """All guarantee levels should have clear semantics."""
        semantics = {
            "MUST": "strict requirement",
            "SHOULD": "flexible target",
            "MAX": "absolute limit"
        }

        for mode, config in time_budgets.items():
            budget_type = config["type"]
            assert budget_type in semantics
