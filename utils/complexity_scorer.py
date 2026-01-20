#!/usr/bin/env python3
"""
Complexity Scoring Algorithm for /craft:do routing decisions.

Scores tasks on 0-10 scale based on 5 factors:
- Multi-step task (requires 3+ distinct operations): +2
- Cross-category task (spans multiple categories): +2
- Requires planning (needs design/architecture phase): +2
- Requires research (needs investigation/exploration): +2
- Multi-file changes (affects 5+ files): +2

Routing decisions:
- 0-3: Route to specific commands
- 4-7: Delegate to single specialized agent
- 8-10: Delegate to orchestrator-v2 for multi-agent coordination
"""

import re
from typing import List, Dict


def calculate_complexity_score(task: str) -> int:
    """
    Calculate complexity score for a task.

    Args:
        task: Task description string

    Returns:
        Complexity score (0-10)
    """
    score = 0
    task_lower = task.lower()

    # Factor 1: Multi-step task (+2)
    # Look for multiple verbs or explicit multi-step indicators
    multi_step_indicators = [
        r"\band\b",  # "lint and test"
        r",",  # "lint, test, build"
        r"\bthen\b",  # "build then deploy"
        r"\bafter\b",  # "test after build"
        r"\bwith\b.*\band\b",  # "with tests and docs"
    ]

    # Count action verbs
    action_verbs = [
        "add",
        "create",
        "implement",
        "build",
        "design",
        "refactor",
        "test",
        "validate",
        "check",
        "lint",
        "format",
        "fix",
        "update",
        "modify",
        "deploy",
        "configure",
        "setup",
        "optimize",
    ]

    # Count complexity indicators that suggest non-trivial work
    complexity_indicators = [
        "comprehensive",
        "complete",
        "full",
        "entire",
        "all",
        "advanced",
        "robust",
        "scalable",
        "production-ready",
    ]

    verb_count = sum(1 for verb in action_verbs if verb in task_lower)
    has_multi_step_indicator = any(
        re.search(pattern, task_lower) for pattern in multi_step_indicators
    )
    has_complexity_indicator = any(
        indicator in task_lower for indicator in complexity_indicators
    )

    # Lower threshold: 2+ verbs OR multi-step indicator OR complexity indicator
    if verb_count >= 2 or has_multi_step_indicator or has_complexity_indicator:
        score += 2

    # Factor 2: Cross-category task (+2)
    # Check for mentions of different categories
    categories = {
        "code": [
            "code",
            "implement",
            "refactor",
            "fix",
            "bug",
            "feature",
            "function",
            "class",
            "module",
        ],
        "test": ["test", "coverage", "validate", "testing"],
        "docs": ["doc", "documentation", "readme", "comment"],
        "ci": ["ci", "pipeline", "workflow", "deploy", "build", "deployment"],
        "architecture": [
            "design",
            "architecture",
            "pattern",
            "structure",
            "system",
            "microservice",
            "api",
        ],
        "security": ["auth", "oauth", "security", "token", "session"],
        "database": ["database", "migration", "schema", "query", "queries", "db"],
        "error_handling": ["error", "exception", "handling", "validation"],
    }

    matched_categories = set()
    for category, keywords in categories.items():
        if any(keyword in task_lower for keyword in keywords):
            matched_categories.add(category)

    if len(matched_categories) >= 2:
        score += 2

    # Bonus for tasks spanning 4+ categories (very comprehensive)
    if len(matched_categories) >= 4:
        score += 2

    # Factor 3: Requires planning (+2)
    # Look for architectural/design keywords or tasks that inherently need planning
    planning_keywords = [
        "design",
        "architecture",
        "plan",
        "strategy",
        "approach",
        "pattern",
        "structure",
        "system",
        "framework",
        "flow",
        "optimize",
        "performance",
        "scalability",
        "microservice",
        "migration",
        "redesign",
        "restructure",
    ]

    if any(keyword in task_lower for keyword in planning_keywords):
        score += 2

    # Factor 4: Requires research (+2)
    # Look for investigation/exploration keywords
    research_keywords = [
        "research",
        "investigate",
        "explore",
        "analyze",
        "study",
        "compare",
        "evaluate",
        "review",
        "understand",
        "how to",
    ]

    if any(keyword in task_lower for keyword in research_keywords):
        score += 2

    # Factor 5: Multi-file changes (+2)
    # Look for keywords indicating broad impact
    multi_file_indicators = [
        "system",
        "module",
        "package",
        "library",
        "entire",
        "all",
        "multiple",
        "across",
        "throughout",
        "ecosystem",
        "microservice",
        "pipeline",
    ]

    # Also check for mentions of multiple specific files/components
    component_mentions = len(re.findall(r"\b\w+\.(py|js|ts|md|yml|json)\b", task))

    if component_mentions >= 5 or any(
        indicator in task_lower for indicator in multi_file_indicators
    ):
        score += 2

    # Factor 6: Inherently complex keywords (+2)
    # Some keywords indicate moderate-to-high complexity by themselves
    high_complexity_keywords = [
        "comprehensive",
        "optimize",
        "redesign",
        "microservice",
        "authentication",
        "migration",
        "scalable",
        "performance",
    ]

    if any(keyword in task_lower for keyword in high_complexity_keywords):
        score += 2

    # Factor 7: Major architectural changes (+2)
    # Detect combinations that indicate system-wide architectural overhaul
    architectural_change_patterns = [
        ("redesign", "architecture"),
        ("redesign", "system"),
        ("refactor", "architecture"),
        ("migrate", "architecture"),
    ]

    for keyword1, keyword2 in architectural_change_patterns:
        if keyword1 in task_lower and keyword2 in task_lower:
            score += 2
            break

    # Cap at 10
    return min(score, 10)


