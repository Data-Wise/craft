"""
Unit tests for semester progress calculation.

Tests week calculation, break handling, edge cases, and date formatting.

Run with:
    python3 -m pytest tests/test_semester_progress.py -v
    python3 -m pytest tests/test_semester_progress.py::TestSemesterProgress::test_week_calculation_no_breaks -v
"""

import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from commands.utils.semester_progress import (
    calculate_current_week,
    count_break_days,
    format_date_range,
    get_week_boundaries,
    is_on_break,
)


class TestSemesterProgress:
    """Test semester progress calculations."""

    def test_week_calculation_no_breaks(self):
        """Test basic week calculation without breaks."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            }
        }

        # Week 1 (start date)
        result = calculate_current_week(config, "2026-01-19")
        assert result["current_week"] == 1
        assert result["total_weeks"] == 16
        assert result["on_break"] is False
        assert result["break_name"] is None
        assert result["percent_complete"] < 10

        # Week 4 (3 weeks after start)
        result = calculate_current_week(config, "2026-02-09")
        assert result["current_week"] == 4
        assert result["on_break"] is False

        # Week 9 (March 16 = 56 days = 8 full weeks)
        result = calculate_current_week(config, "2026-03-16")
        assert result["current_week"] == 9
        assert 50 < result["percent_complete"] < 60

        # Final week
        result = calculate_current_week(config, "2026-05-04")
        assert result["current_week"] == 16
        assert result["percent_complete"] > 90

    def test_week_calculation_with_breaks(self):
        """Test week calculation with spring break."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08",
                "breaks": [
                    {
                        "name": "Spring Break",
                        "start": "2026-03-16",
                        "end": "2026-03-20"
                    }
                ]
            }
        }

        # Before break (Mar 15 = 55 days = 7 full weeks, so week 8)
        result = calculate_current_week(config, "2026-03-15")
        assert result["current_week"] == 8
        assert result["on_break"] is False

        # During break (Week 9 - break days don't advance week)
        result = calculate_current_week(config, "2026-03-18")
        assert result["on_break"] is True
        assert result["break_name"] == "Spring Break"
        assert result["current_week"] == 9

        # After break (Week 9 - 63 total days - 5 break days = 58 days = week 9)
        result = calculate_current_week(config, "2026-03-23")
        assert result["current_week"] == 9
        assert result["on_break"] is False

    def test_multiple_breaks(self):
        """Test semester with multiple breaks."""
        config = {
            "dates": {
                "start": "2025-09-02",
                "end": "2025-12-15",
                "breaks": [
                    {
                        "name": "Fall Break",
                        "start": "2025-10-12",
                        "end": "2025-10-13"
                    },
                    {
                        "name": "Thanksgiving",
                        "start": "2025-11-25",
                        "end": "2025-11-29"
                    }
                ]
            }
        }

        # Before first break
        result = calculate_current_week(config, "2025-10-10")
        assert result["on_break"] is False

        # During first break
        result = calculate_current_week(config, "2025-10-12")
        assert result["on_break"] is True
        assert result["break_name"] == "Fall Break"

        # Between breaks
        result = calculate_current_week(config, "2025-11-15")
        assert result["on_break"] is False

        # During second break
        result = calculate_current_week(config, "2025-11-27")
        assert result["on_break"] is True
        assert result["break_name"] == "Thanksgiving"

        # After all breaks
        result = calculate_current_week(config, "2025-12-10")
        assert result["on_break"] is False

    def test_on_break_detection(self):
        """Test is_on_break function."""
        breaks = [
            {"name": "Spring Break", "start": "2026-03-16", "end": "2026-03-20"},
            {"name": "Reading Week", "start": "2026-04-13", "end": "2026-04-14"}
        ]

        # Not on break
        on_break, name = is_on_break("2026-02-10", breaks)
        assert on_break is False
        assert name is None

        # On Spring Break (first day)
        on_break, name = is_on_break("2026-03-16", breaks)
        assert on_break is True
        assert name == "Spring Break"

        # On Spring Break (middle)
        on_break, name = is_on_break("2026-03-18", breaks)
        assert on_break is True
        assert name == "Spring Break"

        # On Spring Break (last day)
        on_break, name = is_on_break("2026-03-20", breaks)
        assert on_break is True
        assert name == "Spring Break"

        # Between breaks
        on_break, name = is_on_break("2026-04-01", breaks)
        assert on_break is False
        assert name is None

        # On Reading Week
        on_break, name = is_on_break("2026-04-13", breaks)
        assert on_break is True
        assert name == "Reading Week"

    def test_before_semester(self):
        """Test date before semester starts."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            }
        }

        result = calculate_current_week(config, "2025-12-15")
        assert result["current_week"] == 0
        assert result["percent_complete"] == 0.0
        assert result["on_break"] is False
        assert result["days_elapsed"] == 0
        assert result["days_remaining"] > 0

    def test_after_semester(self):
        """Test date after semester ends."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            }
        }

        result = calculate_current_week(config, "2026-06-01")
        assert result["current_week"] == result["total_weeks"]
        assert result["percent_complete"] == 100.0
        assert result["on_break"] is False
        assert result["days_remaining"] == 0

    def test_summer_session_no_breaks(self):
        """Test compressed summer session without breaks."""
        config = {
            "dates": {
                "start": "2026-06-01",
                "end": "2026-07-24"
            }
        }

        # Week 1
        result = calculate_current_week(config, "2026-06-01")
        assert result["current_week"] == 1
        assert result["total_weeks"] == 8

        # Week 4 (21 days = 3 full weeks, so week 4)
        result = calculate_current_week(config, "2026-06-22")
        assert result["current_week"] == 4
        # 21 days out of 53 total = ~40%
        assert 38 < result["percent_complete"] < 42

        # Final week
        result = calculate_current_week(config, "2026-07-20")
        assert result["current_week"] == 8

    def test_manual_override(self):
        """Test manual week override in config."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            },
            "progress": {
                "current_week": 12  # Manual override
            }
        }

        # Should use manual week regardless of date
        result = calculate_current_week(config, "2026-02-01")
        assert result["current_week"] == 12
        assert result["total_weeks"] == 16
        # Percent should reflect manual week
        assert 70 < result["percent_complete"] < 80

    def test_week_boundaries(self):
        """Test week boundary calculation."""
        # No breaks
        start, end = get_week_boundaries(1, "2026-01-19", [])
        assert start == "2026-01-19"
        assert end == "2026-01-25"

        start, end = get_week_boundaries(2, "2026-01-19", [])
        assert start == "2026-01-26"
        assert end == "2026-02-01"

        # With break (week 9 should skip over spring break)
        breaks = [{"name": "Spring Break", "start": "2026-03-16", "end": "2026-03-20"}]
        start, end = get_week_boundaries(9, "2026-01-19", breaks)
        # Week 9 starts after break ends
        assert start > "2026-03-20"

    def test_count_break_days(self):
        """Test counting break days in a range."""
        breaks = [
            {"name": "Spring Break", "start": "2026-03-16", "end": "2026-03-20"}
        ]

        # Entire semester (5-day break)
        days = count_break_days("2026-01-01", "2026-12-31", breaks)
        assert days == 5

        # Range containing break
        days = count_break_days("2026-03-10", "2026-03-25", breaks)
        assert days == 5

        # Range before break
        days = count_break_days("2026-01-01", "2026-03-01", breaks)
        assert days == 0

        # Range after break
        days = count_break_days("2026-04-01", "2026-05-01", breaks)
        assert days == 0

        # Partial overlap (last 2 days of break)
        days = count_break_days("2026-03-19", "2026-03-25", breaks)
        assert days == 2

    def test_date_formatting(self):
        """Test ADHD-friendly date formatting."""
        # Same month
        formatted = format_date_range("2026-01-27", "2026-01-30")
        assert formatted == "Jan 27-30"

        # Different months
        formatted = format_date_range("2026-01-27", "2026-02-02")
        assert formatted == "Jan 27 - Feb 2"

        # Spring break example
        formatted = format_date_range("2026-03-16", "2026-03-20")
        assert formatted == "Mar 16-20"

    def test_first_week_edge_case(self):
        """Test first week of semester."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            }
        }

        # First day
        result = calculate_current_week(config, "2026-01-19")
        assert result["current_week"] == 1
        assert result["week_start"] == "2026-01-19"
        assert result["days_elapsed"] == 0

        # Second day (still week 1)
        result = calculate_current_week(config, "2026-01-20")
        assert result["current_week"] == 1
        assert result["days_elapsed"] == 1

    def test_last_week_edge_case(self):
        """Test last week of semester."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            }
        }

        # Last day
        result = calculate_current_week(config, "2026-05-08")
        assert result["current_week"] == result["total_weeks"]
        assert result["days_remaining"] == 0
        assert result["percent_complete"] == 100.0

        # Day before last
        result = calculate_current_week(config, "2026-05-07")
        assert result["current_week"] == result["total_weeks"]
        assert result["days_remaining"] == 1

    def test_days_elapsed_and_remaining(self):
        """Test days_elapsed and days_remaining calculations."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-02-09",  # 3 weeks
                "breaks": [
                    {"name": "Break", "start": "2026-01-26", "end": "2026-01-28"}  # 3 days
                ]
            }
        }

        # Before break (7 days elapsed)
        result = calculate_current_week(config, "2026-01-25")
        assert result["days_elapsed"] == 6

        # During break (7 days elapsed, frozen)
        result = calculate_current_week(config, "2026-01-27")
        assert result["on_break"] is True
        assert result["days_elapsed"] == 7  # Doesn't count break days

        # After break
        result = calculate_current_week(config, "2026-01-30")
        assert result["days_elapsed"] == 8  # 7 before + 1 after (skipped 3 break days)

    def test_return_structure_completeness(self):
        """Test that return dictionary has all required fields."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            }
        }

        result = calculate_current_week(config, "2026-02-10")

        # Check all required fields exist
        required_fields = {
            "current_week",
            "total_weeks",
            "percent_complete",
            "on_break",
            "break_name",
            "days_elapsed",
            "days_remaining",
            "semester_start",
            "semester_end",
            "week_start",
            "week_end"
        }

        assert set(result.keys()) == required_fields

        # Check types
        assert isinstance(result["current_week"], int)
        assert isinstance(result["total_weeks"], int)
        assert isinstance(result["percent_complete"], (int, float))
        assert isinstance(result["on_break"], bool)
        assert result["break_name"] is None or isinstance(result["break_name"], str)
        assert isinstance(result["days_elapsed"], int)
        assert isinstance(result["days_remaining"], int)
        assert isinstance(result["semester_start"], str)
        assert isinstance(result["semester_end"], str)
        assert isinstance(result["week_start"], str)
        assert isinstance(result["week_end"], str)

    def test_performance(self):
        """Test calculation performance (< 100ms target)."""
        import time

        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08",
                "breaks": [
                    {"name": "Spring Break", "start": "2026-03-16", "end": "2026-03-20"},
                    {"name": "Reading Week", "start": "2026-04-13", "end": "2026-04-14"}
                ]
            }
        }

        # Run 100 calculations
        start_time = time.time()
        for _ in range(100):
            calculate_current_week(config, "2026-03-10")
        elapsed = time.time() - start_time

        # Should complete 100 calculations in < 100ms (avg < 1ms each)
        assert elapsed < 0.1, f"Performance regression: {elapsed*10:.2f}ms per call"

    def test_break_on_semester_boundary(self):
        """Test break that starts/ends on semester boundaries."""
        config = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-03-01",
                "breaks": [
                    # Break starts on semester start
                    {"name": "Orientation", "start": "2026-01-19", "end": "2026-01-20"}
                ]
            }
        }

        result = calculate_current_week(config, "2026-01-19")
        assert result["on_break"] is True
        assert result["break_name"] == "Orientation"

    def test_auto_vs_manual_override(self):
        """Test that manual override takes precedence over auto calculation."""
        config_auto = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            },
            "progress": {
                "current_week": "auto"
            }
        }

        config_manual = {
            "dates": {
                "start": "2026-01-19",
                "end": "2026-05-08"
            },
            "progress": {
                "current_week": 15  # Manual override
            }
        }

        # Auto should calculate based on date
        result_auto = calculate_current_week(config_auto, "2026-02-10")
        assert result_auto["current_week"] == 4

        # Manual should use override
        result_manual = calculate_current_week(config_manual, "2026-02-10")
        assert result_manual["current_week"] == 15

    def test_default_current_date(self):
        """Test using default current date (today)."""
        config = {
            "dates": {
                "start": "2020-01-01",  # Past date
                "end": "2030-12-31"     # Future date
            }
        }

        # Should use today's date when current_date is None
        result = calculate_current_week(config)
        assert result["current_week"] > 0
        assert isinstance(result["current_week"], int)
        assert isinstance(result["percent_complete"], (int, float))


if __name__ == "__main__":
    import pytest
    sys.exit(pytest.main([__file__, "-v"]))
