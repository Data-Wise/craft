# Orchestration: Docs Staleness Detection System

**Branch:** `feature/docs-staleness-detection`
**Base:** `dev` @ `d46d3d8c`
**Brainstorm:** `BRAINSTORM-docs-staleness-detection-2026-02-25.md`

---

## Overview

Build `scripts/docs-staleness-check.sh` -- a 4-phase documentation staleness detector with two-pass interactive review, shared exclusion config, and traffic light output. Integrates as Step 2d in the release pipeline.

---

## Step 1: Shared Exclusion Config

**Create:** `scripts/config/exclusions.txt`

Seed with known exclusions discovered this session:

```text
# Whole-file exclusions
docs/VERSION-HISTORY.md
docs/CHANGELOG.md
docs/specs/_archive/
docs/demos/

# Pattern exclusions (file:pattern)
docs/architecture/HUB-V2-ARCHITECTURE.md:97 commands
docs/tutorials/TUTORIAL-post-merge-pipeline.md:97 commands
docs/demos/hub-v2.tape:97 commands
docs/api/DISCOVERY-API.md:97 commands
docs/API-REFERENCE-COMMANDS.md:97 commands
docs/reference/ERROR-SCENARIOS.md:97 commands
docs/dev/CONTRIBUTING-HUB-V2.md:97 commands
docs/examples/docs-update-interactive-example.md:99 commands
docs/REFCARD.md:99 commands
docs/reference/REFCARD-DOCS-UPDATE.md:99 commands
docs/tutorials/interactive-docs-update-tutorial.md:99 commands
```

**Commit:** `feat: add shared exclusion config for docs staleness detection`

---

## Step 2: Core Script Skeleton

**Create:** `scripts/docs-staleness-check.sh`

Structure:

```text
#!/usr/bin/env bash
# Post: formatting.sh sourced for color output
# Args: --fix, --non-interactive, --json, --audit-exclusions, --version X.Y.Z

main()
  parse_args (while/shift pattern)
  load_exclusions()
  load_counts() -- call validate-counts.sh
  load_version() -- read from plugin.json

  phase6_nav_completeness()
  phase7_count_consistency()
  phase8_skill_agent_coverage()
  phase9_cross_doc_freshness()

  if --fix: pass1_auto_fix()
  if --fix and not --non-interactive: pass2_interactive_review()

  print_summary() -- traffic light status
  exit with appropriate code
```

