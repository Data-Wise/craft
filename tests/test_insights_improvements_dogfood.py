#!/usr/bin/env python3
"""
Dogfooding Tests: Insights-Driven Improvements
================================================
Tests the 10 changes from the insights-driven improvements spec
against the REAL craft repo. Validates skill registration, command
enhancements, hook installation, and cross-file consistency.

Run with: python3 tests/test_insights_improvements_dogfood.py
"""

import json
import os
import re
import unittest
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.structure]


# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
CRAFT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PLUGIN_JSON = os.path.join(CRAFT_ROOT, ".claude-plugin", "plugin.json")
CLAUDE_MD = os.path.join(CRAFT_ROOT, "CLAUDE.md")
SETTINGS_PATH = os.path.expanduser("~/.claude/settings.json")

# New skills
GUARD_AUDIT_SKILL = os.path.join(CRAFT_ROOT, "skills", "guard-audit", "SKILL.md")
INSIGHTS_APPLY_SKILL = os.path.join(CRAFT_ROOT, "skills", "insights-apply", "SKILL.md")
RELEASE_SKILL = os.path.join(CRAFT_ROOT, "skills", "release", "SKILL.md")

# Enhanced commands
CHECK_CMD = os.path.join(CRAFT_ROOT, "commands", "check.md")
WORKTREE_CMD = os.path.join(CRAFT_ROOT, "commands", "git", "worktree.md")
DO_CMD = os.path.join(CRAFT_ROOT, "commands", "do.md")
SMART_HELP_CMD = os.path.join(CRAFT_ROOT, "commands", "smart-help.md")
HUB_CMD = os.path.join(CRAFT_ROOT, "commands", "hub.md")
ORCHESTRATE_CMD = os.path.join(CRAFT_ROOT, "commands", "orchestrate.md")

# New hook
PRETOOLUSE_HOOK = os.path.join(CRAFT_ROOT, ".claude-plugin", "hooks", "pretooluse.py")


def _read_frontmatter(filepath: str) -> dict:
    """Parse YAML frontmatter from a markdown file (simple parser, no deps)."""
    if not os.path.isfile(filepath):
        return {}
    with open(filepath) as f:
        lines = f.readlines()
    if not lines or lines[0].strip() != "---":
        return {}
    fm = {}
    for line in lines[1:]:
        if line.strip() == "---":
            break
        if ":" in line:
            key, _, val = line.partition(":")
            fm[key.strip()] = val.strip()
    return fm


def _read_frontmatter_raw(filepath: str) -> str:
    """Read the raw frontmatter text from a markdown file."""
    if not os.path.isfile(filepath):
        return ""
    with open(filepath) as f:
        lines = f.readlines()
    if not lines or lines[0].strip() != "---":
        return ""
    parts = []
    for line in lines[1:]:
        if line.strip() == "---":
            break
        parts.append(line)
    return "".join(parts)


def _read_file(filepath: str) -> str:
    """Read entire file content."""
    with open(filepath) as f:
        return f.read()


# ============================================================================
# Group 1: New Skills — Guard Audit
# ============================================================================
class TestGuardAuditSkill(unittest.TestCase):
    """Verify guard-audit skill is properly structured."""

    def test_skill_file_exists(self):
        """skills/guard-audit/SKILL.md exists."""
        self.assertTrue(os.path.isfile(GUARD_AUDIT_SKILL))

    def test_frontmatter_has_name(self):
        """Frontmatter name is 'guard-audit'."""
        fm = _read_frontmatter(GUARD_AUDIT_SKILL)
        self.assertEqual(fm.get("name"), "guard-audit")

    def test_frontmatter_has_description(self):
        """Description is substantial (>20 chars)."""
        fm = _read_frontmatter(GUARD_AUDIT_SKILL)
        desc = fm.get("description", "")
        self.assertGreater(len(desc), 20)

    def test_trigger_phrases_in_description(self):
        """Description contains key trigger phrases."""
        fm = _read_frontmatter(GUARD_AUDIT_SKILL)
        desc = fm.get("description", "").lower()
        for phrase in ["audit guard", "guard friction", "false positive"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, desc)

    def test_has_pipeline_steps(self):
        """Skill has the 5-step pipeline (Discovery through Apply)."""
        content = _read_file(GUARD_AUDIT_SKILL)
        for step in ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]:
            with self.subTest(step=step):
                self.assertIn(step, content)

    def test_never_modifies_guard_script(self):
        """Skill explicitly states it never modifies branch-guard.sh."""
        content = _read_file(GUARD_AUDIT_SKILL).lower()
        self.assertTrue(
            "never modify" in content or "never modifies" in content,
            "Should document that it never modifies the guard script"
        )

    def test_targets_json_config(self):
        """Skill targets .claude/branch-guard.json."""
        content = _read_file(GUARD_AUDIT_SKILL)
        self.assertIn("branch-guard.json", content)

    def test_has_error_recovery(self):
        """Skill has error recovery section."""
        content = _read_file(GUARD_AUDIT_SKILL)
        self.assertIn("Error Recovery", content)


