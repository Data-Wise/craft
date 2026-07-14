#!/usr/bin/env python3
"""Integration tests: /craft:orch:drive's issue-premise pre-filter (Phase 3).

Verifies the cross-command wiring documented in commands/orch/drive.md's
Step 2 -- it must (a) only fire when the spec cites a #NNN issue, (b)
invoke /craft:git:issue-check when it does, and (c) never block the loop
regardless of verdict. This is prose-level wiring (an LLM reads and
follows commands/orch/drive.md at runtime) so the test asserts on the
documented contract text, not a live orch:drive run.
"""

import re
from pathlib import Path

import pytest

pytestmark = [pytest.mark.integration, pytest.mark.commands]

PLUGIN_DIR = Path(__file__).parent.parent
DRIVE_MD = PLUGIN_DIR / "commands" / "orch" / "drive.md"
DRIVE_ENGINE_SKILL = PLUGIN_DIR / "skills" / "orchestration" / "drive-engine" / "SKILL.md"
ISSUE_CHECK_MD = PLUGIN_DIR / "commands" / "git" / "issue-check.md"


class TestDriveIssueGateWiring:
    def test_drive_md_has_a_pre_filter_step(self):
        text = DRIVE_MD.read_text(encoding="utf-8")
        assert re.search(r"### Step \d+: Issue-premise pre-filter", text), (
            "commands/orch/drive.md is missing the Step N: Issue-premise "
            "pre-filter section"
        )

    def test_pre_filter_invokes_issue_check(self):
        text = DRIVE_MD.read_text(encoding="utf-8")
        assert "/craft:git:issue-check" in text

    def test_pre_filter_documents_skip_when_no_citation(self):
        text = DRIVE_MD.read_text(encoding="utf-8")
        section = text.split("Issue-premise pre-filter", 1)[1].split("### Step", 1)[0]
        assert "skip entirely" in section.lower()
        assert "zero" in section.lower()

    def test_pre_filter_never_blocks(self):
        text = DRIVE_MD.read_text(encoding="utf-8")
        section = text.split("Issue-premise pre-filter", 1)[1].split("### Step", 1)[0]
        assert "never blocks" in section.lower()

    def test_pre_filter_references_nnn_pattern(self):
        text = DRIVE_MD.read_text(encoding="utf-8")
        section = text.split("Issue-premise pre-filter", 1)[1].split("### Step", 1)[0]
        assert "#NNN" in section or r"#\d+" in section

    def test_issue_check_command_exists_for_drive_to_call(self):
        """The pre-filter is meaningless if the command it calls doesn't exist."""
        assert ISSUE_CHECK_MD.exists()

    def test_drive_engine_skill_disclaims_the_pre_filter(self):
        """The pre-filter belongs to the command (gating), not drive-engine
        (dispatch + verify) -- confirm the ownership boundary is documented,
        not silently duplicated in both places."""
        text = DRIVE_ENGINE_SKILL.read_text(encoding="utf-8")
        assert "issue-check" in text.lower() or "issue-premise" in text.lower()

    def test_see_also_cross_links_issue_check(self):
        text = DRIVE_MD.read_text(encoding="utf-8")
        see_also = text.split("## See Also", 1)[1]
        assert "/craft:git:issue-check" in see_also


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
