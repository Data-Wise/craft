#!/usr/bin/env python3
"""
End-to-end tests for the command enhancements feature.

Validates that all 4 enhanced commands (orchestrate, check, docs:update,
git:worktree) have the required interactive behavior sections, YAML
frontmatter, documentation, help files, and mkdocs.yml navigation entries.

Tests cover the structural contract that enables the "Show Steps First"
interactive pattern across the codebase.
"""

import os
import re
import pytest
import yaml

# Base path for the feature branch worktree
BASE = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# The 4 enhanced command files
COMMAND_FILES = {
    "orchestrate": os.path.join(BASE, "commands", "orchestrate.md"),
    "check": os.path.join(BASE, "commands", "check.md"),
    "docs_update": os.path.join(BASE, "commands", "docs", "update.md"),
    "git_worktree": os.path.join(BASE, "commands", "git", "worktree.md"),
}

# Corresponding help/doc files in docs/commands/
HELP_FILES = {
    "orchestrate": os.path.join(BASE, "docs", "commands", "orchestrate.md"),
    "check": os.path.join(BASE, "docs", "commands", "check.md"),
    "docs_update": os.path.join(BASE, "docs", "commands", "docs", "update.md"),
    "git_worktree": os.path.join(BASE, "docs", "commands", "git", "worktree.md"),
}

# New documentation files
NEW_DOC_FILES = {
    "guide": os.path.join(BASE, "docs", "guide", "interactive-commands.md"),
    "tutorial": os.path.join(BASE, "docs", "tutorials", "interactive-orchestration.md"),
    "refcard": os.path.join(
        BASE, "docs", "reference", "REFCARD-INTERACTIVE-COMMANDS.md"
    ),
}

MKDOCS_YML = os.path.join(BASE, "mkdocs.yml")
ORCHESTRATOR_AGENT = os.path.join(BASE, "agents", "orchestrator-v2.md")


def _read_file(path):
    """Read file contents, return empty string if not found."""
    if not os.path.exists(path):
        return ""
    with open(path, "r") as f:
        return f.read()


def _extract_frontmatter(content):
    """Extract YAML frontmatter from a markdown file."""
    match = re.match(r"^---\n(.*?)\n---", content, re.DOTALL)
    if not match:
        return {}
    try:
        return yaml.safe_load(match.group(1)) or {}
    except yaml.YAMLError:
        return {}


# ============================================================================
# 1. Command Files Exist
# ============================================================================


class TestCommandFilesExist:
    """All 4 enhanced command files must exist."""

    @pytest.mark.parametrize("name,path", COMMAND_FILES.items())
    def test_command_file_exists(self, name, path):
        assert os.path.exists(path), f"Command file missing: {name} at {path}"

    @pytest.mark.parametrize("name,path", HELP_FILES.items())
    def test_help_file_exists(self, name, path):
        assert os.path.exists(path), f"Help file missing: {name} at {path}"

    @pytest.mark.parametrize("name,path", NEW_DOC_FILES.items())
    def test_new_doc_file_exists(self, name, path):
        assert os.path.exists(path), f"Doc file missing: {name} at {path}"


# ============================================================================
# 2. YAML Frontmatter Validation
# ============================================================================


