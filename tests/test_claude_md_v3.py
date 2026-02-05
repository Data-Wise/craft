#!/usr/bin/env python3
"""
Tests for CLAUDE.md v3 - Sync Pipeline & Budget Optimizer

Covers:
- CLAUDEMDSync: 4-phase sync pipeline (detect, update, audit, fix)
- CLAUDEMDOptimizer: section classification, bloat detection, budget enforcement
- Anti-pattern detection across both modules
"""

import unittest
import tempfile
import json
import os
import shutil
import sys
from pathlib import Path
from unittest.mock import patch

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_common import resolve_claude_md_path
from utils.claude_md_sync import (
    CLAUDEMDSync,
    SyncResult,
    Issue,
    Severity,
    MetricChange,
    FixResult,
    sync_claude_md,
    ANTI_PATTERNS,
    DEFAULT_BUDGET,
)
from utils.claude_md_optimizer import (
    CLAUDEMDOptimizer,
    SectionInfo,
    OptimizationAction,
    OptimizeResult,
    analyze_claude_md,
    optimize_claude_md,
    P0_SECTIONS,
    P1_SECTIONS,
    P2_SECTION_NAMES,
    POINTER_PREFIX,
)


# ---------------------------------------------------------------------------
# Fixture templates
# ---------------------------------------------------------------------------

PLUGIN_JSON = json.dumps({
    "name": "test-plugin",
    "version": "1.0.0",
    "description": "Test plugin"
})

CLEAN_CLAUDE_MD = """\
# CLAUDE.md - Test Plugin

> **TL;DR**: Test plugin for unit tests.

**Current Version:** v1.0.0 | **Tests:** 10 passing

## Git Workflow

```text
main <- dev <- feature/*
```

## Quick Commands

| Task | Command |
|------|---------|
| Test | `pytest` |

## Project Structure

```text
src/
  main.py
```

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tests fail | Run pytest |
"""

BLOATED_CLAUDE_MD = CLEAN_CLAUDE_MD + """
## v2.11.0 - Test Suite Cleanup (Released 2026-02-03)

**What Shipped:**
- Feature A
- Feature B

**Files Changed:** 28 (+1,711/-801)

## Recent Major Features

### v2.10.0 - Claude-MD Command Suite (Released 2026-01-30)

**Merged PR:** #39

- 5 new commands
- 81 tests

### Completed Features (v2.8.0)

| Feature | Status |
|---------|--------|
| Lint command | Released |
| Auto-fix | Released |

## Phase 3 Documentation Enhancements

**Status:** Completed (87% -> 95% target)

### Phase 1 Implementation

- Step A
- Step B

### Phase 2 Refinement

- Step C
- Step D
""" + "\n".join([f"Filler line {i}" for i in range(80)])


VERSION_MISMATCH_CLAUDE_MD = """\
# CLAUDE.md - Test Plugin

> **TL;DR**: Test plugin

**Current Version:** v0.9.0 | **Tests:** 10 passing

## Git Workflow

main <- dev <- feature/*

## Quick Commands

| Task | Command |
|------|---------|
| Test | `pytest` |
"""


# ---------------------------------------------------------------------------
# TestCLAUDEMDSync
# ---------------------------------------------------------------------------

