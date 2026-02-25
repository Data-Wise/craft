# Desktop Release Pipeline Architecture

> **Scope:** This document covers the architecture of the desktop app release pipeline — how `/release` auto-routes to Step 10b, how `/craft:dist:homebrew cask` works, and how the system's components fit together. For usage walkthroughs, see the [Desktop Release Guide](../guide/desktop-release.md). For command syntax, see the [Homebrew Quick Reference](../reference/REFCARD-HOMEBREW.md).

---

## 1. System Overview

The desktop release pipeline adds Homebrew Cask distribution for Tauri apps to an existing formula-only release system. The key design constraint was **backward compatibility**: formula-based projects must continue to work without any configuration changes.

The pipeline is implemented across two files:

- `skills/release/SKILL.md` — Step 10 routing logic, full Step 10b implementation, Step 13f verification
- `commands/dist/homebrew.md` — The `cask` subcommand with build orchestration, template generator, updater, content management, and audit support

---

## 2. Component Relationships

```mermaid
graph TB
    release["/release skill"]
    homebrew["/craft:dist:homebrew"]

    subgraph "homebrew subcommands"
        formula["formula\n(CLI tools)"]
        cask["cask\n(desktop apps)"]
        audit["audit\n(formula or cask)"]
        workflow["workflow\n(GitHub Actions)"]
    end

    subgraph "Step 10 routing"
        step10a["Step 10a\nFormula update"]
        step10b["Step 10b\nCask release pipeline"]
        step13f["Step 13f\nCask verification"]
    end

    release -->|"detects dist type"| step10a
    release -->|"detects dist type"| step10b
    release -->|"after Step 10b"| step13f

    homebrew --> formula
    homebrew --> cask
    homebrew --> audit
    homebrew --> workflow

    step10a -.->|"same logic as"| formula
    step10b -.->|"same logic as"| cask
    step13f -.->|"verifies output of"| cask
```

The `/release` skill and `/craft:dist:homebrew cask` share the same underlying pipeline logic. Running `/release` on a Tauri project is equivalent to running the cask subcommand in a release context, plus the surrounding pipeline steps (version bump, PR, GitHub release, etc.).

---

## 3. Detection Hierarchy

Both the `/release` skill (Step 10 routing) and `/craft:dist:homebrew` (subcommand selection) use the same four-level detection hierarchy.

```mermaid
flowchart TD
    A["Start: determine distribution type"] --> B{".craft/homebrew.json\nexists?"}

    B -->|yes| C{"type field\nvalue?"}
    C -->|"'cask'"| CASK["dist_type = cask"]
    C -->|"'formula' or absent"| FORMULA["dist_type = formula"]

    B -->|no| D{"src-tauri/\ntauri.conf.json\nexists?"}
    D -->|yes| CASK2["dist_type = cask\n(auto-detect from Tauri)"]
    D -->|no| E{"git remote\norigin exists?"}
    E -->|yes| FORMULA2["dist_type = formula\n(name from remote URL)"]
    E -->|no| FORMULA3["dist_type = formula\n(name from basename)"]

    CASK --> ROUTE
    CASK2 --> ROUTE
    FORMULA --> ROUTE
    FORMULA2 --> ROUTE
    FORMULA3 --> ROUTE

    ROUTE{"Route"} -->|cask| STEP10B["Step 10b / cask subcommand"]
    ROUTE -->|formula| STEP10A["Step 10a / formula subcommand"]
```

**Why this ordering matters:** `.craft/homebrew.json` with `"type": "cask"` wins over everything, allowing explicit override of auto-detection. Tauri detection wins over the git remote fallback because desktop apps require fundamentally different distribution (Cask with pre-built DMGs vs Formula with source tarballs). The git remote and basename fallbacks both produce formula distribution, which is the safe default.

---

## 4. Step 10b Pipeline: Full Flow

