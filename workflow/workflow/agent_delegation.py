"""
Agent delegation system for workflow plugin.

Provides agent selection, delegation, and result synthesis for:
- quick mode (0 agents)
- default mode (0-2 agents, optional)
- thorough mode (2-4 agents, required)
"""

from typing import Dict, Any, List, Optional, Tuple


class AgentConfig:
    """Agent configuration and availability."""

    # Available agents with specializations
    AGENTS = {
        "backend-architect": {
            "specialization": "Backend architecture, API design, database schema",
            "typical_duration": (60, 180)  # seconds (min, max)
        },
        "ux-ui-designer": {
            "specialization": "UI/UX design, accessibility, user experience",
            "typical_duration": (45, 120)
        },
        "devops-engineer": {
            "specialization": "CI/CD, deployment, infrastructure",
            "typical_duration": (30, 90)
        },
        "security-specialist": {
            "specialization": "Security review, vulnerability assessment",
            "typical_duration": (60, 150)
        },
        "database-architect": {
            "specialization": "Database design, query optimization, indexing",
            "typical_duration": (60, 180)
        },
        "performance-engineer": {
            "specialization": "Performance optimization, profiling, benchmarking",
            "typical_duration": (45, 120)
        }
    }

    # Agent selection rules based on topic keywords
    SELECTION_RULES = {
        "auth": ["backend-architect", "security-specialist"],
        "database": ["backend-architect", "database-architect"],
        "UI": ["ux-ui-designer"],
        "API": ["backend-architect"],
        "deploy": ["devops-engineer"],
        "performance": ["performance-engineer"],
        "security": ["security-specialist"]
    }

    # Mode delegation rules
    MODE_RULES = {
        "quick": {
            "delegation": False,
            "agents_count": 0,
            "output_items": (5, 7)
        },
        "default": {
            "delegation": "optional",
            "agents_count": (0, 2),
            "output_items": (7, 15)
        },
        "thorough": {
            "delegation": True,
            "agents_count": (2, 4),
            "output_items": (15, 30)
        }
    }


