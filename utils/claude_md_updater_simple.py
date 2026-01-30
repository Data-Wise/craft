#!/usr/bin/env python3
"""
CLAUDE.md Simple Updater - Core Metrics Only

Focuses on updating core metrics: version, command/skill/agent counts, test count, docs %.
Individual command tracking deferred to Phase 2.

Version: 1.0.0 (Phase 1 - Simplified)
Author: Craft Plugin
"""

import re
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class MetricChange:
    """Represents a metric change."""
    name: str
    before: str
    after: str
    pattern: str  # Regex pattern to find and replace

    @property
    def description(self) -> str:
        return f"{self.name}: {self.before} → {self.after}"


class SimpleCLAUDEMDUpdater:
    """Simple updater focusing on core metrics."""

    def __init__(self, claude_md_path: Path, project_info):
        self.path = claude_md_path
        self.project_info = project_info
        self.content = claude_md_path.read_text() if claude_md_path.exists() else ""

    def detect_changes(self) -> List[MetricChange]:
        """Detect metric changes.

        Returns:
            List of MetricChange objects
        """
        changes = []

        # 1. Version
        if change := self._check_version():
            changes.append(change)

        # 2. Command count (for craft plugins)
        if self.project_info.type == "craft-plugin":
            if change := self._check_command_count():
                changes.append(change)

            if change := self._check_skill_count():
                changes.append(change)

            if change := self._check_agent_count():
                changes.append(change)

            if change := self._check_test_count():
                changes.append(change)

        # 3. Documentation status (from .STATUS)
        if change := self._check_docs_percent():
            changes.append(change)

        return changes

    def _check_version(self) -> Optional[MetricChange]:
        """Check version mismatch."""
        pattern = r'\*\*Current Version:\*\* v([0-9.]+)'
        match = re.search(pattern, self.content)

        if not match:
            return None

        current = match.group(1)
        actual = self.project_info.version

        if current != actual:
            return MetricChange(
                name="Version",
                before=f"v{current}",
                after=f"v{actual}",
                pattern=r'(\*\*Current Version:\*\* v)[0-9.]+'
            )

        return None

    def _check_command_count(self) -> Optional[MetricChange]:
        """Check command count."""
        pattern = r'\*\*(\d+) commands\*\*'
        match = re.search(pattern, self.content)

        if not match:
            return None

        current = int(match.group(1))
        actual = len(self.project_info.commands)

        if current != actual:
            return MetricChange(
                name="Commands",
                before=f"{current} commands",
                after=f"{actual} commands",
                pattern=r'(\*\*)\d+( commands\*\*)'
            )

        return None

    def _check_skill_count(self) -> Optional[MetricChange]:
        """Check skill count."""
        pattern = r'\*\*(\d+) skills\*\*'
        match = re.search(pattern, self.content)

        if not match:
            return None

        current = int(match.group(1))
        actual = len(self.project_info.skills)

        if current != actual:
            return MetricChange(
                name="Skills",
                before=f"{current} skills",
                after=f"{actual} skills",
                pattern=r'(\*\*)\d+( skills\*\*)'
            )

        return None

    def _check_agent_count(self) -> Optional[MetricChange]:
        """Check agent count."""
        pattern = r'\*\*(\d+) agents\*\*'
        match = re.search(pattern, self.content)

        if not match:
            return None

        current = int(match.group(1))
        actual = len(self.project_info.agents)

        if current != actual:
            return MetricChange(
                name="Agents",
                before=f"{current} agents",
                after=f"{actual} agents",
                pattern=r'(\*\*)\d+( agents\*\*)'
            )

        return None

    def _check_test_count(self) -> Optional[MetricChange]:
        """Check test count."""
        pattern = r'\*\*Tests:\*\* (\d+)'
        match = re.search(pattern, self.content)

        if not match:
            return None

        current = int(match.group(1))
        actual = self.project_info.test_count

        if current != actual:
            return MetricChange(
                name="Tests",
                before=f"{current} passing",
                after=f"{actual} passing",
                pattern=r'(\*\*Tests:\*\* )\d+'
            )

        return None

    def _check_docs_percent(self) -> Optional[MetricChange]:
        """Check documentation percentage."""
        status_file = self.path.parent / ".STATUS"
        if not status_file.exists():
            return None

        # Parse .STATUS
        content = status_file.read_text()
        progress_match = re.search(r'progress:\s*(\d+)', content)

        if not progress_match:
            return None

        actual = int(progress_match.group(1))

        # Extract from CLAUDE.md
        pattern = r'\*\*Documentation Status:\*\* (\d+)%'
        match = re.search(pattern, self.content)

        if match:
            current = int(match.group(1))
            if current != actual:
                return MetricChange(
                    name="Documentation",
                    before=f"{current}%",
                    after=f"{actual}%",
                    pattern=r'(\*\*Documentation Status:\*\* )\d+%'
                )

        return None

    def apply_changes(self, changes: List[MetricChange], dry_run: bool = False) -> str:
        """Apply changes.

        Args:
            changes: List of changes to apply
            dry_run: If True, return updated content without writing

        Returns:
            Updated content
        """
        if not changes:
            return self.content

        updated = self.content

        for change in changes:
            # Use lambda to avoid backreference issues with numbers
            if change.name == "Version":
                version_num = change.after.replace("v", "")
                updated = re.sub(
                    change.pattern,
                    lambda m: m.group(1) + version_num,
                    updated
                )
            elif change.name in ["Commands", "Skills", "Agents"]:
                count = change.after.split()[0]
                updated = re.sub(
                    change.pattern,
                    lambda m: m.group(1) + count + m.group(2),
                    updated
                )
            elif change.name == "Tests":
                count = change.after.split()[0]
                updated = re.sub(
                    change.pattern,
                    lambda m: m.group(1) + count,
                    updated
                )
            elif change.name == "Documentation":
                percent = change.after.replace("%", "")
                updated = re.sub(
                    change.pattern,
                    lambda m: m.group(1) + percent + '%',
                    updated
                )

        if not dry_run:
            self.path.write_text(updated)

        return updated

    def generate_preview(self, changes: List[MetricChange]) -> str:
        """Generate preview box."""
        if not changes:
            return "✅ No changes detected. CLAUDE.md is up to date."

        lines = [
            "╭─ CLAUDE.md Update Plan ──────────────────────────────────╮",
            f"│ Project: {self.project_info.name} ({self.project_info.type})",
            f"│ Version Source: {self.project_info.version_source}",
            "├──────────────────────────────────────────────────────────┤",
            "│                                                          │",
            "│ Changes Detected:                                        │",
            "│                                                          │",
        ]

        for i, change in enumerate(changes, 1):
            lines.append(f"│ {i}. {change.name}")
            lines.append(f"│    Current: {change.before}")
            lines.append(f"│    Actual:  {change.after}")
            lines.append("│                                                          │")

        lines.extend([
            "├──────────────────────────────────────────────────────────┤",
            "│ ? Proceed with these updates?                            │",
            "│   > Yes - Apply all changes (Recommended)                │",
            "│     Dry run - Show preview without applying              │",
            "│     Cancel - Exit without changes                        │",
            "╰──────────────────────────────────────────────────────────╯",
        ])

        return "\n".join(lines)

    def generate_summary(self, changes: List[MetricChange]) -> str:
        """Generate summary after applying."""
        lines = [
            "✅ CLAUDE.MD UPDATED",
            "",
            "Applied:",
        ]

        for change in changes:
            lines.append(f"  • {change.description}")

        lines.extend([
            "",
            "Next steps:",
            "  1. Review: git diff CLAUDE.md",
            '  2. Commit: git add CLAUDE.md && git commit -m "docs: update CLAUDE.md"',
        ])

        return "\n".join(lines)


