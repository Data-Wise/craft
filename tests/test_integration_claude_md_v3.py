#!/usr/bin/env python3
"""
Integration Tests: CLAUDE.md v3 Sync Pipeline & Optimizer
=========================================================
End-to-end tests that combine multiple v3 components (sync, optimizer,
budget enforcement, detail file management) to verify the full pipeline
works as a cohesive system.

Unit tests in test_claude_md_v3.py cover components in isolation.
These integration tests verify combined flows with realistic project fixtures.

Components tested:
- utils/claude_md_sync.py (CLAUDEMDSync, 4-phase pipeline)
- utils/claude_md_optimizer.py (CLAUDEMDOptimizer, budget enforcement)
- scripts/claude-md-budget-check.sh (pre-commit budget check)

Run with: python3 tests/test_integration_claude_md_v3.py
"""

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path

# Add parent to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.claude_md_sync import CLAUDEMDSync, SyncResult
from utils.claude_md_optimizer import (
    CLAUDEMDOptimizer,
    OptimizeResult,
    POINTER_PREFIX,
)


# ---------------------------------------------------------------------------
# Fixture helpers
# ---------------------------------------------------------------------------

def _make_plugin_json(path: Path, version: str = "2.0.0", budget: int = None):
    """Create .claude-plugin/plugin.json."""
    plugin_dir = path / ".claude-plugin"
    plugin_dir.mkdir(parents=True, exist_ok=True)
    data = {"name": "test-plugin", "version": version, "description": "Test"}
    if budget is not None:
        data["claude_md_budget"] = budget
    (plugin_dir / "plugin.json").write_text(json.dumps(data))


def _make_commands(path: Path, count: int = 1):
    """Create commands directory with dummy command files."""
    commands_dir = path / "commands"
    commands_dir.mkdir(parents=True, exist_ok=True)
    for i in range(count):
        (commands_dir / f"cmd{i}.md").write_text(f"# Command {i}")


def _minimal_claude_md(version: str = "1.0.0") -> str:
    """Return a clean, minimal CLAUDE.md under 30 lines."""
    return f"""\
# CLAUDE.md - Test Plugin

> **TL;DR**: Test plugin for integration tests.

**Current Version:** v{version} | **Tests:** 10 passing

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


def _bloated_claude_md() -> str:
    """Return a CLAUDE.md with P2 bloat (release notes, diffstats, phases)."""
    base = _minimal_claude_md(version="2.0.0")
    bloat = """
## v2.11.0 - Test Suite Cleanup (Released 2026-02-03)

**What Shipped:**
- Feature A shipped
- Feature B shipped

**Files Changed:** 28 (+1,711/-801)

## Recent Major Features

### v2.10.0 - Command Suite (Released 2026-01-30)

**Merged PR:** #39

- 5 new commands
- 81 tests
- 3 templates

### v2.9.0 - Command Enhancements (Released 2026-01-29)

- Show Steps First pattern
- Interactive orchestration

## Phase 3 Documentation Enhancements

**Status:** Completed (87% -> 95% target)

### Phase 1 Implementation

- Step A completed
- Step B completed

### Phase 2 Refinement

