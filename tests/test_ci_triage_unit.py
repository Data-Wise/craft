#!/usr/bin/env python3
"""Unit tests for the /craft:ci:triage classification logic.

The classifier lives as a fenced ```python block in commands/ci/triage.md (the
command file is the single source of truth). This test extracts that exact block
and exercises classify_failure() directly — no network, no live gh CLI — so the
documented logic is provably correct and stays correct.
"""

import re
from pathlib import Path

import pytest

pytestmark = [pytest.mark.unit, pytest.mark.commands]

TRIAGE_MD = Path(__file__).parent.parent / "commands" / "ci" / "triage.md"


def _load_classifier():
    """Extract and exec the python block defining classify_failure()."""
    text = TRIAGE_MD.read_text(encoding="utf-8")
    blocks = re.findall(r"```python\n(.*?)```", text, re.DOTALL)
    src = next((b for b in blocks if "def classify_failure" in b), None)
    assert src is not None, "classify_failure block not found in commands/ci/triage.md"
    ns: dict = {}
    exec(compile(src, str(TRIAGE_MD), "exec"), ns)
    return ns


@pytest.fixture(scope="module")
def ns():
    return _load_classifier()


@pytest.fixture(scope="module")
def classify(ns):
    return ns["classify_failure"]


class TestClassificationLogic:
    def test_file_in_diff_is_diff_caused(self, classify):
        r = classify(["scripts/foo.sh:12: syntax error"], {"scripts/foo.sh"})
        assert r["class"] == "DIFF-CAUSED"
        assert r["confidence"] == "HIGH"
        assert "scripts/foo.sh:12" in r["evidence"]

    def test_file_not_in_diff_is_pre_existing(self, classify):
        r = classify(["tests/test_old.py:99: AssertionError"], {"scripts/foo.sh"})
        assert r["class"] == "PRE-EXISTING"
        assert r["confidence"] == "HIGH"

    def test_infra_marker_no_files_is_infra_flake(self, classify):
        r = classify(["remote: rate limit exceeded, try again later"], set())
        assert r["class"] == "INFRA-FLAKE"
        assert r["confidence"] == "LOW"

    def test_mixed_sites_is_partial(self, classify):
        r = classify(
            ["scripts/foo.sh:1: bad", "tests/test_old.py:2: bad"],
            {"scripts/foo.sh"},
        )
        assert r["class"] == "PARTIAL"

    def test_empty_log_is_infra_flake_low(self, classify):
        r = classify([], {"scripts/foo.sh"})
        assert r["class"] == "INFRA-FLAKE"
        assert r["confidence"] == "LOW"

    def test_workflow_yaml_not_in_diff_is_pre_existing(self, classify):
        # .github/workflows/ci.yml exists in repo but is rarely in a feature diff.
        r = classify([".github/workflows/ci.yml:30: error in step"], {"scripts/foo.sh"})
        assert r["class"] == "PRE-EXISTING"

    def test_ansi_codes_are_stripped_before_matching(self, classify):
        r = classify(["\x1b[31mscripts/foo.sh:7:\x1b[0m boom"], {"scripts/foo.sh"})
        assert r["class"] == "DIFF-CAUSED"


class TestVerdictRecommendations:
    def test_all_four_classes_have_recommendations(self, ns):
        rec = ns["_RECOMMEND"]
        for cls in ("DIFF-CAUSED", "PRE-EXISTING", "INFRA-FLAKE", "PARTIAL"):
            assert cls in rec and rec[cls].strip(), f"missing recommendation for {cls}"

    def test_recommendation_is_returned_in_verdict(self, classify, ns):
        r = classify(["scripts/foo.sh:1: bad"], {"scripts/foo.sh"})
        assert r["recommendation"] == ns["_RECOMMEND"]["DIFF-CAUSED"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
