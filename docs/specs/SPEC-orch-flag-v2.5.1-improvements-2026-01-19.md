# SPEC: --orch Flag v2.5.1 Improvements

**Created:** 2026-01-19
**Status:** Draft → Approved
**Version:** v2.5.1
**Priority:** Medium
**Effort:** Medium (4-6 hours)
**Parent Spec:** SPEC-orch-flag-integration-2026-01-19.md

---

## Overview

Address gaps identified in v2.5.0 --orch flag integration to improve user experience, error handling, and documentation completeness. This is a targeted improvement release focusing on the 3 highest-priority gaps from the gap analysis.

---

## Background

The v2.5.0 release successfully shipped the --orch flag feature with:
- ✅ 56 tests (100% passing)
- ✅ 5 commands integrated
- ✅ Comprehensive user guide
- ✅ Website documentation

**Gap Analysis** (GAP-ANALYSIS-orch-flag-v2.5.0.md) identified 12 gaps:
- 1 High priority (mode prompt stub)
- 2 Medium priority (error handling, testing checklist)
- 9 Low priority (documentation enhancements, future features)

This spec addresses the **top 3 gaps** to bring v2.5.0 → v2.5.1 quality.

---

## User Requirements

### Gap 4.1: Interactive Mode Prompt (HIGH PRIORITY)

**Current Behavior:**
```python
def prompt_user_for_mode():
    """Prompt user to select orchestration mode"""
    # TODO: Implement using AskUserQuestion tool
    return "default"  # Stub
```

**Expected Behavior:**
```bash
/craft:do "add auth" --orch

# Shows interactive prompt:
? Which orchestration mode?
  1. default (2 agents) - Quick tasks, moderate parallelization
  2. debug (1 agent) - Sequential, verbose output
  3. optimize (4 agents) - Fast parallel work
  4. release (4 agents) - Pre-release audit

User selects: 3 (optimize)

# Proceeds with optimize mode
```

**Requirements:**
- Use `AskUserQuestion` tool for mode selection
- Display all 4 modes with descriptions
- Handle user cancellation gracefully
- Validate selection is valid mode
- Return selected mode as string

---

### Gap 4.2: Error Handling for Orchestrator Spawn (MEDIUM PRIORITY)

**Current Behavior:**
```python
def spawn_orchestrator(task, mode):
    """Spawn orchestrator with specified mode"""
    Skill(skill="craft:orchestrate", args=f"{task} {mode}")
    # No error handling if skill fails
```

**Expected Behavior:**
```python
def spawn_orchestrator(task, mode):
    """Spawn orchestrator with specified mode"""
    try:
        Skill(skill="craft:orchestrate", args=f"{task} {mode}")
        return True
    except Exception as e:
        print(f"⚠️  Orchestrator spawn failed: {e}")
        print(f"💡 Falling back to command routing...")
        return False
```

**Requirements:**
- Wrap orchestrator spawn in try/except
- Log error message if spawn fails
- Return success boolean
- Provide fallback strategy guidance
- Don't break execution on failure

---

### Gap 3.1: Manual Testing Checklist (MEDIUM PRIORITY)

**Current:** No documented manual testing procedure for user interactions

**Expected:** Comprehensive checklist in IMPLEMENTATION.md covering:
- Mode prompt interaction
- Cancellation behavior
- Invalid selections
- Orchestrator spawn failures
- Flag combinations

**Format:** Step-by-step checklist with expected outcomes

---

### Gap 1.1: CLAUDE.md Cross-Reference (LOW PRIORITY)

**Current:** CLAUDE.md mentions orchestration but doesn't link to orch-flag-usage.md

**Expected:** Direct link in Key Files section:
```markdown
## Key Files

| File | Purpose |
|------|---------|
| `docs/guide/orch-flag-usage.md` | --orch flag usage guide (v2.5.0) |
```

---

## Technical Requirements

### 1. Implement `prompt_user_for_mode()`

**File:** `utils/orch_flag_handler.py`

