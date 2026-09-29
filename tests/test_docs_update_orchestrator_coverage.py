"""Behavior-focused tests for the documentation update orchestrator."""

import sys
from pathlib import Path
from types import ModuleType, SimpleNamespace
from unittest.mock import Mock

import pytest

from utils import docs_update_orchestrator as docs


def result(items=None, **overrides):
    values = {"found": True, "count": len(items or []), "items": items or [], "category": "test", "details": []}
    values.update(overrides)
    return values


def test_detection_flattens_categories_and_badges(tmp_path, monkeypatch):
    detector_module = ModuleType("docs_detector")
    detector_module.DocsDetector = lambda root: SimpleNamespace(
        detect_all=lambda version: {"version_refs": SimpleNamespace(
            category="version_refs", found=True, count=1, items=[{"file": "README.md"}], details=[]
        )}
    )
    validator_module = ModuleType("help_file_validator")
    validator_module.HelpFileValidator = lambda root: object()
    syncer_module = ModuleType("badge_syncer")
    syncer_module.BadgeSyncer = lambda root: SimpleNamespace(sync_badges=lambda **kwargs: [])
    badge_module = ModuleType("badge_detector")
    monkeypatch.setitem(sys.modules, "docs_detector", detector_module)
    monkeypatch.setitem(sys.modules, "help_file_validator", validator_module)
    monkeypatch.setitem(sys.modules, "badge_syncer", syncer_module)
    monkeypatch.setitem(sys.modules, "badge_detector", badge_module)

    orchestrator = docs.DocsUpdateOrchestrator(str(tmp_path), "v9.0.0")
    assert orchestrator.run_detection() == {
        "version_refs": {"category": "version_refs", "found": True, "count": 1,
                          "items": [{"file": "README.md"}], "details": []}
    }


def test_detection_converts_badge_mismatches_and_catches_failures(tmp_path, monkeypatch, capsys):
    mismatch = SimpleNamespace(
        file_path=tmp_path / "README.md", fix_action="Update badge",
        badge_type=SimpleNamespace(value="version"), severity=SimpleNamespace(value="warning"),
    )
    syncer_module = ModuleType("badge_syncer")
    syncer_module.BadgeSyncer = lambda root: SimpleNamespace(sync_badges=lambda **kwargs: [mismatch])
    monkeypatch.setitem(sys.modules, "badge_syncer", syncer_module)
    detector_module = ModuleType("docs_detector")
    detector_module.DocsDetector = lambda root: SimpleNamespace(detect_all=lambda version: {})
    validator_module = ModuleType("help_file_validator")
    validator_module.HelpFileValidator = lambda root: object()
    monkeypatch.setitem(sys.modules, "docs_detector", detector_module)
    monkeypatch.setitem(sys.modules, "help_file_validator", validator_module)
    badge_detector_module = ModuleType("badge_detector")
    badge_detector_module.BadgeDetector = object
    monkeypatch.setitem(sys.modules, "badge_detector", badge_detector_module)

    detected = docs.DocsUpdateOrchestrator(str(tmp_path), "v1").run_detection()
    assert detected["badges"]["items"][0] == {
        "file": "README.md", "issue": "Update badge", "badge_type": "version", "severity": "warning"
    }

    monkeypatch.setitem(sys.modules, "docs_detector", None)
    assert docs.DocsUpdateOrchestrator(str(tmp_path), "v1").run_detection() == {}
    assert "Detection failed" in capsys.readouterr().out


def test_grouping_prompt_preview_and_empty_results(tmp_path):
    orchestrator = docs.DocsUpdateOrchestrator(str(tmp_path), "v1")
    assert orchestrator.group_categories_for_prompts({"empty": result([], found=False)}) == []
    data = {
        key: result([{"file": f"{key}-{i}.md"} for i in range(count)], count=count)
        for key, count in [("version_refs", 4), ("broken_links", 1), ("missing_help", 2),
                           ("stale_examples", 3), ("command_counts", 1), ("missing_xrefs", 1),
                           ("outdated_status", 1), ("inconsistent_terms", 1), ("outdated_diagrams", 1)]
    }
    groups = orchestrator.group_categories_for_prompts(data)
    assert [[key for key, _ in group] for group in groups] == [
        ["version_refs", "command_counts"], ["broken_links", "missing_xrefs"],
        ["missing_help", "outdated_status"], ["stale_examples", "inconsistent_terms", "outdated_diagrams"]
    ]
    one = orchestrator.build_prompt_text([("version_refs", data["version_refs"])])
    assert "4 items" in one and "... and 1 more" in one
    assert "1 item" in orchestrator.build_prompt_text([("x", result([{"description": "one"}], count=1))])
    assert "Multiple documentation updates needed" in orchestrator.build_prompt_text(groups[0])


