# BRAINSTORM: Safety Hardening — hard_deny + insights audit

**Date:** 2026-05-10
**Mode:** feat
**Depth:** default (~3 min)
**Trigger:** `/craft:code:release-watch` surfaced 2 high-leverage improvements from Claude Code v2.1.136

---

## Source

`/craft:code:release-watch` v2 found 2 high-value craft improvements from Claude Code v2.1.136:

1. **`settings.autoMode.hard_deny`** — NEW capability for unconditional auto-deny rules (block regardless of session allow exceptions)
2. **`/insights` crash fix** — Defensive port for the same crash class in `/craft:workflow:insights`

This brainstorm explores both as a paired safety release.

---

## Quick Wins (< 30 min each)

- **Verify `hard_deny` schema** in Claude Code source/docs before any design work. Could change the design space.
- **Insights audit pass** — read `commands/workflow/insights.md` + parsing code; grep for `json.load()` + `facet[...]` without `.get()`; wrap in try/except.
- **Catalog catastrophic patterns** worth hard_denying: `git push --force` on main, `rm -rf .git`, `gh repo delete`. Distinguish from "almost-catastrophic" (force-push on feature branches, `rm -rf tmp/`) which stay in branch-guard's smart mode.

## Medium Effort (1-2 hours)

- **Implement #2** (insights defensive parsing): 15 min audit + targeted try/except + 1 regression test that passes a malformed facet → no crash, skip+log.
- **Implement #1** (hard_deny layer):
  - Design 3-5 catastrophic patterns
  - `/craft:git:protect` integration: detect missing rules + offer to install
  - Update REFCARD-BRANCH-GUARD with the new layer
  - Test: real `git push --force origin main` is hard-denied even with `.claude/allow-once` present

## Long-term (Future sessions)

- **3-layer protection model** documented in `architecture.md` (currently 2 layers: branch-guard + GitHub-side; add hard_deny as the 3rd top layer).
- **`/craft:guard:audit` extension** to check whether installed hard_deny rules align with detected user friction.
- **Cross-plugin pattern**: if hard_deny works well, the pattern can be adopted by other Data-Wise plugins for their destructive operations.

## Recommended Path

**Sequence:** #2 first (defensive, low-risk, independent), then #1 (capability addition, schema-dependent). Ship together as v2.33.0 increment OR as v2.32.2 patch depending on scope.

**Total scope:** ~3h (15min audit + 30min #2 + 1.5h #1 + ~45min docs/tests).

## Open Questions

1. Does `hard_deny` apply via Claude Code `settings.json` only, or via a hook hook contract too? Schema spec needed.
2. Should `hard_deny` rules be auto-installed by `/craft:git:protect`, or opt-in via a separate command like `/craft:git:harden`?
3. Per-project `settings.local.json` vs global `~/.claude/settings.json`?
4. Will increment land as v2.33.0 work or v2.32.2 patch?

## Key Insights

1. **Sequencing matters** — #2 first because it's purely defensive (try/except hardening) with no upstream schema dependency. #1 needs `hard_deny` schema verification — if Claude Code's docs don't fully spec it, scope might shift.
2. **"Almost-catastrophic vs catastrophic"** distinction is the design crux for #1. `git push --force` is catastrophic on main, normal on feature branches. `rm -rf` is catastrophic on `.git`, normal on `target/`. hard_deny rules MUST be narrow — branch-guard's smart-mode handles contextual cases; hard_deny handles absolutes only. Otherwise users hit them, can't bypass, disable the whole layer.
3. **Ecosystem leadership opportunity** — if craft establishes "hard_deny + branch-guard + GitHub-side" as the canonical 3-layer protection model, other Data-Wise plugins (and external Claude Code plugins) can follow.

---

**Next step:** spec captured at `docs/specs/SPEC-safety-hardening-2026-05-10.md`.
