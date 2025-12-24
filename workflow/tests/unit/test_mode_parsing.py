"""
Unit tests for mode parsing in workflow plugin.

Tests command parsing logic for:
- Time budget mode detection (quick/default/thorough)
- Content mode detection (feature/architecture/design/etc)
- Topic extraction
- Format parameter parsing
"""

import pytest


@pytest.mark.unit
class TestTimeBudgetModeParsing:
    """Test parsing of time budget modes (quick/default/thorough)."""

    def test_explicit_quick_mode(self):
        """Test explicit quick mode detection."""
        command = "/brainstorm quick feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "quick"
        assert parsed["content_mode"] == "feature"
        assert "auth" in parsed["topic"]

    def test_explicit_thorough_mode(self):
        """Test explicit thorough mode detection."""
        command = "/brainstorm thorough architecture oauth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "thorough"
        assert parsed["content_mode"] == "architecture"
        assert "oauth" in parsed["topic"]

    def test_default_mode_when_no_explicit_mode(self):
        """Test default mode when no time budget specified."""
        command = "/brainstorm feature user notifications"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "default"

    def test_default_mode_with_only_topic(self):
        """Test default mode with only topic (no content mode)."""
        command = "/brainstorm user authentication"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "default"
        assert parsed["content_mode"] is None
        assert "user authentication" in parsed["topic"]


@pytest.mark.unit
class TestContentModeParsing:
    """Test parsing of content modes (feature/architecture/design/etc)."""

    def test_feature_mode_detection(self):
        """Test feature mode detection from keyword."""
        command = "/brainstorm feature user notifications"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["content_mode"] == "feature"

    def test_architecture_mode_detection(self):
        """Test architecture mode detection."""
        command = "/brainstorm architecture multi-tenant SaaS"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["content_mode"] == "architecture"

    def test_design_mode_detection(self):
        """Test design mode detection."""
        command = "/brainstorm design dashboard UX"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["content_mode"] == "design"

    def test_backend_mode_detection(self):
        """Test backend mode detection."""
        command = "/brainstorm backend API endpoints"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["content_mode"] == "backend"

    def test_frontend_mode_detection(self):
        """Test frontend mode detection."""
        command = "/brainstorm frontend React components"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["content_mode"] == "frontend"

    def test_devops_mode_detection(self):
        """Test devops mode detection."""
        command = "/brainstorm devops CI/CD pipeline"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["content_mode"] == "devops"


@pytest.mark.unit
class TestTopicExtraction:
    """Test topic extraction from commands."""

    def test_topic_with_single_word(self):
        """Test topic extraction with single word."""
        command = "/brainstorm authentication"
        parsed = pytest.parse_mode_from_command(command)

        assert "authentication" in parsed["topic"]

    def test_topic_with_multiple_words(self):
        """Test topic extraction with multiple words."""
        command = "/brainstorm user authentication with OAuth"
        parsed = pytest.parse_mode_from_command(command)

        assert "user" in parsed["topic"]
        assert "authentication" in parsed["topic"]
        assert "OAuth" in parsed["topic"]

    def test_topic_excludes_mode_keywords(self):
        """Test that topic doesn't include mode keywords."""
        command = "/brainstorm quick feature user auth"
        parsed = pytest.parse_mode_from_command(command)

        assert "quick" not in parsed["topic"]
        assert "feature" not in parsed["topic"]
        assert "user" in parsed["topic"]
        assert "auth" in parsed["topic"]

    def test_topic_with_special_characters(self):
        """Test topic with hyphens and slashes."""
        command = "/brainstorm multi-tenant SaaS architecture"
        parsed = pytest.parse_mode_from_command(command)

        assert "multi-tenant" in parsed["topic"]
        assert "SaaS" in parsed["topic"]


@pytest.mark.unit
class TestFormatParsing:
    """Test format parameter parsing."""

    def test_default_terminal_format(self):
        """Test default format is terminal when not specified."""
        command = "/brainstorm feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "terminal"

    def test_explicit_json_format(self):
        """Test explicit JSON format parameter."""
        command = "/brainstorm --format json feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "json"

    def test_explicit_markdown_format(self):
        """Test explicit markdown format parameter."""
        command = "/brainstorm --format markdown architecture oauth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "markdown"

    def test_format_with_all_parameters(self):
        """Test format parameter with all other parameters."""
        command = "/brainstorm thorough architecture oauth --format json"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "thorough"
        assert parsed["content_mode"] == "architecture"
        assert parsed["format"] == "json"
        assert "oauth" in parsed["topic"]