class TestCLAUDEMDSync(unittest.TestCase):
    """Test the CLAUDEMDSync pipeline."""

    def setUp(self):
        """Create temporary project directory with plugin fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create .claude-plugin/plugin.json
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(PLUGIN_JSON)

        # Create commands directory with one command
        commands_dir = self.path / "commands"
        commands_dir.mkdir()
        (commands_dir / "test.md").write_text("# Test command")

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_claude_md(self, content):
        """Helper: write CLAUDE.md to temp dir."""
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)
        return claude_md

    def test_sync_detects_project_type(self):
        """CLAUDEMDSync detects project type via Phase 1."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md)
        result = syncer.sync(dry_run=True)

        self.assertIsNotNone(result.project_info)
        self.assertEqual(result.project_info.type, "craft-plugin")
        self.assertEqual(result.project_info.name, "test-plugin")

    def test_sync_updates_metrics(self):
        """CLAUDEMDSync detects stale version metric."""
        claude_md = self._write_claude_md(VERSION_MISMATCH_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md)
        result = syncer.sync(dry_run=True)

        # Version 0.9.0 in CLAUDE.md vs 1.0.0 in plugin.json
        version_changes = [
            mc for mc in result.metric_changes if mc.name == "Version"
        ]
        self.assertEqual(len(version_changes), 1)
        self.assertIn("0.9.0", version_changes[0].before)
        self.assertIn("1.0.0", version_changes[0].after)

    def test_sync_audit_finds_issues(self):
        """CLAUDEMDSync audit phase catches version mismatch."""
        claude_md = self._write_claude_md(VERSION_MISMATCH_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md)
        result = syncer.sync(dry_run=True)

        version_issues = [
            i for i in result.issues if i.category == "version_mismatch"
        ]
        self.assertTrue(len(version_issues) >= 1)
        self.assertEqual(version_issues[0].severity, Severity.WARNING)
        self.assertTrue(version_issues[0].fixable)

    def test_sync_fix_mode(self):
        """CLAUDEMDSync with fix=True applies fixes."""
        claude_md = self._write_claude_md(VERSION_MISMATCH_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md, budget=500)
        result = syncer.sync(fix=True, scope="warnings")

        # Should have attempted to fix the version mismatch
        version_fixes = [
            fr for fr in result.fix_results
            if "version" in fr.description.lower()
        ]
        self.assertTrue(len(version_fixes) >= 1)
        # At least one fix should succeed
        self.assertTrue(any(fr.success for fr in version_fixes))

        # Verify CLAUDE.md was updated on disk
        updated_content = claude_md.read_text()
        self.assertIn("v1.0.0", updated_content)

    def test_sync_dry_run(self):
        """CLAUDEMDSync dry_run=True does not modify files."""
        claude_md = self._write_claude_md(VERSION_MISMATCH_CLAUDE_MD)
        original_content = claude_md.read_text()

        syncer = CLAUDEMDSync(claude_md, budget=500)
        result = syncer.sync(fix=True, dry_run=True, scope="warnings")

        # File should remain unchanged
        self.assertEqual(claude_md.read_text(), original_content)

    def test_sync_anti_pattern_detection(self):
        """CLAUDEMDSync detects anti-patterns in bloated content."""
        claude_md = self._write_claude_md(BLOATED_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md)
        result = syncer.sync(dry_run=True)

        self.assertTrue(len(result.anti_patterns_found) > 0)

        # Check that specific anti-pattern names appear
        ap_names = [ap["name"] for ap in result.anti_patterns_found]
        # The bloated fixture contains release notes, what_shipped, diffstats
        self.assertTrue(
            any(name in ap_names for name in [
                "release_notes", "release_date", "what_shipped", "diffstats"
            ]),
            f"Expected anti-patterns not found. Got: {ap_names}"
        )

    def test_sync_over_budget_detection(self):
        """CLAUDEMDSync detects when CLAUDE.md exceeds line budget."""
        claude_md = self._write_claude_md(BLOATED_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md, budget=50)
        result = syncer.sync(dry_run=True)

        self.assertTrue(result.over_budget)
        self.assertGreater(result.line_count, 50)

        # Should have a bloat issue
        bloat_issues = [
            i for i in result.issues if i.category == "bloat"
        ]
        self.assertTrue(len(bloat_issues) >= 1)

    def test_sync_clean_file(self):
        """CLAUDEMDSync reports is_clean for a well-formed file."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md, budget=500)
        result = syncer.sync(dry_run=True)

        # A clean file (matching version, no anti-patterns, under budget)
        # may still have info-level issues like missing commands coverage,
        # so we check that there are no errors and no anti-patterns
        self.assertFalse(result.has_errors)
        self.assertEqual(len(result.anti_patterns_found), 0)

    def test_sync_result_properties(self):
        """SyncResult has_errors, has_warnings, is_clean, over_budget work."""
        # Empty result should be clean
        result = SyncResult(project_info=None)
        self.assertTrue(result.is_clean)
        self.assertFalse(result.has_errors)
        self.assertFalse(result.has_warnings)
        self.assertFalse(result.over_budget)

        # Result with an error
        result_err = SyncResult(
            project_info=None,
            issues=[Issue(
                severity=Severity.ERROR,
                category="test",
                message="test error",
            )],
        )
        self.assertTrue(result_err.has_errors)
        self.assertFalse(result_err.is_clean)

        # Result with a warning
        result_warn = SyncResult(
            project_info=None,
            issues=[Issue(
                severity=Severity.WARNING,
                category="test",
                message="test warning",
            )],
        )
        self.assertTrue(result_warn.has_warnings)
        self.assertFalse(result_warn.has_errors)

        # Over budget
        result_budget = SyncResult(
            project_info=None,
            line_count=200,
            budget=150,
        )
        self.assertTrue(result_budget.over_budget)

        # Under budget
        result_ok = SyncResult(
            project_info=None,
            line_count=100,
            budget=150,
        )
        self.assertFalse(result_ok.over_budget)

    def test_sync_convenience_function(self):
        """sync_claude_md() convenience function works."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        result, report = sync_claude_md(path=claude_md, dry_run=True)

        self.assertIsInstance(result, SyncResult)
        self.assertIsInstance(report, str)
        self.assertIn("Sync Report", report)

    def test_sync_convenience_missing_file(self):
        """sync_claude_md() handles missing CLAUDE.md gracefully."""
        missing_path = self.path / "nonexistent" / "CLAUDE.md"
        result, report = sync_claude_md(path=missing_path, dry_run=True)

        self.assertIsNone(result.project_info)
        self.assertIn("not found", report)


