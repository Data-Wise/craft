#!/usr/bin/env python3
"""
CLAUDE.md Budget Enforcer & Content Optimizer

Enforces line budgets on CLAUDE.md files by:
- Classifying sections into priority tiers (P0/P1/P2)
- Detecting bloated content (release history, diffstats, phase notes)
- Moving P2 content to detail files (VERSION-HISTORY.md, CONTRIBUTING.md, etc.)
- Replacing moved content with pointer lines
- Collapsing over-budget P1 sections

Priority tiers:
  P0 - Always keep (header, git workflow, quick commands, structure, troubleshooting, pointers)
  P1 - Include if under budget (agents, execution modes, active dev, key files)
  P2 - Always in detail files (release notes, feature matrices, test breakdowns, diffstats)

Version: 1.0.0
Author: Craft Plugin
"""

import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import project detector - handle both module and script usage
try:
    from .claude_md_detector import CLAUDEMDDetector
except ImportError:
    from claude_md_detector import CLAUDEMDDetector


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BUDGET = 150

# Section priority definitions: (canonical_name, priority, max_lines)
# Canonical names are matched case-insensitively against H2 headers.
P0_SECTIONS: Dict[str, int] = {
    "header": 5,            # TL;DR / title block (above first H2)
    "git workflow": 15,
    "quick commands": 15,
    "project structure": 15,
    "troubleshooting": 10,
    "pointers": 10,
    "references": 10,       # Alias for pointers
    "links": 10,            # Alias for pointers
}

P1_SECTIONS: Dict[str, int] = {
    "agents": 10,
    "routing": 10,           # Alias for agents
    "execution modes": 8,
    "active development": 5,
    "key files": 15,
}

# P2 section names - always moved to detail files
P2_SECTION_NAMES: List[str] = [
    "release",
    "version history",
    "recent major features",
    "feature status",
    "feature matrix",
    "test suite",
    "phase",
    "integration features",
    "documentation guides",
    "phase 3",
]

# Bloat detection patterns
BLOAT_PATTERNS: List[Dict[str, Optional[str]]] = [
    {
        "name": "release_history",
        "pattern": r"^###?\s+v\d+\.\d+.*\n(?:.*\n)*?(?=^##\s|\Z)",
        "target": "docs/VERSION-HISTORY.md",
    },
    {
        "name": "diffstats",
        "pattern": r"\*\*Files Changed:\*\*.*\+.*/-",
        "target": None,  # Delete outright
    },
    {
        "name": "what_shipped",
        "pattern": r"(?:\*\*What Shipped|Merged PR).*\n(?:.*\n)*?(?=^##\s|\Z)",
        "target": "docs/VERSION-HISTORY.md",
    },
    {
        "name": "completed_features",
        "pattern": r"(?:Status.*Complete|Released\s+[^\n]*)",
        "target": "docs/VERSION-HISTORY.md",
    },
    {
        "name": "phase_details",
        "pattern": r"^###\s+Phase\s+\d.*\n(?:.*\n)*?(?=^##\s|\Z)",
        "target": None,  # Delete outright
    },
]

# Standard detail files and their default locations
DETAIL_FILES: Dict[str, str] = {
    "VERSION-HISTORY.md": "docs/VERSION-HISTORY.md",
    "ARCHITECTURE.md": "docs/ARCHITECTURE.md",
    "CONTRIBUTING.md": "CONTRIBUTING.md",
    "COMMANDS.md": "docs/COMMANDS.md",
}

# Pointer format: arrow prefix + markdown link
POINTER_PREFIX = "->"


# ---------------------------------------------------------------------------
# Path Resolution
# ---------------------------------------------------------------------------

def resolve_claude_md_path(global_flag=False, start_dir=None):
    """Resolve CLAUDE.md path. Use --global for ~/.claude/CLAUDE.md.

    Args:
        global_flag: If True, return ~/.claude/CLAUDE.md
        start_dir: Directory to start searching from (default: cwd)

    Returns:
        Absolute path to CLAUDE.md

    Raises:
        FileNotFoundError: If no CLAUDE.md found
    """
    if global_flag:
        path = os.path.expanduser("~/.claude/CLAUDE.md")
        if not os.path.exists(path):
            raise FileNotFoundError(f"Global CLAUDE.md not found at {path}")
        return path

    # Walk up from start_dir to find CLAUDE.md
    search_dir = start_dir or os.getcwd()
    while True:
        candidate = os.path.join(search_dir, "CLAUDE.md")
        if os.path.exists(candidate):
            return os.path.abspath(candidate)
        parent = os.path.dirname(search_dir)
        if parent == search_dir:  # Root reached
            raise FileNotFoundError("No CLAUDE.md found in directory tree")
        search_dir = parent


# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------

@dataclass
class SectionInfo:
    """Information about a CLAUDE.md section."""
    name: str
    start_line: int
    end_line: int
    line_count: int
    priority: str        # "P0", "P1", "P2"
    max_lines: int       # Budget for this section
    content: str = ""    # Raw content of the section

    @property
    def over_budget(self) -> bool:
        """Whether this section exceeds its line budget."""
        return self.line_count > self.max_lines

    @property
    def overage(self) -> int:
        """Number of lines over budget (0 if within)."""
        return max(0, self.line_count - self.max_lines)


@dataclass
class OptimizationAction:
    """A single optimization action to apply."""
    action: str                    # "move", "collapse", "delete", "pointer"
    section_name: str
    line_count: int
    target_file: Optional[str]    # Where to move content
    pointer_text: Optional[str]   # Pointer to insert
    content: str                  # The content being moved/deleted

    @property
    def description(self) -> str:
        """Human-readable description of the action."""
        if self.action == "move":
            return f"Move '{self.section_name}' ({self.line_count} lines) -> {self.target_file}"
        elif self.action == "collapse":
            return f"Collapse '{self.section_name}' ({self.line_count} lines over budget)"
        elif self.action == "delete":
            return f"Delete '{self.section_name}' ({self.line_count} lines)"
        elif self.action == "pointer":
            return f"Add pointer: {self.pointer_text}"
        return f"{self.action}: {self.section_name}"


@dataclass
class OptimizeResult:
    """Result of optimization."""
    before_lines: int
    after_lines: int
    budget: int
    actions: List[OptimizationAction] = field(default_factory=list)
    detail_files_created: List[str] = field(default_factory=list)
    pointers_added: List[str] = field(default_factory=list)

    @property
    def within_budget(self) -> bool:
        """Whether the result is within the line budget."""
        return self.after_lines <= self.budget

    @property
    def lines_saved(self) -> int:
        """Number of lines removed by optimization."""
        return self.before_lines - self.after_lines

    @property
    def reduction_percent(self) -> float:
        """Percentage reduction in line count."""
        if self.before_lines == 0:
            return 0.0
        return round((self.lines_saved / self.before_lines) * 100, 1)


# ---------------------------------------------------------------------------
# Main optimizer class
# ---------------------------------------------------------------------------

