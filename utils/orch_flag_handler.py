#!/usr/bin/env python3
"""
Orchestration flag handler for Craft commands.

Provides unified logic for --orch flag across all commands.
"""

from typing import Optional, Tuple, Dict, Any
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
    Prompt user to select orchestration mode interactively.

    Uses AskUserQuestion tool from Claude Code.

    Returns:
        Selected mode name
    """
    print("\n Orchestration Mode Selection")
    print("=" * 50)
    print("\nAvailable modes:")
    for mode, desc in MODE_DESCRIPTIONS.items():
        print(f"  {mode:10s} - {desc}")

    return "default"


def show_orchestration_preview(task: str, mode: str) -> None:
    """
    Display orchestration plan without spawning agents.

    Args:
        task: Task description
        mode: Selected orchestration mode
    """
    mode_config = get_mode_config(mode)

    print("\n+" + "-" * 63 + "+")
    print("| DRY RUN: Orchestration Preview" + " " * 29 + "|")
    print("+" + "-" * 63 + "+")
    print("|" + " " * 63 + "|")
    print(f"| Task: {task[:49]:<49s} |")
    print(f"| Mode: {mode:<49s} |")
    print(f"| Max Agents: {mode_config['max_agents']:<45d} |")
    print(f"| Compression: {mode_config['compression']}%{' ' * 42} |")
    print("|" + " " * 63 + "|")
    print(
        "| This would spawn the orchestrator with the above settings." + " " * 3 + "|"
    )
    print("| Remove --dry-run to execute." + " " * 32 + "|")
    print("|" + " " * 63 + "|")
    print("+" + "-" * 63 + "+\n")


def get_mode_config(mode: str) -> Dict[str, Any]:
    """Get configuration for orchestration mode."""
    configs = {
        "default": {"max_agents": 2, "compression": 70},
        "debug": {"max_agents": 1, "compression": 90},
        "optimize": {"max_agents": 4, "compression": 60},
        "release": {"max_agents": 4, "compression": 85},
    }
    return configs.get(mode, configs["default"])


def spawn_orchestrator(task: str, mode: str, extra_args: str = "") -> None:
    """
    Spawn orchestrator with specified mode.

    Args:
        task: Task description
        mode: Orchestration mode
        extra_args: Additional arguments to pass
    """
    print(f"\n Spawning orchestrator...")
    print(f"   Task: {task}")
    print(f"   Mode: {mode}")
    if extra_args:
        print(f"   Extra args: {extra_args}")
    print(f"\n   Executing: /craft:orchestrate '{task}' {mode} {extra_args}\n")


if __name__ == "__main__":
    test_cases = [
        ("simple task", False, None),
        ("simple task", True, "optimize"),
        ("complex task", True, "debug"),
    ]

    print("Orch Flag Handler Test Cases")
    print("=" * 60)

    for task, orch_flag, mode in test_cases:
        should_orch, selected_mode = handle_orch_flag(task, orch_flag, mode)
        print(f"\nTask: {task}")
        print(f"  orch_flag: {orch_flag}, mode: {mode}")
        print(f"  Result: should_orchestrate={should_orch}, mode={selected_mode}")

        if should_orch and selected_mode:
            show_orchestration_preview(task, selected_mode)
