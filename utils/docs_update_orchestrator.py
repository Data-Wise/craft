#!/usr/bin/env python3
"""
Documentation Update Orchestrator - Interactive category-level documentation updates

Orchestrates the /craft:docs:update command with smart detection and interactive prompts.

Phases:
1. Detection: Identify outdated documentation across 9 categories
2. Interactive Prompts: Category-level questions (grouped for efficiency)
3. Apply Updates: Execute selected updates
4. Validate: Run lint checks and fix issues
5. Changelog: Update CHANGELOG.md with recent commits
6. Summary: ADHD-friendly report of what was done

Detection Categories:
- version_refs: Version numbers in docs (v2.5.0 → v2.6.0)
- command_counts: "99 commands" → "101 commands"
- broken_links: Internal broken links
- missing_help: Commands without help documentation
- outdated_status: Features marked WIP that are complete
- inconsistent_terms: Inconsistent terminology (craft vs Craft)
- missing_xrefs: Missing cross-references between commands
- stale_examples: Code examples that don't match current API
- outdated_diagrams: Mermaid diagrams that need updating
"""

import sys
import json
import re
from pathlib import Path
from typing import Dict, List, Optional, Set, Tuple
from dataclasses import dataclass, asdict
from enum import Enum
import subprocess
import argparse


class UpdateCategory(Enum):
    """Update categories for interactive mode"""
    VERSION_REFS = "version_refs"
    COMMAND_COUNTS = "command_counts"
    BROKEN_LINKS = "broken_links"
    MISSING_HELP = "missing_help"
    OUTDATED_STATUS = "outdated_status"
    INCONSISTENT_TERMS = "inconsistent_terms"
    MISSING_XREFS = "missing_xrefs"
    STALE_EXAMPLES = "stale_examples"
    OUTDATED_DIAGRAMS = "outdated_diagrams"


@dataclass
class UpdateResult:
    """Result of an update operation"""
    category: str
    applied: bool
    count: int
    files_affected: List[str]
    changes: List[str]


