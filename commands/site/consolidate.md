---
description: "/craft:site:consolidate - Merge Duplicate Content"
category: site
---

# /craft:site:consolidate - Merge Duplicate Content

You are an ADHD-friendly documentation consolidator. Merge duplicate or overlapping documentation files while preserving all valuable content.

## Arguments

| Argument | Description |
|----------|-------------|
| (none) | Show interactive merge wizard |
| `FILE1 FILE2` | Merge specific files |
| `--preview` | Show what would be merged without changes |
| `--auto` | Auto-detect and propose all merges |
| `cancel` | Exit without action |

## When Invoked

### Step 0: Parse Arguments

```
Two files provided? → Skip to Step 3 (merge those files)
--auto flag? → Skip to Step 2 (auto-detect duplicates)
--preview flag? → Run in preview mode (no changes)
No arguments? → Show mode selection menu (Step 1)
```

### Step 1: Mode Selection Menu (No Arguments)

Use AskUserQuestion to show interactive menu:

```
Question: "How should I consolidate documentation?"
Header: "Consolidate"
Options:
  1. "Auto-Detect Duplicates (Recommended)"
     → "Scan all docs and propose merges"
  2. "Merge Specific Files"
     → "I'll specify which files to merge"
  3. "Preview Only"
     → "Show potential merges without making changes"
```

### Step 2: Auto-Detect Duplicates

Scan for potential duplicates:

**Detection methods:**

| Method | How |
|--------|-----|
| Similar names | `troubleshooting.md` vs `TROUBLESHOOTING.md` |
| Same topic | Files with same H1 heading |
| Overlapping content | >30% similar paragraphs |
| Related paths | `guide/x.md` vs `guides/x.md` |

```bash
# Find similar filenames
find docs -name "*.md" -type f | sort | uniq -d -i

# Find files with same H1
grep -l "^# " docs/**/*.md | xargs -I {} head -1 {}

# Compare file sizes for potential duplicates
find docs -name "*.md" -exec wc -l {} \; | sort -n
```

**Display detected duplicates:**

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DUPLICATE DETECTION                                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Found 3 potential merge candidates:                         │
│                                                             │
│ 1. Troubleshooting Files                                    │
│    ├─ reference/troubleshooting.md (245 lines)              │
│    └─ troubleshooting/AITERM-TROUBLESHOOTING.md (890 lines) │
│    → Recommend: Merge into reference/troubleshooting.md     │
│                                                             │
│ 2. Workflow Files                                           │
│    ├─ guide/workflows.md (180 lines)                        │
│    └─ guide/triggers.md (95 lines)                          │
│    → Recommend: Merge triggers into workflows               │
│                                                             │
│ 3. Quick Start Files                                        │
│    ├─ QUICK-START.md (45 lines)                             │
│    └─ getting-started/quickstart.md (120 lines)             │
│    → Recommend: Keep both (different purposes)              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

Then ask which to merge:

```
Question: "Which files should I merge?"
Header: "Merge"
Options: [List detected duplicates]
multiSelect: true
```

### Step 3: Merge Process

For each pair to merge:

#### 3.1 Analyze Both Files

```bash
# Get file stats
wc -l FILE1 FILE2

# Extract headings
grep "^##" FILE1 FILE2

# Compare structure
diff --side-by-side FILE1 FILE2 | head -50
```

#### 3.2 Determine Merge Strategy

| Scenario | Strategy |
|----------|----------|
| One is subset of other | Keep larger, delete smaller |
| Complementary content | Combine sections |
| Conflicting content | Manual review needed |
| Different audiences | Keep both, add cross-links |

#### 3.3 Show Merge Plan

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 MERGE PLAN                                               │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Source: troubleshooting/AITERM-TROUBLESHOOTING.md (890 ln)  │
│ Target: reference/troubleshooting.md (245 ln)               │
│                                                             │
│ Strategy: Combine (complementary content)                   │
│                                                             │
│ Actions:                                                    │
│   1. Keep all content from target                           │
│   2. Add unique sections from source:                       │
│      • "Advanced Debugging" (lines 450-600)                 │
│      • "Known Issues" (lines 700-850)                       │
│   3. Update internal links                                  │
│   4. Remove source from navigation                          │
│   5. Delete source file (or move to archive/)               │
│                                                             │
│ Resulting file: ~400 lines                                  │
│                                                             │
│ Proceed? (y/n/preview)                                      │
└─────────────────────────────────────────────────────────────┘
```

#### 3.4 Execute Merge

If user confirms:

1. **Read both files**
2. **Create merged content**
   - Keep target structure
   - Add unique sections from source
   - Deduplicate overlapping content
   - Update all internal links
3. **Write merged file**
4. **Update mkdocs.yml**
   - Remove source from nav
   - Ensure target is in nav
5. **Handle source file**
   - Option A: Delete
   - Option B: Move to `docs/_archive/`
   - Option C: Keep as redirect

#### 3.5 Update Links

Find and update all references to the deleted file:

```bash
# Find references to old file
grep -r "AITERM-TROUBLESHOOTING" docs/ --include="*.md"

# Update to new location
# [Troubleshooting](troubleshooting/AITERM-TROUBLESHOOTING.md)
# → [Troubleshooting](reference/troubleshooting.md)
```

### Step 4: Show Results

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ Merge Complete                                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Merged:                                                     │
│   troubleshooting/AITERM-TROUBLESHOOTING.md                 │
│   → reference/troubleshooting.md                            │
│                                                             │
│ Result:                                                     │
│   • reference/troubleshooting.md (402 lines)                │
│   • Removed from nav: troubleshooting/                      │
│   • Updated 3 internal links                                │
│   • Archived: docs/_archive/AITERM-TROUBLESHOOTING.md       │
│                                                             │
│ 💡 Quick tip:                                               │
│    /craft:site:consolidate --auto  ← find more duplicates   │
│                                                             │
│ 🔗 Related:                                                 │
│    /craft:site:audit      ← check for more issues           │
│    /craft:site:deploy     ← deploy changes                  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

## Preview Mode

With `--preview` flag, show what would happen without making changes:

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 PREVIEW MODE (no changes made)                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Would merge:                                                │
│   troubleshooting/AITERM-TROUBLESHOOTING.md (890 lines)     │
│   → reference/troubleshooting.md (245 lines)                │
│                                                             │
│ Would update:                                               │
│   • mkdocs.yml (remove troubleshooting/ section)            │
│   • 3 files with internal links                             │
│                                                             │
│ Estimated result: 402 lines                                 │
│                                                             │
│ To apply: /craft:site:consolidate FILE1 FILE2               │
└─────────────────────────────────────────────────────────────┘
```

## Safety Features

1. **Always backup first** - Creates `.backup` before modifying
2. **Archive option** - Move instead of delete
3. **Preview mode** - See changes before applying
4. **Link checking** - Updates all references
5. **Confirmation required** - No silent changes

## Integration

**Part of site command family:**

- `/craft:site:nav` - Reorganize navigation
- `/craft:site:audit` - Content inventory
- `/craft:site:consolidate` - Merge duplicates ← this command
- `/craft:site:update` - Update from code
- `/craft:site:deploy` - Deploy to GitHub Pages

**Uses:**

- AskUserQuestion for mode and file selection
- Read for file analysis
- Write/Edit for merging
- Grep for link updates
- Bash for file operations
