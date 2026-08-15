# ORCHESTRATE: Prose-Check Hardening

**Spec:** [`docs/specs/SPEC-prose-check-hardening-2026-08-15.md`](docs/specs/SPEC-prose-check-hardening-2026-08-15.md)
**Grill:** [`docs/specs/GRILL-prose-check-hardening-2026-08-15.md`](docs/specs/GRILL-prose-check-hardening-2026-08-15.md) — 5 branches locked
**Worktree:** `~/.git-worktrees/craft/feature-doc-staleness-prose-gaps` (exists)
**Branch:** `feature/doc-staleness-prose-gaps` · **PR:** #334 (open, CI green, **do not merge until P6**)

## Objective

Close the 9 defects a high-effort review found in PR #334, per the grill's 5 locked decisions, on
the same branch — so #334 never ships a check that emits false positives or corrupts prose.

## Phase 2 blocker — RESOLVED 2026-08-15

The spec listed 9 decisions; the grill locked 5. The gap was the release-date **window
discipline** (spec D4 / finding F3), surfaced while writing this plan: the grill settled the
*authority* but not *how claims are collected*, so prose like "Upgrading to v4.5.0 is a drop-in
change" would still open a window and turn a nearby unrelated date into a claim for v4.5.0.

**Locked (ledger D6): the version token must appear in a heading or a version-box line to open the
window.** Running prose is excluded by construction rather than by tuning a distance, and every
site that carries a real release entry today is a heading or a box.

## Phase Overview

| # | Phase | Findings | Locked by | Est |
|---|-------|----------|-----------|-----|
| 1 | Matcher, fix payload, floor | F1, F2, F6 | D3 | 20 min |
| 2 | Check 1 → cross-file consistency | F3, F7 | D1 (+ blocker above) | 25 min |
| 3 | Severity split + ADR correction | F5 | D2 | 15 min |
| 4 | Exclusion round-trip, record-level | F4 | D4 | 25 min |
| 5 | Low findings + doc sync | F8, F9 | not branched | 15 min |
| 6 | Verify + update PR #334 | — | D5 | 20 min |

Sequential. Phases 1 and 3 are independent of 2 and 4; 5 depends on all of them; 6 is last.

## Phase 1 — Matcher, fix payload, floor (D3)

- [ ] Trailer: `([^a-z]|$)` → whitespace / closing punctuation / end-of-line, in the check-2
      matcher **and** awk's `hascount()` pre-filter (they must agree, or the pre-filter drops lines
      the matcher would have caught)
- [ ] Floor: `expected * 40 / 100` → `max(2, expected * 40 / 100)`
- [ ] Fix payload: build the substitution from the full matched span, not the bare `N noun` prefix
- [ ] Fixtures: `falsepos/hyphenated-compounds.md` (`command-line`, `agent-facing`,
      `skill-authoring`, `agents-only` — all must be GREEN)
- [ ] Fixtures: `defect/small-count-agents.md` — a wrong agent count that the zero floor used to
      let through only by accident, now caught deliberately
- [ ] **Pin E1 survives:** `clean/structure-table-correct.md` and
      `defect/structure-table-singular.md` must pass unchanged — `8 agent definitions` has a space
      after the noun and `8 ≥ max(2, 0)`
- [ ] Mutation control per change: revert the trailer → hyphen fixture fails; revert the floor →
      small-count fixture fails; revert the span anchor → a fix-application test corrupts prose

## Phase 2 — Check 1 → cross-file consistency (D1, D6)

- [ ] Window opens only on a **markdown heading** or a version-box line containing the version
      token — not on any line mentioning it (D6, closes F3)
- [ ] Replace `resolve_release_date` / `compute_release_date_window` / `release_date_accepted`
      with claim collection + pairwise agreement (one-day tolerance retained)
- [ ] Fixture: `falsepos/version-mentioned-in-prose.md` — "Upgrading to v4.5.0 is a drop-in
      change" followed by an unrelated `Released:` date → GREEN
- [ ] Delete `CRAFT_RELEASE_DATE`; the harness no longer needs to inject an authority
- [ ] Report shape: name **both** disagreeing sites, not one — a finding that names only one file
      cannot be acted on
- [ ] Vacuous when fewer than 2 claims exist (ADR-007's rule: report only what you can establish)
- [ ] Fixtures: `defect/release-date-disagreement.md` pair; `clean/release-date-utc-boundary.md`
      updated to a 2-claim form one day apart → GREEN
- [ ] Delete `defect/release-date-far-edge.md` and `defect/version-box-stale-date.md` or rewrite
      them for the new model — they encode a tag authority that no longer exists
- [ ] **Prove it fires where it matters:** run at the release gate's point in the pipeline (before
      any tag exists) and in a tags-less checkout, and quote both transcripts

