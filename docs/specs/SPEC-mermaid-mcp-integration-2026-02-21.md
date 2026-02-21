# SPEC: Mermaid MCP Integration

**Date:** 2026-02-21
**Status:** Draft
**Focus:** Feature (Lint + Validate + Preview + Create)
**Priority:** High (prevents recurring deployment issues)

## Problem Statement

Mermaid diagram syntax errors silently ship to the live docs site, causing:

- Diagrams rendering as raw code text (broken `fence_code_format` vs `fence_div_format`)
- Syntax errors from `[/text]` being misinterpreted as parallelogram shapes
- Mermaid JS not re-initializing on mkdocs-material instant navigation
- Manual debugging sessions lasting 1+ hours per incident

**Root cause:** No automated Mermaid validation in the docs pipeline.

## Goals

1. **Never ship broken diagrams** — validate every mermaid block before deploy
2. **Auto-fix known gotchas** — `[/` labels, lowercase `end`, unquoted special chars
3. **Live browser preview** — real-time rendering during diagram authoring
4. **NL diagram creation** — describe diagrams in natural language, get validated code
5. **Mermaid health score** — composite quality metric for release pre-flight

## Architecture

### MCP Server: mcp-mermaid (hustcc)

Install via npx as local MCP server. Provides:

- Validation with syntax error details
- Rendering to SVG, PNG, base64, file, svg_url, png_url
- Iterative refinement workflow

```json
{
  "mcpServers": {
    "mcp-mermaid": {
      "command": "npx",
      "args": ["-y", "mcp-mermaid"]
    }
  }
}
```

### Validation Pipeline

```
Pre-commit hook
    │
    ├── Local regex pre-checks (< 1s)
    │   ├── [/ label detection
    │   ├── lowercase 'end' keyword
    │   ├── unquoted special chars
    │   └── <br/> tag detection
    │
    └── MCP full validation (per block)
        ├── Syntax validation
        ├── Rendering test
        └── Error reporting with fix suggestions

/craft:docs:check
    │
    ├── Phase: Mermaid Validation (NEW)
    │   ├── Extract all mermaid blocks
    │   ├── Local regex pre-checks
    │   ├── MCP validation (all blocks)
    │   ├── Auto-fix safe issues
    │   └── Generate health score
    │
    └── Existing phases (links, stale, nav)

/craft:site:deploy
    │
    └── Gate: Mermaid health score > threshold (configurable, default 80)

/craft:check --for release
    │
    └── Include mermaid health score in release pre-flight
```

### Auto-Fix Engine

| Rule | Regex Pattern | Fix Strategy | Safe? |
|------|--------------|--------------|-------|
| Leading `/` in labels | `\[(/[^\]]+)\]` inside mermaid blocks | Wrap in quotes: `["/text"]` | Yes |
| Lowercase `end` | `\bend\b` in node labels | Capitalize: `End` | Yes |
| Unquoted colons | `\[[^\]"]*:[^\]"]*\]` | Wrap in quotes | Yes |
| `<br/>` tags | `<br\s*/?>` in node labels | Convert to markdown strings | Yes |
| Deprecated `graph` | `^graph\s+(TB\|TD\|LR\|RL\|BT)` | Replace with `flowchart` | Yes |
| Long node text (>20 chars) | `"[^"]{20,}"` in node labels | Report + suggest abbreviation | Report only |
| Orphaned nodes | Node ID not in any edge | Report + suggest connection | Report only |
| Complex horizontal | `LR` with >5 connected nodes | Report + suggest `TD` | Report only |

### Health Score

Composite metric (0-100):

```
health_score = (
    syntax_validity * 0.5 +     # % blocks passing MCP validation
    best_practices * 0.3 +      # % blocks following all lint rules
    rendering_success * 0.2     # % blocks rendering to SVG
)
```

Thresholds:

- Release gate: >= 80
- Warning: < 90
- Good: >= 90

### NL Diagram Creation

Extends existing `/craft:docs:mermaid` command:

```bash
# Existing: template-based
/craft:docs:mermaid workflow

# NEW: natural language
/craft:docs:mermaid "show the release pipeline from dev to main"

# NEW: with live preview
/craft:docs:mermaid "auth flow with OAuth2" --preview
```

Workflow:

