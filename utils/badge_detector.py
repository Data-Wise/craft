#!/usr/bin/env python3
"""
Badge Detector - Parse and Classify Badges in Markdown Files

Detects badges in markdown files (README.md, docs/index.md) and classifies them
by type (version, CI status, coverage, custom). Provides location metadata for
targeted badge updates.

Version: 1.0.0
Author: Craft Plugin
"""

import re
from dataclasses import dataclass
from enum import Enum
from pathlib import Path
from typing import List, Dict, Optional


class BadgeType(Enum):
    """Badge type classification."""
    VERSION = "version"
    CI_STATUS = "ci_status"
    DOCS_COVERAGE = "docs_coverage"
    TEST_COVERAGE = "test_coverage"
    CUSTOM = "custom"


@dataclass
class Badge:
    """Represents a badge in markdown."""
    type: BadgeType
    label: str                    # Badge label text
    url: str                      # Badge image URL
    link_url: Optional[str]       # Clickable link URL (None if not linked)
    raw_markdown: str             # Original markdown text
    file_path: Path               # Source file
    line_number: int              # Line location (1-indexed)

    def __repr__(self) -> str:
        """String representation for debugging."""
        link_info = f" -> {self.link_url}" if self.link_url else ""
        return f"<Badge {self.type.value}: {self.label!r} at {self.file_path.name}:{self.line_number}{link_info}>"


