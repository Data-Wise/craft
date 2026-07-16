#!/usr/bin/env python3
"""
Mermaid E2E Tests
==================
End-to-end tests for mermaid validation pipeline integration.

Run with: python3 -m pytest tests/test_mermaid_e2e.py -v
Skip MCP tests: python3 -m pytest tests/test_mermaid_e2e.py -v -m "not mermaid_mcp"
"""

import importlib.util
import subprocess
from pathlib import Path

import pytest

pytestmark = [pytest.mark.e2e]

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


# ─── MCP Validation Tests ────────────────────────────────────────────────────


@pytest.mark.mermaid_mcp
class TestMCPValidation:
    """Tests requiring mcp-mermaid MCP server (skipped in CI without MCP)."""

    def test_mcp_mermaid_validates_good_diagram(self):
        """MCP returns valid for clean diagram."""
        pytest.skip("MCP integration test — requires mcp-mermaid server running")

    def test_mcp_mermaid_rejects_bad_diagram(self):
        """MCP returns error for broken syntax."""
        pytest.skip("MCP integration test — requires mcp-mermaid server running")


# ─── Pipeline Integration Tests ──────────────────────────────────────────────


# NOTE: TestDocsCheckIntegration removed 2026-07-12 — commands/docs/check.md moved to
# the `folio` plugin in the folio split (Phase 3); that coverage is folio's now.
# See ORCHESTRATE-folio-split.md / tasks/todo.md T3.3.

# ─── Validation Pipeline Tests ───────────────────────────────────────────────


@pytest.mark.mermaid
class TestValidationPipeline:
    """Tests for the full validation pipeline."""

    def test_all_existing_blocks_pass_validation(self):
        """Every mermaid block in docs/ passes local regex (errors only)."""
        all_blocks = []
        for md_file in sorted(DOCS_DIR.rglob("*.md")):
            all_blocks.extend(extract_mermaid_blocks(str(md_file)))

        issues = validate_blocks(all_blocks)
        errors = [i for i in issues if i.severity == "error"]

        # Filter out known intentional bad examples (text fences should prevent this)
        assert len(errors) == 0, (
            f"Found {len(errors)} errors in docs/ mermaid blocks:\n"
            + "\n".join(f"  {e.file}:{e.line_number} [{e.rule}] {e.context}" for e in errors[:5])
        )

    def test_autofix_produces_valid_output(self):
        """Auto-fix self-tests pass."""
        result = subprocess.run(
            ["python3", str(SCRIPTS_DIR / "mermaid-autofix.py"), "--test"],
            capture_output=True, text=True, cwd=str(PLUGIN_DIR),
        )
        assert result.returncode == 0, f"Auto-fix self-tests failed:\n{result.stdout}\n{result.stderr}"
        assert "0 failed" in result.stdout


# ─── Pre-commit Hook Tests ───────────────────────────────────────────────────


@pytest.mark.mermaid
class TestPrecommitHook:
    """Tests for pre-commit hook setup."""

    def test_precommit_hook_exists(self):
        """Pre-commit hook script exists and is executable."""
        hook = SCRIPTS_DIR / "hooks" / "pre-commit-mermaid.sh"
        assert hook.exists(), f"Missing: {hook}"
        assert hook.stat().st_mode & 0o111, f"Hook not executable: {hook}"

    def test_precommit_config_has_mermaid(self):
        """Pre-commit config includes mermaid-validate hook."""
        import yaml
        config_path = PLUGIN_DIR / ".pre-commit-config.yaml"
        assert config_path.exists()
        config = yaml.safe_load(config_path.read_text())
        hook_ids = []
        for repo in config.get("repos", []):
            for hook in repo.get("hooks", []):
                hook_ids.append(hook.get("id", ""))
        assert "mermaid-validate" in hook_ids, f"mermaid-validate not in hooks: {hook_ids}"


# NOTE: TestStructure (mermaid-linter skill, docs:mermaid command) removed
# 2026-07-12 — both moved to the `folio` plugin in the folio split (Phase 3);
# that coverage is folio's now. See ORCHESTRATE-folio-split.md / tasks/todo.md T3.3.
