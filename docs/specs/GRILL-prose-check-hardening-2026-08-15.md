# GRILL: Prose-Check Hardening

**Date:** 2026-08-15 · **Spec:** [`SPEC-prose-check-hardening-2026-08-15.md`](SPEC-prose-check-hardening-2026-08-15.md)
**Branches resolved:** 11 (D1–D6 design · D7–D11 plan) · **Status:** locked, ready for implementation

Interrogates the 9 defects a high-effort review found in PR #334. Two branches were reframed by
evidence gathered during the grill rather than by argument — see D1 and the correction under D4.

---

## D1 — Check 1's authority: **cross-file consistency**, not the git tag

**Locked:** drop the external authority. Compare every release-date claim for the current version
against each other and flag disagreement. The one-day window survives as the agreement tolerance
between claims, absorbing the UTC-boundary case that motivated it.

**Why the tag was rejected — evidence, not preference.** The tag is absent in both environments
the check exists to protect:

| Environment | Why no tag |
|---|---|
| Release gate | `skills/release/SKILL.md` runs Step 3b (write doc dates) → **Step 3b.5 (staleness gate)** → Step 8 (create tag). The tag for the version being released does not exist when the gate runs. |
| CI | `docs-quality.yml` uses `actions/checkout@v5` with no `fetch-tags`, so `git for-each-ref refs/tags/vX.Y.Z` returns empty. |

Net: as built, check 1 fires only on a developer machine that has already pulled the tag — which
is not a gate. Cross-file consistency needs no external authority, so it works in both.

**Accepted cost:** cannot catch a date that is uniformly wrong in every file, and says nothing
when only one claim exists. Both are strictly better than never firing.

## D2 — Severity: **split — check 1 RED, check 2 YELLOW**

**Locked:** severity follows demonstrated precision, per-check rather than per-phase.

**Corrects a factually wrong claim in ADR-007.** The ADR justified `warning` by asserting that
warnings and errors both fail the release gate, so only the label differs. Verified false:

- `scripts/pre-release-check.sh:280` — "Check 9: Docs staleness (warn-only, does not block
  release)", and the call is `… || true`, discarding the exit code.
- `.github/workflows/docs-quality.yml` — `continue-on-error: true`.
- `skills/release/SKILL.md:143` — "RED findings block; YELLOW findings warn but allow proceed."

No consumer reads the exit status. The **label is the only gate**, so the severity choice *is* the
block decision the ADR claimed it was not. ADR-007's Severity section must be rewritten with the
verified behavior — removed, not softened.

Check 1 after D1 is near-binary (two claims agree or they do not), so it can afford to block.
Check 2 matches prose patterns and produced three false-positive defects in this PR alone
(F1, F6, and the five sub-threshold counts caught pre-merge), so it has not earned a blocker.

## D3 — F1/F2/F6: **boundary + span-anchored substitution + real floor**, all three

**Locked:**

| Change | From | To |
|---|---|---|
| Noun trailer | `([^a-z]\|$)` | whitespace / closing punctuation / end-of-line |
| Fix payload | substitution built from the bare `N noun` prefix | anchored on the full matched span |
| Floor | `expected * 40 / 100` | `max(2, expected * 40 / 100)` |

**Why all three, not just the trailer.** F1's agent half is *caused* by F6 — the floor is
`$((2 * 40 / 100))` == 0, so the guard ADR-007 and two code comments cite as what makes shaped
lines safe does not exist for the smallest count type. Fixing the trailer alone leaves that root
cause live. And F2 corrupts the author's prose, a worse outcome than any false warning, so the
substitution is anchored independently of the matcher: a future boundary regression then produces
a wrong warning rather than a wrong edit.

**Must stay pinned:** the E1 case (`8 agent definitions`) survives both changes — the noun is
followed by a space, and `8 ≥ max(2, 0)`. Existing `clean/structure-table-correct.md` and
`defect/structure-table-singular.md` already cover it; they must keep passing unchanged.

## D4 — F4 `[e]xclude` no-op: **fix at the record level, both phases**