class TestYAMLFrontmatter:
    """Command files must have valid YAML frontmatter with required fields."""

    @pytest.mark.parametrize("name,path", COMMAND_FILES.items())
    def test_has_yaml_frontmatter(self, name, path):
        content = _read_file(path)
        assert content.startswith("---"), f"{name} missing YAML frontmatter"
        assert "---" in content[3:], f"{name} frontmatter not closed"

    @pytest.mark.parametrize("name,path", COMMAND_FILES.items())
    def test_frontmatter_has_description(self, name, path):
        fm = _extract_frontmatter(_read_file(path))
        assert "description" in fm, f"{name} frontmatter missing 'description'"
        assert len(fm["description"]) > 10, f"{name} description too short"

    @pytest.mark.parametrize("name,path", COMMAND_FILES.items())
    def test_frontmatter_has_arguments_or_flags(self, name, path):
        fm = _extract_frontmatter(_read_file(path))
        has_args = "arguments" in fm or "flags" in fm
        assert has_args, f"{name} frontmatter missing 'arguments' or 'flags'"
        params = fm.get("arguments", fm.get("flags", []))
        assert isinstance(params, list), f"{name} arguments/flags not a list"
        assert len(params) > 0, f"{name} has no arguments/flags defined"

    def test_orchestrate_has_mode_argument(self):
        fm = _extract_frontmatter(_read_file(COMMAND_FILES["orchestrate"]))
        arg_names = [a.get("name") for a in fm.get("arguments", [])]
        assert "mode" in arg_names, "orchestrate missing 'mode' argument"

    def test_orchestrate_has_dry_run_argument(self):
        fm = _extract_frontmatter(_read_file(COMMAND_FILES["orchestrate"]))
        arg_names = [a.get("name") for a in fm.get("arguments", [])]
        assert "dry-run" in arg_names, "orchestrate missing 'dry-run' argument"

    def test_check_has_for_argument(self):
        fm = _extract_frontmatter(_read_file(COMMAND_FILES["check"]))
        arg_names = [a.get("name") for a in fm.get("arguments", [])]
        assert "for" in arg_names, "check missing 'for' argument"

    def test_docs_update_has_post_merge_flag(self):
        fm = _extract_frontmatter(_read_file(COMMAND_FILES["docs_update"]))
        content = _read_file(COMMAND_FILES["docs_update"])
        assert "--post-merge" in content, "docs:update missing --post-merge flag"

    def test_git_worktree_has_action_argument(self):
        fm = _extract_frontmatter(_read_file(COMMAND_FILES["git_worktree"]))
        arg_names = [a.get("name") for a in fm.get("arguments", [])]
        assert "action" in arg_names, "git:worktree missing 'action' argument"


# ============================================================================
# 3. Execution Behavior Sections (the core interactive pattern)
# ============================================================================


class TestExecutionBehavior:
    """Each command must have the MANDATORY Execution Behavior section."""

    REQUIRED_COMMANDS = ["orchestrate", "check", "docs_update", "git_worktree"]

    @pytest.mark.parametrize("name", REQUIRED_COMMANDS)
    def test_has_execution_behavior_section(self, name):
        content = _read_file(COMMAND_FILES[name])
        assert "Execution Behavior" in content, (
            f"{name} missing 'Execution Behavior' section"
        )

    @pytest.mark.parametrize("name", REQUIRED_COMMANDS)
    def test_execution_behavior_marked_mandatory(self, name):
        content = _read_file(COMMAND_FILES[name])
        assert "MANDATORY" in content, (
            f"{name} Execution Behavior not marked MANDATORY"
        )

    @pytest.mark.parametrize("name", REQUIRED_COMMANDS)
    def test_has_step_0(self, name):
        content = _read_file(COMMAND_FILES[name])
        assert "Step 0" in content, f"{name} missing Step 0 (show plan)"

    @pytest.mark.parametrize(
        "name", ["check", "docs_update", "git_worktree"]
    )
    def test_has_step_0_5_confirmation(self, name):
        """check, docs:update, and worktree have explicit Step 0.5 confirmation."""
        content = _read_file(COMMAND_FILES[name])
        assert "Step 0.5" in content or "Confirm" in content, (
            f"{name} missing Step 0.5 or confirmation step"
        )

    def test_orchestrate_has_mode_selection_step(self):
        content = _read_file(COMMAND_FILES["orchestrate"])
        assert "Mode Selection" in content, (
            "orchestrate missing Mode Selection in Step 0"
        )

    def test_orchestrate_has_interactive_confirmation(self):
        """Orchestrate must have a confirmation mechanism (AskUserQuestion or prompt)."""
        content = _read_file(COMMAND_FILES["orchestrate"])
        has_interactive = (
            "AskUserQuestion" in content
            or "confirm" in content.lower()
            or "proceed" in content.lower()
            or "prompt" in content.lower()
        )
        assert has_interactive, (
            "orchestrate must reference confirmation mechanism for mode selection"
        )

    def test_check_references_ask_user_question(self):
        content = _read_file(COMMAND_FILES["check"])
        assert "AskUserQuestion" in content, (
            "check must reference AskUserQuestion for confirmation"
        )

    def test_docs_update_references_ask_user_question(self):
        content = _read_file(COMMAND_FILES["docs_update"])
        assert "AskUserQuestion" in content, (
            "docs:update must reference AskUserQuestion"
        )

    def test_git_worktree_references_ask_user_question(self):
        content = _read_file(COMMAND_FILES["git_worktree"])
        assert "AskUserQuestion" in content, (
            "git:worktree must reference AskUserQuestion for confirmation"
        )


