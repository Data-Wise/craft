#!/usr/bin/env python3
"""
Teaching Configuration Parser

Parses and validates .flow/teach-config.yml files for teaching projects.
Provides robust error handling and comprehensive validation of dates, breaks,
and required fields.

Usage:
    from commands.utils.teach_config import load_teach_config

    config = load_teach_config()
    if config:
        print(f"Course: {config['course']['number']}")
        print(f"Current week: {config['progress']['current_week']}")
"""

import os
import sys
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any

try:
    import yaml
except ImportError:
    print("Error: PyYAML not installed. Run: pip install pyyaml", file=sys.stderr)
    sys.exit(1)


# Default values for optional fields
DEFAULTS = {
    "deployment": {
        "production_branch": "production",
        "draft_branch": "draft",
    },
    "progress": {
        "current_week": "auto",
    },
    "validation": {
        "required_sections": ["grading", "policies", "objectives", "schedule"],
        "strict_mode": True,
    },
    "dates": {
        "breaks": [],
    },
}


# Valid semester values
VALID_SEMESTERS = ["Spring", "Fall", "Winter", "Summer"]


def get_config_path(cwd: str = ".") -> Optional[str]:
    """
    Find the teaching config file.

    Priority:
    1. .flow/teach-config.yml
    2. teach-config.yml (root)

    Args:
        cwd: Current working directory (default: ".")

    Returns:
        Absolute path to config file, or None if not found
    """
    cwd_path = Path(cwd).resolve()

    # Priority 1: .flow/teach-config.yml
    flow_config = cwd_path / ".flow" / "teach-config.yml"
    if flow_config.exists():
        return str(flow_config)

    # Priority 2: teach-config.yml (root)
    root_config = cwd_path / "teach-config.yml"
    if root_config.exists():
        return str(root_config)

    return None


def validate_date(date_str: str) -> bool:
    """
    Validate date string is in YYYY-MM-DD format with zero padding.

    Args:
        date_str: Date string to validate

    Returns:
        True if valid, False otherwise
    """
    if not isinstance(date_str, str):
        return False

    # Check exact format (YYYY-MM-DD with zero padding)
    if len(date_str) != 10:
        return False

    parts = date_str.split("-")
    if len(parts) != 3:
        return False

    # Check each part has correct length
    if len(parts[0]) != 4 or len(parts[1]) != 2 or len(parts[2]) != 2:
        return False

    # Now validate it's a real date
    try:
        datetime.strptime(date_str, "%Y-%m-%d")
        return True
    except (ValueError, TypeError):
        return False


def parse_date(date_str: str) -> Optional[datetime]:
    """
    Parse date string to datetime object.

    Args:
        date_str: Date string in YYYY-MM-DD format

    Returns:
        datetime object or None if invalid
    """
    try:
        return datetime.strptime(date_str, "%Y-%m-%d")
    except (ValueError, TypeError):
        return None


