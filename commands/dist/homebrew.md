---
description: Complete Homebrew automation - formulas, workflows, auditing, and dependency management
arguments:
  - name: subcommand
    description: "Subcommand: formula|workflow|audit|setup|update-resources|deps"
    required: false
    default: formula
  - name: tap
    description: Homebrew tap repository (e.g., user/tap)
    required: false
  - name: version
    description: Specific version to use (default: latest tag)
    required: false
---

# /craft:dist:homebrew - Homebrew Automation Hub

Complete Homebrew formula management with automated workflows.

## Subcommands

| Command | Purpose |
|---------|---------|
| `formula` | Generate or update formula (default) |
| `workflow` | Generate GitHub Actions release workflow |
| `audit` | Run `brew audit` validation + auto-fix |
| `setup` | Full setup wizard (formula + workflow + token) |
| `update-resources` | Fix stale PyPI resource URLs |
| `deps` | Show formula dependency graph + system deps matrix |

## Quick Start

```bash
# Generate formula for current project
/craft:dist:homebrew

# Full automated setup (recommended for new projects)
/craft:dist:homebrew setup

# Generate release workflow
/craft:dist:homebrew workflow

# Validate formula before release
/craft:dist:homebrew audit
```

---

## /craft:dist:homebrew formula

Generate or update a Homebrew formula.

### Usage

```bash
/craft:dist:homebrew formula                    # Auto-detect and create
/craft:dist:homebrew formula --tap user/tap     # Specify target tap
/craft:dist:homebrew formula --version 1.2.3    # Use specific version
```

### Auto-Detection

Detects project type and generates appropriate formula:

| Project Type | Detection | Formula Pattern |
|--------------|-----------|-----------------|
| **Claude Code Plugin** | `.claude-plugin/plugin.json` | `libexec.install` + plugin scripts |
| Python | `pyproject.toml` | `Language::Python::Virtualenv` |
| Node.js | `package.json` | npm install pattern |
| Go | `go.mod` | go build pattern |
| Rust | `Cargo.toml` | cargo install pattern |
| Shell | `*.sh` scripts | bin.install pattern |

> **Detection priority:** Claude Code Plugin > Python > Node.js > Go > Rust > Shell. Plugin detection takes precedence because `.claude-plugin/plugin.json` is the most specific indicator.

### Example Output

```
✓ Detected: Python project (pyproject.toml)
✓ Found version: 0.3.5 (from git tag)
✓ Calculated SHA256: abc123...
✓ Generated: Formula/myapp.rb

Formula saved to: ./Formula/myapp.rb
```

---

## /craft:dist:homebrew workflow

Generate GitHub Actions workflow for automated Homebrew releases. Auto-detects project type and generates a hardened workflow.

### Usage

```bash
/craft:dist:homebrew workflow                   # Auto-detect and generate
/craft:dist:homebrew workflow --tap user/tap    # Specify tap repository
/craft:dist:homebrew workflow --source pypi     # Force PyPI source type
```

### Auto-Detection

Detects project type and customizes the workflow accordingly:

| Project Type | Detection | Source | Extra Steps |
|--------------|-----------|--------|-------------|
| **Claude Code Plugin** | `.claude-plugin/` | GitHub tarball | Plugin metadata extraction |
| **Python** | `pyproject.toml` | PyPI or GitHub | `command_count`, `agent_count` |
| **Node.js** | `package.json` | npm or GitHub | Standard SHA flow |
| **Go / Rust / Shell** | `go.mod` / `Cargo.toml` / scripts | GitHub tarball | Standard SHA flow |

### Output Files

Creates `.github/workflows/homebrew-release.yml` with hardened security:

