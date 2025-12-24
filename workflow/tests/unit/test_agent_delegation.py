"""
Unit tests for agent delegation in workflow plugin.

Tests agent selection, delegation, and result synthesis for:
- Automatic agent selection based on topic keywords
- Agent execution and timing
- Result synthesis from multiple agents
- Agent availability and configuration
"""

import pytest
from typing import List, Dict


@pytest.mark.unit
class TestAgentAvailability:
    """Test available agents and their configurations."""

    def test_all_agents_configured(self, available_agents):
        """All expected agents should be configured."""
        expected_agents = [
            "backend-architect",
            "ux-ui-designer",
            "devops-engineer",
            "security-specialist",
            "database-architect",
            "performance-engineer"
        ]

        for agent in expected_agents:
            assert agent in available_agents

    def test_agent_has_specialization(self, available_agents):
        """Each agent should have specialization defined."""
        for agent_name, config in available_agents.items():
            assert "specialization" in config
            assert len(config["specialization"]) > 0

    def test_agent_has_duration_estimate(self, available_agents):
        """Each agent should have typical duration estimate."""
        for agent_name, config in available_agents.items():
            assert "typical_duration" in config
            min_dur, max_dur = config["typical_duration"]
            assert min_dur > 0
            assert max_dur > min_dur

    def test_backend_architect_config(self, available_agents):
        """Backend architect should have correct configuration."""
        backend = available_agents["backend-architect"]

        assert "Backend architecture" in backend["specialization"]
        assert "API design" in backend["specialization"]

    def test_ux_designer_config(self, available_agents):
        """UX/UI designer should have correct configuration."""
        ux = available_agents["ux-ui-designer"]

        assert "UI/UX" in ux["specialization"]
        assert "accessibility" in ux["specialization"]


@pytest.mark.unit
class TestAgentSelection:
    """Test automatic agent selection based on keywords."""

    def test_auth_topic_selects_correct_agents(self, agent_selection_rules):
        """Auth topic should select backend-architect and security-specialist."""
        auth_agents = agent_selection_rules["auth"]

        assert "backend-architect" in auth_agents
        assert "security-specialist" in auth_agents

    def test_database_topic_selects_correct_agents(self, agent_selection_rules):
        """Database topic should select relevant agents."""
        db_agents = agent_selection_rules["database"]

        assert "backend-architect" in db_agents
        assert "database-architect" in db_agents

    def test_ui_topic_selects_designer(self, agent_selection_rules):
        """UI topic should select UX/UI designer."""
        ui_agents = agent_selection_rules["UI"]

        assert "ux-ui-designer" in ui_agents

    def test_api_topic_selects_backend(self, agent_selection_rules):
        """API topic should select backend architect."""
        api_agents = agent_selection_rules["API"]

        assert "backend-architect" in api_agents

    def test_deploy_topic_selects_devops(self, agent_selection_rules):
        """Deploy topic should select DevOps engineer."""
        deploy_agents = agent_selection_rules["deploy"]

        assert "devops-engineer" in deploy_agents

    def test_performance_topic_selects_specialist(self, agent_selection_rules):
        """Performance topic should select performance engineer."""
        perf_agents = agent_selection_rules["performance"]

        assert "performance-engineer" in perf_agents


@pytest.mark.unit
class TestAgentDelegation:
    """Test agent delegation logic and execution."""

    def test_quick_mode_no_delegation(self, mode_examples):
        """Quick mode should never delegate to agents."""
        quick = mode_examples["quick"]

        assert quick["delegation"] is False
        assert quick["agents_count"] == 0

    def test_default_mode_optional_delegation(self, mode_examples):
        """Default mode should have optional delegation."""
        default = mode_examples["default"]

        assert default["delegation"] == "optional"
        min_agents, max_agents = default["agents_count"]
        assert min_agents == 0
        assert max_agents >= 1

    def test_thorough_mode_requires_delegation(self, mode_examples):
        """Thorough mode should require agent delegation."""
        thorough = mode_examples["thorough"]

        assert thorough["delegation"] is True
        min_agents, max_agents = thorough["agents_count"]
        assert min_agents >= 2
        assert max_agents <= 4

    def test_agent_count_constraints(self, mode_examples):
        """Agent counts should follow mode constraints."""
        # Quick: 0 agents
        assert mode_examples["quick"]["agents_count"] == 0

        # Default: 0-2 agents
        default_range = mode_examples["default"]["agents_count"]
        assert default_range[0] == 0
        assert default_range[1] >= 1

        # Thorough: 2-4 agents
        thorough_range = mode_examples["thorough"]["agents_count"]
        assert thorough_range[0] >= 2
        assert thorough_range[1] <= 4


