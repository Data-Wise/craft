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
| 7 | Count Consistency | Stale `N commands`, `N skills`, `N agents` strings across all docs, plus the two prose checks below |
| 8 | Skill/Agent Coverage | Skills and agents not listed in `docs/skills-agents.md` |
| 9 | Cross-Doc Freshness | Stale version strings in REFCARDs, stale counts in "See Also" sections, `site_description` drift |

---

## Phase 7 prose checks

Added 2026-08-15 — [ADR-007](../adr/ADR-007-pattern-scoped-prose-staleness-gating.md),
[SPEC](../specs/SPEC-doc-staleness-prose-gaps-2026-08-07.md). Both emit `warning`.

| Check | What It Catches |
|-------|-----------------|
| Release-date claims | A `Released: YYYY-MM-DD` on the current version's line **or the 4 lines below it**, more than one day off the version's **git tag date**. The one-day window absorbs releases published across the UTC boundary. |
| Count prose in structured lines | A stale count — **singular or plural** — inside one of four line shapes. Free prose is never checked. |

**The release-date check is vacuous when its authority is unusable** — no tag for the current
version (normal on a feature branch), or a tag date that will not parse. It reports nothing rather
than everything: an empty accept-window would match no claim at all, turning one bad input into a
repo-wide false-positive storm. See [ADR-007](../adr/ADR-007-pattern-scoped-prose-staleness-gating.md).

The four line shapes:

| Shape | Matches |
|-------|---------|
| `version-box` | lines inside a `┌` … `└` box-drawing block — closes at the first line with no box-drawing character at all, even without a matching `└`, so a truncated box can't leak into later shapes |
| `tldr` | a line that opens with `TL;DR` (after optional blockquote/emphasis markers) — not merely one that mentions it, so a doc describing this bug isn't itself flagged for the example it quotes |
| `count-summary` | the bolded badge line, e.g. `**48 commands** \| **41 skills**` |
| `structure-table` | a table row whose first cell is a counted directory, e.g. `` \| `agents/` \| `` — compared only against the type that cell names |

Why shape-scoped: a blanket `N agents?` search over `docs/` returns 90+ hits, nearly
all legitimate (orchestration mode-limit prose, a fictional-plugin tutorial, a
troubleshooting page printing a wrong count on purpose). Shaped lines are additionally
held to the same 40%-of-expected floor as the broad scan, because boxes and badges
still carry category subtotals and subset counts.

Both prose findings are `uncertain`, so they surface in **Pass 2** (interactive), not Pass 1's
auto-apply — the surrounding prose is hand-authored, so a human sees the line before the number
changes under it. Choosing `[f]ix` there really does edit the file; it swaps the digits only,
leaving wording like `agent definitions` intact.

Fixtures and the table-driven runner: `tests/fixtures/prose-staleness/` +
`tests/test_docs_staleness_prose.py`. Every check has a `defect/` fixture as its
positive control; a check without one is a rejected change.

### Test-only environment overrides

| Variable | Effect |
|----------|--------|
| `CRAFT_EXPECTED_CMDS` / `_SKILLS` / `_AGENTS` | Declare expected counts instead of deriving them from `commands/`, `skills/`, `agents/`. Lets a fixture skip materializing 48 command files. |
| `CRAFT_RELEASE_DATE` | Supply the tag date instead of reading git, keeping the fixture suite hermetic. |

Unset on every production path — the derived values are what actually run.

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

`f` reports `Cannot auto-fix (manual edit needed)` when the finding carries no substitution to
run -- Phase 8's doc-coverage findings, for instance. Both passes apply fixes through the same
`apply_line_fix`, which reports success only when the file actually changed; see
[ADR-007](../adr/ADR-007-pattern-scoped-prose-staleness-gating.md) on why that is one shared
function and not two.

Pass 2 is skipped when `--non-interactive` is set, and when stdin is not a TTY (CI).

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

- `/folio:docs:check` (moved to folio) -- Full documentation health check (includes staleness via `--deep`)
- [Release Pipeline Reference](REFCARD-RELEASE.md) -- Step 2d integration
- [Post-Release Sweep Reference](REFCARD-POST-RELEASE-SWEEP.md) -- Shares exclusion config

---

**Version:** 2.28.0
**Last Updated:** 2026-02-25
