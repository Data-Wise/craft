#!/usr/bin/env python3
"""
Focused End-to-End Hub v2.0 Workflow Tests
==========================================
Validates complete user workflows through all 3 layers.

Run with: python tests/test_hub_e2e_focused.py
"""

import sys
from pathlib import Path
from datetime import datetime

sys.path.insert(0, str(Path(__file__).parent.parent))
from commands._discovery import (
    load_cached_commands,
    get_commands_by_category,
    get_category_info,
    get_command_detail,
    generate_command_tutorial
)


class TestE2EWorkflows:
    """Test complete user workflows (focused set)."""

    def __init__(self):
        self.passed = 0
        self.failed = 0

    def run_test(self, test_name, test_func):
        """Run a single test and track results."""
        try:
            start = datetime.now()
            test_func()
            duration = (datetime.now() - start).total_seconds() * 1000
            self.passed += 1
            print(f"  ✅ PASS ({duration:.1f}ms) - {test_name}")
        except AssertionError as e:
            self.failed += 1
            print(f"  ❌ FAIL - {test_name}: {e}")
        except Exception as e:
            self.failed += 1
            print(f"  ❌ ERROR - {test_name}: {e}")

    def test_workflow_browse_by_category(self):
        """
        User Workflow: Browse commands by category.

        Steps:
        1. User invokes /craft:hub
        2. Sees main menu with 16 categories
        3. Selects 'code' category
        4. Sees all code commands grouped
        """
        # Layer 1: Main menu
        commands = load_cached_commands()
        categories = set(cmd['category'] for cmd in commands)
        assert len(categories) == 16, f"Expected 16 categories, got {len(categories)}"

        # Layer 2: Category view
        code_commands = get_commands_by_category('code')
        assert len(code_commands) > 0, "No code commands found"

        # Verify category info complete
        category_info = get_category_info('code')
        assert category_info['count'] == len(code_commands)
        assert 'icon' in category_info

    def test_workflow_search_specific_command(self):
        """
        User Workflow: Search for specific command.

        Steps:
        1. User wants to find 'git:worktree' command
        2. Navigates to git category
        3. Finds git:worktree in list
        4. Views command detail
        """
        # Layer 2: Find in category
        git_commands = get_commands_by_category('git')
        worktree_cmd = next(
            (c for c in git_commands if 'worktree' in c['name']),
            None
        )
        assert worktree_cmd is not None, "git:worktree not found"

        # Layer 3: View detail
        detail = get_command_detail('git:worktree')
        assert detail is not None, "Command detail not found"
        assert detail['name'] == 'git:worktree'

    def test_workflow_learn_with_tutorial(self):
        """
        User Workflow: Learn how to use a command.

        Steps:
        1. User finds 'code:lint' command
        2. Views command detail
        3. Sees auto-generated tutorial
        4. Understands how to use command
        """
        # Get command detail
        detail = get_command_detail('code:lint')
        assert detail is not None, "code:lint not found"

        # Generate tutorial
        tutorial = generate_command_tutorial(detail)
        assert len(tutorial) > 0, "Tutorial generation failed"
        assert 'COMMAND: /craft:code:lint' in tutorial

        # Verify tutorial sections
        assert 'DESCRIPTION' in tutorial
        assert 'BASIC USAGE' in tutorial

    def test_workflow_discover_related_commands(self):
        """
        User Workflow: Discover related commands.

        Steps:
        1. User learns about a command
        2. Sees related commands section
        3. Can navigate to related commands
        """
        # Get all commands
        commands = load_cached_commands()

        # Find command with related commands
        cmd_with_related = None
        for cmd in commands:
            if 'related_commands' in cmd and len(cmd['related_commands']) > 0:
                cmd_with_related = cmd
                break

        if cmd_with_related:
            related = cmd_with_related['related_commands']
            assert len(related) > 0, "No related commands found"

            # Verify related commands exist
            for rel_cmd in related:
                rel_detail = get_command_detail(rel_cmd)
                assert rel_detail is not None, f"Related command {rel_cmd} not found"

    def test_progressive_disclosure(self):
        """
        User Workflow: Progressive disclosure prevents overwhelm.

        Steps:
        1. New user runs /craft:hub
        2. Sees organized categories (not all 97 commands)
        3. Can drill down gradually
        """
        # Main menu shows categories (not all commands)
        commands = load_cached_commands()
        categories = set(cmd['category'] for cmd in commands)
        assert len(categories) <= 20, "Too many categories shown"

        # Each category has manageable number of commands
        for category in list(categories)[:5]:  # Sample 5 categories
            cat_commands = get_commands_by_category(category)
            # Most categories should be < 30 commands
            assert len(cat_commands) < 30, f"Category {category} has too many commands"

    def test_navigation_breadcrumbs(self):
        """
        User Workflow: Navigate back through layers.

        Steps:
        1. User drills down to command detail (Layer 3)
        2. Sees breadcrumbs for navigation back
        3. Can navigate up hierarchy
        """
        # Get command detail
        detail = get_command_detail('code:lint')
        tutorial = generate_command_tutorial(detail)

        # Verify breadcrumbs in tutorial
        assert 'Back to' in tutorial.upper() or 'hub' in tutorial.lower(), \
            "No navigation breadcrumbs found"


def main():
    """Run focused E2E workflow tests."""
    print("=" * 70)
    print("🧪 Hub v2.0 E2E Workflow Tests (Focused)")
    print("=" * 70)
    print()

    tester = TestE2EWorkflows()

    # Run focused set of tests
    tests = [
        ("Browse by category", tester.test_workflow_browse_by_category),
        ("Search specific command", tester.test_workflow_search_specific_command),
        ("Learn with tutorial", tester.test_workflow_learn_with_tutorial),
        ("Discover related commands", tester.test_workflow_discover_related_commands),
        ("Progressive disclosure", tester.test_progressive_disclosure),
        ("Navigation breadcrumbs", tester.test_navigation_breadcrumbs),
    ]

    for test_name, test_func in tests:
        tester.run_test(test_name, test_func)

    print()
    print("=" * 70)
    print(f"📊 Results: {tester.passed}/{len(tests)} tests passed")
    print("=" * 70)

    if tester.failed > 0:
        print(f"\n❌ {tester.failed} test(s) failed")
        return 1
    else:
        print("\n✅ All E2E workflow tests passed!")
        return 0


if __name__ == '__main__':
    sys.exit(main())
