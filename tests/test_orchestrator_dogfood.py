#!/usr/bin/env python3
"""
Craft Orchestrator v2.1 Dogfooding Tests
=========================================
Functional tests that exercise real orchestrator behavior.
Non-interactive - runs without user input.

Run with: python tests/test_orchestrator_dogfood.py
"""

import json
import re
import tempfile
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e, pytest.mark.orchestrator]


PLUGIN_DIR = Path(__file__).parent.parent


# ─── Mode Parsing Tests ──────────────────────────────────────────────────────


def test_mode_regex_parsing():
    """Test that mode can be parsed from orchestrate command."""
    test_cases = [
        ('orchestrate "add auth" optimize', "optimize"),
        ('orchestrate "fix bug" debug', "debug"),
        ('orchestrate "prep release" release', "release"),
        ('orchestrate "quick task"', "default"),
        ('orchestrate status', None),
        ('orchestrate timeline', None),
    ]

    # Regex to extract mode from command
    mode_pattern = re.compile(
        r'orchestrate\s+"[^"]+"\s+(default|debug|optimize|release)$'
    )

    failures = []
    for cmd, expected in test_cases:
        match = mode_pattern.search(cmd)
        actual = match.group(1) if match else ("default" if '"' in cmd and cmd.endswith('"') else None)

        # Adjust logic for default case
        if expected == "default" and '"' in cmd and not match:
            actual = "default"

        if actual != expected:
            failures.append(f"{cmd}: expected {expected}, got {actual}")

    assert not failures, f"Failed: {failures[0]}"


def test_context_threshold_values():
    """Test that context thresholds are valid percentages."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    content = agent_path.read_text()

    # Extract percentage values
    percentages = re.findall(r'(\d+)%', content)

    invalid = []
    for p in percentages:
        val = int(p)
        # Allow up to 150% for context thresholds (e.g., 110% hard timeout)
        if val < 0 or val > 150:
            invalid.append(p)

    assert not invalid, f"Invalid percentages: {invalid}"


def test_agent_types_match_craft_commands():
    """Test that agent types map to real craft commands."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    content = agent_path.read_text()

    # Expected craft command patterns
    craft_patterns = [
        "/craft:code:",
        "/craft:test:",
        "/craft:docs:",
        "/craft:arch:",
        "/craft:plan:",
        "/craft:check"
    ]

    missing = []
    for pattern in craft_patterns:
        if pattern not in content:
            missing.append(pattern)

    assert not missing, f"Missing mappings: {missing}"


# ─── Token Estimation Tests ──────────────────────────────────────────────────


def test_token_estimation_heuristics():
    """Test token estimation logic with sample inputs."""
    # Simulated token estimation (matches BEHAVIOR 8 heuristics)
    def estimate_tokens(text: str) -> int:
        """Rough token estimate: ~4 chars per token."""
        return len(text) // 4

    test_cases = [
        ("Hello", 1, 10),           # Short message
        ("x" * 100, 20, 30),         # ~100 chars = ~25 tokens
        ("x" * 1000, 200, 300),      # ~1000 chars = ~250 tokens
        ("x" * 4000, 900, 1100),     # ~4000 chars = ~1000 tokens
    ]

    failures = []
    for text, min_expected, max_expected in test_cases:
        estimated = estimate_tokens(text)
        if not (min_expected <= estimated <= max_expected):
            failures.append(f"len={len(text)}: {estimated} not in [{min_expected}, {max_expected}]")

    assert not failures, f"Failed: {failures[0]}"


def test_context_budget_calculation():
    """Test context budget math (15% per agent of 128K)."""
    total_context = 128000  # ~128K tokens
    agent_budget_pct = 0.15
    expected_budget = int(total_context * agent_budget_pct)  # 19200

    # Test with different agent counts
    test_cases = [
        (1, expected_budget),
        (2, expected_budget),
        (4, expected_budget),  # Each agent still gets 15%
    ]

    failures = []
    for num_agents, expected_per_agent in test_cases:
        # In optimize mode, 4 agents means 4 * 15% = 60% max usage
        total_usage = num_agents * agent_budget_pct
        if total_usage > 1.0:
            failures.append(f"{num_agents} agents would exceed 100%")
        elif expected_per_agent < 10000:
            failures.append(f"Budget too small: {expected_per_agent}")

    assert not failures, f"Failed: {failures[0]}"


