# BRAINSTORM: Command/Skill Consolidation + Stale-Surface Audit

**Date:** 2026-07-01 · **Depth:** default · **Focus:** arch/ops
**Follows:** [GRILL-craft-bloat-strategy-2026-07-01.md](GRILL-craft-bloat-strategy-2026-07-01.md)
(track A: delete/consolidate). This is the "which surfaces to cull" open question.

---

## Audit findings (measured on `dev`)

- **~56 of ~89 real commands are already thin shims** pointing to 14 skills. Consolidation is
  *largely done*, not pending.
- **Shim clusters:** git (14), site-management (13), adhd-workflow (6), plan-orchestrator (4),
  task-management / navigation / claude-md / dist-extras (3 each), + singles.
- **Shims are already scheduled for v3.0.0 retirement** (`git/status.md`: "At v3.0.0 this shim
  may be retired").
- **Fattest namespaces:** docs/ (21), code/ (17), site/ (16 — 13 are shims), git/ (15 — 14 shims),
  workflow/ (14).
- **A genuinely-stale smell:** `git/status.md` still describes itself as "teaching-specific" —
  but teaching moved out to the `scholar` plugin. Likely orphaned framing.

## Reframe (what the audit changes)

`★ Insight ─────────────────────────────────────`

- **This is a cleanup + deletion job, not a consolidation job.** The consolidation already
  happened. What's left is deciding whether the ~56 shims get *retired* (cut the surface) or
  *kept* (entry points), plus finding genuinely-stale orphans.
- **Retiring shims IS a measured-safe resting win** (unlike the form-conversion the bloat grill
  rejected): each shim's description is always-loaded; deleting 56 removes ~56 descriptions
  (~800 tok) and hits NO skill-activation trap (the skills stay). But it's a *modest* lever —
  the bigger resting cost is skill descriptions (~3,858 tok), which we can't safely trim.
- **So temper expectations:** consolidation/retirement buys a cleaner surface and a modest
  resting cut, not a dramatic one. The dramatic answer still waits on `/usage` (do bodies preload?).

`─────────────────────────────────────────────────`

---

## Quick Wins (< 30 min)

1. **Orphan sweep for genuinely-stale surface** — grep for commands/skills whose framing points
   at moved/removed capability (start with the "teaching-specific" `git/status.md`; teaching left
   for `scholar`). These are delete-now candidates independent of v3.0.0.
2. **Reference-safety check before any deletion** — for each retirement candidate, grep docs/
   tutorials/tests/other-commands for the slash name. A shim with live references isn't safe to
   delete yet (the orchestrate-family audit already found docs treating deprecated commands as live).

## Medium Effort (1–2 hrs)

- [ ] **v3.0.0 shim-retirement plan** — the ~56 shims are the biggest single surface cut
  (~117 → ~60 commands). Retire in cluster batches (git, site, workflow…), skills stay. Gate each
  batch on the reference-safety check. This is track-A of the bloat grill, made concrete.
- [ ] **Skill orphan audit** — 43 skills, only 14 are shim-targets. The other ~29 are either
  legitimate auto-fire-only skills or orphans. Cross-check each skill's description against actual
  invocation/reference; flag any with no shim AND no references AND no plausible auto-fire trigger.

## Long-term (future sessions)

- [ ] **Namespace collapse** — docs/ (21) and code/ (17) are the fattest non-shim namespaces.
  Audit for genuinely-overlapping commands to merge (the orchestrate-family pattern, applied to
  docs/code).
- [ ] **Description-trim pass (commands/agents only)** — per the bloat grill, terse command/agent
  descriptions are safe; measure with `token-probe.py` before/after. Skills excluded (activation trap).

---

## Risks / edge cases

- **Shim retirement removes user-facing slash commands.** `/craft:git:status` disappears even
  though the skill auto-fires — muscle-memory / discoverability cost. Mitigate: announce in v3.0.0
  changelog; keep the highest-traffic shims longer.
- **Count cascade (in reverse).** Deleting ~56 commands triggers the ~30-file count cascade per the
  usual tooling — batch it, run `validate-counts.sh` + `bump-version.sh` sweeps.
- **Reference rot.** Docs/tutorials referencing a retired command break — the reference-safety
  check (Quick Win #2) is mandatory, not optional.
- **Modest payoff.** Be honest: ~800 resting tokens from shim retirement. Don't oversell it as the
  fix for "craft is bloated" — it's cleanup, and the real number waits on `/usage`.

## Test Plan (default-on)

- **e2e:** after a retirement batch, `validate-counts.sh` green; no broken links to retired names
  (`test_craft_plugin.py -k broken_links`).
- **dogfood:** each retired command's capability still reachable via its skill (skill exists +
  auto-fire description intact).

## Documentation (default-on)

- v3.0.0 CHANGELOG: list retired commands + their skill replacements.
- Update REFCARD / skills-agents.md / hub after each batch (count cascade).

## Audit Results (executed 2026-07-01, inline)

Ran the orphan sweep + reference-safety check (`scratchpad/consolidation_audit.py`). Three findings
that **temper and redirect** the plan:

### 1. NO shim is trivially safe to delete — all 56 have live references

Every deprecated shim is woven into the hub catalog, `/do` routing, `smart-help`, and cross-links
(`git:worktree` 80 refs, `git:status` 37, `site:build` 36, `orchestrate:plan` 26; `check` 432 is
inflated — common word). **Retirement is a coordinated cleanup, not a delete.** Each shim needs its
references rewritten to point at the skill first. This is real work per shim — the ~800-token
resting payoff does NOT justify a big-bang retirement.

### 2. The bigger stale surface: teaching framing scattered across craft

Teaching moved to the `scholar` plugin (teaching-only as of v3.0.0), yet craft still carries:

- **Teaching-specific utils** (genuinely stale candidates): `utils/semester_progress.py`,
  `utils/teach_config.py`, `utils/teaching_validation.py`, `utils/readme-teach-config.md`,
  `utils/readme-semester-progress.md`. Check whether `scholar` now owns these → migrate or delete.
- **Stale teaching *framing* on general commands** (cleanup, not deletion): `git/status.md`
  ("teaching-specific context"), the whole `site/` namespace ("Publish teaching site", "teaching
  site" — but the capability is general Quarto/pkgdown/MkDocs infra). De-teaching-ify the wording;
  keep the capability.

This is a **larger and more consequential lever than shim retirement** — a possible cross-plugin
migration (teaching utils → scholar) plus a de-teaching-ify wording pass.

### 3. Two possibly-orphaned skills (refs ≤1, no shim target)

`homebrew-multi-formula`, `architecture-decision-records` — verify they're used/needed or retire.

**Net redirect:** shim retirement is *more expensive and less rewarding* than it looked (all
referenced, ~800 tok). The higher-value cleanup is the **teaching-residue audit** (utils migration
to scholar + de-teaching-ify framing) and the **2 orphan skills**.

## Recommended Next Step

→ **DONE (audit executed above).** The results redirect priority away from shim retirement toward:

1. **Teaching-residue audit** (highest value) — verify which teaching utils `scholar` now owns;
   migrate/delete the stale ones; de-teaching-ify framing on `git/status.md` + `site/*`.
2. **Verify the 2 orphan skills** (`homebrew-multi-formula`, `architecture-decision-records`).
3. **Shim retirement → defer** — all 56 are referenced; it's coordinated cleanup for ~800 tok,
   not worth a big push before `/usage` confirms the resting-cost picture.
