# Documentation Commands

> **TL;DR** (30 seconds)
>
> - **What:** 17 smart documentation commands from generation to ADHD-friendly enhancement
> - **Why:** Automate docs updates, validation, and website optimization with one command
> - **How:** Use `/craft:docs:update --interactive` for category-level prompts (NEW v2.7.0)
> - **Next:** Try `/craft:docs:update --interactive --dry-run` to preview what would change

Smart documentation generation, validation, and enhancement - 17 commands.

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

### /craft:docs:sync

**Detection only:** Classify changes, report stale docs, recommend actions

```bash
/craft:docs:sync                      # Quick: "3 stale, guide recommended"
```

### /craft:docs:check

**Validation:** Links + stale + nav + auto-fix (full by default)

```bash
/craft:docs:check                     # Full check cycle, auto-fixes
/craft:docs:check --report-only       # CI-safe mode (no modifications)
```

## Quality Automation

### /craft:docs:lint

**Markdown quality validation with auto-fix**

```bash
/craft:docs:lint                      # Quick quality check
/craft:docs:lint --fix                # Auto-fix safe issues
/craft:docs:lint release              # Comprehensive validation
/craft:docs:lint --dry-run            # Preview checks
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

### /craft:docs:check-links

**Internal link validation with .linkcheck-ignore support** ⭐ NEW

```bash
/craft:docs:check-links               # Validate all internal links
/craft:docs:check-links release       # Include anchor validation
/craft:docs:check-links docs/guide/   # Check specific directory
/craft:docs:check-links --dry-run     # Preview checks
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

### /craft:docs:website

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
/craft:docs:website                   # Full enhancement (all 3 phases)
/craft:docs:website --analyze         # Show ADHD score only
/craft:docs:website --phase 1         # Quick wins: TL;DR, mermaid fixes
/craft:docs:website --phase 2         # Structure: Visual workflows
/craft:docs:website --phase 3         # Polish: Mobile responsive
/craft:docs:website --dry-run         # Preview changes without writing
```

**ADHD Scoring Categories:**

- Visual Hierarchy (25%): TL;DR boxes, emojis, heading structure
- Time Estimates (20%): Tutorial duration info
- Workflow Diagrams (20%): Mermaid diagrams without errors
- Mobile Responsive (15%): Overflow fixes, touch targets
- Content Density (20%): Paragraph length, callout boxes

## Specialized Commands

### /craft:docs:guide

Feature guide + demo + refcard generator

```bash
/craft:docs:guide "authentication"
```

### /craft:docs:demo

VHS tape generator for GIF demos

```bash
/craft:docs:demo "quick-start"
```

### /craft:docs:mermaid

Mermaid diagram templates (6 types)

```bash
/craft:docs:mermaid flowchart
/craft:docs:mermaid sequence
```

### /craft:docs:api

OpenAPI/Swagger documentation

### /craft:docs:changelog

Auto-update CHANGELOG from commits

### /craft:docs:nav-update

Update mkdocs.yml navigation

### /craft:docs:prompt

Generate reusable maintenance prompts

## Integration Commands

### /craft:docs:site

Site-wide documentation updates (integrates with site commands)

```bash
/craft:docs:site sync    # Sync docs with site structure
```

## Internal Commands

### /craft:docs:claude-md

Update CLAUDE.md (called by other commands)
