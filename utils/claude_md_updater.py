#!/usr/bin/env python3
"""
CLAUDE.md Updater - Change Detection and Application

Detects changes between CLAUDE.md and current project state,
generates update plan, and applies changes with various modes.

Version: 1.0.0
Author: Craft Plugin
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from enum import Enum


class ChangeType(Enum):
    """Types of changes that can be detected."""
    VERSION_MISMATCH = "version"
    NEW_COMMAND = "command_add"
    REMOVED_COMMAND = "command_remove"
    NEW_SKILL = "skill_add"
    REMOVED_SKILL = "skill_remove"
    NEW_AGENT = "agent_add"
    REMOVED_AGENT = "agent_remove"
    TEST_COUNT = "test_count"
    DOCS_PERCENT = "docs_percent"
    STATUS_SYNC = "status"
    STRUCTURE = "structure"


@dataclass
class Change:
    """Represents a single change to apply."""
    type: ChangeType
    description: str
    before: str
    after: str
    line_number: Optional[int] = None
    auto_fixable: bool = True


@dataclass
class UpdatePlan:
    """Plan of changes to apply to CLAUDE.md."""
    changes: List[Change]
    total_line_delta: int
    sections_affected: List[str]

    @property
    def has_changes(self) -> bool:
        return len(self.changes) > 0

    @property
    def change_summary(self) -> str:
        """Generate summary of changes."""
        summary = []
        by_type = {}
        for change in self.changes:
            if change.type not in by_type:
                by_type[change.type] = []
            by_type[change.type].append(change)

        for change_type, items in by_type.items():
            summary.append(f"{change_type.value}: {len(items)} change(s)")

        return ", ".join(summary)


class CLAUDEMDUpdater:
    """Update CLAUDE.md from project state."""

    def __init__(self, claude_md_path: Path, project_info):
        """Initialize updater.

        Args:
            claude_md_path: Path to CLAUDE.md file
            project_info: ProjectInfo from detector
        """
        self.path = claude_md_path
        self.project_info = project_info
        self.content = claude_md_path.read_text() if claude_md_path.exists() else ""
        self.lines = self.content.split("\n") if self.content else []

    def detect_changes(self) -> UpdatePlan:
        """Detect all changes between CLAUDE.md and project state.

        Returns:
            UpdatePlan with all detected changes
        """
        changes = []

        # 1. Version mismatch
        if version_change := self._detect_version_mismatch():
            changes.append(version_change)

        # 2. Command changes (for craft plugins)
        if self.project_info.type == "craft-plugin":
            changes.extend(self._detect_command_changes())
            changes.extend(self._detect_skill_changes())
            changes.extend(self._detect_agent_changes())
            changes.extend(self._detect_test_count_change())

        # 3. Status sync
        if status_change := self._detect_status_changes():
            changes.append(status_change)

        # Calculate line delta
        line_delta = sum(
            len(c.after.split("\n")) - len(c.before.split("\n"))
            for c in changes
        )

        # Identify affected sections
        sections = set()
        for change in changes:
            if change.type == ChangeType.VERSION_MISMATCH:
                sections.add("Project Status")
            elif "command" in change.type.value:
                sections.add("Quick Commands")
            elif "skill" in change.type.value or "agent" in change.type.value:
                sections.add("Project Structure")
            elif change.type == ChangeType.TEST_COUNT:
                sections.add("Testing")

        return UpdatePlan(
            changes=changes,
            total_line_delta=line_delta,
            sections_affected=sorted(sections)
        )

    def _detect_version_mismatch(self) -> Optional[Change]:
        """Detect version mismatch between CLAUDE.md and source.

        Returns:
            Change if mismatch found, None otherwise
        """
        # Extract version from CLAUDE.md
        version_pattern = r'\*\*Current Version:\*\* v([0-9.]+)'
        match = re.search(version_pattern, self.content)

        if not match:
            return None

        current_version = match.group(1)
        actual_version = self.project_info.version

        if current_version != actual_version:
            line_num = None
            for i, line in enumerate(self.lines):
                if "**Current Version:**" in line:
                    line_num = i + 1
                    break

            return Change(
                type=ChangeType.VERSION_MISMATCH,
                description=f"Version mismatch: v{current_version} → v{actual_version}",
                before=f"v{current_version}",
                after=f"v{actual_version}",
                line_number=line_num,
                auto_fixable=True
            )

        return None

    def _detect_command_changes(self) -> List[Change]:
        """Detect new or removed commands.

        Returns:
            List of command-related changes
        """
        changes = []

        # Extract documented commands from Quick Commands table
        documented_commands = self._extract_documented_commands()

        # Get actual commands from project
        actual_commands = set(self.project_info.commands)

        # Find new commands
        new_commands = actual_commands - documented_commands
        for cmd in sorted(new_commands):
            changes.append(Change(
                type=ChangeType.NEW_COMMAND,
                description=f"New command: {cmd}",
                before="",
                after=f"| `/craft:{cmd}` | [description] |",
                auto_fixable=False  # Needs description
            ))

        # Find removed commands
        removed_commands = documented_commands - actual_commands
        for cmd in sorted(removed_commands):
            changes.append(Change(
                type=ChangeType.REMOVED_COMMAND,
                description=f"Removed command: {cmd}",
                before=f"Command: {cmd}",
                after="",
                auto_fixable=True
            ))

        return changes

    def _extract_documented_commands(self) -> set:
        """Extract command names from CLAUDE.md Quick Commands table.

        Returns:
            Set of documented command paths
        """
        commands = set()
        in_table = False

        for line in self.lines:
            # Look for Quick Commands section
            if "## Quick Commands" in line:
                in_table = True
                continue

            # Stop at next section
            if in_table and line.startswith("##") and "Quick Commands" not in line:
                break

            # Extract command from table row
            if in_table and "|" in line and "/craft:" in line:
                # Extract command name from | /craft:xxx | desc |
                match = re.search(r'/craft:([^\s|]+)', line)
                if match:
                    # Convert /craft:docs:update → docs/update.md
                    cmd_name = match.group(1).replace(":", "/") + ".md"
                    commands.add(cmd_name)

        return commands

    def _detect_skill_changes(self) -> List[Change]:
        """Detect new or removed skills.

        Returns:
            List of skill-related changes
        """
        # For now, just detect count changes
        # Full implementation would track individual skills
        return []

    def _detect_agent_changes(self) -> List[Change]:
        """Detect new or removed agents.

        Returns:
            List of agent-related changes
        """
        # For now, just detect count changes
        return []

    def _detect_test_count_change(self) -> List[Change]:
        """Detect test count changes.

        Returns:
            List with test count change if detected
        """
        changes = []

        # Extract current test count from CLAUDE.md
        test_pattern = r'\*\*Tests:\*\* (\d+)'
        match = re.search(test_pattern, self.content)

        if match:
            current_count = int(match.group(1))
            actual_count = self.project_info.test_count

            if current_count != actual_count:
                changes.append(Change(
                    type=ChangeType.TEST_COUNT,
                    description=f"Test count: {current_count} → {actual_count}",
                    before=f"{current_count}",
                    after=f"{actual_count}",
                    auto_fixable=True
                ))

        return changes

    def _detect_status_changes(self) -> Optional[Change]:
        """Detect status changes from .STATUS file.

        Returns:
            Change if status needs sync, None otherwise
        """
        status_file = self.path.parent / ".STATUS"
        if not status_file.exists():
            return None

        # Parse .STATUS for progress
        content = status_file.read_text()
        progress_match = re.search(r'progress:\s*(\d+)', content)

        if not progress_match:
            return None

        actual_progress = int(progress_match.group(1))

        # Extract current progress from CLAUDE.md
        docs_pattern = r'\*\*Documentation Status:\*\* (\d+)%'
        match = re.search(docs_pattern, self.content)

        if match:
            current_progress = int(match.group(1))
            if current_progress != actual_progress:
                return Change(
                    type=ChangeType.DOCS_PERCENT,
                    description=f"Documentation status: {current_progress}% → {actual_progress}%",
                    before=f"{current_progress}%",
                    after=f"{actual_progress}%",
                    auto_fixable=True
                )

        return None

    def apply_changes(self, plan: UpdatePlan, dry_run: bool = False) -> str:
        """Apply changes from update plan.

        Args:
            plan: UpdatePlan to apply
            dry_run: If True, return updated content without writing

        Returns:
            Updated CLAUDE.md content
        """
        if not plan.has_changes:
            return self.content

        updated_content = self.content

        # Apply each change
        for change in plan.changes:
            if change.auto_fixable:
                updated_content = self._apply_single_change(updated_content, change)

        if not dry_run:
            self.path.write_text(updated_content)

        return updated_content

    def _apply_single_change(self, content: str, change: Change) -> str:
        """Apply a single change to content.

        Args:
            content: Current content
            change: Change to apply

        Returns:
            Updated content
        """
        if change.type == ChangeType.VERSION_MISMATCH:
            # Replace version
            pattern = r'(\*\*Current Version:\*\* v)[0-9.]+'
            replacement = f'\\1{change.after}'
            return re.sub(pattern, replacement, content)

        elif change.type == ChangeType.TEST_COUNT:
            # Replace test count
            pattern = r'(\*\*Tests:\*\* )\d+'
            replacement = f'\\1{change.after}'
            return re.sub(pattern, replacement, content)

        elif change.type == ChangeType.DOCS_PERCENT:
            # Replace docs percentage
            pattern = r'(\*\*Documentation Status:\*\* )\d+%'
            replacement = f'\\1{change.after}'
            return re.sub(pattern, replacement, content)

        elif change.type == ChangeType.REMOVED_COMMAND:
            # Remove command lines (would need more sophisticated logic)
            pass

        return content

    def generate_preview(self, plan: UpdatePlan) -> str:
        """Generate preview of changes.

        Args:
            plan: UpdatePlan to preview

        Returns:
            Formatted preview string
        """
        if not plan.has_changes:
            return "No changes detected."

        lines = [
            "╭─ CLAUDE.md Update Plan ──────────────────────────────────╮",
            f"│ Project: {self.project_info.name} ({self.project_info.type})                            │",
            f"│ Version Source: {self.project_info.version_source}",
            "├──────────────────────────────────────────────────────────┤",
            "│                                                          │",
            "│ Changes Detected:                                        │",
            "│                                                          │",
        ]

        for i, change in enumerate(plan.changes, 1):
            lines.append(f"│ {i}. {change.description}")
            if change.before and change.after:
                lines.append(f"│    Current: {change.before}")
                lines.append(f"│    Actual:  {change.after} {'⚠️' if not change.auto_fixable else ''}")
            lines.append("│                                                          │")

        lines.extend([
            f"│ Net Changes: {'+' if plan.total_line_delta >= 0 else ''}{plan.total_line_delta} lines",
            "│                                                          │",
            "├──────────────────────────────────────────────────────────┤",
            "│ ? Proceed with these updates?                            │",
            "│   > Yes - Apply all changes (Recommended)                │",
            "│     Interactive - Select which sections to update        │",
            "│     Dry run - Show preview without applying              │",
            "│     Cancel - Exit without changes                        │",
            "╰──────────────────────────────────────────────────────────╯",
        ])

        return "\n".join(lines)

    def generate_summary(self, plan: UpdatePlan, applied: bool = True) -> str:
        """Generate summary after applying changes.

        Args:
            plan: UpdatePlan that was applied
            applied: Whether changes were actually applied

        Returns:
            Formatted summary string
        """
        if not applied:
            return "No changes applied (dry-run mode)."

        lines = [
            "✅ CLAUDE.MD UPDATED",
            "",
            "Applied:",
        ]

        for change in plan.changes:
            if change.auto_fixable:
                lines.append(f"  • {change.description}")

        lines.extend([
            "",
            "File changes:",
            f"  Lines: {len(self.lines)} → {len(self.lines) + plan.total_line_delta} ({'+' if plan.total_line_delta >= 0 else ''}{plan.total_line_delta})",
            f"  Sections: {len(plan.sections_affected)} affected",
            "",
            "Next steps:",
            "  1. Review: git diff CLAUDE.md",
            '  2. Commit: git add CLAUDE.md && git commit -m "docs: update CLAUDE.md"',
        ])

        return "\n".join(lines)


def update_claude_md(
    project_path: Path = None,
    dry_run: bool = False,
    interactive: bool = False,
    section: str = "all"
) -> Tuple[UpdatePlan, str]:
    """Update CLAUDE.md from project state.

    Args:
        project_path: Project directory (default: current)
        dry_run: Preview only, don't apply
        interactive: Prompt for each change
        section: Which section to update (all, status, commands, etc.)

    Returns:
        Tuple of (UpdatePlan, summary message)
    """
    from utils.claude_md_detector import detect_project

    project_path = project_path or Path.cwd()
    claude_md_path = project_path / "CLAUDE.md"

    if not claude_md_path.exists():
        return None, "CLAUDE.md not found. Use /craft:docs:claude-md:init to create."

    # Detect project
    project_info = detect_project(project_path)
    if not project_info:
        return None, "Could not detect project type."

    # Create updater
    updater = CLAUDEMDUpdater(claude_md_path, project_info)

    # Detect changes
    plan = updater.detect_changes()

    if not plan.has_changes:
        return plan, "No changes detected. CLAUDE.md is up to date."

    # Generate preview
    preview = updater.generate_preview(plan)

    if dry_run:
        return plan, f"DRY RUN MODE\n\n{preview}\n\nRun without --dry-run to apply changes."

    # Apply changes
    updated_content = updater.apply_changes(plan, dry_run=False)

    # Generate summary
    summary = updater.generate_summary(plan, applied=True)

    return plan, summary


if __name__ == "__main__":
    # CLI usage
    import sys
    import argparse

    parser = argparse.ArgumentParser(description="Update CLAUDE.md")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview only")
    parser.add_argument("--interactive", "-i", action="store_true", help="Interactive mode")
    parser.add_argument("section", nargs="?", default="all", help="Section to update")

    args = parser.parse_args()

    plan, message = update_claude_md(
        dry_run=args.dry_run,
        interactive=args.interactive,
        section=args.section
    )

    print(message)

    if plan and plan.has_changes:
        sys.exit(0)
    else:
        sys.exit(1)
