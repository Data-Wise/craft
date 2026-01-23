# 🚧 WIP: Interactive Documentation Update System

**Status:** Work In Progress - Phase 1 Starting
**Branch:** `feature/docs-update-interactive`
**Target Version:** v2.7.0
**Created:** 2026-01-22

## 📋 Quick Status

| Item | Status |
|------|--------|
| **Spec** | ✅ Complete (docs/specs/SPEC-docs-update-interactive-2026-01-22.md, 1,634 lines) |
| **Brainstorm** | ✅ Complete (BRAINSTORM-docs-update-interactive-2026-01-22.md, 502 lines) |
| **Worktree** | ✅ Created (~/.git-worktrees/craft/feature-docs-update-interactive) |
| **Branch** | ✅ Created (feature/docs-update-interactive from dev) |
| **.STATUS** | ✅ Updated with implementation plan |
| **Phase 1: Core Workflow** | ⏳ Not Started |
| **Phase 2: GIF Integration** | ⏳ Not Started |
| **Phase 3: Lint & Tutorial** | ⏳ Not Started |
| **Phase 4: Help Files** | ⏳ Not Started |

## 🎯 Next Action

```bash
# Navigate to worktree
cd ~/.git-worktrees/craft/feature-docs-update-interactive

# Verify branch
git branch --show-current  # Should show: feature/docs-update-interactive

# Start Phase 1
# Create utils/docs_detector.py (category detection logic)
```

## 📚 Key Files

| File | Purpose | Location |
|------|---------|----------|
| **Spec** | Complete feature specification | docs/specs/SPEC-docs-update-interactive-2026-01-22.md |
| **Brainstorm** | Design decisions & requirements | BRAINSTORM-docs-update-interactive-2026-01-22.md |
| **WIP Tracker** | This file | WIP.md (in worktree root) |

## 🔄 Implementation Phases

### Phase 1: Core Workflow (Week 1, 8-10 hours)

**Goal:** Category detection + interactive prompts

- [ ] Create `utils/docs_detector.py` - Detection logic
- [ ] Implement category scanning functions:
  - [ ] `scan_version_refs()` - Find v2.6.0 references
  - [ ] `scan_command_counts()` - Count commands in docs
  - [ ] `scan_broken_links()` - Detect internal link issues
- [ ] Create `UpdateCategory` and `Change` data models
- [ ] Add interactive prompts with `AskUserQuestion`
- [ ] Implement `apply_category_updates()` function
- [ ] Create basic summary output
- [ ] Write unit tests (`tests/test_docs_detector.py`)
- [ ] Test with 2-3 categories before scaling

**Deliverables:**

- Detection working for 3 categories
- Interactive prompts functional
- Updates can be applied
- 90%+ test coverage

### Phase 2: GIF Integration (Week 2, 6-8 hours)

**Goal:** Detect outdated GIFs and regenerate

- [ ] Create `utils/gif_detector.py`
- [ ] Implement `detect_outdated_gifs()` - Compare commands in docs vs GIF metadata
- [ ] Create `generate_command_diff()` - Show OLD vs NEW command
- [ ] Integrate with `/craft:docs:demo` command
- [ ] Add `GIFUpdate` data model
- [ ] Handle recording errors gracefully
- [ ] Write tests (`tests/test_gif_detector.py`)

### Phase 3: Lint & Tutorial (Week 3, 8-10 hours)

**Goal:** Auto-trigger related workflows

- [ ] Auto-trigger `/craft:docs:lint` after updates
- [ ] Parse lint violations by file
- [ ] Add per-file lint prompts (fix vs skip)
- [ ] Implement `detect_tutorial_needs()` - Find gaps
- [ ] Add per-feature tutorial prompts
- [ ] Invoke `/tutorial-engineer` agent
- [ ] Create `TutorialTask` data model
- [ ] Write tests (`tests/test_workflow_integration.py`)

### Phase 4: Help Files (Week 4, 10-12 hours)

**Goal:** Comprehensive help file validation

