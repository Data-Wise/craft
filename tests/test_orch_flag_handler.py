#!/usr/bin/env python3
"""
Unit tests for orch_flag_handler.py
"""

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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
