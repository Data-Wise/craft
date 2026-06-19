# SPEC: /craft:code:fewer-prompts — Curated Read-Only Bash Allowlist

**Status:** READY — implementation pending worktree
**Created:** 2026-06-19
**Author:** dt + Claude
**Motivation:** The `.claude/settings.json` allowlist is write-ops-only. Every read-only Bash call
(git status, grep, ls, cat, find…) triggers a permission prompt. This command installs a
craft-curated, security-reviewed safe set in one shot — distinct from the global
`/fewer-permission-prompts` skill, which scans past transcripts and misses day-one installs.

---

## Problem

Every craft session is interrupted by prompts for harmless read-only operations:
`git status`, `grep`, `ls`, `git log`, `git diff`, `git branch`, `find`, `wc`, `head`, `tail`.
The current allowlist in `.claude/settings.json` covers only write/mutating operations (git
restore, worktree add, gh release create, etc.). No read-only Bash calls are auto-allowed.

The global `/fewer-permission-prompts` skill exists but: (a) it's not wired into craft, (b) it
requires prior transcripts to scan, and (c) its output is not security-reviewed for craft's
specific threat model.

---

## Solution

A new craft command `/craft:code:fewer-prompts` that writes a curated allowlist of safe
read-only Bash patterns directly to `.claude/settings.json`. One command, permanent fix,
no transcript required.

---

## Command Interface

```
/craft:code:fewer-prompts [--dry-run] [--global] [--reset]
```

| Flag | Effect |
|---|---|
| _(none)_ | Write to `.claude/settings.json` in project root (default) |
| `--dry-run` | Preview what would be added/removed; no writes |
| `--global` | Write to `~/.claude/settings.json` instead |
| `--reset` | Remove craft-managed allowlist entries (undo) |

---

## Curated Safe Patterns

Grouped by safety tier. All patterns target the `Bash` tool's `command` input.

### Tier 1 — Unconditionally safe (always add)

```
git status
git log *
git diff *
git branch *
git show *
git shortlog *
git worktree list
git remote -v
git rev-parse *
ls *
ls -la *
find . *         (NOT find / or find ~)
grep *           (NOT grep -r / or grep -r ~)
wc *
head *
tail *
pwd
echo *
which *
python3 --version
node --version
```

### Tier 2 — Safe with extension guard (add with path constraint)

```
cat *.md
cat *.json
cat *.yaml
cat *.yml
cat *.sh
cat *.py
cat *.txt
cat *.toml
cat *.cfg
```

`cat` on arbitrary paths is excluded — a bare `cat` allow would permit reading
`~/.ssh/id_rsa`, `.env`, or credential files. Extension-scoped patterns keep the benefit
(reading source files) while blocking the risk.

### Tier 3 — Craft-specific read-only operations (add)

```
gh pr list *
gh issue list *
gh run list *
gh pr view *
gh issue view *
./scripts/validate-counts.sh
python3 tests/test_craft_plugin.py --list
mkdocs build --dry-run
```

### Excluded (never add)

| Pattern | Reason |
|---|---|
| `cat` (bare) | Can read secrets, credentials, SSH keys |
| `grep -r /` | Filesystem-wide scan, may surface sensitive files |
| `grep -r ~` | Home directory scan |
| `find /` | Same |
| `find ~` | Same |
| `gh secret list` | Lists secret names — info leak |
| `curl *` | Network requests, not read-only |
| `python3 *.py` (arbitrary) | Arbitrary code execution |

---

## Implementation Shape

### File: `commands/code/fewer-prompts.md`

New command file with standard craft frontmatter. Steps:

1. **Parse flags** (`--dry-run`, `--global`, `--reset`)
2. **Locate target settings file** (project `.claude/settings.json` or `~/.claude/settings.json`)
3. **Read existing settings** (create if absent)
4. **For `--reset`**: remove the `craft-managed-allowlist` block and exit
5. **Build allowlist entries** from the three tiers above
6. **For `--dry-run`**: display what would be added/removed, exit without writing
7. **Merge** — add entries under a `# craft-managed-allowlist` comment marker so `--reset` can
   identify and remove them cleanly. Preserve all existing entries.
8. **Write** settings file
9. **Confirm** — show count added and path written

### Settings Structure

Entries are written to `settings.json` under `permissions.allow`:

```json
{
  "permissions": {
    "allow": [
      "Bash(git status*)",
      "Bash(git log*)",
      "Bash(ls*)",
      "Bash(grep*)"
    ]
  }
}
```

Craft-managed entries are grouped with a leading comment (if the format supports it) or tracked
via a `craft_managed_allowlist` metadata key for `--reset` targeting.

### Idempotency

Running the command twice must produce the same result (no duplicate entries).
Running `--reset` followed by the command restores the full curated set.

---

## Security Decisions (Documented)

| Decision | Rationale |
|---|---|
| `cat` requires extension guard | Bare cat can read secrets/credentials |
| `grep` excludes `-r /` and `-r ~` | Prevents filesystem-wide sensitive file scans |
| `find` excludes `/` and `~` as root | Same — `.` is safe (project-scoped) |
| `gh` commands: list/view only | Mutating gh calls (pr merge, release create) stay gated |
| No `python3 *.py` | Arbitrary code; craft's specific scripts are listed individually |

---

## Tests

- `--dry-run` outputs expected tier 1/2/3 entries without modifying settings file
- Default run merges entries into `.claude/settings.json` without clobbering existing entries
- Idempotent: running twice produces identical settings file
- `--reset` removes craft-managed entries, leaves pre-existing entries intact
- `--global` writes to `~/.claude/settings.json` not project settings
- Excluded patterns (bare `cat`, `grep -r /`, `find ~`) are NOT in the written allowlist
- `cat` entries include only the extension-scoped Tier 2 patterns

---

## Acceptance Criteria

- [ ] After running the command, `git status`, `git log`, `ls`, `grep`, `find .`, `wc`, `head`,
  `tail`, `git diff`, `git branch` all run without permission prompts
- [ ] `cat` on `.md`, `.json`, `.yaml`, `.py`, `.sh` files runs without prompts
- [ ] `cat` on arbitrary paths (no extension or sensitive extension) still prompts
- [ ] `--dry-run` produces human-readable preview with entry count
- [ ] `--reset` cleanly removes all craft-managed entries
- [ ] `--global` targets `~/.claude/settings.json`
- [ ] Existing allowlist entries are preserved on merge

---

## Documentation & Discoverability

- [ ] Tutorial (`docs/tutorials/TUTORIAL-fewer-prompts.md`)
- [ ] Command reference (`docs/commands/code/fewer-prompts.md` via hub auto-discovery)
- [ ] REFCARD entry — one-liner in `docs/REFCARD.md` under Utilities
- [ ] Help hub — auto-surfaces via frontmatter; verify `/craft:hub` shows it
- [ ] Website — `mkdocs.yml` nav entry under Code; `docs/skills-agents.md` N/A (command, not skill)
- [ ] CHANGELOG `[Unreleased]` entry + count bumps (113 commands)
- [ ] `validate-counts.sh` + `docs-staleness-check.sh` clean after merge

---

## Sequencing

Standalone — no dependencies. Can start immediately on a `feature/fewer-prompts` worktree.
Bundle the stale parity-gate note fix in `commands/orchestrate.md` and #157 close into the
same PR for efficiency.

---

## Out of Scope

- Transcript-scanning (that's the global `/fewer-permission-prompts` skill's job)
- MCP tool allowlisting (different settings key; separate command if needed)
- Per-user profile management (v1 is all-or-nothing; `--reset` is the undo)
