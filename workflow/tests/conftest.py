"""
Pytest configuration and shared fixtures for workflow plugin tests.

This file provides:
- Mock command data
- Mock brainstorm results
- Time budget fixtures
- Mode detection fixtures
- Format handler fixtures
"""

import pytest
import json
from datetime import datetime
from typing import Dict, List, Any


# ============================================================================
# Mock Data Fixtures
# ============================================================================

@pytest.fixture
def mock_brainstorm_quick_result():
    """Mock result from quick mode brainstorm."""
    return {
        "metadata": {
            "timestamp": "2024-12-24T10:30:00Z",
            "mode": "feature",
            "time_budget": "quick",
            "duration_seconds": 45,
            "agents_used": []
        },
        "content": {
            "topic": "User notifications",
            "quick_wins": [
                {"action": "Email notifications", "benefit": "Easy to implement", "effort": "< 30 min"},
                {"action": "Basic templates", "benefit": "Reusable patterns", "effort": "< 30 min"}
            ],
            "medium_effort": [
                {"task": "In-app notifications", "outcome": "Better UX", "effort": "1-2 hours"}
            ],
            "long_term": [
                {"item": "Push notifications", "strategic_value": "Mobile engagement"}
            ]
        },
        "recommendations": {
            "recommended_path": "Start with email notifications using SendGrid...",
            "next_steps": [
                "Set up email service (SendGrid/Mailgun)",
                "Create notification templates",
                "Add user notification preferences"
            ]
        }
    }


@pytest.fixture
def mock_brainstorm_thorough_result():
    """Mock result from thorough mode with agent delegation."""
    return {
        "metadata": {
            "timestamp": "2024-12-24T14:00:00Z",
            "mode": "architecture",
            "time_budget": "thorough",
            "duration_seconds": 204,  # 3m 24s
            "agents_used": ["backend-architect", "database-architect"]
        },
        "content": {
            "topic": "Multi-tenant SaaS architecture",
            "quick_wins": [
                {"action": "Schema-based isolation", "benefit": "Simpler than DB-per-tenant", "effort": "1-2 days"}
            ],
            "medium_effort": [
                {"task": "Tenant context middleware", "outcome": "Automatic row filtering", "effort": "3-5 days"}
            ],
            "long_term": [
                {"item": "Database-per-tenant for enterprise", "strategic_value": "Data isolation compliance"}
            ],
            "agent_analysis": {
                "backend_architect": {
                    "recommendations": ["Use PostgreSQL row-level security", "Implement tenant_id in all tables"],
                    "duration": 102
                },
                "database_architect": {
                    "recommendations": ["Index on tenant_id + created_at", "Partition large tables by tenant"],
                    "duration": 98
                }
            }
        },
        "recommendations": {
            "recommended_path": "Start with schema-based isolation using PostgreSQL RLS...",
            "next_steps": [
                "Design schema with tenant_id column",
                "Implement RLS policies",
                "Create tenant context middleware",
                "Test with 10+ tenants"
            ]
        }
    }


@pytest.fixture
def mock_command_input():
    """Mock command input for testing mode parsing."""
    return {
        "quick_feature": "/brainstorm quick feature user auth",
        "thorough_architecture": "/brainstorm thorough architecture multi-tenant",
        "default_design": "/brainstorm design dashboard UX",
        "json_format": "/brainstorm --format json feature notifications",
        "markdown_format": "/brainstorm --format markdown architecture oauth"
    }


# ============================================================================
# Time Budget Fixtures
# ============================================================================

@pytest.fixture
def time_budgets():
    """Time budget configurations for all modes."""
    return get_time_budgets()


@pytest.fixture
def mode_examples():
    """Example mode configurations with expected behaviors."""
    return get_mode_examples()


# ============================================================================
# Mode Detection Fixtures
# ============================================================================

@pytest.fixture
def mode_keywords():
    """Keywords that trigger specific modes."""
    return {
        "feature": ["feature", "functionality", "user story", "requirement"],
        "architecture": ["architecture", "system design", "scalability", "infrastructure"],
        "design": ["UI", "UX", "design", "layout", "accessibility", "a11y"],
        "backend": ["API", "backend", "database", "server", "endpoint"],
        "frontend": ["component", "React", "Vue", "Angular", "frontend", "state"],
        "devops": ["deploy", "CI/CD", "Docker", "Kubernetes", "infrastructure"]
    }


