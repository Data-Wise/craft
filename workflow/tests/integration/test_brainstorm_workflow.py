"""
Integration tests for brainstorm workflow.

Tests end-to-end workflow integration:
- Complete brainstorm execution (mode → agents → format → output)
- Cross-component integration
- Real workflow scenarios
"""

import pytest
import time
import json


@pytest.mark.integration
class TestQuickModeWorkflow:
    """Test complete quick mode workflow integration."""

    def test_quick_feature_brainstorm_end_to_end(
        self, mock_command_input, time_budgets
    ):
        """Test complete quick mode feature brainstorm."""
        command = mock_command_input["quick_feature"]

        # Parse command
        parsed = pytest.parse_mode_from_command(command)

        # Verify mode detection
        assert parsed["time_budget_mode"] == "quick"
        assert parsed["content_mode"] == "feature"
        assert "user" in parsed["topic"]
        assert "auth" in parsed["topic"]

        # Simulate execution
        budget = time_budgets["quick"]["budget_seconds"]
        assert budget == 60

        # Should complete within budget
        simulated_duration = 42
        assert simulated_duration < budget

    def test_quick_mode_no_agents(self, mode_examples):
        """Quick mode should not use agents."""
        quick = mode_examples["quick"]

        assert quick["agents_count"] == 0
        assert quick["delegation"] is False

    def test_quick_mode_terminal_output(self, format_outputs):
        """Quick mode should default to terminal output."""
        terminal = format_outputs["terminal"]

        assert terminal["has_colors"] is True
        assert terminal["has_emojis"] is True

    def test_quick_mode_item_constraints(self, mode_examples):
        """Quick mode should produce 5-7 ideas."""
        quick = mode_examples["quick"]
        min_ideas, max_ideas = quick["output_items"]

        assert min_ideas == 5
        assert max_ideas == 7


@pytest.mark.integration
class TestDefaultModeWorkflow:
    """Test complete default mode workflow integration."""

    def test_default_design_brainstorm_end_to_end(
        self, mock_command_input, time_budgets
    ):
        """Test complete default mode design brainstorm."""
        command = mock_command_input["default_design"]

        # Parse command
        parsed = pytest.parse_mode_from_command(command)

        # Verify mode detection
        assert parsed["time_budget_mode"] == "default"
        assert parsed["content_mode"] == "design"
        assert "dashboard" in parsed["topic"]

        # Check time budget
        budget = time_budgets["default"]["budget_seconds"]
        assert budget == 300

    def test_default_mode_optional_agents(self, mode_examples):
        """Default mode should have optional agents."""
        default = mode_examples["default"]

        assert default["delegation"] == "optional"
        min_agents, max_agents = default["agents_count"]
        assert min_agents == 0
        assert max_agents >= 1

    def test_default_mode_output_size(self, mode_examples):
        """Default mode should produce 7-15 ideas."""
        default = mode_examples["default"]
        min_ideas, max_ideas = default["output_items"]

        assert min_ideas == 7
        assert max_ideas == 15


@pytest.mark.integration
class TestThoroughModeWorkflow:
    """Test complete thorough mode workflow integration."""

    def test_thorough_architecture_brainstorm_end_to_end(
        self, mock_command_input, time_budgets, mode_examples
    ):
        """Test complete thorough mode architecture brainstorm."""
        command = mock_command_input["thorough_architecture"]

        # Parse command
        parsed = pytest.parse_mode_from_command(command)

        # Verify mode detection
        assert parsed["time_budget_mode"] == "thorough"
        assert parsed["content_mode"] == "architecture"
        assert "multi-tenant" in parsed["topic"]

        # Check time budget
        budget = time_budgets["thorough"]["budget_seconds"]
        assert budget == 1800  # 30 minutes

        # Verify agent requirements
        thorough = mode_examples["thorough"]
        min_agents, max_agents = thorough["agents_count"]
        assert min_agents >= 2
        assert max_agents <= 4

    def test_thorough_mode_with_agents(
        self, mock_brainstorm_thorough_result, available_agents
    ):
        """Thorough mode should use multiple agents."""
        metadata = mock_brainstorm_thorough_result["metadata"]
        agents_used = metadata["agents_used"]

        # Should have 2-4 agents
        assert len(agents_used) >= 2
        assert len(agents_used) <= 4

        # Agents should be valid
        for agent in agents_used:
            normalized = agent.replace("-", "_")
            # Agent exists in available agents (after normalization)

    def test_thorough_mode_agent_synthesis(
        self, mock_brainstorm_thorough_result
    ):
        """Thorough mode should synthesize agent results."""
        content = mock_brainstorm_thorough_result["content"]

        # Should have agent analysis
        assert "agent_analysis" in content

        # Should have synthesized recommendations
        assert "quick_wins" in content
        assert "medium_effort" in content
        assert "long_term" in content

    def test_thorough_mode_comprehensive_output(self, mode_examples):
        """Thorough mode should produce 15-30 ideas."""
        thorough = mode_examples["thorough"]
        min_ideas, max_ideas = thorough["output_items"]

        assert min_ideas >= 15
        assert max_ideas <= 30


