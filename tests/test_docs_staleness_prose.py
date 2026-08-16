"""Table-driven harness for the prose-staleness checks in docs-staleness-check.sh.

Implements SPEC-doc-staleness-prose-gaps-2026-08-07's "Test Harness" section.

Each row runs the real script against a throwaway repo containing exactly one
fixture document, and asserts on the structured ``count_consistency`` findings
from ``--json`` rather than parsing colored terminal output.

Three fixture classes, and the harness is only meaningful with all three:

* ``clean/``   — correct content must stay GREEN (no false positive)
* ``defect/``  — planted defect must go RED (positive control; a check shipped
                 without one of these is a rejected change)
* ``falsepos/``— content that LOOKS like a stale count but is not, drawn from
                 real pages an earlier build of these checks wrongly flagged

Hermetic by construction: no network, no git-history walk, no TTY. The one git
read check 1 needs (the version's tag date) is injected via ``CRAFT_RELEASE_DATE``,
and the expected counts via ``CRAFT_EXPECTED_*``, so the fixtures do not have to
materialize 48 command files apiece.
"""

from __future__ import annotations

import json
import shutil
import subprocess
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parent.parent
SCRIPT = REPO_ROOT / "scripts" / "docs-staleness-check.sh"
FIXTURES = Path(__file__).resolve().parent / "fixtures" / "prose-staleness"

# The authority values every fixture is written against. Kept here, not derived
# from the live repo, so a future count change cannot silently invalidate a
# planted defect (e.g. an "8 agents" defect stops being a defect the day craft
# actually ships 8 agents).
FIXTURE_VERSION = "4.5.0"
FIXTURE_TAG_DATE = "2026-08-07"
FIXTURE_COUNTS = {"CMDS": "48", "SKILLS": "41", "AGENTS": "2"}

# (fixture, destination path inside the throwaway repo, expect_finding, proves)
#
# Destination matters: `mode-limit-prose` must land on its real path because the
# exclusion that saves it in production is path-keyed.
CASES = [
    pytest.param(
        "clean/version-box-correct.md", "docs/refcard.md", False,
        "correct date + counts in a version box",
        id="clean-version-box",
    ),
    pytest.param(
        "clean/tldr-correct.md", "docs/skills-agents.md", False,
        "correct counts in a TL;DR line",
        id="clean-tldr",
    ),
    pytest.param(
        "clean/structure-table-correct.md", "docs/structure.md", False,
        "E1 stays fixed: correct singular count in a structure-table row",
        id="clean-structure-table",
    ),
    pytest.param(
        "clean/release-date-utc-boundary.md", "docs/news.md", False,
        "E2: a one-day gap is the UTC boundary, not staleness",
        id="clean-utc-boundary",
    ),
    pytest.param(
        "defect/version-box-stale-date.md", "docs/refcard.md", True,
        "check 1 catches a release date well off the tag",
        id="defect-stale-date",
    ),
    pytest.param(
        "defect/release-date-far-edge.md", "docs/news.md", True,
        "check 1 reaches the last line its window documents (off-by-one guard)",
        id="defect-release-date-far-edge",
    ),
    pytest.param(
        "defect/tldr-eight-agents.md", "docs/skills-agents.md", True,
        "check 2 catches the original review bug",
        id="defect-tldr-eight-agents",
    ),
    pytest.param(
        "defect/structure-table-singular.md", "docs/structure.md", True,
        "E1 would now be caught: singular noun form in a structure-table row",
        id="defect-structure-table-singular",
    ),
    pytest.param(
        "falsepos/category-subtotal-box.md", "docs/playground.md", False,
        "category subtotals inside a box are not the grand total",
        id="falsepos-category-subtotal",
    ),
    pytest.param(
        "falsepos/subset-bold-count.md", "docs/help/refine-flag.md", False,
        "a bolded count can describe a subset or another plugin",
        id="falsepos-subset-bold-count",
    ),
    pytest.param(
        "falsepos/mode-limit-prose.md", "docs/guide/orch-flag-usage.md", False,
        "mode-limit prose is free prose and stays exclusion-covered",
        id="falsepos-mode-limit-prose",
    ),
    pytest.param(
        "falsepos/tldr-mentioned-not-claimed.md", "docs/adr/ADR-00N-example.md", False,
        "a doc describing a TL;DR bug is not itself making a TL;DR claim",
        id="falsepos-tldr-mentioned",
    ),
]


def build_repo(tmp_path: Path, fixture: str, dest: str) -> Path:
    """Materialize a throwaway repo holding exactly one fixture document."""
    repo = tmp_path / "repo"
    (repo / ".claude-plugin").mkdir(parents=True)
    (repo / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "craft", "version": FIXTURE_VERSION}) + "\n"
    )
    target = repo / dest
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copyfile(FIXTURES / fixture, target)
    return repo


