#!/usr/bin/env python3
"""
CLAUDE.md Fixer

Auto-fixes issues found by CLAUDEMDAuditor:
- Version mismatches
- Stale command references
- Broken links
- Progress sync with .STATUS

Version: 1.0.0
Author: Craft Plugin
"""

import re
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional

# Import auditor for issue detection
try:
    from .claude_md_auditor import CLAUDEMDAuditor, Issue, Severity
    from .claude_md_detector import CLAUDEMDDetector
except ImportError:
    from claude_md_auditor import CLAUDEMDAuditor, Issue, Severity
    from claude_md_detector import CLAUDEMDDetector


@dataclass
class FixResult:
    """Result of applying a fix."""
    success: bool
    issue: Issue
    description: str
    lines_changed: int = 0


class CLAUDEMDFixer:
    """Auto-fixer for CLAUDE.md files."""

    def __init__(self, claude_md_path: Path):
        """Initialize fixer.

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

        # Initialize auditor
        self.auditor = CLAUDEMDAuditor(claude_md_path)

    def fix_all(self, scope: str = "errors", dry_run: bool = False, interactive: bool = False) -> List[FixResult]:
        """Fix all auto-fixable issues.

        Args:
            scope: What to fix ("errors", "warnings", "all")
            dry_run: Preview fixes without applying
            interactive: Confirm each fix

        Returns:
            List of fix results
        """
        # Get issues from auditor
        all_issues = self.auditor.audit()

        # Filter by scope
        issues_to_fix = self._filter_issues_by_scope(all_issues, scope)

        # Only fixable issues
        fixable_issues = [i for i in issues_to_fix if i.fixable]

        if not fixable_issues:
            return []

        # Apply fixes
        results = []
        for issue in fixable_issues:
            if interactive:
                if not self._confirm_fix(issue):
                    continue

            result = self._apply_fix(issue, dry_run)
            results.append(result)

        # Save changes if not dry run
        if not dry_run and results:
            self._save_changes()

        return results

    def fix_version_mismatch(self, issue: Issue, dry_run: bool = False) -> FixResult:
        """Fix version mismatch.

        Args:
            issue: Version mismatch issue
            dry_run: Preview only

        Returns:
            Fix result
        """
        # Get actual version from project
        detector = CLAUDEMDDetector(self.project_root)
        project_info = detector.detect()

        if not project_info:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not detect project type"
            )

        # Extract current version from CLAUDE.md
        old_version_match = re.search(r'v?([\d.]+)', issue.message)
        if not old_version_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse version from issue"
            )

        old_version = old_version_match.group(1)
        new_version = project_info.version

        # Find and replace version in content
        patterns = [
            (r'\*\*Current Version:\*\*\s+v?[\d.]+', f'**Current Version:** v{new_version}'),
            (r'^version:\s+v?[\d.]+', f'version: {new_version}'),
            (r'v([\d.]+)\s+\(released', f'v{new_version} (released'),
        ]

        lines_changed = 0
        for pattern, replacement in patterns:
            new_content, count = re.subn(pattern, replacement, self.content, flags=re.MULTILINE)
            if count > 0:
                self.content = new_content
                self.lines = self.content.split("\n")
                lines_changed = count
                break

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Updated version: v{old_version} → v{new_version}",
            lines_changed=lines_changed
        )

    def fix_stale_command(self, issue: Issue, dry_run: bool = False) -> FixResult:
        """Fix stale command reference.

        Args:
            issue: Stale command issue
            dry_run: Preview only

        Returns:
            Fix result
        """
        # Extract command from issue message
        cmd_match = re.search(r'(/craft:[a-z0-9:-]+)', issue.message)
        if not cmd_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse command from issue"
            )

        command = cmd_match.group(1)

        # Remove lines containing the command
        lines_changed = 0
        new_lines = []
        for line in self.lines:
            if command in line:
                lines_changed += 1
                # Skip this line (remove it)
                continue
            new_lines.append(line)

        if lines_changed > 0:
            self.lines = new_lines
            self.content = "\n".join(self.lines)

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Removed stale command: {command}",
            lines_changed=lines_changed
        )

    def fix_broken_link(self, issue: Issue, dry_run: bool = False) -> FixResult:
        """Fix broken link.

        Args:
            issue: Broken link issue
            dry_run: Preview only

        Returns:
            Fix result
        """
        # Extract link from issue message
        link_match = re.search(r'file: (.+)$', issue.message)
        if not link_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse link from issue"
            )

        link = link_match.group(1)

        # Comment out the line with the broken link
        lines_changed = 0
        new_lines = []
        for line in self.lines:
            if link in line:
                # Comment out the line
                new_lines.append(f"<!-- {line.strip()} --> (link broken)")
                lines_changed += 1
            else:
                new_lines.append(line)

        if lines_changed > 0:
            self.lines = new_lines
            self.content = "\n".join(self.lines)

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Commented out broken link: {link}",
            lines_changed=lines_changed
        )

    def fix_status_sync(self, issue: Issue, dry_run: bool = False) -> FixResult:
        """Fix progress mismatch with .STATUS.

        Args:
            issue: Status sync issue
            dry_run: Preview only

        Returns:
            Fix result
        """
        # Extract progress values from issue message
        progress_match = re.search(r'CLAUDE\.md=(\d+)%.*\.STATUS=(\d+)%', issue.message)
        if not progress_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse progress from issue"
            )

        old_progress = progress_match.group(1)
        new_progress = progress_match.group(2)

        # Update progress in content
        patterns = [
            (r'progress:\s*\d+%', f'progress: {new_progress}%'),
            (r'\*\*Progress:\*\*\s*\d+%', f'**Progress:** {new_progress}%'),
        ]

        lines_changed = 0
        for pattern, replacement in patterns:
            new_content, count = re.subn(pattern, replacement, self.content, flags=re.IGNORECASE)
            if count > 0:
                self.content = new_content
                self.lines = self.content.split("\n")
                lines_changed = count
                break

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Updated progress: {old_progress}% → {new_progress}%",
            lines_changed=lines_changed
        )

    def _apply_fix(self, issue: Issue, dry_run: bool) -> FixResult:
        """Apply appropriate fix for issue.

        Args:
            issue: Issue to fix
            dry_run: Preview only

        Returns:
            Fix result
        """
        if issue.fix_method == "update_version":
            return self.fix_version_mismatch(issue, dry_run)
        elif issue.fix_method == "remove_command":
            return self.fix_stale_command(issue, dry_run)
        elif issue.fix_method == "remove_link":
            return self.fix_broken_link(issue, dry_run)
        elif issue.fix_method == "update_progress":
            return self.fix_status_sync(issue, dry_run)
        else:
            return FixResult(
                success=False,
                issue=issue,
                description=f"Unknown fix method: {issue.fix_method}"
            )

    def _filter_issues_by_scope(self, issues: List[Issue], scope: str) -> List[Issue]:
        """Filter issues by severity scope.

        Args:
            issues: All issues
            scope: Scope ("errors", "warnings", "all")

        Returns:
            Filtered issues
        """
        if scope == "errors":
            return [i for i in issues if i.severity == Severity.ERROR]
        elif scope == "warnings":
            return [i for i in issues if i.severity in [Severity.ERROR, Severity.WARNING]]
        elif scope == "all":
            return issues
        else:
            return [i for i in issues if i.severity == Severity.ERROR]

    def _confirm_fix(self, issue: Issue) -> bool:
        """Confirm fix in interactive mode.

        Args:
            issue: Issue to confirm

        Returns:
            True if confirmed
        """
        print(f"\nFix: {issue.category}")
        print(f"  {issue.message}")
        print(f"  Action: {issue.fix_method}")

        response = input("Apply this fix? [y/n/skip-all/apply-all] ").lower()

        return response in ["y", "yes", "apply-all"]

    def _save_changes(self):
        """Save changes to CLAUDE.md file.

        Creates backup before saving.
        """
        # Create backup
        backup_path = self.path.parent / f".{self.path.name}.backup"
        shutil.copy2(self.path, backup_path)

        # Write changes
        self.path.write_text(self.content)

    def generate_report(self, results: List[FixResult]) -> str:
        """Generate fix report.

        Args:
            results: List of fix results

        Returns:
            Formatted report string
        """
        if not results:
            return "\n✅ No fixes needed\n"

        lines = []
        lines.append("")
        lines.append("Fixes Applied")
        lines.append("")

        # Successful fixes
        successful = [r for r in results if r.success]
        if successful:
            lines.append(f"Applied {len(successful)} fixes to CLAUDE.md:")
            for result in successful:
                lines.append(f"  ✓ {result.description}")
            lines.append("")

        # Failed fixes
        failed = [r for r in results if not r.success]
        if failed:
            lines.append(f"Failed to apply {len(failed)} fixes:")
            for result in failed:
                lines.append(f"  ✗ {result.description}")
            lines.append("")

        # Summary
        total_lines = sum(r.lines_changed for r in successful)
        lines.append(f"File: {self.path}")
        lines.append(f"Changes: {total_lines} lines modified")
        lines.append("")

        lines.append("Next steps:")
        lines.append("  1. Review: git diff CLAUDE.md")
        lines.append("  2. Run audit: /craft:docs:claude-md:audit")
        lines.append("  3. Commit: git add CLAUDE.md")

        return "\n".join(lines)


def main():
    """CLI entry point."""
    import argparse

    parser = argparse.ArgumentParser(description="Fix CLAUDE.md issues")
    parser.add_argument("file", help="Path to CLAUDE.md file")
    parser.add_argument("--scope", choices=["errors", "warnings", "all"], default="errors",
                        help="What to fix")
    parser.add_argument("--dry-run", "-n", action="store_true",
                        help="Preview fixes without applying")
    parser.add_argument("--interactive", "-i", action="store_true",
                        help="Confirm each fix")

    args = parser.parse_args()

    # Run fixer
    fixer = CLAUDEMDFixer(Path(args.file))
    results = fixer.fix_all(
        scope=args.scope,
        dry_run=args.dry_run,
        interactive=args.interactive
    )

    # Generate report
    report = fixer.generate_report(results)
    print(report)

    # Exit code
    if not results:
        sys.exit(1)  # No fixes needed
    elif any(not r.success for r in results):
        sys.exit(2)  # Some fixes failed
    else:
        sys.exit(0)  # All fixes applied


if __name__ == "__main__":
    main()
