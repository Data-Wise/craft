# ORCHESTRATE - Claude-MD Command Porting

**Feature:** Port claude-md commands from local Claude Code to craft plugin
**Branch:** feature/claude-md-port
**Target:** dev
**Mode:** phase (4 phases)

---

## Overview

Port 7 claude-md subcommands from `~/.claude/commands/claude-md/` to craft plugin as nested commands under `/craft:docs:claude-md:*` namespace.

**User Decisions (from interactive planning):**

- **Scope:** Start with update command, expand to full suite
- **Structure:** Nested namespace `/craft:docs:claude-md:*`
- **Integration:** Replace existing `/craft:docs:claude-md` completely
- **Adaptations:** Add craft project types + minimal changes to local logic

---

## Phase 1: Foundation - Update Command (Priority: HIGH)

**Goal:** Port `/craft:docs:claude-md:update` as foundation

### Files to Create/Modify

1. **commands/docs/claude-md/update.md** (NEW)
   - Source: `~/.claude/commands/claude-md/update.md` (278 lines)
   - Replace: `commands/docs/claude-md.md` (249 lines)
   - Enhancements:
     - Add "Show Steps First" pattern (preview before execute)
     - Integrate craft project type detection
     - Add dry-run mode
     - Interactive section selection

2. **utils/claude_md_detector.py** (NEW)
   - Project type detection for CLAUDE.md templates
   - Extend existing project-detector patterns
   - Add craft-specific types: plugin, teaching, r-package, mcp

3. **tests/test_claude_md_update.py** (NEW)
   - 15-20 tests
   - Test project detection, version sync, dry-run, interactive mode

### Success Criteria

- [ ] Update command works with dry-run preview
- [ ] Detects craft plugin projects correctly
- [ ] Syncs version from plugin.json/package.json/pyproject.toml
- [ ] 15+ tests passing with 90%+ coverage
- [ ] "Show Steps First" pattern implemented

**Estimated:** 2 hours implementation + testing

---

## Phase 2: Validation - Audit & Fix Commands (Priority: HIGH)

**Goal:** Add validation and auto-fix capabilities

### Files to Create

1. **commands/docs/claude-md/audit.md** (NEW)
   - Source: `~/.claude/commands/claude-md/audit.md` (195 lines)
   - Validate CLAUDE.md completeness
   - Check version sync, command coverage, broken links
   - Integration with `/craft:check`

2. **commands/docs/claude-md/fix.md** (NEW)
   - Source: `~/.claude/commands/claude-md/fix.md` (217 lines)
   - Auto-fix version mismatches, broken links
   - Dry-run preview before fixing
   - Interactive mode for manual fixes

3. **tests/test_claude_md_audit.py** (NEW)
   - 10-12 tests for audit functionality

4. **tests/test_claude_md_fix.py** (NEW)
   - 8-10 tests for fix functionality

### Integration Points

- Add CLAUDE.md validation to `/craft:check` workflow
- Coordinate with `/craft:docs:check` for link validation
- Use existing `utils/help_file_validator.py` patterns

### Success Criteria

- [ ] Audit detects version mismatches
- [ ] Audit finds missing commands
- [ ] Fix auto-corrects fixable issues
- [ ] Integration with `/craft:check` works
- [ ] 18+ tests passing

**Estimated:** 2.5 hours implementation + testing

---

## Phase 3: Generation - Scaffold & Edit Commands (Priority: MEDIUM)

**Goal:** Add template-based generation and interactive editing

### Files to Create

1. **commands/docs/claude-md/scaffold.md** (NEW)
   - Source: `~/.claude/commands/claude-md/scaffold.md` (193 lines)
   - Create CLAUDE.md from templates
   - Craft-specific templates (plugin, teaching, r-package)
   - Auto-detect project type and populate

2. **commands/docs/claude-md/edit.md** (NEW)
   - Source: `~/.claude/commands/claude-md/edit.md` (271 lines)
   - Interactive section-by-section editing
   - AskUserQuestion for section selection
   - Preview changes before applying

