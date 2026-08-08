#!/usr/bin/env python3
"""Unit tests for utils/repo_triage_classify.py — the repo-triage skill's
issue-triage step (Phase 1 of ORCHESTRATE-repo-triage.md).

The core assertion (GRILL Decision 9 / Acceptance Criterion 2: "Issue
triage reuses classify_issue() directly -- no parallel classifier") is
mechanical, not aspirational: this loads the classify_issue() source both
the way tests/test_issue_check_unit.py does AND the way
utils/repo_triage_classify.py does, and asserts source identity. If
repo-triage ever grows its own copy of the classifier, this test fails.
"""

import re
import sys
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.commands]

REPO_ROOT = Path(__file__).parent.parent
ISSUE_CHECK_MD = REPO_ROOT / "commands" / "git" / "issue-check.md"

sys.path.insert(0, str(REPO_ROOT))

from utils.repo_triage_classify import (  # noqa: E402
    load_classifier,
    load_classifier_source,
    triage_issues,
)


def _reference_extract():
    """Mirror tests/test_issue_check_unit.py's own extraction, independently."""
    text = ISSUE_CHECK_MD.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    return next((b for b in blocks if "def classify_issue" in b), None)


class TestSourceIdentity:
    def test_repo_triage_loader_matches_issue_check_reference(self):
        """repo-triage's loader and issue-check's own test extraction must
        pull byte-identical source -- proves no parallel classifier exists."""
        reference = _reference_extract()
        assert reference is not None
        assert load_classifier_source() == reference

    def test_loaded_classifier_is_callable(self):
        classify_issue = load_classifier()
        assert callable(classify_issue)

    def test_loaded_classifier_matches_documented_verdict_schema(self):
        classify_issue = load_classifier()
        result = classify_issue(
            {
                "number": 1,
                "title": "test",
                "body": "- [ ] do the `/craft:foo:bar` thing",
                "state": "OPEN",
                "updatedAt": "2026-07-14T00:00:00Z",
            },
            set(),
        )
        assert set(result.keys()) == {"status", "evidence", "reasoning"}
        assert result["status"] in ("valid", "moot", "unclear")


class TestTriageIssues:
    def test_skip_and_continue_on_per_issue_failure(self):
        """A classifier exception on one issue must not abort the loop
        (GRILL Decision 14) -- it's recorded in errors and the loop
        continues to the next issue."""

        def flaky_classify(issue, repo_files):
            if issue["number"] == 2:
                raise ValueError("boom")
            return {"status": "valid", "evidence": [{"file": None, "lines": None, "note": "x"}], "reasoning": "ok"}

        issues = [
            {"number": 1, "title": "a", "body": "", "state": "OPEN"},
            {"number": 2, "title": "b", "body": "", "state": "OPEN"},
            {"number": 3, "title": "c", "body": "", "state": "OPEN"},
        ]
        results, errors = triage_issues(issues, set(), flaky_classify)

        assert [r["number"] for r in results] == [1, 3]
        assert len(errors) == 1
        assert errors[0]["number"] == 2
        assert "boom" in errors[0]["error"]

    def test_no_prefilter_all_open_issues_attempted(self):
        """No pre-filter, no concurrency cap (GRILL Decision 10) -- every
        issue passed in gets a classify_issue() call."""
        seen = []

        def counting_classify(issue, repo_files):
            seen.append(issue["number"])
            return {"status": "valid", "evidence": [{"file": None, "lines": None, "note": "x"}], "reasoning": "ok"}

        issues = [{"number": n, "title": str(n), "body": "", "state": "OPEN"} for n in range(1, 11)]
        results, errors = triage_issues(issues, set(), counting_classify)

        assert seen == list(range(1, 11))
        assert len(results) == 10
        assert errors == []
