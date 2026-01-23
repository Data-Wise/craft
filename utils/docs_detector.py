#!/usr/bin/env python3
"""
Documentation Detector - Identify outdated documentation categories

Detects 9 types of documentation issues:
1. Version references (craft version in docs)
2. Command counts (99 commands, 21 skills, etc.)
3. Broken links (internal documentation)
4. Stale examples (code snippets that don't match current API)
5. Missing command documentation (commands without help)
6. Outdated status (completed features still marked WIP)
7. Inconsistent terminology (craft vs Craft)
8. Missing cross-references (related commands not linked)
9. Outdated architecture diagrams (Mermaid diagrams)
"""

import re
import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from collections import defaultdict


@dataclass
class DetectionResult:
    """Result of a detection check"""
    category: str
    found: bool
    count: int
    items: List[Dict[str, str]] = field(default_factory=list)
    details: str = ""

    def summary(self) -> str:
        """Human-readable summary"""
        if not self.found:
            return f"{self.category}: No issues found"

        item_desc = "item" if self.count == 1 else "items"
        return f"{self.category}: {self.count} {item_desc} need updating"


class DocsDetector:
    """Detect outdated documentation across 9 categories"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.docs_dir = self.project_root / "docs"
        self.commands_dir = self.project_root / "commands"

    def detect_all(self, current_version: str = None) -> Dict[str, DetectionResult]:
        """
        Run all 9 detection checks

        Args:
            current_version: Current craft version (e.g., "2.6.0")

        Returns:
            Dictionary of category -> DetectionResult
        """
        results = {}

        # 1. Version references
        results['version_refs'] = self.detect_version_references(current_version)

        # 2. Command counts
        results['command_counts'] = self.detect_command_counts()

        # 3. Broken links (requires external tool, placeholder)
        results['broken_links'] = self.detect_broken_links()

        # 4. Stale examples
        results['stale_examples'] = self.detect_stale_examples()

        # 5. Missing command documentation
        results['missing_help'] = self.detect_missing_help()

        # 6. Outdated status markers
        results['outdated_status'] = self.detect_outdated_status()

        # 7. Inconsistent terminology
        results['inconsistent_terms'] = self.detect_inconsistent_terminology()

        # 8. Missing cross-references
        results['missing_xrefs'] = self.detect_missing_cross_references()

        # 9. Outdated architecture diagrams
        results['outdated_diagrams'] = self.detect_outdated_diagrams()

        return results

    def detect_version_references(self, current_version: str = None) -> DetectionResult:
        """
        Detect outdated version references in documentation

        Searches for version patterns like:
        - "v2.5.0" in prose
        - "version: 2.5.0" in YAML
        - "Current Version: v2.5.0" in headers
        """
        if not current_version:
            # Try to read from .STATUS file
            status_file = self.project_root / ".STATUS"
            if status_file.exists():
                with open(status_file) as f:
                    for line in f:
                        if line.startswith("version:"):
                            current_version = line.split(":", 1)[1].strip()
                            break

        if not current_version:
            return DetectionResult("Version References", False, 0,
                                 details="No current version specified")

        # Normalize version (remove 'v' prefix if present)
        current_version = current_version.lstrip('v')

        outdated_refs = []
        version_pattern = re.compile(r'v?(\d+\.\d+\.\d+)')

        # Search docs/ and key files
        search_files = list(self.docs_dir.rglob("*.md")) if self.docs_dir.exists() else []
        search_files.extend([
            self.project_root / "README.md",
            self.project_root / "CLAUDE.md",
            self.project_root / "CHANGELOG.md"
        ])

        for file_path in search_files:
            if not file_path.exists():
                continue

            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Find all version references
            for match in version_pattern.finditer(content):
                found_version = match.group(1)
                if found_version != current_version:
                    # Get context (line containing the version)
                    line_num = content[:match.start()].count('\n') + 1
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    context = content[line_start:line_end].strip()

                    outdated_refs.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'line': line_num,
                        'old_version': found_version,
                        'new_version': current_version,
                        'context': context[:80] + '...' if len(context) > 80 else context
                    })

        return DetectionResult(
            "Version References",
            len(outdated_refs) > 0,
            len(outdated_refs),
            outdated_refs,
            f"Found {len(outdated_refs)} outdated version references"
        )

    def detect_command_counts(self) -> DetectionResult:
        """
        Detect outdated command/skill/agent counts

        Searches for patterns like:
        - "99 commands"
        - "21 skills"
        - "8 agents"
        """
        if not self.commands_dir.exists():
            return DetectionResult("Command Counts", False, 0,
                                 details="Commands directory not found")

        # Count actual commands, skills, agents
        actual_counts = self._count_plugin_elements()

        # Search for count references in docs
        outdated_counts = []
        count_patterns = [
            (r'(\d+)\s+commands?', 'commands', actual_counts['commands']),
            (r'(\d+)\s+skills?', 'skills', actual_counts['skills']),
            (r'(\d+)\s+agents?', 'agents', actual_counts['agents']),
        ]

        search_files = list(self.docs_dir.rglob("*.md")) if self.docs_dir.exists() else []
        search_files.extend([
            self.project_root / "README.md",
            self.project_root / "CLAUDE.md"
        ])

        for file_path in search_files:
            if not file_path.exists():
                continue

            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            for pattern, element_type, actual_count in count_patterns:
                for match in re.finditer(pattern, content, re.IGNORECASE):
                    found_count = int(match.group(1))
                    if found_count != actual_count:
                        line_num = content[:match.start()].count('\n') + 1
                        line_start = content.rfind('\n', 0, match.start()) + 1
                        line_end = content.find('\n', match.end())
                        if line_end == -1:
                            line_end = len(content)
                        context = content[line_start:line_end].strip()

                        outdated_counts.append({
                            'file': str(file_path.relative_to(self.project_root)),
                            'line': line_num,
                            'element_type': element_type,
                            'old_count': found_count,
                            'new_count': actual_count,
                            'context': context[:80] + '...' if len(context) > 80 else context
                        })

        return DetectionResult(
            "Command Counts",
            len(outdated_counts) > 0,
            len(outdated_counts),
            outdated_counts,
            f"Found {len(outdated_counts)} outdated count references"
        )

    def _count_plugin_elements(self) -> Dict[str, int]:
        """Count actual commands, skills, and agents"""
        counts = {'commands': 0, 'skills': 0, 'agents': 0}

        # Count commands (all .md files in commands/ directory)
        if self.commands_dir.exists():
            counts['commands'] = len(list(self.commands_dir.rglob("*.md")))

        # Count skills (check skills/ directory)
        skills_dir = self.project_root / "skills"
        if skills_dir.exists():
            counts['skills'] = len(list(skills_dir.glob("*.md")))

        # Count agents (check agents/ directory)
        agents_dir = self.project_root / "agents"
        if agents_dir.exists():
            counts['agents'] = len(list(agents_dir.glob("*.md")))

        return counts

    def detect_broken_links(self) -> DetectionResult:
        """
        Detect broken internal links

        Note: This is a placeholder - actual implementation should use
        /craft:docs:check-links or markdown-link-check
        """
        # Placeholder - would normally integrate with linkcheck tool
        return DetectionResult(
            "Broken Links",
            False,
            0,
            details="Use /craft:docs:check-links for link validation"
        )

    def detect_stale_examples(self) -> DetectionResult:
        """
        Detect stale code examples

        Looks for:
        - Old command syntax in examples
        - Removed flags in code blocks
        - Outdated API patterns
        """
        stale_examples = []

        # Common stale patterns
        stale_patterns = [
            (r'/craft:docs:feature', 'Old command (use /craft:docs:update instead)'),
            (r'/craft:docs:generate', 'Old command (use /craft:docs:update --force)'),
            (r'--mode\s+default', 'Old flag syntax (use --orch=default)'),
        ]

        search_files = list(self.docs_dir.rglob("*.md")) if self.docs_dir.exists() else []

        for file_path in search_files:
            if not file_path.exists():
                continue

            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Check if file contains code blocks
            in_code_block = False
            code_block_start = 0

            for i, line in enumerate(content.split('\n'), 1):
                if line.startswith('```'):
                    if in_code_block:
                        # End of code block
                        in_code_block = False
                    else:
                        # Start of code block
                        in_code_block = True
                        code_block_start = i

                if in_code_block:
                    for pattern, reason in stale_patterns:
                        if re.search(pattern, line):
                            stale_examples.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'pattern': pattern,
                                'reason': reason,
                                'context': line.strip()
                            })

        return DetectionResult(
            "Stale Examples",
            len(stale_examples) > 0,
            len(stale_examples),
            stale_examples,
            f"Found {len(stale_examples)} stale code examples"
        )

    def detect_missing_help(self) -> DetectionResult:
        """
        Detect commands missing help documentation

        Checks for:
        - Command files without YAML frontmatter
        - Missing description field
        - Incomplete arguments array
        """
        # This will be handled by help_file_validator.py
        # Placeholder implementation
        missing_help = []

        if self.commands_dir.exists():
            for cmd_file in self.commands_dir.rglob("*.md"):
                with open(cmd_file, encoding='utf-8') as f:
                    content = f.read()

                # Check for YAML frontmatter
                if not content.startswith('---'):
                    missing_help.append({
                        'file': str(cmd_file.relative_to(self.project_root)),
                        'issue': 'No YAML frontmatter',
                        'severity': 'high'
                    })
                else:
                    # Extract frontmatter
                    try:
                        _, frontmatter, _ = content.split('---', 2)
                        data = yaml.safe_load(frontmatter)

                        if not data or 'description' not in data:
                            missing_help.append({
                                'file': str(cmd_file.relative_to(self.project_root)),
                                'issue': 'Missing description field',
                                'severity': 'medium'
                            })
                    except Exception:
                        missing_help.append({
                            'file': str(cmd_file.relative_to(self.project_root)),
                            'issue': 'Invalid YAML frontmatter',
                            'severity': 'high'
                        })

        return DetectionResult(
            "Missing Help",
            len(missing_help) > 0,
            len(missing_help),
            missing_help,
            f"Found {len(missing_help)} commands with help issues"
        )

    def detect_outdated_status(self) -> DetectionResult:
        """
        Detect outdated status markers

        Looks for:
        - "WIP" or "In Progress" for completed features
        - "Complete" for features with recent commits
        - Status matrix inconsistencies
        """
        outdated_status = []

        # Search for status markers
        status_patterns = [
            (r'\bWIP\b', 'Work In Progress marker'),
            (r'\bIn Progress\b', 'In Progress marker'),
            (r'\bDraft\b', 'Draft status'),
            (r'\bPlanned\b', 'Planned status'),
        ]

        search_files = list(self.docs_dir.rglob("*.md")) if self.docs_dir.exists() else []
        search_files.append(self.project_root / "CLAUDE.md")

        for file_path in search_files:
            if not file_path.exists():
                continue

            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            for pattern, status_type in status_patterns:
                for match in re.finditer(pattern, content):
                    line_num = content[:match.start()].count('\n') + 1
                    line_start = content.rfind('\n', 0, match.start()) + 1
                    line_end = content.find('\n', match.end())
                    if line_end == -1:
                        line_end = len(content)
                    context = content[line_start:line_end].strip()

                    outdated_status.append({
                        'file': str(file_path.relative_to(self.project_root)),
                        'line': line_num,
                        'status_type': status_type,
                        'context': context[:80] + '...' if len(context) > 80 else context
                    })

        return DetectionResult(
            "Outdated Status",
            len(outdated_status) > 0,
            len(outdated_status),
            outdated_status,
            f"Found {len(outdated_status)} potential outdated status markers"
        )

    def detect_inconsistent_terminology(self) -> DetectionResult:
        """
        Detect inconsistent terminology

        Looks for:
        - "craft" vs "Craft" (should be consistent)
        - "command" vs "tool" (for same concept)
        - "flag" vs "option" inconsistencies
        """
        inconsistencies = []

        search_files = list(self.docs_dir.rglob("*.md")) if self.docs_dir.exists() else []
        search_files.extend([
            self.project_root / "README.md",
            self.project_root / "CLAUDE.md"
        ])

        for file_path in search_files:
            if not file_path.exists():
                continue

            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Check for mixed capitalization of "craft"
            lowercase_craft = len(re.findall(r'\bcraft\b', content))
            uppercase_craft = len(re.findall(r'\bCraft\b', content))

            # If both exist (not counting /craft: commands), flag it
            craft_commands = len(re.findall(r'/craft:', content))

            # Only count as inconsistent if we have mixed usage outside commands
            if lowercase_craft > craft_commands and uppercase_craft > 0:
                inconsistencies.append({
                    'file': str(file_path.relative_to(self.project_root)),
                    'issue': f'Mixed capitalization: {lowercase_craft} "craft", {uppercase_craft} "Craft"',
                    'type': 'capitalization'
                })

        return DetectionResult(
            "Inconsistent Terminology",
            len(inconsistencies) > 0,
            len(inconsistencies),
            inconsistencies,
            f"Found {len(inconsistencies)} terminology inconsistencies"
        )

    def detect_missing_cross_references(self) -> DetectionResult:
        """
        Detect missing cross-references between related commands

        Looks for:
        - Related commands not linked in "See Also" sections
        - Missing references to parent/child commands
        """
        missing_xrefs = []

        # Build command relationship map
        command_relationships = self._build_command_relationships()

        # Check each command file for cross-references
        if self.commands_dir.exists():
            for cmd_file in self.commands_dir.rglob("*.md"):
                with open(cmd_file, encoding='utf-8') as f:
                    content = f.read()

                cmd_name = self._extract_command_name(cmd_file)
                if not cmd_name:
                    continue

                # Get related commands
                related = command_relationships.get(cmd_name, [])

                # Check if related commands are mentioned
                for related_cmd in related:
                    if related_cmd not in content:
                        missing_xrefs.append({
                            'file': str(cmd_file.relative_to(self.project_root)),
                            'command': cmd_name,
                            'missing_reference': related_cmd,
                            'reason': 'Related command not mentioned'
                        })

        return DetectionResult(
            "Missing Cross-References",
            len(missing_xrefs) > 0,
            len(missing_xrefs),
            missing_xrefs,
            f"Found {len(missing_xrefs)} missing cross-references"
        )

    def detect_outdated_diagrams(self) -> DetectionResult:
        """
        Detect outdated Mermaid diagrams

        Looks for:
        - Diagrams mentioning removed commands
        - Workflow diagrams with old steps
        - Architecture diagrams referencing old structure
        """
        outdated_diagrams = []

        # Known removed/changed commands
        deprecated_patterns = [
            r'/craft:docs:feature',
            r'/craft:docs:generate',
        ]

        search_files = list(self.docs_dir.rglob("*.md")) if self.docs_dir.exists() else []

        for file_path in search_files:
            if not file_path.exists():
                continue

            with open(file_path, encoding='utf-8') as f:
                content = f.read()

            # Find Mermaid diagram blocks
            in_mermaid = False
            mermaid_start = 0

            for i, line in enumerate(content.split('\n'), 1):
                if '```mermaid' in line:
                    in_mermaid = True
                    mermaid_start = i
                elif in_mermaid and line.startswith('```'):
                    in_mermaid = False
                elif in_mermaid:
                    # Check for deprecated patterns in diagram
                    for pattern in deprecated_patterns:
                        if re.search(pattern, line):
                            outdated_diagrams.append({
                                'file': str(file_path.relative_to(self.project_root)),
                                'line': i,
                                'diagram_start': mermaid_start,
                                'issue': f'References removed command: {pattern}',
                                'context': line.strip()
                            })

        return DetectionResult(
            "Outdated Diagrams",
            len(outdated_diagrams) > 0,
            len(outdated_diagrams),
            outdated_diagrams,
            f"Found {len(outdated_diagrams)} outdated diagram references"
        )

    def _build_command_relationships(self) -> Dict[str, List[str]]:
        """Build map of related commands (parent/child, similar purpose)"""
        relationships = defaultdict(list)

        # Simple heuristic: commands in same directory are related
        if self.commands_dir.exists():
            for cmd_file in self.commands_dir.rglob("*.md"):
                cmd_name = self._extract_command_name(cmd_file)
                if not cmd_name:
                    continue

                # Add parent directory commands as related
                parent_dir = cmd_file.parent
                if parent_dir != self.commands_dir:
                    for sibling in parent_dir.glob("*.md"):
                        if sibling != cmd_file:
                            sibling_name = self._extract_command_name(sibling)
                            if sibling_name:
                                relationships[cmd_name].append(sibling_name)

        return dict(relationships)

    def _extract_command_name(self, cmd_file: Path) -> Optional[str]:
        """Extract command name from file path or frontmatter"""
        # Try to extract from first line (e.g., "# /craft:do - Title")
        with open(cmd_file, encoding='utf-8') as f:
            first_lines = f.read(500)

        match = re.search(r'/craft:[^\s]+', first_lines)
        if match:
            return match.group(0)

        return None


def main():
    """CLI interface for docs detector"""
    import sys
    import json

    project_root = sys.argv[1] if len(sys.argv) > 1 else "."
    current_version = sys.argv[2] if len(sys.argv) > 2 else None

    detector = DocsDetector(project_root)
    results = detector.detect_all(current_version)

    # Print summary
    print("\n" + "=" * 60)
    print("DOCUMENTATION DETECTION RESULTS")
    print("=" * 60 + "\n")

    for category, result in results.items():
        print(f"  {result.summary()}")

    # Print details for categories with issues
    print("\n" + "=" * 60)
    print("DETAILS")
    print("=" * 60 + "\n")

    for category, result in results.items():
        if result.found and result.items:
            print(f"\n{result.category}:")
            for i, item in enumerate(result.items[:5], 1):  # Show first 5
                print(f"  {i}. {item.get('file', 'Unknown')}")
                if 'context' in item:
                    print(f"     {item['context']}")

            if len(result.items) > 5:
                print(f"  ... and {len(result.items) - 5} more")

    print()


if __name__ == "__main__":
    main()
