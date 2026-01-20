#!/usr/bin/env python3
"""
Validation tests for markdownlint list spacing configuration.

Tests config validity, structure, and integration with markdownlint-cli2.
"""

import json
import subprocess
import sys
import tempfile
from pathlib import Path


class TestConfigValidity:
    """Tests for .markdownlint.json validity."""

    def get_config_path(self):
        """Get config file path."""
        return Path(__file__).parent.parent / ".markdownlint.json"

    def load_config(self):
        """Load and parse config."""
        config_path = self.get_config_path()
        with open(config_path) as f:
            return json.load(f)

    def test_config_file_exists(self):
        """Config file should exist."""
        config_path = self.get_config_path()
        assert config_path.exists(), "Config file not found: {0}".format(config_path)

    def test_config_valid_json(self):
        """Config should be valid JSON."""
        config = self.load_config()
        assert isinstance(config, dict), "Config should be a dict"

    def test_config_has_schema(self):
        """Config should have schema reference."""
        config = self.load_config()
        assert "$schema" in config, "Config missing $schema reference"

    def test_schema_url_valid(self):
        """Schema URL should be valid."""
        config = self.load_config()
        schema = config["$schema"]
        # Schema can use github.com or raw.githubusercontent.com
        valid_patterns = [
            "github.com/DavidAnson/markdownlint",
            "raw.githubusercontent.com/DavidAnson/markdownlint",
        ]
        assert any(pattern in schema for pattern in valid_patterns), (
            "Invalid schema URL: {0}".format(schema)
        )

    def test_default_enabled(self):
        """Default rules should be enabled."""
        config = self.load_config()
        assert "default" in config, "Config missing 'default' key"
        assert config["default"] is True, "default should be True, got {0}".format(
            config["default"]
        )

    def test_linter_accepts_config(self):
        """markdownlint-cli2 should accept the config."""
        config_path = self.get_config_path()

        # Create a test file to lint
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n- Item\n")
            temp_path = f.name

        try:
            result = subprocess.run(
                [
                    "npx",
                    "-y",
                    "markdownlint-cli2",
                    "--config",
                    str(config_path),
                    temp_path,
                ],
                capture_output=True,
                text=True,
            )

            # Return code 0 means no violations, 1 means violations found - both are OK
            assert result.returncode in [0, 1], (
                "markdownlint-cli2 rejected config: {0}".format(result.stderr)
            )
        finally:
            Path(temp_path).unlink()


class TestMD030Validation:
    """Tests for MD030 rule configuration."""

    def get_config(self):
        """Load markdownlint config."""
        config_path = Path(__file__).parent.parent / ".markdownlint.json"
        with open(config_path) as f:
            return json.load(f)

    def test_md030_exists(self):
        """MD030 rule should exist in config."""
        config = self.get_config()
        assert "MD030" in config, "MD030 rule not found in config"

    def test_md030_is_dict(self):
        """MD030 should be a dict with configuration."""
        config = self.get_config()
        assert isinstance(config["MD030"], dict), (
            "MD030 should be a dict, got {0}".format(type(config["MD030"]))
        )

    def test_md030_ul_single_exists(self):
        """MD030 should have ul_single configuration."""
        config = self.get_config()
        assert "ul_single" in config["MD030"], "MD030 missing 'ul_single' key"

    def test_md030_ul_single_is_integer(self):
        """MD030 ul_single should be an integer."""
        config = self.get_config()
        assert isinstance(config["MD030"]["ul_single"], int), (
            "ul_single should be int, got {0}".format(
                type(config["MD030"]["ul_single"])
            )
        )

    def test_md030_ul_single_range(self):
        """MD030 ul_single should be between 0 and 3."""
        config = self.get_config()
        value = config["MD030"]["ul_single"]
        assert 0 <= value <= 3, "ul_single should be 0-3, got {0}".format(value)

    def test_md030_ol_single_exists(self):
        """MD030 should have ol_single configuration."""
        config = self.get_config()
        assert "ol_single" in config["MD030"], "MD030 missing 'ol_single' key"

    def test_md030_ol_single_is_integer(self):
        """MD030 ol_single should be an integer."""
        config = self.get_config()
        assert isinstance(config["MD030"]["ol_single"], int), (
            "ol_single should be int, got {0}".format(
                type(config["MD030"]["ol_single"])
            )
        )

    def test_md030_ol_single_range(self):
        """MD030 ol_single should be between 0 and 3."""
        config = self.get_config()
        value = config["MD030"]["ol_single"]
        assert 0 <= value <= 3, "ol_single should be 0-3, got {0}".format(value)

    def test_md030_ul_multi_exists(self):
        """MD030 should have ul_multi configuration."""
        config = self.get_config()
        assert "ul_multi" in config["MD030"], "MD030 missing 'ul_multi' key"

    def test_md030_ul_multi_is_integer(self):
        """MD030 ul_multi should be an integer."""
        config = self.get_config()
        assert isinstance(config["MD030"]["ul_multi"], int), (
            "ul_multi should be int, got {0}".format(type(config["MD030"]["ul_multi"]))
        )

    def test_md030_ul_multi_range(self):
        """MD030 ul_multi should be between 0 and 3."""
        config = self.get_config()
        value = config["MD030"]["ul_multi"]
        assert 0 <= value <= 3, "ul_multi should be 0-3, got {0}".format(value)

    def test_md030_ol_multi_exists(self):
        """MD030 should have ol_multi configuration."""
        config = self.get_config()
        assert "ol_multi" in config["MD030"], "MD030 missing 'ol_multi' key"

    def test_md030_ol_multi_is_integer(self):
        """MD030 ol_multi should be an integer."""
        config = self.get_config()
        assert isinstance(config["MD030"]["ol_multi"], int), (
            "ol_multi should be int, got {0}".format(type(config["MD030"]["ol_multi"]))
        )

    def test_md030_ol_multi_range(self):
        """MD030 ol_multi should be between 0 and 3."""
        config = self.get_config()
        value = config["MD030"]["ol_multi"]
        assert 0 <= value <= 3, "ol_multi should be 0-3, got {0}".format(value)


