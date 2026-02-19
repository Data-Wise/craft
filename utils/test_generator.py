#!/usr/bin/env python3
"""
Test Generation Engine for /craft:test:gen

Detects project type, gathers template variables, and renders Jinja2 templates
to produce project-specific test suites. Supports four project types:

- plugin: Claude Code plugins (.claude-plugin/plugin.json)
- zsh: ZSH plugins (*.plugin.zsh)
- cli: CLI applications (pyproject.toml with [project.scripts])
- mcp: MCP servers (mcp-server/ directory)

Usage:
    from utils.test_generator import generate_tests

    result = generate_tests(Path("."), dry_run=True)
    for filename, content in result["files"]:
        print(f"Would write: {filename}")
"""

import glob as globmod
import json
import re
import subprocess
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple

try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    Environment = None
    FileSystemLoader = None


# ─── Constants ──────────────────────────────────────────────────────────────

TEMPLATES_DIR = Path(__file__).parent.parent / "templates"
REGISTRY_PATH = TEMPLATES_DIR / "registry.json"

VALID_TYPES = ("plugin", "zsh", "cli", "mcp")


# ─── Registry Loading ───────────────────────────────────────────────────────


def _load_registry() -> Dict[str, Any]:
    """
    Load the template registry from templates/registry.json.

    Returns:
        Parsed registry dictionary

    Raises:
        FileNotFoundError: If registry.json is missing
    """
    if not REGISTRY_PATH.exists():
        raise FileNotFoundError(f"Template registry not found: {REGISTRY_PATH}")
    return json.loads(REGISTRY_PATH.read_text(encoding="utf-8"))


# ─── Project Detection ──────────────────────────────────────────────────────


def detect_project_type(project_path: Path) -> str:
    """
    Detect project type from indicator files defined in registry.json.

    Detection order (first match wins):
        1. plugin — .claude-plugin/plugin.json exists
        2. mcp — mcp-server/ directory or src/mcp_server.py exists
        3. cli — pyproject.toml with [project.scripts], package.json with bin
        4. zsh — *.plugin.zsh file exists

    Args:
        project_path: Root directory of the project to analyze

    Returns:
        One of: "plugin", "zsh", "cli", "mcp"

    Raises:
        ValueError: If no project type can be detected
    """
    project_path = Path(project_path).resolve()

    if not project_path.is_dir():
        raise ValueError(f"Not a directory: {project_path}")

    registry = _load_registry()
    type_defs = registry["types"]

    # Check in priority order: plugin > mcp > cli > zsh
    detection_order = ["plugin", "mcp", "cli", "zsh"]

    for ptype in detection_order:
        if ptype not in type_defs:
            continue
        detect_rules = type_defs[ptype].get("detect", [])
        if _matches_detection_rules(project_path, detect_rules):
            return ptype

    raise ValueError(
        f"Cannot detect project type in {project_path}. "
        f"Expected one of: {', '.join(VALID_TYPES)}"
    )


def _matches_detection_rules(project_path: Path, rules: List[str]) -> bool:
    """
    Check if any detection rule matches the project directory.

    Supports rule formats:
        - "path/to/file" — file existence check
        - "*.pattern" — glob match
        - "file.ext:section" — file exists AND contains section string
        - "dir/" — directory existence check
        - "file1+file2" — both files must exist

    Args:
        project_path: Project root directory
        rules: Detection rules from registry.json

    Returns:
        True if any rule matches
    """
    for rule in rules:
        if "+" in rule and ":" not in rule:
            # Compound rule: both files must exist (e.g., "go.mod+main.go")
            parts = rule.split("+")
            if all((project_path / p.strip()).exists() for p in parts):
                return True

        elif rule.endswith("/"):
            # Directory existence check (e.g., "mcp-server/")
            if (project_path / rule.rstrip("/")).is_dir():
                return True

        elif ":" in rule and "*" not in rule:
            # File with content check (e.g., "pyproject.toml:[project.scripts]")
            filepath, section = rule.split(":", 1)
            target = project_path / filepath
            if target.exists():
                content = target.read_text(encoding="utf-8")
                if section in content:
                    return True

        elif "*" in rule:
            # Glob pattern (e.g., "*.plugin.zsh")
            matches = list(project_path.glob(rule))
            if matches:
                return True

        else:
            # Simple file existence (e.g., ".claude-plugin/plugin.json")
            if (project_path / rule).exists():
                return True

    return False


