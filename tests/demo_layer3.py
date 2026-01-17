#!/usr/bin/env python3
"""
Demo: Hub v2.0 Layer 3 - Command Detail View
=============================================
Demonstrates what users see when viewing command details.

Run with: python tests/demo_layer3.py
"""

import sys
from pathlib import Path

# Add plugin directory to path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

# Import discovery engine
from commands._discovery import (
    get_command_detail,
    generate_command_tutorial,
    get_command_stats
)


def display_command_detail(command_name: str):
    """Display Layer 3 view for a command."""
    command = get_command_detail(command_name)

    if not command:
        print(f"❌ Command '{command_name}' not found.")
        print(f"💡 Try: /craft:hub to browse all commands")
        return

    # Generate and display tutorial
    tutorial = generate_command_tutorial(command)
    print(tutorial)
    print()


def main():
    """Demo main."""
    print("=" * 70)
    print("🎨 Hub v2.0 Layer 3 - Command Detail View Demo")
    print("=" * 70)

    stats = get_command_stats()
    print(f"\n📊 Total: {stats['total']} commands across {len(stats['categories'])} categories")

    # Demo commands from different categories
    demo_commands = [
        'code:lint',
        'test:run',
        'docs:sync',
        'git:worktree'
    ]

    for cmd_name in demo_commands:
        print("\n" + "─" * 70)
        print(f"Demo: /craft:hub {cmd_name}")
        print("─" * 70)
        print()
        display_command_detail(cmd_name)

    # Show summary
    print("=" * 70)
    print("✅ Layer 3 Demo Complete")
    print("=" * 70)
    print("\n📝 Features Demonstrated:")
    print("  ✓ Command lookup by name (e.g., 'code:lint')")
    print("  ✓ Detailed descriptions")
    print("  ✓ Mode display with time budgets")
    print("  ✓ Basic usage examples")
    print("  ✓ Common workflows")
    print("  ✓ Related commands (when available)")
    print("  ✓ Navigation breadcrumbs")
    print("\n💡 Next: Integrate all 3 layers into /craft:hub command")


if __name__ == "__main__":
    main()
