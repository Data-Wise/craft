# SPEC: Enhanced `/done` — Memory Optimization + Settings Sync

**Topic:** Add to `/craft:workflow:done`: memory optimization, settings sync, and CLAUDE.md deepen  
**Depth:** max | **Focus:** feat | **Action:** save  
**Date:** 2026-06-23 | **Status:** APPROVED → ready for implementation

---

## Context

The `/craft:workflow:done` command already has:

- **Step 4** — CLAUDE.md sync (fixes stale command/skill/agent/test counts only)
- **Step 5** — Memory Capture (appends new learnings to MEMORY.md, no optimization)
- **Step 6** — Insights Capture (writes session facet JSON)

Both Step 4 and Step 5 are shallow. The memory system has grown to ~95 files; without periodic optimization, the index drifts (orphaned files, ghost entries, stale project memories, missing frontmatter). Settings sync is entirely absent from the workflow — drift between `~/.claude/settings.json` and project-level `.claude/settings.json` is silently ignored.

**Goal:** After every `/done` run, memory is clean and indexed; Claude settings drift is surfaced.

---

## What Changes

Two new steps inserted into `commands/workflow/done.md`:

| New Step | Position | Name | Closes |
|----------|----------|------|--------|
| **Step 4.5** | After CLAUDE.md sync | Claude Settings Sync | Settings drift |
| **Step 5.5** | After Memory Capture | Memory Optimize | Memory staleness |

Step 5 (Memory Capture) is also enhanced: after capturing new learnings, it now triggers the orphan/ghost audit.

---

## Step 4.5: Claude Settings Sync (NEW)

**Insert between existing Steps 4 and 5 in `commands/workflow/done.md`.**

