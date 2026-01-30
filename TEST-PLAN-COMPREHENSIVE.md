# Comprehensive Test Plan for claude-md Commands

**Generated:** 2026-01-29
**Coverage:** Unit + End-to-End Tests
**Target:** 90%+ code coverage for all utilities and commands

---

## Current Test Status

### Existing Tests (78 tests, 100% passing)

| Test File | Tests | Coverage | Status |
|-----------|-------|----------|--------|
| `test_claude_md_phase1.py` | 10 | Phase 1 (update) | ✅ Complete |
| `test_claude_md_audit.py` | 11 | Audit validation | ✅ Complete |
| `test_claude_md_fix.py` | 8 | Auto-fix methods | ✅ Complete |
| `test_claude_md_scaffold.py` | 19 | Template generation | ✅ Complete |
| `test_claude_md_edit.py` | 14 | Section editing | ✅ Complete |
| `test_claude_md_integration_phase2.py` | 6 | Audit/fix workflows | ✅ Complete |
| `test_claude_md_integration_phase3.py` | 10 | Scaffold/edit workflows | ✅ Complete |
| **Total** | **78** | **All phases** | **✅ 100%** |

---

## Test Coverage Map

### Unit Tests by Component

#### 1. Project Detection (`claude_md_detector.py`)

**Functions to Test:**

- `detect_project()` - Main detection function
- `CLAUDEMDDetector` class methods
- Version extraction from 4 sources
- Command/skill/agent counting

**Test Cases (10 tests):**

```python
# Happy path
def test_detect_craft_plugin():
    """Detects craft plugin from .claude-plugin/plugin.json"""

def test_detect_r_package():
    """Detects R package from DESCRIPTION file"""

def test_detect_teaching_site():
    """Detects teaching site from _quarto.yml + course.yml"""

def test_detect_mcp_server():
    """Detects MCP server from mcp-server/ directory"""

def test_detect_node_project():
    """Detects Node.js from package.json"""

def test_detect_python_project():
    """Detects Python from pyproject.toml"""

# Version extraction
def test_extract_version_plugin_json():
    """Extracts version from .claude-plugin/plugin.json"""

def test_extract_version_package_json():
    """Extracts version from package.json"""

def test_extract_version_pyproject_toml():
    """Extracts version from pyproject.toml"""

def test_extract_version_description():
    """Extracts version from DESCRIPTION"""
```

**Edge Cases (5 tests):**

```python
def test_empty_directory():
    """Returns default/unknown for empty directory"""

def test_corrupt_json():
    """Handles corrupt JSON gracefully"""

def test_missing_version():
    """Returns None/default when version not found"""

def test_multiple_indicators():
    """Chooses correct type when multiple indicators present"""

def test_permission_denied():
    """Handles permission errors gracefully"""
```

---

#### 2. Template Population (`claude_md_template_populator.py`)

**Functions to Test:**

- `TemplatePopulator.gather_variables()` - Variable collection
- `TemplatePopulator.render_template()` - Template rendering
- Variable substitution logic

**Test Cases (12 tests):**

```python
# Variable gathering
def test_gather_plugin_variables():
    """Gathers all 18+ variables for craft plugin"""

def test_gather_teaching_variables():
    """Gathers course/semester info for teaching site"""

def test_gather_r_package_variables():
    """Gathers R package metadata"""

# Template rendering
def test_render_simple_template():
    """Renders template with basic {variable} substitution"""

def test_render_with_missing_variables():
    """Handles missing variables with placeholders"""

def test_render_with_special_characters():
    """Escapes special characters correctly"""

# Command table generation
def test_generate_command_table():
    """Generates markdown table from commands/"""

def test_generate_project_structure():
    """Generates directory tree visualization"""

# Test count aggregation
def test_count_python_tests():
    """Counts tests in tests/test_*.py"""

def test_count_js_tests():
    """Counts tests in *.test.js"""

def test_count_r_tests():
    """Counts tests in testthat/"""

# Template validation
def test_validate_template_syntax():
    """Ensures all {variables} are valid"""
```

---

#### 3. Audit Validation (`claude_md_auditor.py`)

**Functions to Test:**

- `CLAUDEMDAuditor.audit()` - Main audit function
- Individual check methods (5 checks)
- Severity classification
- Issue reporting

**Test Cases (15 tests):**