**Implementation:**
```python
def prompt_user_for_mode() -> str:
    """
    Prompt user to select orchestration mode interactively.

    Returns:
        Selected mode (default|debug|optimize|release)

    Raises:
        ValueError: If user cancels or provides invalid selection
    """
    from tools import AskUserQuestion  # Import within function

    try:
        response = AskUserQuestion(
            questions=[{
                "question": "Which orchestration mode should I use?",
                "header": "Mode",
                "multiSelect": False,
                "options": [
                    {
                        "label": "default (2 agents) - Recommended",
                        "description": "Quick tasks, moderate parallelization"
                    },
                    {
                        "label": "debug (1 agent)",
                        "description": "Sequential, verbose output for troubleshooting"
                    },
                    {
                        "label": "optimize (4 agents)",
                        "description": "Fast parallel work, aggressive optimization"
                    },
                    {
                        "label": "release (4 agents)",
                        "description": "Pre-release audit, thorough validation"
                    }
                ]
            }]
        )

        # Extract mode from user selection
        # "default (2 agents) - Recommended" → "default"
        selection = response["Which orchestration mode should I use?"]
        mode = selection.split(" ")[0]  # Extract first word

        if mode not in VALID_MODES:
            raise ValueError(f"Invalid mode selected: {mode}")

        return mode

    except Exception as e:
        print(f"⚠️  Mode selection failed: {e}")
        print(f"💡 Defaulting to 'default' mode")
        return "default"
```

**Tests:**
```python
# tests/test_orch_flag_handler.py

def test_prompt_user_for_mode_returns_valid_mode(monkeypatch):
    """Test mode prompt returns valid mode"""
    mock_response = {"Which orchestration mode should I use?": "optimize (4 agents)"}
    monkeypatch.setattr("utils.orch_flag_handler.AskUserQuestion", lambda **k: mock_response)

    mode = prompt_user_for_mode()
    assert mode == "optimize"

def test_prompt_user_for_mode_handles_cancellation(monkeypatch):
    """Test mode prompt handles user cancellation"""
    def mock_ask_raises():
        raise Exception("User cancelled")
    monkeypatch.setattr("utils.orch_flag_handler.AskUserQuestion", mock_ask_raises)

    mode = prompt_user_for_mode()
    assert mode == "default"  # Falls back to default

def test_prompt_user_for_mode_handles_invalid_selection(monkeypatch):
    """Test mode prompt validates selection"""
    mock_response = {"Which orchestration mode should I use?": "invalid (0 agents)"}
    monkeypatch.setattr("utils.orch_flag_handler.AskUserQuestion", lambda **k: mock_response)

    mode = prompt_user_for_mode()
    assert mode == "default"  # Falls back to default on invalid
```

---

### 2. Add Error Handling to `spawn_orchestrator()`

**File:** `utils/orch_flag_handler.py`

**Implementation:**
```python
def spawn_orchestrator(task: str, mode: str, extra_args: str = "") -> bool:
    """
    Spawn orchestrator with specified mode.

    Args:
        task: Task description
        mode: Orchestration mode (default|debug|optimize|release)
        extra_args: Additional arguments to pass to orchestrator

    Returns:
        True if orchestrator spawned successfully, False otherwise

    Note:
        On failure, caller should implement fallback strategy
        (e.g., route to commands instead)
    """
    try:
        args = f"{task} {mode}"
        if extra_args:
            args += f" {extra_args}"

        Skill(skill="craft:orchestrate", args=args)
        return True

    except Exception as e:
        # Log error but don't crash
        print(f"⚠️  Orchestrator spawn failed: {str(e)}")
        print(f"💡 Suggestion: Try using explicit commands or check orchestrator status")
        return False
```

**Updated Callers:**
```python
# In commands that use spawn_orchestrator

should_orch, mode = handle_orch_flag(task, orch_flag, mode_flag)

if should_orch:
    success = spawn_orchestrator(task, mode)

    if success:
        # Orchestrator handling the task
        return
    else:
        # Fallback to command routing
        print("📋 Falling back to command routing...")
        # Continue with existing command logic
```

**Tests:**
```python
# tests/test_orch_flag_handler.py

def test_spawn_orchestrator_returns_true_on_success(monkeypatch):
    """Test orchestrator spawn returns True on success"""
    mock_skill = MagicMock()
    monkeypatch.setattr("utils.orch_flag_handler.Skill", mock_skill)

    result = spawn_orchestrator("test task", "optimize")
    assert result is True
    mock_skill.assert_called_once()

def test_spawn_orchestrator_returns_false_on_failure(monkeypatch):
    """Test orchestrator spawn returns False on exception"""
    def mock_skill_raises(**kwargs):
        raise Exception("Orchestrator not available")
    monkeypatch.setattr("utils.orch_flag_handler.Skill", mock_skill_raises)

    result = spawn_orchestrator("test task", "optimize")
    assert result is False

def test_spawn_orchestrator_includes_extra_args(monkeypatch):
    """Test extra args are passed to orchestrator"""
    mock_skill = MagicMock()
    monkeypatch.setattr("utils.orch_flag_handler.Skill", mock_skill)

    spawn_orchestrator("test task", "optimize", "--dry-run")

    call_args = mock_skill.call_args[1]["args"]
    assert "test task optimize --dry-run" == call_args
```