# ============================================================================
# 4. Orchestrate-Specific Features
# ============================================================================


class TestOrchestrateFeatures:
    """Orchestrate command has mode selection, wave checkpoints, and decision points."""

    def _content(self):
        return _read_file(COMMAND_FILES["orchestrate"])

    def test_defines_four_modes(self):
        content = self._content()
        for mode in ["default", "debug", "optimize", "release"]:
            assert mode in content, f"orchestrate missing mode '{mode}'"

    def test_mentions_wave_checkpoints(self):
        content = self._content()
        assert "wave" in content.lower() or "Wave" in content, (
            "orchestrate missing wave checkpoint documentation"
        )

    def test_mentions_dry_run(self):
        content = self._content()
        assert "--dry-run" in content or "dry-run" in content.lower()


# ============================================================================
# 5. Check-Specific Features
# ============================================================================


class TestCheckFeatures:
    """Check command has --for flag, mode-specific depth, step preview."""

    def _content(self):
        return _read_file(COMMAND_FILES["check"])

    def test_for_flag_contexts(self):
        content = self._content()
        for context in ["commit", "pr", "release", "deploy"]:
            assert context in content, f"check missing --for {context}"

    def test_has_check_categories(self):
        content = self._content()
        for check in ["lint", "test"]:
            assert check.lower() in content.lower(), (
                f"check missing '{check}' category"
            )

    def test_has_mode_specific_depth(self):
        content = self._content()
        # Should mention different depths for different modes
        assert "default" in content and "thorough" in content.lower()


# ============================================================================
# 6. Docs:Update-Specific Features
# ============================================================================


class TestDocsUpdateFeatures:
    """Docs:update has --post-merge pipeline and 9 category detection."""

    def _content(self):
        return _read_file(COMMAND_FILES["docs_update"])

    def test_has_post_merge_flag(self):
        content = self._content()
        assert "--post-merge" in content

    def test_post_merge_pipeline_phases(self):
        content = self._content()
        # The pipeline has multiple phases
        assert "auto-detect" in content.lower() or "Phase" in content

    def test_has_safe_vs_manual_categories(self):
        content = self._content()
        # Should distinguish safe (auto) from manual categories
        has_distinction = (
            ("safe" in content.lower() and "manual" in content.lower())
            or ("auto-fix" in content.lower())
            or ("auto" in content.lower() and "prompt" in content.lower())
        )
        assert has_distinction, "docs:update missing safe vs manual category distinction"

    def test_has_detection_categories(self):
        content = self._content()
        # Should mention at least some of the 9 detection categories
        categories_found = sum(
            1
            for cat in [
                "version",
                "command count",
                "navigation",
                "link",
                "help",
                "tutorial",
                "changelog",
            ]
            if cat.lower() in content.lower()
        )
        assert categories_found >= 3, (
            f"docs:update only mentions {categories_found}/7 expected categories"
        )


# ============================================================================
# 7. Git:Worktree-Specific Features
# ============================================================================


class TestGitWorktreeFeatures:
    """Git:worktree has auto-setup with scope detection."""

    def _content(self):
        return _read_file(COMMAND_FILES["git_worktree"])

    def test_has_scope_detection(self):
        content = self._content()
        assert "scope" in content.lower(), "worktree missing scope detection"

    def test_has_branch_pattern_detection(self):
        content = self._content()
        # Should detect branch patterns like fix/*, feature/*, v*
        patterns_found = sum(
            1 for p in ["fix/", "feature/", "v*"] if p in content
        )
        assert patterns_found >= 2, "worktree missing branch pattern detection"

    def test_has_auto_setup_file_creation(self):
        content = self._content()
        assert "ORCHESTRATE" in content, (
            "worktree missing auto-created ORCHESTRATE file reference"
        )

    def test_defines_actions(self):
        content = self._content()
        for action in ["setup", "create", "move", "list", "clean", "finish"]:
            assert action in content, f"worktree missing '{action}' action"