```python
# Individual validation checks
def test_check_version_sync():
    """Detects version mismatch between CLAUDE.md and source"""

def test_check_command_coverage():
    """Finds missing and stale command references"""

def test_check_broken_links():
    """Identifies broken internal links"""

def test_check_required_sections():
    """Verifies expected sections present"""

def test_check_status_sync():
    """Checks alignment with .STATUS file"""

# Severity classification
def test_classify_error_severity():
    """Marks blocking issues as ERROR"""

def test_classify_warning_severity():
    """Marks quality issues as WARNING"""

def test_classify_info_severity():
    """Marks suggestions as INFO"""

# Fixable detection
def test_detect_auto_fixable_issues():
    """Identifies issues that can be auto-fixed"""

def test_detect_manual_fix_required():
    """Identifies issues needing manual intervention"""

# Edge cases
def test_audit_empty_file():
    """Handles empty CLAUDE.md"""

def test_audit_missing_file():
    """Handles missing CLAUDE.md"""

def test_audit_malformed_markdown():
    """Handles malformed markdown gracefully"""

# Performance
def test_audit_performance_under_3s():
    """Audit completes in < 3 seconds"""

# Report generation
def test_generate_audit_report():
    """Generates formatted audit report"""
```

---

#### 4. Auto-Fix (`claude_md_fixer.py`)

**Functions to Test:**

- `CLAUDEMDFixer.fix_all()` - Main fix function
- Individual fix methods (4 methods)
- Dry-run mode
- Backup creation

**Test Cases (12 tests):**

```python
# Individual fix methods
def test_fix_version_mismatch():
    """Updates version to match source"""

def test_fix_stale_command():
    """Removes deleted command references"""

def test_fix_broken_link():
    """Updates or removes broken links"""

def test_fix_status_sync():
    """Syncs progress with .STATUS file"""

# Dry-run mode
def test_dry_run_no_file_changes():
    """Dry-run shows preview without modifying file"""

def test_dry_run_report_generation():
    """Dry-run generates fix preview"""

# Backup creation
def test_creates_backup_before_fix():
    """Creates .CLAUDE.md.backup before modifying"""

def test_restores_from_backup_on_error():
    """Restores from backup if fix fails"""

# Scope filtering
def test_fix_errors_only():
    """--scope=errors fixes only ERROR-level issues"""

def test_fix_warnings_only():
    """--scope=warnings fixes only WARNING-level issues"""

# Safety
def test_preserves_user_customizations():
    """Doesn't overwrite user-added content"""

def test_fix_validation():
    """Validates CLAUDE.md after fixing"""
```

---

#### 5. Section Editing (`claude_md_section_editor.py`)

**Functions to Test:**

- `SectionParser.parse()` - Section parsing
- `SectionEditor.update_section()` - Section updates
- Hierarchical navigation
- Diff generation

**Test Cases (10 tests):**

```python
# Section parsing
def test_parse_sections():
    """Parses ## headings into section list"""

def test_parse_nested_sections():
    """Handles ### subsections correctly"""

def test_extract_section_content():
    """Extracts specific section by name"""

# Section updating
def test_update_existing_section():
    """Updates section content"""

def test_preserve_other_sections():
    """Doesn't modify other sections"""

def test_add_new_section():
    """Adds new section if doesn't exist"""

# Diff generation
def test_generate_before_after_diff():
    """Shows before/after preview"""

def test_calculate_change_stats():
    """Reports lines added/removed/modified"""

# Edge cases
def test_fuzzy_section_matching():
    """Matches "Testing" to "## Testing"```

def test_handle_duplicate_section_names():
    """Handles multiple sections with same name"""
```

---

## End-to-End Test Scenarios

### Workflow Tests (10 scenarios)

#### Scenario 1: New Project Setup (5 min)

```bash
# User workflow
/craft:docs:claude-md:scaffold       # Generate CLAUDE.md
/craft:docs:claude-md:audit          # Validate
```

**Test:**

```python
def test_scaffold_to_audit_workflow():
    """scaffold → audit should pass for new project"""
    # 1. Create minimal project structure
    # 2. Run scaffold
    # 3. Run audit
    # 4. Assert: no errors
```

---

#### Scenario 2: Maintenance Workflow (3 min)

```bash
# After adding new commands
/craft:docs:claude-md:update         # Sync changes
/craft:docs:claude-md:audit          # Check quality
/craft:docs:claude-md:fix            # Auto-fix issues
```

**Test:**

```python
def test_update_audit_fix_workflow():
    """update → audit → fix → audit passes"""
    # 1. Add new command file
    # 2. Run update
    # 3. Run audit (should find issues)
    # 4. Run fix
    # 5. Run audit again (should pass)
