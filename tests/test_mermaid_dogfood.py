#!/usr/bin/env python3
"""
Mermaid Dogfood Tests
=======================
Runs mermaid validation tools against the craft repo itself.
Ensures all documentation diagrams are clean and tooling is configured.

Run with: python3 -m pytest tests/test_mermaid_dogfood.py -v
"""

import importlib.util
import subprocess
from pathlib import Path

import pytest
import yaml

pytestmark = [pytest.mark.e2e, pytest.mark.dogfood]

PLUGIN_DIR = Path(__file__).parent.parent
SCRIPTS_DIR = PLUGIN_DIR / "scripts"
DOCS_DIR = PLUGIN_DIR / "docs"
COMMANDS_DIR = PLUGIN_DIR / "commands"
SKILLS_DIR = PLUGIN_DIR / "skills"

def _load_module(name, filename):
    spec = importlib.util.spec_from_file_location(name, SCRIPTS_DIR / filename)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod

validate_mod = _load_module("mermaid_validate", "mermaid-validate.py")
extract_mermaid_blocks = validate_mod.extract_mermaid_blocks
validate_blocks = validate_mod.validate_blocks
calculate_health_score = validate_mod.calculate_health_score


def _collect_all_blocks():
    """Collect mermaid blocks from docs/, commands/, skills/."""
    blocks = []
    for search_dir in [DOCS_DIR, COMMANDS_DIR, SKILLS_DIR]:
        if search_dir.exists():
            for md_file in sorted(search_dir.rglob("*.md")):
                blocks.extend(extract_mermaid_blocks(str(md_file)))
    return blocks


# ─── Syntax Validation ──────────────────────────────────────────────────────


@pytest.mark.mermaid
class TestSyntaxValidation:
    """Validate all mermaid blocks in the repo."""

    def test_all_docs_mermaid_blocks_have_valid_syntax(self):
        """Every block in docs/ passes regex lint (errors only)."""
        blocks = _collect_all_blocks()
        assert len(blocks) > 0, "Should find mermaid blocks in docs"
        issues = validate_blocks(blocks)
        errors = [i for i in issues if i.severity == "error"]
        assert len(errors) == 0, (
            f"Found {len(errors)} syntax errors:\n"
            + "\n".join(f"  {e.file}:{e.line_number} [{e.rule}] {e.context}" for e in errors[:10])
        )

    def test_no_leading_slash_in_mermaid_labels(self):
        """Zero [/ patterns in any mermaid block."""
        blocks = _collect_all_blocks()
        issues = validate_blocks(blocks)
        slash_errors = [i for i in issues if i.rule == "leading-slash"]
        assert len(slash_errors) == 0, (
            f"Found {len(slash_errors)} leading-slash issues:\n"
            + "\n".join(f"  {e.file}:{e.line_number} {e.context}" for e in slash_errors[:5])
        )

    def test_no_lowercase_end_in_mermaid(self):
        """Zero lowercase 'end' in mermaid node labels."""
        blocks = _collect_all_blocks()
        issues = validate_blocks(blocks)
        end_errors = [i for i in issues if i.rule == "lowercase-end"]
        assert len(end_errors) == 0, (
            f"Found {len(end_errors)} lowercase-end issues:\n"
            + "\n".join(f"  {e.file}:{e.line_number} {e.context}" for e in end_errors[:5])
        )

    @pytest.mark.xfail(reason="br-tag cleanup tracked for gradual removal", strict=False)
    def test_no_br_tags_in_mermaid(self):
        """Zero <br/> in mermaid blocks (warning-level, tracked for gradual cleanup)."""
        blocks = _collect_all_blocks()
        issues = validate_blocks(blocks)
        br_warnings = [i for i in issues if i.rule == "br-tag"]
        assert len(br_warnings) == 0, (
            f"Found {len(br_warnings)} br-tag warnings (tracked for cleanup)"
        )


# ─── Health Score ────────────────────────────────────────────────────────────


@pytest.mark.mermaid
class TestHealthScore:
    """Health score meets release threshold."""

    def test_mermaid_health_score_above_threshold(self):
        """Health score >= 80 for entire docs/."""
        blocks = _collect_all_blocks()
        issues = validate_blocks(blocks)
        health = calculate_health_score(blocks, issues)
        assert health["score"] >= 80, (
            f"Health score {health['score']} below release threshold 80\n"
            f"  Syntax: {health['syntax']}%\n"
            f"  Practices: {health['practices']}%\n"
            f"  Rendering: {health['rendering']}%"
        )


# ─── Documentation Structure ────────────────────────────────────────────────


@pytest.mark.structure
class TestDocumentation:
    """Verify all documentation components are updated."""

    def test_mermaid_command_has_mcp_docs(self):
        """/craft:docs:mermaid documents MCP validation."""
        cmd = COMMANDS_DIR / "docs" / "mermaid.md"
        assert cmd.exists()
        content = cmd.read_text()
        assert "mcp-mermaid" in content.lower() or "MCP" in content
        assert "--validate" in content

    def test_mermaid_linter_skill_has_mcp_rules(self):
        """Skill file includes MCP validation rules."""
        skill = SKILLS_DIR / "docs" / "mermaid-linter" / "skill.md"
        assert skill.exists()
        content = skill.read_text()
        assert "mcp-mermaid" in content.lower() or "MCP" in content
        assert "health" in content.lower()

    def test_docs_check_command_mentions_mermaid(self):
        """Check command docs include mermaid phase."""
        cmd = COMMANDS_DIR / "docs" / "check.md"
        assert cmd.exists()
        content = cmd.read_text()
        assert "Mermaid Validation" in content or "mermaid" in content.lower()


# ─── Infrastructure ──────────────────────────────────────────────────────────


@pytest.mark.structure
class TestInfrastructure:
    """Verify MCP config and mkdocs setup."""

    def test_mcp_config_exists(self):
        """.mcp.json exists with mcp-mermaid server."""
        import json
        mcp_json = PLUGIN_DIR / ".mcp.json"
        assert mcp_json.exists(), "Missing .mcp.json"
        config = json.loads(mcp_json.read_text())
        assert "mcp-mermaid" in config.get("mcpServers", {}), "mcp-mermaid not in .mcp.json"

    def test_mermaid_init_js_exists(self):
        """docs/javascripts/mermaid-init.js exists (if referenced in mkdocs.yml)."""
        js_path = DOCS_DIR / "javascripts" / "mermaid-init.js"
        mkdocs = PLUGIN_DIR / "mkdocs.yml"
        if mkdocs.exists():
            # Use regex instead of yaml.safe_load to avoid !!python/name tags
            import re
            content = mkdocs.read_text()
            if re.search(r"mermaid-init", content):
                assert js_path.exists(), "mkdocs.yml references mermaid-init.js but file missing"
