# Implementation Plan: Demo Dependency Management

**Branch:** `feature/demo-dependency-management`
**Worktree:** `~/.git-worktrees/craft/feature-demo-deps`
**Spec:** `docs/specs/SPEC-demo-dependency-management-2026-01-17.md`
**Target:** v1.23.0 → v1.26.0 (4 releases)
**Total Effort:** ~24 hours implementation + 8h testing + 4h docs = 36 hours

---

## Quick Start

```bash
# Navigate to worktree
cd ~/.git-worktrees/craft/feature-demo-deps

# Start Claude Code
claude

# Check current phase
cat IMPLEMENTATION-PLAN.md

# Run tests
python3 tests/test_craft_plugin.py
```

---

## Phase 1: Core Dependency Checking (v1.23.0)

**Duration:** 6 hours
**Status:** Not started

### Objectives
- ✅ Add dependency declarations to command frontmatter
- ✅ Implement tool detection and validation
- ✅ Add session-level caching
- ✅ Create `--check` flag with status table
- ✅ Implement graceful degradation

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `commands/docs/demo.md` | Modify | Add dependencies YAML frontmatter |
| `scripts/dependency-manager.sh` | Create | Core dependency management logic |
| `scripts/tool-detector.sh` | Create | Tool detection utilities |
| `scripts/session-cache.sh` | Create | Session-level caching |
| `tests/test_dependency_checking.py` | Create | Test suite for Phase 1 |

### Implementation Steps

1. **Add frontmatter dependencies (1h)**
   ```yaml
   dependencies:
     asciinema:
       required: true
       methods: ["asciinema"]
       install: { brew: "asciinema", apt: "asciinema" }
       version: { min: "2.0.0", check: "asciinema --version | grep -oE '[0-9.]+'" }
   ```

2. **Create dependency-manager.sh (2h)**
   - `check_dependencies()` - Main entry point
   - `detect_tool()` - Check if tool is installed
   - `get_cached_status()` - Retrieve cached results
   - `store_cache()` - Store results in session cache

3. **Create tool-detector.sh (1h)**
   - `detect_asciinema()`
   - `detect_agg()`
   - `detect_gifsicle()`
   - `detect_vhs()`

4. **Implement --check flag (1.5h)**
   - Parse frontmatter dependencies
   - Run detection for all tools
   - Generate ASCII status table
   - Exit with code 0 (OK) or 1 (missing)

5. **Implement graceful degradation (0.5h)**
   - If asciinema/agg missing → suggest VHS
   - Update command flow to handle fallback

6. **Write tests (1h)**
   - Test tool detection logic
   - Test cache hit/miss scenarios
   - Test --check output formatting

### Deliverables

- [x] `commands/docs/demo.md` updated with dependencies
- [x] `scripts/dependency-manager.sh` created (491 lines)
- [x] `scripts/tool-detector.sh` created (297 lines)
- [x] `scripts/session-cache.sh` created (211 lines)
- [x] `scripts/test-demo-check.sh` created (integration tests)
- [x] All scripts made executable
- [x] All integration tests passing (6/6)
- [x] Documentation added to demo.md
- [ ] Commit: `feat: add core dependency checking to demo command`

**Phase 1 Complete:** 999 lines of production code, fully tested and documented.

---

## Phase 2: Auto-Installation (v1.24.0)

**Duration:** 8 hours
**Status:** Not started

### Objectives
- ✅ Implement multi-strategy installer (brew, cargo, binary)
- ✅ Add informed consent prompts
- ✅ Create `--fix` flag
- ✅ Implement retry with fallbacks
- ✅ Add installation logging

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `scripts/dependency-installer.sh` | Create | Installation orchestration |
| `scripts/installers/brew-installer.sh` | Create | Homebrew installation |
| `scripts/installers/cargo-installer.sh` | Create | Cargo installation |
| `scripts/installers/binary-installer.sh` | Create | Binary download |
| `scripts/consent-prompt.sh` | Create | User consent UI |
| `commands/docs/demo.md` | Modify | Add installation workflow |
| `tests/test_dependency_installation.py` | Create | Installation tests |

### Implementation Steps

1. **Create installer framework (2h)**
   - `dependency-installer.sh` - Main installer
   - `install_tool(tool_name, method)` - Install single tool
   - `try_installation_methods()` - Fallback chain
   - Platform detection (macOS/Linux)

2. **Implement brew installer (1h)**
   - Check if brew installed
   - Run `brew install <package>`
   - Verify installation success

3. **Implement cargo installer (1.5h)**
   - Check if cargo installed
   - Run `cargo install --git <repo>`
   - Handle compilation errors

4. **Implement binary installer (1.5h)**
   - Download from GitHub releases
   - Detect architecture (x86_64, arm64)
   - Make executable and move to PATH

5. **Create consent prompts (1h)**
   - Show tool to install
   - Show installation method
   - Show estimated time
   - Get Y/N/S (Skip) response

