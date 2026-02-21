# Mermaid MCP Integration — Orchestration Plan

> **Branch:** `feature/mermaid-mcp`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-mermaid-mcp`
> **Spec:** `docs/specs/SPEC-mermaid-mcp-integration-2026-02-21.md`
> **Version Target:** TBD (next minor)

## Objective

Integrate mcp-mermaid (hustcc) as the validation backbone for all Mermaid diagrams in the docs pipeline. Add local regex pre-checks, auto-fix engine, health score metric, and NL diagram creation with live browser preview. Goal: never ship broken diagrams again.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|-----------|----------|--------|--------|
| 1 | MCP Server Setup + Local Regex Engine | High | 2-3h | |
| 2 | Validation Pipeline Integration | High | 3-4h | |
| 3 | Auto-Fix Engine | Medium | 2-3h | |
| 4 | Health Score + Release Gate | Medium | 2h | |
| 5 | NL Diagram Creation + Live Preview | Low | 3-4h | |
| 6 | Documentation + Tests | High | 3-4h | |

## Phase 1: MCP Server Setup + Local Regex Engine

**Scope:** Install mcp-mermaid, create the regex pre-check module, and validate against existing docs.

- [ ] 1.1 Configure mcp-mermaid in `.claude/settings.json` (or project MCP config)
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
- [ ] 1.2 Create `scripts/mermaid-validate.py` — extract all mermaid blocks from markdown files
      - Parse ```` ```mermaid ```` fenced blocks
      - Return list of `(file, line_number, block_content)` tuples
      - Ignore non-mermaid fenced blocks
- [ ] 1.3 Add local regex pre-checks to `mermaid-validate.py`
      - `[/text]` leading slash detection
      - Lowercase `end` keyword in node labels
      - Unquoted colons in node labels
      - `<br/>` tags in node labels
      - Deprecated `graph` directive (should be `flowchart`)
- [ ] 1.4 Verify: run against all 152+ existing mermaid blocks with zero false positives

**Key files:**

- `scripts/mermaid-validate.py` (NEW)
- `.claude/settings.json` or project MCP config (UPDATE)

**Verification:**

```bash
python3 scripts/mermaid-validate.py docs/
# Should report 0 issues (all existing blocks are clean after previous fixes)
```

## Phase 2: Validation Pipeline Integration

**Scope:** Wire mermaid validation into `/craft:docs:check` and pre-commit hooks.

- [ ] 2.1 Add "Mermaid Validation" phase to `/craft:docs:check` command
      - After existing phases (links, stale, nav)
      - Extract blocks → run regex pre-checks → call MCP validation → report results
- [ ] 2.2 Update `commands/docs/check.md` to document the new Mermaid Validation phase
- [ ] 2.3 Add pre-commit hook for mermaid validation on changed `.md` files
      - Only validate mermaid blocks in files being committed
      - Local regex only (fast, no MCP dependency for pre-commit)
      - Fall back gracefully if no mermaid blocks found
- [ ] 2.4 Update pre-commit config (`.pre-commit-config.yaml` or hook scripts)

**Key files:**

- `commands/docs/check.md` (UPDATE)
- `scripts/mermaid-validate.py` (UPDATE — add CLI mode for pre-commit)
- `.pre-commit-config.yaml` or `scripts/hooks/` (UPDATE)

**Verification:**

```bash
# Test check command includes mermaid phase
/craft:docs:check

# Test pre-commit catches bad mermaid
echo '```mermaid
graph TB
A[/broken] --> B
```' > /tmp/test-bad-mermaid.md
python3 scripts/mermaid-validate.py /tmp/test-bad-mermaid.md
# Should report: [/broken] leading slash detected
```

## Phase 3: Auto-Fix Engine

**Scope:** Create `scripts/mermaid-autofix.py` to automatically fix known safe patterns.

- [ ] 3.1 Create `scripts/mermaid-autofix.py` with safe auto-fix rules:
  - Leading `/` in labels: `[/text]` -> `["/text"]`
  - Lowercase `end`: `[end]` -> `[End]`
  - Unquoted colons: `[a:b]` -> `["a:b"]`
  - `<br/>` tags -> markdown strings
  - Deprecated `graph` -> `flowchart`