class CLAUDEMDOptimizer:
    """Budget enforcer and content optimizer for CLAUDE.md files.

    Analyzes CLAUDE.md sections, detects bloated content, and optimizes
    the file to fit within a configurable line budget by moving low-priority
    content to detail files and replacing it with pointer lines.

    Usage:
        optimizer = CLAUDEMDOptimizer(Path("CLAUDE.md"), budget=150)
        result = optimizer.optimize(dry_run=True)
        print(optimizer.generate_report(result))
    """

    def __init__(self, claude_md_path: Path, budget: int = None):
        """Initialize optimizer.

        Args:
            claude_md_path: Path to CLAUDE.md file
            budget: Line budget (default: read from plugin.json/package.json or 150)
        """
        self.path = Path(claude_md_path)
        self.project_root = self.path.parent
        self.content = ""
        self.lines: List[str] = []

        if self.path.exists():
            self.content = self.path.read_text()
            self.lines = self.content.split("\n")

        self.budget = budget if budget is not None else self._read_budget()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def analyze(self) -> List[SectionInfo]:
        """Analyze CLAUDE.md sections and classify by priority.

        Parses H2 headers to identify section boundaries, then classifies
        each section as P0 (always keep), P1 (keep if room), or P2
        (always move to detail file).

        Returns:
            List of SectionInfo objects sorted by appearance order
        """
        if not self.lines:
            return []

        raw_sections = self._parse_sections()
        classified: List[SectionInfo] = []

        for name, start, end, content in raw_sections:
            priority, max_lines = self._classify_section(name)
            line_count = end - start

            classified.append(SectionInfo(
                name=name,
                start_line=start,
                end_line=end,
                line_count=line_count,
                priority=priority,
                max_lines=max_lines,
                content=content,
            ))

        return classified

    def detect_bloat(self) -> List[OptimizationAction]:
        """Detect bloated/P2 content that should be moved or deleted.

        Scans the CLAUDE.md content against known bloat patterns
        (release history blocks, diffstats, shipped-item lists, etc.)
        and against P2 section classification.

        Returns:
            List of OptimizationAction objects describing what to do
        """
        actions: List[OptimizationAction] = []

        # 1. Pattern-based bloat detection (inline matches)
        actions.extend(self._detect_pattern_bloat())

        # 2. Section-level P2 detection
        sections = self.analyze()
        for section in sections:
            if section.priority == "P2":
                target = self._default_target_for_section(section.name)
                pointer = self.generate_pointer(
                    target, section.name
                ) if target else None

                actions.append(OptimizationAction(
                    action="move" if target else "delete",
                    section_name=section.name,
                    line_count=section.line_count,
                    target_file=target,
                    pointer_text=pointer,
                    content=section.content,
                ))

        return actions

    def optimize(self, dry_run: bool = False) -> OptimizeResult:
        """Run full optimization: detect bloat, move to detail files, add pointers.

        Algorithm:
            1. Parse all sections
            2. Identify P2 content (always move)
            3. Calculate line count after P2 removal
            4. If still over budget, identify P1 sections that can be cut
            5. For each section to move:
               a. Extract content
               b. Create/append to target detail file
               c. Replace section with pointer line
            6. Verify final line count is within budget

        Args:
            dry_run: If True, compute actions without writing any files

        Returns:
            OptimizeResult with before/after metrics and action list
        """
        before_lines = len(self.lines)
        actions: List[OptimizationAction] = []
        detail_files_created: List[str] = []
        pointers_added: List[str] = []

        # Working copy of content
        working_content = self.content
        working_lines = list(self.lines)

        # --- Step 1: Remove P2 sections ---
        sections = self.analyze()
        p2_sections = [s for s in sections if s.priority == "P2"]

        # Process P2 sections in reverse order to preserve line numbers
        for section in reversed(p2_sections):
            target = self._default_target_for_section(section.name)
            pointer = self.generate_pointer(
                target, section.name
            ) if target else None

            action = OptimizationAction(
                action="move" if target else "delete",
                section_name=section.name,
                line_count=section.line_count,
                target_file=target,
                pointer_text=pointer,
                content=section.content,
            )
            actions.append(action)

            if not dry_run:
                # Move content to detail file
                if target:
                    created = self.move_to_detail_file(
                        section.content, target, section.name
                    )
                    if created and target not in detail_files_created:
                        detail_files_created.append(target)

                # Replace section with pointer or remove entirely
                if pointer:
                    replacement_lines = [pointer, ""]
                    pointers_added.append(pointer)
                else:
                    replacement_lines = []

                working_lines = (
                    working_lines[:section.start_line]
                    + replacement_lines
                    + working_lines[section.end_line:]
                )

        # --- Step 2: Remove pattern-based bloat ---
        pattern_actions = self._detect_pattern_bloat()
        for action in pattern_actions:
            # Only apply if content still present (not already removed by P2 pass)
            if action.content and action.content in "\n".join(working_lines):
                actions.append(action)
                if not dry_run:
                    if action.target_file:
                        created = self.move_to_detail_file(
                            action.content, action.target_file, action.section_name
                        )
                        if created and action.target_file not in detail_files_created:
                            detail_files_created.append(action.target_file)

                    # Remove matched content from working lines
                    joined = "\n".join(working_lines)
                    joined = joined.replace(action.content, "")
                    working_lines = joined.split("\n")

        # --- Step 3: Check if still over budget; trim P1 if needed ---
        current_count = len(working_lines)
        if current_count > self.budget:
            # Re-parse from working content to get updated line numbers
            working_content = "\n".join(working_lines)
            self.content = working_content
            self.lines = working_lines
            updated_sections = self.analyze()

            p1_sections = [
                s for s in updated_sections
                if s.priority == "P1"
            ]
            # Sort by line_count descending to cut largest first
            p1_sections.sort(key=lambda s: s.line_count, reverse=True)

            for section in p1_sections:
                if current_count <= self.budget:
                    break

                target = self._default_target_for_section(section.name)
                pointer = self.generate_pointer(
                    target, section.name
                ) if target else None

                action = OptimizationAction(
                    action="collapse",
                    section_name=section.name,
                    line_count=section.line_count,
                    target_file=target,
                    pointer_text=pointer,
                    content=section.content,
                )
                actions.append(action)

                if not dry_run:
                    if target:
                        created = self.move_to_detail_file(
                            section.content, target, section.name
                        )
                        if created and target not in detail_files_created:
                            detail_files_created.append(target)

                    if pointer:
                        replacement_lines = [pointer, ""]
                        pointers_added.append(pointer)
                    else:
                        replacement_lines = []

                    working_lines = (
                        working_lines[:section.start_line]
                        + replacement_lines
                        + working_lines[section.end_line:]
                    )

                current_count = len(working_lines)

        # --- Step 4: Clean up consecutive blank lines ---
        working_lines = self._collapse_blank_lines(working_lines)

        # --- Step 5: Write result ---
        after_lines = len(working_lines)

        if not dry_run and actions:
            self._save(working_lines)

        # Restore original content for reporting
        if dry_run:
            self.content = "\n".join(self.lines)
        else:
            self.content = "\n".join(working_lines)
            self.lines = working_lines

        return OptimizeResult(
            before_lines=before_lines,
            after_lines=after_lines,
            budget=self.budget,
            actions=actions,
            detail_files_created=detail_files_created,
            pointers_added=pointers_added,
        )

    def move_to_detail_file(self, content: str, target_file: str,
                            section_title: str) -> bool:
        """Move content to a detail file, creating if needed.

        If the target file already exists, the content is appended under
        a new H2 header. If it does not exist, a new file is created
        with a top-level header and the content.

        Args:
            content: Markdown content to move
            target_file: Relative path from project root (e.g. "docs/VERSION-HISTORY.md")
            section_title: Title for the section in the detail file

        Returns:
            True if file was created (new), False if appended to existing
        """
        target_path = self.project_root / target_file
        created = False

        # Ensure parent directory exists
        target_path.parent.mkdir(parents=True, exist_ok=True)

        if target_path.exists():
            existing = target_path.read_text()
            # Append under a separator
            separator = f"\n\n---\n\n## {section_title}\n\n"
            target_path.write_text(existing + separator + content.strip() + "\n")
        else:
            # Create new file with header
            file_title = target_path.stem.replace("-", " ").replace("_", " ").title()
            header = f"# {file_title}\n\n"
            target_path.write_text(header + content.strip() + "\n")
            created = True

        return created

    def generate_pointer(self, target_file: str, description: str) -> str:
        """Generate a pointer line for a detail file.

        Format: -> Description: [FILENAME](relative/path)

        Args:
            target_file: Relative path to detail file
            description: Human-readable description

        Returns:
            Formatted pointer string
        """
        filename = Path(target_file).name
        # Clean up description: remove markdown formatting, trim
        clean_desc = re.sub(r"[*_`#]", "", description).strip()
        # Capitalize first letter
        if clean_desc:
            clean_desc = clean_desc[0].upper() + clean_desc[1:]

        return f"{POINTER_PREFIX} {clean_desc}: [{filename}]({target_file})"

    def generate_report(self, result: OptimizeResult) -> str:
        """Generate formatted optimization report.

        Args:
            result: OptimizeResult from optimize()

        Returns:
            Formatted multi-line report string
        """
        lines: List[str] = []

        # Header
        lines.append("")
        lines.append("CLAUDE.md Optimization Report")
        lines.append("=" * 40)
        lines.append("")

        # Budget summary
        status = "WITHIN BUDGET" if result.within_budget else "OVER BUDGET"
        lines.append(f"Budget:  {result.budget} lines")
        lines.append(f"Before:  {result.before_lines} lines")
        lines.append(f"After:   {result.after_lines} lines")
        lines.append(f"Saved:   {result.lines_saved} lines ({result.reduction_percent}%)")
        lines.append(f"Status:  {status}")
        lines.append("")

        # Actions taken
        if result.actions:
            lines.append(f"Actions ({len(result.actions)}):")
            lines.append("-" * 30)
            for i, action in enumerate(result.actions, 1):
                lines.append(f"  {i}. [{action.action.upper()}] {action.description}")
            lines.append("")

        # Detail files created
        if result.detail_files_created:
            lines.append("Detail files created:")
            for df in result.detail_files_created:
                lines.append(f"  + {df}")
            lines.append("")

        # Pointers added
        if result.pointers_added:
            lines.append("Pointers added:")
            for ptr in result.pointers_added:
                lines.append(f"  {ptr}")
            lines.append("")

        # Remaining budget
        if result.within_budget:
            remaining = result.budget - result.after_lines
            lines.append(f"Remaining budget: {remaining} lines")
        else:
            overage = result.after_lines - result.budget
            lines.append(f"Still over budget by {overage} lines")
            lines.append("Manual editing required to meet budget.")

        lines.append("")

        # Next steps
        if result.actions:
            lines.append("Next steps:")
            lines.append("  1. Review: git diff CLAUDE.md")
            if result.detail_files_created:
                lines.append("  2. Review detail files created")
                lines.append("  3. Run sync: /craft:docs:claude-md:sync")
                lines.append('  4. Commit: git add -A && git commit -m "docs: optimize CLAUDE.md"')
            else:
                lines.append("  2. Run sync: /craft:docs:claude-md:sync")
                lines.append('  3. Commit: git add CLAUDE.md && git commit -m "docs: optimize CLAUDE.md"')
        else:
            lines.append("No optimization needed. CLAUDE.md is within budget.")

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Analysis helpers
    # ------------------------------------------------------------------

    def get_section_breakdown(self) -> str:
        """Generate a section-by-section breakdown table.

        Returns:
            Formatted table showing each section's priority, lines, and budget
        """
        sections = self.analyze()
        if not sections:
            return "No sections found."

        lines: List[str] = []
        lines.append(f"{'Section':<35} {'Priority':>8} {'Lines':>6} {'Budget':>7} {'Status':>10}")
        lines.append("-" * 70)

        total_lines = 0
        for section in sections:
            status = "OVER" if section.over_budget else "OK"
            budget_str = str(section.max_lines) if section.max_lines < 999 else "N/A"
            lines.append(
                f"{section.name[:34]:<35} {section.priority:>8} "
                f"{section.line_count:>6} {budget_str:>7} {status:>10}"
            )
            total_lines += section.line_count

        lines.append("-" * 70)
        budget_status = "WITHIN" if total_lines <= self.budget else "OVER"
        lines.append(
            f"{'TOTAL':<35} {'':>8} {total_lines:>6} {self.budget:>7} {budget_status:>10}"
        )

        return "\n".join(lines)

    # ------------------------------------------------------------------
    # Private helpers
    # ------------------------------------------------------------------

    def _read_budget(self) -> int:
        """Read line budget from project configuration.

        Checks in order:
            1. .claude-plugin/plugin.json -> claude_md_budget
            2. package.json -> claudeMd.budget
            3. Default: 150

        Returns:
            Line budget as integer
        """
        # Try plugin.json
        plugin_json = self.project_root / ".claude-plugin" / "plugin.json"
        if plugin_json.exists():
            try:
                data = json.loads(plugin_json.read_text())
                if "claude_md_budget" in data:
                    return int(data["claude_md_budget"])
            except (json.JSONDecodeError, OSError, ValueError):
                pass

        # Try package.json
        pkg_json = self.project_root / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text())
                claude_md_config = data.get("claudeMd", {})
                if "budget" in claude_md_config:
                    return int(claude_md_config["budget"])
            except (json.JSONDecodeError, OSError, ValueError):
                pass

        return DEFAULT_BUDGET

    def _parse_sections(self) -> List[Tuple[str, int, int, str]]:
        """Parse CLAUDE.md into sections by H2 headers.

        Content before the first H2 is captured as "header".

        Returns:
            List of (name, start_line, end_line, content) tuples
        """
        sections: List[Tuple[str, int, int, str]] = []
        current_name: Optional[str] = None
        current_start = 0

        for i, line in enumerate(self.lines):
            header_match = re.match(r"^##\s+(.+)$", line)
            if header_match:
                # Close previous section
                if current_name is not None:
                    content = "\n".join(self.lines[current_start:i])
                    sections.append((current_name, current_start, i, content))
                elif i > 0:
                    # Content before first H2 -> "header"
                    content = "\n".join(self.lines[0:i])
                    sections.append(("header", 0, i, content))

                current_name = header_match.group(1).strip()
                current_start = i

        # Close final section
        if current_name is not None:
            content = "\n".join(self.lines[current_start:])
            sections.append((current_name, current_start, len(self.lines), content))
        elif not sections and self.lines:
            # Entire file is header (no H2 sections)
            content = "\n".join(self.lines)
            sections.append(("header", 0, len(self.lines), content))

        return sections

    def _classify_section(self, name: str) -> Tuple[str, int]:
        """Classify a section by its name into a priority tier.

        Args:
            name: Section header text

        Returns:
            Tuple of (priority, max_lines) where priority is "P0", "P1", or "P2"
        """
        name_lower = name.lower()

        # Check P0
        for key, max_lines in P0_SECTIONS.items():
            if key in name_lower:
                return ("P0", max_lines)

        # Check P1
        for key, max_lines in P1_SECTIONS.items():
            if key in name_lower:
                return ("P1", max_lines)

        # Check P2
        for p2_name in P2_SECTION_NAMES:
            if p2_name in name_lower:
                return ("P2", 0)

        # Default: treat as P1 with generous budget
        return ("P1", 20)

    def _default_target_for_section(self, section_name: str) -> Optional[str]:
        """Determine the default detail file for a section.

        Args:
            section_name: Section header text

        Returns:
            Relative path to detail file, or None if content should be deleted
        """
        name_lower = section_name.lower()

        # Release / version / feature history -> VERSION-HISTORY.md
        if any(kw in name_lower for kw in [
            "release", "version", "feature status", "feature matrix",
            "recent major", "what shipped", "completed feature",
        ]):
            return DETAIL_FILES["VERSION-HISTORY.md"]

        # Phase / implementation details -> delete (no target)
        if any(kw in name_lower for kw in ["phase", "implementation"]):
            return None

        # Test suite / per-test breakdowns -> CONTRIBUTING.md
        if any(kw in name_lower for kw in ["test suite", "test file", "test breakdown"]):
            return DETAIL_FILES["CONTRIBUTING.md"]

        # Integration features -> VERSION-HISTORY.md
        if "integration" in name_lower:
            return DETAIL_FILES["VERSION-HISTORY.md"]

        # Documentation guides -> CONTRIBUTING.md
        if "documentation guide" in name_lower:
            return DETAIL_FILES["CONTRIBUTING.md"]

        # Fallback: VERSION-HISTORY.md for unknown P2
        return DETAIL_FILES["VERSION-HISTORY.md"]

    def _detect_pattern_bloat(self) -> List[OptimizationAction]:
        """Detect inline bloat via regex patterns.

        Returns:
            List of OptimizationAction for each bloat match found
        """
        actions: List[OptimizationAction] = []

        for bp in BLOAT_PATTERNS:
            pattern = bp["pattern"]
            target = bp["target"]
            name = bp["name"]

            matches = list(re.finditer(pattern, self.content, re.MULTILINE))
            for match in matches:
                matched_text = match.group(0)
                line_count = matched_text.count("\n") + 1

                pointer = None
                if target:
                    pointer = self.generate_pointer(target, name.replace("_", " "))

                actions.append(OptimizationAction(
                    action="move" if target else "delete",
                    section_name=name.replace("_", " "),
                    line_count=line_count,
                    target_file=target,
                    pointer_text=pointer,
                    content=matched_text,
                ))

        return actions

    def _collapse_blank_lines(self, lines: List[str]) -> List[str]:
        """Collapse runs of 3+ consecutive blank lines down to 2.

        Args:
            lines: Input lines

        Returns:
            Cleaned lines with excess blank lines removed
        """
        result: List[str] = []
        blank_count = 0

        for line in lines:
            if line.strip() == "":
                blank_count += 1
                if blank_count <= 2:
                    result.append(line)
            else:
                blank_count = 0
                result.append(line)

        # Strip trailing blank lines
        while result and result[-1].strip() == "":
            result.pop()

        # Ensure file ends with newline (single empty string at end)
        result.append("")

        return result

    def _save(self, lines: List[str]) -> None:
        """Save optimized content to CLAUDE.md with backup.

        Creates a backup at .CLAUDE.md.backup before overwriting.

        Args:
            lines: Optimized lines to write
        """
        # Create backup
        backup_path = self.project_root / ".CLAUDE.md.backup"
        if self.path.exists():
            shutil.copy2(self.path, backup_path)

        # Write optimized content
        self.path.write_text("\n".join(lines))