@pytest.fixture
def context_examples():
    """Example contexts for mode auto-detection."""
    return {
        "feature_context": "I need to add user authentication with OAuth support",
        "architecture_context": "Design a scalable multi-tenant SaaS architecture",
        "design_context": "Improve the dashboard UX with better accessibility",
        "backend_context": "Create REST API endpoints for user management",
        "frontend_context": "Build React components for the notification system",
        "devops_context": "Set up CI/CD pipeline with GitHub Actions"
    }


# ============================================================================
# Format Handler Fixtures
# ============================================================================

@pytest.fixture
def format_outputs():
    """Expected output structures for different formats."""
    return {
        "terminal": {
            "has_colors": True,
            "has_emojis": True,
            "has_tables": False,
            "structure": ["header", "quick_wins", "medium_effort", "long_term", "next_steps"]
        },
        "json": {
            "is_valid_json": True,
            "has_metadata": True,
            "has_content": True,
            "has_recommendations": True,
            "required_fields": ["metadata", "content", "recommendations"]
        },
        "markdown": {
            "has_headers": True,
            "has_lists": True,
            "has_checkboxes": True,
            "structure": ["# Title", "## Quick Wins", "## Medium Effort", "## Next Steps"]
        }
    }


@pytest.fixture
def sample_markdown_output():
    """Sample markdown output for format validation."""
    return """# User Notifications Brainstorm

**Generated:** 2024-12-24 10:30
**Mode:** feature (quick)
**Duration:** 45 seconds

## Quick Wins (< 30 min each)
- ⚡ Email notifications - Easy to implement
- ⚡ Basic templates - Reusable patterns

## Medium Effort (1-2 hours)
- [ ] In-app notifications
- [ ] User preferences UI

## Recommended Path
→ Start with email notifications using SendGrid...

## Next Steps
1. [ ] Set up email service
2. [ ] Create templates
3. [ ] Add preferences
"""


# ============================================================================
# Agent Delegation Fixtures
# ============================================================================

@pytest.fixture
def available_agents():
    """List of agents available for delegation."""
    return get_available_agents()


@pytest.fixture
def agent_selection_rules():
    """Rules for automatic agent selection based on topic."""
    return get_agent_selection_rules()


# ============================================================================
# Skill Activation Fixtures
# ============================================================================

@pytest.fixture
def auto_activating_skills():
    """Skills that auto-activate based on keywords."""
    return get_auto_activating_skills()


# ============================================================================
# Backward Compatibility Fixtures
# ============================================================================

@pytest.fixture
def v1_commands():
    """v0.1.0 commands that must still work in v2.0."""
    return [
        "/brainstorm",
        "/brainstorm quick",
        "/brainstorm thorough",
        "/brainstorm feature auth",
        "/brainstorm architecture oauth",
        "/brainstorm design dashboard"
    ]


@pytest.fixture
def v2_commands():
    """New v2.0 commands with format parameter."""
    return [
        "/brainstorm --format json",
        "/brainstorm --format markdown",
        "/brainstorm quick feature auth",
        "/brainstorm thorough architecture oauth --format json"
    ]


# ============================================================================
# Validation Fixtures
# ============================================================================

@pytest.fixture
def validation_rules():
    """Validation rules for brainstorm outputs."""
    return {
        "quick_wins_count": (3, 7),  # min, max
        "medium_effort_count": (1, 5),
        "long_term_count": (1, 3),
        "next_steps_count": (3, 10),
        "topic_min_length": 3,
        "topic_max_length": 100
    }


# ============================================================================
# Helper Functions
# ============================================================================

# Import the actual implementations
import sys
import os

# Add workflow module to path
workflow_path = os.path.join(os.path.dirname(__file__), '..')
sys.path.insert(0, workflow_path)

from workflow.mode_parser import parse_mode_from_command
from workflow import (
    get_time_budgets,
    get_mode_examples,
    get_available_agents,
    get_agent_selection_rules,
    get_auto_activating_skills
)


# Make helper available to all tests
pytest.parse_mode_from_command = parse_mode_from_command


# ============================================================================
# Pytest Hooks
# ============================================================================

def pytest_configure(config):
    """Configure pytest with custom settings."""
    config.addinivalue_line(
        "markers", "unit: Unit tests (fast, isolated)"
    )
    config.addinivalue_line(
        "markers", "integration: Integration tests (multiple components)"
    )
    config.addinivalue_line(
        "markers", "performance: Performance and benchmark tests"
    )