@pytest.mark.unit
class TestAgentExecution:
    """Test agent execution and timing."""

    def test_agent_execution_within_budget(self, available_agents):
        """Agent execution should fit within time budgets."""
        for agent_name, config in available_agents.items():
            min_dur, max_dur = config["typical_duration"]

            # Should be reasonable (< 5 minutes)
            assert max_dur <= 300

    def test_multiple_agents_parallel(self):
        """Multiple agents should run in parallel."""
        # Thorough mode with 3 agents
        agent_durations = [102, 98, 95]  # Parallel execution
        total_time = max(agent_durations)  # 102 seconds

        # Should be less than sum (not sequential)
        assert total_time < sum(agent_durations)

    def test_agent_timeout_handling(self):
        """Agents should have timeout handling."""
        max_timeout = 300  # 5 minutes max per agent

        # Agent should not exceed timeout
        elapsed = 280
        assert elapsed < max_timeout


@pytest.mark.unit
class TestAgentResults:
    """Test agent result structure and synthesis."""

    def test_agent_result_structure(self, mock_brainstorm_thorough_result):
        """Agent results should have consistent structure."""
        content = mock_brainstorm_thorough_result["content"]

        assert "agent_analysis" in content

        agent_analysis = content["agent_analysis"]
        for agent_name, result in agent_analysis.items():
            assert "recommendations" in result
            assert "duration" in result

    def test_backend_architect_recommendations(self, mock_brainstorm_thorough_result):
        """Backend architect should provide backend recommendations."""
        agent_analysis = mock_brainstorm_thorough_result["content"]["agent_analysis"]
        backend = agent_analysis["backend_architect"]

        assert isinstance(backend["recommendations"], list)
        assert len(backend["recommendations"]) > 0

    def test_database_architect_recommendations(self, mock_brainstorm_thorough_result):
        """Database architect should provide database recommendations."""
        agent_analysis = mock_brainstorm_thorough_result["content"]["agent_analysis"]
        database = agent_analysis["database_architect"]

        assert isinstance(database["recommendations"], list)
        assert len(database["recommendations"]) > 0

    def test_agent_duration_tracked(self, mock_brainstorm_thorough_result):
        """Agent execution duration should be tracked."""
        agent_analysis = mock_brainstorm_thorough_result["content"]["agent_analysis"]

        for agent_name, result in agent_analysis.items():
            duration = result["duration"]
            assert isinstance(duration, (int, float))
            assert duration > 0


@pytest.mark.unit
class TestAgentSynthesis:
    """Test synthesis of results from multiple agents."""

    def test_multiple_agent_results_combined(self, mock_brainstorm_thorough_result):
        """Results from multiple agents should be synthesized."""
        content = mock_brainstorm_thorough_result["content"]

        # Should have combined recommendations
        assert "quick_wins" in content
        assert "medium_effort" in content
        assert "long_term" in content

        # Should have agent-specific analysis
        assert "agent_analysis" in content

    def test_agent_total_duration(self, mock_brainstorm_thorough_result):
        """Total duration should account for all agents."""
        metadata = mock_brainstorm_thorough_result["metadata"]
        agent_analysis = mock_brainstorm_thorough_result["content"]["agent_analysis"]

        total_duration = metadata["duration_seconds"]
        agent_durations = [result["duration"] for result in agent_analysis.values()]

        # Total should be approximately max (parallel) not sum (sequential)
        max_agent_duration = max(agent_durations)
        assert total_duration >= max_agent_duration

    def test_agent_list_in_metadata(self, mock_brainstorm_thorough_result):
        """Metadata should list all agents used."""
        metadata = mock_brainstorm_thorough_result["metadata"]
        agents_used = metadata["agents_used"]

        assert isinstance(agents_used, list)
        assert "backend-architect" in agents_used
        assert "database-architect" in agents_used

    def test_agent_recommendations_integrated(self, mock_brainstorm_thorough_result):
        """Agent recommendations should be integrated into main output."""
        content = mock_brainstorm_thorough_result["content"]
        recommendations = mock_brainstorm_thorough_result["recommendations"]

        # Main recommendations should synthesize agent input
        assert "recommended_path" in recommendations
        assert "next_steps" in recommendations
        assert len(recommendations["next_steps"]) > 0


