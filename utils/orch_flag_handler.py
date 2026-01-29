#!/usr/bin/env python3
"""
Orchestration flag handler for Craft commands.

Provides unified logic for --orch flag across all commands.
"""

from typing import Optional, Tuple, Dict, Any, Union
import sys


VALID_MODES = ["default", "debug", "optimize", "release"]

MODE_DESCRIPTIONS = {
    "default": "Quick tasks (2 agents max, 70% compression)",
    "debug": "Sequential troubleshooting (1 agent, 90% compression)",
    "optimize": "Fast parallel work (4 agents, 60% compression)",
    "release": "Pre-release audit (4 agents, 85% compression)",
}


def handle_orch_flag(
    task: str, orch_flag: bool, mode: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Handle --orch flag logic.

    Args:
        task: Task description
        orch_flag: True if --orch present
        mode: Mode value if --orch=<mode>, None otherwise

    Returns:
        Tuple of (should_orchestrate, selected_mode)

    Raises:
        ValueError: If invalid mode specified
    """
    if not orch_flag:
        return (False, None)

    if mode:
        if mode not in VALID_MODES:
            raise ValueError(
                f"Invalid mode: '{mode}'. Valid modes: {', '.join(VALID_MODES)}"
            )
        return (True, mode)

    selected_mode = prompt_user_for_mode()
    return (True, selected_mode)


def prompt_user_for_mode() -> str:
    """
    Fallback for mode selection in non-interactive contexts.

    IMPORTANT: This function only runs in tests and scripts. The actual
    interactive mode selection is implemented in commands/orchestrate.md
    under "Execution Behavior > Step 0: Mode Selection", which instructs
    Claude to use AskUserQuestion with structured options.

    When called by Claude Code:
        - Claude reads commands/orchestrate.md
        - Step 0 triggers AskUserQuestion (JSON prompt)
        - This Python function is NOT invoked

    When called in tests/scripts:
        - Displays available modes as reference
        - Returns "default" as fallback

    Returns:
        "default" (always, in non-interactive context)

    See Also:
        commands/orchestrate.md - Step 0: Mode Selection (AskUserQuestion)
        agents/orchestrator-v2.md - BEHAVIOR 1: Task Analysis + Plan Confirmation
    """
    # Non-interactive fallback — display modes and return default
    print("\n🎯 Orchestration Mode Selection")
    print("=" * 50)
    print("\nAvailable modes:")
    for mode, desc in MODE_DESCRIPTIONS.items():
        print(f"  {mode:10s} - {desc}")
    print("\n💡 In Claude Code, AskUserQuestion prompts mode selection")
    print("   See: commands/orchestrate.md > Step 0: Mode Selection")
    print("💡 In scripts/tests, defaulting to 'default' mode")
    print("   Use --orch=<mode> for explicit selection\n")

    return "default"


def show_orchestration_preview(
    task: str, mode: str, extra_context: Optional[Dict[str, Any]] = None
) -> None:
    """
    Display orchestration plan without spawning agents.

    Args:
        task: Task description
        mode: Selected orchestration mode
        extra_context: Additional context to display (optional)
    """
    mode_config = get_mode_config(mode)

    print("\n┌" + "─" * 63 + "┐")
    print("│ 🔍 DRY RUN: Orchestration Preview" + " " * 28 + "│")
    print("├" + "─" * 63 + "┤")
    print("│" + " " * 63 + "│")
    print(f"│ ✓ Task: {task[:49]:<49s} │")
    print(f"│ ✓ Mode: {mode:<49s} │")
    print(f"│ ✓ Max Agents: {mode_config['max_agents']:<45d} │")
    print(f"│ ✓ Compression: {mode_config['compression']}%{' ' * 42} │")
    print("│" + " " * 63 + "│")

    if extra_context:
        for key, value in extra_context.items():
            print(f"│ ✓ {key}: {str(value)[:49]:<49s} │")
        print("│" + " " * 63 + "│")

    print(
        "│ This would spawn the orchestrator with the above settings." + " " * 3 + "│"
    )
    print("│ Remove --dry-run to execute." + " " * 32 + "│")
    print("│" + " " * 63 + "│")
    print("└" + "─" * 63 + "┘\n")


def get_mode_config(mode: str) -> Dict[str, Union[int, float]]:
    """
    Get configuration for orchestration mode.

    Args:
        mode: Orchestration mode name

    Returns:
        Configuration dict with max_agents and compression settings
    """
    configs = {
        "default": {"max_agents": 2, "compression": 70},
        "debug": {"max_agents": 1, "compression": 90},
        "optimize": {"max_agents": 4, "compression": 60},
        "release": {"max_agents": 4, "compression": 85},
    }
    return configs.get(mode, configs["default"])


def spawn_orchestrator(task: str, mode: str, extra_args: str = "") -> bool:
    """
    Spawn orchestrator with specified mode.

    This function documents the expected behavior when Claude Code
    uses the Skill tool to spawn the orchestrator agent.

    Args:
        task: Task description
        mode: Orchestration mode (default|debug|optimize|release)
        extra_args: Additional arguments to pass to orchestrator

    Returns:
        True if orchestrator spawned successfully, False otherwise

    Note:
        In actual Claude Code execution, this invokes:
        Skill(skill="craft:orchestrate", args=f"{task} {mode} {extra_args}")

        On failure, callers should implement fallback strategy
        (e.g., route to commands instead of orchestration)

    Example:
        success = spawn_orchestrator("add auth", "optimize")
        if not success:
            print("Falling back to command routing...")
            # Use regular command routing
    """
    try:
        print(f"\n🚀 Spawning orchestrator...")
        print(f"   Task: {task}")
        print(f"   Mode: {mode}")
        if extra_args:
            print(f"   Extra args: {extra_args}")

        # In actual execution by Claude Code, this would invoke:
        # Skill(skill="craft:orchestrate", args=f"{task} {mode} {extra_args}")
        print(f"\n   ✓ Executing: /craft:orchestrate '{task}' {mode} {extra_args}\n")

        # For documentation/testing, return True to indicate success
        # Real execution will be handled by Claude Code
        return True

    except Exception as e:
        # Handle any errors gracefully
        handle_orchestrator_failure(task, str(e))
        return False


def handle_orchestrator_failure(task: str, error: str) -> None:
    """
    Handle orchestrator spawn failure gracefully.

    Displays user-friendly error message and suggestions for recovery.

    Args:
        task: Task that failed to orchestrate
        error: Error message from spawn attempt
    """
    print(f"\n⚠️  Orchestrator Spawn Failed")
    print(f"{'=' * 60}")
    print(f"\n📋 Task: {task}")
    print(f"❌ Error: {error}")
    print(f"\n💡 Suggestions:")
    print(f"   1. Try explicit commands instead of orchestration")
    print(f"   2. Check that orchestrator agent is available")
    print(f"   3. Verify you have sufficient context/resources")
    print(f"   4. Use --dry-run to preview without spawning")
    print(f"\n🔄 Falling back to command routing...")
    print(f"{'=' * 60}\n")


def recommend_orchestration_mode(complexity_score: int) -> str:
    """
    Recommend orchestration mode based on task complexity.

    Args:
        complexity_score: Task complexity (0-10 scale)

    Returns:
        Recommended mode name

    Mapping:
        0-3: default (simple tasks)
        4-7: optimize (medium complexity)
        8-10: release (complex tasks requiring thorough validation)
    """
    if complexity_score <= 3:
        return "default"
    elif complexity_score <= 7:
        return "optimize"
    else:
        return "release"


if __name__ == "__main__":
    """Test cases for orch flag handler"""
    test_cases = [
        ("simple task", False, None),
        ("simple task", True, "optimize"),
        ("complex task", True, "debug"),
    ]

    print("🧪 Orch Flag Handler Test Cases")
    print("=" * 60)

    for task, orch_flag, mode in test_cases:
        print(f"\n📝 Test Case: {task}")
        print(f"   Input: orch_flag={orch_flag}, mode={mode}")

        try:
            should_orch, selected_mode = handle_orch_flag(task, orch_flag, mode)
            print(f"   ✓ Result: should_orchestrate={should_orch}, mode={selected_mode}")

            if should_orch and selected_mode:
                show_orchestration_preview(task, selected_mode)
                spawn_result = spawn_orchestrator(task, selected_mode)
                print(f"   ✓ Spawn result: {spawn_result}")
        except ValueError as e:
            print(f"   ❌ Error: {e}")

    # Test error handling
    print(f"\n🧪 Testing Error Handling")
    print("=" * 60)
    try:
        handle_orch_flag("test", True, "invalid")
    except ValueError as e:
        print(f"✓ Caught expected error: {e}")

    # Test failure handler
    print(f"\n🧪 Testing Failure Handler")
    print("=" * 60)
    handle_orchestrator_failure("test task", "Orchestrator not available")

    # Test mode recommendations
    print(f"\n🧪 Testing Mode Recommendations")
    print("=" * 60)
    for score in [2, 5, 9]:
        mode = recommend_orchestration_mode(score)
        print(f"Complexity {score}/10 → {mode} mode")
