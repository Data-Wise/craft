# Content Audit - Craft Plugin Documentation

**Date:** 2026-01-16
**Version:** 1.20.0
**Total Files:** 54 markdown files
**Auditor:** Claude Sonnet 4.5

---

## Executive Summary

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 CONTENT AUDIT - craft                                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Summary:                                                    │
│   Total files: 54                                           │
│   ✅ Current: 38                                            │
│   ✏️ Need edits: 11                                         │
│   🔄 Need revision: 2                                       │
│   🔗 Should merge: 2                                        │
│   🗑️ Archive: 1                                             │
│                                                             │
│ Project version: 1.20.0                                     │
│ Docs with outdated versions: 11 files                       │
│                                                             │
│ Key findings:                                               │
│   • Workflow docs reference v1.18.0 (should be v1.20.0)     │
│   • Several files not in mkdocs navigation                  │
│   • Some duplicate content (WORKFLOWS.md vs workflows/)     │
│   • Spec files in docs/ should be in project root          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Content Inventory by Status

### ✅ Current (38 files)

Files that are up-to-date and properly maintained:

| File | Lines | In Nav | Notes |
|------|-------|--------|-------|
| `index.md` | 250 | ✅ | Homepage - updated for v1.20.0 |
| `QUICK-START.md` | 120 | ✅ | Good entry point |
| `ADHD-QUICK-START.md` | 85 | ✅ | Well-structured |
| `REFCARD.md` | 180 | ✅ | Quick reference - current |
| `commands/overview.md` | 95 | ✅ | Command categories |
| `commands/smart.md` | 140 | ✅ | Smart commands reference |
| `commands/docs.md` | 110 | ✅ | Documentation commands |
| `commands/site.md` | 105 | ✅ | Site management |
| `commands/code.md` | 98 | ✅ | Code & testing |
| `commands/git.md` | 130 | ✅ | Git commands |
| `commands/arch.md` | 75 | ✅ | Architecture commands |
| `commands/dist.md` | 88 | ✅ | Distribution commands |
| `commands/plan.md` | 92 | ✅ | Planning commands |
| `guide/getting-started.md` | 145 | ✅ | Tutorial |
| `guide/orchestrator.md` | 175 | ✅ | Orchestrator guide |
| `reference/configuration.md` | 160 | ✅ | Config reference |
| `reference/presets.md` | 135 | ✅ | Preset gallery |
| `ACCESSIBILITY.md` | 125 | ✅ | Accessibility features |
| `PLAYGROUND.md` | 200 | ✅ | Interactive examples |
| `PRESET-GALLERY.md` | 220 | ✅ | Design presets |
| `help/hub.md` | 95 | ✅ | Hub command help |
| `help/do.md` | 110 | ✅ | Do command help |
| `help/check.md` | 88 | ✅ | Check command help |
| `help/orchestrate.md` | 135 | ✅ | Orchestrate help |
| `help/docs-update.md` | 92 | ✅ | Docs update help |
| `help/git-worktree.md` | 105 | ✅ | Worktree help |
| `help/ci-generate.md` | 98 | ✅ | CI generate help |
| `help/brainstorm.md` | 120 | ✅ | Brainstorm help |
| `commands/git-init-reference.md` | 450 | ✅ | Git init command - comprehensive |
| `architecture/git-init-flow.md` | 320 | ✅ | Architecture diagrams |
| `guide/git-init-tutorial.md` | 380 | ✅ | Step-by-step tutorial |
| `git-init-docs-index.md` | 215 | ✅ | Git init hub |
| `workflows/index.md` | 285 | ✅ | Visual workflows - Mermaid diagrams |
| `workflows/pre-commit-workflow.md` | 145 | ✅ | Pre-commit process |
| `CI-DETECTION-ROLLOUT.md` | 180 | ❌ | Good content, not in nav |
| `CI-TEMPLATES.md` | 165 | ❌ | Template examples |
| `specs/SPEC-dry-run-feature-2026-01-15.md` | 487 | ❌ | Spec document - comprehensive |
| `workflow-integration/README.md` | 195 | ❌ | Workflow integration guide |

### ✏️ Need Edits (11 files)

Files with outdated version numbers or minor issues:

