# ADR-003: Release-Time Governance Drift Is Advisory, Not a Hard Gate

**Status:** Accepted
**Date:** 2026-06-25
**Context source:** Governance retro [#205](https://github.com/Data-Wise/craft/issues/205), item 3 (+ meta P7)

---

## Context

The skill-ecosystem governance roadmap is complete (v2.43–v2.47: Phase 0–2, soak-then-flip,
cross-repo wrapper, R03/R04 automation). Issue #184 added a release-time governance check to
`scripts/pre-release-check.sh`. It landed as an **advisory**: it prints the count of RED
findings but deliberately never increments `$ERRORS` and never exits non-zero, so it cannot
fail a release.

```
scripts/pre-release-check.sh — governance block prints `⚠ governance: N red finding(s) —
ADVISORY, not blocking this release`; it does not touch $ERRORS. Pinned by
tests/test_governance_dogfood.py::TestReleaseGuard184.
```

The original Phase-2 proposal had called for a **hard guard** at release. #205 item 3 flags
that the downgrade to advisory is a real decision — the incident it addresses (savant pinned
three releases behind; scholar serving zero skills) was an *enforcement* gap, and "a human
ignores a warning as easily as its absence." The downgrade should therefore be a **recorded
decision**, not a silent default.

This ADR also adds R09-status-not-drift (#205 item 1, `.STATUS` drift), whose release-time
firing follows the **same** advisory posture — making the question "advisory or hard?" the one
load-bearing governance decision left to record.

## Decision

**Release-time governance checks stay advisory (warn-only). No hard gate.**

This applies to both the #184 governance annotation and the R09 `.STATUS` drift call in
`pre-release-check.sh`. Both surface findings in release output; neither blocks the release.

Rationale:

1. **Single reader.** craft is maintained by one person who reads their own release output. A
   hard gate buys little when the same human both produces and consumes the warning — the
   value of a gate is stopping work *others* would otherwise miss.
2. **Gentle-ramp is the founding posture.** The whole system promotes `warn → error` only
   after a clean soak (soak-then-flip). A hard *release* gate would contradict that ramp by
   blocking on rules that have not earned `error` severity.
3. **False positives are costly at release.** A blocking check that misfires red-lists a
   release for a tooling fault (cf. the R09 regex false-positive caught during its own
   implementation). Advisory output degrades gracefully; a gate does not.
4. **Reversible if it bites.** If a missed-drift incident recurs *despite* the advisory being
   visible, that is the evidence to revisit — promote the specific rule to `error` at its gate,
   or add a targeted hard check. The decision is cheap to change; the prose here records why it
   starts advisory.

## Alternatives Considered

1. **Hard gate at release (the original proposal).** Rejected for a solo maintainer: see
   rationale 1–3. Reconsider if the ecosystem gains more independent consumers or an incident
   recurs.
2. **Leave it advisory but undocumented.** Rejected — that is the exact "silent default" #205
   objects to. The downgrade from the proposal must be deliberate and traceable.
3. **Per-rule choice (some block, some advise).** Deferred. The existing soak-then-flip already
   provides per-rule severity; a release-specific override layer is unneeded machinery now (see
   the freeze below).

## Consequences

- **Positive:** release pipeline never blocks on governance noise; the posture matches
  soak-then-flip; the decision is now traceable to this ADR instead of being implicit in a
  shell script.
- **Cost:** a real drift can ship if the maintainer ignores the advisory line. Accepted
  knowingly for a single-reader project; the trigger to revisit is a recurrence.
- **Freeze marker (#205 meta / P7).** The founding proposal's P7 — *"lightweight by default;
  governance must not become its own maintenance project"* — applies now that the roadmap is
  complete. **R09 is the last governance addition before a real-use feature freeze.** Further
  phases wait on evidence from actual use, not speculation.

## Verification

- `TestReleaseGuard184` pins the #184 block as non-blocking (no `$ERRORS`, no `exit 1`).
- `test_status_drift_fires_against_repo_root_advisory` pins the R09 release call as advisory
  (`|| true`, inside the same non-blocking block).
- No `pre-release-check.sh` path increments `$ERRORS` from a governance finding.
