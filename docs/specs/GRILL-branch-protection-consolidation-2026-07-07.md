# GRILL — Branch-Protection Command Consolidation

| | |
|---|---|
| **Date** | 2026-07-07 |
| **Target** | `docs/specs/SPEC-branch-protection-consolidation-2026-07-07.md` |
| **Cross-linked SPEC** | SPEC-branch-protection-consolidation-2026-07-07.md |
| **Branches resolved** | 6 (below the ~5-branch unbounded target; grill converged before a milestone checkpoint was needed) |

Interrogates the SPEC's open decisions (§2 registry-ownership scope, §4.6's 5 flagged items,
§4.7's shim-cleanup staging, §5's delivery-scope granularity) one branch at a time,
Recommended-first with a per-option consequence. All 6 branches resolved with the Recommended
answer.

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | §2 registry-ownership: enforce "sole mutator of guards.json" with a test, or leave descriptive? | Descriptive only, not enforced — matches current practice (guard.md already only uses jq); revisit only if a second writer appears. |
| 2 | §4.6 item 1: build the baseline.json extraction inside this SPEC, or treat as a blocking prerequisite? | Build it as part of this SPEC — small mechanical extraction from branch-guard.sh case statement + protect-baseline.md payload, both already exist. |
| 3 | §4.6 item 2: build --classify/GUARD_DRY_RUN ground-truth mode now, or ship LLM-reasoned explain and revisit on drift? | Build it now — cheap (reuses block()/ask()), and makes the Test Plan dogfood tier able to actually fail instead of narrate. |
| 4 | §4.6 item 5: verify now whether the always-confirm revert left stray code in branch-guard.sh, or fold into implementation review? | Verified now via git diff 7195d5c9..HEAD -- scripts/branch-guard.sh: 38 lines total, all in the intentional GIT_CTX_DIR block. Smart-mode tier logic (_low_note/_confirm call sites) is byte-identical to pre-session baseline. CONFIRMED CLEAN — no stray code. |
| 5 | §4.7: move git-recap.md's Learning & Practice content to learning-guide.md in the same PR, or a follow-up PR? | Same PR — matches the SPEC's already-broad combined scope; avoids a second PR re-establishing context on the same file set. |
| 6 | §5: keep the full grill→plan→subagent-TDD cycle as one combined plan, or split into 2 sequenced plans (protection core, then shim cleanup)? | One combined plan — matches branch 5's same-PR decision; subagent-driven-TDD already parallelizes independent tasks within one plan. |

## Open Questions

None outstanding — all 6 branches identified during the SPEC review (§2, §4.6, §4.7, §5) resolved
with their Recommended answer. Ready to hand off to `/craft:plan` (plan-orchestrator tier).