---

### 3. Create Manual Testing Checklist

**File:** `~/.git-worktrees/craft/feature-orch-flag-v2.5.1-improvements/TESTING-CHECKLIST.md`

**Content:**
```markdown
# Manual Testing Checklist: --orch Flag

## Prerequisites
- [ ] Claude Code CLI session active
- [ ] Craft plugin loaded (check with /craft:hub)
- [ ] Test project available (craft repo itself is fine)

## Test 1: Mode Prompt - Happy Path
- [ ] Run: `/craft:do "test task" --orch`
- [ ] **Expected:** Mode selection prompt appears with 4 options
- [ ] Select: "optimize (4 agents)"
- [ ] **Expected:** Task proceeds with optimize mode
- [ ] **Expected:** No errors or warnings

## Test 2: Mode Prompt - Cancellation
- [ ] Run: `/craft:do "test task" --orch`
- [ ] **Expected:** Mode selection prompt appears
- [ ] Select: "Other" (cancel)
- [ ] **Expected:** Falls back to "default" mode
- [ ] **Expected:** Warning message shown

## Test 3: Explicit Mode - No Prompt
- [ ] Run: `/craft:do "test task" --orch=release`
- [ ] **Expected:** No mode prompt (goes directly to release)
- [ ] **Expected:** Orchestrator spawns with release mode

## Test 4: Invalid Mode - Error Handling
- [ ] Run: `/craft:do "test task" --orch=invalid`
- [ ] **Expected:** Error message with valid modes listed
- [ ] **Expected:** Task does not proceed

## Test 5: Dry-Run with Orch
- [ ] Run: `/craft:do "test task" --orch=optimize --dry-run`
- [ ] **Expected:** Preview shown, no orchestrator spawn
- [ ] **Expected:** Mode and settings displayed

## Test 6: Orchestrator Failure Fallback
- [ ] Disable orchestrator (rename agent file temporarily)
- [ ] Run: `/craft:do "test task" --orch=optimize`
- [ ] **Expected:** Error message about spawn failure
- [ ] **Expected:** Falls back to command routing
- [ ] **Expected:** Task still completes (via commands)

## Test 7: Complex Flag Combinations
- [ ] Run: `/craft:check --orch=release --dry-run --for release`
- [ ] **Expected:** All flags work together
- [ ] **Expected:** Dry-run preview shows release checks + orch mode

## Test 8: Brainstorm with Categories + Orch
- [ ] Run: `/craft:workflow:brainstorm "test" --orch=optimize -C req,tech`
- [ ] **Expected:** Orchestrator spawns with categories included
- [ ] **Expected:** Both categories processed

## Pass Criteria
- [ ] All 8 tests pass
- [ ] No unexpected errors or crashes
- [ ] Fallbacks work gracefully
- [ ] User experience is smooth and intuitive
```

---

### 4. Update CLAUDE.md

**File:** `CLAUDE.md`

**Changes:**
```markdown
## Key Files

| File | Purpose |
|------|---------|
| `.STATUS` | Current milestone, progress, session history |
| `commands/do.md` | Universal smart routing with complexity scoring |
| `commands/check.md` | Pre-flight validation |
| `commands/orchestrate.md` | Multi-agent coordination |
| `commands/hub.md` | Zero-maintenance command discovery (v2.0) |
| `commands/workflow/brainstorm.md` | ADHD-friendly brainstorming (v2.4.0 - Question control) |
| `docs/guide/orch-flag-usage.md` | --orch flag usage guide (v2.5.0) | <-- ADD THIS
| `docs/VERSION-HISTORY.md` | Complete version evolution (NEW) |
```

---

## Acceptance Criteria

### Functional Requirements

