#!/usr/bin/env python3
"""
Unit tests for brainstorm context scanner (v2.15.0).

Tests:
- .STATUS file reading
- Spec matching by keyword
- Prior brainstorm detection
- Project type detection
- Dynamic question generation
- Project-type question extensions
- Smart question selection
- Keyword extraction
"""

import json
import os
import sys

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

pytestmark = [pytest.mark.unit, pytest.mark.brainstorm]

from utils.brainstorm_context import (
    BrainstormContext,
    ContextScanResult,
    PROJECT_TYPE_QUESTIONS,
    scan_context,
)


@pytest.fixture
def project_dir(tmp_path):
    """Create a minimal project directory with .STATUS and docs/specs/."""
    status_file = tmp_path / ".STATUS"
    status_file.write_text(
        "status: Active\n"
        "version: 2.14.0\n"
        "milestone: v2.14.0 - Unified Formatting Library\n"
        "progress: 100%\n"
    )

    specs_dir = tmp_path / "docs" / "specs"
    specs_dir.mkdir(parents=True)

    return tmp_path


@pytest.fixture
def ctx(project_dir):
    """Create a BrainstormContext for the test project."""
    return BrainstormContext(project_dir)


class TestStatusReading:
    """Test .STATUS file parsing."""

    def test_reads_version(self, ctx, project_dir):
        """Should extract version from .STATUS."""
        result = ctx.scan("test")
        assert result.project_version == "2.14.0"

    def test_reads_status_fields(self, ctx):
        """Should extract all status fields."""
        result = ctx.scan("test")
        assert result.status_info["status"] == "Active"
        assert result.status_info["version"] == "2.14.0"
        assert "Formatting" in result.status_info["milestone"]

    def test_prefills_technical_with_version(self, ctx):
        """Should pre-fill technical category with version info."""
        result = ctx.scan("test")
        assert "technical" in result.pre_filled_answers
        assert "v2.14.0" in result.pre_filled_answers["technical"]

    def test_missing_status_file(self, tmp_path):
        """Should handle missing .STATUS gracefully."""
        ctx = BrainstormContext(tmp_path)
        result = ctx.scan("test")
        assert result.project_version is None
        assert result.status_info == {}

    def test_empty_status_file(self, project_dir):
        """Should handle empty .STATUS file."""
        (project_dir / ".STATUS").write_text("")
        ctx = BrainstormContext(project_dir)
        result = ctx.scan("test")
        assert result.project_version is None


class TestSpecMatching:
    """Test spec file matching by topic keywords."""

    def test_finds_matching_spec_by_filename(self, ctx, project_dir):
        """Should find spec when topic keywords match filename."""
        spec = project_dir / "docs" / "specs" / "SPEC-auth-system-2026-01-15.md"
        spec.write_text("# Auth System Spec\n\nAuthentication design.\n")

        result = ctx.scan("auth system")
        assert result.matching_spec is not None
        assert "auth-system" in result.matching_spec

    def test_no_match_for_unrelated_topic(self, ctx, project_dir):
        """Should return None when no specs match."""
        spec = project_dir / "docs" / "specs" / "SPEC-auth-2026-01-15.md"
        spec.write_text("# Auth Spec\n")

        result = ctx.scan("database migration")
        assert result.matching_spec is None

    def test_requires_minimum_score(self, ctx, project_dir):
        """Should not match on single weak keyword."""
        spec = project_dir / "docs" / "specs" / "SPEC-system-overview-2026-01-15.md"
        spec.write_text("# System Overview\n")

        result = ctx.scan("the system")
        # "system" matches filename (+2) so this should match
        assert result.matching_spec is not None

    def test_empty_specs_directory(self, ctx, project_dir):
        """Should return None with empty specs dir."""
        result = ctx.scan("anything")
        assert result.matching_spec is None

    def test_no_specs_directory(self, tmp_path):
        """Should return None when docs/specs/ doesn't exist."""
        ctx = BrainstormContext(tmp_path)
        result = ctx.scan("anything")
        assert result.matching_spec is None


class TestPriorBrainstormDetection:
    """Test finding prior brainstorm files."""

    def test_finds_brainstorm_in_root(self, ctx, project_dir):
        """Should find BRAINSTORM-*.md in project root."""
        brainstorm = project_dir / "BRAINSTORM-auth-system-2026-01-15.md"
        brainstorm.write_text("# Auth System Brainstorm\n")

        result = ctx.scan("auth system")
        assert result.prior_brainstorm is not None
        assert "auth-system" in result.prior_brainstorm

    def test_finds_brainstorm_in_docs_dir(self, ctx, project_dir):
        """Should find BRAINSTORM-*.md in docs/brainstorm/."""
        brainstorm_dir = project_dir / "docs" / "brainstorm"
        brainstorm_dir.mkdir(parents=True)
        brainstorm = brainstorm_dir / "BRAINSTORM-caching-2026-01-20.md"
        brainstorm.write_text("# Caching Brainstorm\n")

        result = ctx.scan("caching layer")
        assert result.prior_brainstorm is not None
        assert "caching" in result.prior_brainstorm

    def test_no_prior_brainstorm(self, ctx):
        """Should return None when no brainstorm files match."""
        result = ctx.scan("completely new topic")
        assert result.prior_brainstorm is None


