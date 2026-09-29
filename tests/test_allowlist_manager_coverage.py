"""Unit coverage for the curated allowlist manager and its CLI."""

import json
import sys
from pathlib import Path

from utils import allowlist_manager as manager


def test_load_save_merge_reset_and_preview(tmp_path):
    path = tmp_path / "nested" / "settings.json"
    assert manager.load_settings(path) == {}
    settings = {"permissions": {"allow": ["user entry"]}, "other": True}
    manager.save_settings(path, settings)
    assert json.loads(path.read_text()) == settings
    assert manager._get_allow(settings) == ["user entry"]
    assert manager._get_craft_list(settings) == []

    added, merged = manager.add_entries(settings, ["new", "user entry", "other"])
    assert added == 2 and merged["other"] is True
    assert merged["permissions"]["allow"] == ["user entry", "new", "other"]
    assert merged["craft_allowlist"] == ["new", "other"]

    removed, reset = manager.reset_entries(merged)
    assert removed == 2 and reset["permissions"]["allow"] == ["user entry"]
    assert reset["craft_allowlist"] == []

    preview = manager.dry_run_output({"craft_allowlist": [manager.TIER1[0]]}, [manager.TIER1[0], "unknown"])
    assert "Tier 1" in preview and "already present" in preview and "?" in preview
    assert "Would add 1 new entries" in preview


def test_main_dry_run_add_repeat_and_reset(tmp_path, monkeypatch, capsys):
    path = tmp_path / "settings.json"
    monkeypatch.setattr(sys, "argv", ["allowlist", "--settings-path", str(path), "--dry-run"])
    manager.main()
    assert "Dry run" in capsys.readouterr().out and not path.exists()

    monkeypatch.setattr(sys, "argv", ["allowlist", "--settings-path", str(path)])
    manager.main()
    first = json.loads(path.read_text())
    assert first["craft_allowlist"] == manager.CURATED
    assert "Added" in capsys.readouterr().out

    manager.main()
    assert "Already up to date" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["allowlist", "--settings-path", str(path), "--reset"])
    manager.main()
    reset = json.loads(path.read_text())
    assert reset["craft_allowlist"] == [] and reset["permissions"]["allow"] == []
    assert "Removed" in capsys.readouterr().out