def get_routing_decision(score: int) -> str:
    """
    Map complexity score to routing decision.

    Args:
        score: Complexity score (0-10)

    Returns:
        Routing decision: "commands", "agent", or "orchestrator"
    """
    if score <= 3:
        return "commands"
    elif score <= 7:
        return "agent"
    else:
        return "orchestrator"


def explain_score(task: str) -> Dict[str, any]:
    """
    Calculate score and explain which factors contributed.

    Args:
        task: Task description string

    Returns:
        Dictionary with score, routing, explanation, and factors list
    """
    task_lower = task.lower()
    factors = []

    # Check multi-step
    multi_step_indicators = [r"\band\b", r",", r"\bthen\b", r"\bafter\b", r"\bwith\b.*\band\b"]
    action_verbs = ["add", "create", "implement", "build", "design", "refactor", "test", "validate", "check", "lint", "format", "fix", "update", "modify", "deploy", "configure", "setup", "optimize"]
    complexity_indicators = ["comprehensive", "complete", "full", "entire", "all", "advanced", "robust", "scalable", "production-ready"]

    verb_count = sum(1 for verb in action_verbs if verb in task_lower)
    has_multi_step_indicator = any(re.search(pattern, task_lower) for pattern in multi_step_indicators)
    has_complexity_indicator = any(indicator in task_lower for indicator in complexity_indicators)

    if verb_count >= 2 or has_multi_step_indicator or has_complexity_indicator:
        factors.append("Multi-step task (+2)")

    # Check cross-category
    categories = {
        "code": ["code", "implement", "refactor", "fix", "bug", "feature", "function", "class", "module"],
        "test": ["test", "coverage", "validate", "testing"],
        "docs": ["doc", "documentation", "readme", "comment"],
        "ci": ["ci", "pipeline", "workflow", "deploy", "build", "deployment"],
        "architecture": ["design", "architecture", "pattern", "structure", "system", "microservice", "api"],
        "security": ["auth", "oauth", "security", "token", "session"],
        "database": ["database", "migration", "schema", "query", "queries", "db"],
        "error_handling": ["error", "exception", "handling", "validation"],
    }

    matched_categories = set()
    for category, keywords in categories.items():
        if any(keyword in task_lower for keyword in keywords):
            matched_categories.add(category)

    if len(matched_categories) >= 2:
        factors.append(f"Cross-category task: {', '.join(matched_categories)} (+2)")
    if len(matched_categories) >= 4:
        factors.append("Very comprehensive (4+ categories) (+2)")

    # Check planning
    planning_keywords = ["design", "architecture", "plan", "strategy", "structure", "pattern", "microservice", "system design", "api design", "refactor"]
    if any(keyword in task_lower for keyword in planning_keywords):
        factors.append("Requires planning (+2)")

    # Check research
    research_keywords = ["research", "investigate", "explore", "analyze", "find", "discover", "understand", "learn", "study", "benchmark"]
    if any(keyword in task_lower for keyword in research_keywords):
        factors.append("Requires research (+2)")

    # Check multi-file
    multi_file_indicators = ["multiple files", "across files", "all files", "entire codebase", "whole project", "refactor"]
    large_scope_keywords = ["entire", "whole", "all", "complete", "comprehensive", "system", "module"]

    if any(indicator in task_lower for indicator in multi_file_indicators):
        factors.append("Multi-file changes (+2)")
    elif any(keyword in task_lower for keyword in large_scope_keywords) and len(matched_categories) >= 2:
        factors.append("Multi-file changes (inferred from scope) (+2)")

    score = calculate_complexity_score(task)
    routing = get_routing_decision(score)

    return {
        "task": task,
        "score": score,
        "routing": routing,
        "explanation": f"Score {score}/10 → Route to {routing}",
        "factors": factors,
    }


def recommend_orchestration_mode(complexity_score: int) -> str:
    """
    Recommend orchestration mode based on complexity score.

    Args:
        complexity_score: Task complexity (0-10)

    Returns:
        Recommended mode name: "default", "debug", "optimize", or "release"
    """
    if complexity_score <= 3:
        return "default"
    elif complexity_score <= 5:
        return "default"
    elif complexity_score <= 7:
        return "optimize"
    else:
        return "release"


if __name__ == "__main__":
    # Test cases
    test_cases = [
        "lint code",
        "format code and commit",
        "lint code, run tests, and build project",
        "refactor authentication module and add comprehensive tests",
        "design authentication system with OAuth2, PKCE flow, session management, and refresh token rotation",
        "fix bug in login",
        "investigate performance issue",
        "add feature with tests, docs, and CI",
    ]

    print("Complexity Scoring Test Cases")
    print("=" * 80)

    for task in test_cases:
        result = explain_score(task)
        print(f"\nTask: {task}")
        print(f"Score: {result['score']}/10")
        print(f"Routing: {result['routing']}")
        if result["factors"]:
            print(f"Factors:")
            for factor in result["factors"]:
                print(f"  - {factor}")
        else:
            print("Factors: None (simple task)")