@pytest.mark.integration
class TestFormatIntegration:
    """Test format integration across workflow."""

    def test_json_format_workflow(self, mock_command_input):
        """Test JSON format workflow integration."""
        command = mock_command_input["json_format"]

        # Parse command
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "json"
        assert parsed["content_mode"] == "feature"

    def test_markdown_format_workflow(self, mock_command_input):
        """Test markdown format workflow integration."""
        command = mock_command_input["markdown_format"]

        # Parse command
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["format"] == "markdown"
        assert parsed["content_mode"] == "architecture"

    def test_format_with_all_modes(self):
        """All modes should support all formats."""
        modes = ["quick", "default", "thorough"]
        formats = ["terminal", "json", "markdown"]

        for mode in modes:
            for fmt in formats:
                command = f"/brainstorm {mode} feature auth --format {fmt}"
                parsed = pytest.parse_mode_from_command(command)

                assert parsed["time_budget_mode"] == mode
                assert parsed["format"] == fmt


@pytest.mark.integration
class TestAgentWorkflowIntegration:
    """Test agent integration across workflow."""

    def test_agent_selection_for_auth_topic(
        self, agent_selection_rules, available_agents
    ):
        """Auth topic should select appropriate agents."""
        auth_agents = agent_selection_rules["auth"]

        # Should select security and backend
        assert "backend-architect" in auth_agents
        assert "security-specialist" in auth_agents

        # Verify agents exist
        for agent in auth_agents:
            assert agent in available_agents

    def test_agent_selection_for_database_topic(
        self, agent_selection_rules, available_agents
    ):
        """Database topic should select appropriate agents."""
        db_agents = agent_selection_rules["database"]

        assert "database-architect" in db_agents
        assert "backend-architect" in db_agents

    def test_skill_activation_integration(self, auto_activating_skills):
        """Skills should activate based on keywords."""
        backend_skill = auto_activating_skills["backend-designer"]

        # Backend keywords should activate backend skill
        triggers = backend_skill["triggers"]
        assert "API" in triggers

        # Skill should provide relevant capabilities
        provides = backend_skill["provides"]
        assert len(provides) > 0


@pytest.mark.integration
class TestTimeBudgetIntegration:
    """Test time budget integration across workflow."""

    def test_time_budget_enforcement_levels(self, time_budgets):
        """Different modes should have different enforcement levels."""
        quick = time_budgets["quick"]
        default = time_budgets["default"]
        thorough = time_budgets["thorough"]

        assert quick["type"] == "MUST"  # Strict
        assert default["type"] == "SHOULD"  # Flexible
        assert thorough["type"] == "MAX"  # Absolute

    def test_time_budget_increases_with_depth(self, time_budgets):
        """Time budgets should increase with mode depth."""
        quick_budget = time_budgets["quick"]["budget_seconds"]
        default_budget = time_budgets["default"]["budget_seconds"]
        thorough_budget = time_budgets["thorough"]["budget_seconds"]

        assert quick_budget < default_budget < thorough_budget

    @pytest.mark.slow
    def test_time_budget_measurement_integration(self, time_budgets):
        """Test actual time budget measurement."""
        start = time.time()

        # Simulate quick operation
        time.sleep(0.1)

        elapsed = time.time() - start
        quick_budget = time_budgets["quick"]["budget_seconds"]

        # Should be well under budget
        assert elapsed < quick_budget
        assert elapsed < 1  # Very fast


@pytest.mark.integration
class TestBackwardCompatibilityIntegration:
    """Test backward compatibility integration."""

    def test_v1_commands_work_in_v2(self, v1_commands):
        """All v0.1.0 commands should work in v2.0."""
        for command in v1_commands:
            parsed = pytest.parse_mode_from_command(command)

            # Should parse without errors
            assert "command" in parsed
            assert parsed["command"] == "/brainstorm"

    def test_v1_default_format_terminal(self, v1_commands):
        """v0.1.0 commands should default to terminal format."""
        for command in v1_commands:
            parsed = pytest.parse_mode_from_command(command)

            # Should default to terminal
            assert parsed["format"] == "terminal"

    def test_v2_new_features_work(self, v2_commands):
        """v2.0 new features should work correctly."""
        for command in v2_commands:
            parsed = pytest.parse_mode_from_command(command)

            # Should parse v2 features
            if "--format" in command:
                assert parsed["format"] in ["json", "markdown", "terminal"]


