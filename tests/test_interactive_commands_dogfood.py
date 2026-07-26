# tests/test_interactive_commands_dogfood.py
from pathlib import Path
import pytest
from test_plugin_e2e import PLUGIN_DIR, _find_all_commands

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

DEFAULT_ON = ["commands/brainstorm.md", "commands/do.md", "commands/plan/feature.md"]

@pytest.mark.parametrize("rel", DEFAULT_ON)
def test_refine_default_on_documented(rel):
    text = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "default" in text and "no-refine" in text, \
        f"{rel} must document refine default-on + --no-refine opt-out"


def test_refine_default_policy_table_exhaustive():
    """Every --refine declarer must have a row in SKILL.md's Default Policy table.

    D7 (SPEC-prompt-refiner-remaining-2026-07-26): the table drifted silently
    once before (smart-help and arch/plan.md were live declarers absent from
    it). Keys on the command file's relative path string appearing in the
    table, matching the table's own path-keyed rows.
    """
    skill = (PLUGIN_DIR / "skills/workflow/prompt-refiner/SKILL.md").read_text(encoding="utf-8")
    declarers = {
        str(cmd.relative_to(PLUGIN_DIR))
        for cmd in _find_all_commands()
        if "- name: refine" in cmd.read_text(encoding="utf-8")
    }
    missing = {rel for rel in declarers if f"`{rel}`" not in skill}
    assert not missing, (
        "prompt-refiner SKILL.md's Default Policy table is missing a row for: "
        f"{sorted(missing)}"
    )


def test_yes_cascade_documented():
    # grill's contract moved to the skill (thin-command/fat-skill, ADR-002)
    grill = (PLUGIN_DIR / "skills/workflow/grill/SKILL.md").read_text(encoding="utf-8").lower()
    assert "cascade" in grill, \
        "grill skill must document that --yes cascades (auto-picks Recommended)"
    refiner = (PLUGIN_DIR / "skills/workflow/prompt-refiner/SKILL.md").read_text(encoding="utf-8").lower()
    assert "cascade" in refiner, \
        "prompt-refiner must document the --yes cascade auto-accept path"


def test_orchestrate_clarify_model():
    text = (PLUGIN_DIR / "commands/orch.md").read_text(encoding="utf-8")
    assert "Step 0.5" in text
    lo = text.lower()
    assert "askuserquestion" in lo and "consequence" in lo, \
        "orchestrate Step 0.5 must adopt the structured model"
    assert "--yes" in text, "orchestrate clarify must honor --yes"
