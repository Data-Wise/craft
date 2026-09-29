from pathlib import Path
import runpy
import sys

from utils.claude_md_sync import CLAUDEMDSync, Issue, Severity, SyncResult
from utils.claude_md_detector import ProjectInfo


def test_sync_budget_metrics_and_fix_routes(tmp_path):
    path = tmp_path / "CLAUDE.md"
    path.write_text("**Current Version:** v1.0\n**2 commands** **3 skills** **4 agents**\n**Tests:** 5\n**Documentation Status:** 10%\n/craft:old\n[bad](missing.md)\n**Progress:** 10%\n")
    (tmp_path / ".STATUS").write_text("progress: 20%\n")
    sync = CLAUDEMDSync(path, budget=2)
    info = ProjectInfo(name="demo", type="craft-plugin", version="2.0", version_source="package.json", commands=["a"], skills=[], agents=[], test_count=7, structure={})
    changes = sync._update_metrics(info)
    assert {c.name for c in changes} == {"Version", "Commands", "Skills", "Agents", "Tests", "Documentation"}
    sync._apply_metric_changes(changes)
    assert "v2.0" in path.read_text() and "**1 commands**" in path.read_text()
    assert sync._update_metrics(None) == []
    report_result = SyncResult(project_info=info, metric_changes=changes,
        issues=[Issue(Severity.ERROR, "bad", "error"), Issue(Severity.WARNING, "bad", "warn"), Issue(Severity.INFO, "bad", "info")],
        fix_results=[], line_count=30, budget=2)
    report = sync.generate_report(report_result)
    assert "Errors (1)" in report and "Warnings (1)" in report and "Info (1)" in report
    unknown = Issue(Severity.WARNING, "x", "unknown", fixable=True, fix_method="unknown")
    assert not sync._apply_fix(unknown, dry_run=True).success
    assert sync._check_version_sync(None) == []
    assert sync._check_required_sections(None) == []


def test_sync_audit_and_fix_helpers(tmp_path):
    path = tmp_path / "CLAUDE.md"
    path.write_text("**Current Version:** v1.0\n\n### v1.0\nReleased 2020\nFiles Changed: 2 +3/-1\n")
    (tmp_path / ".STATUS").write_text("progress: 99%\n")
    sync = CLAUDEMDSync(path)
    patterns = sync.detect_anti_patterns()
    assert patterns and all("line_number" in item for item in patterns)
    assert sync._check_docs_percent() is None
    assert sync._check_broken_links() == []
    assert sync._fix_stale_command(Issue(Severity.ERROR, "x", "bad"), True).success is False
    assert sync._fix_broken_link(Issue(Severity.ERROR, "x", "bad"), True).success is False
    assert sync._fix_status_sync(Issue(Severity.ERROR, "x", "bad"), True).success is False
    scoped = sync._filter_issues_by_scope([Issue(Severity.ERROR, "x", "e"), Issue(Severity.WARNING, "x", "w" )], "warnings")
    assert [issue.severity for issue in scoped] == [Severity.ERROR, Severity.WARNING]


def test_sync_cli_modes(tmp_path, monkeypatch, capsys):
    path = tmp_path / "CLAUDE.md"
    path.write_text("# Demo\n\nUse /craft:deleted here.\n")
    for flags, expected_code in [(["--dry-run"], 0), (["--strict"], 1)]:
        monkeypatch.setattr(sys, "argv", ["claude_md_sync.py", str(path), *flags])
        try:
            runpy.run_module("utils.claude_md_sync", run_name="__main__")
        except SystemExit as exc:
            assert exc.code == expected_code
        assert "Sync Report" in capsys.readouterr().out
    monkeypatch.setattr(sys, "argv", ["claude_md_sync.py", str(tmp_path), "--generate-reference"])
    try:
        runpy.run_module("utils.claude_md_sync", run_name="__main__")
    except SystemExit as exc:
        assert exc.code == 0
    assert "reference" in capsys.readouterr().out.lower()
