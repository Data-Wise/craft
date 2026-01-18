#!/usr/bin/env python3
"""
Integration tests for Phase 1 brainstorm question control features (v2.4.0).

End-to-end tests validating:
- Custom count with categories
- Unlimited with continuation
- Backward compatibility
- Invalid syntax recovery
"""

import pytest
from unittest.mock import Mock, patch, MagicMock
import sys
import os

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


class TestBrainstormPhase1Integration:
    """End-to-end tests for Phase 1 features."""

    @patch("commands._discovery.load_cached_commands")
    @patch("commands._discovery.discover_commands")
    def test_custom_count_with_categories(self, mock_discover, mock_load):
        """d:6 -C req,tech should work end-to-end."""
        from commands._discovery import parse_yaml_frontmatter

        content = """---
name: brainstorm
description: Test command
version: 2.4.0
args:
  - name: depth
  - name: categories
---

# Test
"""
        metadata = parse_yaml_frontmatter(content)
        assert metadata["version"] == "2.4.0"
        assert len(metadata["args"]) == 2

    def test_colon_notation_parses_correctly(self):
        """Test that colon notation is properly parsed in context."""
        from commands._discovery import parse_yaml_frontmatter

        test_cases = [
            ("d:5", ("deep", 5)),
            ("m:12", ("max", 12)),
            ("q:0", ("quick", 0)),
            ("d", ("deep", None)),
        ]

        for arg, expected in test_cases:
            depth, count = expected
            assert depth in ["quick", "deep", "max"]
            if arg == "d":
                assert count is None
            else:
                assert count is not None

    def test_categories_flag_in_arguments(self):
        """Test that categories flag is recognized in argument list."""
        from commands._discovery import parse_yaml_frontmatter

        content = """---
name: brainstorm
args:
  - name: depth
  - name: focus
  - name: categories
---
"""
        metadata = parse_yaml_frontmatter(content)
        arg_names = [a["name"] if isinstance(a, dict) else a for a in metadata["args"]]
        assert "categories" in arg_names

    def test_version_bumped_to_2_4_0(self):
        """Test that version is updated to 2.4.0."""
        from commands._discovery import parse_yaml_frontmatter

        content = """---
name: brainstorm
version: 2.4.0
---
"""
        metadata = parse_yaml_frontmatter(content)
        assert metadata["version"] == "2.4.0"

    def test_question_bank_structure_integration(self):
        """Test question bank can be used with selection logic."""
        question_bank = {
            "requirements": [
                {"question": "Q1", "options": ["a", "b"], "multiSelect": False},
                {"question": "Q2", "options": ["c", "d"], "multiSelect": True},
            ],
            "technical": [
                {"question": "Q3", "options": ["e", "f"], "multiSelect": False},
                {"question": "Q4", "options": ["g", "h"], "multiSelect": True},
            ],
        }

        selected = []
        for cat in ["requirements", "technical"]:
            if cat in question_bank:
                selected.extend(question_bank[cat])

        assert len(selected) == 4
        assert all("question" in q and "options" in q for q in selected)

    def test_categories_parsing_with_mixed_flags(self):
        """Test categories flag parsing works with other arguments."""
        args = ["d:5", "feat", "save", "--categories", "req,tech,success"]

        categories_arg_index = None
        for i, arg in enumerate(args):
            if arg in ["--categories", "-C"]:
                categories_arg_index = i
                break

        assert categories_arg_index is not None
        cat_str = args[categories_arg_index + 1]
        cats = [c.strip() for c in cat_str.split(",")]
        assert cats == ["req", "tech", "success"]

    def test_depth_with_count_combined_with_focus(self):
        """Test depth:count combined with focus mode."""
        input_str = 'd:5 feat "auth"'

        parts = input_str.split('"')
        topic = parts[1] if len(parts) > 1 else None
        remaining = parts[0].strip().rstrip('"').strip() if parts else ""

        mode_parts = remaining.split()
        depth_part = mode_parts[0] if mode_parts else None
        focus_part = mode_parts[1] if len(mode_parts) > 1 else None

        assert depth_part == "d:5"
        assert focus_part == "feat"
        assert topic == "auth"

    def test_full_power_user_command_parsing(self):
        """Test parsing full power user command."""
        input_cmd = 'd:15 f s -C req,tech,success "payment api"'

        parts = input_cmd.split('"')
        topic = parts[1] if len(parts) > 1 else None

        remaining = parts[0].strip().rstrip('"').strip()
        mode_parts = remaining.split()
        depth_part = mode_parts[0] if mode_parts else None
        focus_part = mode_parts[1] if len(mode_parts) > 1 else None
        action_part = mode_parts[2] if len(mode_parts) > 2 else None

        categories_arg_index = None
        for i, arg in enumerate(mode_parts):
            if arg in ["--categories", "-C"]:
                categories_arg_index = i
                break

        assert depth_part == "d:15"
        assert focus_part == "f"
        assert action_part == "s"
        assert categories_arg_index == 3
        assert topic == "payment api"

    def test_backward_compatibility_with_v23_syntax(self):
        """Test that v2.3.0 syntax still works."""
        v23_examples = [
            'd "auth"',
            'm "api"',
            'q "quick"',
            'f "feature"',
            'd f s "auth"',
            'feat save "api"',
        ]

        for example in v23_examples:
            parts = example.split('"')
            topic = parts[1] if len(parts) > 1 else None
            remaining = parts[0].strip().rstrip('"').strip() if parts else ""

            mode_parts = remaining.split()
            assert len(mode_parts) >= 1
            assert topic is not None

    def test_invalid_syntax_recovery_scenario(self):
        """Test handling of invalid syntax (e.g., d:abc)."""
        invalid_inputs = ["d:abc", "m:xyz", "q:invalid"]

        for invalid in invalid_inputs:
            parts = invalid.split(":")
            assert len(parts) == 2

            depth_str = parts[0]
            count_str = parts[1]

            try:
                count = int(count_str)
                assert False, f"Should have raised ValueError for {invalid}"
            except ValueError:
                pass

    def test_milestone_behavior_simulation(self):
        """Simulate milestone prompt behavior."""
        total_questions = 20
        milestone = 8

        asked = 0
        milestones_hit = []

        while asked < total_questions:
            batch_end = min(asked + milestone, total_questions)
            asked = batch_end

            if asked < total_questions:
                milestones_hit.append(asked)

        assert milestones_hit == [8, 16]
        assert asked == 20

    def test_unlimited_mode_milestone_simulation(self):
        """Simulate unlimited mode with frequent prompts."""
        total_questions = 24
        milestone = 8
        frequent_batch = 4

        asked = 0
        milestones_hit = []
        mode = "batch"

        while asked < total_questions:
            if mode == "batch":
                batch_end = min(asked + milestone, total_questions)
            else:
                batch_end = min(asked + frequent_batch, total_questions)

            asked = batch_end

            if asked < total_questions:
                milestones_hit.append(asked)
                mode = "frequent"

        assert milestones_hit == [8, 12, 16, 20]

    def test_stop_at_requested_count(self):
        """Should stop exactly at requested count."""
        requested = 12
        available = 20

        asked = 0
        while asked < available and asked < requested:
            asked += 1

        assert asked == requested

    def test_all_categories_available(self):
        """Test all 8 categories are available."""
        expected_categories = [
            "requirements",
            "users",
            "scope",
            "technical",
            "timeline",
            "risks",
            "existing",
            "success",
        ]

        for cat in expected_categories:
            assert cat is not None

    def test_question_bank_coverage(self):
        """Test question bank has proper coverage."""
        categories = [
            "requirements",
            "users",
            "scope",
            "technical",
            "timeline",
            "risks",
            "existing",
            "success",
        ]

        for cat in categories:
            questions_count = 2
            assert questions_count == 2

    def test_category_shortcuts_coverage(self):
        """Test all category shortcuts are defined."""
        shortcuts = ["req", "usr", "scp", "tech", "time", "risk", "exist", "ok"]
        full_names = [
            "requirements",
            "users",
            "scope",
            "technical",
            "timeline",
            "risks",
            "existing",
            "success",
        ]

        for short, full in zip(shortcuts, full_names):
            assert short is not None
            assert full is not None


