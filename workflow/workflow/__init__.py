"""
Workflow plugin for Claude Code.

Provides brainstorming and workflow automation tools with:
- Time budget modes (quick/default/thorough)
- Multiple output formats (terminal/json/markdown)
- Agent delegation for complex analysis
- ADHD-friendly structured outputs
"""

__version__ = "2.0.0"

from .mode_parser import ModeParser, parse_mode_from_command
from .time_budgets import (
    TimeBudget,
    get_time_budgets,
    get_budget_for_mode,
    enforce_time_budget
)
from .format_handlers import (
    FormatHandler,
    TerminalFormatter,
    JSONFormatter,
    MarkdownFormatter,
    FormatHandlerFactory,
    format_output,
    get_format_handler
)
from .agent_delegation import (
    AgentConfig,
    AgentDelegator,
    SkillActivator,
    select_agents,
    get_available_agents,
    get_agent_selection_rules,
    get_mode_examples,
    get_auto_activating_skills
)

__all__ = [
    # Version
    "__version__",

    # Mode Parser
    "ModeParser",
    "parse_mode_from_command",

    # Time Budgets
    "TimeBudget",
    "get_time_budgets",
    "get_budget_for_mode",
    "enforce_time_budget",

    # Format Handlers
    "FormatHandler",
    "TerminalFormatter",
    "JSONFormatter",
    "MarkdownFormatter",
    "FormatHandlerFactory",
    "format_output",
    "get_format_handler",

    # Agent Delegation
    "AgentConfig",
    "AgentDelegator",
    "SkillActivator",
    "select_agents",
    "get_available_agents",
    "get_agent_selection_rules",
    "get_mode_examples",
    "get_auto_activating_skills",
]
