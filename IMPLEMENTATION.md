# Implementation Instructions: --orch Flag Integration

**Branch**: `feature/orch-flag-integration`
**Target Version**: v2.5.0
**Estimated Effort**: 8-12 hours
**Spec**: `docs/specs/SPEC-orch-flag-integration-2026-01-19.md`

## Overview

Add `--orch` flag to 5 key Craft commands to enable explicit orchestration mode without requiring separate `/craft:orchestrate` invocation.

## Implementation Phases

### Phase 1: Core Infrastructure (2-3 hours) ✅ START HERE

**Goal**: Build the foundational orchestration flag handler that all commands will use.

#### Files to Create

1. **`utils/orch_flag_handler.py`** (NEW)
   - Core logic for handling `--orch` flag
   - Mode validation and prompting
   - Orchestrator spawning
   - Dry-run preview

**Implementation Steps**:

```python
# utils/orch_flag_handler.py

"""
Orchestration flag handler for Craft commands.

Provides unified logic for --orch flag across all commands.
"""

from typing import Optional, Tuple, Dict, Any
import sys


VALID_MODES = ["default", "debug", "optimize", "release"]

MODE_DESCRIPTIONS = {
    "default": "Quick tasks (2 agents max, 70% compression)",
    "debug": "Sequential troubleshooting (1 agent, 90% compression)",
    "optimize": "Fast parallel work (4 agents, 60% compression)",
    "release": "Pre-release audit (4 agents, 85% compression)"
}


def handle_orch_flag(
    task: str,
    orch_flag: bool,
    mode: Optional[str] = None
) -> Tuple[bool, Optional[str]]:
    """
    Handle --orch flag logic.

    Args:
        task: Task description
        orch_flag: True if --orch present
        mode: Mode value if --orch=<mode>, None otherwise

    Returns:
        Tuple of (should_orchestrate, selected_mode)

    Raises:
        ValueError: If invalid mode specified
    """
    if not orch_flag:
        return (False, None)

    # If mode specified explicitly
    if mode:
        if mode not in VALID_MODES:
            raise ValueError(
                f"Invalid mode: '{mode}'. Valid modes: {', '.join(VALID_MODES)}"
            )
        return (True, mode)

    # No mode specified → prompt user
    selected_mode = prompt_user_for_mode()
    return (True, selected_mode)


def prompt_user_for_mode() -> str:
    """
    Prompt user to select orchestration mode interactively.

    Uses AskUserQuestion tool from Claude Code.

    Returns:
        Selected mode name
    """
    # This will be implemented using AskUserQuestion tool
    # For now, return a placeholder that Claude will recognize
    print("\n🎯 Orchestration Mode Selection")
    print("=" * 50)
    print("\nAvailable modes:")
    for mode, desc in MODE_DESCRIPTIONS.items():
        print(f"  • {mode:10s} - {desc}")

    # In actual implementation, this calls AskUserQuestion
    # Claude Code will intercept this and show the interactive prompt
    return "default"  # Placeholder


def show_orchestration_preview(task: str, mode: str) -> None:
    """
    Display orchestration plan without spawning agents.

    Args:
        task: Task description
        mode: Selected orchestration mode
    """
    mode_config = get_mode_config(mode)

    print("\n┌" + "─" * 63 + "┐")
    print("│ 🔍 DRY RUN: Orchestration Preview" + " " * 29 + "│")
    print("├" + "─" * 63 + "┤")
    print("│" + " " * 63 + "│")
    print(f"│ ✓ Task: {task[:49]:<49s} │")
    print(f"│ ✓ Mode: {mode:<49s} │")
    print(f"│ ✓ Max Agents: {mode_config['max_agents']:<45d} │")
    print(f"│ ✓ Compression: {mode_config['compression']}%{' ' * 42} │")
    print("│" + " " * 63 + "│")
    print("│ This would spawn the orchestrator with the above settings." + " " * 3 + "│")
    print("│ Remove --dry-run to execute." + " " * 32 + "│")
    print("│" + " " * 63 + "│")
    print("└" + "─" * 63 + "┘\n")


def get_mode_config(mode: str) -> Dict[str, Any]:
    """Get configuration for orchestration mode."""
    configs = {
        "default": {"max_agents": 2, "compression": 70},
        "debug": {"max_agents": 1, "compression": 90},
        "optimize": {"max_agents": 4, "compression": 60},
        "release": {"max_agents": 4, "compression": 85}
    }
    return configs.get(mode, configs["default"])


def spawn_orchestrator(task: str, mode: str, extra_args: str = "") -> None:
    """
    Spawn orchestrator with specified mode.

    Args:
        task: Task description
        mode: Orchestration mode
        extra_args: Additional arguments to pass
    """
    # This will be implemented using Skill tool
    # For now, show what would be executed
    print(f"\n🚀 Spawning orchestrator...")
    print(f"   Task: {task}")
    print(f"   Mode: {mode}")
    if extra_args:
        print(f"   Extra args: {extra_args}")
    print("\n   Executing: /craft:orchestrate '{task}' {mode} {extra_args}\n")
```

