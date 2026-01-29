# Interactive Dry-Run Analysis Plan

**Created:** 2026-01-15
**Purpose:** Command-by-command analysis to design dry-run implementations
**Scope:** 47 commands needing dry-run support

---

## Session Structure

### Overview

Go through each of the 47 commands identified in the dry-run feature brainstorm. For each command:

1. **Understand** - What does the command currently do?
2. **Analyze** - What operations does it perform?
3. **Design** - What should the dry-run preview show?
4. **Refine** - Options to edit/improve command behavior
5. **Document** - Capture the dry-run specification

### Interactive Elements

For each command, you will have options to:

- ✏️ **Edit Description** - Refine what the command does
- 🔍 **Analyze Code** - Deep dive into implementation
- 📝 **Design Preview** - Craft the dry-run output
- 🔧 **Refactor Behavior** - Suggest improvements to command logic
- ⏭️ **Skip** - Move to next command
- 💾 **Save Progress** - Save analysis so far

---

## Analysis Template (Per Command)

### Command: `/craft:[category]:[name]`

#### 1. Current Behavior

**What it does:**

- Primary purpose
- Current arguments
- Key operations performed
- Files/systems affected

**Current implementation:**

```bash
# Command file location
commands/[category]/[name].md
```

**Usage examples:**

```bash
# Current usage
/craft:[category]:[name] [args]
```

---

#### 2. Operations Analysis

**Irreversible Operations:**

- [ ] Deletes files/branches/data
- [ ] Publishes to external service
- [ ] Modifies remote state
- [ ] Creates external resources

**File System Changes:**

- [ ] Creates files
- [ ] Modifies files
- [ ] Deletes files
- [ ] Moves/renames files

**Git Operations:**

- [ ] Creates branches
- [ ] Deletes branches
- [ ] Commits changes
- [ ] Pushes to remote

**External API Calls:**

- [ ] GitHub API
- [ ] PyPI/package registries
- [ ] Build services
- [ ] Other services

**Risk Level:** 🔴 CRITICAL / 🟡 HIGH / 🟢 MEDIUM / ⚪ LOW

---

#### 3. Dry-Run Design

**Preview Output Format:**

```
┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: [Command Name]                                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ [Section 1: High-level operation]                           │
│   - [Detail 1]                                              │
│   - [Detail 2]                                              │
│                                                             │
│ [Section 2: Another operation]                              │
│   - [Detail]                                                │
│                                                             │
│ ⚠ Warnings (if any):                                        │
│   • [Warning message]                                       │
│                                                             │
│ 📊 Summary: [One-line summary]                              │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
└─────────────────────────────────────────────────────────────┘
```

**Information to Show:**

1. _(TBD)_
2. _(TBD)_
3. _(TBD)_

**Warnings to Include:**

- _(TBD)_
- _(TBD)_

**Summary Line:**
_(TBD)_

---

#### 4. Implementation Notes

**Complexity:** ⚡ Simple / 🔧 Medium / 🏗️ Complex

**Estimated Effort:** ___ hours

**Dependencies:**

- Files to read: _(TBD)_
- APIs to check: _(TBD)_
- State to analyze: _(TBD)_

**Edge Cases:**

1. _(TBD)_
2. _(TBD)_

**Best-Effort Limitations:**

- Cannot determine: _(TBD)_
- Runtime-only info: _(TBD)_

---

#### 5. Refinement Options

**Option A: Keep Current Behavior**

- No changes to command logic
- Just add dry-run preview

**Option B: Minor Refinement**

- Small improvements to current behavior
- Examples:
  - Better error messages
  - Additional validation
  - Improved output formatting

**Option C: Major Refactor**

- Significant changes to command behavior
- Examples:
  - Split into multiple commands
  - Change argument structure
  - Rewrite core logic

**Option D: Deprecate**

- Mark command as deprecated
- Suggest alternative command
- Remove in future version

**Recommended:** ☐ A ☐ B ☐ C ☐ D

**Notes:**
_(TBD)_

---

#### 6. Testing Plan

**Test Scenarios:**

1. (TBD)
2. (TBD)
3. (TBD)

**Test Data Needed:**

- (TBD)

**Validation:**

- [ ] Dry-run shows correct preview
- [ ] No side effects during dry-run
- [ ] Actual execution matches preview
- [ ] Warnings appear when expected

---

## Command Categories & Priority

### Priority 0: Critical Safety (6 commands)

**Goal:** Prevent irreversible operations

#### Git Operations (5 commands)

