# Manual Testing Checklist: --orch Flag v2.5.1

**Version:** v2.5.1
**Created:** 2026-01-19
**Purpose:** Validate interactive mode prompts, error handling, and user experience improvements

---

## Prerequisites

- [ ] Claude Code CLI session active
- [ ] Craft plugin loaded (verify with `/craft:hub`)
- [ ] Test project available (craft repo itself works)
- [ ] Git worktree environment (recommended)

---

## Test 1: Mode Prompt - Happy Path

**Scenario:** Interactive mode selection works as expected

### Steps:
1. Run: `/craft:do "test task" --orch`
2. Observe mode selection prompt

### Expected:
- [ ] Mode selection prompt appears with 4 options
- [ ] Each option shows: mode name, agent count, description
- [ ] "default" option is marked as "Recommended"
- [ ] Options are clearly formatted and easy to read

### Action:
3. Select: "optimize (4 agents)"

### Expected:
- [ ] Task proceeds with optimize mode
- [ ] Orchestrator spawns successfully
- [ ] No errors or warnings displayed
- [ ] User sees confirmation of selected mode

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 2: Mode Prompt - Cancellation

**Scenario:** User cancels mode selection gracefully

### Steps:
1. Run: `/craft:do "test task" --orch`
2. Mode selection prompt appears
3. Select: "Other" or cancel the prompt

### Expected:
- [ ] Falls back to "default" mode automatically
- [ ] Warning message shown: "Defaulting to 'default' mode"
- [ ] Task continues with default mode (doesn't crash)
- [ ] User informed about fallback behavior

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 3: Explicit Mode - No Prompt

**Scenario:** Explicit mode bypasses interactive prompt

### Steps:
1. Run: `/craft:do "test task" --orch=release`

### Expected:
- [ ] No mode prompt appears
- [ ] Goes directly to release mode
- [ ] Orchestrator spawns with release configuration
- [ ] Output confirms: "Mode: release"

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 4: Invalid Mode - Error Handling

**Scenario:** Invalid mode shows helpful error

### Steps:
1. Run: `/craft:do "test task" --orch=invalid`

### Expected:
- [ ] Error message displayed clearly
- [ ] Error lists all valid modes: default, debug, optimize, release
- [ ] Task does not proceed
- [ ] Error format: "Invalid mode: 'invalid'. Valid modes: ..."

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 5: Dry-Run with Orch

**Scenario:** Dry-run preview works with orchestration mode

### Steps:
1. Run: `/craft:do "test task" --orch=optimize --dry-run`

### Expected:
- [ ] Preview box displayed (ASCII art borders)
- [ ] Shows task description
- [ ] Shows selected mode: "optimize"
- [ ] Shows max agents: 4
- [ ] Shows compression: 60%
- [ ] Message: "Remove --dry-run to execute"
- [ ] No actual orchestrator spawn

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 6: Orchestrator Failure Fallback

**Scenario:** Graceful handling when orchestrator unavailable

### Preparation:
- Temporarily disable orchestrator (rename agent file or simulate failure)

### Steps:
1. Run: `/craft:do "test task" --orch=optimize`

### Expected:
- [ ] Error message: "⚠️  Orchestrator Spawn Failed"
- [ ] Shows task name in error
- [ ] Shows error details
- [ ] Provides 4 suggestions:
  1. Try explicit commands
  2. Check orchestrator availability
  3. Verify resources/context
  4. Use --dry-run
- [ ] Message: "Falling back to command routing..."
- [ ] Task continues (via command routing, not crash)

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 7: Complex Flag Combinations

**Scenario:** Multiple flags work together correctly

### Test 7a: Orch + Dry-Run + For
```bash
/craft:check --orch=release --dry-run --for release
```

### Expected:
- [ ] All flags recognized
- [ ] Dry-run preview shows orch mode
- [ ] "For release" context included
- [ ] No conflicts between flags

### Test 7b: Orch + Categories (Brainstorm)
```bash
/craft:workflow:brainstorm "test" --orch=optimize -C req,tech
```

### Expected:
- [ ] Orchestrator spawns with optimize mode
- [ ] Categories (req, tech) passed to orchestrator
- [ ] Both features work together

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 8: Mode Recommendation Integration

**Scenario:** Complexity score suggests appropriate mode

### Steps:
1. Check `recommend_orchestration_mode()` in code
2. Verify recommendations align with docs:
   - Score 0-3 → default
   - Score 4-7 → optimize
   - Score 8-10 → release

### Expected:
- [ ] Low complexity tasks recommend default
- [ ] Medium complexity recommend optimize
- [ ] High complexity recommend release
- [ ] Recommendations are sensible

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 9: Error Messages - User Friendliness

**Scenario:** All error messages are clear and actionable

### Review error messages for:
1. Invalid mode error
2. Orchestrator failure error
3. Mode prompt failure

### Expected:
- [ ] Errors use emoji indicators (⚠️, ❌, 💡)
- [ ] Errors explain what went wrong
- [ ] Errors provide specific solutions
- [ ] Tone is helpful, not blaming
- [ ] Technical jargon minimized

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Test 10: Documentation Accuracy

**Scenario:** Documentation matches actual behavior

### Steps:
1. Read: `docs/guide/orch-flag-usage.md`
2. Read: `CLAUDE.md` (orch section)
3. Compare with actual behavior from tests above

### Expected:
- [ ] Examples in docs work as shown
- [ ] All flags documented correctly
- [ ] Troubleshooting section helpful
- [ ] No outdated information

### Result: ☐ PASS ☐ FAIL

**Notes:**
_______________________________________________________________

---

## Pass Criteria

**Minimum Requirements:**
- All 10 tests pass
- No unexpected errors or crashes
- Fallbacks work gracefully
- User experience is smooth and intuitive
- Error messages are helpful

**Optional Enhancements Noted:**
- Performance (mode prompt response time)
- Edge cases discovered during testing
- User feedback incorporated

---

## Test Summary

| Test # | Name | Status | Notes |
|--------|------|--------|-------|
| 1 | Mode Prompt - Happy Path | ☐ | |
| 2 | Mode Prompt - Cancellation | ☐ | |
| 3 | Explicit Mode - No Prompt | ☐ | |
| 4 | Invalid Mode - Error Handling | ☐ | |
| 5 | Dry-Run with Orch | ☐ | |
| 6 | Orchestrator Failure Fallback | ☐ | |
| 7 | Complex Flag Combinations | ☐ | |
| 8 | Mode Recommendation Integration | ☐ | |
| 9 | Error Messages - User Friendliness | ☐ | |
| 10 | Documentation Accuracy | ☐ | |

**Total:** ___/10 passed

---

## Sign-Off

- [ ] All tests completed
- [ ] Results documented above
- [ ] Issues filed for any failures
- [ ] Ready for merge (if all pass)

**Tested by:** _______________________
**Date:** _______________________
**Environment:** _______________________

---

## Additional Notes

Use this space to document:
- Unexpected behaviors
- Performance observations
- User experience feedback
- Suggestions for future improvements

_______________________________________________________________
_______________________________________________________________
_______________________________________________________________
