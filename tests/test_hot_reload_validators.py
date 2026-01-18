#!/usr/bin/env python3
"""
Test hot-reload validators in .claude-plugin/skills/validation/.

Validates that hot-reload validators have correct structure:
- Valid YAML frontmatter
- hot_reload: true flag
- context: fork setting
- Mode-aware behavior
- Multi-language support
"""

import sys
import yaml
from pathlib import Path

# Add project root to path
sys.path.insert(0, str(Path(__file__).parent.parent))

VALIDATORS = [
    "test-coverage.md",
    "broken-links.md",
    "lint-check.md"
]


class TestHotReloadValidators:
    """Tests for hot-reload validator infrastructure."""

    def get_validators_dir(self):
        """Get validators directory."""
        plugin_dir = Path(__file__).parent.parent
        return plugin_dir / ".claude-plugin" / "skills" / "validation"

    def parse_frontmatter(self, file_path: Path):
        """Extract and parse YAML frontmatter from markdown file."""
        content = file_path.read_text()

        # Extract frontmatter between --- delimiters
        parts = content.split("---")
        if len(parts) < 3:
            raise ValueError(f"No frontmatter found in {file_path.name}")

        frontmatter_text = parts[1]

        # Parse YAML
        try:
            return yaml.safe_load(frontmatter_text)
        except yaml.YAMLError as e:
            raise ValueError(f"Invalid YAML in {file_path.name}: {e}")

    def test_validator_files_exist(self):
        """All validator files should exist."""
        validators_dir = self.get_validators_dir()

        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            assert path.exists(), f"Validator not found: {validator_file}"

    def test_validator_frontmatter_valid(self):
        """All validators should have valid YAML frontmatter."""
        validators_dir = self.get_validators_dir()

        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            data = self.parse_frontmatter(path)

            # Check required fields
            required_fields = ["name", "description", "category", "version"]
            for field in required_fields:
                assert field in data, \
                    f"Missing '{field}' in {validator_file} frontmatter"

    def test_validator_has_hot_reload_flag(self):
        """All validators should have hot_reload: true."""
        validators_dir = self.get_validators_dir()

        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            data = self.parse_frontmatter(path)

            assert "hot_reload" in data, \
                f"Missing 'hot_reload' field in {validator_file}"
            assert data["hot_reload"] is True, \
                f"hot_reload must be true in {validator_file}, got {data['hot_reload']}"

    def test_validator_uses_fork_context(self):
        """All validators should use context: fork."""
        validators_dir = self.get_validators_dir()

        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            data = self.parse_frontmatter(path)

            assert "context" in data, \
                f"Missing 'context' field in {validator_file}"
            assert data["context"] == "fork", \
                f"context must be 'fork' in {validator_file}, got {data['context']}"

    def test_coverage_validator_mode_aware(self):
        """Coverage validator should have mode-specific thresholds."""
        validators_dir = self.get_validators_dir()
        path = validators_dir / "test-coverage.md"
        content = path.read_text()

        # Check for mode-aware thresholds
        modes_thresholds = {
            "debug": "60",
            "default": "70",
            "optimize": "75",
            "release": "90"
        }

        for mode, threshold in modes_thresholds.items():
            assert mode in content, \
                f"Missing mode '{mode}' in coverage validator"
            assert threshold in content, \
                f"Missing threshold '{threshold}%' for {mode} mode in coverage validator"

    def test_lint_validator_multi_language(self):
        """Lint validator should support multiple languages."""
        validators_dir = self.get_validators_dir()
        path = validators_dir / "lint-check.md"
        content = path.read_text()

        languages = ["Python", "JavaScript", "TypeScript", "R", "Go", "Rust"]
        tools = ["ruff", "eslint", "lintr", "golangci-lint", "clippy"]

        for lang in languages:
            assert lang in content, \
                f"Missing language support: {lang} in lint validator"

        for tool in tools:
            assert tool in content, \
                f"Missing tool reference: {tool} in lint validator"

    def test_broken_links_validator_integration(self):
        """Broken links validator should reference existing test."""
        validators_dir = self.get_validators_dir()
        path = validators_dir / "broken-links.md"
        content = path.read_text()

        # Should reference the existing test
        assert "test_craft_plugin.py" in content, \
            "Broken links validator should reference existing test suite"
        assert "test_no_broken_links" in content or "broken" in content.lower(), \
            "Broken links validator should reference link checking functionality"

    def test_validator_category_is_validation(self):
        """All validators should be in 'validation' category."""
        validators_dir = self.get_validators_dir()

        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            data = self.parse_frontmatter(path)

            assert data.get("category") == "validation", \
                f"Validator {validator_file} should have category: validation, got {data.get('category')}"

    def test_validator_version_format(self):
        """All validators should have semantic version."""
        validators_dir = self.get_validators_dir()
        import re
        version_pattern = r'^\d+\.\d+\.\d+$'

        for validator_file in VALIDATORS:
            path = validators_dir / validator_file
            data = self.parse_frontmatter(path)

            version = data.get("version")
            assert version, \
                f"Missing version in {validator_file}"
            assert re.match(version_pattern, str(version)), \
                f"Version should be semantic (X.Y.Z) in {validator_file}, got {version}"


def run_tests():
    """Run all tests and report results."""
    import time

    test_class = TestHotReloadValidators()
    test_methods = [
        method for method in dir(test_class)
        if method.startswith('test_')
    ]

    print("=" * 80)
    print("Hot-Reload Validator Tests")
    print("=" * 80)

    passed = 0
    failed = 0
    total_time = 0

    for method_name in test_methods:
        method = getattr(test_class, method_name)
        test_name = method_name.replace('test_', '').replace('_', ' ').title()

        try:
            start = time.time()
            method()
            duration = (time.time() - start) * 1000
            total_time += duration

            print(f"✓ {test_name:60} ({duration:.1f}ms)")
            passed += 1

        except AssertionError as e:
            print(f"✗ {test_name:60} FAILED")
            print(f"  {str(e)}")
            failed += 1

        except Exception as e:
            print(f"✗ {test_name:60} ERROR")
            print(f"  {type(e).__name__}: {str(e)}")
            failed += 1

    print("=" * 80)
    print(f"Results: {passed} passed, {failed} failed ({total_time:.1f}ms total)")
    print("=" * 80)

    return failed == 0


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
