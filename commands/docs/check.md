---
description: Documentation health check (links, staleness, navigation)
category: docs
arguments:
  - name: fix
    description: Auto-fix safe issues
    required: false
    default: false
  - name: dry-run
    description: Preview checks without fixing
    required: false
    default: false
    alias: -n
---

# /craft:docs:check - Documentation Health Check

You are a documentation health checker. Validate, fix, and report on documentation status.

## Purpose

**Full documentation health check by default:**
- Broken links (internal and external)
- Stale docs (not updated when code changed)
- Navigation consistency (mkdocs.yml)
- Auto-fix safe issues
- Report what needs human attention

## Philosophy

> **"Just run it. It fixes what it can and tells you what needs attention."**

## Usage

```bash
# DEFAULT: Full check cycle (links + stale + nav + auto-fix)
/craft:docs:check

# LIMIT SCOPE
/craft:docs:check --report-only       # No auto-fix, just report
/craft:docs:check --links-only        # Just broken links (fast)
/craft:docs:check --no-stale          # Skip stale detection

# CI MODE (use in pipelines)
/craft:docs:check --report-only       # Safe for CI - no modifications
```

## When Invoked

### Step 1: Scan Documentation

```bash
# Find all markdown files
find docs/ -name "*.md" -type f

# Find README and other root docs
ls *.md CLAUDE.md 2>/dev/null

# Check mkdocs.yml for nav entries
cat mkdocs.yml | grep -A 100 "nav:"
```

### Step 2: Run Full Check Cycle

**Phase 1: Link Validation**
```
🔗 CHECKING LINKS...

Internal links:
  ✓ docs/index.md → docs/guide/overview.md
  ✓ docs/guide/overview.md → docs/reference/api.md
  ✗ docs/guide/setup.md → docs/config.md (not found)

External links:
  ✓ README.md → https://github.com/user/repo
  ⚠ README.md → https://old-domain.com/docs (404)

Summary: 45 internal (1 broken), 12 external (1 broken)
```

**Phase 2: Stale Detection**
```
📅 CHECKING STALE DOCS...

Comparing doc modification dates with related code changes...

  ⚠ docs/guide/auth.md
    Last updated: 45 days ago
    Related code changed: 12 days ago (src/auth/)

  ⚠ docs/reference/api.md
    Last updated: 32 days ago
    Related code changed: 5 days ago (src/api/)

Summary: 2 docs may be stale
```

**Phase 3: Navigation Consistency**
```
📁 CHECKING NAVIGATION...

mkdocs.yml nav entries:
  ✓ guide/quickstart.md exists
  ✓ guide/installation.md exists
  ✗ guide/configuration.md missing (in nav but file not found)

Orphan files (not in nav):
  ⚠ docs/guide/advanced-tips.md

Summary: 1 missing, 1 orphan
```

**Phase 4: Auto-Fix Safe Issues**
```
🔧 AUTO-FIXING...

  ✓ Fixed: docs/guide/setup.md
    Link updated: docs/config.md → docs/reference/configuration.md

  ✓ Fixed: mkdocs.yml
    Added missing nav entry: guide/advanced-tips.md

Auto-fixed: 2 issues
```

### Step 3: Show Summary Report

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:check                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Fixed: 2 broken links (auto-fixed)                        │
│ ✓ Fixed: 1 nav entry (auto-added)                           │
│                                                             │
│ ⚠ Stale: 2 docs haven't been updated in 30+ days            │
│   - docs/guide/auth.md (45 days, code changed)              │
│   - docs/reference/api.md (32 days, code changed)           │
│                                                             │
│ ✗ Manual: 1 issue needs attention                           │
│   - External link 404: README.md:120                        │
│     https://old-domain.com/docs                             │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Summary: 3 fixed, 2 stale, 1 manual                         │
│                                                             │
│ Next steps:                                                 │
│   → Update stale docs: /craft:docs:update                   │
│   → Fix manual issues: edit README.md:120                   │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Check Types

### Link Validation