class TestMD004Validation:
    """Tests for MD004 rule configuration."""

    def get_config(self):
        """Load markdownlint config."""
        config_path = Path(__file__).parent.parent / ".markdownlint.json"
        with open(config_path) as f:
            return json.load(f)

    def test_md004_exists(self):
        """MD004 rule should exist in config."""
        config = self.get_config()
        assert "MD004" in config, "MD004 rule not found in config"

    def test_md004_is_dict(self):
        """MD004 should be a dict with configuration."""
        config = self.get_config()
        assert isinstance(config["MD004"], dict), (
            "MD004 should be a dict, got {0}".format(type(config["MD004"]))
        )

    def test_md004_style_exists(self):
        """MD004 should have style configuration."""
        config = self.get_config()
        assert "style" in config["MD004"], "MD004 missing 'style' key"

    def test_md004_style_is_string(self):
        """MD004 style should be a string."""
        config = self.get_config()
        assert isinstance(config["MD004"]["style"], str), (
            "style should be str, got {0}".format(type(config["MD004"]["style"]))
        )

    def test_md004_style_valid_value(self):
        """MD004 style should be a valid value."""
        config = self.get_config()
        style = config["MD004"]["style"]
        valid_styles = ["dash", "asterisk", "plus", "consistent"]
        assert style in valid_styles, (
            "Invalid style '{0}', should be one of: {1}".format(style, valid_styles)
        )

    def test_md004_style_is_dash(self):
        """MD004 style should be 'dash' (project standard)."""
        config = self.get_config()
        assert config["MD004"]["style"] == "dash", (
            "style should be 'dash', got {0}".format(config["MD004"]["style"])
        )


class TestMD032Validation:
    """Tests for MD032 rule configuration."""

    def get_config(self):
        """Load markdownlint config."""
        config_path = Path(__file__).parent.parent / ".markdownlint.json"
        with open(config_path) as f:
            return json.load(f)

    def test_md032_exists(self):
        """MD032 rule should exist in config."""
        config = self.get_config()
        assert "MD032" in config, "MD032 rule not found in config"

    def test_md032_is_boolean(self):
        """MD032 should be a boolean."""
        config = self.get_config()
        assert isinstance(config["MD032"], bool), (
            "MD032 should be bool, got {0}".format(type(config["MD032"]))
        )

    def test_md032_enabled(self):
        """MD032 should be enabled."""
        config = self.get_config()
        assert config["MD032"] is True, "MD032 should be True, got {0}".format(
            config["MD032"]
        )


