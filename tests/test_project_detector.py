#!/usr/bin/env python3
"""
Tests for the project-detector skill.

Tests the detection logic for various project types including:
- Python (uv, poetry, pip)
- Node.js (npm, pnpm, yarn)
- R packages and Quarto
- Rust, Go, Java
- Claude plugins
"""

import json
import tempfile
import unittest
from pathlib import Path
from dataclasses import dataclass
from typing import Optional


# ============================================================================
# Implementation (extracted from skill for testing)
# ============================================================================

@dataclass
class ProjectInfo:
    """Detected project information."""
    type: str
    variant: str
    test_framework: str
    build_tool: str
    ci_template: str
    python_versions: list
    node_versions: list
    has_docs: bool
    has_ci: bool


DETECTORS = [
    ("plugin", "claude", [".claude-plugin/plugin.json"], []),
    ("r", "package", ["DESCRIPTION", "NAMESPACE"], ["R/", "tests/"]),
    ("r", "quarto", ["_quarto.yml"], []),
    ("python", "uv", ["pyproject.toml", "uv.lock"], ["src/"]),
    ("python", "poetry", ["pyproject.toml", "poetry.lock"], ["src/"]),
    ("python", "pip", ["pyproject.toml"], ["requirements.txt"]),
    ("python", "setuptools", ["setup.py"], ["setup.cfg"]),
    ("node", "pnpm", ["package.json", "pnpm-lock.yaml"], []),
    ("node", "yarn", ["package.json", "yarn.lock"], []),
    ("node", "npm", ["package.json"], ["package-lock.json"]),
    ("rust", "cargo", ["Cargo.toml"], ["Cargo.lock"]),
    ("go", "mod", ["go.mod"], ["go.sum"]),
]


def detect_project(path: Path) -> Optional[ProjectInfo]:
    """Detect project type from directory contents."""
    for proj_type, variant, required, optional in DETECTORS:
        if all((path / f).exists() for f in required):
            return ProjectInfo(
                type=proj_type,
                variant=variant,
                test_framework=detect_test_framework(path, proj_type),
                build_tool=variant,
                ci_template=f"{proj_type}-{variant}",
                python_versions=detect_python_versions(path) if proj_type == "python" else [],
                node_versions=detect_node_versions(path) if proj_type == "node" else [],
                has_docs=any(detect_docs(path).values()),
                has_ci=(path / ".github/workflows").exists(),
            )
    return None


def detect_test_framework(path: Path, proj_type: str) -> str:
    """Detect test framework based on project type."""
    if proj_type == "python":
        return detect_python_test_framework(path)
    elif proj_type == "node":
        return detect_node_test_framework(path)
    elif proj_type == "r":
        return detect_r_test_framework(path)
    elif proj_type == "rust":
        return "cargo test"
    elif proj_type == "go":
        return "go test"
    return "unknown"


def detect_python_test_framework(path: Path) -> str:
    """Detect Python test framework."""
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if "pytest" in content:
            return "pytest"
        if "unittest" in content:
            return "unittest"

    if (path / "tests").exists():
        test_files = list((path / "tests").glob("test_*.py"))
        if test_files:
            content = test_files[0].read_text()
            if "import pytest" in content or "@pytest" in content:
                return "pytest"
            if "import unittest" in content:
                return "unittest"

    return "pytest"


def detect_node_test_framework(path: Path) -> str:
    """Detect Node.js test framework."""
    pkg = path / "package.json"
    if pkg.exists():
        data = json.loads(pkg.read_text())
        deps = {**data.get("devDependencies", {}), **data.get("dependencies", {})}

        if "vitest" in deps:
            return "vitest"
        if "jest" in deps:
            return "jest"
        if "mocha" in deps:
            return "mocha"
        if "ava" in deps:
            return "ava"

    return "jest"


