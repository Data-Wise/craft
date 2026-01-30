# Phase 2 Plan: Validation - Audit & Fix Commands

**Status:** Planning
**Dependencies:** Phase 1 complete ✅
**Estimated Time:** 2.5 hours (150 minutes)
**Target:** Add validation and auto-fix capabilities

---

## Overview

Phase 2 builds on Phase 1's update foundation by adding quality assurance:

- **Audit command** - Validates CLAUDE.md completeness and accuracy
- **Fix command** - Auto-fixes common issues detected by audit
- **Integration** - Coordinate with `/craft:check` workflow

---

## Objectives

### Primary Goals

1. **Validate CLAUDE.md Quality**
   - Check version sync with source files
   - Verify command coverage (all commands documented)
   - Detect broken internal links
   - Check required sections present
   - Validate status sync with .STATUS file

2. **Auto-Fix Common Issues**
   - Version mismatches
   - Stale command references
   - Broken links (where fixable)
   - Status sync issues

3. **Integrate with Craft Workflows**
   - Add audit to `/craft:check` validation
   - Coordinate with `/craft:docs:update`
   - Support pre-commit hooks

### Success Criteria

- [ ] Audit command detects version mismatches
- [ ] Audit command finds missing commands
- [ ] Audit command identifies broken links
- [ ] Fix command auto-corrects fixable issues
- [ ] Integration with `/craft:check` works
- [ ] 18-22 tests passing (10-12 audit + 8-10 fix)
- [ ] Dry-run mode for both commands
- [ ] Clear severity levels (error/warning/info)

---

## Implementation Waves

### Wave 1: Audit Command Foundation (45 minutes)

**Goal:** Create audit command with validation checks

#### Deliverables

1. **commands/docs/claude-md/audit.md** (NEW)
   - Source inspiration: `~/.claude/commands/claude-md/audit.md` (195 lines)
   - Frontmatter with arguments
   - "Show Steps First" pattern
   - Validation workflow documentation

2. **utils/claude_md_auditor.py** (NEW)
   - CLAUDEMDAuditor class
   - 5 core validation checks:
     - `check_version_sync()` - Version matches source
     - `check_command_coverage()` - All commands documented
     - `check_broken_links()` - Internal links valid
     - `check_required_sections()` - Expected sections present
     - `check_status_sync()` - .STATUS file alignment
   - Issue severity classification (error/warning/info)
   - Generate audit report

3. **tests/test_claude_md_audit.py** (NEW)
   - 5-6 initial tests (one per validation check)
   - Test fixtures for CLAUDE.md scenarios

#### Success Criteria - Wave 1

- [ ] Audit command structure complete
- [ ] Auditor utility with 5 validation checks
- [ ] 5-6 tests passing
- [ ] Report generation working

---

### Wave 2: Fix Command Implementation (45 minutes)

**Goal:** Create fix command with auto-fix capabilities

#### Deliverables

1. **commands/docs/claude-md/fix.md** (NEW)
   - Source inspiration: `~/.claude/commands/claude-md/fix.md` (217 lines)
   - Frontmatter with dry-run support
   - Auto-fix workflow documentation
   - Interactive mode for manual fixes

2. **utils/claude_md_fixer.py** (NEW)
   - CLAUDEMDFixer class
   - Auto-fix methods:
     - `fix_version_mismatch()` - Update version
     - `fix_stale_command()` - Remove deleted commands
     - `fix_broken_link()` - Update/remove links
     - `fix_status_sync()` - Sync with .STATUS
   - Dry-run support (preview without applying)
   - Fix report generation

3. **tests/test_claude_md_fix.py** (NEW)
   - 4-5 tests (one per fix method)
   - Test dry-run mode
   - Test fix application

#### Success Criteria - Wave 2

- [ ] Fix command structure complete
- [ ] Fixer utility with 4 auto-fix methods
- [ ] 4-5 tests passing
- [ ] Dry-run mode working

---

### Wave 3: Integration & Testing (60 minutes)

**Goal:** Integrate with craft workflows and comprehensive testing

#### Deliverables

1. **Integration with /craft:check**
   - Modify `commands/check.md` to call audit
   - Add CLAUDE.md validation step
   - Handle audit failures gracefully

2. **Comprehensive Testing**
   - Expand audit tests to 10-12 total
   - Expand fix tests to 8-10 total
   - Add integration tests (3-5)
   - Test fixtures for various scenarios

3. **Documentation Updates**
   - Update ORCHESTRATE.md (mark Phase 2 complete)
   - Update CLAUDE.md if needed
   - Create PHASE2-COMPLETE.md summary

4. **Output Formatting**
   - Styled audit report boxes
   - Clear severity indicators (🔴 error, ⚠️ warning, 📝 info)
   - Fix summary with counts

#### Integration Points

