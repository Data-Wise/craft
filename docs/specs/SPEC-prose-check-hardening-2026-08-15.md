# Prose-Check Hardening — Spec

**Generated:** 2026-08-15
**Context:** Craft v4.5.0 — hardens the Phase 7 prose checks added in PR #334
**Sources:** high-effort `/code-review` of PR #334 (9 findings), plus
[`SPEC-doc-staleness-prose-gaps-2026-08-07.md`](SPEC-doc-staleness-prose-gaps-2026-08-07.md)
and [ADR-007](../adr/ADR-007-pattern-scoped-prose-staleness-gating.md)
**Status:** grilled 2026-08-15 — 5 branches locked, ready to implement. Decisions live in
[`GRILL-prose-check-hardening-2026-08-15.md`](GRILL-prose-check-hardening-2026-08-15.md); where
this spec's option tables and the ledger differ, **the ledger wins**.

---

## Problem

PR #334 added two prose checks to `docs-staleness-check.sh` Phase 7. CI is green, the full suite
passes, and the live repo reports GREEN. An adversarial review nonetheless found 9 defects, 7 of
which are invisible to every gate the repo has, because the gates only prove the checks don't fire
on *craft's current docs* — not that they fire correctly on any other input.

Two of the nine make the feature **worse than not having it**, and one suggests it may never fire
where it was designed to.

## Verified findings

Each reproduced against the real script before being written down. F1, F2, F6 reproduced by
constructing input; F5, F7 by reading the consuming code.

| ID | Sev | Defect | Evidence |
|----|-----|--------|----------|
| F1 | HIGH | The singular matcher's `([^a-z]\|$)` trailer accepts `-`, so hyphenated compounds read as counts | `30 command-line entry points` → `'30 command' (expected 48)`; `3 agent-facing surfaces` → `'3 agent' (expected 2)` |
| F2 | HIGH | Accepting the offered fix **corrupts that prose**: the substitution is built from the bare `N noun` prefix | `[f]ix` rewrites `30 command-line entry points` → `48 command-line entry points` |
| F3 | MED | Release-date window is proximity-only — any line mentioning the version opens it, with no requirement the date belongs to that version | an upgrade guide saying "Upgrading to v4.5.0 is a drop-in change" claims the next `Released:` date within 4 lines |
| F4 | MED | Pass 2 `[e]xclude` is a no-op for every Phase 7 prose finding | `file` is now `path:lineno`, so the entry written is `docs/x.md:3:30 command`; `is_pattern_excluded` splits on the first colon and can never match |
| F5 | MED | ADR-007's stated basis for `warning` over `error` is factually wrong | `pre-release-check.sh:280` is headed "warn-only, does not block release" and swallows the exit with `\|\| true`; `docs-quality.yml` sets `continue-on-error: true`; `skills/release/SKILL.md:143` says "RED findings block; YELLOW findings warn" |
| F6 | MED | The 40%-of-expected floor is **0** for agents | `$((2 * 40 / 100))` == 0, so the guard ADR-007 cites as what makes shaped lines safe is absent for the smallest count type |
| F7 | MED | Check 1 is vacuous in both automated environments it targets | `docs-quality.yml` uses `actions/checkout@v5` with no `fetch-tags`, so no tag exists → silent skip on every CI run; and release writes NEWS/REFCARD dates *before* the tag is created |
| F8 | LOW | An unclosed `┌` puts the rest of the file in `version-box` mode, losing the `structure-table` type restriction | a `commands/` row then gets measured against the agent count |
| F9 | LOW | REFCARD says `tldr` matches "a line containing `TL;DR`"; the regex requires the line to *open* with it | doc contradicts implementation |

### Root causes, not nine unrelated bugs

Grouping matters more than the count — patching nine sites individually would leave the classes open.

- **C1 — "one more character class" reasoning.** F1 and F8 are both boundary conditions on a
  regex written for the cases in front of it. F1 assumed word-final; F8 assumed boxes close.
- **C2 — a guard cited but not verified.** F6: ADR-007 and two code comments claim the 40% floor
  makes shaped lines safe. Nobody evaluated it for the smallest count. F1's agent half is a
  *consequence* of F6, not an independent bug.
- **C3 — reporting a result never established.** F2 and F4, both the same family PR #334 already
  fixed once in `[f]`. **Corrected during the grill:** F4 was first written up here as introduced
  by this PR's change of `file` to `path:lineno`. It is not —
  `git show dev:scripts/docs-staleness-check.sh` already has `add_finding 7 "warning"
  "${file}:${lineno}"` at line 341, and the same shape in Phase 9 at 497 and 548. `[e]xclude` has
  been a no-op for **all** Phase 7 and Phase 9 findings, predating this PR.
- **C4 — the check was never exercised where it runs.** F3, F5, F7: proximity heuristic never
  tested against adversarial prose; severity chosen from an unverified claim about consumers;
  authority never checked for availability in CI or at release time.

## Decisions required

These are open. Options are listed with the tradeoff, not pre-resolved.

