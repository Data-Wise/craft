# GRILL: Orchestrate Token-Usage Hooks

**Target:** `.STATUS` backlog item (captured 2026-07-02, from `docs/internal/TUTORIAL-orchestration-and-skill-eval-loop.md` §11's "Recommendation hook for maintainers")
**Date:** 2026-07-06
**From SPEC:** none — bare topic, no SPEC written (backlog was closed before implementation)

---

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Hooks 1+2 (live marker token field + `--report` flag) — hook 1 is infeasible as stated: a live orchestrator session (there is no persistent orchestrator process, it's the LLM session following `commands/orch.md`) has no introspective API for its own token usage; that data only exists in JSONL records the harness writes post-turn (`scripts/orchestrate-token-report.py`'s `iter_usages()` reads `rec["message"]["usage"]` from already-written assistant turns). How to resolve? | Fuse into one post-hoc flag: at run end, shell out to the existing `orchestrate-token-report.py` and write its output back into the marker as a new field. No live self-reporting. |
| 2 | Flag name for the fused hook. | `--token-report` — avoids the naming/semantics collision the interface review flagged against PR #270's `--report-only` (dist:surfaces) convention, which means something different (never-blocking release-state diagnostics). |
| 3 | Hook 3 (surface `cost_weighted` delta in `orchestrate status`) — structurally uncomputable for an in-progress run: the report script needs `end_ts` set and flushed `agent-*.jsonl` files, neither of which exist mid-run; `status` is explicitly a live/in-progress view. | Drop entirely, not deferred-with-a-note. Revisit only if a future retention/history feature makes cross-run historical queries real. |
| 4 | **Top-level: given decisions 1-3 collapse this to a single small `--token-report` flag that doesn't fix the problem that originally motivated the backlog capture (retroactive analysis of 9 old parity-gate markers failed because zero `agent-*.jsonl` transcripts survived) — build it anyway, or close the whole item?** | **Close. Build nothing.** Two independent reasons converged: (a) this session already removed the adjacent quota-tracking feature (`scripts/quota-persist.sh`, `quota_estimate.py`) with "I don't use quota anymore" — token-cost reporting is the same category of accounting tooling for spend nobody is watching; (b) `--token-report` alone doesn't solve the motivating problem — it only helps runs invoked *after* it exists, not the historical-analysis failure that prompted the backlog item, and the real prerequisite (an `agent-*.jsonl` retention policy) remains unaddressed either way. |

---

## Supporting Review Findings (fed in as codebase-first pre-answers)

Two review passes ran before the grill loop (backend/architecture lens + interface/CLI-contract lens), matching this session's earlier adversarial-review pattern:

- **Backend/architecture** (`feature-dev:code-architect`): confirmed no live token-introspection mechanism exists anywhere in craft (the `budget`/Context Monitoring dashboards in `orchestrate-reference.md` are prompt-rendered mockups, not backed by a real API). Recommended the post-hoc write-back redesign that became Decision 1.
- **Interface/CLI-contract** (`feature-dev:code-reviewer`): flagged `--report` as a naming collision risk against `dist:surfaces --report-only` (different semantics: blocking-diagnostic vs. accounting). Flagged that both `--report` and a live `status` delta would silently overpromise real-time accuracy given JSONL flush-lag with no fsync guarantee documented. Confirmed zero count-cascade impact (flags don't trigger `validate-counts.sh`).

---

## Open Questions

None remaining. This ledger's outcome is a closure, not a handoff to `/craft:plan` — there is nothing to implement.

## Handoff

**None.** Per Decision 4, this backlog item is closed. `.STATUS`'s 2026-07-02 backlog entry is updated to reflect the investigation and its outcome rather than left as an open ACTION item.
