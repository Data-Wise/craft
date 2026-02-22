#!/usr/bin/env python3
"""Mermaid diagram auto-fix engine.

Applies safe automatic fixes to common Mermaid syntax issues and
reports issues that require human review.

Usage:
    python3 scripts/mermaid-autofix.py docs/              # Dry-run (default)
    python3 scripts/mermaid-autofix.py docs/ --fix         # Apply safe fixes
    python3 scripts/mermaid-autofix.py docs/ --test        # Run built-in tests
"""

import argparse
import re
import sys
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Fix:
    """A fix applied or suggested for a mermaid block."""
    file: str
    line_number: int
    rule: str
    message: str
    old_text: str
    new_text: str
    safe: bool = True  # False = report-only


@dataclass
class Report:
    """A report-only finding that needs human review."""
    file: str
    line_number: int
    rule: str
    message: str
    context: str


def fix_leading_slash(content: str) -> tuple[str, list[str]]:
    """Fix [/text] -> ["/text"] in node labels."""
    changes = []

    def replacer(m):
        inner = m.group(1)
        changes.append(f'[{inner}] -> ["{inner}"]')
        return f'["{inner}"]'

    fixed = re.sub(r'\[(/[^\]"]+)\]', replacer, content)
    return fixed, changes


def fix_lowercase_end(content: str) -> tuple[str, list[str]]:
    """Fix [end] -> [End] in node labels."""
    changes = []
    lines = content.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        # Skip subgraph end statements and comments
        if stripped == "end" or stripped.startswith("%%"):
            result.append(line)
            continue
        if re.search(r'\[\s*end\s*\]', line) and not re.search(r'\[\s*End\s*\]', line):
            new_line = re.sub(r'\[(\s*)end(\s*)\]', r'[\1End\2]', line)
            if new_line != line:
                changes.append('[end] -> [End]')
                line = new_line
        result.append(line)
    return "\n".join(result), changes


def fix_unquoted_colons(content: str) -> tuple[str, list[str]]:
    """Fix [a:b] -> ["a:b"] in node labels."""
    changes = []

    def replacer(m):
        prefix = m.group(1)
        inner = m.group(2)
        # Skip if already quoted, or if this is a style/classDef line
        if inner.startswith('"') or inner.startswith("'"):
            return m.group(0)
        if ":" in inner:
            changes.append(f'[{inner}] -> ["{inner}"]')
            return f'{prefix}["{inner}"]'
        return m.group(0)

    lines = content.split("\n")
    result = []
    for line in lines:
        stripped = line.strip()
        # Skip classDef, class, and style lines which use colons legitimately
        if stripped.startswith(("classDef", "class ", "style ")):
            result.append(line)
            continue
        # Fix unquoted colons in bracket labels
        fixed = re.sub(r'(\w)\[([^\]"\']+:[^\]"\']+)\]', replacer, line)
        result.append(fixed)
    return "\n".join(result), changes


def fix_br_tags(content: str) -> tuple[str, list[str]]:
    """Fix <br/> tags -> Mermaid line break syntax."""
    changes = []
    # In Mermaid, <br/> inside quoted labels should become <br/>
    # Actually, <br/> IS the standard Mermaid line break in labels.
    # The "fix" wraps the label in quotes if not already quoted,
    # ensuring consistent rendering.
    lines = content.split("\n")
    result = []
    for line in lines:
        if re.search(r'<br\s*/?>', line):
            # Check if the br is inside an unquoted bracket label
            match = re.search(r'\[([^\]"]+<br\s*/?>.*?)\]', line)
            if match:
                inner = match.group(1)
                quoted = f'["{inner}"]'
                new_line = line.replace(f'[{inner}]', quoted)
                if new_line != line:
                    changes.append(f'Quoted label containing <br/>: [{inner}]')
                    line = new_line
        result.append(line)
    return "\n".join(result), changes


def fix_deprecated_graph(content: str) -> tuple[str, list[str]]:
    """Fix graph TD -> flowchart TD."""
    changes = []
    lines = content.split("\n")
    result = []
    for line in lines:
        match = re.match(r'^(\s*)(graph)\s+(TB|TD|LR|RL|BT)\b(.*)', line)
        if match:
            indent, _, direction, rest = match.groups()
            changes.append(f'graph {direction} -> flowchart {direction}')
            line = f'{indent}flowchart {direction}{rest}'
        result.append(line)
    return "\n".join(result), changes


# Safe fix functions in application order
SAFE_FIXES = [
    ("leading-slash", fix_leading_slash),
    ("lowercase-end", fix_lowercase_end),
    ("unquoted-colon", fix_unquoted_colons),
    ("br-tag-quote", fix_br_tags),
    ("deprecated-graph", fix_deprecated_graph),
]


