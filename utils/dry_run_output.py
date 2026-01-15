#!/usr/bin/env python3
"""
Dry-Run Output Utility for Craft Commands

Provides standardized formatting for --dry-run previews across all craft commands.
Follows the specification in docs/specs/SPEC-dry-run-feature-2026-01-15.md

Usage:
    from utils.dry_run_output import render_dry_run_preview, RiskLevel

    preview = render_dry_run_preview(
        command_name="Clean Merged Branches",
        actions=[
            "Delete 3 local branches (merged to dev)",
            "Skip feature/wip (uncommitted changes)"
        ],
        warnings=["Branch feature/wip has uncommitted changes"],
        summary="3 branches to delete, 1 skipped",
        risk_level=RiskLevel.CRITICAL
    )
    print(preview)
"""

from dataclasses import dataclass
from enum import Enum
from typing import List, Optional, Dict, Any


class RiskLevel(Enum):
    """Risk level for operations"""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


class OperationType(Enum):
    """Types of operations"""
    CREATE = "create"
    MODIFY = "modify"
    DELETE = "delete"
    EXECUTE = "execute"
    PUBLISH = "publish"


class Severity(Enum):
    """Warning severity levels"""
    INFO = "info"
    WARNING = "warning"
    CRITICAL = "critical"


@dataclass
class Operation:
    """Single operation in execution plan"""
    type: OperationType
    description: str
    details: List[str]
    target: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        return {
            "type": self.type.value,
            "description": self.description,
            "details": self.details,
            "target": self.target,
            "risk_level": self.risk_level.value
        }


@dataclass
class Warning:
    """Warning about uncertain or risky operation"""
    message: str
    severity: Severity = Severity.WARNING
    reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "message": self.message,
            "severity": self.severity.value,
            "reason": self.reason
        }


@dataclass
class OperationPlan:
    """Represents planned operations for dry-run preview"""
    operations: List[Operation]
    warnings: List[Warning]
    summary: Optional[str] = None
    risk_level: RiskLevel = RiskLevel.MEDIUM

    def to_dict(self) -> Dict[str, Any]:
        return {
            "operations": [op.to_dict() for op in self.operations],
            "warnings": [w.to_dict() for w in self.warnings],
            "summary": self.summary,
            "risk_level": self.risk_level.value
        }


def render_dry_run_preview(
    command_name: str,
    actions: List[str],
    warnings: Optional[List[str]] = None,
    summary: Optional[str] = None,
    risk_level: RiskLevel = RiskLevel.MEDIUM,
    width: int = 65
) -> str:
    """
    Render standardized dry-run output with bordered box.

    Args:
        command_name: Name of the command (e.g., "Clean Merged Branches")
        actions: List of high-level operations (3-7 items)
        warnings: Optional list of warning messages
        summary: Optional summary line (e.g., "5 branches to delete, 2 skipped")
        risk_level: Risk level for context (not displayed, for future use)
        width: Width of the output box (default: 65)

    Returns:
        Formatted dry-run output string with bordered box

    Example:
        >>> preview = render_dry_run_preview(
        ...     command_name="Clean Merged Branches",
        ...     actions=[
        ...         "Delete 3 local branches (merged to dev)",
        ...         "Skip feature/wip (uncommitted changes)"
        ...     ],
        ...     warnings=["Branch feature/wip has uncommitted changes"],
        ...     summary="3 branches to delete, 1 skipped"
        ... )
        >>> print(preview)
        ┌─────────────────────────────────────────────────────────────┐
        │ 🔍 DRY RUN: Clean Merged Branches                           │
        ├─────────────────────────────────────────────────────────────┤
        │                                                             │
        │ Delete 3 local branches (merged to dev)                     │
        │ Skip feature/wip (uncommitted changes)                      │
        │                                                             │
        │ ⚠ Warnings:                                                 │
        │   • Branch feature/wip has uncommitted changes              │
        │                                                             │
        │ 📊 Summary: 3 branches to delete, 1 skipped                 │
        │                                                             │
        ├─────────────────────────────────────────────────────────────┤
        │ Run without --dry-run to execute                            │
        └─────────────────────────────────────────────────────────────┘
    """
    lines = []

    # Top border
    lines.append("┌" + "─" * (width - 2) + "┐")

    # Title
    title = f" 🔍 DRY RUN: {command_name} "
    lines.append("│" + title.ljust(width - 2) + "│")

    # Separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Empty line
    lines.append("│" + " " * (width - 2) + "│")

    # Actions
    for action in actions:
        wrapped = _wrap_text(action, width - 4)
        for line in wrapped:
            lines.append("│ " + line.ljust(width - 3) + "│")

    # Warnings section (if any)
    if warnings and len(warnings) > 0:
        lines.append("│" + " " * (width - 2) + "│")
        lines.append("│ ⚠ Warnings:".ljust(width - 1) + "│")
        for warning in warnings:
            wrapped = _wrap_text(f"• {warning}", width - 6)
            for line in wrapped:
                lines.append("│   " + line.ljust(width - 4) + "│")

    # Summary (if provided)
    if summary:
        lines.append("│" + " " * (width - 2) + "│")
        summary_line = f" 📊 Summary: {summary} "
        lines.append("│" + summary_line.ljust(width - 2) + "│")

    # Empty line before footer
    lines.append("│" + " " * (width - 2) + "│")

    # Bottom separator
    lines.append("├" + "─" * (width - 2) + "┤")

    # Footer
    footer = " Run without --dry-run to execute "
    lines.append("│" + footer.ljust(width - 2) + "│")

    # Bottom border
    lines.append("└" + "─" * (width - 2) + "┘")

    return "\n".join(lines)