- [ ] Create `utils/help_file_validator.py`
- [ ] Implement `scan_all_commands()` - Recursive search (commands/**/*.md)
- [ ] Implement `validate_yaml_structure()` - Required fields
- [ ] Implement `validate_yaml_arguments()` - Arguments array
- [ ] Implement `extract_flags_from_code()` - Code analysis
- [ ] Implement `compare_yaml_vs_code()` - Find missing/extra flags
- [ ] Implement `get_help_output()` - Execute --help
- [ ] Implement `parse_help_output()` - Parse CLI output
- [ ] Implement `validate_help_consistency()` - YAML vs --help
- [ ] Implement `suggest_yaml_frontmatter()` - Generate from template
- [ ] Implement `create_help_file()` - Create from HELP-PAGE-TEMPLATE.md
- [ ] Implement `validate_against_template()` - Template compliance
- [ ] Implement `group_help_issues_by_type()` - Batch prompts
- [ ] Create `HelpFileUpdate` and `HelpMismatch` data models
- [ ] Write comprehensive tests (`tests/test_help_validator.py`)
- [ ] Test with all 101+ commands

## 📊 Data Models

```python
@dataclass
class UpdateCategory:
    name: str                    # "Version References"
    changes: List[Change]        # List of changes in this category
    count: int                   # Number of changes
    priority: int                # For sorting (higher = more important)

@dataclass
class Change:
    file_path: str              # Path to file
    old_value: str              # Current value
    new_value: str              # Proposed value
    line_number: Optional[int]  # Line in file

@dataclass
class GIFUpdate:
    gif_path: str               # Path to GIF file
    old_command: str            # Original command
    new_command: str            # Updated command
    last_updated: datetime      # When GIF was last generated

@dataclass
class TutorialTask:
    feature_name: str           # Feature needing tutorial
    command: str                # Related command
    reason: str                 # Why tutorial is needed

@dataclass
class HelpFileUpdate:
    command_path: str           # e.g., commands/do.md
    command_name: str           # e.g., /craft:do
    issue_type: str             # missing_file, incomplete_yaml, etc.
    current_yaml: Dict          # Current YAML frontmatter
    suggested_yaml: Dict        # Suggested updates
    help_output: Optional[str]  # Output from --help
    help_mismatches: List[HelpMismatch]

@dataclass
class HelpMismatch:
    field: str                  # e.g., "description"
    yaml_value: str             # Value from YAML
    help_value: str             # Value from --help
    severity: str               # missing, mismatch, extra
```

## 🧪 Testing Strategy

**Unit Tests:**

- Category detection (version refs, counts, links)
- Interactive prompt flow
- Update application
- Help file validation (8 issue types)
- GIF detection
- Lint integration

**Integration Tests:**

- Full workflow (detect → prompt → apply → lint → tutorial)
- Help validation with real commands
- GIF regeneration
- Error handling

**Target Coverage:** 90%+

## ✅ Validation Checklist

Before marking Phase 1 complete:

- [ ] Category detection works for 3 categories
- [ ] Interactive prompts appear correctly
- [ ] User can approve/decline each category
- [ ] Updates apply successfully
- [ ] Summary shows what was changed
- [ ] Unit tests pass (90%+ coverage)
- [ ] No breaking changes to existing update command

Before marking complete (all phases):

- [ ] All 9 categories work
- [ ] GIF regeneration tested
- [ ] Lint workflow triggers correctly
- [ ] Tutorial detection works
- [ ] Help validation works for 101+ commands
- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Documentation complete
- [ ] PR created to `dev` branch

## 🚀 Ready to Merge Criteria

1. ✅ All validation checklist items complete
2. ✅ PR created to `dev` branch
3. ✅ CI/CD passing
4. ✅ Code review approved
5. ✅ No breaking changes
6. ✅ All 4 phases complete
7. ✅ 90%+ test coverage

## 📝 Commit Convention

Use conventional commits:

```bash
feat: add docs detector for category scanning
feat: add interactive prompts for update categories
feat: implement GIF regeneration workflow
feat: add help file validation system
test: add unit tests for docs detector
docs: update command docs with interactive mode
fix: handle missing help files gracefully
```

## 🆘 Need Help?

- Read: docs/specs/SPEC-docs-update-interactive-2026-01-22.md (full specification)
- Read: BRAINSTORM-docs-update-interactive-2026-01-22.md (design decisions)
- Run: `/craft:check` before committing
- Reference: Existing `/craft:docs:update` command for patterns

---

**Created:** 2026-01-22
**Last Updated:** 2026-01-22
