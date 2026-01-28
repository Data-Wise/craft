# Teaching Workflow Manual Testing Checklist

## Overview

This checklist covers manual testing scenarios that complement automated tests.
Use with a real teaching project (e.g., STAT 545) when available.

## Pre-Testing Setup

- [ ] Identify test teaching project path
- [ ] Backup project before testing
- [ ] Verify git status is clean
- [ ] Note current git branch

## 1. Teaching Mode Detection

### Test Scenarios

- [ ] **Config Detection**: Project with teach-config.yml
  - Expected: Detects as teaching via "config" method
  - Command: Run detection on project with config

- [ ] **Structure Detection**: Project with syllabus.qmd + schedule.qmd
  - Expected: Detects as teaching via "structure" method
  - Command: Remove config temporarily, test detection

- [ ] **Non-Teaching Project**: Random code project
  - Expected: Not detected as teaching
  - Command: Test detection on ~/projects/dev-tools/flow-cli

### Verification

```bash
# From test project directory
python3 -c "
import sys
from pathlib import Path
sys.path.insert(0, '/path/to/craft')
from utils.detect_teaching_mode import detect_teaching_mode
is_teaching, method = detect_teaching_mode('.')
print(f'Teaching: {is_teaching}, Method: {method}')
"
```

## 2. Configuration Loading & Validation

### Test Scenarios

- [ ] **Valid Minimal Config**: Only required fields
  - Expected: Loads successfully, no errors
  - Fixture: `tests/fixtures/teaching/minimal`

- [ ] **Valid Full Config**: All optional fields
  - Expected: Loads successfully, parses all sections
  - Fixture: `tests/fixtures/teaching/stat-545`

- [ ] **Invalid YAML**: Syntax errors
  - Expected: Returns None or error message
  - Create: Temporarily break YAML syntax

- [ ] **Missing Required Fields**: Incomplete config
  - Expected: Validation errors reported
  - Create: Remove required fields temporarily

- [ ] **Invalid Dates**: End before start
  - Expected: Validation error
  - Create: Swap start/end dates

- [ ] **Overlapping Breaks**: Two breaks overlap
  - Expected: Validation error
  - Create: Configure overlapping break dates

### Verification

```bash
python3 tests/test_teach_config.py
```

## 3. Progress Calculation

### Test Scenarios

- [ ] **During Semester**: Current date within semester
  - Expected: Week 1-16, percentage 0-100
  - Test: Use real course during semester

- [ ] **Before Semester**: Current date before start
  - Expected: Week ≤ 0 or "not started" status
  - Create: Future course config

- [ ] **After Semester**: Current date after end
  - Expected: 100% complete or "ended" status
  - Create: Past course config

- [ ] **During Break**: Currently on break
  - Expected: Break status indicated
  - Test: Configure break around current date

- [ ] **No Breaks**: Summer session
  - Expected: Progress calculated without breaks
  - Fixture: `tests/fixtures/teaching/summer`

### Verification

```bash
python3 tests/test_semester_progress.py
```

## 4. Content Validation

### Test Scenarios

- [ ] **Complete Syllabus**: All recommended sections
  - Expected: No errors, all checkmarks
  - Test: Well-formed syllabus

- [ ] **Missing Syllabus Sections**: Incomplete
  - Expected: Warnings for missing sections
  - Create: Remove grading section

- [ ] **Complete Schedule**: Proper week structure
  - Expected: No errors
  - Test: Well-formed schedule

- [ ] **Malformed Schedule**: Missing week headers
  - Expected: Warnings reported
  - Create: Remove ## Week headers

- [ ] **Missing Assignments**: No homework files
  - Expected: Info message (not error)
  - Test: Project without assignments/

### Verification

```bash
python3 tests/test_teaching_validation.py
```

## 5. Publishing Workflow

### Test Scenarios

**WARNING**: These tests modify git state. Use on test branch only!

- [ ] **Clean Publish**: No uncommitted changes
  - Expected: Builds, pushes, deploys successfully
  - Setup: Clean git status

- [ ] **Dirty Publish**: Uncommitted changes
  - Expected: Prompts to commit or stash
  - Setup: Make uncommitted edits

- [ ] **Build Failure**: Quarto errors
  - Expected: Rollback, clear error message
  - Create: Break quarto syntax

- [ ] **Deployment Verification**: Check GitHub Pages
  - Expected: Site accessible, content updated
  - Verify: Visit <https://username.github.io/course>

- [ ] **Rollback on Failure**: Git restored on error
  - Expected: Returns to pre-publish state
  - Test: Simulate failure (break build)

### Verification