3. **templates/claude-md/** (NEW DIRECTORY)
   - `plugin-template.md` - Craft plugin structure
   - `teaching-template.md` - Course/teaching site
   - `r-package-template.md` - R package with pkgdown
   - `mcp-template.md` - MCP server

4. **tests/test_claude_md_scaffold.py** (NEW)
   - 12-15 tests for template generation

5. **tests/test_claude_md_edit.py** (NEW)
   - 10-12 tests for interactive editing

### Template Requirements

Each template should include:

- Auto-populated version from source files
- Auto-discovered commands/structure
- Project-specific Quick Reference
- Standard sections (Overview, Architecture, Workflow)

### Success Criteria

- [ ] Scaffold detects craft plugin projects
- [ ] Templates auto-populate from project analysis
- [ ] Edit mode allows section selection
- [ ] 22+ tests passing
- [ ] 3 craft-specific templates created

**Estimated:** 3.5 hours implementation + testing

---

## Phase 4: Documentation - Tutorial & Help (Priority: LOW)

**Goal:** Create comprehensive documentation

### Files to Create

1. **docs/tutorials/claude-md-workflows.md** (NEW)
   - Convert `tutorial.md` to craft tutorial format
   - Add craft-specific examples (plugin, teaching)
   - Step-by-step workflows

2. **docs/commands/docs/claude-md.md** (NEW)
   - Convert `help.md` to craft command reference
   - Add mermaid flowcharts
   - Integration with `/craft:hub`

3. **docs/reference/REFCARD-CLAUDE-MD.md** (NEW)
   - Quick reference card
   - Common workflows
   - Command cheat sheet

### Hub Integration

Update `/craft:hub` to include claude-md category:

- Add category detection for claude-md commands
- Create progressive disclosure hierarchy
- Add examples to command listings

### Success Criteria

- [ ] Tutorial covers all 4 phases
- [ ] Help integrated with `/craft:hub`
- [ ] Reference card created
- [ ] All examples work with craft projects

**Estimated:** 2 hours documentation

---

## Cross-Cutting Concerns

### 1. Project Type Detection

Extend existing `skills/ci/project-detector.md` with:

```python
CRAFT_CLAUDE_MD_TYPES = {
    "plugin": {
        "indicators": [".claude-plugin/plugin.json"],
        "template": "plugin-template.md",
        "sections": ["commands", "skills", "agents", "tests"]
    },
    "teaching": {
        "indicators": ["_quarto.yml", "course.yml", ".flow/teach-config.yml"],
        "template": "teaching-template.md",
        "sections": ["weeks", "assignments", "exams"]
    },
    "r-package": {
        "indicators": ["DESCRIPTION", "_pkgdown.yml"],
        "template": "r-package-template.md",
        "sections": ["R/", "tests/testthat/", "vignettes/"]
    },
    "mcp": {
        "indicators": ["mcp-server/", "src/index.ts"],
        "template": "mcp-template.md",
        "sections": ["tools", "resources", "prompts"]
    }
}
```

### 2. Integration with Existing Commands

**`/craft:check` enhancement:**

```bash
# Add CLAUDE.md validation step
if [[ -f CLAUDE.md ]]; then
    /craft:docs:claude-md:audit
fi
```

**`/craft:docs:update` coordination:**

```bash
# After updating other docs
/craft:docs:claude-md:update --dry-run
```

**`/craft:git:worktree` integration:**

```bash
# After finishing feature
/craft:docs:claude-md:update
```

### 3. Testing Infrastructure

Create comprehensive test suite:

```python
# tests/test_claude_md_integration.py
def test_craft_check_includes_claude_md_audit():
    """Verify /craft:check calls claude-md:audit."""

def test_docs_update_coordinates_with_claude_md():
    """Verify docs:update and claude-md:update work together."""

def test_worktree_finish_updates_claude_md():
    """Verify worktree finish includes CLAUDE.md update."""
```

Total test target: 55-69 tests across all phases

---

## Orchestration Strategy

### Mode: phase

Execute phases sequentially with checkpoints:

1. **Phase 1 checkpoint:** Update command working with tests passing
2. **Phase 2 checkpoint:** Audit + fix integrated with `/craft:check`
3. **Phase 3 checkpoint:** Scaffold + edit with templates created
4. **Phase 4 checkpoint:** Documentation complete, hub integration working

### Agent Delegation

- **Phase 1-3:** Use orchestrator-v2 for implementation waves
- **Phase 4:** Use docs-architect for tutorial/reference creation

### Testing Approach

Run tests after each phase:

```bash
python3 tests/test_claude_md_*.py
```

### Validation

Before completing each phase:

- [ ] All phase tests passing
- [ ] Dry-run mode working
- [ ] Documentation updated
- [ ] Integration points tested

---

## Timeline

| Phase | Days | Cumulative |
|-------|------|------------|
| Phase 1 | 1 | Day 1 |
| Phase 2 | 1-2 | Day 2-3 |
| Phase 3 | 2 | Day 4-5 |
| Phase 4 | 1 | Day 6 |
| **Total** | **6 days** | **(relaxed pace)** |

---

## Success Criteria (Overall)

- [ ] All 5 core commands ported (update, audit, fix, scaffold, edit)
- [ ] 55+ tests passing with 85%+ coverage
- [ ] Integration with `/craft:check`, `/craft:docs:update`, `/craft:git:worktree`
- [ ] 3 craft-specific templates created
- [ ] Tutorial and reference documentation complete
- [ ] Hub integration working
- [ ] All commands follow "Show Steps First" pattern

---

## Related Files

**Planning:**

- `/private/tmp/claude-501/-Users-dt-projects-dev-tools-craft/tasks/a659dde.output` - Full implementation plan

**Source Commands:**

- `~/.claude/commands/claude-md/update.md` (278 lines)
- `~/.claude/commands/claude-md/audit.md` (195 lines)
- `~/.claude/commands/claude-md/fix.md` (217 lines)
- `~/.claude/commands/claude-md/scaffold.md` (193 lines)
- `~/.claude/commands/claude-md/edit.md` (271 lines)
- `~/.claude/commands/claude-md/tutorial.md` (558 lines)
- `~/.claude/commands/claude-md/help.md` (430 lines)

**Current Craft:**

- `commands/docs/claude-md.md` (249 lines) - To be replaced
- `skills/ci/project-detector.md` - Extend with claude-md types
- `utils/help_file_validator.py` - Pattern reference

---

## Notes

- Keep local commands intact during port (don't remove until validated)
- Preserve local command logic, add craft-specific features incrementally
- Use existing craft patterns (dry-run, "Show Steps First", interactive prompts)
- Coordinate with existing craft documentation workflow
