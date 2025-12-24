"""
Time budget system for workflow plugin.

Provides time budget specifications, enforcement, and reporting for:
- quick mode (< 60s MUST)
- default mode (< 300s SHOULD)
- thorough mode (< 1800s MAX)
"""

from typing import Dict, Any, Optional
import time


class TimeBudget:
    """Time budget configuration and enforcement."""

    # Budget specifications (in seconds)
    BUDGETS = {
        "quick": {
            "budget_seconds": 60,
            "type": "MUST",
            "description": "Strict requirement"
        },
        "default": {
            "budget_seconds": 300,
            "type": "SHOULD",
            "description": "Flexible target"
        },
        "thorough": {
            "budget_seconds": 1800,
            "type": "MAX",
            "description": "Absolute limit"
        }
    }

    def __init__(self):
        """Initialize time budget tracker."""
        self.start_time: Optional[float] = None
        self.mode: Optional[str] = None

    def start(self, mode: str = "default") -> None:
        """
        Start timing for a mode.

        Args:
            mode: Time budget mode (quick/default/thorough)
        """
        self.start_time = time.time()
        self.mode = mode

    def elapsed(self) -> float:
        """
        Get elapsed time since start.

        Returns:
            Elapsed seconds (or 0 if not started)
        """
        if self.start_time is None:
            return 0.0
        return time.time() - self.start_time

    def check_budget_adherence(self, mode: str, elapsed: float) -> bool:
        """
        Check if execution adheres to budget.

        Args:
            mode: Time budget mode
            elapsed: Elapsed time in seconds

        Returns:
            True if within budget, False otherwise
        """
        budget = self.BUDGETS[mode]["budget_seconds"]
        return elapsed <= budget

    def format_completion_message(
        self,
        mode: str,
        elapsed: float,
        budget: Optional[float] = None,
        exceeded: bool = False,
        agents: Optional[list] = None
    ) -> str:
        """
        Format completion message.

        Args:
            mode: Time budget mode
            elapsed: Elapsed time
            budget: Budget seconds (optional, will look up if not provided)
            exceeded: Whether budget was exceeded
            agents: List of agents used (optional)

        Returns:
            Formatted message string
        """
        if budget is None:
            budget = self.BUDGETS[mode]["budget_seconds"]

        if exceeded:
            msg = f"⚠️  {mode.capitalize()} mode exceeded {budget}s budget ({elapsed:.1f}s)"
        else:
            msg = f"✅ Completed in {elapsed:.1f}s (within {mode} budget)"

        if agents:
            msg += f" with {len(agents)} agents"

        return msg

    @classmethod
    def get_budget(cls, mode: str) -> Dict[str, Any]:
        """
        Get budget configuration for a mode.

        Args:
            mode: Time budget mode

        Returns:
            Budget configuration dictionary
        """
        return cls.BUDGETS.get(mode, cls.BUDGETS["default"])

    @classmethod
    def get_all_budgets(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get all budget configurations.

        Returns:
            Dictionary of all budgets
        """
        return cls.BUDGETS


def enforce_time_budget(budget_seconds: int):
    """
    Decorator to enforce time budget on functions.

    Args:
        budget_seconds: Maximum allowed seconds

    Returns:
        Decorator function

    Example:
        @enforce_time_budget(60)
        def quick_operation():
            # ... implementation ...
            return result
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            start = time.time()
            result = func(*args, **kwargs)
            elapsed = time.time() - start

            within_budget = elapsed <= budget_seconds
            return result, elapsed, within_budget

        return wrapper
    return decorator


# Module-level convenience functions

def get_time_budgets() -> Dict[str, Dict[str, Any]]:
    """
    Get all time budget configurations.

    Returns:
        Dictionary with quick, default, and thorough budgets
    """
    return TimeBudget.get_all_budgets()


def get_budget_for_mode(mode: str) -> Dict[str, Any]:
    """
    Get budget configuration for specific mode.

    Args:
        mode: Time budget mode (quick/default/thorough)

    Returns:
        Budget configuration with budget_seconds, type, and description
    """
    return TimeBudget.get_budget(mode)
