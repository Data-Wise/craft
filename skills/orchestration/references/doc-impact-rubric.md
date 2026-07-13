# Doc-Impact Scoring Rubric

> Single source of truth for the doc-impact scoring algorithm used by `brainstorm`/`plan`/`grill`'s
> default test+doc scaffolding (`plan-orchestrator` skill) and by `arch:plan`/`spec-review`'s
> opt-in scaffolding. Previously lived in `commands/docs/sync.md`; that command moved to `folio`
> in the folio-split (Phase 3, 2026-07-12) — this file is now the canonical copy. Do not
> reimplement or hardcode a parallel type list anywhere else; always defer here.

## Scoring factors

| Factor | Guide | Refcard | Demo | Mermaid | Tutorial | API | Cookbook | Architecture-doc |
|--------|-------|---------|------|---------|----------|-----|----------|-------------------|
| New command (each) | +1 | +1 | +0.5 | +0 | +1 | +0 | +1 | +0 |
| New module | +3 | +1 | +1 | +2 | +2 | +2 | +1 | +2 |
| New hook | +2 | +1 | +1 | +3 | +1 | +0 | +1 | +1 |
| Multi-step workflow | +2 | +0 | +3 | +2 | +3 | +0 | +3 | +1 |
| Config changes | +0 | +2 | +0 | +0 | +0 | +1 | +1 | +0 |
| Architecture change | +1 | +0 | +0 | +3 | +0 | +0 | +0 | +5 (†) |
| User-facing CLI | +1 | +1 | +2 | +0 | +2 | +0 | +2 | +0 |
| New public API/endpoint | +0 | +0 | +0 | +0 | +0 | +5 | +1 | +0 |
| New user-facing surface | +0 | +0 | +0 | +0 | +2 | +2 | +2 | +2 |

**† Architecture-doc double-count subtraction rule:** "Architecture change" already feeds the
Mermaid factor (+3) — a diagram gets generated for the same underlying signal. If the
Architecture-doc type's score were computed by adding its own "Architecture change" contribution
on top of that, one arch change would double-trigger two recommendations (Mermaid diagram +
Architecture-doc write-up) off a single signal. **Fix:** when computing the Architecture-doc
score, first subtract the Mermaid factor's "Architecture change" contribution (3) from the shared
architecture-change signal, then apply the Architecture-doc factor's own weight (5) to what
remains. Concretely: `arch_doc_contribution = max(0, raw_arch_signal_weight - mermaid_arch_weight) + arch_doc_own_weight_if_signal_present`. In practice this means: an architecture change alone
(no other Architecture-doc-triggering factor) scores Mermaid at +3 but contributes 0 net toward
Architecture-doc from that same signal — Architecture-doc only reaches its own threshold via
*other* factors (new module, multi-step workflow, new user-facing surface) that are additive, not
shared with Mermaid.

## Tiered thresholds (spawn-cost-aware)

- **Cheap, in-context types** (Guide, Refcard, Demo, Mermaid) — threshold stays **score ≥3**. These
  are authored inline or via a lightweight embed; no separate agent spawn required.
- **Heavy, agent-authored types** (Tutorial, API, Cookbook, Architecture-doc) — threshold is
  **score ≥5 OR a concrete "new user-facing surface" trigger**, whichever comes first. These are
  authored by spawning a dedicated doc agent (`tutorial-engineer`, `api-documenter`,
  `docs-architect` — note: these 3 agents moved to `folio` in the same split; craft's default
  scaffolding recommends the doc type, the caller decides how to author it) — an expensive
  per-invocation cost that should only be paid when authoring is genuinely needed, not for minor
  edits.
  - **"New user-facing surface" trigger, defined:** a change that adds something an end user (not
    a maintainer) discovers and uses directly for the first time — a new command, a new public
    API/endpoint, a new top-level workflow/concept, or a new architectural component visible in
    the system's public boundary. Config tweaks, internal refactors, and additions to an
    *existing* documented surface do not qualify. When this trigger fires, the heavy type is
    recommended regardless of numeric score.