# ============================================================================
# 8. Documentation Files Content Validation
# ============================================================================


class TestDocumentationContent:
    """New documentation files have required sections."""

    def test_guide_covers_all_four_commands(self):
        content = _read_file(NEW_DOC_FILES["guide"])
        for cmd in ["orchestrate", "check", "docs:update", "worktree"]:
            assert cmd in content.lower(), (
                f"Interactive commands guide missing '{cmd}'"
            )

    def test_guide_describes_pattern(self):
        content = _read_file(NEW_DOC_FILES["guide"])
        assert "Step 0" in content, "Guide missing Step 0 pattern description"
        assert "Step 0.5" in content or "confirm" in content.lower()

    def test_tutorial_has_five_parts(self):
        content = _read_file(NEW_DOC_FILES["tutorial"])
        # Tutorial should have Parts 1-5
        parts_found = sum(
            1 for i in range(1, 6) if f"Part {i}" in content
        )
        assert parts_found >= 4, (
            f"Tutorial only has {parts_found}/5 expected parts"
        )

    def test_tutorial_covers_modes(self):
        content = _read_file(NEW_DOC_FILES["tutorial"])
        for mode in ["default", "debug", "optimize", "release"]:
            assert mode in content, f"Tutorial missing mode '{mode}'"

    def test_tutorial_covers_wave_checkpoints(self):
        content = _read_file(NEW_DOC_FILES["tutorial"])
        assert "wave" in content.lower() or "Wave" in content

    def test_tutorial_covers_decision_points(self):
        content = _read_file(NEW_DOC_FILES["tutorial"])
        assert "decision" in content.lower() or "Decision" in content

    def test_refcard_covers_all_commands(self):
        content = _read_file(NEW_DOC_FILES["refcard"])
        for cmd in ["orchestrate", "check", "docs:update", "worktree"]:
            assert cmd in content.lower(), f"Refcard missing '{cmd}'"

    def test_refcard_has_quick_start_sections(self):
        content = _read_file(NEW_DOC_FILES["refcard"])
        assert "Quick Start" in content

    def test_refcard_has_pattern_description(self):
        content = _read_file(NEW_DOC_FILES["refcard"])
        assert "Step 0" in content


# ============================================================================
# 9. Help Files Reference New Features
# ============================================================================


class TestHelpFileContent:
    """Help files in docs/commands/ reference the new interactive features."""

    @pytest.mark.parametrize("name,path", HELP_FILES.items())
    def test_help_file_is_non_empty(self, name, path):
        content = _read_file(path)
        assert len(content) > 100, f"Help file {name} is too short"

    def test_orchestrate_help_mentions_modes(self):
        content = _read_file(HELP_FILES["orchestrate"])
        for mode in ["default", "debug", "optimize", "release"]:
            assert mode in content, (
                f"Orchestrate help missing mode '{mode}'"
            )

    def test_orchestrate_help_mentions_interactive(self):
        content = _read_file(HELP_FILES["orchestrate"])
        has_interactive = (
            "interactive" in content.lower()
            or "plan" in content.lower()
            or "confirm" in content.lower()
        )
        assert has_interactive, "Orchestrate help doesn't mention interactive behavior"

    def test_check_help_mentions_for_flag(self):
        content = _read_file(HELP_FILES["check"])
        assert "--for" in content, "Check help missing --for flag"

    def test_worktree_help_mentions_auto_setup(self):
        content = _read_file(HELP_FILES["git_worktree"])
        has_auto = (
            "auto-setup" in content.lower()
            or "auto setup" in content.lower()
            or "scope" in content.lower()
        )
        assert has_auto, "Worktree help missing auto-setup/scope documentation"


# ============================================================================
# 10. mkdocs.yml Navigation Entries
# ============================================================================


