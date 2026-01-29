# /craft:docs:update

> **Smart documentation generator that detects what's needed and generates everything automatically.**

---

## Synopsis

```bash
/craft:docs:update [feature] [--flags]
```

**Quick examples:**

```bash
# Smart detection → Full execution
/craft:docs:update                    # Detect changes → generate all needed docs

# Feature-specific
/craft:docs:update "auth"             # Document the "auth" feature

# Force specific doc types
/craft:docs:update --with-tutorial    # Force tutorial generation
/craft:docs:update --all              # Generate all doc types
```

---

## Description

The ONE command for documentation. Detects what changed, figures out what docs are needed, generates everything automatically, and validates.

**Philosophy:**
> "Just run it. It figures out what's needed, then does it."

**What it does:**

1. **Preview** — shows what needs updating before acting (NEW)
2. **Confirm** — asks how to proceed: interactive, auto-apply, or preview-only (NEW)
3. **sync** — detect changes, classify docs needed
4. **generate** — guide, demo, refcard (as needed)
5. **check** — validate + auto-fix
6. **changelog** — if commits present
7. **summary** — report what was done

---

## Usage Modes

### Default Mode (Smart Detection)

```bash
/craft:docs:update
```

Analyzes recent changes and generates appropriate documentation:

```
┌─────────────────────────────────────────────────────────────┐
│ Step 1/5: DETECTING CHANGES                                 │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Analyzing 15 recent commits...                              │
│                                                             │
│ Detected:                                                   │
│   • 5 new CLI commands                                      │
│   • 2 new hooks                                             │
│   • 1 new module                                            │
│                                                             │
│ Classification:                                             │
│   Guide needed:   ✓ (score: 8)                              │
│   Refcard needed: ✓ (score: 5)                              │
│   Demo needed:    ✓ (score: 6)                              │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Feature-Specific Mode

```bash
/craft:docs:update "auth"
```

Scopes documentation to files matching "auth":

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:docs:update "auth"                                   │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Feature: Authentication                                     │
│                                                             │
│ Scope: Files matching "auth" in name/path                   │
│   • src/auth/                                               │
│   • src/**/auth*                                            │
│   • tests/**/test_auth*                                     │
│                                                             │
│ Generated:                                                  │
│   • docs/guide/auth.md (NEW)                                │
│   • docs/reference/REFCARD-AUTH.md (NEW)                    │
│   • Updated 4 existing docs                                 │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Flags

### Basic Flags

| Flag | Effect |
|------|--------|
| (none) | Smart detection → generate needed → check → changelog |
| `"feature"` | Scope to specific feature |
| `--force` | Full cycle regardless of detection |
| `--dry-run` | Preview plan without executing |
| `--no-check` | Skip validation phase |
| `--no-changelog` | Skip changelog update |
| `--post-merge` | Post-merge pipeline — auto-fix safe categories, prompt for manual (NEW) |
| `--verbose` | Detailed output |

### Force Generation Flags

Force specific doc types regardless of scoring:

| Flag | Effect |
|------|--------|
| `--with-tutorial` | Force tutorial generation |
| `--with-help` | Force help page generation |
| `--with-workflow` | Force workflow doc generation |
| `--with-quickstart` | Force quickstart generation |
| `--all` | Generate all doc types |
| `--threshold N` | Override scoring threshold (default: 3) |

**Example:**

```bash
/craft:docs:update "auth" --with-tutorial    # Auth docs + forced tutorial
/craft:docs:update --all                      # Generate everything
/craft:docs:update --threshold 2              # Lower threshold for more docs
```

---

## Scoring Algorithm

Doc types are generated based on classification scores:

| Factor | Guide | Refcard | Demo | Tutorial | Help | Workflow |
|--------|-------|---------|------|----------|------|----------|
| New command (each) | +1 | +1 | +0.5 | +1 | +2 | +0.5 |
| New module | +3 | +1 | +1 | +2 | +1 | +1 |
| New hook | +2 | +1 | +1 | +1 | +0 | +2 |
| Multi-step workflow | +2 | +0 | +3 | +3 | +0 | +4 |
| Config changes | +0 | +2 | +0 | +1 | +1 | +0 |
| User-facing CLI | +1 | +1 | +2 | +2 | +1 | +2 |

**Thresholds:**

- Guide, Refcard, Demo: Score >= 3
- Tutorial, Help, Workflow: Score >= 2

---

## Output Example

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ DOCUMENTATION UPDATE COMPLETE                            │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ Feature: Session Tracking                                   │
│                                                             │
│ Generated:                                                  │
│   • docs/guide/sessions.md (NEW - 275 lines)                │
│   • docs/reference/REFCARD-SESSIONS.md (NEW - 85 lines)     │
│   • docs/demos/sessions.tape (NEW - VHS demo)               │
│                                                             │
│ Updated:                                                    │
│   • docs/reference/commands.md (+45 lines)                  │
│   • README.md (features list)                               │
│   • CLAUDE.md (status)                                      │
│   • mkdocs.yml (navigation)                                 │
│   • CHANGELOG.md (session coordination)                     │
│                                                             │
│ Validated:                                                  │
│   • 3 issues auto-fixed                                     │
│   • 0 manual fixes needed                                   │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ NEXT STEPS:                                                 │
│                                                             │
│ 1. Generate GIF (if demo created):                          │
│    cd docs/demos && vhs sessions.tape                       │
│                                                             │
│ 2. Preview docs:                                            │
│    mkdocs serve                                             │
│                                                             │
│ 3. Commit:                                                  │
│    git commit -m "docs: add session documentation"          │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## Orchestrated Commands

This command internally orchestrates:

| Command | Purpose |
|---------|---------|
| `/craft:docs:sync` | Change detection and classification |
| `/craft:docs:guide` | Guide generation |
| `/craft:docs:tutorial` | Tutorial generation |
| `/craft:docs:help` | Help page generation |
| `/craft:docs:workflow` | Workflow doc generation |
| `/craft:docs:demo` | VHS tape generation |
| `/craft:docs:mermaid` | Diagram generation |
| `/craft:docs:check` | Validation and auto-fix |
| `/craft:docs:changelog` | Changelog updates |

---

## Templates Used

Located in `templates/docs/`:

| Template | Purpose |
|----------|---------|
| `TUTORIAL-TEMPLATE.md` | Progressive learning structure |
| `WORKFLOW-TEMPLATE.md` | Multi-step process docs |
| `HELP-PAGE-TEMPLATE.md` | Command help pages |
| `QUICK-START-TEMPLATE.md` | 5-minute quickstart |
| `REFCARD-TEMPLATE.md` | Quick reference cards |
| `GETTING-STARTED-TEMPLATE.md` | First-time setup |
| `GIF-GUIDELINES.md` | Terminal recording standards |

---

## Post-Merge Pipeline (NEW)

After merging a PR, run `--post-merge` to automatically update all documentation:

```bash
/craft:docs:update --post-merge                  # Full pipeline
/craft:docs:update --post-merge --dry-run        # Preview only
```

### Pipeline Flow

```
PR merged
  → Phase 1: Auto-detect (9 categories)
  → Phase 2: Auto-fix safe categories (no prompts)
  → Phase 3: Prompt for manual categories
  → Phase 4: Lint + validate
  → Phase 5: Summary