| Type | Check | Auto-Fix |
|------|-------|----------|
| Internal `.md` | File exists | ✓ Update path if found elsewhere |
| Internal `#anchor` | Heading exists | ✗ Report only |
| External `http` | Returns 200 | ✗ Report only |
| Image | File exists | ✓ Update path if found elsewhere |

### Stale Detection

| Criteria | Threshold | Action |
|----------|-----------|--------|
| Doc not updated | 30+ days | ⚠ Warning |
| Related code changed | After doc update | ⚠ Warning |
| Both conditions | - | ⚠⚠ High priority |

**Related code detection:**
- `docs/guide/auth.md` → `src/auth/`, `src/**/auth*`
- `docs/reference/api.md` → `src/api/`, `src/**/api*`
- Filename-based matching

### Navigation Consistency

| Check | Auto-Fix |
|-------|----------|
| File in nav but missing | ✗ Report (may be intentional) |
| File exists but not in nav | ✓ Add to appropriate section |
| Nav order issues | ✗ Report only |

## Output Modes

### Default (Interactive)
Full visual output with boxes, colors, and actionable suggestions.

### JSON (`--json`)
```json
{
  "status": "issues_found",
  "fixed": {
    "links": 2,
    "nav": 1
  },
  "stale": [
    {"file": "docs/guide/auth.md", "days": 45, "code_changed": true}
  ],
  "manual": [
    {"type": "external_link", "file": "README.md", "line": 120, "url": "https://old-domain.com/docs"}
  ]
}
```

### CI Mode (`--report-only`)
```
DOCS CHECK: 3 issues found

BROKEN LINKS (1):
  - README.md:120 → https://old-domain.com/docs (404)

STALE DOCS (2):
  - docs/guide/auth.md (45 days)
  - docs/reference/api.md (32 days)

Exit code: 1
```

## Flags Reference

| Flag | Effect |
|------|--------|
| (none) | Full check: links + stale + nav + auto-fix |
| `--report-only` | No auto-fix, just report (CI-safe) |
| `--links-only` | Just broken links (fast) |
| `--no-stale` | Skip stale detection |
| `--no-nav` | Skip navigation check |
| `--json` | JSON output |
| `--verbose` | Detailed output |

## Integration

**Called by:**
- `/craft:docs:update` - Runs check after generating docs

**Works with:**
- `/craft:docs:sync` - Detection pairs with check
- `/craft:docs:guide` - Validate generated guides
- `/craft:ci:validate` - Part of CI pipeline

## CI Pipeline Usage

```yaml
# .github/workflows/docs.yml
- name: Check Documentation
  run: |
    # Use --report-only in CI (no auto-modifications)
    claude "/craft:docs:check --report-only"
```

## Examples

```bash
# Daily workflow: just run it
/craft:docs:check
# → Fixes what it can, reports the rest

# Before PR: quick link check
/craft:docs:check --links-only
# → Fast, just broken links

# CI pipeline: report only
/craft:docs:check --report-only
# → No changes, exit code for CI

# Full report for review
/craft:docs:check --report-only --verbose
# → Detailed report, no changes
```

## Dry-Run Mode

```
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Documentation Health Check                         │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Checks to Perform:                                          │
│   1. Broken links (internal & external)                       │
│   2. Stale documentation detection                            │
│   3. Navigation consistency (mkdocs.yml)                      │
│   4. Spelling and grammar                                     │
│   5. Code block validation                                    │
│                                                               │
│ ✓ Files to Check:                                             │
│   - docs/*.md (~45 files)                                     │
│   - mkdocs.yml                                                │
│   - README.md                                                 │
│                                                               │
│ ⚠ Auto-fix Available:                                         │
│   • Use --fix to apply safe corrections                        │
│                                                               │
│ 📊 Summary: Read-only health check (5 validation types)        │
│                                                               │
├───────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                              │
└───────────────────────────────────────────────────────────────┘
```

**Note**: This is a read-only check, so dry-run shows what will be validated.

## See Also

- `/craft:site:check` - Site validation
- Template: `templates/dry-run-pattern.md`
