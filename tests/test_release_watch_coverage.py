"""Offline unit coverage for release-watch fetch, analysis, and output paths."""

import base64
import importlib.util
import json
import subprocess
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import Mock

import pytest


SCRIPT = Path(__file__).parents[1] / "scripts" / "release-watch.py"
SPEC = importlib.util.spec_from_file_location("release_watch_coverage", SCRIPT)
rw = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(rw)


def findings():
    return {key: [] for key in ("NEW", "DEPRECATED", "BREAKING", "FIXED")}


def state(**overrides):
    value = {"hardcoded_models": [], "agent_features": {}, "hook_events": []}
    value.update(overrides)
    return value


def test_box_cache_load_save_and_secure_write(tmp_path, monkeypatch):
    assert len(rw.box_top()) == rw.BOX_WIDTH
    assert rw.box_line("x").startswith("║  x")
    assert rw.box_blank().strip("║ ") == "" * 0
    monkeypatch.setattr(rw, "CACHE_DIR", tmp_path)
    monkeypatch.setattr(rw, "CACHE_FILE", tmp_path / "cache.json")
    assert rw.load_cache() == {}
    rw.set_cached("x", {"ok": True}, {})
    assert rw.load_cache()["x"]["data"] == {"ok": True}
    rw.CACHE_FILE.write_text("not json")
    assert rw.load_cache() == {}


def test_prerequisite_check_errors(monkeypatch, capsys):
    monkeypatch.setattr(rw.subprocess, "run", Mock(side_effect=FileNotFoundError()))
    with pytest.raises(SystemExit):
        rw.check_gh_installed()
    assert "not installed" in capsys.readouterr().err
    monkeypatch.setattr(rw.subprocess, "run", Mock(side_effect=subprocess.CalledProcessError(1, "gh")))
    with pytest.raises(SystemExit):
        rw.check_gh_installed()
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1))
    with pytest.raises(SystemExit):
        rw.check_gh_auth()
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0))
    rw.check_gh_installed()
    rw.check_gh_auth()


def test_release_fetch_cache_live_fallback_and_errors(monkeypatch, capsys):
    cached = {"github_releases": {"timestamp": rw.time.time(), "data": [
        {"tag_name": "v1.2.0", "published_at": "2026-02"},
        {"tag_name": "v1.1.0", "published_at": "2026-01"},
    ]}}
    monkeypatch.setattr(rw.subprocess, "run", Mock(side_effect=AssertionError("cache should win")))
    assert [r["tag_name"] for r in rw.fetch_releases(5, since="v1.1.0", cache=cached)] == ["v1.2.0"]

    saved = []
    monkeypatch.setattr(rw, "set_cached", lambda key, data, cache: saved.append((key, data)))
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout=json.dumps(cached["github_releases"]["data"]), stderr=""))
    assert len(rw.fetch_releases(1, cache={})) == 1
    assert saved and saved[0][0] == "github_releases"

    stale = {"github_releases": {"timestamp": 0, "data": cached["github_releases"]["data"]}}
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr="offline"))
    assert rw.fetch_releases(1, cache=stale)[0]["tag_name"] == "v1.2.0"
    assert "stale cache" in capsys.readouterr().err
    with pytest.raises(SystemExit):
        rw.fetch_releases(1, cache={}, no_cache=True)

    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout="bad json", stderr=""))
    with pytest.raises(SystemExit):
        rw.fetch_releases(1, cache={}, no_cache=True)


