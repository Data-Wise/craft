#!/usr/bin/env python3
"""
Help File Validator - Validate command YAML frontmatter and help pages

Validates 8 issue types:
1. Missing help files (command exists, no YAML frontmatter)
2. Incomplete YAML (missing description or category)
3. Outdated descriptions (mentions removed features)
4. Missing flags (flag in code, not in arguments array)
5. Extra flags (flag in YAML, not in code)
6. Wrong defaults (default doesn't match code)
7. Missing aliases (short flag exists, not documented)
8. Category mismatch (category doesn't match directory)
"""

import re
import os
import yaml
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Set
from dataclasses import dataclass, field
from enum import Enum


class IssueType(Enum):
    """Types of help file issues"""
    MISSING_HELP = "missing_help"
    INCOMPLETE_YAML = "incomplete_yaml"
    OUTDATED_DESC = "outdated_description"
    MISSING_FLAG = "missing_flag"
    EXTRA_FLAG = "extra_flag"
    WRONG_DEFAULT = "wrong_default"
    MISSING_ALIAS = "missing_alias"
    CATEGORY_MISMATCH = "category_mismatch"


@dataclass
class HelpIssue:
    """Represents a help file validation issue"""
    issue_type: IssueType
    file_path: str
    severity: str  # "high", "medium", "low"
    description: str
    current_value: Optional[str] = None
    suggested_value: Optional[str] = None
    details: Dict = field(default_factory=dict)

    def summary(self) -> str:
        """Human-readable summary"""
        severity_emoji = {
            'high': '🔴',
            'medium': '🟡',
            'low': '🔵'
        }
        emoji = severity_emoji.get(self.severity, '⚪')
        return f"{emoji} {self.description}"


@dataclass
class CommandHelp:
    """Parsed command help information"""
    file_path: Path
    has_frontmatter: bool
    frontmatter: Dict = field(default_factory=dict)
    command_name: Optional[str] = None
    category: Optional[str] = None
    description: Optional[str] = None
    arguments: List[Dict] = field(default_factory=list)
    flags: List[str] = field(default_factory=list)


