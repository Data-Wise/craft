"""
Semester Progress Calculation Utilities

Calculates current week, progress percentage, and milestone information
for teaching projects based on semester dates and break schedules.

Author: Craft Plugin Teaching Workflow
Created: 2026-01-16
"""

from datetime import datetime, timedelta
from typing import Any


def calculate_current_week(
    config: dict[str, Any],
    current_date: str | None = None
) -> dict[str, Any]:
    """
    Calculate current week and semester progress.

    Args:
        config: Teaching configuration dictionary with dates structure:
            {
                "dates": {
                    "start": "YYYY-MM-DD",
                    "end": "YYYY-MM-DD",
                    "breaks": [
                        {"name": str, "start": "YYYY-MM-DD", "end": "YYYY-MM-DD"},
                        ...
                    ]
                },
                "progress": {
                    "current_week": "auto" | int  # Optional manual override
                }
            }
        current_date: ISO date string (YYYY-MM-DD). If None, uses today.

    Returns:
        Dictionary with progress information:
        {
            "current_week": int,           # 1-indexed week number (0 if before start)
            "total_weeks": int,            # Total weeks in semester
            "percent_complete": float,     # 0-100
            "on_break": bool,              # True if currently on break
            "break_name": str | None,      # Name of current break or None
            "days_elapsed": int,           # Days since start (excluding breaks)
            "days_remaining": int,         # Days until end (excluding future breaks)
            "semester_start": str,         # ISO date
            "semester_end": str,           # ISO date
            "week_start": str,             # ISO date (start of current week)
            "week_end": str                # ISO date (end of current week)
        }

    Examples:
        >>> config = {
        ...     "dates": {
        ...         "start": "2026-01-19",
        ...         "end": "2026-05-08",
        ...         "breaks": [
        ...             {"name": "Spring Break", "start": "2026-03-16", "end": "2026-03-20"}
        ...         ]
        ...     }
        ... }
        >>> result = calculate_current_week(config, "2026-02-10")
        >>> result["current_week"]
        4
        >>> result["on_break"]
        False
    """
    # Parse dates
    dates = config.get("dates", {})
    semester_start = datetime.fromisoformat(dates["start"]).date()
    semester_end = datetime.fromisoformat(dates["end"]).date()
    breaks = dates.get("breaks", [])

    # Parse current date
    if current_date is None:
        current = datetime.now().date()
    else:
        current = datetime.fromisoformat(current_date).date()

    # Check for manual override
    progress = config.get("progress", {})
    manual_week = progress.get("current_week")
    if isinstance(manual_week, int):
        # Manual override - calculate other fields but use manual week
        total_weeks = _calculate_total_weeks(semester_start, semester_end, breaks)
        on_break, break_name = is_on_break(current.isoformat(), breaks)

        # Calculate week boundaries for manual week
        week_start, week_end = get_week_boundaries(manual_week, semester_start.isoformat(), breaks)

        # Calculate days
        days_elapsed = _count_days_excluding_breaks(semester_start, current, breaks)
        days_remaining = _count_days_excluding_breaks(current, semester_end, breaks)

        return {
            "current_week": manual_week,
            "total_weeks": total_weeks,
            "percent_complete": min(100.0, (manual_week / total_weeks * 100) if total_weeks > 0 else 0),
            "on_break": on_break,
            "break_name": break_name,
            "days_elapsed": max(0, days_elapsed),
            "days_remaining": max(0, days_remaining),
            "semester_start": semester_start.isoformat(),
            "semester_end": semester_end.isoformat(),
            "week_start": week_start,
            "week_end": week_end
        }

    # Before semester starts
    if current < semester_start:
        total_weeks = _calculate_total_weeks(semester_start, semester_end, breaks)
        return {
            "current_week": 0,
            "total_weeks": total_weeks,
            "percent_complete": 0.0,
            "on_break": False,
            "break_name": None,
            "days_elapsed": 0,
            "days_remaining": _count_days_excluding_breaks(semester_start, semester_end, breaks),
            "semester_start": semester_start.isoformat(),
            "semester_end": semester_end.isoformat(),
            "week_start": semester_start.isoformat(),
            "week_end": (semester_start + timedelta(days=6)).isoformat()
        }

    # After semester ends
    if current > semester_end:
        total_weeks = _calculate_total_weeks(semester_start, semester_end, breaks)
        final_week_start, final_week_end = get_week_boundaries(total_weeks, semester_start.isoformat(), breaks)
        return {
            "current_week": total_weeks,
            "total_weeks": total_weeks,
            "percent_complete": 100.0,
            "on_break": False,
            "break_name": None,
            "days_elapsed": _count_days_excluding_breaks(semester_start, semester_end, breaks),
            "days_remaining": 0,
            "semester_start": semester_start.isoformat(),
            "semester_end": semester_end.isoformat(),
            "week_start": final_week_start,
            "week_end": final_week_end
        }

    # During semester - calculate current week
    on_break, break_name = is_on_break(current.isoformat(), breaks)

    # Count days elapsed excluding breaks
    days_elapsed = _count_days_excluding_breaks(semester_start, current, breaks)

    # Calculate week number (1-indexed)
    current_week = (days_elapsed // 7) + 1

    # Calculate total weeks
    total_weeks = _calculate_total_weeks(semester_start, semester_end, breaks)

    # Cap at total weeks
    current_week = min(current_week, total_weeks)

    # Calculate week boundaries
    week_start, week_end = get_week_boundaries(current_week, semester_start.isoformat(), breaks)

    # Calculate remaining days
    days_remaining = _count_days_excluding_breaks(current, semester_end, breaks)

    # Calculate percent complete
    total_days = _count_days_excluding_breaks(semester_start, semester_end, breaks)
    percent_complete = (days_elapsed / total_days * 100) if total_days > 0 else 0
    percent_complete = min(100.0, percent_complete)

    return {
        "current_week": current_week,
        "total_weeks": total_weeks,
        "percent_complete": round(percent_complete, 2),
        "on_break": on_break,
        "break_name": break_name,
        "days_elapsed": days_elapsed,
        "days_remaining": days_remaining,
        "semester_start": semester_start.isoformat(),
        "semester_end": semester_end.isoformat(),
        "week_start": week_start,
        "week_end": week_end
    }


def _calculate_total_weeks(
    semester_start: datetime.date,
    semester_end: datetime.date,
    breaks: list[dict[str, str]]
) -> int:
    """Calculate total weeks in semester excluding breaks."""
    total_days = _count_days_excluding_breaks(semester_start, semester_end, breaks)
    # Round up to include partial weeks
    return (total_days + 6) // 7


def _count_days_excluding_breaks(
    start_date: datetime.date,
    end_date: datetime.date,
    breaks: list[dict[str, str]]
) -> int:
    """
    Count days between start and end, excluding break days.

    Args:
        start_date: Start date (inclusive)
        end_date: End date (exclusive)
        breaks: List of break dictionaries with "start" and "end" keys

    Returns:
        Number of non-break days
    """
    if start_date >= end_date:
        return 0

    total_days = (end_date - start_date).days

    # Subtract break days that fall within the range
    break_days = 0
    for brk in breaks:
        break_start = datetime.fromisoformat(brk["start"]).date()
        break_end = datetime.fromisoformat(brk["end"]).date()

        # Check if break overlaps with range
        overlap_start = max(start_date, break_start)
        overlap_end = min(end_date, break_end + timedelta(days=1))  # +1 because end is inclusive

        if overlap_start < overlap_end:
            break_days += (overlap_end - overlap_start).days

    return max(0, total_days - break_days)


def count_break_days(
    start_date: str,
    end_date: str,
    breaks: list[dict[str, str]]
) -> int:
    """
    Count total break days between two dates.

    Args:
        start_date: Start date in YYYY-MM-DD format
        end_date: End date in YYYY-MM-DD format
        breaks: List of break dictionaries with "start" and "end" keys

    Returns:
        Number of break days in the range

    Examples:
        >>> breaks = [{"name": "Spring Break", "start": "2026-03-16", "end": "2026-03-20"}]
        >>> count_break_days("2026-01-01", "2026-12-31", breaks)
        5
    """
    start = datetime.fromisoformat(start_date).date()
    end = datetime.fromisoformat(end_date).date()

    total_days = (end - start).days
    days_excluding_breaks = _count_days_excluding_breaks(start, end, breaks)

    return total_days - days_excluding_breaks


def is_on_break(
    current_date: str,
    breaks: list[dict[str, str]]
) -> tuple[bool, str | None]:
    """
    Check if a date falls during a break period.

    Args:
        current_date: Date to check in YYYY-MM-DD format
        breaks: List of break dictionaries with "name", "start", and "end" keys

    Returns:
        Tuple of (is_on_break, break_name). break_name is None if not on break.

    Examples:
        >>> breaks = [{"name": "Spring Break", "start": "2026-03-16", "end": "2026-03-20"}]
        >>> is_on_break("2026-03-18", breaks)
        (True, 'Spring Break')
        >>> is_on_break("2026-02-10", breaks)
        (False, None)
    """
    current = datetime.fromisoformat(current_date).date()

    for brk in breaks:
        break_start = datetime.fromisoformat(brk["start"]).date()
        break_end = datetime.fromisoformat(brk["end"]).date()

        if break_start <= current <= break_end:
            return (True, brk["name"])

    return (False, None)


def get_week_boundaries(
    week_num: int,
    start_date: str,
    breaks: list[dict[str, str]]
) -> tuple[str, str]:
    """
    Get start and end dates for a given week number.

    Week 1 starts on semester start date. Each week is 7 days long.
    Break weeks are skipped - days during breaks don't count toward week progression.

    Args:
        week_num: Week number (1-indexed)
        start_date: Semester start date in YYYY-MM-DD format
        breaks: List of break dictionaries

    Returns:
        Tuple of (week_start_date, week_end_date) in YYYY-MM-DD format

    Examples:
        >>> get_week_boundaries(1, "2026-01-19", [])
        ('2026-01-19', '2026-01-25')
        >>> get_week_boundaries(2, "2026-01-19", [])
        ('2026-01-26', '2026-02-01')
    """
    semester_start = datetime.fromisoformat(start_date).date()

    if week_num <= 0:
        week_num = 1

    # Calculate how many days to advance (accounting for breaks)
    days_to_advance = (week_num - 1) * 7

    # Start from semester start and advance day by day, skipping breaks
    current = semester_start
    days_advanced = 0

    while days_advanced < days_to_advance:
        current += timedelta(days=1)
        # Check if this day is in a break
        on_break, _ = is_on_break(current.isoformat(), breaks)
        if not on_break:
            days_advanced += 1

    week_start = current

    # Find week end (6 days after start, skipping breaks)
    days_in_week = 0
    current = week_start

    while days_in_week < 6:
        current += timedelta(days=1)
        on_break, _ = is_on_break(current.isoformat(), breaks)
        if not on_break:
            days_in_week += 1

    week_end = current

    return (week_start.isoformat(), week_end.isoformat())


def format_date_range(start: str, end: str) -> str:
    """
    Format date range as 'Jan 27 - Feb 2' (ADHD-friendly).

    Args:
        start: Start date in YYYY-MM-DD format
        end: End date in YYYY-MM-DD format

    Returns:
        Formatted date range string

    Examples:
        >>> format_date_range("2026-01-27", "2026-02-02")
        'Jan 27 - Feb 2'
        >>> format_date_range("2026-03-16", "2026-03-20")
        'Mar 16-20'
    """
    start_date = datetime.fromisoformat(start).date()
    end_date = datetime.fromisoformat(end).date()

    # Same month - use compact format
    if start_date.month == end_date.month:
        return f"{start_date.strftime('%b')} {start_date.day}-{end_date.day}"

    # Different months
    return f"{start_date.strftime('%b')} {start_date.day} - {end_date.strftime('%b')} {end_date.day}"