# ---------------------------------------------------------------------------
# TestCLAUDEMDOptimizer
# ---------------------------------------------------------------------------

class TestCLAUDEMDOptimizer(unittest.TestCase):
    """Test the CLAUDEMDOptimizer budget enforcer."""

    def setUp(self):
        """Create temporary project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Create plugin.json
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(PLUGIN_JSON)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_claude_md(self, content):
        """Helper: write CLAUDE.md to temp dir."""
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)
        return claude_md

    def test_optimizer_analyze_sections(self):
        """CLAUDEMDOptimizer.analyze() identifies sections by H2 headers."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md)
        sections = optimizer.analyze()

        # Should find header + Git Workflow + Quick Commands + Project Structure + Troubleshooting
        section_names = [s.name for s in sections]
        self.assertIn("header", section_names)
        self.assertIn("Git Workflow", section_names)
        self.assertIn("Quick Commands", section_names)
        self.assertIn("Project Structure", section_names)
        self.assertIn("Troubleshooting", section_names)

    def test_optimizer_p0_classification(self):
        """P0 sections are classified correctly."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md)
        sections = optimizer.analyze()

        p0_names = [s.name for s in sections if s.priority == "P0"]

        # Git Workflow, Quick Commands, Project Structure, Troubleshooting should be P0
        for expected in ["Git Workflow", "Quick Commands", "Project Structure", "Troubleshooting"]:
            self.assertIn(
                expected, p0_names,
                f"Expected '{expected}' to be P0 but got: {p0_names}"
            )

    def test_optimizer_p1_classification(self):
        """P1 sections are classified correctly."""
        content = CLEAN_CLAUDE_MD + "\n## Agents\n\n| Agent | Purpose |\n|---|---|\n| test | testing |\n"
        content += "\n## Execution Modes\n\n| Mode | Use |\n|---|---|\n| default | normal |\n"
        claude_md = self._write_claude_md(content)
        optimizer = CLAUDEMDOptimizer(claude_md)
        sections = optimizer.analyze()

        p1_names = [s.name for s in sections if s.priority == "P1"]
        self.assertIn("Agents", p1_names)
        self.assertIn("Execution Modes", p1_names)

    def test_optimizer_p2_classification(self):
        """P2 sections (release notes, version history) are classified correctly."""
        claude_md = self._write_claude_md(BLOATED_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md)
        sections = optimizer.analyze()

        p2_names = [s.name for s in sections if s.priority == "P2"]
        # The bloated fixture has "Recent Major Features" and "Phase 3..." sections
        self.assertTrue(
            any("Recent Major Features" in name for name in p2_names)
            or any("Phase" in name for name in p2_names),
            f"Expected P2 sections not found. Got: {p2_names}"
        )

    def test_optimizer_detect_bloat(self):
        """CLAUDEMDOptimizer.detect_bloat() finds bloated content."""
        claude_md = self._write_claude_md(BLOATED_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md)
        actions = optimizer.detect_bloat()

        self.assertTrue(len(actions) > 0)
        action_names = [a.section_name for a in actions]
        # Should detect at least some bloat (diffstats, release_history, etc.)
        self.assertTrue(
            len(action_names) >= 1,
            f"Expected bloat actions, got: {action_names}"
        )

    def test_optimizer_budget_default(self):
        """Default budget is 150 lines."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md)
        self.assertEqual(optimizer.budget, DEFAULT_BUDGET)
        self.assertEqual(optimizer.budget, 150)

    def test_optimizer_budget_custom(self):
        """Custom budget overrides default."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md, budget=75)
        self.assertEqual(optimizer.budget, 75)

    def test_optimizer_budget_from_plugin_json(self):
        """Budget is read from plugin.json when present."""
        plugin_json_path = self.path / ".claude-plugin" / "plugin.json"
        plugin_json_path.write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0",
            "claude_md_budget": 200
        }))
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md)
        self.assertEqual(optimizer.budget, 200)

    def test_optimizer_anti_pattern_blocking(self):
        """Anti-patterns are detected within section content."""
        content = CLEAN_CLAUDE_MD + "\n## Release Notes\n\n### v2.11.0 - Cleanup\n\nReleased 2026-02-03\n\n**Files Changed:** 28 (+1,711/-801)\n"
        claude_md = self._write_claude_md(content)
        optimizer = CLAUDEMDOptimizer(claude_md)
        sections = optimizer.analyze()

        # The "Release Notes" section should be classified as P2
        release_sections = [s for s in sections if "release" in s.name.lower()]
        self.assertTrue(len(release_sections) >= 1)
        self.assertEqual(release_sections[0].priority, "P2")

    def test_optimizer_pointer_generation(self):
        """Pointer format matches: -> Description: [FILE.md](path/FILE.md)."""
        claude_md = self._write_claude_md(CLEAN_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md)

        pointer = optimizer.generate_pointer(
            "docs/VERSION-HISTORY.md", "Release History"
        )

        self.assertTrue(pointer.startswith(POINTER_PREFIX))
        self.assertIn("Release History", pointer)
        self.assertIn("[VERSION-HISTORY.md]", pointer)
        self.assertIn("(docs/VERSION-HISTORY.md)", pointer)

    def test_optimizer_optimize_dry_run(self):
        """Dry-run optimization does not modify files."""
        claude_md = self._write_claude_md(BLOATED_CLAUDE_MD)
        original_content = claude_md.read_text()

        optimizer = CLAUDEMDOptimizer(claude_md, budget=50)
        result = optimizer.optimize(dry_run=True)

        # File should remain unchanged
        self.assertEqual(claude_md.read_text(), original_content)

        # Result should still report metrics
        self.assertIsInstance(result, OptimizeResult)
        self.assertGreater(result.before_lines, 0)

    def test_optimizer_section_info(self):
        """SectionInfo dataclass properties work correctly."""
        section = SectionInfo(
            name="Test Section",
            start_line=10,
            end_line=30,
            line_count=20,
            priority="P0",
            max_lines=15,
            content="test content",
        )
        self.assertTrue(section.over_budget)
        self.assertEqual(section.overage, 5)

        section_ok = SectionInfo(
            name="OK Section",
            start_line=1,
            end_line=6,
            line_count=5,
            priority="P1",
            max_lines=10,
            content="small",
        )
        self.assertFalse(section_ok.over_budget)
        self.assertEqual(section_ok.overage, 0)

    def test_optimizer_optimize_result_properties(self):
        """OptimizeResult properties compute correctly."""
        result = OptimizeResult(
            before_lines=300,
            after_lines=120,
            budget=150,
        )
        self.assertTrue(result.within_budget)
        self.assertEqual(result.lines_saved, 180)
        self.assertEqual(result.reduction_percent, 60.0)

        result_over = OptimizeResult(
            before_lines=300,
            after_lines=200,
            budget=150,
        )
        self.assertFalse(result_over.within_budget)

    def test_optimizer_optimization_action_description(self):
        """OptimizationAction.description formats correctly."""
        move_action = OptimizationAction(
            action="move",
            section_name="Release History",
            line_count=50,
            target_file="docs/VERSION-HISTORY.md",
            pointer_text="-> Release History: [VERSION-HISTORY.md](docs/VERSION-HISTORY.md)",
            content="content",
        )
        self.assertIn("Move", move_action.description)
        self.assertIn("50 lines", move_action.description)

        delete_action = OptimizationAction(
            action="delete",
            section_name="Phase Details",
            line_count=20,
            target_file=None,
            pointer_text=None,
            content="content",
        )
        self.assertIn("Delete", delete_action.description)

        collapse_action = OptimizationAction(
            action="collapse",
            section_name="Agents",
            line_count=15,
            target_file="docs/COMMANDS.md",
            pointer_text=None,
            content="content",
        )
        self.assertIn("Collapse", collapse_action.description)

    def test_optimizer_generate_report(self):
        """Optimizer generates a readable report."""
        claude_md = self._write_claude_md(BLOATED_CLAUDE_MD)
        optimizer = CLAUDEMDOptimizer(claude_md, budget=50)
        result = optimizer.optimize(dry_run=True)
        report = optimizer.generate_report(result)

        self.assertIn("Optimization Report", report)
        self.assertIn("Budget:", report)
        self.assertIn("Before:", report)
        self.assertIn("After:", report)


# ---------------------------------------------------------------------------
# TestAntiPatterns
# ---------------------------------------------------------------------------

class TestAntiPatterns(unittest.TestCase):
    """Focused anti-pattern detection tests using CLAUDEMDSync."""

    def setUp(self):
        """Create temporary project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        # Minimal plugin fixture for detection
        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(PLUGIN_JSON)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _detect_patterns(self, content):
        """Helper: run anti-pattern detection on content."""
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)
        syncer = CLAUDEMDSync(claude_md)
        return syncer.detect_anti_patterns()

    def test_release_notes_pattern(self):
        """Detects versioned release headings like '## v2.11.0 - Test Suite Cleanup'."""
        content = "# Test\n\n## v2.11.0 - Test Suite Cleanup\n\nSome content\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("release_notes", ap_names)

    def test_release_notes_h3(self):
        """Detects H3-level versioned headings like '### v2.10.0 - Suite'."""
        content = "# Test\n\n### v2.10.0 - Command Suite\n\nSome content\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("release_notes", ap_names)

    def test_release_date_pattern(self):
        """Detects release dates like 'Released 2026-02-03'."""
        content = "# Test\n\nReleased 2026-02-03\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("release_date", ap_names)

    def test_diffstats_pattern(self):
        """Detects diffstats like 'Files Changed: 28 (+1,711/-801)'."""
        content = "# Test\n\n**Files Changed:** 28 (+1,711/-801)\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("diffstats", ap_names)

    def test_what_shipped_pattern(self):
        """Detects 'What Shipped:' blocks."""
        content = "# Test\n\n**What Shipped:**\n- Feature A\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("what_shipped", ap_names)

    def test_merged_pr_pattern(self):
        """Detects 'Merged PR:' references."""
        content = "# Test\n\nMerged PR: #42\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("what_shipped", ap_names)

    def test_completed_features_pattern(self):
        """Detects 'Status.*Complete' rows."""
        content = "# Test\n\n| Feature | Status Complete |\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("completed_features", ap_names)

    def test_released_checkmark_pattern(self):
        """Detects 'Released' with checkmark emoji."""
        content = "# Test\n\nSomething Released \u2705\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("completed_features", ap_names)

    def test_phase_details_pattern(self):
        """Detects phase implementation headings like '### Phase 1'."""
        content = "# Test\n\n### Phase 1 Implementation\n\nDetails here\n"
        found = self._detect_patterns(content)

        ap_names = [ap["name"] for ap in found]
        self.assertIn("phase_details", ap_names)

    def test_no_false_positives(self):
        """Normal content does not trigger anti-patterns."""
        content = "# Test Plugin\n\n## Git Workflow\n\nmain <- dev <- feature/*\n\n## Quick Commands\n\n| Task | Command |\n|------|--------|\n| Test | `pytest` |\n"
        found = self._detect_patterns(content)

        self.assertEqual(len(found), 0, f"False positives: {found}")

    def test_code_block_exclusion(self):
        """Anti-patterns inside fenced code blocks are ignored."""
        content = "# Test\n\n```\n## v2.11.0 - In Code Block\nReleased 2026-02-03\n```\n"
        found = self._detect_patterns(content)

        self.assertEqual(
            len(found), 0,
            f"Code block content should not trigger anti-patterns: {found}"
        )

    def test_anti_pattern_line_numbers(self):
        """Anti-pattern results include correct line numbers."""
        content = "# Test\nLine 2\nLine 3\n## v2.11.0 - Release\nLine 5\n"
        found = self._detect_patterns(content)

        release_aps = [ap for ap in found if ap["name"] == "release_notes"]
        self.assertEqual(len(release_aps), 1)
        self.assertEqual(release_aps[0]["line_number"], 4)

    def test_anti_pattern_redirect_field(self):
        """Anti-patterns with redirect targets include the redirect field."""
        content = "# Test\n\n## v2.11.0 - Release\n"
        found = self._detect_patterns(content)

        release_aps = [ap for ap in found if ap["name"] == "release_notes"]
        self.assertTrue(len(release_aps) >= 1)
        self.assertIn("redirect", release_aps[0])
        self.assertEqual(release_aps[0]["redirect"], "VERSION-HISTORY.md")


