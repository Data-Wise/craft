# ORCHESTRATE: Desktop App Release Pipeline

## Issue

[#108](https://github.com/Data-Wise/craft/issues/108) — Revamp /release and /craft:dist:homebrew for desktop app (Tauri/cask) workflows

## Spec

`docs/specs/SPEC-desktop-release-pipeline-2026-02-24.md`

## Branch

`feature/desktop-release-pipeline`

## Goal

Extend `/craft:dist:homebrew` and the `/release` pipeline to support Homebrew Cask distribution for Tauri desktop apps. Local-first approach, auto-detection, multi-arch builds, and automated cask content updates.

---

## Increment Plan

### Increment 1: Detection and Config (1-2 hours)

**Goal:** Auto-detect Tauri projects and extend `.craft/homebrew.json` schema for cask support.

**Files to create/modify:**

| File | Action | What |
|------|--------|------|
| `commands/dist/homebrew.md` | Modify | Add `cask` subcommand, update auto-detection table, add Tauri to detection chain |
| `skills/release/SKILL.md` | Modify | Add Step 10b detection logic (tauri.conf.json check) |

**Implementation:**

1. Update auto-detection table in `commands/dist/homebrew.md`:
   - Add Tauri Desktop App row (priority above Claude Code Plugin)
   - Detection: `src-tauri/tauri.conf.json`
   - Distribution: Cask (DMG, dual-arch)

2. Add `cask` subcommand documentation to `commands/dist/homebrew.md`:
   - Usage, flags (`--update-content`, `--skip-build`, `--desc`, etc.)
   - Auto-detection hierarchy (config > tauri.conf.json > tap structure)
   - Cask file structure reference

3. Document `.craft/homebrew.json` extended schema:
   - `"type": "cask"` field
   - `"cask"` nested object (app_name, identifier, architectures, etc.)
   - Backward-compatible with existing formula configs

4. Add detection logic to `skills/release/SKILL.md` Step 10:
   - Check for `src-tauri/tauri.conf.json` → route to Step 10b
   - Check `.craft/homebrew.json` type field → route accordingly
   - Default: existing Formula path (unchanged)

**Tests:**

- Verify existing formula detection still works
- Verify Tauri project detection from tauri.conf.json
- Verify config override takes precedence

**Commit:** `feat: add Tauri/cask detection and .craft/homebrew.json schema extension`

---

### Increment 2: Build Orchestration (2-3 hours)

**Goal:** Multi-arch Tauri build sequence with environment validation and architecture verification.

**Files to create/modify:**

| File | Action | What |
|------|--------|------|
| `commands/dist/homebrew.md` | Modify | Add build section with environment validation |
| `skills/release/SKILL.md` | Modify | Add Step 10b build sequence |

**Implementation:**

1. Build environment validation (pre-flight for Tauri projects):
   - Check Rust targets installed (aarch64-apple-darwin, x86_64-apple-darwin)
   - Check Tauri CLI available (npx tauri or cargo-tauri)
   - Check node_modules exists
   - Check Xcode SDK
   - Check disk space (>= 2GB)
   - Offer to auto-install missing Rust targets

2. Multi-arch build sequence (serial, not parallel):
   - Native arch first (fast, catches errors early)
   - Cross-compile second (slower)
   - DMG path discovery (primary path + fallback search)
   - Post-build architecture verification (`file` command on binary)

3. SHA256 computation from local artifacts:
   - `shasum -a 256` on local DMG files
   - Validate 64-char hex output
   - No network involved (eliminates race conditions)

4. Asset upload to GitHub release:
   - `gh release upload` with `--clobber` for re-uploads
   - Upload CHECKSUMS.txt alongside DMGs
   - Verify both DMG URLs return 200 before proceeding

**Progress display:**

```
[1/8] Detecting project type ............ Tauri (Scribe)
[2/8] Checking Rust targets ............. 2/2 installed
[3/8] Building aarch64 (native) ......... DONE (2m 14s)
[4/8] Building x86_64 (cross-compile) ... BUILDING...
[5/8] Verifying architectures ........... DONE
[6/8] Computing SHA256 .................. DONE
[7/8] Uploading to GitHub release ....... DONE
[8/8] Verifying upload URLs ............. DONE
```

**Tests:**

- Build env validation catches missing targets
- SHA256 computation produces valid 64-char hex
- Architecture verification catches wrong-arch DMGs

**Commit:** `feat: add multi-arch Tauri build orchestration with SHA256 from local artifacts`

---

### Increment 3: Cask File Generator and Updater (2-3 hours)

**Goal:** Generate new cask files and update existing ones with version, SHA256, and content.

**Files to create/modify:**

| File | Action | What |
|------|--------|------|
| `commands/dist/homebrew.md` | Modify | Add cask template structure and update algorithm |
| `skills/release/SKILL.md` | Modify | Add Step 10b cask update logic |

**Implementation:**

1. Cask template generator (new cask from Tauri project):
   - Read tauri.conf.json for productName, version, identifier, minimumSystemVersion
   - Map macOS version to Homebrew codename (10.15 -> catalina)
   - Generate all zones: on_arm/on_intel, livecheck, postflight, caveats, zap
   - Use `#{version}` interpolation for version display strings

2. Cask file updater (existing cask):
   - Update `version` field
   - Update SHA256 in `on_arm` block (regex: match block, replace hash)
   - Update SHA256 in `on_intel` block (same pattern)
   - Migrate hardcoded version strings to `#{version}` on first run
   - Validate with `ruby -c` after modification

3. CHANGELOG parser for content generation:
   - Extract bullet points from latest version entry
   - Parse test count from "X,XXX tests passing" pattern
   - Generate postflight `ohai` lines (max 5 items)
   - Generate caveats "New in" section (all items)

4. Tap push with conflict resolution:
   - `git pull --rebase` before push
   - On conflict: checkout ours for cask file, continue rebase
   - Retry once, then report to user

**Tests:**

- Cask template generates valid Ruby (ruby -c passes)
- SHA256 update targets correct architecture block
- Version migration replaces hardcoded strings
- CHANGELOG parser extracts correct items

**Commit:** `feat: add cask file generator, updater, and CHANGELOG-driven content management`

---

### Increment 4: Content Update Flag (`--update-content`) (1-2 hours)

**Goal:** The `--update-content` flag and zone-specific overrides for install-time content.

**Files to create/modify:**

| File | Action | What |
|------|--------|------|
| `commands/dist/homebrew.md` | Modify | Document --update-content flag and all zone flags |
| `skills/release/SKILL.md` | Modify | Add content preview and confirmation step |

**Implementation:**

1. `--update-content` umbrella flag:
   - Parse CHANGELOG for latest version entry
   - Generate postflight "What's New" bullets
   - Generate caveats "New in" section
   - Detect test count from CHANGELOG pattern
   - Show preview of all changes before writing

2. Zone-specific override flags:
   - `--desc "text"` — update desc field only (validate <= 80 chars)
   - `--postflight "text"` — override What's New bullets
   - `--caveats-new "text"` — override New in bullets
   - `--content-only` — same as --update-content but skip version/SHA256

3. Static section handling with `--update-static`:
   - Detect changes between current static sections and README/config
   - Show diff with confirmation before applying
   - Separate from dynamic content updates

4. Release flow integration:
   - Auto-generate content from CHANGELOG
   - Show preview: postflight bullets, caveats bullets, desc, static summary
   - Ask "Looks good?" with options: Yes / Edit / Skip
   - Write on confirmation

**Tests:**

- Content generation from CHANGELOG produces correct ohai lines
- `--desc` validates max 80 chars and no "A/An" prefix
- Preview shows all zones with pending changes
- Static sections untouched by default

**Commit:** `feat: add --update-content flag with CHANGELOG parsing and content preview`

---

### Increment 5: End-to-End Verification and Release Pipeline Integration (1-2 hours)

**Goal:** Wire everything into the `/release` pipeline and add post-release verification.

**Files to create/modify:**

| File | Action | What |
|------|--------|------|
| `skills/release/SKILL.md` | Modify | Add full Step 10b with all substeps |
| `commands/dist/homebrew.md` | Modify | Add audit --cask support, verification section |

**Implementation:**

1. Step 10b in release pipeline:
   - Full orchestration: detect -> build -> upload -> SHA256 -> update cask -> preview content -> push tap -> verify
   - Error recovery at each substep (see spec Error Handling section)
   - Rollback guidance on failure
   - Progress display with timing

2. Step 13f: Cask verification:
   - `brew update` to refresh tap
   - `brew info --cask` to verify version matches
   - SHA256 cross-check in cask file
   - Report install command for manual verification

3. Extend `/craft:dist:homebrew audit` for casks:
   - Auto-detect cask vs formula
   - Run `brew audit --cask` with cask-specific checks
   - Report livecheck, zap, uninstall validation results

4. Dry-run support:
   - `/release --dry-run` shows Step 10b plan without building
   - `/craft:dist:homebrew cask --dry-run` shows cask changes without writing

**Tests:**

- Step 10b integrates correctly in pipeline sequence
- Verification catches version mismatch
- Audit detects cask files automatically
- Dry-run produces correct preview without side effects

**Commit:** `feat: integrate cask release into /release pipeline with end-to-end verification`

---

### Increment 6: Documentation and Polish (1-2 hours)

**Goal:** Comprehensive documentation, reference cards, and cleanup.

**Files to create/modify:**

| File | Action | What |
|------|--------|------|
| `docs/guide/desktop-release.md` | Create | Full desktop release guide (tutorial) |
| `docs/reference/REFCARD.md` | Modify | Add desktop distribution section |
| `CLAUDE.md` | Modify | Update command count and test count |
| `README.md` | Modify | Mention desktop app support |
| `CHANGELOG.md` | Modify | Add version entry |

**Implementation:**

1. Create `docs/guide/desktop-release.md`:
   - Overview, prerequisites, configuration
   - Step-by-step release walkthrough
   - Troubleshooting guide (cross-compilation, tap conflicts, DMG issues)
   - Examples with real Scribe commands

2. Update reference card:
   - Desktop App Distribution section
   - Quick-reference table for cask commands

3. Update CLAUDE.md:
   - New command count (if `cask` is a new subcommand)
   - Test count after new tests

4. CHANGELOG entry:
   - Feature description
   - New flags and commands
   - Breaking changes (none expected)

5. Run full test suite and validate counts.

**Commit:** `docs: add desktop release guide and update reference documentation`

---

## Summary

| Increment | Description | Estimated Time | Key Deliverable |
|-----------|-------------|---------------|-----------------|
| 1 | Detection and Config | 1-2 hours | Auto-detect Tauri, extended config schema |
| 2 | Build Orchestration | 2-3 hours | Multi-arch build with SHA256 from local artifacts |
| 3 | Cask Generator/Updater | 2-3 hours | Template generator + zone updater |
| 4 | Content Update Flag | 1-2 hours | `--update-content` with CHANGELOG parsing |
| 5 | Pipeline Integration | 1-2 hours | Step 10b + verification + audit |
| 6 | Documentation | 1-2 hours | Guide, refcard, CHANGELOG |

**Total:** 8-14 hours across 6 increments

## Key Files

| File | Role |
|------|------|
| `commands/dist/homebrew.md` | Main command spec (heavily modified) |
| `skills/release/SKILL.md` | Release pipeline (Step 10b added) |
| `docs/guide/desktop-release.md` | User-facing guide (new) |
| `docs/specs/SPEC-desktop-release-pipeline-2026-02-24.md` | Full spec (reference) |

## Dependencies

- Scribe project for real-world testing (`~/projects/dev-tools/scribe`)
- Homebrew tap (`data-wise/homebrew-tap`) for cask file testing
- Rust toolchain with cross-compilation targets

## Testing Strategy

Each increment is independently testable. Use Scribe as the real-world test case:

1. **Detection:** Does `tauri.conf.json` trigger cask mode?
2. **Build:** Do both arch builds succeed and produce correct DMGs?
3. **Cask update:** Does the updater correctly modify `Casks/scribe.rb`?
4. **Content:** Does CHANGELOG parsing produce correct postflight/caveats?
5. **Pipeline:** Does `/release --dry-run` show the correct Step 10b plan?
6. **Docs:** Do all links resolve and guides render correctly?
