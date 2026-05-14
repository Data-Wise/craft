---
name: claude-md-lifecycle
description: This skill should be used when the user asks to "create CLAUDE.md", "scaffold CLAUDE.md", "sync CLAUDE.md", "update CLAUDE.md", "audit CLAUDE.md", "fix CLAUDE.md", "optimize CLAUDE.md", "edit CLAUDE.md sections", or otherwise wants to manage the CLAUDE.md lifecycle (init, sync, edit). Covers project-local and global (`~/.claude/CLAUDE.md`) files. For applying suggestions from the /insights report specifically, use the `insights-apply` skill instead.
---

# CLAUDE.md Lifecycle

End-to-end management of CLAUDE.md files: scaffold from project-type templates, sync with project state (audit + fix + optimize), and edit sections interactively. Targets both project-local `CLAUDE.md` and global `~/.claude/CLAUDE.md`.

## When to Use

- User asks to **create** a CLAUDE.md from scratch (new project, missing file)
- User asks to **sync / update / audit / fix / optimize** an existing CLAUDE.md
- User asks to **edit** a specific section with preview and validation
- File is over the 150-line budget and needs trimming via pointer architecture
- Version/count drift detected between CLAUDE.md and project sources (`plugin.json`, `DESCRIPTION`, etc.)

## When NOT to Use

| Situation | Use Instead |
|---|---|
| Applying suggestions from `/insights` report to global CLAUDE.md | `insights-apply` skill |
| Classifying which doc types a feature needs | `doc-classifier` skill |
| Generating release notes / CHANGELOG | `changelog-automation` skill |

The boundary with `insights-apply`: that skill is the **rule-applier** for one specific source (the `/insights` report → global CLAUDE.md). This skill is the **editor** for the full lifecycle (init/sync/edit) of any CLAUDE.md. They share the underlying sync pipeline (`utils/claude_md_sync.py`) but enter it from different intents.

## Three Phases

### Phase 1: Init (scaffold)

Create a new CLAUDE.md from a project-type template (lean, < 150 lines, pointer architecture).

| Step | Action |
|---|---|
| 1 | Detect project type: `plugin` (`.claude-plugin/plugin.json`), `teaching` (`_quarto.yml` + `course.yml`), `r-package` (`DESCRIPTION`) |
| 2 | Scan metadata: version, counts (commands/skills/agents), test count, repo URL, git branch |
| 3 | Populate lean template with discovered values |
| 4 | Show preview with line count vs budget |
| 5 | Create file after confirmation; run post-creation audit |

**Flags:** `--type`, `--force` (overwrite), `--dry-run`, `--global` (target `~/.claude/CLAUDE.md`)

**Refusal:** if file exists and `--force` not set, redirect to sync.

### Phase 2: Sync (update + audit + fix + optimize)

Four-phase pipeline against an existing CLAUDE.md.

| Phase | What | Trigger |
|---|---|---|
| Detect | Project type, version source | always |
| Update Metrics | Version, counts, tests, docs% | always |
| Audit | 5 checks + anti-pattern + budget | always |
| Fix | Auto-fix fixable issues | `--fix` |
| Optimize | Enforce budget, move bloat to detail files | `--optimize` |

**Anti-patterns blocked** (refuse to add to CLAUDE.md):

| Pattern | Redirect To |
|---|---|
| Release notes (`### v\d+`) | `docs/VERSION-HISTORY.md` |
| Diffstats (`Files Changed`) | delete |
| "What Shipped" / "Merged PR" | `docs/VERSION-HISTORY.md` |
| "Status: Complete" / `Released ✅` | `docs/VERSION-HISTORY.md` |
| Phase details (`### Phase N`) | detail file |

**Budget resolution order:** `.claude-plugin/config.json` → `package.json` `claudeMd.budget` → default 150. Never store in `plugin.json` (strict schema rejects it).

**Sections:** `--section status|commands|testing|all` (default all).

### Phase 3: Edit (interactive section editing)

Open one or more sections in an external editor with TODO hints, validate after.

| Step | Action |
|---|---|
| 1 | Parse sections (H2 headers + horizontal rules) |
| 2 | Display section table with line ranges |
| 3 | User picks section (or `all`) |
| 4 | Insert `<!-- TODO: ... -->` hints (unless `--no-hints`) |
| 5 | Open in editor (default `ia`, also `code` / `sublime` / `cursor`) |
| 6 | Wait for user to say "done" |
| 7 | Re-read, strip TODO comments |
| 8 | Run post-edit audit (unless `--no-validate`) |
| 9 | Show diff preview before applying |

**iA Writer integration** (default): open via AppleScript

```bash
osascript -e 'tell application "iA Writer"
    activate
    open POSIX file "/path/to/CLAUDE.md"
end tell'
```

## Pointer Architecture

The 150-line budget is enforced by **pointing out of CLAUDE.md** rather than inlining detail:

```markdown
## References

-> Release history: [VERSION-HISTORY.md](docs/VERSION-HISTORY.md)
-> Architecture: [ARCHITECTURE.md](docs/ARCHITECTURE.md)
-> Contributing: [CONTRIBUTING.md](CONTRIBUTING.md)
-> Command reference: [COMMANDS.md](docs/COMMANDS.md)
```

Claude Code follows markdown links naturally — keep CLAUDE.md as an index, not an encyclopedia.

## Global vs Project Targeting

All three phases accept `--global` / `-g`:

```python
if "--global" in args or "-g" in args:
    target = Path.home() / ".claude" / "CLAUDE.md"
else:
    target = Path.cwd() / "CLAUDE.md"
```

Use global for cross-project rules (workflow, git, safety); use project-local for project-specific commands and structure.

## Underlying Utilities

| Utility | Role |
|---|---|
| `utils/claude_md_detector.py` | Project type detection |
| `utils/claude_md_template_populator.py` | Lean template variable substitution |
| `utils/claude_md_sync.py` | 4-phase sync pipeline (also called by `insights-apply`) |
| `utils/claude_md_optimizer.py` | Budget enforcement + bloat detection |
| `templates/claude-md/*.md` | Lean templates per project type |

## Decision Flow

```text
User intent ─┐
             ├─► file missing?       → Init (Phase 1)
             ├─► drift / audit needed?→ Sync (Phase 2)
             ├─► specific section?    → Edit (Phase 3)
             └─► /insights source?    → use `insights-apply` skill
```

## Error Recovery

| Error | Recovery |
|---|---|
| CLAUDE.md not found (sync/edit) | Suggest Init |
| Project type unknown (init) | Offer generic template or `--type <name>` |
| Over budget after edit/sync | Offer `--optimize` or manual edit |
| Section not found (edit) | Show available sections + fuzzy suggestion |
| Editor not installed (edit) | List available editors, prompt to pick |
| Anti-pattern submitted | Block, redirect to detail file |

## See Also

- `insights-apply` — apply `/insights` report suggestions to global CLAUDE.md (specific source)
- `doc-classifier` — decide what doc types a feature needs (sibling in `skills/docs/`)
- `changelog-automation` — release notes / CHANGELOG generation (sibling)
- `/craft:check` — invokes sync internally as part of pre-commit validation
