---
name: project-detector
description: This skill should be used when the user asks to "detect project type", "what kind of project is this", "generate CI workflow", "set up CI", or needs to identify build tools, test frameworks, and CI requirements. Smart detection of project types, build tools, and CI requirements for automated workflow generation.
category: ci
---

# Project Detector Skill

Intelligent detection of project types, build tools, test frameworks, and CI requirements. Used by `/craft:ci:detect` and related commands.

## Detection Priority

Detection runs in priority order (first match wins for primary type):

| Priority | Type | Marker Files | Stack |
|----------|------|--------------|-------|
| 1 | Claude Plugin | `.claude-plugin/plugin.json` | plugin |
| 2 | MCP Server | `package.json` + `mcp` in name/deps | mcp |
| 3 | Tauri | `src-tauri/tauri.conf.json` | tauri |
| 4 | Swift Package | `Package.swift` | swift |
| 5 | Swift iOS/macOS | `*.xcodeproj` OR `*.xcworkspace` | swift |
| 6 | R Package | `DESCRIPTION` + `NAMESPACE` | r |
| 7 | R Quarto | `_quarto.yml` + `*.qmd` | r |
| 8 | Python UV | `pyproject.toml` + `uv.lock` | python |
| 9 | Python Poetry | `pyproject.toml` + `poetry.lock` | python |
| 10 | Python Pip | `pyproject.toml` OR `setup.py` | python |
| 11 | Node Bun | `package.json` + `bun.lock` | node |
| 12 | Node PNPM | `package.json` + `pnpm-lock.yaml` | node |
| 13 | Node Yarn | `package.json` + `yarn.lock` | node |
| 14 | Node NPM | `package.json` + `package-lock.json` | node |
| 15 | Rust | `Cargo.toml` | rust |
| 16 | Go | `go.mod` | go |
| 17 | Java Maven | `pom.xml` | java |
| 18 | Java Gradle | `build.gradle` OR `build.gradle.kts` | java |
| 19 | Homebrew Tap | `Formula/*.rb` OR `Casks/*.rb` | homebrew |
| 20 | ZSH Plugin | `*.plugin.zsh` OR `functions/*.zsh` | zsh |
| 21 | Emacs Package | `*.el` + `-pkg.el` | elisp |
| 22 | Shell | `*.sh` + no other markers | shell |

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
    # Priority 1-5: Specialized/hybrid projects
    ("plugin", "claude", [".claude-plugin/plugin.json"], []),
    ("mcp", "server", ["package.json"], []),  # Check for mcp in name/deps
    ("tauri", "app", ["src-tauri/tauri.conf.json"], ["src-tauri/Cargo.toml"]),
    ("swift", "package", ["Package.swift"], ["Sources/"]),
    ("swift", "xcode", [], []),  # Special: glob for *.xcodeproj
    # Priority 6-7: R ecosystem
    ("r", "package", ["DESCRIPTION", "NAMESPACE"], ["R/", "tests/"]),
    ("r", "quarto", ["_quarto.yml"], ["*.qmd"]),
    # Priority 8-10: Python ecosystem
    ("python", "uv", ["pyproject.toml", "uv.lock"], ["src/"]),
    ("python", "poetry", ["pyproject.toml", "poetry.lock"], ["src/"]),
    ("python", "pip", ["pyproject.toml"], ["requirements.txt"]),
    ("python", "setuptools", ["setup.py"], ["setup.cfg"]),
    # Priority 11-14: Tooling projects (check BEFORE Node to catch hybrids)
    ("homebrew", "tap", [], []),  # Special: glob for Formula/*.rb
    ("zsh", "plugin", [], []),  # Special: glob for *.plugin.zsh
    ("elisp", "package", [], []),  # Special: glob for *-pkg.el
    # Priority 15-18: Node ecosystem (requires real Node project, not just tooling)
    ("node", "bun", ["package.json", "bun.lock"], []),
    ("node", "pnpm", ["package.json", "pnpm-lock.yaml"], []),
    ("node", "yarn", ["package.json", "yarn.lock"], []),
    ("node", "npm", ["package.json"], ["package-lock.json"]),
    # Priority 19-20: Other compiled languages
    ("rust", "cargo", ["Cargo.toml"], ["Cargo.lock"]),
    ("go", "mod", ["go.mod"], ["go.sum"]),
    ("java", "maven", ["pom.xml"], []),
    ("java", "gradle", ["build.gradle"], ["build.gradle.kts"]),
    # Priority 21: Fallback
    ("shell", "script", [], []),  # Fallback for *.sh
]


