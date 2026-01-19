# 🚧 Work In Progress: --orch Flag Integration

**Status**: Planning Complete, Ready for Implementation
**Branch**: `feature/orch-flag-integration`
**Target Version**: v2.5.0
**Created**: 2026-01-19

## 📋 Quick Status

| Item | Status |
| --- | --- |
| **Spec** | ✅ Complete (`docs/specs/SPEC-orch-flag-integration-2026-01-19.md`) |
| **Implementation Plan** | ✅ Complete (`IMPLEMENTATION.md`) |
| **Worktree** | ✅ Created (`~/.git-worktrees/craft/feature-orch-flag-integration`) |
| **Branch** | ✅ Created (`feature/orch-flag-integration` from `dev`) |
| **.STATUS** | ✅ Updated with plan and branch info |
| **Phase 1: Infrastructure** | ⏳ Not Started |
| **Phase 2: Commands** | ⏳ Not Started |
| **Phase 3: Testing** | ⏳ Not Started |
| **Phase 4: Documentation** | ⏳ Not Started |

## 🎯 Next Action

```bash
# Navigate to worktree
cd ~/.git-worktrees/craft/feature-orch-flag-integration

# Verify branch
git branch --show-current  # Should show: feature/orch-flag-integration

# Start Phase 1
# Create utils/orch_flag_handler.py (see IMPLEMENTATION.md)
```

## 📚 Key Files

| File | Purpose | Location |
| --- | --- | --- |
| **Spec** | Complete feature specification | `docs/specs/SPEC-orch-flag-integration-2026-01-19.md` |
| **Implementation Plan** | Step-by-step guide | `IMPLEMENTATION.md` (in worktree root) |
| **WIP Tracker** | This file | `WIP.md` (in worktree root) |

## 🔄 Implementation Workflow

### Phase 1: Core Infrastructure (2-3 hours)

- [ ] Create `utils/orch_flag_handler.py`
- [ ] Implement `handle_orch_flag()`
- [ ] Implement `prompt_user_for_mode()`
- [ ] Implement `show_orchestration_preview()`
- [ ] Implement `spawn_orchestrator()`
- [ ] Update `utils/complexity_scorer.py` with mode mapping
- [ ] Write unit tests (`tests/test_orch_flag_handler.py`)
- [ ] Verify all tests passing

### Phase 2: Command Updates (3-4 hours)

- [ ] Update `/craft:do` (frontmatter + implementation + examples)
- [ ] Update `/craft:workflow:brainstorm` (with category integration)
- [ ] Update `/craft:check`
- [ ] Update `/craft:docs:sync`
- [ ] Update `/craft:ci:generate`

### Phase 3: Testing (2-3 hours)

- [ ] Create `tests/test_integration_orch_flag.py`
- [ ] Test all flag combinations
- [ ] Test error handling
- [ ] Test mode prompt interaction
- [ ] Verify coverage ≥ 95%

### Phase 4: Documentation (1-2 hours)

- [ ] Create `docs/guide/orch-flag-usage.md`
- [ ] Update CLAUDE.md with --orch info
- [ ] Update VERSION-HISTORY.md with v2.5.0
- [ ] Update all 5 command docs with examples

## ✅ Validation Checklist

Before marking as complete:

- [ ] All unit tests pass
- [ ] All integration tests pass
- [ ] Coverage ≥ 95% for core handler
- [ ] Coverage ≥ 90% for command integrations
- [ ] Dry-run mode works for all commands
- [ ] Mode prompt appears correctly
- [ ] Invalid modes show clear errors
- [ ] `--orch` works with `--dry-run`
- [ ] `--orch` works with other flags (e.g., `-C`)
- [ ] Documentation builds without errors

## 🚀 Ready to Merge Criteria

1. ✅ All validation checklist items complete
2. ✅ PR created to `dev` branch
3. ✅ CI/CD passing
4. ✅ Code review approved
5. ✅ No breaking changes
6. ✅ All acceptance criteria met

## 📝 Commit Convention

Use conventional commits:

```bash
feat: add orchestration flag handler
test: add unit tests for orch flag
docs: update command docs with --orch examples
fix: handle invalid mode gracefully
```

## 🆘 Need Help?

- Read: `IMPLEMENTATION.md` (detailed step-by-step guide)
- Read: `docs/specs/SPEC-orch-flag-integration-2026-01-19.md` (full specification)
- Run: `/craft:check` before committing
- Ask: Questions in PR or during implementation

---

**Created**: 2026-01-19
**Last Updated**: 2026-01-19
