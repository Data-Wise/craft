#!/usr/bin/env python3
"""
Unit tests for orch_flag_handler.py
"""

import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import pytest
from unittest.mock import patch
from utils.orch_flag_handler import (
    handle_orch_flag,
    show_orchestration_preview,
    spawn_orchestrator,
    get_mode_config,
    prompt_user_for_mode,
    handle_orchestrator_failure,
    recommend_orchestration_mode,
    VALID_MODES,
    MODE_DESCRIPTIONS,
)

pytestmark = [pytest.mark.integration, pytest.mark.orchestrator]


def test_orch_flag_disabled():
    """Test --orch not present"""
    should_orch, mode = handle_orch_flag("task", orch_flag=False)
    assert should_orch is False
    assert mode is None


def test_orch_flag_with_valid_mode():
    """Test --orch=optimize"""
    should_orch, mode = handle_orch_flag("task", orch_flag=True, mode="optimize")
    assert should_orch is True
    assert mode == "optimize"


def test_orch_flag_with_all_valid_modes():
    """Test --orch with all valid modes"""
    for mode in VALID_MODES:
        should_orch, selected_mode = handle_orch_flag("task", orch_flag=True, mode=mode)
        assert should_orch is True
        assert selected_mode == mode


def test_orch_flag_with_invalid_mode():
    """Test --orch=invalid raises error"""
    with pytest.raises(ValueError, match="Invalid mode"):
        handle_orch_flag("task", orch_flag=True, mode="invalid")


def test_orch_flag_with_invalid_mode_shows_valid_options():
    """Test --orch=invalid shows valid modes in error"""
    try:
        handle_orch_flag("task", orch_flag=True, mode="invalid")
        assert False, "Should have raised ValueError"
    except ValueError as e:
        assert "invalid" in str(e).lower()
        for mode in VALID_MODES:
            assert mode in str(e)


def test_mode_config():
    """Test mode configuration retrieval"""
    config = get_mode_config("optimize")
    assert config["max_agents"] == 4
    assert config["compression"] == 60


def test_mode_config_default():
    """Test default mode configuration"""
    config = get_mode_config("default")
    assert config["max_agents"] == 2
    assert config["compression"] == 70


def test_mode_config_debug():
    """Test debug mode configuration"""
    config = get_mode_config("debug")
    assert config["max_agents"] == 1
    assert config["compression"] == 90


def test_mode_config_release():
    """Test release mode configuration"""
    config = get_mode_config("release")
    assert config["max_agents"] == 4
    assert config["compression"] == 85


def test_mode_config_unknown_falls_back_to_default():
    """Test unknown mode falls back to default"""
    config = get_mode_config("unknown")
    assert config == get_mode_config("default")


def test_all_modes_have_config():
    """Test all valid modes have config"""
    for mode in VALID_MODES:
        config = get_mode_config(mode)
        assert "max_agents" in config
        assert "compression" in config


def test_all_modes_have_description():
    """Test all valid modes have description"""
    for mode in VALID_MODES:
        assert mode in MODE_DESCRIPTIONS


def test_mode_descriptions_are_non_empty():
    """Test all mode descriptions are non-empty strings"""
    for mode, desc in MODE_DESCRIPTIONS.items():
        assert isinstance(desc, str)
        assert len(desc) > 0


def test_handle_orch_flag_returns_tuple():
    """Test handle_orch_flag returns correct tuple types"""
    should_orch, mode = handle_orch_flag("task", orch_flag=False)
    assert isinstance(should_orch, bool)
    assert mode is None or isinstance(mode, str)


def test_handle_orch_flag_with_none_mode():
    """Test handle_orch_flag when mode is explicitly None"""
    should_orch, mode = handle_orch_flag("task", orch_flag=True, mode=None)
    assert should_orch is True
    assert mode is not None


@patch("utils.orch_flag_handler.print")
def test_show_orchestration_preview(mock_print):
    """Test show_orchestration_preview function"""
    show_orchestration_preview("test task", "optimize")
    mock_print.assert_called()


@patch("utils.orch_flag_handler.print")
def test_spawn_orchestrator(mock_print):
    """Test spawn_orchestrator function"""
    spawn_orchestrator("test task", "debug")
    mock_print.assert_called()


@patch("utils.orch_flag_handler.print")
def test_spawn_orchestrator_with_extra_args(mock_print):
    """Test spawn_orchestrator with extra arguments"""
    spawn_orchestrator("test task", "release", extra_args="-v")
    mock_print.assert_called()


# ============================================================================
# v2.5.1 Tests: Mode Prompt
# ============================================================================


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_returns_default_in_test_context(mock_print):
    """Test mode prompt falls back to default in test context"""
    # In test context (no Claude Code), should return default
    mode = prompt_user_for_mode()
    assert mode == "default"
    mock_print.assert_called()


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_handles_exception_gracefully(mock_print):
    """Test mode prompt handles exceptions without crashing"""
    # Even if something goes wrong, should not crash
    try:
        mode = prompt_user_for_mode()
        assert mode in VALID_MODES
    except Exception:
        pytest.fail("prompt_user_for_mode() should not raise exceptions")


