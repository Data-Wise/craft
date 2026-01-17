"""Teaching content validation utilities.

Validates course content for completeness and readiness to publish:
- Syllabus required sections
- Schedule completeness
- Assignment file existence

Designed for ADHD-friendly, scannable output.
"""

import os
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class ValidationResult:
    """Result of teaching content validation.

    Attributes:
        valid: Overall validation status (no errors)
        errors: Blocking issues that prevent publishing
        warnings: Non-blocking issues to review
        checks: Detailed check results (name → passed)
    """
    valid: bool
    errors: list[str] = field(default_factory=list)
    warnings: list[str] = field(default_factory=list)
    checks: dict[str, bool] = field(default_factory=dict)

    def can_publish(self) -> bool:
        """Returns True if no errors (warnings are OK)."""
        return len(self.errors) == 0

    def format_report(self) -> str:
        """Format ADHD-friendly validation report."""
        lines = []

        # Header
        status = "✅ READY TO PUBLISH" if self.can_publish() else "❌ BLOCKED"
        lines.append(f"\n{'=' * 60}")
        lines.append(f"TEACHING CONTENT VALIDATION: {status}")
        lines.append('=' * 60)

        # Errors (critical)
        if self.errors:
            lines.append("\n🚫 ERRORS (must fix before publishing):")
            for i, error in enumerate(self.errors, 1):
                lines.append(f"  {i}. {error}")

        # Warnings (recommended)
        if self.warnings:
            lines.append("\n⚠️  WARNINGS (recommended to fix):")
            for i, warning in enumerate(self.warnings, 1):
                lines.append(f"  {i}. {warning}")

        # Detailed checks
        if self.checks:
            lines.append("\n📋 DETAILED CHECKS:")
            for name, passed in self.checks.items():
                icon = "✓" if passed else "✗"
                lines.append(f"  [{icon}] {name}")

        # Summary
        lines.append(f"\n{'=' * 60}")
        total_checks = len(self.checks)
        passed_checks = sum(1 for v in self.checks.values() if v)
        lines.append(f"Summary: {passed_checks}/{total_checks} checks passed")

        if self.can_publish():
            lines.append("Status: Ready to publish ✅")
        else:
            lines.append(f"Status: {len(self.errors)} error(s) blocking publish ❌")

        lines.append('=' * 60 + '\n')

        return '\n'.join(lines)


def find_file(cwd: str, patterns: list[str]) -> Optional[Path]:
    """Find first matching file from pattern list.

    Args:
        cwd: Working directory
        patterns: File path patterns to search for

    Returns:
        Path to first found file, or None
    """
    base = Path(cwd)
    for pattern in patterns:
        path = base / pattern
        if path.exists() and path.is_file():
            return path
    return None


def validate_syllabus(cwd: str) -> dict[str, bool]:
    """Validate syllabus contains required sections.

    Checks for essential syllabus sections using flexible heuristics:
    - Grading/assessment information
    - Course policies
    - Learning objectives/outcomes
    - Schedule/calendar

    Args:
        cwd: Course directory path

    Returns:
        Dict mapping section name → found (bool)
    """
    # Find syllabus file
    syllabus_patterns = [
        'syllabus/index.qmd',
        'syllabus.qmd',
        'syllabus/syllabus.qmd',
        'index.qmd',  # Sometimes syllabus is the main page
    ]

    syllabus_path = find_file(cwd, syllabus_patterns)

    # Default result: all sections missing
    sections = {
        'grading': False,
        'policies': False,
        'objectives': False,
        'schedule': False,
    }

    if not syllabus_path:
        return sections

    # Read syllabus content
    try:
        content = syllabus_path.read_text(encoding='utf-8').lower()
    except Exception:
        return sections

    # Check for section patterns (case-insensitive)
    # Use word boundaries and context to avoid false positives
    # For policies: must be a header starting with "polic" or "course polic"
    # Not just any mention of "policy" (like "grading policy")
    patterns = {
        'grading': [r'\bgrading\b', r'\bgrade\b', r'\bassessment\b'],
        'policies': [r'^#{1,4}\s+(course\s+)?polic(y|ies)\b'],  # Header starting with policy/policies
        'objectives': [r'\bobjective', r'\blearning outcome', r'\bgoal'],
        'schedule': [r'\bschedule\b', r'\bcalendar\b', r'\btimeline\b'],
    }

    for section, section_patterns in patterns.items():
        for pattern in section_patterns:
            # For policies, use MULTILINE to match line starts
            flags = re.MULTILINE if section == 'policies' else 0
            if re.search(pattern, content, flags):
                sections[section] = True
                break

    return sections


