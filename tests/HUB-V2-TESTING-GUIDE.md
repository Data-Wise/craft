# Hub v2.0 User Testing Guide

**Version:** 1.0
**Date:** 2026-01-17
**Branch:** feature/hub-v2
**Tester:** _______________

---

## Overview

This guide provides a comprehensive checklist for testing Hub v2.0 before merging to `dev`. The testing covers all 3 layers, navigation flows, performance, edge cases, and documentation accuracy.

**Estimated Time:** 30-45 minutes

---

## Prerequisites

### Setup

- [ ] Branch: Checkout `feature/hub-v2`
- [ ] Cache: Delete `commands/_cache.json` to test fresh discovery
- [ ] Tests: Run `python3 tests/test_hub_*.py` - all should pass
- [ ] Location: Test from plugin root directory

### Expected Environment

- [ ] Commands: 97 commands in `commands/` directory
- [ ] Categories: 16 categories (code, test, docs, git, site, arch, ci, dist, plan, workflow, etc.)
- [ ] Python: Python 3.8+ available
- [ ] Working directory: `/Users/dt/.git-worktrees/craft/feature-hub-v2`

---

## Phase 1: Auto-Detection Engine

### Discovery Performance

- [ ] **First run (uncached)**

  ```bash
  rm commands/_cache.json
  python3 commands/_discovery.py
  ```

  - [ ] Completes in < 200ms (target: ~12ms)
  - [ ] Discovers 97 commands
  - [ ] Shows 16 categories
  - [ ] Creates `commands/_cache.json`

- [ ] **Cached run**

  ```bash
  python3 commands/_discovery.py
  ```

  - [ ] Completes in < 10ms (target: ~2ms)
  - [ ] Loads from cache
  - [ ] Shows same counts (97 commands, 16 categories)

- [ ] **Cache invalidation**
  - [ ] Touch a command file: `touch commands/code/lint.md`
  - [ ] Run discovery: `python3 commands/_discovery.py`
  - [ ] Verify cache regenerates (new timestamp)

### Command Statistics

- [ ] **Run stats check**

  ```python
  from commands._discovery import get_command_stats
  stats = get_command_stats()
  print(stats)
  ```

  - [ ] `stats['total']` = 97
  - [ ] `stats['categories']` has 16 entries
  - [ ] `stats['categories']['code']` = 12
  - [ ] `stats['categories']['test']` = 7
  - [ ] `stats['categories']['docs']` = 19

---

## Phase 2: Layer 1 - Main Menu

### Basic Display

- [ ] **Invoke hub**

  ```
  Say to Claude: "/craft:hub"
  ```

  - [ ] Shows main menu with box border
  - [ ] Displays "CRAFT - Full Stack Developer Toolkit"
  - [ ] Shows total: "97 Commands | 21 Skills | 8 Agents"
  - [ ] Shows SMART COMMANDS section (do, check, smart-help)
  - [ ] Shows MODES section (default, debug, optimize, release)

### Category Counts

- [ ] **Verify auto-detected counts**
  - [ ] CODE (12)
  - [ ] TEST (7)
  - [ ] DOCS (19)
  - [ ] GIT (11)
  - [ ] SITE (16)
  - [ ] ARCH (1)
  - [ ] CI (3)
  - [ ] DIST (1)
  - [ ] PLAN (3)
  - [ ] WORKFLOW (2)

### Navigation Hint

- [ ] Shows tip: "Say '/craft:hub <category>' to explore a category"
- [ ] Example provided: "/craft:hub code"

---

## Phase 3: Layer 2 - Category View

### CODE Category

- [ ] **Invoke category view**

  ```
  Say to Claude: "/craft:hub code"
  ```

  - [ ] Shows "💻 CODE COMMANDS (12 total)"
  - [ ] Shows description: "Code Quality & Development Tools"
  - [ ] Commands numbered 1-12
  - [ ] Mode indicators shown: [mode] for commands with mode support
  - [ ] Commands grouped by subcategory (if applicable)

- [ ] **Verify commands listed**
  - [ ] /craft:code:lint [mode]
  - [ ] /craft:code:coverage [mode]
  - [ ] /craft:code:deps-audit
  - [ ] /craft:code:ci-local
  - [ ] At least 10 other code commands

