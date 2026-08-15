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
