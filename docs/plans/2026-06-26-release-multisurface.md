# Multi-surface-aware Release Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Refactor `/release` to propagate to every plugin surface via a declarative surface registry (not just verify some) — closing craft#218 (aggregator no-op), craft#184 (pin lag), and himalaya-mcp#67 (name mismatch) as the durable fix.

**Architecture:** A `scripts/surfaces/registry.json` + `scripts/surfaces.sh` driver (`{detect, propagate, verify, gate}` per surface); `surfaces.sh --verify` WRAPS the existing `verify-surfaces.sh` (no resolver duplication); aggregator propagation moves to a `release: published` CI action; Cowork is a report-only WARN leg.

**Tech Stack:** Bash drivers + JSON data + a standalone `registry.py` helper (precedent: `bump-version-helper.py`), Python 3 stdlib pytest, GitHub Actions (App-auth).

**Source spec:** [SPEC-release-multisurface-2026-06-26.md](../specs/SPEC-release-multisurface-2026-06-26.md)

**Design resolution:** the 3 open questions (§8) were resolved via a dynamic Workflow (3 resolve agents + 3 adversarial verifiers + synthesis); the corrected reasoning is in §1 below.

## Global Constraints

- **Branch:** `feature/release-multisurface` worktree off `dev` — feature code never on `dev`.
- **WRAP not replace:** `surfaces.sh --verify` shells to `verify-surfaces.sh` (preserves exit codes 0/1/2; `SURFACES_*` overrides pass via env inheritance). `verify-surfaces.sh` gets ONLY additive legs — no inverted assertions — to keep the ~1700-test suite green.
- **Parity test uses a name→label alias map** (`git-tag`→`git tag`, `tap`→`tap formula`, `brew`→`brew-installed`, `code-registered`→`Code-registered`) and EXCLUDES INFO surfaces (`desktop-ext` has no verify leg by design) — raw string-equality or including INFO would false-fail CI.
- **Aggregator CI must fail loud:** non-zero exit if a PR opens but doesn't merge — never exit green on an unmerged PR (that was the #218 no-op pattern). Pre-ship gate: confirm the GitHub App on Data-Wise/claude-plugins has contents:write + pull_requests:write + admin/bypass.
- **No new commands except `/craft:dist:surfaces`** → exactly one count cascade (~30-file bump). validate-counts uses SKILL.md-only counting.
- **Test markers:** dogfood needs both `e2e` + `dogfood`; reuse the `.sh`-suite + pytest-shim pattern (`test_verify_surfaces.{py,sh}`).

---

## Implementation detail — surface registry + propagation

**Spec:** `docs/specs/SPEC-release-multisurface-2026-06-26.md` · **Closes:** craft#218, craft#184, himalaya-mcp#67
**Workflow:** worktree off `dev` → TDD per §5 → red-first each task → PR `--base dev`.

---

## 1. Resolved decisions (folds into spec §8)

The three open questions are now locked, adversarially verified:

- **Q1 (registry format) → JSON data + bash driver.** `scripts/surfaces/registry.json` (data) + `scripts/surfaces.sh` (driver); `python3` only for JSON-heavy inline logic, with a standalone `scripts/surfaces/registry.py` helper as the escape hatch for gnarly per-surface gate/matrix logic (precedent: `scripts/bump-version-helper.py`). **No Python module *as the driver*** — the load-bearing reason is **Q3's wrap decision**: `verify-surfaces.sh` is already bash with the full `SURFACES_*` injection contract, so a bash driver that wraps it is the natural seam (a Python driver shelling to a bash verify script is the awkward one). The `.sh`-suite + one-line pytest-shim collection path (`test_verify_surfaces.py` shells to `test_verify_surfaces.sh`) is reused as-is. *(Note: Python helpers ARE sanctioned here — `verify_caveats.py` is import-tested by `tests/test_homebrew_gates.py` — so the "Python has no home" framing is dropped; the decision rests on the wrap seam, not on a false no-precedent claim.)*
- **Q2 (aggregator CI) → auto-merged PR with `gh pr merge --admin --squash`, NOT direct commit.** `Data-Wise/claude-plugins` `main` is PR-required (verified via `gh api`: `required_approving_review_count: 0`, `enforce_admins: false`), so a direct commit is **blocked** — the PR+`--admin` path is required, not merely preferred. No-op short-circuit: `git diff --staged --quiet → exit 0`. **Two mandatory pre-ship gates:** (a) verify the GitHub App is installed on `Data-Wise/claude-plugins` with `contents: write` + `pull_requests: write` + admin/bypass on `main`; (b) the workflow must **fail loud** — non-zero exit if a PR opens but does not merge, surfaced as a BLOCK leg in verify-surfaces — so an unmerged PR can never exit green like the old #218 no-op.
- **Q3 (wrap vs replace) → WRAP.** `surfaces.sh` shells out to `verify-surfaces.sh` as a subprocess (preserves exit codes 0/1/2; passes `SURFACES_*` overrides via env inheritance — confirmed in `test_verify_surfaces.sh:110-113`). `verify-surfaces.sh` gets only **additive** D3/D4 legs, no inverted assertions. **Parity-test correction:** the registry↔verify-leg parity test must use an explicit **name→label alias map** (`git-tag`→`git tag`, `tap`→`tap formula`, `brew`→`brew-installed`, `code-registered`→`Code-registered`, `aggregator`→`aggregator`) and scope to **BLOCK + WARN-verifiable** surfaces only, excluding INFO/N-A surfaces (`desktop-ext`) that intentionally have no verify leg. Asserting raw string equality, or including INFO surfaces, would false-fail CI on a *correct* registry.

