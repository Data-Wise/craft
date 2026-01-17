# Teaching Workflow Implementation - TODO List

**Branch:** feature/teaching-workflow
**Spec:** docs/specs/SPEC-teaching-workflow-2026-01-16.md
**Effort:** ~6-8 hours (4 phases)
**Target:** v1.22.0

---

## Phase 1: Foundation (60 min) ⏱️

### Task 1.1: Teaching Mode Detection Utility (20 min)
- [ ] Create `commands/utils/detect_teaching_mode.py`
  - [ ] Implement detection priority logic:
    - [ ] Priority 1: Check `.flow/teach-config.yml` exists
    - [ ] Priority 2: Check `_quarto.yml` has `teaching: true` field
    - [ ] Priority 3: Check project structure (syllabus/, schedule.qmd)
  - [ ] Return tuple: `(is_teaching: bool, detection_method: str | None)`
  - [ ] Add docstring with examples
- [ ] Write unit tests in `tests/test_teaching_mode.py`
  - [ ] Test all 3 detection strategies
  - [ ] Test priority order (config > metadata > structure)
  - [ ] Test negative case (no teaching mode)
- [ ] **Acceptance:** Detection works for STAT 545 test project

### Task 1.2: Teaching Validation Suite (25 min)
- [ ] Create `commands/utils/teaching_validation.py`
  - [ ] Define `ValidationResult` dataclass
    - [ ] Fields: valid, errors, warnings, checks
    - [ ] Method: `can_publish()` returns True if no errors
  - [ ] Implement `validate_syllabus()` function
    - [ ] Check required sections: grading, policies, objectives, schedule
    - [ ] Return section presence map
  - [ ] Implement `validate_schedule()` function
    - [ ] Parse schedule.qmd
    - [ ] Check all weeks have content
    - [ ] Detect gaps in schedule
  - [ ] Implement `validate_assignments()` function
    - [ ] Find assignment references in schedule
    - [ ] Check if files exist (assignments/hw-N.qmd patterns)
    - [ ] Report missing files as warnings (not errors)
  - [ ] Implement `validate_teaching_content()` main function
    - [ ] Call all validation functions
    - [ ] Combine results into ValidationResult
    - [ ] Format report for display
- [ ] Write unit tests
  - [ ] Test syllabus validation (valid + missing sections)
  - [ ] Test schedule validation (complete + gaps)
  - [ ] Test assignment validation (all exist + some missing)
  - [ ] Test ValidationResult.can_publish() logic
- [ ] **Acceptance:** Validation catches all issues in test course

### Task 1.3: Branch Status Display (15 min)
- [ ] Enhance `/craft:git:status` command
  - [ ] Detect teaching mode using utility
  - [ ] If teaching mode:
    - [ ] Show draft vs production branch diff
    - [ ] Highlight critical files (syllabus, schedule)
    - [ ] Display file change summary
  - [ ] Format in ADHD-friendly box layout
- [ ] Test with STAT 545 project
- [ ] **Acceptance:** Status shows teaching context clearly

---

## Phase 2: Publishing Workflow (90 min) ⏱️

### Task 2.1: Config File Schema (15 min)
- [ ] Document `.flow/teach-config.yml` schema
  - [ ] Create `docs/teaching-config-schema.md`
  - [ ] Define all fields:
    - [ ] course: number, title, semester, year
    - [ ] dates: start, end, breaks[]
    - [ ] instructor: name, email, office_hours
    - [ ] deployment: production_branch, draft_branch, gh_pages_url
    - [ ] progress: current_week (auto or integer)
    - [ ] validation: required sections, flags
  - [ ] Add YAML example
  - [ ] Add field descriptions
- [ ] **Acceptance:** Schema doc is clear and complete

