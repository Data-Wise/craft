# SPEC: Help File Template & Website Menu Design

**Status:** Draft
**Date:** 2026-01-16
**Priority:** High
**Target:** v1.21.0
**Effort:** ~30 hours (7 weeks phased)

---

## Problem Statement

Craft has 90 commands across 8 categories, making it hard for users to find specific commands. Current help files lack consistency - some commands have detailed help, others have minimal documentation, and there's no standardized structure. Users struggle with discoverability and need multiple attempts to find the right command.

---

## Solution Overview

Create a standardized markdown template for help files and reorganize the website menu with a flat category structure. Focus on progressive disclosure (TL;DR → Tabs → Reference) and search-first discovery.

**Key Principles:**
- ADHD-friendly design (TL;DR always at top, tabs hide complexity)
- Pure markdown (no dependencies, no tooling)
- Phased rollout (not big bang - validate early, adjust if needed)
- Search-first discovery (prominent search, keywords in frontmatter)

---

## Scope

### In Scope
- ✅ Markdown help file template with 10 sections
- ✅ Help homepage with popular commands + category tabs
- ✅ 8 category landing pages (one per command category)
- ✅ Navigation restructure in mkdocs.yml
- ✅ 3 pilot commands (validate template)
- ✅ Popular commands page (top 20-30)
- ✅ Pre-commit hook (detect missing help files)

### Out of Scope
- ❌ Auto-generation from command frontmatter (manual creation preserves quality)
- ❌ Help file validation script (future enhancement)
- ❌ Analytics tracking (nice-to-have)
- ❌ External link checking (focus on internal help navigation)

---

## Design

### Template Structure

**Required Sections (always include):**
1. **TL;DR** - 30-second answer (What, Why, How, Next)
2. **Quick Reference** - Copy-paste code snippet
3. **Overview** - 2-3 paragraphs context
4. **Usage Tabs** - Progressive disclosure (Basic → Options → Advanced)
5. **Examples** - 2+ real-world scenarios
6. **See Also** - 3-5 curated links

**Optional Sections (if applicable):**
7. **Options Table** - Flag reference
8. **Modes** - Execution mode explanation
9. **Troubleshooting** - Common errors & fixes
10. **Reference** - Technical metadata

### Menu Structure

**Before:**
```
Help:
  - /craft:hub
  - /craft:do
  - /craft:check
  - /craft:orchestrate
  - /craft:git:init
  - /craft:git:worktree
  ...
```

**After:**
```
Help:
  - Overview (homepage)
  - Popular Commands (top 20-30)
  - Smart Commands (category page)
  - Git Commands (category page)
  - Docs Commands (category page)
  - Site Commands (category page)
  - Code & Testing (category page)
  - CI & Distribution (category page)
  - Architecture (category page)
  - Workflow & Planning (category page)
```

---

## Implementation Phases

### Phase 0: Foundation (Week 1 - 4-6 hours)
**Goal:** Validate template with 3 pilots

**Files to Create:**
- `docs/templates/HELP-TEMPLATE.md` (200 lines)
- `docs/help/index.md` (150 lines)
- `docs/help/smart/index.md` (80 lines)
- `docs/help/smart/do.md` (migrate from existing)
- `docs/help/smart/check.md` (migrate from existing)
- `docs/help/smart/orchestrate.md` (migrate from existing)

**Files to Modify:**
- `mkdocs.yml` - Add Help section with categories
- `docs/CONTRIBUTING.md` - Add "Create help file" to checklist

**Success Criteria:**
- [ ] Template covers all sections
- [ ] 3 pilot commands follow template
- [ ] Help homepage renders correctly
- [ ] Site builds without errors

---

### Phase 1: Git Category (Week 2 - 6-8 hours)
**Goal:** Complete second category to validate landing page pattern

**Files to Create:**
- `docs/help/git/index.md`
- 6 git command help files (init, worktree, clean, sync, branch, recap)

**Success Criteria:**
- [ ] All 6 git commands documented
- [ ] Landing page shows workflows
- [ ] Cross-links work

---

### Phase 2: Docs + Site Categories (Week 3 - 6-8 hours)
**Files:** 11 help files (7 docs + 4 site)

---

### Phase 3: Code + CI Categories (Week 4 - 6-8 hours)
**Files:** 11 help files (5 code + 6 CI)

---

### Phase 4: Arch + Workflow Categories (Week 5 - 3-4 hours)
**Files:** 3 help files (1 arch + 2 workflow)

---

### Phase 5: Popular Commands (Week 6 - 2-3 hours)
**Files:** `docs/help/popular.md` (curated top 20-30)

---

### Phase 6: Pre-commit Hook (Week 7 - 2-3 hours)
**Goal:** Automated validation for new commands

**Integration:**
- Add to `/craft:git:init` command
- Append to existing pre-commit hook
- Prompt if help file missing

---

## Files Created/Modified

### New Files (Phase 0)
| File | Lines | Purpose |
|------|-------|---------|
| `docs/templates/HELP-TEMPLATE.md` | 200 | Template with all sections |
| `docs/help/index.md` | 150 | Help homepage |
| `docs/help/smart/index.md` | 80 | Smart category page |

### Modified Files (Phase 0)
| File | Changes |
|------|---------|
| `mkdocs.yml` | Add Help section with 8 categories |
| `docs/CONTRIBUTING.md` | Add help file creation checklist |

### Full Rollout (Phases 1-6)
- **Total new files:** ~50 help files + 8 category pages
- **Total lines:** ~8,000 lines of documentation

---

## Success Metrics

### Phase 0 (MVP)
| Metric | Target |
|--------|--------|
| Template sections | 10 documented |
| Pilot commands | 3 diverse |
| Site build | No errors |

### Phases 1-4 (Rollout)
| Metric | Target |
|--------|--------|
| Category coverage | 8 categories |
| Command coverage | Top 30 commands |
| Consistency | 100% follow template |
| Search | All findable |

### Phase 6 (Maintenance)
| Metric | Target |
|--------|--------|
| Hook detection | 100% new commands |
| False positives | < 5% |

---

## Risk Assessment

| Risk | Mitigation |
|------|------------|
| Template too rigid | 3 pilots validate early, adjust if needed |
| Migration loses content | "Audit and enhance" preserves examples |
| Too much effort | Phased rollout, focus on top 30 first |
| Search doesn't work | Keywords in frontmatter, test frequently |

---

## Dependencies

**None** - Pure markdown implementation

**Prerequisites:**
- MkDocs Material theme (already configured)
- Tab extension (already enabled)
- Search plugin (already enabled)

---

## Open Questions

1. **Auto-generate help files?**
   - Decision: No (manual creation preserves quality)

2. **Category landing page examples?**
   - Decision: No (keep concise, examples in individual pages)

3. **Commands without help files after Phase 6?**
   - Decision: TBD after Phase 4

4. **Track help coverage in .STATUS?**
   - Decision: Yes (`help_coverage: X/90 commands`)

---

## Next Steps

### Immediate (This Session)
1. Create `docs/templates/HELP-TEMPLATE.md`
2. Create `docs/help/index.md`
3. Create `docs/help/smart/index.md`
4. Migrate 3 pilot commands
5. Update `mkdocs.yml`

### Week 2+ (Follow Plan)
Execute Phases 1-6 as documented

---

**Specification Author:** Claude Sonnet 4.5
**Brainstorm Mode:** Deep Feature (16 questions)
**Plan File:** `/Users/dt/.claude/plans/purring-prancing-mango.md`
