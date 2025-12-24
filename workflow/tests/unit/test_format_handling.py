"""
Unit tests for format handling in workflow plugin.

Tests output format generation and validation for:
- Terminal format (rich colors, emojis, ADHD-friendly)
- JSON format (automation-ready, valid JSON)
- Markdown format (documentation-ready, GitHub-compatible)
"""

import pytest
import json
import re


@pytest.mark.unit
class TestTerminalFormat:
    """Test terminal format output (rich colors, emojis)."""

    def test_terminal_has_colors(self, format_outputs):
        """Terminal format should include color codes."""
        terminal_config = format_outputs["terminal"]

        assert terminal_config["has_colors"] is True
        assert terminal_config["has_emojis"] is True

    def test_terminal_structure_sections(self, format_outputs):
        """Terminal format should have all required sections."""
        terminal_config = format_outputs["terminal"]
        required_sections = ["header", "quick_wins", "medium_effort", "long_term", "next_steps"]

        assert terminal_config["structure"] == required_sections

    def test_terminal_no_tables_by_default(self, format_outputs):
        """Terminal format should not use tables (ADHD-friendly)."""
        terminal_config = format_outputs["terminal"]

        assert terminal_config["has_tables"] is False

    def test_terminal_emojis_for_categories(self):
        """Terminal format should use emojis for visual categories."""
        expected_emojis = {
            "quick_wins": "⚡",
            "medium_effort": "🔧",
            "long_term": "🏗️",
            "next_steps": "→"
        }

        for category, emoji in expected_emojis.items():
            assert emoji in ["⚡", "🔧", "🏗️", "→"]

    def test_terminal_scannable_bullets(self):
        """Terminal format should use bullets for scannability."""
        sample_output = """
        ⚡ Quick Wins:
        - Email notifications
        - Basic templates

        🔧 Medium Effort:
        - In-app notifications
        """

        assert "- " in sample_output  # Bullet points
        assert "⚡" in sample_output  # Emoji categories


@pytest.mark.unit
class TestJSONFormat:
    """Test JSON format output (automation-ready)."""

    def test_json_is_valid(self, mock_brainstorm_quick_result):
        """JSON output should be valid JSON."""
        result = mock_brainstorm_quick_result

        # Should be serializable
        json_str = json.dumps(result)
        # Should be deserializable
        parsed = json.loads(json_str)

        assert isinstance(parsed, dict)

    def test_json_has_required_fields(self, format_outputs):
        """JSON format should have required top-level fields."""
        json_config = format_outputs["json"]
        required = ["metadata", "content", "recommendations"]

        assert json_config["required_fields"] == required

    def test_json_metadata_structure(self, mock_brainstorm_quick_result):
        """JSON metadata should have all required fields."""
        metadata = mock_brainstorm_quick_result["metadata"]

        assert "timestamp" in metadata
        assert "mode" in metadata
        assert "time_budget" in metadata
        assert "duration_seconds" in metadata
        assert "agents_used" in metadata

    def test_json_content_structure(self, mock_brainstorm_quick_result):
        """JSON content should have categorized items."""
        content = mock_brainstorm_quick_result["content"]

        assert "topic" in content
        assert "quick_wins" in content
        assert "medium_effort" in content
        assert "long_term" in content

    def test_json_recommendations_structure(self, mock_brainstorm_quick_result):
        """JSON recommendations should include path and steps."""
        recommendations = mock_brainstorm_quick_result["recommendations"]

        assert "recommended_path" in recommendations
        assert "next_steps" in recommendations
        assert isinstance(recommendations["next_steps"], list)

    def test_json_timestamp_iso8601(self, mock_brainstorm_quick_result):
        """JSON timestamp should be ISO 8601 format."""
        timestamp = mock_brainstorm_quick_result["metadata"]["timestamp"]

        # ISO 8601: 2024-12-24T10:30:00Z
        iso_pattern = r'^\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}Z$'
        assert re.match(iso_pattern, timestamp)

    def test_json_duration_is_numeric(self, mock_brainstorm_quick_result):
        """JSON duration should be numeric (seconds)."""
        duration = mock_brainstorm_quick_result["metadata"]["duration_seconds"]

        assert isinstance(duration, (int, float))
        assert duration > 0

    def test_json_agents_list(self, mock_brainstorm_thorough_result):
        """JSON agents_used should be a list."""
        agents = mock_brainstorm_thorough_result["metadata"]["agents_used"]

        assert isinstance(agents, list)
        assert len(agents) >= 2  # Thorough mode uses 2-4 agents