# ─── Variable Gathering ─────────────────────────────────────────────────────


def gather_variables(project_path: Path, project_type: str) -> Dict[str, Any]:
    """
    Collect template variables based on project type.

    Dispatches to type-specific gatherers and merges with shared variables.

    Args:
        project_path: Root directory of the project
        project_type: One of "plugin", "zsh", "cli", "mcp"

    Returns:
        Dictionary of template variables

    Raises:
        ValueError: If project_type is not recognized
    """
    project_path = Path(project_path).resolve()

    if project_type not in VALID_TYPES:
        raise ValueError(f"Unknown project type: {project_type}")

    # Shared variables available to all templates
    variables: Dict[str, Any] = {
        "project_type": project_type,
        "test_dir": "tests",
    }

    # Dispatch to type-specific gatherer
    gatherers = {
        "plugin": _gather_plugin_variables,
        "zsh": _gather_zsh_variables,
        "cli": _gather_cli_variables,
        "mcp": _gather_mcp_variables,
    }

    type_vars = gatherers[project_type](project_path)
    variables.update(type_vars)

    # Read pytest markers from pyproject.toml if available
    markers = _read_pytest_markers(project_path)
    if markers:
        variables["markers"] = markers

    return variables


def _gather_plugin_variables(project_path: Path) -> Dict[str, Any]:
    """
    Gather variables for Claude Code plugin projects.

    Reads plugin.json manifest, globs commands, skills, and agents.

    Args:
        project_path: Project root directory

    Returns:
        Plugin-specific template variables
    """
    variables: Dict[str, Any] = {}

    # Read plugin.json
    manifest_path = project_path / ".claude-plugin" / "plugin.json"
    if manifest_path.exists():
        plugin_json = json.loads(manifest_path.read_text(encoding="utf-8"))
        variables["plugin_json"] = plugin_json
        variables["project_name"] = plugin_json.get("name", project_path.name)
        variables["project_version"] = plugin_json.get("version", "0.0.0")
    else:
        variables["plugin_json"] = {}
        variables["project_name"] = project_path.name

    # Glob commands
    commands_dir = project_path / "commands"
    if commands_dir.is_dir():
        command_files = sorted(commands_dir.rglob("*.md"))
        variables["commands"] = [
            str(f.relative_to(commands_dir)) for f in command_files
        ]
    else:
        variables["commands"] = []

    # Glob skills
    skills_dir = project_path / "skills"
    if skills_dir.is_dir():
        skill_files = sorted(skills_dir.rglob("SKILL.md"))
        variables["skills"] = [
            str(f.relative_to(skills_dir)) for f in skill_files
        ]
    else:
        variables["skills"] = []

    # Glob agents
    agents_dir = project_path / "agents"
    if agents_dir.is_dir():
        agent_files = sorted(agents_dir.rglob("*.md"))
        variables["agents"] = [
            str(f.relative_to(agents_dir)) for f in agent_files
        ]
    else:
        variables["agents"] = []

    return variables


