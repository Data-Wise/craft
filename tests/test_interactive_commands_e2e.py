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


def test_grill_interaction_model_inverted():
    text = (PLUGIN_DIR / "commands/grill.md").read_text(encoding="utf-8")
    # old directive removed
    assert 'do not "fix" to batches' not in text, "old free-text directive must be removed"
    # new contract present
    assert "AskUserQuestion" in text, "grill must document AskUserQuestion-per-branch"
    assert "consequence" in text.lower(), "grill must require a per-option consequence"
    assert "Recommended" in text, "grill must keep Recommended-first"