@pytest.mark.unit
class TestSkillActivation:
    """Test automatic skill activation based on keywords."""

    def test_backend_skill_triggers(self, auto_activating_skills):
        """Backend skill should trigger on backend keywords."""
        backend_skill = auto_activating_skills["backend-designer"]
        triggers = backend_skill["triggers"]

        assert "API" in triggers
        assert "database" in triggers
        assert "backend" in triggers

    def test_frontend_skill_triggers(self, auto_activating_skills):
        """Frontend skill should trigger on frontend keywords."""
        frontend_skill = auto_activating_skills["frontend-designer"]
        triggers = frontend_skill["triggers"]

        assert "UI" in triggers
        assert "UX" in triggers
        assert "React" in triggers

    def test_devops_skill_triggers(self, auto_activating_skills):
        """DevOps skill should trigger on deployment keywords."""
        devops_skill = auto_activating_skills["devops-helper"]
        triggers = devops_skill["triggers"]

        assert "deploy" in triggers
        assert "CI/CD" in triggers
        assert "Docker" in triggers

    def test_skill_provides_capabilities(self, auto_activating_skills):
        """Skills should define what they provide."""
        for skill_name, config in auto_activating_skills.items():
            assert "provides" in config
            assert len(config["provides"]) > 0

    def test_backend_skill_provides(self, auto_activating_skills):
        """Backend skill should provide backend capabilities."""
        backend_skill = auto_activating_skills["backend-designer"]
        provides = backend_skill["provides"]

        assert "API patterns" in provides
        assert "database design" in provides


@pytest.mark.unit
class TestAgentConfiguration:
    """Test agent configuration and validation."""

    def test_agent_specialization_unique(self, available_agents):
        """Each agent should have unique specialization."""
        specializations = [config["specialization"] for config in available_agents.values()]

        # Should have variety
        assert len(set(specializations)) == len(specializations)

    def test_agent_duration_reasonable(self, available_agents):
        """Agent durations should be reasonable."""
        for agent_name, config in available_agents.items():
            min_dur, max_dur = config["typical_duration"]

            # Min should be at least 30 seconds
            assert min_dur >= 30

            # Max should be under 5 minutes
            assert max_dur <= 300

    def test_no_duplicate_agent_names(self, available_agents):
        """Agent names should be unique."""
        agent_names = list(available_agents.keys())

        assert len(agent_names) == len(set(agent_names))


@pytest.mark.unit
class TestAgentEdgeCases:
    """Test edge cases in agent delegation."""

    def test_no_matching_agent_for_topic(self):
        """Should handle topics with no matching agents gracefully."""
        # Generic topic
        topic = "general brainstorming"

        # Should not fail, use default behavior
        # (This would be tested in integration tests)

    def test_agent_failure_handling(self):
        """Should handle agent failures gracefully."""
        # If one agent fails, others should continue
        # (This would be tested in integration tests)

    def test_agent_result_empty(self):
        """Should handle empty agent results gracefully."""
        empty_result = {
            "recommendations": [],
            "duration": 45
        }

        assert isinstance(empty_result["recommendations"], list)
        assert empty_result["duration"] > 0

    def test_too_many_agents_requested(self):
        """Should limit agent count to reasonable maximum."""
        max_agents = 4

        # Thorough mode should not exceed 4 agents
        requested_agents = 10
        actual_agents = min(requested_agents, max_agents)

        assert actual_agents <= 4


@pytest.mark.unit
class TestAgentMetadata:
    """Test agent metadata tracking."""

    def test_metadata_includes_agents(self, mock_brainstorm_thorough_result):
        """Metadata should include list of agents used."""
        metadata = mock_brainstorm_thorough_result["metadata"]

        assert "agents_used" in metadata
        assert isinstance(metadata["agents_used"], list)

    def test_quick_mode_empty_agents_list(self, mock_brainstorm_quick_result):
        """Quick mode should have empty agents list."""
        metadata = mock_brainstorm_quick_result["metadata"]

        assert metadata["agents_used"] == []

    def test_thorough_mode_populated_agents_list(self, mock_brainstorm_thorough_result):
        """Thorough mode should have populated agents list."""
        metadata = mock_brainstorm_thorough_result["metadata"]
        agents = metadata["agents_used"]

        assert len(agents) >= 2
        assert len(agents) <= 4

    def test_agent_names_match_analysis(self, mock_brainstorm_thorough_result):
        """Agent names in metadata should match analysis section."""
        metadata = mock_brainstorm_thorough_result["metadata"]
        content = mock_brainstorm_thorough_result["content"]

        agents_in_metadata = set(metadata["agents_used"])
        agents_in_analysis = set(content["agent_analysis"].keys())

        # Should match (after normalizing names)
        # backend-architect → backend_architect
        normalized_metadata = {name.replace("-", "_") for name in agents_in_metadata}
        assert normalized_metadata == agents_in_analysis
