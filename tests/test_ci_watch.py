#!/usr/bin/env python3
"""Structural tests for the /craft:ci:watch command.

ci:watch is a thin instruction-file command (no executable logic), so these are
content assertions: valid frontmatter, the safe completion-polling pattern
(gh run view, NOT gh pr checks), both output paths, and the --bg snippet.
"""

import re
from pathlib import Path

import pytest

try:
    import yaml
except ImportError:  # pragma: no cover
    yaml = None

pytestmark = [pytest.mark.integration, pytest.mark.commands]

WATCH_MD = Path(__file__).parent.parent / "commands" / "ci" / "watch.md"


@pytest.fixture(scope="module")
def text():
    assert WATCH_MD.exists(), f"Missing command file: {WATCH_MD}"
    return WATCH_MD.read_text(encoding="utf-8")


@pytest.fixture(scope="module")
def frontmatter(text):
    assert yaml is not None, "PyYAML required"
    fm = text.split("---", 2)[1]
    return yaml.safe_load(fm)


class TestCiWatchStructure:
    def test_command_file_exists(self):
        assert WATCH_MD.exists()

    def test_frontmatter_has_description_and_category(self, frontmatter):
        assert frontmatter.get("description"), "missing description"
        assert frontmatter.get("category") == "ci", "category must be ci"

    def test_frontmatter_declares_target_argument(self, frontmatter):
        names = {a["name"] for a in frontmatter.get("arguments", [])}
        assert "target" in names, f"expected a 'target' argument, got {names}"

    def test_polls_with_gh_run_view_not_pr_checks(self, text):
        # The exit-8 anti-pattern: gh pr checks must NOT be the polling signal.
        assert "gh run view" in text and "--json status" in text, (
            "watch must poll via `gh run view ... --json status`"
        )
        poll_region = text[text.index("Poll loop"):text.index("## Output")]
        assert "gh pr checks" not in poll_region, (
            "gh pr checks exits 8 in-progress — must not be used for polling"
        )

    def test_has_green_and_red_output_paths(self, text):
        assert "Green path" in text and "Red path" in text
        assert "SUCCESS" in text and "FAILURE" in text

    def test_describes_bg_snippet(self, text):
        assert "--bg" in text
        assert re.search(r"until .*gh run view.*completed", text), (
            "missing the --bg background-poll snippet"
        )

    def test_forwards_red_path_to_triage(self, text):
        assert "/craft:ci:triage" in text, "red path must forward to ci:triage"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
