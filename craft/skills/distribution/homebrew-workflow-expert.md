---
name: homebrew-workflow-expert
description: Expert knowledge of GitHub Actions workflows for automated Homebrew formula updates and releases
version: 1.0.0
category: distribution
triggers:
  - homebrew workflow
  - homebrew release automation
  - homebrew github actions
  - formula auto-update
  - homebrew tap workflow
---

# Homebrew Workflow Expert

Deep expertise in GitHub Actions workflows for automating Homebrew formula updates, releases, and tap management.

## Reusable Workflow Pattern

The recommended approach is a **centralized reusable workflow** in your homebrew-tap repository.

### Tap Repository Structure

```
homebrew-tap/
├── .github/
│   └── workflows/
│       └── update-formula.yml    # Reusable workflow
├── Formula/
│   ├── myapp.rb
│   └── othertool.rb
└── README.md
```

### Reusable Workflow (`update-formula.yml`)

```yaml
name: Update Formula

on:
  workflow_call:
    inputs:
      formula_name:
        required: true
        type: string
        description: 'Name of the formula to update (e.g., myapp)'
      version:
        required: true
        type: string
        description: 'New version (e.g., 1.2.3)'
      sha256:
        required: true
        type: string
        description: 'SHA256 hash of the release tarball'
      source_type:
        required: false
        type: string
        default: 'github'
        description: 'Source type: github or pypi'
      source_repo:
        required: false
        type: string
        description: 'Source repository (default: github.repository)'
      auto_merge:
        required: false
        type: boolean
        default: false
        description: 'Auto-merge the PR after creation'
    secrets:
      tap_token:
        required: true
        description: 'PAT with access to tap repository'

jobs:
  update:
    runs-on: ubuntu-latest
    steps:
      - name: Checkout tap repository
        uses: actions/checkout@v4
        with:
          repository: YOUR-ORG/homebrew-tap
          token: ${{ secrets.tap_token }}

      - name: Update formula
        run: |
          FORMULA_FILE="Formula/${{ inputs.formula_name }}.rb"

          if [ ! -f "$FORMULA_FILE" ]; then
            echo "Error: Formula $FORMULA_FILE not found"
            exit 1
          fi

          # Update version in URL
          if [ "${{ inputs.source_type }}" = "pypi" ]; then
            # PyPI URL pattern
            sed -i "s|url \"https://files.pythonhosted.org/packages/.*/.*-[0-9.]*\.tar\.gz\"|url \"https://files.pythonhosted.org/packages/source/${FIRST_CHAR}/${{ inputs.formula_name }}/${{ inputs.formula_name }}-${{ inputs.version }}.tar.gz\"|" "$FORMULA_FILE"
          else
            # GitHub URL pattern
            SOURCE_REPO="${{ inputs.source_repo || github.repository }}"
            sed -i "s|url \"https://github.com/.*/archive/refs/tags/v[0-9.]*\.tar\.gz\"|url \"https://github.com/${SOURCE_REPO}/archive/refs/tags/v${{ inputs.version }}.tar.gz\"|" "$FORMULA_FILE"
          fi

          # Update SHA256
          sed -i "s|sha256 \"[a-f0-9]*\"|sha256 \"${{ inputs.sha256 }}\"|" "$FORMULA_FILE"

          echo "Updated $FORMULA_FILE to version ${{ inputs.version }}"
          cat "$FORMULA_FILE"

      - name: Create Pull Request
        id: create-pr
        uses: peter-evans/create-pull-request@v5
        with:
          token: ${{ secrets.tap_token }}
          commit-message: "Update ${{ inputs.formula_name }} to ${{ inputs.version }}"
          title: "Update ${{ inputs.formula_name }} to ${{ inputs.version }}"
          body: |
            Automated formula update from release workflow.

            **Changes:**
            - Version: ${{ inputs.version }}
            - SHA256: ${{ inputs.sha256 }}
            - Source: ${{ inputs.source_type }}
          branch: update-${{ inputs.formula_name }}-${{ inputs.version }}
          base: main
          delete-branch: true

      - name: Auto-merge PR
        if: inputs.auto_merge && steps.create-pr.outputs.pull-request-number
        env:
          GH_TOKEN: ${{ secrets.tap_token }}
        run: |
          gh pr merge ${{ steps.create-pr.outputs.pull-request-number }} \
            --repo YOUR-ORG/homebrew-tap \
            --merge \
            --delete-branch
```

## Caller Workflow Pattern

In each project that uses Homebrew:

### GitHub Source (Default)

```yaml
name: Homebrew Release

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (e.g., 1.2.3)'
        required: true
      auto_merge:
        description: 'Auto-merge the PR'
        type: boolean
        default: true

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
      sha256: ${{ steps.sha256.outputs.sha256 }}
    steps:
      - name: Get version
        id: version
        run: |
          if [ "${{ github.event_name }}" = "release" ]; then
            VERSION="${{ github.event.release.tag_name }}"
            VERSION="${VERSION#v}"
          else
            VERSION="${{ github.event.inputs.version }}"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT
          echo "Version: $VERSION"

      - name: Calculate SHA256
        id: sha256
        run: |
          TARBALL_URL="https://github.com/${{ github.repository }}/archive/refs/tags/v${{ steps.version.outputs.version }}.tar.gz"
          SHA256=$(curl -sL "$TARBALL_URL" | shasum -a 256 | cut -d' ' -f1)
          echo "sha256=$SHA256" >> $GITHUB_OUTPUT
          echo "SHA256: $SHA256"

  update-homebrew:
    needs: prepare
    uses: YOUR-ORG/homebrew-tap/.github/workflows/update-formula.yml@main
    with:
      formula_name: myapp
      version: ${{ needs.prepare.outputs.version }}
      sha256: ${{ needs.prepare.outputs.sha256 }}
      source_type: github
      auto_merge: ${{ github.event.inputs.auto_merge == 'true' || github.event_name == 'release' }}
    secrets:
      tap_token: ${{ secrets.HOMEBREW_TAP_GITHUB_TOKEN }}
```

