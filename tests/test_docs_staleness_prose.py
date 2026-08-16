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

Hermetic by construction: no network, no git-history walk, no TTY. Expected
counts are injected via ``CRAFT_EXPECTED_*``, so the fixtures do not have to
materialize 48 command files apiece. Check 1 (release-date consistency) has no
external authority (D1) -- it compares every release-date claim in the repo
against every other one -- so its fixtures need a peer claim to agree or
disagree with; see ``build_repo_multi`` and the ``release date`` tests below.
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
        "clean/release-date-companion.md", "docs/news.md", False,
        "D1 accepted cost: a lone release-date claim has no peer to compare "
        "against, so it is vacuous, not verified",
        id="clean-release-date-single-claim",
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
    pytest.param(
        "falsepos/hyphenated-compound-tldr.md", "docs/architecture.md", False,
        "F1/F2: a hyphenated compound (command-line, agent-facing) must never read as a count",
        id="falsepos-hyphenated-compound",
    ),
    pytest.param(
        "falsepos/tldr-agent-subset-count.md", "docs/migration.md", False,
        "F6: a legitimate small subset count for the smallest count type must clear the floor",
        id="falsepos-agent-subset-count",
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


def build_repo_multi(tmp_path: Path, files: list[tuple[str, str]]) -> Path:
    """Materialize a throwaway repo holding several fixture documents at once.

    Check 1 (release-date consistency, D1) needs at least two real claims to
    exercise at all -- a lone claim is vacuous by design -- so its tests pair
    a fixture against `clean/release-date-companion.md` in one repo, unlike
    every other check here, which is fully exercised by a single document.
    """
    repo = tmp_path / "repo"
    (repo / ".claude-plugin").mkdir(parents=True)
    (repo / ".claude-plugin" / "plugin.json").write_text(
        json.dumps({"name": "craft", "version": FIXTURE_VERSION}) + "\n"
    )
    for fixture, dest in files:
        target = repo / dest
        target.parent.mkdir(parents=True, exist_ok=True)
        shutil.copyfile(FIXTURES / fixture, target)
    return repo


def env_for(repo: Path) -> dict:
    return {
        "PATH": "/usr/bin:/bin:/usr/local/bin:/opt/homebrew/bin",
        "HOME": str(repo),
        "CRAFT_PLUGIN_DIR": str(repo),
        "CRAFT_EXPECTED_CMDS": FIXTURE_COUNTS["CMDS"],
        "CRAFT_EXPECTED_SKILLS": FIXTURE_COUNTS["SKILLS"],
        "CRAFT_EXPECTED_AGENTS": FIXTURE_COUNTS["AGENTS"],
    }


def run_check(repo: Path) -> dict:
    """Run the real script against `repo` and return its parsed JSON report."""
    proc = subprocess.run(
        ["bash", str(SCRIPT), "--json"],
        env=env_for(repo), capture_output=True, text=True, timeout=120,
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


def _call_release_date_helpers(script_body: str) -> str:
    """Source majority_date/compute_release_date_window/release_date_accepted
    out of the real script and run `script_body` against them."""
    preamble = "\n".join(
        f"eval \"$(sed -n '/^{fn}()/,/^}}/p' {SCRIPT})\""
        for fn in ("majority_date", "compute_release_date_window", "release_date_accepted")
    )
    proc = subprocess.run(
        ["bash", "-c", f"{preamble}\n{script_body}"],
        capture_output=True, text=True, timeout=60,
    )
    assert proc.returncode == 0, f"helper script failed:\n{proc.stderr}"
    return proc.stdout


def test_broken_authority_window_is_vacuous_not_universal():
    """A release-date window that failed to compute must reject every claim,
    not accept everything (F7-era regression, re-verified after D1).

    `compute_release_date_window` exits silently on an unparseable date,
    leaving `ACCEPTED_RELEASE_DATES` empty. Nothing in the current design can
    feed it anything but a real `YYYY-MM-DD` (`majority_date` only ever
    returns one of the claim strings, all already validated by the regex that
    collected them) -- this is defense in depth, not a live path -- but the
    guard must still hold: an empty window matches nothing, so a single bad
    input must not silently become "everything is accepted" instead.
    """
    out = _call_release_date_helpers(
        'compute_release_date_window "not-a-date"\n'
        'release_date_accepted "2026-08-07" && echo ACCEPTED || echo REJECTED\n'
    )
    assert out.strip() == "REJECTED", (
        f"a broken window accepted a claim instead of rejecting it: {out!r}"
    )


def test_majority_date_ties_break_to_the_later_date():
    """With claims tied 1-1 (the common case: one NEWS.md entry, one REFCARD.md
    box), the later date must win -- a stale-release-date bug is a forgotten
    update, so the wrong claim is normally older than the correct one, never
    newer. Getting this backwards would make the check flag the correct claim
    and accept the stale one.
    """
    out = _call_release_date_helpers('majority_date "2026-07-19" "2026-08-07"\n')
    assert out.strip() == "2026-08-07"

    out = _call_release_date_helpers('majority_date "2026-08-07" "2026-07-19"\n')
    assert out.strip() == "2026-08-07", "order of arguments must not change the outcome"


def test_majority_date_prefers_the_larger_cluster_over_recency():
    """Two files agreeing beats one newer outlier -- majority by count comes
    first; the later-date tie-break only applies when counts are equal."""
    out = _call_release_date_helpers(
        'majority_date "2026-08-07" "2026-08-07" "2026-09-01"\n'
    )
    assert out.strip() == "2026-08-07"


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


def test_fix_preserves_surrounding_prose(tmp_path):
    """[f]ix on a real shape-scoped finding must swap only the digits (F2/D3).

    Before D3, the fix payload was built from a second, un-anchored regex
    ("N noun" with no trailer) rather than the exact span the detection regex
    matched -- on a hyphenated compound that would have rewritten "30
    command-line" into "48 command-line" (the two regexes disagreed on where
    the match ended). Drives the real interactive `[f]` keystroke through a
    pty and asserts the rest of the line is untouched.
    """
    pexpect = pytest.importorskip("pexpect")

    repo, script = _build_repo_with_own_scripts(
        tmp_path, "defect/structure-table-singular.md", "docs/structure.md"
    )
    target = repo / "docs" / "structure.md"

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
        child.sendline("f")
        child.expect_exact("Fixed")
        child.expect(pexpect.EOF)
    finally:
        child.close()

    lines = target.read_text().splitlines()
    assert "| `agents/` | 2 agent definitions |" in lines, (
        f"fix did not land cleanly -- surrounding prose corrupted:\n{target.read_text()}"
    )


def test_release_date_agrees_across_files(tmp_path):
    """Two independently-correct claims one day apart (the real v4.5.0 case:
    NEWS.md says 2026-08-08, REFCARD-style boxes say 2026-08-07) must not
    disagree with each other (E2, re-verified after D1's redesign)."""
    repo = build_repo_multi(tmp_path, [
        ("clean/release-date-companion.md", "docs/news.md"),
        ("clean/release-date-utc-boundary.md", "docs/other-news.md"),
    ])
    report = run_check(repo)
    findings = report["phases"]["count_consistency"]["findings"]
    assert not findings, f"agreeing claims wrongly flagged:\n{findings}"


def test_release_date_disagreement_flags_the_stale_claim(tmp_path):
    """A release date three weeks off must be caught once it has a peer to
    disagree with -- this is the original REFCARD.md bug the parent SPEC
    exists for, re-verified under D1's cross-file design."""
    repo = build_repo_multi(tmp_path, [
        ("clean/release-date-companion.md", "docs/news.md"),
        ("defect/version-box-stale-date.md", "docs/refcard.md"),
    ])
    report = run_check(repo)
    findings = report["phases"]["count_consistency"]["findings"]
    assert findings, "planted defect went undetected once it had a peer to disagree with"
    assert any(f["file"].startswith("docs/refcard.md") for f in findings), (
        f"finding landed on the wrong file:\n{findings}"
    )
    assert not any(f["file"].startswith("docs/news.md") for f in findings), (
        f"the correct companion claim was flagged instead of the stale one:\n{findings}"
    )


def test_release_date_far_edge_still_caught_cross_file(tmp_path):
    """The window's off-by-one guard (win=5, not 4) must still hold once check
    1 compares claims to each other instead of to a tag."""
    repo = build_repo_multi(tmp_path, [
        ("clean/release-date-companion.md", "docs/news.md"),
        ("defect/release-date-far-edge.md", "docs/news-old.md"),
    ])
    report = run_check(repo)
    findings = report["phases"]["count_consistency"]["findings"]
    assert findings, "the far-edge claim was not collected -- window off-by-one regressed"
    assert any(f["file"].startswith("docs/news-old.md") for f in findings), (
        f"finding landed on the wrong file:\n{findings}"
    )


def test_release_date_prose_mention_does_not_open_window(tmp_path):
    """A version mention in running prose must not open the claim window
    (D6/F3) -- paired against the companion so a wrongly-collected claim would
    have a peer to disagree with and surface as a finding."""
    repo = build_repo_multi(tmp_path, [
        ("clean/release-date-companion.md", "docs/news.md"),
        ("falsepos/release-date-prose-mention.md", "docs/upgrade-guide.md"),
    ])
    report = run_check(repo)
    findings = report["phases"]["count_consistency"]["findings"]
    assert not findings, (
        f"prose mention of the version opened the claim window (D6 regressed):\n{findings}"
    )


def test_both_checks_ship_warning_pending_promotion(tmp_path):
    """D11: check 1 is *designed* to block (D2) but ships `warning` until it
    earns `error` via the evidence gate in Phase 6 -- a clean run across every
    tracked doc and both real claim sites, transcript quoted. Promoting in the
    same change that redesigns the check would mean the only evidence of
    soundness is tests written alongside it by the same author in the same
    sitting, which is not independent evidence. This phase must NOT promote.
    """
    repo = build_repo_multi(tmp_path, [
        ("clean/release-date-companion.md", "docs/news.md"),
        ("defect/version-box-stale-date.md", "docs/refcard.md"),
    ])
    findings = run_check(repo)["phases"]["count_consistency"]["findings"]
    date_findings = [f for f in findings if "release date" in f["message"]]
    assert date_findings, f"expected a release-date finding:\n{findings}"
    assert all(f["severity"] == "warning" for f in date_findings), (
        f"check 1 promoted to error before its Phase 6 evidence gate (D11):\n{date_findings}"
    )

    repo2 = build_repo(tmp_path / "case2", "defect/tldr-eight-agents.md", "docs/skills-agents.md")
    findings2 = run_check(repo2)["phases"]["count_consistency"]["findings"]
    assert findings2, f"expected a count-prose finding:\n{findings2}"
    assert all(f["severity"] == "warning" for f in findings2), (
        f"check 2 finding is not severity warning:\n{findings2}"
    )


def test_phase_status_goes_red_on_any_error_finding():
    """print_phase_status / phase_status_label must coexist with mixed
    severities inside one phase (Phase 4's own acceptance bullet) -- a phase
    with one `error` finding among any number of `warning` findings is RED,
    and an all-`warning` phase is YELLOW. Tested directly against
    phase_status_label rather than through a live check, since neither check
    in Phase 7 emits `error` yet under D11 (see the test above) -- this pins
    the *mechanism* check 1's eventual promotion will rely on.
    """
    preamble = f"eval \"$(sed -n '/^phase_status_label()/,/^}}/p' {SCRIPT})\""

    mixed = 'ARR=("error|a.md||msg|false|" "warning|b.md||msg2|false|")'
    proc = subprocess.run(
        ["bash", "-c", f"{preamble}\n{mixed}\nphase_status_label ARR\n"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.stdout.strip() == "RED", f"mixed severity did not go RED: {proc.stdout!r}"

    warnings_only = 'ARR=("warning|a.md||msg|false|" "warning|b.md||msg2|false|")'
    proc = subprocess.run(
        ["bash", "-c", f"{preamble}\n{warnings_only}\nphase_status_label ARR\n"],
        capture_output=True, text=True, timeout=30,
    )
    assert proc.stdout.strip() == "YELLOW", f"warning-only phase was not YELLOW: {proc.stdout!r}"


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
