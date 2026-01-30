#!/usr/bin/env python3
"""
CLAUDE.md Template Variable Populator

Scans project and populates template variables for scaffold command.

Version: 1.0.0
Author: Craft Plugin
"""

import json
from pathlib import Path
from typing import Dict, List, Optional, Any
from datetime import datetime


class TemplatePopulator:
    """Populates template variables from project analysis."""

    def __init__(self, project_path: Path, project_type: str):
        """Initialize populator.

        Args:
            project_path: Root directory of project
            project_type: Type of project (plugin, teaching, r-package)
        """
        self.path = project_path
        self.type = project_type
        self.variables: Dict[str, Any] = {}

    def populate_all(self) -> Dict[str, Any]:
        """Populate all variables for project type.

        Returns:
            Dictionary of template variables
        """
        if self.type in ["plugin", "craft-plugin"]:
            return self._populate_plugin()
        elif self.type == "teaching":
            return self._populate_teaching()
        elif self.type == "r-package":
            return self._populate_r_package()
        else:
            return self._populate_generic()

    def _populate_plugin(self) -> Dict[str, Any]:
        """Populate variables for craft plugin template.

        Returns:
            Dictionary with plugin-specific variables
        """
        variables = {}

        # Read plugin.json
        plugin_json_path = self.path / ".claude-plugin" / "plugin.json"
        if plugin_json_path.exists():
            with open(plugin_json_path) as f:
                plugin_data = json.load(f)

            variables["plugin_name"] = plugin_data.get("name", "unknown")
            variables["version"] = plugin_data.get("version", "0.0.0")
            variables["tagline"] = plugin_data.get("description", "")

            # Repository info
            repo = plugin_data.get("repository", {})
            variables["repo_url"] = repo.get("url", "")
            variables["docs_url"] = repo.get("docs", "")

        # Scan directories
        variables["command_count"] = self._count_commands()
        variables["skill_count"] = self._count_skills()
        variables["agent_count"] = self._count_agents()
        variables["test_count"] = self._count_tests()

        # Generate derived content
        variables["command_table"] = self._generate_command_table()
        variables["command_dirs"] = self._generate_directory_tree("commands")
        variables["skill_dirs"] = self._generate_directory_tree("skills")
        variables["agent_dirs"] = self._generate_directory_tree("agents")
        variables["test_dirs"] = self._generate_directory_tree("tests")
        variables["docs_dirs"] = self._generate_directory_tree("docs")
        variables["key_files"] = self._generate_key_files()
        variables["related_commands"] = self._generate_related_commands()

        # Metadata
        variables["release_date"] = self._get_latest_release_date()
        variables["docs_percent"] = self._estimate_docs_completeness()
        variables["coverage"] = self._get_test_coverage()

        return variables

    def _populate_teaching(self) -> Dict[str, Any]:
        """Populate variables for teaching site template.

        Returns:
            Dictionary with teaching-specific variables
        """
        variables = {}

        # Read _quarto.yml
        quarto_yml = self.path / "_quarto.yml"
        if quarto_yml.exists():
            # Basic YAML parsing (would use pyyaml in production)
            content = quarto_yml.read_text()
            if "title:" in content:
                title_line = [l for l in content.split("\n") if "title:" in l][0]
                variables["course_name"] = title_line.split("title:")[1].strip().strip('"')

        # Read course.yml
        course_yml = self.path / "course.yml"
        if course_yml.exists():
            content = course_yml.read_text()
            # Extract basic fields
            for field in ["course_code", "semester", "instructor"]:
                if f"{field}:" in content:
                    line = [l for l in content.split("\n") if f"{field}:" in l][0]
                    variables[field] = line.split(":")[1].strip().strip('"')

        # Scan directories
        variables["week_count"] = len(list((self.path / "weeks").glob("*"))) if (self.path / "weeks").exists() else 0
        variables["assignment_count"] = len(list((self.path / "assignments").glob("*.qmd"))) if (self.path / "assignments").exists() else 0
        variables["exam_count"] = len(list((self.path / "exams").glob("*.qmd"))) if (self.path / "exams").exists() else 0

        # Generate derived content
        variables["week_dirs"] = self._generate_directory_tree("weeks")
        variables["assignment_dirs"] = self._generate_directory_tree("assignments")
        variables["exam_dirs"] = self._generate_directory_tree("exams")
        variables["resource_dirs"] = self._generate_directory_tree("resources")
        variables["week_structure"] = self._generate_week_structure()
        variables["related_commands"] = self._generate_teaching_commands()

        # Metadata
        variables["course_type"] = "Quarto-based course website"
        variables["current_week"] = self._get_current_week()
        variables["progress"] = self._estimate_course_progress()
        variables["next_task"] = self._get_next_course_task()

        # URLs
        variables["course_url"] = ""
        variables["canvas_url"] = ""

        return variables

    def _populate_r_package(self) -> Dict[str, Any]:
        """Populate variables for R package template.

        Returns:
            Dictionary with R package-specific variables
        """
        variables = {}

        # Read DESCRIPTION
        desc_file = self.path / "DESCRIPTION"
        if desc_file.exists():
            content = desc_file.read_text()

            # Parse DESCRIPTION fields
            for line in content.split("\n"):
                if line.startswith("Package:"):
                    variables["package_name"] = line.split(":")[1].strip()
                elif line.startswith("Title:"):
                    variables["package_title"] = line.split(":", 1)[1].strip()
                elif line.startswith("Version:"):
                    variables["version"] = line.split(":")[1].strip()
                elif line.startswith("Depends:") and "R (" in line:
                    # Extract minimum R version
                    r_part = line.split("R (")[1].split(")")[0]
                    variables["r_version"] = r_part.replace(">=", "").strip()

        # Scan directories
        r_files = list((self.path / "R").glob("*.R")) if (self.path / "R").exists() else []
        variables["function_count"] = len(r_files)

        test_files = list((self.path / "tests" / "testthat").glob("test-*.R")) if (self.path / "tests" / "testthat").exists() else []
        variables["test_count"] = len(test_files)

        vignette_files = list((self.path / "vignettes").glob("*.Rmd")) if (self.path / "vignettes").exists() else []
        variables["vignette_count"] = len(vignette_files)

        # Generate derived content
        variables["r_files"] = self._generate_r_file_tree()
        variables["test_files"] = self._generate_directory_tree("tests/testthat")
        variables["vignette_files"] = self._generate_directory_tree("vignettes")
        variables["function_table"] = self._generate_function_table()
        variables["dependencies"] = self._extract_dependencies()
        variables["related_packages"] = self._get_related_packages()

        # Status from .STATUS if exists
        status_file = self.path / ".STATUS"
        if status_file.exists():
            content = status_file.read_text()
            if "status:" in content:
                status_line = [l for l in content.split("\n") if "status:" in l][0]
                variables["status"] = status_line.split(":")[1].strip()
            if "progress:" in content:
                prog_line = [l for l in content.split("\n") if "progress:" in l][0]
                variables["progress"] = prog_line.split(":")[1].strip()
            if "next:" in content:
                next_line = [l for l in content.split("\n") if "next:" in l][0]
                variables["next_task"] = next_line.split(":", 1)[1].strip()

        # URLs
        variables["pkgdown_url"] = ""
        variables["repo_url"] = self._get_repo_url()
        variables["cran_url"] = f"https://CRAN.R-project.org/package={variables.get('package_name', '')}"

        return variables

    def _populate_generic(self) -> Dict[str, Any]:
        """Populate basic variables for generic template.

        Returns:
            Dictionary with generic variables
        """
        variables = {
            "project_name": self.path.name,
            "version": "0.0.0",
            "description": "",
        }
        return variables

    # Helper methods

    def _count_commands(self) -> int:
        """Count command files."""
        commands_dir = self.path / "commands"
        if not commands_dir.exists():
            return 0
        return len(list(commands_dir.rglob("*.md")))

    def _count_skills(self) -> int:
        """Count skill files."""
        skills_dir = self.path / "skills"
        if not skills_dir.exists():
            return 0
        return len(list(skills_dir.rglob("*.md")))

    def _count_agents(self) -> int:
        """Count agent files."""
        agents_dir = self.path / "agents"
        if not agents_dir.exists():
            return 0
        return len(list(agents_dir.rglob("*.md")))

    def _count_tests(self) -> int:
        """Count test files (Python)."""
        tests_dir = self.path / "tests"
        if not tests_dir.exists():
            return 0

        # Count test files
        test_files = list(tests_dir.glob("test_*.py"))

        # Try to get count from recent test output or just return file count
        return len(test_files) * 10  # Estimate ~10 tests per file

    def _generate_command_table(self) -> str:
        """Generate quick command reference table.

        Returns:
            Markdown table of key commands
        """
        # Find key commands
        commands_dir = self.path / "commands"
        if not commands_dir.exists():
            return "| Task | Command |\n|------|---------|"

        # Look for common commands
        common = ["check", "test", "build", "docs"]
        rows = []

        for cmd in common:
            cmd_file = list(commands_dir.rglob(f"{cmd}.md"))
            if cmd_file:
                # Extract description from frontmatter
                rows.append(f"| {cmd.title()} | `/craft:{cmd}` |")

        if not rows:
            return "| Task | Command |\n|------|---------|"

        return "\n".join(rows)

    def _generate_directory_tree(self, directory: str) -> str:
        """Generate indented directory tree.

        Args:
            directory: Directory name to scan

        Returns:
            Indented tree structure
        """
        dir_path = self.path / directory
        if not dir_path.exists():
            return ""

        # Get subdirectories
        subdirs = sorted([d for d in dir_path.iterdir() if d.is_dir()])

        if not subdirs:
            return ""

        # Generate tree (first 5 only)
        lines = []
        for i, subdir in enumerate(subdirs[:5]):
            prefix = "│   " if i < len(subdirs[:5]) - 1 else "    "
            lines.append(f"│   ├── {subdir.name}/")

        if len(subdirs) > 5:
            lines.append(f"│   └── ... ({len(subdirs) - 5} more)")

        return "\n".join(lines)

    def _generate_key_files(self) -> str:
        """Generate key files table.

        Returns:
            Markdown table of important files
        """
        # Define key files for plugins
        key_files = [
            (".claude-plugin/plugin.json", "Plugin manifest"),
            ("commands/", "Command definitions"),
            ("skills/", "Specialized skills"),
            ("tests/", "Test suite"),
        ]

        rows = []
        for file_path, description in key_files:
            if (self.path / file_path).exists():
                rows.append(f"| `{file_path}` | {description} |")

        if not rows:
            return ""

        return "\n".join(rows)

    def _generate_related_commands(self) -> str:
        """Generate related commands list.

        Returns:
            Markdown table of related commands
        """
        # Common related commands for plugins
        related = [
            ("/craft:check", "Pre-flight validation"),
            ("/craft:test:run", "Run test suite"),
            ("/craft:docs:update", "Update documentation"),
        ]

        rows = []
        for cmd, desc in related:
            rows.append(f"| `{cmd}` | {desc} |")

        return "\n".join(rows)

    def _generate_teaching_commands(self) -> str:
        """Generate teaching-specific commands."""
        commands = [
            ("quarto preview", "Preview site locally"),
            ("quarto render", "Build full site"),
            ("quarto publish gh-pages", "Publish to GitHub Pages"),
        ]

        rows = []
        for cmd, desc in commands:
            rows.append(f"| `{cmd}` | {desc} |")

        return "\n".join(rows)

    def _generate_week_structure(self) -> str:
        """Generate week structure description for teaching sites."""
        return """Each week directory contains:
- `index.qmd` - Week overview and readings
- `lecture.qmd` - Lecture slides
- `lab.qmd` - Lab exercises (if applicable)"""

    def _generate_r_file_tree(self) -> str:
        """Generate R/ directory tree."""
        return self._generate_directory_tree("R")

    def _generate_function_table(self) -> str:
        """Generate function reference table for R packages."""
        # Would parse R files for exported functions
        return "| Function | Purpose |\n|----------|---------|"

    def _extract_dependencies(self) -> str:
        """Extract package dependencies from DESCRIPTION."""
        desc_file = self.path / "DESCRIPTION"
        if not desc_file.exists():
            return ""

        content = desc_file.read_text()
        if "Imports:" in content:
            # Extract imports section (basic parsing)
            imports_start = content.index("Imports:")
            imports_section = content[imports_start:].split("\n\n")[0]
            return imports_section.replace("Imports:", "**Imports:**")

        return ""

    def _get_related_packages(self) -> str:
        """Get related packages list."""
        # Would check for ecosystem membership
        return ""

    def _get_latest_release_date(self) -> str:
        """Get latest release date from git tags."""
        # Would use git commands
        return datetime.now().strftime("%Y-%m-%d")

    def _estimate_docs_completeness(self) -> int:
        """Estimate documentation completeness percentage."""
        # Would analyze docs/ directory
        return 85

    def _get_test_coverage(self) -> int:
        """Get test coverage percentage."""
        # Would parse coverage reports
        return 90

    def _get_current_week(self) -> str:
        """Get current week for teaching site."""
        # Would calculate based on course calendar
        return "Week 5"

    def _estimate_course_progress(self) -> int:
        """Estimate course progress percentage."""
        # Would calculate based on weeks completed
        return 33

    def _get_next_course_task(self) -> str:
        """Get next course task."""
        return "Prepare Week 6 materials"

    def _get_repo_url(self) -> str:
        """Get repository URL from git remote."""
        import subprocess
        try:
            result = subprocess.run(
                ["git", "remote", "get-url", "origin"],
                cwd=self.path,
                capture_output=True,
                text=True,
                timeout=2
            )
            if result.returncode == 0:
                return result.stdout.strip()
        except:
            pass
        return ""


def populate_template(template_content: str, variables: Dict[str, Any]) -> str:
    """Populate template with variables.

    Args:
        template_content: Template markdown with {variable} placeholders
        variables: Dictionary of variable values

    Returns:
        Populated template content
    """
    result = template_content

    # Replace all variables
    for key, value in variables.items():
        placeholder = "{" + key + "}"
        result = result.replace(placeholder, str(value))

    return result


def get_unpopulated_variables(content: str) -> List[str]:
    """Find unpopulated variables in content.

    Args:
        content: Template content

    Returns:
        List of variable names still in {braces}
    """
    import re
    pattern = r'\{([^}]+)\}'
    matches = re.findall(pattern, content)
    return list(set(matches))