class AgentDelegator:
    """Handle agent selection and delegation."""

    def __init__(self):
        """Initialize agent delegator."""
        self.config = AgentConfig()

    def select_agents(self, topic: str, mode: str) -> List[str]:
        """
        Select agents based on topic and mode.

        Args:
            topic: Brainstorm topic
            mode: Time budget mode (quick/default/thorough)

        Returns:
            List of agent names to use
        """
        # Quick mode: no agents
        if mode == "quick":
            return []

        # Get mode rules
        mode_config = self.config.MODE_RULES.get(mode, self.config.MODE_RULES["default"])

        # If delegation not allowed/required, handle accordingly
        if mode_config["delegation"] is False:
            return []

        # Find matching agents based on topic keywords
        selected = set()
        topic_lower = topic.lower() if topic else ""

        for keyword, agents in self.config.SELECTION_RULES.items():
            if keyword.lower() in topic_lower:
                selected.update(agents)

        # Convert to list
        selected_list = list(selected)

        # Enforce agent count constraints
        agents_count = mode_config["agents_count"]

        if isinstance(agents_count, tuple):
            min_agents, max_agents = agents_count

            # Thorough mode requires minimum agents
            if mode == "thorough" and len(selected_list) < min_agents:
                # Add default agents to meet minimum
                all_agents = list(self.config.AGENTS.keys())
                for agent in all_agents:
                    if agent not in selected_list:
                        selected_list.append(agent)
                        if len(selected_list) >= min_agents:
                            break

            # Limit to maximum
            if len(selected_list) > max_agents:
                selected_list = selected_list[:max_agents]

        return selected_list

    def get_agent_config(self, agent_name: str) -> Dict[str, Any]:
        """
        Get configuration for an agent.

        Args:
            agent_name: Agent name

        Returns:
            Agent configuration dict
        """
        return self.config.AGENTS.get(agent_name, {})

    def get_all_agents(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all available agents.

        Returns:
            Dictionary of all agent configurations
        """
        return self.config.AGENTS

    def get_mode_config(self, mode: str) -> Dict[str, Any]:
        """
        Get delegation configuration for a mode.

        Args:
            mode: Time budget mode

        Returns:
            Mode configuration dict
        """
        return self.config.MODE_RULES.get(mode, self.config.MODE_RULES["default"])

    def should_delegate(self, mode: str) -> bool:
        """
        Check if mode should use agent delegation.

        Args:
            mode: Time budget mode

        Returns:
            True if delegation should be used
        """
        mode_config = self.get_mode_config(mode)
        delegation = mode_config.get("delegation", False)

        # Convert to boolean
        if delegation == "optional":
            return True  # Can delegate
        return bool(delegation)

    def get_agent_count_range(self, mode: str) -> Tuple[int, int]:
        """
        Get agent count range for a mode.

        Args:
            mode: Time budget mode

        Returns:
            Tuple of (min_agents, max_agents)
        """
        mode_config = self.get_mode_config(mode)
        agents_count = mode_config.get("agents_count", 0)

        if isinstance(agents_count, tuple):
            return agents_count
        else:
            return (agents_count, agents_count)


class SkillActivator:
    """Auto-activate skills based on keywords."""

    # Auto-activating skills
    SKILLS = {
        "backend-designer": {
            "triggers": ["API", "database", "backend", "auth", "REST"],
            "provides": ["API patterns", "database design", "auth strategies"]
        },
        "frontend-designer": {
            "triggers": ["UI", "UX", "component", "React", "Vue", "accessibility"],
            "provides": ["Component patterns", "state management", "a11y checklist"]
        },
        "devops-helper": {
            "triggers": ["deploy", "CI/CD", "Docker", "Kubernetes", "infrastructure"],
            "provides": ["Deployment strategies", "platform recommendations", "cost estimates"]
        }
    }

    def should_activate(self, skill_name: str, topic: str) -> bool:
        """
        Check if skill should activate for topic.

        Args:
            skill_name: Skill name
            topic: Brainstorm topic

        Returns:
            True if skill should activate
        """
        skill = self.SKILLS.get(skill_name)
        if not skill:
            return False

        topic_lower = topic.lower() if topic else ""
        triggers = skill.get("triggers", [])

        for trigger in triggers:
            if trigger.lower() in topic_lower:
                return True

        return False

    def get_activated_skills(self, topic: str) -> List[str]:
        """
        Get list of skills that should activate.

        Args:
            topic: Brainstorm topic

        Returns:
            List of skill names
        """
        activated = []

        for skill_name in self.SKILLS:
            if self.should_activate(skill_name, topic):
                activated.append(skill_name)

        return activated

    def get_skill_config(self, skill_name: str) -> Dict[str, Any]:
        """
        Get skill configuration.

        Args:
            skill_name: Skill name

        Returns:
            Skill configuration dict
        """
        return self.SKILLS.get(skill_name, {})


# Module-level convenience functions

def select_agents(topic: str, mode: str = "default") -> List[str]:
    """
    Select agents for brainstorm.

    Args:
        topic: Brainstorm topic
        mode: Time budget mode (quick/default/thorough)

    Returns:
        List of agent names to use
    """
    delegator = AgentDelegator()
    return delegator.select_agents(topic, mode)


def get_available_agents() -> Dict[str, Dict[str, Any]]:
    """
    Get all available agents.

    Returns:
        Dictionary of agent configurations
    """
    delegator = AgentDelegator()
    return delegator.get_all_agents()


def get_agent_selection_rules() -> Dict[str, List[str]]:
    """
    Get agent selection rules.

    Returns:
        Dictionary mapping keywords to agent lists
    """
    return AgentConfig.SELECTION_RULES


def get_mode_examples() -> Dict[str, Dict[str, Any]]:
    """
    Get mode configuration examples.

    Returns:
        Dictionary of mode configurations
    """
    return AgentConfig.MODE_RULES


def get_auto_activating_skills() -> Dict[str, Dict[str, Any]]:
    """
    Get auto-activating skill configurations.

    Returns:
        Dictionary of skill configurations
    """
    return SkillActivator.SKILLS
