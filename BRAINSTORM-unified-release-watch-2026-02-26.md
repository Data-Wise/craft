# BRAINSTORM: Unified Release Watch v2

**Date:** 2026-02-26
**Depth:** max | **Focus:** architecture
**Duration:** ~6 min (2 agents + research)
**Supersedes:** BRAINSTORM-release-watcher-2026-02-21.md

---

## Problem Statement

`release-watch.py` has 5 issues identified in a code review:

1. **Stale model patterns** -- missing Claude 4.x family model IDs
2. **Noisy keyword scanning** -- generic words like "new", "model" match nearly every line
3. **Fetches ALL releases** via `--paginate` then slices to 3 (wasteful)
4. **FIXED category never populates** from keyword matching (bug)
5. **Desktop releases invisible** -- `desktop-watch` relies on web search (unreliable)

The user wants a **unified tool** that tracks both Claude Code CLI and Claude Desktop in one command, with caching, cross-referencing, and auto-fix for safe items.

---

## Research Findings (2 Agents)

### Backend Architect: Data Source Strategy

| Product | Primary Source | Enrichment | Why |
|---------|---------------|------------|-----|
| Claude Code | GitHub Releases API (`?per_page=N`) | CHANGELOG.md (structured prefixes) | Releases API = metadata, CHANGELOG = richer categorization |
| Claude Desktop | Releasebot.io JSON/RSS | (none) | Only structured programmatic source; eliminates web search |

Key architectural decision: **single-file with section boundaries** (matching craft convention), not a package with subdirectories.

### Security Specialist: Risk Assessment

