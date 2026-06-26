# tests/test_scaffold_defaults_dogfood.py
import pytest
from test_plugin_e2e import PLUGIN_DIR
pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

SKILLS = ["skills/workflow/brainstorm-insights/SKILL.md",
          "skills/orchestration/plan-orchestrator/SKILL.md"]

@pytest.mark.parametrize("rel", SKILLS)
def test_tier_inference_documented(rel):
    t = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "tier" in t and "dogfood" in t and "scaffold-templates" in t, \
        f"{rel} must document tier inference + reference scaffold-templates.md"
    assert "no-tests" in t, f"{rel} must document the --no-tests opt-out"

@pytest.mark.parametrize("rel", SKILLS)
def test_docs_section_documented(rel):
    t = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "documentation" in t and "no-docs" in t and "scorer" in t, \
        f"{rel} must document the docs-section emission + scorer reuse + --no-docs"

@pytest.mark.parametrize("rel", SKILLS)
def test_yes_nonsuppression_and_cascade_exclusion(rel):
    t = (PLUGIN_DIR / rel).read_text(encoding="utf-8").lower()
    assert "yes" in t and "content" in t, \
        f"{rel} must state --yes does NOT suppress sections (they are content)"
    assert "count" in t and ("exclud" in t or "never" in t), \
        f"{rel} must state the count-cascade exclusion"