```mermaid
sequenceDiagram
    participant R as /release
    participant B as Build (Tauri)
    participant GH as GitHub Release
    participant C as Cask File
    participant T as Tap Repo
    participant V as Verification

    R->>R: 10b-1: Read tauri.conf.json<br/>(productName, version, identifier)
    R->>R: Override from .craft/homebrew.json if present

    R->>R: 10b-2: Validate build environment<br/>(Rust targets, Tauri CLI, Node, Xcode, disk)
    Note over R: Abort if any check fails<br/>Offer auto-fix for Rust targets

    R->>B: 10b-3: npx tauri build --target aarch64-apple-darwin
    B-->>R: DMG_ARM (locate via primary path or fallback find)

    R->>B: 10b-3: npx tauri build --target x86_64-apple-darwin
    B-->>R: DMG_INTEL (locate via primary path or fallback find)

    R->>R: 10b-4: Verify architectures<br/>hdiutil attach → file command → hdiutil detach

    R->>R: 10b-5: shasum -a 256 on local DMG files<br/>Validate 64-char hex
    Note over R: No network involved.<br/>Eliminates CDN race condition.

    R->>GH: 10b-6: gh release upload DMG_ARM DMG_INTEL CHECKSUMS.txt --clobber
    GH-->>R: Verify URLs return 200 (warn if not)

    R->>C: 10b-7: Update version + SHA256 (Zone 1)
    R->>C: 10b-7: Migrate hardcoded version strings to #{version}
    R->>C: 10b-7: Show content preview → update postflight + caveats (Zone 2)
    R->>C: 10b-7: ruby -c validation

    R->>T: 10b-8: git pull --rebase origin main
    Note over T: Conflict: checkout --ours<br/>(freshly computed SHA256 wins)
    R->>T: 10b-8: git commit + git push

    R->>V: Step 13f: brew update
    V-->>R: Verify cask version matches release
    V-->>R: Verify SHA256 ARM + Intel match computed values
    V-->>R: Report: brew install --cask command
```

---

## 5. Zone Architecture: The 3-Zone Cask Update Model

The cask updater treats a `.rb` cask file as having three distinct zones with different update frequencies and triggers.

```mermaid
graph LR
    subgraph "Cask File Zones"
        Z1["Zone 1: Version + SHA256\n──────────────────\nversion '1.21.0'\non_arm { sha256 '...' }\non_intel { sha256 '...' }\n\nUpdated: every release\nTrigger: always (10b-7)"]

        Z2["Zone 2: Dynamic Content\n──────────────────\npostflight 'What's New' bullets\ncaveats 'New in' bullets\n\nUpdated: every release\nTrigger: --update-content or /release"]

        Z3["Zone 3: Static Content\n──────────────────\npostflight 'Quick Start'\ncaveats 'Features' list\ncaveats 'Keyboard Shortcuts'\n\nUpdated: when features change\nTrigger: --update-static only"]
    end

    CHANGELOG["CHANGELOG.md"] -->|"awk parsing"| Z2
    BUILD["Local DMGs"] -->|"shasum -a 256"| Z1
    TAURI["tauri.conf.json"] -->|"version field"| Z1
    MANUAL["Manual / --update-static flag"] --> Z3
```

**Design rationale for zone separation:** Zone 1 must always update (stale SHA256 breaks installations). Zone 2 should update every release to keep install-time messaging current, but the content comes from CHANGELOG so it needs parsing. Zone 3 rarely changes — shipping a broken Features list because a shortcut changed would be worse than leaving it slightly out of date, so it requires an explicit flag.

### Zone 2 Content Pipeline

```mermaid
flowchart LR
    CL["CHANGELOG.md"] -->|"awk: find version header\ncollect '- ' lines"| ITEMS["Bullet items\nfor version X.Y.Z"]

    ITEMS -->|"max 5 items\n+ test count"| PF["postflight\n'What's New' bullets\n(shown during install)"]

    ITEMS -->|"all items\n+ test count"| CV["caveats\n'New in' bullets\n(shown after install)"]

    CL -->|"grep: 'N tests passing'"| TC["Test count string"]
    TC --> PF
    TC --> CV

    PF -->|"python3 re.sub\nbetween markers"| CASK["Cask file\n(written on confirm)"]
    CV -->|"python3 re.sub\nbetween markers"| CASK
```