| Concern | Risk | Mitigation |
|---------|------|------------|
| Releasebot.io supply chain | HIGH | Source-tag findings; NEVER use for auto-fix input |
| Local cache poisoning | MEDIUM | `0o700`/`0o600` permissions; `--no-cache` flag |
| Auto-fix from upstream data | HIGH | Launch as **propose-only** (generate diff, don't apply) |
| `--paginate` over-fetching | MEDIUM | Use `per_page` param; early termination |
| CHANGELOG format changes | LOW | Warn on unrecognized format; supplementary only |
| False positives blocking releases | MEDIUM | Word-boundary matching (`\b`); advisory-only exit codes |

**Critical security rule:** Auto-fix proposals MUST only come from GitHub API data (authenticated via `gh`), never from releasebot.io.

---

## Architecture Design

### Data Flow

```
CLI: release-watch.py --product all --count 5
              │
              ▼
      ┌───────────────┐
      │  Cache Check   │  (~/.claude/release-watch-cache.json)
      │  Per-source    │  24h TTL, per-source independence
      └───────┬───────┘
              │ (stale sources only)
    ┌─────────┼──────────────┐
    ▼         ▼              ▼
 GitHub    CHANGELOG.md   Releasebot.io
 Releases  (enrichment)   (Desktop)
 ?per_page=10             (timeout: 10s)
    │         │              │
    └─────────┼──────────────┘
              ▼
      ┌───────────────┐
      │ Merge + Dedup │  Match by version, CHANGELOG enriches releases
      └───────┬───────┘
              ▼
      ┌───────────────┐
      │   Analyzer    │  Word-boundary keywords, craft state cross-ref
      └───────┬───────┘
              ▼
      ┌───────────────┐
      │  Auto-fix     │  Classify: safe (propose) vs review (report)
      │  Classifier   │  Only from GitHub source, never releasebot
      └───────┬───────┘
              ▼
      ┌───────────────┐
      │   Formatter   │  terminal / json / markdown
      └───────────────┘
```

### Cache Strategy

- **Location:** `~/.claude/release-watch-cache.json` (user-scoped, not project-scoped)
- **Per-source TTL:** Each source tracked independently (24h default)
- **Stale fallback:** If live fetch fails, use stale cache (better than nothing)
- **Atomic writes:** Write to `.tmp`, then rename (prevents corruption)
- **Flags:** `--refresh` (force all), `--no-cache` (for release pipeline)
- **Permissions:** `0o700` dir, `0o600` files

### Merge Logic

CHANGELOG.md prefixes map directly to finding categories:

| Prefix | Category | Better than keywords? |
|--------|----------|----------------------|
| `Added` | NEW | Yes -- explicit intent |
| `Fixed` | FIXED | Yes -- solves the FIXED bug |
| `Improved` | NEW | Yes -- not just "new" keyword |
| `Deprecated` | DEPRECATED | Yes -- precise |
| `Removed` / `Breaking` | BREAKING | Yes -- explicit |

When both GitHub release body AND CHANGELOG section exist for a version, CHANGELOG categories take precedence (structured > freeform keyword matching).

### Keyword Improvements

Replace substring matching with word-boundary regex:

```python
# Before (noisy): "new" matches "renewable"
kw.lower() in line_lower

# After (precise): "new" only matches word "new"
re.search(rf'\b{re.escape(kw)}\b', line_lower)
```

Add confidence scoring: 3+ keyword matches from same category = high confidence.

### Auto-Fix Design (Propose-Only v1)

**Safe (generate diff):**

- Update `MODEL_PATTERNS` list with new model IDs
- Add new keywords to `KEYWORD_CATEGORIES`

**Requires review (report only):**

- Breaking changes, deprecations, schema changes
- Any finding from releasebot.io source

```bash
# Usage
python3 scripts/release-watch.py --auto-fix

# Output: creates .claude/release-watch-fixes.patch
# User reviews and applies: git apply .claude/release-watch-fixes.patch
```

---

## New CLI Interface

```bash
# Unified: both products (new default)
python3 scripts/release-watch.py

# Code only (backward compatible)
python3 scripts/release-watch.py --product code

# Desktop only (replaces desktop-watch)
python3 scripts/release-watch.py --product desktop

# Fresh data, no cache
python3 scripts/release-watch.py --refresh

# Propose auto-fixes
python3 scripts/release-watch.py --auto-fix

# CI mode: only breaking/deprecated, non-zero exit on findings
python3 scripts/release-watch.py --strict
```

---

## Quick Wins (< 30 min each)

1. **Fix `--paginate` to `?per_page=N`** -- One line change, immediate perf improvement
2. **Add word-boundary matching** -- `\b` regex, reduces noise dramatically
3. **Update MODEL_PATTERNS** -- Add missing `claude-sonnet-4-6`, `claude-haiku-4-5`
4. **Fix FIXED category bug** -- Add `"fixed"` to `CATEGORY_MAP`

## Medium Effort (1-2 hours each)

5. **Cache layer** -- `~/.claude/release-watch-cache.json` with per-source TTL
6. **CHANGELOG.md parser** -- Fetch + parse structured prefixes, merge with releases
7. **Releasebot.io integration** -- JSON/RSS fetch for Desktop releases (need to verify API format first)

## Long-term (Future sessions)

8. **Auto-fix propose mode** -- Generate patch files for safe items
9. **`--strict` CI mode** -- Only BREAKING/DEPRECATED, non-zero exit
10. **Deprecate `desktop-watch` command** -- Redirect to `release-watch --product desktop`

---

## Implementation Order

| # | Deliverable | Effort | Dependencies |
|---|-------------|--------|--------------|
| 1 | Quick wins (#1-4 above) | 30 min | None |
| 2 | Cache layer | 30 min | None |
| 3 | CHANGELOG.md parser + merge | 1 hour | Cache |
| 4 | Verify releasebot.io API | 15 min | None (research) |
| 5 | Releasebot.io fetcher | 1 hour | Cache + API verification |
| 6 | `--product` flag + unified output | 30 min | Sources |
| 7 | Auto-fix propose mode | 45 min | Analyzer |
| 8 | Update command files + tests | 30 min | All above |

**Total:** ~5 hours across 2-3 sessions

---

## Key Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Unified vs separate tools | Unified (`--product` flag) | User preference + eliminates web search dependency |
| Releasebot.io trust level | Secondary source, read-only | Security agent: HIGH risk for auto-fix, OK for findings |
| Auto-fix approach | Propose-only (patch file) | Security agent: direct modification too risky for v1 |
| Cache location | `~/.claude/` (user-scoped) | Releases are the same across projects |
| CHANGELOG as source | Cross-reference enrichment | Structured prefixes > keyword matching |
| Keyword matching | Word-boundary regex | Reduces false positives dramatically |

---

## Open Questions

1. **Releasebot.io API format** -- Need to verify JSON endpoint exists. RSS is fallback.
2. **Should `sync-features` skill be updated?** -- Currently chains 3 separate commands; unified tool simplifies Step 2+3.
3. **Test strategy** -- Existing tests use `@requires_gh`. How to test releasebot.io integration without network? Mock? Fixture?

---

## Related Artifacts

- Previous brainstorm: `BRAINSTORM-release-watcher-2026-02-21.md`
- Previous spec: `docs/specs/SPEC-release-watcher-2026-02-21.md`
- Current script: `scripts/release-watch.py` (610 lines)
- Current tests: `tests/test_release_watch.py`
- Command: `commands/code/release-watch.md`
- Desktop command: `commands/code/desktop-watch.md`

Sources:

- [Claude Code Releases](https://github.com/anthropics/claude-code/releases)
- [Claude Code CHANGELOG.md](https://github.com/anthropics/claude-code/blob/main/CHANGELOG.md)
- [Releasebot.io - Claude](https://releasebot.io/updates/anthropic/claude)
- [Releasebot.io - Claude Apps](https://releasebot.io/updates/anthropic/claude-apps)
- [Anthropic Release Notes](https://support.claude.com/en/articles/12138966-release-notes)
