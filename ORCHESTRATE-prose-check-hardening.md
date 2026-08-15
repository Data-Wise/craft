# ORCHESTRATE: Prose-Check Hardening

**Spec:** [`docs/specs/SPEC-prose-check-hardening-2026-08-15.md`](docs/specs/SPEC-prose-check-hardening-2026-08-15.md)
**Grill:** [`docs/specs/GRILL-prose-check-hardening-2026-08-15.md`](docs/specs/GRILL-prose-check-hardening-2026-08-15.md) — 11 branches locked (D1–D6 spec, D7–D11 plan)
**Worktree:** `~/.git-worktrees/craft/feature-doc-staleness-prose-gaps` (exists)
**Branch:** `feature/doc-staleness-prose-gaps` · **PR:** #334 (open, CI green, **do not merge until P6**)

## Objective

Close the 9 defects a high-effort review found in PR #334, per the grill's locked decisions, on the
same branch — so #334 never ships a check that emits false positives or corrupts prose.

## Phase Overview

**Reordered per D7:** the record change goes first. As originally written, Phases 1–3 authored
`add_finding` calls and tests against the old signature and Phase 4 then rewrote all 12 call sites —
every prose finding written twice, its tests touched twice, and the mechanical sweep landing where
a missed site is likeliest.

| # | Phase | Findings | Locked by | Est |
|---|-------|----------|-----------|-----|
| 1 | Finding record: line number as its own field | F4 | D4, D7 | 45 min |
| 2 | Matcher, fix payload, floor | F1, F2, F6 | D3 | 25 min |
| 3 | Check 1 → cross-file consistency | F3, F7 | D1, D6, D8 | 40 min |
| 4 | Severity split + ADR correction | F5 | D2, D11 | 20 min |
| 5 | Low findings, date normalization, doc sync | F8, F9 | D9 | 25 min |
| 6 | Verify, promote, update PR #334 | — | D5, D10, D11 | 30 min |

**Estimate honesty (D11):** ~3 hours, not the 2 first written. Phase 1 alone is 12 call sites plus
JSON rendering plus both fix passes plus an end-to-end exclusion test; 25 minutes was wishful.

Sequential. Phase 1 must complete before any other phase touches `add_finding`.

## Phase 1 — Finding record: line number as its own field (D4, D7)

Goes first so every later phase is written once, against the final signature, and so the
largest-blast-radius change lands against an unmodified baseline where the full suite is a clean
control.

- [ ] `add_finding` takes line number as its own argument instead of glued into `file`
- [ ] Update all 12 call sites: Phase 6 (×2), Phase 7 (×3), Phase 8 (×3), Phase 9 (×4)
- [ ] JSON output preserves today's `file` rendering (`path:lineno`) so consumers do not break —
      the split is internal
- [ ] `[e]` writes `path:pattern`, matching what `is_pattern_excluded` parses
- [ ] **E2E, not inspection:** write the exclusion, re-run, assert the finding is gone
- [ ] Mutation control: revert the record change → the round-trip test fails
- [ ] **Full suite after this phase**, not just the prose tests — this is the widest change here

## Phase 2 — Matcher, fix payload, floor (D3)

- [ ] Trailer: `([^a-z]|$)` → whitespace / closing punctuation / end-of-line, in the check-2
      matcher **and** awk's `hascount()` pre-filter (they must agree, or the pre-filter drops lines
      the matcher would have caught)
- [ ] Floor: `expected * 40 / 100` → `max(2, expected * 40 / 100)`
- [ ] Fix payload: build the substitution from the full matched span, not the bare `N noun` prefix
- [ ] Fixture `falsepos/hyphenated-compounds.md`: `command-line`, `agent-facing`,
      `skill-authoring`, `agents-only` — all GREEN
- [ ] Fixture `defect/small-count-agents.md`: a wrong agent count the zero floor used to pass only
      by accident, now caught deliberately
- [ ] **Pin E1 survives:** `clean/structure-table-correct.md` and
      `defect/structure-table-singular.md` pass unchanged — `8 agent definitions` has a space after
      the noun and `8 ≥ max(2, 0)`
- [ ] Mutation control per change: revert the trailer → hyphen fixture fails; revert the floor →
      small-count fixture fails; revert the span anchor → a fix-application test corrupts prose

## Phase 3 — Check 1 → cross-file consistency (D1, D6, D8)

- [ ] Window opens only on a **markdown heading** or a version-box line containing the version
      token — not on any line mentioning it (D6, closes F3)
- [ ] Replace `resolve_release_date` / `compute_release_date_window` / `release_date_accepted`
      with claim collection + pairwise agreement (one-day tolerance retained)
- [ ] Delete `CRAFT_RELEASE_DATE`; the harness no longer injects an authority
- [ ] Report shape names **both** disagreeing sites — a finding naming one file cannot be acted on
- [ ] Vacuous when fewer than 2 claims exist (ADR-007: report only what you can establish)
- [ ] **Rewrite, never delete, the two existing check-1 fixtures (D8).** The window still exists
      under D6, so the off-by-one class is still live and `defect/release-date-far-edge.md` is its
      only positive control — the exact bug `/code-review` caught. Rewrite it as: heading at line N,
      disagreeing claim at the window's last line → still RED. Rewrite
      `defect/version-box-stale-date.md` as an in-box disagreement, since boxes are where the
      original REFCARD bug lived.
- [ ] Fixture `falsepos/version-mentioned-in-prose.md`: "Upgrading to v4.5.0 is a drop-in change"
      followed by an unrelated `Released:` date → GREEN
- [ ] Fixture `defect/release-date-disagreement.md` pair; `clean/release-date-utc-boundary.md`
      rewritten to a two-claim form one day apart → GREEN

**Real claim sites, confirmed 2026-08-15** — the check must reach both:

