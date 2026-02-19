#!/usr/bin/env python3
"""
CLAUDE.md Sync - Unified Pipeline

Orchestrates a 4-phase sync pipeline for CLAUDE.md files:
  Phase 1: Detect  - Project type, version, counts (via CLAUDEMDDetector)
  Phase 2: Update  - Metric drift detection (version, commands, skills, agents, tests, docs%)
  Phase 3: Audit   - 5 validation checks + bloat audit + anti-pattern detection
  Phase 4: Fix     - Auto-fix issues with backup creation (optional, --fix flag)

Merges logic from:
  - claude_md_detector.py  (CLAUDEMDDetector, ProjectInfo)
  - claude_md_updater_simple.py (SimpleCLAUDEMDUpdater, MetricChange)
  - claude_md_auditor.py (CLAUDEMDAuditor, Issue, Severity)
  - claude_md_fixer.py (CLAUDEMDFixer, FixResult)

Version: 1.0.0
Author: Craft Plugin
"""

import json
import os
import re
import shutil
import sys
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Dict, List, Optional, Tuple

# Import project detector - handle both module and script usage
try:
    from .claude_md_detector import CLAUDEMDDetector, ProjectInfo
except ImportError:
    from claude_md_detector import CLAUDEMDDetector, ProjectInfo


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------

DEFAULT_BUDGET = 150
"""Default line budget for CLAUDE.md when no config override is found."""

ANTI_PATTERNS = [
    {
        "name": "release_notes",
        "pattern": r"^###?\s+v\d+\.\d+",
        "redirect": "VERSION-HISTORY.md",
        "description": "Versioned release headings belong in VERSION-HISTORY.md",
    },
    {
        "name": "release_date",
        "pattern": r"Released\s+\d{4}",
        "redirect": "VERSION-HISTORY.md",
        "description": "Release dates belong in VERSION-HISTORY.md",
    },
    {
        "name": "diffstats",
        "pattern": r"Files Changed:.*\+.*/-",
        "action": "delete",
        "description": "Diffstats are transient and should not appear in CLAUDE.md",
    },
    {
        "name": "what_shipped",
        "pattern": r"What Shipped|Merged PR",
        "redirect": "VERSION-HISTORY.md",
        "description": "Shipping notes belong in VERSION-HISTORY.md",
    },
    {
        "name": "completed_features",
        "pattern": r"Status.*Complete|Released\s+✅",
        "redirect": "VERSION-HISTORY.md",
        "description": "Completed feature tables belong in VERSION-HISTORY.md",
    },
    {
        "name": "phase_details",
        "pattern": r"^###\s+Phase\s+\d",
        "redirect": "VERSION-HISTORY.md",
        "description": "Phase implementation details belong in VERSION-HISTORY.md",
    },
]
"""Anti-patterns that should be blocked from CLAUDE.md."""


# ---------------------------------------------------------------------------
# Shared Data Classes
# ---------------------------------------------------------------------------

