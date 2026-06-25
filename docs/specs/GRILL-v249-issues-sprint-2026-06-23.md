# GRILL: v2.49.x Issues Sprint — Sequencing & Implementation

**Date:** 2026-06-24
**Target grilled:** [`SPEC-v249-issues-sprint-2026-06-23.md`](SPEC-v249-issues-sprint-2026-06-23.md) (APPROVED) + bundled item "wire skill-standards into `/craft:check`"
**Method:** craft:grill (interactive, codebase-first), 8 branches resolved
**Prior:** 4 interface questions resolved earlier this session (carried into the ledger below as D8/D9 + Open Questions)
**Handoff:** → superpowers:writing-plans

---

## Decision Ledger

| # | Branch (question) | Resolution |
|---|-------------------|------------|
| D1 | Is the skill-standards `/craft:check` wiring part of this sprint or separate? | **Independent quick-win-sized PR.** Planned in the same plan doc, sequenced first (cheapest), NOT gated behind PR A/PR B. Self-contained validator: one `.md` in `.claude-plugin/skills/validation/`, no count cascade, legacy skills already 100/100. Folds into the single v2.49.1 cut (D2) but has no build dependency on the sprint. |
| D2 | One coordinated release vs roll a patch per unit? | **Single coordinated `v2.49.1`** after all 4 units (quick-wins, skill-standards, PR A, PR B) merge to `dev`. Amortizes craft's multi-step release overhead 4×; none of the units is same-day urgent. |
| D3 | skill-standards validator severity in `/craft:check`? | **Advisory (report-only).** Runs in the hot-reload fork (`hot_reload: true`), prints per-skill score + sub-100 findings, NEVER exits 1. Mirrors the governance warn→error soak path and the #184 release advisory. Silent-clean today; surfaces only NEW drift. |
| D4 | aggregator-sync (#199) gate strictness in `/release`? | **Blocking (exit 1)** before publish, per spec line 352. Deliberate asymmetry vs the caveats gate (advisory-by-default): stale-aggregator causes *silent wrong-version installs* (severe) — the exact lag the v2.49.0 post-release tooling chased — vs stale-caveats (cosmetic). |
| D5 | SessionEnd hook double-write dedup key? | **Per-session-id, not per-day.** The spec said "SessionStop" — *no such event exists* (registered events: `Stop`, `SessionStart`, `PostToolUse`, …; `SessionEnd` is the once-per-session terminal event). With `SessionEnd` firing once per session, the spec's per-day skip would drop every session after the first each day. Guard must key on the current session id. |
| D6 | `post_install_check.py` — how to verify without destructive execution? | **Structural always + sandbox opt-in.** Default: parse Ruby `post_install` — assert begin/rescue/end, `marketplace update` precedes `plugin update` (the exact v2.49.0 ordering bug), libexec paths resolve. No side effects, runs on any CI. Opt-in flag (macOS-local) runs the block under a HOME-redirected temp dir for higher fidelity. |
| D7 | How does #171 close once ADR-001 is written? | **Auto-close via `Closes #171`.** ⚠️ Fires only on merge to the **default branch (`main`)** — quick-win lands on `dev`, so it closes at the v2.49.1 release merge, **and only if `Closes #171` is also in the release PR body** (squash-merge can drop per-commit trailers). |
| D8 | `verify_caveats.py` interface — `run_all_gates(...)` (spec body) vs `verify_caveats(...)` (agent findings)? | **Single entry `verify_caveats(formula_path, changelog_path, version, strict=False, formula_name=None) -> GateReport`.** Drop the `run_all_gates` dual-name. Drop Check 5 (plugin-version match) — it folds #184, which this sprint explicitly defers; #199's Cowork verify covers install-version drift operationally. Net: Checks 1–4 only. |
| D9 | PR-B hook ships outside the repo (`~/.claude/hooks/...`) but tests live in `craft/tests/`. | **Mirror the v2.45.0 governance SessionStart pattern.** Source-of-truth = `craft/hooks/session-facet.sh`; an installer (`install-guards.sh`-style) copies it to `~/.claude/hooks/` + registers the `SessionEnd` entry in `settings.json`; tests exercise the **in-repo** copy. No test reaches into `~/.claude`. |
| D10 | Build order within the single release? | **PR A & PR B in parallel worktrees** (user choice). ⚠️ Needs two separate Claude sessions; worktrees created ONLY on explicit user request (no-unrequested-switch rule). Quick-wins + skill-standards commit direct to `dev` first. |

---

## Open Questions (carry into PR B / PR A)

- **Per-session dedup shared key (PR B, blocks D5):** current facets are timestamp-named (`session-YYYYMMDD-HHMMSS.json`) and `/done` is a slash command with no stdin `session_id`; the hook gets `session_id` from `SessionEnd` stdin but `/done` does not. Resolve: either (a) both the hook and `/done` stamp `session_id` where available with a per-session marker fallback in `~/.claude/sessions/active/`, or (b) accept rare double-writes and dedupe in the insights reader.
- **post_install sandbox fidelity (PR A, D6):** a HOME-redirected `claude` CLI may behave differently from prod; the sandbox proves "runs without error," not "does the right thing." Runtime truth still comes from the real install + Step-5 `claude plugin list` verify.
- **`verify-caveats.sh` project-contract versioning (PR A, spec risk #2):** version the expected-output contract so downstream per-project scripts don't break silently when craft changes the format.
- **Tap-absent leg (PR A, spec risk #1 / agent-1 #1):** mirror `verify-surfaces.sh` — warn only, never block, when the tap isn't locally checked out (ubuntu CI has no local tap).

---

## Sequencing (locked)

1. **Quick-wins + skill-standards** → direct to `dev`, no worktree. (`insights.md:62` false-auto fix · `ADR-001-workflow-branch-guard.md` · release-runbook `@local-plugins` note · `.claude-plugin/skills/validation/skill-standards-check.md` advisory validator.) `Closes #171` (+ release-PR body).
2. **PR A** `feature/homebrew-dist-gates` (worktree, separate session) — verify-caveats (Checks 1–4) + post_install structural/sandbox gate + aggregator-sync blocking + Cowork Step 10d. `Closes #200, #199`.
3. **PR B** `feature/insights-session-hook` (worktree, separate session, parallel to PR A) — `SessionEnd` facet hook + installer + `insights.md:62` already fixed in quick-wins. `Closes #183`.
4. **Single `v2.49.1` release** after all merge to `dev`.
