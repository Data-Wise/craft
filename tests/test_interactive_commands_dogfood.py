# tests/test_interactive_commands_dogfood.py
from pathlib import Path
import pytest
from test_plugin_e2e import PLUGIN_DIR

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

DEFAULT_ON = ["commands/workflow/brainstorm.md", "commands/do.md", "commands/plan/feature.md"]

@pytest.mark.parametrize("rel", DEFAULT_ON)
def test_refine_default_on_documented(rel):
    text = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "default" in text and "no-refine" in text, \
        f"{rel} must document refine default-on + --no-refine opt-out"


def test_yes_cascade_documented():
    grill = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8").lower()
    assert "zero askuserquestion" in grill or "auto-pick every recommended" in grill
    refiner = (PLUGIN_DIR / "skills/workflow/prompt-refiner/SKILL.md").read_text(encoding="utf-8").lower()
    assert "auto" in refiner and ("--yes" in refiner or "auto-accept" in refiner), \
        "prompt-refiner must document an auto-accept path for --yes"


def test_orchestrate_clarify_model():
    text = (PLUGIN_DIR / "commands/orchestrate.md").read_text(encoding="utf-8")
    assert "Step 0.5" in text
    lo = text.lower()
    assert "askuserquestion" in lo and "consequence" in lo, \
        "orchestrate Step 0.5 must adopt the structured model"
    assert "--yes" in text, "orchestrate clarify must honor --yes"