```yaml
name: Homebrew Release

on:
  release:
    types: [published]
  workflow_dispatch:
    inputs:
      version:
        description: 'Version to release'
        required: true
      auto_merge:
        description: 'Auto-merge the PR'
        type: boolean
        default: true

jobs:
  prepare:
    runs-on: ubuntu-latest
    outputs:
      version: ${{ steps.release.outputs.version }}
      sha256: ${{ steps.release.outputs.sha256 }}
    steps:
      - uses: actions/checkout@v4

      - name: Get version and calculate SHA
        id: release
        env:
          # Use env indirection to prevent script injection
          EVENT_NAME: ${{ github.event_name }}
          INPUT_VERSION: ${{ github.event.inputs.version }}
        run: |
          if [ "$EVENT_NAME" = "workflow_dispatch" ]; then
            VERSION="$INPUT_VERSION"
          else
            VERSION="${GITHUB_REF#refs/tags/}"
            VERSION="${VERSION#v}"
          fi
          echo "version=$VERSION" >> $GITHUB_OUTPUT

          TARBALL_URL="https://github.com/${{ github.repository }}/archive/refs/tags/v${VERSION}.tar.gz"
          SHA256=$(curl -sL --retry 3 --retry-delay 2 "$TARBALL_URL" | sha256sum | cut -d' ' -f1)

          # Validate SHA256 is not empty (download failed)
          if [ -z "$SHA256" ] || [ ${#SHA256} -ne 64 ]; then
            echo "::error::SHA256 calculation failed. Got: '$SHA256'"
            exit 1
          fi
          echo "sha256=$SHA256" >> $GITHUB_OUTPUT

  update-homebrew:
    needs: prepare
    uses: YOUR-ORG/homebrew-tap/.github/workflows/update-formula.yml@main
    with:
      formula_name: YOUR-FORMULA-NAME
      version: ${{ needs.prepare.outputs.version }}
      sha256: ${{ needs.prepare.outputs.sha256 }}
      source_type: github
      auto_merge: ${{ github.event.inputs.auto_merge == 'true' || github.event_name == 'release' }}
    secrets:
      tap_token: ${{ secrets.HOMEBREW_TAP_GITHUB_TOKEN }}
```

### Security Features

| Feature | Purpose |
|---------|---------|
| **`env:` indirection** | Prevents script injection from `github.event.inputs.*` |
| **`sha256sum`** | Standard tool on Ubuntu runners (not `shasum -a 256`) |
| **`--retry 3`** | Handles transient GitHub CDN failures |
| **64-char hex guard** | Catches empty/corrupt SHA before workflow proceeds |

### Workflow Types

| Source | When to Use |
|--------|-------------|
| GitHub | Projects with GitHub releases (default) |
| PyPI | Python packages published to PyPI |

### Plugin Workflow (Extra Metadata)

For Claude Code plugins, the workflow also extracts metadata counts:

```yaml
      - name: Extract plugin metadata
        id: metadata
        run: |
          CMD_COUNT=$(find commands -name "*.md" ! -name "index.md" ! -name "README.md" | wc -l | tr -d ' ')
          AGENT_COUNT=$(find agents -name "*.md" | wc -l | tr -d ' ')
          SKILL_COUNT=$(find skills -name "*.md" | wc -l | tr -d ' ')
          echo "command_count=$CMD_COUNT" >> $GITHUB_OUTPUT
          echo "agent_count=$AGENT_COUNT" >> $GITHUB_OUTPUT
          echo "skill_count=$SKILL_COUNT" >> $GITHUB_OUTPUT
```

---

## /craft:dist:homebrew audit

Validate and auto-fix formula using `brew audit`.

### Usage

```bash
/craft:dist:homebrew audit                      # Validate + auto-fix
/craft:dist:homebrew audit --strict             # Strict mode (extra checks)
/craft:dist:homebrew audit --online             # Online checks (URL validation)
/craft:dist:homebrew audit --check-only         # Report issues without fixing
/craft:dist:homebrew audit --build              # Also run brew install --build-from-source
```

### Checks Performed

| Check | Description | Auto-Fix |
|-------|-------------|----------|
| Syntax | Ruby syntax validation | No |
| `desc` | < 80 chars, no 'A/An' prefix | Yes - truncate |
| `license` | Valid SPDX identifier | No |
| `url` | Accessible (with --online) | No |
| `sha256` | Matches URL content | No |
| `test` | Test block present | No |
| Dependencies | All deps available | No |
| Array comparison | Use `Array#include?` not `==` chains | Yes |
| Hash filtering | Use `Hash#slice` not `select` | Yes |
| Modifier `if` | Single-line body should use modifier | Yes |
| Assertions | Use `assert_path_exists` not `assert_predicate :exist?` | Yes |
| Section order | `caveats` before `test` | Yes |