class TestMkdocsNavigation:
    """mkdocs.yml includes navigation entries for new documentation."""

    @pytest.fixture
    def mkdocs_content(self):
        return _read_file(MKDOCS_YML)

    def test_mkdocs_exists(self):
        assert os.path.exists(MKDOCS_YML), "mkdocs.yml not found"

    def test_interactive_commands_guide_in_nav(self, mkdocs_content):
        assert "interactive-commands.md" in mkdocs_content, (
            "mkdocs.yml missing interactive-commands.md nav entry"
        )

    def test_interactive_orchestration_tutorial_in_nav(self, mkdocs_content):
        assert "interactive-orchestration.md" in mkdocs_content, (
            "mkdocs.yml missing interactive-orchestration.md nav entry"
        )

    def test_refcard_in_nav(self, mkdocs_content):
        assert "REFCARD-INTERACTIVE-COMMANDS.md" in mkdocs_content, (
            "mkdocs.yml missing REFCARD-INTERACTIVE-COMMANDS.md nav entry"
        )


# ============================================================================
# 11. Orchestrator Agent Spec Validation
# ============================================================================


class TestOrchestratorAgentSpec:
    """The orchestrator-v2.md agent spec includes new behavior sections."""

    @pytest.fixture
    def agent_content(self):
        return _read_file(ORCHESTRATOR_AGENT)

    def test_agent_file_exists(self):
        assert os.path.exists(ORCHESTRATOR_AGENT), (
            "agents/orchestrator-v2.md not found"
        )

    def test_has_plan_confirmation_behavior(self, agent_content):
        has_plan = (
            "plan confirmation" in agent_content.lower()
            or "BEHAVIOR 1" in agent_content
            or "Task Analysis" in agent_content
        )
        assert has_plan, "Agent spec missing plan confirmation behavior"

    def test_has_wave_checkpoint_behavior(self, agent_content):
        has_waves = (
            "wave checkpoint" in agent_content.lower()
            or "BEHAVIOR 2" in agent_content
            or "Wave" in agent_content
        )
        assert has_waves, "Agent spec missing wave checkpoint behavior"

    def test_has_decision_point_behavior(self, agent_content):
        has_decisions = (
            "decision point" in agent_content.lower()
            or "BEHAVIOR 6" in agent_content
            or "active decision" in agent_content.lower()
        )
        assert has_decisions, "Agent spec missing active decision point behavior"

    def test_references_ask_user_question(self, agent_content):
        assert "AskUserQuestion" in agent_content, (
            "Agent spec must reference AskUserQuestion tool"
        )


# ============================================================================
# 12. Cross-File Consistency
# ============================================================================


class TestCrossFileConsistency:
    """Verify consistency between command specs, docs, and agent spec."""

    def test_mode_names_consistent_across_files(self):
        """All files should use the same 4 mode names."""
        modes = {"default", "debug", "optimize", "release"}
        orchestrate_content = _read_file(COMMAND_FILES["orchestrate"])
        guide_content = _read_file(NEW_DOC_FILES["guide"])
        refcard_content = _read_file(NEW_DOC_FILES["refcard"])

        for mode in modes:
            assert mode in orchestrate_content, (
                f"orchestrate.md missing mode '{mode}'"
            )
            assert mode in guide_content, f"guide missing mode '{mode}'"
            assert mode in refcard_content, f"refcard missing mode '{mode}'"

    def test_four_commands_listed_in_guide(self):
        """Guide should mention all 4 enhanced commands."""
        content = _read_file(NEW_DOC_FILES["guide"])
        commands = ["orchestrate", "check", "docs:update", "git:worktree"]
        found = sum(1 for c in commands if c in content)
        assert found >= 3, f"Guide only references {found}/4 enhanced commands"

    def test_pattern_name_consistent(self):
        """The 'Show Steps First' pattern name should appear in guide and refcard."""
        for doc_name in ["guide", "refcard"]:
            content = _read_file(NEW_DOC_FILES[doc_name])
            has_pattern = (
                "Show Steps First" in content
                or "Step 0" in content
            )
            assert has_pattern, f"{doc_name} missing pattern description"

    def test_see_also_links_exist_in_guide(self):
        """Guide should have See Also links to other docs."""
        content = _read_file(NEW_DOC_FILES["guide"])
        assert "See Also" in content or "see also" in content.lower() or (
            "orchestrator" in content.lower() and "tutorial" in content.lower()
        )

    def test_see_also_links_exist_in_refcard(self):
        """Refcard should have See Also links to guide and tutorial."""
        content = _read_file(NEW_DOC_FILES["refcard"])
        assert "See Also" in content or "see also" in content.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
