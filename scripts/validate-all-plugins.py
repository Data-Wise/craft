#!/usr/bin/env python3
"""
Comprehensive plugin validation script for Claude Code plugins.

Validates:
- Plugin structure (required files and directories)
- JSON files (package.json, plugin.json)
- Command frontmatter (name, description fields)
- No hardcoded paths
- Consistent metadata across plugins

Usage:
    python3 validate-all-plugins.py [--strict]

Exit codes:
    0 - All plugins valid
    1 - Validation errors found
    2 - Critical errors (missing plugins, bad structure)
"""

import json
import re
import sys
from pathlib import Path
from typing import List, Dict, Tuple

# ANSI color codes
GREEN = '\033[92m'
YELLOW = '\033[93m'
RED = '\033[91m'
BLUE = '\033[94m'
RESET = '\033[0m'
BOLD = '\033[1m'

class PluginValidator:
    """Validates Claude Code plugin structure and content."""

    def __init__(self, plugin_path: Path, strict: bool = False):
        self.plugin_path = plugin_path
        self.plugin_name = plugin_path.name
        self.strict = strict
        self.errors = []
        self.warnings = []
        self.info = []

    def validate(self) -> bool:
        """Run all validation checks. Returns True if valid."""
        print(f"\n{BOLD}{'='*60}{RESET}")
        print(f"{BOLD}Validating: {BLUE}{self.plugin_name}{RESET}")
        print(f"{BOLD}{'='*60}{RESET}\n")

        # Run all checks
        self._check_required_files()
        self._validate_package_json()
        self._validate_plugin_json()
        self._validate_commands()
        self._check_hardcoded_paths()
        self._check_consistency()

        # Print results
        self._print_results()

        # Return True if no errors (warnings OK)
        return len(self.errors) == 0

    def _check_required_files(self):
        """Check that all required files exist."""
        required_files = [
            'package.json',
            '.claude-plugin/plugin.json',
            'README.md',
            'LICENSE'
        ]

        for file in required_files:
            file_path = self.plugin_path / file
            if not file_path.exists():
                self.errors.append(f"Missing required file: {file}")
            else:
                self.info.append(f"✓ {file} exists")

        # Check for commands directory (warning if missing)
        commands_dir = self.plugin_path / 'commands'
        if not commands_dir.exists():
            self.warnings.append("No 'commands' directory found")
        else:
            cmd_count = len(list(commands_dir.rglob('*.md')))
            self.info.append(f"✓ Found {cmd_count} command files")

    def _validate_package_json(self):
        """Validate package.json structure and content."""
        pkg_json = self.plugin_path / 'package.json'

        if not pkg_json.exists():
            return  # Already reported in _check_required_files

        try:
            with open(pkg_json) as f:
                pkg_data = json.load(f)

            # Check required fields
            required_fields = ['name', 'version', 'description', 'license', 'repository']
            for field in required_fields:
                if field not in pkg_data:
                    self.errors.append(f"package.json missing required field: {field}")
                else:
                    self.info.append(f"✓ package.json has '{field}'")

            # Validate version format (semver)
            if 'version' in pkg_data:
                version = pkg_data['version']
                if not re.match(r'^\d+\.\d+\.\d+', version):
                    self.warnings.append(f"Version '{version}' may not follow semver")

            # Check for recommended fields
            recommended = ['author', 'keywords']
            for field in recommended:
                if field not in pkg_data:
                    self.warnings.append(f"package.json missing recommended field: {field}")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in package.json: {e}")
        except Exception as e:
            self.errors.append(f"Error reading package.json: {e}")

    def _validate_plugin_json(self):
        """Validate plugin.json structure and content."""
        plugin_json = self.plugin_path / '.claude-plugin' / 'plugin.json'

        if not plugin_json.exists():
            return  # Already reported in _check_required_files

        try:
            with open(plugin_json) as f:
                plugin_data = json.load(f)

            # Check required fields
            required_fields = ['name', 'version', 'description']
            for field in required_fields:
                if field not in plugin_data:
                    self.errors.append(f"plugin.json missing required field: {field}")
                else:
                    self.info.append(f"✓ plugin.json has '{field}'")

        except json.JSONDecodeError as e:
            self.errors.append(f"Invalid JSON in plugin.json: {e}")
        except Exception as e:
            self.errors.append(f"Error reading plugin.json: {e}")

    def _validate_commands(self):
        """Validate command files have proper frontmatter."""
        commands_dir = self.plugin_path / 'commands'

        if not commands_dir.exists():
            return

        cmd_files = list(commands_dir.rglob('*.md'))
        missing_name = []
        missing_desc = []

        for cmd_file in cmd_files:
            try:
                with open(cmd_file, 'r') as f:
                    content = f.read(500)  # First 500 chars

                # Check for frontmatter with name field
                if not re.search(r'^---\s*\nname:\s*.+', content, re.MULTILINE):
                    missing_name.append(cmd_file.relative_to(self.plugin_path))

                # Check for description (recommended)
                if not re.search(r'description:\s*.+', content):
                    missing_desc.append(cmd_file.relative_to(self.plugin_path))

            except Exception as e:
                self.warnings.append(f"Error reading {cmd_file.name}: {e}")

        # Report issues
        if missing_name:
            for f in missing_name[:3]:  # Show first 3
                self.errors.append(f"Command missing 'name:' field: {f}")
            if len(missing_name) > 3:
                self.errors.append(f"... and {len(missing_name) - 3} more")

        if missing_desc:
            for f in missing_desc[:3]:
                self.warnings.append(f"Command missing 'description:' field: {f}")
            if len(missing_desc) > 3:
                self.warnings.append(f"... and {len(missing_desc) - 3} more")

        if not missing_name and not missing_desc:
            self.info.append(f"✓ All {len(cmd_files)} commands have proper frontmatter")

    def _check_hardcoded_paths(self):
        """Check for hardcoded absolute paths."""
        patterns = [
            (r'/Users/[^/\s]+', '/Users/ paths'),
            (r'/home/[^/\s]+', '/home/ paths'),
            (r'C:\\Users\\', 'Windows paths')
        ]

        # Files to skip (documentation, installation guides, etc.)
        skip_files = {
            'README.md', 'LICENSE', 'INSTALL.md', 'INSTALL-PRIVATE.md',
            'TESTING.md', 'DEVELOPMENT.md', 'CHANGELOG.md'
        }

        for pattern, name in patterns:
            for file in self.plugin_path.rglob('*.md'):
                # Skip documentation files
                if file.name in skip_files:
                    continue
                # Skip files in docs/ directory
                if 'docs/' in str(file.relative_to(self.plugin_path)):
                    continue

                try:
                    with open(file, 'r') as f:
                        content = f.read()

                    matches = re.findall(pattern, content)
                    if matches:
                        rel_path = file.relative_to(self.plugin_path)
                        self.errors.append(f"Hardcoded {name} in {rel_path}: {matches[0]}")
                except:
                    pass  # Skip files we can't read

    def _check_consistency(self):
        """Check consistency between package.json and plugin.json."""
        pkg_json = self.plugin_path / 'package.json'
        plugin_json = self.plugin_path / '.claude-plugin' / 'plugin.json'

        if not (pkg_json.exists() and plugin_json.exists()):
            return

        try:
            with open(pkg_json) as f:
                pkg_data = json.load(f)
            with open(plugin_json) as f:
                plugin_data = json.load(f)

            # Check version consistency
            pkg_version = pkg_data.get('version')
            plugin_version = plugin_data.get('version')

            if pkg_version and plugin_version:
                if pkg_version != plugin_version:
                    self.warnings.append(
                        f"Version mismatch: package.json ({pkg_version}) != "
                        f"plugin.json ({plugin_version})"
                    )
                else:
                    self.info.append(f"✓ Consistent version: {pkg_version}")

            # Check name consistency (plugin name should be in package name)
            pkg_name = pkg_data.get('name', '')
            plugin_name = plugin_data.get('name', '')

            if plugin_name and plugin_name not in pkg_name:
                self.warnings.append(
                    f"Plugin name '{plugin_name}' not in package name '{pkg_name}'"
                )

        except:
            pass  # Already reported errors in earlier checks

    def _print_results(self):
        """Print validation results with colors."""
        print()

        # Print errors
        if self.errors:
            print(f"{RED}{BOLD}❌ Errors:{RESET}")
            for error in self.errors:
                print(f"  {RED}• {error}{RESET}")
            print()

        # Print warnings
        if self.warnings:
            print(f"{YELLOW}{BOLD}⚠️  Warnings:{RESET}")
            for warning in self.warnings:
                print(f"  {YELLOW}• {warning}{RESET}")
            print()

        # Print info in verbose mode
        if not self.errors and not self.warnings:
            print(f"{GREEN}{BOLD}✅ All checks passed!{RESET}")
            if self.info:
                print(f"\n{BLUE}Details:{RESET}")
                for info in self.info[:5]:  # Show first 5
                    print(f"  {info}")
                if len(self.info) > 5:
                    print(f"  ... and {len(self.info) - 5} more")

