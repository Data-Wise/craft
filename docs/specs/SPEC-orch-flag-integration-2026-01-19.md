# SPEC: --orch Flag Integration

**Created**: 2026-01-19
**Status**: Approved
**Version**: v2.5.0
**Priority**: High
**Effort**: Medium (8-12 hours)

## Overview

Add `--orch` flag to selected Craft commands to enable explicit orchestration mode. This provides a shorthand for spawning the orchestrator without requiring separate `/craft:orchestrate` invocation.

## User Requirements

### Commands to Enhance

1. `/craft:do` - Universal router
2. `/craft:workflow:brainstorm` - ADHD-friendly brainstorming
3. `/craft:check` - Pre-flight validation
4. `/craft:docs:sync` - Documentation sync
5. `/craft:ci:generate` - CI workflow generation

### Behavior Specification

#### Flag Syntax

```bash
# No mode specified → prompt user
/craft:do "add auth" --orch

# Explicit mode
/craft:do "add auth" --orch=optimize
/craft:do "add auth" --orch=debug

# Compatibility with other flags
/craft:do "add auth" --orch=optimize --dry-run
/craft:workflow:brainstorm "payment" --orch -C req,tech
```

#### Mode Selection

- **Explicit mode**: `--orch=<mode>` (default|debug|optimize|release)
- **No mode**: Prompt user interactively to select mode
- **Invalid mode**: Error with valid options

#### Integration Requirements

✅ Compatible with `--dry-run` flag (preview orchestration plan)
✅ Compatible with mode flags (`--orch debug` or `--orch=debug`)
✅ Compatible with category filters for brainstorm (`-C req,tech`)
✅ Overrides complexity-based routing in `/craft:do`

### User Stories

**Story 1**: Quick Orchestration

```
As a developer
I want to quickly orchestrate a task without separate command
So that I can save keystrokes and mental overhead

Example:
/craft:do "add auth" --orch=optimize
```

**Story 2**: Preview Orchestration

```
As a developer
I want to preview what orchestration will do
So that I can decide if it's worth the context cost

Example:
/craft:do "add auth" --orch=optimize --dry-run
```

**Story 3**: Brainstorm with Orchestration

```
As a developer with ADHD
I want to orchestrate brainstorm sessions
So that multiple agents gather context in parallel

Example:
/craft:workflow:brainstorm "payment system" --orch -C req,tech,risk
```

## Technical Requirements

### 1. Command YAML Frontmatter Updates

Add `--orch` argument to each command's frontmatter:

```yaml
arguments:
  - name: orch
    description: Enable orchestration mode (optionally specify mode)
    required: false
    default: null
    alias: --orch
  - name: orch-mode
    description: Orchestration mode (default|debug|optimize|release)
    required: false
    default: null
```

### 2. Orchestration Logic

Each command must implement:

```python
def handle_orch_flag(task, orch_flag, mode_flag):
    """
    Handle --orch flag logic

    Args:
        task: Task description
        orch_flag: True if --orch present, False otherwise
        mode_flag: Mode value if --orch=<mode>, None otherwise

    Returns:
        Tuple (should_orchestrate, selected_mode)
    """
    if not orch_flag:
        return (False, None)

    # If mode specified explicitly
    if mode_flag:
        valid_modes = ["default", "debug", "optimize", "release"]
        if mode_flag not in valid_modes:
            raise ValueError(f"Invalid mode: {mode_flag}. Valid: {valid_modes}")
        return (True, mode_flag)

    # No mode specified → prompt user
    selected_mode = prompt_user_for_mode()
    return (True, selected_mode)


def prompt_user_for_mode():
    """Prompt user to select orchestration mode"""
    # Use AskUserQuestion tool
    response = AskUserQuestion(
        questions=[{
            "question": "Which orchestration mode?",
            "header": "Mode",
            "multiSelect": False,
            "options": [
                {
                    "label": "default (2 agents)",
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
    return response["Which orchestration mode?"]


def spawn_orchestrator(task, mode):
    """Spawn orchestrator with specified mode"""
    # Use Skill tool to invoke orchestrator
    Skill(
        skill="craft:orchestrate",
        args=f"{task} {mode}"
    )
```

### 3. Integration with Existing Flags

#### /craft:do Integration

```python
# In /craft:do command implementation
task = args.task
orch_flag = args.orch
mode_flag = args.orch_mode
dry_run = args.dry_run

# Check for --orch flag first
if orch_flag:
    should_orchestrate, mode = handle_orch_flag(task, orch_flag, mode_flag)

    if dry_run:
        show_orchestration_preview(task, mode)
        return

    spawn_orchestrator(task, mode)
    return

# Otherwise, use complexity-based routing (existing logic)
complexity_score = calculate_complexity(task)
route_by_complexity(task, complexity_score)
```

#### /craft:workflow:brainstorm Integration