def run_check(repo: Path) -> dict:
    """Run the real script against `repo` and return its parsed JSON report."""
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
        "HOME": str(repo),
        "CRAFT_PLUGIN_DIR": str(repo),
        "CRAFT_RELEASE_DATE": FIXTURE_TAG_DATE,
        "CRAFT_EXPECTED_CMDS": FIXTURE_COUNTS["CMDS"],
        "CRAFT_EXPECTED_SKILLS": FIXTURE_COUNTS["SKILLS"],
        "CRAFT_EXPECTED_AGENTS": FIXTURE_COUNTS["AGENTS"],
    }
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--json"],
        env=env, capture_output=True, text=True, timeout=120,
    )
    assert proc.stdout.strip(), f"no JSON emitted; stderr:\n{proc.stderr}"
    return json.loads(proc.stdout)


@pytest.mark.parametrize("fixture,dest,expect_finding,proves", CASES)
def test_prose_staleness_fixture(tmp_path, fixture, dest, expect_finding, proves):
    report = run_check(build_repo(tmp_path, fixture, dest))
    findings = report["phases"]["count_consistency"]["findings"]

    rendered = "\n".join(f"  {f['file']}: {f['message']}" for f in findings) or "  (none)"

    if expect_finding:
        assert findings, (
            f"planted defect went undetected — {proves}\n"
            f"fixture: {fixture} -> {dest}\nfindings:\n{rendered}"
        )
    else:
        assert not findings, (
            f"false positive on content that is correct — {proves}\n"
            f"fixture: {fixture} -> {dest}\nfindings:\n{rendered}"
        )


def test_unparseable_authority_date_is_vacuous_not_universal(tmp_path):
    """A broken release-date authority must skip the check, not flag everything.

    Found in review of PR #334. `compute_release_date_window` exits silently on
    an unparseable date, leaving an empty accept-window — and an empty window
    matches nothing, so every release-date claim in the repo failed at once. One
    bad input became a repo-wide false-positive storm. The guard is that the
    check is vacuous unless the authority actually parsed.

    Uses the `clean/` fixture on purpose: it is correct against a real tag date,
    so any finding here is caused by the broken authority alone.
    """
    repo = build_repo(tmp_path, "clean/release-date-utc-boundary.md", "docs/news.md")
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
        "HOME": str(repo),
        "CRAFT_PLUGIN_DIR": str(repo),
        "CRAFT_RELEASE_DATE": "not-a-date",
        "CRAFT_EXPECTED_CMDS": FIXTURE_COUNTS["CMDS"],
        "CRAFT_EXPECTED_SKILLS": FIXTURE_COUNTS["SKILLS"],
        "CRAFT_EXPECTED_AGENTS": FIXTURE_COUNTS["AGENTS"],
    }
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--json"],
        env=env, capture_output=True, text=True, timeout=120,
    )
    findings = json.loads(proc.stdout)["phases"]["count_consistency"]["findings"]
    rendered = "\n".join(f"  {f['file']}: {f['message']}" for f in findings)
    assert not findings, (
        f"unparseable authority date produced findings instead of skipping:\n{rendered}"
    )


def _call_apply_line_fix(path: Path, lineno: int, fix_detail: str) -> str:
    """Source apply_line_fix out of the real script and call it directly."""
    script = (
        f"eval \"$(sed -n '/^apply_line_fix()/,/^}}/p' {SCRIPT})\"\n"
        f"apply_line_fix {path} {lineno} {json.dumps(fix_detail)}\n"
    )
    proc = subprocess.run(["bash", "-c", script], capture_output=True, text=True, timeout=60)
    return proc.stdout.strip()


def test_apply_line_fix_edits_the_file_and_reports_truthfully(tmp_path):
    """The shared applier must change the file when it says it did.

    pass 2's [f]ix branch printed "Fixed" and incremented TOTAL_FIXED without
    touching anything — the same reports-success-changes-nothing bug pass 1 had
    already been fixed for. Both now route through apply_line_fix, so this is
    the one place that contract is pinned.
    """
    doc = tmp_path / "structure.md"
    doc.write_text("intro\n| `agents/` | 8 agent definitions |\noutro\n")

    assert _call_apply_line_fix(doc, 2, "s/8 agent/2 agent/") == "true"
    assert doc.read_text().splitlines()[1] == "| `agents/` | 2 agent definitions |"


def test_apply_line_fix_returns_false_without_changing_anything(tmp_path):
    """False must mean untouched, for every way a fix can fail to apply."""
    doc = tmp_path / "structure.md"
    original = "intro\n| `agents/` | 2 agent definitions |\noutro\n"
    doc.write_text(original)

    # Phase 8 emits this marker rather than a substitution — must not be run.
    assert _call_apply_line_fix(doc, 2, "doc-coverage:refcard:craft:do") == "false"
    # Pattern that matches nothing on that line.
    assert _call_apply_line_fix(doc, 2, "s/9 agent/2 agent/") == "false"
    # Line number past the end of the file.
    assert _call_apply_line_fix(doc, 99, "s/2 agent/3 agent/") == "false"

    assert doc.read_text() == original, "a false result still modified the file"


def test_every_check_has_a_planted_defect():
    """A check without a defect fixture is a rejected change (SPEC harness rule).

    Guards the harness itself: it is the one assertion that fails if someone
    adds a check and only ever tests the happy path.
    """
    defects = {p.name for p in (FIXTURES / "defect").glob("*.md")}
    assert "version-box-stale-date.md" in defects, "check 1 lost its positive control"
    assert {"tldr-eight-agents.md", "structure-table-singular.md"} <= defects, (
        "check 2 lost a positive control"
    )