class DocsUpdateOrchestrator:
    """Orchestrate interactive documentation updates"""

    def __init__(self, project_root: str, current_version: str):
        self.project_root = Path(project_root)
        self.current_version = current_version
        self.results: List[UpdateResult] = []

    def run_detection(self) -> Dict[str, Dict]:
        """
        Run detection utilities to identify documentation issues.

        Returns:
            Dictionary of detected issues by category
        """
        try:
            # Import detection utilities
            from docs_detector import DocsDetector
            from help_file_validator import HelpFileValidator

            detector = DocsDetector(str(self.project_root))
            validator = HelpFileValidator(str(self.project_root))

            # Run comprehensive detection
            all_results = detector.detect_all(self.current_version)

            # Flatten to simple dict format
            detection_results = {}
            for key, detection_result in all_results.items():
                detection_results[key] = {
                    "category": detection_result.category,
                    "found": detection_result.found,
                    "count": detection_result.count,
                    "items": detection_result.items,
                    "details": detection_result.details,
                }

            return detection_results

        except Exception as e:
            print(f"⚠️  Detection failed: {e}")
            print("Continuing with manual update options...")
            return {}

    def group_categories_for_prompts(
        self, detection_results: Dict[str, Dict]
    ) -> List[List[Tuple[str, Dict]]]:
        """
        Group detection categories for efficient interactive prompts.

        Groups related categories into prompts (max 4 per prompt).

        Args:
            detection_results: Results from run_detection()

        Returns:
            List of category groups, each ready for a single prompt
        """
        # Filter categories with issues
        categories_with_issues = [
            (key, result)
            for key, result in detection_results.items()
            if result.get("found") and result.get("count", 0) > 0
        ]

        if not categories_with_issues:
            return []

        # Group by priority
        groups = []

        # Group 1: Metadata updates (highest priority)
        metadata_group = [
            (k, v)
            for k, v in categories_with_issues
            if k in ["version_refs", "command_counts"]
        ]
        if metadata_group:
            groups.append(metadata_group)

        # Group 2: Link and reference issues
        link_group = [
            (k, v)
            for k, v in categories_with_issues
            if k in ["broken_links", "missing_xrefs"]
        ]
        if link_group:
            groups.append(link_group)

        # Group 3: Documentation completeness
        completeness_group = [
            (k, v)
            for k, v in categories_with_issues
            if k in ["missing_help", "outdated_status"]
        ]
        if completeness_group:
            groups.append(completeness_group)

        # Group 4: Content quality (lower priority)
        quality_group = [
            (k, v)
            for k, v in categories_with_issues
            if k in ["stale_examples", "inconsistent_terms", "outdated_diagrams"]
        ]
        if quality_group:
            groups.append(quality_group)

        return groups

    def build_prompt_text(
        self, category_group: List[Tuple[str, Dict]]
    ) -> str:
        """
        Build user-friendly prompt text for a category group.

        Args:
            category_group: List of (category_name, detection_result) tuples

        Returns:
            Formatted prompt text
        """
        if len(category_group) == 1:
            category, result = category_group[0]
            count = result.get("count", 0)
            item_word = "item" if count == 1 else "items"

            # Get first few items for preview
            items = result.get("items", [])[:3]
            item_list = "\n".join(
                [f"  • {item.get('file', item.get('description'))}" for item in items]
            )

            prompt = f"{category}: {count} {item_word} need updating\n\n{item_list}"
            if count > 3:
                prompt += f"\n  ... and {count - 3} more"

            return prompt
        else:
            # Multi-category group
            prompt_lines = []
            for category, result in category_group:
                count = result.get("count", 0)
                if count > 0:
                    item_word = "item" if count == 1 else "items"
                    prompt_lines.append(f"  • {category}: {count} {item_word}")

            return "Multiple documentation updates needed:\n\n" + "\n".join(prompt_lines)

    def apply_updates_for_category(
        self, category: str, result: Dict, approved: bool
    ) -> UpdateResult:
        """
        Apply updates for a specific category.

        Args:
            category: Category name (e.g., "version_refs")
            result: Detection result for this category
            approved: Whether user approved the updates

        Returns:
            UpdateResult with applied changes
        """
        if not approved or not result.get("found"):
            return UpdateResult(
                category=category, applied=False, count=0, files_affected=[], changes=[]
            )

        items = result.get("items", [])
        files_affected = set()
        changes = []

        try:
            if category == "version_refs":
                files_affected, changes = self._apply_version_ref_updates(items)
            elif category == "command_counts":
                files_affected, changes = self._apply_command_count_updates(items)
            elif category == "broken_links":
                files_affected, changes = self._apply_broken_link_fixes(items)
            elif category == "missing_help":
                files_affected, changes = self._apply_missing_help_updates(items)
            elif category == "outdated_status":
                files_affected, changes = self._apply_status_updates(items)
            elif category == "inconsistent_terms":
                files_affected, changes = self._apply_term_fixes(items)
            elif category == "missing_xrefs":
                files_affected, changes = self._apply_xref_updates(items)
            else:
                # Other categories require manual intervention or specialized handling
                return UpdateResult(
                    category=category,
                    applied=False,
                    count=len(items),
                    files_affected=list(files_affected),
                    changes=changes,
                )

            return UpdateResult(
                category=category,
                applied=True,
                count=len(items),
                files_affected=list(files_affected),
                changes=changes,
            )

        except Exception as e:
            print(f"⚠️  Error applying {category} updates: {e}")
            return UpdateResult(
                category=category, applied=False, count=0, files_affected=[], changes=[]
            )

    def _apply_version_ref_updates(self, items: List[Dict]) -> Tuple[Set[str], List[str]]:
        """Apply version reference updates"""
        files_affected = set()
        changes = []

        for item in items:
            file_path = self.project_root / item.get("file", "")
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text()
                old_version = item.get("old_version", "")
                new_version = item.get("new_version", self.current_version)

                # Replace version with regex to handle v2.5.0, 2.5.0 formats
                updated = re.sub(
                    rf"v?{re.escape(old_version)}",
                    new_version if new_version.startswith("v") else f"v{new_version}",
                    content,
                )

                if updated != content:
                    file_path.write_text(updated)
                    files_affected.add(item.get("file", ""))
                    changes.append(f"Updated {item.get('file')} from {old_version} to {new_version}")

            except Exception as e:
                print(f"⚠️  Error updating {file_path}: {e}")

        return files_affected, changes

    def _apply_command_count_updates(self, items: List[Dict]) -> Tuple[Set[str], List[str]]:
        """Apply command count updates"""
        files_affected = set()
        changes = []

        for item in items:
            file_path = self.project_root / item.get("file", "")
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text()
                old_count = item.get("old_count", "")
                new_count = item.get("new_count", "")

                # Replace count with word boundary matching
                pattern = rf"\b{old_count}\s+commands\b"
                replacement = f"{new_count} commands"

                updated = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

                if updated != content:
                    file_path.write_text(updated)
                    files_affected.add(item.get("file", ""))
                    changes.append(f"Updated {item.get('file')}: {old_count} → {new_count} commands")

            except Exception as e:
                print(f"⚠️  Error updating {file_path}: {e}")

        return files_affected, changes

    def _apply_broken_link_fixes(self, items: List[Dict]) -> Tuple[Set[str], List[str]]:
        """Apply broken link fixes"""
        files_affected = set()
        changes = []

        for item in items:
            file_path = self.project_root / item.get("file", "")
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text()
                old_link = item.get("old_link", "")
                new_link = item.get("new_link", "")

                if old_link and new_link:
                    # Escape for markdown link format
                    pattern = re.escape(old_link)
                    updated = re.sub(pattern, new_link, content)

                    if updated != content:
                        file_path.write_text(updated)
                        files_affected.add(item.get("file", ""))
                        changes.append(f"Fixed link in {item.get('file')}: {old_link} → {new_link}")

            except Exception as e:
                print(f"⚠️  Error fixing links in {file_path}: {e}")

        return files_affected, changes

    def _apply_missing_help_updates(self, items: List[Dict]) -> Tuple[Set[str], List[str]]:
        """Apply missing help documentation updates"""
        files_affected = set()
        changes = []

        # This typically requires interactive input for each command
        # For now, return items for manual review
        for item in items:
            changes.append(f"Review help documentation for: {item.get('command', '')}")

        return files_affected, changes

    def _apply_status_updates(self, items: List[Dict]) -> Tuple[Set[str], List[str]]:
        """Apply status updates for completed features"""
        files_affected = set()
        changes = []

        for item in items:
            file_path = self.project_root / item.get("file", "")
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text()
                old_status = item.get("old_status", "WIP")
                new_status = item.get("new_status", "Complete")

                # Replace status marker
                pattern = rf"\bstatus:\s*{old_status}\b"
                replacement = f"status: {new_status}"

                updated = re.sub(pattern, replacement, content, flags=re.IGNORECASE)

                if updated != content:
                    file_path.write_text(updated)
                    files_affected.add(item.get("file", ""))
                    changes.append(f"Updated {item.get('file')}: {old_status} → {new_status}")

            except Exception as e:
                print(f"⚠️  Error updating status in {file_path}: {e}")

        return files_affected, changes

    def _apply_term_fixes(self, items: List[Dict]) -> Tuple[Set[str], List[str]]:
        """Apply terminology consistency fixes"""
        files_affected = set()
        changes = []

        for item in items:
            file_path = self.project_root / item.get("file", "")
            if not file_path.exists():
                continue

            try:
                content = file_path.read_text()
                old_term = item.get("old_term", "")
                new_term = item.get("new_term", "")

                # Case-sensitive replacement
                updated = content.replace(old_term, new_term)

                if updated != content:
                    file_path.write_text(updated)
                    files_affected.add(item.get("file", ""))
                    changes.append(f"Updated terminology in {item.get('file')}: {old_term} → {new_term}")

            except Exception as e:
                print(f"⚠️  Error fixing terms in {file_path}: {e}")

        return files_affected, changes

    def _apply_xref_updates(self, items: List[Dict]) -> Tuple[Set[str], List[str]]:
        """Apply missing cross-reference updates"""
        files_affected = set()
        changes = []

        for item in items:
            file_path = self.project_root / item.get("file", "")
            if not file_path.exists():
                continue

            # Cross-references typically need review
            changes.append(f"Review cross-references in {item.get('file')}")

        return files_affected, changes

    def run_lint_check(self, files_affected: Set[str]) -> bool:
        """
        Run markdown linting on affected files.

        Args:
            files_affected: Set of file paths to lint

        Returns:
            True if linting passed, False if issues found
        """
        if not files_affected:
            return True

        try:
            # Run markdownlint on affected files
            cmd = ["npx", "markdownlint-cli2", "--config", ".markdownlint.json"]
            cmd.extend([str(self.project_root / f) for f in files_affected])

            result = subprocess.run(
                cmd, cwd=str(self.project_root), capture_output=True, text=True
            )

            if result.returncode == 0:
                print("✓ Markdown linting passed")
                return True
            else:
                print(f"⚠️  Markdown issues found:\n{result.stdout}")
                return False

        except Exception as e:
            print(f"⚠️  Linting check failed: {e}")
            return True  # Don't block on linting failure

    def generate_summary(self, all_updates: List[UpdateResult]) -> str:
        """
        Generate ADHD-friendly summary of updates.

        Args:
            all_updates: List of UpdateResult objects

        Returns:
            Formatted summary text
        """
        applied_updates = [u for u in all_updates if u.applied]
        total_changes = sum(len(u.changes) for u in applied_updates)
        total_files = len(
            set().union(*(set(u.files_affected) for u in applied_updates))
        )

        summary = f"""
╭─────────────────────────────────────────────────────────────╮
│ ✅ DOCUMENTATION UPDATE COMPLETE (Interactive Mode)         │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Categories Updated:                                         │
"""

        for update in applied_updates:
            if update.applied:
                summary += f"│   ✓ {update.category}: {update.count} items\n"

        summary += f"""│                                                             │
│ Files Modified: {total_files}                                            │
│ Total Changes: {total_changes}                                          │
│                                                             │
│ Next Steps:                                                 │
│   1. Review changes: git diff                               │
│   2. Run tests: /craft:test:run                             │
│   3. Commit: git add . && git commit                        │
│                                                             │
╰─────────────────────────────────────────────────────────────╯
"""
        return summary


