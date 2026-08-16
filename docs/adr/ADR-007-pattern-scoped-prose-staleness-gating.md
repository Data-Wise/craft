# ADR-007: Documentation prose staleness is gated by pattern-scoped line shapes

**Status:** Accepted
**Date:** 2026-08-15
**Implements:** [`SPEC-doc-staleness-prose-gaps-2026-08-07.md`](../specs/SPEC-doc-staleness-prose-gaps-2026-08-07.md)
**Related:** ADR-003 (release drift is advisory, not a hard gate) — the severity
posture below follows its gentle-ramp precedent.

## Context

`scripts/docs-staleness-check.sh` Phase 7 anchors on structured patterns: badge
strings (`version-X.Y.Z`), declared count lines (`N commands`). That is enough to
keep *numbers* honest and nothing else. Four real staleness bugs shipped and sat
live while Phase 7 reported GREEN over every one of them:

| Bug | Why Phase 7 missed it |
|---|---|
| `docs/REFCARD.md` — version box with the right number, wrong release date | dates were never checked |
| `docs/skills-agents.md` — TL;DR claiming "8 specialized agents" two lines above its own correct "2" | the intervening word broke the `N agents` pattern |
| `CLAUDE.md` — Project Structure row reading "8 agent definitions" for five minors | the scan matches the plural noun only |
| `README.md` — a v2.36.0 highlight block still headlining at v4.5.0 | highlight prose was never checked |

The obvious wide fix — search all prose for `\d+ agents?` — was tried in review
and rejected: a grep over `docs/**/*.md` returned 90+ hits, the great majority
legitimate. Orchestration mode-limit prose ("2 agents max", "4 agents"), a
tutorial built around an intentionally fictional plugin, and a troubleshooting
page that prints a wrong count *on purpose* to teach the bug all look identical
to a stale total from a regex's point of view.

## Decision

Extend Phase 7 in place with **line-shape-scoped** regexes. A count in free prose
is not checked; a count inside one of four enumerated structured shapes is:

| Shape | What it is |
|---|---|
| `version-box` | lines inside a box-drawing block (`┌` … `└`) |
| `tldr` | a TL;DR summary line |
| `count-summary` | the bolded badge line (`**48 commands** \| **41 skills**`) |
| `structure-table` | a table row whose first cell names a counted directory |

Inside those shapes only, the singular noun form is checked alongside the plural,
and the `structure-table` shape compares against the type its own first cell
names. The existing 40%-of-expected floor applies to shaped lines too — structured
shapes still carry legitimate non-totals (category subtotals in a reference box,
a bolded subset count, a narrative count about another plugin).

Release dates for the current version are checked **against each other**, with a
one-day agreement window — not against the git tag's local date, as originally
built. The tag doesn't exist at either point this check actually runs (the
release pipeline writes NEWS/REFCARD dates *before* the tag is created; CI's
checkout has no `fetch-tags`), so a tag-based check only ever fired on a
developer machine that had already pulled the tag for a *previous* release —
never a real gate. Not `.STATUS`'s `release_date:` either — claims legitimately
disagree by a day whenever a release publishes across the UTC boundary (v4.5.0:
NEWS.md 2026-08-08, REFCARD.md 2026-08-07), and a check that flags a correct repo
on its first run does not survive its first release. See the prose-check
hardening's `GRILL-prose-check-hardening-2026-08-15.md` D1 for the full account.

Constraints held from the BRAINSTORM: no new script (D1), craft only (D2), no
semantic/NLP layer (D3), no external prose tool (D4).

## Severity

Split per check, not uniform across the phase: check 1 (release-date consistency)
emits `error`; check 2 (count prose) emits `warning`.

An earlier version of this section claimed the choice barely mattered — that
`main()` exits 1 for warnings and errors alike, so both already fail
`/craft:check --for release` and `pre-release-check.sh`, and the only difference
was the RED/YELLOW label. **That claim was checked during the prose-check
hardening review (2026-08-15) and found false**, not softened:

- `pre-release-check.sh:280` runs the whole script as `… || true`, discarding the
  exit code — "Check 9: Docs staleness (warn-only, does not block release)".
- `.github/workflows/docs-quality.yml` sets `continue-on-error: true`.
- `skills/release/SKILL.md:143` is explicit: "RED findings block; YELLOW findings
  warn but allow proceed."

