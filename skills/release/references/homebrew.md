# Homebrew Release Reference

Detailed implementation for Step 10: Update Homebrew Tap.

## Table of Contents

- [Distribution Type Detection](#distribution-type-detection)
- [Step 10a: Update Formula](#step-10a-update-formula)
  - [Formula Name Lookup Chain](#formula-name-lookup-chain)
  - [.craft/homebrew.json Config Format](#crafthomebrewjson-config-format)
  - [Tap Update Script](#tap-update-script)
  - [Verify Homebrew Release Workflow](#verify-homebrew-release-workflow)
- [Step 10b: Desktop App Cask Release (Tauri)](#step-10b-desktop-app-cask-release-tauri)
  - [10b-1: Read Project Config](#10b-1-read-project-config)
  - [10b-2: Build Environment Validation](#10b-2-build-environment-validation)
  - [10b-3: Multi-Architecture Build (Serial)](#10b-3-multi-architecture-build-serial)
  - [10b-4: Architecture Verification](#10b-4-architecture-verification)
  - [10b-5: SHA256 Computation (Local Artifacts)](#10b-5-sha256-computation-local-artifacts)
  - [10b-6: Asset Upload to GitHub Release](#10b-6-asset-upload-to-github-release)
  - [10b-7: Cask File Update](#10b-7-cask-file-update)
  - [10b-8: Tap Push with Conflict Resolution](#10b-8-tap-push-with-conflict-resolution)
- [Step 10b Error Recovery](#step-10b-error-recovery)
- [Dry-Run Support for 10b](#dry-run-support-for-10b)

---

## Distribution Type Detection

Determine whether this is a Formula (CLI tool) or Cask (desktop app) release:

```bash
# 1. Explicit config (highest priority)
if [ -f ".craft/homebrew.json" ]; then
    DIST_TYPE=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json')).get('type', 'formula'))")
    FORMULA_NAME=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['formula_name'])")
    TAP=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['tap'])")

# 2. Tauri project auto-detection
elif [ -f "src-tauri/tauri.conf.json" ]; then
    DIST_TYPE="cask"
    FORMULA_NAME=$(python3 -c "import json; c=json.load(open('src-tauri/tauri.conf.json')); print(c.get('productName', c.get('package', {}).get('productName', 'unknown')).lower())")
    TAP="data-wise/tap"

# 3. Git remote mapping (formula default)
elif git remote get-url origin &>/dev/null; then
    DIST_TYPE="formula"
    REPO_NAME=$(git remote get-url origin | sed 's/\.git$//' | sed 's|.*/||' | tr '[:upper:]' '[:lower:]')
    FORMULA_NAME="$REPO_NAME"
    TAP="data-wise/tap"

# 4. Basename fallback (formula default)
else
    DIST_TYPE="formula"
    FORMULA_NAME=$(basename "$PWD" | tr '[:upper:]' '[:lower:]')
    TAP="data-wise/tap"
fi

# Route to appropriate step
if [ "$DIST_TYPE" = "cask" ]; then
    echo "Detected: Cask distribution (desktop app) → Step 10b"
    # Proceed to Step 10b (Cask release pipeline)
else
    echo "Detected: Formula distribution (CLI tool) → Step 10a"
    # Proceed to Step 10a (existing formula update)
fi
```

---

## Step 10a: Update Formula

For CLI tools distributed as Homebrew Formulas. This is the existing formula update path, unchanged.

### Formula Name Lookup Chain

Determine the formula name using this priority order:

1. **Config file** — `.craft/homebrew.json` (most reliable)
2. **Git remote** — extract repo name from `origin` URL
3. **Directory basename** — fallback (least reliable)

### `.craft/homebrew.json` Config Format

```json
{
  "formula_name": "craft",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

| Field | Required | Description |
|-------|----------|-------------|
| `formula_name` | Yes | Name of the Homebrew formula (e.g., `craft`, `aiterm`) |
| `tap` | Yes | Tap in `org/name` format (e.g., `data-wise/tap`) |
| `source_type` | No | `github` (default) or `pypi` |

### Tap Update Script

```bash
# Locate tap directory
TAP_ORG=$(echo "$TAP" | cut -d/ -f1)
TAP_NAME=$(echo "$TAP" | cut -d/ -f2)
TAP_LOCAL="$HOME/projects/dev-tools/homebrew-${TAP_NAME}"
TAP_BREW="$(brew --repository 2>/dev/null)/Library/Taps/${TAP_ORG}/homebrew-${TAP_NAME}"

if [ -d "$TAP_LOCAL" ]; then
    TAP_DIR="$TAP_LOCAL"
    cd "$TAP_DIR" && git pull
elif [ -d "$TAP_BREW" ]; then
    TAP_DIR="$TAP_BREW"
    cd "$TAP_DIR" && git pull
else
    echo "No local tap found — skip tap update (CI workflow handles this)"
fi

if [ -n "$TAP_DIR" ]; then
    FORMULA="$TAP_DIR/Formula/${FORMULA_NAME}.rb"
    if [ -f "$FORMULA" ]; then
        # Calculate SHA256 from GitHub release tarball
        REPO=$(git remote get-url origin | sed 's/\.git$//' | sed 's|https://github.com/||')
        SHA256=$(curl -sL --retry 3 --retry-delay 2 "https://github.com/${REPO}/archive/refs/tags/v${VERSION}.tar.gz" | shasum -a 256 | cut -d' ' -f1)

        # Validate SHA256 is not empty
        if [ -z "$SHA256" ] || [ ${#SHA256} -ne 64 ]; then
            echo "ERROR: SHA256 calculation failed. Got: '$SHA256'"
            exit 1
        fi

        # Update version and sha256 in formula
        sed -i '' "s|/archive/refs/tags/v[0-9.]*\.tar\.gz|/archive/refs/tags/v${VERSION}.tar.gz|" "$FORMULA"
        sed -i '' "s/sha256 \"[a-f0-9]*\"/sha256 \"${SHA256}\"/" "$FORMULA"

        # Syntax check before committing
        ruby -c "$FORMULA" || { echo "ERROR: Formula has syntax errors after update"; exit 1; }

        # Commit and push
        cd "$TAP_DIR"
        git add "Formula/${FORMULA_NAME}.rb"
        git commit -m "${FORMULA_NAME}: update to v${VERSION}"
        git push
        echo "Homebrew tap updated: ${FORMULA_NAME} v${VERSION}"
    fi
fi
```

Skip if no local tap exists — the GitHub Actions workflow (`homebrew-release.yml`) handles tap updates automatically on release trigger.

### Verify Homebrew Release Workflow

After the GitHub release is created, verify the `homebrew-release` workflow succeeded:

```bash
# Wait for workflow to trigger
sleep 30

# Check homebrew-release workflow status
gh run list --repo Data-Wise/craft --workflow=homebrew-release.yml --limit 1 \
  --json status,conclusion --jq '.[0]'
```

If the workflow failed, check with `/craft:ci:status` for diagnosis.

---

## Step 10b: Desktop App Cask Release (Tauri)

For desktop apps distributed as Homebrew Casks. Triggered when detection finds `src-tauri/tauri.conf.json` or `.craft/homebrew.json` has `"type": "cask"`.

**Overview:** Build multi-arch DMGs → upload to GitHub release → compute SHA256 from local artifacts → update cask file → push tap.

**Progress display:**

```
┌─────────────────────────────────────────────────────────────┐
│ Step 10b: Desktop App Release (Tauri)                        │
├─────────────────────────────────────────────────────────────┤
│  [1/8] Detecting project type ............ Tauri (Scribe)   │
│  [2/8] Checking build environment ........ 6/6 passed       │
│  [3/8] Building aarch64 (native) ......... DONE (2m 14s)    │
│  [4/8] Building x86_64 (cross-compile) ... DONE (4m 31s)    │
│  [5/8] Verifying architectures ........... PASSED            │
│  [6/8] Computing SHA256 .................. DONE              │
│  [7/8] Uploading to GitHub release ....... DONE              │
│  [8/8] Updating cask + pushing tap ....... DONE              │
└─────────────────────────────────────────────────────────────┘
```

### 10b-1: Read Project Config

```bash
# Read from tauri.conf.json
TAURI_CONF="src-tauri/tauri.conf.json"
PRODUCT_NAME=$(python3 -c "import json; c=json.load(open('$TAURI_CONF')); print(c.get('productName', c.get('package', {}).get('productName', 'unknown')))")
VERSION=$(python3 -c "import json; c=json.load(open('$TAURI_CONF')); print(c.get('version', 'unknown'))")
IDENTIFIER=$(python3 -c "import json; c=json.load(open('$TAURI_CONF')); print(c.get('identifier', c.get('tauri', {}).get('bundle', {}).get('identifier', 'unknown')))")

# Override from .craft/homebrew.json if present
if [ -f ".craft/homebrew.json" ]; then
    FORMULA_NAME=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['formula_name'])")
    TAP=$(python3 -c "import json; print(json.load(open('.craft/homebrew.json'))['tap'])")
    # Read cask-specific overrides
    CASK_CONFIG=$(python3 -c "import json; print(json.dumps(json.load(open('.craft/homebrew.json')).get('cask', {})))")
else
    FORMULA_NAME=$(echo "$PRODUCT_NAME" | tr '[:upper:]' '[:lower:]')
    TAP="data-wise/tap"
fi
```

### 10b-2: Build Environment Validation

```bash
ERRORS=0

# Check Rust targets
NATIVE_TARGET="aarch64-apple-darwin"
CROSS_TARGET="x86_64-apple-darwin"
for TARGET in "$NATIVE_TARGET" "$CROSS_TARGET"; do
    if ! rustup target list --installed | grep -q "$TARGET"; then
        echo "MISSING: Rust target $TARGET"
        echo "  Fix: rustup target add $TARGET"
        echo "  Or:  Install now and continue? (y/n)"
        ERRORS=$((ERRORS + 1))
    fi
done

# Check Tauri CLI
if ! npx tauri --version &>/dev/null 2>&1 && ! command -v cargo-tauri &>/dev/null; then
    echo "MISSING: Tauri CLI (fix: cargo install tauri-cli)"
    ERRORS=$((ERRORS + 1))
fi

# Check Node.js + node_modules
if ! command -v node &>/dev/null; then
    echo "MISSING: Node.js (fix: brew install node)"
    ERRORS=$((ERRORS + 1))
fi
if [ ! -d "node_modules" ]; then
    echo "MISSING: node_modules (fix: npm install)"
    ERRORS=$((ERRORS + 1))
fi

# Check Xcode SDK
if ! xcrun --show-sdk-path &>/dev/null 2>&1; then
    echo "MISSING: Xcode SDK (fix: xcode-select --install)"
    ERRORS=$((ERRORS + 1))
fi

# Check disk space (>= 2GB free)
FREE_KB=$(df -k . | tail -1 | awk '{print $4}')
if [ "$FREE_KB" -lt 2097152 ]; then
    echo "WARNING: Less than 2GB free disk space"
    ERRORS=$((ERRORS + 1))
fi

if [ "$ERRORS" -gt 0 ]; then
    echo "ERROR: $ERRORS pre-build checks failed. Fix and retry."
    exit 1
fi
```

### 10b-3: Multi-Architecture Build (Serial)

Build native architecture first (fast, catches errors early), then cross-compile:

```bash
# Build 1: Native arch (aarch64 on Apple Silicon)
echo "[3/8] Building aarch64 (native)..."
BUILD_START=$(date +%s)
npx tauri build --target "$NATIVE_TARGET"
BUILD_END=$(date +%s)
echo "  DONE ($((BUILD_END - BUILD_START))s)"

# Locate DMG (primary path with fallback)
DMG_ARM="src-tauri/target/$NATIVE_TARGET/release/bundle/dmg/${PRODUCT_NAME}_${VERSION}_aarch64.dmg"
if [ ! -f "$DMG_ARM" ]; then
    DMG_ARM=$(find "src-tauri/target/$NATIVE_TARGET/release/bundle" -name "*.dmg" -type f | head -1)
fi
if [ ! -f "$DMG_ARM" ]; then
    echo "ERROR: ARM DMG not found after build"
    exit 1
fi

# Build 2: Cross-compile (x86_64)
echo "[4/8] Building x86_64 (cross-compile)..."
BUILD_START=$(date +%s)
npx tauri build --target "$CROSS_TARGET"
BUILD_END=$(date +%s)
echo "  DONE ($((BUILD_END - BUILD_START))s)"

# Locate DMG
DMG_INTEL="src-tauri/target/$CROSS_TARGET/release/bundle/dmg/${PRODUCT_NAME}_${VERSION}_x64.dmg"
if [ ! -f "$DMG_INTEL" ]; then
    DMG_INTEL=$(find "src-tauri/target/$CROSS_TARGET/release/bundle" -name "*.dmg" -type f | head -1)
fi
if [ ! -f "$DMG_INTEL" ]; then
    echo "ERROR: Intel DMG not found after build"
    exit 1
fi
```

### 10b-4: Architecture Verification

Verify each DMG contains the correct architecture binary:

```bash
echo "[5/8] Verifying architectures..."
verify_arch() {
    local DMG_PATH="$1"
    local EXPECTED="$2"
    local MOUNT_POINT="/Volumes/${PRODUCT_NAME}_verify_$$"

    hdiutil attach "$DMG_PATH" -nobrowse -quiet -mountpoint "$MOUNT_POINT"
    BINARY=$(find "$MOUNT_POINT" -name "$PRODUCT_NAME" -type f -perm +111 | head -1)
    ARCH=$(file "$BINARY" | grep -oE 'arm64|x86_64')
    hdiutil detach "$MOUNT_POINT" -quiet

    if [ "$ARCH" != "$EXPECTED" ]; then
        echo "ERROR: DMG contains $ARCH binary, expected $EXPECTED"
        return 1
    fi
    echo "  ✓ $DMG_PATH → $ARCH"
}

verify_arch "$DMG_ARM" "arm64"
verify_arch "$DMG_INTEL" "x86_64"
```

### 10b-5: SHA256 Computation (Local Artifacts)

Compute SHA256 from local build artifacts — no network involved:

```bash
echo "[6/8] Computing SHA256..."
SHA256_ARM=$(shasum -a 256 "$DMG_ARM" | cut -d' ' -f1)
SHA256_INTEL=$(shasum -a 256 "$DMG_INTEL" | cut -d' ' -f1)

# Validate both are 64-char hex strings
for SHA in "$SHA256_ARM" "$SHA256_INTEL"; do
    if [ -z "$SHA" ] || [ ${#SHA} -ne 64 ]; then
        echo "ERROR: SHA256 calculation failed. Got: '$SHA'"
        exit 1
    fi
done

echo "  ARM:   $SHA256_ARM"
echo "  Intel: $SHA256_INTEL"
```

**Key design decision:** Computing SHA256 from local artifacts eliminates the race condition where GitHub CDN hasn't propagated uploaded assets yet. This was the root cause of tap conflicts during earlier Scribe releases.

### 10b-6: Asset Upload to GitHub Release

```bash
echo "[7/8] Uploading to GitHub release..."
REPO=$(git remote get-url origin | sed 's/\.git$//' | sed 's|https://github.com/||')

# Upload DMGs (--clobber handles re-uploads)
gh release upload "v${VERSION}" "$DMG_ARM" "$DMG_INTEL" --clobber

# Generate and upload CHECKSUMS.txt (use temp file to avoid polluting project root)
CHECKSUMS_TMP=$(mktemp)
echo "${SHA256_ARM}  ${PRODUCT_NAME}_${VERSION}_aarch64.dmg" > "$CHECKSUMS_TMP"
echo "${SHA256_INTEL}  ${PRODUCT_NAME}_${VERSION}_x64.dmg" >> "$CHECKSUMS_TMP"
gh release upload "v${VERSION}" "$CHECKSUMS_TMP#CHECKSUMS.txt" --clobber
rm -f "$CHECKSUMS_TMP"

# Verify upload (check URLs return 200)
for ARCH in "aarch64" "x64"; do
    URL="https://github.com/${REPO}/releases/download/v${VERSION}/${PRODUCT_NAME}_${VERSION}_${ARCH}.dmg"
    STATUS=$(curl -sI -o /dev/null -w "%{http_code}" -L "$URL")
    if [ "$STATUS" != "200" ]; then
        echo "WARNING: Asset URL returned $STATUS (CDN may need propagation time)"
    fi
done
```

### 10b-7: Cask File Update

Update the cask file with new version, SHA256 hashes, and content:

```bash
echo "[8/8] Updating cask + pushing tap..."

# Locate tap directory
TAP_ORG=$(echo "$TAP" | cut -d/ -f1)
TAP_NAME=$(echo "$TAP" | cut -d/ -f2)
TAP_LOCAL="$HOME/projects/dev-tools/homebrew-${TAP_NAME}"
TAP_BREW="$(brew --repository 2>/dev/null)/Library/Taps/${TAP_ORG}/homebrew-${TAP_NAME}"

if [ -d "$TAP_LOCAL" ]; then
    TAP_DIR="$TAP_LOCAL"
elif [ -d "$TAP_BREW" ]; then
    TAP_DIR="$TAP_BREW"
else
    echo "No local tap found — skip tap update (CI workflow handles this)"
    # Skip to Step 11
fi

CASK_FILE="$TAP_DIR/Casks/${FORMULA_NAME}.rb"

if [ -f "$CASK_FILE" ]; then
    # --- Zone 1: Update version and SHA256 ---

    # Update version field
    sed -i '' 's/version ".*"/version "'"$VERSION"'"/' "$CASK_FILE"

    # Update SHA256 in architecture blocks (regex targets block structure)
    python3 -c "
import re, sys
content = open(sys.argv[1]).read()
content = re.sub(
    r'(on_arm do\s+sha256 \")[a-f0-9]{64}(\")',
    r'\g<1>$SHA256_ARM\2', content)
content = re.sub(
    r'(on_intel do\s+sha256 \")[a-f0-9]{64}(\")',
    r'\g<1>$SHA256_INTEL\2', content)
open(sys.argv[1], 'w').write(content)
" "$CASK_FILE"

    # --- Zone 2: Migrate hardcoded version strings to #{version} ---
    sed -i '' "s/What's New in v[0-9.]*:/What's New in v#{version}:/" "$CASK_FILE"
    sed -i '' "s/New in v[0-9.]*:/New in v#{version}:/" "$CASK_FILE"

    # --- Zone 3: Dynamic content (postflight/caveats bullets) ---
    # During /release, auto-generate from CHANGELOG with preview

    # Extract changelog items for this version
    CHANGELOG_ITEMS=$(awk -v ver="$VERSION" '
        /^## / { if (found) exit; if ($0 ~ ver) found=1; next }
        found && /^- / { sub(/^- /, ""); print }
    ' CHANGELOG.md)

    TEST_COUNT=$(echo "$CHANGELOG_ITEMS" | grep -oE '[0-9,]+ tests? passing' | head -1)

    # Generate postflight bullets (max 5 items)
    POSTFLIGHT_LINES=""
    COUNT=0
    while IFS= read -r ITEM; do
        [ -z "$ITEM" ] && continue
        [ $COUNT -ge 5 ] && break
        POSTFLIGHT_LINES="${POSTFLIGHT_LINES}    ohai \"  - ${ITEM}\"\n"
        COUNT=$((COUNT + 1))
    done <<< "$CHANGELOG_ITEMS"
    if [ -n "$TEST_COUNT" ]; then
        POSTFLIGHT_LINES="${POSTFLIGHT_LINES}    ohai \"  - ${TEST_COUNT}\"\n"
    fi

    # Generate caveats bullets (all items)
    CAVEATS_LINES=""
    while IFS= read -r ITEM; do
        [ -z "$ITEM" ] && continue
        CAVEATS_LINES="${CAVEATS_LINES}    - ${ITEM}\n"
    done <<< "$CHANGELOG_ITEMS"
    if [ -n "$TEST_COUNT" ]; then
        CAVEATS_LINES="${CAVEATS_LINES}    - ${TEST_COUNT}\n"
    fi

    # Show preview and ask for confirmation
    echo ""
    echo "Content preview:"
    echo "  postflight \"What's New in v${VERSION}:\""
    echo "$POSTFLIGHT_LINES" | head -6
    echo "  caveats \"New in v${VERSION}:\""
    echo "$CAVEATS_LINES" | head -10
    echo ""
    echo "Options: (1) Yes - write to cask  (2) Edit  (3) Skip"

    # Apply content update using Python regex replacement
    python3 -c "
import re, sys

content = open(sys.argv[1]).read()
postflight = sys.argv[2]
caveats = sys.argv[3]

# Replace postflight bullets (between What's New and next empty ohai)
content = re.sub(
    r'(ohai \"What.s New in v[^\"]*:\"\n)(.*?)(    ohai \"\"\n    ohai \"(?:Quick Start|Report))',
    r'\1' + postflight + r'\3',
    content, flags=re.DOTALL)

# Replace caveats bullets (between New in and Features:/Report)
content = re.sub(
    r'(New in v[^\n]*:\n)(.*?)(\n\s*(?:Features:|Report))',
    r'\1' + caveats + r'\3',
    content, flags=re.DOTALL)

open(sys.argv[1], 'w').write(content)
" "$CASK_FILE" "$POSTFLIGHT_LINES" "$CAVEATS_LINES"

    echo "  ✓ Content: postflight + caveats updated from CHANGELOG"

    # --- Validate ---
    ruby -c "$CASK_FILE" || { echo "ERROR: Cask has syntax errors after update"; exit 1; }
    echo "  ✓ Version: updated to $VERSION"
    echo "  ✓ SHA256 (on_arm): updated"
    echo "  ✓ SHA256 (on_intel): updated"
    echo "  ✓ ruby -c: PASSED"

else
    echo "Cask file not found at $CASK_FILE"
    echo "Generate a new cask with: /craft:dist:homebrew cask"
    # Skip tap push if no cask file exists
fi
```

### 10b-8: Tap Push with Conflict Resolution

```bash
if [ -n "$TAP_DIR" ] && [ -f "$CASK_FILE" ]; then
    cd "$TAP_DIR"

    # Pull latest with rebase (avoid merge commits in tap)
    git pull --rebase origin main || {
        echo "Rebase conflict — resolving with ours (fresh SHA256 wins)"
        git checkout --ours "Casks/${FORMULA_NAME}.rb"
        git add "Casks/${FORMULA_NAME}.rb"
        GIT_EDITOR=true git rebase --continue
    }

    # Commit and push
    git add "Casks/${FORMULA_NAME}.rb"
    git commit -m "${FORMULA_NAME}: update to v${VERSION}"
    git push origin main || {
        echo "Push failed — retrying after pull"
        git pull --rebase origin main
        git push origin main
    }

    echo "  ✓ Tap push: ${TAP}/${FORMULA_NAME} v${VERSION}"
fi
```

> **Conflict resolution strategy:** "Ours" always wins because the local cask has freshly computed SHA256 hashes from local build artifacts. Any remote SHA256 values are stale by definition.

**Skip to Step 11 after Step 10b completes.**

---

## Step 10b Error Recovery

| Error | Substep | Recovery |
|-------|---------|----------|
| Missing Rust target | 10b-2 | `rustup target add <target>` (offer auto-install) |
| Missing Tauri CLI | 10b-2 | `cargo install tauri-cli` or `npm install @tauri-apps/cli` |
| Build fails (native) | 10b-3 | Check `src-tauri/` for Rust compilation errors |
| Build fails (cross-compile) | 10b-3 | Verify Xcode SDK, check for platform-specific code |
| DMG not found after build | 10b-3 | Run fallback search: `find src-tauri/target -name "*.dmg"` |
| Architecture mismatch | 10b-4 | Wrong build target used — rebuild with correct `--target` |
| SHA256 validation fails | 10b-5 | DMG file corrupt — rebuild |
| `gh release upload` fails | 10b-6 | Check `gh auth status`, verify release exists |
| Cask syntax error | 10b-7 | Check `ruby -c` output, fix regex replacement |
| Tap push conflict | 10b-8 | Auto-resolved with "ours" strategy, retry once |
| Tap push auth failure | 10b-8 | Check git credentials for tap repo |
| Cask version mismatch (13f) | 13f | Re-run `brew update`, check tap repo directly |
| SHA256 mismatch (13f) | 13f | Conflicting push overwrote cask — re-push from local |

---

## Dry-Run Support for 10b

When `/release --dry-run` detects a Tauri project, the Step 10 line expands:

```text
│ 10. ✓ Update Homebrew Cask (desktop app detected)           │
│      10b-1. Read tauri.conf.json (Scribe, v1.21.0)          │
│      10b-2. Validate build environment (6 checks)            │
│      10b-3. Build aarch64 (native)                           │
│      10b-4. Build x86_64 (cross-compile)                     │
│      10b-5. Compute SHA256 from local DMGs                   │
│      10b-6. Upload DMGs to GitHub release                    │
│      10b-7. Update Casks/scribe.rb (version + SHA256 +       │
│             content from CHANGELOG)                          │
│      10b-8. Push tap (data-wise/tap)                         │
```

`/craft:dist:homebrew cask --dry-run` shows what would change without building or writing:

```text
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:homebrew cask --dry-run                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  Cask: scribe (Casks/scribe.rb)                             │
│  Tap:  data-wise/tap                                        │
│                                                             │
│  Changes:                                                   │
│    version:     1.20.0 -> 1.21.0                            │
│    sha256 ARM:  440b3b83... -> (will compute from build)    │
│    sha256 x64:  2bdf8914... -> (will compute from build)    │
│    postflight:  Updated (3 items from CHANGELOG)            │
│    caveats:     Updated (version + "New in" section)        │
│    desc:        (unchanged)                                 │
│    static:      (unchanged)                                 │
│                                                             │
│  No changes were made. Run without --dry-run to execute.    │
└─────────────────────────────────────────────────────────────┘
```
