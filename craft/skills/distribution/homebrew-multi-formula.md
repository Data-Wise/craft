---
name: homebrew-multi-formula
description: Coordinate releases across multiple Homebrew formulas with dependency ordering
version: 1.0.0
category: distribution
triggers:
  - multi-formula release
  - batch homebrew release
  - formula dependency order
  - coordinated release
---

# Multi-Formula Coordinator

Coordinate releases across multiple Homebrew formulas, respecting dependency order and handling batch updates.

## Use Cases

1. **Monorepo Releases** - Multiple packages from one repository
2. **Ecosystem Releases** - Related packages with dependencies (e.g., rforge ecosystem)
3. **Batch Updates** - Update multiple formulas in one PR
4. **Dependency Chains** - Release in correct order when packages depend on each other

## Dependency Detection

### Formula Dependencies

```ruby
# In myapp-cli.rb
depends_on "myapp-core"  # Runtime dependency

# In myapp-plugin.rb
depends_on "myapp-cli"   # Also depends on cli
```

### Build Order

```
myapp-core    →  myapp-cli    →  myapp-plugin
    ↓              ↓
    └──────────────┴──────→ (can release in parallel after core)
```

## Workflow: Batch Release

### Input Manifest

Create `.homebrew-batch.yml`:

```yaml
# Batch release configuration
tap: data-wise/tap
auto_merge: true

formulas:
  - name: myapp-core
    version: "2.0.0"
    source: github

  - name: myapp-cli
    version: "2.0.0"
    source: github
    depends_on:
      - myapp-core

  - name: myapp-plugin
    version: "1.5.0"
    source: pypi
    depends_on:
      - myapp-cli
```

### Execution Order

```
Step 1: Build dependency graph
────────────────────────────────
  myapp-core (no deps) → Level 0
  myapp-cli (deps: core) → Level 1
  myapp-plugin (deps: cli) → Level 2

Step 2: Release in waves
────────────────────────────────
  Wave 0: myapp-core
    ✓ Updated formula
    ✓ PR created: #42
    ✓ Auto-merged

  Wave 1: myapp-cli
    ⏳ Waiting for Wave 0...
    ✓ Updated formula
    ✓ PR created: #43
    ✓ Auto-merged

  Wave 2: myapp-plugin
    ⏳ Waiting for Wave 1...
    ✓ Updated formula
    ✓ PR created: #44
    ✓ Auto-merged

Step 3: Summary
────────────────────────────────
  ✓ 3 formulas updated
  ✓ 3 PRs merged
  ⏱ Total time: 4m 23s
```

## GitHub Actions Workflow

### Reusable Batch Workflow

```yaml
# homebrew-tap/.github/workflows/batch-update.yml
name: Batch Formula Update

on:
  workflow_call:
    inputs:
      formulas:
        required: true
        type: string
        description: 'JSON array of {name, version, sha256, source_type}'
      auto_merge:
        required: false
        type: boolean
        default: true
    secrets:
      tap_token:
        required: true

jobs:
  parse:
    runs-on: ubuntu-latest
    outputs:
      matrix: ${{ steps.parse.outputs.matrix }}
      order: ${{ steps.parse.outputs.order }}
    steps:
      - name: Parse formulas and build order
        id: parse
        run: |
          echo '${{ inputs.formulas }}' | jq -r '
            # Build dependency graph
            def toposort:
              # ... topological sort implementation
            ;
            toposort | @json
          ' > order.json
          echo "order=$(cat order.json)" >> $GITHUB_OUTPUT

  update:
    needs: parse
    runs-on: ubuntu-latest
    strategy:
      max-parallel: 1  # Sequential for dependency order
      matrix:
        formula: ${{ fromJson(needs.parse.outputs.order) }}
    steps:
      - name: Wait for dependencies
        if: matrix.formula.depends_on
        run: |
          for dep in ${{ join(matrix.formula.depends_on, ' ') }}; do
            echo "Waiting for $dep to complete..."
            # Poll for PR merge status
          done

      - name: Update formula
        uses: ./.github/actions/update-formula
        with:
          formula_name: ${{ matrix.formula.name }}
          version: ${{ matrix.formula.version }}
          sha256: ${{ matrix.formula.sha256 }}
          source_type: ${{ matrix.formula.source_type }}
          auto_merge: ${{ inputs.auto_merge }}
```

### Caller Workflow