@pytest.mark.parametrize("category,item,expected", [
    ("version_refs", {"old_version": "1.0", "new_version": "2.0"}, "v2.0"),
    ("command_counts", {"old_count": 3, "new_count": 4}, "4 commands"),
    ("broken_links", {"old_link": "old/path", "new_link": "new/path"}, "new/path"),
    ("outdated_status", {"old_status": "WIP", "new_status": "Done"}, "status: Done"),
    ("inconsistent_terms", {"old_term": "craft", "new_term": "Craft"}, "Craft"),
])
def test_file_update_categories(tmp_path, category, item, expected):
    orchestrator = docs.DocsUpdateOrchestrator(str(tmp_path), "v9.0")
    path = tmp_path / "README.md"
    path.write_text({
        "version_refs": "Release 1.0", "command_counts": "3 commands",
        "broken_links": "old/path", "outdated_status": "status: WIP",
        "inconsistent_terms": "craft",
    }[category])
    payload = {"file": "README.md", **item}
    applied = orchestrator.apply_updates_for_category(category, result([payload]), approved=True)
    assert applied.applied and applied.files_affected == ["README.md"]
    assert expected in path.read_text()


def test_manual_categories_approval_unknown_and_error_paths(tmp_path, monkeypatch):
    orchestrator = docs.DocsUpdateOrchestrator(str(tmp_path), "v1")
    path = tmp_path / "README.md"
    path.write_text("unchanged")
    items = [{"file": "README.md", "command": "run"}]
    assert not orchestrator.apply_updates_for_category("version_refs", result(items), False).applied
    assert not orchestrator.apply_updates_for_category("version_refs", result(items, found=False), True).applied
    help_result = orchestrator.apply_updates_for_category("missing_help", result(items), True)
    assert help_result.changes == ["Review help documentation for: run"]
    xref = orchestrator.apply_updates_for_category("missing_xrefs", result(items), True)
    assert xref.changes == ["Review cross-references in README.md"]
    unknown = orchestrator.apply_updates_for_category("stale_examples", result(items), True)
    assert not unknown.applied and unknown.count == 1
    monkeypatch.setattr(orchestrator, "_apply_version_ref_updates", Mock(side_effect=RuntimeError("write failed")))
    bad = orchestrator.apply_updates_for_category("version_refs", result(items), True)
    assert not bad.applied and bad.count == 0


def test_badges_lint_and_summary(tmp_path, monkeypatch):
    orchestrator = docs.DocsUpdateOrchestrator(str(tmp_path), "v1")
    assert orchestrator._apply_badge_updates([], {}) == (set(), [])
    mismatch = SimpleNamespace(file_path=tmp_path / "README.md", fix_action="Badge fixed")
    syncer_module = ModuleType("badge_syncer")
    syncer_module.BadgeSyncer = lambda root: SimpleNamespace(_apply_updates=lambda items, auto_confirm: [mismatch])
    monkeypatch.setitem(sys.modules, "badge_syncer", syncer_module)
    files, changes = orchestrator._apply_badge_updates([], {"details": [mismatch]})
    assert files == {"README.md"} and changes == ["Badge fixed in README.md"]

    assert orchestrator.run_lint_check(set()) is True
    monkeypatch.setattr(docs.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=0, stdout=""))
    assert orchestrator.run_lint_check({"README.md"}) is True
    monkeypatch.setattr(docs.subprocess, "run", lambda *a, **k: SimpleNamespace(returncode=1, stdout="lint issue"))
    assert orchestrator.run_lint_check({"README.md"}) is False
    monkeypatch.setattr(docs.subprocess, "run", Mock(side_effect=OSError("missing npx")))
    assert orchestrator.run_lint_check({"README.md"}) is True

    summary = orchestrator.generate_summary([
        docs.UpdateResult("version_refs", True, 2, ["README.md"], ["one", "two"]),
        docs.UpdateResult("manual", False, 1, [], ["ignored"]),
    ])
    assert "Categories Updated" in summary and "Files Modified: 1" in summary


def test_main_default_and_interactive_paths(monkeypatch, capsys, tmp_path):
    monkeypatch.setattr(sys, "argv", ["docs:update", "--project-root", str(tmp_path)])
    monkeypatch.setattr(docs.DocsUpdateOrchestrator, "run_detection", lambda self: {})
    assert docs.main() == 0
    assert "No documentation issues" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["docs:update", "--project-root", str(tmp_path)])
    monkeypatch.setattr(docs.DocsUpdateOrchestrator, "run_detection", lambda self: {"version_refs": result([{"file": "README.md"}], count=1)})
    assert docs.main() == 0
    assert "version_refs: 1 items" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["docs:update", "--project-root", str(tmp_path), "--interactive", "--auto-yes"])
    monkeypatch.setattr(docs.DocsUpdateOrchestrator, "run_detection", lambda self: {"version_refs": result([{"file": "README.md", "old_version": "1.0", "new_version": "2.0"}], count=1)})
    (tmp_path / "README.md").write_text("Version 1.0")
    assert docs.main() == 0
    assert "DOCUMENTATION UPDATE COMPLETE" in capsys.readouterr().out

    monkeypatch.setattr(sys, "argv", ["docs:update", "--project-root", str(tmp_path), "--interactive"])
    monkeypatch.setattr("builtins.input", lambda _: "no")
    assert docs.main() == 0