- Step C completed
- Step D completed
"""
    # Add filler to push well over budget
    filler = "\n".join([f"Filler line {i}" for i in range(60)])
    return base + bloat + filler


# ---------------------------------------------------------------------------
# TestSyncPipelineIntegration
# ---------------------------------------------------------------------------

class TestSyncPipelineIntegration(unittest.TestCase):
    """Tests the full 4-phase sync pipeline with realistic project fixtures."""

    def setUp(self):
        """Create temp project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_claude_md(self, content: str) -> Path:
        """Write CLAUDE.md to temp dir and return path."""
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)
        return claude_md

    def test_01_full_sync_detect_fix_verify(self):
        """Version mismatch detected -> fixed -> file verified on disk."""
        # Arrange: plugin.json says v2.0.0, CLAUDE.md says v1.0.0
        _make_plugin_json(self.path, version="2.0.0")
        _make_commands(self.path)
        claude_md = self._write_claude_md(_minimal_claude_md(version="1.0.0"))

        # Act: run full sync with fix=True
        syncer = CLAUDEMDSync(claude_md)
        result = syncer.sync(fix=True, scope="warnings")

        # Assert: version mismatch was detected
        version_changes = [mc for mc in result.metric_changes if mc.name == "Version"]
        self.assertEqual(len(version_changes), 1, "Should detect version drift")
        self.assertIn("1.0.0", version_changes[0].before)
        self.assertIn("2.0.0", version_changes[0].after)

        # Assert: fix was applied
        version_fixes = [
            fr for fr in result.fix_results
            if "version" in fr.description.lower()
        ]
        self.assertTrue(
            any(fr.success for fr in version_fixes),
            "At least one version fix should succeed"
        )

        # Assert: file on disk is updated
        updated_content = claude_md.read_text()
        self.assertIn("v2.0.0", updated_content)
        self.assertNotIn("v1.0.0", updated_content)

        # Assert: backup was created
        backup = self.path / ".CLAUDE.md.backup"
        self.assertTrue(backup.exists(), "Backup file should be created")

    def test_02_sync_plus_optimize_combined(self):
        """Sync detects bloat -> optimizer moves P2 content to detail files."""
        # Arrange: bloated project
        _make_plugin_json(self.path, version="2.0.0")
        _make_commands(self.path)
        claude_md = self._write_claude_md(_bloated_claude_md())
        original_lines = len(claude_md.read_text().split("\n"))

        # Act phase 1: sync detects anti-patterns
        syncer = CLAUDEMDSync(claude_md, budget=50)
        sync_result = syncer.sync(dry_run=True)

        self.assertTrue(
            len(sync_result.anti_patterns_found) > 0,
            "Should detect anti-patterns in bloated content"
        )

        # Act phase 2: optimize to fit budget
        optimizer = CLAUDEMDOptimizer(claude_md, budget=50)
        opt_result = optimizer.optimize()

        # Assert: detail files created
        self.assertTrue(
            len(opt_result.detail_files_created) > 0,
            "Optimizer should create detail files"
        )

        # Assert: pointers inserted
        self.assertTrue(
            len(opt_result.pointers_added) > 0,
            "Optimizer should add pointer lines"
        )

        # Assert: CLAUDE.md reduced
        after_content = claude_md.read_text()
        after_lines = len(after_content.split("\n"))
        self.assertLess(
            after_lines, original_lines,
            f"Line count should decrease: {after_lines} < {original_lines}"
        )

    def test_03_anti_pattern_to_detail_file_flow(self):
        """Anti-pattern content moves to correct detail files."""
        # Arrange: CLAUDE.md with identifiable anti-pattern content
        _make_plugin_json(self.path, version="2.0.0")
        _make_commands(self.path)
        claude_md = self._write_claude_md(_bloated_claude_md())

        # Act: run optimizer
        optimizer = CLAUDEMDOptimizer(claude_md, budget=50)
        opt_result = optimizer.optimize()

        # Assert: VERSION-HISTORY.md created with moved content
        vh_path = self.path / "docs" / "VERSION-HISTORY.md"
        self.assertTrue(vh_path.exists(), "docs/VERSION-HISTORY.md should be created")

        vh_content = vh_path.read_text()
        # The release notes, what-shipped, etc. should be in the detail file
        self.assertTrue(
            len(vh_content) > 50,
            "Detail file should contain substantial moved content"
        )

        # Assert: pointers present in CLAUDE.md
        optimized = claude_md.read_text()
        pointer_lines = [ln for ln in optimized.split("\n") if ln.startswith(POINTER_PREFIX)]
        self.assertTrue(
            len(pointer_lines) > 0,
            "CLAUDE.md should contain pointer lines after optimization"
        )

        # Assert: original bloat sections removed
        self.assertNotIn("**Files Changed:**", optimized)
        self.assertNotIn("**What Shipped:**", optimized)


# ---------------------------------------------------------------------------
# TestBudgetEnforcementIntegration
# ---------------------------------------------------------------------------