### Task 2.2: Preview-Before-Publish Workflow (75 min)
- [ ] Enhance `/craft:site:publish` command
  - [ ] **Step 1: Validate draft branch (10 min)**
    - [ ] Detect teaching mode
    - [ ] If teaching: run `validate_teaching_content()`
    - [ ] Show validation results (ADHD-friendly format)
    - [ ] If errors: ask "Continue anyway?" (AskUserQuestion)
    - [ ] If no: abort publish
  - [ ] **Step 2: Preview changes (15 min)**
    - [ ] Run `git diff production..draft --stat`
    - [ ] Parse output to identify changed files
    - [ ] Highlight critical files (syllabus, schedule, assignments)
    - [ ] Show summary: X files, +Y lines, -Z lines
    - [ ] Format in box layout with critical change warnings
  - [ ] **Step 3: Confirm publish (10 min)**
    - [ ] AskUserQuestion: "Publish these changes?"
      - [ ] Option 1: "Yes - Merge and deploy (Recommended)"
      - [ ] Option 2: "Preview full diff first"
      - [ ] Option 3: "Cancel"
    - [ ] If "Preview full diff": show `git diff production..draft` output
    - [ ] Loop back to confirmation
  - [ ] **Step 4: Execute publish (30 min)**
    - [ ] Create backup of production branch
      - [ ] `git branch production-backup-$(date +%Y%m%d-%H%M%S)`
    - [ ] Checkout production branch
    - [ ] Merge draft with fast-forward only
      - [ ] `git merge draft --ff-only`
      - [ ] If conflict: show error, suggest manual resolution, abort
    - [ ] Push to origin/production
      - [ ] `git push origin production`
    - [ ] Wait for GitHub Actions deploy (optional)
      - [ ] Poll GH Actions API for status
      - [ ] Show progress: "⏳ Deploying... (Xs)"
    - [ ] Verify deployment (check URL returns 200)
    - [ ] If success: show success message + URL
    - [ ] If fail: rollback to backup, show error
  - [ ] **Step 5: Cleanup (10 min)**
    - [ ] Checkout draft branch
    - [ ] Show completion message
    - [ ] Suggest next steps (review site, clean worktree)
- [ ] Write integration tests
  - [ ] Mock git operations
  - [ ] Test validation flow
  - [ ] Test confirmation prompts
  - [ ] Test rollback scenario
- [ ] **Acceptance:** Can publish STAT 545 draft → production safely

---

## Phase 3: Progress Tracking (120 min) ⏱️

### Task 3.1: Config File Parser (20 min)
- [ ] Create `commands/utils/teach_config.py`
  - [ ] Implement `load_teach_config(cwd)` function
    - [ ] Auto-detect config path (.flow/ or root)
    - [ ] Parse YAML safely (handle errors)
    - [ ] Validate required fields
    - [ ] Return dict or None
  - [ ] Add schema validation
    - [ ] Check course fields present
    - [ ] Check dates are valid (YYYY-MM-DD)
    - [ ] Check breaks are within semester
- [ ] Write unit tests
  - [ ] Test valid config
  - [ ] Test invalid YAML
  - [ ] Test missing required fields
  - [ ] Test malformed dates
- [ ] **Acceptance:** Parser handles all edge cases

### Task 3.2: Week Calculation Logic (40 min)
- [ ] Create `commands/utils/semester_progress.py`
  - [ ] Implement `calculate_current_week(config, current_date)` function
    - [ ] Parse semester start/end dates
    - [ ] Calculate days since start
    - [ ] Check if on break (return break info)
    - [ ] Subtract break days from elapsed time
    - [ ] Calculate week number (1-indexed)
    - [ ] Calculate total weeks (accounting for breaks)
    - [ ] Calculate percent complete
    - [ ] Return dict with week info
  - [ ] Implement `format_date_range(start, end)` utility
    - [ ] Format as "Jan 27 - Feb 2"
  - [ ] Implement `get_next_milestone(config, current_week)` function
    - [ ] Check schedule for upcoming deadlines
    - [ ] Return next assignment/exam due
- [ ] Write unit tests
  - [ ] Test week calculation (no breaks)
  - [ ] Test week calculation (with breaks)
  - [ ] Test on break detection
  - [ ] Test edge cases (first week, last week, summer)
  - [ ] Test manual override
- [ ] **Acceptance:** Week calculation matches manual tracking

### Task 3.3: Progress Dashboard Command (60 min)
- [ ] Create `/craft:site:progress` command
  - [ ] Detect teaching mode
  - [ ] If not teaching: show error, suggest config setup
  - [ ] Load teach config
  - [ ] Calculate current week info
  - [ ] Format ADHD-friendly dashboard:
    - [ ] Course header (number, title, semester)
    - [ ] Current week and date range
    - [ ] Progress bar (▓▓▓░░░░░░░░░░░░)
    - [ ] Percent complete
    - [ ] Current week status (lectures posted, assignments)
    - [ ] Upcoming milestones (next 3 items)
    - [ ] Next break countdown
  - [ ] Add flags:
    - [ ] `--week <N>` - override current week (manual)
    - [ ] `--json` - output JSON for scripting
- [ ] Test with STAT 545 config
- [ ] **Acceptance:** Dashboard shows accurate semester progress

---

## Phase 4: Integration (60 min) ⏱️

