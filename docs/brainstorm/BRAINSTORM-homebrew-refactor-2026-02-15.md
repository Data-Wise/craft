# Homebrew Automation Refactor - Brainstorm

**Generated:** 2026-02-15
**Context:** craft plugin, /craft:dist:homebrew + CI + release skill
**Depth:** max | **Focus:** feature | **Agents:** backend-architect, devops-engineer

## Overview

Full audit and refactor of craft's Homebrew tap automation: commands, CI workflows, formula templates, and the release pipeline. Goal: close coverage gaps, codify hard-won lessons (sandbox, schema, Claude detection), and consolidate duplicated formula code across 14 tap entries.

---

## Current State

### Tap Inventory (14 formulas)

| Formula | Type | Has CI Caller? | Issues |
|---------|------|---------------|--------|
| craft | plugin | Yes | `shasum` not `sha256sum`, no retry |
| scholar | plugin | Yes | Bare `rescue` in post_install |
| rforge | plugin | No | Head-only, no tags |
| rforge-orchestrator | plugin (monorepo) | No | Missing Claude-running guard |
| workflow | plugin (monorepo) | No | Old-gen: uses `cp -r`, no marketplace |
| himalaya-mcp | plugin+npm | Yes | Most hardened formula |
| aiterm | python | Yes | Script injection vuln, no retry |
| atlas | python | Yes | Script injection vuln, no retry |
| nexus-cli | python | Yes | OK |
| flow-cli | shell | Yes | Script injection vuln, no retry |
| examark | npm | No | Needs npm source type |
| examify | npm | No | Deprecated |
| mcp-bridge | node | No | Standard github |
| scribe-cli | swift | No | No SHA, not released |

### Coverage Gap Summary

- **7/14** have CI caller workflows
- **Only 4** actually need new callers now (examark, mcp-bridge, rforge-orchestrator, workflow)
- **3 blocked**: rforge (no tags), examify (deprecated), scribe-cli (not released)

### Critical Bugs Found

1. **Script injection** in aiterm, atlas, flow-cli callers (direct `${{ github.event.inputs.version }}` in `run:`)
2. **Bare `rescue`** in scholar post_install catches everything
3. **Missing Claude-running guard** in rforge-orchestrator
4. **`shasum -a 256` vs `sha256sum`** inconsistency (4 callers use macOS command on Linux runners)
5. **No retry/empty-SHA guard** in 4 callers
6. **workflow.rb** uses `cp -r` pattern, no marketplace, no Claude detection

---

## Decisions Made (from 12 expert questions)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Scope | Full audit | Commands + close gaps + verify each formula |
| Subcommands | Review interactively | 8 → 6 (rename validate→audit, fold token→setup, drop release-batch) |
| CI template | Cross-reference | ci:generate homebrew delegates to dist:homebrew workflow |
| Tap update | Keep both paths | Local = fast dev, CI = automated releases |
| Workflow gen | Smart per-project | Detect plugin/python/node, customize metadata |
| Batch setup | One at a time | Run dist:homebrew setup per project |
| Source types | Add R + npm + cask | Expand reusable workflow |
| Validation | Audit + build test | --build flag for `brew install --build-from-source` |
| Marketplace | Include full registration | Symlink + manifest + settings.json |
| Deps scope | Both | Inter-formula + system deps matrix |
| Build test env | Local + warn | Fast feedback with env warnings |
| Formula name | Git remote + mapping | Map repo name → formula name |
| Lessons codified | Yes - all patterns | Sandbox, schema, Claude detection baked into template |
| Generator | Python script | Testable, like other craft utils |
| Output modes | Both (full + diff) | --diff for updates, default full |
| Build steps | Auto-detect | Check package.json, pyproject.toml, etc. |
| Retrofit | Plugins only | 4 plugin formulas to latest patterns |
| Nightly CI | Yes in spec | Weekly validation of all 14 formulas |

---

## Refactored Command Structure

### Before (8 subcommands)

`formula`, `workflow`, `validate`, `token`, `setup`, `update-resources`, `release-batch`, `deps`

### After (6 subcommands)

