# 🧠 BRAINSTORM: Merge `/craft:docs:sync` into `/craft:docs:update`

**Mode:** deep + optimize + save
**Duration:** Analysis + spec revision
**Generated:** 2026-01-22
**Decision:** ✅ MERGE (user selected)

---

## Context

Two craft commands with overlapping functionality:

1. **/craft:docs:sync** - Detection & Classification (read-only)
   - Scans git history for code changes
   - Scores what docs are needed (guide: 8, demo: 6, etc.)
   - Reports stale docs
   - Recommends `/craft:docs:update`

2. **/craft:docs:update** - Interactive Updates (write operations)
   - Updates version refs, counts, links
   - Regenerates GIFs
   - Creates/updates help files
   - Triggers lint, tutorials

**Problem:** Two separate commands for a single workflow (detect → update)

---

## Quick Wins (Merge Benefits)

⚡ **Single command UX**

- Users don't need to know about sync
- One command does detection + updates
- Less cognitive overhead

⚡ **Auto-detection**

- `/craft:docs:update` always detects first
- No manual sync step required
- Prioritized prompts (high-score categories first)

⚡ **Backward compatibility**

- `/craft:docs:sync` becomes alias
- Existing scripts still work
- Deprecation warning guides migration

⚡ **Code consolidation**

- Shared detection module
- No duplication
- Single source of truth

---

## Decision Matrix

### Options Considered

| Option | Pros | Cons | User Vote |
|--------|------|------|-----------|
| **Merge** | Single command, auto-detection, simpler UX | Breaking change for sync users | ✅ **SELECTED** |
| **Keep separate** | Clear separation, no breaking changes | Confusing workflow, duplication | ❌ |
| **Hybrid** | Sync as --detect flag | Middle ground complexity | ❌ |

**User Decision:** Merge - Single `/craft:docs:update` command

---

## Merged Command Behavior

### Default: Auto-Detect + Prompt

```bash
/craft:docs:update

# Step 1: Auto-detection (NEW - replaces manual sync)
Scanning git history (HEAD~10)...
Found 15 commits, 23 files changed

Classification:
  Guide:   ✓ 8  → Help files (priority: 10)
  Demo:    ✓ 6  → GIF regeneration (priority: 8)
  Stale:   ✓ 2  → Broken links (priority: 6)

# Step 2: Interactive prompts (EXISTING - prioritized by detection)
┌─────────────────────────────────────────────┐
│ Category: Help Files (Priority: 10)         │
├─────────────────────────────────────────────┤
│ Detected from git scan:                     │
│   • 5 new commands need help files          │
│   • Guide score: 8 (recommended)            │
│                                             │
│ Create help files for new commands?         │
│   ○ Yes - Create all (Recommended)          │
│   ○ No - Skip this category                 │
└─────────────────────────────────────────────┘
```

### Detection-Only Mode (Replaces /craft:docs:sync)

```bash
/craft:docs:update --detect-only

# Runs detection, shows report, exits (no prompts)
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:update --detect-only                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ 📊 DOCUMENTATION STATUS                                     │
│                                                             │
│ Recent changes: 15 commits, 23 files                        │
│ Feature detected: "session tracking"                        │
│                                                             │
│ Classification (scores):                                    │
│   Guide:   ✓ 8  → Help files + Changelog                    │
│   Demo:    ✓ 6  → GIF regeneration                          │
│   Stale:   ✓ 2  → Broken links                              │
│                                                             │
│ Run without --detect-only to apply updates interactively    │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Manual Mode (Skip Detection)

```bash
/craft:docs:update --no-detect

# Skips detection, uses manual category selection
# (Same as old update behavior)
```

---

## Migration Path

### Old Workflow

```bash
# Step 1: Detection
/craft:docs:sync
# Output: "Guide score: 8, suggested: /craft:docs:update"

# Step 2: Manual update
/craft:docs:update
# Prompts for categories (no prioritization)
```

### New Workflow

```bash
# Single command (detection + update)
/craft:docs:update
# Auto-detects, prioritizes, prompts, applies
```

### Backward Compatibility

```bash
# Old sync command still works
/craft:docs:sync

# Shows deprecation warning:
⚠️  /craft:docs:sync is deprecated
   Use: /craft:docs:update --detect-only
   (or just: /craft:docs:update for full workflow)

