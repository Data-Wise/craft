---
description: Complete Homebrew automation - formulas, casks, workflows, auditing, and dependency management
arguments:
  - name: subcommand
    description: "Subcommand: formula|cask|workflow|audit|setup|update-resources|deps"
    required: false
    default: formula
  - name: tap
    description: "Homebrew tap repository (e.g., user/tap)"
    required: false
  - name: version
    description: "Specific version to use (default: latest tag)"
    required: false
---

# /craft:dist:homebrew - Homebrew Automation Hub

Complete Homebrew formula management with automated workflows.

## Subcommands

| Command | Purpose |
|---------|---------|
| `formula` | Generate or update formula (default) |
| `cask` | Generate or update Homebrew Cask for desktop apps (Tauri) |
| `workflow` | Generate GitHub Actions release workflow |
| `audit` | Run `brew audit` validation + auto-fix (formula or cask) |
| `setup` | Full setup wizard (formula/cask + workflow + token) |
| `update-resources` | Fix stale PyPI resource URLs |
| `deps` | Show formula dependency graph + system deps matrix |

## Quick Start

```bash
# Generate formula for current project
/craft:dist:homebrew

# Generate or update cask for Tauri desktop app
/craft:dist:homebrew cask

# Full automated setup (recommended for new projects)
/craft:dist:homebrew setup

# Generate release workflow
/craft:dist:homebrew workflow

# Validate formula or cask before release
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

Detects project type and generates appropriate formula or cask:

| Project Type | Detection | Distribution |
|--------------|-----------|--------------|
| **Tauri Desktop App** | `src-tauri/tauri.conf.json` | Cask (DMG, dual-arch) |
| **Claude Code Plugin** | `.claude-plugin/plugin.json` | Formula (`libexec.install` + plugin scripts) |
| Python | `pyproject.toml` | Formula (`Language::Python::Virtualenv`) |
| Node.js | `package.json` | Formula (npm install pattern) |
| Go | `go.mod` | Formula (go build pattern) |
| Rust | `Cargo.toml` | Formula (cargo install pattern) |
| Shell | `*.sh` scripts | Formula (bin.install pattern) |

> **Detection priority:** `.craft/homebrew.json` config (explicit) > Tauri Desktop App > Claude Code Plugin > Python > Node.js > Go > Rust > Shell. Config file always wins. Tauri takes precedence over Plugin because desktop apps require fundamentally different distribution (Cask with DMGs vs Formula with source tarballs).

### Example Output

```
✓ Detected: Python project (pyproject.toml)
✓ Found version: 0.3.5 (from git tag)
✓ Calculated SHA256: abc123...
✓ Generated: Formula/myapp.rb