**Correction made during the grill.** This was initially reported, and relayed, as a regression
introduced by PR #334's change of the finding's `file` field to `path:lineno`. It is not.
`git show dev:scripts/docs-staleness-check.sh` has `add_finding 7 "warning" "${file}:${lineno}"`
at line 341 and the same shape in Phase 9 at 497 and 548. `[e]xclude` has been a no-op for **all**
Phase 7 and Phase 9 findings, predating this PR.

**Locked:** carry the line number as its own field instead of glued into `file`, so `[e]` writes
`docs/x.md:30 command` and `is_pattern_excluded` can match it.

**Why the larger blast radius is accepted.** The bug prints "Excluded (added to exclusions.txt)"
and the finding returns on the next run — a live instance of the exact
reports-success-changes-nothing class ADR-007 states as a rule. Shipping that rule while the same
file violates it twice is worse than either fixing it or not writing the rule. Fixing it in the
`[e]` branch alone would leave the underlying ambiguity (is `file` a path or a location?) for the
next person.

## D5 — Delivery: **amend PR #334 before merging**

**Locked:** all fixes land on `feature/doc-staleness-prose-gaps`; nothing merges until the checks
are correct.

**Why not merge-then-harden.** As it stands the check false-positives on any hyphenated compound,
and pass 2's `[f]` would rewrite the author's prose around it. craft's own docs are hyphen-heavy,
so "merge now, harden in #335" means `dev` carries a `--fix` that can mangle documents for as long
as the follow-up takes. The PR has not shipped and nothing depends on it, so the cost of holding is
only review surface.

**Accepted cost:** #334 becomes a large single review, and the D4 record change touches all four
phases.

## D6 — Window discipline: **the version token must be in a heading**

**Added 2026-08-15, after the initial 5 branches.** Surfaced while authoring
`ORCHESTRATE-prose-check-hardening.md`: the spec listed 9 decisions and the grill locked 5, leaving
the release-date **window discipline** (spec D4 / finding F3) unresolved. D1 settled where the
authority comes from, not how claims are collected — so the false positive survived the redesign
in a new place.

**Locked:** the window opens only when the version token appears in a markdown heading or a
version-box line. Prose mentioning the version — "Upgrading to v4.5.0 is a drop-in change" — does
not open it, so a nearby unrelated date is never collected as a claim for that version.

**Why structural over numeric.** Shrinking the window (spec D4c) narrows the class without closing
it: a date two lines under a prose mention still false-positives. Requiring version and date on the
same line (D4b) closes it completely but misses the real `docs/NEWS.md` layout, where the heading
carries the version and the date sits two lines below — i.e. it would not catch the bug the check
exists for. A heading requirement excludes running prose by construction, and every site carrying
a real release entry today is a heading or a box.

**Raised stakes:** D2 makes check 1 RED, so each surviving false positive blocks a release. That
rules out spec D4d (accept and exclude case-by-case).

---

## Plan-level branches — grilling `ORCHESTRATE-prose-check-hardening.md`

D1–D6 interrogated the *design*. These interrogate the *plan to build it*, and four of the five
found defects in the plan rather than confirming it.

### D7 — Phase order: **the record change goes first**

**Locked:** reorder to record-change → matcher → check 1 → severity → low findings → verify.

As written, Phases 1–3 authored `add_finding` calls and tests against the old signature and Phase 4
then rewrote all **12 call sites** (Phase 6 ×2, Phase 7 ×3, Phase 8 ×3, Phase 9 ×4). Every prose
finding would be written twice and its tests touched twice, with the mechanical 12-site sweep
landing last — where a missed site is likeliest and hardest to spot against three phases of other
changes. Going first also lands the widest change against an unmodified baseline, so the full suite
is a clean control.

**Accepted cost:** the largest-blast-radius change precedes the bug fixes, so stopping halfway
leaves the HIGH findings open.

### D8 — Fixtures: **rewrite, never delete**

**Locked:** the plan's "delete … or rewrite them" is narrowed to rewrite-only.

