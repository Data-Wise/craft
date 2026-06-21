# Governance Phase 2 — Enforced Gates (PR #1) — Orchestration Plan

> **Branch:** `feature/governance-phase2-gates`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-governance-phase2-gates`
> **Spec:** `docs/specs/SPEC-governance-phase2-gates-2026-06-20.md`
> **Version Target:** next minor (v2.44.0) — but DO NOT bump in this PR; bump happens at release time.

## Objective

Turn the just-shipped Phase 0 governance engine into an **enforced author/PR gate** and **automate R03**
(the one `error` rule that's still `kind: manual`, currently flagged as an enforcement gap by selftest).
Scope is deliberately the cheapest, highest-certainty slice: pre-commit + CI gating + R03, no live-env
dependency. SessionStart hook, soak machinery, and the cross-repo wrapper are **PR #2** (out of scope here).

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|-----------|----------|--------|--------|
| 1 | Automate R03 (manual → script) + fixtures + engine `{marketplace}` sub | High | ~60 min | |
| 2 | pre-commit gate (`^governance/` → selftest + drift) | High | ~20 min | |
| 3 | CI governance gate (ci.yml: selftest + drift, after the test step) | High | ~20 min | |
| 4 | Tests (R03 dogfood; flip e2e enforcement-gap invariant) | High | ~30 min | |
| 5 | Docs & Discoverability (README, guide, CHANGELOG) | Required | ~20 min | |

## Phase 1: Automate R03 (manual → script)

**Scope:** R03 = "a PII-bearing plugin publishes only to a PRIVATE marketplace; a public marketplace never
references a private repo." Make it machine-checkable and CI-runnable.

- [ ] 1.1 Write `governance/checks/no_private_in_public_marketplace.py` — given a marketplace.json path,
      parse it and exit 1 if any plugin entry's `source`/repo points at a **known-private** repo.
- [ ] 1.2 Add `governance/fixtures/no-private-in-public/{good,bad}/marketplace.json` — *good*: only public
      repos (craft, scholar, rforge, aiterm, flow-cli); *bad*: one entry referencing `savant` (private).
- [ ] 1.3 Engine wiring: add a `{marketplace}` substitution to `run_rules.py` (new `--marketplace` arg,
      default `.claude-plugin/marketplace.json` relative to repo root) so R03's cmd template resolves.
      The selftest fixtures pass `{marketplace}` = the fixture file (mirror how `{target}` works).
- [ ] 1.4 `RULES.yaml` R03: `kind: manual` → `kind: script`, `cmd: "checks/no_private_in_public_marketplace.py {marketplace}"`,
      add `fixtures: { good: fixtures/no-private-in-public/good, bad: fixtures/no-private-in-public/bad }`.
      Keep `severity: error`, `gates: [release, ci]`.
- [ ] 1.5 Regenerate the rule block: `python3 governance/render_rules.py --apply governance/CLAUDE-rules.md`
      (the rendered line for R03 won't visibly change — only `kind` changed — but run it + `--check` to confirm).

**Key files:**

- `governance/checks/no_private_in_public_marketplace.py` (NEW)
- `governance/fixtures/no-private-in-public/{good,bad}/marketplace.json` (NEW)
- `governance/run_rules.py` (add `{marketplace}` sub + `--marketplace`)
- `governance/RULES.yaml` (R03 manual → script)

**⚠ Design decision to resolve in-session (flag, don't guess):**

- **How to determine "private"?** Recommended: a small hardcoded denylist constant in the checker
  (`PRIVATE_REPOS = {"savant"}`) with a comment — simple, CI-portable, no network. Alternatives:
  `gh api` repo-visibility lookup (network → fragile in CI) or a `private_repos:` list in RULES.yaml
  (future enhancement). Pick the denylist for PR #1.
- **Which marketplace?** R03 is about the *public aggregator* (`Data-Wise/claude-plugins`), which is a
  **separate repo** — not present in craft CI (same vacuity trap as R01). For PR #1, scope the checker to
  the **in-repo `.claude-plugin/marketplace.json`** (CI-checkable, honest). Note in the checker docstring
  and the guide that the cross-repo aggregator scan is a `release`/`session` concern for PR #2. If the
  given marketplace path is absent, print a visible `skip:` and return 0 (mirror `no_duplicate_canon.py`).

## Phase 2: pre-commit gate (author)

**Scope:** Block a `governance/` change that breaks the engine or hand-edits the generated block.

- [ ] 2.1 Add a `repo: local` hook to `.pre-commit-config.yaml`, `files: ^governance/`, that runs:
      `python3 governance/run_rules.py --selftest` AND
      `python3 governance/render_rules.py --check governance/CLAUDE-rules.md`.
      (`language: system`, `pass_filenames: false`.) Do NOT run the live-env audit at commit time.
- [ ] 2.2 Verify: `pre-commit run --files governance/RULES.yaml` passes clean; intentionally break
      `CLAUDE-rules.md` and confirm the hook fails, then revert.

**Key files:** `.pre-commit-config.yaml` (extend)

## Phase 3: CI governance gate (PR)

**Scope:** Make a PR that breaks the engine or drifts the generated block fail CI.

- [ ] 3.1 Edit `.github/workflows/ci.yml` (the `Validate Plugin Structure` job — it's the one that runs
      `python -m pytest tests/ -v`). After the test-suite step add two steps:
      `python3 governance/run_rules.py --selftest` and
      `python3 governance/render_rules.py --check governance/CLAUDE-rules.md`.
- [ ] 3.2 Add an explicit echo/comment in the job stating CI does **NOT** evaluate R01/R07 live-env state
      (canon repos / cross-surface feed only exist locally) — no silent green.
- [ ] 3.3 Confirm `pytest -m governance` is already covered by `pytest tests/` (it is — governance tests
      live in `tests/`); no separate invocation needed unless you want a named gate.

**Key files:** `.github/workflows/ci.yml` (extend)

## Phase 4: Tests

- [ ] 4.1 `tests/test_governance_dogfood.py` — add R03 checker tests: bad marketplace (private ref) → exit 1;
      good → 0; absent path → visible skip + exit 0. Add a selftest assertion that R03 now shows `fixtures:`
      (no longer the `enforcement gap` warning).
- [ ] 4.2 `tests/test_governance_e2e.py` — `test_error_rules_are_enforceable_or_delegated` currently asserts
      `manual_error == ["R03-private-marketplace"]`. After R03 → script there are **zero** manual error-rules;
      flip the assertion to `== []`. Update `test_check_kinds_valid` / wiring tests if needed.
- [ ] 4.3 Run the full governance suite + the whole `pytest tests/` and confirm green.

**Key files:** `tests/test_governance_dogfood.py`, `tests/test_governance_e2e.py`

## Documentation & Discoverability (REQUIRED — final phase)

- [ ] Guide — `docs/guide/governance.md`: add a **"Gates & enforcement"** section (pre-commit + CI surfaces,
      the visibility-vs-prevention distinction, what CI does NOT check). Note R03 is now automated.
- [ ] Reference — `governance/README.md`: document the R03 checker + the `--marketplace` arg; update the
      "Adding a rule" / enforcement notes.
- [ ] REFCARD — N/A (governance is scripts/hooks, not a `/craft:` command). Confirm no REFCARD row needed.
- [ ] Help hub / discovery — N/A (no new command; `_discovery.py` excludes `governance/`).
- [ ] Website — `mkdocs.yml` nav already carries the governance guide; run `mkdocs build` clean.
- [ ] Catalog — N/A (no new skill/agent for `docs/skills-agents.md`).
- [ ] CHANGELOG `[Unreleased]` in **both** `CHANGELOG.md` and `docs/CHANGELOG.md` (they must mirror) —
      Added: R03 automation + pre-commit/CI governance gates. No count changes (no new command/skill/agent),
      so no `plugin.json`/`CLAUDE.md` count bump.
- [ ] `./scripts/validate-counts.sh` ✓ and `./scripts/docs-staleness-check.sh` ✓.

## Friction Prevention (from this project's history)

- **CWD check**: confirm `pwd` is the worktree (`~/.git-worktrees/craft/feature-governance-phase2-gates`),
  NOT the main repo, before editing. `git branch --show-current` must read `feature/governance-phase2-gates`.
- **`--strict-markers`**: the `governance` marker is already registered in `pyproject.toml` — good. If you
  add a new marker, register it or CI hard-errors at collection.
- **CI test job is substantive**: `Validate Plugin Structure` IS the full pytest run (~4–5 min). Don't treat
  it as a non-substantive flake; wait for it green, never `--admin` past it.
- **CHANGELOG mirror**: root `CHANGELOG.md` and `docs/CHANGELOG.md` must mirror — edit both.
- **No autonomous phase jumps**: after each phase, run verification and STOP to confirm before the next.
- **Don't bump version in this PR**: version bump is a release-time step on `dev`, not here.

## Acceptance Criteria

- [ ] R03 is `kind: script`; `run_rules.py --selftest` shows R03 `fixtures:` (no enforcement-gap warning) and
      exits 0; bad marketplace fixture → exit 1, good → 0, absent → visible skip + 0.
- [ ] pre-commit on a `governance/` change blocks a broken `--selftest` or a drifted `CLAUDE-rules.md`.
- [ ] CI runs selftest + drift-check after the test suite and prints what it does NOT check (R01/R07).
- [ ] `tests/test_governance_e2e.py` enforcement-gap invariant flipped to "zero manual error-rules"; all
      governance tests green; full `pytest tests/` green.
- [ ] Docs + both CHANGELOGs updated; `validate-counts.sh` ✓, `docs-staleness-check.sh` ✓.
- [ ] Documentation & Discoverability phase complete.

## Commit Strategy

- Phase 1: `feat(governance): automate R03 (marketplace private-repo checker)`
- Phase 2: `feat(governance): pre-commit gate for governance/ (selftest + drift)`
- Phase 3: `feat(governance): CI governance gate (selftest + drift)`
- Phase 4: `test(governance): R03 checker coverage; flip enforcement-gap invariant`
- Phase 5: `docs(governance): gates & enforcement + R03 automation`

## Verification (after each phase)

```bash
# Governance suite (fast)
python3 -m pytest tests/test_governance_e2e.py tests/test_governance_dogfood.py -q
# Engine self-checks
python3 governance/run_rules.py --selftest
python3 governance/render_rules.py --check governance/CLAUDE-rules.md
# Pre-commit (phase 2+)
pre-commit run --files governance/RULES.yaml
# Full suite before PR
python3 -m pytest tests/ -q
```

## Session Instructions

### Context

You are in the **craft worktree** for the governance Phase 2 gates feature (PR #1). The spec
(`docs/specs/SPEC-governance-phase2-gates-2026-06-20.md`) has the full design; this ORCHESTRATE scopes
PR #1 (R03 + pre-commit + CI). Phase 0 already shipped in v2.43.0 on `main`.

### How to Start

```bash
cd ~/.git-worktrees/craft/feature-governance-phase2-gates
claude
```

On session start, paste:

> Read `ORCHESTRATE-governance-phase2-gates.md` and the spec at
> `docs/specs/SPEC-governance-phase2-gates-2026-06-20.md`. Resolve the two Phase 1 design decisions
> (private-repo denylist; in-repo marketplace scope), then start Phase 1.

### Phase-by-Phase

1. Read the current state of each file listed in the phase.
2. Implement per this plan + the spec; resolve flagged design decisions explicitly.
3. Run verification after each phase.
4. Commit in logical groups (see Commit Strategy).
5. STOP and confirm before the next phase.

### Integrate

When all phases pass: `gh pr create --base dev --head feature/governance-phase2-gates`. Delete this
ORCHESTRATE file as part of the merge cleanup (working artifact — belongs on the feature branch only).
