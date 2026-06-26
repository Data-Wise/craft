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


DEFAULT_ON = {"commands/workflow/brainstorm.md", "commands/plan/feature.md", "commands/grill.md"}
OPT_IN = {"commands/arch/plan.md", "commands/workflow/spec-review.md"}

def test_scaffold_flag_scope():
    no_tests, no_docs, opt_tests, opt_docs = set(), set(), set(), set()
    for cmd in PLUGIN_DIR.glob("commands/**/*.md"):
        rel = str(cmd.relative_to(PLUGIN_DIR))
        t = cmd.read_text(encoding="utf-8")
        if "- name: no-tests" in t: no_tests.add(rel)
        if "- name: no-docs" in t: no_docs.add(rel)
        if "- name: tests" in t: opt_tests.add(rel)
        if "- name: docs" in t: opt_docs.add(rel)
    assert no_tests == DEFAULT_ON, f"no-tests scope drift: {no_tests ^ DEFAULT_ON}"
    assert no_docs == DEFAULT_ON, f"no-docs scope drift: {no_docs ^ DEFAULT_ON}"
    assert opt_tests == OPT_IN, f"opt-in tests scope drift: {opt_tests ^ OPT_IN}"
    assert opt_docs == OPT_IN, f"opt-in docs scope drift: {opt_docs ^ OPT_IN}"