```python
# In /craft:workflow:brainstorm command implementation
task = args.task
categories = args.categories
orch_flag = args.orch
mode_flag = args.orch_mode

# Check for --orch flag
if orch_flag:
    should_orchestrate, mode = handle_orch_flag(task, orch_flag, mode_flag)

    # Pass category filters to orchestrator
    orchestrator_task = f"brainstorm '{task}' with categories: {categories}"
    spawn_orchestrator(orchestrator_task, mode)
    return

# Otherwise, run brainstorm directly (existing logic)
run_brainstorm(task, categories)
```

### 4. Dry-Run Mode Integration

When `--orch` and `--dry-run` are both present:

```python
def show_orchestration_preview(task, mode):
    """Show orchestration plan without spawning agents"""
    print(f"""
┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Orchestration Preview                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Task: {task}                                                │
│ ✓ Mode: {mode}                                                │
│ ✓ Max Agents: {get_max_agents(mode)}                          │
│ ✓ Compression: {get_compression_threshold(mode)}%             │
│                                                               │
│ This would spawn the orchestrator with the above settings.    │
│ Remove --dry-run to execute.                                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
""")
```

## Acceptance Criteria

### Functional Requirements

✅ **AC1**: `/craft:do "task" --orch` prompts for mode selection
✅ **AC2**: `/craft:do "task" --orch=optimize` spawns orchestrator in optimize mode
✅ **AC3**: `/craft:do "task" --orch=invalid` shows error with valid modes
✅ **AC4**: `/craft:do "task" --orch --dry-run` shows preview without spawning
✅ **AC5**: `/craft:workflow:brainstorm "task" --orch -C req,tech` orchestrates with categories
✅ **AC6**: All 5 commands support `--orch` flag
✅ **AC7**: `--orch` overrides complexity-based routing in `/craft:do`

### Non-Functional Requirements

✅ **AC8**: Flag is opt-in (no breaking changes to existing behavior)
✅ **AC9**: Error messages are clear and actionable
✅ **AC10**: Documentation updated for all 5 commands
✅ **AC11**: Tests cover all flag combinations
✅ **AC12**: Performance: Mode prompt < 1 second response time

## Implementation Plan

### Phase 1: Core Infrastructure (2-3 hours)

**Deliverables**:

- [ ] Create `utils/orch_flag_handler.py` with core logic
- [ ] Add mode prompt using `AskUserQuestion`
- [ ] Add orchestrator spawning logic
- [ ] Add dry-run preview logic

**Files**:

- `utils/orch_flag_handler.py` (NEW)
- `utils/complexity_scorer.py` (UPDATE: add orchestrator mode mapping)

### Phase 2: Command Updates (3-4 hours)

**Deliverables**:

- [ ] Update `/craft:do` YAML frontmatter + implementation
- [ ] Update `/craft:workflow:brainstorm` YAML frontmatter + implementation
- [ ] Update `/craft:check` YAML frontmatter + implementation
- [ ] Update `/craft:docs:sync` YAML frontmatter + implementation
- [ ] Update `/craft:ci:generate` YAML frontmatter + implementation

**Files**:

- `commands/do.md` (UPDATE)
- `commands/workflow/brainstorm.md` (UPDATE)
- `commands/check.md` (UPDATE)
- `commands/docs/sync.md` (UPDATE)
- `commands/ci/generate.md` (UPDATE)

### Phase 3: Testing (2-3 hours)

**Deliverables**:

- [ ] Unit tests for `orch_flag_handler.py`
- [ ] Integration tests for each command
- [ ] Test flag combinations (--orch + --dry-run, --orch + -C)
- [ ] Test error handling (invalid modes)
- [ ] Test mode prompt interaction

**Files**:

- `tests/test_orch_flag_handler.py` (NEW)
- `tests/test_integration_orch_flag.py` (NEW)

**Test Cases**:

```python
def test_orch_flag_with_mode():
    """Test --orch=optimize spawns orchestrator"""
    result = craft_do("add auth", orch=True, mode="optimize")
    assert result.orchestrator_spawned
    assert result.mode == "optimize"

def test_orch_flag_no_mode():
    """Test --orch prompts for mode"""
    result = craft_do("add auth", orch=True, mode=None)
    assert result.prompted_for_mode

def test_orch_flag_invalid_mode():
    """Test --orch=invalid shows error"""
    with pytest.raises(ValueError):
        craft_do("add auth", orch=True, mode="invalid")

def test_orch_flag_with_dry_run():
    """Test --orch --dry-run shows preview"""
    result = craft_do("add auth", orch=True, mode="optimize", dry_run=True)
    assert result.preview_shown
    assert not result.orchestrator_spawned

def test_brainstorm_orch_with_categories():
    """Test brainstorm --orch -C req,tech"""
    result = brainstorm("payment", orch=True, mode="optimize", categories=["req", "tech"])
    assert result.orchestrator_spawned
    assert "req" in result.categories
    assert "tech" in result.categories
```

### Phase 4: Documentation (1-2 hours)

**Deliverables**:

