# SPEC: Desktop App Release Pipeline

## Metadata

| Field | Value |
|-------|-------|
| **Status** | draft |
| **Created** | 2026-02-24 |
| **Issue** | [#108](https://github.com/Data-Wise/craft/issues/108) |
| **From Brainstorm** | `BRAINSTORM-desktop-release-pipeline-2026-02-24.md` |
| **Scope** | Scribe (Tauri) — generalize later |
| **Estimated Effort** | Medium-Large (2-3 dev sessions) |

---

## Overview

Extend `/craft:dist:homebrew` and the `/release` pipeline to support **Homebrew Cask** distribution for desktop apps built with Tauri. The current pipeline handles CLI tools distributed as Homebrew Formulas (source tarballs). Desktop apps require a fundamentally different distribution model: pre-built architecture-specific DMGs, dual SHA256 hashes, and release-specific cask content (postflight messages, caveats).

This was painfully exposed during the Scribe v1.20.0 release, which required ~15 manual steps that should have been automated.

**Key design decision:** Compute SHA256 from **local build artifacts** (not GitHub downloads), eliminating the race condition that caused tap conflicts during Scribe releases.

---

## Primary User Story

**As a** desktop app developer using Craft,
**I want** `/release` to automatically build, sign, upload, and distribute my Tauri app via Homebrew Cask,
**So that** I can release a new version with a single command instead of 15 manual steps.

### Acceptance Criteria

- [ ] `/release` detects Tauri projects (via `tauri.conf.json`) and includes build step
- [ ] Multi-architecture builds (aarch64 + x64) automated with progress feedback
- [ ] DMGs uploaded to GitHub release with `--clobber` for asset conflicts
- [ ] SHA256 computed from local build artifacts (not downloaded from GitHub)
- [ ] Homebrew Cask file updated correctly (version, both arch SHA256 blocks, postflight, caveats)
- [ ] Tap push handles conflicts with `git pull --rebase` + retry
- [ ] End-to-end `brew upgrade --cask` verification
- [ ] `.craft/homebrew.json` supports `"type": "cask"` configuration
- [ ] Existing Formula workflow unaffected (backward compatible)

---

## Secondary User Stories

### Story 2: Cask-Only Updates (No Build)

**As a** developer who pre-builds DMGs manually,
**I want** `/craft:dist:homebrew cask` to update the cask file from existing release assets,
**So that** I can fix cask metadata without rebuilding.

**Acceptance Criteria:**

- [ ] `--skip-build` flag accepts pre-built DMG paths
- [ ] SHA256 computed from provided local files or downloaded from release assets
- [ ] Cask version, SHA256, postflight, and caveats updated

### Story 3: Cask Audit

**As a** developer maintaining a Homebrew Cask,
**I want** `/craft:dist:homebrew audit` to validate cask files,
**So that** I catch issues before pushing to the tap.

**Acceptance Criteria:**

- [ ] Auto-detect cask vs formula for audit
- [ ] Run `brew audit --cask` with error reporting
- [ ] Check SHA256 matches actual release assets

---

## Architecture

### System Flow

```
/release (Tauri project detected)
  │
  ├─ Step 10b: Desktop App Release
  │   │
  │   ├─ 1. Detect: tauri.conf.json → read productName, version, identifier
  │   ├─ 2. Config: .craft/homebrew.json (optional overrides)
  │   ├─ 3. Pre-check: rustup target list → ensure both targets installed
  │   ├─ 4. Build native: npx tauri build (aarch64-apple-darwin)
  │   ├─ 5. Build cross: npx tauri build --target x86_64-apple-darwin
  │   ├─ 6. Locate DMGs: src-tauri/target/{target}/release/bundle/dmg/
  │   ├─ 7. Rename DMGs: {ProductName}_{version}_{arch}.dmg
  │   ├─ 8. Upload: gh release upload v{version} *.dmg --clobber
  │   ├─ 9. SHA256: shasum -a 256 <local DMG files>
  │   ├─ 10. Update cask: Casks/{name}.rb (version, SHA256, postflight, caveats)
  │   ├─ 11. Validate: ruby -c && brew audit --cask
  │   ├─ 12. Push tap: git pull --rebase && git commit && git push
  │   └─ 13. Verify: brew update && brew info --cask {name}
  │
  └─ Continue to Step 11 (sync dev)
```

### Component Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                     /release Pipeline                            │
├─────────────────────────────────────────────────────────────────┤
│  Steps 1-9 (existing)     │  Step 10a (Formula)                 │
│  Version → Preflight →    │  ├─ SHA256 from tarball             │
│  Bump → Commit → PR →     │  ├─ Update Formula/*.rb             │
│  CI → Merge → GH Release  │  └─ Push tap                       │
│                            ├────────────────────────────────────┤
│                            │  Step 10b (Cask) ← NEW             │
│                            │  ├─ Build aarch64 + x64             │
│                            │  ├─ Upload DMGs                     │
│                            │  ├─ SHA256 from local artifacts     │
│                            │  ├─ Update Casks/*.rb               │
│                            │  │   ├─ on_arm SHA256               │
│                            │  │   ├─ on_intel SHA256             │
│                            │  │   ├─ postflight (from CHANGELOG) │
│                            │  │   └─ caveats (from template)     │
│                            │  ├─ Validate (ruby -c + brew audit) │
│                            │  └─ Push tap                        │
├────────────────────────────┴────────────────────────────────────┤
│  Steps 11-13 (existing): Sync dev → Verify CI → Verify downstream│
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                /craft:dist:homebrew (extended)                    │
├─────────────────────────────────────────────────────────────────┤
│  formula  │  cask (NEW)  │  workflow  │  audit    │  setup      │
│  ─────────┼──────────────┼───────────┼───────────┼─────────────│
│  Generate/ │  Generate/   │  CI YAML   │  Validate │  Wizard     │
│  update    │  update      │  for both  │  formula  │  for both   │
│  Formula/  │  Casks/      │  types     │  + cask   │  types      │
│  *.rb      │  *.rb        │            │           │             │
├────────────┴──────────────┴───────────┴───────────┴─────────────┤
│  update-resources  │  deps  │  (unchanged)                       │
└────────────────────┴─────────────────────────────────────────────┘
```

### Auto-Detection Hierarchy

```
1. .craft/homebrew.json  →  { "type": "cask" }     (explicit, highest priority)
2. tauri.conf.json       →  Tauri desktop app       (auto-detect)
3. Casks/ in tap repo    →  Cask file exists         (tap structure)
4. Formula/ in tap repo  →  Formula file exists      (existing behavior)
5. Project type fallback →  Python/Node/Go/Rust/Shell (existing behavior)
```

---

## API Design

### Extended `.craft/homebrew.json` Schema

```json
{
  "formula_name": "scribe",
  "tap": "data-wise/tap",
  "type": "cask",
  "architectures": ["aarch64", "x64"],
  "artifact_pattern": "{name}_{version}_{arch}.dmg",
  "build_command": "npx tauri build --target {target}",
  "targets": {
    "aarch64": "aarch64-apple-darwin",
    "x64": "x86_64-apple-darwin"
  },
  "cask": {
    "app_name": "Scribe.app",
    "identifier": "com.scribe.app",
    "min_macos": "catalina",
    "postflight_template": "changelog",
    "caveats_template": "full"
  }
}
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `formula_name` | Yes | — | Name in tap (e.g., `scribe`) |
| `tap` | Yes | — | Tap in `org/name` format |
| `type` | No | `"formula"` | `"formula"` or `"cask"` |
| `architectures` | No | `["aarch64", "x64"]` | Architectures to build |
| `artifact_pattern` | No | `"{name}_{version}_{arch}.dmg"` | DMG naming pattern |
| `build_command` | No | `"npx tauri build --target {target}"` | Build command template |
| `targets` | No | see above | Rust target triple mapping |
| `cask.app_name` | No | from `tauri.conf.json` productName | `.app` bundle name |
| `cask.identifier` | No | from `tauri.conf.json` identifier | macOS bundle identifier |
| `cask.min_macos` | No | from `tauri.conf.json` bundle.macOS | Minimum macOS version |
| `cask.postflight_template` | No | `"changelog"` | `"changelog"` or `"none"` |
| `cask.caveats_template` | No | `"full"` | `"full"`, `"minimal"`, or `"none"` |

### Auto-Detection from `tauri.conf.json`

When no `.craft/homebrew.json` exists (or `type` is not specified), detect from:

```python
# Pseudo-code for auto-detection
if Path("src-tauri/tauri.conf.json").exists():
    config = json.load("src-tauri/tauri.conf.json")
    type = "cask"
    app_name = config["productName"] + ".app"    # "Scribe.app"
    identifier = config["identifier"]             # "com.scribe.app"
    version = config["version"]                   # "1.20.0"
    min_macos = config["bundle"]["macOS"]["minimumSystemVersion"]  # "10.15"
    # Map min version to Homebrew codename
    min_macos_name = {"10.15": "catalina", "11.0": "big_sur", "12.0": "monterey", ...}
```

### New Subcommand: `/craft:dist:homebrew cask`

```bash
# Generate new cask from Tauri project
/craft:dist:homebrew cask

# Update existing cask with new version + SHA256
/craft:dist:homebrew cask --version 1.21.0

# Update from pre-built DMGs (skip build)
/craft:dist:homebrew cask --skip-build --dmg-arm ./Scribe_1.21.0_aarch64.dmg --dmg-intel ./Scribe_1.21.0_x64.dmg

# Update cask content only (postflight, caveats) without version bump
/craft:dist:homebrew cask --content-only

# Dry-run (show what would change)
/craft:dist:homebrew cask --dry-run
```

| Flag | Description |
|------|-------------|
| `--version` | Specific version (default: from tauri.conf.json) |
| `--skip-build` | Don't build; use pre-built DMGs |
| `--dmg-arm` | Path to ARM DMG (with `--skip-build`) |
| `--dmg-intel` | Path to Intel DMG (with `--skip-build`) |
| `--content-only` | Update postflight/caveats without version bump |
| `--dry-run` | Preview changes without modifying files |
| `--tap` | Override tap (default: from config) |
| `--desc` | Override cask description (max 80 chars, `brew audit` enforced) |
| `--release-notes` | Custom release notes for postflight/caveats (default: from CHANGELOG) |
| `--no-verify` | Skip `brew audit --cask` after update |
| `--no-push` | Update cask locally but don't push to tap |

---

## Data Models

### Cask Template Structure

The cask file is generated/updated using a template with replaceable zones:

```ruby
# ===== TEMPLATE: Casks/{name}.rb =====
cask "{name}" do
  version "{version}"

  # ZONE: architecture (auto-generated)
  on_arm do
    sha256 "{sha256_arm}"
    url "https://github.com/{repo}/releases/download/v#{version}/{artifact_arm}"
  end
  on_intel do
    sha256 "{sha256_intel}"
    url "https://github.com/{repo}/releases/download/v#{version}/{artifact_intel}"
  end

  name "{display_name}"
  desc "{description}"
  homepage "https://github.com/{repo}"

  # ZONE: livecheck (static, generated once)
  livecheck do
    url "https://github.com/{repo}/releases"
    regex(/^v?(\d+(?:\.\d+)+)$/i)
    strategy :github_releases do |json, regex|
      json.filter_map do |release|
        match = release["tag_name"]&.match(regex)
        next unless match
        next if release["draft"] || release["prerelease"]
        match[1]
      end
    end
  end

  depends_on macos: ">= :{min_macos}"

  app "{app_name}"

  # ZONE: postflight (auto-generated from CHANGELOG)
  postflight do
    ohai "{display_name} v#{version} installed successfully!"
    ohai ""
    ohai "What's New in v{version}:"
    {postflight_items}
    ohai ""
    ohai "Report issues: https://github.com/{repo}/issues"
  end

  uninstall quit: "{identifier}"

  # ZONE: zap (static, generated once)
  zap trash: [
    "~/Library/Application Support/{identifier}",
    "~/Library/Caches/{identifier}",
    "~/Library/Logs/{identifier}",
    "~/Library/Preferences/{identifier}.plist",
    "~/Library/Saved Application State/{identifier}.savedState",
  ]

  # ZONE: caveats (auto-generated from template + CHANGELOG)
  caveats <<~EOS
    {caveats_content}
  EOS
end
```

### Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{name}` | config or repo name | `scribe` |
| `{version}` | tauri.conf.json or --version | `1.20.0` |
| `{sha256_arm}` | `shasum -a 256` of ARM DMG | `440b3b83...` |
| `{sha256_intel}` | `shasum -a 256` of Intel DMG | `2bdf8914...` |
| `{artifact_arm}` | artifact_pattern with arch=aarch64 | `Scribe_1.20.0_aarch64.dmg` |
| `{artifact_intel}` | artifact_pattern with arch=x64 | `Scribe_1.20.0_x64.dmg` |
| `{repo}` | git remote origin | `Data-Wise/scribe` |
| `{display_name}` | tauri.conf.json productName | `Scribe` |
| `{description}` | cask desc field (preserved) | `ADHD-friendly...` |
| `{app_name}` | productName + ".app" | `Scribe.app` |
| `{identifier}` | tauri.conf.json identifier | `com.scribe.app` |
| `{min_macos}` | mapped from minimumSystemVersion | `catalina` |
| `{postflight_items}` | Generated from CHANGELOG | See below |
| `{caveats_content}` | Generated from template | See below |

### Cask Install-Time Content (3 Zones)

The cask file contains 3 content zones that users see during/after `brew install` or `brew upgrade`. Each zone has **dynamic** parts (change every release) and **static** parts (rarely change).

#### Zone Map

```ruby
# ZONE 1: postflight — shown DURING install
postflight do                                          # ─── dynamic start
  ohai "Scribe v#{version} installed successfully!"    #  ✓ uses #{version}
  ohai ""
  ohai "What's New in v1.20.0:"                        #  ✗ HARDCODED version!
  ohai "  - Settings infrastructure ..."               #  ✗ release-specific
  ohai "  - Session timer replaced ..."                #  ✗ release-specific
  ohai "  - 2,280 tests passing"                       #  ✗ release-specific
  ohai ""                                              # ─── dynamic end
  ohai "Quick Start:"                                  # ─── static start
  ohai "  - Global hotkey: Cmd+Shift+N ..."            #  (rarely changes)
  ohai "  - Command palette: Cmd+K"
  ohai "  - Focus mode: Cmd+Shift+F"
  ohai ""
  ohai "Report issues: https://github.com/..."         # ─── static end
end

# ZONE 2: caveats — shown AFTER install
caveats <<~EOS
  Scribe v#{version} - ADHD-Friendly ...               #  ✓ uses #{version}
                                                       # ─── dynamic start
  New in v1.20.0:                                      #  ✗ HARDCODED version!
  - Settings infrastructure ...                        #  ✗ release-specific
  - Session timer removed ...                          #  ✗ release-specific
  - 2,280 tests passing                                #  ✗ release-specific
                                                       # ─── dynamic end
  Features:                                            # ─── static start
  - Three Editor Modes ...                             #  (full feature list)
  ...
  Keyboard Shortcuts:                                  #  (shortcut reference)
  ...
  Optional Dependencies:                               #  (install hints)
  ...                                                  # ─── static end
EOS

# ZONE 3: desc — one-liner (max 80 chars)
desc "ADHD-friendly distraction-free writer ..."       #  rarely changes
```

#### Problem: Hardcoded Versions

Lines like `"What's New in v1.20.0:"` and `"New in v1.20.0:"` use **literal strings**, not `#{version}` interpolation. On every release these go stale. The updater must find and replace these patterns.

#### Update Algorithm

```python
def update_cask_content(cask_path, new_version, changelog_items, test_count=None):
    content = read(cask_path)

    # --- ZONE 1: postflight ---

    # 1a. Replace hardcoded "What's New in vX.Y.Z:" line
    content = re.sub(
        r'ohai "What\'s New in v[\d.]+:?"',
        f'ohai "What\'s New in v{new_version}:"',
        content
    )

    # 1b. Replace release-specific bullet points (between "What's New" and "Quick Start")
    postflight_bullets = generate_postflight_bullets(changelog_items, test_count)
    content = replace_between_markers(
        content,
        start_pattern=r'ohai "What\'s New in v[\d.]+:"',
        end_pattern=r'ohai ""\s*\n\s*ohai "Quick Start:"',
        replacement=postflight_bullets
    )

    # --- ZONE 2: caveats ---

    # 2a. Replace hardcoded "New in vX.Y.Z:" line
    content = re.sub(
        r'New in v[\d.]+:',
        f'New in v{new_version}:',
        content
    )

    # 2b. Replace release-specific bullet points (between "New in" and "Features:")
    caveats_bullets = generate_caveats_bullets(changelog_items, test_count)
    content = replace_between_markers(
        content,
        start_pattern=r'New in v[\d.]+:',
        end_pattern=r'\n\s*Features:',
        replacement=caveats_bullets
    )

    # --- ZONE 3: desc (only if --desc flag provided) ---
    # Handled separately by --desc flag

    return content
```

#### Postflight Bullet Generation

```python
def generate_postflight_bullets(changelog_items, test_count=None):
    """
    Input:  changelog_items = ["Added dark mode support", "Fixed PDF export crash"]
            test_count = 2500
    Output: list of ohai lines for the postflight block
    """
    lines = []
    for item in changelog_items[:5]:  # Max 5 items in postflight (keep it short)
        lines.append(f'    ohai "  - {item}"')

    if test_count:
        lines.append(f'    ohai "  - {test_count:,} tests passing"')

    return "\n".join(lines)
```

#### Caveats Bullet Generation

```python
def generate_caveats_bullets(changelog_items, test_count=None):
    """
    Input:  changelog_items = ["Added dark mode", "Fixed PDF export", "SHORTCUTS registry"]
            test_count = 2500
    Output: bullet list for the caveats "New in" section
    """
    lines = []
    for item in changelog_items:  # All items (caveats can be longer than postflight)
        lines.append(f"    - {item}")

    if test_count:
        lines.append(f"    - {test_count:,} tests passing")

    return "\n".join(lines)
```

#### CHANGELOG Parsing

```bash
# Extract bullet points from the latest version entry in CHANGELOG.md
extract_changelog_items() {
    local VERSION="$1"
    local CHANGELOG="${2:-CHANGELOG.md}"

    # Find the version header, collect lines until next version header
    awk -v ver="$VERSION" '
        /^## / { if (found) exit; if ($0 ~ ver) found=1; next }
        found && /^- / { sub(/^- /, ""); print }
    ' "$CHANGELOG"
}

# Example:
# extract_changelog_items "1.21.0" → prints each bullet point
```

#### Test Count Extraction

```bash
# Auto-detect test count from project
extract_test_count() {
    # Try: npm test output, vitest, jest, pytest, cargo test
    if [ -f "package.json" ]; then
        # Look for test count in recent test output or CI badge
        npm test 2>&1 | grep -oE '[0-9,]+ (tests?|passed)' | head -1 | grep -oE '[0-9,]+'
    fi
}
```

#### The `--update-content` Flag

**Design:** A single umbrella flag that updates all install-time content from CHANGELOG.md. Zone-specific flags available for overrides. During `/release`, this is automatic.

```bash
# Update all install content from CHANGELOG
/craft:dist:homebrew cask --update-content

# Override specific zones
/craft:dist:homebrew cask --update-content \
  --desc "New description" \
  --postflight "Custom what's new text" \
  --caveats-new "Custom new-in section"

# Content-only (no version/SHA256 bump)
/craft:dist:homebrew cask --content-only

# During /release, --update-content is automatic
/release  # Step 10b auto-updates all content with preview
```

#### Flag Reference

| Flag | What it Updates | When to Use |
|------|----------------|-------------|
| `--update-content` | All 3 dynamic zones from CHANGELOG | Standalone content update |
| (automatic during `/release`) | Same as `--update-content` | Every release (Step 10b) |
| `--content-only` | Same + skip version/SHA256 bump | Fix content post-release |
| `--desc "text"` | `desc` field only (max 80 chars) | Change app description |
| `--postflight "text"` | Override "What's New" bullets | Custom postflight |
| `--caveats-new "text"` | Override "New in" bullets | Custom caveats |
| `--update-static` | Static sections with confirmation | When features/shortcuts change |

#### Version String Migration

**Decision:** Migrate hardcoded version strings to Ruby `#{version}` interpolation where possible.

Before (current):

```ruby
ohai "What's New in v1.20.0:"     # hardcoded — goes stale!
# ...
caveats <<~EOS
  New in v1.20.0:                  # hardcoded — goes stale!
```

After (migrated):

```ruby
ohai "What's New in v#{version}:"  # auto-updates on brew upgrade
# ...
caveats <<~EOS
  New in v#{version}:              # auto-updates on brew upgrade
```

**What CAN use `#{version}`:** Version display strings ("What's New in vX.Y.Z", "New in vX.Y.Z")
**What CANNOT:** Content bullets are release-specific and must be replaced mechanically.

The `--update-content` flag performs this migration automatically on first run.

#### Content Source Chain

| Content | Primary Source | Fallback |
|---------|---------------|----------|
| "What's New" bullets | CHANGELOG.md latest entry | `--postflight` flag override |
| "New in" bullets | CHANGELOG.md latest entry | `--caveats-new` flag override |
| Test count | Parsed from CHANGELOG (e.g., "2,500 tests passing") | Omitted if not found |
| `desc` field | Existing cask (preserved) | `--desc` flag or `.craft/homebrew.json` |
| Static sections | Existing cask (preserved) | `--update-static` regenerates from README |

#### Release Flow (Auto with Preview)

During `/release`, the content update runs automatically but shows a preview for confirmation:

```
┌─────────────────────────────────────────────────────────────┐
│ Step 10b: Cask Content Preview                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ postflight "What's New in v1.21.0:"                         │
│   - Dark mode with 3 new themes                             │
│   - PDF export with custom headers                          │
│   - 2,500 tests passing                                     │
│                                                             │
│ caveats "New in v1.21.0:"                                   │
│   - Dark mode with 3 new themes                             │
│   - PDF export with custom headers and footers              │
│   - Inline code highlighting in preview mode                │
│   - 2,500 tests passing                                     │
│                                                             │
│ desc: (unchanged) "ADHD-friendly distraction-free writer..."│
│                                                             │
│ Static sections: (unchanged)                                │
│   - Features: 10 items                                      │
│   - Keyboard Shortcuts: 6 items                             │
│   - Optional Dependencies: 2 items                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Looks good?                                                 │
│   ○ Yes - write to cask (Recommended)                       │
│   ○ Edit - let me modify before writing                     │
│   ○ Skip - don't update content this release                │
└─────────────────────────────────────────────────────────────┘
```

#### Static Section Update (with confirmation)

When `--update-static` is used, or `--update-content` detects that README has changed:

```
┌─────────────────────────────────────────────────────────────┐
│ Static section changes detected:                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Features (2 changes):                                       │
│   + NEW: Dark mode with 3 new themes                        │
│   ~ CHANGED: "10 ADHD-friendly themes" → "13 themes"        │
│                                                             │
│ Keyboard Shortcuts (1 change):                              │
│   + NEW: Cmd+D    Toggle dark mode                          │
│                                                             │
│ Optional Dependencies: (no changes)                          │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Apply static section updates?                               │
│   ○ Yes - update static sections                            │
│   ○ No - keep current static sections                       │
└─────────────────────────────────────────────────────────────┘
```

#### Example: Full Release Content Update

Before (v1.20.0):

```ruby
postflight do
  ohai "Scribe v#{version} installed successfully!"
  ohai ""
  ohai "What's New in v1.20.0:"
  ohai "  - Settings infrastructure (SettingsToggle, usePreferences hook)"
  ohai "  - Session timer replaced by Pomodoro focus counter"
  ohai "  - 2,280 tests passing"
```

After (v1.21.0, automated):

```ruby
postflight do
  ohai "Scribe v#{version} installed successfully!"
  ohai ""
  ohai "What's New in v1.21.0:"
  ohai "  - Dark mode with 3 new themes"
  ohai "  - PDF export with custom headers"
  ohai "  - 2,500 tests passing"
```

Before caveats (v1.20.0):

```
  New in v1.20.0:
  - Settings infrastructure (reusable SettingsToggle, usePreferences hook)
  - Session timer removed, replaced by Pomodoro focus counter in StatsPanel
  - SHORTCUTS registry (25 keyboard shortcuts, single source of truth)
  - 2,280 tests passing
```

After caveats (v1.21.0, automated):

```
  New in v1.21.0:
  - Dark mode with 3 new themes
  - PDF export with custom headers and footers
  - Inline code highlighting in preview mode
  - 2,500 tests passing
```

Static sections (Features, Keyboard Shortcuts, Optional Dependencies) remain untouched.

---

## Dependencies

| Dependency | Purpose | Required? |
|------------|---------|-----------|
| `rustup` | Rust toolchain + cross-compilation targets | Yes (for build) |
| `npm` / `npx` | Tauri CLI (`@tauri-apps/cli`) | Yes (for build) |
| `gh` | GitHub CLI for release upload | Yes |
| `shasum` | SHA256 computation | Yes (macOS built-in) |
| `ruby` | Cask file syntax check | Yes (macOS built-in) |
| `brew` | Audit and verification | Yes |
| `jq` | JSON parsing (optional, Python fallback) | No |

### Rust Target Setup

```bash
# Check installed targets
rustup target list --installed

# Install missing targets
rustup target add aarch64-apple-darwin    # Native (usually pre-installed)
rustup target add x86_64-apple-darwin     # Cross-compile (may need install)
```

---

## UI/UX Specifications

### Build Progress Display

```
┌─────────────────────────────────────────────────────────────┐
│ Step 10b: Desktop App Release (Tauri)                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1/8] Detecting project type .............. Tauri (Scribe) │
│  [2/8] Checking Rust targets ............... 2/2 installed  │
│  [3/8] Building aarch64 (native) ........... DONE (2m 14s)  │
│  [4/8] Building x86_64 (cross-compile) ..... BUILDING...    │
│        └─ Progress: Compiling scribe v1.21.0                │
│  [5/8] Collecting DMGs ..................... pending         │
│  [6/8] Uploading to GitHub release ......... pending         │
│  [7/8] Updating Homebrew Cask .............. pending         │
│  [8/8] Verifying install ................... pending         │
│                                                             │
│  Elapsed: 3m 42s                                            │
└─────────────────────────────────────────────────────────────┘
```

### Cask Update Preview (dry-run)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:homebrew cask --dry-run                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cask: scribe (Casks/scribe.rb)                             │
│  Tap:  data-wise/tap                                        │
│                                                             │
│  Changes:                                                   │
│    version:     1.20.0 → 1.21.0                             │
│    sha256 ARM:  440b3b83... → (will compute from build)     │
│    sha256 x64:  2bdf8914... → (will compute from build)     │
│    postflight:  Updated (3 items from CHANGELOG)             │
│    caveats:     Updated (version + "New in" section)         │
│                                                             │
│  No changes were made. Run without --dry-run to execute.    │
└─────────────────────────────────────────────────────────────┘
```

### Error Recovery UX

```
┌─────────────────────────────────────────────────────────────┐
│ Step 10b: Desktop App Release — ERROR                        │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  [1/8] Detecting project type .............. Tauri (Scribe) │
│  [2/8] Checking Rust targets ............... MISSING x86_64 │
│                                                             │
│  ERROR: Target x86_64-apple-darwin not installed.            │
│                                                             │
│  Fix: rustup target add x86_64-apple-darwin                  │
│                                                             │
│  Options:                                                   │
│    ○ Install target and continue (Recommended)               │
│    ○ Skip cross-compile (ARM-only release)                   │
│    ○ Abort                                                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Accessibility

- All progress output uses plain text (no emoji by default)
- Error messages include copy-pasteable fix commands
- `--dry-run` available for all operations
- Color output respects `NO_COLOR` environment variable

---

## Build Sequence (Detailed)

### Step-by-Step Build Process

```bash
# 1. Read project config
TAURI_CONF="src-tauri/tauri.conf.json"
PRODUCT_NAME=$(python3 -c "import json; print(json.load(open('$TAURI_CONF'))['productName'])")
VERSION=$(python3 -c "import json; print(json.load(open('$TAURI_CONF'))['version'])")
IDENTIFIER=$(python3 -c "import json; print(json.load(open('$TAURI_CONF'))['identifier'])")

# 2. Verify Rust targets
NATIVE_TARGET="aarch64-apple-darwin"   # Apple Silicon (native on M-series)
CROSS_TARGET="x86_64-apple-darwin"     # Intel (cross-compile)

for TARGET in "$NATIVE_TARGET" "$CROSS_TARGET"; do
    if ! rustup target list --installed | grep -q "$TARGET"; then
        echo "Installing Rust target: $TARGET"
        rustup target add "$TARGET"
    fi
done

# 3. Build native (fast — no cross-compile overhead)
echo "Building for $NATIVE_TARGET..."
npx tauri build --target "$NATIVE_TARGET"
DMG_ARM="src-tauri/target/$NATIVE_TARGET/release/bundle/dmg/${PRODUCT_NAME}_${VERSION}_aarch64.dmg"

# 4. Build cross-compile (slower)
echo "Building for $CROSS_TARGET..."
npx tauri build --target "$CROSS_TARGET"
DMG_INTEL="src-tauri/target/$CROSS_TARGET/release/bundle/dmg/${PRODUCT_NAME}_${VERSION}_x64.dmg"

# 5. Verify DMGs exist
for DMG in "$DMG_ARM" "$DMG_INTEL"; do
    if [ ! -f "$DMG" ]; then
        echo "ERROR: DMG not found at $DMG"
        # Try to locate it
        find src-tauri/target -name "*.dmg" -type f 2>/dev/null
        exit 1
    fi
done

# 6. Compute SHA256 from LOCAL files (not downloaded!)
SHA256_ARM=$(shasum -a 256 "$DMG_ARM" | cut -d' ' -f1)
SHA256_INTEL=$(shasum -a 256 "$DMG_INTEL" | cut -d' ' -f1)

# Validate
for SHA in "$SHA256_ARM" "$SHA256_INTEL"; do
    if [ -z "$SHA" ] || [ ${#SHA} -ne 64 ]; then
        echo "ERROR: SHA256 calculation failed. Got: '$SHA'"
        exit 1
    fi
done

# 7. Upload DMGs to GitHub release (--clobber handles re-uploads)
gh release upload "v${VERSION}" "$DMG_ARM" "$DMG_INTEL" --clobber

# 8. Generate CHECKSUMS.txt
echo "${SHA256_ARM}  ${PRODUCT_NAME}_${VERSION}_aarch64.dmg" > CHECKSUMS.txt
echo "${SHA256_INTEL}  ${PRODUCT_NAME}_${VERSION}_x64.dmg" >> CHECKSUMS.txt
gh release upload "v${VERSION}" CHECKSUMS.txt --clobber
```

### DMG Location Discovery

Tauri places DMGs at predictable paths, but the exact filename may vary by Tauri version:

```bash
# Primary path (Tauri v2)
src-tauri/target/{target}/release/bundle/dmg/{ProductName}_{version}_{arch}.dmg

# Fallback: search for any DMG in the target directory
find "src-tauri/target/${TARGET}/release/bundle" -name "*.dmg" -type f
```

---

## Cask Update Algorithm

### Updating an Existing Cask File

```python
# Pseudo-code for cask update
def update_cask(cask_path, version, sha256_arm, sha256_intel, changelog_items):
    content = read(cask_path)

    # 1. Update version
    content = re.sub(r'version ".*"', f'version "{version}"', content)

    # 2. Update SHA256 in on_arm block
    content = update_arch_block(content, "on_arm", sha256_arm)

    # 3. Update SHA256 in on_intel block
    content = update_arch_block(content, "on_intel", sha256_intel)

    # 4. Update postflight (replace "What's New" section)
    postflight_lines = generate_postflight(version, changelog_items)
    content = replace_postflight(content, postflight_lines)

    # 5. Update caveats (replace "New in vX.Y.Z" section)
    caveats_section = generate_caveats(version, changelog_items)
    content = replace_caveats_new_section(content, version, caveats_section)

    # 6. Validate
    write(cask_path, content)
    run("ruby -c", cask_path)  # Syntax check

    return content
```

### SHA256 Block Update (Regex)

```python
def update_arch_block(content, block_name, new_sha256):
    # Match: on_arm do\n    sha256 "..."
    # Replace only the SHA256 value within the block
    pattern = rf'({block_name} do\s+sha256 ")[a-f0-9]{{64}}(")'
    return re.sub(pattern, rf'\g<1>{new_sha256}\2', content)
```

### Tap Push with Conflict Resolution

```bash
# Navigate to tap directory
cd "$TAP_DIR"

# Pull latest (rebase to avoid merge commits)
git pull --rebase origin main || {
    echo "Rebase conflict — attempting resolution"
    # For cask files, "ours" is always correct (we just computed fresh SHA256)
    git checkout --ours "Casks/${FORMULA_NAME}.rb"
    git add "Casks/${FORMULA_NAME}.rb"
    git rebase --continue
}

# Commit and push
git add "Casks/${FORMULA_NAME}.rb"
git commit -m "${FORMULA_NAME}: update to v${VERSION}"
git push origin main
```

---

## Release Pipeline Integration

### Modified Step 10 in `/release` SKILL.md

The existing Step 10 handles Formula updates. Add Step 10b for Cask updates:

```
Step 10: Update Homebrew Tap (Formula — existing)
  └─ If Formula/{name}.rb exists → update version + SHA256

Step 10b: Update Homebrew Cask (NEW)
  └─ If Casks/{name}.rb exists OR type == "cask":
     ├─ Build: both architectures
     ├─ Upload: DMGs to GitHub release
     ├─ SHA256: from local build artifacts
     ├─ Update: Casks/{name}.rb
     ├─ Validate: ruby -c + brew audit --cask
     └─ Push: tap with conflict resolution
```

### Detection Logic in `/release`

```bash
# After Step 8 (GitHub release created), determine distribution type
if [ -f "src-tauri/tauri.conf.json" ]; then
    # Desktop app — run Step 10b
    run_cask_release "$VERSION"
elif [ -f ".craft/homebrew.json" ]; then
    TYPE=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json')).get('type', 'formula'))")
    if [ "$TYPE" = "cask" ]; then
        run_cask_release "$VERSION"
    else
        run_formula_release "$VERSION"
    fi
else
    # Default: Formula release (existing behavior)
    run_formula_release "$VERSION"
fi
```

---

## Build Environment Validation

Before any multi-arch build, validate the environment. This runs as part of Step 2 (Pre-flight) when a Tauri project is detected.

```bash
#!/bin/bash
# Pre-build validation for multi-arch Tauri builds
ERRORS=0

# Check Rust targets
for target in aarch64-apple-darwin x86_64-apple-darwin; do
    if ! rustup target list --installed | grep -q "$target"; then
        echo "MISSING: Rust target $target (fix: rustup target add $target)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check Tauri CLI
if ! command -v cargo-tauri &>/dev/null && ! npx tauri --version &>/dev/null 2>&1; then
    echo "MISSING: Tauri CLI (fix: cargo install tauri-cli)"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js
if ! command -v node &>/dev/null; then
    echo "MISSING: Node.js (fix: brew install node)"
    ERRORS=$((ERRORS + 1))
fi

# Check node_modules
if [ ! -d "node_modules" ]; then
    echo "MISSING: node_modules (fix: npm install)"
    ERRORS=$((ERRORS + 1))
fi

# Check Xcode SDK (required for cross-compilation)
if ! xcrun --sdk macosx --show-sdk-path &>/dev/null; then
    echo "MISSING: macOS SDK (fix: xcode-select --install)"
    ERRORS=$((ERRORS + 1))
fi

# Check disk space (need at least 2GB free for multi-arch builds)
FREE_MB=$(df -m . | tail -1 | awk '{print $4}')
if [ "$FREE_MB" -lt 2048 ]; then
    echo "WARNING: Low disk space (${FREE_MB}MB free, need 2048MB)"
    ERRORS=$((ERRORS + 1))
fi

if [ $ERRORS -eq 0 ]; then
    echo "Build environment validated. Ready for multi-arch build."
else
    echo "Found $ERRORS issues. Fix them before building."
    exit 1
fi
```

### Post-Build Architecture Verification

After each build, verify the DMG contains the correct binary architecture. This catches the sneakiest failure mode — a successful build that produces the wrong architecture:

```bash
# Mount DMG and verify binary architecture
verify_dmg_arch() {
    local DMG_PATH="$1"
    local EXPECTED_ARCH="$2"  # "arm64" or "x86_64"
    local APP_NAME="$3"

    local MOUNT_POINT=$(hdiutil attach "$DMG_PATH" -nobrowse -quiet -plist | \
        python3 -c "import plistlib,sys; print([e['mount-point'] for e in plistlib.load(sys.stdin.buffer)['system-entities'] if 'mount-point' in e][0])")

    ACTUAL_ARCH=$(file "$MOUNT_POINT/$APP_NAME/Contents/MacOS/"* | head -1)

    hdiutil detach "$MOUNT_POINT" -quiet

    if echo "$ACTUAL_ARCH" | grep -q "$EXPECTED_ARCH"; then
        echo "VERIFIED: $DMG_PATH contains $EXPECTED_ARCH binary"
        return 0
    else
        echo "ERROR: $DMG_PATH expected $EXPECTED_ARCH but got: $ACTUAL_ARCH"
        return 1
    fi
}
```

---

## End-to-End Verification

### Post-Release Checks (Step 13 extension)

```bash
# 13f: Cask Verification (NEW)
if [ "$DIST_TYPE" = "cask" ]; then
    # Refresh tap
    brew update

    # Verify cask info shows new version
    BREW_VERSION=$(brew info --cask "${TAP}/${FORMULA_NAME}" 2>/dev/null | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+')
    if [ "$BREW_VERSION" != "$VERSION" ]; then
        echo "WARNING: brew info shows $BREW_VERSION, expected $VERSION"
        echo "Tap may need time to propagate. Run: brew update && brew info --cask ${TAP}/${FORMULA_NAME}"
    else
        echo "Cask version verified: $BREW_VERSION"
    fi

    # Verify SHA256 in cask matches our computed values
    CASK_FILE="$TAP_DIR/Casks/${FORMULA_NAME}.rb"
    if grep -q "$SHA256_ARM" "$CASK_FILE" && grep -q "$SHA256_INTEL" "$CASK_FILE"; then
        echo "SHA256 hashes verified in cask file"
    else
        echo "WARNING: SHA256 mismatch in cask file!"
    fi

    # Optional: test install (only if user confirms — downloads DMG)
    echo "Run 'brew upgrade --cask ${TAP}/${FORMULA_NAME}' to test install"
fi
```

---

## Help and Documentation

### Command Help: `/craft:dist:homebrew cask --help`

```
USAGE:
  /craft:dist:homebrew cask [OPTIONS]

DESCRIPTION:
  Generate or update a Homebrew Cask for desktop app distribution.
  Auto-detects Tauri projects from tauri.conf.json and generates
  architecture-specific cask files with dual SHA256 hashes.

OPTIONS:
  --version <VERSION>     Specific version (default: from tauri.conf.json)
  --tap <ORG/NAME>        Homebrew tap repository (default: from .craft/homebrew.json)
  --skip-build            Don't build; use pre-built DMGs or download from release
  --dmg-arm <PATH>        Path to ARM64 DMG (requires --skip-build)
  --dmg-intel <PATH>      Path to x64 DMG (requires --skip-build)
  --content-only          Update postflight/caveats without version bump
  --dry-run               Preview changes without modifying files
  --no-verify             Skip brew audit after cask update
  --no-push               Update cask locally but don't push to tap

  Content flags:
  --update-content        Update all install-time content (postflight, caveats) from CHANGELOG
  --content-only          Same as --update-content but skip version/SHA256 bump
  --desc <TEXT>           Override cask description (max 80 chars, no "A/An" prefix)
  --postflight <TEXT>     Override "What's New" bullet points in postflight block
  --caveats-new <TEXT>    Override "New in" bullet points in caveats block
  --update-static         Regenerate static sections (Features, Shortcuts) with confirmation

EXAMPLES:
  # Generate cask from Tauri project (most common)
  /craft:dist:homebrew cask

  # Update cask to specific version
  /craft:dist:homebrew cask --version 1.21.0

  # Update from pre-built DMGs (skip build step)
  /craft:dist:homebrew cask --skip-build \
    --dmg-arm ./Scribe_1.21.0_aarch64.dmg \
    --dmg-intel ./Scribe_1.21.0_x64.dmg

  # Preview what would change
  /craft:dist:homebrew cask --dry-run

  # Update cask content only (postflight, caveats)
  # Use when: release notes or test count changed post-release
  /craft:dist:homebrew cask --content-only

  # Update Homebrew description (max 80 chars, no "A/An" prefix)
  /craft:dist:homebrew cask --desc "ADHD-friendly writer with LaTeX and Pandoc"

  # Update install-time messages with custom release notes
  /craft:dist:homebrew cask --release-notes "Dark mode, PDF export, 2500 tests"

AUTO-DETECTION:
  The command auto-detects project configuration from:
    1. .craft/homebrew.json (explicit config, highest priority)
    2. src-tauri/tauri.conf.json (Tauri project detection)
    3. Existing cask file in tap repo

  From tauri.conf.json, it extracts:
    - productName → app name and DMG naming
    - version → cask version
    - identifier → bundle ID for uninstall/zap
    - bundle.macOS.minimumSystemVersion → depends_on macos

CONFIGURATION:
  Optional .craft/homebrew.json for overrides:

  {
    "formula_name": "scribe",
    "tap": "data-wise/tap",
    "type": "cask",
    "architectures": ["aarch64", "x64"],
    "artifact_pattern": "{name}_{version}_{arch}.dmg",
    "cask": {
      "postflight_template": "changelog",
      "caveats_template": "full"
    }
  }

  All fields except formula_name and tap have smart defaults
  that are auto-detected from tauri.conf.json.

CASK FILE STRUCTURE:
  A Homebrew Cask for a Tauri desktop app contains:

  ┌─────────────────────────────────────────────┐
  │ version "1.20.0"                            │
  │                                             │
  │ on_arm do                                   │
  │   sha256 "<arm64-hash>"                     │
  │   url "https://...aarch64.dmg"              │
  │ end                                         │
  │ on_intel do                                 │
  │   sha256 "<x64-hash>"                       │
  │   url "https://...x64.dmg"                  │
  │ end                                         │
  │                                             │
  │ name, desc, homepage                        │
  │ livecheck (GitHub releases)                 │
  │ depends_on macos                            │
  │ app "Name.app"                              │
  │ postflight (what's new)                     │
  │ uninstall quit: "com.app.id"                │
  │ zap trash: [app data paths]                 │
  │ caveats (features + release notes)          │
  └─────────────────────────────────────────────┘

BUILD REQUIREMENTS:
  - Rust toolchain (rustup) with targets:
    - aarch64-apple-darwin (native on Apple Silicon)
    - x86_64-apple-darwin (cross-compilation)
  - Node.js + npm (for Tauri CLI)
  - Xcode Command Line Tools

  If a Rust target is missing, the command will offer to
  install it automatically via: rustup target add <target>

TROUBLESHOOTING:
  Cross-compile fails:
    Ensure Xcode CLT is installed: xcode-select --install
    Check Rust targets: rustup target list --installed
    Try clean build: cargo clean && npx tauri build --target <target>

  SHA256 mismatch after upload:
    This command computes SHA256 from LOCAL build artifacts,
    not downloaded files. If you see a mismatch, the upload
    may have been corrupted. Re-upload with: gh release upload --clobber

  Tap push conflict:
    The command auto-rebases before pushing. If conflicts persist:
    cd $(brew --repository)/Library/Taps/<org>/homebrew-<tap>
    git status  # Check conflict files
    git pull --rebase  # Resolve manually

  Cask audit fails:
    Run: brew audit --cask <tap>/<name>
    Common fixes:
    - desc too long (max 80 chars)
    - Missing livecheck block
    - sha256 doesn't match downloaded DMG

SEE ALSO:
  /craft:dist:homebrew formula    Generate/update Homebrew Formula
  /craft:dist:homebrew audit      Validate formula or cask
  /craft:dist:homebrew setup      Full setup wizard
  /release                        Full release pipeline (includes cask step)
```

### Documentation: Release Pipeline Guide

The following documentation should be added to `docs/guide/desktop-release.md`:

```markdown
# Desktop App Release Guide

## Overview

Craft supports releasing desktop apps (Tauri) via Homebrew Cask.
When `/release` detects a Tauri project, it automatically:

1. Builds both architectures (Apple Silicon + Intel)
2. Uploads DMGs to the GitHub release
3. Updates the Homebrew Cask with correct SHA256 hashes
4. Pushes the updated cask to your tap
5. Verifies the install path works

## Prerequisites

### Rust Toolchain

```bash
# Install Rust (if not installed)
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh

# Add cross-compilation target
rustup target add x86_64-apple-darwin
```

### Tauri CLI

```bash
npm install -g @tauri-apps/cli
# or use npx (no global install needed)
```

### Homebrew Tap

Your tap repository needs a `Casks/` directory:

```
homebrew-tap/
  ├── Formula/
  │   ├── craft.rb
  │   └── ...
  └── Casks/        ← Desktop app casks go here
      ├── scribe.rb
      └── ...
```

## Configuration

### Automatic (Recommended)

If your project has `src-tauri/tauri.conf.json`, Craft auto-detects
everything. No configuration file needed.

### Manual Override

Create `.craft/homebrew.json` for custom settings:

```json
{
  "formula_name": "my-app",
  "tap": "my-org/tap",
  "type": "cask",
  "artifact_pattern": "{name}-{version}-{arch}.dmg"
}
```

## Release Workflow

### Full Release (Recommended)

```bash
/release
# Craft detects Tauri → builds both arches → uploads → updates cask → verifies
```

### Cask-Only Update

```bash
# Update cask after manual build
/craft:dist:homebrew cask --skip-build

# Update cask content only (postflight, caveats)
/craft:dist:homebrew cask --content-only
```

### Dry-Run Preview

```bash
/release --dry-run
# Shows Step 10b plan without building or modifying anything
```

## How It Works

### Build Sequence

1. **Native build** (fast): `npx tauri build` on your current architecture
2. **Cross-compile** (slower): `npx tauri build --target x86_64-apple-darwin`
3. Both DMGs are collected from `src-tauri/target/<target>/release/bundle/dmg/`

### SHA256 Strategy

SHA256 hashes are computed from **local build artifacts**, not downloaded
from GitHub. This eliminates the race condition where CI updates the tap
with different hashes than your local build.

```
Local build → SHA256 from disk → Update cask → Push tap
                    ↑
          No network involved!
```

### Cask Content

The `postflight` and `caveats` sections are auto-generated from:

- **CHANGELOG.md**: "What's New" bullet points
- **Existing cask**: Preserved static content (features, shortcuts)
- **tauri.conf.json**: Version, app name, identifier

## Troubleshooting

### Cross-Compilation Fails

```bash
# Check installed targets
rustup target list --installed

# Install missing target
rustup target add x86_64-apple-darwin

# Clean build (if incremental build is corrupted)
cd src-tauri && cargo clean && cd ..
npx tauri build --target x86_64-apple-darwin
```

### Tap Push Conflicts

If CI also updates the tap (from a `homebrew-release.yml` workflow),
you may hit conflicts. Solutions:

1. **Disable CI workflow** for cask releases (recommended for local-first)
2. **Use `--no-push`** and push manually after resolving
3. Craft auto-rebases, but manual resolution may be needed

### DMG Not Found After Build

Tauri outputs DMGs to architecture-specific directories:

```
src-tauri/target/aarch64-apple-darwin/release/bundle/dmg/
src-tauri/target/x86_64-apple-darwin/release/bundle/dmg/
```

If the expected filename doesn't match, check your `artifact_pattern`
in `.craft/homebrew.json` or inspect the actual output:

```bash
find src-tauri/target -name "*.dmg" -type f
```

### Verifying the Release

```bash
# After release, verify cask is correct
brew update
brew info --cask data-wise/tap/scribe

# Test upgrade
brew upgrade --cask data-wise/tap/scribe
```

### Homebrew Description Management

The `--desc` flag allows updating the cask `desc` field during release. This is important because:

- `brew audit` enforces a max of 80 characters
- The description should not start with "A" or "An"
- It should be a concise, user-facing summary

**During `/release`**, the description is handled as follows:

1. Read existing desc from cask file (default: preserve)
2. If `--desc` flag provided, use override
3. If `.craft/homebrew.json` has `cask.description`, use config
4. If generating new cask, extract from `tauri.conf.json` or README first line
5. Validate: length <= 80, no "A/An" prefix
6. If validation fails, prompt user with suggested fix

**Example usage in release pipeline:**

```bash
# Release with custom description
/release --desc "ADHD-friendly distraction-free writer with LaTeX and citations"

# Or set permanently in config
# .craft/homebrew.json
{
  "cask": {
    "description": "ADHD-friendly distraction-free writer with LaTeX and citations"
  }
}
```

**Description sources (priority order):**

| Priority | Source | When Used |
|----------|--------|-----------|
| 1 | `--desc` flag | One-time override |
| 2 | `.craft/homebrew.json` → `cask.description` | Persistent config |
| 3 | Existing cask file | Update (preserve current) |
| 4 | README.md first paragraph | New cask generation |
| 5 | `tauri.conf.json` (no desc field) | N/A — Tauri has no desc |

### Reference Card Entry

Add to `docs/reference/REFCARD.md`:

```markdown
### Desktop App Distribution

| Task | Command |
|------|---------|
| Release Tauri app | `/release` (auto-detects) |
| Update cask only | `/craft:dist:homebrew cask` |
| Preview cask changes | `/craft:dist:homebrew cask --dry-run` |
| Audit cask | `/craft:dist:homebrew audit` (auto-detects) |
| Skip build | `/craft:dist:homebrew cask --skip-build --dmg-arm <path> --dmg-intel <path>` |
```

### Updated Auto-Detection Table

Update the existing table in `commands/dist/homebrew.md`:

```markdown
| Project Type | Detection | Distribution |
|--------------|-----------|--------------|
| **Tauri Desktop App** | `src-tauri/tauri.conf.json` | Cask (DMG, dual-arch) |
| **Claude Code Plugin** | `.claude-plugin/plugin.json` | Formula (source tarball) |
| Python | `pyproject.toml` | Formula (virtualenv) |
| Node.js | `package.json` | Formula (npm) |
| Go | `go.mod` | Formula (go build) |
| Rust (CLI) | `Cargo.toml` (no tauri.conf.json) | Formula (cargo) |
| Shell | `*.sh` scripts | Formula (bin.install) |
```

---

## Error Handling and Recovery

### Cross-Compilation Failure Modes

| Failure Mode | Symptom | Detection | Recovery |
|-------------|---------|-----------|----------|
| **Missing Rust target** | `can't find crate for std` | Pre-check `rustup target list --installed` | Auto: `rustup target add x86_64-apple-darwin` |
| **Missing x86_64 SDK** | `ld: library not found for -lSystem` | `xcrun --sdk macosx --show-sdk-path` | Manual: `xcode-select --install` |
| **Frontend build fails** | `RollupError: Could not resolve entry module` | Error occurs before Rust compilation | Auto: `npm install` then retry |
| **Tauri CLI version mismatch** | `CLI version doesn't match @tauri-apps/api` | Compare versions | Manual: `cargo install tauri-cli` |
| **DMG wrong architecture** | Build succeeds but binary is wrong arch | `file` command on app binary (see verification script) | Clean build: `cargo clean --target x86_64-apple-darwin` |
| **Disk space exhausted** | Build hangs or fails mid-compile | `df -m .` < 2048 MB | Manual: free disk space |
| **Tap push conflict** | `git push` rejected | Check exit code | Auto: `git pull --rebase` + retry once |
| **Upload conflict** | `gh release upload` fails (asset exists) | Check exit code | Auto: retry with `--clobber` |

### Error Recovery Strategy

```
For each step in the build pipeline:
  1. Run the step
  2. If success → continue
  3. If failure:
     a. If auto-recoverable (see table) → apply fix → retry once
     b. If retry succeeds → continue with warning
     c. If retry fails or not auto-recoverable → show error + fix command → ask user
     d. Options: [Fix and retry] [Skip step] [Abort]
```

### Rollback on Failure

| Failed At | What Needs Cleanup |
|-----------|-------------------|
| Build step | Nothing — no side effects |
| Upload step | Remove partial assets: `gh release delete-asset v{version} <filename>` |
| Cask update | Revert cask file: `git checkout -- Casks/{name}.rb` |
| Tap push | Nothing pushed — no side effects |

---

## Open Questions

1. **Cask conflicts_with**: Should we auto-generate `conflicts_with cask: "...-dev"` for dev channel support, or is that a manual setup?

2. **Codesigning**: Tauri supports macOS code signing. Should `/release` handle signing, or is that a separate concern (and should it be a prerequisite check)?

3. **Universal binary**: macOS supports universal binaries (fat binaries combining both architectures into one DMG). Should we support this as an alternative to dual-architecture DMGs?

4. **Caveats preservation**: The current caveats in Scribe's cask include a full feature list + keyboard shortcuts that don't change between releases. How much of this should be auto-generated vs preserved verbatim?

---

## Review Checklist

- [ ] Architecture: Auto-detection hierarchy is correct
- [ ] API: `.craft/homebrew.json` schema is backward-compatible
- [ ] Build: Multi-arch build sequence handles failures gracefully
- [ ] SHA256: Local computation eliminates race conditions
- [ ] Cask: Template covers all zones (version, SHA256, postflight, caveats)
- [ ] Integration: Step 10b fits into existing 13-step pipeline
- [ ] Verification: End-to-end brew install path is tested
- [ ] Docs: Command help, guide, and reference card are comprehensive
- [ ] Backward compatibility: Existing Formula workflow unaffected
- [ ] Error handling: Missing targets, build failures, tap conflicts

---

## Implementation Notes

1. **Build native first**: The native arch build is significantly faster (no cross-compile overhead). Build it first to get early feedback — if the native build fails, no point cross-compiling.

2. **SHA256 from local files is the key insight**: The Scribe v1.20.0 release had 3 rebase conflicts because CI computed SHA256 from downloaded DMGs while local pushes used different values. Computing from local build artifacts means the SHA256 is always consistent with what gets uploaded.

3. **Preserve cask structure on update**: Don't regenerate the entire cask file — parse and update only the zones that change (version, SHA256, postflight, new-in-version section of caveats). This preserves manual customizations like the full feature list in caveats.

4. **Tauri v2 DMG paths**: Tauri v2 places DMGs at `src-tauri/target/{target}/release/bundle/dmg/`. The exact filename format may vary by Tauri version and config — always search for `*.dmg` as a fallback.

5. **Ruby `-c` check is cheap insurance**: Always run `ruby -c` on the cask file after modification. It catches syntax errors (unclosed strings, bad heredocs) before pushing to the tap.

6. **The `--clobber` flag on `gh release upload`**: Essential for re-uploading DMGs when a build is re-run. Without it, the upload fails if an asset with the same name already exists.

---

## History

| Date | Change |
|------|--------|
| 2026-02-24 | Initial spec from deep brainstorm (Issue #108) |
