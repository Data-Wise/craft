#!/usr/bin/env python3
"""
Mermaid Validation Unit Tests
===============================
Tests for regex detection, auto-fix, health score, and block extraction.

Run with: python3 -m pytest tests/test_mermaid_validation.py -v
"""

import sys
from pathlib import Path

import pytest

# Add scripts directory to path
sys.path.insert(0, str(Path(__file__).parent.parent / "scripts"))

# Import from mermaid-validate.py (hyphen in name requires importlib)
import importlib.util
SCRIPTS_DIR = Path(__file__).parent.parent / "scripts"

def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

validate_mod = _load_module("mermaid_validate", "mermaid-validate.py")
autofix_mod = _load_module("mermaid_autofix", "mermaid-autofix.py")

MermaidBlock = validate_mod.MermaidBlock
extract_mermaid_blocks = validate_mod.extract_mermaid_blocks
check_leading_slash = validate_mod.check_leading_slash
check_lowercase_end = validate_mod.check_lowercase_end
check_unquoted_colons = validate_mod.check_unquoted_colons
check_br_tags = validate_mod.check_br_tags
check_deprecated_graph = validate_mod.check_deprecated_graph
validate_blocks = validate_mod.validate_blocks
calculate_health_score = validate_mod.calculate_health_score

fix_leading_slash = autofix_mod.fix_leading_slash
fix_lowercase_end = autofix_mod.fix_lowercase_end
fix_unquoted_colons = autofix_mod.fix_unquoted_colons
fix_br_tags = autofix_mod.fix_br_tags
fix_deprecated_graph = autofix_mod.fix_deprecated_graph

pytestmark = [pytest.mark.unit]

PLUGIN_DIR = Path(__file__).parent.parent


# ─── Regex Detection Tests ───────────────────────────────────────────────────


class TestRegexDetection:
    """Tests for regex pre-check rules."""

    def test_regex_detects_leading_slash(self):
        """[/text] detected in mermaid blocks."""
        block = MermaidBlock(file="test.md", line_number=1, content='A[/broken] --> B')
        issues = check_leading_slash(block)
        assert len(issues) == 1
        assert issues[0].rule == "leading-slash"
        assert issues[0].severity == "error"

    def test_regex_detects_lowercase_end(self):
        """Lowercase 'end' in node labels detected."""
        block = MermaidBlock(file="test.md", line_number=1, content='A --> B[end]')
        issues = check_lowercase_end(block)
        assert len(issues) == 1
        assert issues[0].rule == "lowercase-end"
        assert issues[0].severity == "error"

    def test_regex_detects_unquoted_special_chars(self):
        """Colons without quotes detected."""
        block = MermaidBlock(file="test.md", line_number=1, content='A[Status: OK] --> B')
        issues = check_unquoted_colons(block)
        assert len(issues) == 1
        assert issues[0].rule == "unquoted-colon"
        assert issues[0].severity == "warning"

    def test_regex_detects_br_tags(self):
        """<br/> in mermaid blocks detected."""
        block = MermaidBlock(file="test.md", line_number=1, content='A[First<br/>Second] --> B')
        issues = check_br_tags(block)
        assert len(issues) == 1
        assert issues[0].rule == "br-tag"
        assert issues[0].severity == "warning"

    def test_regex_detects_deprecated_graph(self):
        """graph TB flagged, flowchart TD passes."""
        block_bad = MermaidBlock(file="test.md", line_number=1, content='graph TB\n  A --> B')
        block_good = MermaidBlock(file="test.md", line_number=1, content='flowchart TD\n  A --> B')
        issues_bad = check_deprecated_graph(block_bad)
        issues_good = check_deprecated_graph(block_good)
        assert len(issues_bad) == 1
        assert issues_bad[0].rule == "deprecated-graph"
        assert issues_bad[0].severity == "warning"
        assert len(issues_good) == 0


# ─── Auto-Fix Tests ─────────────────────────────────────────────────────────


