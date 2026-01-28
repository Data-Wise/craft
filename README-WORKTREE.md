# Feature Branch: Demo Dependency Management

**Quick Start:**

```bash
cd ~/.git-worktrees/craft/feature-demo-deps
claude
```

## What This Branch Does

Implements dependency management for `/craft:docs:demo` command:

- `--check` - Validate dependencies
- `--fix` - Auto-install missing tools
- `--batch` - Convert multiple .cast files
- `--convert` - Convert single .cast file

## Files to Reference

| File | Purpose |
|------|---------|
| `IMPLEMENTATION-PLAN.md` | Complete 4-phase implementation plan |
| `docs/specs/SPEC-demo-dependency-management-2026-01-17.md` | Full specification |
| `commands/docs/demo.md` | Command to modify |

## Current Phase

**Phase 1: Core Dependency Checking** ✅ COMPLETE

- [x] Add dependencies frontmatter
- [x] Create dependency-manager.sh (491 lines)
- [x] Create tool-detector.sh (297 lines)
- [x] Create session-cache.sh (211 lines)
- [x] Implement --check flag
- [x] Add session caching
- [x] Integration tests (6/6 passing)
- [x] Documentation updates

**Total:** 999 lines of production code

**Next:** Phase 2 - Auto-Installation with `--fix` flag

## Todo List

See full todo list in Claude Code session or run:

```bash
cat IMPLEMENTATION-PLAN.md | grep "^###"
```

## Testing

```bash
# Run all tests
python3 tests/test_craft_plugin.py

# Run specific test
python3 -m pytest tests/test_dependency_checking.py -v
```

## Branch Info

- **Branch:** feature/demo-dependency-management
- **Base:** dev
- **Target:** v1.23.0 → v1.26.0
- **Effort:** ~36 hours total
- **Created:** 2026-01-17

## Links

- Spec: `/Users/dt/projects/dev-tools/craft/docs/specs/SPEC-demo-dependency-management-2026-01-17.md`
- Main repo: `/Users/dt/projects/dev-tools/craft`
