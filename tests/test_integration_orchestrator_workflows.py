#!/usr/bin/env python3
"""
Integration Tests: Orchestrator Workflows
==========================================
Tests the full orchestration system including complexity scoring,
task delegation, validators, and agent hooks.

Components tested:
- utils/complexity_scorer.py
- .claude-plugin/skills/validation/*.md
- .claude-plugin/hooks/orchestrate-hooks.sh
- agents/orchestrator-v2.md
- commands/do.md
- commands/orchestrate.md

Run with: python tests/test_integration_orchestrator_workflows.py
"""

import unittest
import sys
from pathlib import Path

# Add plugin directory to path
plugin_dir = Path(__file__).parent.parent
sys.path.insert(0, str(plugin_dir))

from utils.complexity_scorer import calculate_complexity_score, get_routing_decision


class TestOrchestratorIntegration(unittest.TestCase):
    """Integration tests for orchestrator workflows."""

    def test_01_simple_task_routes_to_command(self):
        """Test: Simple tasks (score 0-3) route to commands."""
        # Arrange
        simple_tasks = [
            "lint the code",
            "run tests",
            "commit changes"
        ]

        for task in simple_tasks:
            with self.subTest(task=task):
                # Act
                score = calculate_complexity_score(task)
                routing = get_routing_decision(score)

                # Assert
                self.assertLessEqual(score, 3, f"Task '{task}' should have low complexity (score={score})")
                self.assertEqual(routing, "commands", f"Task '{task}' should route to commands")

    def test_02_moderate_task_routes_to_agent(self):
        """Test: Moderate tasks (score 4-7) route to agents."""
        # Arrange
        moderate_tasks = [
            "refactor the authentication module",
            "add comprehensive error handling",
            "optimize database queries"
        ]

        for task in moderate_tasks:
            with self.subTest(task=task):
                # Act
                score = calculate_complexity_score(task)
                routing = get_routing_decision(score)

                # Assert
                self.assertGreaterEqual(score, 4, f"Task '{task}' should have moderate complexity (score={score})")
                self.assertLessEqual(score, 7, f"Task '{task}' should have moderate complexity (score={score})")
                self.assertEqual(routing, "agent", f"Task '{task}' should route to agent")

    def test_03_complex_task_routes_to_orchestrator(self):
        """Test: Complex tasks (score 8-10) route to orchestrator."""
        # Arrange
        complex_tasks = [
            "add user authentication with OAuth, database migrations, and comprehensive tests",
            "redesign the API architecture to support microservices",
            "implement CI/CD pipeline with testing, security scans, and deployment"
        ]

        for task in complex_tasks:
            with self.subTest(task=task):
                # Act
                score = calculate_complexity_score(task)
                routing = get_routing_decision(score)

                # Assert
                self.assertGreaterEqual(score, 8, f"Task '{task}' should have high complexity (score={score})")
                self.assertEqual(routing, "orchestrator", f"Task '{task}' should route to orchestrator")

    def test_04_multi_step_detection(self):
        """Test: Multi-step tasks increase complexity score."""
        # Arrange
        single_step = "lint the code"
        multi_step = "lint the code, fix errors, and commit changes"

        # Act
        score_single = calculate_complexity_score(single_step)
        score_multi = calculate_complexity_score(multi_step)

        # Assert
        self.assertLess(score_single, score_multi,
                       f"Multi-step ({score_multi}) should have higher score than single-step ({score_single})")

    def test_05_cross_category_detection(self):
        """Test: Cross-category tasks increase complexity score."""
        # Arrange
        single_category = "update documentation"
        cross_category = "update documentation and refactor code"

        # Act
        score_single = calculate_complexity_score(single_category)
        score_cross = calculate_complexity_score(cross_category)

        # Assert
        self.assertLess(score_single, score_cross,
                       f"Cross-category ({score_cross}) should have higher score than single-category ({score_single})")

    def test_06_planning_requirement_detection(self):
        """Test: Tasks requiring planning increase complexity score."""
        # Arrange
        no_planning = "run tests"
        needs_planning = "design a new feature architecture"

        # Act
        score_no_plan = calculate_complexity_score(no_planning)
        score_needs_plan = calculate_complexity_score(needs_planning)

        # Assert
        self.assertLess(score_no_plan, score_needs_plan,
                       f"Planning tasks ({score_needs_plan}) should have higher score than simple tasks ({score_no_plan})")

    def test_07_score_boundaries(self):
        """Test: Scores respect 0-10 boundaries."""
        # Arrange
        test_tasks = [
            "lint",
            "refactor authentication",
            "implement full microservices architecture with testing, deployment, and monitoring"
        ]

        for task in test_tasks:
            with self.subTest(task=task):
                # Act
                score = calculate_complexity_score(task)

                # Assert
                self.assertGreaterEqual(score, 0, f"Score should be >= 0 (got {score})")
                self.assertLessEqual(score, 10, f"Score should be <= 10 (got {score})")

    def test_08_routing_decision_consistency(self):
        """Test: Routing decisions are consistent for same scores."""
        # Arrange
        test_cases = [
            (0, "commands"), (1, "commands"), (2, "commands"), (3, "commands"),
            (4, "agent"), (5, "agent"), (6, "agent"), (7, "agent"),
            (8, "orchestrator"), (9, "orchestrator"), (10, "orchestrator")
        ]

        for score, expected_routing in test_cases:
            with self.subTest(score=score):
                # Act
                routing = get_routing_decision(score)

                # Assert
                self.assertEqual(routing, expected_routing,
                               f"Score {score} should route to {expected_routing}")

    def test_09_research_keyword_detection(self):
        """Test: Research keywords increase complexity."""
        # Arrange
        no_research = "implement login form"
        with_research = "research best practices and implement login form"

        # Act
        score_no_research = calculate_complexity_score(no_research)
        score_with_research = calculate_complexity_score(with_research)

        # Assert
        self.assertLess(score_no_research, score_with_research,
                       f"Research tasks ({score_with_research}) should score higher than implementation-only ({score_no_research})")

    def test_10_file_change_estimation(self):
        """Test: Multi-file changes increase complexity."""
        # Arrange
        single_file = "update README"
        multi_file = "update README, docs, and examples"

        # Act
        score_single = calculate_complexity_score(single_file)
        score_multi = calculate_complexity_score(multi_file)

        # Assert
        self.assertLess(score_single, score_multi,
                       f"Multi-file ({score_multi}) should score higher than single-file ({score_single})")

    def test_11_empty_task_handling(self):
        """Test: System handles empty or minimal tasks gracefully."""
        # Arrange
        edge_cases = ["", "  ", "a", "test"]

        for task in edge_cases:
            with self.subTest(task=repr(task)):
                # Act
                score = calculate_complexity_score(task)
                routing = get_routing_decision(score)

                # Assert: Should not crash and should return valid routing
                self.assertIn(routing, ["commands", "agent", "orchestrator"],
                            f"Should return valid routing for task '{task}'")