The postflight limit of 5 items exists because postflight output appears during `brew install` / `brew upgrade` and should not overwhelm the terminal. Caveats appear in a separate block after install completes, so they can include the full list.

---

## 6. Data Flow

```mermaid
flowchart TD
    subgraph "Input Sources"
        TC["src-tauri/tauri.conf.json\n──────────────────\nproductName\nversion\nidentifier\nminimumSystemVersion"]
        CF[".craft/homebrew.json\n──────────────────\nformula_name\ntap\ntype: cask\ncask.artifact_pattern\ncask.build_command"]
        CL2["CHANGELOG.md\n──────────────────\n## vX.Y.Z entry\nbullet items\ntest count"]
    end

    subgraph "Build Artifacts"
        ARM["ProductName_X.Y.Z_aarch64.dmg\n(src-tauri/target/aarch64-apple-darwin/\nrelease/bundle/dmg/)"]
        INTEL["ProductName_X.Y.Z_x64.dmg\n(src-tauri/target/x86_64-apple-darwin/\nrelease/bundle/dmg/)"]
    end

    subgraph "Computed Values"
        SHA["SHA256_ARM\nSHA256_INTEL\n(shasum -a 256, local only)"]
        CHECKSUMS["CHECKSUMS.txt"]
    end

    subgraph "Output Artifacts"
        CASK2["Casks/scribe.rb\n(in tap repo)"]
        GHREL["GitHub Release Assets\n(DMGs + CHECKSUMS.txt)"]
    end

    TC -->|"productName, version"| ARM
    TC -->|"productName, version"| INTEL
    CF -->|"formula_name, tap"| CASK2
    TC -->|"identifier, min_macos"| CASK2
    ARM -->|"shasum"| SHA
    INTEL -->|"shasum"| SHA
    SHA -->|"Zone 1 update"| CASK2
    CL2 -->|"Zone 2 update"| CASK2
    ARM -->|"gh release upload"| GHREL
    INTEL -->|"gh release upload"| GHREL
    SHA -->|"echo"| CHECKSUMS
    CHECKSUMS -->|"gh release upload"| GHREL
```

---

## 7. Multi-Architecture Build Strategy

```mermaid
gantt
    title Step 10b Build Sequence (serial, not parallel)
    dateFormat X
    axisFormat %s

    section Build
    Pre-flight validation        :a1, 0, 10
    aarch64 native build         :a2, after a1, 134
    Locate + verify ARM DMG      :a3, after a2, 5
    x86_64 cross-compile build   :a4, after a3, 271
    Locate + verify Intel DMG    :a5, after a4, 5

    section Post-build
    Architecture verification    :b1, after a5, 15
    SHA256 computation           :b2, after b1, 2
    GitHub upload                :b3, after b2, 30
    Cask update + tap push       :b4, after b3, 20
```

Builds run serially rather than in parallel because parallel Tauri builds on a developer machine cause memory exhaustion — each build compiles the full Rust + frontend dependency tree. Native architecture (aarch64) runs first so compilation errors surface quickly before committing to the longer cross-compile step.

---

## 8. Tap Conflict Resolution

```mermaid
flowchart TD
    A["git pull --rebase origin main"] --> B{Conflict?}

    B -->|no| C["git add Casks/name.rb\ngit commit\ngit push"]

    B -->|yes| D["git checkout --ours Casks/name.rb\n(local freshly-computed SHA256 wins)"]
    D --> E["git add Casks/name.rb\ngit rebase --continue"]
    E --> F["git push origin main"]

    F --> G{Push succeeds?}
    G -->|yes| DONE["Done"]
    G -->|no| H["git pull --rebase origin main\ngit push origin main"]
    H --> DONE

    C --> DONE
```