def report_long_text(content: str) -> list[str]:
    """Report node labels longer than 20 characters."""
    findings = []
    for i, line in enumerate(content.split("\n"), 1):
        # Match quoted labels
        for match in re.finditer(r'"([^"]{21,})"', line):
            text = match.group(1)
            findings.append(f"  Line {i}: Long label ({len(text)} chars): \"{text[:30]}...\"")
        # Match unquoted bracket labels
        for match in re.finditer(r'\[([^\]"]{21,})\]', line):
            text = match.group(1)
            findings.append(f"  Line {i}: Long label ({len(text)} chars): [{text[:30]}...]")
    return findings


def report_orphaned_nodes(content: str) -> list[str]:
    """Report nodes that appear in definitions but not in any edge."""
    findings = []
    # Extract node IDs from definitions (ID[label] or ID{label} etc)
    defined = set(re.findall(r'^\s*(\w+)\s*[\[\{\(\|]', content, re.MULTILINE))
    # Extract node IDs from edges (ID --> ID, ID --- ID, etc)
    edge_nodes = set()
    for match in re.finditer(r'(\w+)\s*[-=.]+>?\s*(?:\|[^|]*\|)?\s*(\w+)', content):
        edge_nodes.add(match.group(1))
        edge_nodes.add(match.group(2))
    # Find orphans (defined but not in any edge)
    orphans = defined - edge_nodes
    # Filter out common non-node keywords
    keywords = {"flowchart", "graph", "subgraph", "end", "classDef", "class",
                "style", "click", "linkStyle", "direction"}
    orphans -= keywords
    for node_id in sorted(orphans):
        findings.append(f"  Orphaned node: {node_id} (defined but not connected)")
    return findings


def report_complex_horizontal(content: str) -> list[str]:
    """Report LR layouts with >5 connected nodes."""
    findings = []
    first_line = content.strip().split("\n")[0].strip()
    if not re.match(r'^(flowchart|graph)\s+LR\b', first_line):
        return findings
    # Count unique nodes in edges
    edge_nodes = set()
    for match in re.finditer(r'(\w+)\s*[-=.]+>?\s*(?:\|[^|]*\|)?\s*(\w+)', content):
        edge_nodes.add(match.group(1))
        edge_nodes.add(match.group(2))
    if len(edge_nodes) > 5:
        findings.append(f"  LR layout with {len(edge_nodes)} nodes — consider TD for readability")
    return findings


REPORT_RULES = [
    ("long-text", "Long node text (>20 chars)", report_long_text),
    ("orphaned-nodes", "Orphaned nodes", report_orphaned_nodes),
    ("complex-horizontal", "Complex horizontal layout", report_complex_horizontal),
]


def extract_mermaid_blocks(filepath: str) -> list[tuple[int, int, str]]:
    """Extract mermaid blocks as (start_line, end_line, content) tuples."""
    blocks = []
    try:
        with open(filepath, "r", encoding="utf-8") as f:
            lines = f.readlines()
    except (OSError, UnicodeDecodeError):
        return blocks

    in_mermaid = False
    block_start = 0
    block_lines: list[str] = []

    for i, line in enumerate(lines):
        stripped = line.rstrip()
        if not in_mermaid:
            if re.match(r'^\s*```mermaid\s*$', stripped):
                in_mermaid = True
                block_start = i
                block_lines = []
        else:
            if re.match(r'^\s*```\s*$', stripped):
                content = "\n".join(block_lines)
                if content.strip():
                    blocks.append((block_start, i, content))
                in_mermaid = False
                block_lines = []
            else:
                block_lines.append(line.rstrip())

    return blocks


def process_file(filepath: str, apply_fixes: bool = False) -> tuple[list[Fix], list[Report]]:
    """Process a file: find issues and optionally apply fixes."""
    fixes = []
    reports = []

    blocks = extract_mermaid_blocks(filepath)
    if not blocks:
        return fixes, reports

    with open(filepath, "r", encoding="utf-8") as f:
        lines = f.readlines()

    modified = False

    # Process blocks in reverse order to prevent line-index drift
    # when fixes change the number of lines in earlier blocks
    for block_start, block_end, content in reversed(blocks):
        original = content
        block_line = block_start + 1  # 1-indexed for display

        # Apply safe fixes
        for rule_name, fix_fn in SAFE_FIXES:
            new_content, changes = fix_fn(content)
            for change in changes:
                fixes.append(Fix(
                    file=filepath,
                    line_number=block_line,
                    rule=rule_name,
                    message=change,
                    old_text=content,
                    new_text=new_content,
                ))
            content = new_content

        # Report-only rules (run on original content)
        for rule_name, description, report_fn in REPORT_RULES:
            findings = report_fn(original)
            for finding in findings:
                reports.append(Report(
                    file=filepath,
                    line_number=block_line,
                    rule=rule_name,
                    message=description,
                    context=finding,
                ))

        # Update file content if fixes were applied
        if content != original and apply_fixes:
            new_block_lines = content.split("\n")
            # Replace lines between fence markers
            lines[block_start + 1:block_end] = [l + "\n" for l in new_block_lines]
            modified = True

    if modified and apply_fixes:
        with open(filepath, "w", encoding="utf-8") as f:
            f.writelines(lines)

    return fixes, reports