✅ **AC1:** `prompt_user_for_mode()` displays 4 options with descriptions
✅ **AC2:** User can select mode interactively
✅ **AC3:** Invalid/cancelled selection falls back to "default" mode
✅ **AC4:** `spawn_orchestrator()` returns success boolean
✅ **AC5:** Orchestrator failure shows error + fallback message
✅ **AC6:** Failed spawn doesn't crash execution
✅ **AC7:** Manual testing checklist covers 8 scenarios
✅ **AC8:** CLAUDE.md links to orch-flag-usage.md

### Non-Functional Requirements

✅ **AC9:** No breaking changes to existing API
✅ **AC10:** Backward compatible with v2.5.0
✅ **AC11:** Error messages are user-friendly
✅ **AC12:** Code coverage ≥ 95% for modified functions

---

## Implementation Plan

### Phase 1: Core Improvements (2-3 hours)

**Deliverables:**
- [ ] Implement `prompt_user_for_mode()` with `AskUserQuestion`
- [ ] Add error handling to `spawn_orchestrator()`
- [ ] Update function signatures and return types
- [ ] Add type hints

**Files:**
- `utils/orch_flag_handler.py` (UPDATE)

### Phase 2: Testing (1-2 hours)

**Deliverables:**
- [ ] Add 6 new unit tests for prompt function
- [ ] Add 3 new unit tests for error handling
- [ ] Create manual testing checklist
- [ ] Run all existing tests (ensure no regression)

**Files:**
- `tests/test_orch_flag_handler.py` (UPDATE)
- `TESTING-CHECKLIST.md` (NEW)

### Phase 3: Documentation (1 hour)

**Deliverables:**
- [ ] Update CLAUDE.md with orch guide link
- [ ] Update orch-flag-usage.md with troubleshooting section
- [ ] Update VERSION-HISTORY.md with v2.5.1 entry

**Files:**
- `CLAUDE.md` (UPDATE)
- `docs/guide/orch-flag-usage.md` (UPDATE)
- `docs/VERSION-HISTORY.md` (UPDATE)

---

## Dependencies

### Internal Dependencies
- `utils/orch_flag_handler.py` - Core handler (exists)
- `AskUserQuestion` tool - Claude Code 2.1.0+ (available)
- `Skill` tool - For orchestrator spawn (available)

### External Dependencies
None

---

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| `AskUserQuestion` not available in context | High | Low | Fallback to default mode (already implemented) |
| User confusion with mode selection | Medium | Low | Clear descriptions + "Recommended" tag |
| Orchestrator spawn failures break flow | High | Medium | Return boolean + fallback strategy |

---

## Testing Strategy

### Unit Tests (9 new tests)

**Mode Prompt Tests (6):**
- test_prompt_user_for_mode_returns_valid_mode
- test_prompt_user_for_mode_handles_cancellation
- test_prompt_user_for_mode_handles_invalid_selection
- test_prompt_user_for_mode_all_modes
- test_prompt_user_for_mode_extracts_mode_correctly
- test_prompt_user_for_mode_tool_unavailable

**Error Handling Tests (3):**
- test_spawn_orchestrator_returns_true_on_success
- test_spawn_orchestrator_returns_false_on_failure
- test_spawn_orchestrator_includes_extra_args

### Manual Testing (8 scenarios)
See TESTING-CHECKLIST.md for complete manual test plan.

---

## Success Metrics

- **Test Coverage:** 95%+ for modified functions
- **Bug Reports:** < 2 issues related to mode selection
- **User Satisfaction:** Positive feedback on interactive prompt
- **Fallback Success:** 100% graceful degradation on errors

---

## Rollout Plan

### Week 1: Development + Testing
- Complete Phase 1-2 (implementation + unit tests)
- Internal testing with TESTING-CHECKLIST.md

### Week 2: Documentation + Release
- Complete Phase 3 (documentation updates)
- Merge to `dev` branch
- Create v2.5.1 release

---

## Future Enhancements (Not in Scope)

- **Session state:** Remember last-used mode per session
- **Smart mode detection:** Infer mode from task complexity
- **Custom mode profiles:** User-defined modes
- **Performance optimization:** Measure and optimize spawn time

---

## Related Specifications

- SPEC-orch-flag-integration-2026-01-19.md - Parent spec (v2.5.0)
- GAP-ANALYSIS-orch-flag-v2.5.0.md - Gap analysis (source)
- SPEC-craft-hub-v2-2026-01-15.md - Hub v2.0 architecture

---

## Approval

**Approved by:** DT (user)
**Date:** 2026-01-19
**Implementation target:** v2.5.1
**Branch:** `feature/orch-flag-v2.5.1-improvements`
