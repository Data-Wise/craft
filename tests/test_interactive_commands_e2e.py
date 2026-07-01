# tests/test_interactive_commands_e2e.py
from pathlib import Path
import pytest
from test_plugin_e2e import PLUGIN_DIR  # reuse existing helper module

pytestmark = pytest.mark.e2e

YES_COMMANDS = ["commands/grill.md", "commands/orchestrate.md"]

@pytest.mark.parametrize("rel", YES_COMMANDS)
def test_yes_flag_declared(rel):
    text = (PLUGIN_DIR / rel).read_text(encoding="utf-8")
    assert "- name: yes" in text, f"{rel} must declare the --yes flag"
    assert "non-interactive" in text.lower(), f"{rel} must document non-interactive semantics"


# The interaction contract now lives in the grill SKILL (thin-command/fat-skill,
# ADR-002). Frontmatter flags stay on the command; behavioral contract asserts the skill.
GRILL_SKILL = "skills/workflow/grill/SKILL.md"


def test_grill_interaction_model_inverted():
    text = (PLUGIN_DIR / GRILL_SKILL).read_text(encoding="utf-8")
    shim = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8")
    # old directive removed from both surfaces
    assert 'do not "fix" to batches' not in text and 'do not "fix" to batches' not in shim, \
        "old free-text directive must be removed"
    # new contract present in the skill
    assert "AskUserQuestion" in text, "grill skill must document AskUserQuestion-per-branch"
    assert "consequence" in text.lower(), "grill skill must require a per-option consequence"
    assert "Recommended" in text, "grill skill must keep Recommended-first"


def test_grill_declares_refine():
    text = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8")
    assert "- name: refine" in text


def test_grill_refine_path_rule():
    text = (PLUGIN_DIR / GRILL_SKILL).read_text(encoding="utf-8").lower()
    assert "skip refine entirely" in text, \
        "grill skill must document: skip refine entirely when arg is a path"