- [ ] **Common workflows section**
  - [ ] Shows "Common Workflows" section
  - [ ] Lists 2-3 workflows (Pre-commit, Debug, Release)
  - [ ] Each workflow shows steps

- [ ] **Navigation footer**
  - [ ] Shows "🔙 Back to hub: /craft:hub"
  - [ ] Shows "📚 Learn more: /craft:hub code:[command]"

### TEST Category

- [ ] **Invoke TEST category**

  ```
  Say to Claude: "/craft:hub test"
  ```

  - [ ] Shows "🧪 TEST COMMANDS (7 total)"
  - [ ] Lists all 7 test commands
  - [ ] Shows mode indicators
  - [ ] Shows common workflows

### DOCS Category

- [ ] **Invoke DOCS category**

  ```
  Say to Claude: "/craft:hub docs"
  ```

  - [ ] Shows "📄 DOCS COMMANDS (19 total)"
  - [ ] Lists all 19 docs commands
  - [ ] Shows workflows

### GIT Category

- [ ] **Invoke GIT category**

  ```
  Say to Claude: "/craft:hub git"
  ```

  - [ ] Shows "🔀 GIT COMMANDS (11 total)"
  - [ ] Lists all 11 git commands
  - [ ] Shows workflows

---

## Phase 4: Layer 3 - Command Detail

### CODE:LINT Command

- [ ] **Invoke command detail**

  ```
  Say to Claude: "/craft:hub code:lint"
  ```

  - [ ] Shows "📚 COMMAND: /craft:code:lint"
  - [ ] Shows description section
  - [ ] Shows MODES section (if command has modes)
    - [ ] default (< 10s)
    - [ ] debug (< 120s)
    - [ ] optimize (< 180s)
    - [ ] release (< 300s)
  - [ ] Shows BASIC USAGE section with examples
  - [ ] Shows usage examples with mode variations

- [ ] **Tutorial sections present**
  - [ ] DESCRIPTION
  - [ ] MODES (if applicable)
  - [ ] BASIC USAGE
  - [ ] COMMON WORKFLOWS (if available)
  - [ ] RELATED COMMANDS (if available)

- [ ] **Navigation footer**
  - [ ] Shows "🔙 Back to CODE: /craft:hub code"
  - [ ] Shows "🏠 Back to Hub: /craft:hub"

### TEST:RUN Command

- [ ] **Invoke command detail**

  ```
  Say to Claude: "/craft:hub test:run"
  ```

  - [ ] Shows command tutorial
  - [ ] Shows modes (if applicable)
  - [ ] Shows usage examples
  - [ ] Navigation breadcrumbs present

### DOCS:SYNC Command

- [ ] **Invoke command detail**

  ```
  Say to Claude: "/craft:hub docs:sync"
  ```

  - [ ] Shows command tutorial
  - [ ] Shows description
  - [ ] Usage examples present

### GIT:WORKTREE Command

- [ ] **Invoke command detail**

  ```
  Say to Claude: "/craft:hub git:worktree"
  ```

  - [ ] Shows command tutorial
  - [ ] All sections present
  - [ ] Navigation works

---

## Phase 5: Navigation Flows

### Drill-Down Flow

- [ ] **Main Menu → Category → Command**

  ```
  Step 1: /craft:hub
  Step 2: Select CODE category → /craft:hub code
  Step 3: Select lint command → /craft:hub code:lint
  ```

  - [ ] Each step shows appropriate content
  - [ ] Navigation breadcrumbs work
  - [ ] Can navigate back at each step

### Direct Jump

- [ ] **Jump directly to command**

  ```
  Say to Claude: "/craft:hub test:coverage"
  ```

  - [ ] Goes directly to Layer 3 (command detail)
  - [ ] Skips Layer 1 and Layer 2
  - [ ] Shows complete tutorial

### Category Browse

- [ ] **Browse multiple categories**

  ```
  /craft:hub code
  /craft:hub test
  /craft:hub docs
  /craft:hub git
  ```

  - [ ] Each shows correct command count
  - [ ] Each shows category-specific commands
  - [ ] Navigation consistent across all

### Cross-Category Navigation

- [ ] **Use related commands**
  - [ ] View `/craft:hub code:lint`
  - [ ] Check RELATED COMMANDS section
  - [ ] Try one of the related commands
  - [ ] Verify it navigates correctly