**Why "ours" always wins:** During a release, the local cask file has SHA256 hashes freshly computed from local build artifacts. Any remote SHA256 values are stale by definition — they cannot be more current than what was just built and hashed locally. This strategy was adopted after SHA256 mismatches caused tap conflicts in earlier Scribe releases.

---

## 9. Step 13f Verification

Step 13f runs only when Step 10b was executed. It verifies the tap push actually propagated.

```mermaid
flowchart LR
    A["brew update"] --> B["brew info --cask TAP/NAME"]
    B -->|"extract version"| C{"version ==\nrelease version?"}
    C -->|no| FAIL1["MISMATCH\n(tap push failed silently\nor brew cache stale)"]
    C -->|yes| D["gh api: fetch cask file from tap repo"]
    D -->|"grep SHA256_ARM"| E{"ARM SHA256\nfound?"}
    E -->|no| FAIL2["MISMATCH\n(conflicting push\noverwrote SHA256)"]
    E -->|yes| F{"Intel SHA256\nfound?"}
    F -->|no| FAIL2
    F -->|yes| PASS["ALL GREEN\nReport: brew install --cask command"]
```

**What 13f catches that tap push logging misses:** The tap push may report success but a concurrent push (e.g., from CI) can overwrite the cask file immediately after. Verifying the live tap content against the locally-computed hashes catches this race condition.

---

## 10. Formula vs Cask: Architectural Differences

| Dimension | Step 10a (Formula) | Step 10b (Cask) |
|-----------|-------------------|-----------------|
| **Artifact** | Source tarball (`.tar.gz`) from GitHub | Pre-built DMGs (2 per release) |
| **SHA256 source** | Downloaded from GitHub CDN | Computed from local build output |
| **Build required** | No (user builds from source) | Yes (2 Tauri builds per release) |
| **Architecture** | Source is arch-agnostic | Separate binary per arch (aarch64, x86_64) |
| **Tap file** | `Formula/{name}.rb` | `Casks/{name}.rb` |
| **Content management** | Not applicable | 3-zone model (version, dynamic, static) |
| **CDN race condition** | Possible (must wait for GitHub CDN) | Eliminated (local artifacts) |
| **Conflict resolution** | Simple push | Rebase with "ours" strategy |
| **Post-release verification** | Step 13d | Step 13f |
| **Time cost** | ~1 minute | ~8-12 minutes (build-dominated) |

---

## 11. Configuration Schema Summary

```
.craft/homebrew.json
├── formula_name    (string, required)   — name in tap
├── tap             (string, required)   — "org/name" format
├── type            (string, optional)   — "formula" | "cask", default "formula"
└── cask            (object, optional)   — only when type = "cask"
    ├── app_name         — "Scribe.app" (default: productName + .app)
    ├── identifier       — "com.scribe.app" (default: from tauri.conf.json)
    ├── min_macos        — "catalina" (default: from minimumSystemVersion)
    ├── architectures    — ["aarch64", "x64"] (default)
    ├── artifact_pattern — "{name}_{version}_{arch}.dmg" (default)
    ├── build_command    — "npx tauri build --target {target}" (default)
    ├── targets          — {"aarch64": "aarch64-apple-darwin", "x64": "x86_64-apple-darwin"}
    ├── postflight_template — "changelog" | "none"
    └── caveats_template    — "full" | "minimal" | "none"
```

Fields not present in `.craft/homebrew.json` fall back to auto-detection from `src-tauri/tauri.conf.json`. The `cask` object is optional even when `type = "cask"` — all fields within it have defaults derived from Tauri's config.

---

## See Also

- [Desktop Release Guide](../guide/desktop-release.md) — Step-by-step usage walkthrough
- [Homebrew Quick Reference](../reference/REFCARD-HOMEBREW.md) — Command syntax and flags
- `/craft:dist:homebrew` command — Full command specification (see `commands/dist/homebrew.md`)
- `/release` skill — Complete pipeline specification (see `skills/release/SKILL.md`)