```bash
# Dry run first
python3 commands/teaching/publish.py --dry-run

# Real publish (test branch only!)
python3 commands/teaching/publish.py
```

## 6. Dashboard & Progress Display

### Test Scenarios

- [ ] **Progress Bar**: Visual indicator
  - Expected: ASCII progress bar, percentage
  - Test: View dashboard during semester

- [ ] **Week Display**: Current week highlighted
  - Expected: Week X of Y format
  - Test: View at different semester points

- [ ] **Break Indicator**: Currently on break
  - Expected: Break name shown
  - Test: Configure break around today

- [ ] **Upcoming Milestones**: Next 3 assignments
  - Expected: Due dates listed
  - Test: Course with upcoming deadlines

- [ ] **Dashboard Layout**: ADHD-friendly format
  - Expected: Short paragraphs, visual structure
  - Test: Read dashboard output

### Verification

```bash
# View semester progress
python3 commands/teaching/semester-progress.py

# View full dashboard (when implemented)
python3 commands/teaching/dashboard.py
```

## 7. Cross-Component Integration

### Test Scenarios

- [ ] **Detection → Config → Validation**: Full chain
  - Expected: Smooth flow, no errors
  - Test: Run all three in sequence

- [ ] **Config → Progress → Dashboard**: Data flow
  - Expected: Consistent data across tools
  - Test: Verify week numbers match

- [ ] **Validation → Publish**: Blocking errors
  - Expected: Publish blocked if validation fails
  - Test: Try publishing with errors

### Verification

Run complete workflow manually:

```bash
# 1. Detect
python3 utils/detect_teaching_mode.py

# 2. Validate
python3 commands/teaching/validate.py

# 3. Progress
python3 commands/teaching/semester-progress.py

# 4. Publish (if clean)
python3 commands/teaching/publish.py --dry-run
```

## 8. Performance Checks

### Test Scenarios

- [ ] **Detection Speed**: < 100ms
  - Method: Time detection command
  - Target: Instant response

- [ ] **Config Parsing**: < 200ms
  - Method: Time config load
  - Target: Very fast

- [ ] **Full Validation**: < 5s
  - Method: Time validation command
  - Target: Complete in seconds

- [ ] **Progress Calculation**: < 100ms
  - Method: Time progress calculation
  - Target: Instant

### Verification

```bash
# Time each component
time python3 -c "from utils.detect_teaching_mode import detect_teaching_mode; detect_teaching_mode('.')"
time python3 -c "from commands.utils.teach_config import load_teach_config; load_teach_config('.')"
time python3 commands/teaching/validate.py
time python3 commands/teaching/semester-progress.py
```

## 9. Error Handling & Messages

### Test Scenarios

- [ ] **Clear Error Messages**: Actionable guidance
  - Expected: Specific error + suggestion
  - Test: Trigger various errors

- [ ] **Graceful Degradation**: Partial failures
  - Expected: Continues with warnings
  - Test: Missing optional content

- [ ] **Help Text**: Useful documentation
  - Expected: Clear usage instructions
  - Test: Run with --help

### Verification

Trigger errors intentionally and verify messages are helpful.

## 10. Edge Cases

### Test Scenarios

- [ ] **Empty Config**: Valid YAML but no content
  - Expected: Validation errors for missing fields

- [ ] **Very Long Semester**: 20+ weeks
  - Expected: Handles correctly

- [ ] **Very Short Semester**: 4 weeks (summer)
  - Expected: Handles correctly
  - Fixture: `tests/fixtures/teaching/summer`

- [ ] **Many Breaks**: 5+ break periods
  - Expected: All counted correctly

- [ ] **Break Spanning Weeks**: Multi-week break
  - Expected: All weeks excluded

- [ ] **Unicode Content**: Non-ASCII characters
  - Expected: Handles correctly

### Verification

Create edge case configs and test each component.

## Success Criteria

### Must Pass

- [x] All automated tests pass (139+ tests)
- [ ] All detection scenarios work
- [ ] All validation checks accurate
- [ ] Progress calculation correct
- [ ] Publish workflow safe (no data loss)

### Quality Metrics

- [ ] Performance targets met
- [ ] Error messages clear and actionable
- [ ] ADHD-friendly output maintained
- [ ] No false positives (warnings OK)

## Testing Notes

### Date

### Tester

### Project Used

### Issues Found

1.

### Suggestions

1.

## Sign-Off

- [ ] All critical scenarios tested
- [ ] No blocking bugs found
- [ ] Documentation accurate
- [ ] Ready for merge

**Tester Signature**: ___________________________

**Date**: ___________________________