### Build-from-Source Testing

When `--build` is specified, the audit also runs a full build test:

```bash
/craft:dist:homebrew audit --build
```

This executes:

1. `brew audit --strict` — style and correctness checks
2. `brew install --build-from-source <formula>` — full build verification
3. `brew test <formula>` — run the formula's test block

Useful before releases to catch build failures that audit alone won't find.

### Auto-Fix Patterns

When issues are found, the audit command automatically applies known fixes:

```ruby
# Fix 1: Description too long (> 80 chars)
# Before:
desc "Full-stack developer toolkit - 110 commands, 8 agents, 25 skills - Claude Code plugin"
# After:
desc "Full-stack developer toolkit for Claude Code with 110 commands"

# Fix 2: Array comparison (use Array#include?)
# Before:
libexec.install Dir["*", ".*"].reject { |f| f == "." || f == ".." || f == ".git" }
# After:
libexec.install Dir["*", ".*"].reject { |f| %w[. .. .git].include?(f) }

# Fix 3: Hash filtering (use Hash#slice)
# Before:
cleaned = data.select { |k, _| allowed_keys.include?(k) }
# After:
cleaned = data.slice(*allowed_keys)

# Fix 4: Modifier if (single-line body)
# Before:
if cleaned.size < data.size
  plugin_json.write(JSON.pretty_generate(cleaned) + "\n")
end
# After:
plugin_json.write(JSON.pretty_generate(cleaned) + "\n") if cleaned.size < data.size

# Fix 5: Assertions (use assert_path_exists)
# Before:
assert_predicate libexec/".claude-plugin/plugin.json", :exist?
# After:
assert_path_exists libexec/".claude-plugin/plugin.json"

# Fix 6: Section order (caveats before test)
# Reorder def caveats ... end to appear before def test ... end
```

### Workflow

1. Run `brew audit --strict --formula <tap>/<name>` to detect issues
2. Parse audit output for known fixable patterns
3. Apply auto-fixes to the formula file
4. Copy fixed formula to tap location (`/opt/homebrew/Library/Taps/...`)
5. Re-run audit to verify fixes
6. Report results

### Example Output

```
Running: brew audit --strict data-wise/tap/craft

Found 6 issues (6 auto-fixable):
  1. desc too long (85 chars, max 80) ........... FIXED
  2. Use Array#include? ......................... FIXED
  3. Use Hash#slice ............................. FIXED
  4. Use modifier if ............................ FIXED
  5. Use assert_path_exists ..................... FIXED
  6. caveats before test ........................ FIXED

Re-running audit... PASSED

All 6 issues auto-fixed. Formula is ready for release!
```

---

## /craft:dist:homebrew setup

Full guided setup for Homebrew automation.

### Usage

```bash
/craft:dist:homebrew setup                      # Interactive wizard
/craft:dist:homebrew setup --tap user/tap       # Specify tap
```

### Setup Flow

```
╔═══════════════════════════════════════════════════════════════╗
║           HOMEBREW AUTOMATION SETUP WIZARD                     ║
╠═══════════════════════════════════════════════════════════════╣
║                                                               ║
║  Step 1: Detect Project Type                                  ║
║  ───────────────────────────────────────                      ║
║  ✓ Detected: Python (pyproject.toml)                          ║
║  ✓ Name: myapp                                                ║
║  ✓ Version: 0.3.5                                             ║
║                                                               ║
║  Step 2: Generate Formula                                     ║
║  ───────────────────────────────────────                      ║
║  ✓ Created: Formula/myapp.rb                                  ║
║  ✓ Validated: brew audit passed                               ║
║                                                               ║
║  Step 3: Generate Workflow                                    ║
║  ───────────────────────────────────────                      ║
║  ✓ Created: .github/workflows/homebrew-release.yml            ║
║  ✓ Configured for: Data-Wise/homebrew-tap                     ║
║                                                               ║
║  Step 4: Token Setup                                          ║
║  ───────────────────────────────────────                      ║
║  ⚠ HOMEBREW_TAP_GITHUB_TOKEN not found                        ║
║                                                               ║
║  Creating Fine-Grained PAT...                                 ║
║  → URL: github.com/settings/tokens?type=beta                  ║
║  → Repos: YOUR-ORG/homebrew-tap only                          ║
║  → Permissions: Contents (RW) + Pull requests (RW)            ║
║  → Expiration: 90 days (set rotation reminder)                ║
║                                                               ║
║  Run: gh secret set HOMEBREW_TAP_GITHUB_TOKEN                 ║
║                                                               ║
║  Step 5: Commit Changes                                       ║
║  ───────────────────────────────────────                      ║
║  ✓ Staged: Formula/myapp.rb                                   ║
║  ✓ Staged: .github/workflows/homebrew-release.yml             ║
║                                                               ║
║  Ready to commit? (y/n)                                       ║
║                                                               ║
╚═══════════════════════════════════════════════════════════════╝
```