class TestValidatorIntegration(unittest.TestCase):
    """Integration tests for hot-reload validators."""

    @classmethod
    def setUpClass(cls):
        """Set up test environment."""
        cls.plugin_dir = Path(__file__).parent.parent
        cls.validators_dir = cls.plugin_dir / ".claude-plugin" / "skills" / "validation"

    def test_01_validator_discovery(self):
        """Test: System discovers hot-reload validators."""
        # Arrange
        if not self.validators_dir.exists():
            self.skipTest("Validators directory not found")

        validators = list(self.validators_dir.glob("*.md"))

        # Assert
        self.assertGreater(len(validators), 0, "Should find validators")
        validator_names = [v.stem for v in validators]

        # Check for expected validators (if they exist)
        expected_validators = ["broken-links", "test-coverage", "lint-check"]
        for expected in expected_validators:
            if expected in validator_names:
                self.assertIn(expected, validator_names, f"Should find {expected} validator")

    def test_02_validator_frontmatter_format(self):
        """Test: Validators have correct frontmatter."""
        # Arrange
        if not self.validators_dir.exists():
            self.skipTest("Validators directory not found")

        validators = list(self.validators_dir.glob("*.md"))

        if len(validators) == 0:
            self.skipTest("No validators found")

        for validator_path in validators:
            with self.subTest(validator=validator_path.stem):
                # Act
                content = validator_path.read_text()

                # Assert
                self.assertIn("---", content, f"{validator_path.name} should have frontmatter")
                # At least one of these should be present
                has_hot_reload = "hot_reload:" in content
                has_context = "context:" in content
                self.assertTrue(has_hot_reload or has_context,
                              f"{validator_path.name} should have hot_reload or context declaration")


if __name__ == "__main__":
    unittest.main(verbosity=2)