2. **Update `utils/complexity_scorer.py`** (UPDATE)
   - Add function to map complexity score → orchestration mode
   - Add orchestrator mode recommendations

```python
# Add to utils/complexity_scorer.py

def recommend_orchestration_mode(complexity_score: int) -> str:
    """
    Recommend orchestration mode based on complexity score.

    Args:
        complexity_score: Task complexity (0-10)

    Returns:
        Recommended mode name
    """
    if complexity_score <= 3:
        return "default"
    elif complexity_score <= 5:
        return "default"
    elif complexity_score <= 7:
        return "optimize"
    else:
        return "release"
```

#### Testing Phase 1

Create tests BEFORE implementing commands:

```bash
# tests/test_orch_flag_handler.py

import pytest
from utils.orch_flag_handler import (
    handle_orch_flag,
    show_orchestration_preview,
    get_mode_config,
    VALID_MODES
)


def test_orch_flag_disabled():
    """Test --orch not present"""
    should_orch, mode = handle_orch_flag("task", orch_flag=False)
    assert should_orch is False
    assert mode is None


def test_orch_flag_with_valid_mode():
    """Test --orch=optimize"""
    should_orch, mode = handle_orch_flag("task", orch_flag=True, mode="optimize")
    assert should_orch is True
    assert mode == "optimize"


def test_orch_flag_with_invalid_mode():
    """Test --orch=invalid raises error"""
    with pytest.raises(ValueError, match="Invalid mode"):
        handle_orch_flag("task", orch_flag=True, mode="invalid")


def test_mode_config():
    """Test mode configuration retrieval"""
    config = get_mode_config("optimize")
    assert config["max_agents"] == 4
    assert config["compression"] == 60


def test_all_modes_have_config():
    """Test all valid modes have config"""
    for mode in VALID_MODES:
        config = get_mode_config(mode)
        assert "max_agents" in config
        assert "compression" in config


# Run tests
pytest tests/test_orch_flag_handler.py -v
```

**Checkpoint**: Phase 1 complete when all tests pass ✅

---

### Phase 2: Command Updates (3-4 hours)

**Goal**: Add `--orch` flag to 5 commands with proper integration.

#### Command 1: `/craft:do` (HIGHEST PRIORITY)

**File**: `commands/do.md`

**Changes**:

1. Add to YAML frontmatter:
```yaml
arguments:
  - name: task
    description: Natural language description of what you want to do
    required: true
  - name: dry-run
    description: Preview routing plan without executing commands
    required: false
    default: false
    alias: -n
  # ADD THESE TWO:
  - name: orch
    description: Enable orchestration mode
    required: false
    default: false
  - name: orch-mode
    description: Orchestration mode (default|debug|optimize|release)
    required: false
    default: null
```

2. Update implementation section:
```markdown
## Implementation (UPDATED for v2.5.0)

When `/craft:do` is invoked, follow these steps:

### Step 0: Check for --orch Flag (NEW)

```python
from utils.orch_flag_handler import handle_orch_flag, show_orchestration_preview, spawn_orchestrator

task = args.task
orch_flag = args.orch
mode_flag = args.orch_mode
dry_run = args.dry_run

# Check for --orch flag FIRST
if orch_flag:
    should_orchestrate, mode = handle_orch_flag(task, orch_flag, mode_flag)

    if dry_run:
        show_orchestration_preview(task, mode)
        return

    spawn_orchestrator(task, mode)
    return

# Otherwise, continue with complexity-based routing...
```

### Step 1: Analyze Task and Calculate Complexity
[...existing content...]
```

3. Add examples section:
```markdown
## Examples with --orch Flag (NEW in v2.5.0)

### Quick Orchestration
```bash
/craft:do "add user authentication" --orch=optimize

## 🚀 ORCHESTRATOR v2.1 — OPTIMIZE MODE
Spawning orchestrator...
```

### Mode Selection Prompt
```bash
/craft:do "add payment" --orch

🎯 Orchestration Mode Selection
Available modes:
  • default    - Quick tasks (2 agents max)
  • debug      - Sequential troubleshooting
  • optimize   - Fast parallel work (4 agents)
  • release    - Pre-release audit

[AskUserQuestion prompt appears]
```

### Preview Orchestration
```bash
/craft:do "refactor auth" --orch=release --dry-run