Formula saved to: ./Formula/myapp.rb
```

---

## /craft:dist:homebrew cask

Generate or update a Homebrew Cask for desktop apps (Tauri). Handles multi-architecture DMGs, SHA256 computation from local artifacts, and release-specific content (postflight, caveats).

### Usage

```bash
/craft:dist:homebrew cask                          # Auto-detect and create/update
/craft:dist:homebrew cask --tap user/tap           # Specify target tap
/craft:dist:homebrew cask --version 1.2.0          # Use specific version
/craft:dist:homebrew cask --skip-build             # Update cask from existing release assets
/craft:dist:homebrew cask --update-content         # Update postflight/caveats from CHANGELOG
/craft:dist:homebrew cask --content-only           # Update content only (skip version/SHA256)
/craft:dist:homebrew cask --dry-run                # Preview changes without writing
```

### Auto-Detection

Detects Tauri desktop app projects and extracts metadata:

```
Detection Chain:
1. .craft/homebrew.json  →  { "type": "cask" }     (explicit config, highest priority)
2. src-tauri/tauri.conf.json  →  productName, version, identifier  (auto-detect)
3. Casks/ in tap repo  →  existing cask file      (tap structure)
```

When `src-tauri/tauri.conf.json` is found, the following fields are extracted:

| tauri.conf.json Field | Used For |
|-----------------------|----------|
| `productName` | Cask `app` name, DMG naming |
| `version` | Cask `version` field |
| `identifier` | macOS bundle identifier |
| `bundle.macOS.minimumSystemVersion` | Cask `depends_on macos:` |

### Flags

| Flag | Description |
|------|-------------|
| `--tap` | Target tap repository (e.g., `data-wise/tap`) |
| `--version` | Specific version (default: from tauri.conf.json or latest tag) |
| `--skip-build` | Skip build, use existing DMGs (from release assets or local paths) |
| `--update-content` | Update postflight/caveats from CHANGELOG (all dynamic zones) |
| `--content-only` | Same as `--update-content` but skip version/SHA256 changes |
| `--desc "text"` | Override cask `desc` field (validates <= 80 chars, no "A/An" prefix) |
| `--postflight "text"` | Override "What's New" bullets in postflight zone |
| `--caveats-new "text"` | Override "New in" bullets in caveats zone |
| `--update-static` | Update static sections (Features, Shortcuts) with confirmation |
| `--dry-run` | Preview all changes without writing files |

### Extended `.craft/homebrew.json` Schema

The existing config file supports a new `"type": "cask"` field and a `"cask"` nested object for desktop app projects:

```json
{
  "formula_name": "scribe",
  "tap": "data-wise/tap",
  "type": "cask",
  "cask": {
    "app_name": "Scribe.app",
    "identifier": "com.scribe.app",
    "min_macos": "catalina",
    "architectures": ["aarch64", "x64"],
    "artifact_pattern": "{name}_{version}_{arch}.dmg",
    "build_command": "npx tauri build --target {target}",
    "targets": {
      "aarch64": "aarch64-apple-darwin",
      "x64": "x86_64-apple-darwin"
    },
    "postflight_template": "changelog",
    "caveats_template": "full"
  }
}
```

| Field | Required | Default | Description |
|-------|----------|---------|-------------|
| `formula_name` | Yes | — | Name in tap (used for both formula and cask) |
| `tap` | Yes | — | Tap in `org/name` format |
| `type` | No | `"formula"` | `"formula"` or `"cask"` |
| `cask.app_name` | No | from `tauri.conf.json` productName + `.app` | `.app` bundle name |
| `cask.identifier` | No | from `tauri.conf.json` identifier | macOS bundle identifier |
| `cask.min_macos` | No | from `tauri.conf.json` minimumSystemVersion | Homebrew macOS codename |
| `cask.architectures` | No | `["aarch64", "x64"]` | Architectures to build |
| `cask.artifact_pattern` | No | `"{name}_{version}_{arch}.dmg"` | DMG naming pattern |
| `cask.build_command` | No | `"npx tauri build --target {target}"` | Build command template |
| `cask.targets` | No | `{"aarch64": "aarch64-apple-darwin", "x64": "x86_64-apple-darwin"}` | Rust target triple mapping |
| `cask.postflight_template` | No | `"changelog"` | `"changelog"` or `"none"` |
| `cask.caveats_template` | No | `"full"` | `"full"`, `"minimal"`, or `"none"` |

> **Backward compatibility:** Existing `.craft/homebrew.json` files without a `"type"` field default to `"formula"`. No changes needed for existing formula-based projects.

### macOS Version Mapping

When auto-detecting from `tauri.conf.json`, the `minimumSystemVersion` is mapped to Homebrew codenames:

| macOS Version | Homebrew Codename |
|---------------|-------------------|
| `10.13` | `:high_sierra` |
| `10.14` | `:mojave` |
| `10.15` | `:catalina` |
| `11.0` | `:big_sur` |
| `12.0` | `:monterey` |
| `13.0` | `:ventura` |
| `14.0` | `:sonoma` |
| `15.0` | `:sequoia` |

### Build Environment Validation

Before building, the `cask` subcommand validates the environment. This runs as a pre-flight check and offers to auto-install missing components.

| Check | What | Fix |
|-------|------|-----|
| Rust targets | `aarch64-apple-darwin` + `x86_64-apple-darwin` installed | `rustup target add <target>` |
| Tauri CLI | `npx tauri --version` or `cargo-tauri` available | `cargo install tauri-cli` |
| Node.js | `node` in PATH | `brew install node` |
| node_modules | `node_modules/` directory exists | `npm install` |
| Xcode SDK | `xcrun --show-sdk-path` succeeds | `xcode-select --install` |
| Disk space | >= 2GB free in project directory | Manual cleanup |

```
Pre-build validation:
  ✓ Rust target aarch64-apple-darwin .......... installed
  ✓ Rust target x86_64-apple-darwin ........... installed
  ✓ Tauri CLI .................................. v2.1.0 (npx)
  ✓ Node.js .................................... v22.5.0
  ✓ node_modules ............................... present
  ✓ Xcode SDK .................................. /Applications/Xcode.app/...
  ✓ Disk space ................................. 45GB free