def test_changelog_and_desktop_fetch_cache_and_graceful_failures(monkeypatch, capsys):
    fresh = {"changelog": {"timestamp": rw.time.time(), "data": "cached"}}
    monkeypatch.setattr(rw.subprocess, "run", Mock(side_effect=AssertionError("cache should win")))
    assert rw.fetch_changelog(fresh) == "cached"
    monkeypatch.setattr(rw, "set_cached", lambda *args: None)
    encoded = base64.b64encode(b"## 1.2.3\n- Fixed issue").decode()
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout=encoded, stderr=""))
    assert "Fixed issue" in rw.fetch_changelog({})
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout="/w==", stderr=""))
    assert rw.fetch_changelog({}) is None
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr="offline"))
    assert rw.fetch_changelog({}) is None
    assert "continuing without it" in capsys.readouterr().err

    cached_desktop = {"desktop_releases": {"timestamp": rw.time.time(), "data": [{"date": "today"}]}}
    assert rw.fetch_desktop_releases(cached_desktop) == [{"date": "today"}]
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout="<h2>January 1, 2026</h2><p>Plugin support</p>", stderr=""))
    assert rw.fetch_desktop_releases({})[0]["date"] == "January 1, 2026"
    monkeypatch.setattr(rw.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="", stderr="offline"))
    assert rw.fetch_desktop_releases({"desktop_releases": {"data": [{"date": "stale"}]}})[0]["date"] == "stale"
    assert rw.fetch_desktop_releases({}) == []


def test_scanners_action_items_and_desktop_parser():
    releases = [{"tag_name": "v2.0.0", "body": "- Added new plugin support\n- Breaking migration required\n- Fixed bug\n# ignored"}]
    scan = rw.scan_releases(releases)
    assert scan["NEW"] and scan["BREAKING"] and scan["FIXED"]
    enriched = [{"tag_name": "v2.0.0", "body": "Removed old API" , "body_changelog": [{"text": "Removed old API", "category": "FIXED"}]}]
    assert rw.scan_releases(enriched)["FIXED"]
    desktop = rw._parse_desktop_html("<h2>January 1, 2026</h2><p><strong>New feature</strong> Plugin support</p><h2>bad heading</h2>")
    assert desktop and desktop[0]["source"] == "anthropic-docs"
    assert rw.scan_desktop_releases(desktop)["NEW"]
    actions = rw.generate_action_items({**scan, "DEPRECATED": [{"version": "2", "summary": "old"}]}, state(hardcoded_models=[{"model": "claude-sonnet-4"}]))
    assert len(actions) == 3
    safe, review = rw.classify_action_items({"NEW": [{"source": "github", "keywords": ["model"]}],
        "BREAKING": [{"source": "github"}], "FIXED": [{"source": "anthropic-docs"}]})
    assert len(safe) == 1 and len(review) == 2


def test_state_analysis_and_patch_generation(tmp_path, monkeypatch):
    (tmp_path / "agents").mkdir()
    (tmp_path / "commands").mkdir()
    (tmp_path / "agents" / "agent.md").write_text("---\nmemory: user\nbackground: true\n---\nclaude-sonnet-4")
    (tmp_path / "commands" / "test.md").write_text("---\ntrigger: on-save\nevent: stop\n---\n")
    monkeypatch.setattr(rw, "PLUGIN_ROOT", tmp_path)
    analyzed = rw.analyze_craft_state()
    assert analyzed["agent_features"]["agents/agent.md"]["memory"] == "user"
    assert analyzed["hardcoded_models"]
    assert len(analyzed["hook_events"]) == 2

    monkeypatch.setattr(rw, "CACHE_DIR", tmp_path / ".claude")
    monkeypatch.setattr(rw, "PATCH_FILE", tmp_path / ".claude" / "fix.patch")
    monkeypatch.setattr(rw, "MODEL_PATTERNS", [r"claude-sonnet-4"])
    item = {"keywords": ["plugin", "model"], "raw_line": "New model claude-sonnet-4-7"}
    patch = rw.generate_patch([item], analyzed)
    assert "claude-sonnet-4-7" in patch and rw.PATCH_FILE.exists()
    assert rw.generate_patch([], analyzed) == ""