def _wrap_text(text: str, max_width: int) -> List[str]:
    """
    Wrap text to fit within max_width, preserving words.

    Args:
        text: Text to wrap
        max_width: Maximum width per line

    Returns:
        List of wrapped lines
    """
    if len(text) <= max_width:
        return [text]

    lines = []
    words = text.split()
    current_line = []
    current_length = 0

    for word in words:
        word_length = len(word)
        # +1 for space between words
        if current_length + word_length + len(current_line) <= max_width:
            current_line.append(word)
            current_length += word_length
        else:
            if current_line:
                lines.append(" ".join(current_line))
            current_line = [word]
            current_length = word_length

    if current_line:
        lines.append(" ".join(current_line))

    return lines


def render_simple_preview(
    command_name: str,
    message: str,
    width: int = 65
) -> str:
    """
    Render a simple dry-run preview with just a message.

    Useful for commands that don't have complex operations to preview.

    Args:
        command_name: Name of the command
        message: Single message to display
        width: Width of the output box

    Returns:
        Formatted dry-run output

    Example:
        >>> preview = render_simple_preview(
        ...     "Git Recap",
        ...     "This command only reads git history and displays information. No changes will be made."
        ... )
    """
    return render_dry_run_preview(
        command_name=command_name,
        actions=[message],
        warnings=None,
        summary=None
    )


# Example usage and testing
if __name__ == "__main__":
    # Example 1: Git clean with warnings
    print("Example 1: Git Clean")
    print("=" * 65)
    preview1 = render_dry_run_preview(
        command_name="Clean Merged Branches",
        actions=[
            "✓ Delete 3 local branches (merged to dev):",
            "  - feature/auth-system",
            "  - fix/login-bug",
            "  - refactor/api-cleanup",
            "",
            "⊘ Skip 1 branch:",
            "  - feature/wip (uncommitted changes)"
        ],
        warnings=["Branch feature/wip has uncommitted changes"],
        summary="3 branches to delete, 1 skipped",
        risk_level=RiskLevel.CRITICAL
    )
    print(preview1)
    print("\n")

    # Example 2: CI Generate
    print("Example 2: CI Generate")
    print("=" * 65)
    preview2 = render_dry_run_preview(
        command_name="Generate CI Workflow",
        actions=[
            "✓ Create .github/workflows/ci.yml (~45 lines)",
            "",
            "Configuration:",
            "  - Project type: Python (uv)",
            "  - Test framework: pytest",
            "  - Python versions: 3.9, 3.10, 3.11"
        ],
        warnings=["No existing workflow file"],
        summary="1 file to create",
        risk_level=RiskLevel.MEDIUM
    )
    print(preview2)
    print("\n")

    # Example 3: Simple read-only command
    print("Example 3: Simple Read-Only")
    print("=" * 65)
    preview3 = render_simple_preview(
        "Git Recap",
        "This command only reads git history. No changes will be made."
    )
    print(preview3)