---

## Phase 6: Edge Cases & Error Handling

### Invalid Category

- [ ] **Non-existent category**

  ```
  Say to Claude: "/craft:hub nonexistent"
  ```

  - [ ] Shows error message
  - [ ] Suggests valid alternatives
  - [ ] Doesn't crash

### Invalid Command

- [ ] **Non-existent command**

  ```
  Say to Claude: "/craft:hub code:nonexistent"
  ```

  - [ ] Shows "Command not found" message
  - [ ] Suggests browsing category
  - [ ] Doesn't crash

### Partial Command Name

- [ ] **Command name without category**

  ```
  Say to Claude: "/craft:hub lint"
  ```

  - [ ] Either shows error or finds unique match
  - [ ] Handles gracefully

### Empty Category (if any)

- [ ] **Category with 0 commands**
  - [ ] Shows appropriate message
  - [ ] Doesn't show empty lists
  - [ ] Navigation still works

### Cache Corruption

- [ ] **Corrupt cache file**

  ```bash
  echo "invalid json" > commands/_cache.json
  python3 commands/_discovery.py
  ```

  - [ ] Regenerates valid cache
  - [ ] Doesn't crash
  - [ ] Shows correct counts after regeneration

---

## Phase 7: Performance Testing

### Response Time

- [ ] **Layer 1 (Main Menu)**
  - [ ] Displays in < 1 second
  - [ ] No noticeable lag

- [ ] **Layer 2 (Category View)**
  - [ ] Displays in < 1 second
  - [ ] Filtering feels instant

- [ ] **Layer 3 (Command Detail)**
  - [ ] Displays in < 2 seconds
  - [ ] Tutorial generation feels smooth

### Cache Performance

- [ ] **First invocation (cache miss)**
  - [ ] Slightly slower but acceptable
  - [ ] Creates cache file

- [ ] **Subsequent invocations (cache hit)**
  - [ ] Instant response
  - [ ] Uses cached data

### Large Category Handling

- [ ] **DOCS category (19 commands)**

  ```
  Say to Claude: "/craft:hub docs"
  ```

  - [ ] Handles large list gracefully
  - [ ] No performance degradation
  - [ ] All commands listed

---

## Phase 8: Documentation Accuracy

### Help Page

- [ ] **Read documentation**

  ```bash
  cat docs/help/hub.md
  ```

  - [ ] Mentions v2.0
  - [ ] Explains 3 layers
  - [ ] Shows all categories with counts
  - [ ] Examples match implementation
  - [ ] Command counts accurate (97 total)

### CHANGELOG

- [ ] **Read changelog**

  ```bash
  cat CHANGELOG.md | head -100
  ```

  - [ ] Hub v2.0 entry present
  - [ ] Lists all features
  - [ ] Performance metrics included
  - [ ] Test coverage mentioned

### Command Frontmatter

- [ ] **Check sample commands**

  ```bash
  head -20 commands/code/lint.md
  head -20 commands/test/run.md
  ```

  - [ ] YAML frontmatter present
  - [ ] Required fields: name, category, description
  - [ ] Optional fields used appropriately

---

## Phase 9: Integration Testing

### With /craft:do

- [ ] **Test smart routing interaction**

  ```
  Say to Claude: "/craft:do check code quality"
  ```

  - [ ] Doesn't conflict with hub
  - [ ] Can still use hub after /craft:do

### With /craft:check

- [ ] **Test validation interaction**

  ```
  Say to Claude: "/craft:check"
  ```

  - [ ] Hub still accessible
  - [ ] No conflicts

### With Other Commands

- [ ] **Run actual commands after hub browsing**

  ```
  Step 1: /craft:hub code
  Step 2: /craft:hub code:lint
  Step 3: Actually run /craft:code:lint
  ```

  - [ ] Hub browsing doesn't break command execution
  - [ ] Commands work as expected

---

## Phase 10: Backward Compatibility

### Old Usage Still Works

- [ ] **Plain hub invocation**

  ```
  Say to Claude: "/craft:hub"
  ```

  - [ ] Works same as before (shows main menu)