def test_renderers_include_products_and_action_items():
    f = findings()
    f["NEW"].append({"version": "v2", "summary": "Added a plugin", "keywords": []})
    cs = state(hardcoded_models=[{"file": "x.py", "model": "claude-sonnet-4"}],
               agent_features={"agents/a.md": {"memory": "user"}},
               hook_events=[{"file": "commands/a.md", "field": "trigger", "value": "stop"}])
    desktop = [{"date": "January 1, 2026"}]
    df = findings()
    df["FIXED"].append({"version": "January 1", "summary": "Fixed item"})
    term = rw.format_terminal([{"tag_name": "v2", "published_at": "2026-01-01"}], f, cs, ["Review"], desktop, df)
    assert "CLAUDE DESKTOP" in term and "Hardcoded models" in term and "Action Items" in term
    markdown = rw.format_markdown([{"tag_name": "v2"}], f, cs, ["Review"], desktop, df)
    assert "Claude Code Changes" in markdown and "Claude Desktop Changes" in markdown and "[ ] Review" in markdown
    data = json.loads(rw.format_json([], findings(), state(), [], desktop, df))
    assert data["latest_version"] == "unknown" and data["desktop"]["entries_checked"] == 1


def test_main_no_results_and_all_output_formats(monkeypatch, capsys):
    monkeypatch.setattr(rw, "check_gh_installed", lambda: None)
    monkeypatch.setattr(rw, "check_gh_auth", lambda: None)
    monkeypatch.setattr(rw, "load_cache", lambda: {})
    monkeypatch.setattr(rw, "fetch_releases", lambda *a, **k: [])
    monkeypatch.setattr(rw, "fetch_changelog", lambda *a, **k: None)
    monkeypatch.setattr(rw, "fetch_desktop_releases", lambda *a, **k: [])
    monkeypatch.setattr(rw.sys, "argv", ["release-watch", "--format", "json"])
    with pytest.raises(SystemExit) as exit_info:
        rw.main()
    assert exit_info.value.code == 0 and json.loads(capsys.readouterr().out)["releases_checked"] == 0

    monkeypatch.setattr(rw, "fetch_releases", lambda *a, **k: [{"tag_name": "v2.0", "body": "Added plugin"}])
    monkeypatch.setattr(rw, "fetch_changelog", lambda *a, **k: "## 2.0.0\n- Added plugin")
    monkeypatch.setattr(rw, "analyze_craft_state", lambda: state())
    for fmt in ("terminal", "json", "markdown"):
        monkeypatch.setattr(rw.sys, "argv", ["release-watch", "--product", "code", "--format", fmt])
        rw.main()
        output = capsys.readouterr().out
        assert output
        if fmt == "json":
            assert json.loads(output)["latest_version"] == "v2.0"
        if fmt == "markdown":
            assert "Release Watch -- Claude Code" in output


def test_main_desktop_autofix_empty_and_review_paths(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(rw, "check_gh_installed", lambda: None)
    monkeypatch.setattr(rw, "check_gh_auth", lambda: None)
    monkeypatch.setattr(rw, "analyze_craft_state", lambda: state())
    monkeypatch.setattr(rw, "fetch_desktop_releases", lambda *a, **k: [{"date": "today", "title": "Breaking change", "body": "Migration"}])
    monkeypatch.setattr(rw, "CACHE_DIR", tmp_path / ".claude")
    monkeypatch.setattr(rw, "PATCH_FILE", tmp_path / ".claude" / "fix.patch")
    monkeypatch.setattr(rw.sys, "argv", ["release-watch", "--product", "desktop", "--auto-fix", "--format", "markdown"])
    rw.main()
    output = capsys.readouterr()
    assert "Claude Desktop Changes" in output.out
    assert "No safe auto-fix items" in output.err

    monkeypatch.setattr(rw, "fetch_releases", lambda *a, **k: [{"tag_name": "v3", "body": "Breaking migration"}])
    monkeypatch.setattr(rw, "fetch_changelog", lambda *a, **k: None)
    monkeypatch.setattr(rw.sys, "argv", ["release-watch", "--product", "code", "--auto-fix", "--format", "json"])
    rw.main()
    output = capsys.readouterr()
    assert "Items requiring manual review" in output.err