Use `while [[ $# -gt 0 ]]; do ... shift; done` for arg parsing (lesson from PR #110).

**Commit:** `feat: add docs-staleness-check.sh skeleton with arg parsing and exclusion loading`

---

## Step 3: Phase 6 -- Nav Completeness

Implement nav completeness detection:

1. Extract all `.md` paths from `mkdocs.yml` nav section
2. Find all `.md` files in `docs/` (excluding paths in exclusions.txt)
3. Report files on disk but not in nav
4. Report nav entries pointing to missing files

Key considerations:

- mkdocs.yml nav uses relative paths from `docs/` (e.g., `guide/desktop-release.md`)
- Some dirs are legitimately excluded (`docs_dir` exclusions in mkdocs.yml)
- Parse the `exclude_docs` config from mkdocs.yml if present

**Commit:** `feat: implement Phase 6 nav completeness check`

---

## Step 4: Phase 7 -- Count Consistency

Implement count scanning:

1. Run `validate-counts.sh` to get authoritative counts
2. Grep all non-excluded docs for `\d+ commands`, `\d+ skills`, `\d+ agents`
3. Compare against authoritative counts
4. Mark fixable items (exact count swaps) vs uncertain items (counts in context)
5. `--fix` mode: sed-replace fixable items

Key considerations:

- Match whole-word patterns to avoid false positives (e.g., "97 commands" but not "fetch 97 commands from")
- Some counts are embedded in sentences, some in table cells, some in badges
- Skip excluded files and patterns from exclusions.txt
- JSON quote escaping for `--json` mode (lesson from PR #110)

**Commit:** `feat: implement Phase 7 count consistency check with auto-fix`

---

## Step 5: Phase 8 -- Skill/Agent Coverage

Implement coverage detection:

1. `find skills -name "*.md"` to get all skill files
2. Parse each skill's frontmatter for `name` and `description`
3. Check if skill path appears in `docs/skills-agents.md` AND `docs/guide/skills-agents.md`
4. Same for agents: `find agents -name "*.md"`
5. Report undocumented skills/agents

`--fix` mode:

1. Determine category from filesystem path (e.g., `skills/code/sync-features.md` -> Code)
2. Find the correct category table in both skills-agents.md files
3. Append a new row: `| name | description from frontmatter | path |`
4. Update the category count in the heading (e.g., `### Code (0)` -> `### Code (1)`)

Key considerations:

- Frontmatter parsing: handle both `---` delimited YAML and bare markdown
- Category matching: skill dir name maps to heading name (lowercase -> Title Case)
- If category heading doesn't exist yet, create it in alphabetical order

**Commit:** `feat: implement Phase 8 skill/agent coverage check with auto-add`

---

## Step 6: Phase 9 -- Cross-Doc Freshness

Implement cross-doc freshness detection:

1. Scan "See Also" sections for count patterns (e.g., `26 skills, 8 agents`)
2. Scan REFCARD files for `Version:` headers with old version
3. Compare `mkdocs.yml` `site_description` against latest CHANGELOG entry headline
4. Architecture docs: flag stale metrics as warnings (not errors)

Key considerations:

- "See Also" pattern: `\d+ skills.*\d+ agents` or `\d+ agents.*\d+ skills`
- REFCARD version pattern: `**Version**: v?X.Y.Z` or `Version: X.Y.Z`
- site_description: extract first feature mention, compare against CHANGELOG v{CURRENT}
- Architecture docs are always warnings, never errors (per decision)

**Commit:** `feat: implement Phase 9 cross-doc freshness check`

---

## Step 7: Two-Pass Interactive Review

Implement the two-pass UX:

### Pass 1 (auto-fix, non-interactive)

- Collect all Phase 7 fixable items and Phase 8 auto-addable skills
- Apply fixes via sed/append
- Report what was fixed

### Pass 2 (interactive, skipped with --non-interactive)

- Present remaining uncertain items one at a time
- Options: `[f]ix / [s]kip / [e]xclude permanently`
- `[e]xclude`: append to `scripts/config/exclusions.txt` with auto-generated reason
- `[f]ix`: apply sed replacement
- `[s]kip`: do nothing

Key considerations:

- Script must work in non-TTY mode (CI) -- `--non-interactive` skips Pass 2
- Track fix count and exclusion count for summary

**Commit:** `feat: implement two-pass interactive review for --fix mode`

---

## Step 8: Audit Subcommand

Implement `--audit-exclusions`:

1. Read `scripts/config/exclusions.txt`
2. For each file exclusion: check if file exists on disk
3. For each pattern exclusion: check if pattern still matches in the file
4. Report stale exclusions
5. If interactive: prompt to remove each stale exclusion
6. If `--non-interactive`: just report

**Commit:** `feat: implement --audit-exclusions for exclusion list maintenance`

---

## Step 9: Traffic Light Output and JSON

Implement output formatting:

### Traffic light

```text
Phase 6: Nav Completeness ............ GREEN (0 issues)
Phase 7: Count Consistency ........... YELLOW (3 warnings)
Phase 8: Skill/Agent Coverage ........ GREEN (0 issues)
Phase 9: Cross-Doc Freshness ......... YELLOW (2 warnings)

Status: YELLOW (5 warnings, 0 errors)
```

- GREEN: 0 issues in that phase
- YELLOW: warnings only (arch docs, uncertain items)
- RED: errors (missing nav for new files, wrong counts in primary docs)

### JSON output (`--json`)

```json
{
  "version": "2.27.0",
  "status": "YELLOW",
  "phases": {
    "nav_completeness": {"status": "GREEN", "issues": 0, "findings": []},
    "count_consistency": {"status": "YELLOW", "issues": 3, "findings": [...]},
    "skill_agent_coverage": {"status": "GREEN", "issues": 0, "findings": []},
    "cross_doc_freshness": {"status": "YELLOW", "issues": 2, "findings": [...]}
  },
  "total_issues": 5,
  "total_fixed": 0
}
```

**Commit:** `feat: add traffic light output and JSON mode`

---

## Step 10: Tests

**Create:** `tests/test_docs_staleness.py`

Test cases:

1. Script runs without error on current repo (`--non-interactive`)
2. Exclusion config parsing: file exclusions, pattern exclusions, comments, blank lines
3. Phase 6: detects a file not in nav (create temp file in docs/, verify detected)
4. Phase 7: detects stale count (temporarily modify a file, verify detected)
5. Phase 8: detects undocumented skill (verify known exclusions don't trigger)
6. Phase 9: detects stale version in REFCARD pattern
7. `--json` output is valid JSON
8. `--audit-exclusions` reports stale entries
9. Exit codes: 0 (GREEN), 1 (YELLOW/RED), 2 (usage error)
10. `--fix --non-interactive` mode auto-fixes and reports

**Commit:** `test: add docs staleness detection tests`

---

## Step 11: Documentation and Integration

### Create REFCARD

**Create:** `docs/reference/REFCARD-DOCS-STALENESS.md`

Contents: usage, phases, exclusion format, traffic light meanings, integration with release pipeline.

### Update existing docs

- `skills/release/SKILL.md` -- add Step 2d to pre-flight checks
- `commands/docs/check.md` -- document `--deep` flag
- `docs/reference/REFCARD-RELEASE.md` -- add Step 2d to pipeline table
- `CLAUDE.md` -- add to Quick Commands table
- `mkdocs.yml` -- add REFCARD to nav
- `CHANGELOG.md` -- add entry under next version

### Update post-release-sweep.sh

- Source shared exclusion config instead of hardcoded file list
- Keep existing Tier 2 version scanning logic

**Commit:** `docs: add REFCARD and update release pipeline docs for staleness check`

---

## Step 12: Final Validation

1. Run `./scripts/docs-staleness-check.sh` -- verify traffic light output
2. Run `./scripts/docs-staleness-check.sh --json | python3 -m json.tool` -- verify JSON
3. Run `./scripts/docs-staleness-check.sh --audit-exclusions` -- verify audit
4. Run full test suite: `python3 -m pytest tests/ -v`
5. Run `mkdocs build --strict` -- verify no warnings
6. Run `./scripts/validate-counts.sh` -- verify counts still match
7. Run `./scripts/post-release-sweep.sh` -- verify no regression

**Commit:** (no commit -- validation only)

---

## Summary

| Step | What | Commit |
|------|------|--------|
| 1 | Shared exclusion config | `feat: add shared exclusion config` |
| 2 | Script skeleton + arg parsing | `feat: add script skeleton` |
| 3 | Phase 6: Nav completeness | `feat: implement Phase 6` |
| 4 | Phase 7: Count consistency | `feat: implement Phase 7` |
| 5 | Phase 8: Skill/agent coverage | `feat: implement Phase 8` |
| 6 | Phase 9: Cross-doc freshness | `feat: implement Phase 9` |
| 7 | Two-pass interactive review | `feat: implement two-pass review` |
| 8 | Audit subcommand | `feat: implement --audit-exclusions` |
| 9 | Traffic light + JSON output | `feat: add output formatting` |
| 10 | Tests | `test: add staleness tests` |
| 11 | Docs + integration | `docs: add REFCARD and pipeline updates` |
| 12 | Final validation | (no commit) |
