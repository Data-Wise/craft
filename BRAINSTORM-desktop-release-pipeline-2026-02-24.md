# BRAINSTORM: Desktop App Release Pipeline (Issue #108)

**Mode:** max | **Focus:** feature | **Duration:** ~15 min
**Source:** [GitHub Issue #108](https://github.com/Data-Wise/craft/issues/108)
**Date:** 2026-02-24

---

## Context Summary

| Question | Answer |
|----------|--------|
| **Scope** | Scribe only (for now), generalize later |
| **Pain points** | All four — build, SHA/conflicts, cask updates, verification |
| **CI model** | Local-first — `/release` owns the full pipeline |
| **Cask content** | Templated — can auto-generate from CHANGELOG |
| **Command design** | Extend existing `/craft:dist:homebrew` with auto-detection |
| **Build role** | `/release` runs Tauri builds (both arches) |
| **Tap location** | Same tap (data-wise/tap), cask alongside formulas |
| **Config** | Auto-detect from tauri.conf.json + optional `.craft/homebrew.json` overrides |
| **Phasing** | Ship Phase 1 + Phase 2 together as one feature |

---

## Quick Wins (< 30 min each)

1. **Auto-detect Formula vs Cask** — Check for `Casks/` vs `Formula/` directory in tap repo. One `if` statement in the detection chain.

2. **SHA256 from local build artifacts** — Instead of downloading from GitHub (race condition!), compute SHA256 directly from the DMG files that `/release` just built. Zero network latency, zero race conditions.

3. **`.craft/homebrew.json` schema extension** — Add `"type": "cask"` and `"architectures"` fields to the existing config format. Backward-compatible with existing Formula configs.

---

## Medium Effort (1-2 hours each)

4. **Cask template generator** — Parse `tauri.conf.json` for `productName`, `version`, `identifier`, `bundle.macOS.minimumSystemVersion`. Generate cask file with `on_arm`/`on_intel` blocks. Use existing cask (Scribe) as reference template.

5. **Multi-arch Tauri build orchestration** — Sequential build: native arch first (fast), then cross-compile (slower, may need `rustup target add`). Collect DMG paths for SHA256 computation.

6. **Cask content updater** — Parse existing cask file, update:
   - `version` field
   - `sha256` in both `on_arm` and `on_intel` blocks
   - `postflight` block from CHANGELOG
   - `caveats` heredoc from release notes template

7. **Release pipeline integration** — Add Step 10b to the 13-step release pipeline: detect Tauri project, build, upload DMGs, update cask, push tap.

---

## Long-term (Future sessions)

8. **CI workflow for cask releases** — Optional `homebrew-cask-release.yml` for teams that prefer CI-driven releases (not needed for local-first).

9. **Electron/other desktop app support** — Generalize beyond Tauri to support Electron Builder, PKG installers, etc.

10. **Homebrew Cask audit** — Extend `/craft:dist:homebrew audit` to validate cask files (`brew audit --cask`).

11. **Livecheck maintenance** — Auto-update the `livecheck` block when version patterns change.

---

## Recommended Path

Start with items 1-3 (quick wins) to establish the detection and config foundation, then items 4-7 as a single feature branch. The build sequence should be:

```
detect Tauri project → build native arch → build cross-compile → collect DMGs
→ upload to GitHub release → compute SHA256 from local files → update cask
→ push tap → verify brew upgrade --cask
```

**Key insight:** Computing SHA256 from local build artifacts (not GitHub downloads) eliminates the race condition problem entirely. This is the single most impactful design decision.

---

## Architecture Overview

```
/release (Step 10b: Desktop App)
  ├── Detect: tauri.conf.json → type: "cask"
  ├── Build: npx tauri build --target aarch64-apple-darwin
  ├── Build: npx tauri build --target x86_64-apple-darwin
  ├── Upload: gh release upload v1.20.0 Scribe_1.20.0_aarch64.dmg Scribe_1.20.0_x64.dmg
  ├── SHA256: shasum -a 256 <local DMG files>
  ├── Update: Casks/scribe.rb (version, SHA256, postflight, caveats)
  ├── Push: cd tap-dir && git commit && git push
  └── Verify: brew update && brew upgrade --cask scribe
```

```
/craft:dist:homebrew (extended)
  ├── formula (existing) — generates Formula/*.rb
  ├── cask (NEW) — generates/updates Casks/*.rb
  ├── workflow (existing) — generates CI workflows
  ├── audit (extended) — validates both formulas and casks
  ├── setup (extended) — setup wizard with cask support
  ├── update-resources (existing) — PyPI resource URLs
  └── deps (extended) — includes cask dependencies
```

---

## Risk Analysis

| Risk | Mitigation |
|------|------------|
| Cross-compilation fails (missing target) | Pre-check `rustup target list --installed`, auto-install if missing |
| DMG naming convention differs | Config override in `.craft/homebrew.json` (`artifact_pattern`) |
| Tap push conflicts | `git pull --rebase` before push, retry once |
| Cask syntax errors after update | `ruby -c` syntax check + `brew audit --cask` before commit |
| Build takes too long | Show progress, allow `--skip-build` flag for pre-built artifacts |
| Caveats/postflight content drift | Template from CHANGELOG, user review before commit |

---

## Agent Analysis

Two expert agents were launched for deep analysis:

- **Backend Architect**: Analyzing subcommand extension strategy, build sequencing, and error recovery patterns
- **Codebase Explorer**: Examining real Scribe cask structure, tauri.conf.json, and existing homebrew configs

**Real-world findings from direct inspection:**

- Scribe cask at `Casks/scribe.rb` uses `on_arm`/`on_intel` with `Scribe_#{version}_{arch}.dmg` URL pattern
- `tauri.conf.json` provides: productName="Scribe", version="1.20.0", identifier="com.scribe.app", minimumSystemVersion="10.15"
- Cask has 3 release-specific zones: `postflight` (what's new), `caveats` (full feature list), `version` field
- Existing tap structure: `Formula/` (craft, rforge, scholar, etc.) + `Casks/` (scribe, scribe-dev)

---

## Files

- **Brainstorm:** `BRAINSTORM-desktop-release-pipeline-2026-02-24.md`
- **Spec:** `docs/specs/SPEC-desktop-release-pipeline-2026-02-24.md`