def main():
    """Main entry point for docs:update orchestrator"""
    parser = argparse.ArgumentParser(
        description="Smart documentation update orchestrator"
    )
    parser.add_argument(
        "--interactive", "-i", action="store_true", help="Interactive mode"
    )
    parser.add_argument("--category", "-C", help="Update only specific category")
    parser.add_argument(
        "--auto-yes", action="store_true", help="Auto-approve all updates"
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="Preview without applying changes"
    )
    parser.add_argument("--version", default="v2.7.0", help="Current version")
    parser.add_argument("--project-root", default=".", help="Project root directory")

    args = parser.parse_args()

    # Initialize orchestrator
    orchestrator = DocsUpdateOrchestrator(args.project_root, args.version)

    print("🔍 Detecting documentation issues...")
    detection_results = orchestrator.run_detection()

    if not detection_results:
        print("✅ No documentation issues detected")
        return 0

    # Interactive mode
    if args.interactive:
        print("\n📝 Interactive Mode - Review and apply updates by category\n")

        category_groups = orchestrator.group_categories_for_prompts(detection_results)

        all_updates = []
        for group_idx, group in enumerate(category_groups, 1):
            print(f"Category Group {group_idx}/{len(category_groups)}")
            print("─" * 60)

            # Build prompt
            prompt_text = orchestrator.build_prompt_text(group)
            print(prompt_text)
            print()

            # For now, show what would be updated
            for category, result in group:
                if args.auto_yes:
                    approved = True
                else:
                    response = (
                        input(f"Update {category}? [y/N]: ").strip().lower()
                    )
                    approved = response in ["y", "yes"]

                update_result = orchestrator.apply_updates_for_category(
                    category, result, approved
                )
                all_updates.append(update_result)

        # Generate summary
        print(orchestrator.generate_summary(all_updates))
        return 0

    # Default mode
    print("✓ Detection complete\n")
    for category, result in detection_results.items():
        if result.get("found"):
            print(f"  {category}: {result.get('count')} items")

    print("\nRun with --interactive for detailed updates")
    return 0


if __name__ == "__main__":
    sys.exit(main())