```

---

#### Scenario 3: Pre-Commit Validation

```bash
# Before git commit
/craft:check                         # Includes claude-md:audit
```

**Test:**

```python
def test_craft_check_integration():
    """craft:check calls audit and enforces quality"""
    # 1. Make changes
    # 2. Run craft:check
    # 3. Assert: audit ran
    # 4. Assert: issues reported correctly
```

---

#### Scenario 4: Git Worktree Workflow

```bash
# Feature branch
git worktree add feature/new-command
/craft:docs:claude-md:update         # Keep docs current
git commit && git push
```

**Test:**

```python
def test_worktree_workflow():
    """git worktree → update → commit works correctly"""
    # 1. Simulate feature branch
    # 2. Add feature
    # 3. Update CLAUDE.md
    # 4. Verify synced with source
```

---

#### Scenario 5: Template Customization

```bash
# Customize plugin template
/craft:docs:claude-md:edit --section="Quick Commands"
```

**Test:**

```python
def test_edit_section_workflow():
    """edit → preview → apply → audit passes"""
    # 1. Edit section
    # 2. Preview changes
    # 3. Apply
    # 4. Run audit
    # 5. Assert: still valid
```

---

### Error Recovery Tests (5 scenarios)

#### Scenario 6: Corrupt File Recovery

```python
def test_fix_corrupt_claude_md():
    """Handles and recovers from malformed CLAUDE.md"""
    # 1. Create malformed CLAUDE.md
    # 2. Run audit (should report errors)
    # 3. Run scaffold with --force
    # 4. Verify regenerated correctly
```

---

#### Scenario 7: Permission Denied

```python
def test_handle_permission_denied():
    """Gracefully handles permission errors"""
    # 1. Make CLAUDE.md read-only
    # 2. Try to fix
    # 3. Assert: clear error message
    # 4. Assert: no data loss
```

---

#### Scenario 8: Backup Restoration

```python
def test_restore_from_backup_on_failure():
    """Restores from backup if fix fails"""
    # 1. Create CLAUDE.md
    # 2. Simulate fix failure mid-operation
    # 3. Assert: original restored from .backup
```

---

#### Scenario 9: Version Conflict

```python
def test_resolve_version_conflict():
    """Handles conflicting version sources"""
    # 1. Create project with multiple version files
    # 2. Make versions different
    # 3. Run audit
    # 4. Assert: reports conflict
    # 5. Run fix with priority
```

---

#### Scenario 10: Large File Performance

```python
def test_large_claude_md_performance():
    """Handles large CLAUDE.md (1000+ lines) efficiently"""
    # 1. Create large CLAUDE.md
    # 2. Run audit
    # 3. Assert: completes < 5 seconds
    # 4. Run fix
    # 5. Assert: completes < 10 seconds
```

---

## Integration Tests

### Cross-Command Integration (5 tests)

```python
def test_scaffold_then_update():
    """scaffold → update maintains consistency"""

def test_audit_identifies_fix_targets():
    """audit marks issues for fix correctly"""

def test_fix_then_audit_validates():
    """fix → audit shows improvement"""

def test_edit_preserves_auto_generated():
    """edit doesn't break auto-generated content"""

def test_update_after_edit_merges():
    """update + edit coexist without conflict"""
```

---

### Craft Workflow Integration (5 tests)

```python
def test_craft_check_integration():
    """/craft:check includes claude-md validation"""

def test_craft_docs_update_coordination():
    """/craft:docs:update triggers claude-md:update"""

def test_craft_git_worktree_integration():
    """/craft:git:worktree finish updates CLAUDE.md"""

def test_craft_hub_discovery():
    """/craft:hub lists claude-md commands"""

def test_craft_do_routing():
    """/craft:do routes claude-md tasks correctly"""