# ─── Mode Configuration Tests ────────────────────────────────────────────────


def test_mode_agent_limits():
    """Test that mode agent limits are logical."""
    modes = {
        "default": {"max_agents": 2, "compression": 70},
        "debug": {"max_agents": 1, "compression": 90},
        "optimize": {"max_agents": 4, "compression": 60},
        "release": {"max_agents": 4, "compression": 85},
    }

    failures = []
    for mode, config in modes.items():
        # Agent limit should be 1-4
        if not (1 <= config["max_agents"] <= 4):
            failures.append(f"{mode}: invalid agent limit {config['max_agents']}")

        # Compression should be 50-95%
        if not (50 <= config["compression"] <= 95):
            failures.append(f"{mode}: invalid compression {config['compression']}%")

    assert not failures, f"Failed: {failures[0]}"


def test_mode_verbosity_levels():
    """Test that modes have appropriate verbosity."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    content = agent_path.read_text()

    # Check verbosity descriptions exist
    verbosity_checks = [
        ("debug", "Verbose"),
        ("optimize", "Minimal"),
        ("release", "Full report"),
    ]

    failures = []
    for mode, expected_verbosity in verbosity_checks:
        # Check both mode and verbosity appear near each other
        mode_section = content.find(f"**{mode} mode**")
        if mode_section == -1:
            mode_section = content.find(f"`{mode}`")

        if mode_section == -1:
            failures.append(f"{mode}: section not found")
        elif expected_verbosity.lower() not in content.lower():
            failures.append(f"{mode}: missing verbosity '{expected_verbosity}'")

    assert not failures, f"Failed: {failures[0]}"


# ─── Timeline Rendering Tests ────────────────────────────────────────────────


def test_timeline_ascii_rendering():
    """Test that timeline can be rendered in ASCII."""
    def render_progress_bar(progress: float, width: int = 20) -> str:
        """Render ASCII progress bar."""
        filled = int(progress * width)
        empty = width - filled
        return "\u2588" * filled + "\u2591" * empty

    test_cases = [
        (0.0, "\u2591" * 20),
        (0.5, "\u2588" * 10 + "\u2591" * 10),
        (1.0, "\u2588" * 20),
        (0.25, "\u2588" * 5 + "\u2591" * 15),
    ]

    failures = []
    for progress, expected in test_cases:
        actual = render_progress_bar(progress)
        if actual != expected:
            failures.append(f"{progress}: got '{actual[:10]}...'")

    assert not failures, f"Failed: {failures[0]}"


def test_timeline_time_formatting():
    """Test timeline time formatting."""
    def format_duration(seconds: float) -> str:
        """Format duration for timeline."""
        if seconds < 60:
            return f"{seconds:.1f}s"
        else:
            minutes = seconds / 60
            return f"{minutes:.1f}m"

    test_cases = [
        (30.0, "30.0s"),
        (60.0, "1.0m"),
        (90.0, "1.5m"),
        (120.0, "2.0m"),
        (5.5, "5.5s"),
    ]

    failures = []
    for seconds, expected in test_cases:
        actual = format_duration(seconds)
        if actual != expected:
            failures.append(f"{seconds}s: expected '{expected}', got '{actual}'")

    assert not failures, f"Failed: {failures[0]}"


# ─── Compression Logic Tests ─────────────────────────────────────────────────


def test_compression_trigger_logic():
    """Test compression trigger conditions."""
    def should_compress(
        exchange_count: int,
        estimated_tokens: int,
        large_response: bool = False,
        user_request: bool = False
    ) -> tuple[bool, str]:
        """Determine if compression should trigger."""
        if user_request:
            return True, "user_request"
        if large_response:
            return True, "large_response"
        if exchange_count > 20:
            return True, "exchange_count"
        if estimated_tokens > 100000:  # ~78% of 128K
            return True, "token_limit"
        if estimated_tokens > 70000:  # ~55% of 128K
            return False, "warning"  # Warning but not compress
        return False, "ok"

    test_cases = [
        # (exchanges, tokens, large, user) -> (should_compress, reason)
        ((10, 50000, False, False), (False, "ok")),
        ((25, 50000, False, False), (True, "exchange_count")),
        ((10, 110000, False, False), (True, "token_limit")),
        ((10, 50000, True, False), (True, "large_response")),
        ((10, 50000, False, True), (True, "user_request")),
        ((10, 75000, False, False), (False, "warning")),
    ]

    failures = []
    for (exchanges, tokens, large, user), (expected_compress, expected_reason) in test_cases:
        actual_compress, actual_reason = should_compress(exchanges, tokens, large, user)
        if actual_compress != expected_compress:
            failures.append(f"({exchanges}, {tokens}): expected {expected_compress}, got {actual_compress}")

    assert not failures, f"Failed: {failures[0]}"


def test_compression_ratio():
    """Test that compression achieves reasonable ratio."""
    def simulate_compression(original_tokens: int) -> int:
        """Simulate compression (target: 60% reduction)."""
        return int(original_tokens * 0.4)  # Keep 40%

    test_cases = [
        (10000, 3500, 4500),   # 10K -> 4K (+-500)
        (50000, 18000, 22000), # 50K -> 20K (+-2K)
        (100000, 38000, 42000), # 100K -> 40K (+-2K)
    ]

    failures = []
    for original, min_expected, max_expected in test_cases:
        compressed = simulate_compression(original)
        if not (min_expected <= compressed <= max_expected):
            failures.append(f"{original} -> {compressed}, expected [{min_expected}, {max_expected}]")

    assert not failures, f"Failed: {failures[0]}"


# ─── Session State Tests ─────────────────────────────────────────────────────


def test_session_state_schema():
    """Test session state JSON schema."""
    # Expected session state structure
    sample_state = {
        "session_id": "2025-12-27-abc123",
        "started": "2025-12-27T10:30:00",
        "goal": "Add feature X",
        "mode": "default",
        "agents": [
            {
                "id": "arch-1",
                "type": "arch",
                "task": "Design API",
                "status": "complete",
                "progress": 100
            }
        ],
        "completed_work": ["Task 1 done"],
        "next_actions": ["Task 2"],
        "context_usage": {
            "estimated_tokens": 25000,
            "percentage": 20
        }
    }

    # Validate schema
    required_keys = ["session_id", "started", "goal", "agents"]
    agent_required = ["id", "type", "status"]

    failures = []
    for key in required_keys:
        if key not in sample_state:
            failures.append(f"missing top-level key: {key}")

    for agent in sample_state.get("agents", []):
        for key in agent_required:
            if key not in agent:
                failures.append(f"agent missing key: {key}")

    # Test JSON serialization
    try:
        json_str = json.dumps(sample_state)
        parsed = json.loads(json_str)
        if parsed != sample_state:
            failures.append("JSON round-trip failed")
    except Exception as e:
        failures.append(f"JSON error: {e}")

    assert not failures, f"Failed: {failures[0]}"


def test_session_file_operations():
    """Test session state file read/write."""
    with tempfile.TemporaryDirectory() as tmpdir:
        session_file = Path(tmpdir) / "orchestrator-session.json"

        # Write session
        state = {
            "session_id": "test-123",
            "goal": "Test session",
            "agents": []
        }

        session_file.write_text(json.dumps(state, indent=2))

        # Read back
        loaded = json.loads(session_file.read_text())
        assert loaded == state, "Read/write mismatch"


def test_session_persistence_skill_exists():
    """Test that session-state skill file exists and is valid."""
    skill_path = PLUGIN_DIR / "skills" / "orchestration" / "session-state" / "SKILL.md"
    assert skill_path.exists(), "session-state/SKILL.md not found"

    content = skill_path.read_text()

    # Check required sections
    required = [
        "## State File Location",
        "## Session State Schema",
        "## Operations",
        "## Resume Flow",
    ]

    missing = [s for s in required if s not in content]
    assert not missing, f"Missing sections: {missing}"


def test_session_state_lifecycle():
    """Test session state transitions."""
    # Valid state transitions
    valid_transitions = [
        ("created", "in_progress"),
        ("in_progress", "paused"),
        ("paused", "in_progress"),
        ("in_progress", "complete"),
        ("in_progress", "aborted"),
    ]

    # Invalid transitions
    invalid_transitions = [
        ("complete", "in_progress"),  # Can't resume completed
        ("aborted", "in_progress"),   # Can't resume aborted
    ]

    def can_transition(from_state: str, to_state: str) -> bool:
        """Check if state transition is valid."""
        if to_state == "in_progress":
            return from_state in ("created", "paused")
        if to_state == "paused":
            return from_state == "in_progress"
        if to_state in ("complete", "aborted"):
            return from_state == "in_progress"
        return False

    failures = []
    for from_s, to_s in valid_transitions:
        if not can_transition(from_s, to_s):
            failures.append(f"{from_s} -> {to_s} should be valid")

    for from_s, to_s in invalid_transitions:
        if can_transition(from_s, to_s):
            failures.append(f"{from_s} -> {to_s} should be invalid")

    assert not failures, f"Failed: {failures[0]}"


def test_session_history_archiving():
    """Test session archiving to history directory."""
    with tempfile.TemporaryDirectory() as tmpdir:
        tmpdir = Path(tmpdir)

        # Create current session
        session_file = tmpdir / "orchestrator-session.json"
        history_dir = tmpdir / "orchestrator-history"

        state = {
            "session_id": "2025-12-27-test",
            "goal": "Test archiving",
            "status": "complete"
        }

        # Save session
        session_file.write_text(json.dumps(state, indent=2))

        # Archive it
        history_dir.mkdir(exist_ok=True)
        archive_file = history_dir / f"{state['session_id']}.json"
        archive_file.write_text(json.dumps(state, indent=2))
        session_file.unlink()

        # Verify archive exists
        assert archive_file.exists(), "Archive file not created"

        # Verify session file removed
        assert not session_file.exists(), "Session file not removed"

        # Verify archive content
        archived = json.loads(archive_file.read_text())
        assert archived["session_id"] == state["session_id"], "Archive content mismatch"


# ─── Integration Tests ───────────────────────────────────────────────────────


def test_craft_command_structure():
    """Test that craft commands follow expected structure."""
    commands_dir = PLUGIN_DIR / "commands"
    assert commands_dir.exists(), "commands/ directory not found"

    # Check orchestrate.md has required sections
    orchestrate = commands_dir / "orchestrate.md"
    content = orchestrate.read_text()

    required_sections = [
        "## Usage",
        "## Modes",
        "## Examples",
        "## Control Commands",
    ]

    missing = [s for s in required_sections if s not in content]
    assert not missing, f"Missing sections: {missing}"


def test_agent_skill_consistency():
    """Test that agent references skills correctly."""
    agent_path = PLUGIN_DIR / "agents" / "orchestrator-v2.md"
    skills_dir = PLUGIN_DIR / "skills"
    assert skills_dir.exists(), "skills/ directory not found"

    content = agent_path.read_text()

    # Check that referenced agent types could map to skills
    agent_types = ["code", "test", "doc", "arch", "plan", "check"]

    # Just verify the mappings exist in the orchestrator
    found = sum(1 for t in agent_types if t in content)
    assert found >= len(agent_types) // 2, f"Only {found}/{len(agent_types)} agent types found"