# ---------------------------------------------------------------------------
# TestMetricChange
# ---------------------------------------------------------------------------

class TestMetricChange(unittest.TestCase):
    """Test MetricChange dataclass."""

    def test_metric_change_description(self):
        """MetricChange.description formats name: before -> after."""
        mc = MetricChange(
            name="Version",
            before="v1.0.0",
            after="v2.0.0",
            pattern=r"test",
        )
        self.assertEqual(mc.description, "Version: v1.0.0 -> v2.0.0")

    def test_issue_str_formatting(self):
        """Issue.__str__ includes severity icon and message."""
        issue = Issue(
            severity=Severity.ERROR,
            category="test",
            message="Something broke",
            line_number=42,
        )
        result = str(issue)
        self.assertIn("[E]", result)
        self.assertIn("L42", result)
        self.assertIn("Something broke", result)

    def test_issue_str_no_line_number(self):
        """Issue.__str__ without line number omits line prefix."""
        issue = Issue(
            severity=Severity.WARNING,
            category="test",
            message="A warning",
        )
        result = str(issue)
        self.assertIn("[W]", result)
        self.assertNotIn("L", result)
        self.assertIn("A warning", result)


# ---------------------------------------------------------------------------
# TestSyncReport
# ---------------------------------------------------------------------------