6. **Implement --fix flag (1h)**
   - Detect missing tools
   - Prompt for consent
   - Install with fallback chain
   - Update cache

7. **Add installation logging (0.5h)**
   - Log to `.craft/logs/install-<timestamp>.log`
   - Track success/failure per tool

8. **Write tests (1.5h)**
   - Mock installation methods
   - Test fallback chain
   - Test consent flow

### Deliverables

- [ ] `scripts/dependency-installer.sh` created
- [ ] Installer strategies implemented (brew, cargo, binary)
- [ ] `--fix` flag working
- [ ] Consent prompts functional
- [ ] Installation logs generated
- [ ] All tests passing
- [ ] Commit: `feat: add auto-installation with consent prompts`

---

## Phase 3: Batch Conversion (v1.25.0)

**Duration:** 4 hours
**Status:** Not started

### Objectives
- ✅ Implement `--convert` flag for single files
- ✅ Implement `--batch` flag for bulk processing
- ✅ Add progress indicators
- ✅ Add size reporting
- ✅ Add `--force` flag

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `scripts/batch-convert.sh` | Create | Batch conversion logic |
| `scripts/convert-cast.sh` | Create | Single .cast → .gif conversion |
| `commands/docs/demo.md` | Modify | Add --convert and --batch flags |
| `docs/GIF-REGENERATION-CHECKLIST.md` | Modify | Add batch mode instructions |

### Implementation Steps

1. **Create convert-cast.sh (1h)**
   - `convert_single(cast_file, output_gif)` - Convert one file
   - Run `agg` with standard settings
   - Run `gifsicle` for optimization
   - Return success/failure + file size

2. **Implement --convert flag (0.5h)**
   - Parse file path argument
   - Call `convert_single()`
   - Show progress and size

3. **Create batch-convert.sh (1.5h)**
   - Find all `.cast` files in `docs/demos/` and `docs/gifs/`
   - Skip existing `.gif` files (unless `--force`)
   - Process sequentially with progress
   - Show progress bar: `[████████░░] 8/11 (73%)`

4. **Add size reporting (0.5h)**
   - Track total size before/after
   - Show size reduction percentage
   - Show per-file sizes

5. **Update documentation (0.5h)**
   - Add batch mode to checklist
   - Update examples

### Deliverables

- [ ] `scripts/batch-convert.sh` created
- [ ] `scripts/convert-cast.sh` created
- [ ] `--convert` flag working
- [ ] `--batch` flag working
- [ ] Progress indicators functional
- [ ] Size reporting accurate
- [ ] Documentation updated
- [ ] Commit: `feat: add batch conversion for .cast files`

---

## Phase 4: Advanced Features (v1.26.0)

**Duration:** 6 hours
**Status:** Not started

### Objectives
- ✅ Implement health check validation
- ✅ Add version checking with warnings
- ✅ Implement repair functionality
- ✅ Add JSON output (`--check --json`)
- ✅ Create CI/CD integration
- ✅ Write comprehensive guide

### Files to Create/Modify

| File | Action | Purpose |
|------|--------|---------|
| `scripts/health-check.sh` | Create | Health validation |
| `scripts/version-check.sh` | Create | Version validation |
| `scripts/repair-tools.sh` | Create | Repair broken installs |
| `commands/docs/demo.md` | Modify | Add JSON output |
| `.github/workflows/validate-dependencies.yml` | Create | CI integration |
| `docs/reference/dependency-management.md` | Create | Complete guide |

### Implementation Steps

1. **Create health-check.sh (1.5h)**
   - `health_check_asciinema()` - Run `asciinema --help`
   - `health_check_agg()` - Run `agg --help`
   - `health_check_gifsicle()` - Run `gifsicle --help`
   - Return pass/fail per tool

2. **Create version-check.sh (1h)**
   - Parse version from tool output
   - Compare against minimum version
   - Return OK/OUTDATED/UNPARSEABLE

3. **Implement repair functionality (1.5h)**
   - Detect broken/outdated tools
   - Reinstall via installer
   - Validate post-repair

4. **Add JSON output (1h)**
   - `--check --json` flag
   - Output structured JSON:
     ```json
     {
       "status": "missing",
       "tools": [
         {"name": "asciinema", "installed": true, "version": "2.3.0", "health": "ok"},
         {"name": "agg", "installed": false, "version": null, "health": "n/a"}
       ]
     }
     ```

5. **Create CI workflow (0.5h)**
   - Run `--check` in CI
   - Fail if dependencies missing
   - Optional: Auto-install in CI

6. **Write guide (0.5h)**
   - Overview of dependency system
   - Flag reference
   - Troubleshooting
   - CI integration examples

### Deliverables

- [ ] `scripts/health-check.sh` created
- [ ] `scripts/version-check.sh` created
- [ ] `scripts/repair-tools.sh` created
- [ ] JSON output working
- [ ] CI workflow created
- [ ] Guide written
- [ ] All tests passing
- [ ] Commit: `feat: add health checks, version validation, and JSON output`

