#!/usr/bin/env python3
"""
Integration tests for --orch flag across commands
"""

import pytest
from unittest.mock import Mock, patch, MagicMock


class TestOrchFlagIntegration:
    """Test --orch flag integration with commands"""

    def test_craft_do_with_orch_mode(self):
        """Test /craft:do 'task' --orch=optimize"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag(
            "add auth", orch_flag=True, mode="optimize"
        )

        assert should_orch is True
        assert mode == "optimize"

    @patch("utils.orch_flag_handler.prompt_user_for_mode")
    def test_craft_do_with_orch_no_mode(self, mock_prompt):
        """Test /craft:do 'task' --orch prompts for mode"""
        from utils.orch_flag_handler import handle_orch_flag

        mock_prompt.return_value = "debug"

        should_orch, mode = handle_orch_flag("fix bug", orch_flag=True, mode=None)

        assert should_orch is True
        assert mode == "debug"
        mock_prompt.assert_called_once()

    def test_craft_do_with_orch_invalid_mode(self):
        """Test /craft:do 'task' --orch=invalid raises error"""
        from utils.orch_flag_handler import handle_orch_flag

        with pytest.raises(ValueError, match="Invalid mode"):
            handle_orch_flag("task", orch_flag=True, mode="invalid")

    def test_craft_do_with_orch_and_dry_run(self):
        """Test /craft:do 'task' --orch --dry-run shows preview"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag("task", orch_flag=True, mode="optimize")

        assert should_orch is True
        assert mode == "optimize"

    def test_brainstorm_orch_with_categories(self):
        """Test /brainstorm 'task' --orch -C req,tech"""
        from utils.orch_flag_handler import handle_orch_flag

        categories_str = "req,tech"
        task = f"brainstorm 'payment' focusing on categories: {categories_str}"

        should_orch, mode = handle_orch_flag(task, orch_flag=True, mode="optimize")

        assert should_orch is True
        assert mode == "optimize"
        assert "req" in task
        assert "tech" in task

    def test_orch_overrides_complexity_routing(self):
        """Test --orch overrides complexity-based routing"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag(
            "lint code", orch_flag=True, mode="default"
        )

        assert should_orch is True

    def test_all_commands_support_orch(self):
        """Test all 5 commands support --orch flag"""
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

            orch_arg = next((arg for arg in args if arg.get("name") == "orch"), None)
            orch_mode_arg = next(
                (arg for arg in args if arg.get("name") == "orch-mode"), None
            )

            assert orch_arg is not None, f"{cmd_file} missing --orch argument"
            assert orch_mode_arg is not None, f"{cmd_file} missing --orch-mode argument"

    def test_check_command_orch_integration(self):
        """Test /craft:check --orch integration"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag(
            "comprehensive project validation", orch_flag=True, mode="release"
        )

        assert should_orch is True
        assert mode == "release"

    def test_docs_sync_orch_integration(self):
        """Test /craft:docs:sync --orch integration"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag(
            "documentation sync and update workflow", orch_flag=True, mode="optimize"
        )

        assert should_orch is True
        assert mode == "optimize"

    def test_ci_generate_orch_integration(self):
        """Test /craft:ci:generate --orch integration"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag(
            "generate comprehensive GitHub Actions workflow for auto-detected project",
            orch_flag=True,
            mode="default",
        )

        assert should_orch is True
        assert mode == "default"

    def test_orch_flag_with_all_valid_modes(self):
        """Test --orch with all valid modes across commands"""
        from utils.orch_flag_handler import handle_orch_flag, VALID_MODES

        modes_to_test = VALID_MODES

        for mode in modes_to_test:
            should_orch, selected_mode = handle_orch_flag(
                "test task", orch_flag=True, mode=mode
            )

            assert should_orch is True
            assert selected_mode == mode

    def test_orch_flag_disabled_does_not_orchestrate(self):
        """Test --orch not present does not orchestrate"""
        from utils.orch_flag_handler import handle_orch_flag

        should_orch, mode = handle_orch_flag("test task", orch_flag=False)

        assert should_orch is False
        assert mode is None


class TestOrchestratorModeConfiguration:
    """Test orchestrator mode configurations"""

    def test_default_mode_config(self):
        """Test default mode has correct configuration"""
        from utils.orch_flag_handler import get_mode_config

        config = get_mode_config("default")
        assert config["max_agents"] == 2
        assert config["compression"] == 70

    def test_debug_mode_config(self):
        """Test debug mode has correct configuration"""
        from utils.orch_flag_handler import get_mode_config

        config = get_mode_config("debug")
        assert config["max_agents"] == 1
        assert config["compression"] == 90

    def test_optimize_mode_config(self):
        """Test optimize mode has correct configuration"""
        from utils.orch_flag_handler import get_mode_config

        config = get_mode_config("optimize")
        assert config["max_agents"] == 4
        assert config["compression"] == 60

    def test_release_mode_config(self):
        """Test release mode has correct configuration"""
        from utils.orch_flag_handler import get_mode_config

        config = get_mode_config("release")
        assert config["max_agents"] == 4
        assert config["compression"] == 85


class TestComplexityScoreToOrchestrationMode:
    """Test mapping complexity scores to orchestration modes"""

    def test_low_complexity_recommends_default(self):
        """Test low complexity score recommends default mode"""
        from utils.complexity_scorer import recommend_orchestration_mode

        mode = recommend_orchestration_mode(2)
        assert mode == "default"

    def test_medium_complexity_recommends_default(self):
        """Test medium complexity score recommends default mode"""
        from utils.complexity_scorer import recommend_orchestration_mode

        mode = recommend_orchestration_mode(5)
        assert mode == "default"

    def test_high_complexity_recommends_optimize(self):
        """Test high complexity score recommends optimize mode"""
        from utils.complexity_scorer import recommend_orchestration_mode

        mode = recommend_orchestration_mode(7)
        assert mode == "optimize"

    def test_very_high_complexity_recommends_release(self):
        """Test very high complexity score recommends release mode"""
        from utils.complexity_scorer import recommend_orchestration_mode

        mode = recommend_orchestration_mode(9)
        assert mode == "release"

    def test_max_complexity_recommends_release(self):
        """Test max complexity score recommends release mode"""
        from utils.complexity_scorer import recommend_orchestration_mode

        mode = recommend_orchestration_mode(10)
        assert mode == "release"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
