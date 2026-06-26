# tests/test_scaffold_defaults_e2e.py
from pathlib import Path
import pytest
from test_plugin_e2e import PLUGIN_DIR

pytestmark = pytest.mark.e2e

TEMPLATES = PLUGIN_DIR / "skills/workflow/brainstorm-insights/references/scaffold-templates.md"

def test_scaffold_templates_exist():
    assert TEMPLATES.exists(), "shared scaffold-templates.md must exist"
    body = TEMPLATES.read_text(encoding="utf-8")
    assert "Test plan (TDD)" in body, "must hold the test-plan template"
    assert "Documentation" in body, "must hold the doc-section template"
