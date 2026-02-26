# ORCHESTRATE: Unified Release Watch v2

**Feature Branch:** `feature/unified-release-watch`
**Spec:** `docs/specs/SPEC-unified-release-watch-2026-02-26.md`
**Brainstorm:** `BRAINSTORM-unified-release-watch-2026-02-26.md`
**Created:** 2026-02-26
**Estimated:** ~5 hours across 2-3 sessions

---

## Goal

Redesign `scripts/release-watch.py` to track both Claude Code CLI and Claude Desktop releases in a single unified tool. Replace noisy keyword-only scanning with structured CHANGELOG parsing, add a 24h cache, integrate releasebot.io for Desktop tracking, and introduce propose-only auto-fix.

## Architecture

Single-file layout (matches craft convention):

```
scripts/release-watch.py
  ├── Constants & Config (MODEL_PATTERNS, KEYWORD_CATEGORIES, CATEGORY_MAP)
  ├── Cache Layer (load, save, freshness check)
  ├── Source: GitHub Releases API (?per_page=N)
  ├── Source: GitHub CHANGELOG.md (parser)
  ├── Source: Releasebot.io (Desktop)
  ├── Merge & Deduplicate
  ├── Analyzer (word-boundary keyword scan + craft state)
  ├── Auto-Fix Classifier (safe=patch, review=report)
  ├── Formatters (terminal, json, markdown)
  └── Main (CLI + orchestration)
```

## Increments

### Increment 1: Quick Wins (30 min) — Session 1

**Files:** `scripts/release-watch.py`
**Risk:** Low

Tasks:

- [x] Fix `--paginate` to `?per_page=N` — uses URL query param (not -f flag)
- [x] Add word-boundary matching — `re.search(rf'\b...\b', ...)`
- [x] Update MODEL_PATTERNS — added sonnet-4-6, haiku-4-5, future-proof regex
- [x] Fix FIXED category bug — added "fixed" keyword category + CATEGORY_MAP entry

**Verify:**

```bash
python3 tests/test_release_watch.py  # All existing tests pass
python3 scripts/release-watch.py --product code --count 3 --format json  # Fewer API calls, word-boundary matches
```

---

### Increment 2: Cache Layer (30 min) — Session 1

**Files:** `scripts/release-watch.py`
**Risk:** Low

Tasks:

- [ ] Add cache constants

  ```python
  CACHE_DIR = Path.home() / ".claude"
  CACHE_FILE = CACHE_DIR / "release-watch-cache.json"
  CACHE_TTL = 86400  # 24 hours
  ```

- [x] Implement `load_cache()` — read JSON, return dict with per-source entries
- [x] Implement `save_cache(data)` — atomic write (tmp + rename), `0o700` dir, `0o600` file
- [x] Implement `is_fresh(cache_entry, source)` — check timestamp vs TTL
- [x] Add `--refresh` flag — force all sources stale
- [x] Add `--no-cache` flag — skip cache entirely
- [x] Stale fallback: if live fetch fails and stale cache exists, use it with warning

**Verify:**

```bash
python3 scripts/release-watch.py --count 3  # Creates cache
python3 scripts/release-watch.py --count 3  # Uses cache (faster)
python3 scripts/release-watch.py --refresh   # Bypasses cache
ls -la ~/.claude/release-watch-cache.json    # Exists with correct permissions
```

---

### Increment 3: CHANGELOG.md Parser (1 hour) — Session 1 or 2

**Files:** `scripts/release-watch.py`
**Risk:** Medium (CHANGELOG format may vary)

Tasks:

- [x] Implement `fetch_changelog()` — fetch via gh API + base64 decode, cached
- [x] Implement `parse_changelog(content)` — `## version` headers, prefix categorization
- [x] Implement `merge_changelog_with_releases()` — adds `body_changelog` field
- [x] CHANGELOG categories take precedence in `scan_releases()` via lookup table
- [x] Graceful degradation: warns and continues if fetch fails

**Verify:**

```bash
python3 scripts/release-watch.py --count 5 --format json | python3 -m json.tool
# Check that findings have CHANGELOG-enriched categories
```

---

### Increment 4: Verify Releasebot.io API (15 min) — Session 1 (parallel research)

**Files:** None (research only, document findings in this file)

Tasks:

- [x] Check JSON endpoint — all return 404
- [x] Check apps endpoint — 404
- [x] Check RSS fallback — 404 (all feeds require auth)
- [x] Document response format — no public API exists
- [x] Determine Desktop endpoint — "claude-apps" slug, upstream at docs.anthropic.com
- [x] Decision: fetch docs.anthropic.com directly instead of releasebot.io

**Findings (completed 2026-02-26):**

```
Releasebot.io API:
  JSON endpoint: DOES NOT EXIST (all .json URLs return 404)
  RSS endpoint:  DOES NOT EXIST (all .rss URLs return 404)
  Feed access:   Authenticated only — requires account at /notifications

  Desktop releases: Use product slug "claude-apps" (63 entries)
  Upstream source:  https://docs.anthropic.com/en/release-notes/claude-apps

  Rate limits: Not publicly documented
  Authentication: Account token required for any feed format

  DECISION: Fetch upstream source directly (docs.anthropic.com)
  instead of releasebot.io. Source tag: "anthropic-docs"
```

---

### Increment 5: Releasebot.io Fetcher + --product Flag (1 hour) — Session 2

