# SPEC: Governance Retro Hardening (#205)

**Status:** APPROVED (design) · **Date:** 2026-06-25 · **Issue:** [#205](https://github.com/Data-Wise/craft/issues/205)
**Source flow:** craft review → superpowers:brainstorming → superpowers:writing-plans

## Problem

The skill-ecosystem governance system is "roadmap complete" (v2.43–v2.47: Phase 0–2,
soak-then-flip, cross-repo wrapper, R03/R04, suite 47→59). #205 files four
post-completion **hardening + proportionality** items — not new scope — plus a meta
recommendation to freeze and soak.

A code review (2026-06-25) grounded each item against the actual tree and **materially
re-scoped two of four**:

| # | Issue's claim | Reality in code |
|---|---------------|-----------------|
| 1 | `.STATUS` is hand-stamped prose that drifts; add a `status_drift` check | **True.** Clean checker pattern exists (`no_drifted_copy.py`). Real new work. |
| 2 | Soak-poison is only a memory note; `grep poison` finds no test | **Largely pinned already.** `soak.py:58` `setdefault` never resets `first_seen`; `test_record_audit_preserves_first_seen_across_runs` + `test_record_audit_clears_then_restamps_red` pin the invariant. R04 pinned by 3 tests. Gap: one explicitly-named end-to-end promotion-poison test. |
| 3 | #184 advisory downgrade should be a recorded ADR | **True, pure doc.** Advisory confirmed (`pre-release-check.sh:326–334`, never touches `$ERRORS`), pinned by `TestReleaseGuard184`. Next ADR number is 003. |
| 4 | `session_hook.py` supersedes the `skills-audit.py --write-index` line → remove it | **Premise mostly false.** `session_hook.py` does NOT write an index (it audits + feeds the soak ledger, *reads* the index) and is **not wired into `settings.json`**. `skills-audit.py --write-index` is the sole writer. No double-write exists. |

## Decision

**Scope: hardening + `status_drift` (`severity: warn`), with the feature freeze recorded
in ADR-003.**

Rationale for including item 1 despite the P7 freeze: P7 forbids governance becoming a
*new maintenance project* (new phases). `status_drift` is not a new phase — it **completes
the existing "data-not-prose" thesis on the one load-bearing artifact still hand-stamped**
(`.STATUS`). It reuses the existing engine (one `warn` rule + one checker following the
established pattern — zero new machinery) and is advisory, so it cannot block. In-session
evidence of need: `.STATUS`'s branch table was found stale at v2.48.0 while the repo was at
v2.50.0 on 2026-06-25 — exactly the drift `status_drift` flags. ADR-003 records that this is
the **last governance addition before a real-use freeze**.

## Deliverables

### D1 — `status_drift` check (the only runtime code)

**New:** `governance/checks/status_drift.py`, mirroring `governance/checks/no_drifted_copy.py`.

- **Exit contract:** `0` pass / vacuous · `1` drift found · `2` usage error. Vacuous-skip
  (exit 0, announced on stdout) when `.STATUS` is absent or the checked claims are
  unparseable — never a false positive.
- **Modes:**
  - **LIVE** (`status_drift.py <repo_root>`): parse `.STATUS`; derive ground truth from the
    manifest source-of-truth (`plugin.json` `version` / `DESCRIPTION` `Version` /
    `package.json` `version`, first found) and from `git` (tag → commit).
  - **FIXTURE** (`status_drift.py <fixture_root>`): detect `good/` + `bad/` subdirs;
    ground-truth values are supplied as **pure files** in the fixture (a sidecar
    `expected.json` with `{version, released_tags}`) so tests need **no git fixture**.
    This is the key isolation decision: the checker accepts ground truth as data; only LIVE
    mode shells out to `git`.
- **Claims checked (load-bearing only — keep the surface small):**
  1. `version:` frontmatter field vs the manifest version → drift if mismatch.
  2. A "released/synced to vX" claim (frontmatter `milestone:`/`version:` or the Branch
     Status table) vs the actual git **tag** `vX` existing → drift if the claim names a
     release whose tag is missing.
- **Registration:** new `RULES.yaml` rule `R09-status-not-drift` (R01–R08 exist; R09 is next),
  `severity: warn`, `status: active`, `gates: [release]`, `check.kind: script`,
  `check.cmd: "checks/status_drift.py {target}"`, `check.fixtures: {good, bad}`.
  `run_rules.py --selftest` auto-validates good→0, bad→1.
- **Fixtures:** `governance/fixtures/status-not-drift/{good,bad}/` — each a `.STATUS` +
  `expected.json`; good is consistent, bad has a version mismatch.

### D2 — Soak-poison regression test (test only)

**New test** in `tests/test_governance_dogfood.py` (governance marker), explicitly named for
the failure mode, e.g. `test_promotion_not_poisoned_by_repeated_clean_audits`:

- A `warn` rule that has soaked clean for `>= window_days` with `last_red` null/old becomes
  `promotion_eligible == True`, and **stays** eligible across repeated clean audits (no
  silent reset).
- A transient RED → clean restamps `last_red` to the RED date (not the clean date) and does
  not permanently block promotion once the window re-clears.
- The spec records that R04 content-drift is **already** pinned (`test_drifted_copy_checker`,
  `test_r04_runs_as_a_script_rule_in_audit`, `test_live_env_never_errors`) — no new R04 work.

### D3 — ADR-003: release-drift advisory, not hard gate (doc only)

**New:** `docs/adr/ADR-003-release-drift-advisory-not-hard-gate.md` (+ `site/adr/` mirror),
in the ADR-001/002 format. Records:

- **Context:** #184 landed the release-time governance check as an *advisory* (prints RED
  count, never increments `$ERRORS`), a deliberate downgrade from the proposal's "hard guard."
- **Decision:** keep it advisory for a solo maintainer who reads their own output
  (gentle-ramp; a human ignores a warning as easily as its absence, so a hard gate buys
  little for one reader). Revisit if a missed-drift incident recurs.
- **Consequence / freeze marker:** this is the last governance addition before a real-use
  feature freeze (P7).

### D4 — Hook reconciliation note (doc only, in-repo)

**Edit:** `governance/README.md` — add a short "SessionStart coordination" note recording the
division of labor and decision:

- `session_hook.py` = audit + soak-ledger feed; it **reads** `SKILLS-INDEX.md`, does not write it.
- `skills-audit.py --write-index` (in `~/.claude/settings.json`) = the **sole** index writer; **keep it**.
- Wiring `session_hook.py` globally remains **deferred** (point at the released plugin path
  when done). No `settings.json` change in this work — the documented non-conflict closes the
  coordination ambiguity #205 item 4 raised.

## Non-goals / YAGNI

- No hard release gate (explicitly deferred by D3).
- No `settings.json` / global-hook edits.
- No new governance *phase*; `status_drift` is the final additive rule before the freeze.
- `status_drift` checks only the two load-bearing claims above — not the full `.STATUS` prose.

## Isolation & testing

- D1 is the single code unit: self-contained checker, `warn`-only (cannot block), validated by
  `--selftest` fixtures + one targeted test. Internals changeable without touching consumers.
- D2 is test-only; D3/D4 are docs. Combined runtime risk: none beyond D1, which is advisory.
- Acceptance: `--selftest` green for the new rule; new soak test green; ADR + README render in
  docs (mkdocs build clean); full governance suite stays green.

## Sequencing (for writing-plans)

1. D1 checker + fixtures + RULES.yaml rule (TDD: fixture selftest first).
2. D2 soak-poison test.
3. D3 ADR-003. 4. D4 README note. (3 and 4 are independent docs.)
