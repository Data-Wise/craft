# SPEC: Broken Link Validation with .linkcheck-ignore Support

**Version:** 1.0.0
**Status:** Draft
**Created:** 2026-01-17
**Target:** v1.23.0
**Effort:** 2-3 hours (4 phases)

---

## Problem Statement

Documentation commands (`/craft:docs:check-links`, `/craft:docs:check`, `/craft:docs:update`) don't support ignoring expected broken links, leading to:

1. **Noise in validation reports**: ~30 expected broken links (test files, brainstorm references, external docs) flagged as errors
2. **No distinction between critical and expected**: All broken links treated equally
3. **Manual filtering required**: Developers must mentally filter expected issues from reports
4. **CI pipeline friction**: Expected broken links cause false-positive failures

### Context

PR #13 (Website Organization Phase 1) documented ~30 expected broken links in `.linkcheck-ignore` file, establishing a pattern for tracking known issues. This spec implements parser support for that pattern.

---

## Solution Overview

Enhance existing documentation validation commands with `.linkcheck-ignore` pattern support:

1. **Add `.linkcheck-ignore` parser utility** (`utils/linkcheck_ignore_parser.py`)
2. **Integrate parser into existing commands** (docs:check-links, docs:check, docs:update)
3. **Categorize broken links** (critical vs expected)
4. **Update reporting** to distinguish between link types

---

## Architecture

### Component Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     Craft Commands                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  /craft:docs:check-links                                    │
│         │                                                   │
│         ├─→ Link extraction (existing)                      │
│         ├─→ Link validation (existing)                      │
│         └─→ [NEW] linkcheck_ignore_parser.parse()           │
│                    ├─→ Load .linkcheck-ignore               │
│                    ├─→ Parse patterns                       │
│                    └─→ Return ignore list                   │
│                                                             │
│  /craft:docs:check                                          │
│         │                                                   │
│         └─→ Calls docs:check-links (inherits ignore support)│
│                                                             │
│  /craft:docs:update                                         │
│         │                                                   │
│         └─→ Calls docs:check (inherits ignore support)      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Implementation Plan

### Phase 1: .linkcheck-ignore Parser (60 min)

**File:** `utils/linkcheck_ignore_parser.py`

**Functionality:**
- Parse `.linkcheck-ignore` markdown file
- Extract file patterns and link targets
- Support comment lines and section headers
- Return structured ignore rules

**API:**
```python
def parse_linkcheck_ignore(filepath: str = ".linkcheck-ignore") -> dict:
    """
    Parse .linkcheck-ignore file and return ignore patterns.

    Returns:
        {
            "files": ["docs/test-violations.md", "docs/specs/*.md"],
            "patterns": [
                {"file": "docs/TEACHING-DOCS-INDEX.md", "target": "../README.md"},
                {"file": "docs/teaching-migration.md", "target": "../commands/site/publish.md"},
            ],
            "categories": {
                "test_files": [...],
                "brainstorm": [...],
                "external": [...],
            }
        }
    """
```

**Pattern Matching:**
- Exact match: `docs/test-violations.md` → `nonexistent.md`
- Glob patterns: `docs/specs/*.md` → `../brainstorm/*.md`
- Partial match: Any file linking to `../README.md`

**Tasks:**
1. Create `utils/linkcheck_ignore_parser.py` (30 min)
2. Implement markdown parsing logic (20 min)
3. Add basic tests (10 min)

---

### Phase 2: Integrate into docs:check-links (30 min)

**File:** `commands/docs/check-links.md`

**Changes:**
1. Call parser at start of validation
2. Check each broken link against ignore patterns
3. Categorize links: `critical`, `expected`, `external`
4. Update output format to show categories

**Output Example:**
```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:check-links (default mode)                      │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ ✓ Checked: 45 internal links in 54 files                    │
│                                                             │
│ ✗ Critical Broken Links (2):                                │
│   1. docs/index.md:34                                       │
│      [Configuration](/docs/config.md)                       │
│      → File not found                                       │
│                                                             │
│   2. README.md:67                                           │
│      [Guide](docs/guide/nonexistent.md)                     │
│      → File not found                                       │
│                                                             │
│ ⚠ Expected Broken Links (3):                                │
│   1. docs/test-violations.md:12                             │
│      [nonexistent.md](nonexistent.md)                       │
│      → Intentional (test file)                              │
│                                                             │
│   2. docs/specs/SPEC-teaching-workflow.md:45                │
│      [brainstorm](../brainstorm/BRAINSTORM-teaching.md)     │
│      → Expected (gitignored)                                │
│                                                             │
│   3. docs/TEACHING-DOCS-INDEX.md:23                         │
│      [README](../README.md)                                 │
│      → Expected (outside docs/)                             │
│                                                             │
│ ─────────────────────────────────────────────────────────── │
│                                                             │
│ Exit code: 1 (2 critical broken links)                      │
│                                                             │
│ Fix critical links before deployment.                       │
│ Expected links documented in .linkcheck-ignore              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

**Exit Codes:**
- `0`: All links valid (or only expected broken)
- `1`: Critical broken links found
- `2`: Validation error

**Tasks:**
1. Import parser in command (5 min)
2. Filter broken links by category (10 min)
3. Update output formatting (10 min)
4. Update exit code logic (5 min)

---

### Phase 3: Integration Tests (30 min)

**File:** `tests/test_linkcheck_ignore.py`

**Test Cases:**
1. Parse valid .linkcheck-ignore file
2. Handle missing .linkcheck-ignore (graceful)
3. Match exact file patterns
4. Match glob patterns
5. Categorize links correctly
6. Exit codes based on categories
7. VS Code format with categories

**Tasks:**
1. Create test file (10 min)
2. Write 7 test cases (15 min)
3. Run tests and fix issues (5 min)

---

### Phase 4: Documentation & CI (30 min)

**Files to Update:**
1. `commands/docs/check-links.md` - Add .linkcheck-ignore section
2. `commands/docs/check.md` - Document ignore support
3. `.linkcheck-ignore` - Add usage instructions (header comment)
4. `CLAUDE.md` - Update command count if needed
5. `CI-TEMPLATES.md` - Add .linkcheck-ignore example

**New Section for check-links.md:**
```markdown
## .linkcheck-ignore Support

