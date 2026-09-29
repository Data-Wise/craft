import json
import runpy
import sys
from pathlib import Path

from utils.claude_md_optimizer import (
    CLAUDEMDOptimizer, analyze_claude_md, optimize_claude_md,
)


def test_budget_config_priority_and_fallbacks(tmp_path):
    path = tmp_path / "CLAUDE.md"
    path.write_text("# Project\n")
    config = tmp_path / ".claude-plugin" / "config.json"
    config.parent.mkdir()
    config.write_text('{"claude_md_budget": "42"}')
    (tmp_path / "package.json").write_text('{"claudeMd": {"budget": 20}}')
    assert CLAUDEMDOptimizer(path).budget == 42
    config.write_text("{")
    assert CLAUDEMDOptimizer(path).budget == 20
    (tmp_path / "package.json").write_text('{"claudeMd": {"budget": "bad"}}')
    assert CLAUDEMDOptimizer(path).budget == 150


def test_classification_and_section_parsing(tmp_path):
    optimizer = CLAUDEMDOptimizer(tmp_path / "CLAUDE.md", budget=10)
    assert optimizer.analyze() == []
    sections = optimizer.analyze(["intro", "", "## Overview", "one", "## Release History", "two"])
    assert [section.name for section in sections] == ["header", "Overview", "Release History"]
    assert optimizer._classify_section("Project Structure") == ("P0", 15)
    assert optimizer._classify_section("Installation") == ("P1", 20)
    assert optimizer._classify_section("Release History") == ("P2", 0)
    assert optimizer._default_target_for_section("Implementation Phase") is None
    assert optimizer._default_target_for_section("Test Suite")


def test_detail_file_creation_append_pointer_and_report(tmp_path):
    optimizer = CLAUDEMDOptimizer(tmp_path / "CLAUDE.md", budget=100)
    assert optimizer.move_to_detail_file("old", "docs/detail.md", "History")
    assert not optimizer.move_to_detail_file("new", "docs/detail.md", "More")
    assert "## More" in (tmp_path / "docs/detail.md").read_text()
    assert optimizer.generate_pointer("docs/detail.md", "**recent** `history`").startswith("-> Recent history:")
    result = optimizer.optimize(dry_run=True)
    report = optimizer.generate_report(result)
    assert "WITHIN BUDGET" in report and "No optimization needed" in report
    assert "No sections found" in optimizer.get_section_breakdown()


def test_optimize_moves_p2_and_saves_backup(tmp_path):
    path = tmp_path / "CLAUDE.md"
    path.write_text("# Project\n\n## Overview\nShort\n\n## Release History\n- v1\n- v2\n")
    result = optimize_claude_md(path, budget=100)
    assert result.actions
    assert (tmp_path / ".CLAUDE.md.backup").exists()
    assert "VERSION-HISTORY.md" in path.read_text()
    assert "WITHIN BUDGET" in CLAUDEMDOptimizer(path).generate_report(result)


def test_optimize_collapses_p1_and_deletes_phase_without_target(tmp_path):
    path = tmp_path / "CLAUDE.md"
    path.write_text("# Project\n\n## Overview\nkeep\n\n## Implementation Phase Details\nphase data\n\n## Installation\n" + "line\n" * 12)
    optimizer = CLAUDEMDOptimizer(path, budget=5)
    result = optimizer.optimize()
    assert any(a.action == "collapse" for a in result.actions)
    assert result.after_lines <= result.before_lines
    assert "OVER BUDGET" in optimizer.generate_report(result) or result.within_budget
    assert len(optimizer._collapse_blank_lines(["a", "", "", "", "b", "", ""])) == 5


def test_pattern_bloat_dry_run_and_wrappers(tmp_path, monkeypatch):
    path = tmp_path / "CLAUDE.md"
    path.write_text("# Project\n\n## Overview\nShort\n\n## Release Notes\n- v1.0.0 - Released\n")
    assert analyze_claude_md(path)
    result = optimize_claude_md(path, budget=200, dry_run=True)
    assert result.actions
    assert not (tmp_path / ".CLAUDE.md.backup").exists()
    optimizer = CLAUDEMDOptimizer(path, budget=1)
    assert "OVER" in optimizer.get_section_breakdown()


def test_budget_json_valid_but_missing_key(tmp_path):
    path = tmp_path / "CLAUDE.md"
    path.write_text("x")
    config = tmp_path / ".claude-plugin" / "config.json"
    config.parent.mkdir()
    config.write_text(json.dumps({"other": 1}))
    assert CLAUDEMDOptimizer(path).budget == 150


def test_optimizer_cli_modes_and_errors(tmp_path, monkeypatch, capsys):
    path = tmp_path / "CLAUDE.md"
    path.write_text("# Demo\n\n## Project Structure\nshort\n")
    for flags, expected in [(["--breakdown"], "Section"), (["--analyze"], "CLAUDE.md Analysis"), (["--dry-run"], "Dry run")]:
        monkeypatch.setattr(sys, "argv", ["claude_md_optimizer.py", str(path), *flags])
        try:
            runpy.run_module("utils.claude_md_optimizer", run_name="__main__")
        except SystemExit as exc:
            assert exc.code == 0
        assert expected in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["claude_md_optimizer.py", str(tmp_path / "missing.md")])
    try:
        runpy.run_module("utils.claude_md_optimizer", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 1
    assert "not found" in capsys.readouterr().out


def test_optimizer_strict_exit_when_still_over_budget(tmp_path, monkeypatch, capsys):
    path = tmp_path / "CLAUDE.md"
    path.write_text("# Demo\n\n## Overview\n" + "detail\n" * 30)
    monkeypatch.setattr(sys, "argv", ["claude_md_optimizer.py", str(path), "--strict", "--budget", "1", "--dry-run"])
    try:
        runpy.run_module("utils.claude_md_optimizer", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 1
    assert "OVER BUDGET" in capsys.readouterr().out