**`/craft:check` Enhancement:**

```bash
# Add to commands/check.md

## Step 4: Documentation Validation (NEW)

if [[ -f CLAUDE.md ]]; then
    echo "Validating CLAUDE.md..."
    /craft:docs:claude-md:audit

    if [[ $? -ne 0 ]]; then
        echo "⚠️  CLAUDE.md has issues"
        echo "Fix: /craft:docs:claude-md:fix"
        exit 1
    fi
fi
```

**`/craft:docs:update` Coordination:**

```bash
# Add to commands/docs/update.md

## Phase 5: CLAUDE.md Sync (NEW)

if [[ -f CLAUDE.md ]]; then
    /craft:docs:claude-md:update --dry-run

    if [[ has changes ]]; then
        echo "CLAUDE.md needs updating"
        /craft:docs:claude-md:update
    fi
fi
```

#### Success Criteria - Wave 3

- [ ] Audit integrated with `/craft:check`
- [ ] 18-22 total tests passing
- [ ] All integration points working
- [ ] Documentation complete
- [ ] Phase 2 success criteria met

---

## File Structure

```
craft/
├── commands/
│   ├── check.md                          # Modified (add audit step)
│   └── docs/
│       ├── update.md                     # Modified (add sync step)
│       └── claude-md/
│           ├── update.md                 # Exists from Phase 1
│           ├── audit.md                  # NEW - Phase 2
│           └── fix.md                    # NEW - Phase 2
├── utils/
│   ├── claude_md_detector.py             # Exists from Phase 1
│   ├── claude_md_updater_simple.py       # Exists from Phase 1
│   ├── claude_md_auditor.py              # NEW - Phase 2
│   └── claude_md_fixer.py                # NEW - Phase 2
├── tests/
│   ├── test_claude_md_phase1.py          # Exists from Phase 1
│   ├── test_claude_md_audit.py           # NEW - Phase 2 (10-12 tests)
│   ├── test_claude_md_fix.py             # NEW - Phase 2 (8-10 tests)
│   └── test_claude_md_integration.py     # NEW - Phase 2 (3-5 tests)
└── PHASE2-COMPLETE.md                    # NEW - Phase 2 summary
```

---

## Technical Specifications

### Audit Report Format

```
╭─ CLAUDE.md Audit Report ─────────────────────────╮
│ File: /Users/dt/projects/dev-tools/craft/CLAUDE.md│
│ Lines: 329                                        │
│ Last modified: 2 days ago                         │
├───────────────────────────────────────────────────┤
│                                                   │
│ 🔴 Errors (2) - Must Fix                          │
│                                                   │
│ 1. Stale Command Reference                        │
│    Line 45: /craft:deploy:heroku                  │
│    Status: Command removed in v2.0.0              │
│    Fix: /craft:docs:claude-md:fix                 │
│                                                   │
│ 2. Dead Link                                      │
│    Line 112: See src/legacy/deploy.ts             │
│    Status: File deleted                           │
│    Fix: /craft:docs:claude-md:fix                 │
│                                                   │
│ ⚠️  Warnings (3) - Should Fix                     │
│                                                   │
│ 1. Version Mismatch                               │
│    CLAUDE.md: v2.8.1                              │
│    Actual: v2.9.0                                 │
│    Fix: /craft:docs:claude-md:fix                 │
│                                                   │
│ 2. Progress Out of Sync                           │
│    CLAUDE.md: 95%                                 │
│    .STATUS: 98%                                   │
│    Fix: /craft:docs:claude-md:fix                 │
│                                                   │
│ 3. Missing Section                                │
│    Template expects "Contributing" section        │
│    Fix: Manual edit required                      │
│                                                   │
│ 📝 Info (2) - Optional                            │
│                                                   │
│ 1. Undocumented Commands (3)                      │
│    - /craft:docs:claude-md:audit                  │
│    - /craft:docs:claude-md:fix                    │
│    - /craft:docs:claude-md:scaffold               │
│    Fix: /craft:docs:claude-md:update              │
│                                                   │
│ 2. Optimization Opportunity                       │
│    "Architecture" section is verbose (45 lines)   │
│    Could condense to ~25 lines                    │
│    Fix: /craft:docs:claude-md:update --optimize   │
│                                                   │
├───────────────────────────────────────────────────┤
│ Summary:                                          │
│   🔴 Errors:   2 (auto-fixable)                   │
│   ⚠️  Warnings: 3 (2 auto-fixable, 1 manual)      │
│   📝 Info:     2 (optional)                       │
│                                                   │
│ Next: /craft:docs:claude-md:fix                   │
╰───────────────────────────────────────────────────╯
```

### Fix Preview Format