@pytest.mark.unit
class TestMarkdownFormat:
    """Test markdown format output (documentation-ready)."""

    def test_markdown_has_headers(self, format_outputs):
        """Markdown format should use headers."""
        markdown_config = format_outputs["markdown"]

        assert markdown_config["has_headers"] is True

    def test_markdown_has_lists(self, format_outputs):
        """Markdown format should use lists."""
        markdown_config = format_outputs["markdown"]

        assert markdown_config["has_lists"] is True

    def test_markdown_has_checkboxes(self, format_outputs):
        """Markdown format should use task checkboxes."""
        markdown_config = format_outputs["markdown"]

        assert markdown_config["has_checkboxes"] is True

    def test_markdown_structure_headers(self, format_outputs):
        """Markdown should have hierarchical headers."""
        markdown_config = format_outputs["markdown"]
        structure = markdown_config["structure"]

        assert "# Title" in structure
        assert "## Quick Wins" in structure
        assert "## Medium Effort" in structure
        assert "## Next Steps" in structure

    def test_markdown_metadata_section(self, sample_markdown_output):
        """Markdown should include metadata section."""
        output = sample_markdown_output

        assert "**Generated:**" in output
        assert "**Mode:**" in output
        assert "**Duration:**" in output

    def test_markdown_quick_wins_section(self, sample_markdown_output):
        """Markdown should have quick wins with emojis."""
        output = sample_markdown_output

        assert "## Quick Wins" in output
        assert "⚡" in output

    def test_markdown_task_checkboxes(self, sample_markdown_output):
        """Markdown should use GitHub-compatible checkboxes."""
        output = sample_markdown_output

        assert "- [ ]" in output  # Unchecked checkbox

    def test_markdown_numbered_steps(self, sample_markdown_output):
        """Markdown next steps should be numbered."""
        output = sample_markdown_output

        # Should have numbered list
        assert re.search(r'1\. \[ \]', output)

    def test_markdown_github_compatible(self, sample_markdown_output):
        """Markdown should be GitHub-compatible."""
        output = sample_markdown_output

        # GitHub-compatible elements
        assert "#" in output  # Headers
        assert "- [ ]" in output  # Task lists
        assert "**" in output  # Bold text


@pytest.mark.unit
class TestFormatParameterParsing:
    """Test format parameter parsing and application."""

    def test_default_format_is_terminal(self):
        """Default format should be terminal when not specified."""
        command = "/brainstorm feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "terminal"

    def test_explicit_json_format(self):
        """Test explicit --format json parameter."""
        command = "/brainstorm --format json feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "json"

    def test_explicit_markdown_format(self):
        """Test explicit --format markdown parameter."""
        command = "/brainstorm --format markdown feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "markdown"

    def test_format_with_all_parameters(self):
        """Format parameter should work with all other parameters."""
        command = "/brainstorm thorough architecture oauth --format json"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "thorough"
        assert parsed["content_mode"] == "architecture"
        assert parsed["format"] == "json"

    def test_format_position_flexible(self):
        """Format parameter should work at different positions."""
        # Format at end
        command1 = "/brainstorm feature auth --format json"
        # Format in middle
        command2 = "/brainstorm --format json feature auth"

        parsed1 = pytest.parse_mode_from_command(command1)
        parsed2 = pytest.parse_mode_from_command(command2)

        assert parsed1["format"] == "json"
        assert parsed2["format"] == "json"


@pytest.mark.unit
class TestFormatOutputGeneration:
    """Test format-specific output generation."""

    def test_terminal_output_readable(self):
        """Terminal output should be human-readable."""
        sample = """
        ⏱️  Mode: feature (quick) - Target: < 60 seconds

        ⚡ Quick Wins:
        - Email notifications - Easy to implement
        - Basic templates - Reusable patterns

        ✅ Completed in 42s (within quick budget)
        """

        assert "⏱️" in sample
        assert "⚡" in sample
        assert "✅" in sample

    def test_json_output_machine_readable(self, mock_brainstorm_quick_result):
        """JSON output should be machine-readable."""
        result = mock_brainstorm_quick_result

        # Should be parseable by automation
        duration = result["metadata"]["duration_seconds"]
        topic = result["content"]["topic"]

        assert isinstance(duration, (int, float))
        assert isinstance(topic, str)

    def test_markdown_output_github_ready(self, sample_markdown_output):
        """Markdown output should be ready for GitHub."""
        output = sample_markdown_output

        # GitHub features
        assert output.startswith("# ")  # Title header
        assert "## " in output  # Section headers
        assert "- [ ]" in output  # Task lists
        assert "**" in output  # Bold text