All checks passed. Ready to build.
```

If a Rust target is missing, the user is offered:

```
WARNING: Rust target x86_64-apple-darwin not installed.

Options:
  1. Install target and continue (Recommended)
     → rustup target add x86_64-apple-darwin
  2. Skip cross-compile (ARM-only release)
  3. Abort
```

### Multi-Architecture Build Sequence

Builds are executed **serially** (not parallel) to avoid memory exhaustion on developer machines. Native architecture builds first for faster error detection.

```bash
# Step 1: Build native arch (fast, catches errors early)
npx tauri build --target aarch64-apple-darwin

# Step 2: Build cross-compile (slower)
npx tauri build --target x86_64-apple-darwin
```

#### DMG Location Discovery

Tauri places DMGs at predictable paths. The build locates them using a primary path with fallback search:

```bash
# Primary path (Tauri v2)
src-tauri/target/{target}/release/bundle/dmg/{ProductName}_{version}_{arch}.dmg

# Fallback: search for any DMG in the target directory
find "src-tauri/target/${TARGET}/release/bundle" -name "*.dmg" -type f
```

#### Architecture Verification

After building, verify each DMG contains the correct architecture binary:

```bash
# Mount DMG and check binary architecture
hdiutil attach "$DMG_PATH" -nobrowse -quiet
BINARY=$(find /Volumes/"${PRODUCT_NAME}" -name "${PRODUCT_NAME}" -type f | head -1)
ARCH=$(file "$BINARY" | grep -oE 'arm64|x86_64')
hdiutil detach /Volumes/"${PRODUCT_NAME}" -quiet

# Verify expected architecture
if [ "$ARCH" != "$EXPECTED_ARCH" ]; then
    echo "ERROR: DMG contains $ARCH binary, expected $EXPECTED_ARCH"
    exit 1
fi
```

### SHA256 Computation (Local Artifacts)

SHA256 is computed from **local build artifacts**, not downloaded from GitHub. This eliminates the race condition where GitHub CDN hasn't propagated the asset yet.

```bash
# Compute SHA256 from local DMG files
SHA256_ARM=$(shasum -a 256 "$DMG_ARM" | cut -d' ' -f1)
SHA256_INTEL=$(shasum -a 256 "$DMG_INTEL" | cut -d' ' -f1)