```yaml
# In project repo
name: Release Ecosystem

on:
  workflow_dispatch:
    inputs:
      core_version:
        description: 'Core version'
        required: true
      cli_version:
        description: 'CLI version'
        required: true

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      formulas: ${{ steps.build.outputs.formulas }}
    steps:
      - name: Calculate SHA256s
        id: sha
        run: |
          CORE_SHA=$(curl -sL "https://github.com/.../v${{ inputs.core_version }}.tar.gz" | shasum -a 256 | cut -d' ' -f1)
          CLI_SHA=$(curl -sL "https://github.com/.../v${{ inputs.cli_version }}.tar.gz" | shasum -a 256 | cut -d' ' -f1)
          echo "core_sha=$CORE_SHA" >> $GITHUB_OUTPUT
          echo "cli_sha=$CLI_SHA" >> $GITHUB_OUTPUT

      - name: Build formula list
        id: build
        run: |
          echo 'formulas=[
            {"name":"myapp-core","version":"${{ inputs.core_version }}","sha256":"${{ steps.sha.outputs.core_sha }}","source_type":"github"},
            {"name":"myapp-cli","version":"${{ inputs.cli_version }}","sha256":"${{ steps.sha.outputs.cli_sha }}","source_type":"github","depends_on":["myapp-core"]}
          ]' >> $GITHUB_OUTPUT

  release:
    needs: prepare
    uses: data-wise/homebrew-tap/.github/workflows/batch-update.yml@main
    with:
      formulas: ${{ needs.prepare.outputs.formulas }}
      auto_merge: true
    secrets:
      tap_token: ${{ secrets.HOMEBREW_TAP_GITHUB_TOKEN }}
```

## CLI Command

### Usage

```bash
/craft:dist:homebrew release-batch                 # Interactive mode
/craft:dist:homebrew release-batch --manifest .homebrew-batch.yml
/craft:dist:homebrew release-batch --formulas "core,cli,plugin"
```

### Interactive Flow

```
╔═══════════════════════════════════════════════════════════════╗
║           MULTI-FORMULA RELEASE                                ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Detected formulas in Data-Wise/homebrew-tap:                 ║
║                                                               ║
║  [ ] aiterm (v0.3.8)                                          ║
║  [ ] atlas (v1.2.0)                                           ║
║  [x] flow-cli (v2.1.0) → v2.2.0                               ║
║  [x] nexus-cli (v0.5.0) → v0.6.0                              ║
║  [ ] mcp-bridge (v0.1.0)                                      ║
║  [ ] scribe (v1.0.0)                                          ║
║                                                               ║
║  Selected: 2 formulas                                         ║
║  Dependencies: None detected                                  ║
║                                                               ║
║  Release order:                                               ║
║    1. flow-cli                                                ║
║    2. nexus-cli (parallel OK)                                 ║
║                                                               ║
║  [Continue] [Edit Selection] [Cancel]                         ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

## Dependency Graph Visualization

Generate Mermaid diagram of formula dependencies:

```bash
/craft:dist:homebrew deps --mermaid
```

Output:

```mermaid
graph LR
    subgraph "Data-Wise Tap"
        aiterm
        atlas
        flow-cli
        nexus-cli
        mcp-bridge
        scribe
    end

    subgraph "System Dependencies"
        python@3.12
        node
        rust
    end

    aiterm --> python@3.12
    atlas --> python@3.12
    nexus-cli --> python@3.12
    mcp-bridge --> node
    scribe --> rust
```

## Error Handling

### Dependency Failure

```
Error: myapp-cli release failed

Dependency chain affected:
  ✗ myapp-cli (failed)
  ⏸ myapp-plugin (skipped - depends on cli)

Options:
  1. Retry myapp-cli release
  2. Skip myapp-cli, continue with others
  3. Abort batch release

Choice: _
```

### Version Conflict

```
Warning: Version mismatch detected

myapp-cli v2.0.0 depends on myapp-core >= 2.0.0
But myapp-core in batch is v1.9.0

Options:
  1. Update myapp-core version to 2.0.0
  2. Lower myapp-cli dependency requirement
  3. Abort

Choice: _
```

## Integration

| Command | Purpose |
|---------|---------|
| `/craft:dist:homebrew release-batch` | Run batch release |
| `/craft:dist:homebrew deps` | Show dependency graph |
| `/craft:dist:homebrew validate --all` | Validate all formulas |

## Best Practices

1. **Test Dependencies First** - Run `brew install --build-from-source` for base packages
2. **Use Semantic Versioning** - Makes dependency resolution predictable
3. **Pin Major Versions** - `depends_on "myapp-core" => "~> 2.0"`
4. **Batch Related Releases** - Release ecosystem packages together
5. **Auto-merge for Speed** - Safe for personal taps with CI validation