# ============================================================================
# Group 2: New Skills — Insights Apply
# ============================================================================
class TestInsightsApplySkill(unittest.TestCase):
    """Verify insights-apply skill is properly structured."""

    def test_skill_file_exists(self):
        """skills/insights-apply/SKILL.md exists."""
        self.assertTrue(os.path.isfile(INSIGHTS_APPLY_SKILL))

    def test_frontmatter_has_name(self):
        """Frontmatter name is 'insights-apply'."""
        fm = _read_frontmatter(INSIGHTS_APPLY_SKILL)
        self.assertEqual(fm.get("name"), "insights-apply")

    def test_frontmatter_has_description(self):
        """Description is substantial (>20 chars)."""
        fm = _read_frontmatter(INSIGHTS_APPLY_SKILL)
        desc = fm.get("description", "")
        self.assertGreater(len(desc), 20)

    def test_trigger_phrases_in_description(self):
        """Description contains key trigger phrases."""
        fm = _read_frontmatter(INSIGHTS_APPLY_SKILL)
        desc = fm.get("description", "").lower()
        for phrase in ["apply insights", "insights", "claude.md"]:
            with self.subTest(phrase=phrase):
                self.assertIn(phrase, desc)

    def test_has_pipeline_steps(self):
        """Skill has the 5-step pipeline."""
        content = _read_file(INSIGHTS_APPLY_SKILL)
        for step in ["Step 1", "Step 2", "Step 3", "Step 4", "Step 5"]:
            with self.subTest(step=step):
                self.assertIn(step, content)

    def test_targets_global_claude_md(self):
        """Skill targets global ~/.claude/CLAUDE.md (cross-project)."""
        content = _read_file(INSIGHTS_APPLY_SKILL)
        self.assertIn("~/.claude/CLAUDE.md", content)

    def test_references_sync_pipeline(self):
        """Skill references the sync pipeline utility."""
        content = _read_file(INSIGHTS_APPLY_SKILL)
        self.assertIn("claude_md_sync", content)

    def test_has_budget_check(self):
        """Skill includes budget check step."""
        content = _read_file(INSIGHTS_APPLY_SKILL).lower()
        self.assertIn("budget", content)

    def test_has_error_recovery(self):
        """Skill has error recovery section."""
        content = _read_file(INSIGHTS_APPLY_SKILL)
        self.assertIn("Error Recovery", content)


