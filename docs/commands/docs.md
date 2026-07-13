# Documentation Commands

> **TL;DR** (30 seconds)
>
> - **What:** 25 smart documentation commands from generation to ADHD-friendly enhancement
> - **Why:** Automate docs updates, validation, and website optimization with one command
> - **How:** Use `/craft:docs:update --interactive` for category-level prompts (NEW v2.7.0)
> - **Next:** Try `/craft:docs:update --interactive --dry-run` to preview what would change

Smart documentation generation, validation, and enhancement - 25 commands.

## Which Docs Command for What

| Scenario | Command | What It Does |
|----------|---------|--------------|
| "Update everything after changes" | `/craft:docs:update` | Full cycle: detect → generate → validate → changelog |
| "What docs need updating?" | `/folio:docs:sync` | Detection only — reports what's stale |
| "Are my docs valid?" | `/folio:docs:check` | Validates links + nav + staleness + mermaid, auto-fixes |
| "Fix markdown formatting" | `/folio:docs:lint` | Markdownlint with auto-fix |
| "Check only broken links" | `/folio:docs:check-links` | Internal link validation with .linkcheck-ignore |
| "Update CLAUDE.md" | `/craft:docs:claude-md` | Sync CLAUDE.md with project state |
| "Update changelog" | `/craft:docs:changelog` | Generate entries from git commits |
| "Add page to nav" | `/folio:docs:nav-update` | Update mkdocs.yml navigation |

**Decision flow:**

1. **After writing code** → `/craft:docs:update` (does everything)
2. **Before committing** → `/folio:docs:check` (validates)
3. **PR merged to dev** → `/craft:docs:update --post-merge` (auto-fix pipeline)
4. **Just want to check** → `/folio:docs:sync` (detection only, no changes)

---

## Super Commands

### /craft:docs:update

**Smart-Full cycle with Interactive Mode (v2.7.0):** 9-category detection with category-level prompts

```bash
/craft:docs:update --interactive              # Category-level prompts (9 categories)
/craft:docs:update --category=version_refs    # Update only version references
/craft:docs:update --interactive --dry-run    # Preview without applying changes
/craft:docs:update --auto-yes                 # Batch mode (no prompts)
```

**9 Detection Categories:**

1. Version references (545 found in craft)
2. Command counts (289 found)
3. Broken links
4. Stale examples
5. Missing help files (60 found)
6. Outdated status markers
7. Inconsistent terminology
8. Missing cross-references (366 found)
9. Outdated diagrams

**Comprehensive Documentation:**

- [Interactive Tutorial](../tutorials/interactive-docs-update-tutorial.md) - Step-by-step guide (10-15 min)
- [Quick Reference Card](../reference/REFCARD-DOCS-UPDATE.md) - All flags and options
- [Real-World Example](../examples/docs-update-interactive-example.md) - Full workflow walkthrough

### /folio:docs:sync

**Detection only:** Classify changes, report stale docs, recommend actions

```bash
/folio:docs:sync                      # Quick: "3 stale, guide recommended"
```

### /folio:docs:check

**Validation:** Links + stale + nav + mermaid + auto-fix (full by default)

```bash
/folio:docs:check                     # Full check cycle, auto-fixes
/folio:docs:check --report-only       # CI-safe mode (no modifications)
/folio:docs:check --no-mermaid        # Skip mermaid validation phase
/folio:docs:check --mermaid-gate 90   # Custom health score threshold
```

**Phase 5: Mermaid Validation** runs 5 regex pre-checks on all mermaid blocks, calculates a health score (0-100), and reports errors/warnings. See [Mermaid Authoring Guide](../guide/mermaid-authoring.md).

### /folio:docs:mermaid

**Diagram creation:** Templates, natural language, MCP validation, browser preview

```bash
/folio:docs:mermaid workflow                           # Get workflow template
/folio:docs:mermaid "auth flow with OAuth2" --validate # NL creation + validation
/folio:docs:mermaid "CI pipeline" --preview            # Render SVG in browser
```

See [Mermaid Authoring Guide](../guide/mermaid-authoring.md) for templates and syntax rules.

## Quality Automation

### /folio:docs:lint

**Markdown quality validation with auto-fix**

```bash
/folio:docs:lint                      # Quick quality check
/folio:docs:lint --fix                # Auto-fix safe issues
/folio:docs:lint release              # Comprehensive validation
/folio:docs:lint --dry-run            # Preview checks
```

**Features:**

- Critical error detection (MD032, MD040, MD009, MD011, MD042)
- Automatic fixing of trailing spaces, hard tabs, blank lines
- Smart code fence language detection (Python, JavaScript, Bash, etc.)
- VS Code clickable output format

**Exit codes:**

