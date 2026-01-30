#!/usr/bin/env python3
"""
CLAUDE.md Section Editor

Parses CLAUDE.md into sections for interactive editing.

Version: 1.0.0
Author: Craft Plugin
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Tuple


@dataclass
class Section:
    """Represents a section in CLAUDE.md."""
    name: str          # Section name
    start_line: int    # Starting line number (0-indexed)
    end_line: int      # Ending line number (exclusive)
    content: str       # Section content
    level: int         # Header level (1 for #, 2 for ##, etc.)


class SectionParser:
    """Parses CLAUDE.md into editable sections."""

    def __init__(self, claude_md_path: Path):
        """Initialize parser.

        Args:
            claude_md_path: Path to CLAUDE.md file
        """
        self.path = claude_md_path
        self.content = claude_md_path.read_text()
        self.lines = self.content.split("\n")

    def parse_sections(self) -> List[Section]:
        """Parse CLAUDE.md into sections.

        Returns:
            List of Section objects
        """
        sections = []
        current_section = None
        current_start = 0

        for i, line in enumerate(self.lines):
            # Detect headers
            header_match = re.match(r'^(#{1,6})\s+(.+)$', line)

            if header_match:
                # Save previous section
                if current_section is not None:
                    sections.append(Section(
                        name=current_section["name"],
                        start_line=current_section["start"],
                        end_line=i,
                        content="\n".join(self.lines[current_section["start"]:i]),
                        level=current_section["level"]
                    ))

                # Start new section
                level = len(header_match.group(1))
                name = header_match.group(2).strip()

                current_section = {
                    "name": name,
                    "start": i,
                    "level": level
                }

        # Add final section
        if current_section is not None:
            sections.append(Section(
                name=current_section["name"],
                start_line=current_section["start"],
                end_line=len(self.lines),
                content="\n".join(self.lines[current_section["start"]:]),
                level=current_section["level"]
            ))

        return sections

    def get_section(self, name: str) -> Optional[Section]:
        """Get section by name (case-insensitive).

        Args:
            name: Section name to find

        Returns:
            Section if found, None otherwise
        """
        sections = self.parse_sections()
        name_lower = name.lower()

        for section in sections:
            if section.name.lower() == name_lower:
                return section

        return None

    def find_section_fuzzy(self, name: str) -> Optional[Section]:
        """Find section by partial/fuzzy name match.

        Args:
            name: Partial section name

        Returns:
            Best matching section, or None
        """
        sections = self.parse_sections()
        name_lower = name.lower()

        # Try exact match first
        for section in sections:
            if section.name.lower() == name_lower:
                return section

        # Try contains match
        for section in sections:
            if name_lower in section.name.lower():
                return section

        return None


class SectionEditor:
    """Handles section editing operations."""

    def __init__(self, claude_md_path: Path):
        """Initialize editor.

        Args:
            claude_md_path: Path to CLAUDE.md file
        """
        self.path = claude_md_path
        self.parser = SectionParser(claude_md_path)

    def replace_section(self, section_name: str, new_content: str) -> bool:
        """Replace section content.

        Args:
            section_name: Name of section to replace
            new_content: New content for section

        Returns:
            True if successful, False otherwise
        """
        section = self.parser.get_section(section_name)
        if not section:
            return False

        # Read current file
        lines = self.path.read_text().split("\n")

        # Replace section lines
        new_lines = lines[:section.start_line] + new_content.split("\n") + lines[section.end_line:]

        # Write back
        self.path.write_text("\n".join(new_lines))

        return True

    def delete_section(self, section_name: str) -> bool:
        """Delete section.

        Args:
            section_name: Name of section to delete

        Returns:
            True if successful, False otherwise
        """
        section = self.parser.get_section(section_name)
        if not section:
            return False

        # Read current file
        lines = self.path.read_text().split("\n")

        # Remove section lines
        new_lines = lines[:section.start_line] + lines[section.end_line:]

        # Write back
        self.path.write_text("\n".join(new_lines))

        return True

    def preview_change(self, section_name: str, new_content: str) -> Tuple[str, str]:
        """Preview section change.

        Args:
            section_name: Name of section to change
            new_content: New content for section

        Returns:
            Tuple of (before_content, after_content)
        """
        section = self.parser.get_section(section_name)
        if not section:
            return ("", "")

        before = section.content
        after = new_content

        return (before, after)

    def backup(self) -> Path:
        """Create backup of CLAUDE.md.

        Returns:
            Path to backup file
        """
        backup_path = self.path.parent / ".CLAUDE.md.bak"
        backup_path.write_text(self.path.read_text())
        return backup_path

    def restore_backup(self) -> bool:
        """Restore from backup.

        Returns:
            True if successful, False if no backup exists
        """
        backup_path = self.path.parent / ".CLAUDE.md.bak"
        if not backup_path.exists():
            return False

        self.path.write_text(backup_path.read_text())
        return True


def format_section_list(sections: List[Section]) -> str:
    """Format sections as numbered list.

    Args:
        sections: List of Section objects

    Returns:
        Formatted string with numbered sections
    """
    lines = []
    for i, section in enumerate(sections, 1):
        line_range = f"lines {section.start_line+1}-{section.end_line}"
        lines.append(f"  {i}. {section.name} ({line_range})")

    return "\n".join(lines)


def get_section_diff(before: str, after: str) -> str:
    """Generate unified diff for section change.

    Args:
        before: Before content
        after: After content

    Returns:
        Unified diff string
    """
    import difflib

    before_lines = before.split("\n")
    after_lines = after.split("\n")

    diff = difflib.unified_diff(
        before_lines,
        after_lines,
        fromfile="BEFORE",
        tofile="AFTER",
        lineterm=""
    )

    return "\n".join(diff)


def calculate_change_stats(before: str, after: str) -> dict:
    """Calculate change statistics.

    Args:
        before: Before content
        after: After content

    Returns:
        Dictionary with change stats
    """
    before_lines = before.split("\n")
    after_lines = after.split("\n")

    before_count = len(before_lines)
    after_count = len(after_lines)
    diff = after_count - before_count

    return {
        "before_lines": before_count,
        "after_lines": after_count,
        "diff_lines": diff,
        "diff_percent": round((diff / before_count * 100) if before_count > 0 else 0, 1)
    }
