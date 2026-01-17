#!/usr/bin/env python3
"""
Parser for .linkcheck-ignore files.

Parses markdown-formatted ignore files that document known broken links
in categories (test files, brainstorm references, external links, etc.).

Format:
    # Known Broken Links

    ### 1. Category Name
    File: path/to/file.md
    - Purpose: Why this is ignored

    Files with broken links:
    - `file1.md`
    - `file2.md`

    Target: ../target.md
"""

import re
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from dataclasses import dataclass, field
import fnmatch


@dataclass
class IgnorePattern:
    """Represents a single ignore pattern."""
    category: str
    files: List[str] = field(default_factory=list)  # File patterns (can be glob)
    targets: List[str] = field(default_factory=list)  # Target patterns (can be glob)
    reason: Optional[str] = None


@dataclass
class IgnoreRules:
    """Collection of ignore patterns organized by category."""
    patterns: List[IgnorePattern] = field(default_factory=list)

    def should_ignore(self, source_file: str, target_link: str) -> Tuple[bool, Optional[str]]:
        """
        Check if a broken link should be ignored.

        Args:
            source_file: Path to the file containing the link
            target_link: The broken link target

        Returns:
            (should_ignore, category) tuple
        """
        for pattern in self.patterns:
            # Check if source file matches any file pattern
            file_match = any(
                fnmatch.fnmatch(source_file, file_pattern) or source_file == file_pattern
                for file_pattern in pattern.files
            )

            if not file_match:
                continue

            # If targets list is empty, ignore all links from this file
            if not pattern.targets:
                return True, pattern.category

            # Check if target matches any target pattern
            # Normalize paths for comparison (handle docs/brainstorm vs ../brainstorm)
            target_match = any(
                fnmatch.fnmatch(target_link, target_pattern) or
                target_link == target_pattern or
                target_link.endswith(target_pattern) or
                target_pattern in target_link or
                # Handle docs/path vs ../path normalization
                fnmatch.fnmatch(target_link.replace('../', 'docs/'), target_pattern) or
                fnmatch.fnmatch(target_link, target_pattern.replace('docs/', '../'))
                for target_pattern in pattern.targets
            )

            if target_match:
                return True, pattern.category

        return False, None

    def get_categories(self) -> List[str]:
        """Get list of all categories."""
        return list(set(p.category for p in self.patterns))

    def get_patterns_by_category(self, category: str) -> List[IgnorePattern]:
        """Get all patterns for a specific category."""
        return [p for p in self.patterns if p.category == category]