# ---------------------------------------------------------------------------
# Convenience functions
# ---------------------------------------------------------------------------

def analyze_claude_md(path: Path = None, budget: int = None) -> List[SectionInfo]:
    """Convenience function to analyze a CLAUDE.md file.

    Args:
        path: Path to CLAUDE.md (default: ./CLAUDE.md)
        budget: Line budget override

    Returns:
        List of SectionInfo objects
    """
    claude_md = Path(path) if path else Path.cwd() / "CLAUDE.md"
    optimizer = CLAUDEMDOptimizer(claude_md, budget=budget)
    return optimizer.analyze()


def optimize_claude_md(path: Path = None, budget: int = None,
                       dry_run: bool = False) -> OptimizeResult:
    """Convenience function to optimize a CLAUDE.md file.

    Args:
        path: Path to CLAUDE.md (default: ./CLAUDE.md)
        budget: Line budget override
        dry_run: Preview only

    Returns:
        OptimizeResult with metrics and actions
    """
    claude_md = Path(path) if path else Path.cwd() / "CLAUDE.md"
    optimizer = CLAUDEMDOptimizer(claude_md, budget=budget)
    return optimizer.optimize(dry_run=dry_run)


# ---------------------------------------------------------------------------
# CLI entry point
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Optimize CLAUDE.md to fit within line budget"
    )
    parser.add_argument(
        "file",
        nargs="?",
        default=None,
        help="Path to CLAUDE.md file (default: auto-detect)",
    )
    parser.add_argument(
        "--global",
        dest="global_flag",
        action="store_true",
        help="Operate on ~/.claude/CLAUDE.md",
    )
    parser.add_argument(
        "--budget", "-b",
        type=int,
        default=None,
        help="Line budget (default: read from config or 150)",
    )
    parser.add_argument(
        "--dry-run", "-n",
        action="store_true",
        help="Preview optimization without applying changes",
    )
    parser.add_argument(
        "--analyze", "-a",
        action="store_true",
        help="Show section analysis only (no optimization)",
    )
    parser.add_argument(
        "--breakdown",
        action="store_true",
        help="Show section-by-section breakdown table",
    )

    args = parser.parse_args()

    # Resolve path: explicit file > --global > auto-detect
    if args.file:
        file_path = Path(args.file)
    else:
        try:
            resolved = resolve_claude_md_path(global_flag=args.global_flag)
            file_path = Path(resolved)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    if not file_path.exists():
        print(f"Error: {file_path} not found")
        sys.exit(1)

    optimizer = CLAUDEMDOptimizer(file_path, budget=args.budget)

    if args.breakdown:
        print(optimizer.get_section_breakdown())
        sys.exit(0)

    if args.analyze:
        sections = optimizer.analyze()
        print(f"\nCLAUDE.md Analysis ({len(sections)} sections, {len(optimizer.lines)} lines)")
        print(f"Budget: {optimizer.budget} lines\n")

        for section in sections:
            status = " [OVER]" if section.over_budget else ""
            print(
                f"  [{section.priority}] {section.name} "
                f"(lines {section.start_line + 1}-{section.end_line}, "
                f"{section.line_count} lines, max {section.max_lines}){status}"
            )

        total = sum(s.line_count for s in sections)
        budget_status = "WITHIN" if total <= optimizer.budget else "OVER"
        print(f"\nTotal: {total} lines ({budget_status} budget of {optimizer.budget})")
        sys.exit(0)

    # Run optimization
    result = optimizer.optimize(dry_run=args.dry_run)
    report = optimizer.generate_report(result)
    print(report)

    if args.dry_run:
        print("(Dry run - no changes applied. Remove --dry-run to apply)\n")

    sys.exit(0 if result.within_budget else 1)
