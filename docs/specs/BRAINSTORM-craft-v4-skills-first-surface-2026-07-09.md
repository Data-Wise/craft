# BRAINSTORM — craft v4 Skills-First Surface (69 → ~22 commands)

> **Adversarial-creative review of the post-split "69 commands are too many" problem.**
> **Date:** 2026-07-09 · Rider on the folio v4.0.0 breaking release (one major, one migration).
> **Grounding:** full 69-command classification (Explore agent, repo-verified) + Anthropic
> Agent Skills guidance. Composes with `BRAINSTORM-folio-border-filter-2026-07-09.md`.

## The Central Finding: "69" is an illusion

The classification breaks the 69 into:

| Type | N | Reality |
|---|---|---|
| **Already-deprecated shims** (`deprecated: true` + `replaced-by:` a skill) | **27** | The v3.0.0 skill-migration debt — scheduled to die, never executed |
| Non-deprecated thin shims (grill, code:release) | 2 | Slash entries over skills |
| Routers (do, plan, orch, smart-help, orch:drive, orch:workflow) | 6 | Dispatch, not behavior |
| References (hub catalog, discovery-usage `internal:true`) | 2 | Docs wearing command clothes |
| **Genuinely rich** | **32** | The real surface |

**craft's true post-split surface is 32 rich commands.** The other 37 are migration debt,
plumbing, and catalog. The "too many commands" problem is ~60% already-solved-on-paper.

## Why this does NOT re-run the refuted native-first thesis

The refutation (memory `native-first-thinning-refuted-for-craft-dev-ops`) killed routing to
NATIVE/THIRD-PARTY replacements — weaker tools, cross-plugin wall. This proposal converts
commands into **craft's OWN skills** — the same plugin, behavior preserved, the exact ADR-002
migration craft has been running since v2.34. The router wall is irrelevant: skills auto-fire
on NL match and (current Claude Code) are **directly slash-invocable** when top-level
registered. Anthropic's guidance points the same way: skills = on-demand, progressive
disclosure, one concern each; commands = explicit deterministic entry points, kept few.

## The Funnel (v4.0.0, all in the same breaking release as the folio split)

```
69 stays-set
 ├─ −27  KILL the deprecated shims (complete the v3 migration at v4)
 │        ⚠ ADR-002 gate per shim: PR #279 caught 3/24 "shims" that were rich-body
 │        (git:docs:refcard 363L, check:gen-validator 447L, workflow:insights 194L) —
 │        salvage bodies → skills/*/references/ BEFORE deletion; expect ~5 salvage jobs
 │        (+ claude-md trio: 320/362/635L vs one skill — verify carriage)
 ├─ −2   KILL teaching residue: utils:readme-teach-config, utils:readme-semester-progress
 │        (scholar leftovers — same class as site:progress)
 ├─ −1   DEMOTE discovery-usage (internal:true) → docs page
 ├─ −7   ci: 8 → 1   /craft:ci <detect|fix|generate|local|status|triage|validate|watch>
 │        (all 8 back onto the single skills/ci — savant's proven subcommand pattern,
 │         zero count-cascade for subcommands)
 ├─ −3   arch: 4 → 1   /craft:arch <analyze|diagram|plan|review>  (single architecture skill)
 ├─ −4   code audits: 5 → 1   /craft:code:audit <deps|deps-quick|docs|commands|skills>
 │        (deps-audit, deps-check, docs-check, command-audit, skill-standards)
 ├─ −2   orch: orch + orch:drive + orch:workflow → /craft:orch [--drive|--workflow]
 ├─ −1   plan: root plan absorbs plan:feature (sprint/roadmap already in the −27)
 └─ = ~22 commands  +  ~40 skills carrying ALL behavior
```

**craft v4 ≈ 22 commands** — do · hub · check · test · brief · next · done · refine ·
brainstorm · grill · plan · orch · ci · arch · smart-help · insights-family ·
code:{lint, debug, refactor, test-gen, audit, release(-watch), fewer-prompts} ·
dist:{homebrew, surfaces} · git (0 — all 9 were deprecated shims; skill + hub carry it) ·
docs:{update, changelog}. *(Exact roster is a spec deliverable; ±3.)*

## Adversarial self-attack (what could kill this)

1. **The shim-kill is NOT free** — PR #279's base rate: ~12% of "shims" are secretly
   rich-body. Gate: per-shim diff of body vs skill+references, salvage first, then delete;
   `test_skill_referenced_commands_exist` + bash suites as the tripwire. **Survives — this is
   process cost, not a blocker.**
2. **Slash-entry loss for heavy-use commands** (next/done/refine were root-promoted FOR heavy
   use). Mitigation: skills are slash-invocable in current Claude Code — BUT memory
   `prompt-refiner-not-skill-tool-invokable` proves NESTED skills aren't. Gate: per-skill
   invocability test before its shim dies; non-invocable skills keep a 5-line shim or get
   promoted to top-level. **Survives with a verification gate.**
3. **Subcommand routers = fewer memorable names?** savant runs 35 commands with this exact
   pattern (`repo voice-init`), depth-1 namespace cap enforced at build time. hub + smart-help
   remain the discovery surface. **Survives — proven in-family.**
4. **Deterministic pipelines need commands.** release, check, do stay commands — Anthropic's
   own boundary (explicit user-triggered workflow = command). **Agreed — they're in the 22.**
5. **Another ~30-file count cascade + test churn.** Cost is real — but it lands INSIDE the
   already-breaking v4.0.0 with the folio split's cascade run. Two breaking changes, one
   release, one MIGRATION-v4.md. Doing it later = a second major. **Survives — timing is the
   whole argument.**
6. **Does this contradict "craft's commands beat alternatives"?** No — behavior is preserved
   in skills; only the ENTRY-POINT count shrinks. The 4-axis gate compared craft vs
   *replacements*; here the replacement is craft itself.

## Not Doing

- Converting do/hub/check/release to skills — deterministic entry points stay commands.
- Touching dist:homebrew's 1691 lines — biggest rich command, release-critical, works.
- Any cross-plugin routing (still walled; folio unaffected by this rider).
- docs:update decomposition (1046L) — release-plumbing, defer to its own cycle.

## Sequencing (rider, not blocker)

folio split Phases 1–3 land first (craft at 69 momentarily), then this consolidation as
**Phase 3.5 of the same v4.0.0 train** — same feature branch family, same MIGRATION-v4.md,
same count-cascade sweep, same CI-floor edit (the review's B2 fix must target the FINAL
number ~22, not 67). Alternative (do it first) re-orders the folio caller-audit ground truth —
rejected: the border filter already keyed on today's paths.

## Recommended Next Step

→ Accept as **v4 target shape (~22 cmds / ~40 skills)**; fold the CI-floor + count numbers
into the pending review amendment so v4.0.0 is planned against the REAL final surface; grill
the exact 22-roster + per-shim salvage list as its own short spec before Phase 3.5 executes.
