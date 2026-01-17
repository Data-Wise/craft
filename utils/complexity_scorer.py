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
        r'\band\b',  # "lint and test"
        r',',  # "lint, test, build"
        r'\bthen\b',  # "build then deploy"
        r'\bafter\b',  # "test after build"
        r'\bwith\b.*\band\b',  # "with tests and docs"
    ]

    # Count action verbs
    action_verbs = [
        'add', 'create', 'implement', 'build', 'design', 'refactor',
        'test', 'validate', 'check', 'lint', 'format', 'fix',
        'update', 'modify', 'deploy', 'configure', 'setup'
    ]

    verb_count = sum(1 for verb in action_verbs if verb in task_lower)
    has_multi_step_indicator = any(re.search(pattern, task_lower) for pattern in multi_step_indicators)

    if verb_count >= 3 or has_multi_step_indicator:
        score += 2

    # Factor 2: Cross-category task (+2)
    # Check for mentions of different categories
    categories = {
        'code': ['code', 'implement', 'refactor', 'fix', 'bug', 'feature'],
        'test': ['test', 'coverage', 'validate'],
        'docs': ['doc', 'documentation', 'readme', 'comment'],
        'ci': ['ci', 'pipeline', 'workflow', 'deploy', 'build'],
        'architecture': ['design', 'architecture', 'pattern', 'structure', 'system'],
        'security': ['auth', 'oauth', 'security', 'token', 'session']
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
    # Look for architectural/design keywords
    planning_keywords = [
        'design', 'architecture', 'plan', 'strategy', 'approach',
        'pattern', 'structure', 'system', 'framework', 'flow'
    ]

    if any(keyword in task_lower for keyword in planning_keywords):
        score += 2

    # Factor 4: Requires research (+2)
    # Look for investigation/exploration keywords
    research_keywords = [
        'research', 'investigate', 'explore', 'analyze', 'study',
        'compare', 'evaluate', 'review', 'understand', 'how to'
    ]

    if any(keyword in task_lower for keyword in research_keywords):
        score += 2

    # Factor 5: Multi-file changes (+2)
    # Look for keywords indicating broad impact
    multi_file_indicators = [
        'system', 'module', 'package', 'library', 'entire',
        'all', 'multiple', 'across', 'throughout', 'ecosystem'
    ]

    # Also check for mentions of multiple specific files/components
    component_mentions = len(re.findall(r'\b\w+\.(py|js|ts|md|yml|json)\b', task))

    if component_mentions >= 5 or any(indicator in task_lower for indicator in multi_file_indicators):
        score += 2

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
        Dictionary with score, routing, and explanation
    """
    score = calculate_complexity_score(task)
    routing = get_routing_decision(score)

    # Re-calculate to get explanations
    task_lower = task.lower()
    factors = []

    # Check each factor
    action_verbs = ['add', 'create', 'implement', 'build', 'design', 'refactor',
                   'test', 'validate', 'check', 'lint', 'format', 'fix',
                   'update', 'modify', 'deploy', 'configure', 'setup']
    verb_count = sum(1 for verb in action_verbs if verb in task_lower)

    if verb_count >= 3 or any(pattern in task_lower for pattern in ['and', ',', 'then']):
        factors.append("Multi-step task (+2)")

    categories = {
        'code': ['code', 'implement', 'refactor', 'fix', 'bug', 'feature'],
        'test': ['test', 'coverage', 'validate'],
        'docs': ['doc', 'documentation', 'readme', 'comment'],
        'ci': ['ci', 'pipeline', 'workflow', 'deploy', 'build'],
        'architecture': ['design', 'architecture', 'pattern', 'structure', 'system'],
        'security': ['auth', 'oauth', 'security', 'token', 'session']
    }

    matched_categories = set()
    for category, keywords in categories.items():
        if any(keyword in task_lower for keyword in keywords):
            matched_categories.add(category)

    if len(matched_categories) >= 2:
        factors.append(f"Cross-category task ({', '.join(matched_categories)}) (+2)")

    if len(matched_categories) >= 4:
        factors.append(f"Comprehensive task ({len(matched_categories)} categories) (+2)")

    planning_keywords = ['design', 'architecture', 'plan', 'strategy', 'approach',
                        'pattern', 'structure', 'system', 'framework', 'flow']
    if any(keyword in task_lower for keyword in planning_keywords):
        factors.append("Requires planning (+2)")

    research_keywords = ['research', 'investigate', 'explore', 'analyze', 'study',
                        'compare', 'evaluate', 'review', 'understand', 'how to']
    if any(keyword in task_lower for keyword in research_keywords):
        factors.append("Requires research (+2)")

    multi_file_indicators = ['system', 'module', 'package', 'library', 'entire',
                            'all', 'multiple', 'across', 'throughout', 'ecosystem']
    component_mentions = len(re.findall(r'\b\w+\.(py|js|ts|md|yml|json)\b', task))

    if component_mentions >= 5 or any(indicator in task_lower for indicator in multi_file_indicators):
        factors.append("Multi-file changes (+2)")

    return {
        "task": task,
        "score": score,
        "routing": routing,
        "factors": factors,
        "explanation": f"Score {score}/10 → Route to {routing}" +
                      (f" ({', '.join(factors)})" if factors else " (no complexity factors)")
    }


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
        if result['factors']:
            print(f"Factors:")
            for factor in result['factors']:
                print(f"  - {factor}")
        else:
            print("Factors: None (simple task)")