def validate_schedule(cwd: str) -> dict:
    """Validate schedule completeness.

    Checks that:
    - Schedule file exists
    - All weeks are defined
    - Each week has meaningful content (>20 chars)

    Args:
        cwd: Course directory path

    Returns:
        Dict with keys:
        - total_weeks: Number of weeks found
        - complete_weeks: Number of weeks with content
        - gaps: List of week numbers missing content
    """
    result = {
        'total_weeks': 0,
        'complete_weeks': 0,
        'gaps': [],
    }

    # Find schedule file
    schedule_patterns = [
        'schedule.qmd',
        'schedule/index.qmd',
        'calendar.qmd',
    ]

    schedule_path = find_file(cwd, schedule_patterns)

    if not schedule_path:
        return result

    try:
        content = schedule_path.read_text(encoding='utf-8')
    except Exception:
        return result

    # Find all week sections (flexible patterns)
    # Matches: "## Week 1", "### Week 1:", "Week 1 -", etc.
    week_pattern = re.compile(
        r'^#{1,4}\s*Week\s+(\d+)',
        re.MULTILINE | re.IGNORECASE
    )

    matches = list(week_pattern.finditer(content))

    if not matches:
        return result

    result['total_weeks'] = len(matches)

    # Check content for each week
    for i, match in enumerate(matches):
        week_num = int(match.group(1))
        start_pos = match.end()

        # Find content until next week or end
        if i + 1 < len(matches):
            end_pos = matches[i + 1].start()
        else:
            end_pos = len(content)

        week_content = content[start_pos:end_pos].strip()

        # Week is complete if it has meaningful content (>20 chars)
        if len(week_content) > 20:
            result['complete_weeks'] += 1
        else:
            result['gaps'].append(week_num)

    return result


def validate_assignments(cwd: str) -> dict:
    """Validate assignment files exist.

    Finds assignment references in schedule and checks if files exist.

    Args:
        cwd: Course directory path

    Returns:
        Dict with keys:
        - referenced: List of assignment names found in schedule
        - missing: List of assignment files that don't exist
        - found: List of assignment files that exist
    """
    result = {
        'referenced': [],
        'missing': [],
        'found': [],
    }

    # Find schedule file
    schedule_patterns = [
        'schedule.qmd',
        'schedule/index.qmd',
        'calendar.qmd',
    ]

    schedule_path = find_file(cwd, schedule_patterns)

    if not schedule_path:
        return result

    try:
        content = schedule_path.read_text(encoding='utf-8')
    except Exception:
        return result

    # Find assignment references
    # Matches: "HW 1", "HW1", "Assignment 1", "Homework 1", etc.
    assignment_patterns = [
        re.compile(r'\bHW\s*(\d+)\b', re.IGNORECASE),
        re.compile(r'\bAssignment\s+(\d+)\b', re.IGNORECASE),
        re.compile(r'\bHomework\s+(\d+)\b', re.IGNORECASE),
    ]

    assignment_numbers = set()
    for pattern in assignment_patterns:
        for match in pattern.finditer(content):
            assignment_numbers.add(int(match.group(1)))

    # Check if assignment files exist
    base = Path(cwd)
    assignments_dir = base / 'assignments'

    for num in sorted(assignment_numbers):
        name = f"HW {num}"
        result['referenced'].append(name)

        # Check multiple possible locations
        possible_paths = [
            assignments_dir / f'hw-{num}.qmd',
            assignments_dir / f'hw{num}.qmd',
            assignments_dir / f'hw-{num}' / 'index.qmd',
            assignments_dir / f'assignment-{num}.qmd',
            assignments_dir / f'homework-{num}.qmd',
        ]

        exists = any(p.exists() for p in possible_paths)

        if exists:
            result['found'].append(name)
        else:
            result['missing'].append(name)

    return result


def validate_teaching_content(cwd: str) -> ValidationResult:
    """Run all teaching content validations.

    Combines syllabus, schedule, and assignment validations into
    a single comprehensive result.

    Args:
        cwd: Course directory path

    Returns:
        ValidationResult with errors, warnings, and detailed checks
    """
    result = ValidationResult(valid=True)

    # Validate syllabus
    syllabus_sections = validate_syllabus(cwd)

    required_sections = ['grading', 'policies', 'objectives', 'schedule']
    missing_sections = [s for s in required_sections if not syllabus_sections[s]]

    if missing_sections:
        result.errors.append(
            f"Syllabus missing required sections: {', '.join(missing_sections)}"
        )
        result.valid = False

    for section, found in syllabus_sections.items():
        result.checks[f'Syllabus: {section}'] = found

    # Validate schedule
    schedule_info = validate_schedule(cwd)

    if schedule_info['total_weeks'] == 0:
        result.errors.append("No schedule file found or no weeks defined")
        result.valid = False
        result.checks['Schedule: exists'] = False
    else:
        result.checks['Schedule: exists'] = True

        if schedule_info['gaps']:
            gap_list = ', '.join(str(w) for w in schedule_info['gaps'])
            result.errors.append(
                f"Schedule has incomplete weeks (no content): Week {gap_list}"
            )
            result.valid = False

        result.checks[f"Schedule: {schedule_info['complete_weeks']}/{schedule_info['total_weeks']} weeks complete"] = len(schedule_info['gaps']) == 0

    # Validate assignments
    assignment_info = validate_assignments(cwd)

    if assignment_info['missing']:
        missing_list = ', '.join(assignment_info['missing'])
        result.warnings.append(
            f"Missing assignment files: {missing_list}"
        )

    if assignment_info['referenced']:
        result.checks[f"Assignments: {len(assignment_info['found'])}/{len(assignment_info['referenced'])} found"] = len(assignment_info['missing']) == 0
    else:
        result.checks['Assignments: referenced in schedule'] = False

    return result
