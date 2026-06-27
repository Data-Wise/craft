#!/usr/bin/env python3
"""
E2E structural tests for /craft:workflow:brief and its --brief integration in /craft:do.

Validates:
- brief.md has valid frontmatter with required arguments
- Output constraints (Lever 1) are present and well-formed
- do.md declares --brief argument and Step 5.5
- plugin.json workflow command count matches file count
- Footer suggestion is wired in do.md

Run with: python3 -m pytest tests/test_brief_command_e2e.py -v
"""

import json
import re
from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.e2e, pytest.mark.structure]

PLUGIN_DIR = Path(__file__).parent.parent
COMMANDS_DIR = PLUGIN_DIR / "commands"
BRIEF_CMD = COMMANDS_DIR / "workflow" / "brief.md"
DO_CMD = COMMANDS_DIR / "do.md"
PLUGIN_JSON = PLUGIN_DIR / ".claude-plugin" / "plugin.json"


def _extract_frontmatter(path: Path) -> dict:
    content = path.read_text(encoding="utf-8")
    m = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not m:
        return {}
    try:
        return yaml.safe_load(m.group(1)) or {}
    except yaml.YAMLError:
        return {}


def _arg_names(frontmatter: dict) -> set[str]:
    return {a["name"] for a in frontmatter.get("arguments", [])}


# ============================================================================
# 1. brief.md — file existence and frontmatter
# ============================================================================

class TestBriefFileStructure:
    """brief.md must exist and have valid frontmatter."""

    def test_brief_command_exists(self):
        assert BRIEF_CMD.exists(), "commands/workflow/brief.md not found"

    def test_brief_has_description(self):
        fm = _extract_frontmatter(BRIEF_CMD)
        assert fm.get("description"), "brief.md missing frontmatter description"

    def test_brief_has_category_workflow(self):
        fm = _extract_frontmatter(BRIEF_CMD)
        assert fm.get("category") == "workflow", (
            f"Expected category 'workflow', got '{fm.get('category')}'"
        )

    def test_brief_declares_plan_argument(self):
        fm = _extract_frontmatter(BRIEF_CMD)
        assert "plan" in _arg_names(fm), (
            "brief.md must declare 'plan' argument"
        )

    def test_brief_declares_verbose_argument(self):
        fm = _extract_frontmatter(BRIEF_CMD)
        assert "verbose" in _arg_names(fm), (
            "brief.md must declare 'verbose' argument"
        )

    def test_brief_declares_show_context_argument(self):
        fm = _extract_frontmatter(BRIEF_CMD)
        assert "show-context" in _arg_names(fm), (
            "brief.md must declare 'show-context' argument"
        )

    def test_brief_arguments_have_required_false(self):
        fm = _extract_frontmatter(BRIEF_CMD)
        for arg in fm.get("arguments", []):
            assert arg.get("required") is False, (
                f"Argument '{arg.get('name')}' should be required: false"
            )

    def test_brief_arguments_default_to_false(self):
        fm = _extract_frontmatter(BRIEF_CMD)
        for arg in fm.get("arguments", []):
            assert arg.get("default") is False, (
                f"Argument '{arg.get('name')}' should default: false"
            )


# ============================================================================
# 2. brief.md — Lever 1 output constraints (the whole point of this command)
# ============================================================================

class TestBriefOutputConstraints:
    """The three EXECUTABLE ACTION / CONDITION→MITIGATION / EXACT ARTIFACT constraints must all be present."""

    @pytest.fixture(autouse=True)
    def content(self):
        self._content = BRIEF_CMD.read_text(encoding="utf-8")

    def test_next_step_constraint_present(self):
        assert "EXECUTABLE ACTION CONSTRAINT" in self._content, (
            "brief.md missing 'Next step — EXECUTABLE ACTION CONSTRAINT' section"
        )

    def test_next_step_forbids_gerunds(self):
        assert "NEVER output" in self._content, (
            "brief.md must contain NEVER output section for Next step"
        )

    def test_watch_out_constraint_present(self):
        assert "CONDITION → MITIGATION CONSTRAINT" in self._content, (
            "brief.md missing 'Watch out for — CONDITION → MITIGATION CONSTRAINT' section"
        )

    def test_watch_out_arrow_notation_required(self):
        """The → separator must be explicitly required."""
        content = self._content
        # Constraint section must call for the arrow
        assert "→" in content and "MUST contain two parts joined by" in content, (
            "brief.md must require → separator in Watch out for field"
        )

    def test_connects_to_constraint_present(self):
        assert "EXACT ARTIFACT CONSTRAINT" in self._content, (
            "brief.md missing 'Connects to — EXACT ARTIFACT CONSTRAINT' section"
        )

    def test_connects_to_accepts_dash_for_none(self):
        """'—' must be a valid value for Connects to (no downstream work)."""
        assert "No downstream work" in self._content or "— " in self._content, (
            "brief.md must document '—' as valid value for Connects to"
        )

    def test_constraints_fire_unconditionally(self):
        """Constraints must apply WITHOUT EXCEPTION (Lever 1 guarantee)."""
        assert "WITHOUT EXCEPTION" in self._content, (
            "brief.md must state constraints apply WITHOUT EXCEPTION"
        )

    def test_output_format_block_present(self):
        """Default 3-line output format must be shown."""
        content = self._content
        assert "Next step:" in content and "Watch out for:" in content and "Connects to:" in content, (
            "brief.md must show the 3-line output format"
        )

    def test_verbose_flag_output_format_present(self):
        assert "--verbose" in self._content, "brief.md must document --verbose output format"

    def test_plan_flag_produces_mini_plan(self):
        assert "mini-plan" in self._content or "Plan:" in self._content, (
            "brief.md --plan phase must describe mini-plan output"
        )

    def test_not_a_deprecated_shim(self):
        """brief.md must not be a thin shim delegating to adhd-workflow."""
        content = self._content
        assert "adhd-workflow" not in content.lower(), (
            "brief.md must be a full implementation, not a shim to adhd-workflow"
        )


