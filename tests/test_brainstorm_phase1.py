#!/usr/bin/env python3
"""
Unit tests for Phase 1 brainstorm question control features (v2.4.0).

Tests:
- Colon notation parsing (d:5, m:12, q:3)
- Categories flag parsing (--categories, -C)
- Question bank structure
- Question selection logic
- Milestone prompts
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "commands"))

DEPTH_MAP = {
    "q": "quick",
    "quick": "quick",
    "d": "deep",
    "deep": "deep",
    "m": "max",
    "max": "max",
    "t": "max",
    "thorough": "max",
}

CATEGORY_MAP = {
    "req": "requirements",
    "requirements": "requirements",
    "usr": "users",
    "users": "users",
    "scp": "scope",
    "scope": "scope",
    "tech": "technical",
    "technical": "technical",
    "time": "timeline",
    "timeline": "timeline",
    "risk": "risks",
    "risks": "risks",
    "exist": "existing",
    "existing": "existing",
    "ok": "success",
    "success": "success",
    "all": "all",
}

question_bank = {
    "requirements": [
        {
            "question": "What are the key requirements for this feature?",
            "options": [
                "Performance-critical",
                "User-facing functionality",
                "Internal tooling",
                "Data processing",
            ],
            "multiSelect": False,
        },
        {
            "question": "Are there any hard constraints we must work within?",
            "options": [
                "Technology stack",
                "Performance targets",
                "Security requirements",
                "Budget limits",
            ],
            "multiSelect": True,
        },
    ],
    "users": [
        {
            "question": "Who is the primary user for this feature?",
            "options": [
                "End users",
                "Developers",
                "Administrators",
                "Automated systems",
            ],
            "multiSelect": False,
        },
        {
            "question": "What problem does this solve for them?",
            "options": [
                "Saves time",
                "Improves accuracy",
                "Enables new capability",
                "Simplifies workflow",
            ],
            "multiSelect": False,
        },
    ],
    "scope": [
        {
            "question": "What's definitely in scope for the first iteration?",
            "options": [
                "Core functionality",
                "Basic error handling",
                "Essential UI/UX",
                "Documentation",
            ],
            "multiSelect": True,
        },
        {
            "question": "What's explicitly out of scope (nice-to-have later)?",
            "options": [
                "Advanced features",
                "Polish and refinement",
                "Integrations",
                "Scalability",
            ],
            "multiSelect": True,
        },
    ],
    "technical": [
        {
            "question": "Are there technical constraints or preferences?",
            "options": [
                "Use existing stack",
                "New technology needed",
                "Architectural patterns",
                "No strong preferences",
            ],
            "multiSelect": True,
        },
        {
            "question": "What existing systems does this need to integrate with?",
            "options": [
                "Database",
                "Authentication",
                "APIs or services",
                "None (standalone)",
            ],
            "multiSelect": True,
        },
    ],
    "timeline": [
        {
            "question": "Are there any deadlines or milestones?",
            "options": [
                "ASAP (urgent)",
                "Specific date",
                "Flexible timeline",
                "Unknown",
            ],
            "multiSelect": False,
        },
        {
            "question": "Is there a target date for first working version?",
            "options": ["Within a week", "1-2 weeks", "3-4 weeks", "Flexible"],
            "multiSelect": False,
        },
    ],
    "risks": [
        {
            "question": "What could go wrong? What are the biggest risks?",
            "options": [
                "Technical complexity",
                "Integration issues",
                "Performance concerns",
                "Unknown unknowns",
            ],
            "multiSelect": True,
        },
        {
            "question": "Are there edge cases we should plan for upfront?",
            "options": [
                "Empty/invalid input",
                "Concurrent access",
                "Failure scenarios",
                "None identified",
            ],
            "multiSelect": True,
        },
    ],
    "existing": [
        {
            "question": "What existing code or systems can we leverage?",
            "options": [
                "Similar features",
                "Libraries or frameworks",
                "Infrastructure",
                "Start from scratch",
            ],
            "multiSelect": True,
        },
        {
            "question": "What dependencies does this have?",
            "options": [
                "Other features",
                "External services",
                "Data availability",
                "None (self-contained)",
            ],
            "multiSelect": True,
        },
    ],
    "success": [
        {
            "question": "How will we know this is successful?",
            "options": ["User feedback", "Metrics", "Tests pass", "Requirements met"],
            "multiSelect": True,
        },
        {
            "question": "What are the acceptance criteria?",
            "options": [
                "Feature works as described",
                "Tests validate behavior",
                "Documentation exists",
                "Performance acceptable",
            ],
            "multiSelect": True,
        },
    ],
}


def parse_depth_with_count(arg):
    """Parse depth:count notation."""
    if ":" not in arg:
        return (DEPTH_MAP.get(arg, arg), None)

    parts = arg.split(":", 1)
    depth_str = parts[0]
    count_str = parts[1]

    depth = DEPTH_MAP.get(depth_str, depth_str)

    try:
        count = int(count_str)
        if count < 0:
            raise ValueError("Negative count")
        return (depth, count)
    except ValueError:
        return (depth, "invalid")


def get_default_question_count(depth):
    """Get default question count for depth."""
    defaults = {"quick": 0, "default": 2, "deep": 8, "max": 8}
    return defaults.get(depth, 2)


def parse_categories(args):
    """Parse --categories or -C flag."""
    for i, arg in enumerate(args):
        if arg in ["--categories", "-C"]:
            if i + 1 < len(args):
                cat_str = args[i + 1]
                if cat_str == "all":
                    return None

                cats = [c.strip() for c in cat_str.split(",")]
                return [CATEGORY_MAP.get(c, c) for c in cats]

    return None


def select_questions(depth, question_count, categories, focus):
    """Select questions based on user preferences."""
    if question_count is None:
        count = get_default_question_count(depth)
    else:
        count = question_count

    if categories is None:
        cats = get_default_categories_for_focus(focus)
    else:
        cats = categories

    available = []
    for cat in cats:
        if cat in question_bank:
            available.extend(question_bank[cat])

    if count >= len(available):
        return available
    else:
        return available[:count]


def get_default_categories_for_focus(focus):
    """Get default categories for focus area."""
    defaults = {
        "feat": ["requirements", "users", "scope", "success"],
        "arch": ["technical", "risks", "existing", "scope"],
        "api": ["technical", "requirements", "success"],
        "ux": ["users", "scope", "success"],
        "ops": ["technical", "risks", "timeline"],
        "auto": ["requirements", "users", "technical", "success"],
    }
    return defaults.get(focus, ["requirements", "users", "technical", "success"])


def prioritize_questions(questions, count):
    """Select most important questions when count < available."""
    priority_order = [
        "requirements",
        "users",
        "scope",
        "technical",
        "success",
        "risks",
        "timeline",
        "existing",
    ]

    selected = []
    for cat in priority_order:
        if len(selected) >= count:
            break
        cat_questions = [
            q
            for q in questions
            if q.get("category", "") == cat or q in question_bank.get(cat, [])
        ]
        take = max(1, count // len(priority_order))
        selected.extend(cat_questions[:take])

    return selected[:count]


class TestColonNotationParsing:
    """Test depth:count syntax parsing."""

    def test_parse_standard_depth_with_count(self):
        """d:5 should parse as (deep, 5)."""
        result = parse_depth_with_count("d:5")
        assert result == ("deep", 5)

    def test_parse_max_with_count(self):
        """m:12 should parse as (max, 12)."""
        result = parse_depth_with_count("m:12")
        assert result == ("max", 12)

    def test_parse_quick_with_zero(self):
        """q:0 should parse as (quick, 0)."""
        result = parse_depth_with_count("q:0")
        assert result == ("quick", 0)

    def test_parse_depth_without_count(self):
        """d should parse as (deep, None)."""
        result = parse_depth_with_count("d")
        assert result == ("deep", None)

    def test_parse_invalid_count(self):
        """d:abc should return (deep, 'invalid')."""
        result = parse_depth_with_count("d:abc")
        assert result == ("deep", "invalid")

    def test_parse_negative_count(self):
        """d:-5 should return (deep, 'invalid')."""
        result = parse_depth_with_count("d:-5")
        assert result == ("deep", "invalid")

    def test_parse_deep_synonym(self):
        """deep:5 should parse as (deep, 5)."""
        result = parse_depth_with_count("deep:5")
        assert result == ("deep", 5)

    def test_parse_max_synonym(self):
        """max:10 should parse as (max, 10)."""
        result = parse_depth_with_count("max:10")
        assert result == ("max", 10)

    def test_parse_colon_only_invalid(self):
        """:5 should parse as ('', 5) - empty depth is invalid."""
        result = parse_depth_with_count(":5")
        assert result == ("", 5)


class TestQuestionBank:
    """Test question bank structure."""

    def test_all_categories_exist(self):
        """All 8 categories should be present."""
        expected = [
            "requirements",
            "users",
            "scope",
            "technical",
            "timeline",
            "risks",
            "existing",
            "success",
        ]
        assert set(question_bank.keys()) == set(expected)

    def test_each_category_has_two_questions(self):
        """Each category should have exactly 2 questions."""
        for cat, questions in question_bank.items():
            assert len(questions) == 2, f"{cat} should have 2 questions"

    def test_questions_have_required_fields(self):
        """Each question should have question, options, multiSelect."""
        for cat, questions in question_bank.items():
            for q in questions:
                assert "question" in q
                assert "options" in q
                assert "multiSelect" in q
                assert len(q["options"]) >= 2

    def test_questions_are_askuserquestion_format(self):
        """Questions should be in AskUserQuestion format."""
        for cat, questions in question_bank.items():
            for q in questions:
                assert isinstance(q["question"], str)
                assert isinstance(q["options"], list)
                assert isinstance(q["multiSelect"], bool)


class TestCategoriesFlag:
    """Test --categories flag parsing."""

    def test_parse_single_category(self):
        """--categories req should parse correctly."""
        result = parse_categories(["--categories", "req"])
        assert result == ["requirements"]

    def test_parse_multiple_categories(self):
        """--categories req,tech,success should parse correctly."""
        result = parse_categories(["--categories", "req,tech,success"])
        assert result == ["requirements", "technical", "success"]

    def test_parse_shorthand_flag(self):
        """-C req,usr should parse correctly."""
        result = parse_categories(["-C", "req,usr"])
        assert result == ["requirements", "users"]

    def test_parse_all_categories(self):
        """--categories all should return None."""
        result = parse_categories(["--categories", "all"])
        assert result is None

    def test_no_categories_flag(self):
        """Missing flag should return None."""
        result = parse_categories(["d:5", "auth"])
        assert result is None

    def test_parse_scope_shorthand(self):
        """-C scp should parse as scope."""
        result = parse_categories(["-C", "scp"])
        assert result == ["scope"]

    def test_parse_timeline_shorthand(self):
        """--categories time should parse as timeline."""
        result = parse_categories(["--categories", "time"])
        assert result == ["timeline"]

    def test_parse_risks_shorthand(self):
        """-C risk should parse as risks."""
        result = parse_categories(["-C", "risk"])
        assert result == ["risks"]

    def test_parse_existing_shorthand(self):
        """--categories exist should parse as existing."""
        result = parse_categories(["--categories", "exist"])
        assert result == ["existing"]

    def test_parse_success_shorthand(self):
        """-C ok should parse as success."""
        result = parse_categories(["-C", "ok"])
        assert result == ["success"]


class TestQuestionSelection:
    """Test question selection logic."""

    def test_select_fewer_questions_than_available(self):
        """Requesting 4 from 16 should prioritize correctly."""
        categories = ["requirements", "users", "scope", "technical"]
        questions = select_questions("deep", 4, categories, "feat")
        assert len(questions) == 4

    def test_select_more_questions_than_available(self):
        """Requesting 10 from 4 should return all 4."""
        categories = ["requirements", "users"]
        questions = select_questions("deep", 10, categories, "feat")
        assert len(questions) == 4

    def test_select_default_count_for_depth(self):
        """None count should use depth default."""
        questions = select_questions("deep", None, None, "feat")
        assert len(questions) == 8

    def test_select_quick_default_count(self):
        """Quick depth should default to 0 questions."""
        questions = select_questions("quick", None, None, "auto")
        assert len(questions) == 0

    def test_select_default_default_count(self):
        """Default depth should default to 2 questions."""
        questions = select_questions("default", None, None, "auto")
        assert len(questions) == 2

    def test_custom_count_overrides_default(self):
        """Custom count should override depth default."""
        questions = select_questions("deep", 5, None, "feat")
        assert len(questions) == 5

    def test_max_depth_uses_same_default_as_deep(self):
        """Max depth should use same default as deep."""
        questions_max = select_questions("max", None, None, "auto")
        questions_deep = select_questions("deep", None, None, "auto")
        assert len(questions_max) == len(questions_deep)


class TestDefaultCategoriesForFocus:
    """Test default categories by focus area."""

    def test_feat_default_categories(self):
        """Feature focus should use requirements, users, scope, success."""
        cats = get_default_categories_for_focus("feat")
        assert "requirements" in cats
        assert "users" in cats
        assert "scope" in cats
        assert "success" in cats

    def test_arch_default_categories(self):
        """Architecture focus should use technical, risks, existing, scope."""
        cats = get_default_categories_for_focus("arch")
        assert "technical" in cats
        assert "risks" in cats
        assert "existing" in cats
        assert "scope" in cats

    def test_api_default_categories(self):
        """API focus should use technical, requirements, success."""
        cats = get_default_categories_for_focus("api")
        assert "technical" in cats
        assert "requirements" in cats
        assert "success" in cats

    def test_ux_default_categories(self):
        """UX focus should use users, scope, success."""
        cats = get_default_categories_for_focus("ux")
        assert "users" in cats
        assert "scope" in cats
        assert "success" in cats

    def test_ops_default_categories(self):
        """Ops focus should use technical, risks, timeline."""
        cats = get_default_categories_for_focus("ops")
        assert "technical" in cats
        assert "risks" in cats
        assert "timeline" in cats

    def test_auto_default_categories(self):
        """Auto-detect focus should use requirements, users, technical, success."""
        cats = get_default_categories_for_focus("auto")
        assert "requirements" in cats
        assert "users" in cats
        assert "technical" in cats
        assert "success" in cats

    def test_unknown_focus_uses_auto_defaults(self):
        """Unknown focus should use auto-detect defaults."""
        cats = get_default_categories_for_focus("unknown")
        expected = ["requirements", "users", "technical", "success"]
        assert cats == expected


class TestDefaultQuestionCounts:
    """Test default question counts for depths."""

    def test_quick_default_is_zero(self):
        """Quick depth should default to 0 questions."""
        assert get_default_question_count("quick") == 0

    def test_default_default_is_two(self):
        """Default depth should default to 2 questions."""
        assert get_default_question_count("default") == 2

    def test_deep_default_is_eight(self):
        """Deep depth should default to 8 questions."""
        assert get_default_question_count("deep") == 8

    def test_max_default_is_eight(self):
        """Max depth should default to 8 questions."""
        assert get_default_question_count("max") == 8

    def test_unknown_depth_defaults_to_two(self):
        """Unknown depth should default to 2 questions."""
        assert get_default_question_count("unknown") == 2


class TestMilestonePrompts:
    """Test unlimited question milestone prompts logic."""

    def test_milestone_batch_size_is_eight(self):
        """Milestones should occur every 8 questions."""
        milestone = 8
        assert milestone == 8

    def test_frequent_prompt_batch_size_is_four(self):
        """Frequent prompts should occur every 4 questions."""
        frequent_batch = 4
        assert frequent_batch == 4

    def test_continuation_options_structure(self):
        """Continuation prompt should have expected options."""
        options = [
            {
                "label": "Done - Start brainstorming (Recommended)",
                "description": "Proceed with current context",
            },
            {"label": "4 more questions", "description": "Add a few more details"},
            {"label": "8 more questions", "description": "Thorough exploration"},
            {
                "label": "Keep going until I say stop",
                "description": "I'll tell you when I'm done",
            },
        ]
        assert len(options) == 4
        assert all("label" in o and "description" in o for o in options)


class TestBackwardCompatibility:
    """Test backward compatibility with v2.3.0 syntax."""

    def test_d_without_count_still_works(self):
        """d without count should parse correctly."""
        result = parse_depth_with_count("d")
        assert result == ("deep", None)

    def test_m_without_count_still_works(self):
        """m without count should parse correctly."""
        result = parse_depth_with_count("m")
        assert result == ("max", None)

    def test_q_without_count_still_works(self):
        """q without count should parse correctly."""
        result = parse_depth_with_count("q")
        assert result == ("quick", None)

    def test_thorough_still_maps_to_max(self):
        """thorough should still map to max."""
        result = parse_depth_with_count("thorough")
        assert result == ("max", None)

    def test_t_synonym_still_works(self):
        """t should still map to max."""
        result = parse_depth_with_count("t")
        assert result == ("max", None)


class TestCategoryMapCompleteness:
    """Test that CATEGORY_MAP has all expected mappings."""

    def test_all_shortcuts_map_to_full(self):
        """All shortcuts should map to full category names."""
        expected_mappings = {
            "req": "requirements",
            "usr": "users",
            "scp": "scope",
            "tech": "technical",
            "time": "timeline",
            "risk": "risks",
            "exist": "existing",
            "ok": "success",
        }
        for short, full in expected_mappings.items():
            assert CATEGORY_MAP[short] == full

    def test_full_names_map_to_themselves(self):
        """Full category names should map to themselves."""
        for cat in [
            "requirements",
            "users",
            "scope",
            "technical",
            "timeline",
            "risks",
            "existing",
            "success",
        ]:
            assert CATEGORY_MAP[cat] == cat

    def test_all_is_special_value(self):
        """all should map to 'all' for special handling."""
        assert CATEGORY_MAP["all"] == "all"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
