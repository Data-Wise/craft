#!/usr/bin/env python3
"""Unit tests for the /craft:git:issue-check classification logic.

The classifier lives as a fenced ```python block in
commands/git/issue-check.md (the command file is the single source of
truth). This test extracts that exact block and exercises
classify_issue() directly -- no network, no live gh CLI -- so the
documented logic is provably correct and stays correct.
"""

import sys
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.commands]

REPO_ROOT = Path(__file__).parent.parent
ISSUE_CHECK_MD = REPO_ROOT / "commands" / "git" / "issue-check.md"

sys.path.insert(0, str(REPO_ROOT))
from utils.classifier_loader import extract_classifier_source  # noqa: E402


def _load_classifier():
    """Extract and exec the python block defining classify_issue()."""
    src = extract_classifier_source(ISSUE_CHECK_MD)
    ns: dict = {}
    exec(compile(src, str(ISSUE_CHECK_MD), "exec"), ns)
    return ns


@pytest.fixture(scope="module")
def ns():
    return _load_classifier()


@pytest.fixture(scope="module")
def classify(ns):
    return ns["classify_issue"]


def _issue(body, state="OPEN", number=1, title="test issue"):
    return {"number": number, "title": title, "body": body, "state": state, "updatedAt": "2026-07-14T00:00:00Z"}


class TestVerdictSchema:
    def test_verdict_has_required_keys(self, classify):
        r = classify(_issue("- [ ] do the `/craft:foo:bar` thing"), set())
        assert set(r.keys()) == {"status", "evidence", "reasoning"}
        assert r["status"] in ("valid", "moot", "unclear")
        assert isinstance(r["evidence"], list) and r["evidence"], "evidence must never be empty"
        assert isinstance(r["reasoning"], str) and r["reasoning"].strip()

    def test_evidence_items_are_never_bare(self, classify):
        r = classify(_issue("- [ ] ship `/craft:foo:bar`"), set())
        for item in r["evidence"]:
            assert set(item.keys()) == {"file", "lines", "note"}
            assert item["note"], "every evidence item must cite a note"


class TestClosedIssue:
    def test_closed_issue_is_always_moot(self, classify):
        r = classify(_issue("- [ ] ship `/craft:foo:bar`", state="CLOSED"), set())
        assert r["status"] == "moot"
        assert "closed" in r["evidence"][0]["note"].lower()

    def test_closed_wins_even_with_unmet_missing_criteria(self, classify):
        # Closed short-circuits before any code-search reasoning runs.
        r = classify(_issue("- [ ] ship `/craft:nonexistent:cmd`", state="CLOSED"), set())
        assert r["status"] == "moot"


class TestNoCriteria:
    def test_no_checkboxes_is_unclear(self, classify):
        r = classify(_issue("Just prose, no acceptance criteria at all."), {"commands/foo.md"})
        assert r["status"] == "unclear"
        assert "checkbox" in r["evidence"][0]["note"].lower()


class TestAllChecked:
    def test_all_criteria_checked_is_moot(self, classify):
        body = "- [x] ship `/craft:foo:bar`\n- [x] write docs\n"
        r = classify(_issue(body), {"commands/foo/bar.md"})
        assert r["status"] == "moot"
        assert "2" in r["evidence"][0]["note"]


class TestUnmetCriteria:
    def test_unmet_criterion_citing_missing_command_is_valid(self, classify):
        body = "- [ ] add a craft command (e.g. `/craft:dist:cowork`)\n"
        r = classify(_issue(body), set())  # repo has no such file
        assert r["status"] == "valid"
        assert r["evidence"][0]["file"] == "commands/dist/cowork.md"

    def test_unmet_criterion_citing_existing_command_is_unclear(self, classify):
        body = "- [ ] ship `/craft:git:status`\n"
        r = classify(_issue(body), {"commands/git/status.md"})
        assert r["status"] == "unclear"
        assert r["evidence"][0]["file"] == "commands/git/status.md"

    def test_missing_evidence_wins_over_shipped_evidence(self, classify):
        # Mirrors the real #199 case: one cited command exists elsewhere in
        # prose, another genuinely-cited deliverable does not exist -- the
        # missing one should win (premise still valid).
        body = (
            "- [ ] add `/craft:dist:cowork` (extends `/craft:git:status` machinery)\n"
        )
        r = classify(_issue(body), {"commands/git/status.md"})
        assert r["status"] == "valid"
        paths = {e["file"] for e in r["evidence"]}
        assert "commands/dist/cowork.md" in paths

    def test_unmet_criterion_with_no_command_reference_is_still_valid(self, classify):
        body = "- [ ] fix the thing described in prose, no slash command cited\n"
        r = classify(_issue(body), set())
        assert r["status"] == "valid"
        assert "no citable command reference" in r["evidence"][0]["note"]

    def test_partial_completion_only_unmet_drive_the_verdict(self, classify):
        body = "- [x] already done\n- [ ] add `/craft:dist:cowork`\n"
        r = classify(_issue(body), set())
        assert r["status"] == "valid"
        assert "1 of 2" in r["reasoning"]


class TestRealIssue199Shape:
    """Regression guard for the exact `gh issue view --json` shape used by
    the command (Step 1) and the dogfood test (real #199 snapshot)."""

    def test_matches_gh_issue_view_json_keys(self, classify):
        issue = {
            "number": 199,
            "title": "Overhaul plugin update + Homebrew install path for Cowork / Claude Desktop",
            "body": "- [ ] A craft command (e.g. `/craft:dist:cowork`) ...\n",
            "state": "OPEN",
            "updatedAt": "2026-07-10T19:02:27Z",
        }
        r = classify(issue, set())
        assert r["status"] == "valid"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