### Task 4.1: Teaching-Aware Site Build (30 min)
- [ ] Enhance `/craft:site:build` command
  - [ ] Detect teaching mode
  - [ ] If teaching:
    - [ ] Show semester progress before build
    - [ ] Run validation checks
    - [ ] Warn if critical issues (errors)
    - [ ] Allow warnings to proceed
  - [ ] After build (if teaching):
    - [ ] Show deployment URLs
    - [ ] Show semester progress again
    - [ ] Suggest next steps (publish, review)
- [ ] Test build workflow
- [ ] **Acceptance:** Build shows teaching context

### Task 4.2: Documentation (30 min)
- [ ] Create teaching mode documentation
  - [ ] README section: "Teaching Mode"
    - [ ] Overview of features
    - [ ] Quick start guide
    - [ ] Config file setup
  - [ ] Tutorial: `docs/tutorials/teaching-mode-setup.md`
    - [ ] Step-by-step first-time setup
    - [ ] Create .flow/teach-config.yml
    - [ ] Test validation
    - [ ] First publish workflow
  - [ ] Command reference updates
    - [ ] `/craft:site:publish --help` - add teaching flags
    - [ ] `/craft:site:progress --help` - document flags
    - [ ] `/craft:site:validate --help` - add teaching mode
  - [ ] Migration guide: `docs/teaching-migration.md`
    - [ ] From manual workflow to Craft
    - [ ] Common patterns
    - [ ] Troubleshooting
- [ ] **Acceptance:** Docs are clear for first-time users

---

## Testing & Validation

### Integration Tests
- [ ] Create test course project
  - [ ] Minimal course (syllabus + schedule)
  - [ ] Full course (STAT 545 structure)
  - [ ] Edge case course (no breaks, summer session)
- [ ] Test end-to-end workflow
  - [ ] Init config → validate → publish → progress
- [ ] Test error scenarios
  - [ ] Invalid config
  - [ ] Missing files
  - [ ] Git conflicts
  - [ ] Deployment failures

### Manual Testing
- [ ] Test with STAT 545 (Spring 2026)
  - [ ] Detection accuracy
  - [ ] Validation completeness
  - [ ] Publish workflow safety
  - [ ] Progress tracking accuracy
- [ ] Cross-platform testing
  - [ ] macOS (primary)
  - [ ] Linux (if applicable)

---

## Success Metrics (Track These)

### Performance
- [ ] Teaching mode detection: < 100ms
- [ ] Full validation: < 5s
- [ ] Diff preview: < 1s
- [ ] Complete publish workflow: < 5 min

### Quality
- [ ] All validation checks pass
- [ ] No false positives (warnings OK)
- [ ] Week calculation accurate
- [ ] Rollback works on failure

### User Experience
- [ ] ADHD-friendly output (short paragraphs, visual structure)
- [ ] Clear error messages with suggestions
- [ ] Confirmation prompts before destructive actions
- [ ] Success messages include next steps

---

## Commit Strategy (Conventional Commits)

### Phase 1
- `feat(teaching): add teaching mode detection utility`
- `feat(teaching): add content validation suite`
- `feat(git): enhance status with teaching context`

### Phase 2
- `docs(teaching): add teach-config.yml schema`
- `feat(site): add preview-before-publish workflow`
- `test(teaching): add publish workflow integration tests`

### Phase 3
- `feat(teaching): add config file parser`
- `feat(teaching): add semester progress calculation`
- `feat(site): add progress dashboard command`

### Phase 4
- `feat(site): add teaching context to build command`
- `docs(teaching): add setup guide and tutorials`
- `docs: update command references for teaching mode`

---

## PR Checklist

Before creating PR:
- [ ] All phases complete
- [ ] All tests passing (≥90% coverage)
- [ ] Documentation complete
- [ ] CHANGELOG.md updated
- [ ] .STATUS updated
- [ ] Manual testing with STAT 545
- [ ] Performance benchmarks met
- [ ] Code review checklist items addressed

---

## Notes

### Key Insights from Spec
- Preview-before-publish eliminates deployment anxiety
- Validation warnings OK, only errors block publish
- Semester progress auto-calculated, manual override available
- Fast-forward only merges keep clean git history
- ADHD-friendly output throughout

### Potential Extensions (Future)
- LMS integration (Canvas, Moodle) - v1.23.0
- Multi-instructor support - v1.23.0
- Assignment template library - Phase 5
- Multi-platform deployment - v1.23.0

---

**Last Updated:** 2026-01-16
**Status:** Ready to start Phase 1