# Validate both are 64-char hex strings
for SHA in "$SHA256_ARM" "$SHA256_INTEL"; do
    if [ -z "$SHA" ] || [ ${#SHA} -ne 64 ]; then
        echo "ERROR: SHA256 calculation failed. Got: '$SHA'"
        exit 1
    fi
done
```

### Asset Upload to GitHub Release

Upload DMGs and a CHECKSUMS.txt file to the GitHub release:

```bash
# Upload DMGs (--clobber handles re-uploads if assets already exist)
gh release upload "v${VERSION}" "$DMG_ARM" "$DMG_INTEL" --clobber

# Generate and upload CHECKSUMS.txt (use temp file to avoid polluting project root)
CHECKSUMS_TMP=$(mktemp)
echo "${SHA256_ARM}  ${PRODUCT_NAME}_${VERSION}_aarch64.dmg" > "$CHECKSUMS_TMP"
echo "${SHA256_INTEL}  ${PRODUCT_NAME}_${VERSION}_x64.dmg" >> "$CHECKSUMS_TMP"
gh release upload "v${VERSION}" "$CHECKSUMS_TMP#CHECKSUMS.txt" --clobber
rm -f "$CHECKSUMS_TMP"

# Verify both DMG URLs return 200
for ARCH in "aarch64" "x64"; do
    URL="https://github.com/${REPO}/releases/download/v${VERSION}/${PRODUCT_NAME}_${VERSION}_${ARCH}.dmg"
    STATUS=$(curl -sI -o /dev/null -w "%{http_code}" -L "$URL")
    if [ "$STATUS" != "200" ]; then
        echo "WARNING: Asset URL returned $STATUS (may need CDN propagation time)"
    fi
done
```

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
│  [5/8] Verifying architectures ............. pending         │
│  [6/8] Computing SHA256 .................... pending         │
│  [7/8] Uploading to GitHub release ......... pending         │
│  [8/8] Updating cask + pushing tap ......... pending         │
│                                                             │
│  Elapsed: 3m 42s                                            │
└─────────────────────────────────────────────────────────────┘
```

### Cask Template (New Cask Generation)

When no cask file exists, generate one from the Tauri project. The template includes all zones: architecture, livecheck, postflight, uninstall, zap, and caveats.

```ruby
cask "{name}" do
  version "{version}"

  # ZONE: architecture (auto-generated, updated every release)
  on_arm do
    sha256 "{sha256_arm}"
    url "https://github.com/{repo}/releases/download/v#{version}/{name}_{arch_arm}.dmg"
  end
  on_intel do
    sha256 "{sha256_intel}"
    url "https://github.com/{repo}/releases/download/v#{version}/{name}_{arch_intel}.dmg"
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

  # ZONE: postflight (dynamic — auto-generated from CHANGELOG)
  postflight do
    ohai "{display_name} v#{version} installed successfully!"
    ohai ""
    ohai "What's New in v#{version}:"
    # --- dynamic bullets (replaced by --update-content) ---
    ohai "  - Initial release"
    # --- end dynamic bullets ---
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

  # ZONE: caveats (dynamic + static — auto-generated)
  caveats <<~EOS
    {display_name} v#{version} — {description}

    New in v#{version}:
    - Initial release

    Report issues: https://github.com/{repo}/issues
  EOS
end
```

#### Template Variables

| Variable | Source | Example |
|----------|--------|---------|
| `{name}` | config `formula_name` or repo name | `scribe` |
| `{version}` | tauri.conf.json or `--version` | `1.20.0` |
| `{sha256_arm}` | `shasum -a 256` of ARM DMG | `440b3b83...` |
| `{sha256_intel}` | `shasum -a 256` of Intel DMG | `2bdf8914...` |
| `{repo}` | git remote origin | `Data-Wise/scribe` |
| `{display_name}` | tauri.conf.json `productName` | `Scribe` |
| `{description}` | `--desc` flag or preserved from existing | `ADHD-friendly writer` |
| `{app_name}` | productName + `.app` | `Scribe.app` |
| `{identifier}` | tauri.conf.json `identifier` | `com.scribe.app` |
| `{min_macos}` | mapped from `minimumSystemVersion` | `catalina` |

### Cask File Updater (Existing Cask)

When a cask file already exists, the updater modifies specific zones without regenerating the entire file. This preserves customizations in static sections.

#### Update Algorithm

The updater operates on 3 independent zones:

```
1. Version + SHA256 (always updated)
   ├─ version "X.Y.Z"
   ├─ on_arm { sha256 "..." }
   └─ on_intel { sha256 "..." }

2. Dynamic content (updated with --update-content or during /release)
   ├─ postflight "What's New" bullets
   └─ caveats "New in" bullets

3. Static content (updated only with --update-static)
   ├─ postflight "Quick Start" section
   ├─ caveats "Features" list
   └─ caveats "Keyboard Shortcuts" list
```

#### Zone 1: Version and SHA256 Update

```bash
# Update version field
sed -i '' 's/version ".*"/version "'"$VERSION"'"/' "$CASK_FILE"

# Update SHA256 in on_arm block (regex targets the block structure)
# Match: on_arm do\n    sha256 "..." → replace hash only
python3 -c "
import re, sys
content = open(sys.argv[1]).read()

# Update on_arm SHA256
content = re.sub(
    r'(on_arm do\s+sha256 \")[a-f0-9]{64}(\")',
    r'\g<1>${SHA256_ARM}\2',
    content
)

# Update on_intel SHA256
content = re.sub(
    r'(on_intel do\s+sha256 \")[a-f0-9]{64}(\")',
    r'\g<1>${SHA256_INTEL}\2',
    content
)

open(sys.argv[1], 'w').write(content)
" "$CASK_FILE"
```

#### Zone 2: Version String Migration

On first run, migrate hardcoded version strings to Ruby `#{version}` interpolation:

```bash
# Before: ohai "What's New in v1.20.0:"
# After:  ohai "What's New in v#{version}:"
sed -i '' "s/What's New in v[0-9.]*:/What's New in v#{version}:/" "$CASK_FILE"

# Before: New in v1.20.0:
# After:  New in v#{version}:
sed -i '' "s/New in v[0-9.]*:/New in v#{version}:/" "$CASK_FILE"
```

After migration, Homebrew handles version display automatically during `brew install`/`brew upgrade`.

#### Cask Validation

After any modification, validate the cask file:

```bash
# Ruby syntax check (fast, catches missing quotes/brackets)
ruby -c "$CASK_FILE" || { echo "ERROR: Cask has syntax errors"; exit 1; }

# Homebrew audit (thorough, checks field lengths, livecheck, etc.)
brew audit --cask "$FORMULA_NAME" 2>&1
```

### Tap Push with Conflict Resolution

After updating the cask file, push to the tap repository with rebase-based conflict resolution:

```bash
TAP_ORG=$(echo "$TAP" | cut -d/ -f1)
TAP_NAME=$(echo "$TAP" | cut -d/ -f2)
TAP_LOCAL="$HOME/projects/dev-tools/homebrew-${TAP_NAME}"
TAP_BREW="$(brew --repository 2>/dev/null)/Library/Taps/${TAP_ORG}/homebrew-${TAP_NAME}"

# Find tap directory
if [ -d "$TAP_LOCAL" ]; then
    TAP_DIR="$TAP_LOCAL"
elif [ -d "$TAP_BREW" ]; then
    TAP_DIR="$TAP_BREW"
else
    echo "No local tap found — skip (CI workflow handles this)"
    exit 0
fi

cd "$TAP_DIR"

# Pull latest with rebase (avoid merge commits)
git pull --rebase origin main || {
    echo "Rebase conflict — resolving with ours (freshly computed SHA256 wins)"
    git checkout --ours "Casks/${FORMULA_NAME}.rb"
    git add "Casks/${FORMULA_NAME}.rb"
    GIT_EDITOR=true git rebase --continue
}

# Stage, commit, and push
git add "Casks/${FORMULA_NAME}.rb"
git commit -m "${FORMULA_NAME}: update to v${VERSION}"
git push origin main || {
    echo "Push failed — retrying after pull"
    git pull --rebase origin main
    git push origin main
}

echo "Tap updated: ${TAP}/${FORMULA_NAME} v${VERSION}"
```

> **Why "ours" wins on conflict:** During a release, the local cask file has freshly computed SHA256 hashes from local build artifacts. Any remote changes to SHA256 are stale by definition. Content conflicts (postflight/caveats) are also resolved with "ours" since we just generated them from the latest CHANGELOG.

### Content Update (`--update-content`)

The `--update-content` flag updates all dynamic install-time content from CHANGELOG.md. This is the mechanism that keeps postflight "What's New" and caveats "New in" sections current across releases.

#### How It Works

```
--update-content pipeline:

1. Parse CHANGELOG.md → extract bullets for current version
2. Extract test count (if present in CHANGELOG)
3. Generate postflight bullets (max 5 items + test count)
4. Generate caveats bullets (all items + test count)
5. Show preview of all changes
6. Write on confirmation (or automatically during /release)
```

#### CHANGELOG Parsing

Extracts bullet points from the latest version entry:

```bash
# Extract items from CHANGELOG.md for a given version
extract_changelog_items() {
    local VERSION="$1"
    local CHANGELOG="${2:-CHANGELOG.md}"

    # Find version header, collect lines until next version header
    awk -v ver="$VERSION" '
        /^## / { if (found) exit; if ($0 ~ ver) found=1; next }
        found && /^- / { sub(/^- /, ""); print }
    ' "$CHANGELOG"
}

# Extract test count from CHANGELOG pattern like "X,XXX tests passing"
extract_test_count() {
    local VERSION="$1"
    local CHANGELOG="${2:-CHANGELOG.md}"

    awk -v ver="$VERSION" '
        /^## / { if (found) exit; if ($0 ~ ver) found=1; next }
        found && /[0-9,]+ tests? passing/ {
            match($0, /[0-9,]+[ ]+tests? passing/)
            print substr($0, RSTART, RLENGTH)
            exit
        }
    ' "$CHANGELOG"
}
```

#### Postflight Bullet Generation

Postflight is shown **during** `brew install`/`brew upgrade`. Keep it short (max 5 items):

```bash
# Generate ohai lines for the postflight block
generate_postflight() {
    local VERSION="$1"
    local ITEMS=($(extract_changelog_items "$VERSION"))
    local TEST_COUNT=$(extract_test_count "$VERSION")
    local COUNT=0

    for ITEM in "${ITEMS[@]}"; do
        [ $COUNT -ge 5 ] && break
        echo "    ohai \"  - $ITEM\""
        COUNT=$((COUNT + 1))
    done

    if [ -n "$TEST_COUNT" ]; then
        echo "    ohai \"  - $TEST_COUNT\""
    fi
}
```

#### Caveats Bullet Generation

Caveats are shown **after** install. Can include all items (no limit):

```bash
# Generate bullet lines for the caveats "New in" section
generate_caveats() {
    local VERSION="$1"
    local ITEMS=($(extract_changelog_items "$VERSION"))
    local TEST_COUNT=$(extract_test_count "$VERSION")

    for ITEM in "${ITEMS[@]}"; do
        echo "    - $ITEM"
    done

    if [ -n "$TEST_COUNT" ]; then
        echo "    - $TEST_COUNT"
    fi
}
```

#### Content Replacement Algorithm

Replace dynamic bullets between known markers in the cask file:

```python
# Postflight: replace between "What's New" and the next empty ohai line
import re

def replace_postflight_bullets(content, new_bullets):
    """Replace release-specific bullets in postflight block."""
    # Match: ohai "What's New..." through the next ohai "" (before Quick Start or Report)
    pattern = r'(ohai "What\'s New in v[^"]*:"\n)(.*?)(    ohai ""\n    ohai "(?:Quick Start|Report))'
    replacement = r'\1' + new_bullets + r'\n\3'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)

def replace_caveats_bullets(content, new_bullets):
    """Replace release-specific bullets in caveats block."""
    # Match: "New in v..." through the next blank line or "Features:" marker
    pattern = r'(New in v[^\n]*:\n)(.*?)(\n\s*(?:Features:|Report|$))'
    replacement = r'\1' + new_bullets + r'\n\3'
    return re.sub(pattern, replacement, content, flags=re.DOTALL)
```

#### Content Source Chain

| Content | Primary Source | Fallback |
|---------|---------------|----------|
| "What's New" bullets | CHANGELOG.md latest entry | `--postflight` flag override |
| "New in" bullets | CHANGELOG.md latest entry | `--caveats-new` flag override |
| Test count | Parsed from CHANGELOG (e.g., "2,500 tests passing") | Omitted if not found |
| `desc` field | Existing cask (preserved) | `--desc` flag or `.craft/homebrew.json` |
| Static sections | Existing cask (preserved) | `--update-static` regenerates |

#### Flag Reference

| Flag | What it Updates | When to Use |
|------|----------------|-------------|
| `--update-content` | All dynamic zones from CHANGELOG | Standalone content update |
| (automatic during `/release`) | Same as `--update-content` | Every release (Step 10b) |
| `--content-only` | Same + skip version/SHA256 bump | Fix content post-release |
| `--desc "text"` | `desc` field only (max 80 chars) | Change app description |
| `--postflight "text"` | Override "What's New" bullets | Custom postflight |
| `--caveats-new "text"` | Override "New in" bullets | Custom caveats |
| `--update-static` | Static sections with confirmation | When features/shortcuts change |

#### Content Preview (during `/release`)

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
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Looks good?                                                 │
│   1. Yes - write to cask (Recommended)                      │
│   2. Edit - let me modify before writing                    │
│   3. Skip - don't update content this release               │
└─────────────────────────────────────────────────────────────┘
```

#### Static Section Update (`--update-static`)

Static sections (Features, Keyboard Shortcuts, Optional Dependencies) rarely change. When `--update-static` is used, changes are shown as a diff with confirmation:

```
┌─────────────────────────────────────────────────────────────┐
│ Static section changes detected:                             │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Features (2 changes):                                       │
│   + NEW: Dark mode with 3 new themes                        │
│   ~ CHANGED: "10 ADHD-friendly themes" -> "13 themes"       │
│                                                             │
│ Keyboard Shortcuts (1 change):                              │
│   + NEW: Cmd+D    Toggle dark mode                          │
│                                                             │
│ Optional Dependencies: (no changes)                         │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Apply static section updates?                               │
│   1. Yes - update static sections                           │
│   2. No - keep current static sections                      │
└─────────────────────────────────────────────────────────────┘
```

### Example Output

```
✓ Detected: Tauri Desktop App (src-tauri/tauri.conf.json)
✓ Product: Scribe (com.scribe.app)
✓ Version: 1.20.0
✓ Architectures: aarch64, x64
✓ Config: .craft/homebrew.json (type: cask)
✓ Tap: data-wise/tap

Build:
  ✓ aarch64 (native) ............. DONE (2m 14s)
  ✓ x86_64 (cross-compile) ....... DONE (4m 31s)
  ✓ Architecture verification ..... PASSED (arm64, x86_64)

SHA256:
  ARM:   440b3b83e7f29a2b...
  Intel: 2bdf8914a1c7e6d3...

Upload:
  ✓ Scribe_1.20.0_aarch64.dmg .... uploaded
  ✓ Scribe_1.20.0_x64.dmg ........ uploaded
  ✓ CHECKSUMS.txt ................. uploaded

Cask update:
  ✓ Version ....................... 1.19.0 → 1.20.0
  ✓ SHA256 (on_arm) .............. updated
  ✓ SHA256 (on_intel) ............ updated
  ✓ Version strings .............. migrated to #{version}
  ✓ ruby -c ...................... PASSED
  ✓ Tap push ..................... data-wise/tap updated

Cask file: Casks/scribe.rb
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

Validate and auto-fix formulas and casks using `brew audit`. Auto-detects whether the project uses a formula or cask.

### Usage

```bash
/craft:dist:homebrew audit                      # Auto-detect formula or cask, validate + auto-fix
/craft:dist:homebrew audit --strict             # Strict mode (extra checks)
/craft:dist:homebrew audit --online             # Online checks (URL validation)
/craft:dist:homebrew audit --check-only         # Report issues without fixing
/craft:dist:homebrew audit --build              # Also run brew install --build-from-source
/craft:dist:homebrew audit --cask               # Force cask audit mode
```

### Auto-Detection (Formula vs Cask)

The audit command auto-detects whether to run formula or cask audit:

```bash
# Detection priority:
# 1. --cask flag → cask audit
# 2. .craft/homebrew.json type == "cask" → cask audit
# 3. src-tauri/tauri.conf.json exists → cask audit
# 4. Casks/ directory in tap → cask audit
# 5. Default → formula audit
```

### Formula Checks

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

### Cask Checks

| Check | Description | Auto-Fix |
|-------|-------------|----------|
| Syntax | Ruby syntax validation (`ruby -c`) | No |
| `desc` | < 80 chars, no 'A/An' prefix | Yes - truncate |
| `version` | Present and valid | No |
| `sha256` | Present in both `on_arm`/`on_intel` blocks, 64-char hex | No |
| `url` | Accessible in both architecture blocks (with --online) | No |
| `livecheck` | Block present with valid strategy | No |
| `app` | `.app` bundle name matches productName | No |
| `uninstall` | `quit:` with valid bundle identifier | No |
| `zap` | `trash:` paths use correct identifier | No |
| `depends_on` | Valid macOS codename | No |
| `postflight` | Block present (if cask has install-time content) | No |

### Cask Audit Workflow

```bash
# 1. Auto-detect cask
FORMULA_NAME=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['formula_name'])" 2>/dev/null)

# 2. Run brew audit --cask
brew audit --cask "$TAP/$FORMULA_NAME" 2>&1

# 3. Check SHA256 matches actual release assets (cross-verify)
CASK_FILE=$(brew --repository)/Library/Taps/${TAP_ORG}/homebrew-${TAP_NAME}/Casks/${FORMULA_NAME}.rb
CASK_SHA=$(grep -A1 'on_arm' "$CASK_FILE" | grep sha256 | grep -oE '[a-f0-9]{64}')
# Compare with actual DMG SHA if available

# 4. Validate livecheck
brew livecheck --cask "$TAP/$FORMULA_NAME" 2>&1

# 5. Report results
```

### Cask Audit Example Output

```
Running: brew audit --cask data-wise/tap/scribe

Cask audit results:
  ✓ Ruby syntax ........................ PASSED
  ✓ desc length ........................ 62 chars (max 80)
  ✓ version ............................ 1.20.0
  ✓ SHA256 (on_arm) ................... 64 chars, valid hex
  ✓ SHA256 (on_intel) ................. 64 chars, valid hex
  ✓ livecheck .......................... configured (github_releases)
  ✓ app ................................ Scribe.app
  ✓ uninstall .......................... quit: com.scribe.app
  ✓ zap ................................ 5 trash paths
  ✓ depends_on ........................ macos: >= :catalina

All checks passed. Cask is ready for release!
```

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
desc "Full-stack developer toolkit - 107 commands, 8 agents, 26 skills - Claude Code plugin"
# After:
desc "Full-stack developer toolkit for Claude Code with 107 commands"

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

    # Step 2: Run install script with 30s timeout
    begin
      require "timeout"
      pid = Process.spawn("#{bin}/my-plugin-install")
      Timeout.timeout(30) { Process.waitpid(pid) }
    rescue Timeout::Error
      Process.kill("TERM", pid) rescue nil
      Process.waitpid(pid) rescue nil
      opoo "my-plugin-install timed out after 30 seconds (skipping)"
    rescue
      nil
    end

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
| `craft.rb` | 107 commands | `brew audit --strict` clean |
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
