# SPEC: Token Efficiency Retrospective + Context-Tooling Follow-on Work

**Status:** approved — Task 1 DONE (docx corrected 2026-07-01, tracked changes); Task 2 clear to implement; Task 4 resolved this session; Task 3 blocked on MCP install (see Part B). Linear implementation plan: [`docs/plans/2026-07-01-token-efficiency-linear-implementation.md`](../plans/2026-07-01-token-efficiency-linear-implementation.md)
**Date:** 2026-07-01
**Consolidates:** `_archive/SPEC-token-efficiency-research-2026-06-30.md` + `_archive/SPEC-superpowers-claude-context-workflows-2026-07-01.md` (both superseded by this file, moved to `_archive/` with pointer headers)
**Grilled:** this file, 2026-07-01, 5 branches resolved — see [GRILL-token-efficiency-and-context-tooling-2026-07-01.md](GRILL-token-efficiency-and-context-tooling-2026-07-01.md) for the ledger. Satisfies `.STATUS` Next Action A's "grill before implementing" requirement for the superpowers/claude-context proposal.

---

## Part A — Retrospective: what shipped (PR #232, v2.56.0)

*(Condensed from `_archive/SPEC-token-efficiency-research-2026-06-30.md` §1–7; full research detail — sources, methodology, the 3 regressions caught by full-suite verification — stays in that file, not duplicated here.)*

**Question this started from:** abandon craft's plugin architecture for native skills/dynamic workflows, or fix the token cost within it?

**Answer:** fix it. Three structural facts drove the fix: (1) command/agent files load in full, unconditionally, on every invocation; (2) skills load conditionally, on trigger-phrase match; (3) subagent spawns inherit the caller's model tier unless pinned. None are craft-specific — they're properties of Claude Code's loading model, which is why "abandon craft" wasn't the right call.

**Quantified result:**

| Metric | Before | After | Change |
|---|---:|---:|---:|
| `/refine` command file | 630 lines | 42 lines | −93% |
| `/brainstorm` command file | 528 lines | 112 lines | −79% |
| `orchestrator-v2.md` agent file | 1473 lines | 1212 lines | −18% |
| Combined always-loaded total | 2631 lines | 1366 lines | **−48%** |
| Orchestrator agents with model pin | 0 | 2 (`sonnet`, `haiku`) | new lever |

**What this does NOT mean:** a 48% line-count reduction is a measured `wc -l` fact, not the same claim as "48% token savings." That causal link is unvalidated — see Part C, item 1.

**Status correction (this consolidation):** the original spec's header said "branch IMPLEMENTED, PR #232 open." PR #232 has since merged (`e6c24a27`, 2026-07-01, shipped in v2.56.0). Corrected here.

**Skill built as recommended:** `skills/code/command-skill-token-efficiency/SKILL.md` — scoped narrowly to command/skill/agent authoring, not a general devops token-saving skill (rejected as too broad/context-dependent — the real levers are separate problems already owned by existing craft surfaces).

---

## Part B — Follow-on work (from the superpowers/claude-context proposal)

*(Condensed from `_archive/SPEC-superpowers-claude-context-workflows-2026-07-01.md`; full task detail stays in that file.)*