class BadgeDetector:
    """Badge detection and parsing for markdown files."""

    # Regex patterns for badge detection
    BADGE_LINKED = re.compile(
        r'\[!\[([^\]]*)\]\(([^\)]+)\)\]\(([^\)]+)\)'  # [![label](img)](link)
    )
    BADGE_UNLINKED = re.compile(
        r'!\[([^\]]*)\]\(([^\)]+)\)'  # ![label](img)
    )

    def __init__(self, project_root: Path = None):
        """Initialize badge detector.

        Args:
            project_root: Project directory path (default: current directory)
        """
        self.project_root = Path(project_root) if project_root else Path.cwd()

    def detect_all(self, files: Optional[List[str]] = None) -> Dict[Path, List[Badge]]:
        """Detect all badges in specified files.

        Args:
            files: List of file paths relative to project_root.
                   Defaults to ['README.md', 'docs/index.md']

        Returns:
            Dictionary mapping file paths to lists of Badge objects
        """
        if files is None:
            files = ['README.md', 'docs/index.md']

        results = {}
        for file_rel in files:
            file_path = self.project_root / file_rel
            if file_path.exists():
                badges = self.parse_badges(file_path)
                if badges:
                    results[file_path] = badges

        return results

    def parse_badges(self, file_path: Path) -> List[Badge]:
        """Parse badges from a single markdown file.

        Args:
            file_path: Absolute path to markdown file

        Returns:
            List of Badge objects found in file
        """
        if not file_path.exists():
            return []

        try:
            content = file_path.read_text(encoding='utf-8')
        except (OSError, UnicodeDecodeError):
            return []

        badges = []
        for line_num, line in enumerate(content.splitlines(), start=1):
            # Try linked badges first (more specific pattern)
            for match in self.BADGE_LINKED.finditer(line):
                label = match.group(1)
                img_url = match.group(2)
                link_url = match.group(3)
                raw_md = match.group(0)

                badge_type = self._classify_badge(label, img_url)
                badges.append(Badge(
                    type=badge_type,
                    label=label,
                    url=img_url,
                    link_url=link_url,
                    raw_markdown=raw_md,
                    file_path=file_path,
                    line_number=line_num
                ))

            # Try unlinked badges (simpler pattern)
            # Skip if already matched by linked pattern
            if not self.BADGE_LINKED.search(line):
                for match in self.BADGE_UNLINKED.finditer(line):
                    label = match.group(1)
                    img_url = match.group(2)
                    raw_md = match.group(0)

                    badge_type = self._classify_badge(label, img_url)
                    badges.append(Badge(
                        type=badge_type,
                        label=label,
                        url=img_url,
                        link_url=None,
                        raw_markdown=raw_md,
                        file_path=file_path,
                        line_number=line_num
                    ))

        return badges

    def _classify_badge(self, label: str, url: str) -> BadgeType:
        """Classify badge by type based on label and URL.

        Classification priority:
        1. GitHub Actions URL -> CI_STATUS
        2. "version" in label -> VERSION
        3. "coverage" or "cov" in label -> TEST_COVERAGE or DOCS_COVERAGE
        4. shields.io with specific patterns -> appropriate type
        5. Default -> CUSTOM

        Args:
            label: Badge label text
            url: Badge image URL

        Returns:
            BadgeType classification
        """
        label_lower = label.lower()
        url_lower = url.lower()

        # Priority 1: GitHub Actions CI badges
        if 'github.com' in url_lower and 'actions/workflows' in url_lower:
            return BadgeType.CI_STATUS

        # Priority 2: Version badges
        if 'version' in label_lower or 'release' in label_lower:
            return BadgeType.VERSION

        # Priority 3: Coverage badges
        if 'coverage' in label_lower or 'cov' in label_lower:
            # Distinguish docs vs test coverage
            if 'doc' in label_lower or 'documentation' in label_lower:
                return BadgeType.DOCS_COVERAGE
            else:
                return BadgeType.TEST_COVERAGE

        # Priority 4: shields.io badge patterns
        if 'shields.io' in url_lower:
            # Version pattern: badge/version-X.Y.Z-color
            if '/badge/version-' in url_lower or '/v/' in url_lower:
                return BadgeType.VERSION

            # Coverage pattern: badge/coverage-XX%-color
            if '/badge/coverage-' in url_lower or 'codecov' in url_lower:
                if 'docs' in url_lower:
                    return BadgeType.DOCS_COVERAGE
                else:
                    return BadgeType.TEST_COVERAGE

        # Default: custom badge
        return BadgeType.CUSTOM

    def extract_version_from_badge(self, badge: Badge) -> Optional[str]:
        """Extract version string from a version badge.

        Args:
            badge: Badge object (should be VERSION type)

        Returns:
            Version string (e.g., "2.10.0-dev") or None if not extractable
        """
        if badge.type != BadgeType.VERSION:
            return None

        # Pattern 1: shields.io badge URL format
        # Example: badge/version-2.10.0--dev-blue.svg → "2.10.0-dev"
        # The version part is everything after "version-" until the last "-color"
        version_match = re.search(r'/badge/version-(.+?)-([a-z]+)(?:\.svg)?(?:\?|$)', badge.url)
        if version_match:
            # Shields.io escapes single dash as double dash
            version = version_match.group(1).replace('--', '-')
            return version

        # Pattern 2: shields.io /v/ format
        # Example: /v/2.10.0 → "2.10.0"
        v_match = re.search(r'/v/([0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9]+)?)', badge.url)
        if v_match:
            return v_match.group(1)

        # Pattern 3: GitHub releases badge
        # Example: github.com/.../release/v2.10.0 → "2.10.0"
        release_match = re.search(r'/release/v?([0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9]+)?)', badge.url)
        if release_match:
            return release_match.group(1)

        # Pattern 4: Version in label (fallback)
        # Example: "Version 2.10.0-dev" → "2.10.0-dev"
        label_match = re.search(r'v?([0-9]+\.[0-9]+\.[0-9]+(?:-[a-z0-9]+)?)', badge.label)
        if label_match:
            return label_match.group(1)

        return None

    def extract_workflow_name(self, badge: Badge) -> Optional[str]:
        """Extract workflow filename from a CI status badge.

        Args:
            badge: Badge object (should be CI_STATUS type)

        Returns:
            Workflow filename (e.g., "ci.yml") or None if not extractable
        """
        if badge.type != BadgeType.CI_STATUS:
            return None

        # Pattern: github.com/.../actions/workflows/FILENAME/badge.svg
        workflow_match = re.search(r'/actions/workflows/([^/]+)/badge\.svg', badge.url)
        if workflow_match:
            return workflow_match.group(1)

        return None

    def extract_branch_from_ci_badge(self, badge: Badge) -> Optional[str]:
        """Extract branch parameter from a CI status badge URL.

        Args:
            badge: Badge object (should be CI_STATUS type)

        Returns:
            Branch name (e.g., "dev") or None if not specified
        """
        if badge.type != BadgeType.CI_STATUS:
            return None

        # Pattern: badge.svg?branch=BRANCH_NAME
        branch_match = re.search(r'badge\.svg\?branch=([^&\)]+)', badge.url)
        if branch_match:
            return branch_match.group(1)

        return None

    def get_badges_by_type(
        self,
        badge_type: BadgeType,
        badges: Optional[Dict[Path, List[Badge]]] = None
    ) -> List[Badge]:
        """Filter badges by type.

        Args:
            badge_type: Type to filter for
            badges: Badge dictionary from detect_all(). If None, calls detect_all()

        Returns:
            List of badges matching the specified type
        """
        if badges is None:
            badges = self.detect_all()

        results = []
        for badge_list in badges.values():
            results.extend(b for b in badge_list if b.type == badge_type)

        return results

    def get_badges_by_file(
        self,
        file_path: Path,
        badges: Optional[Dict[Path, List[Badge]]] = None
    ) -> List[Badge]:
        """Get all badges from a specific file.

        Args:
            file_path: Absolute path to file
            badges: Badge dictionary from detect_all(). If None, calls detect_all()

        Returns:
            List of badges from the specified file
        """
        if badges is None:
            badges = self.detect_all()

        return badges.get(file_path, [])

    def format_badge_summary(self, badges: Dict[Path, List[Badge]]) -> str:
        """Format badge summary for display.

        Args:
            badges: Badge dictionary from detect_all()

        Returns:
            Formatted summary string
        """
        if not badges:
            return "No badges found"

        lines = []
        for file_path, badge_list in sorted(badges.items()):
            rel_path = file_path.relative_to(self.project_root)
            lines.append(f"\n📁 {rel_path}")

            # Group by type
            by_type: Dict[BadgeType, List[Badge]] = {}
            for badge in badge_list:
                by_type.setdefault(badge.type, []).append(badge)

            for badge_type in sorted(by_type.keys(), key=lambda t: t.value):
                count = len(by_type[badge_type])
                type_label = badge_type.value.replace('_', ' ').title()
                lines.append(f"  • {type_label}: {count} badge{'s' if count != 1 else ''}")

        return '\n'.join(lines)


def main():
    """CLI entry point for testing."""
    import sys

    if len(sys.argv) > 1:
        project_root = Path(sys.argv[1])
    else:
        project_root = Path.cwd()

    detector = BadgeDetector(project_root)
    badges = detector.detect_all()

    if not badges:
        print("No badges found")
        return

    print(f"Found {sum(len(b) for b in badges.values())} badges in {len(badges)} files")
    print(detector.format_badge_summary(badges))

    # Show details
    print("\n" + "=" * 60)
    for file_path, badge_list in badges.items():
        print(f"\n{file_path.relative_to(project_root)}:")
        for badge in badge_list:
            print(f"  Line {badge.line_number}: [{badge.type.value}] {badge.label}")
            if badge.type == BadgeType.VERSION:
                version = detector.extract_version_from_badge(badge)
                if version:
                    print(f"    Version: {version}")
            elif badge.type == BadgeType.CI_STATUS:
                workflow = detector.extract_workflow_name(badge)
                branch = detector.extract_branch_from_ci_badge(badge)
                if workflow:
                    print(f"    Workflow: {workflow}")
                if branch:
                    print(f"    Branch: {branch}")


if __name__ == '__main__':
    main()
