# Tutorial: Session Wrap with Memory Optimization & Settings Sync

**Commands covered:** `/craft:workflow:done`  
**Added in:** v2.49.0  
**Time:** ~10 minutes

---

## Overview

When you run `/done` at the end of a session, two new steps now run automatically:

1. **Step 1.10.5 — Claude Settings Sync**: detects drift between your global `~/.claude/settings.json` and the project's `.claude/settings.json`, and flags rules files that changed since the last session.

2. **Step 1.12 — Memory Optimize**: audits your project's memory directory for orphaned files, ghost index entries, stale project memories, and suspected duplicate entries — then offers to rebuild the index.

---

## Step-by-step

### 1. Run `/done` as usual

```
/done
```

The existing steps run first (CLAUDE.md sync, memory capture, insights). Then you'll see the new output.

### 2. Settings Sync output (Step 1.10.5)

If drift is found between your global and project settings, you'll see:

```
⚙️  SETTINGS CHECK:
  Allowlist: 3 entries in global not in project settings
  Rules updated since last session: response-style.md
  → Run /craft:docs:claude-md:sync to pull in updated rules
```

**No output = no drift.** The step is silent when everything is in sync.

Settings sync is **read-only** — it never modifies `settings.json`. It reports; you decide what to do.

### 3. Memory Optimize output (Step 1.12)

After memory capture, the audit runs:

```
🧹 MEMORY AUDIT (95 files, 92 index entries):
  Orphans: 3  (files in dir, missing from index)
  Ghosts:  1  (index entries pointing to missing files)
  Stale:   2  (type=project, >90 days since last edit)
  Dupes:   0  suspected pairs

  A) Rebuild index + remove ghosts  (Recommended if orphans > 0)
  B) Report only
  C) Skip
```

**No output = clean.** The step is silent when 0 issues are found.

### 4. Choose an action for the memory audit

| Option | Effect |
|--------|--------|
| **A) Rebuild** | Writes a new MEMORY.md (sorted by type: feedback → user → project → reference). Removes ghost entries. Adds orphaned files to the index using their `description:` frontmatter. **Never deletes files.** |
| **B) Report only** | Shows the list without changing anything. You can fix manually. |
| **C) Skip** | Skips the interactive prompt entirely this session. |

### 5. Index rebuild safety

The rebuild writes to a temp file first, validates the entry count, then atomically renames it over the existing `MEMORY.md`. If the sanity check fails (the new count diverges by more than 3 entries), the original file is left untouched and you'll see an error.

---

## Opt-out

Both new steps respect opt-out env vars if you need to skip them:

```bash
SKIP_SETTINGS_SYNC=1 /done      # skip settings drift check
SKIP_MEMORY_OPTIMIZE=1 /done    # skip memory audit
```

---

## Common questions

**Why do I have orphaned memory files?**  
Orphans happen when you write a memory file but forget to add it to `MEMORY.md`, or when `MEMORY.md` is synced between sessions and the new files haven't been indexed yet. The rebuild (Option A) fixes this automatically.

**Why does the settings drift check exist?**  
The global `~/.claude/settings.json` accumulates allowlist entries as you add permissions across projects. These don't automatically propagate to project-level settings files. The check surfaces the gap so you can decide whether to sync them.

**What's a "ghost" entry?**  
A ghost entry is a line in `MEMORY.md` that links to a `.md` file that no longer exists in the memory directory. This can happen after manual cleanup. The rebuild removes ghost entries; it never recreates the missing files.

---

## See also

- [Memory Optimization Reference](../help/memory-optimization.md)
- [CLAUDE.md Sync tutorial](claude-md-workflows.md)
- `/craft:workflow:done` command reference