┌───────────────────────────────────────────────────────────────┐
│ 🔍 DRY RUN: Orchestration Preview                            │
├───────────────────────────────────────────────────────────────┤
│ ✓ Task: refactor auth                                         │
│ ✓ Mode: release                                               │
│ ✓ Max Agents: 4                                               │
│ ✓ Compression: 85%                                            │
└───────────────────────────────────────────────────────────────┘
```
```

#### Command 2: `/craft:workflow:brainstorm`

**File**: `commands/workflow/brainstorm.md`

**Similar changes** to frontmatter + implementation + examples.

Key difference: Pass category filters to orchestrator:

```python
if orch_flag:
    should_orchestrate, mode = handle_orch_flag(task, orch_flag, mode_flag)

    # Build orchestrator task with category context
    categories_str = ",".join(args.categories) if args.categories else "all"
    orchestrator_task = f"brainstorm '{task}' focusing on categories: {categories_str}"

    spawn_orchestrator(orchestrator_task, mode)
    return
```

#### Commands 3-5: `/craft:check`, `/craft:docs:sync`, `/craft:ci:generate`

**Similar pattern for each**:
1. Add YAML frontmatter arguments
2. Add --orch check at start of implementation
3. Add examples section
4. Document integration

**Checkpoint**: Phase 2 complete when all 5 commands updated ✅

---

### Phase 3: Testing (2-3 hours)

**Goal**: Comprehensive test coverage for all flag combinations.

#### Integration Tests

**File**: `tests/test_integration_orch_flag.py`

```python
"""Integration tests for --orch flag across commands"""

import pytest
from unittest.mock import Mock, patch


class TestOrchFlagIntegration:
    """Test --orch flag integration with commands"""

    def test_craft_do_with_orch_mode(self):
        """Test /craft:do 'task' --orch=optimize"""
        # Mock orchestrator spawn
        with patch('utils.orch_flag_handler.spawn_orchestrator') as mock_spawn:
            result = craft_do("add auth", orch=True, mode="optimize")

            mock_spawn.assert_called_once_with("add auth", "optimize", extra_args="")
            assert result.orchestrator_spawned

    def test_craft_do_with_orch_no_mode(self):
        """Test /craft:do 'task' --orch prompts for mode"""
        with patch('utils.orch_flag_handler.prompt_user_for_mode') as mock_prompt:
            mock_prompt.return_value = "debug"

            result = craft_do("fix bug", orch=True, mode=None)

            mock_prompt.assert_called_once()
            assert result.prompted_for_mode
            assert result.selected_mode == "debug"

    def test_craft_do_with_orch_invalid_mode(self):
        """Test /craft:do 'task' --orch=invalid raises error"""
        with pytest.raises(ValueError, match="Invalid mode"):
            craft_do("task", orch=True, mode="invalid")

    def test_craft_do_with_orch_and_dry_run(self):
        """Test /craft:do 'task' --orch --dry-run shows preview"""
        result = craft_do("task", orch=True, mode="optimize", dry_run=True)

        assert result.preview_shown
        assert not result.orchestrator_spawned

    def test_brainstorm_orch_with_categories(self):
        """Test /brainstorm 'task' --orch -C req,tech"""
        with patch('utils.orch_flag_handler.spawn_orchestrator') as mock_spawn:
            result = brainstorm(
                "payment",
                orch=True,
                mode="optimize",
                categories=["req", "tech"]
            )

            # Check orchestrator receives category context
            call_args = mock_spawn.call_args[0]
            assert "req" in call_args[0]
            assert "tech" in call_args[0]

    def test_orch_overrides_complexity_routing(self):
        """Test --orch overrides complexity-based routing"""
        # Simple task (score 2) would normally use commands
        with patch('utils.orch_flag_handler.spawn_orchestrator') as mock_spawn:
            result = craft_do("lint code", orch=True, mode="default")

            # Despite low complexity, orchestrator spawned
            mock_spawn.assert_called_once()

    def test_all_commands_support_orch(self):
        """Test all 5 commands support --orch flag"""
        commands = [
            "craft:do",
            "craft:workflow:brainstorm",
            "craft:check",
            "craft:docs:sync",
            "craft:ci:generate"
        ]

        for cmd in commands:
            # Verify each command has --orch argument
            assert has_orch_argument(cmd)


# Run integration tests
pytest tests/test_integration_orch_flag.py -v
```

#### Test Coverage Goals

| Component | Target Coverage | Tests |
|-----------|----------------|-------|
| `orch_flag_handler.py` | 95%+ | 15+ tests |
| Command integrations | 90%+ | 25+ tests |
| Flag combinations | 100% | 10+ tests |
| Error handling | 100% | 8+ tests |

