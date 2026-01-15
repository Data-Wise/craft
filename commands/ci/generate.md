---
description: Generate GitHub Actions CI workflow from project detection
arguments:
  - name: template
    description: Template to use (auto|python|node|r|rust|go|plugin)
    required: false
    default: auto
  - name: output
    description: Output path (defaults to .github/workflows/ci.yml)
    required: false
  - name: dry-run
    description: Preview workflow generation without creating files
    required: false
    default: false
    alias: -n
---

# /craft:ci:generate - Generate CI Workflow

Generate a GitHub Actions workflow file based on project detection or specified template.

## Quick Start

```bash
/craft:ci:generate              # Auto-detect and generate
/craft:ci:generate python       # Force Python template
/craft:ci:generate --output .github/workflows/test.yml

# Preview without creating files
/craft:ci:generate --dry-run
/craft:ci:generate -n
/craft:ci:generate python --dry-run
```

## Dry-Run Mode

Preview the CI workflow that would be generated without creating any files:

```bash
/craft:ci:generate --dry-run
/craft:ci:generate -n
```

### Example Output

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Generate CI Workflow                               │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Project Detection:                                          │
│   - Type: Python (uv)                                         │
│   - Test framework: pytest                                    │
│   - Linter: ruff                                              │
│   - Type checker: mypy                                        │
│   - Python versions: 3.10, 3.11, 3.12                         │
│                                                               │
│ ✓ File to Create:                                             │
│   - .github/workflows/ci.yml (~85 lines)                      │
│                                                               │
│ ✓ Workflow Configuration:                                     │
│   - Triggers: push (main, dev), pull_request (main)           │
│   - Jobs: test (matrix: 3 Python versions)                   │
│   - Steps: checkout, setup uv, install, lint, type-check, test│
│   - Coverage: Upload to codecov (Python 3.12 only)           │
│                                                               │
│ ⚠ Warnings:                                                   │
│   • No existing workflow file found                            │
│   • Will create .github/workflows/ directory                  │
│                                                               │
│ 📊 Summary: 1 file to create (~85 lines YAML)                  │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Benefits:**
- Preview detected project configuration before generating
- Verify template selection is correct
- Check workflow triggers and job configuration
- See exact file path and estimated size

## Workflow

1. **Detect** - Run project detection (or use specified template)
2. **Customize** - Adjust based on detected features
3. **Generate** - Write workflow file
4. **Validate** - Check for common issues

## Generated Templates

### Python (UV)

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      fail-fast: false
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Install uv
        uses: astral-sh/setup-uv@v4

      - name: Set up Python ${{ matrix.python-version }}
        run: uv python install ${{ matrix.python-version }}

      - name: Install dependencies
        run: uv sync --all-extras --dev

      - name: Run linting
        run: uv run ruff check .

      - name: Run type checking
        run: uv run mypy src/

      - name: Run tests
        run: uv run pytest --cov --cov-report=xml

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        if: matrix.python-version == '3.12'
        with:
          files: ./coverage.xml
```

### Python (Poetry)

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install Poetry
        uses: snok/install-poetry@v1

      - name: Install dependencies
        run: poetry install

      - name: Run tests
        run: poetry run pytest --cov
```

### Python (Pip)

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        python-version: ['3.10', '3.11', '3.12']

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python ${{ matrix.python-version }}
        uses: actions/setup-python@v5
        with:
          python-version: ${{ matrix.python-version }}

      - name: Install dependencies
        run: |
          python -m pip install --upgrade pip
          pip install -e ".[dev]"

      - name: Run tests
        run: pytest --cov
```

### Node.js (NPM)

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ['18', '20', '22']

    steps:
      - uses: actions/checkout@v4

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'

      - name: Install dependencies
        run: npm ci

      - name: Run linting
        run: npm run lint --if-present

      - name: Run tests
        run: npm test
```

### Node.js (PNPM)

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: ['18', '20', '22']

    steps:
      - uses: actions/checkout@v4

      - uses: pnpm/action-setup@v2
        with:
          version: 8

      - name: Use Node.js ${{ matrix.node-version }}
        uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'pnpm'

      - name: Install dependencies
        run: pnpm install --frozen-lockfile

      - name: Run tests
        run: pnpm test
```

### R Package

```yaml
name: R-CMD-check

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  R-CMD-check:
    runs-on: ${{ matrix.config.os }}
    strategy:
      fail-fast: false
      matrix:
        config:
          - {os: macos-latest, r: 'release'}
          - {os: windows-latest, r: 'release'}
          - {os: ubuntu-latest, r: 'devel', http-user-agent: 'release'}
          - {os: ubuntu-latest, r: 'release'}
          - {os: ubuntu-latest, r: 'oldrel-1'}

    steps:
      - uses: actions/checkout@v4

      - uses: r-lib/actions/setup-r@v2
        with:
          r-version: ${{ matrix.config.r }}
          http-user-agent: ${{ matrix.config.http-user-agent }}
          use-public-rspm: true

      - uses: r-lib/actions/setup-r-dependencies@v2
        with:
          extra-packages: any::rcmdcheck
          needs: check

      - uses: r-lib/actions/check-r-package@v2
        with:
          upload-snapshots: true