def test_mode_descriptions_match_valid_modes():
    """Test all valid modes have descriptions"""
    for mode in VALID_MODES:
        assert mode in MODE_DESCRIPTIONS
        assert len(MODE_DESCRIPTIONS[mode]) > 0


@patch("utils.orch_flag_handler.print")
def test_prompt_displays_all_modes(mock_print):
    """Test prompt displays all available modes"""
    prompt_user_for_mode()
    # Verify print was called multiple times (for each mode)
    assert mock_print.call_count > len(VALID_MODES)


@patch("utils.orch_flag_handler.print")
def test_prompt_provides_usage_hint(mock_print):
    """Test prompt provides hint about explicit mode selection"""
    prompt_user_for_mode()
    # Check that print was called with helpful messages
    calls = [str(call) for call in mock_print.call_args_list]
    full_output = " ".join(calls)
    assert "mode" in full_output.lower() or "claude" in full_output.lower()


def test_prompt_returns_valid_mode():
    """Test prompt always returns a valid mode"""
    mode = prompt_user_for_mode()
    assert mode in VALID_MODES


# ============================================================================
# v2.5.1 Tests: Error Handling
# ============================================================================


@patch("utils.orch_flag_handler.print")
def test_spawn_orchestrator_returns_boolean(mock_print):
    """Test spawn_orchestrator returns boolean result"""
    result = spawn_orchestrator("test task", "optimize")
    assert isinstance(result, bool)


@patch("utils.orch_flag_handler.print")
def test_spawn_orchestrator_returns_true_on_success(mock_print):
    """Test spawn_orchestrator returns True on successful spawn"""
    result = spawn_orchestrator("test task", "optimize")
    assert result is True


@patch("utils.orch_flag_handler.print")
def test_spawn_orchestrator_accepts_extra_args(mock_print):
    """Test spawn_orchestrator accepts additional arguments"""
    # Should not raise exception with extra args
    result = spawn_orchestrator("test task", "optimize", "--dry-run")
    assert isinstance(result, bool)
    assert result is True


@patch("utils.orch_flag_handler.print")
def test_handle_orchestrator_failure_displays_message(mock_print):
    """Test failure handler displays user-friendly message"""
    handle_orchestrator_failure("test task", "Orchestrator not found")

    # Verify error message components were printed
    assert mock_print.call_count > 5  # Multiple lines of output
    calls = [str(call) for call in mock_print.call_args_list]
    full_output = " ".join(calls)

    # Check for key elements in output
    assert "test task" in full_output.lower() or "test" in full_output
    assert "error" in full_output.lower() or "failed" in full_output
    assert "suggestion" in full_output.lower() or "fallback" in full_output


@patch("utils.orch_flag_handler.print")
def test_handle_orchestrator_failure_provides_suggestions(mock_print):
    """Test failure handler provides actionable suggestions"""
    handle_orchestrator_failure("test task", "Error message")

    calls = [str(call) for call in mock_print.call_args_list]
    full_output = " ".join(calls)

    # Should mention explicit commands or dry-run
    has_helpful_content = any(
        keyword in full_output.lower()
        for keyword in ["command", "dry-run", "check", "available"]
    )
    assert has_helpful_content


# ============================================================================
# v2.5.1 Tests: Mode Recommendation
# ============================================================================


def test_recommend_orchestration_mode_low_complexity():
    """Test mode recommendation for low complexity (0-3)"""
    assert recommend_orchestration_mode(0) == "default"
    assert recommend_orchestration_mode(2) == "default"
    assert recommend_orchestration_mode(3) == "default"


def test_recommend_orchestration_mode_medium_complexity():
    """Test mode recommendation for medium complexity (4-7)"""
    assert recommend_orchestration_mode(4) == "optimize"
    assert recommend_orchestration_mode(5) == "optimize"
    assert recommend_orchestration_mode(7) == "optimize"


def test_recommend_orchestration_mode_high_complexity():
    """Test mode recommendation for high complexity (8-10)"""
    assert recommend_orchestration_mode(8) == "release"
    assert recommend_orchestration_mode(9) == "release"
    assert recommend_orchestration_mode(10) == "release"


def test_recommend_orchestration_mode_returns_valid_modes():
    """Test recommendations always return valid modes"""
    for score in range(0, 11):
        mode = recommend_orchestration_mode(score)
        assert mode in VALID_MODES