def update_claude_md(dry_run: bool = False) -> Tuple[List[MetricChange], str]:
    """Main update function.

    Args:
        dry_run: Preview only

    Returns:
        Tuple of (changes, message)
    """
    # Import here to avoid circular dependency issues
    sys.path.insert(0, str(Path(__file__).parent.parent))
    from utils.claude_md_detector import detect_project

    project_path = Path.cwd()
    claude_md_path = project_path / "CLAUDE.md"

    if not claude_md_path.exists():
        return [], "❌ CLAUDE.md not found. Use /craft:docs:claude-md:scaffold to create."

    # Detect project
    project_info = detect_project(project_path)
    if not project_info:
        return [], "❌ Could not detect project type."

    # Create updater
    updater = SimpleCLAUDEMDUpdater(claude_md_path, project_info)

    # Detect changes
    changes = updater.detect_changes()

    if not changes:
        return [], "✅ No changes detected. CLAUDE.md is up to date."

    # Generate preview
    preview = updater.generate_preview(changes)

    if dry_run:
        message = f"{preview}\n\n(Dry run - no changes applied. Remove --dry-run to apply)"
        return changes, message

    # Apply changes
    updater.apply_changes(changes, dry_run=False)

    # Generate summary
    summary = updater.generate_summary(changes)

    return changes, summary


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Update CLAUDE.md core metrics")
    parser.add_argument("--dry-run", "-n", action="store_true", help="Preview only")
    args = parser.parse_args()

    changes, message = update_claude_md(dry_run=args.dry_run)
    print(message)

    sys.exit(0 if changes or "up to date" in message.lower() else 1)
