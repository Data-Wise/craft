# 🧠 BRAINSTORM: Interactive `/craft:docs:update` Workflow

**Mode:** deep + feature + save
**Duration:** 12 questions + comprehensive spec
**Generated:** 2026-01-22
**Revised:** 2026-01-22 (Comprehensive help file validation added)

---

## Context Summary

Based on deep requirement gathering (12 expert questions), designed an interactive workflow for `/craft:docs:update` that transforms it from batch operation to guided, category-based updates with integrated workflows.

### Key User Needs (From Questions)

1. **Control Level:** Category-level (not file-level, not change-level)
2. **Primary Pain:** Lack of control over what gets updated
3. **GIF Workflow:** Integrated (not separate), preview changes first, user decides
4. **Related Commands:** Auto-trigger lint and tutorials (not separate manual steps)
5. **Lint Handling:** Interactive per-file (not auto-fix all)
6. **Tutorial Creation:** Per-feature prompts (not batch at end)
7. **Existing Tutorials:** Offer to update (not skip or version)
8. **Dry-Run:** Via flag (not default)
9. **Bulk Changes:** Group by type (one prompt per category)
10. **Declined Updates:** Skip silently (no logging/tasks)
11. **Help Files:** Auto-detect outdated help text, offer updates
12. **Command Integration:** Orchestrated workflow (update → lint → tutorial → help)

---

## Quick Wins (< 30 min each)

⚡ **Implement category detection**

- Scan docs for version refs, command counts, broken links
- Group by type (12 version refs vs 47 links)
- Benefit: Foundation for interactive prompts

⚡ **Add `--dry-run` flag**

- Preview all changes without prompting
- Show what would be updated
- Benefit: Build trust, let users verify before running

⚡ **Create help file scanner**