def _gather_zsh_variables(project_path: Path) -> Dict[str, Any]:
    """
    Gather variables for ZSH plugin projects.

    Finds plugin file, greps for functions, aliases, and completions.

    Args:
        project_path: Project root directory

    Returns:
        ZSH-specific template variables
    """
    variables: Dict[str, Any] = {
        "project_name": project_path.name,
    }

    # Find main plugin file
    plugin_files = list(project_path.glob("*.plugin.zsh"))
    if plugin_files:
        plugin_file = plugin_files[0]
        variables["plugin_file"] = plugin_file.name
        content = plugin_file.read_text(encoding="utf-8")
    else:
        # Fall back to any .zsh file
        zsh_files = list(project_path.glob("*.zsh"))
        if zsh_files:
            variables["plugin_file"] = zsh_files[0].name
            content = zsh_files[0].read_text(encoding="utf-8")
        else:
            variables["plugin_file"] = ""
            content = ""

    # Grep for function definitions
    func_pattern = re.compile(r"^([a-z_][a-z0-9_]*)\s*\(\)", re.MULTILINE)
    variables["functions"] = func_pattern.findall(content)

    # Grep for aliases
    alias_pattern = re.compile(r"^alias\s+([a-zA-Z0-9_-]+)=", re.MULTILINE)
    variables["aliases"] = alias_pattern.findall(content)

    # Grep for completions
    compdef_pattern = re.compile(r"(?:compdef|_comps)\s+\S+", re.MULTILINE)
    variables["completions"] = compdef_pattern.findall(content)

    return variables


def _gather_cli_variables(project_path: Path) -> Dict[str, Any]:
    """
    Gather variables for CLI application projects.

    Reads pyproject.toml or package.json for entry points, parses --help
    output for subcommands.

    Args:
        project_path: Project root directory

    Returns:
        CLI-specific template variables
    """
    variables: Dict[str, Any] = {}

    # Try pyproject.toml first
    pyproject = project_path / "pyproject.toml"
    package_json = project_path / "package.json"

    if pyproject.exists():
        variables.update(_parse_pyproject_cli(pyproject))
    elif package_json.exists():
        variables.update(_parse_package_json_cli(package_json))
    else:
        variables["project_name"] = project_path.name
        variables["cli_name"] = project_path.name
        variables["entry_points"] = {}

    # Try to discover subcommands from --help output
    cli_name = variables.get("cli_name", "")
    variables["commands"] = _discover_subcommands(cli_name)
    variables["subcommands"] = {}
    variables["flags"] = _discover_flags(cli_name)

    return variables


def _parse_pyproject_cli(pyproject_path: Path) -> Dict[str, Any]:
    """
    Parse CLI information from pyproject.toml.

    Args:
        pyproject_path: Path to pyproject.toml

    Returns:
        Dictionary with project_name, cli_name, entry_points
    """
    content = pyproject_path.read_text(encoding="utf-8")
    variables: Dict[str, Any] = {}

    # Extract project name
    name_match = re.search(r'^\s*name\s*=\s*"([^"]+)"', content, re.MULTILINE)
    variables["project_name"] = name_match.group(1) if name_match else "unknown"

    # Extract [project.scripts] entries
    entry_points: Dict[str, str] = {}
    in_scripts = False
    for line in content.splitlines():
        stripped = line.strip()
        if stripped == "[project.scripts]":
            in_scripts = True
            continue
        if in_scripts:
            if stripped.startswith("["):
                break
            ep_match = re.match(r'^([a-zA-Z0-9_-]+)\s*=\s*"([^"]+)"', stripped)
            if ep_match:
                entry_points[ep_match.group(1)] = ep_match.group(2)

    variables["entry_points"] = entry_points

    # Use first entry point as cli_name
    if entry_points:
        variables["cli_name"] = next(iter(entry_points))
    else:
        variables["cli_name"] = variables["project_name"]

    return variables


def _parse_package_json_cli(package_json_path: Path) -> Dict[str, Any]:
    """
    Parse CLI information from package.json.

    Args:
        package_json_path: Path to package.json

    Returns:
        Dictionary with project_name, cli_name, entry_points
    """
    data = json.loads(package_json_path.read_text(encoding="utf-8"))
    variables: Dict[str, Any] = {}

    variables["project_name"] = data.get("name", "unknown")

    # Extract bin entries
    bin_field = data.get("bin", {})
    if isinstance(bin_field, str):
        # Single binary: "bin": "./cli.js"
        entry_points = {variables["project_name"]: bin_field}
    elif isinstance(bin_field, dict):
        entry_points = dict(bin_field)
    else:
        entry_points = {}

    variables["entry_points"] = entry_points

    if entry_points:
        variables["cli_name"] = next(iter(entry_points))
    else:
        variables["cli_name"] = variables["project_name"]

    return variables


