# Governance Phase 2 — PR #2: SessionStart Hook — Orchestration Plan

> **Branch:** `feature/governance-phase2-hook`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-governance-phase2-hook`
> **Spec:** `docs/specs/SPEC-governance-phase2-gates-2026-06-20.md`
> **Builds on:** PR #1 (R03 + pre-commit/CI gates), shipped in **v2.44.0**.

## Locked decisions (from brainstorm)

- **Scope = SessionStart hook ONLY.** The soak-then-flip machinery and the cross-repo wrapper move to
  **PR #3**. (Matches PR #1's tight-scope discipline.)
- **Install = global** (`~/.claude/settings.json` SessionStart hook) — skills live machine-wide under
  `~/.claude/skills`, so whole-machine drift coverage fits; fires in every session.
- **Release guard (#184) = annotate only** (recorded for the future #184 PR — NOT in this PR's scope):
  surface RED governance findings in release output without halting the release. Gentle-ramp posture.

## Objective

Add a **visibility gate**: at session open, run the live-env governance audit against `~/.claude/skills`
and surface a compact RED-only summary into session context — so drift (e.g. a dead skill symlink) is
seen immediately, locally, where the canon repos exist. SessionStart hooks **inject context, they do not
block** — this is visibility, by design; prevention lives in the pre-commit + CI gates (PR #1).

## Phase Overview

| Phase | Increment | Effort | Status |
|-------|-----------|--------|--------|
| 1 | `hooks/governance-session.sh` — RED-only summary + mtime cache | ~60 min | |
| 2 | Global install wiring + docs for `~/.claude/settings.json` | ~30 min | |
| 3 | Tests (dogfood the hook script) | ~30 min | |
| 4 | Docs & Discoverability | ~20 min | |

## Phase 1: the hook script

- [ ] 1.1 `hooks/governance-session.sh` — runs `python3 <plugin>/governance/run_rules.py --target
      ~/.claude/skills --index ~/.claude/skills/SKILLS-INDEX.md --json`, parses the JSON, and emits a
      **compact RED-only** line into session context (e.g. `GOVERNANCE: 1 red — R08 dead link skills/foo`).
      Clean → silent (or a one-line OK). Warn/external → not escalated to RED.
- [ ] 1.2 Performance: must be <1–2s. **Cache by `~/.claude/skills` mtime** — if the dir is unchanged
      since the last run, skip re-audit and reuse the cached verdict (store under a cache path, e.g.
      `~/.claude/.cache/governance-session.json`).
- [ ] 1.3 Resolve the installed plugin path robustly (the engine is `__file__`-relative; the hook needs
      to find `governance/run_rules.py` in the installed craft plugin).

**⚠ Design decisions to resolve in-session:**

- Exact RED-summary format + whether to also show a one-line "governance clean" on success (lean: silent
  on clean to avoid noise; RED only).
- Cache invalidation: mtime of the skills dir vs a content hash (mtime is cheaper; start there).
- Hook contract: SessionStart hooks receive JSON on **stdin** (not env vars) and emit context via stdout
  per the Claude Code hook contract — verify the exact additionalContext mechanism.

## Phase 2: global install + wiring

- [ ] 2.1 Document the `~/.claude/settings.json` SessionStart hook entry that invokes
      `hooks/governance-session.sh`. **This modifies the user's GLOBAL config** — it is an *install step*,
      not a repo change; do it via the `update-config` skill / with explicit user confirmation, NOT
      silently. The PR ships the script + install docs; the global wiring is applied separately.
- [ ] 2.2 Make the hook a no-op-safe when `~/.claude/skills` is absent (other machines) — visible skip.

## Phase 3: Tests

- [ ] 3.1 Dogfood `hooks/governance-session.sh` against temp skills dirs: a dead-symlink dir → RED line;
      a clean dir → silent/OK; mtime cache → second run skips re-audit. Hermetic (temp dirs, never the
      live `~/.claude`). Add under the `governance` pytest marker.

## Documentation & Discoverability (REQUIRED)

- [ ] Guide — `docs/guide/governance.md` "Gates & enforcement": add the SessionStart hook as the third
      (visibility) surface; reiterate visibility-vs-prevention.
- [ ] README — `governance/README.md`: document the hook + its global install.
- [ ] CHANGELOG `[Unreleased]` in **both** files (mirror). No count change.
- [ ] `validate-counts.sh` + `docs-staleness-check.sh` clean.

## Acceptance Criteria

- [ ] Opening a session with a dead skill symlink surfaces a **RED governance line**; a clean tree is silent.
- [ ] Hook runs <2s and skips re-audit when `~/.claude/skills` is unchanged (mtime cache).
- [ ] Hook is no-op-safe where `~/.claude/skills` is absent (visible skip, never an error).
- [ ] Dogfood tests green; full suite green; docs + CHANGELOG updated; counts clean.
- [ ] Global install is applied **only with explicit user confirmation** (it touches `~/.claude/settings.json`).

## Commit Strategy

- Phase 1: `feat(governance): SessionStart drift-visibility hook`
- Phase 3: `test(governance): hook dogfood coverage`
- Phase 4: `docs(governance): SessionStart visibility gate`

## Notes (this repo's reality)

- **branch-guard is worktree-path-aware** — this worktree's code can be implemented from any session via
  absolute paths + `git -C` (no separate session required). Drive it however you like.
- The live-env audit (`run_rules.py` default mode) is what this hook finally wires — it was the one
  "not yet wired" piece after PR #1 wired selftest + drift.
- Deferred to PR #3: soak-then-flip (`--promote-check` + `STATE.json`), cross-repo wrapper. R04 deferred.