### What It Does

1. **Detects** project type and metadata
2. **Generates** Homebrew formula
3. **Validates** formula with `brew audit`
4. **Creates** GitHub Actions workflow
5. **Sets up token** — checks for `HOMEBREW_TAP_GITHUB_TOKEN`, guides creation of Fine-Grained PAT if missing (repos: tap only, permissions: Contents RW + PRs RW, 90-day expiry)
6. **Commits** all changes (with confirmation)

### Post-Setup

After setup completes:

```bash
# Create first release
git tag -a v0.3.5 -m "Release v0.3.5"
git push --tags

# Or trigger manually
gh workflow run homebrew-release.yml -f version=0.3.5
```

---

## Formula Templates

### Python (virtualenv)

```ruby
class MyApp < Formula
  include Language::Python::Virtualenv

  desc "Description from pyproject.toml"
  homepage "https://github.com/user/repo"
  url "https://github.com/user/repo/archive/v1.0.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "python@3.12"

  def install
    virtualenv_install_with_resources
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/myapp --version")
  end
end
```

### Node.js

```ruby
class MyApp < Formula
  desc "Description from package.json"
  homepage "https://github.com/user/repo"
  url "https://registry.npmjs.org/myapp/-/myapp-1.0.0.tgz"
  sha256 "..."
  license "MIT"

  depends_on "node"

  def install
    system "npm", "install", *std_npm_args
    bin.install_symlink Dir["#{libexec}/bin/*"]
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/myapp --version")
  end
end
```

### Go

```ruby
class MyApp < Formula
  desc "Description"
  homepage "https://github.com/user/repo"
  url "https://github.com/user/repo/archive/v1.0.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "go" => :build

  def install
    system "go", "build", *std_go_args(ldflags: "-s -w -X main.version=#{version}")
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/myapp --version")
  end
end
```

### Rust

```ruby
class MyApp < Formula
  desc "Description from Cargo.toml"
  homepage "https://github.com/user/repo"
  url "https://github.com/user/repo/archive/v1.0.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "rust" => :build

  def install
    system "cargo", "install", *std_cargo_args
  end

  test do
    assert_match version.to_s, shell_output("#{bin}/myapp --version")
  end
end
```

---

## /craft:dist:homebrew update-resources

Fix stale PyPI resource URLs in formulas automatically.

### The Problem

PyPI occasionally changes the directory structure for package downloads, causing formulas with `resource` blocks to break:

```
Error: Failed to download resource "click"
expected sha256 checksum <old>, got <new>
```

### Usage

```bash
/craft:dist:homebrew update-resources myapp        # Update specific formula
/craft:dist:homebrew update-resources --all        # Update all formulas
/craft:dist:homebrew update-resources --dry-run    # Preview changes only
```

### How It Works

1. **Parse Formula** - Extract all `resource` blocks
2. **Query PyPI API** - Get current URLs and checksums for each package
3. **Update Formula** - Replace stale URLs and SHA256 values
4. **Validate** - Run `brew audit` on updated formula

### Example

**Before (stale):**

```ruby
resource "click" do
  url "https://files.pythonhosted.org/packages/old/path/click-8.0.0.tar.gz"
  sha256 "abc123..."
end
```

**After (updated):**