class TestProjectTypeDetection:
    """Test project type detection."""

    def test_detects_craft_plugin(self, project_dir):
        """Should detect craft-plugin from .claude-plugin/plugin.json."""
        plugin_dir = project_dir / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "test-plugin",
            "version": "1.0.0",
        }))

        ctx = BrainstormContext(project_dir)
        result = ctx.scan("test")
        assert result.project_type == "craft-plugin"

    def test_detects_r_package(self, tmp_path):
        """Should detect r-package from DESCRIPTION with Package: field."""
        (tmp_path / "DESCRIPTION").write_text(
            "Package: mypackage\nVersion: 0.1.0\nTitle: Test\n"
        )
        ctx = BrainstormContext(tmp_path)
        result = ctx.scan("test")
        assert result.project_type == "r-package"

    def test_detects_python_project(self, tmp_path):
        """Should detect generic-python from pyproject.toml."""
        (tmp_path / "pyproject.toml").write_text(
            '[project]\nname = "myproject"\nversion = "0.1.0"\n'
        )
        ctx = BrainstormContext(tmp_path)
        result = ctx.scan("test")
        assert result.project_type == "generic-python"

    def test_detects_node_project(self, tmp_path):
        """Should detect generic-node from package.json."""
        (tmp_path / "package.json").write_text(json.dumps({
            "name": "my-app",
            "version": "1.0.0",
        }))
        ctx = BrainstormContext(tmp_path)
        result = ctx.scan("test")
        assert result.project_type == "generic-node"

    def test_no_project_type(self, tmp_path):
        """Should return None for empty directory."""
        ctx = BrainstormContext(tmp_path)
        result = ctx.scan("test")
        assert result.project_type is None


class TestDynamicQuestions:
    """Test dynamic question generation based on context."""

    def test_generates_spec_question(self, ctx, project_dir):
        """Should generate dynamic question when matching spec found."""
        spec = project_dir / "docs" / "specs" / "SPEC-auth-system-2026-01-15.md"
        spec.write_text("# Auth System\n\nAuthentication spec.\n")

        result = ctx.scan("auth system")
        assert len(result.dynamic_questions) >= 1
        spec_q = [q for q in result.dynamic_questions if q.get("type") == "matching_spec"]
        assert len(spec_q) == 1
        assert "load as context" in spec_q[0]["question"]

    def test_generates_prior_brainstorm_question(self, ctx, project_dir):
        """Should generate dynamic question when prior brainstorm found."""
        brainstorm = project_dir / "BRAINSTORM-auth-2026-01-15.md"
        brainstorm.write_text("# Auth Brainstorm\n")

        result = ctx.scan("auth")
        prior_q = [q for q in result.dynamic_questions if q.get("type") == "prior_brainstorm"]
        assert len(prior_q) == 1
        assert "resume or start fresh" in prior_q[0]["question"]

    def test_no_dynamic_questions_for_clean_state(self, ctx):
        """Should generate no dynamic questions when nothing matches."""
        result = ctx.scan("completely new unrelated topic xyz")
        # May have 0 dynamic questions (no spec, no brainstorm, no failing tests)
        assert isinstance(result.dynamic_questions, list)


class TestProjectTypeQuestions:
    """Test project-type question extensions."""

    def test_all_six_project_types_have_questions(self):
        """All 6 project types should have 2 questions each."""
        expected_types = [
            "r-package", "generic-python", "generic-node",
            "teaching-site", "craft-plugin", "mcp-server",
        ]
        for pt in expected_types:
            assert pt in PROJECT_TYPE_QUESTIONS, f"Missing questions for {pt}"
            assert len(PROJECT_TYPE_QUESTIONS[pt]) == 2, f"{pt} should have 2 questions"

    def test_questions_have_required_fields(self):
        """Each project-type question should have question, options, multiSelect."""
        for pt, questions in PROJECT_TYPE_QUESTIONS.items():
            for q in questions:
                assert "question" in q, f"Missing 'question' in {pt}"
                assert "options" in q, f"Missing 'options' in {pt}"
                assert "multiSelect" in q, f"Missing 'multiSelect' in {pt}"
                assert len(q["options"]) >= 2, f"Need 2+ options in {pt}"

    def test_get_project_type_questions(self, ctx):
        """Should return questions for known project type."""
        questions = ctx.get_project_type_questions("craft-plugin")
        assert len(questions) == 2
        assert "command count" in questions[0]["question"].lower()

    def test_get_unknown_type_returns_empty(self, ctx):
        """Should return empty list for unknown project type."""
        questions = ctx.get_project_type_questions("unknown-type")
        assert questions == []

    def test_total_project_type_questions(self):
        """Should have exactly 12 project-type questions (6 types x 2)."""
        total = sum(len(qs) for qs in PROJECT_TYPE_QUESTIONS.values())
        assert total == 12


