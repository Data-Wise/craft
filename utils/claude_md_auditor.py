#!/usr/bin/env python3
"""
CLAUDE.md Auditor

Validates CLAUDE.md files for:
- Version sync with source files
- Command coverage (missing/stale)
- Broken internal links
- Required sections
- Status file alignment

Version: 1.0.0
Author: Craft Plugin
"""

import re
import sys
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Optional, Set

# Import project detector - handle both module and script usage
try:
    from .claude_md_detector import CLAUDEMDDetector
except ImportError:
    from claude_md_detector import CLAUDEMDDetector


class Severity(Enum):
    """Issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """Validation issue found in CLAUDE.md."""
    severity: Severity
    category: str
    message: str
    line_number: Optional[int] = None
    fixable: bool = False
    fix_method: Optional[str] = None

    def __str__(self):
        """Format issue for display."""
        severity_icon = {
            Severity.ERROR: "🔴",
            Severity.WARNING: "⚠️ ",
            Severity.INFO: "📝"
        }
        icon = severity_icon[self.severity]
        line_info = f"Line {self.line_number}: " if self.line_number else ""
        return f"{icon} {line_info}{self.message}"


class CLAUDEMDAuditor:
    """Auditor for CLAUDE.md files."""

    def __init__(self, claude_md_path: Path):
        """Initialize auditor.

        Args:
            claude_md_path: Path to CLAUDE.md file
        """
        self.path = Path(claude_md_path)
        self.project_root = self.path.parent
        self.content = ""
        self.lines = []

        if self.path.exists():
            self.content = self.path.read_text()
            self.lines = self.content.split("\n")

    def audit(self) -> List[Issue]:
        """Run all validation checks.

        Returns:
            List of issues found
        """
        issues = []

        # Run all checks
        issues.extend(self.check_version_sync())
        issues.extend(self.check_command_coverage())
        issues.extend(self.check_broken_links())
        issues.extend(self.check_required_sections())
        issues.extend(self.check_status_sync())

        return issues

    def check_version_sync(self) -> List[Issue]:
        """Verify version matches source file.

        Returns:
            List of version-related issues
        """
        issues = []

        # Extract version from CLAUDE.md
        claude_version = self._extract_version_from_claude_md()
        if not claude_version:
            return issues  # No version found in CLAUDE.md

        # Detect project and get actual version
        detector = CLAUDEMDDetector(self.project_root)
        project_info = detector.detect()

        if not project_info:
            return issues  # Can't detect project type

        # Compare versions
        if claude_version != project_info.version:
            issues.append(Issue(
                severity=Severity.WARNING,
                category="version_mismatch",
                message=f"Version {claude_version} in CLAUDE.md doesn't match {project_info.version} in {project_info.version_source}",
                line_number=self._find_version_line(),
                fixable=True,
                fix_method="update_version"
            ))

        return issues

    def check_command_coverage(self) -> List[Issue]:
        """Verify all commands are documented.

        Returns:
            List of command coverage issues
        """
        issues = []

        # Extract documented commands from CLAUDE.md
        documented = self._extract_documented_commands()

        # Scan actual commands directory
        actual = self._scan_commands_directory()

        # Missing commands (exist but not documented)
        for cmd in actual - documented:
            issues.append(Issue(
                severity=Severity.INFO,
                category="missing_command",
                message=f"Command {cmd} exists but not documented in CLAUDE.md",
                fixable=False  # Needs description
            ))

        # Stale commands (documented but don't exist)
        for cmd in documented - actual:
            issues.append(Issue(
                severity=Severity.ERROR,
                category="stale_command",
                message=f"Command {cmd} documented but file deleted",
                line_number=self._find_command_line(cmd),
                fixable=True,
                fix_method="remove_command"
            ))

        return issues

    def check_broken_links(self) -> List[Issue]:
        """Find broken internal links.

        Returns:
            List of broken link issues
        """
        issues = []

        # Extract internal links
        internal_links = self._extract_internal_links()

        for link, line_num in internal_links:
            # Skip external URLs
            if link.startswith("http"):
                continue

            # Resolve link path
            target = self._resolve_link_path(link)

            if not target.exists():
                issues.append(Issue(
                    severity=Severity.ERROR,
                    category="broken_link",
                    message=f"Link points to non-existent file: {link}",
                    line_number=line_num,
                    fixable=True,
                    fix_method="remove_link"
                ))

        return issues

    def check_required_sections(self) -> List[Issue]:
        """Verify expected sections are present.

        Returns:
            List of missing section issues
        """
        issues = []

        # Detect project type to determine required sections
        detector = CLAUDEMDDetector(self.project_root)
        project_info = detector.detect()

        if not project_info:
            return issues

        # Define required sections by project type
        required_sections = {
            "craft-plugin": ["Quick Commands", "Project Structure", "Testing"],
            "teaching-site": ["Overview", "Workflow"],
            "r-package": ["Quick Reference", "Development", "Testing"],
            "mcp-server": ["Tools", "Resources"],
            "generic-node": ["Quick Reference"],
            "generic-python": ["Quick Reference"],
        }

        required = required_sections.get(project_info.type, ["Quick Reference"])

        # Extract section headers from CLAUDE.md
        present_sections = self._extract_section_headers()

        # Check for missing sections
        for section in required:
            # Fuzzy match (case-insensitive, partial)
            if not any(section.lower() in s.lower() for s in present_sections):
                issues.append(Issue(
                    severity=Severity.WARNING,
                    category="missing_section",
                    message=f"Expected section '{section}' not found",
                    fixable=False  # Needs manual creation
                ))

        return issues

    def check_status_sync(self) -> List[Issue]:
        """Verify .STATUS file alignment.

        Returns:
            List of status sync issues
        """
        issues = []

        status_file = self.project_root / ".STATUS"
        if not status_file.exists():
            return issues

        # Parse .STATUS file
        status_data = self._parse_status_file(status_file)

        # Extract progress from CLAUDE.md
        claude_progress = self._extract_progress_from_claude_md()

        # Compare progress
        if status_data.get("progress") and claude_progress:
            if status_data["progress"] != claude_progress:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    category="status_sync",
                    message=f"Progress mismatch: CLAUDE.md={claude_progress}%, .STATUS={status_data['progress']}%",
                    line_number=self._find_progress_line(),
                    fixable=True,
                    fix_method="update_progress"
                ))

        return issues

    # Helper methods for extraction

    def _extract_version_from_claude_md(self) -> Optional[str]:
        """Extract version from CLAUDE.md.

        Returns:
            Version string or None
        """
        # Common patterns:
        # **Current Version:** v2.9.0
        # version: 2.9.0
        # v2.9.0 (released ...)

        patterns = [
            r'\*\*Version:\*\*\s+v?([\d.]+)',
            r'\*\*Current Version:\*\*\s+v?([\d.]+)',
            r'^version:\s+v?([\d.]+)',
            r'v([\d.]+)\s+\(released',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.content, re.MULTILINE)
            if match:
                return match.group(1)

        return None

    def _find_version_line(self) -> Optional[int]:
        """Find line number where version is mentioned.

        Returns:
            Line number (1-indexed) or None
        """
        patterns = [
            r'\*\*Current Version:\*\*',
            r'^version:',
        ]

        for i, line in enumerate(self.lines, 1):
            for pattern in patterns:
                if re.search(pattern, line):
                    return i

        return None

    def _extract_documented_commands(self) -> Set[str]:
        """Extract command references from CLAUDE.md.

        Returns:
            Set of command paths (e.g., {"/craft:check", "/craft:docs:update"})
        """
        commands = set()

        # Pattern: /craft:xxx or /craft:xxx:yyy
        pattern = r'/craft:[a-z0-9:-]+'

        for match in re.finditer(pattern, self.content):
            commands.add(match.group(0))

        return commands

    def _scan_commands_directory(self) -> Set[str]:
        """Scan commands/ directory for actual commands.

        Returns:
            Set of command paths
        """
        commands_dir = self.project_root / "commands"
        if not commands_dir.exists():
            return set()

        commands = set()

        for cmd_file in commands_dir.rglob("*.md"):
            # Convert file path to command name
            # commands/check.md -> /craft:check
            # commands/docs/update.md -> /craft:docs:update
            rel_path = cmd_file.relative_to(commands_dir)
            cmd_name = "/craft:" + str(rel_path.with_suffix("")).replace("/", ":")

            commands.add(cmd_name)

        return commands

    def _find_command_line(self, cmd: str) -> Optional[int]:
        """Find line number where command is mentioned.

        Args:
            cmd: Command path (e.g., "/craft:check")

        Returns:
            Line number (1-indexed) or None
        """
        for i, line in enumerate(self.lines, 1):
            if cmd in line:
                return i
        return None

    def _extract_internal_links(self) -> List[tuple]:
        """Extract internal file links from CLAUDE.md.

        Returns:
            List of (link, line_number) tuples
        """
        links = []

        # Markdown link pattern: [text](path)
        pattern = r'\[([^\]]+)\]\(([^)]+)\)'

        for i, line in enumerate(self.lines, 1):
            for match in re.finditer(pattern, line):
                link = match.group(2)
                # Filter internal links (not http/https/mailto)
                if not link.startswith(("http://", "https://", "mailto:", "#")):
                    links.append((link, i))

        return links

    def _resolve_link_path(self, link: str) -> Path:
        """Resolve link to absolute path.

        Args:
            link: Link from markdown (relative or absolute)

        Returns:
            Resolved path
        """
        # Absolute from project root
        if link.startswith("/"):
            return self.project_root / link.lstrip("/")

        # Relative from CLAUDE.md location
        return (self.path.parent / link).resolve()

    def _extract_section_headers(self) -> List[str]:
        """Extract section headers (H1, H2) from CLAUDE.md.

        Returns:
            List of section titles
        """
        sections = []

        # Pattern: ## Section Title or # Section Title
        pattern = r'^##?\s+(.+)$'

        for line in self.lines:
            match = re.match(pattern, line)
            if match:
                # Remove markdown formatting
                title = match.group(1)
                title = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', title)  # Remove links
                title = re.sub(r'[*_`]', '', title)  # Remove emphasis
                sections.append(title.strip())

        return sections

    def _extract_progress_from_claude_md(self) -> Optional[int]:
        """Extract progress percentage from CLAUDE.md.

        Returns:
            Progress as integer (0-100) or None
        """
        # Patterns to match:
        # progress: 95%
        # **Progress:** 60%
        # Progress: 85%
        patterns = [
            r'progress:\s*(\d+)%',
            r'\*\*Progress:\*\*\s*(\d+)%',
        ]

        for pattern in patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                return int(match.group(1))

        return None

    def _find_progress_line(self) -> Optional[int]:
        """Find line number where progress is mentioned.

        Returns:
            Line number (1-indexed) or None
        """
        patterns = [
            r'progress:\s*\d+%',
            r'\*\*Progress:\*\*\s*\d+%',
        ]

        for i, line in enumerate(self.lines, 1):
            for pattern in patterns:
                if re.search(pattern, line, re.IGNORECASE):
                    return i

        return None
        pattern = r'progress:\s*\d+%'

        for i, line in enumerate(self.lines, 1):
            if re.search(pattern, line, re.IGNORECASE):
                return i

        return None

    def _parse_status_file(self, status_file: Path) -> dict:
        """Parse .STATUS file.

        Args:
            status_file: Path to .STATUS file

        Returns:
            Dictionary with status data
        """
        data = {}

        try:
            content = status_file.read_text()
            for line in content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # Parse progress as integer
                    if key == "progress":
                        # Extract percentage: "95% (Planning)" -> 95
                        match = re.search(r'(\d+)%', value)
                        if match:
                            data[key] = int(match.group(1))
                    else:
                        data[key] = value
        except Exception:
            pass

        return data

    def generate_report(self, issues: List[Issue]) -> str:
        """Generate formatted audit report.

        Args:
            issues: List of issues found

        Returns:
            Formatted report string
        """
        # Group issues by severity
        errors = [i for i in issues if i.severity == Severity.ERROR]
        warnings = [i for i in issues if i.severity == Severity.WARNING]
        infos = [i for i in issues if i.severity == Severity.INFO]

        # Build report
        lines = []
        lines.append("")
        lines.append("Audit Results for CLAUDE.md")
        lines.append("")

        # Errors
        if errors:
            lines.append(f"🔴 Errors ({len(errors)}) - Must Fix")
            lines.append("")
            for i, issue in enumerate(errors, 1):
                lines.append(f"{i}. {issue.category.replace('_', ' ').title()}")
                lines.append(f"   {issue.message}")
                if issue.fixable:
                    lines.append("   Fix: /craft:docs:claude-md:sync --fix")
                lines.append("")

        # Warnings
        if warnings:
            lines.append(f"⚠️  Warnings ({len(warnings)}) - Should Fix")
            lines.append("")
            for i, issue in enumerate(warnings, 1):
                lines.append(f"{i}. {issue.category.replace('_', ' ').title()}")
                lines.append(f"   {issue.message}")
                if issue.fixable:
                    lines.append("   Fix: /craft:docs:claude-md:sync --fix")
                else:
                    lines.append("   Fix: Manual edit required")
                lines.append("")

        # Info
        if infos:
            lines.append(f"📝 Info ({len(infos)}) - Optional")
            lines.append("")
            for i, issue in enumerate(infos, 1):
                lines.append(f"{i}. {issue.category.replace('_', ' ').title()}")
                lines.append(f"   {issue.message}")
                lines.append("")

        # Summary
        lines.append("Summary:")
        lines.append(f"  🔴 Errors:   {len(errors)} ({sum(1 for i in errors if i.fixable)} auto-fixable)")
        lines.append(f"  ⚠️  Warnings: {len(warnings)} ({sum(1 for i in warnings if i.fixable)} auto-fixable)")
        lines.append(f"  📝 Info:     {len(infos)}")
        lines.append("")

        if errors or warnings:
            lines.append("Next: /craft:docs:claude-md:sync --fix")
        else:
            lines.append("✅ No issues found")

        return "\n".join(lines)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Audit CLAUDE.md file")
    parser.add_argument("file", help="Path to CLAUDE.md file")
    parser.add_argument("--strict", action="store_true", help="Exit with error code if issues found")

    args = parser.parse_args()

    # Run audit
    auditor = CLAUDEMDAuditor(Path(args.file))
    issues = auditor.audit()

    # Generate report
    report = auditor.generate_report(issues)
    print(report)

    # Exit code
    errors = [i for i in issues if i.severity == Severity.ERROR]
    if args.strict and errors:
        sys.exit(1)
    else:
        sys.exit(0)


if __name__ == "__main__":
    main()
