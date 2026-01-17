#!/usr/bin/env python3
"""
Teaching Mode Detection Utility for Craft Commands

Detects whether a project is in teaching mode using multiple strategies with
priority-based fallback. Used by workflow commands to determine context.

Detection Priority:
    1. Config file (.flow/teach-config.yml)
    2. Metadata (_quarto.yml teaching: true)
    3. Project structure (syllabus/ + schedule.qmd)

Usage:
    from utils.detect_teaching_mode import detect_teaching_mode

    is_teaching, method = detect_teaching_mode()
    if is_teaching:
        print(f"Teaching mode detected via: {method}")
    else:
        print("Not in teaching mode")

    # Or with custom directory
    is_teaching, method = detect_teaching_mode("/path/to/project")
"""

import os
from pathlib import Path
from typing import Tuple, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False


def detect_teaching_mode(cwd: str = ".") -> Tuple[bool, Optional[str]]:
    """
    Detect if current project is in teaching mode.

    Uses a priority-based detection system:
    1. Config file: Check for .flow/teach-config.yml
    2. Metadata: Check _quarto.yml for teaching: true
    3. Structure: Check for syllabus/ (or syllabus.qmd) AND schedule.qmd

    Args:
        cwd: Working directory to check (default: current directory)

    Returns:
        Tuple of (is_teaching: bool, detection_method: str | None)
        - is_teaching: True if teaching mode detected
        - detection_method: One of "config", "metadata", "structure", or None

    Examples:
        >>> # Project with .flow/teach-config.yml
        >>> is_teaching, method = detect_teaching_mode("/path/to/course")
        >>> print(is_teaching, method)
        True config

        >>> # Project with _quarto.yml teaching: true
        >>> is_teaching, method = detect_teaching_mode("/path/to/course")
        >>> print(is_teaching, method)
        True metadata

        >>> # Project with syllabus/ and schedule.qmd
        >>> is_teaching, method = detect_teaching_mode("/path/to/course")
        >>> print(is_teaching, method)
        True structure

        >>> # Non-teaching project
        >>> is_teaching, method = detect_teaching_mode("/path/to/research")
        >>> print(is_teaching, method)
        False None
    """
    project_path = Path(cwd).resolve()

    # Priority 1: Check for .flow/teach-config.yml
    config_file = project_path / ".flow" / "teach-config.yml"
    if config_file.exists():
        return (True, "config")

    # Priority 2: Check _quarto.yml for teaching: true
    quarto_file = project_path / "_quarto.yml"
    if quarto_file.exists():
        if _check_quarto_metadata(quarto_file):
            return (True, "metadata")

    # Priority 3: Check project structure
    if _check_project_structure(project_path):
        return (True, "structure")

    return (False, None)


def _check_quarto_metadata(quarto_file: Path) -> bool:
    """
    Check if _quarto.yml contains teaching: true.

    Args:
        quarto_file: Path to _quarto.yml file

    Returns:
        True if teaching: true is found, False otherwise
    """
    if not YAML_AVAILABLE:
        # Fallback: Simple text search if PyYAML not available
        try:
            content = quarto_file.read_text()
            # Look for "teaching: true" (with or without quotes)
            return "teaching:" in content and "true" in content.lower()
        except Exception:
            return False

    try:
        with open(quarto_file, 'r') as f:
            data = yaml.safe_load(f)
            if data and isinstance(data, dict):
                return data.get('teaching', False) is True
    except Exception:
        return False

    return False


def _check_project_structure(project_path: Path) -> bool:
    """
    Check if project has teaching structure.

    Requires BOTH:
    - syllabus/ directory OR syllabus.qmd file
    - schedule.qmd file

    Args:
        project_path: Path to project directory

    Returns:
        True if both conditions are met, False otherwise
    """
    # Check for syllabus/ directory or syllabus.qmd file
    has_syllabus = (
        (project_path / "syllabus").is_dir() or
        (project_path / "syllabus.qmd").is_file()
    )

    # Check for schedule.qmd file
    has_schedule = (project_path / "schedule.qmd").is_file()

    return has_syllabus and has_schedule


# Example usage and testing
if __name__ == "__main__":
    import sys

    # Test current directory
    is_teaching, method = detect_teaching_mode()
    print(f"Current directory:")
    print(f"  Teaching mode: {is_teaching}")
    print(f"  Detection method: {method}")

    # Test with command line argument
    if len(sys.argv) > 1:
        test_path = sys.argv[1]
        is_teaching, method = detect_teaching_mode(test_path)
        print(f"\nTest directory: {test_path}")
        print(f"  Teaching mode: {is_teaching}")
        print(f"  Detection method: {method}")