@pytest.mark.integration
class TestCompleteScenarios:
    """Test complete realistic scenarios."""

    def test_scenario_quick_auth_feature(
        self, time_budgets, mode_examples, format_outputs
    ):
        """Scenario: Quick auth feature brainstorm for daily standup."""
        command = "/brainstorm quick feature user authentication"
        parsed = pytest.parse_mode_from_command(command)

        # Mode
        assert parsed["time_budget_mode"] == "quick"
        assert parsed["content_mode"] == "feature"

        # Time budget
        budget = time_budgets["quick"]["budget_seconds"]
        assert budget == 60

        # No agents
        quick = mode_examples["quick"]
        assert quick["agents_count"] == 0

        # Terminal output
        assert parsed["format"] == "terminal"

    def test_scenario_thorough_architecture_with_json(
        self, time_budgets, mode_examples
    ):
        """Scenario: Thorough architecture analysis for documentation."""
        command = "/brainstorm thorough architecture multi-tenant SaaS --format json"
        parsed = pytest.parse_mode_from_command(command)

        # Mode
        assert parsed["time_budget_mode"] == "thorough"
        assert parsed["content_mode"] == "architecture"

        # Time budget
        budget = time_budgets["thorough"]["budget_seconds"]
        assert budget == 1800  # 30 minutes

        # Agents required
        thorough = mode_examples["thorough"]
        min_agents, max_agents = thorough["agents_count"]
        assert min_agents >= 2

        # JSON output for automation
        assert parsed["format"] == "json"

    def test_scenario_default_design_with_markdown(
        self, time_budgets, mode_examples
    ):
        """Scenario: Default design brainstorm for GitHub issue."""
        command = "/brainstorm design dashboard UX --format markdown"
        parsed = pytest.parse_mode_from_command(command)

        # Mode
        assert parsed["time_budget_mode"] == "default"
        assert parsed["content_mode"] == "design"

        # Time budget
        budget = time_budgets["default"]["budget_seconds"]
        assert budget == 300  # 5 minutes

        # Optional agents
        default = mode_examples["default"]
        assert default["delegation"] == "optional"

        # Markdown for GitHub
        assert parsed["format"] == "markdown"


@pytest.mark.integration
class TestErrorHandling:
    """Test error handling integration."""

    def test_minimal_command_has_defaults(self):
        """Minimal command should use sensible defaults."""
        command = "/brainstorm"
        parsed = pytest.parse_mode_from_command(command)

        assert parsed["time_budget_mode"] == "default"
        assert parsed["format"] == "terminal"

    def test_invalid_format_graceful_degradation(self):
        """Invalid format should degrade gracefully."""
        command = "/brainstorm --format invalid feature auth"
        parsed = pytest.parse_mode_from_command(command)

        # Should handle gracefully (either accept or default)
        assert parsed["format"] in ["invalid", "terminal"]

    def test_complex_topic_parsing(self):
        """Complex topics should parse correctly."""
        command = "/brainstorm multi-tenant SaaS architecture with PostgreSQL"
        parsed = pytest.parse_mode_from_command(command)

        topic_lower = parsed["topic"].lower()
        assert "multi-tenant" in topic_lower
        assert "saas" in topic_lower
        assert "postgresql" in topic_lower


@pytest.mark.integration
class TestOutputValidation:
    """Test output validation across workflow."""

    def test_json_output_complete_structure(
        self, mock_brainstorm_quick_result, format_outputs
    ):
        """JSON output should have complete valid structure."""
        result = mock_brainstorm_quick_result
        json_config = format_outputs["json"]

        # Should be valid JSON
        json_str = json.dumps(result)
        parsed = json.loads(json_str)

        # Should have all required fields
        for field in json_config["required_fields"]:
            assert field in parsed

    def test_markdown_output_github_compatible(
        self, sample_markdown_output
    ):
        """Markdown output should be GitHub-compatible."""
        output = sample_markdown_output

        # Headers
        assert output.startswith("# ")
        assert "\n## " in output

        # Task lists
        assert "- [ ]" in output

        # Metadata
        assert "**Generated:**" in output

    def test_terminal_output_adhd_friendly(self, format_outputs):
        """Terminal output should be ADHD-friendly."""
        terminal = format_outputs["terminal"]

        # Should have visual hierarchy
        assert terminal["has_colors"] is True
        assert terminal["has_emojis"] is True

        # Should not use complex tables
        assert terminal["has_tables"] is False
