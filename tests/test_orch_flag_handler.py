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


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