```ruby
resource "click" do
  url "https://files.pythonhosted.org/packages/source/c/click/click-8.1.7.tar.gz"
  sha256 "def456..."
end
```

### PyPI API Integration

```bash
# Fetch package info
curl -s "https://pypi.org/pypi/click/json" | jq '{
  name: .info.name,
  version: .info.version,
  url: .urls[] | select(.packagetype == "sdist") | .url,
  sha256: .urls[] | select(.packagetype == "sdist") | .digests.sha256
}'
```

### Output

```
Updating resources for: nexus-cli

Checking 5 resources...
  ✓ click: 8.0.0 → 8.1.7 (URL updated)
  ✓ rich: 13.0.0 → 13.7.0 (URL updated)
  - typer: 0.9.0 (no changes)
  - httpx: 0.24.0 (no changes)
  ✓ pydantic: 2.0.0 → 2.5.3 (URL updated)

Updated 3 resources in Formula/nexus-cli.rb
Running brew audit... ✓ passed
```

### Options

| Option | Description |
|--------|-------------|
| `--dry-run` | Show what would change without modifying |
| `--all` | Update all formulas in tap |
| `--pin` | Don't upgrade versions, only fix URLs |
| `--commit` | Auto-commit changes |

### Common Issues

**Issue: Package renamed on PyPI**

```
Warning: Package 'old-name' not found on PyPI
Hint: Check if package was renamed or deprecated
```

**Issue: Source distribution not available**

```
Warning: No sdist found for 'package-name'
Only wheel distributions available
```

---

## /craft:dist:homebrew deps

Show formula dependency graph and system dependency matrix.

### Usage

```bash
/craft:dist:homebrew deps                       # All formulas in tap
/craft:dist:homebrew deps --formula craft       # Single formula
/craft:dist:homebrew deps --system              # Include system deps
/craft:dist:homebrew deps --dot                 # Output in Graphviz DOT format
```

### Inter-Formula Dependencies

Shows how formulas in the tap depend on each other and on shared system packages:

```
Inter-Formula Dependency Graph (data-wise/tap):

  craft ─────────── jq (optional)
  rforge ────────── jq (optional)
  scholar ────────── jq (optional)
  himalaya-mcp ──── himalaya, node, jq (optional)
  atlas ─────────── python@3.12 (build), node@20
  aiterm ────────── python@3.12
  nexus-cli ────── python@3.12, libyaml
  mcp-bridge ───── node
  examark ─────── node
  examify ─────── node
  flow-cli ────── (none)
  scribe-cli ──── xcode (build), macos

Shared Dependencies:
  python@3.12 ← aiterm, atlas, nexus-cli
  node ────── ← himalaya-mcp, mcp-bridge, examark, examify
  jq ──────── ← craft, rforge, scholar, himalaya-mcp (all optional)
```

### System Dependencies Matrix

With `--system`, also shows runtime requirements:

```
System Dependencies Matrix:

| Formula | python | node | jq | swift | himalaya |
|---------|--------|------|----|-------|----------|
| craft | - | - | opt | - | - |
| atlas | build | ✓ | - | - | - |
| aiterm | ✓ | - | - | - | - |
| nexus-cli | ✓ | - | - | - | - |
| himalaya-mcp | - | ✓ | opt | - | ✓ |
| mcp-bridge | - | ✓ | - | - | - |
| scribe-cli | - | - | - | build | - |
```

---

## Integration

| Command | Use With |
|---------|----------|
| `/craft:check --for release` | Pre-release validation |
| `/craft:git:tag` | Create version tag |
| `/craft:docs:changelog` | Update changelog |
| `/craft:ci:generate` | Full CI/CD setup (see also `ci:generate homebrew`) |

## Skills Used

- `homebrew-formula-expert` - Formula syntax and patterns
- `homebrew-workflow-expert` - GitHub Actions automation
- `homebrew-setup-wizard` - Setup wizard implementation
- `distribution-strategist` - Multi-channel distribution

---

## Claude Code Plugin Formulas

For Claude Code plugins distributed via Homebrew, use the special plugin pattern.

### Plugin Formula Pattern

Auto-detected when `.claude-plugin/plugin.json` exists. Generates a `brew audit --strict` compliant formula.