class TestAutoFix:
    """Tests for auto-fix rules."""

    def test_autofix_quotes_slash_labels(self):
        """[/text] -> ["/text"]"""
        fixed, changes = fix_leading_slash('A[/text] --> B')
        assert fixed == 'A["/text"] --> B'
        assert len(changes) == 1

    def test_autofix_capitalizes_end(self):
        """[end] -> [End]"""
        fixed, changes = fix_lowercase_end('A --> B[end]')
        assert fixed == 'A --> B[End]'
        assert len(changes) == 1

    def test_autofix_quotes_special_chars(self):
        """[a:b] -> ["a:b"]"""
        fixed, changes = fix_unquoted_colons('A[Status: OK] --> B')
        assert fixed == 'A["Status: OK"] --> B'
        assert len(changes) == 1

    def test_autofix_replaces_br_tags(self):
        """<br/> labels get quoted."""
        fixed, changes = fix_br_tags('A[First<br/>Second] --> B')
        assert '["First<br/>Second"]' in fixed
        assert len(changes) == 1

    def test_autofix_graph_to_flowchart(self):
        """graph TB -> flowchart TB"""
        fixed, changes = fix_deprecated_graph('graph TB\n  A --> B')
        assert fixed == 'flowchart TB\n  A --> B'
        assert len(changes) == 1

    def test_autofix_preserves_valid_diagrams(self):
        """Clean diagrams should be unchanged."""
        valid = 'flowchart TD\n  A["Hello"] --> B["World"]'
        f1, c1 = fix_leading_slash(valid)
        f2, c2 = fix_lowercase_end(f1)
        f3, c3 = fix_unquoted_colons(f2)
        f4, c4 = fix_br_tags(f3)
        f5, c5 = fix_deprecated_graph(f4)
        assert f5 == valid
        assert sum(len(c) for c in [c1, c2, c3, c4, c5]) == 0


# ─── Health Score Tests ──────────────────────────────────────────────────────


class TestHealthScore:
    """Tests for health score calculation."""

    def test_health_score_calculation(self):
        """Score = 0.5*validity + 0.3*practices + 0.2*rendering."""
        blocks = [MermaidBlock(file="a.md", line_number=i, content=f"flowchart TD\n  A{i} --> B{i}") for i in range(10)]
        # No issues = perfect score
        health = calculate_health_score(blocks, [])
        assert health["score"] == 100.0
        assert health["syntax"] == 100.0
        assert health["practices"] == 100.0

    def test_health_score_thresholds(self):
        """>= 80 pass, < 80 fail gate."""
        # Mix of clean blocks and blocks with warnings — 2/10 have deprecated graph
        blocks = [MermaidBlock(file="a.md", line_number=i, content=f"flowchart TD\n  A{i} --> B{i}") for i in range(8)]
        blocks += [MermaidBlock(file="a.md", line_number=i+8, content=f"graph TD\n  C{i} --> D{i}") for i in range(2)]
        issues = validate_blocks(blocks)
        health = calculate_health_score(blocks, issues)
        # Only 2/10 blocks have deprecated-graph warning, no errors
        assert health["syntax"] == 100.0  # No errors
        assert health["practices"] < 100.0  # Has warnings
        assert health["score"] >= 80  # Should still pass gate


# ─── Block Extraction Tests ──────────────────────────────────────────────────


class TestBlockExtraction:
    """Tests for mermaid block extraction from markdown."""

    def test_block_extraction_from_markdown(self, tmp_path):
        """Correctly extracts mermaid fenced blocks."""
        md = tmp_path / "test.md"
        md.write_text("# Title\n\n```mermaid\nflowchart TD\n  A --> B\n```\n\nSome text.\n")
        blocks = extract_mermaid_blocks(str(md))
        assert len(blocks) == 1
        assert "flowchart TD" in blocks[0].content
        assert blocks[0].line_number == 3  # Line of ```mermaid

    def test_block_extraction_ignores_non_mermaid(self, tmp_path):
        """Doesn't match python or bash blocks."""
        md = tmp_path / "test.md"
        md.write_text("```python\nprint('hi')\n```\n\n```bash\necho hi\n```\n\n```mermaid\nflowchart TD\n  A --> B\n```\n")
        blocks = extract_mermaid_blocks(str(md))
        assert len(blocks) == 1
        assert "flowchart" in blocks[0].content