class TestIntegrationWithDefaultRules:
    """Tests for integration with existing markdownlint config."""

    def get_config(self):
        """Load markdownlint config."""
        config_path = Path(__file__).parent.parent / ".markdownlint.json"
        with open(config_path) as f:
            return json.load(f)

    def test_md013_disabled(self):
        """MD013 (line length) should be disabled (project convention)."""
        config = self.get_config()
        assert "MD013" in config, "MD013 not found in config"
        assert config["MD013"] is False, "MD013 should be False, got {0}".format(
            config["MD013"]
        )

    def test_md033_configured(self):
        """MD033 (HTML elements) should be configured."""
        config = self.get_config()
        assert "MD033" in config, "MD033 not found in config"
        assert isinstance(config["MD033"], dict), (
            "MD033 should be a dict, got {0}".format(type(config["MD033"]))
        )

    def test_md033_has_allowed_elements(self):
        """MD033 should have allowed_elements list."""
        config = self.get_config()
        assert "allowed_elements" in config["MD033"], (
            "MD033 missing 'allowed_elements' key"
        )
        assert isinstance(config["MD033"]["allowed_elements"], list), (
            "allowed_elements should be a list"
        )

    def test_md024_configured(self):
        """MD024 (headings) should be configured."""
        config = self.get_config()
        assert "MD024" in config, "MD024 not found in config"
        assert isinstance(config["MD024"], dict), (
            "MD024 should be a dict, got {0}".format(type(config["MD024"]))
        )

    def test_md024_siblings_only(self):
        """MD024 should have siblings_only: true."""
        config = self.get_config()
        assert config["MD024"]["siblings_only"] is True, (
            "MD024 should have siblings_only=True, got {0}".format(config["MD024"])
        )

    def test_md041_disabled(self):
        """MD041 (first heading) should be disabled."""
        config = self.get_config()
        assert "MD041" in config, "MD041 not found in config"
        assert config["MD041"] is False, "MD041 should be False, got {0}".format(
            config["MD041"]
        )

    def test_md049_disabled(self):
        """MD049 (emphasis style) should be disabled."""
        config = self.get_config()
        assert "MD049" in config, "MD049 not found in config"
        assert config["MD049"] is False, "MD049 should be False, got {0}".format(
            config["MD049"]
        )

    def test_md050_disabled(self):
        """MD050 (strong style) should be disabled."""
        config = self.get_config()
        assert "MD050" in config, "MD050 not found in config"
        assert config["MD050"] is False, "MD050 should be False, got {0}".format(
            config["MD050"]
        )

    def test_new_rules_dont_break_existing(self):
        """New rules should not break existing config structure."""
        config = self.get_config()

        # Check that all keys are valid
        valid_keys = [
            "$schema",
            "default",
            "MD013",
            "MD033",
            "MD024",
            "MD041",
            "MD049",
            "MD050",
            "MD030",
            "MD004",
            "MD032",
        ]
        for key in config.keys():
            assert key in valid_keys, "Unexpected config key: {0}".format(key)

    def test_config_completeness(self):
        """Config should have all required keys."""
        config = self.get_config()
        required_keys = ["$schema", "default", "MD030", "MD004", "MD032"]
        for key in required_keys:
            assert key in config, "Config missing required key: {0}".format(key)


class TestMarkdownlintCLI2Availability:
    """Tests for markdownlint-cli2 availability and version."""

    def test_npx_available(self):
        """npx should be available."""
        result = subprocess.run(["npx", "--version"], capture_output=True, text=True)
        assert result.returncode == 0, "npx not available: {0}".format(result.stderr)

    def test_markdownlint_cli2_available(self):
        """markdownlint-cli2 should be available via npx."""
        result = subprocess.run(
            ["npx", "-y", "markdownlint-cli2", "--version"],
            capture_output=True,
            text=True,
        )
        assert result.returncode == 0, "markdownlint-cli2 not available: {0}".format(
            result.stderr
        )

    def test_markdownlint_cli2_version_output(self):
        """markdownlint-cli2 should output version information."""
        result = subprocess.run(
            ["npx", "-y", "markdownlint-cli2", "--version"],
            capture_output=True,
            text=True,
        )
        output = result.stdout + result.stderr
        assert "markdownlint-cli2" in output, (
            "Version info missing in output: {0}".format(output)
        )


if __name__ == "__main__":
    import pytest

    sys.exit(pytest.main([__file__, "-v"]))
