---
title: "Recipe: Post-Merge Documentation Update"
description: "Automatically update documentation after merging feature branches"
category: "cookbook"
level: "beginner"
time_estimate: "3-5 minutes"
related:
  - ../../commands/docs/update.md
  - ../../tutorials/TUTORIAL-post-merge-pipeline.md
  - ../../reference/REFCARD-DOCS-UPDATE.md
---

# Recipe: Post-Merge Documentation Update

**Time:** 3-5 minutes
**Level:** Beginner
**Prerequisites:** Just merged a feature branch to dev/main
**NEW:** v2.9.0 - Automated 5-phase documentation pipeline

## Problem

I just merged a feature branch and need to update documentation to reflect the changes. I want an automated workflow that catches stale docs, broken links, and missing updates.

## Solution

1. **Run post-merge documentation update (v2.9.0)**

   ```bash
   /craft:docs:update --post-merge
   ```

   **What happens (v2.9.0 automated pipeline):**

   ```
   ╭─ Post-Merge Documentation Pipeline ──────────╮
   │ Analyzing merged changes...                   │
   │ Detected: 8 files changed in last merge       │
   │                                               │
   │ Running 5-phase pipeline:                     │
   │ 1. Detect stale documentation                 │
   │ 2. Validate internal links                    │
   │ 3. Auto-fix safe issues                       │
   │ 4. Generate update recommendations            │
   │ 5. Rebuild documentation site                 │
   │                                               │
   │ Starting phase 1...                           │
   ╰───────────────────────────────────────────────╯
   ```

2. **Review detected issues (Phase 1)**

   The pipeline analyzes your merge and reports:

   ```
   ╭─ Phase 1: Stale Documentation Detected ──────╮
   │                                               │
   │ Found 3 potentially stale documents:          │
   │                                               │
   │ 1. docs/commands/check.md                     │
   │    Reason: /commands/check.md changed         │
   │    Recommendation: Update command examples    │
   │                                               │
   │ 2. docs/reference/REFCARD.md                  │
   │    Reason: New flags added to check command   │
   │    Recommendation: Add --post-merge to flags  │
   │                                               │
   │ 3. CLAUDE.md                                  │
   │    Reason: Version likely outdated            │
   │    Recommendation: Sync version number        │
   │                                               │
   ╰───────────────────────────────────────────────╯

   Continue to phase 2? (y/n)
   ```

3. **Validate links (Phase 2)**

   Automatically checks all documentation links:

   ```
   ╭─ Phase 2: Link Validation ───────────────────╮
   │                                               │
   │ Checking 1,247 links across 94 files...      │
   │                                               │
   │ Results:                                      │
   │ ✓ 1,243 links valid                           │
   │ ✗ 4 broken links found:                       │
   │                                               │
   │ 1. docs/guide/old-tutorial.md                 │
   │    → docs/tutorials/new-tutorial.md (moved)   │
   │                                               │
   │ 2. commands/deprecated.md                     │
   │    → File deleted in merge                    │
   │                                               │
   ╰───────────────────────────────────────────────╯

   Continue to phase 3? (y/n/fix-manually)
   ```

4. **Auto-fix safe issues (Phase 3)**

   The pipeline automatically fixes what it can:

   ```
   ╭─ Phase 3: Auto-Fix ──────────────────────────╮
   │                                               │
   │ Fixing safe issues:                           │
   │                                               │
   │ ✓ Updated 2 redirected links                  │
   │ ✓ Removed 1 link to deleted file              │
   │ ✓ Fixed 3 version numbers in CLAUDE.md        │
   │ ✓ Updated navigation in mkdocs.yml            │
   │                                               │
   │ Manual intervention needed:                   │
   │ • docs/commands/check.md (content update)     │
   │   Action: Add examples for --post-merge flag  │
   │                                               │
   ╰───────────────────────────────────────────────╯

   Continue to phase 4? (y/n)
   ```

5. **Review recommendations (Phase 4)**

   Guidance for manual updates:

   ```
   ╭─ Phase 4: Update Recommendations ────────────╮
   │                                               │
   │ Priority updates needed:                      │
   │                                               │
   │ HIGH PRIORITY:                                │
   │ • docs/commands/check.md                      │
   │   Add: --post-merge flag documentation        │
   │   Add: Example of post-merge workflow         │
   │   Estimated: 5-10 minutes                     │
   │                                               │
   │ MEDIUM PRIORITY:                              │
   │ • docs/tutorials/                             │
   │   Consider: Tutorial for post-merge pipeline  │
   │   Estimated: 30 minutes                       │
   │                                               │
   │ LOW PRIORITY:                                 │
   │ • docs/changelog.md                           │
   │   Add: Entry for v2.9.0 post-merge feature    │
   │   Estimated: 2 minutes                        │
   │                                               │
   ╰───────────────────────────────────────────────╯

   Update now or defer? (update/defer/list)
   ```