- [ ] 3.2 Add report-only rules (no auto-fix):
      - Long node text (>20 chars) — suggest abbreviation
      - Orphaned nodes — suggest connection
      - Complex horizontal layouts (LR with >5 nodes) — suggest TD
- [ ] 3.3 Wire auto-fix into `/craft:docs:check` (with `--fix` flag)
      - Default: report only
      - `--fix`: apply safe auto-fixes and report remaining issues

**Key files:**

- `scripts/mermaid-autofix.py` (NEW)
- `scripts/mermaid-validate.py` (UPDATE — import autofix module)

**Verification:**

```bash
# Test auto-fix on known patterns
python3 scripts/mermaid-autofix.py --test
# Should show: 5 safe fixes applied, 3 report-only items

# Verify clean diagrams are unchanged
python3 scripts/mermaid-autofix.py docs/ --dry-run
# Should report: 0 changes needed (all blocks already clean)
```

## Phase 4: Health Score + Release Gate

**Scope:** Implement composite health score metric and wire into release pipeline.

- [ ] 4.1 Add health score calculation to `mermaid-validate.py`:
      ```
      health_score = (
          syntax_validity * 0.5 +     # % blocks passing MCP validation
          best_practices * 0.3 +      # % blocks following all lint rules
          rendering_success * 0.2     # % blocks rendering to SVG
      )
      ```
- [ ] 4.2 Display health score in `/craft:docs:check` output
      - >= 90: Good (green)
      - >= 80: Warning (yellow) — passes release gate
      - < 80: Fail (red) — blocks release
- [ ] 4.3 Add health score gate to `/craft:site:deploy` and `/craft:check --for release`
      - Configurable threshold (default 80)
      - Skip with `--skip-mermaid` flag for emergencies

**Key files:**

- `scripts/mermaid-validate.py` (UPDATE — add health score)
- `commands/docs/check.md` (UPDATE — health score output)
- Release pipeline integration points (UPDATE)

**Verification:**

```bash
python3 scripts/mermaid-validate.py docs/ --health-score
# Should output: Mermaid Health Score: 95/100 (Good)
```

## Phase 5: NL Diagram Creation + Live Preview

**Scope:** Extend `/craft:docs:mermaid` command with natural language generation and live browser preview.

- [ ] 5.1 Update `commands/docs/mermaid.md` to support NL input:
      ```bash
      /craft:docs:mermaid "show the release pipeline from dev to main"
      ```
      - Claude generates Mermaid code from description
      - mcp-mermaid validates + renders
      - Output to file or clipboard
- [ ] 5.2 Add `--preview` flag for live browser preview:
      - Render to SVG via mcp-mermaid
      - Open in browser for visual inspection
      - User iterates via conversation
- [ ] 5.3 Update `mermaid-expert` agent with MCP rendering capability
      - Agent can validate diagrams via MCP
      - Agent can render to SVG/PNG for preview

**Key files:**

- `commands/docs/mermaid.md` (UPDATE)
- `agents/mermaid-expert.md` (UPDATE — if exists, or skills)
- `skills/docs/mermaid-linter/SKILL.md` (UPDATE — add MCP validation rules)

**Verification:**

```bash
# Test NL generation (manual — requires Claude interaction)
/craft:docs:mermaid "auth flow with OAuth2"
# Should generate valid mermaid code, validate via MCP

# Test preview (manual — requires browser)
/craft:docs:mermaid "simple flowchart" --preview
# Should open rendered diagram in browser
```

## Phase 6: Documentation + Tests

**Scope:** Write all documentation deliverables and test suites from the spec.

- [ ] 6.1 Update documentation files:
  - `commands/docs/mermaid.md` — add NL creation usage, MCP validation, `--preview`
  - `skills/docs/mermaid-linter/SKILL.md` — add MCP validation rules, health score
  - `commands/docs/check.md` — document Mermaid Validation phase
  - `docs/guide/mermaid-authoring.md` (NEW) — end-to-end guide
  - `docs/REFCARD.md` — health score and lint rules quick reference
  - `CHANGELOG.md` — feature entry
  - `mkdocs.yml` — add guide page to navigation