def detect_r_test_framework(path: Path) -> str:
    """Detect R test framework."""
    desc = path / "DESCRIPTION"
    if desc.exists():
        content = desc.read_text()
        if "testthat" in content:
            return "testthat"
        if "tinytest" in content:
            return "tinytest"

    if (path / "tests/testthat").exists():
        return "testthat"

    return "testthat"


def detect_python_versions(path: Path) -> list:
    """Detect Python version requirements."""
    import re
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            constraint = match.group(1)
            if ">=" in constraint:
                min_ver = constraint.replace(">=", "").strip()
                return get_versions_from(min_ver)

    return ["3.10", "3.11", "3.12"]


def get_versions_from(min_version: str) -> list:
    """Get Python versions >= min_version."""
    all_versions = ["3.9", "3.10", "3.11", "3.12", "3.13"]
    try:
        idx = all_versions.index(min_version)
        return all_versions[idx:]
    except ValueError:
        return ["3.10", "3.11", "3.12"]


def detect_node_versions(path: Path) -> list:
    """Detect Node.js version requirements."""
    return ["18", "20", "22"]


def detect_docs(path: Path) -> dict:
    """Detect documentation setup."""
    return {
        "mkdocs": (path / "mkdocs.yml").exists(),
        "sphinx": (path / "docs/conf.py").exists(),
        "docusaurus": (path / "docusaurus.config.js").exists(),
        "vitepress": (path / ".vitepress").exists(),
        "quarto": (path / "_quarto.yml").exists(),
        "readme": (path / "README.md").exists(),
    }


def has_coverage_config(path: Path) -> bool:
    """Check for coverage configuration."""
    pyproject = path / "pyproject.toml"
    if pyproject.exists() and "coverage" in pyproject.read_text():
        return True
    if (path / ".coveragerc").exists():
        return True
    if (path / "codecov.yml").exists():
        return True
    return False


def has_linting_config(path: Path) -> bool:
    """Check for linting configuration."""
    lint_files = [".eslintrc", ".eslintrc.js", ".eslintrc.json",
                  "ruff.toml", ".ruff.toml", ".flake8", ".pylintrc"]
    return any((path / f).exists() for f in lint_files)


def has_type_checking(path: Path) -> bool:
    """Check for type checking configuration."""
    type_files = ["mypy.ini", ".mypy.ini", "pyrightconfig.json", "tsconfig.json"]
    pyproject = path / "pyproject.toml"
    if pyproject.exists() and "[tool.mypy]" in pyproject.read_text():
        return True
    return any((path / f).exists() for f in type_files)


# ============================================================================
# Test Cases
# ============================================================================

