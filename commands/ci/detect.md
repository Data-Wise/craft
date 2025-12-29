---
description: Smart detection of project type, build tools, test frameworks, and CI requirements
arguments:
  - name: path
    description: Project directory to analyze (defaults to current directory)
    required: false
  - name: output
    description: Output format (terminal|json|markdown)
    required: false
    default: terminal
---

# /craft:ci:detect - Project & CI Detection

Analyze a project directory to detect its type, build tools, test framework, and recommend appropriate CI configuration.

## Quick Start

```bash
/craft:ci:detect              # Analyze current directory
/craft:ci:detect ./my-project # Analyze specific directory
/craft:ci:detect --json       # Output as JSON for automation
```

## What Gets Detected

| Category | Detection |
|----------|-----------|
| **Project Type** | Python, Node, R, Rust, Go, Claude Plugin |
| **Build Tool** | uv, poetry, pip, npm, pnpm, yarn, cargo |
| **Test Framework** | pytest, jest, vitest, testthat, cargo test |
| **Linting** | ruff, eslint, lintr, clippy |
| **Type Checking** | mypy, pyright, typescript |
| **Documentation** | mkdocs, sphinx, docusaurus, quarto |
| **Existing CI** | GitHub Actions, GitLab CI, CircleCI |

## Detection Priority

Projects are detected in priority order (first match wins):

1. **Claude Plugin** - `.claude-plugin/plugin.json`
2. **R Package** - `DESCRIPTION` + `NAMESPACE`
3. **R Quarto** - `_quarto.yml` + `*.qmd`
4. **Python UV** - `pyproject.toml` + `uv.lock`
5. **Python Poetry** - `pyproject.toml` + `poetry.lock`
6. **Python Pip** - `pyproject.toml` or `setup.py`
7. **Node PNPM** - `package.json` + `pnpm-lock.yaml`
8. **Node Yarn** - `package.json` + `yarn.lock`
9. **Node NPM** - `package.json` + `package-lock.json`
10. **Rust** - `Cargo.toml`
11. **Go** - `go.mod`

## Output Example

```
╭─ Project Detection ─────────────────────────────────────╮
│                                                         │
│  📦 Type:      Python                                   │
│  🔧 Build:     uv (pyproject.toml + uv.lock)           │
│  🧪 Tests:     pytest (tests/)                         │
│  📊 Coverage:  ✓ configured                            │
│  🔍 Linting:   ruff                                    │
│  📝 Types:     mypy                                    │
│  📚 Docs:      mkdocs                                  │
│  🔄 CI:        ❌ not configured                       │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Python Versions: 3.10, 3.11, 3.12                     │
│                                                         │
│  Features:                                              │
│  ✅ Tests      ✅ Coverage   ✅ Linting                 │
│  ✅ Types      ✅ Docs       ❌ Docker                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  📋 Recommended: python-uv-ci.yml                       │
│                                                         │
│  Next Steps:                                            │
│  → /craft:ci:generate to create workflow               │
│  → /craft:ci:validate to check existing CI             │
╰─────────────────────────────────────────────────────────╯
```

## JSON Output

```bash
/craft:ci:detect --json
```

```json
{
  "project": {
    "type": "python",
    "variant": "uv",
    "path": "/path/to/project"
  },
  "build": {
    "tool": "uv",
    "config_file": "pyproject.toml",
    "lock_file": "uv.lock"
  },
  "testing": {
    "framework": "pytest",
    "directory": "tests/",
    "config": "pyproject.toml"
  },
  "features": {
    "tests": true,
    "coverage": true,
    "linting": true,
    "type_checking": true,
    "docs": true,
    "docker": false
  },
  "versions": {
    "python": ["3.10", "3.11", "3.12"],
    "min_python": "3.10"
  },
  "ci": {
    "existing": false,
    "recommended_template": "python-uv-ci.yml"
  }
}
```

## Execution Steps

When you run `/craft:ci:detect`:

1. **Scan Directory** - Check for marker files (pyproject.toml, package.json, etc.)
2. **Identify Type** - Match against detection priority list
3. **Detect Features** - Find test framework, linting, docs
4. **Check Versions** - Parse version constraints from config files
5. **Analyze CI** - Check for existing `.github/workflows/`
6. **Recommend** - Suggest appropriate CI template

## Implementation

```bash
# Step 1: Check marker files
if [ -f ".claude-plugin/plugin.json" ]; then
    TYPE="plugin"
elif [ -f "DESCRIPTION" ] && [ -f "NAMESPACE" ]; then
    TYPE="r-package"
elif [ -f "pyproject.toml" ]; then
    if [ -f "uv.lock" ]; then
        TYPE="python-uv"
    elif [ -f "poetry.lock" ]; then
        TYPE="python-poetry"
    else
        TYPE="python-pip"
    fi
elif [ -f "package.json" ]; then
    if [ -f "pnpm-lock.yaml" ]; then
        TYPE="node-pnpm"
    elif [ -f "yarn.lock" ]; then
        TYPE="node-yarn"
    else
        TYPE="node-npm"
    fi
elif [ -f "Cargo.toml" ]; then
    TYPE="rust"
elif [ -f "go.mod" ]; then
    TYPE="go"
fi

# Step 2: Detect test framework
if [ "$TYPE" = "python-"* ]; then
    if grep -q "pytest" pyproject.toml 2>/dev/null; then
        TEST_FRAMEWORK="pytest"
    fi
fi

# Step 3: Check for existing CI
if [ -d ".github/workflows" ]; then
    HAS_CI=true
fi
```

## Multi-Project Detection

For monorepos or multi-project directories:

```bash
/craft:ci:detect --recursive
```

```
╭─ Multi-Project Detection ───────────────────────────────╮
│                                                         │
│  Found 3 projects:                                      │
│                                                         │
│  📁 ./backend                                           │
│     Type: Python (uv)  Tests: pytest                   │
│                                                         │
│  📁 ./frontend                                          │
│     Type: Node (pnpm)  Tests: vitest                   │
│                                                         │
│  📁 ./shared                                            │
│     Type: TypeScript   Tests: jest                     │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  📋 Recommended: monorepo-ci.yml                        │
│     Matrix: python + node                              │
╰─────────────────────────────────────────────────────────╯
```

## Integration

Works with:
- `/craft:ci:generate` - Generate workflow from detection
- `/craft:ci:validate` - Validate existing CI configuration
- `/craft:check ci` - Quick CI pre-flight check
- `/craft:do "setup ci"` - Let orchestrator handle CI setup

## Related Skills

- `project-detector` - Core detection logic
- `test-strategist` - Test framework recommendations
- `devops-helper` - CI/CD best practices
