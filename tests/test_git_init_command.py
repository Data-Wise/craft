#!/usr/bin/env python3
"""
Test suite for /craft:git:init command implementation
Generated: 2025-01-15

Tests the git:init command structure, documentation, and integration.
Run: python3 tests/test_git_init_command.py
"""

import os
import sys
import re
from pathlib import Path

# Color codes for output
GREEN = '\033[0;32m'
RED = '\033[0;31m'
YELLOW = '\033[0;33m'
BLUE = '\033[0;34m'
BOLD = '\033[1m'
NC = '\033[0m'  # No Color

class TestGitInitCommand:
    def __init__(self):
        self.plugin_root = Path(__file__).parent.parent
        self.passed = 0
        self.failed = 0
        self.skipped = 0

    def log_pass(self, msg):
        """Log a passed test."""
        print(f"{GREEN}✓{NC} {msg}")
        self.passed += 1

    def log_fail(self, msg):
        """Log a failed test."""
        print(f"{RED}✗{NC} {msg}")
        self.failed += 1

    def log_skip(self, msg):
        """Log a skipped test."""
        print(f"{YELLOW}⊘{NC} {msg}")
        self.skipped += 1

    def section(self, name):
        """Print a section header."""
        print(f"\n{BLUE}{BOLD}{'─' * 60}{NC}")
        print(f"{BLUE}{BOLD}{name}{NC}")
        print(f"{BLUE}{BOLD}{'─' * 60}{NC}")

    def test_command_file_exists(self):
        """Test that the git:init command file exists."""
        self.section("Command File Structure")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        if cmd_file.exists():
            self.log_pass(f"Command file exists: {cmd_file.relative_to(self.plugin_root)}")
        else:
            self.log_fail(f"Command file missing: {cmd_file.relative_to(self.plugin_root)}")
            return False

        return True

    def test_frontmatter(self):
        """Test that the command has valid YAML frontmatter."""
        self.section("Command Frontmatter")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        content = cmd_file.read_text()

        # Check for frontmatter
        if content.startswith('---'):
            end_idx = content.find('---', 3)
            if end_idx > 0:
                self.log_pass("Valid YAML frontmatter found")
                frontmatter = content[3:end_idx]

                # Check required fields
                if 'description:' in frontmatter:
                    self.log_pass("Has description field")
                else:
                    self.log_fail("Missing description field")

                if 'arguments:' in frontmatter:
                    self.log_pass("Has arguments field")

                    # Check for specific arguments
                    required_args = ['remote', 'workflow', 'dry-run', 'yes']
                    for arg in required_args:
                        if f'name: {arg}' in frontmatter:
                            self.log_pass(f"  Argument defined: {arg}")
                        else:
                            self.log_fail(f"  Missing argument: {arg}")
                else:
                    self.log_fail("Missing arguments field")
            else:
                self.log_fail("Malformed frontmatter (no closing ---)")
        else:
            self.log_fail("No YAML frontmatter found")

    def test_documentation_sections(self):
        """Test that the command has all required documentation sections."""
        self.section("Documentation Sections")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        content = cmd_file.read_text()

        required_sections = [
            'Quick Start',
            'What It Does',
            'Workflow Patterns',
            'Interactive Wizard',
            'Dry-Run Mode',
            'Error Handling',
            'Integration',
            'Examples',
            'Troubleshooting'
        ]

        for section in required_sections:
            if f'## {section}' in content or f'### {section}' in content:
                self.log_pass(f"Section present: {section}")
            else:
                self.log_fail(f"Section missing: {section}")

    def test_workflow_patterns(self):
        """Test that all three workflow patterns are documented."""
        self.section("Workflow Patterns")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        content = cmd_file.read_text()

        patterns = ['Main + Dev', 'Simple', 'GitFlow']
        for pattern in patterns:
            if pattern in content:
                self.log_pass(f"Workflow pattern documented: {pattern}")
            else:
                self.log_fail(f"Workflow pattern missing: {pattern}")

    def test_wizard_steps(self):
        """Test that all 9 wizard steps are documented."""
        self.section("Interactive Wizard Steps")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        content = cmd_file.read_text()

        steps = [
            'Step 1: Repository Check',
            'Step 2: Remote Setup',
            'Step 3: Branch Structure',
            'Step 4: Branch Protection',
            'Step 5: CI Workflow',
            'Step 6: Project Files',
            'Step 7: Initial Commit',
            'Step 8: Push to Remote',
            'Step 9: Validation'
        ]

        for step in steps:
            if f'### {step}' in content:
                self.log_pass(f"Wizard step documented: {step}")
            else:
                self.log_fail(f"Wizard step missing: {step}")

    def test_template_files(self):
        """Test that all template files exist."""
        self.section("Template Files")

        templates_dir = self.plugin_root / "templates" / "git-init"

        if templates_dir.exists():
            self.log_pass(f"Templates directory exists: {templates_dir.relative_to(self.plugin_root)}")
        else:
            self.log_fail(f"Templates directory missing: {templates_dir.relative_to(self.plugin_root)}")
            return

        required_templates = [
            'STATUS-template.yaml',
            'CLAUDE-template.md',
            'pull_request_template.md'
        ]

        for template in required_templates:
            template_file = templates_dir / template
            if template_file.exists():
                self.log_pass(f"Template exists: {template}")

                # Check for placeholders
                content = template_file.read_text()
                if '{{USER}}' in content or '{{REPO}}' in content or '{{PROJECT_NAME}}' in content:
                    self.log_pass(f"  Template has placeholders")
                else:
                    self.log_skip(f"  No placeholders in template (may be intentional)")
            else:
                self.log_fail(f"Template missing: {template}")

    def test_hub_integration(self):
        """Test that the command is registered in hub.md."""
        self.section("Hub Integration")

        hub_file = self.plugin_root / "commands" / "hub.md"
        content = hub_file.read_text()

        if '/craft:git:init' in content:
            self.log_pass("Command listed in hub.md")
        else:
            self.log_fail("Command not listed in hub.md")

        if 'GIT COMMANDS (5 commands' in content:
            self.log_pass("Git commands count updated (5 commands)")
        elif 'GIT COMMANDS (4 commands' in content:
            self.log_fail("Git commands count not updated (still shows 4)")
        else:
            self.log_skip("Could not verify git commands count")

    def test_getting_started_integration(self):
        """Test that the command is mentioned in getting-started guide."""
        self.section("Getting Started Guide")

        guide_file = self.plugin_root / "docs" / "guide" / "getting-started.md"

        if guide_file.exists():
            content = guide_file.read_text()

            if '/craft:git:init' in content:
                self.log_pass("Command mentioned in getting-started.md")
            else:
                self.log_fail("Command not mentioned in getting-started.md")

            if 'Initialize a New Project' in content:
                self.log_pass("Initialization section present")
            else:
                self.log_fail("Initialization section missing")
        else:
            self.log_skip("getting-started.md not found")

    def test_smart_routing(self):
        """Test that smart routing phrases are documented."""
        self.section("Smart Routing")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        content = cmd_file.read_text()

        phrases = [
            'initialize project',
            'set up git',
            'create repository',
            'bootstrap project',
            'new project setup'
        ]

        routing_section = False
        for phrase in phrases:
            if phrase in content.lower():
                if not routing_section:
                    self.log_pass("Smart routing phrases documented")
                    routing_section = True
                break

        if not routing_section:
            self.log_fail("No smart routing phrases found")

    def test_related_commands(self):
        """Test that related commands are documented."""
        self.section("Related Commands")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        content = cmd_file.read_text()

        related = [
            '/craft:git:worktree',
            '/craft:git:branch',
            '/craft:git:clean',
            '/craft:ci:generate',
            '/craft:check'
        ]

        for cmd in related:
            if cmd in content:
                self.log_pass(f"Related command mentioned: {cmd}")
            else:
                self.log_fail(f"Related command missing: {cmd}")

    def test_error_handling(self):
        """Test that error handling and rollback are documented."""
        self.section("Error Handling")

        cmd_file = self.plugin_root / "commands" / "git" / "init.md"
        content = cmd_file.read_text()

        if 'rollback' in content.lower():
            self.log_pass("Rollback strategy documented")
        else:
            self.log_fail("No rollback strategy mentioned")

        if 'Error Handling' in content:
            self.log_pass("Error handling section present")
        else:
            self.log_fail("Error handling section missing")

    def test_plugin_json_count(self):
        """Test that plugin.json has updated command count."""
        self.section("Plugin Manifest")

        plugin_json = self.plugin_root / ".claude-plugin" / "plugin.json"
        content = plugin_json.read_text()

        # Look for command count in description
        if '90 commands' in content:
            self.log_pass("Command count updated to 90 in plugin.json")
        elif '89 commands' in content:
            self.log_fail("Command count not updated (still shows 89)")
        else:
            self.log_skip("Could not verify command count in plugin.json")

    def run_all_tests(self):
        """Run all tests and print summary."""
        print(f"\n{BOLD}Testing /craft:git:init Command Implementation{NC}")
        print(f"{BOLD}Generated: 2025-01-15{NC}\n")

        # Run all tests
        if self.test_command_file_exists():
            self.test_frontmatter()
            self.test_documentation_sections()
            self.test_workflow_patterns()
            self.test_wizard_steps()

        self.test_template_files()
        self.test_hub_integration()
        self.test_getting_started_integration()
        self.test_smart_routing()
        self.test_related_commands()
        self.test_error_handling()
        self.test_plugin_json_count()

        # Print summary
        self.section("Test Summary")
        total = self.passed + self.failed + self.skipped
        print(f"\n{BOLD}Results:{NC}")
        print(f"  {GREEN}Passed:{NC}  {self.passed}/{total}")
        print(f"  {RED}Failed:{NC}  {self.failed}/{total}")
        print(f"  {YELLOW}Skipped:{NC} {self.skipped}/{total}")

        if self.failed > 0:
            print(f"\n{RED}{BOLD}FAIL: {self.failed} test(s) failed{NC}")
            return 1
        elif self.passed == 0:
            print(f"\n{YELLOW}{BOLD}SKIP: No tests passed{NC}")
            return 2
        else:
            print(f"\n{GREEN}{BOLD}PASS: All tests passed!{NC}")
            return 0

if __name__ == "__main__":
    tester = TestGitInitCommand()
    sys.exit(tester.run_all_tests())