def main():
    """Main validation function."""
    # Check for --strict flag
    strict = '--strict' in sys.argv

    # Find all plugins
    repo_root = Path(__file__).parent.parent
    plugins = ['rforge-orchestrator', 'statistical-research', 'workflow']

    all_valid = True
    results = []

    for plugin_name in plugins:
        plugin_path = repo_root / plugin_name

        if not plugin_path.exists():
            print(f"{RED}❌ Plugin directory not found: {plugin_name}{RESET}")
            all_valid = False
            continue

        validator = PluginValidator(plugin_path, strict)
        is_valid = validator.validate()

        results.append((plugin_name, is_valid, len(validator.errors), len(validator.warnings)))

        if not is_valid:
            all_valid = False

    # Print summary
    print(f"\n{BOLD}{'='*60}{RESET}")
    print(f"{BOLD}VALIDATION SUMMARY{RESET}")
    print(f"{BOLD}{'='*60}{RESET}\n")

    for name, is_valid, error_count, warning_count in results:
        status = f"{GREEN}✅ PASS{RESET}" if is_valid else f"{RED}❌ FAIL{RESET}"
        print(f"  {status}  {name}")
        if error_count > 0:
            print(f"         {RED}{error_count} errors{RESET}")
        if warning_count > 0:
            print(f"         {YELLOW}{warning_count} warnings{RESET}")

    print()

    if all_valid:
        print(f"{GREEN}{BOLD}✅ All plugins validated successfully!{RESET}\n")
        return 0
    else:
        print(f"{RED}{BOLD}❌ Validation failed for one or more plugins{RESET}\n")
        return 1

if __name__ == '__main__':
    sys.exit(main())