```

### Rust

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Install Rust
        uses: dtolnay/rust-toolchain@stable
        with:
          components: clippy, rustfmt

      - name: Check formatting
        run: cargo fmt --all -- --check

      - name: Run clippy
        run: cargo clippy --all-targets --all-features -- -D warnings

      - name: Run tests
        run: cargo test --all-features
```

### Go

```yaml
name: CI

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Go
        uses: actions/setup-go@v5
        with:
          go-version-file: 'go.mod'

      - name: Run go vet
        run: go vet ./...

      - name: Run tests
        run: go test -v -race -coverprofile=coverage.out ./...

      - name: Upload coverage
        uses: codecov/codecov-action@v4
        with:
          files: ./coverage.out
```

### Claude Plugin

```yaml
name: Validate Plugin

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  validate:
    runs-on: ubuntu-latest

    steps:
      - uses: actions/checkout@v4

      - name: Set up Python
        uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Validate plugin structure
        run: |
          test -f .claude-plugin/plugin.json || exit 1
          python3 -m json.tool .claude-plugin/plugin.json > /dev/null
          echo "✅ Plugin structure valid"

      - name: Check for hardcoded paths
        run: |
          if grep -r "/Users/" commands/ 2>/dev/null; then
            echo "❌ Found hardcoded /Users/ paths"
            exit 1
          fi
          echo "✅ No hardcoded paths"

      - name: Validate command files
        run: |
          for f in commands/**/*.md; do
            if [ -f "$f" ]; then
              head -1 "$f" | grep -qE '^---|^#' || echo "⚠️ $f missing structure"
            fi
          done
          echo "✅ Commands validated"
```

## Customization Options

When generating, the command will ask about optional features:

| Feature | Question | Default |
|---------|----------|---------|
| **Coverage** | Upload to Codecov? | Yes if codecov.yml exists |
| **Matrix** | Test multiple versions? | Yes |
| **Linting** | Include lint step? | Yes if config found |
| **Types** | Include type checking? | Yes if mypy/typescript found |
| **Docs** | Build documentation? | Yes if mkdocs/sphinx found |

## Output

```
╭─ CI Workflow Generated ─────────────────────────────────╮
│                                                         │
│  📁 Created: .github/workflows/ci.yml                   │
│                                                         │
│  Template: python-uv                                    │
│  Python versions: 3.10, 3.11, 3.12                     │
│                                                         │
│  Features included:                                     │
│  ✅ Test matrix                                         │
│  ✅ Linting (ruff)                                      │
│  ✅ Type checking (mypy)                                │
│  ✅ Coverage upload                                     │
│  ❌ Documentation build (not detected)                  │
│                                                         │
├─────────────────────────────────────────────────────────┤
│  Next Steps:                                            │
│  1. Review the generated workflow                       │
│  2. Add secrets if needed (CODECOV_TOKEN)              │
│  3. Commit and push to trigger CI                       │
│                                                         │
│  → git add .github/workflows/ci.yml                     │
│  → git commit -m "ci: add GitHub Actions workflow"      │
│  → git push                                             │
╰─────────────────────────────────────────────────────────╯
```

## Integration

Works with:
- `/craft:ci:detect` - Run detection first
- `/craft:ci:validate` - Validate generated workflow
- `/craft:check ci` - Quick CI check
- `/craft:git:sync` - Commit and push

## Additional Templates

### Tauri (Rust + Vite)

```yaml
name: Tests

on:
  push:
    branches: [main, dev]
  pull_request:
    branches: [main]

jobs:
  frontend-tests:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: '20'
          cache: 'npm'
      - run: npm ci
      - run: npm run typecheck
      - run: npm run test:run

  rust-tests:
    runs-on: ${{ matrix.os }}
    strategy:
      matrix:
        os: [ubuntu-latest, macos-latest]
    steps:
      - uses: actions/checkout@v4
      - uses: dtolnay/rust-toolchain@stable
      - uses: Swatinem/rust-cache@v2
        with:
          workspaces: src-tauri
      - name: Install deps (Ubuntu)
        if: matrix.os == 'ubuntu-latest'
        run: sudo apt-get install -y libwebkit2gtk-4.1-dev libappindicator3-dev librsvg2-dev patchelf
      - working-directory: src-tauri
        run: cargo test
      - working-directory: src-tauri
        run: cargo clippy -- -D warnings
```

### MCP Server

```yaml
name: Tests

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    strategy:
      matrix:
        node-version: [18, 20, 22]
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm test
```

## CI Templates Reference

For more templates and best practices, see **[CI-TEMPLATES.md](../../docs/CI-TEMPLATES.md)**.

## Related Skills

- `project-detector` - Core detection logic
- `devops-helper` - CI/CD best practices

## See Also

- `/craft:ci:validate` - Validate existing CI workflows
- `/craft:ci:detect` - Detect project configuration
- Template: `templates/dry-run-pattern.md`
- Utility: `utils/dry_run_output.py`
- Specification: `docs/specs/SPEC-dry-run-feature-2026-01-15.md`