| # | Decision | Options |
|---|----------|---------|
| D1 | F1 trailer fix | (a) `([^a-z-]\|$)` — minimal; (b) also exclude `'` and Unicode dashes; (c) require the noun be followed by whitespace/punctuation via an explicit allowlist |
| D2 | F6 floor for small counts | (a) `max(2, 40%)`; (b) a fixed absolute floor per type; (c) drop the floor inside shapes and rely on tighter shapes instead |
| D3 | F2 substitution safety | (a) anchor the substitution with the same trailing guard as D1; (b) include the full matched span incl. trailing char; (c) stop offering a fix for prose findings and route to manual edit only |
| D4 | F3 window discipline | (a) require the version token be in a **heading** line; (b) require the date line itself to name the version; (c) keep proximity but shrink to 2 lines; (d) accept the false-positive class and exclude case-by-case |
| D5 | F5 severity, re-decided on correct facts | (a) `error` (RED) — the label *is* the gate per `skills/release/SKILL.md:143`; (b) keep `warning` and correct the ADR's reasoning; (c) `error` for check 1, `warning` for check 2 |
| D6 | F7 CI availability | (a) add `fetch-tags: true` to `docs-quality.yml`; (b) change the authority to `.STATUS`'s `release_date:` with the same one-day window; (c) accept vacuity in CI and document it |
| D7 | F7 release-time ordering | (a) move the check after tag creation; (b) compare against the *version being released* rather than the tag; (c) accept and document |
| D8 | F4 exclusion round-trip | (a) split `file` back into path + lineno in the finding record; (b) have `[e]` strip the `:lineno` suffix before writing |
| D9 | F8 box-close discipline | (a) close the box at the first line with no box character; (b) cap box mode at N lines; (c) require a matching `└` within the same fenced block |

### Non-negotiable, not up for decision

Anything shipped must not **report a result it did not establish** (ADR-007). D3 option (c) and
D5 are constrained by that: an offered fix must be applicable and correct, and a severity must be
chosen from verified consumer behavior rather than an assumption about exit codes.

## Scope

**In:** `scripts/docs-staleness-check.sh` Phase 7 checks and their fix payloads; the pass-2
`[e]` branch; `docs-quality.yml` checkout config if D6(a); ADR-007's severity section; the REFCARD
shape table; fixtures + harness rows for every fix.

**In (added by the grill):** Phase 9's `[e]` findings, which carry the same `path:lineno` shape —
the ledger's D4 fixes this at the record level rather than per-phase, so both are covered by one
change. The git-tag authority and `docs-quality.yml`'s checkout config drop out of scope entirely:
D1 replaces the authority with cross-file consistency, so there is no tag to fetch.

**Out:** the version-highlight proxy (dropped in the parent SPEC, still dropped); porting to
sibling repos; any new script or dependency (D1/D4 of the parent SPEC still hold); Phase 9's
*severity*, which D2 leaves as-is.

## Acceptance criteria

- [x] Every finding F1–F9 has a fixture or test that **fails before the fix and passes after**,
      verified by planted mutation — not merely a passing test after the change. Every phase's
      fix was reverted and re-tested before restoring (F1/F2/F4/F6/F8 confirmed via source
      revert; F3/F7 confirmed by reverting D1/D6 together, since they share one redesign;
      D2/D11's severity confirmed by reverting the severity string itself). This pass also
      caught the broad, unscoped plural-only count scan sharing F1's hyphen-boundary bug
      (`"7 agents-only"` matched as `"7 agents"`) — not separately enumerated as an F-number,
      surfaced by this criterion's own hyphenated-compound corpus, fixed alongside F1/F2.
- [x] A hyphenated-compound corpus (`command-line`, `agent-facing`, `skill-authoring`,
      `agents-only`) produces zero findings, and the corresponding real counts still do —
      `falsepos/hyphenated-compound-tldr.md`.
- [x] `[e]xclude` round-trips: writing the entry actually suppresses the finding on the next run,
      asserted end-to-end rather than by inspecting the written line —
      `test_exclude_round_trips_end_to_end` drives the real `[e]` keystroke through a pty.
- [x] The severity decision (D2, GRILL numbering — the SPEC's own D5 above referred to the
      pre-grill options table) is recorded in ADR-007 with the **verified** consumer behavior,
      and the incorrect claim is removed, not softened.
- [x] Check 1 demonstrably fires — proven by running it, not by reasoning that it should. D1
      dropped the environment dependency this criterion originally asked about (no tag, no CI
      availability concern left to prove); demonstrated instead by injecting a real mismatch
      into `docs/REFCARD.md`'s live date and confirming check 1 caught it
      (`release date '2020-01-01' ... disagrees with other claims (majority: 2026-08-07)`)
      before reverting the injection.
- [x] `docs-staleness-check.sh` stays under the `test_pre_release_check_runs` 30s budget — ~11s.
- [x] Live repo stays GREEN.

## Test plan

| Tier | Coverage |
|------|----------|
| unit | `apply_line_fix` substitution safety for hyphenated spans (D3); floor arithmetic at every count magnitude incl. 1 and 2 (D2) |
| fixture | New `falsepos/` entries for hyphenated compounds and unclosed boxes; new `defect/` entries for each still-must-catch case |
| e2e | `[e]xclude` round-trip through a real `exclusions.txt`; check 1 firing in the D6-selected environment |
| dogfood | live repo GREEN; runtime under budget |
| negative | planted mutation per fix — the point is that each new test can fail |

## Risks

- **D4 and D6/D7 may interact.** If the authority moves to `.STATUS` (D6b), the release-ordering
  problem (D7) changes shape, because `.STATUS` is written in the same commit as the doc dates.
- **Tightening F1 could re-mask the E1 bug** the parent SPEC exists to catch
  (`8 agent definitions` — noun followed by a space, so it should survive; must be pinned).
- **D5 → `error` makes this a release blocker.** Every remaining false positive becomes a blocked
  release rather than a warning, which raises the bar on D1/D2/D3 being right.

## Next step

Grill this spec before implementing. The decisions most worth attacking: **D5** (severity, given
the corrected facts), **D6/D7** (whether check 1 can fire anywhere that matters), and **D4**
(whether proximity is salvageable at all).

> Interrogated by grill — see [GRILL-prose-check-hardening-2026-08-15.md](GRILL-prose-check-hardening-2026-08-15.md)