### PyPI Source

```yaml
name: Homebrew Release (PyPI)

on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release (matches PyPI)'
        required: true

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.version.outputs.version }}
      sha256: ${{ steps.sha256.outputs.sha256 }}
    steps:
      - name: Get version
        id: version
        run: echo "version=${{ github.event.inputs.version }}" >> $GITHUB_OUTPUT

      - name: Get PyPI SHA256
        id: sha256
        run: |
          PACKAGE_NAME="myapp"
          VERSION="${{ steps.version.outputs.version }}"

          # Fetch package info from PyPI API
          PYPI_JSON=$(curl -s "https://pypi.org/pypi/${PACKAGE_NAME}/${VERSION}/json")

          # Extract SHA256 for source distribution (.tar.gz)
          SHA256=$(echo "$PYPI_JSON" | jq -r '.urls[] | select(.packagetype == "sdist") | .digests.sha256')

          echo "sha256=$SHA256" >> $GITHUB_OUTPUT
          echo "SHA256: $SHA256"

  update-homebrew:
    needs: prepare
    uses: YOUR-ORG/homebrew-tap/.github/workflows/update-formula.yml@main
    with:
      formula_name: myapp
      version: ${{ needs.prepare.outputs.version }}
      sha256: ${{ needs.prepare.outputs.sha256 }}
      source_type: pypi
      auto_merge: true
    secrets:
      tap_token: ${{ secrets.HOMEBREW_TAP_GITHUB_TOKEN }}
```

## Token Setup

### Fine-Grained PAT Requirements

Create a fine-grained Personal Access Token with:

| Setting | Value |
|---------|-------|
| **Name** | `homebrew-tap-updater` |
| **Expiration** | 90 days (set reminder to rotate) |
| **Repository access** | Only select repositories |
| **Selected repositories** | `YOUR-ORG/homebrew-tap` |
| **Permissions** | |
| - Contents | Read and write |
| - Pull requests | Read and write |

### Adding Token to Repositories

```bash
# Add to a single repo
gh secret set HOMEBREW_TAP_GITHUB_TOKEN --repo YOUR-ORG/myapp

# Paste the token when prompted

# Verify it exists
gh secret list --repo YOUR-ORG/myapp
```

### Token Rotation

1. Create new token with same permissions
2. Update in all repos using the token
3. Delete old token
4. Set calendar reminder for next rotation

## Auto-Merge Strategies

### Strategy 1: Immediate Auto-Merge

```yaml
auto_merge: true  # Always auto-merge
```

Best for:
- Personal taps
- Trusted automated releases
- CI-validated releases

### Strategy 2: Release-Only Auto-Merge

```yaml
auto_merge: ${{ github.event_name == 'release' }}
```

Best for:
- Manual workflow dispatches need review
- Releases are pre-validated

### Strategy 3: Manual Review

```yaml
auto_merge: false  # Always create PR for review
```

Best for:
- Team taps
- Critical packages
- Compliance requirements

## Workflow Triggers

### On Release (Recommended)

```yaml
on:
  release:
    types: [published]
```

Triggers when:
- New release is published
- Draft is converted to release

### On Tag Push

```yaml
on:
  push:
    tags:
      - 'v*'
```

Triggers when:
- Any tag matching `v*` is pushed

### Manual Dispatch

```yaml
on:
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release'
        required: true
```

Triggers when:
- User manually runs workflow
- Provides version input

## Multi-Formula Coordination

For releasing multiple related packages:

```yaml
jobs:
  release-matrix:
    strategy:
      matrix:
        package:
          - name: core-lib
            formula: myapp-core
          - name: cli-tool
            formula: myapp-cli
          - name: plugin
            formula: myapp-plugin
      fail-fast: false
    steps:
      - name: Update ${{ matrix.package.formula }}
        uses: YOUR-ORG/homebrew-tap/.github/workflows/update-formula.yml@main
        with:
          formula_name: ${{ matrix.package.formula }}
          # ... other inputs
```

## Troubleshooting

### Issue: Workflow call permission denied

```yaml
# Ensure the reusable workflow allows external calls
on:
  workflow_call:  # This enables external calling
```

### Issue: Token doesn't have access

Check token has:
- Correct repository scope (tap repo, not source repo)
- Contents: Read and write
- Pull requests: Read and write

### Issue: PR conflicts

```yaml
# In create-pull-request step
- uses: peter-evans/create-pull-request@v5
  with:
    # ... other options
    delete-branch: true  # Clean up after merge
```

### Issue: Auto-merge fails

Ensure:
- Token has PR write permissions
- No branch protection requiring reviews
- PR passes any required checks

```yaml
# Check PR status before merge
- name: Wait for checks
  run: |
    gh pr checks $PR_NUMBER --watch
```

## Validation Before Release

```yaml
- name: Validate formula
  run: |
    # Install Homebrew (Linux)
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"

    # Run audit
    brew audit --strict Formula/${{ inputs.formula_name }}.rb

    # Test installation
    brew install --build-from-source Formula/${{ inputs.formula_name }}.rb
    brew test ${{ inputs.formula_name }}
```

## Integration

Use with:
- `/craft:dist:homebrew workflow` - Generate caller workflow
- `/craft:dist:homebrew setup` - Full setup wizard
- `/craft:dist:homebrew validate` - Pre-release validation
- `homebrew-formula-expert` skill - Formula syntax and patterns
