# SPEC: Multi-surface plugin distribution — `/craft:dist:surfaces` + Cowork verify-surfaces leg

**Status:** SUBSUMED by [SPEC-release-multisurface-2026-06-26.md](SPEC-release-multisurface-2026-06-26.md) (2026-06-26) — the release-revamp made the surface *registry* the core; this spec's `/craft:dist:surfaces` command (D1), Cowork verify leg (D2), name-match (D3), and dist-extras reference (D4) are folded in there as registry views/steps. Kept for the standalone framing; implement via the umbrella spec.
**Source:** `/craft:workflow:brainstorm` (deep) — learnings from the 2026-06-26 session
**Related issues:** [craft#218](https://github.com/Data-Wise/craft/issues/218) (aggregator-sync no-op), [craft#184](https://github.com/Data-Wise/craft/issues/184) (dist public/private + pin-refresh), [himalaya-mcp#67](https://github.com/Data-Wise/himalaya-mcp/issues/67) (plugin-name mismatch)

---

## 1. Problem

craft's distribution tooling models **one surface** (Claude Code + Homebrew). This session surfaced **three** plugin surfaces with different rules, and craft has no coverage for two of them. Three concrete failures resulted, all silent:

1. **Aggregator drift undetected** — `Data-Wise/claude-plugins` was 14 craft minors / a full scholar major behind, because Step 10d aggregator-sync is a green-check no-op (gated on an unset env var) and verify-surfaces skips the aggregator leg when unconfigured.
2. **Cowork is invisible** — verify-surfaces checks Code/tap/brew/marketplace/git-tag, never the Cowork store. Cowork drift (e.g. the stuck savant pin) can't be seen at release.
3. **Name mismatch = silent unresolvable** — the aggregator named a plugin `himalaya-mcp`; its repo declares `email`. The entry never resolved in any catalog, with no error.

## 2. The three-surface model (the durable knowledge)

| Surface | Store | Holds | craft fit |
|---------|-------|-------|-----------|
| **Code** | `~/.claude/plugins` (`installed_plugins.json`) | commands + agents + skills + MCP + hooks | ✅ full (craft lives here) |
| **Cowork** | `…/local-agent-mode-sessions/<s>/<s>/cowork_plugins/` (`known_marketplaces.json`, `cache/`, `installed_plugins.json`) | **skills + connectors only** | skill-first plugins only — craft (command/agent-centric) does NOT surface |
| **Desktop Extensions** | `…/Claude/Claude Extensions/` (`extensions-installations.json`) | DXT/MCP servers | N/A for craft |

Add paths: **Code** = `+` next to prompt → Plugins → Add plugin (or `claude plugin marketplace add owner/repo`). **Cowork** = Customize → **Skills** → Personal plugins → `+` → Add marketplace from GitHub. **Personal** marketplace accepts public OR private; **Org** marketplace is private-only.

## 3. Locked decisions (from brainstorm)

| # | Decision | Detail |
|---|----------|--------|
| **D1** | **New command** | `/craft:dist:surfaces` — read-only detect + report which surfaces each (Data-Wise) plugin is on, with versions. Fits the `dist:*` family; discoverable via hub. |
| **D2** | **Cowork leg in verify-surfaces** | Extend `scripts/verify-surfaces.sh` to read the Cowork store (`cowork_plugins/known_marketplaces.json` + `installed_plugins.json`) as a **warn-not-block** leg (Cowork is a manual surface) — so Cowork drift is visible at release. |
| **D3** | **Name-match assertion** | The aggregator/verify-surfaces aggregator leg must assert each entry's `name` == the source repo's declared plugin name (not just version). Closes the #67 silent-mismatch class. |
| **D4** | **dist-extras reference** | Add a `## Cowork & Desktop surfaces` section to `skills/distribution/dist-extras/SKILL.md` documenting the §2 model + add paths + name-matching rule. The command points at it. |
| **D5** | **Scope boundary** | Release-flow auto-locate+run of aggregator-sync (#218) and post-release pin-refresh (#184) are **tracked elsewhere** — this spec is the *visibility + new-surface* layer, not the release-flow rewrite. |

## 4. Components

- **Create:** `commands/dist/surfaces.md` — `/craft:dist:surfaces` (detect Code via `claude plugin list`; Cowork via the `cowork_plugins` store; Desktop via `extensions-installations.json`; report a per-plugin × per-surface × version matrix; `--json`).
- **Modify:** `scripts/verify-surfaces.sh` — add the Cowork leg (D2) + name-match assertion (D3); both warn (don't block) for Cowork.
- **Modify:** `skills/distribution/dist-extras/SKILL.md` — the §2 reference section (D4).
- **Cascade:** new command → ~30-file count bump (`bump-version.sh`, plugin.json subtotal, hub/refcard/docs, Phase 8 entry).

## 5. Test plan (TDD)

Tier selection (auto): e2e + dogfood + unit. Markers: `e2e`, `dogfood`, `unit`.

### 5a. e2e (structural — `tests/test_dist_surfaces_e2e.py`)

- [ ] `commands/dist/surfaces.md` exists with valid frontmatter + a `category: dist` and an `arguments` block (incl `--json`).
- [ ] Count cascade: `validate-counts.sh` exits 0 after the command is added; `plugin.json (N craft)` subtotal bumped.
- [ ] dist-extras SKILL.md documents the three surfaces (assert "Cowork", "Desktop Extensions", "Code" + the name-matching rule present).

### 5b. dogfood (behavioral — `tests/test_dist_surfaces_dogfood.py`)

- [ ] `verify-surfaces.sh` with an injected Cowork store fixture reports the Cowork leg (warn on mismatch, never exit 1 for Cowork-only drift).
- [ ] Name-match assertion: an aggregator fixture whose entry name ≠ source-declared name produces a flagged finding.
- [ ] `/craft:dist:surfaces` (or its backing script) reports a plugin present on Code but absent on Cowork without error (the craft case).

### 5c. unit (`tests/test_verify_surfaces_cowork.sh` or py)

- [ ] The Cowork-store parser reads `known_marketplaces.json` + `installed_plugins.json` and returns the registered marketplaces + pinned versions (fixture-driven, no live store dependency — injectable like the existing `SURFACES_*` overrides).

## 6. Documentation & Discoverability

- [ ] Tutorial (`docs/tutorials/TUTORIAL-dist-surfaces.md`)
- [ ] Help + command reference (`docs/commands/dist/surfaces.md`)
- [ ] REFCARD entry (`docs/REFCARD.md` dist section)
- [ ] Help hub / discovery (`/craft:hub` via frontmatter; `commands/smart-help.md` entry)
- [ ] Website (`mkdocs.yml` nav) + `docs/skills-agents.md` (dist-extras section updated)
- [ ] CHANGELOG `[Unreleased]` ×2 mirror + count bumps; `validate-counts.sh` + `docs-staleness-check.sh` clean

## 7. Non-goals

- Not rewriting the release flow's aggregator-sync (that's #218) — only making the drift **visible** (verify-surfaces Cowork leg).
- Not the post-release pin-refresh (#184).
- Not making craft installable in Cowork — craft is command/agent-centric and Cowork is skills-first by design; this spec documents that boundary, it doesn't fight it.

## 8. Open questions

1. Should the Cowork leg session-dir discovery be hardcoded-glob or read from a config? (Cowork nests under two session-id dirs.) Lean: glob `local-agent-mode-sessions/*/*/cowork_plugins/` and pick the one with a non-empty `known_marketplaces.json`.
2. Does `/craft:dist:surfaces` scope to Data-Wise plugins only, or all installed? Lean: all installed, with a `--owner Data-Wise` filter.

---

## Handoff

`/craft:plan` (tier 4) → `ORCHESTRATE-dist-multi-surface.md` → worktree → TDD per §5. Sequence: D4 (doc) + D3 (name-match) are quick wins; D1 (command) + D2 (Cowork leg) are the core.
