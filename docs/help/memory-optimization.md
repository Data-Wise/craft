# Memory Optimization Reference

**Feature:** `/done` Step 1.12 — Memory Optimize  
**Added in:** v2.49.0

---

## What it does

The memory optimize step audits `~/.claude/projects/<project-hash>/memory/` for four classes of issues:

| Issue class | Definition | Action |
|-------------|-----------|--------|
| **Orphan** | `.md` file in dir but not referenced in `MEMORY.md` | Listed; optionally added to index |
| **Ghost** | `MEMORY.md` entry whose linked file doesn't exist | Listed; removed on rebuild |
| **Stale** | `metadata.type: project` file not edited in > 90 days | Flagged for manual review |
| **Duplicate suspect** | Two files whose `description:` values share > 80% word overlap (Jaccard) | Flagged for manual review |

---

## Index rebuild

When you choose **Option A (Rebuild)**, the step:

1. Reads all `.md` files in the memory dir (excluding `MEMORY.md` itself)
2. Reads `MEMORY.md` and builds a map of linked filenames
3. Computes orphans and ghosts
4. Writes a new `MEMORY.md` to a temp file with:
   - All valid existing entries (sorted: `feedback` → `user` → `project` → `reference`)
   - Ghost entries removed
   - Orphan files added (auto-generated one-line entries from their `description:` frontmatter)
5. Validates the new entry count (must not diverge by more than 3 from expected)
6. Atomically renames the temp file over `MEMORY.md`

**What it never does:**

- Never deletes memory files (only index entries)
- Never modifies frontmatter in existing files
- Never merges suspected duplicates
- Never writes if the entry count sanity check fails

---

## Frontmatter requirements

Every memory file must have:

```markdown
---
name: short-kebab-case-slug
description: one-line summary used to decide relevance in future conversations
metadata:
  type: user | feedback | project | reference
---
```

Files missing any of these fields are flagged during the audit. They are NOT auto-fixed — fix them manually and re-run the step.

---

## Project hash resolution

The memory directory path is derived from the current working directory:

```
~/.claude/projects/<CWD-hash>/memory/
```

The step uses a fuzzy match on the trailing 30 characters of the encoded CWD path (the same logic used by `session-facet.sh`). If no matching directory is found, the step skips silently.

---

## Opt-out

```bash
SKIP_MEMORY_OPTIMIZE=1 /done    # skip for this session only
```

---

## Triggers

Step 1.12 runs unconditionally after Step 1.11 (Memory Capture) unless opted out. If the Step 1.11 orphan pre-check detects a count delta > 2, a warning is surfaced and Step 1.12 is explicitly flagged as the resolution.

---

## Related

- [Tutorial: Session Wrap with Memory Optimization](../tutorials/TUTORIAL-done-optimization.md)
- [Memory system overview](https://data-wise.github.io/craft/)
