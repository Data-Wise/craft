# Desktop App Release Guide (Tauri/Cask)

> **TL;DR** (30 seconds)
>
> - **What:** Automated multi-arch Tauri builds + Homebrew Cask distribution
> - **Why:** Release desktop apps with a single `/release` command instead of 15 manual steps
> - **How:** Detect Tauri project → build aarch64 + x64 → upload DMGs → update cask → push tap
> - **Config:** `.craft/homebrew.json` with `"type": "cask"` (or auto-detect from `tauri.conf.json`)

---

## Overview

The desktop release pipeline extends `/craft:dist:homebrew` and the `/release` skill to support **Homebrew Cask** distribution for Tauri desktop apps. This was motivated by the Scribe v1.20.0 release, which required ~15 manual steps that are now automated.

### What's Different from Formula Releases

| Aspect | Formula (CLI tool) | Cask (Desktop app) |
|--------|-------------------|-------------------|
| **Artifact** | Source tarball (`.tar.gz`) | Pre-built DMGs (2 architectures) |
| **SHA256** | From GitHub tarball download | From local build artifacts |
| **Build** | User builds from source | Pre-built during release |
| **Architecture** | Single (source is arch-agnostic) | Dual (aarch64 + x86_64) |
| **Install location** | `/opt/homebrew/bin/` | `/Applications/` |
| **Update content** | Not applicable | postflight, caveats, desc |
| **Tap file** | `Formula/{name}.rb` | `Casks/{name}.rb` |

---

## Prerequisites

### Required Tools

| Tool | Purpose | Install |
|------|---------|---------|
| Rust toolchain | Tauri builds | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| Both Rust targets | Multi-arch builds | `rustup target add aarch64-apple-darwin x86_64-apple-darwin` |
| Tauri CLI | Build command | `cargo install tauri-cli` or `npm install @tauri-apps/cli` |
| Node.js | Frontend build | `brew install node` |
| GitHub CLI | Release upload | `brew install gh` |
| Xcode SDK | macOS compilation | `xcode-select --install` |

### Configuration

Create `.craft/homebrew.json` in your project root (optional — auto-detection works without it):

```json
{
  "formula_name": "scribe",
  "tap": "data-wise/tap",
  "type": "cask",
  "cask": {
    "app_name": "Scribe.app",
    "identifier": "com.scribe.app",
    "min_macos": "catalina"
  }
}
```

If this file is absent, the pipeline auto-detects from `src-tauri/tauri.conf.json`.

---

## Release Walkthrough

### Step 1: Run `/release`

From your project root (on `dev` branch):

```bash
/release
```

The pipeline detects `src-tauri/tauri.conf.json` and automatically routes to Step 10b (Cask release) instead of Step 10a (Formula release).

### Step 2: Build (Automatic)

The pipeline builds both architectures serially:

```
[3/8] Building aarch64 (native) ......... DONE (2m 14s)
[4/8] Building x86_64 (cross-compile) ... DONE (4m 31s)
```

Native arch builds first (faster, catches errors early). Cross-compile follows.

### Step 3: Upload + SHA256 (Automatic)

DMGs are uploaded to the GitHub release. SHA256 is computed from **local files** (not downloaded from GitHub), eliminating CDN race conditions.

### Step 4: Content Preview

The pipeline shows what will be written to the cask file:

```
postflight "What's New in v1.21.0:"
  - Dark mode with 3 new themes
  - PDF export with custom headers
  - 2,500 tests passing

caveats "New in v1.21.0:"
  - Dark mode with 3 new themes
  - PDF export with custom headers and footers
  - 2,500 tests passing

Looks good? (1) Yes  (2) Edit  (3) Skip
```

### Step 5: Verification (Automatic)

After pushing to the tap, the pipeline verifies:

- `brew info --cask` shows correct version
- SHA256 in cask file matches computed hashes
- Reports `brew install --cask` command for manual verification

---

## Standalone Cask Commands

Outside of `/release`, you can manage casks directly:

```bash
# Generate or update cask
/craft:dist:homebrew cask

# Update cask from existing release assets (no build)
/craft:dist:homebrew cask --skip-build

# Update only postflight/caveats from CHANGELOG
/craft:dist:homebrew cask --update-content

# Update content without version/SHA256 change
/craft:dist:homebrew cask --content-only

# Preview changes without writing
/craft:dist:homebrew cask --dry-run

# Validate cask file
/craft:dist:homebrew audit --cask
```

---

## Troubleshooting

### Cross-Compilation Failures

**Symptom:** `x86_64-apple-darwin` build fails with linker errors.

**Fix:** Ensure Xcode SDK is installed and both targets are registered:

```bash
xcode-select --install
rustup target add x86_64-apple-darwin
```

### DMG Not Found After Build

**Symptom:** Build succeeds but DMG path doesn't exist.

**Fix:** Tauri's DMG path varies by version. The pipeline uses fallback search:

```bash
find src-tauri/target -name "*.dmg" -type f
```

Check if the DMG naming pattern in `.craft/homebrew.json` matches.

### Tap Push Conflict

**Symptom:** `git push` fails after cask update.

**Fix:** The pipeline auto-resolves with `git pull --rebase` and "ours" strategy. If it fails twice, check if another process is pushing to the tap concurrently.

### SHA256 Mismatch in Verification

**Symptom:** Step 13f reports SHA256 mismatch after tap push.

**Fix:** Another push may have overwritten the cask. Re-run:

```bash
/craft:dist:homebrew cask --skip-build
```

### Architecture Mismatch

**Symptom:** `file` command shows wrong architecture in DMG.

**Fix:** Verify the correct `--target` flag was passed to `npx tauri build`. Check that Rust targets are installed with `rustup target list --installed`.

---

## See Also

- [Homebrew Automation Guide](homebrew-automation.md) — Formula distribution for CLI tools
- [Homebrew Quick Reference](../reference/REFCARD-HOMEBREW.md) — Command quick reference
- `/craft:dist:homebrew` command — Full command documentation (see `commands/dist/homebrew.md`)
- `/release` skill — Complete release pipeline specification (see `skills/release/SKILL.md`)