No consumer reads the process exit status. **The label is the only gate.** The
severity choice a finding gets *is* the block decision — not a cosmetic split of
an already-blocking outcome.

Given that, severity now follows demonstrated precision per check rather than a
single phase-wide default:

- **Check 1 is near-binary after the cross-file redesign** (release-date claims
  either agree with each other or they do not) — it can afford to block.
- **Check 2 matches prose patterns**, and produced three false-positive defects
  in the PR that introduced it alone (a hyphenated-compound false match, a
  zero-floor for the smallest count type, and five sub-threshold counts caught
  pre-merge) — it has not earned that yet. `warning` here still follows
  ADR-003's gentle-ramp precedent: earn `error` after the check runs clean
  across a few real releases.

## A failed authority makes a check vacuous, never universal

Every check here compares documentation against an authority — `plugin.json`'s counts for check 2,
and (after the check-1 redesign below) the other release-date claims in the repo for check 1, no
longer a git tag. When an authority is **missing**, the check skips: fewer than two release-date
claims to compare is the normal state on a feature branch, or in a repo where only one doc names a
date at all. The rule this ADR adds is that when an authority is **present but unusable**, the
check skips too.

The first build did not do this, back when the authority was a git tag. An unparseable tag date
left an empty accept-window, and an empty window matches nothing, so every release-date claim in
the repo failed at once. One bad input became a repo-wide false-positive storm — the loudest
possible output from the least reliable possible input. The guard survives the redesign: an
unparseable authority (now impossible in practice, since it can only come from a claim string
already validated by the collection regex) still produces an empty window, and an empty window
still rejects a claim rather than accepting it.

Stated generally, for any check added to this script later: **a check may only report a finding it
can positively establish.** Absence of a usable comparison is not evidence of drift. The failure
modes are not symmetric — a skipped check costs one missed bug, a check that fires on every
document costs the gate its credibility, and a gate nobody trusts gets bypassed.

## Fixes must be applied, not announced

A finding carries a `fix_detail`. Both prose checks emit `uncertain`, routing to pass 2's
interactive review rather than pass 1's auto-apply: the surrounding prose is hand-authored, so a
human should see the line before the number changes under it. The `fix_detail` is nonetheless a
real `s/…/…/` substitution rather than a human-readable note, so confirming one actually edits the
file — it swaps the digits only, leaving `agent definitions` intact.

This is a recurrence guard, not a preference. Pass 1 shipped a version of this bug once already
(BSD `sed -i` exits 0 when nothing matched, so the script reported "Fixed: N items" having
modified nothing on every macOS run) and was fixed for it. Pass 2 kept the same bug in simpler
form — it printed `-> Fixed` and incremented the counter without calling anything at all. Patching
the second site would have left a third to find later, so the applier is now a single shared
function, `apply_line_fix`, which returns true only when the file actually changed and refuses to
execute a `fix_detail` that is not a substitution (Phase 8's `doc-coverage:surface:cmd` markers).

Same family as the rule above: **do not report a result you have not established.** The vacuous
rule keeps the script from claiming drift it cannot demonstrate; this one keeps it from claiming a
repair it did not perform.

## Consequences

**Accepted:**

- Coverage is exactly as good as the four enumerated shapes. A genuinely new
  prose shape requires a code change, not a config change.
- `scripts/config/exclusions.txt` keeps growing. Raised in review, accepted:
  it is already craft's mechanism for this class of exception, and shape-scoping
  shrinks how fast the list has to grow.
- Two env overrides (`CRAFT_EXPECTED_*`, `CRAFT_RELEASE_DATE`) exist for test
  hermeticity. Unset on every production path.

**Rejected alternatives:**

- **Vale / `drift` / an LLM-in-CI pass** — dependency weight, and
  non-determinism in a release gate is worse than a missed prose bug.
- **A whole-file git-log-touch staleness proxy** — rejected as *falsified*, not
  merely unattractive. `bump-version.sh` rewrites `docs/REFCARD.md`'s version
  line on every release, so the proxy would report "recently touched, not stale"
  on the very file whose staleness motivated this work. A per-line/per-span
  version could work; it is real complexity for an advisory signal and is not
  being built preemptively.

## Revisit trigger

A prose staleness bug that lands **despite** these checks and whose shape cannot
be expressed as a line-shape regex. That, and only that, reopens the D3/D4
rejection of semantic tooling. A bug that merely needs a fifth shape is a shape,
not a reason to change approach.