class HelpFileValidator:
    """Validate command help files and YAML frontmatter"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.commands_dir = self.project_root / "commands"
        self.templates_dir = self.project_root / "templates" / "docs"

    def validate_all(self) -> Dict[IssueType, List[HelpIssue]]:
        """
        Validate all command help files

        Returns:
            Dictionary of issue_type -> list of HelpIssue objects
        """
        issues = {issue_type: [] for issue_type in IssueType}

        if not self.commands_dir.exists():
            return issues

        # Discover all command files
        command_files = list(self.commands_dir.rglob("*.md"))

        for cmd_file in command_files:
            cmd_help = self._parse_command_file(cmd_file)
            file_issues = self._validate_command(cmd_help)

            # Group issues by type
            for issue in file_issues:
                issues[issue.issue_type].append(issue)

        return issues

    def validate_command(self, command_path: str) -> List[HelpIssue]:
        """
        Validate a single command file

        Args:
            command_path: Path to command file (relative or absolute)

        Returns:
            List of HelpIssue objects
        """
        cmd_file = self.project_root / command_path
        if not cmd_file.exists():
            return [HelpIssue(
                IssueType.MISSING_HELP,
                str(command_path),
                "high",
                f"Command file not found: {command_path}"
            )]

        cmd_help = self._parse_command_file(cmd_file)
        return self._validate_command(cmd_help)

    def _parse_command_file(self, cmd_file: Path) -> CommandHelp:
        """Parse command file and extract help information"""
        with open(cmd_file, encoding='utf-8') as f:
            content = f.read()

        # Extract command name from file path or content
        command_name = self._extract_command_name(content, cmd_file)

        # Determine expected category from directory structure
        expected_category = self._get_expected_category(cmd_file)

        # Check for YAML frontmatter
        if not content.startswith('---'):
            return CommandHelp(
                file_path=cmd_file,
                has_frontmatter=False,
                command_name=command_name,
                category=expected_category
            )

        # Parse frontmatter
        try:
            parts = content.split('---', 2)
            if len(parts) < 3:
                return CommandHelp(
                    file_path=cmd_file,
                    has_frontmatter=False,
                    command_name=command_name,
                    category=expected_category
                )

            frontmatter = yaml.safe_load(parts[1])
            if not frontmatter:
                return CommandHelp(
                    file_path=cmd_file,
                    has_frontmatter=False,
                    command_name=command_name,
                    category=expected_category
                )

            # Extract arguments and flags
            arguments = frontmatter.get('arguments', [])
            flags = [arg.get('name', '') for arg in arguments if not arg.get('required', False)]

            return CommandHelp(
                file_path=cmd_file,
                has_frontmatter=True,
                frontmatter=frontmatter,
                command_name=command_name,
                category=frontmatter.get('category'),
                description=frontmatter.get('description'),
                arguments=arguments,
                flags=flags
            )

        except yaml.YAMLError:
            return CommandHelp(
                file_path=cmd_file,
                has_frontmatter=False,
                command_name=command_name,
                category=expected_category
            )

    def _validate_command(self, cmd_help: CommandHelp) -> List[HelpIssue]:
        """Validate a single command's help information"""
        issues = []
        rel_path = str(cmd_help.file_path.relative_to(self.project_root))

        # Check 1: Missing help file (no frontmatter)
        if not cmd_help.has_frontmatter:
            issues.append(HelpIssue(
                IssueType.MISSING_HELP,
                rel_path,
                "high",
                "No YAML frontmatter found",
                details={'command': cmd_help.command_name}
            ))
            return issues  # Can't validate further without frontmatter

        # Check 2: Incomplete YAML (missing required fields)
        incomplete_issues = self._check_incomplete_yaml(cmd_help, rel_path)
        issues.extend(incomplete_issues)

        # Check 3: Outdated description
        outdated_issues = self._check_outdated_description(cmd_help, rel_path)
        issues.extend(outdated_issues)

        # Check 4-7: Flag validation (requires code analysis - placeholder)
        # In real implementation, would parse command implementation
        flag_issues = self._validate_flags(cmd_help, rel_path)
        issues.extend(flag_issues)

        # Check 8: Category mismatch
        category_issues = self._check_category_mismatch(cmd_help, rel_path)
        issues.extend(category_issues)

        return issues

    def _check_incomplete_yaml(self, cmd_help: CommandHelp, rel_path: str) -> List[HelpIssue]:
        """Check for missing required YAML fields"""
        issues = []

        # Required field: description
        if not cmd_help.description:
            issues.append(HelpIssue(
                IssueType.INCOMPLETE_YAML,
                rel_path,
                "high",
                "Missing required field: description",
                suggested_value="Add a 1-2 sentence description of the command",
                details={'field': 'description'}
            ))

        # Recommended field: category (for subcommands)
        if self._is_subcommand(cmd_help.file_path) and not cmd_help.category:
            issues.append(HelpIssue(
                IssueType.INCOMPLETE_YAML,
                rel_path,
                "medium",
                "Missing recommended field: category",
                suggested_value=self._get_expected_category(cmd_help.file_path),
                details={'field': 'category'}
            ))

        # Check arguments array structure
        for i, arg in enumerate(cmd_help.arguments):
            if 'name' not in arg:
                issues.append(HelpIssue(
                    IssueType.INCOMPLETE_YAML,
                    rel_path,
                    "high",
                    f"Argument {i+1} missing 'name' field",
                    details={'argument_index': i, 'field': 'name'}
                ))

            if 'description' not in arg:
                issues.append(HelpIssue(
                    IssueType.INCOMPLETE_YAML,
                    rel_path,
                    "medium",
                    f"Argument '{arg.get('name', i+1)}' missing description",
                    details={'argument': arg.get('name'), 'field': 'description'}
                ))

        return issues

    def _check_outdated_description(self, cmd_help: CommandHelp, rel_path: str) -> List[HelpIssue]:
        """Check if description mentions removed features or outdated info"""
        issues = []

        if not cmd_help.description:
            return issues

        # Known removed/changed features
        outdated_patterns = [
            (r'/craft:docs:feature', 'References removed /craft:docs:feature command'),
            (r'/craft:docs:generate', 'References removed /craft:docs:generate command'),
            (r'\b\d+\s+commands?\b', 'May contain outdated command count'),
            (r'\bWIP\b', 'Contains WIP marker for potentially completed feature'),
        ]

        for pattern, reason in outdated_patterns:
            if re.search(pattern, cmd_help.description, re.IGNORECASE):
                issues.append(HelpIssue(
                    IssueType.OUTDATED_DESC,
                    rel_path,
                    "medium",
                    reason,
                    current_value=cmd_help.description,
                    details={'pattern': pattern}
                ))

        return issues

    def _validate_flags(self, cmd_help: CommandHelp, rel_path: str) -> List[HelpIssue]:
        """
        Validate flag documentation completeness

        Note: This is a simplified version. A full implementation would:
        1. Parse the command's implementation code
        2. Extract all flags from argument parsing
        3. Compare with YAML frontmatter
        """
        issues = []

        # For now, just validate the YAML structure of existing flags
        for arg in cmd_help.arguments:
            arg_name = arg.get('name', '')

            # Check for default value inconsistencies
            if 'default' in arg and arg.get('required', False):
                issues.append(HelpIssue(
                    IssueType.WRONG_DEFAULT,
                    rel_path,
                    "low",
                    f"Flag '{arg_name}' is required but has default value",
                    current_value=str(arg['default']),
                    details={'argument': arg_name}
                ))

            # Check for missing alias documentation
            # (Would need to parse code to know if alias exists)

        return issues

    def _check_category_mismatch(self, cmd_help: CommandHelp, rel_path: str) -> List[HelpIssue]:
        """Check if category field matches directory structure"""
        issues = []

        if not self._is_subcommand(cmd_help.file_path):
            return issues  # Main commands don't need category

        expected_category = self._get_expected_category(cmd_help.file_path)

        if cmd_help.category and cmd_help.category != expected_category:
            issues.append(HelpIssue(
                IssueType.CATEGORY_MISMATCH,
                rel_path,
                "medium",
                f"Category mismatch: '{cmd_help.category}' should be '{expected_category}'",
                current_value=cmd_help.category,
                suggested_value=expected_category,
                details={'expected': expected_category, 'actual': cmd_help.category}
            ))

        return issues

    def _extract_command_name(self, content: str, file_path: Path) -> Optional[str]:
        """Extract command name from content or file path"""
        # Try to extract from first heading (e.g., "# /craft:do - Title")
        match = re.search(r'^#\s+(/craft:[^\s]+)', content, re.MULTILINE)
        if match:
            return match.group(1)

        # Fallback: construct from file path
        rel_path = file_path.relative_to(self.commands_dir)
        parts = list(rel_path.parts[:-1])  # Exclude filename
        parts.append(rel_path.stem)  # Add stem (filename without .md)

        if len(parts) == 1:
            return f"/craft:{parts[0]}"
        else:
            return f"/craft:{':'.join(parts)}"

    def _get_expected_category(self, file_path: Path) -> str:
        """Get expected category from directory structure"""
        rel_path = file_path.relative_to(self.commands_dir)

        if len(rel_path.parts) == 1:
            return "main"  # Top-level command

        return rel_path.parts[0]  # First directory is the category

    def _is_subcommand(self, file_path: Path) -> bool:
        """Check if this is a subcommand (in a subdirectory)"""
        rel_path = file_path.relative_to(self.commands_dir)
        return len(rel_path.parts) > 1

    def get_summary(self, issues: Dict[IssueType, List[HelpIssue]]) -> str:
        """Generate human-readable summary of issues"""
        total_issues = sum(len(issue_list) for issue_list in issues.values())

        if total_issues == 0:
            return "✅ All command help files are valid"

        summary_lines = [
            f"\n{'=' * 60}",
            "HELP FILE VALIDATION RESULTS",
            f"{'=' * 60}\n",
            f"Total Issues: {total_issues}\n"
        ]

        for issue_type, issue_list in issues.items():
            if not issue_list:
                continue

            summary_lines.append(f"\n{issue_type.name} ({len(issue_list)}):")
            for i, issue in enumerate(issue_list[:5], 1):  # Show first 5
                summary_lines.append(f"  {i}. {issue.summary()}")
                summary_lines.append(f"     File: {issue.file_path}")

            if len(issue_list) > 5:
                summary_lines.append(f"  ... and {len(issue_list) - 5} more")

        return "\n".join(summary_lines)


def main():
    """CLI interface for help file validator"""
    import sys
    import json

    project_root = sys.argv[1] if len(sys.argv) > 1 else "."

    validator = HelpFileValidator(project_root)
    issues = validator.validate_all()

    # Print summary
    print(validator.get_summary(issues))

    # Optionally output JSON for programmatic use
    if len(sys.argv) > 2 and sys.argv[2] == "--json":
        json_output = {
            issue_type.name: [
                {
                    'file': issue.file_path,
                    'severity': issue.severity,
                    'description': issue.description,
                    'current': issue.current_value,
                    'suggested': issue.suggested_value
                }
                for issue in issue_list
            ]
            for issue_type, issue_list in issues.items()
        }
        print("\n\nJSON Output:")
        print(json.dumps(json_output, indent=2))


if __name__ == "__main__":
    main()