**Files:** `scripts/release-watch.py`, `commands/code/release-watch.md`
**Risk:** Medium (depends on Increment 4 research)
**Depends on:** Increment 2 (cache), Increment 4 (API verification)

Tasks:

- [x] Implement `fetch_desktop_releases()` — fetches from docs.anthropic.com (not releasebot)
- [x] HTML parser extracts date-based entries with feature descriptions
- [x] Add `--product` flag: all/code/desktop with backward compat
- [x] Integrate with cache layer (per-source TTL)
- [x] Security: Desktop data source-tagged, NEVER used for auto-fix

**Verify:**

```bash
python3 scripts/release-watch.py --product desktop  # Desktop releases shown
python3 scripts/release-watch.py --product code     # Backward compatible
python3 scripts/release-watch.py                     # Both products
```

---

### Increment 6: Auto-Fix Propose Mode (45 min) — Session 2

**Files:** `scripts/release-watch.py`
**Risk:** Low
**Depends on:** Increment 3 (analyzer)

Tasks:

- [x] Implement `classify_action_items(findings)` — safe vs review classification
- [x] Implement `generate_patch(safe_items)` — unified diff for MODEL_PATTERNS
- [x] Add `--auto-fix` flag — triggers patch generation
- [x] Report all items (safe proposed as patch, review items listed)

**Verify:**

```bash
python3 scripts/release-watch.py --auto-fix
cat .claude/release-watch-fixes.patch  # Valid patch
git apply --check .claude/release-watch-fixes.patch  # Validates
```

---

### Increment 7: Unified Output + Command Updates (30 min) — Session 2

**Files:** `scripts/release-watch.py`, `commands/code/release-watch.md`, `commands/code/desktop-watch.md`
**Risk:** Low
**Depends on:** Increment 5

Tasks:

- [x] Update terminal formatter — unified Code + Desktop sections
- [x] JSON v2 schema — version field, desktop findings, product-aware
- [x] Markdown formatter — per-product sections
- [x] Update `commands/code/release-watch.md` — new flags, JSON v2 schema
- [x] Update `commands/code/desktop-watch.md` — redirects to --product desktop
- [x] Update `skills/code/sync-features.md` — simplified to unified command

**Verify:**

```bash
python3 scripts/release-watch.py --format json | python3 -c "import json,sys; d=json.load(sys.stdin); assert d['version']==2"
```

---

### Increment 8: Tests (30 min) — Session 2 or 3

**Files:** `tests/test_release_watch.py`
**Risk:** Low
**Depends on:** All above

Tasks:

- [ ] Add cache tests
  - `test_cache_creation` — verify file created with correct permissions
  - `test_cache_freshness` — verify TTL check logic
  - `test_cache_stale_fallback` — verify stale data used when fetch fails
- [ ] Add CHANGELOG parser tests
  - `test_parse_changelog_added` — Added items map to NEW
  - `test_parse_changelog_fixed` — Fixed items map to FIXED
  - `test_parse_changelog_format_error` — graceful degradation on bad format
- [ ] Add Desktop source tests
  - `test_releasebot_source_tag` — all entries tagged with source
  - `test_releasebot_excluded_from_autofix` — security constraint
- [ ] Add backward compatibility test
  - `test_v1_json_compat` — `--product code --format json` output parseable by v1 consumers
- [ ] Add word-boundary matching tests
  - `test_word_boundary_no_false_positive` — "new" doesn't match "renewable"
  - `test_word_boundary_matches` — "new" matches "new feature"

**Verify:**

```bash
python3 -m pytest tests/test_release_watch.py -v  # All tests pass
```

---

## Session Plan

### Session 1 (~2.5 hours)

1. Increment 1: Quick wins
2. Increment 4: Releasebot research (can do early, informs later work)
3. Increment 2: Cache layer
4. Increment 3: CHANGELOG parser (start, may continue into Session 2)

### Session 2 (~2 hours)

5. Increment 5: Releasebot fetcher + --product flag
6. Increment 6: Auto-fix propose mode
7. Increment 7: Unified output + command updates

### Session 3 (~30 min)

8. Increment 8: Tests
9. Final integration test: run full `python3 scripts/release-watch.py --format json`
10. PR creation: `gh pr create --base dev`

---

## Security Checklist

- [ ] Releasebot.io data source-tagged on all findings
- [ ] Auto-fix NEVER uses releasebot.io data
- [ ] Auto-fix generates .patch file only (propose-only, never modifies files)
- [ ] Cache file permissions: `0o700` dir, `0o600` files
- [ ] All subprocess calls use list-form `subprocess.run()` (no shell injection)
- [ ] Subprocess timeouts: 30s GitHub API, 10s releasebot.io
- [ ] Exit code always 0 (advisory tool, not a gate)

## Backward Compatibility

- [ ] `--product code` produces identical output to current v1
- [ ] `--count N` still works
- [ ] `--format json` with `--product code` is parseable by existing consumers
- [ ] All existing tests in `test_release_watch.py` pass unchanged

## Done Criteria

- [ ] All acceptance criteria from spec met
- [ ] All existing tests pass + new tests added
- [ ] `python3 scripts/release-watch.py` shows both Code and Desktop
- [ ] `python3 scripts/release-watch.py --product code` backward compatible
- [ ] Cache working with correct permissions
- [ ] Auto-fix generates valid patch file
- [ ] PR created to dev
