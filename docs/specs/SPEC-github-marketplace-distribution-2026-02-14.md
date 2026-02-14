# SPEC: Marketplace Distribution & Release Integration

**Date:** 2026-02-14
**Status:** Draft
**Author:** DT + Claude
**From Brainstorm:** `docs/brainstorm/BRAINSTORM-marketplace-commands-2026-02-14.md`

## Overview

Add Claude Code marketplace distribution as a first-class channel alongside Homebrew. Create a new `/craft:dist:marketplace` command, update the release skill to auto-detect and bump marketplace.json, fix Homebrew formula templates for `brew audit --strict` compliance, and add tap auto-update to the release pipeline.

## Primary User Story

**As a** plugin developer distributing a Claude Code plugin,
**I want** marketplace distribution managed through craft commands,
**So that** users can install my plugin via `/plugin marketplace add` without needing Homebrew, and my release pipeline handles both channels automatically.

### Acceptance Criteria

- [ ] `/craft:dist:marketplace init` generates a valid `marketplace.json` from `plugin.json`
- [ ] `/craft:dist:marketplace validate` runs `claude plugin validate .` and reports results
- [ ] `/craft:dist:marketplace test` does a local install/uninstall cycle
- [ ] `/craft:dist:marketplace publish` tags and pushes to make marketplace installable
- [ ] `/release` auto-detects `marketplace.json` and bumps version during Step 3
- [ ] `/release` pre-flight includes `claude plugin validate .` (Step 2)
- [ ] `/release` auto-updates Homebrew tap formula (new Step 8.5)
- [ ] All Homebrew formula templates pass `brew audit --strict`
- [ ] `.claude-plugin/` auto-detected as Claude Code plugin formula type
- [ ] Installation docs recommend marketplace for new users, Homebrew for power users

## Secondary User Stories

**As a** craft user running `/release`,
**I want** the release pipeline to automatically update both marketplace.json and the Homebrew tap formula,
**So that** I don't have to manually sync versions across distribution channels.

**As a** new craft user on Linux,
**I want** to install craft via `/plugin marketplace add Data-Wise/craft`,
**So that** I can use craft without Homebrew (macOS-only).

## Architecture

### New Command: `/craft:dist:marketplace`

```
commands/dist/marketplace.md
```

#### Subcommands

| Subcommand | Purpose | Key Actions |
|------------|---------|-------------|
| `init` | Generate marketplace.json | Read plugin.json, prompt for marketplace name, generate `.claude-plugin/marketplace.json` |
| `validate` | Validate marketplace | Run `claude plugin validate .`, report errors/warnings |
| `test` | Local install test | `/plugin marketplace add ./`, install, verify commands load, uninstall |
| `publish` | Push to GitHub | Verify clean tree, tag if needed, `git push`, show install command |

#### init Subcommand Detail

```bash
/craft:dist:marketplace init
```

1. Read `.claude-plugin/plugin.json` for name, version, description, author
2. Prompt: "Marketplace name?" (suggest `{org}-{plugin}`, e.g., `data-wise-craft`)
3. Generate `.claude-plugin/marketplace.json`:
   - `$schema`, `name`, `owner` from plugin.json author
   - `metadata.description` from plugin.json description (truncated to 1 line)
   - `metadata.version` from plugin.json version
   - Single plugin entry with `"source": "./"`, homepage, repository, license, category, tags
4. Run `claude plugin validate .` to verify
5. Show install command: `/plugin marketplace add {owner}/{repo}`

#### validate Subcommand Detail

```bash
/craft:dist:marketplace validate
```

1. Check `.claude-plugin/marketplace.json` exists
2. Run `claude plugin validate .`
3. Parse output for errors vs warnings
4. Check version consistency: marketplace.json version == plugin.json version
5. Report results in box-drawing format

#### test Subcommand Detail

```bash
/craft:dist:marketplace test
```