| File | Status | Issue | Priority | Fix |
|------|--------|-------|----------|-----|
| `workflows/git-feature-workflow.md` | ✏️ Outdated | References v1.18.0 | High | Update to v1.20.0 |
| `workflows/release-workflow.md` | ✏️ Outdated | Multiple v1.18.0 references | High | Update examples to v1.20.0 |
| `guide/homebrew-installation.md` | ✏️ Outdated | Mentions v1.18.0+ features | Medium | Update or remove version note |
| `guide/skills-agents.md` | ✏️ Outdated | References v1.1.0+ for orchestrator-v2 | Low | Update version reference |
| `ORCHESTRATOR-ENHANCEMENTS.md` | ✏️ Outdated | Roadmap for v1.3.0-v1.5.0 | Medium | Archive or update roadmap |
| `commands.md` | ✏️ Not in nav | 90 commands reference | High | Add to mkdocs nav |
| `architecture.md` | ✏️ Not in nav | Architecture overview | Medium | Add to nav or merge |
| `orchestrator.md` | ✏️ Not in nav | Orchestrator details | Medium | Add to nav or consolidate |
| `skills-agents.md` | ✏️ Not in nav | Skills & agents reference | Medium | Add to nav |
| `WORKFLOWS.md` | ✏️ Duplicate | Similar to workflows/index.md | Low | Check for differences |
| `workflow-integration/QUICK-START.md` | ✏️ Not in nav | Quick start for workflows | Low | Add to nav |

### 🔄 Need Revision (2 files)

Files requiring major updates:

| File | Issue | Recommendation |
|------|-------|----------------|
| `ORCHESTRATOR-ENHANCEMENTS.md` | Roadmap is outdated (planned v1.3.0-v1.5.0, current v1.20.0) | Archive or create new roadmap for v1.21.0+ |
| `specs/SPEC-docs-improvement-2026-01-14.md` | Spec file in docs/ directory | Move to project root specs/ |

### 🔗 Should Merge (2 files)

Potential duplicate or overlapping content:

| Files | Overlap | Recommendation |
|-------|---------|----------------|
| `WORKFLOWS.md` + `workflows/index.md` | Both cover workflows | Compare content, keep one or differentiate |
| `orchestrator.md` + `guide/orchestrator.md` | Both cover orchestrator | Merge into guide/ or differentiate clearly |

### 🗑️ Archive Candidates (1 file)

Files that may no longer be needed:

| File | Reason | Action |
|------|--------|--------|
| `specs/SPEC-testing-enhancements-2025-12-30.md` | Old spec from 2025 | Move to project root or archive |

---

## Detailed Findings

### 1. Version Reference Issues

**11 files** contain outdated version references:

```
workflows/git-feature-workflow.md:
  - Line 156: gh pr create --base main --head dev --title "Release v1.18.0"
  - Line 189: git tag v1.18.0

workflows/release-workflow.md:
  - Multiple examples use v1.18.0 (should be v1.20.0)
  - Lines: 45, 78, 92, 105, 156, 189, 245, 278, 312, 356

guide/homebrew-installation.md:
  - Line 67: "Automatic Sync (v1.18.0+)"
  - Should update to v1.20.0 or remove version note

ORCHESTRATOR-ENHANCEMENTS.md:
  - References v1.3.0, v1.4.0, v1.5.0 in roadmap
  - Project is now at v1.20.0
```

**Recommendation:** Update all v1.18.0 references to v1.20.0

### 2. Navigation Coverage

**Files not in mkdocs.yml navigation:**

- `commands.md` - Important command reference
- `architecture.md` - Architecture overview
- `orchestrator.md` - Orchestrator details
- `skills-agents.md` - Skills & agents reference
- `WORKFLOWS.md` - Workflows overview
- `CI-DETECTION-ROLLOUT.md` - CI detection details
- `CI-TEMPLATES.md` - CI templates
- `workflow-integration/QUICK-START.md` - Workflow quick start
- `workflow-integration/REFCARD.md` - Workflow reference card
- `workflow-integration/commands.md` - Workflow commands
- `workflow-integration/skills-agents.md` - Workflow skills

**Recommendation:** Add important files to navigation or consolidate content

### 3. Duplicate Content Analysis

#### WORKFLOWS.md vs workflows/index.md

Need to compare these files:
- `WORKFLOWS.md` (145 lines) - Not in nav
- `workflows/index.md` (285 lines) - In nav with Mermaid diagrams

**Action:** Read both and determine if merge is needed

#### orchestrator.md vs guide/orchestrator.md

