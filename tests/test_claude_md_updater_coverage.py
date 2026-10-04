"""Focused coverage for the CLAUDE.md updater's detection and apply paths."""

from types import SimpleNamespace


from utils.claude_md_updater import (
    CLAUDEMDUpdater,
    Change,
    ChangeType,
    UpdatePlan,
    update_claude_md,
)


def project_info(**overrides):
    values = {
        "name": "Example",
        "type": "craft-plugin",
        "version": "2.0.0",
        "version_source": "plugin.json",
        "commands": {"docs/update.md", "new.md"},
        "test_count": 20,
    }
    values.update(overrides)
    return SimpleNamespace(**values)


def make_updater(tmp_path, content=None, info=None):
    path = tmp_path / "CLAUDE.md"
    path.write_text(content if content is not None else (
        "**Current Version:** v1.0.0\n"
        "**Tests:** 10\n"
        "**Documentation Status:** 50%\n"
        "## Quick Commands\n"
        "| `/craft:docs:update` | Update docs |\n"
        "| `/craft:old` | Old command |\n"
        "## Other\n"
    ))
    return CLAUDEMDUpdater(path, info or project_info())


def test_detects_version_command_test_and_status_changes(tmp_path):
    updater = make_updater(tmp_path)
    (tmp_path / ".STATUS").write_text("progress: 80\n")

    plan = updater.detect_changes()

    assert {change.type for change in plan.changes} == {
        ChangeType.VERSION_MISMATCH,
        ChangeType.NEW_COMMAND,
        ChangeType.REMOVED_COMMAND,
        ChangeType.TEST_COUNT,
        ChangeType.DOCS_PERCENT,
    }
    assert plan.total_line_delta == 0
    assert plan.sections_affected == ["Project Status", "Quick Commands", "Testing"]
    assert "command_add: 1 change(s)" in plan.change_summary


def test_detection_handles_non_plugin_synced_and_missing_metadata(tmp_path):
    content = "## Quick Commands\n| `/craft:old` | old |\n"
    updater = make_updater(tmp_path, content, project_info(type="project"))
    assert updater.detect_changes().changes == []
    assert updater._detect_version_mismatch() is None
    assert updater._detect_test_count_change() == []
    assert updater._detect_status_changes() is None
    assert updater._detect_skill_changes() == []
    assert updater._detect_agent_changes() == []


def test_extract_documented_commands_stops_at_next_section(tmp_path):
    updater = make_updater(tmp_path, """## Quick Commands
| `/craft:docs:update` | Update |
| `/craft:docs:check` | Check |
## Other
| `/craft:ignored` | Ignored |
""")
    assert updater._extract_documented_commands() == {"docs/update.md", "docs/check.md"}


def test_apply_changes_dry_run_then_persist(tmp_path):
    updater = make_updater(tmp_path)
    (tmp_path / ".STATUS").write_text("progress: 80\n")
    plan = updater.detect_changes()
    original = updater.path.read_text()

    preview = updater.apply_changes(plan, dry_run=True)
    assert "v2.0.0" in preview and "**Tests:** 20" in preview
    assert updater.path.read_text() == original

    written = updater.apply_changes(plan)
    assert updater.path.read_text() == written
    assert "**Documentation Status:** 80%" in written
    assert "/craft:new" not in written  # New commands need a human description.


def test_preview_and_summary_cover_empty_and_populated_plans(tmp_path):
    updater = make_updater(tmp_path)
    empty = UpdatePlan([], 0, [])
    assert not empty.has_changes
    assert updater.apply_changes(empty) == updater.content
    assert updater.generate_preview(empty) == "No changes detected."
    assert updater.generate_summary(empty, applied=False) == "No changes applied (dry-run mode)."

    change = Change(ChangeType.NEW_COMMAND, "New command", "old", "row", auto_fixable=False)
    plan = UpdatePlan([change], 1, ["Quick Commands"])
    preview = updater.generate_preview(plan)
    assert "New command" in preview and "⚠️" in preview
    assert "No changes applied" in updater.generate_summary(plan, applied=False)
    summary = updater.generate_summary(plan)
    assert "Sections: 1 affected" in summary
    assert "New command" not in summary  # Manual changes are not claimed as applied.


def test_single_change_replacements_and_unknown_change(tmp_path):
    updater = make_updater(tmp_path)
    content = "**Current Version:** v1.0.0\n**Tests:** 10\n**Documentation Status:** 50%\n"
    cases = [
        (ChangeType.VERSION_MISMATCH, "2.0.0", "**Current Version:** v2.0.0"),
        (ChangeType.TEST_COUNT, "20", "**Tests:** 20"),
        (ChangeType.DOCS_PERCENT, "80%", "Status:** 80%"),
    ]
    for change_type, after, expected in cases:
        result = updater._apply_single_change(content, Change(change_type, "", "", after))
        assert expected in result
    removed = updater._apply_single_change(content, Change(ChangeType.REMOVED_COMMAND, "", "", ""))
    assert removed == content


def test_update_convenience_function_reports_missing_unknown_dry_run_and_apply(tmp_path, monkeypatch):
    assert update_claude_md(tmp_path)[1].startswith("CLAUDE.md not found")
    claude_path = tmp_path / "CLAUDE.md"
    claude_path.write_text("**Current Version:** v1.0.0\n")

    import utils.claude_md_detector as detector
    monkeypatch.setattr(detector, "detect_project", lambda _: None)
    assert update_claude_md(tmp_path)[1] == "Could not detect project type."

    monkeypatch.setattr(detector, "detect_project", lambda _: project_info(type="project", version="1.0.0"))
    plan, message = update_claude_md(tmp_path)
    assert not plan.has_changes and "up to date" in message

    monkeypatch.setattr(detector, "detect_project", lambda _: project_info())
    plan, message = update_claude_md(tmp_path, dry_run=True)
    assert plan.has_changes and message.startswith("DRY RUN MODE")
    assert "v1.0.0" in claude_path.read_text()

    plan, message = update_claude_md(tmp_path)
    assert plan.has_changes and "CLAUDE.MD UPDATED" in message
    assert "v2.0.0" in claude_path.read_text()