def parse_linkcheck_ignore(filepath: str = ".linkcheck-ignore") -> IgnoreRules:
    """
    Parse .linkcheck-ignore file and return ignore rules.

    Args:
        filepath: Path to .linkcheck-ignore file

    Returns:
        IgnoreRules object containing parsed patterns

    Raises:
        FileNotFoundError: If file doesn't exist (caller should handle gracefully)
    """
    path = Path(filepath)

    if not path.exists():
        # Return empty rules - caller decides how to handle
        return IgnoreRules()

    rules = IgnoreRules()
    current_category = "uncategorized"
    current_pattern = None
    in_files_section = False
    in_targets_section = False

    with path.open('r', encoding='utf-8') as f:
        for line in f:
            line = line.rstrip()

            # Skip empty lines
            if not line.strip():
                continue

            # Skip top-level headers (## Purpose, ## Build Status, etc.)
            if line.startswith('## ') and not line.startswith('### '):
                continue

            # Category headers (### 1. Category Name)
            if line.startswith('### '):
                # Save current pattern before starting new category
                if current_pattern and (current_pattern.files or current_pattern.targets):
                    rules.patterns.append(current_pattern)

                # Extract category name (remove numbers and parenthetical notes)
                category_text = line.lstrip('#').strip()
                category_text = re.sub(r'^\d+\.\s*', '', category_text)  # Remove "1. "
                category_text = re.sub(r'\s*\([^)]+\)\s*$', '', category_text)  # Remove "(Note)"
                current_category = category_text.strip()
                current_pattern = IgnorePattern(category=current_category)
                in_files_section = False
                in_targets_section = False
                continue

            # "Files with broken links:" subsection
            if 'Files with broken links:' in line or 'File with broken links:' in line:
                if not current_pattern:
                    current_pattern = IgnorePattern(category=current_category)
                in_files_section = True
                in_targets_section = False
                continue

            # Single "File:" line
            file_match = re.match(r'^File:\s*`?([^`\s]+)`?', line)
            if file_match:
                if not current_pattern:
                    current_pattern = IgnorePattern(category=current_category)
                current_pattern.files.append(file_match.group(1))
                in_files_section = False
                in_targets_section = False
                continue

            # "Targets:" header line with or without value
            targets_match = re.match(r'^Targets?:\s*(.*)$', line)
            if targets_match:
                if not current_pattern:
                    current_pattern = IgnorePattern(category=current_category)
                target_text = targets_match.group(1).strip()

                # If target_text is provided on same line, add it
                if target_text and target_text not in ['', '`', '``']:
                    # Remove backticks and parenthetical notes
                    target_text = target_text.replace('`', '')
                    target_text = target_text.split('(')[0].strip()
                    if target_text:
                        current_pattern.targets.append(target_text)

                # Mark that we're in targets section for bullet lists
                in_files_section = False
                in_targets_section = True
                continue

            # Single "Target:" line
            target_match = re.match(r'^Target:\s*`?([^`(]+)`?', line)
            if target_match:
                if not current_pattern:
                    current_pattern = IgnorePattern(category=current_category)
                target_text = target_match.group(1).strip()
                target_text = target_text.split('(')[0].strip()
                current_pattern.targets.append(target_text)
                in_files_section = False
                in_targets_section = False
                continue

            # Bullet list items
            if line.startswith('- '):
                # Skip special lines (Reason, Purpose, Fix, etc.)
                if any(line.startswith(f'- {keyword}:') for keyword in ['Reason', 'Purpose', 'Fix', 'Should', 'Contains', 'Links', 'Brainstorm']):
                    # Try to capture reason
                    if current_pattern and (line.startswith('- Reason:') or line.startswith('- Purpose:')):
                        reason_text = re.sub(r'^-\s*(?:Reason|Purpose):\s*', '', line).strip()
                        if not current_pattern.reason:
                            current_pattern.reason = reason_text
                    continue

                # Extract backtick-enclosed paths
                backtick_match = re.search(r'`([^`]+)`', line)
                if backtick_match:
                    path_text = backtick_match.group(1)

                    if not current_pattern:
                        current_pattern = IgnorePattern(category=current_category)

                    # Add to files or targets based on section
                    if in_files_section:
                        current_pattern.files.append(path_text)
                    elif in_targets_section:
                        current_pattern.targets.append(path_text)
                    else:
                        # Default: docs/ paths are files, ../ paths are targets
                        if path_text.startswith('docs/'):
                            current_pattern.files.append(path_text)
                        elif path_text.startswith('../'):
                            current_pattern.targets.append(path_text)

    # Add final pattern
    if current_pattern and (current_pattern.files or current_pattern.targets):
        rules.patterns.append(current_pattern)

    return rules


def main():
    """Test the parser with .linkcheck-ignore file."""
    try:
        rules = parse_linkcheck_ignore()
        print(f"Parsed {len(rules.patterns)} ignore patterns")
        print(f"Categories: {', '.join(rules.get_categories())}")
        print()

        # Show all patterns
        for i, pattern in enumerate(rules.patterns, 1):
            print(f"{i}. {pattern.category}")
            print(f"   Files: {pattern.files}")
            print(f"   Targets: {pattern.targets}")
            if pattern.reason:
                print(f"   Reason: {pattern.reason}")
            print()

        # Test some examples
        test_cases = [
            ("docs/test-violations.md", "nonexistent.md"),
            ("docs/specs/SPEC-teaching-workflow-2026-01-16.md", "../brainstorm/BRAINSTORM-teaching.md"),
            ("docs/TEACHING-DOCS-INDEX.md", "../README.md"),
            ("docs/teaching-migration.md", "../commands/site/publish.md"),
            ("docs/guide/setup.md", "missing.md"),  # Should not be ignored
        ]

        print("Test cases:")
        for source, target in test_cases:
            should_ignore, category = rules.should_ignore(source, target)
            status = "IGNORE" if should_ignore else "CRITICAL"
            cat_text = f" ({category})" if category else ""
            print(f"  {status}: {source} → {target}{cat_text}")

    except FileNotFoundError:
        print("Error: .linkcheck-ignore file not found")
    except Exception as e:
        import traceback
        print(f"Error: {e}")
        traceback.print_exc()


if __name__ == "__main__":
    main()