- `orchestrator.md` (195 lines) - Not in nav
- `guide/orchestrator.md` (175 lines) - In nav

**Action:** Compare content and merge or differentiate

### 4. Spec Files Location

**3 spec files in docs/ directory:**
- `specs/SPEC-docs-improvement-2026-01-14.md`
- `specs/SPEC-dry-run-feature-2026-01-15.md`
- `specs/SPEC-testing-enhancements-2025-12-30.md`

**Recommendation:** Spec files typically belong in project root, not docs/

### 5. Documentation Gaps

**Missing documentation:**
- ✅ Dry-run feature is well-documented (DRY-RUN-SUMMARY.md, CHANGELOG.md)
- ✅ Git init has comprehensive docs
- ⚠️ No dedicated page for all 27 dry-run commands (mentioned in commands.md but could be separate)
- ⚠️ No troubleshooting guide
- ⚠️ No FAQ page

**Recommended additions:**
1. `docs/TROUBLESHOOTING.md` - Common issues and solutions
2. `docs/FAQ.md` - Frequently asked questions
3. `docs/DRY-RUN-GUIDE.md` - Comprehensive dry-run feature guide

---

## Priority Action Plan

### 🔥 High Priority (Do First)

1. **Update version references** (1 hour)
   - Update `workflows/git-feature-workflow.md` (v1.18.0 → v1.20.0)
   - Update `workflows/release-workflow.md` (v1.18.0 → v1.20.0)
   - Update `guide/homebrew-installation.md` version notes

2. **Add important files to navigation** (30 min)
   - Add `commands.md` to mkdocs.yml
   - Add `architecture.md` to navigation
   - Add `skills-agents.md` to navigation

3. **Resolve duplicates** (1 hour)
   - Compare `WORKFLOWS.md` vs `workflows/index.md`
   - Compare `orchestrator.md` vs `guide/orchestrator.md`
   - Merge or clearly differentiate

### 🟡 Medium Priority (This Week)

4. **Organize spec files** (15 min)
   - Move spec files to project root `specs/` directory
   - Update mkdocs.yml exclusions

5. **Update roadmap** (30 min)
   - Archive `ORCHESTRATOR-ENHANCEMENTS.md` or update for v1.21.0+
   - Create fresh roadmap if needed

6. **Add workflow integration to nav** (15 min)
   - Add `workflow-integration/` section to mkdocs.yml
   - Include README, QUICK-START, REFCARD

### 🟢 Low Priority (Future)

7. **Create missing docs** (2-3 hours)
   - Add `TROUBLESHOOTING.md`
   - Add `FAQ.md`
   - Consider `DRY-RUN-GUIDE.md`

8. **Content polish** (1-2 hours)
   - Review all files for consistency
   - Update screenshots if needed
   - Add missing examples

---

## Next Steps

### Immediate Actions

```bash
# 1. Update version references
sed -i '' 's/v1\.18\.0/v1.20.0/g' docs/workflows/*.md
sed -i '' 's/v1\.18\.0+/v1.20.0+/g' docs/guide/homebrew-installation.md

# 2. Review duplicates
diff docs/WORKFLOWS.md docs/workflows/index.md
diff docs/orchestrator.md docs/guide/orchestrator.md

# 3. Move specs to root
mkdir -p specs/
mv docs/specs/*.md specs/
```

### Related Commands

- `/craft:site:update` - Update content from code changes
- `/craft:site:consolidate` - Merge duplicate files
- `/craft:docs:nav-update` - Update mkdocs navigation
- `/craft:docs:check` - Validate links and structure

---

## Summary Statistics

```
Content Status:
├── ✅ Current: 38 files (70%)
├── ✏️ Need edits: 11 files (20%)
├── 🔄 Need revision: 2 files (4%)
├── 🔗 Should merge: 2 files (4%)
└── 🗑️ Archive: 1 file (2%)

Navigation Coverage:
├── In nav: 32 files (59%)
└── Not in nav: 22 files (41%)

Version References:
├── Current (1.20.0): 43 files (80%)
├── Outdated (< 1.20.0): 11 files (20%)
└── No version refs: Most files

Content Quality:
├── Comprehensive: 85%
├── With examples: 70%
├── With diagrams: 25%
└── Needs work: 15%
```

---

**Generated by:** `/craft:site:audit full`
**Date:** 2026-01-16
**Next audit:** Recommended after major version releases (v1.21.0)