- [ ] **Category invocation**

  ```
  Say to Claude: "/craft:hub code"
  ```

  - [ ] Works (shows Layer 2)
  - [ ] Even though this format existed before, now shows improved view

### No Breaking Changes

- [ ] Previous hub usage patterns still work
- [ ] No errors for old invocation styles
- [ ] Graceful enhancement of existing features

---

## Phase 11: User Experience

### ADHD-Friendly Features

- [ ] **Progressive disclosure**
  - [ ] Doesn't overwhelm with all 97 commands at once
  - [ ] Clear hierarchy (categories → commands → details)

- [ ] **Visual hierarchy**
  - [ ] Box borders clear and consistent
  - [ ] Sections clearly delineated
  - [ ] Icons help with scanning

- [ ] **Navigation clarity**
  - [ ] Always know where you are
  - [ ] Easy to go back
  - [ ] Breadcrumbs present

### Discoverability

- [ ] **New users**
  - [ ] Can easily find commands
  - [ ] Tips guide to next steps
  - [ ] Examples clear

- [ ] **Power users**
  - [ ] Can jump directly to commands
  - [ ] Quick reference available
  - [ ] No friction

---

## Phase 12: Final Checks

### Code Quality

- [ ] **Run linters**

  ```bash
  # If applicable
  python3 -m pylint commands/_discovery.py
  ```

  - [ ] No critical issues

### Test Suite

- [ ] **All tests pass**

  ```bash
  python3 tests/test_hub_discovery.py
  python3 tests/test_hub_integration.py
  python3 tests/test_hub_layer2.py
  python3 tests/test_hub_layer3.py
  ```

  - [ ] 12/12 discovery tests pass
  - [ ] 7/7 integration tests pass
  - [ ] 7/7 Layer 2 tests pass
  - [ ] 8/8 Layer 3 tests pass
  - [ ] Total: 34/34 tests passing

### Demos Run Successfully

- [ ] **Layer 2 demo**

  ```bash
  python3 tests/demo_layer2.py
  ```

  - [ ] Runs without errors
  - [ ] Shows 4 category examples

- [ ] **Layer 3 demo**

  ```bash
  python3 tests/demo_layer3.py
  ```

  - [ ] Runs without errors
  - [ ] Shows 4 command detail examples

### Git Status Clean

- [ ] **No uncommitted changes**

  ```bash
  git status
  ```

  - [ ] All changes committed
  - [ ] Cache file ignored (in .gitignore)
  - [ ] No unexpected files

### Remote Synced

- [ ] **Push to remote**

  ```bash
  git log origin/feature/hub-v2 -3
  ```

  - [ ] All commits pushed
  - [ ] Branch up to date

---

## Issues Found

### Critical Issues

| # | Description | Severity | Status | Notes |
|---|-------------|----------|--------|-------|
|   |             |          |        |       |

### Minor Issues

| # | Description | Severity | Status | Notes |
|---|-------------|----------|--------|-------|
|   |             |          |        |       |

### Enhancement Ideas

| # | Description | Priority | Notes |
|---|-------------|----------|-------|
|   |             |          |       |

---

## Sign-Off

### Testing Complete

- [ ] All checklist items completed
- [ ] No critical issues found
- [ ] Minor issues documented (if any)
- [ ] Ready for PR to dev

**Tester Signature:** _______________

**Date:** _______________

**Recommendation:**

- [ ] ✅ Approve for merge to dev
- [ ] ⚠️ Approve with minor fixes
- [ ] ❌ Request changes before merge

**Comments:**

```
[Add any additional comments, observations, or recommendations here]
```

---

## Next Steps After Testing

1. **If approved:** Create PR from `feature/hub-v2` to `dev`
2. **Review PR:** Team review and approval
3. **Merge to dev:** Integrate Hub v2.0
4. **Test on dev:** Validate in dev environment
5. **Release:** Include in next version release (v1.23.0 or later)

---

## Resources

- **Branch:** `feature/hub-v2`
- **Commits:** 4 total (03bf1c6, 29f6865, 426c369, 0b3ba06)
- **Documentation:** `docs/help/hub.md`
- **Tests:** `tests/test_hub_*.py`
- **Demos:** `tests/demo_layer*.py`
- **Discovery Engine:** `commands/_discovery.py`

---

**End of Testing Guide**