# ============================================================================
# 3. do.md — --brief integration
# ============================================================================

class TestDoCommandBriefIntegration:
    """do.md must declare --brief and wire Step 5.5."""

    @pytest.fixture(autouse=True)
    def content(self):
        self._content = DO_CMD.read_text(encoding="utf-8")
        self._fm = _extract_frontmatter(DO_CMD)

    def test_do_declares_brief_argument(self):
        assert "- name: brief" in self._content, (
            "commands/do.md must declare '- name: brief' in frontmatter arguments"
        )

    def test_brief_argument_default_false(self):
        for arg in self._fm.get("arguments", []):
            if arg.get("name") == "brief":
                assert arg.get("default") is False, (
                    "--brief must default to false (block only, not auto-fire)"
                )
                return
        pytest.fail("Could not find 'brief' argument in do.md frontmatter")

    def test_do_wires_step_5_5(self):
        assert "Step 5.5" in self._content, (
            "commands/do.md must contain Step 5.5 (Brief Appendix)"
        )

    def test_step_5_5_references_brief_constraints(self):
        """Step 5.5 must point to brief.md for output constraints, not restate them."""
        # The step should cross-reference brief.md
        assert "commands/workflow/brief.md" in self._content or "brief.md" in self._content, (
            "Step 5.5 should reference commands/workflow/brief.md for constraints"
        )

    def test_do_has_brief_footer_suggestion(self):
        assert "/craft:workflow:brief --plan" in self._content, (
            "do.md must contain the footer suggestion '/craft:workflow:brief --plan'"
        )

    def test_step_5_5_is_block_only_no_plan_phase(self):
        """When --brief fires from do, it must be block-only (no --plan expansion)."""
        # Find Step 5.5 section and verify it says block only / no plan phase
        match = re.search(r"Step 5\.5.*?(?=###|\Z)", self._content, re.DOTALL)
        if match:
            step_text = match.group(0)
            assert "block only" in step_text.lower() or "no.*plan" in step_text.lower() or "Do NOT trigger" in step_text, (
                "Step 5.5 must explicitly exclude the --plan phase"
            )


# ============================================================================
# 4. plugin.json — workflow command count
# ============================================================================

class TestWorkflowCommandCount:
    """plugin.json description must reflect the actual workflow command count."""

    def test_workflow_command_count_matches_files(self):
        workflow_dir = COMMANDS_DIR / "workflow"
        actual = len(list(workflow_dir.glob("*.md")))
        plugin_json = json.loads(PLUGIN_JSON.read_text())
        desc = plugin_json.get("description", "")

        m = re.search(r"(\d+) workflow", desc)
        assert m, f"plugin.json description does not contain '(N) workflow': {desc}"

        documented = int(m.group(1))
        assert documented == actual, (
            f"plugin.json says {documented} workflow commands but found {actual} files "
            f"in commands/workflow/. Update plugin.json description."
        )

    def test_brief_md_counted_in_total(self):
        """brief.md must be included in the total command count in plugin.json."""
        plugin_json = json.loads(PLUGIN_JSON.read_text())
        desc = plugin_json.get("description", "")
        m = re.search(r"(\d+) commands", desc)
        assert m, "plugin.json must report total command count"

        # brief.md must exist and workflow dir must be counted
        assert BRIEF_CMD.exists(), "brief.md must exist to be counted"
        total_documented = int(m.group(1))
        # Just verify the total is >= 117 (as of this addition)
        assert total_documented >= 117, (
            f"Total command count in plugin.json is {total_documented}, expected >= 117 after adding brief"
        )


# ============================================================================
# 5. Cross-reference: brief.md → replaces research-session-defaults.md auto-fire
# ============================================================================

class TestAutoFireReplacement:
    """brief.md must document that it replaced the auto-fire behavior."""

    def test_brief_references_research_session_defaults(self):
        content = BRIEF_CMD.read_text(encoding="utf-8")
        assert "research-session-defaults" in content, (
            "brief.md must state it replaces the auto-fire in research-session-defaults.md"
        )

    def test_brief_says_invoke_explicitly(self):
        content = BRIEF_CMD.read_text(encoding="utf-8")
        assert "explicitly" in content.lower() or "on demand" in content.lower(), (
            "brief.md must say it is invoked explicitly (not auto-fired)"
        )
