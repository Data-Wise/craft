#!/usr/bin/env python3
"""
CLAUDE.md Project Type Detector

Detects craft-specific project types for CLAUDE.md generation/updating.
Integrates with existing project-detector skill patterns.

Version: 1.0.0
Author: Craft Plugin
"""

import json
from dataclasses import dataclass
from pathlib import Path
from typing import Optional, Dict, List, Any


@dataclass
class ProjectInfo:
    """Detected project information for CLAUDE.md generation."""
    type: str              # craft-plugin, teaching-site, r-package, mcp-server, generic
    version: str           # Extracted from version source
    version_source: str    # plugin.json, package.json, pyproject.toml, DESCRIPTION
    name: str              # Project name
    commands: List[str]    # Discovered commands (for plugins)
    skills: List[str]      # Discovered skills (for plugins)
    agents: List[str]      # Discovered agents (for plugins)
    test_count: int        # Number of tests
    structure: Dict[str, Any]  # Project-specific structure info


class CLAUDEMDDetector:
    """Project type detector for CLAUDE.md workflows."""

    def __init__(self, path: Path = None):
        """Initialize detector.

        Args:
            path: Project directory path (default: current directory)
        """
        self.path = Path(path) if path else Path.cwd()

    def detect(self) -> Optional[ProjectInfo]:
        """Detect project type and gather information.

        Returns:
            ProjectInfo if project type detected, None otherwise
        """
        # Priority 1: Craft Plugin
        if info := self._detect_craft_plugin():
            return info

        # Priority 2: Teaching Site
        if info := self._detect_teaching_site():
            return info

        # Priority 3: R Package
        if info := self._detect_r_package():
            return info

        # Priority 4: MCP Server
        if info := self._detect_mcp_server():
            return info

        # Priority 5: Generic fallback (detect from package.json/pyproject.toml)
        if info := self._detect_generic():
            return info

        return None

    def _detect_craft_plugin(self) -> Optional[ProjectInfo]:
        """Detect craft plugin project.

        Markers:
        - .claude-plugin/plugin.json exists
        - commands/ directory exists

        Returns:
            ProjectInfo for craft plugin, or None
        """
        plugin_json = self.path / ".claude-plugin" / "plugin.json"
        if not plugin_json.exists():
            return None

        try:
            data = json.loads(plugin_json.read_text())
        except (json.JSONDecodeError, OSError):
            return None

        # Scan for commands, skills, agents
        commands = self._scan_commands()
        skills = self._scan_skills()
        agents = self._scan_agents()
        test_count = self._count_tests()

        return ProjectInfo(
            type="craft-plugin",
            version=data.get("version", "0.0.0"),
            version_source="plugin.json",
            name=data.get("name", self.path.name),
            commands=commands,
            skills=skills,
            agents=agents,
            test_count=test_count,
            structure={
                "has_commands": len(commands) > 0,
                "has_skills": len(skills) > 0,
                "has_agents": len(agents) > 0,
                "repository": data.get("repository", {}),
            }
        )

    def _detect_teaching_site(self) -> Optional[ProjectInfo]:
        """Detect teaching site (Quarto course).

        Markers:
        - _quarto.yml exists
        - course.yml OR weeks/ directory exists

        Returns:
            ProjectInfo for teaching site, or None
        """
        quarto_yml = self.path / "_quarto.yml"
        course_yml = self.path / "course.yml"
        weeks_dir = self.path / "weeks"

        if not quarto_yml.exists():
            return None

        # Must have either course.yml or weeks/ directory
        if not (course_yml.exists() or weeks_dir.exists()):
            return None

        # Try to extract course info from _quarto.yml
        version = "1.0.0"  # Default for teaching sites
        name = self.path.name

        try:
            import yaml
            quarto_data = yaml.safe_load(quarto_yml.read_text())
            name = quarto_data.get("project", {}).get("title", name)
        except Exception:
            pass

        # Scan for weeks
        weeks = []
        if weeks_dir.exists():
            weeks = [w.name for w in weeks_dir.iterdir() if w.is_dir()]

        return ProjectInfo(
            type="teaching-site",
            version=version,
            version_source="_quarto.yml",
            name=name,
            commands=[],
            skills=[],
            agents=[],
            test_count=0,
            structure={
                "weeks": weeks,
                "has_course_yml": course_yml.exists(),
            }
        )

    def _detect_r_package(self) -> Optional[ProjectInfo]:
        """Detect R package.

        Markers:
        - DESCRIPTION file exists
        - Contains "Package:" field

        Returns:
            ProjectInfo for R package, or None
        """
        description = self.path / "DESCRIPTION"
        if not description.exists():
            return None

        try:
            content = description.read_text()
        except OSError:
            return None

        # Must contain Package: field
        if "Package:" not in content:
            return None

        # Parse DESCRIPTION
        name = "unknown"
        version = "0.0.0"

        for line in content.split("\n"):
            if line.startswith("Package:"):
                name = line.split(":", 1)[1].strip()
            elif line.startswith("Version:"):
                version = line.split(":", 1)[1].strip()

        # Count tests (testthat convention)
        test_count = 0
        testthat_dir = self.path / "tests" / "testthat"
        if testthat_dir.exists():
            test_count = len(list(testthat_dir.glob("test-*.R")))

        return ProjectInfo(
            type="r-package",
            version=version,
            version_source="DESCRIPTION",
            name=name,
            commands=[],
            skills=[],
            agents=[],
            test_count=test_count,
            structure={
                "has_namespace": (self.path / "NAMESPACE").exists(),
                "has_tests": testthat_dir.exists(),
                "has_pkgdown": (self.path / "_pkgdown.yml").exists(),
            }
        )

    def _detect_mcp_server(self) -> Optional[ProjectInfo]:
        """Detect MCP (Model Context Protocol) server.

        Markers:
        - package.json exists
        - Name contains "mcp" OR has @modelcontextprotocol dependency

        Returns:
            ProjectInfo for MCP server, or None
        """
        pkg_json = self.path / "package.json"
        if not pkg_json.exists():
            return None

        try:
            data = json.loads(pkg_json.read_text())
        except (json.JSONDecodeError, OSError):
            return None

        name = data.get("name", "").lower()

        # Check if name contains mcp
        is_mcp = "mcp" in name

        # Check for MCP dependencies
        if not is_mcp:
            deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
            is_mcp = "@modelcontextprotocol/sdk" in deps or any("mcp" in dep.lower() for dep in deps)

        if not is_mcp:
            return None

        version = data.get("version", "0.0.0")
        test_count = self._count_tests()

        return ProjectInfo(
            type="mcp-server",
            version=version,
            version_source="package.json",
            name=data.get("name", self.path.name),
            commands=[],
            skills=[],
            agents=[],
            test_count=test_count,
            structure={
                "has_src": (self.path / "src").exists(),
                "main": data.get("main", ""),
                "bin": data.get("bin", {}),
            }
        )

    def _detect_generic(self) -> Optional[ProjectInfo]:
        """Detect generic project from common markers.

        Checks for:
        - package.json (Node.js)
        - pyproject.toml (Python)

        Returns:
            ProjectInfo for generic project, or None
        """
        # Try package.json
        pkg_json = self.path / "package.json"
        if pkg_json.exists():
            try:
                data = json.loads(pkg_json.read_text())
                return ProjectInfo(
                    type="generic-node",
                    version=data.get("version", "0.0.0"),
                    version_source="package.json",
                    name=data.get("name", self.path.name),
                    commands=[],
                    skills=[],
                    agents=[],
                    test_count=self._count_tests(),
                    structure={}
                )
            except (json.JSONDecodeError, OSError):
                pass

        # Try pyproject.toml
        pyproject = self.path / "pyproject.toml"
        if pyproject.exists():
            try:
                import tomllib
                data = tomllib.loads(pyproject.read_text())
                project_data = data.get("project", {})
                return ProjectInfo(
                    type="generic-python",
                    version=project_data.get("version", "0.0.0"),
                    version_source="pyproject.toml",
                    name=project_data.get("name", self.path.name),
                    commands=[],
                    skills=[],
                    agents=[],
                    test_count=self._count_tests(),
                    structure={}
                )
            except Exception:
                pass

        return None

    def _scan_commands(self) -> List[str]:
        """Scan commands/ directory for craft commands.

        Returns:
            List of command paths (e.g., ["docs/update.md", "check.md"])
        """
        commands_dir = self.path / "commands"
        if not commands_dir.exists():
            return []

        commands = []
        for cmd_file in commands_dir.rglob("*.md"):
            # Relative path from commands/
            rel_path = cmd_file.relative_to(commands_dir)
            commands.append(str(rel_path))

        return sorted(commands)

    def _scan_skills(self) -> List[str]:
        """Scan skills/ directory for craft skills.

        Returns:
            List of skill paths (e.g., ["ci/detect.md", "docs/sync.md"])
        """
        skills_dir = self.path / "skills"
        if not skills_dir.exists():
            return []

        skills = []
        for skill_file in skills_dir.rglob("*.md"):
            # Relative path from skills/
            rel_path = skill_file.relative_to(skills_dir)
            skills.append(str(rel_path))

        return sorted(skills)

    def _scan_agents(self) -> List[str]:
        """Scan agents/ directory for craft agents.

        Returns:
            List of agent paths (e.g., ["orchestrator.md", "docs-architect.md"])
        """
        agents_dir = self.path / "agents"
        if not agents_dir.exists():
            return []

        agents = []
        for agent_file in agents_dir.rglob("*.md"):
            # Relative path from agents/
            rel_path = agent_file.relative_to(agents_dir)
            agents.append(str(rel_path))

        return sorted(agents)

    def _count_tests(self) -> int:
        """Count test files in project.

        Returns:
            Number of test files found
        """
        tests_dir = self.path / "tests"
        if not tests_dir.exists():
            return 0

        # Python tests
        py_tests = list(tests_dir.glob("test_*.py"))

        # JavaScript tests
        js_tests = list(tests_dir.glob("*.test.js")) + list(tests_dir.glob("*.test.ts"))

        # R tests
        r_tests = list((tests_dir / "testthat").glob("test-*.R")) if (tests_dir / "testthat").exists() else []

        return len(py_tests) + len(js_tests) + len(r_tests)

    def get_version_from_source(self, source: str) -> str:
        """Extract version from specified source file.

        Args:
            source: Source file to read (plugin.json, package.json, pyproject.toml, DESCRIPTION)

        Returns:
            Version string, or "0.0.0" if not found
        """
        if source == "plugin.json":
            file_path = self.path / ".claude-plugin" / "plugin.json"
            if file_path.exists():
                try:
                    data = json.loads(file_path.read_text())
                    return data.get("version", "0.0.0")
                except Exception:
                    pass

        elif source == "package.json":
            file_path = self.path / "package.json"
            if file_path.exists():
                try:
                    data = json.loads(file_path.read_text())
                    return data.get("version", "0.0.0")
                except Exception:
                    pass

        elif source == "pyproject.toml":
            file_path = self.path / "pyproject.toml"
            if file_path.exists():
                try:
                    import tomllib
                    data = tomllib.loads(file_path.read_text())
                    return data.get("project", {}).get("version", "0.0.0")
                except Exception:
                    pass

        elif source == "DESCRIPTION":
            file_path = self.path / "DESCRIPTION"
            if file_path.exists():
                try:
                    content = file_path.read_text()
                    for line in content.split("\n"):
                        if line.startswith("Version:"):
                            return line.split(":", 1)[1].strip()
                except Exception:
                    pass

        return "0.0.0"


def detect_project(path: Path = None) -> Optional[ProjectInfo]:
    """Convenience function to detect project type.

    Args:
        path: Project directory (default: current directory)

    Returns:
        ProjectInfo if detected, None otherwise
    """
    detector = CLAUDEMDDetector(path)
    return detector.detect()


if __name__ == "__main__":
    # CLI usage for testing
    import sys

    path = Path(sys.argv[1]) if len(sys.argv) > 1 else Path.cwd()
    info = detect_project(path)

    if info:
        print(f"Project Type: {info.type}")
        print(f"Name: {info.name}")
        print(f"Version: {info.version} (from {info.version_source})")
        if info.commands:
            print(f"Commands: {len(info.commands)}")
        if info.skills:
            print(f"Skills: {len(info.skills)}")
        if info.agents:
            print(f"Agents: {len(info.agents)}")
        if info.test_count:
            print(f"Tests: {info.test_count}")
    else:
        print("Could not detect project type")
        sys.exit(1)
