# SPEC: Multi-surface-aware release — surface registry + propagation

**Status:** design (locked via brainstorm 2026-06-26) · **Driver:** "revamp /release to propagate to every surface, not just verify some"
**Subsumes:** [SPEC-dist-multi-surface-2026-06-26.md](SPEC-dist-multi-surface-2026-06-26.md) — its `/craft:dist:surfaces` command becomes the read-only view over this registry; its Cowork leg + name-match become registry verify steps.
**Closes (as the durable fix):** [craft#218](https://github.com/Data-Wise/craft/issues/218) (aggregator-sync no-op), [craft#184](https://github.com/Data-Wise/craft/issues/184) (pin-refresh), [himalaya-mcp#67](https://github.com/Data-Wise/himalaya-mcp/issues/67) (name mismatch).

---

## 1. Problem

`/release` already **verifies** every surface (verify-surfaces: git-tag, marketplace, tap, brew, Code, aggregator) but only **propagates** to three (git-tag, repo marketplace.json, tap). The rest drift:

- **aggregator** — Step 10d aggregator-sync is a green-check no-op (gated on the unset `DATA_WISE_AGGREGATOR_FILE`); drifted 14 craft minors / a scholar major undetected.
- **local pins** (brew + Code) — manual lag every release.
- **Cowork** — never touched, WARN-only.

The design intent exists (a `D5` "aggregator-sync before verify" hook) but is wired behind a manual env var and a "commit/push separately" note that never runs. The revamp turns "propagate-to-some + verify" into a **surface registry** that propagates everywhere it can, verifies all, and reports the manual residue.

## 2. Core abstraction — the surface registry

A single declarative registry (`scripts/surfaces/registry.json`) where each surface is `{name, detect, propagate, verify, gate}`:

| name | detect (read current) | propagate (push new) | verify | gate |
|------|----------------------|----------------------|--------|------|
| `git-tag` | `git describe` | `gh release create` (existing) | == plugin.json | BLOCK |
| `marketplace` | repo `.claude-plugin/marketplace.json` | `bump-version.sh` (existing) | == | BLOCK |
| `tap` | `Formula/<name>.rb` | homebrew-release workflow (existing) | == | BLOCK |
| `brew` | `brew list --versions` | **NEW: post-release `brew upgrade`** (#184) | == | WARN (local) |
| `code-registered` | `installed_plugins.json` | **NEW: marketplace-update→plugin-update** (#184) | == | WARN (local) |
| `aggregator` | `Data-Wise/claude-plugins` marketplace.json | **NEW: CI action** (D2) | == version AND name==source-declared (#67) | BLOCK |
| `cowork` | `cowork_plugins/known_marketplaces.json` + `installed_plugins.json` | **manual** (separate GUI store) | report only | WARN + remind |
| `desktop-ext` | `extensions-installations.json` | N/A (DXT) | N/A | INFO |

The release "surfaces phase" iterates the registry: **propagate** each (where possible) → **verify** each → emit a **surface matrix** (every surface × {propagated / manual / verified / N/A}). `/craft:dist:surfaces` is the read-only `detect+verify` view over the same registry.

## 3. Locked decisions

| # | Decision | Detail |
|---|----------|--------|
| **D1** | **Surface registry phase** | Refactor release Steps 10/13.6 into one registry-driven phase. `scripts/surfaces.sh` (driver) + `scripts/surfaces/registry.json` (data). `verify-surfaces.sh` becomes the registry's `verify` half (kept backward-compatible / wrapped). Adding a surface = one registry entry. |
| **D2** | **Aggregator via CI action** | A `release: published` workflow (`.github/workflows/aggregator-sync.yml`) checks out `Data-Wise/claude-plugins`, runs `aggregator-sync.sh` for the released plugin (version **and** name), commits + pushes (or PRs). Removes the local-env dependency that caused the no-op. Uses the existing GitHub-App cross-repo auth (APP_ID / APP_PRIVATE_KEY on the aggregator repo). Satellites (scholar/rforge/himalaya) get the same workflow. |
| **D3** | **Cowork = report + remind** | Registry `cowork` surface: read the `cowork_plugins` store (glob `local-agent-mode-sessions/*/*/cowork_plugins/`), report its marketplaces + pins as a WARN leg, print the re-sync reminder. The release does NOT auto-push to Cowork (separate GUI store; the Update path no-ops per #199). Visibility is the honest ceiling. |
| **D4** | **Name-match in verify** | The aggregator (and every github-source) verify step asserts the entry `name` == the source repo's declared plugin name, not just version (#67 class). |
| **D5** | **`/craft:dist:surfaces`** | The read-only CLI view over the registry (`detect` + `verify`, no propagate). Folds in the prior spec's D1. `--owner`, `--json`. |
| **D6** | **Local pin-refresh (advisory)** | Post-release, refresh local brew + Code pins (#184) — advisory (WARN, never block); prints the exact commands when it can't (e.g. needs a Code restart). |

## 4. Components

- **Create:** `scripts/surfaces/registry.json` (the surface model), `scripts/surfaces.sh` (driver: `--propagate`, `--verify`, `--report`, `--json`).
- **Create:** `.github/workflows/aggregator-sync.yml` (release-triggered aggregator propagation, App-auth).
- **Create:** `commands/dist/surfaces.md` (`/craft:dist:surfaces` — read-only view).
- **Modify:** `scripts/verify-surfaces.sh` — become registry-backed (or wrap); add Cowork leg + name-match. Keep the existing `SURFACES_*` injectable overrides for tests.
- **Modify:** `skills/release/SKILL.md` + `references/downstream-verification.md` — replace Steps 10d/13.6 prose with the registry phase; document the CI-action propagation + the surface matrix.
- **Modify:** `skills/distribution/dist-extras/SKILL.md` — the three-surface reference (from the subsumed spec).
- **Cascade:** new command → ~30-file count bump.

## 5. Test plan (TDD)

Tiers (auto): unit + e2e + dogfood + integration (cross-surface). Markers: `unit`, `e2e`, `dogfood`, `integration`.

### 5a. unit (`tests/test_surface_registry.py`)

- [ ] Registry loads; every entry has `{name, detect, propagate, verify, gate}`; gates ∈ {BLOCK, WARN, INFO}.
- [ ] The Cowork-store parser reads fixture `known_marketplaces.json` + `installed_plugins.json` → marketplaces + pins (injectable, no live store).
- [ ] Name-match validator flags an entry whose name ≠ source-declared name.

### 5b. e2e (`tests/test_release_surfaces_e2e.py`)

- [ ] `commands/dist/surfaces.md` exists, `category: dist`, declares `--json`/`--owner`.
- [ ] Release skill prose references the registry phase (not the old gated Step 10d env-var hook); `verify-surfaces` retains its injectable overrides.
- [ ] `.github/workflows/aggregator-sync.yml` triggers on `release: published` and references App-auth secrets.
- [ ] Count cascade green (`validate-counts.sh`).

### 5c. dogfood (`tests/test_release_surfaces_dogfood.py`)

- [ ] `surfaces.sh --verify` with injected fixtures: a present-but-mismatched BLOCK surface → exit 1; a Cowork-only mismatch → WARN, exit 0.
- [ ] `surfaces.sh --report` emits the full surface matrix (every registry surface a row).
- [ ] aggregator-sync `--check` mode: a stale aggregator fixture reports a would-change; a current one reports no-op (the propagate half is dry-runnable).
- [ ] Name-mismatch fixture → flagged finding (mutate-and-revert, proves the gate fires).

### 5d. integration (`tests/test_integration_surfaces.py`)

- [ ] Full registry pass over a fixture set: propagate (dry-run) → verify → report, asserting the matrix end-to-end without touching real stores.

## 6. Documentation & Discoverability

- [ ] Tutorial (`docs/tutorials/TUTORIAL-release-surfaces.md`) — the surface model + the release matrix.
- [ ] Help + command ref (`docs/commands/dist/surfaces.md`).
- [ ] REFCARD entry (dist + release sections).
- [ ] Hub / smart-help discovery for `/craft:dist:surfaces`.
- [ ] Website nav + `docs/skills-agents.md`; release skill reference pages updated.
- [ ] CHANGELOG `[Unreleased]` ×2 mirror + count bumps; staleness clean.
- [ ] ADR: "release propagates via a surface registry; Cowork is report-only" (records the auto-vs-manual boundary).

## 7. Non-goals

- Auto-pushing to Cowork or Desktop Extensions (separate GUI stores; report-only).
- A general plugin-host abstraction beyond the Data-Wise surfaces.
- Replacing the homebrew-release workflow (the tap propagation stays; the registry just *verifies* it).

## 8. Open questions

1. Registry format — JSON data + bash driver, or a small Python module? Lean JSON + bash (matches existing `scripts/` + injectable env overrides; no new dep).
2. Aggregator CI action — direct commit to the aggregator's `main` (0-review protected) vs auto-merged PR? Lean PR + `--admin` auto-merge (audit trail, matches today's manual flow).
3. Should `surfaces.sh` fully replace `verify-surfaces.sh` or wrap it? Lean **wrap** first (verify-surfaces stays the verify half; `surfaces.sh` adds propagate + report) to keep the ~1700-test suite green, then consolidate.

---

## Handoff

`/craft:plan` (tier 4) → `ORCHESTRATE-release-multisurface.md` → worktree → TDD per §5. Build order: registry + verify-wrap (D1) → Cowork leg + name-match (D3/D4) → `/craft:dist:surfaces` (D5) → aggregator CI action (D2) → pin-refresh advisory (D6) → release-skill prose + docs.
