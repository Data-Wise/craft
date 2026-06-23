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


def _grill_body():
    return open(os.path.join(CRAFT, "commands", "grill.md"), encoding="utf-8").read()


def test_grill_body_carries_contract():
    body = _grill_body()
    low = body.lower()
    assert "one question at a time" in low                     # core directive
    assert "recommended" in low                                # recommended-answer rule
    assert "explore the codebase" in low                       # codebase-first
    assert "/done" in body                                     # distinct halt sentinel (not "stop")
    assert "milestone" in low                                  # ADHD-friendly progress checkpoints
    assert "bound" in low                                      # bounded pass honored
    # justify the deliberate AskUserQuestion exception so a future audit won't "fix" it:
    assert ("one at a time" in low or "one-at-a-time" in low) and "askuserquestion" in low


def test_grill_body_captures_and_hands_off():
    body = _grill_body()
    assert "grill_ledger" in body                              # uses the util, not ad-hoc writes
    assert "resolve_ledger_path" in body
    assert "no-capture" in body.lower()                        # embedded-caller suppression
    assert "/craft:plan" in body or "plan-orchestrator" in body  # handoff to the spine


# ── /done enhancements (v2.49.0) structural tests ─────────────────────────────

def _done_body():
    return open(os.path.join(CRAFT, "commands", "workflow", "done.md"), encoding="utf-8").read()


def test_done_has_settings_sync_step():
    """Step 1.10.5 (Claude Settings Sync) must be present in done.md."""
    body = _done_body()
    assert "Step 1.10.5" in body, "Settings Sync step missing"
    low = body.lower()
    assert "settings sync" in low or "settings check" in low, "Settings Sync label missing"


def test_done_has_memory_optimize_step():
    """Step 1.12 (Memory Optimize) must be present in done.md."""
    body = _done_body()
    assert "Step 1.12" in body, "Memory Optimize step missing"
    low = body.lower()
    assert "memory optimize" in low or "memory audit" in low, "Memory Optimize label missing"


def test_done_memory_optimize_covers_key_behaviors():
    """Step 1.12 must document: orphan, ghost, stale, duplicate detection."""
    body = _done_body()
    low = body.lower()
    for keyword in ("orphan", "ghost", "stale", "duplicate"):
        assert keyword in low, f"Memory Optimize missing '{keyword}' behavior"


def test_done_settings_sync_is_readonly():
    """Settings Sync step must declare read-only intent (no auto-write)."""
    body = _done_body()
    # Find the section between "Step 1.10.5" and the next "### Step"
    start = body.find("Step 1.10.5")
    end = body.find("### Step 1.11", start)
    section = body[start:end].lower() if end > start else body[start:start + 800].lower()
    assert "read-only" in section or "report only" in section or "never log" in section, (
        "Settings Sync must declare its read-only intent"
    )