6. **Rebuild and verify (Phase 5)**

   Final phase rebuilds documentation:

   ```
   ╭─ Phase 5: Rebuild Documentation Site ────────╮
   │                                               │
   │ Building with mkdocs...                       │
   │ ✓ Build successful (3.2s)                     │
   │ ✓ All pages generated                         │
   │ ✓ No build warnings                           │
   │                                               │
   │ Verification:                                 │
   │ ✓ Site builds without errors                  │
   │ ✓ Navigation structure valid                  │
   │ ✓ Search index generated                      │
   │                                               │
   ╰───────────────────────────────────────────────╯

   ╭─ Pipeline Complete ──────────────────────────╮
   │ Documentation updated successfully!           │
   │                                               │
   │ Auto-fixed: 6 issues                          │
   │ Manual updates recommended: 1                 │
   │ Site rebuilt: 94 pages                        │
   │                                               │
   │ Next steps:                                   │
   │ 1. Review auto-fixes: git diff                │
   │ 2. Address manual updates if desired          │
   │ 3. Commit documentation changes               │
   ╰───────────────────────────────────────────────╯
   ```

## Explanation

### 5-Phase Pipeline (v2.9.0)

The post-merge documentation update runs an automated pipeline:

**Phase 1: Detect Stale Documentation**

- Analyzes files changed in last merge
- Identifies related documentation files
- Suggests specific updates needed
- Uses git history to detect likely staleness

**Phase 2: Validate Internal Links**

- Checks all markdown links in documentation
- Detects broken links from file moves/deletions
- Identifies redirect opportunities
- Reports external link status (optional)

**Phase 3: Auto-Fix Safe Issues**

- Updates redirected links automatically
- Removes links to deleted files
- Syncs version numbers (from package.json, pyproject.toml, etc.)
- Updates navigation structures
- Safe changes only (no content modification)

**Phase 4: Generate Update Recommendations**

- Prioritizes manual updates (HIGH/MEDIUM/LOW)
- Provides specific guidance for each file
- Estimates time for each update
- Can open files for editing

**Phase 5: Rebuild Documentation Site**

- Runs documentation build (mkdocs, Quarto, pkgdown)
- Validates structure and links
- Generates search index
- Verifies no build errors

### Why Use --post-merge?

Without --post-merge:

- `/craft:docs:update` does general documentation updates
- Focuses on completeness, not recent changes

With --post-merge:

- Analyzes specific merge commit
- Targeted updates for changed files
- Automated fixes for common post-merge issues
- Faster, more focused workflow

## Variations

- **Dry-run to preview changes:**

  ```bash
  /craft:docs:update --post-merge --dry-run
  ```

  Shows what would be fixed without making changes

- **Auto-confirm all phases:**

  ```bash
  /craft:docs:update --post-merge --yes
  ```

  Runs all phases without confirmation prompts

- **Skip specific phases:**

  ```bash
  /craft:docs:update --post-merge --skip-rebuild
  ```

  Skips phase 5 (useful if site build is slow)

- **Target specific merge commit:**

  ```bash
  /craft:docs:update --post-merge --commit abc1234
  ```

  Analyzes a specific merge instead of latest

- **Manual intervention for recommendations:**

  ```bash
  /craft:docs:update --post-merge --interactive
  ```

  Opens each recommended file for editing

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No merge commit detected" | Ensure you just merged a branch; if not, specify --commit flag |
| "Phase 2 reports false positives" | Some links may be external or intentionally broken (tests); ignore or add to .linkcheck-ignore |
| "Auto-fix changed wrong content" | Review git diff, revert if needed, file issue for improvement |
| "Phase 5 build fails" | Check build output for errors, may be unrelated to merge |
| "Too many manual recommendations" | Prioritize HIGH only, defer MEDIUM/LOW for later |
| "Want to skip confirmations" | Use --yes flag for non-interactive mode |

## Integration with Git Workflow

### After Feature Merge

```bash
# Merge feature to dev
gh pr merge 123 --squash

# Update documentation
/craft:docs:update --post-merge

# Review and commit
git diff                    # Review auto-fixes
git add -u                  # Stage documentation updates
git commit -m "docs: post-merge documentation update"
git push
```

### After Release Merge

```bash
# Merge dev to main
gh pr merge 456 --merge

# Comprehensive documentation update
/craft:docs:update --post-merge --mode thorough

# Deploy updated docs
/craft:site:deploy
```

## Example: Complete Post-Merge Workflow

```bash
# Scenario: Just merged feature/new-command to dev

# Step 1: Run post-merge pipeline
/craft:docs:update --post-merge

# Pipeline detects:
# - commands/new-command.md needs examples
# - REFCARD.md needs new command added
# - Version number needs sync

# Step 2: Review phase 1 output
# Shows 3 stale files detected
# Confirm: y

# Step 3: Phase 2 validates links
# Found 2 broken links (expected - new command not in nav yet)
# Confirm: y

# Step 4: Phase 3 auto-fixes
# ✓ Added new command to mkdocs.yml nav
# ✓ Updated version in CLAUDE.md
# ✓ Fixed broken links
# Confirm: y

# Step 5: Phase 4 recommendations
# HIGH: Add examples to commands/new-command.md
# MEDIUM: Add to REFCARD.md
# Choose: update (opens files)

# Step 6: Make manual edits
# Add examples, update refcard

# Step 7: Phase 5 rebuilds
# ✓ Site builds successfully

# Step 8: Commit changes
git diff                    # Review all changes
git add -u
git commit -m "docs: post-merge update for new-command feature"
git push
```

## Related

- [Docs Update Command](../../commands/docs/update.md) — Full command reference
- [Post-Merge Pipeline Tutorial](../../tutorials/TUTORIAL-post-merge-pipeline.md) — Detailed guide
- [Docs Update Reference](../../reference/REFCARD-DOCS-UPDATE.md) — Quick reference
- [Git Workflow](../../workflows/git-feature-workflow.md) — Feature branch workflow
