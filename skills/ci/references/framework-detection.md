# CI Framework Detection — Implementation Reference

Per-language detection functions used by `/craft:ci:detect`. These implement the test framework and project-type detection logic referenced in `SKILL.md`.

## Table of Contents

- [Test Framework Detection](#test-framework-detection)
  - [Python](#python)
  - [Node.js](#nodejs)
  - [R](#r)
  - [Rust](#rust)
  - [Go](#go)
  - [Tauri (Rust + Node hybrid)](#tauri-rust--node-hybrid)
  - [Swift](#swift)
  - [MCP Server](#mcp-server)
  - [Homebrew Tap](#homebrew-tap)
  - [ZSH Plugin](#zsh-plugin)
  - [Emacs Lisp Package](#emacs-lisp-package)
- [Version Detection](#version-detection)
  - [Python Versions](#python-versions)
  - [Node Versions](#node-versions)
- [Documentation Detection](#documentation-detection)
- [CI Feature Detection](#ci-feature-detection)

## Test Framework Detection

### Python

```python
def detect_python_test_framework(path: Path) -> str:
    """Detect Python test framework."""
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()
        if "pytest" in content:
            return "pytest"
        if "unittest" in content:
            return "unittest"

    # Check for test directories
    if (path / "tests").exists():
        test_files = list((path / "tests").glob("test_*.py"))
        if test_files:
            # Check first file for framework hints
            content = test_files[0].read_text()
            if "import pytest" in content or "@pytest" in content:
                return "pytest"
            if "import unittest" in content:
                return "unittest"

    return "pytest"  # Default for Python
```

### Node.js

```python
def detect_node_test_framework(path: Path) -> str:
    """Detect Node.js test framework."""
    pkg = path / "package.json"
    if pkg.exists():
        import json
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

    return "jest"  # Default for Node
```

### R

```python
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

    return "testthat"  # Default for R
```

### Rust

```python
def detect_rust_test_framework(path: Path) -> str:
    """Detect Rust test framework."""
    cargo = path / "Cargo.toml"
    if cargo.exists():
        content = cargo.read_text()

        # Check for test frameworks in dev-dependencies
        if "rstest" in content:
            return "rstest"
        if "proptest" in content:
            return "proptest"
        if "quickcheck" in content:
            return "quickcheck"
        if "criterion" in content:
            return "criterion"  # Benchmarking

    # Check for test modules in src/
    if (path / "src/lib.rs").exists():
        content = (path / "src/lib.rs").read_text()
        if "#[cfg(test)]" in content:
            return "cargo-test"

    # Check for tests/ directory
    if (path / "tests").exists():
        return "cargo-test"

    return "cargo-test"  # Built-in Rust testing
```

### Go

```python
def detect_go_test_framework(path: Path) -> str:
    """Detect Go test framework."""
    # Check for test files
    test_files = list(path.glob("*_test.go"))
    if not test_files and (path / "pkg").exists():
        test_files = list((path / "pkg").rglob("*_test.go"))

    if test_files:
        # Check first test file for framework hints
        content = test_files[0].read_text()

        if "github.com/stretchr/testify" in content:
            return "testify"
        if "github.com/onsi/ginkgo" in content:
            return "ginkgo"
        if "github.com/onsi/gomega" in content:
            return "ginkgo"  # Gomega usually paired with Ginkgo
        if "gocheck" in content or "gopkg.in/check" in content:
            return "gocheck"
        if "goconvey" in content:
            return "goconvey"

    # Check go.mod for test dependencies
    gomod = path / "go.mod"
    if gomod.exists():
        content = gomod.read_text()
        if "testify" in content:
            return "testify"
        if "ginkgo" in content:
            return "ginkgo"

    return "go-test"  # Built-in Go testing
```

### Tauri (Rust + Node hybrid)

```python
def detect_tauri_project(path: Path) -> bool:
    """Detect Tauri desktop app project."""
    return (path / "src-tauri/tauri.conf.json").exists()

def detect_tauri_test_framework(path: Path) -> dict:
    """Detect test frameworks for both Rust and Node sides."""
    result = {"rust": "cargo-test", "node": "vitest"}

    # Check Rust side
    cargo = path / "src-tauri/Cargo.toml"
    if cargo.exists():
        content = cargo.read_text()
        if "rstest" in content:
            result["rust"] = "rstest"

    # Check Node side
    pkg = path / "package.json"
    if pkg.exists():
        content = pkg.read_text()
        if "vitest" in content:
            result["node"] = "vitest"
        elif "jest" in content:
            result["node"] = "jest"

    return result
```

### Swift

```python
def detect_swift_project(path: Path) -> Optional[str]:
    """Detect Swift project type."""
    # Swift Package Manager
    if (path / "Package.swift").exists():
        return "swift-package"

    # Xcode project
    xcodeproj = list(path.glob("*.xcodeproj"))
    if xcodeproj:
        return "swift-xcode"

    # Xcode workspace
    xcworkspace = list(path.glob("*.xcworkspace"))
    if xcworkspace:
        return "swift-xcode"

    return None

def detect_swift_test_framework(path: Path) -> str:
    """Detect Swift test framework."""
    # Check for Quick/Nimble (BDD)
    pkg = path / "Package.swift"
    if pkg.exists():
        content = pkg.read_text()
        if "Quick" in content or "Nimble" in content:
            return "quick-nimble"

    # Check for test targets in Package.swift
    if pkg.exists():
        content = pkg.read_text()
        if ".testTarget" in content:
            return "xctest"

    # Default to XCTest
    return "xctest"
```

### MCP Server

```python
def detect_mcp_server(path: Path) -> bool:
    """Detect MCP (Model Context Protocol) server project."""
    pkg = path / "package.json"
    if pkg.exists():
        import json
        data = json.loads(pkg.read_text())

        # Check name contains mcp
        name = data.get("name", "").lower()
        if "mcp" in name:
            return True

        # Check for @modelcontextprotocol dependency
        deps = {**data.get("dependencies", {}), **data.get("devDependencies", {})}
        if "@modelcontextprotocol/sdk" in deps:
            return True
        if any("mcp" in dep.lower() for dep in deps):
            return True

    return False
```

### Homebrew Tap

```python
def detect_homebrew_tap(path: Path) -> bool:
    """Detect Homebrew tap project."""
    # Check for Formula directory
    if (path / "Formula").exists():
        rb_files = list((path / "Formula").glob("*.rb"))
        if rb_files:
            return True

    # Check for Casks directory
    if (path / "Casks").exists():
        rb_files = list((path / "Casks").glob("*.rb"))
        if rb_files:
            return True

    return False
```

### ZSH Plugin

```python
def detect_zsh_plugin(path: Path) -> bool:
    """Detect ZSH plugin project."""
    # Check for .plugin.zsh file
    plugin_files = list(path.glob("*.plugin.zsh"))
    if plugin_files:
        return True

    # Check for functions directory with .zsh files
    if (path / "functions").exists():
        zsh_files = list((path / "functions").glob("*.zsh"))
        if zsh_files:
            return True

    # Check for antidote/antigen/oh-my-zsh markers
    if (path / ".zsh_plugins.txt").exists():
        return True

    return False
```

### Emacs Lisp Package

```python
def detect_elisp_package(path: Path) -> bool:
    """Detect Emacs Lisp package project."""
    # Check for *-pkg.el file (MELPA convention)
    pkg_files = list(path.glob("*-pkg.el"))
    if pkg_files:
        return True

    # Check for Cask file (dependency management)
    if (path / "Cask").exists():
        return True

    # Check for .el files with ;;;### autoload markers
    el_files = list(path.glob("*.el"))
    for el_file in el_files:
        if ";;;###autoload" in el_file.read_text():
            return True

    return False

def detect_elisp_test_framework(path: Path) -> str:
    """Detect Emacs test framework."""
    # Check for ERT tests
    test_files = list(path.glob("test*.el")) + list(path.glob("*-test.el"))
    for test_file in test_files:
        content = test_file.read_text()
        if "ert-deftest" in content:
            return "ert"
        if "buttercup" in content:
            return "buttercup"

    return "ert"  # Default to ERT
```

## Version Detection

### Python Versions

```python
def detect_python_versions(path: Path) -> list[str]:
    """Detect Python version requirements."""
    pyproject = path / "pyproject.toml"
    if pyproject.exists():
        content = pyproject.read_text()

        # Check requires-python
        import re
        match = re.search(r'requires-python\s*=\s*["\']([^"\']+)["\']', content)
        if match:
            constraint = match.group(1)
            # Parse constraint to version list
            if ">=" in constraint:
                min_ver = constraint.replace(">=", "").strip()
                return get_versions_from(min_ver)

    # Default: Python 3.10-3.12
    return ["3.10", "3.11", "3.12"]

def get_versions_from(min_version: str) -> list[str]:
    """Get Python versions >= min_version."""
    all_versions = ["3.9", "3.10", "3.11", "3.12", "3.13"]
    try:
        idx = all_versions.index(min_version)
        return all_versions[idx:]
    except ValueError:
        return ["3.10", "3.11", "3.12"]
```

### Node Versions

```python
def detect_node_versions(path: Path) -> list[str]:
    """Detect Node.js version requirements."""
    pkg = path / "package.json"
    if pkg.exists():
        import json
        data = json.loads(pkg.read_text())
        engines = data.get("engines", {})
        node_constraint = engines.get("node", "")

        if ">=" in node_constraint:
            # Parse and return appropriate versions
            pass

    # Default: LTS versions
    return ["18", "20", "22"]
```

## Documentation Detection

```python
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
```

## CI Feature Detection

```python
def detect_ci_features(path: Path) -> dict:
    """Detect what CI features are needed."""
    return {
        "tests": detect_test_framework(path) is not None,
        "coverage": has_coverage_config(path),
        "linting": has_linting_config(path),
        "type_checking": has_type_checking(path),
        "docs_build": detect_docs(path).get("mkdocs") or detect_docs(path).get("sphinx"),
        "docker": (path / "Dockerfile").exists(),
        "matrix": should_use_matrix(path),
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
```
