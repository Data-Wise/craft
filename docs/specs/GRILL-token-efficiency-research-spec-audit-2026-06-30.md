# GRILL: SPEC-token-efficiency-research-2026-06-30.md audit — 2026-06-30

**Target:** `docs/specs/SPEC-token-efficiency-research-2026-06-30.md` (path argument — the full
research report, all 9 sections, including the §9 addendum just merged in from the earlier
usage-checkpoint-tooling grill session this same day).

**Note on interactivity:** the first `AskUserQuestion` in this session also went unanswered
(same pattern as the earlier grill pass). Resolved via each question's own **Recommended**
option and continued autonomously, per this session's established convention.

---

## Decision Ledger

### 1. Cross-spec factual disagreement: 18 vs. ~20 of 56 flagged commands

**Resolved: fixed.** `SPEC-craft-audit-and-next-steps-2026-06-30.md:74` said "~20 of 56"; this
SPEC's §6 said "18 of 56." Live re-run of `python3 scripts/audit-deprecated-commands.py
--threshold 2.0` returned exactly 18 flagged commands — confirming this SPEC was accurate and the
other one was stale. Corrected `SPEC-craft-audit-and-next-steps-2026-06-30.md:74` to "18 of 56,"
citing the live verification and cross-referencing this SPEC.

**Why this matters generically:** the same fact stated in two sibling specs had silently diverged
— exactly the kind of drift this branch's own §4 methodology (verify against ground truth, not a
sampled/assumed check) exists to catch. Left unfixed, either number could get cited downstream and
propagate the wrong one.

### 2. §8's third open question was stale relative to §9

**Resolved: fixed.** §8 originally read as if the `/usage` validation gap were fully untouched;
§9 (added the same day) actually fixed the tracking *mechanism*, though the checkpoint itself
(~2026-07-14) is still pending. Appended an inline "Update (§9)" note to the bullet rather than
rewriting it, preserving the original open-question framing while making clear what changed.

### 3. GRILL ledger cross-link isn't programmatically discoverable

**Found, not fixed — flagged as a known limitation.** `spec_crosslink('usage-checkpoint-tooling',
'docs/specs')` returns `None` even though `docs/specs/GRILL-usage-checkpoint-tooling-2026-06-30.md`
now correctly documents in prose that its target moved to
`SPEC-token-efficiency-research-2026-06-30.md` §9. The automated lookup keys on the GRILL file's
own topic slug matching a `SPEC-<same-slug>-*.md` filename pattern — that pattern doesn't hold
once a spec's content gets merged into a *different*, pre-existing spec (as directed by "amend the
existing spec, don't create a new doc," the same principle decision 1 in that grill session
applied). Not fixed here because there's no clear generalizable rule to encode — a one-off manual
cross-reference is the correct fix for a one-off manual merge, and no other current tooling in
this session's line of sight actually calls `spec_crosslink()` in an automated path (only manual,
interactive Python calls during grill sessions themselves). Worth revisiting only if this pattern
(merging a fresh grill's target spec into a different pre-existing spec) recurs often enough to be
worth a codified convention.

### 4. Script threshold default matches all doc references

**Checked, no drift found.** `scripts/audit-deprecated-commands.py:102` defaults `--threshold` to
`2.0`, matching every doc reference (§6 here, `SPEC-craft-audit-and-next-steps-2026-06-30.md`,
`skills/code/command-skill-token-efficiency/SKILL.md`). No action needed.

### 5. Referenced artifacts (issue #233, commit `81750e05`, the built skill file) all verified real

**Checked, no drift found.** `gh issue view 233` confirms OPEN and title matches §6's description;
`git log --oneline -1 81750e05` resolves to the exact commit message §4 attributes the fix to;
`skills/code/command-skill-token-efficiency/SKILL.md` exists on disk, matching §7's "Built:"
claim. No fabricated or stale references found.

---

## Open Questions

None outstanding this pass. Decision 3 (crosslink discoverability) is logged as a known,
accepted limitation rather than a task — revisit only if the underlying pattern (grill target
merging into a different pre-existing spec) recurs.
