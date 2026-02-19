#!/usr/bin/env python3
"""Tests for utils/test_generator.py — the Jinja2 test generation engine.

Covers the 3-phase pipeline (detect → gather → render), helper functions,
template syntax validation, and full integration via generate_tests().
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).parent.parent))

from utils.test_generator import (
    TEMPLATES_DIR,
    VALID_TYPES,
    _load_registry,
    _parse_help_commands,
    _parse_package_json_cli,
    _parse_pyproject_cli,
    detect_project_type,
    gather_variables,
    generate_tests,
    render_templates,
)

pytestmark = [pytest.mark.unit]


# ─── Detection Tests ────────────────────────────────────────────────────────


class TestDetectProjectType:
    """Phase 1: detect_project_type() from indicator files."""

    def test_detect_plugin_type(self, temp_plugin_dir: Path):
        """Plugin.json triggers 'plugin' detection."""
        assert detect_project_type(temp_plugin_dir) == "plugin"

    def test_detect_zsh_type(self, temp_zsh_plugin: Path):
        """*.plugin.zsh triggers 'zsh' detection."""
        assert detect_project_type(temp_zsh_plugin) == "zsh"

    def test_detect_cli_pyproject(self, temp_cli_project: Path):
        """pyproject.toml with [project.scripts] triggers 'cli'."""
        assert detect_project_type(temp_cli_project) == "cli"

    def test_detect_cli_package_json(self, tmp_path: Path):
        """package.json with 'bin' triggers 'cli'."""
        d = tmp_path / "js-cli"
        d.mkdir()
        (d / "package.json").write_text(json.dumps({
            "name": "js-cli",
            "bin": {"js-cli": "./cli.js"},
        }))
        assert detect_project_type(d) == "cli"

    def test_detect_mcp_directory(self, temp_mcp_project: Path):
        """mcp-server/ directory triggers 'mcp' detection."""
        assert detect_project_type(temp_mcp_project) == "mcp"

    def test_detect_priority_plugin_over_cli(self, tmp_path: Path):
        """Plugin wins over CLI when both indicators present."""
        d = tmp_path / "mixed"
        d.mkdir()
        (d / ".claude-plugin").mkdir()
        (d / ".claude-plugin" / "plugin.json").write_text('{"name": "mixed"}')
        (d / "pyproject.toml").write_text(
            '[project]\nname = "mixed"\n\n[project.scripts]\nmixed = "m:main"\n'
        )
        assert detect_project_type(d) == "plugin"

    def test_detect_unknown_raises(self, tmp_path: Path):
        """Empty directory raises ValueError."""
        d = tmp_path / "empty"
        d.mkdir()
        with pytest.raises(ValueError, match="Cannot detect project type"):
            detect_project_type(d)

    def test_detect_nonexistent_raises(self, tmp_path: Path):
        """Missing path raises ValueError."""
        with pytest.raises(ValueError, match="Not a directory"):
            detect_project_type(tmp_path / "nonexistent")


# ─── Variable Gathering Tests ───────────────────────────────────────────────


class TestGatherVariables:
    """Phase 2: gather_variables() for each project type."""

    def test_gather_plugin_variables(self, temp_plugin_dir: Path):
        """Plugin gatherer reads manifest and globs commands/skills/agents."""
        # Add some command files
        cmd_dir = temp_plugin_dir / "commands"
        (cmd_dir / "test.md").write_text("---\nname: test\n---\n")
        (cmd_dir / "lint.md").write_text("---\nname: lint\n---\n")

        v = gather_variables(temp_plugin_dir, "plugin")
        assert v["project_type"] == "plugin"
        assert v["project_name"] == "test-plugin"
        assert v["project_version"] == "1.0.0"
        assert isinstance(v["commands"], list)
        assert len(v["commands"]) == 2
        assert isinstance(v["skills"], list)
        assert isinstance(v["agents"], list)
        assert "plugin_json" in v

    def test_gather_zsh_variables(self, temp_zsh_plugin: Path):
        """ZSH gatherer finds functions, aliases, and completions."""
        v = gather_variables(temp_zsh_plugin, "zsh")
        assert v["project_type"] == "zsh"
        assert v["project_name"] == "my-zsh-plugin"
        assert "my_func" in v["functions"]
        assert "another_func" in v["functions"]
        assert "mf" in v["aliases"]
        assert "af" in v["aliases"]
        assert len(v["completions"]) >= 1

    def test_gather_cli_variables(self, temp_cli_project: Path):
        """CLI gatherer parses pyproject.toml entry points."""
        v = gather_variables(temp_cli_project, "cli")
        assert v["project_type"] == "cli"
        assert v["project_name"] == "my-cli"
        assert v["cli_name"] == "my-cli"
        assert "my-cli" in v["entry_points"]
        assert v["entry_points"]["my-cli"] == "my_cli.main:app"

    def test_gather_mcp_variables(self, temp_mcp_project: Path):
        """MCP gatherer reads server name and discovers tools."""
        v = gather_variables(temp_mcp_project, "mcp")
        assert v["project_type"] == "mcp"
        assert v["server_name"] == "my-mcp-server"
        assert "fetch_data" in v["tools"]
        assert "run_query" in v["tools"]
        assert v["transport"] == "stdio"

    def test_gather_includes_markers(self, craft_root: Path):
        """Markers are read from pyproject.toml when present."""
        v = gather_variables(craft_root, "plugin")
        assert "markers" in v
        assert "unit" in v["markers"]
        assert "integration" in v["markers"]

    def test_gather_invalid_type_raises(self, tmp_path: Path):
        """Unknown project type raises ValueError."""
        d = tmp_path / "any"
        d.mkdir()
        with pytest.raises(ValueError, match="Unknown project type"):
            gather_variables(d, "invalid_type")


# ─── Rendering Tests ────────────────────────────────────────────────────────


class TestRenderTemplates:
    """Phase 3: render_templates() for each project type."""

    def _get_variables(self, project_path: Path, project_type: str):
        """Helper to get variables with safe defaults for rendering."""
        try:
            return gather_variables(project_path, project_type)
        except Exception:
            # Fallback minimal variables for rendering
            return {
                "project_type": project_type,
                "project_name": "test-project",
                "test_dir": "tests",
            }

    def test_render_plugin_templates(self, temp_plugin_dir: Path):
        """All 7 plugin templates render without errors."""
        v = gather_variables(temp_plugin_dir, "plugin")
        files = render_templates(temp_plugin_dir, "plugin", v)
        filenames = [f[0] for f in files]
        assert "test_structure.py" in filenames
        assert "test_commands.py" in filenames
        # No ERROR markers in rendered content
        for name, content in files:
            assert not content.startswith("# ERROR:"), f"{name} failed to render"

    def test_render_zsh_templates(self, temp_zsh_plugin: Path):
        """All 5 ZSH templates render without errors."""
        v = gather_variables(temp_zsh_plugin, "zsh")
        files = render_templates(temp_zsh_plugin, "zsh", v)
        filenames = [f[0] for f in files]
        assert "test_sourcing.sh" in filenames
        assert "test_functions.sh" in filenames
        for name, content in files:
            assert not content.startswith("# ERROR:"), f"{name} failed to render"

    def test_render_cli_templates(self, temp_cli_project: Path):
        """All 7 CLI templates render without errors."""
        v = gather_variables(temp_cli_project, "cli")
        files = render_templates(temp_cli_project, "cli", v)
        filenames = [f[0] for f in files]
        assert "test_smoke.py" in filenames
        assert "test_commands.py" in filenames
        for name, content in files:
            assert not content.startswith("# ERROR:"), f"{name} failed to render"

    def test_render_mcp_templates(self, temp_mcp_project: Path):
        """All 5 MCP templates render without errors."""
        v = gather_variables(temp_mcp_project, "mcp")
        files = render_templates(temp_mcp_project, "mcp", v)
        filenames = [f[0] for f in files]
        assert "test_protocol.py" in filenames
        assert "test_tools.py" in filenames
        for name, content in files:
            assert not content.startswith("# ERROR:"), f"{name} failed to render"

    def test_rendered_python_compiles(self, temp_plugin_dir: Path):
        """All rendered .py files pass compile() — valid Python syntax."""
        v = gather_variables(temp_plugin_dir, "plugin")
        files = render_templates(temp_plugin_dir, "plugin", v)
        for name, content in files:
            if name.endswith(".py"):
                try:
                    compile(content, name, "exec")
                except SyntaxError as exc:
                    pytest.fail(f"{name} has invalid Python syntax: {exc}")

    def test_rendered_bash_has_header(self, temp_zsh_plugin: Path):
        """All rendered .sh files start with a shebang line."""
        v = gather_variables(temp_zsh_plugin, "zsh")
        files = render_templates(temp_zsh_plugin, "zsh", v)
        for name, content in files:
            if name.endswith(".sh"):
                assert content.startswith("#!/"), (
                    f"{name} missing shebang header"
                )


# ─── Integration Tests ──────────────────────────────────────────────────────


class TestGenerateTests:
    """Full pipeline: generate_tests() end-to-end."""

    pytestmark = [pytest.mark.unit, pytest.mark.integration]

    def test_generate_tests_dry_run(self, temp_plugin_dir: Path, tmp_path: Path):
        """Dry run returns files without writing anything."""
        out_dir = tmp_path / "output"
        result = generate_tests(
            temp_plugin_dir, output_dir=out_dir, dry_run=True
        )
        assert result["project_type"] == "plugin"
        assert len(result["files"]) > 0
        assert result["written"] == 0
        assert not out_dir.exists()

    def test_generate_tests_writes_files(self, temp_plugin_dir: Path, tmp_path: Path):
        """Full pipeline writes rendered files to output dir."""
        out_dir = tmp_path / "output"
        result = generate_tests(
            temp_plugin_dir, output_dir=out_dir, dry_run=False
        )
        assert result["written"] > 0
        assert out_dir.is_dir()
        written_files = list(out_dir.iterdir())
        assert len(written_files) == result["written"]

    def test_generate_tests_skips_existing(self, temp_plugin_dir: Path, tmp_path: Path):
        """Existing files are skipped, not overwritten."""
        out_dir = tmp_path / "output"
        # First run — writes files
        result1 = generate_tests(
            temp_plugin_dir, output_dir=out_dir, dry_run=False
        )
        assert result1["written"] > 0

        # Second run — all should be skipped
        result2 = generate_tests(
            temp_plugin_dir, output_dir=out_dir, dry_run=False
        )
        assert result2["written"] == 0
        assert result2["skipped"] == result1["written"]

    def test_generate_tests_against_craft(self, craft_root: Path):
        """Dogfood: dry-run against the real craft directory succeeds."""
        result = generate_tests(craft_root, dry_run=True)
        assert result["project_type"] == "plugin"
        assert len(result["files"]) > 0
        assert "project_name" in result["variables"]


# ─── Helper Function Tests ──────────────────────────────────────────────────


class TestHelpers:
    """Tests for parsing and registry helpers."""

    def test_parse_help_commands(self):
        """Parses subcommands from --help output."""
        help_text = (
            "Usage: my-cli [OPTIONS] COMMAND\n\n"
            "Commands:\n"
            "  init       Initialize project\n"
            "  build      Build the project\n"
            "  deploy     Deploy to server\n\n"
            "Options:\n"
            "  --help     Show this message\n"
        )
        commands = _parse_help_commands(help_text)
        assert commands == ["init", "build", "deploy"]

    def test_parse_help_commands_empty(self):
        """Returns empty list when no commands section found."""
        assert _parse_help_commands("Usage: tool [OPTIONS]\n") == []

    def test_parse_pyproject_cli(self, temp_cli_project: Path):
        """Extracts entry points from pyproject.toml."""
        result = _parse_pyproject_cli(temp_cli_project / "pyproject.toml")
        assert result["project_name"] == "my-cli"
        assert result["cli_name"] == "my-cli"
        assert "my-cli" in result["entry_points"]
        assert "my-cli-helper" in result["entry_points"]

    def test_parse_package_json_cli(self, tmp_path: Path):
        """Extracts bin field from package.json."""
        pkg = tmp_path / "package.json"
        pkg.write_text(json.dumps({
            "name": "my-node-cli",
            "bin": {"my-node-cli": "./cli.js", "helper": "./helper.js"},
        }))
        result = _parse_package_json_cli(pkg)
        assert result["project_name"] == "my-node-cli"
        assert result["cli_name"] == "my-node-cli"
        assert len(result["entry_points"]) == 2

    def test_load_registry(self):
        """Registry loads and has expected structure."""
        registry = _load_registry()
        assert "types" in registry
        assert "shared" in registry
        for ptype in VALID_TYPES:
            assert ptype in registry["types"]
            assert "detect" in registry["types"][ptype]
            assert "templates" in registry["types"][ptype]


# ─── Template Syntax Validation ─────────────────────────────────────────────


class TestTemplateSyntax:
    """Validate all .j2 templates parse without Jinja2 syntax errors."""

    @staticmethod
    def _all_j2_files():
        """Collect all .j2 template files."""
        return sorted(TEMPLATES_DIR.rglob("*.j2"))

    @pytest.mark.parametrize(
        "template_path",
        _all_j2_files.__func__(),
        ids=lambda p: str(p.relative_to(TEMPLATES_DIR)),
    )
    def test_template_parses(self, template_path: Path):
        """Each .j2 file parses without Jinja2 syntax errors."""
        from jinja2 import Environment, FileSystemLoader

        parent_dir = template_path.parent
        env = Environment(
            loader=FileSystemLoader([str(parent_dir), str(TEMPLATES_DIR)]),
            keep_trailing_newline=True,
        )
        # env.parse() checks syntax without needing variable values
        source = template_path.read_text(encoding="utf-8")
        env.parse(source)