**Finding 1 — Superpowers scoping correction.** An external deliverable (`Token-Efficiency-Report-and-Proposal.docx` §3.3/C1) recommended blanket non-adoption of Superpowers. That's correct only for the orchestrate/brainstorm/clarify-design-plan-code-verify layer (redundant with `/craft:orchestrate` + `/craft:grill`). It's wrong for `subagent-driven-development`, which every *implementation* plan under `docs/plans/*.md` names as its execution sub-skill (10 of 12 plan files; the 2 exceptions are a handoff and an issue-draft doc, not implementation plans) and which `.superpowers/sdd/` shows in active use (18 review-diff artifacts plus per-task briefs/reports across 8 tasks — 36 files total). *(Corrected 2026-07-01 adversarial pass: the archived original said "39 real review-diff artifacts"; the true figure is 36 total SDD files, of which 18 are `.diff` review artifacts — the "39" was a misread of the directory's `ls -la` hardlink count. The core claim — SDD is load-bearing and actively used, not dormant — holds regardless.)*

**Finding 2 — claude-context has zero namespace clashes** with craft (`mcp-mermaid` only) or savant (no MCP servers registered). Proposed as a parallel, opt-in semantic-search path for large/fuzzy queries on `~/projects/r-packages/` — not a replacement for `Grep`/`Glob`.

### Task 1 — Correct the external report (DONE 2026-07-01)

- The docx was downloaded to `~/Downloads/Token-Efficiency-Report-and-Proposal.docx` and corrected via the `docx` skill (unpack → edit XML → repack, validated).
- **What changed:** a tracked-changes insertion (author `Claude`) was added immediately after §3.3/C1's body, scoping the blanket "do not adopt Superpowers" verdict into the 3-row per-component table — subagent-driven-development=KEEP (load-bearing, plan template requires it), executing-plans=KEEP as fallback, orchestrate/brainstorm/clarify→…→verify layer=DO NOT ADOPT. The insertion explicitly notes it *narrows* C1's scope, not overturns its token-efficiency reasoning. The original C1 prose was left intact (still valid for the workflow layer).
- **§4 Summary Table** C1 row also corrected (tracked change): "Do not adopt" → "Do not adopt workflow layer only — keep subagent-driven-development (see §3.3)", so the summary and body no longer contradict.
- **Output (non-destructive):** `~/Downloads/Token-Efficiency-Report-and-Proposal-corrected.docx` (original preserved alongside). 9 `Claude` tracked-insertion markers total; `pack.py` validation passed.

### Task 2 — Generalize the token-probe script (~30-45 min, do before Task 3)

- Generalize `docs/plans/2026-06-30-namespace-token-probe.md`'s disposable probe into `scripts/token-probe.py` — parameterize on `--before <glob>` / `--after <glob>` instead of hardcoded namespace fixtures.
- Keep the cl100k_base-vs-real-tokenizer caveat in the module docstring (relative comparison, not exact Claude token count).
- Sanity-check by reproducing the original 68.3% namespace-refactor figure.
- **Done when:** runs standalone against any before/after glob pair with no hardcoded fixture data.

### Task 3 — claude-context pilot skill (~1-2 hrs, BLOCKED)

- **Precondition (locked in grill, this is the load-bearing correction from the original proposal):** the `claude-context` MCP server is not installed or connected anywhere in this environment as of 2026-07-01 — confirmed against this session's full MCP tool inventory. **This task cannot start until someone runs `claude mcp add` (or equivalent) and verifies the server is connected.** The original proposal treated this as shovel-ready; it is not.
- Once unblocked: scaffold `skills/code/semantic-code-search/SKILL.md` (template: `command-skill-token-efficiency`'s structure), define fuzzy-query trigger conditions, implement MCP-availability fallback to `Grep`/`Glob`, pilot against `medfit` (P0 MediationVerse package), measure 3-5 queries with Task 2's probe script, write up adopt/expand/abandon.

### Task 4 — `executing-plans` vs `subagent-driven-development` (RESOLVED this session)

- **Finding:** `git log --all --grep="executing-plans"` → zero commits. `.superpowers/` contains only `sdd/` (subagent-driven-development's state dir) — no `executing-plans` state directory exists. **Zero real usage confirmed.**
- **No central template/generator exists** — the "REQUIRED SUB-SKILL: ... subagent-driven-development (recommended) or executing-plans ..." line is copy-pasted inline across 10+ `docs/plans/*.md` files (not stamped from one source).
- **Decision:** going forward, new plan docs should name only `subagent-driven-development`. Not worth a retroactive 10-file edit for a doc-hygiene nit — historical docs stay as-is.

---

## Part C — Unified Open Questions / Next Actions (priority order, locked in grill)

1. **[HIGHEST PRIORITY] Real `/usage` checkpoint (~2026-07-14).** The only thing that confirms or refutes whether Part A's 48% line-reduction actually translated to session token savings. Commands ready (`npx ccusage daily --since 2026-07-01` vs. the pre-merge baseline already captured `--since 2026-06-25 --until 2026-06-30`). Record the result back in `_archive/SPEC-token-efficiency-research-2026-06-30.md` §9 (per prior explicit instruction — one doc, not a new one). **Nothing else in this file should be read as "the token-efficiency work succeeded" until this closes.**
2. Task 1 — correct external docx (blocked only on file existing in this session's reachable paths).
3. Task 2 — generalize `scripts/token-probe.py`.
4. Task 3 — claude-context pilot, **blocked on MCP install** (see above).
5. **Cross-reference, not absorbed here (locked in grill):** the 18 flagged deprecated commands (bloated body vs. `replaced-by` skill) stay tracked in issue #233 / `SPEC-craft-audit-and-next-steps-2026-06-30.md` — not duplicated into this file. Same for that spec's own open scheduling question (dedicated pre-v3.0.0 session vs. folded into general maintenance).

---

## Part D — Brainstorm addendum (2026-07-01): plugin audit, workflow-plugin deprecation, next levers

*(`/craft:workflow:brainstorm` — max depth, arch focus, 10 branches resolved. Research: [Claude Code plugin marketplaces docs](https://code.claude.com/docs/en/plugin-marketplaces), [Claude Code Plugin Marketplace 2026 — Context Cost Transparency](https://www.qcode.cc/claude-code-plugin-marketplace-2026), [Claude Code Token Optimization guide](https://buildtolaunch.substack.com/p/claude-code-token-optimization).)*

**Executed this session:**

- **Deprecated and removed the standalone `workflow@local-plugins` plugin** — verified duplicate of craft's own `commands/workflow/*` namespace (its `brainstorm.md` was 1131 legacy lines vs. craft's 112-line thin shim, same command name, same purpose). Uninstalled from `~/.claude/settings.json` `enabledPlugins`, removed from the personal `~/.claude/local-marketplace/` catalog (symlink + `marketplace.json` entry) — corrected note: that marketplace is local-only, not shared with other users, so this was a personal-config cleanup, not a community-impact fix.

**New backlog items (priority order):**

1. **Deprecated-command audit execution** (issue #233) — promoted from unscheduled backlog to next concrete task. Execute as **one batch, worst-offenders first**: `commands/check.md` (8.9:1 ratio) and the 6 commands consolidating into `skills/dev/git/` (4185 combined source lines). Same methodology as Part A (extract don't delete, full-suite verify before merge — not a sampled subset).
2. **Hooks audit** (new lever, not previously measured) — community research flagged hooks as running on every response regardless of relevance, a cost lever separate from commands/skills/agents. craft's branch-guard, no-switch-guard, and session-facet hooks have never been measured for per-turn token cost the way Part A measured commands/agents. Extend the same methodology to hooks.
3. **Automated recurring plugin-audit skill** — the 2026-06-29 manual 60-plugin audit missed the `workflow@local-plugins` duplicate found in this session. A skill that diffs `installed_plugins.json`/`enabledPlugins` against each plugin's actual command/skill surface (flagging name collisions like `workflow` vs. `craft:workflow`) would catch this class of finding automatically instead of relying on infrequent manual sweeps.
4. **Context-mode-style output routing** — research-only note, not yet actionable. Routing verbose tool/command output into a sandboxed knowledge base (vs. dumping into the conversation) is reported to cut MCP-related tokens 50-90% in active sessions. Doesn't map cleanly onto craft's actual measured cost driver (always-loaded prompt text, not tool-output volume) — flagged for future investigation, not scheduled.

**Explicit no-gos (considered and rejected, with reasoning — don't re-litigate without new evidence):**

- **Splitting craft into 2+ plugins.** The token-cost problem this lineage of work targeted (unconditional command/agent loading) is a *within-plugin* structural issue, already fixed by the thin-command/fat-skill pattern throughout craft. A plugin split addresses install-time discoverability and per-plugin context-cost display (a real 2026-era marketplace feature per the research above) — not runtime token cost, which is already measured and reduced. Revisit only after the `/usage` checkpoint (~2026-07-14, Part C item 1) confirms whether the within-plugin fixes were sufficient.

---

## Superseded originals

- `_archive/SPEC-token-efficiency-research-2026-06-30.md` — archived (research detail + §9 addendum are the source of record for Part A); not deleted, cross-linked from here.
- `_archive/SPEC-superpowers-claude-context-workflows-2026-07-01.md` — archived (full task steps are the source of record for Part B); status header already points here.

> Interrogated by grill — see [GRILL-token-efficiency-and-context-tooling-2026-07-01.md](GRILL-token-efficiency-and-context-tooling-2026-07-01.md)