| Subcommand | Purpose | Change |
|-----------|---------|--------|
| `formula` | Generate or update formula | Keep |
| `workflow` | Generate CI caller workflow | Keep (now smart per-project) |
| `audit` | Validate with brew audit | Renamed from `validate` |
| `setup` | Full wizard (formula+workflow+token+commit) | Keep (now includes token guide) |
| `update-resources` | Fix stale PyPI URLs | Keep |
| `deps` | Formula dependency + system deps graph | Keep (expanded scope) |

**Dropped:** `release-batch` (too niche), `token` (folded into `setup` step 4)

---

## Architecture: Formula Generator

### Design: YAML Manifest + Python Generator

```
homebrew-tap/
  generator/
    generate.py           # Reads manifest, produces Formula/*.rb
    manifest.yml          # Single source of truth for all 14 formulas
    blocks/               # Composable bash/ruby blocks
      install-header.sh
      schema-cleanup.sh
      symlink.sh
      marketplace.sh
      claude-detection.sh
      branch-guard.sh
      uninstall.sh
  Formula/                # Generated output (committed)
```

### Manifest Structure (per formula)

```yaml
craft:
  type: claude-plugin
  desc: "Full-stack toolkit for Claude Code with {command_count} commands"
  source: github
  features:
    schema_cleanup: true
    branch_guard: true
    marketplace: true
    claude_detection: true
  dynamic_counts: [commands, agents, skills]
  test_paths: [.claude-plugin/plugin.json, commands, skills, agents]
```

### Generator Principle

**Generator owns structure. CI workflow owns version numbers.**

| Concern | Owner |
|---------|-------|
| Ruby class, install method, test block | Generator |
| Install script (bash heredoc) | Generator (composed from blocks) |
| `url`, `sha256`, `version` strings | CI workflow (sed) |
| Dynamic counts | CI workflow (sed) |

### Scope

- **Generate:** 5 plugin formulas (craft, scholar, rforge, workflow, himalaya-mcp)
- **Hand-craft:** 9 other formulas (different enough)
- **Validate all:** CI checks all 14

---

## CI/CD Improvements

### 1. Fix Existing Callers (Security + Reliability)

- **Script injection fix**: Use `env:` indirection in all callers
- **Standardize SHA**: `sha256sum` everywhere (not `shasum -a 256`)
- **Add retry + empty-SHA guard** to all callers
- **Fix bare `rescue`** in scholar post_install
- **Add Claude-running guard** to rforge-orchestrator

### 2. Expand Reusable Workflow

Add source types to `update-formula.yml`:

| Source | URL Pattern | Sed Pattern |
|--------|------------|-------------|
| github | `/vX.Y.Z.tar.gz` | Current |
| pypi | `/package-X.Y.Z.tar.gz` | Current |
| npm | `/package-X.Y.Z.tgz` | New |
| cran | `/Package_X.Y.Z.tar.gz` | New |

### 3. New Caller Workflows (4 projects)

| Project | Source | Formula Name |
|---------|--------|-------------|
| examark | npm | examark |
| mcp-bridge | github | mcp-bridge |
| rforge-orchestrator | github | rforge-orchestrator |
| workflow (claude-plugins) | github | workflow |

### 4. Weekly Validation Workflow (new in tap repo)

`validate-formulas.yml`:

- Runs on `macos-latest` (needed for brew build)
- Discovers all formulas
- Runs `brew audit --strict`
- Verifies URLs are reachable
- SHA256 verification
- `brew install --build-from-source` for testable formulas
- Summary report

### 5. Auth Migration (future)

Current: Fine-grained PAT (90-day rotation, manual)
Recommended: GitHub App (`actions/create-github-app-token@v1`)

- Auto-rotating
- No manual rotation
- Properly scoped

---

## Release Skill Updates

### Step 8.5 Improvements

1. **Formula name lookup**: Git remote → mapping table (not `basename $PWD`)
2. **Both paths preserved**: Local sed for dev, CI for automated
3. **Local path now triggers validation**: After sed, run `ruby -c` syntax check

### Formula Name Mapping

Store in `.craft/homebrew.json` or detect from git remote:

```json
{
  "formula_name": "craft",
  "tap": "data-wise/tap",
  "source_type": "github"
}
```