def _build_repo_with_own_scripts(tmp_path: Path, fixture: str, dest: str) -> tuple[Path, Path]:
    """Like build_repo, but copies scripts/ alongside so EXCLUSIONS_FILE (which
    is resolved relative to the running script's own directory) lands inside
    the throwaway tree instead of this repo's real
    scripts/config/exclusions.txt. Returns (repo, script_copy).
    """
    repo = build_repo(tmp_path, fixture, dest)
    scripts_copy = repo / "scripts"
    shutil.copytree(REPO_ROOT / "scripts", scripts_copy)
    return repo, scripts_copy / "docs-staleness-check.sh"


def _run_check(script: Path, repo: Path) -> dict:
    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
        "HOME": str(repo),
        "CRAFT_PLUGIN_DIR": str(repo),
        "CRAFT_RELEASE_DATE": FIXTURE_TAG_DATE,
        "CRAFT_EXPECTED_CMDS": FIXTURE_COUNTS["CMDS"],
        "CRAFT_EXPECTED_SKILLS": FIXTURE_COUNTS["SKILLS"],
        "CRAFT_EXPECTED_AGENTS": FIXTURE_COUNTS["AGENTS"],
    }
    proc = subprocess.run(
        ["bash", str(script), "--json"], env=env, capture_output=True, text=True, timeout=120,
    )
    assert proc.stdout.strip(), f"no JSON emitted; stderr:\n{proc.stderr}"
    return json.loads(proc.stdout)


def test_exclude_round_trips_end_to_end(tmp_path):
    """[e]xclude must actually suppress the finding on the next run (F4/D4).

    Before D4, `file` was `path:lineno` glued into one field, so the entry
    pass 2 wrote (`path:lineno:pattern`) could never match
    `is_pattern_excluded`'s `path:pattern` parse — it printed "Excluded" and
    the finding came back on the next run.

    Drives the REAL interactive `[e]` keystroke through a pty (pexpect),
    not a reimplementation of pass 2's write logic in Python — a hand-copy
    of the same bug pass 2 had would pass either way and prove nothing.
    """
    pexpect = pytest.importorskip("pexpect")

    # structure-table-singular, not tldr-eight-agents: its noun ("8 agent")
    # matches exactly what the check-time exclusion lookup passes
    # (`${found} ${singular}`). tldr's noun ("8 specialized agents") does not
    # — a separate, pre-existing exclusion-matching gap unrelated to D4 — and
    # would make this test fail for a reason this phase does not fix.
    repo, script = _build_repo_with_own_scripts(
        tmp_path, "defect/structure-table-singular.md", "docs/structure.md"
    )

    before = _run_check(script, repo)
    findings = before["phases"]["count_consistency"]["findings"]
    assert findings, "fixture did not produce the finding this test excludes"

    env = {
        "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
        "HOME": str(repo),
        "CRAFT_PLUGIN_DIR": str(repo),
        "CRAFT_RELEASE_DATE": FIXTURE_TAG_DATE,
        "CRAFT_EXPECTED_CMDS": FIXTURE_COUNTS["CMDS"],
        "CRAFT_EXPECTED_SKILLS": FIXTURE_COUNTS["SKILLS"],
        "CRAFT_EXPECTED_AGENTS": FIXTURE_COUNTS["AGENTS"],
    }
    child = pexpect.spawn("bash", [str(script), "--fix"], env=env, cwd=str(repo), timeout=30)
    try:
        child.expect_exact("[f]ix  [s]kip  [e]xclude permanently:")
        child.sendline("e")
        child.expect_exact("Excluded")
        child.expect(pexpect.EOF)
    finally:
        child.close()

    exclusions_file = script.parent / "config" / "exclusions.txt"
    assert exclusions_file.exists(), "no exclusions.txt was written"
    written = exclusions_file.read_text()
    assert "docs/structure.md:8 agent" in written, (
        f"exclusions.txt does not carry the expected pattern:\n{written}"
    )

    after = _run_check(script, repo)
    after_findings = after["phases"]["count_consistency"]["findings"]
    assert not after_findings, (
        f"[e]xclude did not suppress the finding on the next run — "
        f"round-trip broken. exclusions.txt:\n{written}\nfindings:\n{after_findings}"
    )


def test_live_repo_stays_green_on_count_consistency():
    """The checks must not fire on craft's own already-corrected docs.

    SPEC acceptance criterion: running against current HEAD stays GREEN. This is
    the assertion that would have caught the first build of check 2, which
    flagged five legitimate subset counts before the 40%-of-expected floor.
    """
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--json"],
        cwd=REPO_ROOT, capture_output=True, text=True, timeout=180,
    )
    report = json.loads(proc.stdout)
    findings = report["phases"]["count_consistency"]["findings"]
    rendered = "\n".join(f"  {f['file']}: {f['message']}" for f in findings)
    assert not findings, f"count_consistency regressed on the live repo:\n{rendered}"