class TestProjectDetection(unittest.TestCase):
    """Test project type detection."""

    def setUp(self):
        """Create temp directory for each test."""
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up temp directory."""
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    # -------------------------------------------------------------------------
    # Python Project Detection
    # -------------------------------------------------------------------------

    def test_detect_python_uv_project(self):
        """Detect Python project with uv."""
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')
        (self.path / "uv.lock").write_text("# uv lockfile")

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "python")
        self.assertEqual(result.variant, "uv")
        self.assertEqual(result.ci_template, "python-uv")

    def test_detect_python_poetry_project(self):
        """Detect Python project with Poetry."""
        (self.path / "pyproject.toml").write_text('[tool.poetry]\nname = "test"')
        (self.path / "poetry.lock").write_text("# poetry lockfile")

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "python")
        self.assertEqual(result.variant, "poetry")

    def test_detect_python_pip_project(self):
        """Detect Python project with pip (pyproject.toml only)."""
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "python")
        self.assertEqual(result.variant, "pip")

    def test_detect_python_setuptools_project(self):
        """Detect Python project with setup.py."""
        (self.path / "setup.py").write_text('from setuptools import setup\nsetup()')

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "python")
        self.assertEqual(result.variant, "setuptools")

    def test_uv_takes_priority_over_pip(self):
        """UV should be detected over plain pip when uv.lock exists."""
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')
        (self.path / "uv.lock").write_text("# lockfile")

        result = detect_project(self.path)

        self.assertEqual(result.variant, "uv")

    # -------------------------------------------------------------------------
    # Node.js Project Detection
    # -------------------------------------------------------------------------

    def test_detect_node_npm_project(self):
        """Detect Node.js project with npm."""
        (self.path / "package.json").write_text('{"name": "test"}')

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "node")
        self.assertEqual(result.variant, "npm")

    def test_detect_node_pnpm_project(self):
        """Detect Node.js project with pnpm."""
        (self.path / "package.json").write_text('{"name": "test"}')
        (self.path / "pnpm-lock.yaml").write_text("# pnpm lockfile")

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "node")
        self.assertEqual(result.variant, "pnpm")

    def test_detect_node_yarn_project(self):
        """Detect Node.js project with yarn."""
        (self.path / "package.json").write_text('{"name": "test"}')
        (self.path / "yarn.lock").write_text("# yarn lockfile")

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "node")
        self.assertEqual(result.variant, "yarn")

    # -------------------------------------------------------------------------
    # R Project Detection
    # -------------------------------------------------------------------------

    def test_detect_r_package(self):
        """Detect R package project."""
        (self.path / "DESCRIPTION").write_text("Package: test\nTitle: Test")
        (self.path / "NAMESPACE").write_text("export(test)")

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "r")
        self.assertEqual(result.variant, "package")

    def test_detect_r_quarto(self):
        """Detect R Quarto project."""
        (self.path / "_quarto.yml").write_text("project:\n  type: book")

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "r")
        self.assertEqual(result.variant, "quarto")

    # -------------------------------------------------------------------------
    # Other Project Types
    # -------------------------------------------------------------------------

    def test_detect_rust_project(self):
        """Detect Rust project."""
        (self.path / "Cargo.toml").write_text('[package]\nname = "test"')

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "rust")
        self.assertEqual(result.variant, "cargo")

    def test_detect_go_project(self):
        """Detect Go project."""
        (self.path / "go.mod").write_text("module test")

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "go")
        self.assertEqual(result.variant, "mod")

    def test_detect_claude_plugin(self):
        """Detect Claude plugin project."""
        (self.path / ".claude-plugin").mkdir()
        (self.path / ".claude-plugin/plugin.json").write_text('{"name": "test"}')

        result = detect_project(self.path)

        self.assertIsNotNone(result)
        self.assertEqual(result.type, "plugin")
        self.assertEqual(result.variant, "claude")

    def test_detect_empty_directory(self):
        """Empty directory returns None."""
        result = detect_project(self.path)
        self.assertIsNone(result)

    # -------------------------------------------------------------------------
    # Priority Tests
    # -------------------------------------------------------------------------

    def test_claude_plugin_highest_priority(self):
        """Claude plugin should be detected first even with other markers."""
        (self.path / ".claude-plugin").mkdir()
        (self.path / ".claude-plugin/plugin.json").write_text('{"name": "test"}')
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')
        (self.path / "package.json").write_text('{"name": "test"}')

        result = detect_project(self.path)

        self.assertEqual(result.type, "plugin")


class TestTestFrameworkDetection(unittest.TestCase):
    """Test test framework detection."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_pytest_from_pyproject(self):
        """Detect pytest from pyproject.toml."""
        (self.path / "pyproject.toml").write_text('[project.optional-dependencies]\ndev = ["pytest"]')

        result = detect_python_test_framework(self.path)

        self.assertEqual(result, "pytest")

    def test_detect_pytest_from_test_file(self):
        """Detect pytest from test file imports."""
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')
        (self.path / "tests").mkdir()
        (self.path / "tests/test_main.py").write_text("import pytest\n\ndef test_something(): pass")

        result = detect_python_test_framework(self.path)

        self.assertEqual(result, "pytest")

    def test_detect_unittest_from_test_file(self):
        """Detect unittest from test file imports."""
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')
        (self.path / "tests").mkdir()
        (self.path / "tests/test_main.py").write_text("import unittest\n\nclass TestMain(unittest.TestCase): pass")

        result = detect_python_test_framework(self.path)

        self.assertEqual(result, "unittest")

    def test_detect_jest_from_package_json(self):
        """Detect Jest from package.json."""
        (self.path / "package.json").write_text('{"devDependencies": {"jest": "^29.0.0"}}')

        result = detect_node_test_framework(self.path)

        self.assertEqual(result, "jest")

    def test_detect_vitest_from_package_json(self):
        """Detect Vitest from package.json."""
        (self.path / "package.json").write_text('{"devDependencies": {"vitest": "^1.0.0"}}')

        result = detect_node_test_framework(self.path)

        self.assertEqual(result, "vitest")

    def test_detect_testthat_from_description(self):
        """Detect testthat from DESCRIPTION."""
        (self.path / "DESCRIPTION").write_text("Package: test\nSuggests: testthat")

        result = detect_r_test_framework(self.path)

        self.assertEqual(result, "testthat")

    def test_detect_testthat_from_directory(self):
        """Detect testthat from tests/testthat directory."""
        (self.path / "tests/testthat").mkdir(parents=True)

        result = detect_r_test_framework(self.path)

        self.assertEqual(result, "testthat")


