---
name: project-detector
description: Smart detection of project types, build tools, and CI requirements for automated workflow generation
version: 1.0.0
category: ci
triggers:
  - detect project
  - project type
  - ci detection
  - what kind of project
  - analyze project
  - ci setup
---

# Project Detector Skill

Intelligent detection of project types, build tools, test frameworks, and CI requirements. Used by `/craft:ci:detect` and related commands.

## Detection Priority

Detection runs in priority order (first match wins for primary type):

| Priority | Type | Marker Files | Stack |
|----------|------|--------------|-------|
| 1 | Claude Plugin | `.claude-plugin/plugin.json` | plugin |
| 2 | R Package | `DESCRIPTION` + `NAMESPACE` | r |
| 3 | R Quarto | `_quarto.yml` + `*.qmd` | r |
| 4 | Python UV | `pyproject.toml` + `uv.lock` | python |
| 5 | Python Poetry | `pyproject.toml` + `poetry.lock` | python |
| 6 | Python Pip | `pyproject.toml` OR `setup.py` | python |
| 7 | Node PNPM | `package.json` + `pnpm-lock.yaml` | node |
| 8 | Node Yarn | `package.json` + `yarn.lock` | node |
| 9 | Node NPM | `package.json` + `package-lock.json` | node |
| 10 | Rust | `Cargo.toml` | rust |
| 11 | Go | `go.mod` | go |
| 12 | Java Maven | `pom.xml` | java |
| 13 | Java Gradle | `build.gradle` OR `build.gradle.kts` | java |
| 14 | Shell | `*.sh` + no other markers | shell |

## Detection Algorithm

```python
from pathlib import Path
from dataclasses import dataclass
from typing import Optional

@dataclass
class ProjectInfo:
    """Detected project information."""
    type: str              # Primary type (python, node, r, etc.)
    variant: str           # Specific variant (uv, poetry, npm, etc.)
    test_framework: str    # pytest, jest, testthat, etc.
    build_tool: str        # uv, npm, cargo, etc.
    ci_template: str       # Recommended CI template
    python_versions: list  # For Python projects
    node_versions: list    # For Node projects
    has_docs: bool         # Has documentation setup
    has_ci: bool           # Already has CI configured

DETECTORS = [
    # (type, variant, required_files, optional_files)
    ("plugin", "claude", [".claude-plugin/plugin.json"], []),
    ("r", "package", ["DESCRIPTION", "NAMESPACE"], ["R/", "tests/"]),
    ("r", "quarto", ["_quarto.yml"], ["*.qmd"]),
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
                has_docs=detect_docs(path),
                has_ci=(path / ".github/workflows").exists(),
            )
    return None
```

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

## CI Template Selection

Based on detection, recommend appropriate CI template:

| Project | Template | Key Features |
|---------|----------|--------------|
| `python-uv` | `python-uv-ci.yml` | uv sync, pytest, coverage |
| `python-poetry` | `python-poetry-ci.yml` | poetry install, pytest |
| `python-pip` | `python-pip-ci.yml` | pip install, pytest |
| `node-npm` | `node-npm-ci.yml` | npm ci, jest/vitest |
| `node-pnpm` | `node-pnpm-ci.yml` | pnpm install, tests |
| `r-package` | `r-package-ci.yml` | R CMD check, testthat |
| `r-quarto` | `r-quarto-ci.yml` | quarto render |
| `rust-cargo` | `rust-cargo-ci.yml` | cargo test, clippy |
| `go-mod` | `go-mod-ci.yml` | go test, go vet |
| `plugin-claude` | `plugin-ci.yml` | Structure validation |

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

## Output Format

When `/craft:ci:detect` runs, output structured results:

```markdown
## Project Detection Results

**Type:** Python (uv)
**Test Framework:** pytest
**Python Versions:** 3.10, 3.11, 3.12

### Detected Features
| Feature | Status |
|---------|--------|
| Tests | ✅ pytest in tests/ |
| Coverage | ✅ coverage config in pyproject.toml |
| Linting | ✅ ruff configured |
| Type Checking | ✅ mypy configured |
| Documentation | ✅ mkdocs.yml found |
| Docker | ❌ No Dockerfile |
| Existing CI | ❌ No .github/workflows/ |

### Recommended CI Template
`python-uv-ci.yml`

### Suggested Workflow
```yaml
name: CI
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']
    steps:
      - uses: actions/checkout@v4
      - uses: astral-sh/setup-uv@v4
      - run: uv sync
      - run: uv run pytest --cov
```

### Next Steps
1. Run `/craft:ci:generate` to create workflow file
2. Customize matrix if needed
3. Add secrets for coverage upload
```

## Integration

Use with:
- `/craft:ci:detect` - Run detection and show results
- `/craft:ci:generate` - Generate workflow from detection
- `/craft:ci:validate` - Validate existing CI against project
- `/craft:check ci` - Quick CI pre-flight check
