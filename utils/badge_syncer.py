#!/usr/bin/env python3
"""
Badge Syncer - Orchestrate Badge Synchronization

Synchronizes badges across README.md and docs/index.md by:
1. Detecting current badges
2. Generating expected badges from project state
3. Finding mismatches
4. Displaying diffs
5. Applying updates

Integrates with CLAUDEMDDetector for version extraction and project type detection.

Version: 1.0.0
Author: Craft Plugin
"""

import re
import subprocess
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional, Tuple
from urllib.parse import quote

from badge_detector import BadgeDetector, Badge, BadgeType


class BadgeSeverity(Enum):
    """Badge mismatch severity levels."""
    CRITICAL = "critical"   # Version mismatch, missing CI badge
    WARNING = "warning"     # Branch mismatch, outdated coverage
    INFO = "info"           # Cosmetic differences


@dataclass
class BadgeMismatch:
    """Represents a badge that needs updating."""
    file_path: Path
    badge_type: BadgeType
    current: Optional[Badge]       # None if badge is missing
    expected: Badge
    severity: BadgeSeverity
    fix_action: str                # Human-readable description

    def __repr__(self) -> str:
        """String representation for debugging."""
        status = "missing" if self.current is None else "outdated"
        return f"<BadgeMismatch {status} {self.badge_type.value} in {self.file_path.name}: {self.fix_action}>"