class TestPythonVersionDetection(unittest.TestCase):
    """Test Python version detection."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_requires_python_310(self):
        """Detect requires-python >= 3.10."""
        (self.path / "pyproject.toml").write_text('requires-python = ">=3.10"')

        result = detect_python_versions(self.path)

        self.assertEqual(result, ["3.10", "3.11", "3.12", "3.13"])

    def test_detect_requires_python_311(self):
        """Detect requires-python >= 3.11."""
        (self.path / "pyproject.toml").write_text('requires-python = ">=3.11"')

        result = detect_python_versions(self.path)

        self.assertEqual(result, ["3.11", "3.12", "3.13"])

    def test_default_versions_when_no_constraint(self):
        """Default to 3.10-3.12 when no constraint."""
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')

        result = detect_python_versions(self.path)

        self.assertEqual(result, ["3.10", "3.11", "3.12"])

    def test_get_versions_from_valid(self):
        """get_versions_from returns correct versions."""
        self.assertEqual(get_versions_from("3.10"), ["3.10", "3.11", "3.12", "3.13"])
        self.assertEqual(get_versions_from("3.12"), ["3.12", "3.13"])

    def test_get_versions_from_invalid(self):
        """get_versions_from handles invalid version."""
        result = get_versions_from("3.99")
        self.assertEqual(result, ["3.10", "3.11", "3.12"])


class TestDocumentationDetection(unittest.TestCase):
    """Test documentation setup detection."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_mkdocs(self):
        """Detect MkDocs documentation."""
        (self.path / "mkdocs.yml").write_text("site_name: Test")

        result = detect_docs(self.path)

        self.assertTrue(result["mkdocs"])
        self.assertFalse(result["sphinx"])

    def test_detect_sphinx(self):
        """Detect Sphinx documentation."""
        (self.path / "docs").mkdir()
        (self.path / "docs/conf.py").write_text("# Sphinx config")

        result = detect_docs(self.path)

        self.assertTrue(result["sphinx"])
        self.assertFalse(result["mkdocs"])

    def test_detect_readme(self):
        """Detect README.md."""
        (self.path / "README.md").write_text("# Project")

        result = detect_docs(self.path)

        self.assertTrue(result["readme"])


