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

Release dates are checked against the **git tag's local date** for the current
version, with a one-day window. Not `.STATUS`'s `release_date:` — the two
legitimately disagree whenever a release publishes across the UTC boundary
(v4.5.0: tag 2026-08-07, GitHub release 2026-08-08T03:44Z), and a check that
flags a correct repo on its first run does not survive its first release.

Constraints held from the BRAINSTORM: no new script (D1), craft only (D2), no
semantic/NLP layer (D3), no external prose tool (D4).

## Severity

Findings are emitted at **`warning`**, matching every existing Phase 7 finding —
not `error`, which the SPEC's first draft specified.

This is a smaller difference than it reads. `main()` exits 1 for warnings and
errors alike, so both already fail `/craft:check --for release` and
`pre-release-check.sh`; the divergence is the RED/YELLOW label, not whether the
gate blocks. Given that these are the first checks in this repo to judge *prose*
rather than structured tokens, and that the first build of check 2 produced five
false positives before the floor was added, shipping at `warning` follows
ADR-003's gentle-ramp precedent: earn `error` after the checks run clean across a
few real releases.

## A failed authority makes a check vacuous, never universal

Every check here compares documentation against an authority — the git tag date, `plugin.json`'s
counts. When an authority is **missing**, the check skips: no tag yet is the normal state on a
feature branch. The rule this ADR adds is that when an authority is **present but unusable**, the
check skips too.

The first build did not do this. An unparseable tag date left an empty accept-window, and an empty
window matches nothing, so every release-date claim in the repo failed at once. One bad input
became a repo-wide false-positive storm — the loudest possible output from the least reliable
possible input.

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