Ignore expected broken links by creating a `.linkcheck-ignore` file:

### Format

```markdown
# Known Broken Links

## Category: Test Files
File: docs/test-violations.md
- Purpose: Test data for validation
- Links: Intentionally broken

## Category: Brainstorm References
Files: docs/specs/*.md
Target: ../brainstorm/*.md
- Reason: Brainstorm files are gitignored
```

### Behavior

- **Critical links**: Not in ignore file → Exit code 1
- **Expected links**: In ignore file → Exit code 0 (with warning)
- **All valid**: No broken links → Exit code 0

### CI Integration

```yaml
- name: Check Documentation Links
  run: |
    claude "/craft:docs:check-links"
    # Only fails on critical broken links
    # Expected links (in .linkcheck-ignore) don't block CI
```
```

**Tasks:**
1. Update check-links.md (10 min)
2. Update check.md (5 min)
3. Add .linkcheck-ignore header (5 min)
4. Update CI templates (5 min)
5. Update CLAUDE.md if needed (5 min)

---

## File Structure

```
craft/
├── commands/
│   └── docs/
│       ├── check-links.md          [MODIFY] Add ignore support
│       ├── check.md                [MODIFY] Document ignore feature
│       └── update.md               [NO CHANGE] Inherits from check
│
├── utils/
│   └── linkcheck_ignore_parser.py  [NEW] Parser utility
│
├── tests/
│   └── test_linkcheck_ignore.py    [NEW] Parser and integration tests
│
├── .linkcheck-ignore               [MODIFY] Add usage instructions
│
└── docs/
    └── specs/
        └── SPEC-broken-link-validation-2026-01-17.md  [NEW] This spec
```

---

## Success Metrics

| Metric | Before | After | Goal |
|--------|--------|-------|------|
| CI false positives | ~30 expected links fail | 0 (ignored) | 100% reduction |
| Report clarity | All broken = errors | Critical vs expected | Clear distinction |
| Manual filtering | Developer must ignore | Automatic | 0 manual work |
| Exit code accuracy | Fails on expected links | Fails only on critical | Correct behavior |

---

## Implementation Order

### Wave 1: Foundation (60 min)
- [x] Create worktree branch
- [x] Create implementation spec
- [ ] Implement `linkcheck_ignore_parser.py`
- [ ] Write parser unit tests

### Wave 2: Integration (30 min)
- [ ] Integrate into `docs:check-links.md`
- [ ] Update output formatting
- [ ] Update exit code logic

### Wave 3: Testing (30 min)
- [ ] Integration tests
- [ ] End-to-end validation
- [ ] Edge case testing

### Wave 4: Documentation (30 min)
- [ ] Update command docs
- [ ] Add CI examples
- [ ] Update .linkcheck-ignore header

---

## Edge Cases

| Case | Behavior |
|------|----------|
| Missing .linkcheck-ignore | Treat all broken links as critical |
| Invalid .linkcheck-ignore format | Log warning, treat as missing |
| Circular ignore patterns | Parser handles gracefully (no infinite loops) |
| Case-sensitive paths | Match exactly (respect filesystem) |
| Relative vs absolute paths | Normalize before matching |

---

## Rollout Plan

1. **Merge to dev**: Feature branch → dev
2. **Test in real project**: Run on craft docs
3. **Verify CI behavior**: Check GitHub Actions
4. **Merge to main**: If tests pass
5. **Release**: v1.23.0

---

## Related

- **PR #13**: Created .linkcheck-ignore pattern (Website Organization Phase 1)
- **Existing Commands**: `/craft:docs:check-links` (MVP), `/craft:docs:check` (full), `/craft:docs:update` (orchestrator)
- **Similar Tools**: markdown-link-check, linkchecker, htmlproofer

---

## Future Enhancements (Out of Scope)

- [ ] External link checking (HTTP status codes)
- [ ] Automatic ignore pattern suggestions
- [ ] VS Code extension integration
- [ ] GitHub Actions annotation format
- [ ] Link fix suggestions (fuzzy matching)
- [ ] Performance optimization for large doc sets

---

**Status**: Ready for implementation
**Review**: Pending
**Approval**: Pending