- Parse YAML frontmatter from commands/*.md
- Extract `help:` field
- Benefit: Detect stale help text automatically

⚡ **Basic category prompt**

- Single AskUserQuestion for one category
- Yes/No decision
- Benefit: Validate UX pattern before scaling

---

## Medium Effort (1-2 hours each)

### GIF Integration

□ **Detect outdated GIFs**

- Compare commands in docs vs GIF metadata
- Extract command from markdown code blocks
- Check last updated timestamp

□ **Show command diffs**

- Display: `OLD: /craft:hub` → `NEW: /craft:hub --format=table`
- Highlight what changed (flags, args, syntax)
- Ask: "Regenerate this GIF?"

□ **Integrate with `/craft:docs:demo`**

- Invoke demo command for regeneration
- Handle recording process (asciinema)
- Update GIF file in place

### Lint Workflow

□ **Auto-trigger after updates**

- Run `/craft:docs:lint` on changed files
- Parse violation output (MD030, MD004, etc.)
- Group by file

□ **Per-file prompts**

- Show violations per file
- Offer: "Fix this file?" with preview
- Apply fixes on approval

### Tutorial Integration

□ **Detect new/changed features**

- Scan for new commands, updated features
- Compare docs vs existing tutorials
- Identify gaps

□ **Per-feature prompts**

- "Create tutorial for new feature X?"
- "Tutorial exists for Y, update it?"
- Invoke `/tutorial-engineer` agent

### Help File Updates

□ **Parse command YAML**

- Extract `help:` field from all commands
- Compare with current implementation
- Detect mentions of removed/added features

□ **Suggest updates**

- Show current vs suggested help text
- Explain reason (e.g., "Missing --orch flag")
- Offer: "Update help text?"

---

## Long-term (Future sessions)

### Advanced Features

□ **Smart auto-approve**

- Add `--auto-approve=links,lint` flag
- Auto-fix safe categories without prompt
- Power user mode

□ **JSON output format**

- Add `--format=json` for dry-run
- Machine-readable output
- CI/CD integration

□ **Partial category updates**

- Allow file-level selection within category
- "Fix 5 of 47 links" granularity
- Requires deeper interactive mode

### Workflow Enhancements

□ **Background tutorial generation**

- Run tutorial-engineer in Task (non-blocking)
- Notify when complete
- Continue with other categories

□ **Help text AI generation**

- Use LLM to generate help text from implementation
- Compare with current help
- Suggest improvements

□ **Version-aware updates**

- Detect version bumps from git tags
- Auto-update version refs
- Generate changelog entries

---

## Architecture Highlights

### Category-Based Workflow

```
Scan → Group → Prompt → Apply → Lint → Tutorial → Help → Summary
  ↓       ↓        ↓       ↓       ↓         ↓        ↓       ↓
  All     By       One     If      Auto-     Per      Per     Show
  docs    type     prompt  yes     trigger   feature  cmd     results
```

### Integration Flow

```
/craft:docs:update
  → Scan for updates (7 categories)
  → Category prompts (user approval)
  → Apply approved changes
  → Auto-trigger /craft:docs:lint
    → Per-file lint prompts
  → Detect tutorial needs
    → Per-feature tutorial prompts
    → Invoke /tutorial-engineer
  → Detect help file staleness
    → Per-command help prompts
  → Show summary
```

### Update Categories (9 total)

1. **Version References** - v2.5.1 → v2.6.0
2. **Command Counts** - 99 → 101 commands
3. **Feature Status** - Mark complete in matrix
4. **Broken Links** - Internal refs
5. **GIF Regeneration** - Outdated demos
6. **Changelog** - Add release notes
7. **Navigation** - mkdocs.yml updates
8. **Help Files** - Command YAML frontmatter
9. **Tutorial Updates** - Existing tutorial files

---

## Technical Implementation

### Phase Breakdown

**Phase 1: Core (Week 1)**

- Category detection & grouping
- AskUserQuestion prompts
- Apply updates
- Basic summary

**Phase 2: GIF (Week 2)**

- Outdated GIF detection
- Command diff generation
- Integration with docs:demo
- Error handling

**Phase 3: Lint & Tutorial (Week 3)**

- Auto-trigger lint workflow
- Per-file lint prompts
- Tutorial detection
- Agent invocation

**Phase 4: Help & Polish (Week 4)**

- Help file scanning
- YAML frontmatter parsing
- Suggestion generation
- Flags (`--dry-run`, `--category`, `--skip-*`)

### Data Models

```python
UpdateCategory      # Group changes by type
Change              # Individual file change
GIFUpdate           # Outdated GIF info + command diff
TutorialTask        # Feature needing tutorial
HelpFileUpdate      # Command help text update
```

### Key Functions

```python
scan_for_updates()              # Detect all update types
detect_outdated_gifs()          # Find GIFs with changed commands
prompt_for_category()           # Interactive approval
apply_category_updates()        # Execute changes
run_lint_workflow()             # Auto-lint + prompts
detect_tutorial_needs()         # Find tutorial gaps
detect_outdated_help_files()    # Scan YAML frontmatter
```

---

## UX Design

### Category Prompt Format

```
╭─────────────────────────────────────────────╮
│ Category: Version References                │
├─────────────────────────────────────────────┤
│                                             │
│ Update 12 version references to v2.6.0?     │
│                                             │
│   ○ Yes - Update all (Recommended)          │
│   ○ No - Skip this category                 │
│   ○ Show details                            │
│                                             │
╰─────────────────────────────────────────────╯
```

### GIF Preview

```
╭─────────────────────────────────────────────╮
│ GIF Update: hub-demo.gif (1 of 3)           │
├─────────────────────────────────────────────┤
│                                             │
│ Command Changed:                            │
│   OLD: /craft:hub                           │
│   NEW: /craft:hub --format=table            │
│                                             │
│ Regenerate this GIF?                        │
│   ○ Yes - Record new demo (Recommended)     │
│   ○ No - Keep current GIF                   │
│                                             │
╰─────────────────────────────────────────────╯
```

### Help File Update

```
╭─────────────────────────────────────────────╮
│ Help Text: /craft:do (1 of 5)               │
├─────────────────────────────────────────────┤
│                                             │
│ Current: "Smart task routing (0-10 scale)"  │
│                                             │
│ Suggested: "Smart routing with complexity   │
│ scoring. Use --orch for orchestration."     │
│                                             │
│ Reason: Missing --orch flag (v2.5.0)        │
│                                             │
│ Update help text?                           │
│   ○ Yes - Update (Recommended)              │
│   ○ No - Keep current                       │
│                                             │
╰─────────────────────────────────────────────╯
```

---

## Revision: Comprehensive Help File Validation

**Added:** 2026-01-22 (same session)
**Trigger:** User feedback - "make sure to test every command subcommand have help files along with flags; also offer to create/update; use help command styles and standards; check command line help as well"

### New Requirements Added

1. **Test ALL Commands & Subcommands**
   - Recursive scan of `commands/**/*.md` (not just top-level)
   - Validate 101+ commands including nested subcommands
   - Example: `commands/orchestrate/resume.md` is not skipped

2. **Validate ALL Flags**
   - Parse `arguments:` array in YAML frontmatter
   - Compare with actual implementation (code analysis)
   - Find missing flags (in code, not documented)
   - Find extra flags (documented, not in code)
   - Validate defaults, required status, aliases

3. **Offer to CREATE Missing Help Files**
   - Not just update existing, but CREATE from scratch
   - Use HELP-PAGE-TEMPLATE.md as basis
   - Generate YAML frontmatter from code analysis
   - Offer "Full help page" vs "YAML only" options

4. **CLI --help Output Validation**
   - Execute each command with `--help` flag
   - Parse output, compare with YAML frontmatter
   - Detect inconsistencies (description, flags, aliases)
   - Offer to fix YAML or fix --help implementation
   - Priority: YAML is source of truth

5. **Standards Compliance**
   - Validate against HELP-PAGE-TEMPLATE.md structure
   - Check Synopsis, Options, Examples sections exist
   - Ensure consistent flag table format
   - Validate category field matches directory path

### Implementation Changes

**Data Models Added:**

- `HelpMismatch` - Track YAML vs --help discrepancies
- `CommandArgument` - Parse arguments from YAML or --help
- Enhanced `HelpFileUpdate` with CLI validation

**API Functions Added (14 new):**

```python
scan_all_commands()                    # Recursive file scan
validate_yaml_structure()              # Required fields check
validate_yaml_arguments()              # Arguments array validation
extract_flags_from_code()              # Code analysis
compare_yaml_vs_code()                 # Find missing/extra flags
get_help_output()                      # Execute --help
parse_help_output()                    # Parse CLI output
validate_help_consistency()            # YAML vs --help check
suggest_yaml_frontmatter()             # Generate from template
create_help_file()                     # Create from scratch
validate_against_template()            # Template compliance
group_help_issues_by_type()            # Batch prompts
```

**Phase Plan Updated:**

- Phase 3: Added comprehensive help validation
- Phase 4: Added template compliance checking

**New Category:**

- Help Files: "5 outdated, 2 missing" (not just "5 commands need updates")

### Testing Requirements Added

- 15+ new test cases for help validation
- Performance targets: 101 commands in < 15s
- Edge cases: missing YAML, wrong category, --help failures

### Success Metrics Added

| Metric | Target |
|--------|--------|
| Help file coverage | 100% of commands |
| Help consistency | 100% YAML matches --help |
| Template compliance | 90%+ follow structure |

---

## Open Questions

1. **GIF Timeout:** Cancel after 5min or let user control?
   → Recommendation: Let user cancel, show progress

2. **Partial Updates:** Allow file-level within category?
   → Recommendation: Keep simple, all-or-nothing per category

3. **Tutorial Blocking:** Inline or background Task?
   → Recommendation: Inline (blocking) for immediate feedback

4. **Dry-Run Format:** Markdown or JSON or both?
   → Recommendation: Add `--format` flag for flexibility

5. **Auto-Approve:** Auto-fix safe categories?
   → Recommendation: Add `--auto-approve` flag for power users

---

## Success Metrics

| Metric | Target | Measure |
|--------|--------|---------|
| **Adoption** | 80% use interactive mode | Track invocations |
| **Trust** | 0 "surprise" updates | User feedback |
| **Efficiency** | < 5 min for 50 updates | Time tracking |
| **Tutorial coverage** | 2x increase | Count before/after |
| **GIF freshness** | 0 GIFs > 30 days old | Metadata scan |

---

## Next Steps

### Immediate (This session)

1. ✅ **Spec captured** - SPEC-docs-update-interactive-2026-01-22.md
2. □ Review spec for completeness
3. □ Validate with existing `/craft:docs:update` implementation

### Short-term (This week)

1. □ Implement Phase 1: Core workflow
2. □ Write unit tests for category detection
3. □ Create integration test for full workflow

### Medium-term (Next 2 weeks)

1. □ Implement Phase 2: GIF integration
2. □ Implement Phase 3: Lint & tutorial workflows
3. □ Implement Phase 4: Help file detection

---

## Related Work

- **SPEC-brainstorm-phase1** - Question control patterns
- **SPEC-craft-hub-v2** - Auto-discovery inspiration
- **SPEC-teaching-workflow** - Safe publish workflow (preview → validate → deploy)

---

## Recommended Path

→ **Start with Phase 1 (Core Workflow)** because it establishes the foundation for category-based prompting and validates the UX pattern before adding complexity.

**Why Phase 1 first:**

1. Validates interactive UX (is category-level the right granularity?)
2. Proves technical feasibility (can we detect all update types?)
3. Delivers value immediately (version refs, counts, links work)
4. De-risks later phases (GIF, lint, tutorial build on proven base)

**After Phase 1:**

- Get user feedback on prompt UX
- Measure time to complete 50 updates
- Validate category grouping is correct
- Then proceed to Phase 2 (GIF integration)

---

## Files Created

- ✅ `SPEC-docs-update-interactive-2026-01-22.md` - Comprehensive implementation spec
- ✅ `BRAINSTORM-docs-update-interactive-2026-01-22.md` - This brainstorm summary

---

**Session complete in deep mode with feature focus and spec capture.**