class TestSyncReport(unittest.TestCase):
    """Test report generation."""

    def setUp(self):
        """Create temporary project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

        plugin_dir = self.path / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(PLUGIN_JSON)

    def tearDown(self):
        """Clean up temporary directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_clean_report(self):
        """Report for a clean file shows CLEAN status."""
        result = SyncResult(project_info=None)
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(CLEAN_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md, budget=500)
        report = syncer.generate_report(result)

        self.assertIn("CLEAN", report)

    def test_report_with_issues(self):
        """Report includes issue counts by severity."""
        result = SyncResult(
            project_info=None,
            issues=[
                Issue(severity=Severity.ERROR, category="test", message="error1"),
                Issue(severity=Severity.WARNING, category="test", message="warn1"),
                Issue(severity=Severity.INFO, category="test", message="info1"),
            ],
        )
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(CLEAN_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md, budget=500)
        report = syncer.generate_report(result)

        self.assertIn("Errors (1)", report)
        self.assertIn("Warnings (1)", report)
        self.assertIn("Info (1)", report)

    def test_report_with_anti_patterns(self):
        """Report includes anti-pattern listing."""
        result = SyncResult(
            project_info=None,
            anti_patterns_found=[
                {"name": "release_notes", "line_number": 10, "redirect": "VERSION-HISTORY.md"},
            ],
        )
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(CLEAN_CLAUDE_MD)
        syncer = CLAUDEMDSync(claude_md, budget=500)
        report = syncer.generate_report(result)

        self.assertIn("Anti-Patterns (1)", report)
        self.assertIn("release_notes", report)