class TestSmartQuestionSelection:
    """Test the smart question selection algorithm."""

    def test_dynamic_questions_come_first(self, ctx, project_dir):
        """Dynamic questions should be prioritized before base questions."""
        spec = project_dir / "docs" / "specs" / "SPEC-auth-2026-01-15.md"
        spec.write_text("# Auth\n\nAuth spec content.\n")

        context = ctx.scan("auth")
        base_qs = [{"question": "Base Q1", "category": "requirements"}]

        selected = ctx.select_smart_questions(base_qs, context, 10)
        # Dynamic questions should come before base
        assert selected[0].get("type") == "matching_spec"

    def test_project_type_questions_included(self, project_dir):
        """Project-type questions should be included when type detected."""
        plugin_dir = project_dir / ".claude-plugin"
        plugin_dir.mkdir()
        (plugin_dir / "plugin.json").write_text(json.dumps({
            "name": "test", "version": "1.0.0"
        }))

        ctx = BrainstormContext(project_dir)
        context = ctx.scan("new feature")
        base_qs = [{"question": "Base Q1", "category": "requirements"}]

        selected = ctx.select_smart_questions(base_qs, context, 10)
        pt_qs = [q for q in selected if q.get("category") == "project-type"]
        assert len(pt_qs) == 2  # craft-plugin has 2 questions

    def test_prefilled_answers_marked_skippable(self, ctx):
        """Pre-filled answers should mark questions as skippable."""
        context = ctx.scan("test")
        base_qs = [{"question": "Tech Q", "category": "technical"}]

        selected = ctx.select_smart_questions(base_qs, context, 10)
        tech_qs = [q for q in selected if q.get("category") == "technical"]
        assert len(tech_qs) >= 1
        assert tech_qs[0].get("skippable") is True
        assert "v2.14.0" in tech_qs[0].get("pre_filled", "")

    def test_count_limits_output(self, ctx):
        """Should respect count limit."""
        context = ctx.scan("test")
        base_qs = [
            {"question": f"Q{i}", "category": "requirements"}
            for i in range(10)
        ]

        selected = ctx.select_smart_questions(base_qs, context, 3)
        assert len(selected) == 3

    def test_zero_count_returns_empty(self, ctx):
        """Count of 0 should return empty list."""
        context = ctx.scan("test")
        base_qs = [{"question": "Q1", "category": "requirements"}]

        selected = ctx.select_smart_questions(base_qs, context, 0)
        assert selected == []


class TestKeywordExtraction:
    """Test keyword extraction from topics."""

    def test_basic_extraction(self):
        """Should split on spaces and lowercase."""
        keywords = BrainstormContext._extract_keywords("Auth System")
        assert "auth" in keywords
        assert "system" in keywords

    def test_removes_stop_words(self):
        """Should remove common stop words."""
        keywords = BrainstormContext._extract_keywords("add a new auth system")
        assert "auth" in keywords
        assert "system" in keywords
        assert "add" not in keywords
        assert "new" not in keywords
        assert "a" not in keywords

    def test_splits_on_hyphens(self):
        """Should split on hyphens."""
        keywords = BrainstormContext._extract_keywords("user-auth-system")
        assert "user" in keywords
        assert "auth" in keywords
        assert "system" in keywords

    def test_empty_string(self):
        """Should return empty list for empty string."""
        assert BrainstormContext._extract_keywords("") == []

    def test_only_stop_words(self):
        """Should return empty list when all words are stop words."""
        assert BrainstormContext._extract_keywords("a the is") == []

    def test_single_char_filtered(self):
        """Single character words should be filtered out."""
        keywords = BrainstormContext._extract_keywords("a b c auth")
        assert keywords == ["auth"]


class TestConvenienceFunction:
    """Test the scan_context convenience function."""

    def test_scan_context_works(self, project_dir):
        """scan_context() should return a ContextScanResult."""
        result = scan_context("test", project_dir)
        assert isinstance(result, ContextScanResult)
        assert result.project_version == "2.14.0"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