---

## 2. TDD build order (spec Handoff sequence)

Each task: write the red test first, watch it fail, implement, watch it pass. Reuse spec §5 test file names.

### Task 1 — Registry + verify-wrap (D1)

**Red first** — `tests/test_surface_registry.py` (spec §5a):

- Registry loads; every entry has `{name, detect, propagate, verify, gate}`; `gate ∈ {BLOCK, WARN, INFO}`.
- Add the **parity test** here (Q3-corrected): for every registry surface whose gate is BLOCK or WARN-with-verify, its name maps (via the alias map above) onto a `verify-surfaces.sh` leg label; INFO/N-A surfaces (`desktop-ext`) are excluded.

**Create:**

- `scripts/surfaces/registry.json` — the 8-surface model from spec §2 (`git-tag`, `marketplace`, `tap`, `brew`, `code-registered`, `aggregator`, `cowork`, `desktop-ext`), each `{name, detect, propagate, verify, gate}`.
- `scripts/surfaces.sh` — driver with `--propagate`, `--verify`, `--report`, `--json`. `--verify` shells to `verify-surfaces.sh` (wrap, not reimplement — avoids the dual-resolver drift in spec risk #2).
- `scripts/surfaces/registry.py` — standalone helper (à la `bump-version-helper.py`) for JSON-heavy matrix/gate logic, called by `surfaces.sh`.

**Modify:** none to `verify-surfaces.sh` resolver logic yet (kept intact for green suite).

**Green gate:** `python3 tests/test_surface_registry.py` + existing `tests/test_verify_surfaces.py` still pass (wrap preserves exit codes 0/1/2).

### Task 2 — Cowork leg + name-match (D3/D4)

**Red first** — extend `tests/test_surface_registry.py` (§5a):

- Cowork-store parser reads fixture `known_marketplaces.json` + `installed_plugins.json` → marketplaces + pins (injectable, no live store).
- Name-match validator flags an entry whose `name ≠ source-declared name`.

Plus `tests/test_release_surfaces_dogfood.py` (§5c) red legs:

- `surfaces.sh --verify` with injected fixtures: mismatched BLOCK surface → exit 1; Cowork-only mismatch → WARN, exit 0.
- Name-mismatch fixture → flagged finding (mutate-and-revert proves the gate fires).

**Modify:**

- `scripts/verify-surfaces.sh` — **additive** legs only: add a `cowork` WARN leg (`add_leg "cowork" ...` reading the `cowork_plugins` store via `SURFACES_*`-injectable glob `local-agent-mode-sessions/*/*/cowork_plugins/`), and extend the aggregator/github-source legs to assert `name == source-declared name` (#67), not just version. Keep all `SURFACES_*` override hooks.
- `scripts/surfaces/registry.json` — `cowork` = WARN+remind, `desktop-ext` = INFO/N-A.

**Test-shim parity:** mirror new bash assertions into `tests/test_verify_surfaces.sh`; the `.py` shim shells to it.

**Green gate:** dogfood §5c Cowork/name-match legs pass; `verify-surfaces.sh` exit codes unchanged for the existing 6 legs.

### Task 3 — `/craft:dist:surfaces` read-only view (D5)

**Red first** — `tests/test_release_surfaces_e2e.py` (§5b):

- `commands/dist/surfaces.md` exists, `category: dist`, declares `--json` / `--owner`.

**Create:** `commands/dist/surfaces.md` — the read-only `detect + verify` view (no `--propagate`) over the registry. Calls `scripts/surfaces.sh --verify --report` with `--owner`/`--json`. Subsumes SPEC-dist-multi-surface's `/craft:dist:surfaces`.

**Green gate:** e2e command-existence/frontmatter test passes; `surfaces.sh --report` emits the full matrix (every registry surface = one row, §5c).

### Task 4 — Aggregator CI action (D2)

**Pre-ship gate (blocking, do FIRST):** confirm GitHub App on `Data-Wise/claude-plugins` has `contents: write` + `pull_requests: write` + admin/bypass on `main`. Block this task until verified.

**Red first** — `tests/test_release_surfaces_e2e.py` (§5b) + dogfood (§5c):

- `.github/workflows/aggregator-sync.yml` triggers on `release: published` and references App-auth secrets (`APP_ID` / `APP_PRIVATE_KEY`).
- aggregator-sync `--check` mode: stale fixture → would-change; current fixture → no-op (propagate half is dry-runnable).

**Create:** `.github/workflows/aggregator-sync.yml` — `release: published`; mints App token → checks out `Data-Wise/claude-plugins` → runs `aggregator-sync.sh` (version **and** name, D4) → `git diff --staged --quiet → exit 0` no-op short-circuit → else `gh pr create` → `gh pr merge --admin --squash` → **fail loud**: non-zero exit if PR opens but doesn't merge.

**Modify:** `scripts/surfaces.sh` `--propagate` for the `aggregator` surface delegates to the existing `aggregator-sync.sh` (reuse `tests/test_aggregator_sync.{py,sh}` harness); add `--check` dry-run.

**Green gate:** e2e workflow-trigger test + dogfood `--check` legs pass. Satellites (scholar/rforge/himalaya) get the same workflow as a follow-up (note in PR body, not this task).

### Task 5 — Pin-refresh advisory (D6)

**Red first** — `tests/test_release_surfaces_dogfood.py` / `tests/test_integration_surfaces.py`:

- `surfaces.sh --propagate` for `brew` + `code-registered` is **advisory** — WARN, never exit-1; prints exact `brew upgrade` / `marketplace update → plugin update` commands when it can't act (e.g. needs Code restart).

**Modify:** `scripts/surfaces.sh` — `brew` propagate = post-release `brew upgrade` (#184); `code-registered` propagate = `marketplace-update → plugin-update` (#184), both WARN-gated.

**Green gate:** advisory legs never flip exit code; integration §5d full pass (propagate dry-run → verify → report) without touching real stores.

### Task 6 — Release-skill prose + docs

**Red first** — `tests/test_release_surfaces_e2e.py` (§5b):

- Release skill prose references the **registry phase** (not the old gated Step 10d env-var hook); `verify-surfaces` retains injectable overrides.
- Count cascade green (`validate-counts.sh`).

**Modify:**

- `skills/release/SKILL.md` + `references/downstream-verification.md` — replace Steps 10d/13.6 prose with the registry phase; document CI-action propagation + the surface matrix; document the **fail-loud unmerged-PR BLOCK** (Q2 gate).
- `skills/distribution/dist-extras/SKILL.md` — the three-surface reference (from subsumed spec).

**Green gate:** full §5 suite green: `tests/test_surface_registry.py`, `tests/test_release_surfaces_e2e.py`, `tests/test_release_surfaces_dogfood.py`, `tests/test_integration_surfaces.py`.

---

## 3. Count cascade + Documentation steps

**Count cascade (new command `/craft:dist:surfaces` → ~30-file bump, spec §4):**

- [ ] `./scripts/validate-counts.sh` — expect command count +1; run `--fix` if it bumps. Use **SKILL.md-only** counting semantics (per memory: `-name "*.md"` over-counts references).
- [ ] `plugin.json` description + subtotal (manual — bump-version.sh doesn't touch categorical subtotals).
- [ ] `bump-version.sh`-swept totals (~14 files) + the ~29-ref staleness long tail: `./scripts/docs-staleness-check.sh --fix`.
- [ ] Hub / smart-help discovery entry for `/craft:dist:surfaces` (`commands/**/*.md` auto-discovered; verify it appears).
- [ ] `docs/skills-agents.md` — add the command; ensure no `references/*.md` shows as a spurious skill row.
- [ ] mkdocs nav (`/craft:docs:nav-update`) for the new `docs/commands/dist/surfaces.md` page.

**Documentation (spec §6):**

- [ ] `docs/tutorials/TUTORIAL-release-surfaces.md` — surface model + release matrix.
- [ ] `docs/commands/dist/surfaces.md` — help + command ref (site page; sync manually, gitignored `_cache.json` not committed).
- [ ] REFCARD entry — dist + release sections.
- [ ] Website nav + release-skill reference pages updated; `/craft:site:check` for broken links.
- [ ] `CHANGELOG.md` **and** `docs/CHANGELOG.md` `[Unreleased]` ×2 mirror (craft maintains both — diff them to catch drift) + count bumps; `docs-staleness-check.sh` clean.
- [ ] **ADR** (`docs/adr/`): "release propagates via a surface registry; Cowork is report-only" — records the auto-vs-manual boundary and the Q2 PR+`--admin` decision.

**Final gate before PR:** full `python3 -m pytest tests/` (not the 3-file subset — CI runs ~1700 tests), `validate-counts.sh` green, `docs-staleness-check.sh` clean, then `gh pr create --base dev`.

**Files created (net-new):** `scripts/surfaces/registry.json`, `scripts/surfaces/registry.py`, `scripts/surfaces.sh`, `.github/workflows/aggregator-sync.yml`, `commands/dist/surfaces.md`, `tests/test_surface_registry.py`, `tests/test_release_surfaces_e2e.py`, `tests/test_release_surfaces_dogfood.py`, `tests/test_integration_surfaces.py`, `docs/tutorials/TUTORIAL-release-surfaces.md`, `docs/commands/dist/surfaces.md`, the ADR.
**Files modified:** `scripts/verify-surfaces.sh`, `tests/test_verify_surfaces.sh` (+`.py` shim), `skills/release/SKILL.md`, `references/downstream-verification.md`, `skills/distribution/dist-extras/SKILL.md`, `plugin.json`, CHANGELOG ×2, count-cascade long tail.