1. ☐ `/craft:git:init` - Already has dry-run ✅
2. ☐ `/craft:git:clean` - Delete branches (CRITICAL)
3. ☐ `/craft:git:worktree` - Worktree operations (HIGH)
4. ☐ `/craft:git:branch` - Branch operations (HIGH)
5. ☐ `/craft:git:sync` - Sync with remote

#### Distribution (1 command)

6. ☐ `/craft:dist:pypi` - PyPI publish (CRITICAL)

---

### Priority 1: High-Impact File Generation (17 commands)

**Goal:** Build trust in file creation/modification

#### Documentation (5 commands)

7. ☐ `/craft:docs:sync`
8. ☐ `/craft:docs:changelog`
9. ☐ `/craft:docs:claude-md`
10. ☐ `/craft:docs:validate`
11. ☐ `/craft:docs:nav-update`

#### Site Management (6 commands)

12. ☐ `/craft:site:init` - Already via git:init ✅
13. ☐ `/craft:site:build`
14. ☐ `/craft:site:deploy` - HIGH PRIORITY
15. ☐ `/craft:site:check`
16. ☐ `/craft:site:frameworks`
17. ☐ `/craft:site:update`

#### CI/CD (3 commands)

18. ☐ `/craft:ci:generate` - HIGH PRIORITY
19. ☐ `/craft:ci:validate`
20. ☐ `/craft:ci:detect`

#### Smart Routing (4 commands)

21. ☐ `/craft:do` - Universal router (HIGH)
22. ☐ `/craft:orchestrate` - Multi-agent (HIGH)
23. ☐ `/craft:check` - Validation
24. ☐ `/craft:help` - Context-aware help

---

### Priority 2: Medium-Impact Operations (15 commands)

#### Distribution (2 commands)

25. ☐ `/craft:dist:homebrew` - Already has dry-run ✅
26. ☐ `/craft:dist:curl-install` - Has preview action ✅

#### Code Quality (8 commands)

27. ☐ `/craft:code:lint`
28. ☐ `/craft:code:coverage`
29. ☐ `/craft:code:deps-check`
30. ☐ `/craft:code:deps-audit`
31. ☐ `/craft:code:ci-local`
32. ☐ `/craft:code:ci-fix` - Already has dry-run ✅
33. ☐ `/craft:code:refactor`
34. ☐ `/craft:code:release`

#### Testing (3 commands)

35. ☐ `/craft:test:run`
36. ☐ `/craft:test:coverage`
37. ☐ `/craft:test:watch`

---

### Priority 3: Long-Tail Commands (9 commands)

#### Architecture (2 commands)

38. ☐ `/craft:arch:analyze`
39. ☐ `/craft:arch:diagram`

#### Planning (1 command)

40. ☐ `/craft:plan:feature`

#### Documentation with Partial Dry-Run (6 commands)

41. ☐ `/craft:docs:quickstart` - Already has ✅
42. ☐ `/craft:docs:website` - Already has ✅
43. ☐ `/craft:docs:workflow` - Already has ✅
44. ☐ `/craft:docs:help` - Already has ✅
45. ☐ `/craft:docs:demo` - Already has ✅
46. ☐ `/craft:docs:tutorial` - Already has ✅

#### Additional (1 command)

47. ☐ `/craft:test:cli-gen`

---

## Session Flow

### Start Session

```bash
/craft:workflow:brainstorm
# Trigger: "analyze dry-run for [category]"
# Or: "continue dry-run analysis from command #N"
```

**For each command:**

1. **Display command card** with current behavior
2. **Ask:** "What would you like to do?"
   - Analyze code
   - Design preview
   - Refine behavior
   - Skip
   - Save progress

3. **Interactive design loop:**
   - Show draft dry-run output
   - Options to edit sections
   - Preview before/after
   - Mark as complete

4. **Save analysis** to per-command file

5. **Move to next** command or save progress

---

## Output Files

### Per-Command Analysis

**Location:** `docs/dry-run-analysis/`

**Files:**

```
docs/dry-run-analysis/
├── git-clean.md
├── git-worktree.md
├── git-branch.md
├── dist-pypi.md
├── ci-generate.md
└── ... (47 total)
```

**Template:** See "Analysis Template" above

---

### Summary Report

**File:** `docs/dry-run-analysis/SUMMARY.md`

**Contents:**

- Commands analyzed: X/47
- Commands with dry-run designed: X/47
- Commands needing refactor: X/47
- Total estimated effort: X hours
- Risk breakdown (Critical/High/Medium/Low)
- Priority order for implementation

---

## Interactive Commands During Session

### Edit Mode

```
> edit description
> edit preview
> edit warnings
> edit summary
```

