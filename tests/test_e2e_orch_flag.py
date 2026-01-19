#!/usr/bin/env python3
"""
End-to-end tests for --orch flag integration

Tests complete workflows from command invocation through orchestrator spawning.
"""

import pytest
import subprocess
import sys


class TestOrchFlagE2E:
    """End-to-end tests for --orch flag functionality"""

    def test_orch_flag_handler_cli(self):
        """Test orch_flag_handler.py runs as CLI"""
        result = subprocess.run(
            [sys.executable, "utils/orch_flag_handler.py"],
            capture_output=True,
            text=True,
            cwd="/Users/dt/.git-worktrees/craft/feature-orch-flag-integration",
        )
        assert result.returncode == 0
        assert "Orch Flag Handler Test Cases" in result.stdout

    def test_handle_orch_flag_with_optimize(self):
        """Test handle_orch_flag returns correct values for optimize mode"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag(
            "test task", orch_flag=True, mode="optimize"
        )

        assert should_orch is True
        assert mode == "optimize"

    def test_handle_orch_flag_with_debug(self):
        """Test handle_orch_flag returns correct values for debug mode"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag("debug task", orch_flag=True, mode="debug")

        assert should_orch is True
        assert mode == "debug"

    def test_handle_orch_flag_with_release(self):
        """Test handle_orch_flag returns correct values for release mode"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag(
            "release task", orch_flag=True, mode="release"
        )

        assert should_orch is True
        assert mode == "release"

    def test_handle_orch_flag_disabled(self):
        """Test handle_orch_flag returns False when orch_flag is False"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag("simple task", orch_flag=False)

        assert should_orch is False
        assert mode is None

    def test_handle_orch_flag_invalid_mode_raises(self):
        """Test handle_orch_flag raises ValueError for invalid mode"""
        from utils.orch_flag_handler import handle_orch_flag

        with pytest.raises(ValueError, match="Invalid mode"):
            handle_orch_flag("task", orch_flag=True, mode="invalid_mode")

    def test_get_mode_config_all_modes(self):
        """Test get_mode_config returns correct config for all modes"""
        from utils.orch_flag_handler import get_mode_config

        configs = {
            "default": {"max_agents": 2, "compression": 70},
            "debug": {"max_agents": 1, "compression": 90},
            "optimize": {"max_agents": 4, "compression": 60},
            "release": {"max_agents": 4, "compression": 85},
        }

        for mode, expected in configs.items():
            config = get_mode_config(mode)
            assert config["max_agents"] == expected["max_agents"]
            assert config["compression"] == expected["compression"]

    def test_recommend_orchestration_mode_boundaries(self):
        """Test recommend_orchestration_mode at score boundaries"""
        from utils.complexity_scorer import recommend_orchestration_mode

        assert recommend_orchestration_mode(0) == "default"
        assert recommend_orchestration_mode(3) == "default"
        assert recommend_orchestration_mode(4) == "default"
        assert recommend_orchestration_mode(5) == "default"
        assert recommend_orchestration_mode(6) == "optimize"
        assert recommend_orchestration_mode(7) == "optimize"
        assert recommend_orchestration_mode(8) == "release"
        assert recommend_orchestration_mode(9) == "release"
        assert recommend_orchestration_mode(10) == "release"

    def test_valid_modes_constant(self):
        """Test VALID_MODES contains expected values"""
        from utils.orch_flag_handler import VALID_MODES

        assert "default" in VALID_MODES
        assert "debug" in VALID_MODES
        assert "optimize" in VALID_MODES
        assert "release" in VALID_MODES
        assert len(VALID_MODES) == 4

    def test_mode_descriptions_complete(self):
        """Test MODE_DESCRIPTIONS has entries for all valid modes"""
        from utils.orch_flag_handler import VALID_MODES, MODE_DESCRIPTIONS

        for mode in VALID_MODES:
            assert mode in MODE_DESCRIPTIONS
            assert len(MODE_DESCRIPTIONS[mode]) > 0

    def test_command_files_have_orch_args(self):
        """Test all 5 commands have --orch arguments in frontmatter"""
        import yaml

        commands = [
            "commands/do.md",
            "commands/workflow/brainstorm.md",
            "commands/check.md",
            "commands/docs/sync.md",
            "commands/ci/generate.md",
        ]

        for cmd_file in commands:
            with open(cmd_file, "r") as f:
                content = f.read()

            frontmatter_start = content.find("---")
            frontmatter_end = content.find("---", frontmatter_start + 1)
            frontmatter = yaml.safe_load(
                content[frontmatter_start + 3 : frontmatter_end]
            )

            args = frontmatter.get("arguments", []) or frontmatter.get("args", [])

            arg_names = [arg.get("name") for arg in args]

            assert "orch" in arg_names, f"{cmd_file} missing 'orch' argument"
            assert "orch-mode" in arg_names, f"{cmd_file} missing 'orch-mode' argument"


class TestOrchFlagPythonImports:
    """Test that all modules can be imported correctly"""

    def test_import_orch_flag_handler(self):
        """Test utils.orch_flag_handler imports successfully"""
        from utils.orch_flag_handler import (
            handle_orch_flag,
            prompt_user_for_mode,
            show_orchestration_preview,
            spawn_orchestrator,
            get_mode_config,
            VALID_MODES,
            MODE_DESCRIPTIONS,
        )

        assert callable(handle_orch_flag)
        assert callable(prompt_user_for_mode)
        assert callable(show_orchestration_preview)
        assert callable(spawn_orchestrator)
        assert callable(get_mode_config)
        assert isinstance(VALID_MODES, list)
        assert isinstance(MODE_DESCRIPTIONS, dict)

    def test_import_complexity_scorer(self):
        """Test complexity_scorer imports and has new function"""
        from utils.complexity_scorer import (
            calculate_complexity_score,
            get_routing_decision,
            recommend_orchestration_mode,
        )

        assert callable(calculate_complexity_score)
        assert callable(get_routing_decision)
        assert callable(recommend_orchestration_mode)


class TestOrchFlagDocumentation:
    """Test documentation files exist and are valid"""

    def test_user_guide_exists(self):
        """Test orch-flag-usage.md user guide exists"""
        import os

        guide_path = "/Users/dt/.git-worktrees/craft/feature-orch-flag-integration/docs/guide/orch-flag-usage.md"
        assert os.path.exists(guide_path)

    def test_user_guide_has_content(self):
        """Test user guide has substantial content"""
        guide_path = "/Users/dt/.git-worktrees/craft/feature-orch-flag-integration/docs/guide/orch-flag-usage.md"
        with open(guide_path, "r") as f:
            content = f.read()

        assert "## Overview" in content
        assert "## Supported Commands" in content
        assert "## Usage Patterns" in content
        assert "## Orchestration Modes" in content
        assert len(content) > 2000

    def test_claude_md_updated(self):
        """Test CLAUDE.md has --orch flag documentation"""
        with open(
            "/Users/dt/.git-worktrees/craft/feature-orch-flag-integration/CLAUDE.md",
            "r",
        ) as f:
            content = f.read()

        assert "--orch" in content
        assert "v2.5.0" in content

    def test_version_history_updated(self):
        """Test VERSION-HISTORY.md has v2.5.0 release notes"""
        with open(
            "/Users/dt/.git-worktrees/craft/feature-orch-flag-integration/docs/VERSION-HISTORY.md",
            "r",
        ) as f:
            content = f.read()

        assert "v2.5.0" in content
        assert "--orch Flag Integration" in content


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
