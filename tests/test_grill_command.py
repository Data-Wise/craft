"""Structural tests for commands/grill.md (the /craft:grill command surface).

The interactive grill loop is model-executed and not behaviorally unit-testable;
these assert the command's static contract + discovery/audit cleanliness.
"""
import os
import subprocess

CRAFT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_grill_command_exists_and_has_frontmatter():
    p = os.path.join(CRAFT, "commands", "grill.md")
    assert os.path.exists(p), "commands/grill.md missing"
    head = open(p, encoding="utf-8").read()
    assert head.startswith("---"), "missing frontmatter"
    assert "description:" in head
    assert "name: bound" in head, "missing --bound arg (orchestrate Step 0.5 needs it)"
    assert "name: no-capture" in head, "missing --no-capture arg (embedded callers need it)"


def test_grill_passes_command_audit():
    # command-audit.sh is a bash script; invoke via bash from the repo root
    r = subprocess.run(["bash", os.path.join(CRAFT, "scripts", "command-audit.sh")],
                       cwd=CRAFT, capture_output=True, text=True)
    combined = (r.stdout + r.stderr).lower()
    assert not any("error" in line and "grill" in line
                   for line in combined.splitlines()), combined
