#!/usr/bin/env python3
"""Mermaid diagram validation script.

Extracts mermaid fenced blocks from markdown files and runs
local regex pre-checks for common syntax issues.

Usage:
    python3 scripts/mermaid-validate.py docs/
    python3 scripts/mermaid-validate.py docs/ --json
    python3 scripts/mermaid-validate.py path/to/file.md
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


@dataclass
class MermaidBlock:
    """A mermaid code block extracted from a markdown file."""
    file: str
    line_number: int
    content: str


@dataclass
class Issue:
    """A validation issue found in a mermaid block."""
    file: str
    line_number: int
    rule: str
    message: str
    severity: str = "error"  # "error" or "warning"
    context: str = ""


def extract_mermaid_blocks(filepath: str) -> list[MermaidBlock]:
    """Extract all mermaid fenced code blocks from a markdown file.

    Returns list of (file, line_number, block_content) tuples.
    Only matches ```mermaid blocks, ignoring other fenced blocks.
    """
    blocks = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return blocks

    in_mermaid = False
    block_start = 0
    block_lines: list[str] = []
    fence_indent = ""

    for i, line in enumerate(lines, start=1):
        stripped = line.rstrip()

        if not in_mermaid:
            # Match opening ```mermaid fence (with optional leading whitespace)
            match = re.match(r'^(\s*)```mermaid\s*$', stripped)
            if match:
                in_mermaid = True
                fence_indent = match.group(1)
                block_start = i
                block_lines = []
        else:
            # Match closing ``` fence at same or less indentation
            if re.match(r'^' + re.escape(fence_indent) + r'```\s*$', stripped):
                content = "\n".join(block_lines)
                if content.strip():
                    blocks.append(MermaidBlock(
                        file=filepath,
                        line_number=block_start,
                        content=content,
                    ))
                in_mermaid = False
                block_lines = []
            else:
                block_lines.append(line.rstrip())

    return blocks


def check_leading_slash(block: MermaidBlock) -> list[Issue]:
    """Detect [/text] patterns that Mermaid misparses as parallelogram shapes."""
    issues = []
    for i, line in enumerate(block.content.split("\n")):
        # Match [/...] but not ["/..."] (already quoted)
        if re.search(r'\[/[^\]"]+\]', line):
            issues.append(Issue(
                file=block.file,
                line_number=block.line_number + i + 1,
                rule="leading-slash",
                message="Leading / in label will be misinterpreted as parallelogram shape",
                severity="error",
                context=line.strip(),
            ))
    return issues


def check_lowercase_end(block: MermaidBlock) -> list[Issue]:
    """Detect lowercase 'end' in node labels that conflicts with Mermaid keywords."""
    issues = []
    for i, line in enumerate(block.content.split("\n")):
        # Match [end] or [... end ...] but not ["end"] (quoted)
        # Also skip subgraph end statements and %%end comments
        stripped = line.strip()
        if stripped == "end" or stripped.startswith("%%"):
            continue
        # Look for unquoted 'end' as a node label
        if re.search(r'\[\s*end\s*\]', line, re.IGNORECASE):
            # Only flag if it's actually lowercase
            if re.search(r'\[\s*end\s*\]', line) and not re.search(r'\[\s*End\s*\]', line):
                issues.append(Issue(
                    file=block.file,
                    line_number=block.line_number + i + 1,
                    rule="lowercase-end",
                    message="Lowercase 'end' in node label conflicts with Mermaid keyword",
                    severity="error",
                    context=line.strip(),
                ))
    return issues


def check_unquoted_colons(block: MermaidBlock) -> list[Issue]:
    """Detect unquoted colons in node labels."""
    issues = []
    for i, line in enumerate(block.content.split("\n")):
        # Match [...:...] where the content is not quoted
        # Skip lines that are just edge definitions (-->)
        # Skip classDef and class statements which use colons legitimately
        stripped = line.strip()
        if stripped.startswith("classDef") or stripped.startswith("class "):
            continue
        if stripped.startswith("style "):
            continue
        # Look for bracket content with unquoted colons
        matches = re.findall(r'\[([^\]"]+)\]', line)
        for match in matches:
            if ":" in match and not match.startswith('"'):
                issues.append(Issue(
                    file=block.file,
                    line_number=block.line_number + i + 1,
                    rule="unquoted-colon",
                    message="Unquoted colon in node label may cause parsing issues",
                    severity="warning",
                    context=line.strip(),
                ))
                break
    return issues


