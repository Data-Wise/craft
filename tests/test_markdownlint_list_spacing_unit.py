#!/usr/bin/env python3
"""
Unit tests for markdownlint list spacing rules (MD030, MD004, MD032).

Tests individual rule configurations, spacing normalization, and marker style enforcement.
"""

import json
import subprocess
import tempfile
from pathlib import Path
import pytest


class TestMD030ListSpacing:
    """Tests for MD030 rule (spaces after list markers)."""

    def get_config(self):
        """Load markdownlint config."""
        config_path = Path(__file__).parent.parent / ".markdownlint.json"
        with open(config_path) as f:
            return json.load(f)

    def test_md030_config_exists(self):
        """MD030 rule should be configured."""
        config = self.get_config()
        assert "MD030" in config, "MD030 rule not found in config"

    def test_md030_ul_single_one_space(self):
        """Unordered single-line lists should have 1 space."""
        config = self.get_config()
        assert config["MD030"]["ul_single"] == 1, (
            "MD030 ul_single should be 1, got {0}".format(config["MD030"]["ul_single"])
        )

    def test_md030_ol_single_one_space(self):
        """Ordered single-line lists should have 1 space."""
        config = self.get_config()
        assert config["MD030"]["ol_single"] == 1, (
            "MD030 ol_single should be 1, got {0}".format(config["MD030"]["ol_single"])
        )

    def test_md030_ul_multi_one_space(self):
        """Unordered multi-line lists should have 1 space."""
        config = self.get_config()
        assert config["MD030"]["ul_multi"] == 1, (
            "MD030 ul_multi should be 1, got {0}".format(config["MD030"]["ul_multi"])
        )

    def test_md030_ol_multi_one_space(self):
        """Ordered multi-line lists should have 1 space."""
        config = self.get_config()
        assert config["MD030"]["ol_multi"] == 1, (
            "MD030 ol_multi should be 1, got {0}".format(config["MD030"]["ol_multi"])
        )

    def test_md030_detects_two_spaces(self):
        """MD030 should detect 2 spaces after marker."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n-  Item with 2 spaces\n")
            temp_path = f.name

        try:
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD030" in result.stdout or "MD030" in result.stderr, (
                "MD030 should detect 2 spaces after marker"
            )
        finally:
            Path(temp_path).unlink()

    def test_md030_autofixes_two_spaces(self):
        """MD030 auto-fix should reduce 2 spaces to 1."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n-  Item with 2 spaces\n")
            temp_path = f.name

        try:
            # Run auto-fix
            subprocess.run(
                ["npx", "-y", "markdownlint-cli2", "--fix", temp_path],
                capture_output=True,
            )

            # Read fixed content
            content = Path(temp_path).read_text()

            # Should have 1 space after marker
            assert (
                "- Item with 2 spaces" in content or "-Item with 2 spaces" in content
            ), "Auto-fix should normalize to 1 space: {0}".format(content)

            # Verify no violations remain
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD030" not in result.stdout and "MD030" not in result.stderr, (
                "MD030 violations should be fixed: {0}".format(result.stdout)
            )
        finally:
            Path(temp_path).unlink()


class TestMD004MarkerStyle:
    """Tests for MD004 rule (consistent list marker style)."""

    def get_config(self):
        """Load markdownlint config."""
        config_path = Path(__file__).parent.parent / ".markdownlint.json"
        with open(config_path) as f:
            return json.load(f)

    def test_md004_config_exists(self):
        """MD004 rule should be configured."""
        config = self.get_config()
        assert "MD004" in config, "MD004 rule not found in config"

    def test_md004_style_is_dash(self):
        """MD004 should enforce dash style."""
        config = self.get_config()
        assert "style" in config["MD004"], "MD004 missing 'style' key: {0}".format(
            config["MD004"]
        )
        assert config["MD004"]["style"] == "dash", (
            "MD004 style should be 'dash', got {0}".format(config["MD004"]["style"])
        )

    def test_md004_detects_asterisk_marker(self):
        """MD004 should detect asterisk markers."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n* Item with asterisk\n")
            temp_path = f.name

        try:
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD004" in result.stdout or "MD004" in result.stderr, (
                "MD004 should detect asterisk marker"
            )
        finally:
            Path(temp_path).unlink()

    def test_md004_detects_plus_marker(self):
        """MD004 should detect plus markers."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n+ Item with plus\n")
            temp_path = f.name

        try:
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD004" in result.stdout or "MD004" in result.stderr, (
                "MD004 should detect plus marker"
            )
        finally:
            Path(temp_path).unlink()

    def test_md004_autofixes_asterisk_to_dash(self):
        """MD004 auto-fix should change asterisk to dash."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n* Item with asterisk\n")
            temp_path = f.name

        try:
            # Run auto-fix
            subprocess.run(
                ["npx", "-y", "markdownlint-cli2", "--fix", temp_path],
                capture_output=True,
            )

            # Read fixed content
            content = Path(temp_path).read_text()

            # Should have dash marker
            assert (
                "- Item with asterisk" in content or "-Item with asterisk" in content
            ), "Auto-fix should change to dash: {0}".format(content)

            # Verify no violations remain
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD004" not in result.stdout and "MD004" not in result.stderr, (
                "MD004 violations should be fixed: {0}".format(result.stdout)
            )
        finally:
            Path(temp_path).unlink()

    def test_md004_autofixes_plus_to_dash(self):
        """MD004 auto-fix should change plus to dash."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n+ Item with plus\n")
            temp_path = f.name

        try:
            # Run auto-fix
            subprocess.run(
                ["npx", "-y", "markdownlint-cli2", "--fix", temp_path],
                capture_output=True,
            )

            # Read fixed content
            content = Path(temp_path).read_text()

            # Should have dash marker
            assert "- Item with plus" in content or "-Item with plus" in content, (
                "Auto-fix should change to dash: {0}".format(content)
            )

            # Verify no violations remain
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD004" not in result.stdout and "MD004" not in result.stderr, (
                "MD004 violations should be fixed: {0}".format(result.stdout)
            )
        finally:
            Path(temp_path).unlink()