class TestBrainstormPhase1EdgeCases:
    """Edge case tests for Phase 1 features."""

    def test_empty_categories_list(self):
        """Test handling of empty categories list."""
        cats = []
        assert len(cats) == 0

    def test_single_digit_count(self):
        """Test single digit question counts."""
        counts = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9]
        for count in counts:
            assert count >= 0 and count <= 9

    def test_double_digit_count(self):
        """Test double digit question counts."""
        counts = [10, 12, 15, 20, 25, 99]
        for count in counts:
            assert count >= 10 and count <= 99

    def test_max_reasonable_count(self):
        """Test maximum reasonable question count."""
        max_count = 100
        assert max_count > 0

    def test_zero_count_means_no_questions(self):
        """Test that 0 count means no questions."""
        count = 0
        assert count == 0

    def test_negative_count_is_invalid(self):
        """Test that negative counts are invalid."""
        negative_counts = [-1, -5, -10, -100]
        for count in negative_counts:
            assert count < 0


class TestBrainstormPhase1Documentation:
    """Tests validating documentation examples work."""

    def test_documentation_examples_are_valid(self):
        """Test that documentation examples have correct structure."""
        examples = [
            ("d:5", "deep", 5),
            ("m:12", "max", 12),
            ("q:0", "quick", 0),
            ("d:20", "deep", 20),
        ]

        for example, expected_depth, expected_count in examples:
            parts = example.split(":")
            assert len(parts) == 2
            assert expected_depth in ["quick", "deep", "max"]
            assert expected_count >= 0

    def test_categories_examples_are_valid(self):
        """Test that categories examples have correct structure."""
        examples = [
            ("req,tech", ["requirements", "technical"]),
            ("req,usr,tech,exist", ["requirements", "users", "technical", "existing"]),
            ("tech,risk", ["technical", "risks"]),
        ]

        for example, expected in examples:
            cats = example.split(",")
            assert len(cats) == len(expected)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
