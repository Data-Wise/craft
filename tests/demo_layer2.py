#!/usr/bin/env python3
"""
Demo: Hub v2.0 Layer 2 - Category View
=======================================
Demonstrates what users see when navigating categories.

Run with: python tests/demo_layer2.py
"""

import sys
from pathlib import Path

# Add plugin directory to path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

# Import discovery engine
from commands._discovery import get_category_info, get_command_stats


def display_category_view(category: str):
    """Display Layer 2 view for a category."""
    info = get_category_info(category)

    if info['count'] == 0:
        print(f"❌ Category '{category}' not found or has no commands.")
        print(f"💡 Try: /craft:hub to see all categories")
        return

    # Build display
    print()
    print("┌" + "─" * 65 + "┐")
    print(f"│ {info['icon']} {info['name'].upper()} COMMANDS ({info['count']} total)".ljust(66) + "│")

    # Add category description
    descriptions = {
        'code': 'Code Quality & Development Tools',
        'test': 'Testing & Quality Assurance',
        'docs': 'Documentation Automation',
        'git': 'Git Workflow & Branch Management',
        'site': 'Documentation Sites (MkDocs, Quarto, pkgdown)',
        'arch': 'Architecture & Design',
        'plan': 'Planning & Project Management',
        'ci': 'Continuous Integration',
        'dist': 'Distribution & Packaging',
        'workflow': 'Workflow Automation'
    }

    if category in descriptions:
        print(f"│ {descriptions[category]}".ljust(66) + "│")

    print("├" + "─" * 65 + "┤")

    # Group by subcategory
    cmd_num = 1
    for subcat, commands in sorted(info['subcategories'].items()):
        if subcat != 'general' or len(info['subcategories']) > 1:
            subcat_display = subcat.upper() if subcat != 'general' else "GENERAL"
            print(f"│".ljust(66) + "│")
            print(f"│ 🔹 {subcat_display} ({len(commands)} commands)".ljust(66) + "│")

        for cmd in sorted(commands, key=lambda x: x['name']):
            mode_indicator = " [mode]" if cmd.get('modes') else ""
            desc = cmd.get('description', 'No description')[:35]

            # Format command line
            cmd_part = f"/craft:{cmd['name']}{mode_indicator}"
            line = f"│   {cmd_num}. {cmd_part:<30s} {desc}"
            print(line[:66].ljust(66) + "│")
            cmd_num += 1

    # Add common workflows
    workflows = {
        'code': [
            ('Pre-commit', 'lint → test:run → ci-local'),
            ('Debug', 'debug → test:debug → coverage'),
            ('Release', 'deps-audit → test:run release → release')
        ],
        'test': [
            ('Daily', 'test:run'),
            ('Debug', 'test:run debug → test:debug'),
            ('Release', 'test:run release → test:coverage')
        ],
        'docs': [
            ('Auto-update', 'docs:sync → docs:changelog'),
            ('Validate', 'docs:check → docs:lint'),
            ('Publish', 'docs:sync → site:build → site:deploy')
        ],
        'git': [
            ('Feature', 'git:worktree → [work] → git:sync'),
            ('Cleanup', 'git:clean'),
            ('Review', 'git:recap')
        ]
    }

    if category in workflows:
        print("│".ljust(66) + "│")
        print("├" + "─" * 65 + "┤")
        print("│ 💡 Common Workflows:".ljust(66) + "│")
        for name, steps in workflows[category]:
            print(f"│   • {name}: {steps}".ljust(66) + "│")

    # Navigation
    print("│".ljust(66) + "│")
    print("│ 🔙 Back to hub: /craft:hub".ljust(66) + "│")
    print(f"│ 📚 Learn more: /craft:hub {category}:[command]".ljust(66) + "│")
    print("└" + "─" * 65 + "┘")
    print()


def main():
    """Demo main."""
    print("=" * 70)
    print("🎨 Hub v2.0 Layer 2 - Category View Demo")
    print("=" * 70)

    stats = get_command_stats()
    print(f"\n📊 Total: {stats['total']} commands across {len(stats['categories'])} categories")

    # Demo categories
    demo_categories = ['code', 'test', 'docs', 'git']

    for category in demo_categories:
        print("\n" + "─" * 70)
        print(f"Demo: /craft:hub {category}")
        print("─" * 70)
        display_category_view(category)

    # Show summary
    print("=" * 70)
    print("✅ Layer 2 Demo Complete")
    print("=" * 70)
    print("\n📝 Features Demonstrated:")
    print("  ✓ Category filtering")
    print("  ✓ Command grouping by subcategory")
    print("  ✓ Mode indicators")
    print("  ✓ Command descriptions")
    print("  ✓ Common workflows")
    print("  ✓ Navigation breadcrumbs")
    print("\n💡 Next: Implement Layer 3 (Command Detail + Tutorials)")


if __name__ == "__main__":
    main()