1. Claude generates Mermaid code from description
2. mcp-mermaid validates + renders
3. Live preview opens in browser
4. User iterates via conversation
5. Final code saved to specified file or clipboard

## Integration Points

### Existing Components (Augmented)

| Component | Change |
|-----------|--------|
| `/craft:docs:check` | Add "Mermaid Validation" phase |
| `/craft:docs:mermaid` command | Add NL generation + MCP validation |
| `mermaid-linter` skill | Update to use MCP for syntax validation |
| `mermaid-expert` agent | Add MCP rendering capability |
| Pre-commit hooks | Add mermaid validation for .md files |

### New Components

| Component | Description |
|-----------|-------------|
| `scripts/mermaid-validate.py` | Extract + validate all mermaid blocks |
| `scripts/mermaid-autofix.py` | Auto-fix known patterns |
| `mermaid-init.js` | Already created (instant nav fix) |
| Health score reporter | Generate composite quality metric |

## Acceptance Criteria

- [ ] mcp-mermaid installed and functional as MCP server
- [ ] All 152+ mermaid blocks validated without false positives
- [ ] Auto-fix correctly handles: `[/` labels, lowercase `end`, unquoted chars, `<br/>`, deprecated `graph`
- [ ] Health score displays in `/craft:docs:check` output
- [ ] Pre-commit hook validates mermaid blocks in changed .md files
- [ ] `/craft:site:deploy` gates on health score >= 80
- [ ] NL diagram creation works: describe -> generate -> validate -> preview
- [ ] Live browser preview functional during authoring
- [ ] No regression in existing mermaid template functionality

## Documentation Requirements

| Document | Location | Content |
|----------|----------|---------|
| Command update | `commands/docs/mermaid.md` | Add NL creation usage, MCP validation flag, `--preview` |
| Skill update | `skills/docs/mermaid-linter/skill.md` | Add MCP validation rules, health score output format |
| Docs check update | `commands/docs/check.md` | Document new Mermaid Validation phase |
| Guide page | `docs/guide/mermaid-authoring.md` | End-to-end guide: create, validate, preview, deploy |
| REFCARD entry | `docs/REFCARD.md` | Quick reference for mermaid health score and lint rules |
| CHANGELOG | `CHANGELOG.md` | Feature entry for Mermaid MCP integration |
| mkdocs nav | `mkdocs.yml` | Add guide page to navigation |

## Test Plan

### Unit Tests (`tests/test_mermaid_validation.py`)

| Test | Description | Marker |
|------|-------------|--------|
| `test_regex_detects_leading_slash` | `[/text]` detected in mermaid blocks | `@pytest.mark.unit` |
| `test_regex_detects_lowercase_end` | Lowercase `end` in node labels detected | `@pytest.mark.unit` |
| `test_regex_detects_unquoted_special_chars` | Colons/brackets without quotes detected | `@pytest.mark.unit` |
| `test_regex_detects_br_tags` | `<br/>` in mermaid blocks detected | `@pytest.mark.unit` |
| `test_regex_detects_deprecated_graph` | `graph TB` flagged, `flowchart TD` passes | `@pytest.mark.unit` |
| `test_autofix_quotes_slash_labels` | `[/text]` -> `["/text"]` | `@pytest.mark.unit` |
| `test_autofix_capitalizes_end` | `[end]` -> `[End]` | `@pytest.mark.unit` |
| `test_autofix_quotes_special_chars` | `[a:b]` -> `["a:b"]` | `@pytest.mark.unit` |
| `test_autofix_replaces_br_tags` | `<br/>` -> markdown strings | `@pytest.mark.unit` |
| `test_autofix_graph_to_flowchart` | `graph TB` -> `flowchart TB` | `@pytest.mark.unit` |
| `test_autofix_preserves_valid_diagrams` | Clean diagrams unchanged | `@pytest.mark.unit` |
| `test_health_score_calculation` | Score = 0.5*validity + 0.3*practices + 0.2*rendering | `@pytest.mark.unit` |
| `test_health_score_thresholds` | >= 80 pass, < 80 fail gate | `@pytest.mark.unit` |
| `test_block_extraction_from_markdown` | Correctly extracts mermaid fenced blocks | `@pytest.mark.unit` |
| `test_block_extraction_ignores_non_mermaid` | Doesn't match ```python or```bash blocks | `@pytest.mark.unit` |

