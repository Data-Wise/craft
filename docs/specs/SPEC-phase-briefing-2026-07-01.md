# SPEC: Phase-End Briefing (skill)

- **Status:** Draft
- **Created:** 2026-07-01
- **Owner:** dt
- **Depth/Focus:** default · feat
- **Source:** `/craft:workflow:brainstorm --refine`

## 1. Summary

A **Phase-End Briefing** ritual for multi-phase / background work: at each phase
boundary, emit an ADHD-friendly briefing (Done / Next / Watch), proactively offer
to re-plan when a Watch item bears on Next, and run a best-practice + token-cost +
new-skill lens over the approach. **Tiered by default** — terse unless there's a
decision — so the ritual never costs more than it saves.

## 2. Why a skill (not just a habit)

Composition of existing primitives, made repeatable and testable:

| Reuses | Adds |
|---|---|
| `/craft:workflow:brief` (Next/Watch/Connects engine) | **phase-boundary trigger** + tiering |
| `adhd-friendly-message-format` memory | the **causal amend-offer** (Watch⇄Next → update SPEC + todos) |
| token-efficiency work (`command-skill-token-efficiency`) | the **token/best-practice/new-skill lens** |

## 3. Behavior

At the end of each phase of a tracked multi-phase effort (orchestrate / dynamic
workflow / background pipeline / TodoWrite-tracked plan):

**Tier 1 — default (terse, ~3 lines):**

```
✅ <phase> done — <one-line evidence>
➡️ Next: <immediate action>
⚠️ Watch: <top risk for Next>
```

**Tier 2 — expand ONLY when a decision/link exists:**

- 🔗 **Amend-offer** — if Watch causally affects Next, offer (via `AskUserQuestion`,
  Recommended-first) to amend the SPEC/plan + `TodoWrite` tasks before proceeding.
- 💡 **Lens** — creatively surface a best practice; if the current approach is
  token-heavy, flag it + offer a token-saving alternative; if a recurring pattern
  emerges, propose extracting a **new skill**.

**Escalation rule (token-aware):** Tier 1 always; Tier 2 only on a real
link/decision. Never emit Tier 2 boilerplate "just because."

## 4. Realization (recommended)

- Primary: **new skill** `skills/workflow/phase-briefing/SKILL.md` (fat-skill,
  ADR-002) encoding the tiers + escalation rule + amend-offer + lens.
- Wire-in: a `--phase` mode on `/craft:workflow:brief` (thin shim → the skill),
  and an emit-point in `orchestrator-v2` / `orchestrate:workflow` phase loops.
- Rejected: a brand-new top-level command (adds a count-cascade for no gain when
  `brief --phase` already fits).

## 5. Test plan (tier-inferred: new skill + flag)

| Tier | In scope | What |
|---|---|---|
| e2e | ✅ | `brief --phase` emits Tier-1 block; Tier-2 only when a link flag/param is set |
| dogfood | ✅ | skill self-usage from an orchestrate phase loop; count-cascade for the new skill |
| unit | N/A | prose skill, no new parser |

## 6. Open questions (→ grill)

1. Where exactly does the emit-point live in `orchestrator-v2` / `orchestrate:workflow`?
2. Does the amend-offer write to `TodoWrite`, the SPEC file, or both?
3. Skill count cascade (44→45) — bump-version + doc sweep.

## 7. Applied NOW (ahead of the skill)

The protocol is in force for the current dist-surface pipeline (A→B→C) this session,
tiered, regardless of when the skill lands.
