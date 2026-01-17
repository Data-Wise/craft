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
  - name: dry-run
    description: Preview what files will be analyzed without reading them
    required: false
    default: false
    alias: -n
---

# /craft:ci:detect - Project & CI Detection

Analyze a project directory to detect its type, build tools, test framework, and recommend appropriate CI configuration.

## Quick Start

```bash
/craft:ci:detect              # Analyze current directory
/craft:ci:detect ./my-project # Analyze specific directory
/craft:ci:detect --json       # Output as JSON for automation

# Preview detection plan
/craft:ci:detect --dry-run
/craft:ci:detect -n
```

## Dry-Run Mode

Preview what files will be analyzed for project detection:

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Project Detection                                  │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Directory to Analyze:                                       │
│   - Path: /path/to/your/project                               │
│   - Files checked: 60+ detection patterns                     │
│                                                               │
│ ✓ Detection Categories:                                       │
│   - Project type (19 patterns)                                │
│   - Build tools (uv, poetry, npm, cargo, etc.)                │
│   - Test frameworks (pytest, jest, cargo test, etc.)          │
│   - Linting tools (ruff, eslint, clippy)                      │
│   - Type checkers (mypy, typescript)                          │
│   - Documentation (mkdocs, quarto, sphinx)                    │
│   - Existing CI workflows                                     │
│                                                               │
│ ✓ Files to Check:                                             │
│   - pyproject.toml, package.json, Cargo.toml, etc.            │
│   - Lock files (uv.lock, package-lock.json, etc.)             │
│   - Config files (mkdocs.yml, _quarto.yml, etc.)              │
│   - CI files (.github/workflows/*.yml)                        │
│                                                               │
│ 📊 Summary: Read-only analysis of project structure            │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: This is a read-only command (no files modified), so dry-run mainly shows what will be checked.

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
2. **MCP Server** - `package.json` + `@modelcontextprotocol/sdk`
3. **Tauri App** - `src-tauri/tauri.conf.json`
4. **Swift Package** - `Package.swift`
5. **Swift iOS/macOS** - `*.xcodeproj` or `*.xcworkspace`
6. **R Package** - `DESCRIPTION` + `NAMESPACE`
7. **R Quarto** - `_quarto.yml` + `*.qmd`
8. **Python UV** - `pyproject.toml` + `uv.lock`
9. **Python Poetry** - `pyproject.toml` + `poetry.lock`
10. **Python Pip** - `pyproject.toml` or `setup.py`
11. **Homebrew Tap** - `Formula/*.rb` or `Casks/*.rb`
12. **ZSH Plugin** - `*.plugin.zsh` or `functions/*.zsh`
13. **Emacs Package** - `*-pkg.el` or `Cask`
14. **Node Bun** - `package.json` + `bun.lock`
15. **Node PNPM** - `package.json` + `pnpm-lock.yaml`
16. **Node Yarn** - `package.json` + `yarn.lock`
17. **Node NPM** - `package.json` + `package-lock.json` (real projects only)
18. **Rust** - `Cargo.toml`
19. **Go** - `go.mod`

> **Note:** Node.js detection requires a "real" project (has `main`, `bin`, `dependencies`, or `exports`). Projects with only `devDependencies` (ESLint, Prettier) are skipped to allow ZSH/Homebrew detection.

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

## CI Templates

For production-ready CI examples, see **[CI-TEMPLATES.md](../../docs/CI-TEMPLATES.md)** with templates from exemplary projects:

| Template | Source Project | Key Features |
|----------|----------------|--------------|
| Python/uv | aiterm, nexus-cli | Multi-OS, Codecov |
| Node/npm | atlas | Multi-Node matrix |
| Tauri | scribe | Rust + Vitest |
| MCP Server | statistical-research | Bun/Node tests |

## Related Skills

- `project-detector` - Core detection logic
- `test-strategist` - Test framework recommendations
- `devops-helper` - CI/CD best practices