def validate_breaks(breaks: List[Dict[str, str]], start: str, end: str) -> List[str]:
    """
    Validate break periods.

    Checks:
    - Each break has required fields (name, start, end)
    - Break dates are valid YYYY-MM-DD format
    - Break start < break end
    - Breaks fall within semester dates
    - Breaks don't overlap

    Args:
        breaks: List of break dictionaries
        start: Semester start date (YYYY-MM-DD)
        end: Semester end date (YYYY-MM-DD)

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    if not breaks:
        return errors

    semester_start = parse_date(start)
    semester_end = parse_date(end)

    if not semester_start or not semester_end:
        errors.append("Cannot validate breaks: invalid semester dates")
        return errors

    parsed_breaks = []

    for i, break_period in enumerate(breaks, 1):
        # Check required fields
        if not isinstance(break_period, dict):
            errors.append(f"Break {i}: must be a dictionary")
            continue

        if "name" not in break_period:
            errors.append(f"Break {i}: missing 'name' field")
        if "start" not in break_period:
            errors.append(f"Break {i}: missing 'start' field")
        if "end" not in break_period:
            errors.append(f"Break {i}: missing 'end' field")

        if len(errors) > 0 and f"Break {i}:" in errors[-1]:
            continue  # Skip further validation if missing required fields

        name = break_period["name"]
        break_start_str = break_period["start"]
        break_end_str = break_period["end"]

        # Validate date formats
        if not validate_date(break_start_str):
            errors.append(f"Break '{name}': invalid start date format (expected YYYY-MM-DD)")
            continue
        if not validate_date(break_end_str):
            errors.append(f"Break '{name}': invalid end date format (expected YYYY-MM-DD)")
            continue

        break_start = parse_date(break_start_str)
        break_end = parse_date(break_end_str)

        # Validate break start < end
        if break_start >= break_end:
            errors.append(f"Break '{name}': start date must be before end date")
            continue

        # Validate break falls within semester
        if break_start < semester_start:
            errors.append(f"Break '{name}': starts before semester begins ({start})")
        if break_end > semester_end:
            errors.append(f"Break '{name}': ends after semester ends ({end})")

        parsed_breaks.append({
            "name": name,
            "start": break_start,
            "end": break_end,
        })

    # Check for overlapping breaks
    parsed_breaks.sort(key=lambda x: x["start"])
    for i in range(len(parsed_breaks) - 1):
        current = parsed_breaks[i]
        next_break = parsed_breaks[i + 1]

        if current["end"] >= next_break["start"]:
            errors.append(
                f"Breaks '{current['name']}' and '{next_break['name']}' overlap"
            )

    return errors


def apply_defaults(config: Dict[str, Any]) -> Dict[str, Any]:
    """
    Apply default values for optional fields.

    Args:
        config: Parsed configuration dictionary

    Returns:
        Configuration with defaults applied
    """
    # Apply deployment defaults
    if "deployment" not in config:
        config["deployment"] = {}
    for key, value in DEFAULTS["deployment"].items():
        if key not in config["deployment"]:
            config["deployment"][key] = value

    # Apply progress defaults
    if "progress" not in config:
        config["progress"] = {}
    for key, value in DEFAULTS["progress"].items():
        if key not in config["progress"]:
            config["progress"][key] = value

    # Apply validation defaults
    if "validation" not in config:
        config["validation"] = {}
    for key, value in DEFAULTS["validation"].items():
        if key not in config["validation"]:
            config["validation"][key] = value

    # Apply dates defaults
    if "dates" in config and "breaks" not in config["dates"]:
        config["dates"]["breaks"] = DEFAULTS["dates"]["breaks"]

    return config


def validate_config(config: Dict[str, Any]) -> List[str]:
    """
    Validate configuration structure and values.

    Args:
        config: Parsed configuration dictionary

    Returns:
        List of error messages (empty if valid)
    """
    errors = []

    # Check required top-level sections
    required_sections = ["course", "dates"]
    for section in required_sections:
        if section not in config:
            errors.append(f"Missing required section: '{section}'")

    if errors:
        return errors  # Can't continue without required sections

    # Validate course section
    course = config.get("course", {})
    required_course_fields = ["number", "title", "semester", "year"]
    for field in required_course_fields:
        if field not in course:
            errors.append(f"Missing required field: 'course.{field}'")

    # Validate semester value
    if "semester" in course:
        if course["semester"] not in VALID_SEMESTERS:
            errors.append(
                f"Invalid semester: '{course['semester']}' "
                f"(must be one of: {', '.join(VALID_SEMESTERS)})"
            )

    # Validate year
    if "year" in course:
        year = course["year"]
        if not isinstance(year, int):
            errors.append(f"Invalid year: must be an integer (got {type(year).__name__})")
        elif year < 2000 or year > 2100:
            errors.append(f"Invalid year: {year} (must be between 2000 and 2100)")

    # Validate dates section
    dates = config.get("dates", {})
    required_date_fields = ["start", "end"]
    for field in required_date_fields:
        if field not in dates:
            errors.append(f"Missing required field: 'dates.{field}'")

    if "start" in dates and "end" in dates:
        start = dates["start"]
        end = dates["end"]

        # Validate date formats
        if not validate_date(start):
            errors.append(f"Invalid start date format: '{start}' (expected YYYY-MM-DD)")
        if not validate_date(end):
            errors.append(f"Invalid end date format: '{end}' (expected YYYY-MM-DD)")

        # Validate date order
        if validate_date(start) and validate_date(end):
            start_dt = parse_date(start)
            end_dt = parse_date(end)
            if start_dt >= end_dt:
                errors.append(f"Semester end date must be after start date")

            # Validate breaks if present
            if "breaks" in dates:
                break_errors = validate_breaks(dates["breaks"], start, end)
                errors.extend(break_errors)

    # Validate progress.current_week
    if "progress" in config and "current_week" in config["progress"]:
        current_week = config["progress"]["current_week"]
        if current_week != "auto" and not isinstance(current_week, int):
            errors.append(
                f"Invalid current_week: must be 'auto' or integer "
                f"(got {type(current_week).__name__})"
            )
        if isinstance(current_week, int) and (current_week < 1 or current_week > 52):
            errors.append(f"Invalid current_week: {current_week} (must be between 1 and 52)")

    # Validate validation.strict_mode
    if "validation" in config and "strict_mode" in config["validation"]:
        strict_mode = config["validation"]["strict_mode"]
        if not isinstance(strict_mode, bool):
            errors.append(
                f"Invalid strict_mode: must be boolean "
                f"(got {type(strict_mode).__name__})"
            )

    return errors


def load_teach_config(cwd: str = ".") -> Optional[Dict[str, Any]]:
    """
    Load and validate teaching configuration.

    Finds config file, parses YAML, validates required fields and dates,
    and applies defaults for optional fields.

    Args:
        cwd: Current working directory (default: ".")

    Returns:
        Configuration dictionary with defaults applied, or None if not found/invalid

    Raises:
        ValueError: For critical validation failures (invalid dates, etc.)
    """
    # Find config file
    config_path = get_config_path(cwd)
    if not config_path:
        return None  # No config file found (not an error)

    # Parse YAML
    try:
        with open(config_path, "r") as f:
            config = yaml.safe_load(f)
    except yaml.YAMLError as e:
        print(f"Warning: Malformed YAML in {config_path}: {e}", file=sys.stderr)
        return None
    except Exception as e:
        print(f"Warning: Failed to read {config_path}: {e}", file=sys.stderr)
        return None

    if not isinstance(config, dict):
        print(f"Warning: Config must be a YAML dictionary (got {type(config).__name__})", file=sys.stderr)
        return None

    # Apply defaults
    config = apply_defaults(config)

    # Validate configuration
    errors = validate_config(config)
    if errors:
        error_msg = "\n".join(f"  - {error}" for error in errors)
        raise ValueError(f"Configuration validation failed:\n{error_msg}")

    return config


if __name__ == "__main__":
    """CLI for testing config parser"""
    import json

    config = load_teach_config()
    if config:
        print(json.dumps(config, indent=2, default=str))
    else:
        print("No teaching config found")
        sys.exit(1)