```ruby
class MyPlugin < Formula
  desc "Short description under 80 chars for Claude Code"
  homepage "https://github.com/user/my-plugin"
  url "https://github.com/user/my-plugin/archive/refs/tags/v1.0.0.tar.gz"
  sha256 "..."
  license "MIT"

  depends_on "jq" => :optional

  def install
    # Use Array#include? (brew audit compliant)
    libexec.install Dir["*", ".*"].reject { |f| %w[. .. .git].include?(f) }

    (bin/"my-plugin-install").write <<~EOS
      #!/bin/bash
      PLUGIN_NAME="my-plugin"
      TARGET_DIR="$HOME/.claude/plugins/$PLUGIN_NAME"
      SOURCE_DIR="$(brew --prefix)/opt/my-plugin/libexec"

      # Strip unrecognized keys from plugin.json (Claude Code strict schema)
      PLUGIN_JSON="$SOURCE_DIR/.claude-plugin/plugin.json"
      if grep -q 'claude_md_budget' "$PLUGIN_JSON" 2>/dev/null; then
          python3 -c "import json,sys;p=sys.argv[1];d=json.load(open(p));c={k:v for k,v in d.items() if k in('name','version','description','author')};f=open(p,'w');json.dump(c,f,indent=2);f.write(chr(10));f.close()" "$PLUGIN_JSON" 2>/dev/null || true
      fi

      echo "Installing plugin to Claude Code..."
      mkdir -p "$HOME/.claude/plugins" 2>/dev/null || true

      # Remove existing and create symlink
      if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
          rm -rf "$TARGET_DIR" 2>/dev/null || rm -f "$TARGET_DIR" 2>/dev/null || true
      fi
      ln -sf "$SOURCE_DIR" "$TARGET_DIR" 2>/dev/null || \
          ln -sfh "$SOURCE_DIR" "$TARGET_DIR" 2>/dev/null

      if [ -L "$TARGET_DIR" ]; then
          # Marketplace registration
          MARKETPLACE_DIR="$HOME/.claude/local-marketplace"
          mkdir -p "$MARKETPLACE_DIR" 2>/dev/null || true
          ln -sfh "$TARGET_DIR" "$MARKETPLACE_DIR/$PLUGIN_NAME" 2>/dev/null || true

          # Claude detection - skip auto-enable if Claude is running
          SETTINGS_FILE="$HOME/.claude/settings.json"
          AUTO_ENABLED=false
          CLAUDE_RUNNING=false

          if command -v lsof &>/dev/null; then
              if lsof "$SETTINGS_FILE" 2>/dev/null | grep -q "claude"; then
                  CLAUDE_RUNNING=true
              fi
          elif pgrep -x "claude" >/dev/null 2>&1; then
              CLAUDE_RUNNING=true
          fi

          if [ "$CLAUDE_RUNNING" = false ] && command -v jq &>/dev/null && [ -f "$SETTINGS_FILE" ]; then
              TEMP_FILE=$(mktemp)
              if jq --arg plugin "${PLUGIN_NAME}@local-plugins" '.enabledPlugins[$plugin] = true' "$SETTINGS_FILE" > "$TEMP_FILE" 2>/dev/null; then
                  mv "$TEMP_FILE" "$SETTINGS_FILE" 2>/dev/null && AUTO_ENABLED=true
              fi
              [ -f "$TEMP_FILE" ] && rm -f "$TEMP_FILE" 2>/dev/null
          fi

          # Branch guard hook (optional - copy if scripts/branch-guard.sh exists)
          HOOK_SRC="$SOURCE_DIR/scripts/branch-guard.sh"
          if [ -f "$HOOK_SRC" ] && [ ! -L "$HOME/.claude/hooks/branch-guard.sh" ]; then
              mkdir -p "$HOME/.claude/hooks" 2>/dev/null || true
              cp "$HOOK_SRC" "$HOME/.claude/hooks/branch-guard.sh" 2>/dev/null
              chmod +x "$HOME/.claude/hooks/branch-guard.sh" 2>/dev/null
          fi

          echo "Plugin installed successfully!"
          if [ "$AUTO_ENABLED" = true ]; then
              echo "Plugin auto-enabled in Claude Code."
          elif [ "$CLAUDE_RUNNING" = true ]; then
              echo "Claude Code is running - skipped auto-enable."
              echo "Run: claude plugin install ${PLUGIN_NAME}@local-plugins"
          else
              echo "Run: claude plugin install ${PLUGIN_NAME}@local-plugins"
          fi
      else
          echo "Automatic symlink failed. Run manually:"
          echo "  ln -sf $SOURCE_DIR $TARGET_DIR"
      fi
    EOS

    (bin/"my-plugin-uninstall").write <<~EOS
      #!/bin/bash
      PLUGIN_NAME="my-plugin"
      TARGET_DIR="$HOME/.claude/plugins/$PLUGIN_NAME"
      if [ -L "$TARGET_DIR" ] || [ -d "$TARGET_DIR" ]; then
          rm -rf "$TARGET_DIR"
          echo "Plugin uninstalled"
      else
          echo "Plugin not found at $TARGET_DIR"
      fi
    EOS

    chmod "+x", bin/"my-plugin-install"
    chmod "+x", bin/"my-plugin-uninstall"
  end

  def post_install
    # Step 1: Strip unrecognized keys from plugin.json
    begin
      require "json"
      plugin_json = libexec/".claude-plugin/plugin.json"
      if plugin_json.exist?
        allowed_keys = %w[name version description author]
        data = JSON.parse(plugin_json.read)
        cleaned = data.slice(*allowed_keys)
        plugin_json.write(JSON.pretty_generate(cleaned) + "\n") if cleaned.size < data.size
      end
    rescue
      nil
    end

    # Step 2: Run install script
    system bin/"my-plugin-install"

    # Step 3: Sync registry (optional)
    begin
      system "claude", "plugin", "update", "my-plugin@local-plugins" if which("claude")
    rescue
      nil
    end
  end

  def post_uninstall
    system bin/"my-plugin-uninstall" if (bin/"my-plugin-uninstall").exist?
  end

  # caveats BEFORE test (brew audit requirement)
  def caveats
    <<~EOS
      Plugin installed to ~/.claude/plugins/my-plugin

      If not auto-enabled, run:
        claude plugin install my-plugin@local-plugins
    EOS
  end

  test do
    # Use assert_path_exists (brew audit compliant)
    assert_path_exists libexec/".claude-plugin/plugin.json"
    assert_predicate libexec/"commands", :directory?
  end
end
```