### E2E Tests (`tests/test_mermaid_e2e.py`)

| Test | Description | Marker |
|------|-------------|--------|
| `test_mcp_mermaid_validates_good_diagram` | MCP returns valid for clean diagram | `@pytest.mark.e2e, @pytest.mark.mermaid` |
| `test_mcp_mermaid_rejects_bad_diagram` | MCP returns error for `[/text]` syntax | `@pytest.mark.e2e, @pytest.mark.mermaid` |
| `test_docs_check_includes_mermaid_phase` | `/craft:docs:check` output includes mermaid section | `@pytest.mark.e2e, @pytest.mark.docs` |
| `test_all_existing_blocks_pass_validation` | Every mermaid block in docs/ passes local regex | `@pytest.mark.e2e, @pytest.mark.mermaid` |
| `test_autofix_produces_valid_output` | Auto-fixed files pass MCP validation | `@pytest.mark.e2e, @pytest.mark.mermaid` |
| `test_health_score_reports_in_docs_check` | Health score appears in check output | `@pytest.mark.e2e, @pytest.mark.docs` |
| `test_precommit_catches_bad_mermaid` | Pre-commit hook blocks commit with broken diagram | `@pytest.mark.e2e, @pytest.mark.mermaid` |
| `test_mermaid_linter_skill_updated` | Skill references MCP validation | `@pytest.mark.e2e, @pytest.mark.structure` |

### Dogfood Tests (`tests/test_mermaid_dogfood.py`)

| Test | Description | Marker |
|------|-------------|--------|
| `test_all_docs_mermaid_blocks_have_valid_syntax` | Every block in docs/ passes regex lint | `@pytest.mark.dogfood, @pytest.mark.mermaid` |
| `test_no_leading_slash_in_mermaid_labels` | Zero `[/` patterns in any mermaid block | `@pytest.mark.dogfood, @pytest.mark.mermaid` |
| `test_no_lowercase_end_in_mermaid` | Zero lowercase `end` in mermaid node labels | `@pytest.mark.dogfood, @pytest.mark.mermaid` |
| `test_no_br_tags_in_mermaid` | Zero `<br/>` in mermaid blocks | `@pytest.mark.dogfood, @pytest.mark.mermaid` |
| `test_mermaid_health_score_above_threshold` | Health score >= 80 for entire docs/ | `@pytest.mark.dogfood, @pytest.mark.mermaid` |
| `test_mermaid_command_has_mcp_docs` | `/craft:docs:mermaid` documents MCP validation | `@pytest.mark.dogfood, @pytest.mark.structure` |
| `test_mermaid_linter_skill_has_mcp_rules` | Skill file includes MCP validation rules | `@pytest.mark.dogfood, @pytest.mark.structure` |
| `test_mkdocs_yml_has_mermaid_init_js` | `extra_javascript` includes `mermaid-init.js` | `@pytest.mark.dogfood, @pytest.mark.structure` |
| `test_mermaid_init_js_exists` | `docs/javascripts/mermaid-init.js` exists | `@pytest.mark.dogfood, @pytest.mark.structure` |
| `test_docs_check_command_mentions_mermaid` | Check command docs include mermaid phase | `@pytest.mark.dogfood, @pytest.mark.docs` |

## Known Risks (from session insights)

- **CDN cache propagation** — deployed fixes may not be visible for 5-10 minutes. Add cache-busting to deploy verification.
- **MCP server availability** — local regex fallback must handle 90% of cases if MCP is down
- **Pre-commit performance** — full MCP validation of all blocks may be slow. Consider validating only changed files.
- **mcp-mermaid stability** — pin version, test upgrades in CI before adopting

## Out of Scope

- Mermaid theme customization (use mkdocs-material defaults)
- Diagram complexity scoring (Phase 2)
- Auto-suggest layout direction (Phase 2)
- SVG/PNG export to docs (Phase 2)

## References

- [mcp-mermaid (hustcc)](https://github.com/hustcc/mcp-mermaid) — chosen MCP server
- [claude-mermaid (veelenga)](https://github.com/veelenga/claude-mermaid) — alternative with live reload
- [Mermaid Chart MCP (built-in V1)](https://mermaid.live/) — working but limited
- [mkdocs-material diagrams](https://squidfunk.github.io/mkdocs-material/reference/diagrams/) — native integration docs
