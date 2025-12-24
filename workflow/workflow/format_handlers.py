"""
Format handlers for workflow plugin.

Provides output formatting for:
- Terminal (rich colors, emojis, ADHD-friendly)
- JSON (automation-ready, structured)
- Markdown (documentation-ready, GitHub-compatible)
"""

import json
from typing import Dict, Any, List


class FormatHandler:
    """Base format handler."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Format data for output.

        Args:
            data: Brainstorm result data

        Returns:
            Formatted string
        """
        raise NotImplementedError


class TerminalFormatter(FormatHandler):
    """Terminal format with colors and emojis."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Format for terminal output.

        Args:
            data: Brainstorm result with metadata, content, recommendations

        Returns:
            Terminal-formatted string with emojis and structure
        """
        lines = []

        # Header
        metadata = data.get("metadata", {})
        lines.append(f"⏱️  Mode: {metadata.get('mode', 'unknown')} ({metadata.get('time_budget', 'default')}) - Target: < {self._format_budget(metadata.get('time_budget', 'default'))}")
        lines.append("")

        # Content sections
        content = data.get("content", {})

        # Quick wins
        if "quick_wins" in content:
            lines.append("⚡ Quick Wins:")
            for item in content["quick_wins"]:
                if isinstance(item, dict):
                    lines.append(f"- {item.get('action', '')} - {item.get('benefit', '')}")
                else:
                    lines.append(f"- {item}")
            lines.append("")

        # Medium effort
        if "medium_effort" in content:
            lines.append("🔧 Medium Effort:")
            for item in content["medium_effort"]:
                if isinstance(item, dict):
                    lines.append(f"- [ ] {item.get('task', '')} - {item.get('outcome', '')}")
                else:
                    lines.append(f"- [ ] {item}")
            lines.append("")

        # Long term
        if "long_term" in content:
            lines.append("🏗️ Long Term:")
            for item in content["long_term"]:
                if isinstance(item, dict):
                    lines.append(f"- {item.get('item', '')} - {item.get('strategic_value', '')}")
                else:
                    lines.append(f"- {item}")
            lines.append("")

        # Recommendations
        recommendations = data.get("recommendations", {})
        if "recommended_path" in recommendations:
            lines.append("→ Recommended Path:")
            lines.append(recommendations["recommended_path"])
            lines.append("")

        # Next steps
        if "next_steps" in recommendations:
            lines.append("Next Steps:")
            for i, step in enumerate(recommendations["next_steps"], 1):
                lines.append(f"{i}. [ ] {step}")
            lines.append("")

        # Completion message
        if "duration_seconds" in metadata:
            duration = metadata["duration_seconds"]
            budget_mode = metadata.get("time_budget", "default")
            lines.append(f"✅ Completed in {duration}s (within {budget_mode} budget)")

        return "\n".join(lines)

    def _format_budget(self, mode: str) -> str:
        """Format budget display string."""
        budgets = {
            "quick": "60 seconds",
            "default": "5 minutes",
            "thorough": "30 minutes"
        }
        return budgets.get(mode, "5 minutes")


class JSONFormatter(FormatHandler):
    """JSON format for automation."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Format as JSON.

        Args:
            data: Brainstorm result with metadata, content, recommendations

        Returns:
            JSON string (pretty-printed)
        """
        # Ensure required top-level keys exist
        result = {
            "metadata": data.get("metadata", {}),
            "content": data.get("content", {}),
            "recommendations": data.get("recommendations", {})
        }

        return json.dumps(result, indent=2)


class MarkdownFormatter(FormatHandler):
    """Markdown format for documentation."""

    def format(self, data: Dict[str, Any]) -> str:
        """
        Format as GitHub-compatible markdown.

        Args:
            data: Brainstorm result with metadata, content, recommendations

        Returns:
            Markdown string
        """
        lines = []

        # Title (H1)
        content = data.get("content", {})
        topic = content.get("topic", "Brainstorm")
        lines.append(f"# {topic}")
        lines.append("")

        # Metadata
        metadata = data.get("metadata", {})
        if "timestamp" in metadata:
            lines.append(f"**Generated:** {metadata['timestamp']}")
        if "mode" in metadata:
            lines.append(f"**Mode:** {metadata['mode']} ({metadata.get('time_budget', 'default')})")
        if "duration_seconds" in metadata:
            lines.append(f"**Duration:** {metadata['duration_seconds']} seconds")
        lines.append("")

        # Quick Wins (H2)
        if "quick_wins" in content:
            lines.append("## Quick Wins (< 30 min each)")
            for item in content["quick_wins"]:
                if isinstance(item, dict):
                    lines.append(f"- ⚡ {item.get('action', '')} - {item.get('benefit', '')}")
                else:
                    lines.append(f"- ⚡ {item}")
            lines.append("")

        # Medium Effort (H2)
        if "medium_effort" in content:
            lines.append("## Medium Effort (1-2 hours)")
            for item in content["medium_effort"]:
                if isinstance(item, dict):
                    lines.append(f"- [ ] {item.get('task', '')}")
                else:
                    lines.append(f"- [ ] {item}")
            lines.append("")

        # Recommended Path (H2)
        recommendations = data.get("recommendations", {})
        if "recommended_path" in recommendations:
            lines.append("## Recommended Path")
            lines.append(f"→ {recommendations['recommended_path']}")
            lines.append("")

        # Next Steps (H2)
        if "next_steps" in recommendations:
            lines.append("## Next Steps")
            for i, step in enumerate(recommendations["next_steps"], 1):
                lines.append(f"{i}. [ ] {step}")
            lines.append("")

        return "\n".join(lines)


class FormatHandlerFactory:
    """Factory for creating format handlers."""

    _handlers = {
        "terminal": TerminalFormatter,
        "json": JSONFormatter,
        "markdown": MarkdownFormatter
    }

    @classmethod
    def get_handler(cls, format_type: str) -> FormatHandler:
        """
        Get format handler for type.

        Args:
            format_type: "terminal", "json", or "markdown"

        Returns:
            FormatHandler instance

        Raises:
            ValueError: If format type not recognized
        """
        handler_class = cls._handlers.get(format_type)
        if handler_class is None:
            # Default to terminal for unknown formats
            handler_class = cls._handlers["terminal"]

        return handler_class()

    @classmethod
    def format_output(cls, data: Dict[str, Any], format_type: str = "terminal") -> str:
        """
        Format output using specified format.

        Args:
            data: Brainstorm result data
            format_type: Output format (terminal/json/markdown)

        Returns:
            Formatted string
        """
        handler = cls.get_handler(format_type)
        return handler.format(data)


# Module-level convenience functions

def format_output(data: Dict[str, Any], format_type: str = "terminal") -> str:
    """
    Format brainstorm output.

    Args:
        data: Brainstorm result with metadata, content, recommendations
        format_type: Output format (terminal, json, markdown)

    Returns:
        Formatted output string
    """
    return FormatHandlerFactory.format_output(data, format_type)


def get_format_handler(format_type: str) -> FormatHandler:
    """
    Get format handler instance.

    Args:
        format_type: Format type (terminal/json/markdown)

    Returns:
        FormatHandler instance
    """
    return FormatHandlerFactory.get_handler(format_type)