---

## Testing Strategy

### Unit Tests
```bash
# Test individual functions
python3 -m pytest tests/test_dependency_checking.py::test_detect_asciinema
python3 -m pytest tests/test_dependency_installation.py::test_brew_installer
```

### Integration Tests
```bash
# Test full workflows
python3 -m pytest tests/test_dependency_checking.py -k integration
```

### E2E Tests
```bash
# Test on clean environment (GitHub Actions)
.github/workflows/test-dependencies.yml
```

### Manual Testing Checklist

- [ ] Run `--check` on system with all tools
- [ ] Run `--check` on system with missing tools
- [ ] Run `--fix` and verify installation
- [ ] Run `--batch` on 11 GIF checklist
- [ ] Test graceful degradation (remove asciinema)
- [ ] Verify cache hit/miss behavior
- [ ] Test on macOS and Linux

---

## Git Workflow

### Commits
```bash
# Phase 1
git add commands/docs/demo.md scripts/dependency-*.sh tests/
git commit -m "feat: add core dependency checking to demo command

- Add dependencies section to command frontmatter
- Implement tool detection and validation
- Add session-level caching
- Create --check flag with ASCII table
- Implement graceful degradation (asciinema → VHS)

Closes #XXX"

# Phase 2
git commit -m "feat: add auto-installation with consent prompts

- Implement multi-strategy installer (brew, cargo, binary)
- Add informed consent prompts
- Create --fix flag
- Implement retry with fallback methods
- Add installation logging

Closes #XXX"

# Phase 3
git commit -m "feat: add batch conversion for .cast files

- Implement --convert flag for single files
- Implement --batch flag for bulk processing
- Add progress indicators
- Add size reporting
- Add --force flag

Closes #XXX"

# Phase 4
git commit -m "feat: add health checks, version validation, and JSON output

- Implement health check validation
- Add version checking with warnings
- Implement repair functionality
- Add JSON output (--check --json)
- Create CI/CD integration
- Write dependency management guide

Closes #XXX"
```

### PR Creation
```bash
# After all phases complete
cd /Users/dt/.git-worktrees/craft/feature-demo-deps
gh pr create --base dev --title "feat: Add dependency management to demo command (v1.23.0-v1.26.0)" --body "$(cat <<'EOF'
## Summary
Embeds dependency checking, installation, and management directly into `/craft:docs:demo` command to eliminate manual setup friction when creating GIF demos.

## Changes
- **Phase 1 (v1.23.0):** Core dependency checking with --check flag
- **Phase 2 (v1.24.0):** Auto-installation with informed consent
- **Phase 3 (v1.25.0):** Batch conversion with --batch flag
- **Phase 4 (v1.26.0):** Health checks, version validation, JSON output

## New Flags
- `--check` - Validate dependencies and show status
- `--fix` - Auto-install/repair missing or broken dependencies
- `--convert` - Convert existing .cast files to .gif
- `--batch` - Process multiple recordings in one command
- `--force` - Overwrite existing files in batch mode
- `--json` - Output machine-readable JSON

## Testing
- [ ] All unit tests passing
- [ ] Integration tests passing
- [ ] Manual testing on macOS
- [ ] Manual testing on Linux (CI)
- [ ] Batch conversion tested on 11 GIFs

## Documentation
- [x] Spec: docs/specs/SPEC-demo-dependency-management-2026-01-17.md
- [x] Implementation plan: IMPLEMENTATION-PLAN.md
- [x] Guide: docs/reference/dependency-management.md
- [x] Updated: commands/docs/demo.md
- [x] Updated: docs/GIF-REGENERATION-CHECKLIST.md

## Breaking Changes
None - all new flags are additive

## Spec Reference
See: docs/specs/SPEC-demo-dependency-management-2026-01-17.md

🤖 Generated with [Claude Code](https://claude.com/claude-code)
EOF
)"
```

---

## Useful Commands

```bash
# Navigate to worktree
cd ~/.git-worktrees/craft/feature-demo-deps

# Check status
git status
git branch --show-current

# Run tests
python3 tests/test_craft_plugin.py
python3 -m pytest tests/ -v

# Test demo command
/craft:docs:demo --check
/craft:docs:demo --fix
/craft:docs:demo --batch

# Switch back to main repo
cd /Users/dt/projects/dev-tools/craft

# List all worktrees
git worktree list

# Remove worktree when done
git worktree remove ~/.git-worktrees/craft/feature-demo-deps
```

---

## Notes

- Work incrementally: finish Phase 1 completely before starting Phase 2
- Commit after each phase
- Run tests before moving to next phase
- Update this plan as needed
- Reference spec frequently: `docs/specs/SPEC-demo-dependency-management-2026-01-17.md`

---

**Good luck with implementation!** 🚀