## Phase 3 — Severity split + ADR correction (D2)

- [ ] Check 1 → `error`; check 2 stays `warning`
- [ ] `print_phase_status` / phase label handling copes with mixed severities in one phase
- [ ] ADR-007 Severity section: **remove** the false claim (that both severities fail the gate
      identically), replace with the verified behavior — `pre-release-check.sh:280` swallows the
      exit code, `docs-quality.yml` sets `continue-on-error`, `skills/release/SKILL.md:143` blocks
      on the RED label
- [ ] Test: a check-1 finding makes overall status RED; a check-2-only finding stays YELLOW

## Phase 4 — Exclusion round-trip, record-level (D4)

- [ ] `add_finding` takes line number as its own argument instead of glued into `file`
- [ ] Update every caller across Phases 6–9 (Phase 7 line ~341, Phase 9 ~497/~548, plus the new
      prose calls)
- [ ] JSON output preserves today's `file` rendering (`path:lineno`) so consumers do not break —
      the split is internal
- [ ] `[e]` writes `path:pattern`, matching `is_pattern_excluded`
- [ ] **E2E, not inspection:** write the exclusion, re-run, assert the finding is gone
- [ ] Mutation control: revert the record change → the round-trip test fails

## Phase 5 — Low findings + doc sync (F8, F9)

- [ ] F8: close `version-box` mode at the first line carrying no box character
- [ ] F8 fixture: unclosed `┌` followed by a `commands/` structure-table row → the row is still
      measured against commands, not agents
- [ ] F9: REFCARD `tldr` row → "a line that **opens** with `TL;DR`"
- [ ] Sync REFCARD, both CHANGELOGs, and the parent
      `SPEC-doc-staleness-prose-gaps-2026-08-07.md` (its check-1 description is now wrong)
- [ ] Mark the hardening SPEC's acceptance criteria

## Phase 6 — Verify + update PR #334 (D5)

- [ ] Full suite in-tree; compare against the dev baseline (20 failed / 2462 passed)
- [ ] `docs-staleness-check.sh` GREEN, runtime under the 30s `test_pre_release_check_runs` budget
- [ ] `validate-counts.sh`, markdownlint, `mkdocs build --strict`
- [ ] Update the PR #334 body with the hardening summary and quoted E2E transcripts
- [ ] Watch CI to green — **then stop.** Merging is a separate, explicit instruction.

## Friction Prevention

- **The awk pre-filter and the bash matcher must stay in sync** (Phase 1). They are two regexes
  expressing one rule; if the pre-filter is tighter, lines silently never reach the matcher. This
  already caused a 4× perf regression once when they were tuned independently.
- **Runtime budget is real, not theoretical.** `test_pre_release_check_runs` times out at 30s and
  it is the only thing that caught the last perf regression. Re-time after Phase 2.
- **Do not widen the broad plural-only scan.** Every hardening here is inside the line shapes; the
  unscoped scan stays plural-only or the 90+ false positives return.
- **Phase 4 has the largest blast radius** — it touches a record consumed by four phases, JSON
  output, and both fix passes. Run the whole suite after it, not just the prose tests.

## Acceptance Criteria

- [ ] Every finding F1–F9 has a test that **fails before its fix and passes after**, each verified
      by planted mutation
- [ ] Hyphenated-compound corpus produces zero findings; real counts still caught
- [ ] `[e]xclude` round-trips end-to-end
- [ ] ADR-007's incorrect severity claim is removed, not softened
- [ ] Check 1 demonstrably fires with no tag present — transcript quoted
- [ ] Live repo GREEN; runtime under budget; dev-baseline parity

## Commit Strategy

One commit per phase, conventional prefix, each naming the finding IDs it closes. Phase 4 commits
alone given its blast radius. No squashing before review — the phase boundaries are the review
units.

## Verification

```bash
cd ~/.git-worktrees/craft/feature-doc-staleness-prose-gaps
python3 -m pytest tests/test_docs_staleness_prose.py -q     # per phase
./scripts/docs-staleness-check.sh                            # GREEN
time ./scripts/docs-staleness-check.sh                       # under 30s
python3 -m pytest tests/ -q                                  # after Phase 4 and at Phase 6
```

## Session Instructions

Implementation continues in this session per craft's ORCHESTRATE convention (no handoff to a new
session). Resolve the Phase 2 blocker before starting Phase 2 — ask, do not guess.