```

### Phase 1: Detection

```
Post-Merge Documentation Scan:
  Merge: PR #42 "feat: add auth system" → dev
  Changed files: 15
  New commands: 3

  Detected categories:
  [AUTO]   Version references — 12 files
  [AUTO]   Command counts — 4 files
  [AUTO]   Navigation entries — 2 new pages
  [AUTO]   Broken links — 1 link
  [MANUAL] Help files — 3 new commands
  [MANUAL] Changelog draft — from PR description
  [SKIP]   GIF regeneration — no changed commands
```

### Phase 2: Auto-Fix (no prompts)

Safe categories are fixed automatically:

| Category | Action |
|----------|--------|
| Version references | Find-replace version strings across all docs |
| Command counts | Recalculate from `commands/**/*.md` |
| Navigation entries | Add new pages to mkdocs.yml |
| Broken links | Update changed file paths |

### Phase 3: Manual Categories (interactive)

Categories requiring judgment prompt via interactive questions:

```
? 3 new commands need help documentation. How should I handle them?
  › Generate all (Recommended)
    Generate one at a time
    Skip for now
```

### Phase 4-5: Validate and Summarize

```
Validation:
  Markdown lint... ✅ 0 issues
  Internal links... ✅ all resolved
  Count validation... ✅ matches

Post-Merge Documentation Update Complete:
  Auto-fixed: 4 categories (19 files changed)
  Manual: 2 categories (3 files created)
  Skipped: 3 categories (no changes needed)
```

### Safe vs Manual Categories

| Category | Safe (auto-fix) | Manual (prompt) |
|----------|:-:|:-:|
| Version references | ✅ | |
| Command counts | ✅ | |
| Navigation entries | ✅ | |
| Broken links | ✅ | |
| Help files | | ✅ |
| Tutorials | | ✅ |
| Changelog | | ✅ |
| GIF regeneration | | ✅ |
| Feature status | | ✅ |

---

## Troubleshooting

| Issue | Solution |
|-------|----------|
| "No changes detected" | Use `--force` to generate anyway |
| Wrong doc type generated | Use `--with-*` flags to force specific types |
| Threshold too high | Use `--threshold 2` to lower |
| Validation errors | Run `/craft:docs:check` separately for details |
| Demo not generated | Check if VHS is installed |

---

## ADHD-Friendly Design

1. **One command** - No multi-step process to remember
2. **Smart defaults** - Detects what's needed automatically
3. **Visual progress** - See each phase completing
4. **Clear summary** - Know exactly what was done
5. **Next steps** - Always shows what to do next

---

## See Also

- **Individual commands:** `/craft:docs:guide`, `/craft:docs:tutorial`, `/craft:docs:help`
- **Validation:** `/craft:docs:check` - Validate documentation
- **Pre-flight:** `/craft:check` - Full project validation
- **Navigation:** `/craft:docs:nav-update` - Update mkdocs.yml