- [ ] 6.2 Create unit tests (`tests/test_mermaid_validation.py`) — 15 tests
      - Regex detection tests (5)
      - Auto-fix tests (5)
      - Health score tests (3)
      - Block extraction tests (2)
- [ ] 6.3 Create e2e tests (`tests/test_mermaid_e2e.py`) — 8 tests
      - MCP validation (2)
      - docs:check integration (2)
      - Auto-fix + validation (1)
      - Pre-commit hook (1)
      - Skill/command structure (2)
- [ ] 6.4 Create dogfood tests (`tests/test_mermaid_dogfood.py`) — 10 tests
      - All docs blocks valid syntax (1)
      - No leading slash patterns (1)
      - No lowercase end (1)
      - No br tags (1)
      - Health score above threshold (1)
      - Command/skill docs updated (3)
      - mkdocs config correct (2)

**Key files:**

- `tests/test_mermaid_validation.py` (NEW)
- `tests/test_mermaid_e2e.py` (NEW)
- `tests/test_mermaid_dogfood.py` (NEW)
- `docs/guide/mermaid-authoring.md` (NEW)
- All doc files listed in 6.1

**Verification:**

```bash
python3 -m pytest tests/test_mermaid_validation.py -v
python3 -m pytest tests/test_mermaid_e2e.py -v -m "not mermaid"  # Skip MCP-dependent tests initially
python3 -m pytest tests/test_mermaid_dogfood.py -v
```

## Friction Prevention (from session insights)

- **Context first**: Read this ORCHESTRATE file and the spec at `docs/specs/SPEC-mermaid-mcp-integration-2026-02-21.md` BEFORE starting work
- **Verify location**: Confirm CWD is the worktree (`~/.git-worktrees/craft/feature-mermaid-mcp`), not the main repo
- **No autonomous starts**: After each phase, STOP and confirm before proceeding
- **Test per phase**: Run tests after each phase to catch regressions
- **MCP availability**: mcp-mermaid requires `npx` — verify Node.js is available before Phase 1
- **Pre-commit hooks**: markdownlint may auto-fix files on commit — re-stage if commit fails
- **Mermaid `[/` gotcha**: All existing `[/text]` patterns were fixed in v2.24.0 — don't reintroduce them

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

## Commit Strategy

- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `refactor:`, `chore:`
- Phase 1: `feat(mermaid): add validation script with regex pre-checks`
- Phase 2: `feat(mermaid): integrate validation into docs:check pipeline`
- Phase 3: `feat(mermaid): add auto-fix engine for safe patterns`
- Phase 4: `feat(mermaid): add health score metric and release gate`
- Phase 5: `feat(mermaid): add NL diagram creation and live preview`
- Phase 6: `docs(mermaid): add guide, tests, and documentation updates`

## Verification

After each phase:

```bash
# Run existing tests (no regressions)
python3 -m pytest tests/ -x -q --tb=short

# Validate plugin structure
./scripts/validate-counts.sh

# Check mermaid-specific tests (Phase 6+)
python3 -m pytest tests/test_mermaid_validation.py -v
python3 -m pytest tests/test_mermaid_dogfood.py -v
```

## Session Instructions

### Context

You are in the **craft repo worktree** for the Mermaid MCP integration feature. The spec at `docs/specs/SPEC-mermaid-mcp-integration-2026-02-21.md` has the full design details including lint rules, health score formula, and test plans.

### How to Start

```bash
cd ~/.git-worktrees/craft/feature-mermaid-mcp
claude
```

On session start, paste:

> Read `ORCHESTRATE-mermaid-mcp.md` and the spec at `docs/specs/SPEC-mermaid-mcp-integration-2026-02-21.md`. Start Phase 1.

### Phase-by-Phase

1. Read current state of each file listed in the phase
2. Implement changes per the spec design
3. Run verification after each phase
4. Commit in logical groups
5. STOP and confirm before next phase