class TestMD032BlankLines:
    """Tests for MD032 rule (blank lines around lists)."""

    def get_config(self):
        """Load markdownlint config."""
        config_path = Path(__file__).parent.parent / ".markdownlint.json"
        with open(config_path) as f:
            return json.load(f)

    def test_md032_config_exists(self):
        """MD032 rule should be configured."""
        config = self.get_config()
        assert "MD032" in config, "MD032 rule not found in config"

    def test_md032_enabled(self):
        """MD032 should be enabled."""
        config = self.get_config()
        assert config["MD032"] is True, "MD032 should be True, got {0}".format(
            config["MD032"]
        )

    def test_md032_detects_missing_blank_line_before(self):
        """MD032 should detect missing blank line before list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n- Item without blank line\n")
            temp_path = f.name

        try:
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD032" in result.stdout or "MD032" in result.stderr, (
                "MD032 should detect missing blank line"
            )
        finally:
            Path(temp_path).unlink()

    def test_md032_autofixes_blank_line_before(self):
        """MD032 auto-fix should add blank line before list."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n- Item without blank line\n")
            temp_path = f.name

        try:
            # Run auto-fix
            subprocess.run(
                ["npx", "-y", "markdownlint-cli2", "--fix", temp_path],
                capture_output=True,
            )

            # Read fixed content
            content = Path(temp_path).read_text()

            # Should have blank line before list
            assert "\n\n- Item without blank line" in content, (
                "Auto-fix should add blank line: {0}".format(content)
            )

            # Verify no violations remain
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD032" not in result.stdout and "MD032" not in result.stderr, (
                "MD032 violations should be fixed: {0}".format(result.stdout)
            )
        finally:
            Path(temp_path).unlink()


class TestNestedLists:
    """Tests for nested list handling."""

    def test_nested_list_spacing_consistent(self):
        """Nested lists should also follow spacing rules."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n- Parent\n  -  Child with 2 spaces\n")
            temp_path = f.name

        try:
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD030" in result.stdout or "MD030" in result.stderr, (
                "MD030 should detect spacing in nested lists"
            )
        finally:
            Path(temp_path).unlink()

    def test_nested_list_autofix(self):
        """Auto-fix should normalize nested list spacing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n- Parent\n  -  Child with 2 spaces\n")
            temp_path = f.name

        try:
            # Run auto-fix
            subprocess.run(
                ["npx", "-y", "markdownlint-cli2", "--fix", temp_path],
                capture_output=True,
            )

            # Read fixed content
            content = Path(temp_path).read_text()

            # Should have 1 space after nested marker
            assert "  - Child with 2 spaces" in content, (
                "Auto-fix should normalize nested spacing: {0}".format(content)
            )

            # Verify no violations remain
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD030" not in result.stdout and "MD030" not in result.stderr, (
                "MD030 violations should be fixed: {0}".format(result.stdout)
            )
        finally:
            Path(temp_path).unlink()


class TestOrderedLists:
    """Tests for ordered list handling."""

    def test_ordered_list_spacing(self):
        """Ordered lists should also follow spacing rules."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n1.  Item with 2 spaces\n")
            temp_path = f.name

        try:
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD030" in result.stdout or "MD030" in result.stderr, (
                "MD030 should detect ordered list spacing"
            )
        finally:
            Path(temp_path).unlink()

    def test_ordered_list_autofix(self):
        """Auto-fix should normalize ordered list spacing."""
        with tempfile.NamedTemporaryFile(mode="w", suffix=".md", delete=False) as f:
            f.write("## Test\n\n1.  Item with 2 spaces\n")
            temp_path = f.name

        try:
            # Run auto-fix
            subprocess.run(
                ["npx", "-y", "markdownlint-cli2", "--fix", temp_path],
                capture_output=True,
            )

            # Read fixed content
            content = Path(temp_path).read_text()

            # Should have 1 space after number
            assert "1. Item with 2 spaces" in content, (
                "Auto-fix should normalize ordered spacing: {0}".format(content)
            )

            # Verify no violations remain
            result = subprocess.run(
                ["npx", "-y", "markdownlint-cli2", temp_path],
                capture_output=True,
                text=True,
            )
            assert "MD030" not in result.stdout and "MD030" not in result.stderr, (
                "MD030 violations should be fixed: {0}".format(result.stdout)
            )
        finally:
            Path(temp_path).unlink()
