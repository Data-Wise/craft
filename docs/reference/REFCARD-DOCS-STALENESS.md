# Quick Reference: Docs Staleness Detection

**4-phase documentation staleness detector** -- nav gaps, count drift, skill/agent coverage, cross-doc freshness. Two-pass interactive fix mode with shared exclusion config.

**Version:** 2.28.0 | **Script:** `scripts/docs-staleness-check.sh` | **Config:** `scripts/config/exclusions.txt`

---

## Usage

```bash
# Default: scan and report (non-destructive)
./scripts/docs-staleness-check.sh

# Auto-fix mode (Pass 1 auto, Pass 2 interactive)
./scripts/docs-staleness-check.sh --fix

# CI mode: auto-fix without prompts
./scripts/docs-staleness-check.sh --fix --non-interactive

# JSON output for tooling
./scripts/docs-staleness-check.sh --json

# Audit stale exclusions
./scripts/docs-staleness-check.sh --audit-exclusions

```

---

## Flags

| Flag | Effect |
|------|--------|
| (none) | Scan all 4 phases, report traffic light summary |
| `--fix` | Pass 1: auto-fix safe items. Pass 2: interactive review |
| `--non-interactive` | Skip Pass 2 interactive prompts (CI-safe) |
| `--json` | Output structured JSON instead of traffic light |
| `--audit-exclusions` | Check exclusion config for stale entries |

---

## Phases

| Phase | Name | What It Checks |
|-------|------|---------------|
| 6 | Nav Completeness | Files in `docs/` missing from `mkdocs.yml` nav; nav entries pointing to missing files |
| 7 | Count Consistency | Stale `N commands`, `N skills`, `N agents` strings across all docs |
| 8 | Skill/Agent Coverage | Skills and agents not listed in `docs/skills-agents.md` or `docs/guide/skills-agents.md` |
| 9 | Cross-Doc Freshness | Stale version strings in REFCARDs, stale counts in "See Also" sections, `site_description` drift |

---

## Traffic Light Output

```text
Phase 6: Nav Completeness ............ GREEN (0 issues)
Phase 7: Count Consistency ........... YELLOW (3 warnings)
Phase 8: Skill/Agent Coverage ........ GREEN (0 issues)
Phase 9: Cross-Doc Freshness ......... YELLOW (2 warnings)

Status: YELLOW (5 warnings, 0 errors)
```

| Color | Meaning | Examples |
|-------|---------|---------|
| GREEN | No issues in phase | All nav entries match, all counts current |
| YELLOW | Warnings only (non-blocking) | Architecture docs with old metrics, uncertain count context |
| RED | Errors (blocking) | Missing nav for new files, wrong counts in primary docs |

---

## Two-Pass Fix Mode

When `--fix` is specified:

**Pass 1 (automatic):** Applies safe fixes without prompting -- exact count replacements, skill/agent table additions.

**Pass 2 (interactive):** Presents uncertain items one at a time. Options per item:

| Key | Action |
|-----|--------|
| `f` | Fix -- apply the suggested replacement |
| `s` | Skip -- leave unchanged |
| `e` | Exclude -- add to `exclusions.txt` permanently |

Pass 2 is skipped when `--non-interactive` is set.

---

## Exclusion Config

**File:** `scripts/config/exclusions.txt`

```text
# Whole-file exclusion (skip entire file)
docs/VERSION-HISTORY.md
docs/CHANGELOG.md

# Directory exclusion (skip all files under path)
docs/specs/_archive/

# Pattern exclusion (skip specific pattern in specific file)
docs/architecture/HUB-V2-ARCHITECTURE.md:97 commands
docs/REFCARD.md:99 commands
```

**Format rules:**

- Lines starting with `#` are comments
- Blank lines are ignored
- `filepath` -- excludes the entire file from all phases
- `dir/` -- excludes all files under that directory
- `filepath:pattern` -- excludes only that pattern match in that file

Use `--audit-exclusions` to find stale entries (deleted files, patterns that no longer match).

---

## Release Pipeline Integration

Runs as **Step 2d** in the release pipeline, after pre-release-check.sh:

| Step | Action | Script |
|------|--------|--------|
| 2a | `/craft:check --for release` | (command) |
| 2b | `pre-release-check.sh` | `scripts/pre-release-check.sh` |
| 2c | Marketplace validation | `claude plugin validate .` |
| **2d** | **Docs staleness check** | **`scripts/docs-staleness-check.sh`** |

In release mode, RED status blocks the release. YELLOW status is reported but does not block.

---

## Exit Codes

| Code | Meaning |
|------|---------|
| 0 | GREEN -- no issues found |
| 1 | YELLOW or RED -- issues found (see output for details) |
| 2 | Usage error (bad flags) |

---

## See Also

- [/craft:docs:check](../commands/docs/check.md) -- Full documentation health check (includes staleness via `--deep`)
- [Release Pipeline Reference](REFCARD-RELEASE.md) -- Step 2d integration
- [Post-Release Sweep Reference](REFCARD-POST-RELEASE-SWEEP.md) -- Shares exclusion config

---

**Version:** 2.28.0
**Last Updated:** 2026-02-25