**Checkpoint**: Phase 3 complete when coverage targets met ✅

---

### Phase 4: Documentation (1-2 hours)

**Goal**: Comprehensive documentation for users and developers.

#### 1. Create User Guide

**File**: `docs/guide/orch-flag-usage.md` (NEW)

```markdown
# Using the --orch Flag for Quick Orchestration

**Added in**: v2.5.0
**Status**: Stable

## Overview

The `--orch` flag provides a shorthand for spawning the orchestrator without requiring a separate `/craft:orchestrate` command invocation.

## Supported Commands

| Command | Use Case |
|---------|----------|
| `/craft:do` | Universal task routing with orchestration |
| `/craft:workflow:brainstorm` | Parallel context gathering |
| `/craft:check` | Orchestrated validation workflows |
| `/craft:docs:sync` | Multi-agent documentation updates |
| `/craft:ci:generate` | Complex CI workflow generation |

## Usage Patterns

[...comprehensive examples...]

## When to Use --orch

[...decision guide...]

## Troubleshooting

[...common issues...]
```

#### 2. Update CLAUDE.md

Add section in "Quick Commands" table:

```markdown
| Orchestrate task | - | `/craft:do "task" --orch=optimize` |
```

Add to "Recent Major Features":

```markdown
### --orch Flag Integration (v2.5.0) ✅
- Explicit orchestration for 5 key commands
- Mode selection with interactive prompts
- Dry-run preview support
- 58 tests, 95% coverage
```

#### 3. Update VERSION-HISTORY.md

```markdown
## v2.5.0 - --orch Flag Integration (2026-01-XX)

### Added
- **--orch Flag**: Explicit orchestration mode for 5 commands
  - `/craft:do`, `/craft:workflow:brainstorm`, `/craft:check`
  - `/craft:docs:sync`, `/craft:ci:generate`
- **Mode Selection**: Interactive prompts when mode not specified
- **Dry-Run Support**: Preview orchestration without spawning agents

### Implementation
- Core handler: `utils/orch_flag_handler.py`
- 58 tests (unit + integration), 95% coverage
- Backward compatible (opt-in flag)
```

#### 4. Update Command Documentation

For each of the 5 commands, add:

1. Flag documentation in frontmatter
2. Usage examples with `--orch`
3. Integration notes
4. Link to guide

**Checkpoint**: Phase 4 complete when all docs updated ✅

---

## Testing Checklist

Before marking as complete, verify:

- [ ] All unit tests pass (`pytest tests/test_orch_flag_handler.py`)
- [ ] All integration tests pass (`pytest tests/test_integration_orch_flag.py`)
- [ ] Coverage ≥ 95% for core handler
- [ ] Coverage ≥ 90% for command integrations
- [ ] Dry-run mode works for all commands
- [ ] Mode prompt appears when mode not specified
- [ ] Invalid modes show clear error messages
- [ ] `--orch` works with `--dry-run`
- [ ] `--orch` works with other flags (e.g., `-C` for brainstorm)
- [ ] Documentation builds without errors

## Validation Commands

```bash
# Run all tests
python3 tests/test_orch_flag_handler.py
python3 tests/test_integration_orch_flag.py

# Check coverage
pytest tests/test_orch_flag_handler.py --cov=utils.orch_flag_handler --cov-report=term-missing

# Validate command frontmatter
python3 utils/validate_frontmatter.py commands/do.md
python3 utils/validate_frontmatter.py commands/workflow/brainstorm.md

# Build documentation
mkdocs build

# Run validation script
./scripts/validate-counts.sh
```

## Success Criteria

✅ All acceptance criteria from spec met
✅ Test coverage targets achieved
✅ Documentation complete and accurate
✅ No breaking changes to existing commands
✅ Performance: Mode prompt < 1 second
✅ All validation commands pass

## Next Steps After Implementation

1. Create PR to `dev` branch
2. Run full test suite
3. Update CLAUDE.md with implementation status
4. Announce in release notes
5. Clean up worktree after merge

---

## Quick Start

```bash
# 1. Navigate to worktree
cd ~/.git-worktrees/craft/feature-orch-flag-integration

# 2. Verify on correct branch
git branch --show-current  # Should show: feature/orch-flag-integration

# 3. Start with Phase 1
# Create utils/orch_flag_handler.py

# 4. Run tests frequently
pytest tests/test_orch_flag_handler.py -v

# 5. Commit small, atomic changes
git add utils/orch_flag_handler.py
git commit -m "feat: add orchestration flag handler"
```

## Need Help?

- Read spec: `docs/specs/SPEC-orch-flag-integration-2026-01-19.md`
- Check examples in existing commands
- Run tests to understand expected behavior
- Use `/craft:check` before committing