- `0` = No errors or all auto-fixed
- `1` = Manual fixes required
- `2` = Configuration error

### /folio:docs:check-links

**Internal link validation with .linkcheck-ignore support** ⭐ NEW

```bash
/folio:docs:check-links               # Validate all internal links
/folio:docs:check-links release       # Include anchor validation
/folio:docs:check-links docs/guide/   # Check specific directory
/folio:docs:check-links --dry-run     # Preview checks
```

**Features:**

- Relative and absolute path validation
- Anchor/header existence checking (release mode)
- **`.linkcheck-ignore` pattern support** - Document expected broken links
- Categorized output: Critical vs Expected broken links
- VS Code clickable error format
- Ignores external URLs by default

**Exit codes:**

- `0` = All links valid OR only expected broken links
- `1` = Critical broken links found
- `2` = Invalid arguments

**NEW: .linkcheck-ignore Support**

Create a `.linkcheck-ignore` file to document expected broken links:

```markdown
# Known Broken Links

### Test Files
File: `docs/test-violations.md`
- Purpose: Test data for validation

### Brainstorm References
Files: `docs/specs/*.md`
Targets: `docs/brainstorm/*.md`
```

**Benefits:**

- ✅ 100% reduction in CI false positives
- ✅ Expected links don't block CI (exit code 0)
- ✅ Critical links still fail properly (exit code 1)
- ✅ Clear categorization in output

## NEW: ADHD-Friendly Website Enhancement

### /folio:docs:website

**Purpose:** One command to make any documentation site ADHD-friendly.

**Features:**

- ADHD scoring algorithm (0-100) across 5 categories
- 3-phase enhancement: Quick Wins, Structure, Polish
- Mermaid syntax error detection and fixing
- TL;DR box generation
- Time estimate addition
- ADHD Quick Start page creation

**Usage:**

```bash
/folio:docs:website                   # Full enhancement (all 3 phases)
/folio:docs:website --analyze         # Show ADHD score only
/folio:docs:website --phase 1         # Quick wins: TL;DR, mermaid fixes
/folio:docs:website --phase 2         # Structure: Visual workflows
/folio:docs:website --phase 3         # Polish: Mobile responsive
/folio:docs:website --dry-run         # Preview changes without writing
```

**ADHD Scoring Categories:**

- Visual Hierarchy (25%): TL;DR boxes, emojis, heading structure
- Time Estimates (20%): Tutorial duration info
- Workflow Diagrams (20%): Mermaid diagrams without errors
- Mobile Responsive (15%): Overflow fixes, touch targets
- Content Density (20%): Paragraph length, callout boxes

## All Docs Commands

| Command | Description | Help Page |
|---------|-------------|-----------|
| `/craft:docs:update` | Smart full-cycle documentation generator | [Help](docs/update.md) |
| `/folio:docs:sync` | Change detection and classification | (moved to folio) |
| `/folio:docs:check` | Documentation health check with auto-fix | (moved to folio) |
| `/folio:docs:lint` | Markdown quality validation with auto-fix | (moved to folio) |
| `/folio:docs:check-links` | Internal link validation | (moved to folio) |
| `/craft:docs:changelog` | Auto-update CHANGELOG from commits | [Help](docs/changelog.md) |
| `/folio:docs:nav-update` | Update mkdocs.yml navigation | (moved to folio) |
| `/folio:docs:guide` | Feature guide + demo + refcard generator | (moved to folio) |
| `/folio:docs:tutorial` | Interactive tutorial generator | (moved to folio) |
| `/folio:docs:workflow` | Workflow documentation generator | (moved to folio) |
| `/folio:docs:demo` | Terminal recording & GIF generator | (moved to folio) |
| `/folio:docs:mermaid` | Mermaid diagram templates & NL creation | (moved to folio) |
| `/folio:docs:website` | ADHD-friendly website enhancement | (moved to folio) |
| `/folio:docs:api` | OpenAPI/Swagger documentation | (moved to folio) |
| `/folio:docs:help` | Help page generator | (moved to folio) |
| `/folio:docs:prompt` | Generate reusable maintenance prompts | (moved to folio) |
| `/folio:docs:quickstart` | Quick start guide generator | (moved to folio) |
| `/folio:docs:site` | Site-wide documentation updates | (moved to folio) |
| `/craft:docs:claude-md` | CLAUDE.md management hub | [Help](docs/claude-md.md) |
| `/craft:docs:claude-md:edit` | Interactive CLAUDE.md editing | [Help](docs/claude-md/edit.md) |
| `/craft:docs:claude-md:init` | Create CLAUDE.md from template | [Help](docs/claude-md/init.md) |
| `/craft:docs:claude-md:sync` | Sync CLAUDE.md with project state | [Help](docs/claude-md/sync.md) |