```
╭─ CLAUDE.md Fix Preview ──────────────────────────╮
│ Auto-fixable Issues: 4                            │
│ Manual fixes needed: 1                            │
├───────────────────────────────────────────────────┤
│                                                   │
│ Will Apply:                                       │
│                                                   │
│ 1. Update version v2.8.1 → v2.9.0                 │
│    Line 12                                        │
│                                                   │
│ 2. Remove stale command /craft:deploy:heroku      │
│    Line 45                                        │
│                                                   │
│ 3. Update progress 95% → 98%                      │
│    Line 98                                        │
│                                                   │
│ 4. Remove broken link to src/legacy/deploy.ts    │
│    Line 112                                       │
│                                                   │
│ Manual Fixes Needed:                              │
│                                                   │
│ 1. Missing "Contributing" section                │
│    Add after "Development Workflow" section       │
│                                                   │
├───────────────────────────────────────────────────┤
│ Proceed with auto-fixes? (y/n/preview)            │
╰───────────────────────────────────────────────────╯
```

---

## Validation Checks (Detailed)

### 1. Version Sync Check

```python
def check_version_sync(self) -> List[Issue]:
    """Verify version matches source file."""
    claude_version = self._extract_version_from_claude_md()
    project_info = detect_project_info(".")
    actual_version = project_info.get("version")

    if claude_version != actual_version:
        return [Issue(
            severity=Severity.WARNING,
            category="version_mismatch",
            message=f"Version {claude_version} in CLAUDE.md doesn't match {actual_version} in source",
            line_number=self._find_version_line(),
            fixable=True,
            fix_method="update_version"
        )]
    return []
```

### 2. Command Coverage Check

```python
def check_command_coverage(self) -> List[Issue]:
    """Verify all commands are documented."""
    documented = self._extract_documented_commands()
    actual = self._scan_commands_directory()

    issues = []

    # Missing commands
    for cmd in actual - documented:
        issues.append(Issue(
            severity=Severity.INFO,
            category="missing_command",
            message=f"Command {cmd} exists but not documented",
            fixable=False  # Needs description
        ))

    # Stale commands
    for cmd in documented - actual:
        issues.append(Issue(
            severity=Severity.ERROR,
            category="stale_command",
            message=f"Command {cmd} documented but file deleted",
            line_number=self._find_command_line(cmd),
            fixable=True,
            fix_method="remove_command"
        ))

    return issues
```

### 3. Broken Links Check

```python
def check_broken_links(self) -> List[Issue]:
    """Find broken internal links."""
    issues = []
    internal_links = self._extract_internal_links()

    for link in internal_links:
        if link.startswith("http"):
            continue  # Skip external links

        target = self._resolve_link_path(link)
        if not target.exists():
            issues.append(Issue(
                severity=Severity.ERROR,
                category="broken_link",
                message=f"Link points to non-existent file: {link}",
                line_number=self._find_link_line(link),
                fixable=True if self._can_suggest_replacement(link) else False,
                fix_method="update_link" if fixable else None
            ))

    return issues
```

### 4. Required Sections Check

```python
def check_required_sections(self) -> List[Issue]:
    """Verify expected sections are present."""
    required = ["Quick Commands", "Project Structure", "Testing"]
    present = self._extract_section_headers()

    issues = []
    for section in required:
        if section not in present:
            issues.append(Issue(
                severity=Severity.WARNING,
                category="missing_section",
                message=f"Expected section '{section}' not found",
                fixable=False  # Needs manual creation
            ))

    return issues
```

### 5. Status Sync Check

```python
def check_status_sync(self) -> List[Issue]:
    """Verify .STATUS file alignment."""
    if not Path(".STATUS").exists():
        return []

    status_data = self._parse_status_file()
    claude_progress = self._extract_progress_from_claude_md()

    if status_data.get("progress") != claude_progress:
        return [Issue(
            severity=Severity.WARNING,
            category="status_sync",
            message=f"Progress mismatch: CLAUDE.md={claude_progress}%, .STATUS={status_data['progress']}%",
            line_number=self._find_progress_line(),
            fixable=True,
            fix_method="update_progress"
        )]

    return []
```

---

## Testing Strategy

### Test Categories

| Category | Tests | Coverage | Priority |
|----------|-------|----------|----------|
| Audit unit tests | 10-12 | Each validation check | High |
| Fix unit tests | 8-10 | Each fix method | High |
| Integration tests | 3-5 | End-to-end workflows | Medium |
| **Total** | **21-27** | **85-90%** | - |

### Example Tests