```

---

## Performance Benchmarks

### Target Metrics

| Operation | Target | Actual | Status |
|-----------|--------|--------|--------|
| Project detection | < 100ms | TBD | 📊 |
| Template population | < 500ms | TBD | 📊 |
| Audit (small file) | < 1s | TBD | 📊 |
| Audit (large file) | < 3s | TBD | 📊 |
| Fix (single issue) | < 500ms | TBD | 📊 |
| Fix (multiple issues) | < 2s | TBD | 📊 |
| Section parse | < 200ms | TBD | 📊 |
| Section edit | < 300ms | TBD | 📊 |

---

## Test Execution Strategy

### Test Phases

**Phase 1: Unit Tests (Fast)**

```bash
pytest tests/test_claude_md_comprehensive.py::TestProjectDetection -v
pytest tests/test_claude_md_comprehensive.py::TestTemplatePopulation -v
pytest tests/test_claude_md_comprehensive.py::TestAuditValidation -v
pytest tests/test_claude_md_comprehensive.py::TestAutoFix -v
pytest tests/test_claude_md_comprehensive.py::TestSectionEditing -v

# Target: < 10 seconds total
```

**Phase 2: Integration Tests (Medium)**

```bash
pytest tests/test_claude_md_comprehensive.py::TestEndToEndWorkflows -v
pytest tests/test_claude_md_comprehensive.py::TestCraftIntegration -v

# Target: < 30 seconds total
```

**Phase 3: Performance Tests (Slow)**

```bash
pytest tests/test_claude_md_comprehensive.py::TestPerformance -v

# Target: < 60 seconds total
```

**Full Suite:**

```bash
pytest tests/test_claude_md*.py -v --cov=utils --cov-report=html

# Target: 90%+ coverage
```

---

## Coverage Goals

### Minimum Coverage by Component

| Component | Target | Priority |
|-----------|--------|----------|
| `claude_md_detector.py` | 95% | High |
| `claude_md_template_populator.py` | 90% | High |
| `claude_md_auditor.py` | 95% | High |
| `claude_md_fixer.py` | 95% | High |
| `claude_md_section_editor.py` | 90% | Medium |
| `claude_md_updater_simple.py` | 90% | Medium |
| **Overall** | **90%+** | **High** |

---

## Test Data Fixtures

### Fixture Projects

**1. Minimal Craft Plugin**

```
temp-plugin/
├── .claude-plugin/
│   └── plugin.json         # version: 1.0.0
├── commands/
│   └── test.md
└── CLAUDE.md               # Basic structure
```

**2. Complete Craft Plugin**

```
full-plugin/
├── .claude-plugin/
├── commands/ (10 files)
├── skills/ (5 files)
├── agents/ (2 files)
├── tests/ (20 files)
├── CLAUDE.md               # Complete with all sections
└── .STATUS                 # Progress tracking
```

**3. R Package**

```
r-package/
├── DESCRIPTION             # Package metadata
├── R/ (5 functions)
├── tests/testthat/ (10 tests)
└── _pkgdown.yml
```

**4. Teaching Site**

```
teaching/
├── _quarto.yml
├── course.yml
├── weeks/ (15 weeks)
└── assignments/ (5 assignments)
```

---

## Running the Tests

### Quick Test (Existing 78 tests)

```bash
# Run all existing tests
python3 -m pytest tests/test_claude_md*.py -v

# Expected: 78/78 passing
```

### With Coverage

```bash
# Generate coverage report
python3 -m pytest tests/ --cov=utils --cov-report=term-missing --cov-report=html

# View report: open htmlcov/index.html
```

### Continuous Integration

```bash
# Pre-commit hook
pytest tests/ -x -v --tb=short

# CI pipeline
pytest tests/ --cov=utils --cov-fail-under=90 --junitxml=results.xml
```

---

## Summary

**Current Status:**

- ✅ 78 tests implemented (100% passing)
- ✅ All major workflows covered
- ✅ Unit + integration + e2e tests
- ✅ Performance benchmarks planned
- 📊 Coverage analysis pending

**Test Plan Completeness:**

- Unit test scenarios: 60+ defined
- Integration scenarios: 20+ defined
- E2E workflows: 10 scenarios
- Edge cases: 15+ scenarios
- Performance benchmarks: 8 metrics

**Next Steps:**

1. Run existing test suite: `pytest tests/test_claude_md*.py -v`
2. Add coverage analysis: `pytest --cov=utils`
3. Implement remaining edge cases
4. Add performance benchmarks
5. Target 90%+ coverage

---

**Test Plan Status:** ✅ Comprehensive, Ready for Execution
**Coverage Target:** 90%+ code coverage
**Test Count:** 78 implemented + 60+ planned = 138+ total tests