1. Run validate first (fail fast)
2. `/plugin marketplace add ./` (local path)
3. Check plugin appears in `/plugin` installed list
4. Verify key commands are discoverable (check a few command files exist in cache)
5. `/plugin uninstall {name}@{marketplace}`
6. Report pass/fail

#### publish Subcommand Detail

```bash
/craft:dist:marketplace publish
```

1. Run validate
2. Verify git working tree is clean
3. Verify current branch is `dev` or `main`
4. Show install command user would run
5. Confirm with user before pushing
6. `git push`
7. Display: "Users can now install with: `/plugin marketplace add {owner}/{repo}`"

### Release Skill Updates

#### Step 2 (Pre-Flight): Add Marketplace Validation

Add to Step 2a after `/craft:check --for release`:

```bash
# If marketplace.json exists, validate it
if [ -f ".claude-plugin/marketplace.json" ]; then
    claude plugin validate .
fi
```

#### Step 3 (Version Bump): Add marketplace.json

Add to the version bump files table:

| Project Type | Files to Update |
|-------------|-----------------|
| Craft plugin | `.claude-plugin/plugin.json`, **`.claude-plugin/marketplace.json`** (if exists), `CLAUDE.md`, `README.md`, ... |

Auto-detect logic:

```python
if os.path.exists(".claude-plugin/marketplace.json"):
    # Bump metadata.version
    # Bump plugins[0].version (if present)
```

#### Step 8.5 (NEW): Update Homebrew Tap

After docs deploy, before dev sync:

```bash
# Step 8.5: Update Homebrew tap formula
TAP_LOCAL="$HOME/projects/dev-tools/homebrew-tap"
TAP_REMOTE="https://github.com/Data-Wise/homebrew-tap.git"

if [ -d "$TAP_LOCAL" ]; then
    TAP_DIR="$TAP_LOCAL"
    cd "$TAP_DIR" && git pull
else
    TAP_DIR=$(mktemp -d)
    git clone "$TAP_REMOTE" "$TAP_DIR"
fi

FORMULA="$TAP_DIR/Formula/<name>.rb"
if [ -f "$FORMULA" ]; then
    # Calculate new SHA256 from GitHub release tarball
    SHA256=$(curl -sL "https://github.com/<owner>/<repo>/archive/refs/tags/v<version>.tar.gz" | shasum -a 256 | cut -d' ' -f1)

    # Update version and sha256 in formula
    # Use sed or python to update url and sha256 lines

    # Commit and push
    cd "$TAP_DIR"
    git add "Formula/<name>.rb"
    git commit -m "<name>: update to v<version>"
    git push
fi
```

