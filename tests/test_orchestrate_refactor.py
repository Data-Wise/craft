"""Tests for the orchestrate optimize/refactor (W3): lean contract + reference split,
plus Step 0.5 Clarify invoking bounded /craft:grill."""
import os

CRAFT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CMD = os.path.join(CRAFT, "commands", "orchestrate.md")
REF = os.path.join(CRAFT, "docs", "reference", "orchestrate-reference.md")


def _cmd():
    return open(CMD, encoding="utf-8").read()


def test_contract_preserved_and_reference_extracted():
    cmd = _cmd()
    for marker in ["Step 0:", "Step 0.5", "Step 1:", "Step 2:", "Steps 3-N"]:
        assert marker in cmd, f"contract step missing after split: {marker}"
    assert os.path.exists(REF), "reference doc not created"
    # a bulky reference section must have moved OUT of the command and INTO the reference doc
    assert "Token Instrumentation" not in cmd, "reference still bloats the command"
    assert "Token Instrumentation" in open(REF, encoding="utf-8").read()
    # the command points at the reference
    assert "orchestrate-reference" in cmd


def test_step_0_5_invokes_bounded_grill():
    cmd = _cmd()
    assert "Step 0.5" in cmd
    assert "/craft:grill" in cmd and "bound" in cmd
    assert "--no-capture" in cmd        # embedded grill must not write a spec file
    assert "--no-clarify" in cmd        # suppress path documented