`defect/release-date-far-edge.md` is the positive control for the off-by-one `/code-review` caught.
D6 keeps a window (a heading opens it, claims are collected below), so **the off-by-one class is
still live** — deleting the fixture would re-open a bug a reviewer already found once, and the plan
permitted exactly that with an "or". Rewritten as: heading at line N, disagreeing claim at the
window's last line → still RED. `defect/version-box-stale-date.md` becomes an in-box disagreement,
since boxes are where the original REFCARD bug lived.

**Generalized into Friction Prevention:** never delete a positive control to make a redesign
easier; if its model is obsolete, rewrite it so the boundary it pinned stays pinned.

### D9 — Normalize the two claim sites

**Locked:** make `docs/NEWS.md` and `docs/REFCARD.md` agree exactly, and record the convention.

Evidence gathered while grilling the plan — craft has exactly two release-date claim sites for the
current version, and they already disagree:

| Site | Claim |
|---|---|
| `docs/NEWS.md:9` | `**Released:** 2026-08-08` (UTC date) |
| `docs/REFCARD.md:7` | `│  Version: 4.5.0 (released 2026-08-07)` (tag-local date) |

Both are reachable under D6, so check 1 fires on craft today and **only the one-day tolerance keeps
it GREEN**. With D2 making check 1 RED, the repo would sit permanently one day from a blocked
release, with no warning beforehand because one day always reads GREEN. Normalizing returns the
tolerance to headroom; it still exists for the real UTC-boundary cause D1 preserved.

**Rejected:** widening the tolerance to 2 days buys headroom by blunting the check; dropping it
entirely throws away the UTC handling D1 deliberately kept.

### D10 — Phase 6 must carry the workflow steps

**Locked:** Phase 6 refreshes the `.STATUS` worktree row, and the ORCHESTRATE file is deleted at
merge.

Both are required by craft's own `CLAUDE.md` and **neither is enforced** — `ORCHESTRATE-*.md` is
not gitignored, not in `exclusions.txt`, and no test guards it. The `.STATUS` row still describes
this branch as only the parent SPEC and its harness. Shipping a doc-staleness feature while leaving
a stale status row and a working artifact on `dev` would be its own small joke.

### D11 — RED promotion is **evidence-gated**

**Locked:** check 1 ships as `warning` in the severity phase; promotion to `error` happens in
Phase 6 only after it runs clean across every tracked `.md` and both known claim sites, transcript
quoted. If not clean, it stays `warning` and promotion becomes a follow-up.

Check 1 is being *redesigned* (D1, D6) and *promoted to release-blocking* (D2) in the same PR. The
only evidence it is sound would otherwise be tests written alongside it by the same author in the
same sitting. A false-positive class in a freshly-redesigned blocking check is discovered at the
worst possible moment — mid-release.

This does not reverse D2; it makes RED earned rather than assumed.

**Also recorded:** the plan's original 2-hour estimate was optimistic. Phase 1 alone is 12 call
sites plus JSON rendering plus both fix passes plus an end-to-end exclusion test. Revised to ~3
hours.

---

## Not branched (no genuine alternative)

- **F8** — unclosed `┌` leaks `version-box` mode into the rest of the file, losing the
  `structure-table` type restriction. Fix: close the box on the first line carrying no box
  character.
- **F9** — REFCARD says `tldr` matches "a line containing `TL;DR`"; the regex requires the line to
  *open* with it. The regex is deliberate (`falsepos/tldr-mentioned-not-claimed.md` depends on
  it). Fix the doc.

## Open questions

- **D1 leaves single-claim files unguarded.** If only `docs/NEWS.md` carries a release date for the
  current version, cross-file consistency says nothing. Worth revisiting once a second claim site
  is guaranteed — not blocking, since the status quo catches nothing anywhere.
- **Phase 9's severity is untouched.** D2 sets per-check severity in Phase 7 only; whether Phase 9
  should follow is unexamined.
- **The floor's 40% constant is still unjustified.** D3 puts a minimum under it but does not ask
  whether 40% was ever the right shape. Inherited from the pre-existing broad scan.

## Next step

`/craft:plan docs/specs/SPEC-prose-check-hardening-2026-08-15.md` → `plan-orchestrator` →
`ORCHESTRATE-*.md`, then implement on `feature/doc-staleness-prose-gaps` per D5.