**Tap location strategy:** Check `$HOME/projects/dev-tools/homebrew-tap/` first (DT's layout). If not found, check `$(brew --repository)/Library/Taps/data-wise/homebrew-tap/`. Fall back to temp clone.

### Homebrew Template Fixes

Update all formula templates in `commands/dist/homebrew.md` for `brew audit --strict`:

| Fix | Before | After |
|-----|--------|-------|
| Array comparison | `f == "." \|\| f == ".."` | `%w[. .. .git].include?(f)` |
| Hash filtering | `data.select { \|k, _\| ... }` | `data.slice(*allowed_keys)` |
| Modifier if | Multi-line if/end | Single-line modifier `if` |
| Assertion | `assert_predicate :exist?` | `assert_path_exists` |
| Section order | `test` before `caveats` | `caveats` before `test` |
| Description | > 80 chars | < 80 chars |

### Claude Code Plugin Formula Type

Add auto-detection for `.claude-plugin/` directory in `/craft:dist:homebrew formula`:

| Project Type | Detection | Formula Pattern |
|--------------|-----------|-----------------|
| **Claude Code Plugin** | `.claude-plugin/plugin.json` | `libexec.install` + symlink script + `post_install` |
| Python | `pyproject.toml` | `Language::Python::Virtualenv` |
| Node.js | `package.json` | npm install pattern |
| ... | ... | ... |

Detection priority: Claude Code Plugin > Python > Node > Go > Rust > Shell

The generated plugin formula should:

- Use `libexec.install` for all files
- Generate `{name}-install` and `{name}-uninstall` wrapper scripts
- Include Claude detection (lsof/pgrep check)
- Pass `brew audit --strict` out of the box
- Include `post_install` with auto-install
- Include `caveats` with manual install instructions
- Include `test` with `assert_path_exists`

## API Design

N/A - No API changes. These are CLI commands.

## Data Models

### marketplace.json (created by `init`)

**Note:** The `$schema` URL (`https://anthropic.com/claude-code/marketplace.schema.json`) returns 404 — open issue [#9686](https://github.com/anthropics/claude-code/issues/9686). Omit `$schema` field.

```json
{
  "name": "{org}-{plugin}",
  "owner": {
    "name": "{author.name from plugin.json}",
    "email": "{author.email from plugin.json}"
  },
  "metadata": {
    "description": "{description from plugin.json, truncated}"
  },
  "plugins": [
    {
      "name": "{name from plugin.json}",
      "source": "./",
      "description": "{description, 1 line}",
      "version": "{version from plugin.json}",
      "author": { "name": "...", "email": "..." },
      "homepage": "{from repo or docs site}",
      "repository": "{git remote origin URL}",
      "license": "{from LICENSE file or plugin.json}",
      "category": "development",
      "keywords": ["{relevant tags}"]
    }
  ]
}
```

**Schema notes:**

- `metadata.version` not standard — version goes on each plugin entry only
- `keywords` (not `tags`) for plugin discovery. `tags` is marketplace-level (e.g., `"community-managed"`)
- `source: "./"` for single-plugin repos. GitHub source objects (`{ "source": "github", "repo": "..." }`) for multi-plugin marketplaces
- Categories: `development`, `productivity`, `learning`, `testing`, `security`, `database`, `monitoring`, `deployment`, `design`

## Dependencies

- `claude` CLI (for `claude plugin validate .`)
- `git` (for publish subcommand)
- `gh` CLI (for release skill tap update)
- `curl` + `shasum` (for SHA256 calculation in tap update)
- `jq` (optional, for JSON manipulation)

## UI/UX Specifications

### Command Output Format

All subcommands use box-drawing format consistent with craft conventions:

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace init                                 │
├─────────────────────────────────────────────────────────────┤
│ Plugin: craft v2.18.0                                        │
│ Marketplace: data-wise-craft                                 │
│ Source: ./                                                   │
├─────────────────────────────────────────────────────────────┤
│ Created: .claude-plugin/marketplace.json                     │
│ Validated: claude plugin validate . ... PASSED               │
├─────────────────────────────────────────────────────────────┤
│ Install with:                                                │
│   /plugin marketplace add Data-Wise/craft                    │
│   /plugin install craft@data-wise-craft                      │
└─────────────────────────────────────────────────────────────┘
```

### Installation Docs Hierarchy

**Recommended (new users):** Marketplace

```
/plugin marketplace add Data-Wise/craft
/plugin install craft@data-wise-craft
```

**Power users (macOS):** Homebrew

```
brew install data-wise/tap/craft
```

**Manual:** Direct symlink

```
git clone ... && ln -sf ...
```

## Additional Decisions (from follow-up questions)

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Plugin formula template | Full featured | Include branch guard, marketplace registration, Claude detection, auto-enable |
| `/craft:dist:homebrew validate` | Validate + auto-fix | Auto-fix known `brew audit` patterns (desc, Array#include?, section order, assertions) |

### Homebrew Validate Auto-Fix Patterns

`/craft:dist:homebrew validate` should detect and auto-fix these common `brew audit` issues:

| Pattern | Detection | Fix |
|---------|-----------|-----|
| desc > 80 chars | `desc "..."` line length check | Truncate or suggest shorter desc |
| `f == "." \|\| f == ".."` | Regex match on reject block | Replace with `%w[. .. .git].include?(f)` |
| `data.select { \|k, _\| ... }` | Regex match | Replace with `data.slice(*keys)` |
| Multi-line if/end (single body) | AST-like detection | Convert to modifier `if` |
| `assert_predicate :exist?` | Literal match | Replace with `assert_path_exists` |
| `test` before `caveats` | Section order detection | Reorder `caveats` before `test` |

## Open Questions

1. ~~Should `metadata.version` track independently?~~ **Resolved:** Keep in sync, auto-bump during release.
2. ~~Which branch-guard gap option?~~ **Resolved:** Option A (README instructions) for now. SessionStart hook as future enhancement.
3. ~~Plugin formula template scope?~~ **Resolved:** Full featured (all features).
4. ~~Validate auto-fix?~~ **Resolved:** Always auto-fix known patterns.
5. ~~Should the `publish` subcommand also create a GitHub release, or just push?~~ **Resolved:** Push only. `publish` pushes + displays install command. Tagging and GitHub releases are `/release`'s responsibility.

## Review Checklist

- [ ] marketplace.json schema matches Claude Code docs
- [ ] All Homebrew templates pass `brew audit --strict`
- [ ] Release skill handles missing marketplace.json gracefully (no-op)
- [ ] Tap update handles missing local tap (falls back to clone)
- [ ] `init` generates valid marketplace.json on first run
- [ ] `validate` catches version mismatches
- [ ] `test` cleans up after itself (no leftover marketplace registrations)
- [ ] No hardcoded paths (use `$(brew --prefix)`, `$HOME`, etc.)
- [ ] Documentation recommends marketplace first, Homebrew second

## Coordination Notes

**Release skill overlap:** Both this spec and `SPEC-insights-driven-improvements-2026-02-14.md` modify `skills/release/SKILL.md`. This spec adds Steps 2c, 3 (marketplace bump), and 8.5 (tap update). The insights spec adds `--autonomous` flag. These touch different sections — no conflict — but should be implemented in the same feature branch or coordinated to avoid merge conflicts.

**Homebrew audit fixes:** The 6 `brew audit --strict` fixes listed in the Architecture section were already applied to the actual formula in commit `63b11d2`. The template fixes in `commands/dist/homebrew.md` may be partially done — verify during implementation.

## Implementation Notes

### File Changes Summary

| File | Action | Size |
|------|--------|------|
| `commands/dist/marketplace.md` | CREATE | ~200 lines |
| `commands/dist/homebrew.md` | UPDATE | Fix templates + add plugin type |
| `skills/release/SKILL.md` | UPDATE | Add Steps 2c, 3 marketplace bump, 8.5 tap update |
| `.claude-plugin/marketplace.json` | CREATE | ~30 lines |
| `docs/guide/homebrew-installation.md` | UPDATE | Add marketplace as recommended path |
| `README.md` | UPDATE | Installation section |
| `CLAUDE.md` | UPDATE | Version, counts if changed |
| `scripts/pre-release-check.sh` | UPDATE | Add marketplace.json version check |

### Implementation Order

1. Create `marketplace.json` (quick win, unblocks testing)
2. Create `commands/dist/marketplace.md` (new command)
3. Update `commands/dist/homebrew.md` (template fixes + plugin type)
4. Update `skills/release/SKILL.md` (marketplace bump + tap update)
5. Update `scripts/pre-release-check.sh` (marketplace validation)
6. Update docs (README, installation guide, CLAUDE.md)

## History

| Date | Change |
|------|--------|
| 2026-02-14 | Initial spec from deep brainstorm (8 questions) |
| 2026-02-14 | Schema verified (no $schema URL, keywords not tags, version on plugin entry). Resolved Q5 (publish=push only). Added coordination notes for release skill overlap. |