class Severity(Enum):
    """Issue severity levels."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


@dataclass
class Issue:
    """Validation issue found in CLAUDE.md."""
    severity: Severity
    category: str
    message: str
    line_number: Optional[int] = None
    fixable: bool = False
    fix_method: Optional[str] = None

    def __str__(self):
        """Format issue for display."""
        severity_icon = {
            Severity.ERROR: "[E]",
            Severity.WARNING: "[W]",
            Severity.INFO: "[I]",
        }
        icon = severity_icon[self.severity]
        line_info = f"L{self.line_number}: " if self.line_number else ""
        return f"{icon} {line_info}{self.message}"


@dataclass
class FixResult:
    """Result of applying a single fix."""
    success: bool
    issue: Issue
    description: str
    lines_changed: int = 0


@dataclass
class MetricChange:
    """Represents a metric drift between CLAUDE.md and project state."""
    name: str
    before: str
    after: str
    pattern: str  # Regex pattern used to locate and replace

    @property
    def description(self) -> str:
        """Human-readable description of the change."""
        return f"{self.name}: {self.before} -> {self.after}"


@dataclass
class SyncResult:
    """Bundled result of the full sync pipeline."""
    project_info: Optional[ProjectInfo]
    metric_changes: List[MetricChange] = field(default_factory=list)
    issues: List[Issue] = field(default_factory=list)
    fix_results: List[FixResult] = field(default_factory=list)
    anti_patterns_found: List[dict] = field(default_factory=list)
    line_count: int = 0
    budget: int = DEFAULT_BUDGET

    @property
    def has_errors(self) -> bool:
        """True if any ERROR-level issues exist."""
        return any(i.severity == Severity.ERROR for i in self.issues)

    @property
    def has_warnings(self) -> bool:
        """True if any WARNING-level issues exist."""
        return any(i.severity == Severity.WARNING for i in self.issues)

    @property
    def is_clean(self) -> bool:
        """True when no metric drift, no issues, and no anti-patterns."""
        return (
            not self.metric_changes
            and not self.issues
            and not self.anti_patterns_found
        )

    @property
    def over_budget(self) -> bool:
        """True when line count exceeds budget."""
        return self.line_count > self.budget


# ---------------------------------------------------------------------------
# Path Resolution (shared via claude_md_common)
# ---------------------------------------------------------------------------

from utils.claude_md_common import resolve_claude_md_path  # noqa: F401, E402


# ---------------------------------------------------------------------------
# CLAUDEMDSync
# ---------------------------------------------------------------------------

class CLAUDEMDSync:
    """Unified sync orchestrator for CLAUDE.md files.

    Runs a 4-phase pipeline:
      1. Detect  - project type via CLAUDEMDDetector
      2. Update  - metric drift detection
      3. Audit   - validation checks + bloat + anti-patterns
      4. Fix     - auto-fix (optional)
    """

    def __init__(self, claude_md_path: Path, budget: int = None):
        """Initialize sync orchestrator.

        Args:
            claude_md_path: Path to the CLAUDE.md file.
            budget: Maximum line count budget.  When *None* the budget is
                    resolved from plugin.json -> package.json -> DEFAULT_BUDGET.
        """
        self.path = Path(claude_md_path)
        self.project_root = self.path.parent
        self.content = ""
        self.lines: List[str] = []

        if self.path.exists():
            self.content = self.path.read_text()
            self.lines = self.content.split("\n")

        # Resolve budget
        self.budget = budget if budget is not None else self._resolve_budget()

        # Lazy-initialised detector result
        self._project_info: Optional[ProjectInfo] = None

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def sync(
        self,
        fix: bool = False,
        optimize: bool = False,
        dry_run: bool = False,
        section: str = "all",
        scope: str = "errors",
    ) -> SyncResult:
        """Run the full 4-phase sync pipeline.

        Args:
            fix:      Apply auto-fixes for detected issues (Phase 4).
            optimize: Aggressively trim bloat when fixing.
            dry_run:  Preview changes without writing to disk.
            section:  Restrict metric updates to a section ("all", "status",
                      "commands", "testing").
            scope:    Fix scope - "errors", "warnings", or "all".

        Returns:
            SyncResult with full pipeline output.
        """
        # Phase 1: Detect
        project_info = self._detect()

        # Phase 2: Update metrics
        metric_changes = self._update_metrics(project_info, section)

        # Phase 3: Audit
        issues = self._audit(project_info)
        anti_patterns = self.detect_anti_patterns()

        # Add bloat issue if over budget
        line_count = len(self.lines)
        if line_count > self.budget:
            issues.append(Issue(
                severity=Severity.WARNING,
                category="bloat",
                message=(
                    f"CLAUDE.md is {line_count} lines "
                    f"(budget: {self.budget}). "
                    f"Consider moving release history to VERSION-HISTORY.md"
                ),
                fixable=False,
            ))

        # Add anti-pattern issues
        for ap in anti_patterns:
            redirect = ap.get("redirect", "")
            action = ap.get("action", "redirect")
            if redirect:
                hint = f" -> move to {redirect}"
            elif action == "delete":
                hint = " -> delete"
            else:
                hint = ""

            issues.append(Issue(
                severity=Severity.WARNING,
                category="anti_pattern",
                message=f"Anti-pattern '{ap['name']}' detected at L{ap['line_number']}{hint}",
                line_number=ap["line_number"],
                fixable=False,
            ))

        # Phase 4: Fix (optional)
        fix_results: List[FixResult] = []
        if fix:
            fix_results = self._fix(issues, scope=scope, dry_run=dry_run)

        # Apply metric updates (unless dry_run)
        if metric_changes and not dry_run:
            self._apply_metric_changes(metric_changes)

        return SyncResult(
            project_info=project_info,
            metric_changes=metric_changes,
            issues=issues,
            fix_results=fix_results,
            anti_patterns_found=anti_patterns,
            line_count=len(self.lines),
            budget=self.budget,
        )

    def detect_anti_patterns(self) -> List[dict]:
        """Detect anti-patterns in CLAUDE.md content.

        Scans every line against the ANTI_PATTERNS registry.  Skips lines
        inside fenced code blocks so that example snippets do not trigger
        false positives.

        Returns:
            List of dicts with keys: name, line_number, line_text, redirect|action,
            description.
        """
        found: List[dict] = []
        in_code_block = False

        for line_num, line in enumerate(self.lines, 1):
            # Track fenced code blocks
            if line.strip().startswith("```"):
                in_code_block = not in_code_block
                continue

            if in_code_block:
                continue

            for ap in ANTI_PATTERNS:
                if re.search(ap["pattern"], line, re.MULTILINE):
                    entry: dict = {
                        "name": ap["name"],
                        "line_number": line_num,
                        "line_text": line.strip(),
                        "description": ap.get("description", ""),
                    }
                    if "redirect" in ap:
                        entry["redirect"] = ap["redirect"]
                    if "action" in ap:
                        entry["action"] = ap["action"]
                    found.append(entry)

        return found

    def generate_report(self, result: SyncResult) -> str:
        """Generate a formatted sync report.

        Args:
            result: SyncResult from a previous sync() call.

        Returns:
            Multi-line report string.
        """
        sections: List[str] = []

        # Header
        if result.project_info:
            sections.append(
                f"Sync Report: {result.project_info.name} "
                f"({result.project_info.type})"
            )
        else:
            sections.append("Sync Report")
        sections.append("")

        # Budget
        budget_status = "OK" if not result.over_budget else "OVER"
        sections.append(
            f"Lines: {result.line_count}/{result.budget} ({budget_status})"
        )
        sections.append("")

        # Metric changes
        if result.metric_changes:
            sections.append(f"Metric Changes ({len(result.metric_changes)}):")
            for mc in result.metric_changes:
                sections.append(f"  {mc.description}")
            sections.append("")

        # Issues grouped by severity
        errors = [i for i in result.issues if i.severity == Severity.ERROR]
        warnings = [i for i in result.issues if i.severity == Severity.WARNING]
        infos = [i for i in result.issues if i.severity == Severity.INFO]

        if errors:
            sections.append(f"Errors ({len(errors)}):")
            for i, issue in enumerate(errors, 1):
                sections.append(f"  {i}. {issue}")
            sections.append("")

        if warnings:
            sections.append(f"Warnings ({len(warnings)}):")
            for i, issue in enumerate(warnings, 1):
                sections.append(f"  {i}. {issue}")
            sections.append("")

        if infos:
            sections.append(f"Info ({len(infos)}):")
            for i, issue in enumerate(infos, 1):
                sections.append(f"  {i}. {issue}")
            sections.append("")

        # Anti-patterns
        if result.anti_patterns_found:
            sections.append(
                f"Anti-Patterns ({len(result.anti_patterns_found)}):"
            )
            for ap in result.anti_patterns_found:
                redirect = ap.get("redirect", "")
                target = f" -> {redirect}" if redirect else ""
                sections.append(
                    f"  L{ap['line_number']}: {ap['name']}{target}"
                )
            sections.append("")

        # Fix results
        if result.fix_results:
            applied = [r for r in result.fix_results if r.success]
            failed = [r for r in result.fix_results if not r.success]

            if applied:
                sections.append(f"Fixes Applied ({len(applied)}):")
                for r in applied:
                    sections.append(f"  + {r.description}")
                sections.append("")

            if failed:
                sections.append(f"Fixes Failed ({len(failed)}):")
                for r in failed:
                    sections.append(f"  - {r.description}")
                sections.append("")

        # Summary line
        total_issues = len(errors) + len(warnings) + len(infos)
        if result.is_clean and not result.metric_changes:
            sections.append("Status: CLEAN - no drift, no issues")
        else:
            parts: List[str] = []
            if result.metric_changes:
                parts.append(f"{len(result.metric_changes)} metric(s) drifted")
            if total_issues:
                parts.append(
                    f"{total_issues} issue(s) "
                    f"({len(errors)}E/{len(warnings)}W/{len(infos)}I)"
                )
            if result.anti_patterns_found:
                parts.append(
                    f"{len(result.anti_patterns_found)} anti-pattern(s)"
                )
            sections.append(f"Status: {', '.join(parts)}")

        # Next steps
        sections.append("")
        if errors or warnings:
            sections.append("Next: sync --fix to auto-fix, or edit manually")
        elif result.metric_changes:
            sections.append("Next: review changes then commit")
        else:
            sections.append("Next: no action needed")

        return "\n".join(sections)

    # ------------------------------------------------------------------
    # Phase 1: Detect
    # ------------------------------------------------------------------

    def _detect(self) -> Optional[ProjectInfo]:
        """Run project detection (cached).

        Returns:
            ProjectInfo or None if detection fails.
        """
        if self._project_info is None:
            detector = CLAUDEMDDetector(self.project_root)
            self._project_info = detector.detect()
        return self._project_info

    # ------------------------------------------------------------------
    # Phase 2: Update Metrics
    # ------------------------------------------------------------------

    def _update_metrics(
        self,
        project_info: Optional[ProjectInfo],
        section: str = "all",
    ) -> List[MetricChange]:
        """Detect metric drift between CLAUDE.md and project state.

        Checks: version, command count, skill count, agent count, test count,
        documentation percentage.

        Args:
            project_info: Detected project info (may be None).
            section: Restrict to a specific section or "all".

        Returns:
            List of MetricChange objects for every drifted metric.
        """
        if not project_info:
            return []

        changes: List[MetricChange] = []

        # Version
        if section in ("all", "status"):
            if change := self._check_version(project_info):
                changes.append(change)

        # Craft-plugin specific counts
        if project_info.type == "craft-plugin":
            if section in ("all", "commands"):
                if change := self._check_command_count(project_info):
                    changes.append(change)
                if change := self._check_skill_count(project_info):
                    changes.append(change)
                if change := self._check_agent_count(project_info):
                    changes.append(change)

            if section in ("all", "testing"):
                if change := self._check_test_count(project_info):
                    changes.append(change)

        # Documentation percentage (from .STATUS)
        if section in ("all", "status"):
            if change := self._check_docs_percent():
                changes.append(change)

        return changes

    def _check_version(self, info: ProjectInfo) -> Optional[MetricChange]:
        """Check version drift."""
        pattern = r"\*\*Current Version:\*\* v([0-9.]+)"
        match = re.search(pattern, self.content)
        if not match:
            return None

        current = match.group(1)
        actual = info.version

        if current != actual:
            return MetricChange(
                name="Version",
                before=f"v{current}",
                after=f"v{actual}",
                pattern=r"(\*\*Current Version:\*\* v)[0-9.]+",
            )
        return None

    def _check_command_count(self, info: ProjectInfo) -> Optional[MetricChange]:
        """Check command count drift."""
        pattern = r"\*\*(\d+) commands\*\*"
        match = re.search(pattern, self.content)
        if not match:
            return None

        current = int(match.group(1))
        actual = len(info.commands)

        if current != actual:
            return MetricChange(
                name="Commands",
                before=f"{current} commands",
                after=f"{actual} commands",
                pattern=r"(\*\*)\d+( commands\*\*)",
            )
        return None

    def _check_skill_count(self, info: ProjectInfo) -> Optional[MetricChange]:
        """Check skill count drift."""
        pattern = r"\*\*(\d+) skills\*\*"
        match = re.search(pattern, self.content)
        if not match:
            return None

        current = int(match.group(1))
        actual = len(info.skills)

        if current != actual:
            return MetricChange(
                name="Skills",
                before=f"{current} skills",
                after=f"{actual} skills",
                pattern=r"(\*\*)\d+( skills\*\*)",
            )
        return None

    def _check_agent_count(self, info: ProjectInfo) -> Optional[MetricChange]:
        """Check agent count drift."""
        pattern = r"\*\*(\d+) agents\*\*"
        match = re.search(pattern, self.content)
        if not match:
            return None

        current = int(match.group(1))
        actual = len(info.agents)

        if current != actual:
            return MetricChange(
                name="Agents",
                before=f"{current} agents",
                after=f"{actual} agents",
                pattern=r"(\*\*)\d+( agents\*\*)",
            )
        return None

    def _check_test_count(self, info: ProjectInfo) -> Optional[MetricChange]:
        """Check test count drift."""
        pattern = r"\*\*Tests:\*\* (\d+)"
        match = re.search(pattern, self.content)
        if not match:
            return None

        current = int(match.group(1))
        actual = info.test_count

        if current != actual:
            return MetricChange(
                name="Tests",
                before=f"{current} passing",
                after=f"{actual} passing",
                pattern=r"(\*\*Tests:\*\* )\d+",
            )
        return None

    def _check_docs_percent(self) -> Optional[MetricChange]:
        """Check documentation percentage drift against .STATUS file."""
        status_file = self.project_root / ".STATUS"
        if not status_file.exists():
            return None

        try:
            status_content = status_file.read_text()
        except OSError:
            return None

        progress_match = re.search(r"progress:\s*(\d+)", status_content)
        if not progress_match:
            return None

        actual = int(progress_match.group(1))

        pattern = r"\*\*Documentation Status:\*\* (\d+)%"
        match = re.search(pattern, self.content)
        if not match:
            return None

        current = int(match.group(1))
        if current != actual:
            return MetricChange(
                name="Documentation",
                before=f"{current}%",
                after=f"{actual}%",
                pattern=r"(\*\*Documentation Status:\*\* )\d+%",
            )
        return None

    def _apply_metric_changes(self, changes: List[MetricChange]) -> None:
        """Apply metric changes to in-memory content and write to disk.

        Uses the same regex-replacement strategy as SimpleCLAUDEMDUpdater.

        Args:
            changes: List of MetricChange objects to apply.
        """
        updated = self.content

        for change in changes:
            if change.name == "Version":
                version_num = change.after.replace("v", "")
                updated = re.sub(
                    change.pattern,
                    lambda m, v=version_num: m.group(1) + v,
                    updated,
                )
            elif change.name in ("Commands", "Skills", "Agents"):
                count = change.after.split()[0]
                updated = re.sub(
                    change.pattern,
                    lambda m, c=count: m.group(1) + c + m.group(2),
                    updated,
                )
            elif change.name == "Tests":
                count = change.after.split()[0]
                updated = re.sub(
                    change.pattern,
                    lambda m, c=count: m.group(1) + c,
                    updated,
                )
            elif change.name == "Documentation":
                percent = change.after.replace("%", "")
                updated = re.sub(
                    change.pattern,
                    lambda m, p=percent: m.group(1) + p + "%",
                    updated,
                )

        self.content = updated
        self.lines = updated.split("\n")
        self.path.write_text(updated)

    # ------------------------------------------------------------------
    # Phase 3: Audit
    # ------------------------------------------------------------------

    def _audit(self, project_info: Optional[ProjectInfo]) -> List[Issue]:
        """Run all validation checks.

        Checks:
          1. Version sync
          2. Command coverage
          3. Broken internal links
          4. Required sections
          5. Status file alignment

        Args:
            project_info: Detected project info (may be None).

        Returns:
            List of Issue objects.
        """
        issues: List[Issue] = []

        issues.extend(self._check_version_sync(project_info))
        issues.extend(self._check_command_coverage())
        issues.extend(self._check_broken_links())
        issues.extend(self._check_required_sections(project_info))
        issues.extend(self._check_status_sync())

        return issues

    def _check_version_sync(self, project_info: Optional[ProjectInfo]) -> List[Issue]:
        """Verify CLAUDE.md version matches source file."""
        issues: List[Issue] = []

        claude_version = self._extract_version_from_content()
        if not claude_version or not project_info:
            return issues

        if claude_version != project_info.version:
            issues.append(Issue(
                severity=Severity.WARNING,
                category="version_mismatch",
                message=(
                    f"Version {claude_version} in CLAUDE.md doesn't match "
                    f"{project_info.version} in {project_info.version_source}"
                ),
                line_number=self._find_line_matching(
                    r"\*\*Current Version:\*\*|^version:"
                ),
                fixable=True,
                fix_method="update_version",
            ))

        return issues

    def _check_command_coverage(self) -> List[Issue]:
        """Verify all commands are documented and no stale references exist."""
        issues: List[Issue] = []

        documented = self._extract_documented_commands()
        actual = self._scan_commands_directory()

        # Stale commands (documented but file deleted)
        for cmd in documented - actual:
            issues.append(Issue(
                severity=Severity.ERROR,
                category="stale_command",
                message=f"Command {cmd} documented but file deleted",
                line_number=self._find_line_containing(cmd),
                fixable=True,
                fix_method="remove_command",
            ))

        # Missing commands (exist but not documented)
        for cmd in actual - documented:
            issues.append(Issue(
                severity=Severity.INFO,
                category="missing_command",
                message=f"Command {cmd} exists but not documented in CLAUDE.md",
                fixable=False,
            ))

        return issues

    def _check_broken_links(self) -> List[Issue]:
        """Find broken internal file links."""
        issues: List[Issue] = []

        link_pattern = re.compile(r"\[([^\]]+)\]\(([^)]+)\)")
        for line_num, line in enumerate(self.lines, 1):
            for match in link_pattern.finditer(line):
                link = match.group(2)

                # Skip external / anchor links
                if link.startswith(("http://", "https://", "mailto:", "#")):
                    continue

                target = self._resolve_link_path(link)
                if not target.exists():
                    issues.append(Issue(
                        severity=Severity.ERROR,
                        category="broken_link",
                        message=f"Link points to non-existent file: {link}",
                        line_number=line_num,
                        fixable=True,
                        fix_method="remove_link",
                    ))

        return issues

    def _check_required_sections(
        self, project_info: Optional[ProjectInfo]
    ) -> List[Issue]:
        """Verify expected sections are present for the project type."""
        issues: List[Issue] = []
        if not project_info:
            return issues

        required_map: Dict[str, List[str]] = {
            "craft-plugin": ["Quick Commands", "Project Structure", "Testing"],
            "teaching-site": ["Overview", "Workflow"],
            "r-package": ["Quick Reference", "Development", "Testing"],
            "mcp-server": ["Tools", "Resources"],
            "generic-node": ["Quick Reference"],
            "generic-python": ["Quick Reference"],
        }

        required = required_map.get(project_info.type, ["Quick Reference"])
        present = self._extract_section_headers()

        for section in required:
            if not any(section.lower() in s.lower() for s in present):
                issues.append(Issue(
                    severity=Severity.WARNING,
                    category="missing_section",
                    message=f"Expected section '{section}' not found",
                    fixable=False,
                ))

        return issues

    def _check_status_sync(self) -> List[Issue]:
        """Verify .STATUS file alignment."""
        issues: List[Issue] = []

        status_file = self.project_root / ".STATUS"
        if not status_file.exists():
            return issues

        status_data = self._parse_status_file(status_file)
        claude_progress = self._extract_progress_from_content()

        if status_data.get("progress") and claude_progress is not None:
            if status_data["progress"] != claude_progress:
                issues.append(Issue(
                    severity=Severity.WARNING,
                    category="status_sync",
                    message=(
                        f"Progress mismatch: "
                        f"CLAUDE.md={claude_progress}%, "
                        f".STATUS={status_data['progress']}%"
                    ),
                    line_number=self._find_line_matching(
                        r"progress:\s*\d+%|\*\*Progress:\*\*\s*\d+%"
                    ),
                    fixable=True,
                    fix_method="update_progress",
                ))

        return issues

    # ------------------------------------------------------------------
    # Phase 4: Fix
    # ------------------------------------------------------------------

    def _fix(
        self,
        issues: List[Issue],
        scope: str = "errors",
        dry_run: bool = False,
    ) -> List[FixResult]:
        """Apply auto-fixes for fixable issues.

        Creates a backup before any modifications.

        Args:
            issues: Issues from audit phase.
            scope: Fix scope - "errors", "warnings", or "all".
            dry_run: Preview fixes without writing to disk.

        Returns:
            List of FixResult objects.
        """
        filtered = self._filter_issues_by_scope(issues, scope)
        fixable = [i for i in filtered if i.fixable]

        if not fixable:
            return []

        # Create backup before fixing
        if not dry_run:
            self._create_backup()

        results: List[FixResult] = []
        for issue in fixable:
            result = self._apply_fix(issue, dry_run)
            results.append(result)

        # Persist changes
        if not dry_run and any(r.success for r in results):
            self.path.write_text(self.content)

        return results

    def _apply_fix(self, issue: Issue, dry_run: bool) -> FixResult:
        """Route an issue to its fix handler.

        Args:
            issue: Issue to fix.
            dry_run: Preview only.

        Returns:
            FixResult describing outcome.
        """
        handler_map = {
            "update_version": self._fix_version_mismatch,
            "remove_command": self._fix_stale_command,
            "remove_link": self._fix_broken_link,
            "update_progress": self._fix_status_sync,
        }

        handler = handler_map.get(issue.fix_method)
        if handler is None:
            return FixResult(
                success=False,
                issue=issue,
                description=f"Unknown fix method: {issue.fix_method}",
            )

        return handler(issue, dry_run)

    def _fix_version_mismatch(self, issue: Issue, dry_run: bool) -> FixResult:
        """Fix version mismatch by updating CLAUDE.md to match source."""
        detector = CLAUDEMDDetector(self.project_root)
        project_info = detector.detect()

        if not project_info:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not detect project type",
            )

        old_match = re.search(r"v?([\d.]+)", issue.message)
        if not old_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse version from issue",
            )

        old_version = old_match.group(1)
        new_version = project_info.version

        patterns = [
            (
                r"\*\*Current Version:\*\*\s+v?[\d.]+",
                f"**Current Version:** v{new_version}",
            ),
            (r"^version:\s+v?[\d.]+", f"version: {new_version}"),
            (r"v([\d.]+)\s+\(released", f"v{new_version} (released"),
        ]

        lines_changed = 0
        for pattern, replacement in patterns:
            new_content, count = re.subn(
                pattern, replacement, self.content, flags=re.MULTILINE
            )
            if count > 0:
                if not dry_run:
                    self.content = new_content
                    self.lines = self.content.split("\n")
                lines_changed = count
                break

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Updated version: v{old_version} -> v{new_version}",
            lines_changed=lines_changed,
        )

    def _fix_stale_command(self, issue: Issue, dry_run: bool) -> FixResult:
        """Remove references to a deleted command."""
        cmd_match = re.search(r"(/craft:[a-z0-9:-]+)", issue.message)
        if not cmd_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse command from issue",
            )

        command = cmd_match.group(1)
        lines_changed = 0
        new_lines = []

        for line in self.lines:
            if command in line:
                lines_changed += 1
                continue  # drop the line
            new_lines.append(line)

        if lines_changed > 0 and not dry_run:
            self.lines = new_lines
            self.content = "\n".join(self.lines)

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Removed stale command: {command}",
            lines_changed=lines_changed,
        )

    def _fix_broken_link(self, issue: Issue, dry_run: bool) -> FixResult:
        """Comment out a broken link."""
        link_match = re.search(r"file: (.+)$", issue.message)
        if not link_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse link from issue",
            )

        link = link_match.group(1)
        lines_changed = 0
        new_lines = []

        for line in self.lines:
            if link in line:
                new_lines.append(f"<!-- {line.strip()} --> (link broken)")
                lines_changed += 1
            else:
                new_lines.append(line)

        if lines_changed > 0 and not dry_run:
            self.lines = new_lines
            self.content = "\n".join(self.lines)

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Commented out broken link: {link}",
            lines_changed=lines_changed,
        )

    def _fix_status_sync(self, issue: Issue, dry_run: bool) -> FixResult:
        """Fix progress mismatch by syncing from .STATUS."""
        progress_match = re.search(
            r"CLAUDE\.md=(\d+)%.*\.STATUS=(\d+)%", issue.message
        )
        if not progress_match:
            return FixResult(
                success=False,
                issue=issue,
                description="Could not parse progress from issue",
            )

        old_progress = progress_match.group(1)
        new_progress = progress_match.group(2)

        patterns = [
            (r"progress:\s*\d+%", f"progress: {new_progress}%"),
            (r"\*\*Progress:\*\*\s*\d+%", f"**Progress:** {new_progress}%"),
        ]

        lines_changed = 0
        for pattern, replacement in patterns:
            new_content, count = re.subn(
                pattern, replacement, self.content, flags=re.IGNORECASE
            )
            if count > 0:
                if not dry_run:
                    self.content = new_content
                    self.lines = self.content.split("\n")
                lines_changed = count
                break

        return FixResult(
            success=lines_changed > 0,
            issue=issue,
            description=f"Updated progress: {old_progress}% -> {new_progress}%",
            lines_changed=lines_changed,
        )

    # ------------------------------------------------------------------
    # Helpers: Extraction
    # ------------------------------------------------------------------

    def _extract_version_from_content(self) -> Optional[str]:
        """Extract version string from CLAUDE.md content."""
        patterns = [
            r"\*\*Version:\*\*\s+v?([\d.]+)",
            r"\*\*Current Version:\*\*\s+v?([\d.]+)",
            r"^version:\s+v?([\d.]+)",
            r"v([\d.]+)\s+\(released",
        ]
        for pattern in patterns:
            match = re.search(pattern, self.content, re.MULTILINE)
            if match:
                return match.group(1)
        return None

    def _extract_documented_commands(self) -> set:
        """Extract command paths referenced in CLAUDE.md."""
        commands: set = set()
        pattern = r"/craft:[a-z0-9:-]+"
        for match in re.finditer(pattern, self.content):
            commands.add(match.group(0))
        return commands

    def _scan_commands_directory(self) -> set:
        """Scan commands/ for actual command files."""
        commands_dir = self.project_root / "commands"
        if not commands_dir.exists():
            return set()

        commands: set = set()
        for cmd_file in commands_dir.rglob("*.md"):
            rel = cmd_file.relative_to(commands_dir)
            cmd_name = "/craft:" + str(rel.with_suffix("")).replace("/", ":")
            commands.add(cmd_name)
        return commands

    def _extract_section_headers(self) -> List[str]:
        """Extract H1/H2 section headers from CLAUDE.md."""
        sections: List[str] = []
        pattern = re.compile(r"^##?\s+(.+)$")
        for line in self.lines:
            match = pattern.match(line)
            if match:
                title = match.group(1)
                title = re.sub(r"\[([^\]]+)\]\([^)]+\)", r"\1", title)
                title = re.sub(r"[*_`]", "", title)
                sections.append(title.strip())
        return sections

    def _extract_progress_from_content(self) -> Optional[int]:
        """Extract progress percentage from CLAUDE.md."""
        patterns = [
            r"progress:\s*(\d+)%",
            r"\*\*Progress:\*\*\s*(\d+)%",
        ]
        for pattern in patterns:
            match = re.search(pattern, self.content, re.IGNORECASE)
            if match:
                return int(match.group(1))
        return None

    # ------------------------------------------------------------------
    # Helpers: Line Search
    # ------------------------------------------------------------------

    def _find_line_matching(self, pattern: str) -> Optional[int]:
        """Find the first line matching a regex pattern (1-indexed)."""
        compiled = re.compile(pattern, re.IGNORECASE)
        for i, line in enumerate(self.lines, 1):
            if compiled.search(line):
                return i
        return None

    def _find_line_containing(self, text: str) -> Optional[int]:
        """Find the first line containing literal text (1-indexed)."""
        for i, line in enumerate(self.lines, 1):
            if text in line:
                return i
        return None

    # ------------------------------------------------------------------
    # Helpers: Link Resolution
    # ------------------------------------------------------------------

    def _resolve_link_path(self, link: str) -> Path:
        """Resolve an internal markdown link to an absolute path."""
        if link.startswith("/"):
            return self.project_root / link.lstrip("/")
        return (self.path.parent / link).resolve()

    # ------------------------------------------------------------------
    # Helpers: Status Parsing
    # ------------------------------------------------------------------

    def _parse_status_file(self, status_file: Path) -> dict:
        """Parse .STATUS file into a dict.

        Args:
            status_file: Path to .STATUS file.

        Returns:
            Dictionary with parsed fields.  The ``progress`` key is an int
            when present.
        """
        data: dict = {}
        try:
            content = status_file.read_text()
            for line in content.split("\n"):
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    if key == "progress":
                        match = re.search(r"(\d+)%", value)
                        if match:
                            data[key] = int(match.group(1))
                    else:
                        data[key] = value
        except OSError:
            pass
        return data

    # ------------------------------------------------------------------
    # Helpers: Scope Filtering
    # ------------------------------------------------------------------

    def _filter_issues_by_scope(
        self, issues: List[Issue], scope: str
    ) -> List[Issue]:
        """Filter issues by severity scope.

        Args:
            issues: Full issue list.
            scope: "errors" | "warnings" | "all".

        Returns:
            Filtered list.
        """
        if scope == "errors":
            return [i for i in issues if i.severity == Severity.ERROR]
        elif scope == "warnings":
            return [
                i
                for i in issues
                if i.severity in (Severity.ERROR, Severity.WARNING)
            ]
        elif scope == "all":
            return issues
        # Default: errors only
        return [i for i in issues if i.severity == Severity.ERROR]

    # ------------------------------------------------------------------
    # Helpers: Backup & Budget
    # ------------------------------------------------------------------

    def _create_backup(self) -> Path:
        """Create a backup of CLAUDE.md before modifying.

        Returns:
            Path to the backup file.
        """
        backup_path = self.path.parent / f".{self.path.name}.backup"
        shutil.copy2(self.path, backup_path)
        return backup_path

    def _resolve_budget(self) -> int:
        """Resolve line budget from config files.

        Priority:
          1. .claude-plugin/config.json ``claude_md_budget`` field
          2. package.json ``claudeMd.budget`` field
          3. DEFAULT_BUDGET constant (150)

        Note: plugin.json is NOT checked — Claude Code's strict schema
        rejects unrecognized keys and breaks plugin loading.

        Returns:
            Line budget as integer.
        """
        # Try .claude-plugin/config.json (separate from manifest)
        config_json = self.project_root / ".claude-plugin" / "config.json"
        if config_json.exists():
            try:
                data = json.loads(config_json.read_text())
                if "claude_md_budget" in data:
                    return int(data["claude_md_budget"])
            except (json.JSONDecodeError, OSError, ValueError):
                pass

        # Try package.json
        package_json = self.project_root / "package.json"
        if package_json.exists():
            try:
                data = json.loads(package_json.read_text())
                claude_md_config = data.get("claudeMd", {})
                if "budget" in claude_md_config:
                    return int(claude_md_config["budget"])
            except (json.JSONDecodeError, OSError, ValueError):
                pass

        return DEFAULT_BUDGET


# ---------------------------------------------------------------------------
# Reference File Generation
# ---------------------------------------------------------------------------

class ReferenceFileGenerator:
    """Generates .claude/reference/ files from project state.

    Produces on-demand reference files that complement the lean CLAUDE.md:
      - agents.md    — Agent table from agents/ directory
      - test-suite.md — Test file inventory with counts
      - project-structure.md — Directory tree, key files, version history
    """

    def __init__(self, project_root: Path):
        self.project_root = Path(project_root)
        self.reference_dir = self.project_root / ".claude" / "reference"

    def generate_all(self) -> List[str]:
        """Generate all reference files. Returns list of files written."""
        self.reference_dir.mkdir(parents=True, exist_ok=True)
        written: List[str] = []

        for gen_func in (
            self._generate_agents,
            self._generate_test_suite,
            self._generate_project_structure,
        ):
            path = gen_func()
            if path:
                written.append(str(path))

        return written

    def _generate_agents(self) -> Optional[Path]:
        """Generate agents.md from agents/ directory."""
        agents_dir = self.project_root / "agents"
        if not agents_dir.exists():
            return None

        agents: List[dict] = []
        for md_file in sorted(agents_dir.rglob("*.md")):
            name = md_file.stem
            model = "—"
            description = ""

            content = md_file.read_text()
            for line in content.split("\n")[:30]:
                if line.strip().startswith("model:"):
                    model = line.split(":", 1)[1].strip().strip('"\'')
                elif line.strip().startswith("description:"):
                    desc = line.split(":", 1)[1].strip()
                    # Truncate long descriptions
                    description = desc[:80] + "..." if len(desc) > 80 else desc

            agents.append({"name": name, "model": model, "description": description})

        # Deduplicate by name (rglob may find duplicates)
        seen: set = set()
        unique_agents: List[dict] = []
        for a in agents:
            if a["name"] not in seen:
                seen.add(a["name"])
                unique_agents.append(a)

        lines = [
            f"# Craft Agents\n",
            f"{len(unique_agents)} agents in `agents/` directory.\n",
            "| Agent | Model | Use For |",
            "|-------|-------|---------|",
        ]
        for a in unique_agents:
            lines.append(f"| **{a['name']}** | {a['model']} | {a['description']} |")
        lines.append("")

        out = self.reference_dir / "agents.md"
        out.write_text("\n".join(lines))
        return out

    def _generate_test_suite(self) -> Optional[Path]:
        """Generate test-suite.md from test files."""
        tests_dir = self.project_root / "tests"
        if not tests_dir.exists():
            return None

        test_files: List[dict] = []
        for tf in sorted(tests_dir.glob("test_*")):
            name = tf.name
            # Classify test type
            if "e2e" in name:
                test_type = "E2E"
            elif "integration" in name:
                test_type = "Integration"
            elif "dogfood" in name:
                test_type = "Dogfood"
            else:
                test_type = "Unit"
            test_files.append({"name": name, "type": test_type})

        lines = [
            "# Craft Test Suite\n",
            "## Test Files\n",
            "| File | Type |",
            "|------|------|",
        ]
        for tf in test_files:
            lines.append(f"| `{tf['name']}` | {tf['type']} |")

        lines.extend([
            "",
            "## Run All Tests\n",
            "```bash",
            "python3 tests/test_craft_plugin.py && \\",
            "python3 tests/test_integration_*.py && \\",
            "bash tests/test_dependency_management.sh && \\",
            "bash tests/test_formatting.sh && \\",
            "bash tests/test_branch_guard.sh && \\",
            "bash tests/test_branch_guard_e2e.sh && \\",
            "bash tests/test_release_skill_e2e.sh",
            "```",
            "",
        ])

        out = self.reference_dir / "test-suite.md"
        out.write_text("\n".join(lines))
        return out

    def _generate_project_structure(self) -> Optional[Path]:
        """Generate project-structure.md from filesystem."""
        # Count items
        commands_dir = self.project_root / "commands"
        skills_dir = self.project_root / "skills"
        agents_dir = self.project_root / "agents"
        specs_dir = self.project_root / "docs" / "specs"

        cmd_count = len(list(commands_dir.rglob("*.md"))) if commands_dir.exists() else 0
        skill_count = len(list(skills_dir.rglob("*.md"))) if skills_dir.exists() else 0
        agent_count = len(list(agents_dir.rglob("*.md"))) if agents_dir.exists() else 0
        spec_count = len(list(
            specs_dir.rglob("SPEC-*.md")
        )) if specs_dir.exists() else 0

        # Read version from plugin.json or .STATUS
        version = "unknown"
        plugin_json = self.project_root / ".claude-plugin" / "plugin.json"
        if plugin_json.exists():
            try:
                data = json.loads(plugin_json.read_text())
                version = data.get("version", version)
            except (json.JSONDecodeError, OSError):
                pass

        lines = [
            "# Craft Project Structure\n",
            f"**{cmd_count} commands** . **{skill_count} skills** . "
            f"**{agent_count} agents** . **{spec_count} specs**\n",
            f"**Version:** v{version}\n",
            "## Directory Layout\n",
            "```text",
            "craft/",
            f"├── .claude-plugin/     # Plugin manifest, hooks, validators",
            f"├── commands/           # {cmd_count} commands",
            f"├── skills/             # {skill_count} skills",
            f"├── agents/             # {agent_count} agents",
            f"├── scripts/            # Utility scripts",
            f"├── utils/              # Python utilities",
            f"├── tests/              # Test suite",
            "├── docs/",
            f"│   ├── specs/          # {spec_count} specs",
            "│   ├── guide/          # User guides",
            "│   ├── tutorials/      # Step-by-step guides",
            "│   └── brainstorm/     # Working drafts (gitignored)",
            "└── .STATUS             # Current milestone and progress",
            "```",
            "",
        ]

        out = self.reference_dir / "project-structure.md"
        out.write_text("\n".join(lines))
        return out


# ---------------------------------------------------------------------------
# Convenience Function
# ---------------------------------------------------------------------------

def sync_claude_md(
    path: Path = None,
    fix: bool = False,
    optimize: bool = False,
    dry_run: bool = False,
    section: str = "all",
) -> Tuple[SyncResult, str]:
    """Main entry point for syncing CLAUDE.md.

    Locates the CLAUDE.md file (at *path* or in the current directory),
    runs the full sync pipeline, and returns both the structured result
    and a formatted human-readable report.

    Args:
        path:     Path to CLAUDE.md or its parent directory.
                  Defaults to ``Path.cwd() / "CLAUDE.md"``.
        fix:      Apply auto-fixes for detected issues.
        optimize: Aggressively trim bloat when fixing.
        dry_run:  Preview changes without writing to disk.
        section:  Restrict metric updates to a section ("all", "status",
                  "commands", "testing").

    Returns:
        Tuple of (SyncResult, report_string).
    """
    if path is None:
        claude_md_path = Path.cwd() / "CLAUDE.md"
    elif path.is_dir():
        claude_md_path = path / "CLAUDE.md"
    else:
        claude_md_path = path

    if not claude_md_path.exists():
        empty_result = SyncResult(project_info=None)
        return empty_result, "CLAUDE.md not found. Use /craft:docs:claude-md:init to create."

    syncer = CLAUDEMDSync(claude_md_path)
    result = syncer.sync(
        fix=fix,
        optimize=optimize,
        dry_run=dry_run,
        section=section,
    )
    report = syncer.generate_report(result)

    return result, report


# ---------------------------------------------------------------------------
# CLI
# ---------------------------------------------------------------------------

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Sync CLAUDE.md with project state"
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
        "--fix",
        action="store_true",
        help="Apply auto-fixes for detected issues",
    )
    parser.add_argument(
        "--optimize",
        action="store_true",
        help="Aggressively trim bloat when fixing",
    )
    parser.add_argument(
        "--dry-run",
        "-n",
        action="store_true",
        help="Preview changes without writing to disk",
    )
    parser.add_argument(
        "--section",
        default="all",
        choices=["all", "status", "commands", "testing"],
        help="Restrict to a specific section (default: all)",
    )
    parser.add_argument(
        "--scope",
        default="errors",
        choices=["errors", "warnings", "all"],
        help="Fix scope (default: errors)",
    )
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Exit with error code if issues found",
    )
    parser.add_argument(
        "--generate-reference",
        action="store_true",
        help="Generate .claude/reference/ files from project state",
    )

    args = parser.parse_args()

    # Handle --generate-reference
    if args.generate_reference:
        project_root = Path(args.file).parent if args.file else Path.cwd()
        if args.file and Path(args.file).is_file():
            project_root = Path(args.file).parent
        gen = ReferenceFileGenerator(project_root)
        written = gen.generate_all()
        if written:
            print(f"Generated {len(written)} reference file(s):")
            for f in written:
                print(f"  {f}")
        else:
            print("No reference files generated (missing source directories)")
        sys.exit(0)

    # Resolve path: explicit file > --global > auto-detect
    if args.file:
        file_path = args.file
    else:
        try:
            file_path = resolve_claude_md_path(global_flag=args.global_flag)
        except FileNotFoundError as e:
            print(f"Error: {e}", file=sys.stderr)
            sys.exit(1)

    syncer = CLAUDEMDSync(Path(file_path))
    result = syncer.sync(
        fix=args.fix,
        optimize=args.optimize,
        dry_run=args.dry_run,
        section=args.section,
        scope=args.scope,
    )
    report = syncer.generate_report(result)
    print(report)

    if args.strict and result.has_errors:
        sys.exit(1)
    elif result.is_clean:
        sys.exit(0)
    else:
        sys.exit(0)