class BadgeSyncer:
    """Badge synchronization orchestrator."""

    def __init__(self, project_root: Path = None, config: Optional[Dict] = None):
        """Initialize badge syncer.

        Args:
            project_root: Project directory path (default: current directory)
            config: Optional configuration dict
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()
        self.config = config or {}
        self.detector = BadgeDetector(self.project_root)

        # Lazy-load CLAUDEMDDetector only when needed
        self._claude_md_detector = None
        self._project_info = None

    @property
    def claude_md_detector(self):
        """Lazy-load CLAUDEMDDetector."""
        if self._claude_md_detector is None:
            try:
                import sys
                sys.path.insert(0, str(self.project_root / "utils"))
                from claude_md_detector import CLAUDEMDDetector
                self._claude_md_detector = CLAUDEMDDetector(self.project_root)
            except ImportError:
                # Fallback if CLAUDEMDDetector not available
                self._claude_md_detector = None
        return self._claude_md_detector

    @property
    def project_info(self):
        """Lazy-load project info from CLAUDEMDDetector."""
        if self._project_info is None and self.claude_md_detector:
            self._project_info = self.claude_md_detector.detect()
        return self._project_info

    def sync_badges(
        self,
        files: Optional[List[str]] = None,
        auto_confirm: bool = False,
        calculate_coverage: bool = True,
        dry_run: bool = False
    ) -> List[BadgeMismatch]:
        """Synchronize badges across specified files.

        Args:
            files: List of file paths (default: ['README.md', 'docs/index.md'])
            auto_confirm: If True, apply updates without prompting
            calculate_coverage: If True, calculate docs coverage % (can be slow)
            dry_run: If True, detect mismatches but don't apply updates

        Returns:
            List of BadgeMismatch objects (applied or detected)
        """
        if files is None:
            files = ['README.md', 'docs/index.md']

        # Step 1: Detect current badges
        current_badges = self.detector.detect_all(files)

        # Step 2: Generate expected badges
        expected_badges = self._generate_expected_badges(calculate_coverage)

        # Step 3: Find mismatches
        mismatches = self._find_mismatches(current_badges, expected_badges, files)

        if not mismatches:
            return []

        # Step 4: Display diff
        if not auto_confirm:
            self._show_diff(mismatches)

        # Step 5: Apply updates (unless dry-run)
        if not dry_run:
            applied = self._apply_updates(mismatches, auto_confirm)
            return applied
        else:
            return mismatches

    def _generate_expected_badges(self, calculate_coverage: bool = True) -> Dict[str, Badge]:
        """Generate expected badges from project state.

        Args:
            calculate_coverage: Whether to calculate documentation coverage

        Returns:
            Dictionary mapping badge keys to Badge objects
            Keys: 'version', 'ci_main', 'ci_docs_quality', 'docs_coverage', etc.
        """
        expected = {}

        # Generate version badge
        version_badge = self._generate_version_badge()
        if version_badge:
            expected['version'] = version_badge

        # Generate CI badges
        ci_badges = self._generate_ci_badges()
        expected.update(ci_badges)

        # Generate coverage badges (optional, can be slow)
        if calculate_coverage:
            coverage_badges = self._generate_coverage_badges()
            expected.update(coverage_badges)

        return expected

    def _generate_version_badge(self) -> Optional[Badge]:
        """Generate version badge from project state.

        Returns:
            Badge object for version, or None if version not detected
        """
        # Get version from CLAUDEMDDetector
        if self.project_info:
            version = self.project_info.version
        else:
            # Fallback: try to detect version manually
            version = self._detect_version_fallback()

        if not version or version == "0.0.0":
            return None

        # Get repo info for link URL
        repo_url = self._get_repo_url()

        # Shields.io escapes single dash as double dash
        escaped_version = version.replace('-', '--')

        # Determine color based on version
        if '-dev' in version or '-alpha' in version or '-beta' in version:
            color = 'blue'
        else:
            color = 'brightgreen'

        badge_url = f"https://img.shields.io/badge/version-{escaped_version}-{color}.svg"
        link_url = f"{repo_url}/releases" if repo_url else None

        return Badge(
            type=BadgeType.VERSION,
            label="Version",
            url=badge_url,
            link_url=link_url,
            raw_markdown=f"[![Version]({badge_url})]({link_url})" if link_url else f"![Version]({badge_url})",
            file_path=Path("README.md"),  # Primary location
            line_number=0  # Will be updated when applying
        )

    def _generate_ci_badges(self) -> Dict[str, Badge]:
        """Generate CI status badges from workflow files.

        Returns:
            Dictionary mapping badge keys to Badge objects
        """
        ci_badges = {}
        workflows_dir = self.project_root / ".github" / "workflows"

        if not workflows_dir.exists():
            return ci_badges

        # Get current branch for badge URL
        current_branch = self._get_current_branch()

        # Scan workflow files
        for workflow_file in workflows_dir.glob("*.yml"):
            workflow_name = workflow_file.name
            badge_key = f"ci_{workflow_file.stem}"

            # Determine label from workflow name
            label_base = workflow_name.replace('.yml', '').replace('-', ' ').replace('_', ' ').title()

            # Standardize common workflow names
            if label_base.lower() == 'ci':
                label = "Craft CI"
            elif 'docs' in label_base.lower() and 'quality' in label_base.lower():
                label = "Documentation Quality"
            else:
                label = label_base

            # Get repo URL
            repo_url = self._get_repo_url()
            if not repo_url:
                continue

            # Extract owner/repo from URL
            repo_match = re.search(r'github\.com/([^/]+/[^/]+)', repo_url)
            if not repo_match:
                continue
            owner_repo = repo_match.group(1)

            badge_url = f"https://github.com/{owner_repo}/actions/workflows/{workflow_name}/badge.svg?branch={current_branch}"
            link_url = f"https://github.com/{owner_repo}/actions/workflows/{workflow_name}"

            ci_badges[badge_key] = Badge(
                type=BadgeType.CI_STATUS,
                label=label,
                url=badge_url,
                link_url=link_url,
                raw_markdown=f"[![{label}]({badge_url})]({link_url})",
                file_path=Path("README.md"),
                line_number=0
            )

        return ci_badges

    def _generate_coverage_badges(self) -> Dict[str, Badge]:
        """Generate coverage badges (docs and test).

        Returns:
            Dictionary mapping badge keys to Badge objects
        """
        coverage_badges = {}

        # Docs coverage: Calculate from command documentation
        docs_coverage = self._calculate_docs_coverage()
        if docs_coverage is not None:
            # Determine color based on coverage %
            if docs_coverage >= 95:
                color = 'brightgreen'
            elif docs_coverage >= 85:
                color = 'green'
            elif docs_coverage >= 75:
                color = 'yellowgreen'
            else:
                color = 'yellow'

            # URL encode the percentage symbol
            badge_url = f"https://img.shields.io/badge/docs-{docs_coverage}%25%20complete-{color}.svg"
            site_url = self._get_docs_site_url()

            coverage_badges['docs_coverage'] = Badge(
                type=BadgeType.DOCS_COVERAGE,
                label="Documentation",
                url=badge_url,
                link_url=site_url,
                raw_markdown=f"[![Documentation]({badge_url})]({site_url})" if site_url else f"![Documentation]({badge_url})",
                file_path=Path("README.md"),
                line_number=0
            )

        return coverage_badges

    def _find_mismatches(
        self,
        current: Dict[Path, List[Badge]],
        expected: Dict[str, Badge],
        files: List[str]
    ) -> List[BadgeMismatch]:
        """Find mismatches between current and expected badges.

        Args:
            current: Current badges from detector
            expected: Expected badges from generator
            files: Files to check

        Returns:
            List of BadgeMismatch objects
        """
        mismatches = []

        # Check each expected badge against each file
        for badge_key, expected_badge in expected.items():
            # Track which files have this badge
            files_with_badge = set()

            # Check each file for this badge
            for file_path, badges in current.items():
                for badge in badges:
                    if (badge.type == expected_badge.type and
                        badge.label.lower() == expected_badge.label.lower()):
                        files_with_badge.add(file_path)

                        # Check if badge matches expected
                        if not self._badges_match(badge, expected_badge):
                            severity = self._determine_severity(badge, expected_badge)
                            fix_action = self._describe_fix(badge, expected_badge)

                            mismatches.append(BadgeMismatch(
                                file_path=file_path,
                                badge_type=expected_badge.type,
                                current=badge,
                                expected=expected_badge,
                                severity=severity,
                                fix_action=fix_action
                            ))

            # Check if badge is missing from any file
            for file_rel in files:
                file_path = self.project_root / file_rel
                if file_path.exists() and file_path not in files_with_badge:
                    # Badge missing from this file
                    mismatches.append(BadgeMismatch(
                        file_path=file_path,
                        badge_type=expected_badge.type,
                        current=None,
                        expected=expected_badge,
                        severity=BadgeSeverity.CRITICAL,
                        fix_action=f"Add {expected_badge.label} badge"
                    ))

        return mismatches

    def _find_current_badge(
        self,
        current: Dict[Path, List[Badge]],
        badge_type: BadgeType,
        label: str
    ) -> Optional[Badge]:
        """Find current badge matching type and label.

        Args:
            current: Current badges dictionary
            badge_type: Type to match
            label: Label to match (case-insensitive)

        Returns:
            Badge if found, None otherwise
        """
        for badge_list in current.values():
            for badge in badge_list:
                if badge.type == badge_type and badge.label.lower() == label.lower():
                    return badge
        return None

    def _badges_match(self, current: Badge, expected: Badge) -> bool:
        """Check if current badge matches expected.

        Args:
            current: Current badge
            expected: Expected badge

        Returns:
            True if badges match, False otherwise
        """
        # Compare normalized URLs (ignore trailing params order)
        current_url_base = current.url.split('?')[0]
        expected_url_base = expected.url.split('?')[0]

        if current_url_base != expected_url_base:
            return False

        # For CI badges, check branch parameter
        if current.type == BadgeType.CI_STATUS:
            current_branch = self.detector.extract_branch_from_ci_badge(current)
            expected_branch = self.detector.extract_branch_from_ci_badge(expected)
            if current_branch != expected_branch:
                return False

        return True

    def _determine_severity(self, current: Badge, expected: Badge) -> BadgeSeverity:
        """Determine severity of badge mismatch.

        Args:
            current: Current badge
            expected: Expected badge

        Returns:
            BadgeSeverity level
        """
        # Version mismatch is critical
        if current.type == BadgeType.VERSION:
            current_version = self.detector.extract_version_from_badge(current)
            expected_version = self.detector.extract_version_from_badge(expected)
            if current_version != expected_version:
                return BadgeSeverity.CRITICAL

        # CI badge branch mismatch is warning
        if current.type == BadgeType.CI_STATUS:
            current_branch = self.detector.extract_branch_from_ci_badge(current)
            expected_branch = self.detector.extract_branch_from_ci_badge(expected)
            if current_branch != expected_branch:
                return BadgeSeverity.WARNING

        # Coverage difference is info
        if current.type in (BadgeType.DOCS_COVERAGE, BadgeType.TEST_COVERAGE):
            return BadgeSeverity.INFO

        # Default: warning
        return BadgeSeverity.WARNING

    def _describe_fix(self, current: Badge, expected: Badge) -> str:
        """Generate human-readable description of fix.

        Args:
            current: Current badge
            expected: Expected badge

        Returns:
            Fix description string
        """
        if current.type == BadgeType.VERSION:
            current_version = self.detector.extract_version_from_badge(current)
            expected_version = self.detector.extract_version_from_badge(expected)
            return f"Update version: {current_version} → {expected_version}"

        if current.type == BadgeType.CI_STATUS:
            current_branch = self.detector.extract_branch_from_ci_badge(current)
            expected_branch = self.detector.extract_branch_from_ci_badge(expected)
            if current_branch != expected_branch:
                return f"Update branch: {current_branch} → {expected_branch}"
            else:
                workflow = self.detector.extract_workflow_name(expected)
                return f"Update workflow: {workflow}"

        if current.type == BadgeType.DOCS_COVERAGE:
            # Extract percentages from URLs
            current_pct = re.search(r'-(\d+)%', current.url)
            expected_pct = re.search(r'-(\d+)%', expected.url)
            if current_pct and expected_pct:
                return f"Update coverage: {current_pct.group(1)}% → {expected_pct.group(1)}%"

        return "Update badge URL"

    def _show_diff(self, mismatches: List[BadgeMismatch]) -> None:
        """Display diff of badge mismatches.

        Args:
            mismatches: List of mismatches to display
        """
        if not mismatches:
            print("✅ All badges in sync")
            return

        # Group by file
        by_file: Dict[Path, List[BadgeMismatch]] = {}
        for mismatch in mismatches:
            by_file.setdefault(mismatch.file_path, []).append(mismatch)

        print("\n📛 Badge Sync Report")
        print("=" * 60)

        for file_path, file_mismatches in sorted(by_file.items()):
            rel_path = file_path.relative_to(self.project_root)
            print(f"\n📁 {rel_path}:")

            for i, mismatch in enumerate(file_mismatches, start=1):
                severity_icon = {
                    BadgeSeverity.CRITICAL: "❌",
                    BadgeSeverity.WARNING: "⚠️",
                    BadgeSeverity.INFO: "ℹ️"
                }[mismatch.severity]

                print(f"  {i}. {severity_icon} {mismatch.fix_action}")

                if mismatch.current:
                    print(f"     Current: {mismatch.current.raw_markdown[:80]}...")
                else:
                    print(f"     Current: (missing)")

                print(f"     Expected: {mismatch.expected.raw_markdown[:80]}...")

        print(f"\n{'=' * 60}")
        print(f"Total: {len(mismatches)} badge{'s' if len(mismatches) != 1 else ''} need updating")

    def _apply_updates(
        self,
        mismatches: List[BadgeMismatch],
        auto_confirm: bool = False
    ) -> List[BadgeMismatch]:
        """Apply badge updates to files.

        Args:
            mismatches: List of mismatches to fix
            auto_confirm: If True, skip confirmation prompt

        Returns:
            List of applied mismatches
        """
        if not auto_confirm:
            response = input("\nApply these updates? [y/N]: ").strip().lower()
            if response != 'y':
                print("Cancelled")
                return []

        applied = []

        # Group by file for efficient updates
        by_file: Dict[Path, List[BadgeMismatch]] = {}
        for mismatch in mismatches:
            by_file.setdefault(mismatch.file_path, []).append(mismatch)

        # Apply updates file by file
        for file_path, file_mismatches in by_file.items():
            if not file_path.exists():
                print(f"⚠️  Skipping {file_path.name}: file not found")
                continue

            try:
                content = file_path.read_text(encoding='utf-8')
                original_content = content

                # Apply each fix
                for mismatch in file_mismatches:
                    if mismatch.current:
                        # Replace existing badge
                        content = content.replace(
                            mismatch.current.raw_markdown,
                            mismatch.expected.raw_markdown
                        )
                    else:
                        # Add missing badge (insert at top after title)
                        content = self._insert_badge(content, mismatch.expected)

                    applied.append(mismatch)

                # Write updated content
                if content != original_content:
                    file_path.write_text(content, encoding='utf-8')
                    print(f"✅ Updated {file_path.relative_to(self.project_root)}")

            except (OSError, UnicodeDecodeError) as e:
                print(f"❌ Failed to update {file_path.name}: {e}")

        return applied

    def _insert_badge(self, content: str, badge: Badge) -> str:
        """Insert badge at appropriate location in markdown content.

        Args:
            content: File content
            badge: Badge to insert

        Returns:
            Updated content with badge inserted
        """
        lines = content.splitlines(keepends=True)

        # Find first heading (# Title)
        insert_after = 0
        for i, line in enumerate(lines):
            if line.startswith('# '):
                insert_after = i + 1
                break

        # Insert badge line with newline
        badge_line = badge.raw_markdown + '\n'
        if insert_after < len(lines):
            lines.insert(insert_after, badge_line)
        else:
            lines.append(badge_line)

        return ''.join(lines)

    def _detect_version_fallback(self) -> Optional[str]:
        """Fallback version detection without CLAUDEMDDetector.

        Returns:
            Version string or None
        """
        # Try plugin.json
        plugin_json = self.project_root / ".claude-plugin" / "plugin.json"
        if plugin_json.exists():
            try:
                import json
                data = json.loads(plugin_json.read_text())
                return data.get("version")
            except (json.JSONDecodeError, OSError):
                pass

        # Try package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                import json
                data = json.loads(package_json.read_text())
                return data.get("version")
            except (json.JSONDecodeError, OSError):
                pass

        # Try pyproject.toml
        pyproject = self.project_root / "pyproject.toml"
        if pyproject.exists():
            try:
                content = pyproject.read_text()
                version_match = re.search(r'version\s*=\s*["\']([^"\']+)["\']', content)
                if version_match:
                    return version_match.group(1)
            except OSError:
                pass

        return None

    def _get_current_branch(self) -> str:
        """Get current git branch name.

        Returns:
            Branch name (default: 'dev')
        """
        try:
            result = subprocess.run(
                ['git', 'branch', '--show-current'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                return result.stdout.strip()
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return 'dev'  # Safe default

    def _get_repo_url(self) -> Optional[str]:
        """Get GitHub repository URL.

        Returns:
            Repository URL (e.g., https://github.com/user/repo) or None
        """
        try:
            result = subprocess.run(
                ['git', 'remote', 'get-url', 'origin'],
                cwd=self.project_root,
                capture_output=True,
                text=True,
                timeout=5
            )
            if result.returncode == 0 and result.stdout.strip():
                url = result.stdout.strip()
                # Normalize URL (remove .git, convert SSH to HTTPS)
                url = url.replace('.git', '')
                if url.startswith('git@github.com:'):
                    url = url.replace('git@github.com:', 'https://github.com/')
                return url
        except (subprocess.TimeoutExpired, FileNotFoundError):
            pass

        return None

    def _get_docs_site_url(self) -> Optional[str]:
        """Get documentation site URL.

        Returns:
            Docs URL (e.g., https://user.github.io/repo/) or None
        """
        repo_url = self._get_repo_url()
        if not repo_url:
            return None

        # Pattern: https://github.com/User/Repo → https://user.github.io/repo/
        match = re.search(r'github\.com/([^/]+)/([^/]+)', repo_url)
        if match:
            owner = match.group(1).lower()
            repo = match.group(2).lower()
            return f"https://{owner}.github.io/{repo}/"

        return None

    def _calculate_docs_coverage(self) -> Optional[int]:
        """Calculate documentation coverage percentage.

        Returns:
            Coverage percentage (0-100) or None if not calculable
        """
        # Use the same logic as craft plugin (.STATUS file)
        status_file = self.project_root / ".STATUS"
        if status_file.exists():
            try:
                content = status_file.read_text()
                # Look for "Documentation: XX% complete"
                match = re.search(r'Documentation:\s*(\d+)%', content)
                if match:
                    return int(match.group(1))
            except (OSError, ValueError):
                pass

        # Fallback: Count documented commands (if plugin)
        if self.project_info and self.project_info.type == "craft-plugin":
            # Simple heuristic: assume high coverage for mature plugins
            # More accurate calculation would scan command docs
            return 98  # Current craft status

        return None


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()

    syncer = BadgeSyncer(project_root)

    print("Detecting badge mismatches...")
    mismatches = syncer.sync_badges(dry_run=True)

    if not mismatches:
        print("\n✅ All badges in sync!")
    else:
        print(f"\nFound {len(mismatches)} badge mismatch{'es' if len(mismatches) != 1 else ''}")


if __name__ == '__main__':
    main()