def collect_files(paths: list[str]) -> list[str]:
    """Collect all markdown files from given paths."""
    files = []
    for path in paths:
        p = Path(path)
        if p.is_file() and p.suffix == ".md":
            files.append(str(p))
        elif p.is_dir():
            files.extend(str(f) for f in sorted(p.rglob("*.md")))
    return files


def run_tests():
    """Run built-in self-tests."""
    passed = 0
    failed = 0

    def test(name, actual, expected):
        nonlocal passed, failed
        if actual == expected:
            passed += 1
            print(f"  PASS: {name}")
        else:
            failed += 1
            print(f"  FAIL: {name}")
            print(f"    Expected: {expected!r}")
            print(f"    Actual:   {actual!r}")

    print("Running auto-fix self-tests...\n")

    # Leading slash
    fixed, changes = fix_leading_slash('A[/text] --> B')
    test("leading-slash fix", fixed, 'A["/text"] --> B')
    test("leading-slash change count", len(changes), 1)

    # Already quoted should not change
    fixed, changes = fix_leading_slash('A["/text"] --> B')
    test("leading-slash skip quoted", len(changes), 0)

    # Lowercase end
    fixed, changes = fix_lowercase_end('A --> B[end]')
    test("lowercase-end fix", fixed, 'A --> B[End]')

    # Subgraph end should not change
    fixed, changes = fix_lowercase_end('end')
    test("lowercase-end skip subgraph", len(changes), 0)

    # Unquoted colons
    fixed, changes = fix_unquoted_colons('A[Status: OK] --> B')
    test("unquoted-colon fix", fixed, 'A["Status: OK"] --> B')

    # br tags
    fixed, changes = fix_br_tags('A[First<br/>Second] --> B')
    test("br-tag quote", fixed, 'A["First<br/>Second"] --> B')

    # Deprecated graph
    fixed, changes = fix_deprecated_graph('graph TD\n  A --> B')
    test("graph-to-flowchart", fixed, 'flowchart TD\n  A --> B')

    # Preserve valid
    valid = 'flowchart TD\n  A["Hello"] --> B["World"]'
    fixed_slash, c1 = fix_leading_slash(valid)
    fixed_end, c2 = fix_lowercase_end(fixed_slash)
    fixed_colon, c3 = fix_unquoted_colons(fixed_end)
    fixed_br, c4 = fix_br_tags(fixed_colon)
    fixed_graph, c5 = fix_deprecated_graph(fixed_br)
    test("valid-preserved", fixed_graph, valid)
    test("valid-no-changes", sum(len(c) for c in [c1, c2, c3, c4, c5]), 0)

    # Report: long text
    findings = report_long_text('A["This is a very long node label text that should be flagged"] --> B')
    test("long-text detected", len(findings), 1)

    # Report: complex horizontal
    findings = report_complex_horizontal('flowchart LR\nA --> B\nB --> C\nC --> D\nD --> E\nE --> F\nF --> G')
    test("complex-horizontal detected", len(findings), 1)

    print(f"\n{passed} passed, {failed} failed")
    return failed == 0


def main():
    parser = argparse.ArgumentParser(
        description="Auto-fix Mermaid diagram issues in markdown files"
    )
    parser.add_argument(
        "paths",
        nargs="*",
        help="Markdown files or directories to process",
    )
    parser.add_argument(
        "--fix",
        action="store_true",
        help="Apply safe auto-fixes (default: dry-run / report only)",
    )
    parser.add_argument(
        "--test",
        action="store_true",
        help="Run built-in self-tests",
    )
    args = parser.parse_args()

    if args.test:
        success = run_tests()
        sys.exit(0 if success else 1)

    if not args.paths:
        parser.error("paths are required (unless using --test)")

    files = collect_files(args.paths)
    if not files:
        print("No markdown files found.", file=sys.stderr)
        sys.exit(1)

    all_fixes = []
    all_reports = []

    for filepath in files:
        fixes, reports = process_file(filepath, apply_fixes=args.fix)
        all_fixes.extend(fixes)
        all_reports.extend(reports)

    # Display results
    mode = "APPLIED" if args.fix else "DRY RUN"
    safe_fixes = [f for f in all_fixes if f.safe]
    print(f"Scanned {len(files)} files\n")

    if safe_fixes:
        print(f"SAFE FIXES ({mode}) — {len(safe_fixes)}:")
        for fix in safe_fixes:
            print(f"  {fix.file}:{fix.line_number} [{fix.rule}] {fix.message}")
        print()

    if all_reports:
        print(f"REPORT ONLY — {len(all_reports)} items (needs human review):")
        for report in all_reports:
            print(f"  {report.file}:{report.line_number} [{report.rule}] {report.message}")
            print(f"  {report.context}")
        print()

    if not safe_fixes and not all_reports:
        print("No issues found.")
    elif safe_fixes and not args.fix:
        print(f"Run with --fix to apply {len(safe_fixes)} safe fixes.")

    sys.exit(0)


if __name__ == "__main__":
    main()
