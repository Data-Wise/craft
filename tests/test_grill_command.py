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


def _grill_shim():
    return open(os.path.join(CRAFT, "commands", "grill.md"), encoding="utf-8").read()


def _grill_skill():
    return open(
        os.path.join(CRAFT, "skills", "workflow", "grill", "SKILL.md"), encoding="utf-8"
    ).read()


def test_grill_command_is_shim_routing_to_skill():
    """commands/grill.md must be a thin shim routing to the canonical grill skill,
    not a duplicate of the full procedure (thin-command/fat-skill, ADR-002)."""
    shim = _grill_shim()
    assert "skills/workflow/grill/SKILL.md" in shim, "shim must point to the grill skill"
    assert len(shim.splitlines()) < 80, "shim should be thin, not a copy of the full body"


def test_grill_skill_carries_contract():
    body = _grill_skill()
    low = body.lower()
    assert "one question at a time" in low                     # core directive
    assert "recommended" in low                                # recommended-answer rule
    assert "explore the codebase" in low                       # codebase-first
    assert "/done" in body                                     # distinct halt sentinel (not "stop")
    assert "milestone" in low                                  # ADHD-friendly progress checkpoints
    assert "bound" in low                                      # bounded pass honored
    # justify the deliberate AskUserQuestion exception so a future audit won't "fix" it:
    assert ("one at a time" in low or "one-at-a-time" in low) and "askuserquestion" in low


def test_grill_skill_captures_and_hands_off():
    body = _grill_skill()
    assert "grill_ledger" in body                              # uses the util, not ad-hoc writes
    assert "resolve_ledger_path" in body
    assert "no-capture" in body.lower()                        # embedded-caller suppression
    assert "/craft:plan" in body or "plan-orchestrator" in body  # handoff to the spine


def test_grill_skill_has_attack_angles():
    """The skill enumerates adversarial attack angles (feature added with the extraction)."""
    low = _grill_skill().lower()
    assert "attack angle" in low or "weakest recommendation" in low
    assert "riskiest assumption" in low
    assert "reversibility" in low or "scope creep" in low


def test_grill_skill_no_hardcoded_project_gotchas():
    """Attack angles must stay project-agnostic — no craft-internal gotchas hardcoded
    (they would poison grills of other projects). Angle 3 reads the target's CLAUDE.md."""
    low = _grill_skill().lower()
    for leaked in ("_discovery.py", "python3.9", "python 3.9", "rich-body-trap"):
        assert leaked not in low, f"craft-internal gotcha '{leaked}' leaked into the generic skill"
    assert "claude.md" in low, "angle 3 must instruct reading the target project's CLAUDE.md"


# ── /done enhancements (v2.49.0) structural tests ─────────────────────────────
# Canonical body lives in the skill reference (ADR-002); the command is a shim.

def _done_body():
    return open(
        os.path.join(CRAFT, "skills", "workflow", "adhd-workflow", "references", "done.md"),
        encoding="utf-8",
    ).read()


def test_done_command_is_shim_routing_to_skill():
    """commands/workflow/done.md must be a thin shim that routes to the canonical
    skill reference (ADR-002), not a duplicate of the full body."""
    shim = open(os.path.join(CRAFT, "commands", "workflow", "done.md"), encoding="utf-8").read()
    assert "skills/workflow/adhd-workflow/references/done.md" in shim, "shim must point to the reference"
    assert "ADR-002" in shim, "shim must cite the consolidation ADR"
    assert len(shim.splitlines()) < 80, "shim should be thin, not a copy of the full body"


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