# ============================================================================
# v2.8.0+ Tests: Interactive Command Enhancements
# ============================================================================


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_always_returns_default(mock_print):
    """Test non-interactive fallback always returns 'default'"""
    result = prompt_user_for_mode()
    assert result == "default"


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_displays_all_mode_names(mock_print):
    """Test fallback displays every valid mode name in output"""
    prompt_user_for_mode()
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    for mode in VALID_MODES:
        assert mode in all_output, f"Mode '{mode}' not found in printed output"


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_displays_all_descriptions(mock_print):
    """Test fallback displays mode descriptions"""
    prompt_user_for_mode()
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    for desc in MODE_DESCRIPTIONS.values():
        assert desc in all_output, f"Description '{desc}' not found in output"


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_mentions_ask_user_question(mock_print):
    """Test fallback references AskUserQuestion (the real interactive mechanism)"""
    prompt_user_for_mode()
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "AskUserQuestion" in all_output


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_mentions_step_0(mock_print):
    """Test fallback references Step 0 (the orchestrate.md spec location)"""
    prompt_user_for_mode()
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "Step 0" in all_output


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_mentions_explicit_flag_usage(mock_print):
    """Test fallback tells users about --orch=<mode> for explicit selection"""
    prompt_user_for_mode()
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "--orch=" in all_output


@patch("utils.orch_flag_handler.print")
def test_prompt_user_for_mode_print_count(mock_print):
    """Test fallback prints header + modes + hints (at least 8 lines)"""
    prompt_user_for_mode()
    # Header (2) + separator (1) + 4 modes + 3 hint lines = 10 minimum
    assert mock_print.call_count >= 8


@patch("utils.orch_flag_handler.print")
def test_show_preview_with_extra_context(mock_print):
    """Test orchestration preview displays extra context dict"""
    extra = {"Branch": "feature/auth", "Files": "12 changed"}
    show_orchestration_preview("add auth", "optimize", extra_context=extra)
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "feature/auth" in all_output
    assert "12 changed" in all_output


@patch("utils.orch_flag_handler.print")
def test_show_preview_without_extra_context(mock_print):
    """Test preview works without extra context"""
    show_orchestration_preview("task", "default")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "task" in all_output
    assert "default" in all_output


@patch("utils.orch_flag_handler.print")
def test_show_preview_displays_mode_config(mock_print):
    """Test preview shows max_agents and compression for the mode"""
    show_orchestration_preview("task", "release")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "4" in all_output  # max_agents for release
    assert "85" in all_output  # compression for release


@patch("utils.orch_flag_handler.print")
def test_show_preview_displays_dry_run_banner(mock_print):
    """Test preview shows DRY RUN header"""
    show_orchestration_preview("task", "default")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "DRY RUN" in all_output


@patch("utils.orch_flag_handler.print")
def test_show_preview_truncates_long_task(mock_print):
    """Test preview truncates task descriptions >49 chars"""
    long_task = "a" * 100
    show_orchestration_preview(long_task, "default")
    # Should not crash - preview handles long strings
    mock_print.assert_called()


def test_mode_config_values_in_range():
    """Test all mode configs have sensible values"""
    for mode in VALID_MODES:
        config = get_mode_config(mode)
        assert 1 <= config["max_agents"] <= 8
        assert 0 < config["compression"] <= 100


def test_handle_orch_flag_no_mode_calls_prompt(capsys):
    """Test orch_flag=True with no mode triggers prompt fallback"""
    should_orch, mode = handle_orch_flag("task", orch_flag=True, mode=None)
    assert should_orch is True
    assert mode == "default"  # prompt_user_for_mode returns "default"
    captured = capsys.readouterr()
    assert "Orchestration Mode" in captured.out


@patch("utils.orch_flag_handler.print")
def test_spawn_orchestrator_displays_task_and_mode(mock_print):
    """Test spawn shows both task and mode in output"""
    spawn_orchestrator("refactor auth", "debug")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "refactor auth" in all_output
    assert "debug" in all_output


@patch("utils.orch_flag_handler.print")
def test_spawn_orchestrator_shows_craft_command(mock_print):
    """Test spawn shows the /craft:orchestrate command it would execute"""
    spawn_orchestrator("add tests", "optimize")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "/craft:orchestrate" in all_output


@patch("utils.orch_flag_handler.print")
def test_failure_handler_shows_task_name(mock_print):
    """Test failure handler includes the failed task name"""
    handle_orchestrator_failure("deploy to prod", "timeout")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "deploy to prod" in all_output


@patch("utils.orch_flag_handler.print")
def test_failure_handler_shows_error_message(mock_print):
    """Test failure handler includes the error message"""
    handle_orchestrator_failure("task", "Agent pool exhausted")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "Agent pool exhausted" in all_output


@patch("utils.orch_flag_handler.print")
def test_failure_handler_mentions_dry_run(mock_print):
    """Test failure handler suggests --dry-run as recovery option"""
    handle_orchestrator_failure("task", "error")
    all_output = " ".join(str(c) for c in mock_print.call_args_list)
    assert "dry-run" in all_output.lower()


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