def _discover_subcommands(cli_name: str) -> List[str]:
    """
    Discover subcommands by running --help and parsing output.

    Silently returns empty list if the CLI is not available or fails.

    Args:
        cli_name: Name of the CLI executable

    Returns:
        List of discovered subcommand names
    """
    if not cli_name:
        return []

    try:
        result = subprocess.run(
            [cli_name, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []
        return _parse_help_commands(result.stdout)
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def _parse_help_commands(help_text: str) -> List[str]:
    """
    Parse subcommand names from --help output.

    Looks for common patterns in CLI help text:
      - "Commands:" or "commands:" sections
      - Indented lines with command names

    Args:
        help_text: Raw --help output

    Returns:
        List of subcommand names
    """
    commands: List[str] = []
    in_commands_section = False

    for line in help_text.splitlines():
        stripped = line.strip()

        # Detect commands section header
        if re.match(r"^(commands|subcommands|available commands)\s*:?\s*$", stripped, re.IGNORECASE):
            in_commands_section = True
            continue

        # Detect end of section (empty line or new section header)
        if in_commands_section:
            if not stripped:
                in_commands_section = False
                continue
            if re.match(r"^[A-Z].*:$", stripped):
                in_commands_section = False
                continue

            # Extract command name (first word on indented line)
            cmd_match = re.match(r"^\s{2,}([a-z][a-z0-9_-]*)", line)
            if cmd_match:
                commands.append(cmd_match.group(1))

    return commands


def _discover_flags(cli_name: str) -> List[str]:
    """
    Discover global flags from --help output.

    Args:
        cli_name: Name of the CLI executable

    Returns:
        List of flag strings (e.g., ["--verbose", "--quiet"])
    """
    if not cli_name:
        return []

    try:
        result = subprocess.run(
            [cli_name, "--help"],
            capture_output=True,
            text=True,
            timeout=10,
        )
        if result.returncode != 0:
            return []

        flags: List[str] = []
        for line in result.stdout.splitlines():
            flag_match = re.findall(r"(--[a-z][a-z0-9-]*)", line)
            flags.extend(flag_match)

        # Deduplicate while preserving order
        seen: set = set()
        unique_flags: List[str] = []
        for flag in flags:
            if flag not in seen:
                seen.add(flag)
                unique_flags.append(flag)

        return unique_flags
    except (FileNotFoundError, subprocess.TimeoutExpired, OSError):
        return []


def _gather_mcp_variables(project_path: Path) -> Dict[str, Any]:
    """
    Gather variables for MCP server projects.

    Reads manifest files for tools, resources, and transport configuration.

    Args:
        project_path: Project root directory

    Returns:
        MCP-specific template variables
    """
    variables: Dict[str, Any] = {
        "transport": "stdio",
        "tools": [],
        "resources": [],
    }

    # Try to find the manifest/config
    manifest_candidates = [
        project_path / "mcp-server" / "package.json",
        project_path / "package.json",
        project_path / "pyproject.toml",
    ]

    for candidate in manifest_candidates:
        if not candidate.exists():
            continue

        if candidate.name == "package.json":
            data = json.loads(candidate.read_text(encoding="utf-8"))
            variables["server_name"] = data.get("name", project_path.name)

            # Check for MCP-specific config
            mcp_config = data.get("mcp", {})
            if isinstance(mcp_config, dict):
                variables["tools"] = mcp_config.get("tools", [])
                variables["resources"] = mcp_config.get("resources", [])
                variables["transport"] = mcp_config.get("transport", "stdio")
            break

        elif candidate.name == "pyproject.toml":
            content = candidate.read_text(encoding="utf-8")
            name_match = re.search(r'^\s*name\s*=\s*"([^"]+)"', content, re.MULTILINE)
            variables["server_name"] = name_match.group(1) if name_match else project_path.name
            break
    else:
        variables["server_name"] = project_path.name

    # Try to discover tools from source files
    if not variables["tools"]:
        variables["tools"] = _discover_mcp_tools(project_path)

    return variables


def _discover_mcp_tools(project_path: Path) -> List[str]:
    """
    Discover MCP tool names by scanning source files for tool registrations.

    Args:
        project_path: Project root directory

    Returns:
        List of discovered tool names
    """
    tools: List[str] = []

    # Scan Python files for @server.tool or tool registration patterns
    py_files = list(project_path.rglob("*.py"))
    for py_file in py_files:
        if ".git" in str(py_file) or "node_modules" in str(py_file):
            continue
        try:
            content = py_file.read_text(encoding="utf-8")
            # Pattern: @server.tool("tool_name") or register_tool("tool_name")
            tool_matches = re.findall(
                r'(?:@\w+\.tool|register_tool)\s*\(\s*["\']([^"\']+)["\']',
                content,
            )
            tools.extend(tool_matches)
        except (OSError, UnicodeDecodeError):
            continue

    # Scan TypeScript/JavaScript files
    ts_files = list(project_path.rglob("*.ts")) + list(project_path.rglob("*.js"))
    for ts_file in ts_files:
        if "node_modules" in str(ts_file) or ".git" in str(ts_file):
            continue
        try:
            content = ts_file.read_text(encoding="utf-8")
            tool_matches = re.findall(
                r'(?:addTool|registerTool|server\.tool)\s*\(\s*["\']([^"\']+)["\']',
                content,
            )
            tools.extend(tool_matches)
        except (OSError, UnicodeDecodeError):
            continue

    return tools


def _read_pytest_markers(project_path: Path) -> List[str]:
    """
    Read pytest markers from pyproject.toml if available.

    Args:
        project_path: Project root directory

    Returns:
        List of marker names, or empty list
    """
    pyproject = project_path / "pyproject.toml"
    if not pyproject.exists():
        return []

    content = pyproject.read_text(encoding="utf-8")
    markers: List[str] = []

    # Look for [tool.pytest.ini_options] markers
    marker_pattern = re.compile(r'^\s+"([a-z_]+):', re.MULTILINE)
    in_markers = False
    for line in content.splitlines():
        stripped = line.strip()
        if "markers" in stripped and "=" in stripped:
            in_markers = True
            continue
        if in_markers:
            if stripped.startswith("]"):
                break
            m = re.match(r'^"([a-z_]+)\s*:', stripped)
            if m:
                markers.append(m.group(1))

    return markers


# ─── Template Rendering ─────────────────────────────────────────────────────


def render_templates(
    project_path: Path,
    project_type: str,
    variables: Dict[str, Any],
) -> List[Tuple[str, str]]:
    """
    Render Jinja2 templates for the given project type.

    Uses dual template paths so that type-specific templates can include
    shared base templates via {% include '_base/...' %}.

    Args:
        project_path: Project root (used for context, not template loading)
        project_type: One of "plugin", "zsh", "cli", "mcp"
        variables: Template variables from gather_variables()

    Returns:
        List of (filename, rendered_content) tuples

    Raises:
        ImportError: If jinja2 is not installed
        ValueError: If project_type is not recognized
    """
    if Environment is None or FileSystemLoader is None:
        raise ImportError(
            "jinja2 is required for template rendering. "
            "Install it with: pip install jinja2"
        )

    if project_type not in VALID_TYPES:
        raise ValueError(f"Unknown project type: {project_type}")

    registry = _load_registry()
    type_config = registry["types"][project_type]
    template_names = type_config.get("templates", [])

    # Dual loader: type-specific directory first, then templates root for _base/
    type_dir = TEMPLATES_DIR / project_type
    loader = FileSystemLoader([str(type_dir), str(TEMPLATES_DIR)])
    env = Environment(
        loader=loader,
        keep_trailing_newline=True,
        trim_blocks=True,
        lstrip_blocks=True,
    )

    rendered_files: List[Tuple[str, str]] = []

    for template_name in template_names:
        try:
            template = env.get_template(template_name)
            content = template.render(**variables)
            # Output filename: strip .j2 suffix
            output_name = template_name.removesuffix(".j2")
            rendered_files.append((output_name, content))
        except Exception as exc:
            # Log but don't crash — skip templates that fail
            rendered_files.append((
                template_name.removesuffix(".j2"),
                f"# ERROR: Failed to render {template_name}: {exc}\n",
            ))

    # Also render shared helpers template
    shared_templates = registry.get("shared", {}).get("templates", [])
    for shared_name in shared_templates:
        try:
            template = env.get_template(shared_name)
            content = template.render(**variables)
            output_name = Path(shared_name).name.removesuffix(".j2")
            rendered_files.append((output_name, content))
        except Exception:
            # Shared templates are optional — skip silently if missing
            pass

    return rendered_files


# ─── Main Entry Point ───────────────────────────────────────────────────────


def generate_tests(
    project_path: Path,
    project_type: Optional[str] = None,
    output_dir: Optional[Path] = None,
    dry_run: bool = False,
) -> Dict[str, Any]:
    """
    Generate test files for a project.

    This is the main entry point. It detects the project type (if not given),
    gathers variables, renders templates, and writes output files.

    Args:
        project_path: Root directory of the project
        project_type: Override auto-detection with explicit type
        output_dir: Output directory (default: project_path/tests/)
        dry_run: If True, return what would be generated without writing

    Returns:
        Dictionary with keys:
            - project_type: Detected or specified project type
            - variables: Gathered template variables
            - files: List of (filename, content) tuples
            - output_dir: Path where files were/would be written
            - written: Number of files written (0 in dry-run mode)
            - skipped: Number of files skipped (already exist)

    Raises:
        ValueError: If project type cannot be detected
        ImportError: If jinja2 is not installed
    """
    project_path = Path(project_path).resolve()

    # Step 1: Detect project type
    if project_type is None:
        project_type = detect_project_type(project_path)
    elif project_type not in VALID_TYPES:
        raise ValueError(
            f"Invalid project type: {project_type}. "
            f"Must be one of: {', '.join(VALID_TYPES)}"
        )

    # Step 2: Gather variables
    variables = gather_variables(project_path, project_type)

    # Step 3: Render templates
    rendered_files = render_templates(project_path, project_type, variables)

    # Step 4: Determine output directory
    if output_dir is None:
        output_dir = project_path / variables.get("test_dir", "tests")
    else:
        output_dir = Path(output_dir).resolve()

    # Step 5: Write or preview
    written = 0
    skipped = 0

    if not dry_run:
        output_dir.mkdir(parents=True, exist_ok=True)

        for filename, content in rendered_files:
            target = output_dir / filename
            if target.exists():
                skipped += 1
                continue
            target.write_text(content, encoding="utf-8")
            written += 1

    return {
        "project_type": project_type,
        "variables": variables,
        "files": rendered_files,
        "output_dir": str(output_dir),
        "written": written,
        "skipped": skipped,
    }


# ─── CLI Entry Point ────────────────────────────────────────────────────────

if __name__ == "__main__":
    import sys

    # Simple CLI for testing
    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    is_dry_run = "--dry-run" in sys.argv

    try:
        result = generate_tests(path, dry_run=is_dry_run)
    except (ValueError, ImportError) as exc:
        print(f"Error: {exc}", file=sys.stderr)
        sys.exit(1)

    print(f"Project type: {result['project_type']}")
    print(f"Output dir:   {result['output_dir']}")
    print(f"Files:        {len(result['files'])}")

    if is_dry_run:
        print("\nDry-run — files that would be generated:")
        for filename, content in result["files"]:
            line_count = content.count("\n")
            print(f"  {filename} ({line_count} lines)")
    else:
        print(f"\nWritten: {result['written']}, Skipped: {result['skipped']}")