def check_br_tags(block: MermaidBlock) -> list[Issue]:
    """Detect <br/> tags in mermaid blocks."""
    issues = []
    for i, line in enumerate(block.content.split("\n")):
        if re.search(r'<br\s*/?>', line):
            issues.append(Issue(
                file=block.file,
                line_number=block.line_number + i + 1,
                rule="br-tag",
                message="<br/> tag in mermaid block — use Mermaid line break syntax instead",
                severity="warning",
                context=line.strip(),
            ))
    return issues


def check_deprecated_graph(block: MermaidBlock) -> list[Issue]:
    """Detect deprecated 'graph' directive (should be 'flowchart')."""
    issues = []
    first_line = block.content.strip().split("\n")[0].strip()
    if re.match(r'^graph\s+(TB|TD|LR|RL|BT)\b', first_line):
        issues.append(Issue(
            file=block.file,
            line_number=block.line_number + 1,
            rule="deprecated-graph",
            message="'graph' directive is deprecated — use 'flowchart' instead",
            severity="warning",
            context=first_line,
        ))
    return issues


# All pre-check rules
RULES = [
    check_leading_slash,
    check_lowercase_end,
    check_unquoted_colons,
    check_br_tags,
    check_deprecated_graph,
]


def validate_blocks(blocks: list[MermaidBlock]) -> list[Issue]:
    """Run all regex pre-checks on a list of mermaid blocks."""
    issues = []
    for block in blocks:
        for rule in RULES:
            issues.extend(rule(block))
    return issues


def collect_files(paths: list[str]) -> list[str]:
    """Collect all markdown files from given paths (files or directories)."""
    files = []
    for path in paths:
        p = Path(path)
        if p.is_file() and p.suffix == ".md":
            files.append(str(p))
        elif p.is_dir():
            files.extend(str(f) for f in sorted(p.rglob("*.md")))
    return files


def main():
    parser = argparse.ArgumentParser(
        description="Validate mermaid diagrams in markdown files"
    )
    parser.add_argument(
        "paths",
        nargs="+",
        help="Markdown files or directories to validate",
    )
    parser.add_argument(
        "--json",
        action="store_true",
        help="Output results as JSON",
    )
    parser.add_argument(
        "--errors-only",
        action="store_true",
        help="Only report errors, not warnings",
    )
    args = parser.parse_args()

    files = collect_files(args.paths)
    if not files:
        print("No markdown files found.", file=sys.stderr)
        sys.exit(1)

    all_blocks = []
    for filepath in files:
        all_blocks.extend(extract_mermaid_blocks(filepath))

    issues = validate_blocks(all_blocks)

    if args.errors_only:
        issues = [i for i in issues if i.severity == "error"]

    if args.json:
        print(json.dumps([{
            "file": i.file,
            "line": i.line_number,
            "rule": i.rule,
            "message": i.message,
            "severity": i.severity,
            "context": i.context,
        } for i in issues], indent=2))
    else:
        errors = [i for i in issues if i.severity == "error"]
        warnings = [i for i in issues if i.severity == "warning"]

        print(f"Scanned {len(files)} files, found {len(all_blocks)} mermaid blocks")
        print()

        if errors:
            print(f"ERRORS ({len(errors)}):")
            for issue in errors:
                print(f"  {issue.file}:{issue.line_number} [{issue.rule}] {issue.message}")
                if issue.context:
                    print(f"    > {issue.context}")
            print()

        if warnings and not args.errors_only:
            print(f"WARNINGS ({len(warnings)}):")
            for issue in warnings:
                print(f"  {issue.file}:{issue.line_number} [{issue.rule}] {issue.message}")
                if issue.context:
                    print(f"    > {issue.context}")
            print()

        error_count = len(errors)
        warn_count = len(warnings)
        if error_count == 0:
            print(f"OK: 0 errors, {warn_count} warnings")
        else:
            print(f"FAIL: {error_count} errors, {warn_count} warnings")

    sys.exit(1 if any(i.severity == "error" for i in issues) else 0)


if __name__ == "__main__":
    main()