- [ ] Update command documentation with `--orch` examples
- [ ] Add guide: "Using --orch Flag for Quick Orchestration"
- [ ] Update CLAUDE.md with --orch flag info
- [ ] Update VERSION-HISTORY.md with v2.5.0 entry

**Files**:

- `docs/guide/orch-flag-usage.md` (NEW)
- `CLAUDE.md` (UPDATE)
- `docs/VERSION-HISTORY.md` (UPDATE)
- All 5 command files (UPDATE with examples)

## Examples

### Example 1: Quick Orchestration

```bash
/craft:do "add user authentication" --orch=optimize

## 🚀 ORCHESTRATOR v2.1 — OPTIMIZE MODE

Spawning orchestrator...
- Task: add user authentication
- Mode: optimize (4 agents max)
- Strategy: Aggressive parallelization

Wave 1: Spawning arch-1, doc-1 in parallel...
```

### Example 2: Mode Prompt

```bash
/craft:do "add payment integration" --orch

[AskUserQuestion]
Which orchestration mode?

Options:
1. default (2 agents) - Quick tasks, moderate parallelization
2. debug (1 agent) - Sequential, verbose output
3. optimize (4 agents) - Fast parallel work
4. release (4 agents) - Pre-release audit

User selects: optimize

Spawning orchestrator in optimize mode...
```

### Example 3: Dry-Run Preview

```bash
/craft:do "refactor authentication" --orch=release --dry-run

┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Orchestration Preview                            │
├───────────────────────────────────────────────────────────────┤
│                                                               │
│ ✓ Task: refactor authentication                              │
│ ✓ Mode: release                                               │
│ ✓ Max Agents: 4                                               │
│ ✓ Compression: 85%                                            │
│                                                               │
│ This would spawn the orchestrator with:                       │
│ - backend-architect (design refactor)                         │
│ - code-quality-reviewer (analyze current code)                │
│ - test-specialist (ensure test coverage)                      │
│ - docs-architect (update architecture docs)                   │
│                                                               │
│ Remove --dry-run to execute.                                  │
│                                                               │
└───────────────────────────────────────────────────────────────┘
```

### Example 4: Brainstorm with Orchestration

```bash
/craft:workflow:brainstorm "payment processing system" --orch=optimize -C req,tech,risk

## 🚀 ORCHESTRATOR v2.1 — OPTIMIZE MODE

Orchestrating brainstorm session...

Wave 1 (Parallel):
- Agent 1: Gather requirements (req category)
- Agent 2: Research tech stack (tech category)
- Agent 3: Identify risks (risk category)

Synthesizing results into comprehensive spec...
```

## Dependencies

### Internal Dependencies

- `utils/complexity_scorer.py` - For complexity calculation
- `commands/orchestrate.md` - Orchestrator command
- `.claude-plugin/plugin.json` - Plugin manifest

### External Dependencies

- AskUserQuestion tool (Claude Code 2.1.0+)
- Skill tool (for spawning orchestrator)

## Risks and Mitigations

| Risk | Impact | Probability | Mitigation |
|------|--------|-------------|------------|
| Breaking existing workflows | High | Low | Make `--orch` opt-in, no default behavior change |
| Mode prompt confusion | Medium | Medium | Clear descriptions, sensible defaults |
| Flag parsing conflicts | Medium | Low | Use standard argparse patterns |
| Orchestrator spawn failures | High | Low | Graceful error handling, fallback to command routing |

## Success Metrics

- **Adoption**: 30%+ of `/craft:do` invocations use `--orch` within 2 weeks
- **User satisfaction**: Positive feedback on shortcuts saved
- **Bug reports**: < 3 bugs related to flag parsing
- **Performance**: Mode prompt response < 1 second

## Rollout Plan

### Week 1: Development

- Complete Phase 1-2 (infrastructure + command updates)
- Internal testing

### Week 2: Testing & Documentation

- Complete Phase 3-4 (tests + docs)
- Update CLAUDE.md and VERSION-HISTORY.md

### Week 3: Release

- Merge to `dev` branch
- PR to `main` with v2.5.0 tag
- Announce in release notes

## Future Enhancements (Not in Scope)

- **Auto-mode detection**: Infer mode from task complexity/keywords
- **Custom mode profiles**: User-defined modes (e.g., `--orch=myprofile`)
- **Mode presets**: Save favorite modes per project
- **Global default mode**: Set default mode in `.claude/settings.json`
- **Orchestrator templates**: Predefined agent coordination patterns

## Related Specifications

- SPEC-craft-hub-v2-2026-01-15.md - Hub v2.0 architecture
- SPEC-brainstorm-question-control-phase1-2026-01-18.md - Question control system
- SPEC-teaching-workflow-2026-01-16.md - Teaching mode integration

## Approval

**Approved by**: DT (user)
**Date**: 2026-01-19
**Implementation target**: v2.5.0
**Branch**: `feature/orch-flag-integration`
