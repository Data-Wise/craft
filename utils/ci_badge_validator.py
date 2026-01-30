#!/usr/bin/env python3
"""
CI Badge Validator - Validate GitHub Actions CI Badges

Focused validator for CI badges that checks:
1. Workflow file exists for badge URL
2. Badge branch parameter matches current branch
3. Badge URL format is correct

Lightweight module separate from full badge system, designed for use
in /craft:ci:validate command.

Version: 1.0.0
Author: Craft Plugin
"""

import re
from dataclasses import dataclass
from pathlib import Path
from typing import List, Optional, Dict

from badge_detector import BadgeDetector, Badge, BadgeType


@dataclass
class CIBadgeIssue:
    """Represents an issue with a CI badge."""
    severity: str                  # 'error', 'warning', 'info'
    badge_type: str                # 'missing_workflow', 'wrong_branch', etc.
    file_path: Path
    line_number: int
    current_badge: str             # Raw markdown
    expected_badge: Optional[str]  # Suggested fix (if available)
    message: str                   # Human-readable description

    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"<CIBadgeIssue {self.severity}: {self.badge_type} at {self.file_path.name}:{self.line_number}>"


class CIBadgeValidator:
    """Validator for GitHub Actions CI badges."""

    def __init__(self, project_root: Path = None):
        """Initialize CI badge validator.

        Args:
            project_root: Project directory path (default: current directory)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.detector = BadgeDetector(self.project_root)

    def validate_badges(
        self,
        files: Optional[List[str]] = None,
        branch: Optional[str] = None
    ) -> List[CIBadgeIssue]:
        """Validate CI badges in specified files.

        Args:
            files: List of files to check (default: ['README.md', 'docs/index.md'])
            branch: Expected branch for badges (default: auto-detect)

        Returns:
            List of CIBadgeIssue objects
        """
        if files is None:
            files = ['README.md', 'docs/index.md']

        if branch is None:
            branch = self._detect_current_branch()

        # Get available workflows
        workflows = self._get_workflow_files()

        # Detect all badges
        all_badges = self.detector.detect_all(files)

        # Validate each file
        issues = []
        for file_path, badges in all_badges.items():
            file_issues = self._validate_file_badges(
                file_path, badges, workflows, branch
            )
            issues.extend(file_issues)

        return issues

    def _validate_file_badges(
        self,
        file_path: Path,
        badges: List[Badge],
        workflows: Dict[str, Path],
        expected_branch: str
    ) -> List[CIBadgeIssue]:
        """Validate CI badges in a single file.

        Args:
            file_path: File being validated
            badges: Badges from this file
            workflows: Available workflow files
            expected_branch: Expected branch for badge URLs

        Returns:
            List of issues found
        """
        issues = []

        for badge in badges:
            if not self._is_ci_badge(badge.label, badge.url):
                continue

            # Check 1: Workflow file exists
            workflow_name = self.detector.extract_workflow_name(badge)
            if workflow_name and workflow_name not in workflows:
                issues.append(CIBadgeIssue(
                    severity='error',
                    badge_type='missing_workflow',
                    file_path=file_path,
                    line_number=badge.line_number,
                    current_badge=badge.raw_markdown,
                    expected_badge=None,
                    message=f"Badge points to non-existent workflow: {workflow_name}"
                ))
                continue

            # Check 2: Branch parameter matches
            badge_branch = self.detector.extract_branch_from_ci_badge(badge)
            if badge_branch and badge_branch != expected_branch:
                # Generate expected badge with correct branch
                expected_url = re.sub(
                    r'branch=[^&\)]+',
                    f'branch={expected_branch}',
                    badge.url
                )
                expected_badge = badge.raw_markdown.replace(badge.url, expected_url)

                issues.append(CIBadgeIssue(
                    severity='warning',
                    badge_type='wrong_branch',
                    file_path=file_path,
                    line_number=badge.line_number,
                    current_badge=badge.raw_markdown,
                    expected_badge=expected_badge,
                    message=f"Badge uses '{badge_branch}', expected '{expected_branch}'"
                ))

            # Check 3: URL format is correct
            if not self._is_valid_ci_badge_url(badge.url):
                issues.append(CIBadgeIssue(
                    severity='warning',
                    badge_type='invalid_format',
                    file_path=file_path,
                    line_number=badge.line_number,
                    current_badge=badge.raw_markdown,
                    expected_badge=None,
                    message="Badge URL format is invalid"
                ))

        return issues

    def _is_ci_badge(self, label: str, url: str) -> bool:
        """Check if badge is a GitHub Actions CI badge.

        Args:
            label: Badge label
            url: Badge URL

        Returns:
            True if this is a CI badge
        """
        # GitHub Actions URL pattern
        if 'github.com' in url and 'actions/workflows' in url:
            return True

        # Common CI label patterns
        ci_labels = ['ci', 'build', 'test', 'workflow', 'actions']
        label_lower = label.lower()
        return any(ci_label in label_lower for ci_label in ci_labels)

    def _is_valid_ci_badge_url(self, url: str) -> bool:
        """Validate CI badge URL format.

        Args:
            url: Badge URL to validate

        Returns:
            True if URL format is valid
        """
        # GitHub Actions badge pattern
        # https://github.com/OWNER/REPO/actions/workflows/WORKFLOW/badge.svg?branch=BRANCH
        pattern = r'https://github\.com/[^/]+/[^/]+/actions/workflows/[^/]+/badge\.svg'
        return bool(re.match(pattern, url))

    def _get_workflow_files(self) -> Dict[str, Path]:
        """Get available GitHub Actions workflow files.

        Returns:
            Dictionary mapping workflow filename to file path
        """
        workflows = {}
        workflows_dir = self.project_root / ".github" / "workflows"

        if not workflows_dir.exists():
            return workflows

        for workflow_file in workflows_dir.glob("*.yml"):
            workflows[workflow_file.name] = workflow_file

        # Also check .yaml extension
        for workflow_file in workflows_dir.glob("*.yaml"):
            workflows[workflow_file.name] = workflow_file

        return workflows

    def _detect_current_branch(self) -> str:
        """Detect current git branch.

        Returns:
            Branch name (default: 'dev')
        """
        try:
            import subprocess
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError, ImportError):
            pass

        return 'dev'  # Safe default


def format_issues_report(issues: List[CIBadgeIssue]) -> str:
    """Format CI badge issues for display.

    Args:
        issues: List of CIBadgeIssue objects

    Returns:
        Formatted report string
    """
    if not issues:
        return "✅ All CI badges valid"

    # Group by file
    by_file: Dict[Path, List[CIBadgeIssue]] = {}
    for issue in issues:
        by_file.setdefault(issue.file_path, []).append(issue)

    lines = []
    lines.append("╭─ CI Badge Validation ───────────────────────────╮")
    lines.append("│                                                  │")

    for file_path, file_issues in sorted(by_file.items()):
        lines.append(f"│  📁 {file_path.name:<44} │")
        lines.append("│                                                  │")

        for issue in file_issues:
            severity_icon = {
                'error': '❌',
                'warning': '⚠️',
                'info': 'ℹ️'
            }[issue.severity]

            # Truncate message to fit
            msg = issue.message
            if len(msg) > 38:
                msg = msg[:35] + "..."

            lines.append(f"│    {severity_icon} Line {issue.line_number}: {issue.badge_type:<30} │")
            lines.append(f"│       {msg:<42} │")
            lines.append("│                                                  │")

    # Summary
    error_count = sum(1 for i in issues if i.severity == 'error')
    warning_count = sum(1 for i in issues if i.severity == 'warning')

    summary_parts = []
    if error_count:
        summary_parts.append(f"{error_count} error{'s' if error_count != 1 else ''}")
    if warning_count:
        summary_parts.append(f"{warning_count} warning{'s' if warning_count != 1 else ''}")

    summary = "Total: " + ", ".join(summary_parts)
    lines.append("├──────────────────────────────────────────────────┤")
    lines.append(f"│  {summary:<47} │")

    if error_count:
        lines.append("│  Run with --fix to update badges                 │")

    lines.append("╰──────────────────────────────────────────────────╯")

    return '\n'.join(lines)


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()

    validator = CIBadgeValidator(project_root)

    print("Validating CI badges...")
    issues = validator.validate_badges()

    if not issues:
        print("✅ All CI badges valid")
    else:
        print(format_issues_report(issues))


if __name__ == '__main__':
    main()