### Analysis Commands

```
> analyze [section]
> show implementation
> show usage examples
> show related commands
```

### Design Commands

```
> draft preview
> show preview
> test preview with sample data
> compare with similar command
```

### Navigation

```
> next
> previous
> skip
> goto [command-name]
> list remaining
> show progress
```

### Save/Load

```
> save
> save and exit
> load progress
> export all
```

---

## Sample Interactive Session

```
┌─────────────────────────────────────────────────────────────┐
│ 📋 DRY-RUN ANALYSIS SESSION                                 │
│ Command 2 of 47: /craft:git:clean                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Current Behavior:                                           │
│   Cleans up merged git branches (local and remote)          │
│                                                             │
│ Risk Level: 🔴 CRITICAL (deletes branches)                  │
│                                                             │
│ What would you like to do?                                  │
│   [A]nalyze code                                            │
│   [D]esign preview                                          │
│   [R]efine behavior                                         │
│   [S]kip                                                    │
│   [P]rogress                                                │
│                                                             │
└─────────────────────────────────────────────────────────────┘

> d

┌─────────────────────────────────────────────────────────────┐
│ 🎨 DESIGN PREVIEW                                           │
├─────────────────────────────────────────────────────────────┤
│ What should the dry-run output show?                        │
│                                                             │
│ [1] List of branches to delete                              │
│ [2] Merge status of each branch                             │
│ [3] Uncommitted changes warnings                            │
│ [4] Protected branches (won't delete)                       │
│ [5] Summary count                                           │
│                                                             │
│ Select all that apply: 1,2,3,4,5                            │
│                                                             │
│ [G]enerate draft preview                                    │
│ [B]ack                                                      │
└─────────────────────────────────────────────────────────────┘

> g

┌─────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Clean Merged Branches                           │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ The following branches would be deleted:                    │
│                                                             │
│ ✓ Local Branches (3)                                        │
│   - feature/auth-system (merged to dev)                     │
│   - fix/login-bug (merged to main)                          │
│   - refactor/api-cleanup (merged to dev)                    │
│                                                             │
│ ⚠ Skipped (uncommitted changes):                            │
│   • feature/wip                                             │
│                                                             │
│ 📊 Summary: 3 branches to delete, 1 skipped                 │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Run without --dry-run to execute                            │
└─────────────────────────────────────────────────────────────┘

Looks good?
  [Y]es - Save and continue
  [E]dit - Modify sections
  [R]egenerate with changes
  [B]ack

> y

✅ Saved to docs/dry-run-analysis/git-clean.md
Moving to next command...
```

---

## Benefits of This Approach

### 1. Thorough Understanding

- Deep dive into each command before implementation
- Uncover edge cases and limitations early
- Document assumptions and decisions

### 2. Consistent Design

- Standardized analysis template
- Uniform dry-run output format
- Reusable patterns across similar commands

### 3. Quality Improvement

- Identify commands that need refactoring
- Spot inconsistent behavior
- Improve error handling and validation

### 4. Better Estimates

- Accurate effort estimation per command
- Identify dependencies and blockers
- Prioritize based on actual complexity

### 5. Documentation Artifact

- Analysis serves as implementation spec
- Testing scenarios already defined
- User documentation can reference designs

---

## Next Steps

1. **Review this plan** - Adjust structure/template as needed
2. **Start session** - Begin with P0 commands (git:clean, dist:pypi)
3. **Set cadence** - Aim for 5-10 commands per session
4. **Track progress** - Update checklist as commands are completed
5. **Generate specs** - Convert analysis to formal implementation specs

---

## Estimated Timeline

**Per Command Analysis:**

- Simple commands: 15-20 minutes
- Medium commands: 30-45 minutes
- Complex commands: 1-2 hours

**Total Effort:**

- 47 commands × 30 min average = ~24 hours
- Spread over 5-6 sessions
- 1-2 weeks calendar time

**Deliverable:**

- 47 command analysis files
- Comprehensive implementation guide
- Testing scenarios
- Effort estimates for Phase 1-3

---

## Success Criteria

- [ ] All 47 commands analyzed
- [ ] Dry-run preview designed for each
- [ ] Risk level assigned
- [ ] Implementation complexity estimated
- [ ] Edge cases documented
- [ ] Testing plan defined
- [ ] Refactoring opportunities identified
- [ ] Summary report generated

---

**Ready to begin?**

Start with: `/craft:workflow:brainstorm "analyze dry-run for git:clean"`

Or continue from any command number: `/craft:workflow:brainstorm "continue dry-run analysis from command #5"`