Fallback chain: `.craft/homebrew.json` → git remote mapping → `basename $PWD`

---

## Codified Patterns (from himalaya-mcp lessons)

### Pattern 1: macOS Sandbox Workaround

`post_install` CANNOT write to `$HOME`. All symlink/registration logic goes in the install script (bash heredoc), invoked manually via `{name}-install`.

### Pattern 2: plugin.json Schema Cleanup

Dual defense:

1. Ruby `JSON.parse` + `slice(*allowed_keys)` in `post_install` (works during build)
2. Python one-liner fallback in install script (works at user runtime)

### Pattern 3: Claude Detection

Before modifying `settings.json`:

```bash
CLAUDE_RUNNING=false
if pgrep -x "claude" >/dev/null 2>&1; then
    CLAUDE_RUNNING=true
fi
```

Skip auto-enable if Claude is running (avoids file lock conflicts).

### Pattern 4: Marketplace Registration

Full: symlink to `local-marketplace/` + update `marketplace.json` manifest + auto-enable in `settings.json`

### Pattern 5: Retry + SHA Guard (CI)

```bash
EMPTY_SHA="e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
for attempt in 1 2 3 4 5; do
    curl -sL --max-time 60 -o "$TMPFILE" "$URL"
    SHA256=$(sha256sum "$TMPFILE" | cut -d' ' -f1)
    [ "$SHA256" != "$EMPTY_SHA" ] && break
    sleep 15
done
```

---

## Live Audit Results (brew audit --strict)

**Only 1/14 passes: craft.** 57 total issues across 13 formulas.

| Formula | # | Key Issues |
|---------|---|-----------|
| craft | 0 | CLEAN |
| scholar | 1 | modifier `if` |
| himalaya-mcp | 2 | redundant begin, annotation |
| rforge | 3 | license order, Array#include?, assert |
| rforge-orchestrator | 2 | assert, caveats order |
| workflow | 9 | redundant version, 6x assert_predicate |
| aiterm | 3 | URL refs/tags, pkgshare |
| atlas | 4 | desc length, dep order, spacing, assert |
| nexus-cli | 3 | PyPI URL, missing libyaml, caveats order |
| examark | 1 | deprecated npm args |
| examify | 1 | deprecated npm args |
| flow-cli | 1 | man page location |
| mcp-bridge | 16 | desc starts with name, whitespace, npm args |
| scribe-cli | 11 | empty SHA, version redundancy, whitespace |

### Additional Decisions (from deep-dive round)

| Decision | Choice |
|----------|--------|
| Generator location | Both repos (source in tap, craft calls it) |
| GitHub App | Do in Increment 4 |
| workflow.rb | Full rewrite via generator |
| rforge | Start tagging releases |
| New caller workflows | Save for implementation |

---

## Quick Wins (< 30 min each)

1. Fix script injection in 3 callers (env: indirection)
2. Fix `shasum` → `sha256sum` in 4 callers
3. Fix bare `rescue` in scholar post_install
4. Add Claude-running guard to rforge-orchestrator
5. Rename `validate` → `audit` in homebrew.md

## Medium Effort (1-4 hours)

6. Add npm + cran source types to update-formula.yml
7. Create 4 missing caller workflows
8. Build formula name mapping for release skill
9. Update homebrew.md command docs (6 subcommands)

## Large Effort (1-2 days)

10. Build Python formula generator (manifest + blocks)
11. Retrofit 4 plugin formulas to use generator
12. Create weekly validation workflow in tap repo
13. Comprehensive spec for all changes

## Future (separate session)

14. Migrate PAT auth to GitHub App
15. Add `brew audit` step to reusable workflow
16. Add `--build` flag to /craft:dist:homebrew audit

---

## Recommended Path

Start with quick wins (items 1-5) as immediate security/reliability fixes. Then build the generator (item 10) as it unlocks items 6-9 and 11-12. The spec should cover all 13 items with the generator as the centerpiece.

## Next Steps

1. [ ] Generate formal SPEC from this brainstorm
2. [ ] Create worktree for implementation
3. [ ] Quick wins first (security fixes)
4. [ ] Generator + retrofit
5. [ ] CI expansion