# Then executes as --detect-only mode
```

---

## Implementation Plan

### Phase 1: Detection Integration (Week 1)

**Goal:** Merge sync detection into update

1. Extract detection logic to `utils/docs_detector.py`
2. Integrate into `/craft:docs:update` as **Step 1**
3. Add `--detect-only` flag
4. Add `--no-detect` flag (skip detection)

**Deliverables:**

- `/craft:docs:update` always runs detection first
- `--detect-only` works like old sync
- No breaking changes to update behavior

### Phase 2: Priority Integration (Week 2)

**Goal:** Use detection scores to prioritize prompts

1. Map classifications (guide, demo) → update categories
2. Sort categories by score (highest first)
3. Show detection summary before prompts
4. Update prompt UX to show priorities

**Deliverables:**

- High-score categories prompted first
- Detection summary shown to user
- Prioritization transparent

### Phase 3: Deprecation (Week 3)

**Goal:** Deprecate `/craft:docs:sync`

1. Make sync an alias to `update --detect-only`
2. Add deprecation warning
3. Update all documentation
4. Create migration guide

**Deliverables:**

- `/craft:docs:sync` still works (aliased)
- Clear deprecation path
- Documentation updated

### Phase 4: Polish (Week 4)

**Goal:** Refine UX and performance

1. Optimize detection performance
2. Add comprehensive tests
3. Tutorial: "Documentation Workflow"
4. Remove old sync code (if no usage)

**Deliverables:**

- 90%+ test coverage
- Tutorial published
- Clean codebase

---

## Key Architectural Changes

### Before: Two Separate Commands

```python
# craft/commands/docs/sync.md
def docs_sync():
    detect_changes()
    classify_needs()
    show_report()
    # Recommend: /craft:docs:update

# craft/commands/docs/update.md
def docs_update():
    prompt_for_category()
    apply_updates()
    show_summary()
```

### After: Unified Command

```python
# craft/commands/docs/update.md (merged)
def docs_update(detect_only=False, no_detect=False):

    if not no_detect:
        # Step 1: Detection (from old sync)
        result = detect_changes()
        result = classify_needs(result)
        priorities = map_to_categories(result)

        if detect_only:
            show_sync_report(result)
            return  # Exit (no prompts)

        # Show detection summary
        show_detection_summary(result)

    else:
        # Manual mode (skip detection)
        priorities = None

    # Step 2: Interactive prompts (existing)
    categories = get_categories(priorities)
    prompt_for_each_category(categories)
    apply_updates()
    show_summary()

# craft/commands/docs/sync.md (deprecated alias)
def docs_sync(*args):
    print("⚠️ /craft:docs:sync is deprecated")
    print("   Use: /craft:docs:update --detect-only")
    docs_update(detect_only=True, *args)
```

---

## Success Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| **UX simplification** | 1 command instead of 2 | User surveys |
| **Workflow efficiency** | 50% faster (no manual sync) | Time tracking |
| **Adoption** | 90% use default (auto-detect) | Command invocations |
| **Migration** | 100% sync users migrated in 3 months | Deprecation warnings |
| **Code reduction** | -200 lines (shared module) | LOC count |

---

## Risks & Mitigation

| Risk | Impact | Mitigation |
|------|--------|------------|
| **Breaking changes** | High | Keep sync as alias with warning |
| **User confusion** | Medium | Clear migration guide + tutorial |
| **Performance** | Low | Optimize detection, cache results |
| **Feature regression** | Low | Comprehensive test suite |

---

## Open Questions

1. **Sync Deprecation Timeline**
   Q: When to remove `/craft:docs:sync` completely?
   Options: (a) 1 release; (b) 3 releases; (c) Never (always alias)
   **Recommendation:** (c) Always alias (no breaking changes)

2. **Default Detection Range**
   Q: Default git commit range for detection?
   Options: (a) HEAD~10; (b) HEAD~20; (c) User configurable
   **Recommendation:** (a) HEAD~10 (fast, recent changes)

3. **Detection Cache**
   Q: Should detection results be cached between runs?
   Options: (a) No cache; (b) Cache for 1 hour; (c) Cache until next run
   **Recommendation:** (a) No cache (always fresh)

4. **Verbose Mode Default**
   Q: Show detection summary by default or require --verbose?
   Options: (a) Always show; (b) Require --verbose; (c) Show if scores > threshold
   **Recommendation:** (a) Always show (transparency)

---

## Related Work

- **SPEC-docs-update-interactive-2026-01-22.md** - Interactive update workflow (63KB spec)
- **SPEC-docs-sync-update-integration-2026-01-22.md** - This spec (revised for merge)

---

## Files Created

- ✅ SPEC-docs-sync-update-integration-2026-01-22.md (Revised for merge decision)
- ✅ BRAINSTORM-docs-sync-update-merge-2026-01-22.md (This summary)

---

**Decision Finalized:** Merge `/craft:docs:sync` into `/craft:docs:update` with auto-detection
**Next Steps:** Update SPEC with merged command behavior