class TestBudgetEnforcementIntegration(unittest.TestCase):
    """Tests budget enforcement across sync and optimizer."""

    def setUp(self):
        """Create temp project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_claude_md(self, content: str) -> Path:
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)
        return claude_md

    def test_04_budget_from_plugin_json_flows_through(self):
        """Budget in plugin.json respected by both sync and optimizer."""
        # Arrange: plugin.json with budget=75, CLAUDE.md at 100 lines
        _make_plugin_json(self.path, version="1.0.0", budget=75)
        _make_commands(self.path)

        content = _minimal_claude_md()
        # Pad to ~100 lines
        content += "\n".join([f"Extra line {i}" for i in range(70)])
        claude_md = self._write_claude_md(content)

        # Assert: CLAUDEMDSync reads budget=75 and reports over_budget
        syncer = CLAUDEMDSync(claude_md)
        self.assertEqual(syncer.budget, 75, "Sync should read budget from plugin.json")
        sync_result = syncer.sync(dry_run=True)
        self.assertTrue(sync_result.over_budget, "Should be over budget=75")

        # Assert: CLAUDEMDOptimizer also reads budget=75
        optimizer = CLAUDEMDOptimizer(claude_md)
        self.assertEqual(optimizer.budget, 75, "Optimizer should read budget from plugin.json")

    def test_05_budget_script_integration(self):
        """Budget check script works with custom budget."""
        plugin_dir = Path(__file__).parent.parent
        budget_script = plugin_dir / "scripts" / "claude-md-budget-check.sh"
        if not budget_script.exists():
            self.skipTest("claude-md-budget-check.sh not found")

        # The script derives PROJECT_ROOT from BASH_SOURCE, so we copy it
        # into the temp project and run from there.
        scripts_dir = self.path / "scripts"
        scripts_dir.mkdir()
        shutil.copy2(budget_script, scripts_dir / "claude-md-budget-check.sh")
        local_script = scripts_dir / "claude-md-budget-check.sh"

        # Arrange: project with budget=50 and CLAUDE.md at 80 lines
        _make_plugin_json(self.path, version="1.0.0", budget=50)

        content = _minimal_claude_md()
        content += "\n".join([f"Padding line {i}" for i in range(55)])
        self._write_claude_md(content)

        # Act: run budget check (--all mode since no git staged files)
        result = subprocess.run(
            ["bash", str(local_script), "--all"],
            capture_output=True,
            text=True,
            cwd=self.path,
        )

        # Assert: exit code 1 (over budget)
        self.assertEqual(result.returncode, 1, "Should fail when over budget")
        self.assertIn("budget", result.stderr.lower(), "Should mention budget in error")

        # Arrange: replace with small CLAUDE.md under budget
        self._write_claude_md(_minimal_claude_md())

        # Act: re-run
        result2 = subprocess.run(
            ["bash", str(local_script), "--all"],
            capture_output=True,
            text=True,
            cwd=self.path,
        )

        # Assert: exit code 0 (under budget)
        self.assertEqual(result2.returncode, 0, "Should pass when under budget")


# ---------------------------------------------------------------------------
# TestDetailFileManagement
# ---------------------------------------------------------------------------

class TestDetailFileManagement(unittest.TestCase):
    """Tests the optimizer's file creation and content movement."""

    def setUp(self):
        """Create temp project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)
        _make_plugin_json(self.path, version="1.0.0")

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_claude_md(self, content: str) -> Path:
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)
        return claude_md

    def test_06_detail_file_creation_and_append(self):
        """New detail file created, then content appended on second call."""
        claude_md = self._write_claude_md(_minimal_claude_md())
        optimizer = CLAUDEMDOptimizer(claude_md)

        target = "docs/VERSION-HISTORY.md"
        target_path = self.path / target

        # Act 1: first move creates the file
        created = optimizer.move_to_detail_file(
            "## v2.11.0 - Cleanup\n\n- Feature A\n- Feature B\n",
            target,
            "Release Notes",
        )

        # Assert: file created
        self.assertTrue(created, "First call should create the file")
        self.assertTrue(target_path.exists(), "Detail file should exist on disk")
        content1 = target_path.read_text()
        self.assertIn("Feature A", content1)

        # Act 2: second move appends
        created2 = optimizer.move_to_detail_file(
            "## v2.10.0 - Suite\n\n- 5 new commands\n",
            target,
            "More Notes",
        )

        # Assert: appended (not created fresh)
        self.assertFalse(created2, "Second call should append, not create")
        content2 = target_path.read_text()
        self.assertIn("Feature A", content2, "Original content preserved")
        self.assertIn("5 new commands", content2, "New content appended")
        self.assertIn("---", content2, "Sections separated by ---")

    def test_07_pointer_format_in_optimized_output(self):
        """Pointer lines match spec format after optimization."""
        # Arrange: bloated CLAUDE.md
        _make_commands(self.path)
        claude_md = self._write_claude_md(_bloated_claude_md())

        # Act: optimize
        optimizer = CLAUDEMDOptimizer(claude_md, budget=50)
        result = optimizer.optimize()

        # Assert: pointers in the result match the spec format
        for pointer in result.pointers_added:
            self.assertTrue(
                pointer.startswith(POINTER_PREFIX),
                f"Pointer should start with '{POINTER_PREFIX}': {pointer}"
            )
            # Should contain a markdown link [FILENAME](path/FILENAME)
            self.assertRegex(
                pointer,
                r"\[[\w.-]+\]\([\w/.:-]+\)",
                f"Pointer should contain markdown link: {pointer}"
            )

        # Assert: pointers also present in the file on disk
        optimized = claude_md.read_text()
        pointer_lines = [
            ln for ln in optimized.split("\n")
            if ln.startswith(POINTER_PREFIX)
        ]
        self.assertTrue(
            len(pointer_lines) > 0,
            "Optimized file should have pointer lines on disk"
        )
        for pl in pointer_lines:
            self.assertRegex(
                pl,
                r"\[[\w.-]+\]\([\w/.:-]+\)",
                f"On-disk pointer should contain markdown link: {pl}"
            )


# ---------------------------------------------------------------------------
# TestEdgeCases
# ---------------------------------------------------------------------------

class TestEdgeCases(unittest.TestCase):
    """Edge cases for the combined pipeline."""

    def setUp(self):
        """Create temp project directory."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)
        _make_plugin_json(self.path, version="1.0.0")
        _make_commands(self.path)

    def tearDown(self):
        """Clean up."""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def _write_claude_md(self, content: str) -> Path:
        claude_md = self.path / "CLAUDE.md"
        claude_md.write_text(content)
        return claude_md

    def test_08_clean_file_no_modifications(self):
        """Clean CLAUDE.md under budget produces no changes."""
        # Arrange: clean, minimal file well under budget
        content = _minimal_claude_md(version="1.0.0")
        claude_md = self._write_claude_md(content)
        original = claude_md.read_text()

        # Act: sync pipeline (dry_run to check detection only — no fixes applied)
        syncer = CLAUDEMDSync(claude_md, budget=500)
        sync_result = syncer.sync(dry_run=True)

        # Assert: no anti-patterns, no errors
        self.assertEqual(len(sync_result.anti_patterns_found), 0, "No anti-patterns expected")
        self.assertFalse(sync_result.has_errors, "No errors expected")

        # Act: optimizer (budget is generous, should find nothing to move)
        optimizer = CLAUDEMDOptimizer(claude_md, budget=500)
        opt_result = optimizer.optimize()

        # Assert: no actions, no detail files, no pointers
        self.assertEqual(len(opt_result.detail_files_created), 0, "No detail files should be created")
        self.assertEqual(len(opt_result.pointers_added), 0, "No pointers should be added")

        # Assert: file unchanged (content may have minor whitespace normalization)
        final = claude_md.read_text()
        self.assertEqual(
            original.strip(),
            final.strip(),
            "Clean file should not be modified"
        )

    def test_09_p1_collapse_when_p2_removal_insufficient(self):
        """P1 sections collapsed when still over budget after P2 removal."""
        # Arrange: CLAUDE.md with P0 (core) + P1 (Agents) + P2 (Release), budget=70
        content = """\
# CLAUDE.md - Test Plugin

> **TL;DR**: Test plugin.

**Current Version:** v1.0.0

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

## Agents

| Agent | Model | Use For |
|-------|-------|---------|
| orchestrator | sonnet | Complex tasks |
| docs-arch | sonnet | System docs |
| api-doc | sonnet | API specs |
| tutorial | sonnet | Tutorials |
| ref-builder | haiku | References |
| mermaid | haiku | Diagrams |
| demo | haiku | Demos |
| reviewer | sonnet | Code review |

## Execution Modes

| Mode | Budget | Use Case |
|------|--------|----------|
| default | <10s | Quick tasks |
| debug | <120s | Verbose traces |
| optimize | <180s | Performance |
| release | <300s | Validation |

## Recent Major Features

### v2.10.0 - Command Suite (Released 2026-01-30)

- 5 new commands
- 81 tests

### v2.9.0 - Enhancements (Released 2026-01-29)

- Show Steps First
- Interactive orchestration
- Worktree auto-setup

## Troubleshooting

| Issue | Fix |
|-------|-----|
| Tests fail | Run pytest |
"""
        claude_md = self._write_claude_md(content)
        original_lines = len(content.split("\n"))

        # Act: optimize with tight budget
        optimizer = CLAUDEMDOptimizer(claude_md, budget=70)
        opt_result = optimizer.optimize()

        # Assert: P2 moved to detail file
        p2_actions = [a for a in opt_result.actions if a.action == "move"]
        self.assertTrue(len(p2_actions) > 0, "P2 sections should be moved")

        # Assert: if still over budget, P1 should be collapsed
        if opt_result.after_lines > 70:
            p1_collapses = [a for a in opt_result.actions if a.action == "collapse"]
            self.assertTrue(
                len(p1_collapses) > 0,
                "P1 sections should be collapsed when still over budget after P2 removal"
            )

        # Assert: final count reduced significantly from original
        self.assertLess(
            opt_result.after_lines, original_lines,
            f"Should reduce from {original_lines} to ≤70, got {opt_result.after_lines}"
        )


if __name__ == "__main__":
    unittest.main(verbosity=2)