### Key Features

| Feature | Purpose |
|---------|---------|
| **`brew audit --strict` compliant** | Uses `Array#include?`, `Hash#slice`, modifier `if`, `assert_path_exists`, correct section order |
| **Claude detection** | Uses `lsof` to check if Claude has settings.json open |
| **Skip auto-enable** | Avoids file lock conflicts when Claude is running |
| **plugin.json cleanup** | Ruby `JSON` + bash fallback to strip unrecognized keys |
| **Branch guard hook** | Auto-installs if `scripts/branch-guard.sh` exists |
| **Marketplace registration** | Creates symlink in `local-marketplace/` for discovery |
| **Uninstall script** | Cleanup on `brew uninstall` via `post_uninstall` |
| **Registry sync** | Runs `claude plugin update` in post_install |

### Existing Plugin Formulas

| Formula | Plugin | Status |
|---------|--------|--------|
| `craft.rb` | 110 commands | `brew audit --strict` clean |
| `rforge.rb` | 15 commands | Claude detection |
| `scholar.rb` | 21 commands | Claude detection |

### Testing Plugin Installation

```bash
# Reinstall and verify speed
time brew reinstall data-wise/tap/craft

# Check detection message
/opt/homebrew/opt/craft/bin/craft-install

# Verify plugin loaded
claude plugin list | grep craft

# Validate formula
brew audit --strict --formula data-wise/tap/craft
```

---

## Tips

- Always run `audit` before creating releases
- Use semantic versioning for clean formulas
- Set token rotation reminders (90-day expiry recommended)
- Test locally: `brew install --build-from-source ./Formula/myapp.rb`
- Auto-merge is safe for personal taps; disable for team taps
- For Claude Code plugins, always include Claude detection to avoid install hangs
