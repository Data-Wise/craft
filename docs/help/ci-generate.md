# /craft:ci:generate

> **Generate GitHub Actions CI workflow from project detection.**

---

## Synopsis

```bash
/craft:ci:generate [template] [--output PATH]
```

**Quick examples:**
```bash
# Auto-detect and generate
/craft:ci:generate

# Force specific template
/craft:ci:generate python
/craft:ci:generate node

# Custom output path
/craft:ci:generate --output .github/workflows/test.yml
```

---

## Description

Generates a GitHub Actions workflow file based on project detection or a specified template. Automatically detects project type, build tools, test frameworks, and creates an appropriate CI configuration.

**Workflow:**
1. **Detect** - Run project detection (or use specified template)
2. **Customize** - Adjust based on detected features
3. **Generate** - Write workflow file
4. **Validate** - Check for common issues

---

## Templates

| Template | Detection | What's Generated |
|----------|-----------|------------------|
| `auto` | Auto-detect project type | Best-fit template |
| `python` | pyproject.toml, requirements.txt | UV/Poetry/Pip workflow |
| `node` | package.json | NPM/PNPM/Bun workflow |
| `r` | DESCRIPTION | R CMD check workflow |
| `rust` | Cargo.toml | Cargo test workflow |
| `go` | go.mod | Go test workflow |
| `plugin` | .claude-plugin/ | Plugin validation |

---

## Generated Features

The generator can include:

| Feature | Question | Default |
|---------|----------|---------|
| **Coverage** | Upload to Codecov? | Yes if codecov.yml exists |
| **Matrix** | Test multiple versions? | Yes |
| **Linting** | Include lint step? | Yes if config found |
| **Types** | Include type checking? | Yes if mypy/typescript found |
| **Docs** | Build documentation? | Yes if mkdocs/sphinx found |

---

## Examples

### Python (UV)

```bash
/craft:ci:generate python
```

Generates:
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
      - uses: astral-sh/setup-uv@v4
      - run: uv python install ${{ matrix.python-version }}
      - run: uv sync --all-extras --dev
      - run: uv run ruff check .
      - run: uv run mypy src/
      - run: uv run pytest --cov --cov-report=xml
```

### Node.js

```bash
/craft:ci:generate node
```

Generates:
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
      - uses: actions/setup-node@v4
        with:
          node-version: ${{ matrix.node-version }}
          cache: 'npm'
      - run: npm ci
      - run: npm run lint --if-present
      - run: npm test
```

### Claude Plugin

```bash
/craft:ci:generate plugin
```

Generates:
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
      - uses: actions/setup-python@v5
        with:
          python-version: '3.12'

      - name: Validate plugin structure
        run: |
          test -f .claude-plugin/plugin.json || exit 1
          python3 -m json.tool .claude-plugin/plugin.json > /dev/null

      - name: Check for hardcoded paths
        run: |
          if grep -r "/Users/" commands/ 2>/dev/null; then
            exit 1
          fi

      - name: Validate command files
        run: |
          for f in commands/**/*.md; do
            head -1 "$f" | grep -qE '^---|^#' || echo "⚠️ $f"
          done
```

---

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

---

## Additional Templates

| Template | Use Case |
|----------|----------|
| `tauri` | Rust + Vite desktop apps |
| `mcp` | MCP server projects |
| `monorepo` | Multi-package repositories |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| Wrong template detected | Specify template explicitly: `/craft:ci:generate python` |
| Missing features | Check if config files exist (ruff.toml, mypy.ini, etc.) |
| Workflow fails | Run `/craft:ci:validate` to check for issues |
| Need different versions | Edit the matrix in the generated file |

---

## See Also

- **Detection:** `/craft:ci:detect` - Run detection without generating
- **Validation:** `/craft:ci:validate` - Validate generated workflow
- **Pre-flight:** `/craft:check` - Quick CI check
- **Git sync:** `/craft:git:sync` - Commit and push