```python
# tests/test_claude_md_audit.py

def test_audit_detects_version_mismatch():
    """Verify version mismatch detection."""
    with temp_project(claude_version="v1.0.0", actual_version="v2.0.0"):
        auditor = CLAUDEMDAuditor("CLAUDE.md")
        issues = auditor.check_version_sync()

        assert len(issues) == 1
        assert issues[0].category == "version_mismatch"
        assert issues[0].severity == Severity.WARNING
        assert issues[0].fixable == True

def test_audit_finds_stale_commands():
    """Verify stale command detection."""
    with temp_project():
        # CLAUDE.md references /craft:test:old
        # But commands/test/old.md doesn't exist
        auditor = CLAUDEMDAuditor("CLAUDE.md")
        issues = auditor.check_command_coverage()

        stale = [i for i in issues if i.category == "stale_command"]
        assert len(stale) == 1
        assert "/craft:test:old" in stale[0].message

def test_audit_identifies_broken_links():
    """Verify broken link detection."""
    with temp_project():
        # CLAUDE.md links to docs/removed.md
        auditor = CLAUDEMDAuditor("CLAUDE.md")
        issues = auditor.check_broken_links()

        broken = [i for i in issues if i.category == "broken_link"]
        assert len(broken) == 1
        assert "docs/removed.md" in broken[0].message

# tests/test_claude_md_fix.py

def test_fix_version_mismatch():
    """Verify version fix."""
    with temp_project(claude_version="v1.0.0", actual_version="v2.0.0"):
        fixer = CLAUDEMDFixer("CLAUDE.md")
        issue = Issue(category="version_mismatch", fixable=True)

        fixer.fix_version_mismatch(issue)

        updated = read_file("CLAUDE.md")
        assert "v2.0.0" in updated
        assert "v1.0.0" not in updated

def test_fix_dry_run_no_changes():
    """Verify dry-run doesn't modify files."""
    with temp_project():
        before = read_file("CLAUDE.md")
        fixer = CLAUDEMDFixer("CLAUDE.md")

        fixer.fix_all(dry_run=True)

        after = read_file("CLAUDE.md")
        assert before == after

# tests/test_claude_md_integration.py

def test_craft_check_runs_audit():
    """Verify /craft:check includes audit."""
    with temp_project():
        result = run_command("/craft:check")
        assert "Validating CLAUDE.md" in result.output
        assert "/craft:docs:claude-md:audit" in result.commands_run

def test_fix_then_audit_passes():
    """Verify fix resolves audit issues."""
    with temp_project_with_issues():
        # Run fix
        run_command("/craft:docs:claude-md:fix")

        # Run audit
        result = run_command("/craft:docs:claude-md:audit")
        assert result.exit_code == 0
        assert "0 errors" in result.output
```

---

## Timeline

| Wave | Duration | Tasks |
|------|----------|-------|
| Wave 1 | 45 min | Audit command + utility + 5-6 tests |
| Wave 2 | 45 min | Fix command + utility + 4-5 tests |
| Wave 3 | 60 min | Integration + comprehensive testing + docs |
| **Total** | **150 min** | **Phase 2 complete** |

---

## Dependencies

**From Phase 1:**

- ✅ `utils/claude_md_detector.py` - Project detection
- ✅ `commands/docs/claude-md/update.md` - Update command
- ✅ Directory structure established

**External:**

- Existing `/craft:check` command
- Existing `/craft:docs:update` command
- .STATUS file format (if present)

---

## Risk Assessment

### Risk 1: Link Validation Complexity

**Probability:** Medium
**Impact:** Low

**Mitigation:**

- Start with internal links only (skip external URLs)
- Use simple path existence check
- Defer advanced link checking to Phase 4

### Risk 2: Auto-Fix Safety

**Probability:** Low
**Impact:** High

**Mitigation:**

- Require dry-run preview before applying
- Create backup before fixing
- Only auto-fix safe patterns (version, counts)
- Require manual confirmation for structural changes

### Risk 3: Integration Conflicts

**Probability:** Low
**Impact:** Medium

**Mitigation:**

- Test `/craft:check` integration early
- Make audit failures non-blocking initially
- Provide clear fix instructions

---

## Success Metrics

### Functional Metrics

- [ ] Audit command working with 5 validation checks
- [ ] Fix command working with 4 auto-fix methods
- [ ] 21-27 tests passing with 85-90% coverage
- [ ] Integration with `/craft:check` working

### Quality Metrics

- [ ] Clear severity levels (error/warning/info)
- [ ] Dry-run mode for both commands
- [ ] Styled output boxes
- [ ] Fix preview before applying

### User Experience Metrics

- [ ] Audit completes in < 3 seconds
- [ ] Fix auto-corrects 70%+ of issues
- [ ] Clear next-step guidance
- [ ] No false positives in validation

---

## Next Steps After Phase 2

**Phase 3:** Scaffold & Edit commands (templates + interactive editing)
**Phase 4:** Documentation (tutorial + reference + hub integration)

---

**Phase 2 Status:** Planning Complete - Ready to Execute
**Estimated Start:** After Phase 1 commit
**Estimated Completion:** ~2.5 hours from start