```markdown
### Step 4.5: Claude Settings Sync

Read `~/.claude/settings.json` and project `.claude/settings.json` (if it exists).
Compare allowlist entries; detect drift.

Check `~/.claude/rules/*.md` modification times vs. last session timestamp.

Present findings:
- N allowlist entries in global missing from project (drift)
- N rules files modified since last session
- Suggest: "Run /craft:docs:claude-md:sync to pull in updated rules" if any changed

Do NOT auto-apply. Report only. User action on separate command.
```

**Key behaviors:**

- Read-only diff; never writes settings.json
- Skips gracefully if no project `.claude/settings.json` exists (not all projects have one)
- Shows rules diff in a collapsed section (details on request)
- Feeds into the interactive summary at Step 8 (user sees "2 settings drift, 1 rule updated")

---

## Step 5.5: Memory Optimize (NEW)

**Insert between existing Steps 5 and 6 in `commands/workflow/done.md`.**

```markdown
### Step 5.5: Memory Optimize

Scan `~/.claude/projects/<project-hash>/memory/`:

1. **Index audit**: Compare files in dir vs. entries in MEMORY.md
   - Orphaned files (in dir, not in index) → list them
   - Ghost entries (in index, path doesn't exist) → list them

2. **Frontmatter validation**: Every .md must have name, description, metadata.type
   - Missing fields → flag file, suggest fix

3. **Staleness check**: type=project memories older than 90 days
   - Flag as "may be stale" (not deleted automatically)

4. **Duplicate detection**: Files where description is near-identical (edit distance < 10%)
   - List suspected duplicates for manual review

5. **Index rebuild** (if user approves):
   - Sort by type: feedback → user → project → reference
   - Regenerate MEMORY.md with corrected links
   - Remove ghost entries

Interactive prompt:
  A) Rebuild index + remove ghosts
  B) Report only (default)
  C) Skip
```

**Key behaviors:**

- Duplicate detection is heuristic — flag for human review, never auto-merge
- Index rebuild is the only write operation; frontmatter fixes are NOT auto-applied
- Project hash resolution: derive from `$CWD` using same logic as `session-facet.sh`
- Graceful skip if memory dir doesn't exist (non-craft projects)

---

## Step 5 Enhancement (existing)

At the end of existing Step 5 (Memory Capture), after writing new learnings:

```markdown
After writing new entries, run a quick orphan check:
- Count .md files in memory/ dir
- Count entries in MEMORY.md
- If counts differ by >2, flag: "Memory index may be out of sync — Step 5.5 will audit"
```

---

## Files to Modify

### On `dev` (editing existing file — allowed)

- **`commands/workflow/done.md`** — insert Step 4.5 + Step 5.5 + enhance Step 5 orphan check

### On `dev` (new .md files — allowed)

- **`docs/tutorials/TUTORIAL-done-optimization.md`** — tutorial for the new steps
- **`docs/help/memory-optimization.md`** — reference for memory optimize behavior

### Requires worktree if added (new code files — NOT allowed on dev)

- `utils/memory_optimizer.py` — if logic grows complex enough to warrant extraction
- **Decision:** Start inline in `done.md` (bash/inline instructions). Extract to Python utility only if the logic exceeds ~40 lines or needs unit testing.

---

## Testing Plan

### Tier 1 — Structural (add to existing test file)

File: `tests/test_grill_command.py` or new `tests/test_done_workflow.py`

```python
def test_done_has_step_4_5():
    """Step 4.5 (Settings Sync) must exist in done.md."""
    done_md = (CRAFT_ROOT / "commands/workflow/done.md").read_text()
    assert "Step 4.5" in done_md
    assert "Settings Sync" in done_md or "settings sync" in done_md.lower()

def test_done_has_step_5_5():
    """Step 5.5 (Memory Optimize) must exist in done.md."""
    done_md = (CRAFT_ROOT / "commands/workflow/done.md").read_text()
    assert "Step 5.5" in done_md
    assert "Memory Optimize" in done_md or "memory optim" in done_md.lower()

def test_done_memory_optimize_behaviors():
    """Key behaviors must be spelled out: orphan, ghost, stale, duplicate."""
    done_md = (CRAFT_ROOT / "commands/workflow/done.md").read_text()
    for keyword in ["orphan", "ghost", "stale", "duplicate"]:
        assert keyword in done_md.lower(), f"Missing '{keyword}' in Step 5.5"

def test_done_settings_sync_is_readonly():
    """Settings sync must NOT auto-write settings.json."""
    done_md = (CRAFT_ROOT / "commands/workflow/done.md").read_text()
    # Verify step 4.5 says report-only
    step_section = done_md[done_md.find("Step 4.5"):]
    assert "report" in step_section[:500].lower() or "read-only" in step_section[:500].lower()
```

### Tier 2 — Integration (if `utils/memory_optimizer.py` is extracted)

File: `tests/test_memory_optimizer.py`

```python
# Only needed if Python utility is extracted from done.md

def test_orphan_detection(tmp_path):
    """Files in dir but missing from MEMORY.md are flagged as orphans."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    (memory_dir / "MEMORY.md").write_text("# Memory\n- nothing here\n")
    (memory_dir / "orphan.md").write_text("---\nname: orphan\n---\ncontent\n")
    result = audit_memory(memory_dir)
    assert "orphan.md" in result.orphans

def test_ghost_detection(tmp_path):
    """Entries in MEMORY.md pointing to missing files are flagged as ghosts."""
    memory_dir = tmp_path / "memory"
    memory_dir.mkdir()
    (memory_dir / "MEMORY.md").write_text(
        "# Memory\n- [Missing](missing.md) — gone\n"
    )
    result = audit_memory(memory_dir)
    assert "missing.md" in result.ghosts

def test_stale_project_memory(tmp_path):
    """type=project memories older than 90 days are flagged."""
    # ... mock file mtime > 90 days
    pass

def test_index_rebuild_sorts_by_type(tmp_path):
    """Rebuild produces feedback → user → project → reference order."""
    pass
```

### Tier 3 — Dogfood

Run `/craft:workflow:done` against the craft repo itself after implementing, verify:

- Step 4.5 output appears in terminal
- Step 5.5 audit runs without errors
- Memory dir file count matches MEMORY.md entry count post-rebuild

---

## Documentation & Discoverability

| Surface | File | Status |
|---------|------|--------|
| Tutorial | `docs/tutorials/TUTORIAL-done-optimization.md` | Create |
| Help reference | `docs/help/memory-optimization.md` | Create |
| Command help | Update `commands/workflow/done.md` frontmatter description | Edit |
| REFCARD | `docs/REFCARD.md` — add memory optimize shorthand | Edit |
| Hub auto-surface | No change — `/done` is already in hub via frontmatter | N/A |
| Website | `mkdocs.yml` nav → Workflow section | Edit |
| CHANGELOG | `[Unreleased]` section: add `feat(done): memory optimization + settings sync` | Edit |
| Count bumps | No new commands — no count cascade | N/A |
| validate-counts.sh | Run after changes; should be clean (no new command files) | Verify |

---

## Acceptance Criteria

- [ ] `/done` Step 4.5 reads `~/.claude/settings.json` and reports drift vs. project settings — never writes
- [ ] `/done` Step 5.5 audits memory dir: reports orphans, ghosts, stale project memories, duplicate suspects
- [ ] Step 5.5 interactive prompt offers index rebuild with Y/n/skip
- [ ] Index rebuild sorts entries by type (feedback → user → project → reference) and removes ghost entries
- [ ] Step 5 (existing) shows orphan count warning when dir file count ≠ MEMORY.md entry count
- [ ] All new behavior is graceful-skip when memory dir doesn't exist (other projects)
- [ ] `tests/test_done_workflow.py` passes: structural checks for Step 4.5 and Step 5.5
- [ ] `docs/tutorials/TUTORIAL-done-optimization.md` created
- [ ] `validate-counts.sh` clean
- [ ] `docs-staleness-check.sh` clean

---

## Implementation Order

1. **Edit `commands/workflow/done.md`** (on `dev`, existing file edit — no worktree needed):
   - Add Step 4.5 (Settings Sync) after Step 4
   - Add Step 5.5 (Memory Optimize) after Step 5, with full behavior specification
   - Enhance Step 5 with orphan count pre-check

2. **Add structural tests** (on `dev` — editing existing test file OR new .md, not new .py):
   - If adding to `test_grill_command.py` (existing file) → `dev` OK
   - If new `tests/test_done_workflow.py` → requires worktree (new .py file = new code file)
   - **Recommendation:** Add 4 assertions to existing `tests/test_craft_plugin.py` or `test_grill_command.py` (existing file, no worktree needed)

3. **Create doc files on `dev`** (new .md files — allowed on dev):
   - `docs/tutorials/TUTORIAL-done-optimization.md`
   - `docs/help/memory-optimization.md`

4. **Edit CHANGELOG, REFCARD, mkdocs.yml** (existing files on dev — allowed)

5. **Worktree only if:** logic is extracted to `utils/memory_optimizer.py` (new .py = new code file = needs `feature/done-memory-optimize` worktree)

---

## Known Risks

- **Memory dir path**: Must resolve project hash from CWD correctly. Pattern: `~/.claude/projects/<CWD-hash>/memory/`. If wrong hash, audit silently finds nothing. Mitigation: validate dir exists and contains MEMORY.md before proceeding; warn if not found.
- **Index rebuild safety**: Writing MEMORY.md must not corrupt existing links. Always write to temp file, diff, then atomic rename. Never in-place sed.
- **Settings.json privacy**: `settings.json` may contain tokens. Never log full content — log only key names and entry counts.
- **Dogfood correctness**: Step 5.5 runs against its own memory dir. Ensure it finds the craft project memory dir specifically (not a sibling project).

---

## Deferred / Out of Scope

- Auto-fix frontmatter in memory files (too risky without user confirmation — report only)
- Auto-merge duplicate memories (heuristic is fuzzy — flag for manual review only)  
- Sync settings.json to remote or backup (separate feature)
- Memory optimization as a standalone `/craft:workflow:memory-optimize` command (could extract later)

---

## Spec Path

`docs/specs/SPEC-done-memory-settings-2026-06-23.md`  
_(Written to plan file; will be saved to docs/specs/ during implementation session)_
