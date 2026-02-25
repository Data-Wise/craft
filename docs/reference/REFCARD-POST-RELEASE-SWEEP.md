# Quick Reference: post-release-sweep.sh

**Post-release drift detection for Tier 2+ references** — catches stale version strings, counts, and content that `bump-version.sh` doesn't manage.

**Script:** `scripts/post-release-sweep.sh` | **Pipeline Step:** 13.5 (after downstream verification)

---

## Quick Decision Tree

```text
Just finished a release?
|
+-- Want a quick health check?
|   +-- ./scripts/post-release-sweep.sh
|
+-- Found drift, want auto-fix?
|   +-- ./scripts/post-release-sweep.sh --fix
|
+-- Need machine-readable output?
|   +-- ./scripts/post-release-sweep.sh --json
|
+-- Checking against a specific version?
|   +-- ./scripts/post-release-sweep.sh --version 2.27.0
|
+-- Not sure what's stale?
    +-- Run without flags (dry-run is default)
    +-- Review the per-file report
```

---

## Usage

```bash
# Dry-run: report drift without changes (default)
./scripts/post-release-sweep.sh

# Auto-fix mechanical items (Tier 2 version refs)
./scripts/post-release-sweep.sh --fix

# Check against a specific version (instead of reading plugin.json)
./scripts/post-release-sweep.sh --version 2.27.0

# JSON output for CI or scripting
./scripts/post-release-sweep.sh --json

# Combine flags
./scripts/post-release-sweep.sh --fix --json
```

---

## Three-Tier Detection Model

| Tier | What It Catches | Fix Mode | Phase |
|------|----------------|----------|-------|
| 1 | Core file drift (13 files managed by `bump-version.sh`) | Delegates to `bump-version.sh --verify` | Phase 1 |
| 2 | Stale version refs in secondary docs (guides, refcards) | `--fix` auto-corrects via sed | Phase 2 |
| 2 | Stale test/command counts in docs | Manual review (reported) | Phase 3 |
| 3 | Content staleness (CHANGELOG vs index.md, README features) | Manual review (never auto-fixed) | Phase 4 |

---

## Tier 2 Files Scanned

These files are NOT managed by `bump-version.sh` but commonly contain version references:

| File | Why It Drifts |
|------|--------------|
| `docs/reference/REFCARD-RELEASE.md` | Contains pipeline version examples |
| `docs/reference/REFCARD-HOMEBREW.md` | Contains formula version examples |
| `docs/reference/REFCARD-BUMP-VERSION.md` | Contains usage examples with versions |
| `docs/reference/REFCARD-CHECK.md` | Version in check output examples |
| `docs/reference/REFCARD-TESTING.md` | Test count references |
| `docs/guide/badge-management.md` | Badge URL version strings |
| `docs/guide/homebrew-automation.md` | Homebrew formula version examples |
| `docs/guide/homebrew-installation.md` | Install command version refs |
| `docs/guide/getting-started.md` | Quickstart version references |
| `docs/guide/marketplace-distribution.md` | Marketplace version examples |
| `docs/testing-quickstart.md` | Test count and version strings |

**Excluded:** `docs/VERSION-HISTORY.md` — legitimately lists all past versions.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | Clean — no drift detected |
| 1 | Drift found (any tier) |
| 2 | Usage error (bad args) |

---

## Modes Compared

| Mode | Changes Files | Version Refs | Counts | Content |
|------|:---:|:---:|:---:|:---:|
| (default / `--dry-run`) | No | Reports | Reports | Reports |
| `--fix` | Yes (Tier 2 only) | Auto-fixes | Reports | Reports |
| `--json` | No | Reports as JSON | Reports as JSON | Reports as JSON |
| `--fix --json` | Yes (Tier 2 only) | Fixes + JSON | Reports as JSON | Reports as JSON |

---

## JSON Output Schema

```json
{
  "version": "2.27.0",
  "previous_version": "2.26.0",
  "mode": "dry-run",
  "tier1_issues": 0,
  "tier2_issues": 2,
  "tier2_fixed": 0,
  "tier3_issues": 0,
  "total_issues": 2,
  "findings": [
    {
      "tier": 2,
      "file": "docs/guide/homebrew-automation.md",
      "detail": "2 stale v2.26.0 ref(s)",
      "fixable": "auto"
    }
  ],
  "clean": false
}
```

---

## Previous Version Derivation

The script automatically derives the previous version to search for:

| Current Version | Derived Previous | Logic |
|----------------|-----------------|-------|
| `2.27.0` | `2.26.0` | Decrement patch |
| `2.1.0` | `2.0.0` | Decrement patch |
| `3.0.0` | `2.0.0` | Patch=0, decrement minor... minor=0, decrement major |
| `1.0.0` | (empty) | Cannot derive — Tier 2 scan skipped |

Override with `--version` if the automatic derivation doesn't match your actual previous release.

---

## Integration with Release Pipeline

`post-release-sweep.sh` runs as Step 13.5, after all downstream verification:

```text
Step 13: Downstream verification (docs, brew, badges)
    |
Step 13.5: ./scripts/post-release-sweep.sh --fix   <-- catches long-tail drift
    |       git add + commit if fixes applied
    |
    Release complete
```

---

## Architecture

```text
post-release-sweep.sh
    |
    +-- formatting.sh (color output)
    |
    +-- bump-version.sh --verify (Phase 1: Tier 1 delegation)
    |
    +-- grep + sed (Phase 2: Tier 2 version ref scan/fix)
    |       Scans 11 secondary docs for v{PREV_VERSION}
    |       --fix mode: sed replaces old -> current version
    |
    +-- grep (Phase 3: Tier 2 count staleness)
    |       Compares test/command counts against CLAUDE.md + filesystem
    |
    +-- grep (Phase 4: Tier 3 content staleness)
            Compares CHANGELOG version vs docs/index.md info box
            Compares README feature count vs CHANGELOG entries
```

---

## Relationship to bump-version.sh

These two scripts form a complementary pair:

| Aspect | `bump-version.sh` | `post-release-sweep.sh` |
|--------|-------------------|------------------------|
| **When** | Before release (Step 3) | After release (Step 13.5) |
| **Scope** | 13 core files | 11+ secondary files |
| **Action** | Proactive: sets new version | Reactive: finds what was missed |
| **Fix mode** | Always writes | `--fix` flag required |
| **Default** | Requires version arg | Dry-run (safe) |

---

## Platform Note

Uses BSD `sed -i ''` (macOS) for `--fix` mode. For GNU/Linux, change to `sed -i` (no empty string argument).

---

## See Also

- [bump-version.sh Reference](REFCARD-BUMP-VERSION.md) — Core version sync (Tier 1)
- [Release Pipeline Reference](REFCARD-RELEASE.md) — Full 13.5-step pipeline
- Release Skill (`skills/release/SKILL.md`) — Complete release orchestration