| Site | Shape | Reached via |
|---|---|---|
| `docs/NEWS.md:9` | `**Released:** 2026-08-08` | `## v4.5.0 …` heading two lines above |
| `docs/REFCARD.md:7` | `│  Version: 4.5.0 (released 2026-08-07)` | version-box line, claim on the same line |

## Phase 4 — Severity split + ADR correction (D2, D11)

- [ ] Check 1 ships as **`warning`** in this phase. Promotion to `error` happens in Phase 6, gated
      on evidence (D11) — the check is being redesigned and promoted in one PR, and the only
      evidence it is sound would otherwise be tests written alongside it.
- [ ] `print_phase_status` / phase-label handling copes with mixed severities in one phase
- [ ] ADR-007 Severity section: **remove** the false claim (that both severities fail the gate
      identically), replace with verified behavior — `pre-release-check.sh:280` swallows the exit
      code, `docs-quality.yml` sets `continue-on-error`, `skills/release/SKILL.md:143` blocks on
      the RED label. Record the D11 gate as the reason RED is earned, not assumed.
- [ ] Test: a check-1 finding makes overall status RED once promoted; a check-2-only finding stays
      YELLOW

## Phase 5 — Low findings, date normalization, doc sync (D9)

- [ ] F8: close `version-box` mode at the first line carrying no box character
- [ ] F8 fixture: unclosed `┌` followed by a `commands/` structure-table row → the row is still
      measured against commands, not agents
- [ ] F9: REFCARD `tldr` row → "a line that **opens** with `TL;DR`"
- [ ] **Normalize the two claim sites (D9).** `NEWS.md` and `REFCARD.md` currently sit exactly one
      day apart (2026-08-08 vs 2026-08-07), so the tolerance is the only thing keeping the repo
      GREEN. Make them agree on the tag-local date and record the convention where the release
      skill writes these, so the tolerance is headroom rather than load-bearing.
- [ ] Sync REFCARD, both CHANGELOGs, and the parent
      `SPEC-doc-staleness-prose-gaps-2026-08-07.md` — its check-1 description is now wrong
- [ ] Mark the hardening SPEC's acceptance criteria

## Phase 6 — Verify, promote, update PR #334 (D5, D10, D11)

- [ ] Full suite in-tree; compare against the dev baseline (20 failed / 2462 passed)
- [ ] `docs-staleness-check.sh` GREEN; runtime under the 30s `test_pre_release_check_runs` budget
- [ ] `validate-counts.sh`, markdownlint, `mkdocs build --strict`
- [ ] **D11 promotion gate:** check 1 ran clean across every tracked `.md` and both known claim
      sites, transcript quoted → promote to `error`. If not clean, it **stays `warning`** and the
      promotion becomes a follow-up. Do not promote on a passing unit suite alone.
- [ ] **D10:** refresh the `.STATUS` worktree row — it still describes this branch as only the
      parent SPEC and its harness, with no mention of the hardening work
- [ ] Update the PR #334 body with the hardening summary and quoted E2E transcripts
- [ ] Watch CI to green — **then stop.** Merging is a separate, explicit instruction.
- [ ] **At merge (D10):** delete `ORCHESTRATE-prose-check-hardening.md`. It is a feature-branch
      working artifact, not `dev` content (craft CLAUDE.md). Nothing enforces this — not
      `.gitignore`, not `exclusions.txt`, not a test — so it only happens if someone does it.

## Friction Prevention

- **The awk pre-filter and the bash matcher must stay in sync** (Phase 2). Two regexes expressing
  one rule; if the pre-filter is tighter, lines silently never reach the matcher. This already
  caused a 4× perf regression once when they were tuned independently.
- **Runtime budget is real, not theoretical.** `test_pre_release_check_runs` times out at 30s and
  is the only thing that caught the last perf regression. Re-time after Phase 3.
- **Do not widen the broad plural-only scan.** Every hardening here is inside the line shapes; the
  unscoped scan stays plural-only or the 90+ false positives return.
- **Phase 1 has the largest blast radius** — a record consumed by four phases, JSON output, and
  both fix passes. Full suite after it, not just the prose tests.
- **Never delete a positive control to make a redesign easier** (D8). If a fixture's model is
  obsolete, rewrite it so the boundary it pinned stays pinned.

## Acceptance Criteria

- [ ] Every finding F1–F9 has a test that **fails before its fix and passes after**, each verified
      by planted mutation
- [ ] Hyphenated-compound corpus produces zero findings; real counts still caught
- [ ] `[e]xclude` round-trips end-to-end
- [ ] ADR-007's incorrect severity claim is removed, not softened
- [ ] Check 1 reaches both real claim sites (`docs/NEWS.md`, `docs/REFCARD.md`) — transcript quoted
- [ ] The two claim sites agree exactly, so the one-day tolerance is headroom (D9)
- [ ] RED promotion is evidence-gated, not assumed (D11)
- [ ] Live repo GREEN; runtime under budget; dev-baseline parity

## Commit Strategy

One commit per phase, conventional prefix, each naming the finding IDs it closes. Phase 1 commits
alone given its blast radius. No squashing before review — the phase boundaries are the review
units.

## Verification

```bash
cd ~/.git-worktrees/craft/feature-doc-staleness-prose-gaps
python3 -m pytest tests/test_docs_staleness_prose.py -q     # per phase
python3 -m pytest tests/ -q                                  # after Phase 1 and at Phase 6
./scripts/docs-staleness-check.sh                            # GREEN
time ./scripts/docs-staleness-check.sh                       # under 30s
```

## Session Instructions

Implementation continues in this session per craft's ORCHESTRATE convention (no handoff to a new
session). Every phase ends with its mutation controls demonstrated, not merely a passing suite.