def is_real_node_project(path: Path) -> bool:
    """Check if package.json indicates a real Node.js project vs just tooling.

    A real Node.js project has at least one of:
    - 'main' field (library entry point)
    - 'bin' field (CLI commands)
    - 'dependencies' (not just devDependencies)
    - 'type': 'module' with actual source files

    Projects with only devDependencies (ESLint, Prettier, etc.) are
    just using Node tooling, not actual Node.js projects.
    """
    pkg = path / "package.json"
    if not pkg.exists():
        return False

    import json
    try:
        data = json.loads(pkg.read_text())
    except json.JSONDecodeError:
        return False

    # Has entry point = real Node project
    if data.get("main"):
        return True

    # Has CLI commands = real Node project
    if data.get("bin"):
        return True

    # Has real dependencies (not just devDependencies) = real Node project
    if data.get("dependencies") and len(data["dependencies"]) > 0:
        return True

    # Has exports field = real Node project (modern ESM)
    if data.get("exports"):
        return True

    # Only has devDependencies = just tooling, not a Node project
    return False


def detect_project(path: Path) -> Optional[ProjectInfo]:
    """Detect project type from directory contents."""
    for proj_type, variant, required, optional in DETECTORS:
        if all((path / f).exists() for f in required):
            # Special handling for Node.js - skip if only tooling
            if proj_type == "node" and not is_real_node_project(path):
                continue  # Skip Node detection, try next detector

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

Per-language detection functions (Python, Node, R, Rust, Go, Tauri, Swift, MCP, Homebrew, ZSH, Elisp) are in [`references/framework-detection.md`](references/framework-detection.md). Each function inspects marker files and dependency manifests; defaults are listed in the CI Template Selection table below.

## CI Template Selection

Based on detection, recommend appropriate CI template:

| Project | Template | Key Features |
|---------|----------|--------------|
| `python-uv` | `python-uv-ci.yml` | uv sync, pytest, coverage |
| `python-poetry` | `python-poetry-ci.yml` | poetry install, pytest |
| `python-pip` | `python-pip-ci.yml` | pip install, pytest |
| `node-npm` | `node-npm-ci.yml` | npm ci, jest/vitest |
| `node-pnpm` | `node-pnpm-ci.yml` | pnpm install, tests |
| `node-bun` | `node-bun-ci.yml` | bun install, bun test |
| `r-package` | `r-package-ci.yml` | R CMD check, testthat |
| `r-quarto` | `r-quarto-ci.yml` | quarto render |
| `rust-cargo` | `rust-cargo-ci.yml` | cargo test, clippy |
| `go-mod` | `go-mod-ci.yml` | go test, go vet |
| `plugin-claude` | `plugin-ci.yml` | Structure validation |
| `tauri-app` | `tauri-ci.yml` | Rust + Node build, tauri-action |
| `swift-package` | `swift-ci.yml` | swift build, swift test |
| `swift-xcode` | `xcode-ci.yml` | xcodebuild, xctest |
| `mcp-server` | `mcp-ci.yml` | Node tests, MCP validation |
| `homebrew-tap` | `homebrew-ci.yml` | Formula syntax check, brew audit |
| `zsh-plugin` | `zsh-ci.yml` | Shellcheck, zsh -n syntax check |
| `elisp-package` | `elisp-ci.yml` | Emacs batch compile, ert tests |

Version detection (Python, Node), documentation detection, and CI feature detection helpers are also in [`references/framework-detection.md`](references/framework-detection.md).

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

## CI Templates Reference

For production-ready CI examples, see **CI-TEMPLATES.md** with templates from:

| Template Source | Project Type | Key Features |
|-----------------|--------------|--------------|
| aiterm | Python/uv | Multi-OS, multi-Python, Codecov |
| atlas | Node/npm | Multi-Node, unit/integration/e2e |
| nexus-cli | Python/uv | Quality gates, bandit security |
| scribe | Tauri | Rust + Vitest, cross-platform |

**Exemplary patterns from real projects:**
- Python: `uv sync --all-extras`, `pytest --cov`
- Node: `npm ci`, matrix 18/20/22
- Tauri: Separate frontend/backend jobs, Swatinem cache
- MCP: Simple Node tests, optional Bun support

## Integration

Use with:
- `/craft:ci:detect` - Run detection and show results
- `/craft:ci:generate` - Generate workflow from detection
- `/craft:ci:validate` - Validate existing CI against project
- `/craft:check ci` - Quick CI pre-flight check

**After detection:**
1. Review recommended template in CI-TEMPLATES.md
2. Copy template, adjust matrix/coverage as needed
3. Commit to `.github/workflows/test.yml`