# ============================================================================
# Group 3: Release Skill — Autonomous Mode
# ============================================================================
class TestReleaseAutonomousMode(unittest.TestCase):
    """Verify --autonomous flag was added to release skill."""

    def test_autonomous_section_exists(self):
        """SKILL.md has an Autonomous Mode section."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("Autonomous Mode", content)

    def test_autonomous_argument_documented(self):
        """--autonomous argument is in the arguments table."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("--autonomous", content)

    def test_auto_alias_documented(self):
        """--auto alias is documented."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("--auto", content)

    def test_autonomous_safety_checks(self):
        """Autonomous mode has safety checks section."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("Autonomous Safety Checks", content)

    def test_autonomous_version_detection(self):
        """Autonomous mode documents version auto-detection."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("Autonomous Version Detection", content)

    def test_autonomous_error_recovery(self):
        """Autonomous mode has error recovery section."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("Autonomous Error Recovery", content)

    def test_autonomous_admin_override(self):
        """Autonomous mode documents --admin override for branch protection."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("Admin Override", content)

    def test_dry_run_still_works(self):
        """Dry-run section still exists (not clobbered by autonomous)."""
        content = _read_file(RELEASE_SKILL)
        self.assertIn("## Dry-Run Mode", content)


# ============================================================================
# Group 4: Check Command — --context Flag
# ============================================================================
class TestCheckContextFlag(unittest.TestCase):
    """Verify --context flag was added to check command."""

    def test_context_in_frontmatter(self):
        """--context argument appears in frontmatter arguments."""
        fm_text = _read_frontmatter_raw(CHECK_CMD)
        self.assertIn("context", fm_text)

    def test_context_mode_section_exists(self):
        """Context-Only Mode section exists."""
        content = _read_file(CHECK_CMD)
        self.assertIn("Context-Only Mode", content)

    def test_phase_detection_documented(self):
        """Phase detection logic is documented."""
        content = _read_file(CHECK_CMD)
        for phase in ["implementation", "testing", "pr-prep", "release"]:
            with self.subTest(phase=phase):
                self.assertIn(phase, content)

    def test_session_context_box(self):
        """Session context box template is present."""
        content = _read_file(CHECK_CMD)
        self.assertIn("SESSION CONTEXT", content)


# ============================================================================
# Group 5: Worktree Command — validate Action
# ============================================================================
class TestWorktreeValidateAction(unittest.TestCase):
    """Verify validate action was added to worktree command."""

    def test_validate_in_frontmatter(self):
        """validate appears in action enum in frontmatter."""
        # Check first 30 lines for frontmatter
        with open(WORKTREE_CMD) as f:
            header = "".join(f.readlines()[:30])
        self.assertIn("validate", header)

    def test_validate_section_exists(self):
        """Validate section exists in the command body."""
        content = _read_file(WORKTREE_CMD)
        self.assertIn("validate", content.lower())

    def test_validate_checks_documented(self):
        """Validate checks are documented (branch, config, path)."""
        content = _read_file(WORKTREE_CMD)
        # Should mention checking branch alignment, guard config, path structure
        self.assertIn("Verify Worktree", content)


# ============================================================================
# Group 6: PreToolUse Hook
# ============================================================================
class TestPreToolUseHook(unittest.TestCase):
    """Verify pretooluse.py hook is properly structured."""

    def test_hook_file_exists(self):
        """.claude-plugin/hooks/pretooluse.py exists."""
        self.assertTrue(os.path.isfile(PRETOOLUSE_HOOK))

    def test_hook_has_python_shebang(self):
        """Hook has python3 shebang."""
        with open(PRETOOLUSE_HOOK) as f:
            first_line = f.readline().strip()
        self.assertIn("python3", first_line)

    def test_hook_syntax_valid(self):
        """Hook passes python3 -m py_compile syntax check."""
        import subprocess
        result = subprocess.run(
            ["python3", "-m", "py_compile", PRETOOLUSE_HOOK],
            capture_output=True, text=True,
        )
        self.assertEqual(result.returncode, 0, f"Syntax error: {result.stderr}")

    def test_hook_checks_tool_name(self):
        """Hook checks CLAUDE_TOOL_NAME environment variable."""
        content = _read_file(PRETOOLUSE_HOOK)
        self.assertIn("CLAUDE_TOOL_NAME", content)

    def test_hook_checks_write_and_edit(self):
        """Hook filters for Write and Edit tool operations."""
        content = _read_file(PRETOOLUSE_HOOK)
        self.assertIn('"Write"', content)
        self.assertIn('"Edit"', content)

    def test_hook_checks_worktree_path(self):
        """Hook checks for .git-worktrees in path."""
        content = _read_file(PRETOOLUSE_HOOK)
        self.assertIn(".git-worktrees", content)

    def test_hook_is_non_blocking(self):
        """Hook never exits with non-zero code (warnings only)."""
        content = _read_file(PRETOOLUSE_HOOK)
        # Should not have sys.exit(1) or sys.exit(2)
        self.assertNotIn("sys.exit(1)", content)
        self.assertNotIn("sys.exit(2)", content)
        self.assertNotIn("exit(1)", content)

    def test_hook_uses_stderr_for_warnings(self):
        """Hook outputs warnings to stderr, not stdout."""
        content = _read_file(PRETOOLUSE_HOOK)
        self.assertIn("file=sys.stderr", content)


# ============================================================================
# Group 7: Orchestrate Command — --swarm Flag
# ============================================================================
class TestOrchestrateSwarmFlag(unittest.TestCase):
    """Verify --swarm flag was added to orchestrate command."""

    def test_swarm_in_frontmatter(self):
        """swarm appears in command arguments."""
        fm_text = _read_frontmatter_raw(ORCHESTRATE_CMD)
        self.assertIn("swarm", fm_text)

    def test_swarm_mode_section_exists(self):
        """Swarm Mode section exists."""
        content = _read_file(ORCHESTRATE_CMD)
        self.assertIn("Swarm Mode", content)

    def test_swarm_uses_worktrees(self):
        """Swarm mode documents worktree isolation."""
        content = _read_file(ORCHESTRATE_CMD)
        self.assertIn("worktree", content.lower())

    def test_swarm_convergence_documented(self):
        """Swarm mode documents branch convergence strategy."""
        content = _read_file(ORCHESTRATE_CMD)
        self.assertIn("convergence", content.lower())

    def test_swarm_status_command(self):
        """swarm status is in control commands table."""
        content = _read_file(ORCHESTRATE_CMD)
        self.assertIn("swarm status", content)


# ============================================================================
# Group 8: Smart Help & Do Routing
# ============================================================================
class TestSmartHelpAndDoRouting(unittest.TestCase):
    """Verify smart-help and do.md were updated with new features."""

    def test_smart_help_has_guard_suggestion(self):
        """smart-help.md suggests guard-audit for guard friction."""
        content = _read_file(SMART_HELP_CMD)
        self.assertIn("guard", content.lower())

    def test_smart_help_has_insights_suggestion(self):
        """smart-help.md suggests insights-apply."""
        content = _read_file(SMART_HELP_CMD)
        self.assertIn("insights", content.lower())

    def test_do_routes_to_guard_audit(self):
        """do.md has routing example for guard-audit."""
        content = _read_file(DO_CMD)
        self.assertIn("guard", content.lower())

    def test_do_routes_to_insights_apply(self):
        """do.md has routing example for insights-apply."""
        content = _read_file(DO_CMD)
        self.assertIn("insights", content.lower())

    def test_do_routes_to_autonomous_release(self):
        """do.md has routing for autonomous release."""
        content = _read_file(DO_CMD)
        self.assertIn("autonomous", content.lower())


# ============================================================================
# Group 9: Hub Counts & Entries
# ============================================================================
class TestHubConsistency(unittest.TestCase):
    """Verify hub.md counts match actual project state."""

    def test_hub_mentions_guard_audit(self):
        """hub.md lists guard-audit skill."""
        content = _read_file(HUB_CMD)
        self.assertIn("guard-audit", content)

    def test_hub_mentions_insights_apply(self):
        """hub.md lists insights-apply skill."""
        content = _read_file(HUB_CMD)
        self.assertIn("insights-apply", content)

    def test_hub_mentions_release_skill(self):
        """hub.md lists release skill."""
        content = _read_file(HUB_CMD)
        self.assertIn("release", content.lower())

    def test_skill_count_matches_plugin_json(self):
        """hub.md skill count matches plugin.json description."""
        with open(PLUGIN_JSON) as f:
            plugin = json.load(f)
        desc = plugin.get("description", "")
        # Extract skill count from plugin.json description
        match = re.search(r"(\d+)\s+skills", desc)
        if not match:
            self.skipTest("No skill count in plugin.json description")
        plugin_count = match.group(1)
        # Check hub references same count (case-insensitive)
        hub_content = _read_file(HUB_CMD).lower()
        self.assertIn(f"{plugin_count} skill", hub_content)

    def test_claude_md_skill_count_matches(self):
        """CLAUDE.md skill count matches plugin.json."""
        with open(PLUGIN_JSON) as f:
            plugin = json.load(f)
        desc = plugin.get("description", "")
        match = re.search(r"(\d+)\s+skills", desc)
        if not match:
            self.skipTest("No skill count in plugin.json description")
        plugin_count = match.group(1)
        claude_content = _read_file(CLAUDE_MD)
        self.assertIn(f"{plugin_count} skills", claude_content)


# ============================================================================
# Group 10: Cross-File Consistency
# ============================================================================
class TestCrossFileConsistency(unittest.TestCase):
    """Validate consistency across modified files."""

    def test_new_skills_have_skill_md(self):
        """New skills from this spec have SKILL.md files."""
        new_skills = ["guard-audit", "insights-apply", "release"]
        for name in new_skills:
            skill_file = os.path.join(CRAFT_ROOT, "skills", name, "SKILL.md")
            with self.subTest(skill=name):
                self.assertTrue(
                    os.path.isfile(skill_file),
                    f"skills/{name}/ missing SKILL.md"
                )

    def test_all_skills_have_valid_frontmatter(self):
        """Every SKILL.md has name and description in frontmatter."""
        skills_dir = os.path.join(CRAFT_ROOT, "skills")
        for name in os.listdir(skills_dir):
            skill_file = os.path.join(skills_dir, name, "SKILL.md")
            if os.path.isfile(skill_file):
                fm = _read_frontmatter(skill_file)
                with self.subTest(skill=name):
                    self.assertIn("name", fm, f"{name} missing frontmatter 'name'")
                    self.assertIn("description", fm, f"{name} missing frontmatter 'description'")

    def test_plugin_json_valid(self):
        """plugin.json is valid JSON with required fields."""
        with open(PLUGIN_JSON) as f:
            data = json.load(f)
        self.assertIn("name", data)
        self.assertIn("version", data)
        self.assertIn("description", data)

    def test_no_skill_has_empty_description(self):
        """No skill has an empty or trivially short description."""
        skills_dir = os.path.join(CRAFT_ROOT, "skills")
        for name in os.listdir(skills_dir):
            skill_file = os.path.join(skills_dir, name, "SKILL.md")
            if os.path.isfile(skill_file):
                fm = _read_frontmatter(skill_file)
                desc = fm.get("description", "")
                with self.subTest(skill=name):
                    self.assertGreater(
                        len(desc), 20,
                        f"skills/{name} description too short: '{desc[:30]}...'"
                    )


if __name__ == "__main__":
    unittest.main(verbosity=2)
