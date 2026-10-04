"""claude_md_sync must not treat a rename note as a live reference to a deleted command.

Regression: CLAUDE.md said "`/craft:finish` renamed from `/craft:done`"; the stale-command
check reported /craft:done as an ERROR and `--fix` (run automatically by /finish Step 1.10)
would have deleted the whole line.
"""
from utils.claude_md_sync import CLAUDEMDSync


def _sync(tmp_path, claude_md, commands):
    (tmp_path / "commands").mkdir()
    for name in commands:
        (tmp_path / "commands" / f"{name}.md").write_text("# cmd\n")
    path = tmp_path / "CLAUDE.md"
    path.write_text(claude_md)
    return CLAUDEMDSync(path, budget=200)


def _stale(sync):
    return {i.message.split()[1] for i in sync._check_command_coverage() if i.category == "stale_command"}


def test_rename_note_is_not_stale(tmp_path):
    s = _sync(tmp_path, "> `/craft:finish` — renamed from `/craft:done` (ADR-006)\n", ["finish"])
    assert _stale(s) == set()


def test_other_history_markers_are_not_stale(tmp_path):
    md = ("`/craft:new` formerly `/craft:old1`\n"
          "`/craft:new` previously `/craft:old2`\n"
          "`/craft:new` replaces `/craft:old3`\n"
          "`/craft:new` supersedes `/craft:old4`\n")
    assert _stale(_sync(tmp_path, md, ["new"])) == set()


def test_genuinely_stale_reference_is_still_flagged(tmp_path):
    # positive control: a live instruction pointing at a deleted command must still be an error
    s = _sync(tmp_path, "Run `/craft:gone` to clean up.\n`/craft:finish` ok\n", ["finish"])
    assert _stale(s) == {"/craft:gone"}


def test_deleted_command_documented_elsewhere_is_still_flagged(tmp_path):
    # mentioned in a rename note AND used as a live instruction -> still stale
    md = "`/craft:finish` renamed from `/craft:done`\nRun `/craft:done` at the end of a session.\n"
    assert _stale(_sync(tmp_path, md, ["finish"])) == {"/craft:done"}


def test_fix_does_not_delete_the_rename_note_line(tmp_path):
    md = "> `/craft:finish` — renamed from `/craft:done` (ADR-006) · other headline text\nline two\n"
    s = _sync(tmp_path, md, ["finish"])
    s.sync(fix=True)
    assert "renamed from `/craft:done`" in (tmp_path / "CLAUDE.md").read_text()