# ---------------------------------------------------------------------------
# TestGlobalFlagResolution
# ---------------------------------------------------------------------------

class TestGlobalFlagResolution(unittest.TestCase):
    """Test resolve_claude_md_path() from claude_md_common."""

    def setUp(self):
        """Create temporary directories simulating home and project."""
        self.temp_dir = tempfile.mkdtemp()
        self.global_dir = os.path.join(self.temp_dir, '.claude')
        os.makedirs(self.global_dir, exist_ok=True)

    def tearDown(self):
        """Clean up temporary directory."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_global_flag_returns_global_path(self):
        """--global resolves to ~/.claude/CLAUDE.md when it exists."""
        global_path = os.path.join(self.global_dir, 'CLAUDE.md')
        with open(global_path, 'w') as f:
            f.write('# Global CLAUDE.md\n')

        with patch('utils.claude_md_common.os.path.expanduser', return_value=global_path):
            result = resolve_claude_md_path(global_flag=True)
            self.assertEqual(result, global_path)

    def test_global_flag_missing_raises_error(self):
        """--global raises FileNotFoundError when ~/.claude/CLAUDE.md is absent."""
        missing_path = os.path.join(self.global_dir, 'CLAUDE.md')
        # Do NOT create the file

        with patch('utils.claude_md_common.os.path.expanduser', return_value=missing_path):
            with self.assertRaises(FileNotFoundError) as ctx:
                resolve_claude_md_path(global_flag=True)
            self.assertIn("Global CLAUDE.md not found", str(ctx.exception))

    def test_local_resolution_walks_up(self):
        """Without --global, walks up directory tree to find CLAUDE.md."""
        project_root = os.path.join(self.temp_dir, 'project')
        nested_dir = os.path.join(project_root, 'src', 'lib')
        os.makedirs(nested_dir, exist_ok=True)

        claude_md_path = os.path.join(project_root, 'CLAUDE.md')
        with open(claude_md_path, 'w') as f:
            f.write('# Project CLAUDE.md\n')

        result = resolve_claude_md_path(global_flag=False, start_dir=nested_dir)
        self.assertEqual(result, os.path.abspath(claude_md_path))

    def test_local_resolution_not_found_raises(self):
        """Raises FileNotFoundError when no CLAUDE.md in tree."""
        empty_dir = os.path.join(self.temp_dir, 'empty', 'nested')
        os.makedirs(empty_dir, exist_ok=True)

        with self.assertRaises(FileNotFoundError) as ctx:
            resolve_claude_md_path(global_flag=False, start_dir=empty_dir)
        self.assertIn("No CLAUDE.md found", str(ctx.exception))

    def test_reexport_from_sync(self):
        """Verify resolve_claude_md_path is re-exported from sync module."""
        from utils.claude_md_sync import resolve_claude_md_path as sync_resolve
        self.assertIs(sync_resolve, resolve_claude_md_path)

    def test_reexport_from_optimizer(self):
        """Verify resolve_claude_md_path is re-exported from optimizer module."""
        from utils.claude_md_optimizer import resolve_claude_md_path as opt_resolve
        self.assertIs(opt_resolve, resolve_claude_md_path)


if __name__ == '__main__':
    unittest.main()