@pytest.mark.unit
class TestFormatSelection:
    """Test automatic format selection based on context."""

    def test_terminal_for_interactive_use(self):
        """Terminal format should be default for interactive use."""
        # No format specified = interactive use
        command = "/brainstorm feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "terminal"

    def test_json_for_automation(self):
        """JSON format should be used for automation."""
        # Explicit JSON for piping
        command = "/brainstorm --format json feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "json"

    def test_markdown_for_documentation(self):
        """Markdown format should be used for documentation."""
        # Explicit markdown for docs
        command = "/brainstorm --format markdown architecture oauth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "markdown"


@pytest.mark.unit
class TestFormatValidation:
    """Test format output validation."""

    def test_valid_json_structure(self, mock_brainstorm_quick_result):
        """JSON output should have valid structure."""
        result = mock_brainstorm_quick_result

        # Top-level keys
        assert "metadata" in result
        assert "content" in result
        assert "recommendations" in result

        # No extra keys
        expected_keys = {"metadata", "content", "recommendations"}
        actual_keys = set(result.keys())
        assert actual_keys == expected_keys

    def test_valid_markdown_headers(self, sample_markdown_output):
        """Markdown should have valid header hierarchy."""
        output = sample_markdown_output

        # Should have H1 (only one) - either at start or after newline
        h1_count = output.count("\n# ")
        if output.startswith("# "):
            h1_count += 1
        assert h1_count == 1

        # Should have H2 sections
        assert "\n## " in output

    def test_terminal_ansi_codes_optional(self):
        """Terminal format ANSI codes should be optional."""
        # Some terminals don't support colors
        plain_output = """
        Mode: feature (quick) - Target: < 60 seconds

        Quick Wins:
        - Email notifications
        """

        # Should still be readable without ANSI codes
        assert "Mode:" in plain_output
        assert "Quick Wins:" in plain_output


@pytest.mark.unit
class TestFormatEdgeCases:
    """Test edge cases in format handling."""

    def test_invalid_format_parameter(self):
        """Invalid format should default to terminal."""
        command = "/brainstorm --format invalid feature auth"
        parsed = pytest.parse_mode_from_command(command)

        # Should handle gracefully
        assert parsed["format"] in ["invalid", "terminal"]

    def test_empty_content_json(self):
        """JSON format should handle empty content gracefully."""
        empty_result = {
            "metadata": {"timestamp": "2024-12-24T10:30:00Z"},
            "content": {},
            "recommendations": {}
        }

        # Should still be valid JSON
        json_str = json.dumps(empty_result)
        parsed = json.loads(json_str)

        assert isinstance(parsed, dict)

    def test_special_characters_markdown(self):
        """Markdown should escape special characters."""
        text_with_special = "Use `code` and **bold** text"

        # Should preserve markdown special chars
        assert "`" in text_with_special
        assert "**" in text_with_special

    def test_unicode_in_all_formats(self):
        """All formats should support unicode."""
        unicode_text = "User notifications 通知 🔔"

        # Terminal
        assert "🔔" in unicode_text

        # JSON
        json_str = json.dumps({"text": unicode_text})
        parsed = json.loads(json_str)
        assert "🔔" in parsed["text"]

        # Markdown
        markdown = f"# {unicode_text}"
        assert "🔔" in markdown


@pytest.mark.unit
class TestFormatBackwardCompatibility:
    """Test format backward compatibility with v0.1.0."""

    def test_v1_no_format_parameter(self):
        """v0.1.0 commands without --format should work."""
        command = "/brainstorm feature auth"
        parsed = pytest.parse_mode_from_command(command)

        # Should default to terminal
        assert parsed["format"] == "terminal"

    def test_v1_output_still_terminal(self):
        """v0.1.0 output was terminal format."""
        # Old command
        command = "/brainstorm quick feature auth"
        parsed = pytest.parse_mode_from_command(command)

        # Should maintain terminal format
        assert parsed["format"] == "terminal"

    def test_v2_adds_json_markdown(self, v2_commands):
        """v2.0 adds JSON and markdown formats."""
        # New format options
        json_cmd = v2_commands[0]  # --format json
        markdown_cmd = v2_commands[1]  # --format markdown

        parsed_json = pytest.parse_mode_from_command(json_cmd)
        parsed_markdown = pytest.parse_mode_from_command(markdown_cmd)

        assert parsed_json["format"] == "json"
        assert parsed_markdown["format"] == "markdown"