class TestCIFeatureDetection(unittest.TestCase):
    """Test CI feature detection."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_detect_coverage_in_pyproject(self):
        """Detect coverage config in pyproject.toml."""
        (self.path / "pyproject.toml").write_text('[tool.coverage.run]\nsource = ["src"]')

        result = has_coverage_config(self.path)

        self.assertTrue(result)

    def test_detect_coveragerc(self):
        """Detect .coveragerc file."""
        (self.path / ".coveragerc").write_text("[run]\nsource = src")

        result = has_coverage_config(self.path)

        self.assertTrue(result)

    def test_detect_codecov_yml(self):
        """Detect codecov.yml file."""
        (self.path / "codecov.yml").write_text("coverage:\n  status: true")

        result = has_coverage_config(self.path)

        self.assertTrue(result)

    def test_detect_ruff_config(self):
        """Detect ruff linting configuration."""
        (self.path / "ruff.toml").write_text('[lint]\nselect = ["E", "W"]')

        result = has_linting_config(self.path)

        self.assertTrue(result)

    def test_detect_eslint_config(self):
        """Detect ESLint configuration."""
        (self.path / ".eslintrc.json").write_text('{"extends": "standard"}')

        result = has_linting_config(self.path)

        self.assertTrue(result)

    def test_detect_mypy_in_pyproject(self):
        """Detect mypy config in pyproject.toml."""
        (self.path / "pyproject.toml").write_text('[tool.mypy]\nstrict = true')

        result = has_type_checking(self.path)

        self.assertTrue(result)

    def test_detect_tsconfig(self):
        """Detect TypeScript configuration."""
        (self.path / "tsconfig.json").write_text('{"compilerOptions": {}}')

        result = has_type_checking(self.path)

        self.assertTrue(result)

    def test_detect_existing_ci(self):
        """Detect existing CI workflows."""
        (self.path / ".github/workflows").mkdir(parents=True)
        (self.path / ".github/workflows/ci.yml").write_text("name: CI")
        (self.path / "pyproject.toml").write_text('[project]\nname = "test"')

        result = detect_project(self.path)

        self.assertTrue(result.has_ci)


class TestIntegration(unittest.TestCase):
    """Integration tests for complete detection flow."""

    def setUp(self):
        self.temp_dir = tempfile.mkdtemp()
        self.path = Path(self.temp_dir)

    def tearDown(self):
        import shutil
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def test_full_python_uv_project(self):
        """Test complete Python/uv project detection."""
        # Create full project structure
        (self.path / "pyproject.toml").write_text('''
[project]
name = "test"
requires-python = ">=3.10"

[project.optional-dependencies]
dev = ["pytest", "pytest-cov", "ruff", "mypy"]

[tool.coverage.run]
source = ["src"]

[tool.mypy]
strict = true
''')
        (self.path / "uv.lock").write_text("# lockfile")
        (self.path / "src/test").mkdir(parents=True)
        (self.path / "tests").mkdir()
        (self.path / "tests/test_main.py").write_text("import pytest\ndef test_main(): pass")
        (self.path / "mkdocs.yml").write_text("site_name: Test")
        (self.path / "README.md").write_text("# Test Project")

        result = detect_project(self.path)

        self.assertEqual(result.type, "python")
        self.assertEqual(result.variant, "uv")
        self.assertEqual(result.test_framework, "pytest")
        self.assertEqual(result.ci_template, "python-uv")
        self.assertIn("3.10", result.python_versions)
        self.assertTrue(result.has_docs)
        self.assertFalse(result.has_ci)

        # Check additional features
        self.assertTrue(has_coverage_config(self.path))
        self.assertTrue(has_type_checking(self.path))

    def test_full_node_project(self):
        """Test complete Node.js project detection."""
        (self.path / "package.json").write_text(json.dumps({
            "name": "test",
            "version": "1.0.0",
            "devDependencies": {
                "vitest": "^1.0.0",
                "eslint": "^8.0.0"
            },
            "engines": {
                "node": ">=18"
            }
        }))
        (self.path / "pnpm-lock.yaml").write_text("# lockfile")
        (self.path / ".eslintrc.json").write_text('{}')
        (self.path / "tsconfig.json").write_text('{}')

        result = detect_project(self.path)

        self.assertEqual(result.type, "node")
        self.assertEqual(result.variant, "pnpm")
        self.assertEqual(result.test_framework, "vitest")
        self.assertTrue(has_linting_config(self.path))
        self.assertTrue(has_type_checking(self.path))


if __name__ == "__main__":
    # Run tests with verbose output
    unittest.main(verbosity=2)