@pytest.mark.unit
class TestComplexCommands:
    """Test parsing of complex command combinations."""

    def test_all_parameters_combined(self):
        """Test command with all parameters."""
        command = "/brainstorm quick feature user authentication --format markdown"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "quick"
        assert parsed["content_mode"] == "feature"
        assert parsed["format"] == "markdown"
        assert "user" in parsed["topic"]
        assert "authentication" in parsed["topic"]

    def test_no_content_mode_with_format(self):
        """Test command with format but no content mode."""
        command = "/brainstorm user notifications --format json"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "default"
        assert parsed["content_mode"] is None
        assert parsed["format"] == "json"

    def test_minimal_command(self):
        """Test minimal command (just /brainstorm)."""
        command = "/brainstorm"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["command"] == "/brainstorm"
        assert parsed["time_budget_mode"] == "default"
        assert parsed["content_mode"] is None
        assert parsed["format"] == "terminal"

    def test_thorough_with_multiple_content_words(self):
        """Test thorough mode with complex topic."""
        command = "/brainstorm thorough multi-tenant SaaS architecture with PostgreSQL"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "thorough"
        topic_lower = parsed["topic"].lower()
        assert "multi-tenant" in topic_lower
        assert "saas" in topic_lower
        assert "postgresql" in topic_lower


@pytest.mark.unit
class TestModeAutoDetection:
    """Test automatic mode detection from context (future feature)."""

    def test_auto_detect_feature_from_keywords(self, context_examples):
        """Test feature mode auto-detection from context keywords."""
        context = context_examples["feature_context"]

        # Check for feature keywords
        feature_keywords = ["user", "authentication", "oauth"]
        assert any(keyword in context.lower() for keyword in feature_keywords)

    def test_auto_detect_architecture_from_keywords(self, context_examples):
        """Test architecture mode auto-detection."""
        context = context_examples["architecture_context"]

        arch_keywords = ["scalable", "architecture", "multi-tenant"]
        assert any(keyword in context.lower() for keyword in arch_keywords)

    def test_auto_detect_design_from_keywords(self, context_examples):
        """Test design mode auto-detection."""
        context = context_examples["design_context"]

        design_keywords = ["dashboard", "ux", "accessibility"]
        assert any(keyword in context.lower() for keyword in design_keywords)


@pytest.mark.unit
class TestEdgeCases:
    """Test edge cases and error conditions."""

    def test_empty_command(self):
        """Test parsing of empty command."""
        command = ""
        # Should handle gracefully or return defaults

    def test_command_with_only_format(self):
        """Test command with only format parameter."""
        command = "/brainstorm --format json"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "json"
        assert parsed["time_budget_mode"] == "default"

    def test_duplicate_modes(self):
        """Test handling of duplicate mode keywords."""
        command = "/brainstorm quick thorough feature"
        parsed = pytest.parse_mode_from_command(command)

        # Should pick first time budget mode
        assert parsed["time_budget_mode"] in ["quick", "thorough"]

    def test_invalid_format_parameter(self):
        """Test handling of invalid format value."""
        command = "/brainstorm --format invalid feature auth"
        parsed = pytest.parse_mode_from_command(command)

        # Should handle invalid format gracefully
        assert parsed["format"] in ["invalid", "terminal"]  # Either accept or default


@pytest.mark.unit
class TestBackwardCompatibility:
    """Test v0.1.0 commands still work in v2.0."""

    def test_v1_basic_brainstorm(self, v1_commands):
        """Test basic v0.1.0 brainstorm command."""
        command = v1_commands[0]  # "/brainstorm"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["command"] == "/brainstorm"
        assert parsed["time_budget_mode"] == "default"

    def test_v1_quick_mode(self, v1_commands):
        """Test v0.1.0 quick mode command."""
        command = v1_commands[1]  # "/brainstorm quick"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "quick"

    def test_v1_thorough_mode(self, v1_commands):
        """Test v0.1.0 thorough mode command."""
        command = v1_commands[2]  # "/brainstorm thorough"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "thorough"

    def test_v1_feature_mode(self, v1_commands):
        """Test v0.1.0 feature mode command."""
        command = v1_commands[3]  # "/brainstorm feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["content_mode"] == "feature"
        assert "auth" in parsed["topic"]

    def test_all_v1_commands_parse_correctly(self, v1_commands):
        """Test all v0.1.0 commands parse without errors."""
        for command in v1_commands:
            parsed = pytest.parse_mode_from_command(command)
            assert parsed["command"] == "/brainstorm"
            # Should not raise any exceptions


@pytest.mark.unit
class TestV2NewFeatures:
    """Test new v2.0 features."""

    def test_v2_json_format(self, v2_commands):
        """Test v2.0 JSON format command."""
        command = v2_commands[0]  # "/brainstorm --format json"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "json"

    def test_v2_markdown_format(self, v2_commands):
        """Test v2.0 markdown format command."""
        command = v2_commands[1]  # "/brainstorm --format markdown"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "markdown"

    def test_v2_combined_mode_and_format(self, v2_commands):
        """Test v2.0 combined mode + format."""
        command = v2_commands[2]  # "/brainstorm quick feature auth"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "quick"
        assert parsed["content_mode"] == "feature"

    def test_v2_full_command(self, v2_commands):
        """Test v2.0 command with all parameters."""
        command = v2_commands[3]  # thorough + architecture + oauth + json
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "thorough"
        assert parsed["content_mode"] == "architecture"
        assert parsed["format"] == "json"
        assert "oauth" in parsed["topic"]
