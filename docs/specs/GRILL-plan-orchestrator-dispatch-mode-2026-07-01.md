# GRILL: plan-orchestrator In-Session Background-Dispatch Mode

**Target:** quoted topic (no path argument) — a new `--output orchestrate-dispatch` mode for
`skills/orchestration/plan-orchestrator/SKILL.md` Mode 1 (Spec -> ORCHESTRATE), formalizing the
ad hoc worktree + background-`Agent` dispatch pattern used earlier in this same session (tasks #3/#4
of docs/plans/2026-07-01-token-efficiency-linear-implementation.md), while closing the safety gap
that pattern had relative to the existing STOP-new-session mode.

**Date:** 2026-07-01
**Outcome:** 10 branches resolved, design locked. Not yet implemented — hand off to `/craft:plan`.

**Prior research this session established** (not re-litigated here): ad hoc background-agent
dispatch beats `/craft:orchestrate:plan`'s existing STOP-new-session mode on token cost (no N
cold-started sessions reloading CLAUDE.md/system-prompt) and on attention cost (zero — background
agents notify on completion vs. you personally babysitting N terminals). It loses on the STOP
rule's safety guarantee (a new session structurally cannot depend on live-conversation-only
context) and on traceability (durable ORCHESTRATE file vs. ephemeral session task list). This
design closes both gaps without giving back the token/attention win.

**Confirmed non-duplicate:** checked `commands/orchestrate/workflow.md` +
`skills/orchestration/` first — nothing in craft currently dispatches background agents into
several separate pre-existing worktrees from one live planning session. `orchestrate:workflow`
fans out multiple agents *within* one already-open worktree via a coded YAML control-flow; this
is a different capability (cross-worktree, from the planning session, no YAML required).

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| 1 | Attachment point | New flag on plan-orchestrator Mode 1 only (Spec->ORCHESTRATE) -- not bolted onto brainstorm (wrong layer -- brainstorm is divergent, ends in a SPEC, never touches code) and not a wholly separate 5th mode (would duplicate Mode 1's spec-parsing/ORCHESTRATE-generation logic -- the exact rich-duplicate-body anti-pattern this session's deprecated-command audit is hunting elsewhere). |
| 2 | Flag shape | Third `output` enum value on the existing deprecated command shim's frontmatter arg: `orchestrate-worktree \| orchestrate-only \| orchestrate-dispatch`. Not a separate boolean --dispatch flag (would allow nonsensical combos like --output orchestrate-only --dispatch, needing validation logic). |
| 3 | Self-containment enforcement | The dispatched Agent's entire prompt is 'read ORCHESTRATE-`<topic>`.md in full, then execute it' -- the SAME durable artifact a fresh human session would read under the existing STOP mode. Self-containment becomes structural (inherited from the ORCHESTRATE file's own completeness, already required by Mode 1) rather than a checklist followed by discipline or a phrase-scanning lint script (can't catch semantic context-dependence anyway). |
| 4 | Multiplicity | One spec per invocation, matching every existing plan-orchestrator mode. For N independent backlog items (this session's actual case: #3 + #4), call the command N times in one message -- parallelism comes from multiple calls, not from teaching the skill to fan out internally. Explicitly rejected batch multi-spec dispatch to avoid overlapping with orchestrate:workflow's parallel() fan-out (the same duplicate-capability risk as branch 1). |
| 5 | Review gate before merge | The dispatched agent updates the ORCHESTRATE file's own '- [ ] 1.1 `<task>`' checkboxes and Phase Overview status column AS it completes each phase -- durable, session-independent progress tracking reusing the existing template. Review gate = dispatching session re-reads the updated file + runs its own Verification section's test command before offering merge. Rejected: relying solely on the Agent tool's ephemeral final-message summary (lost once the session ends, no record for a human opening the worktree cold later); rejected auto-invoking /code-review as a hard gate (adds cost/latency, duplicates the human review that's happening anyway). |
| 6 | Stuck-agent handling | orchestrate-dispatch requires (or strongly warns if missing) a GRILL-*.md for the underlying spec -- grilling is exactly the step that resolves judgment calls BEFORE dispatch, since background agents are one-shot and cannot pause to ask a question. Backstop: dispatched agents that hit genuine unresolved ambiguity must leave that phase's checkbox unchecked, add a one-line blocker note to the ORCHESTRATE file, and stop -- never guess. |
| 7 | Confirm-before-dispatch gate | Keep an explicit AskUserQuestion confirm step mirroring Mode 1's existing step 4 (confirm plan with user) -- show the generated ORCHESTRATE summary + worktree path, ask dispatch-now/review-first/cancel before calling Agent. Matches how this session actually proceeded (grill gate, worktree confirmation, agent-prompt review before each of the 2 real dispatches). |
| 8 | Resumability | Idempotent resume: a re-dispatch against the SAME ORCHESTRATE file must detect already-checked '- [ ] 1.1' phases (per branch #5's own tracking) and instruct the new agent to skip them, starting from the first unchecked phase. Reuses data the design already produces -- no new tracking mechanism. Rejected: always-restart-from-Phase-1 (risks redoing completed work / conflicting edits on re-run, since Agent calls have no built-in retry/resume semantics). |
| 9 | Concurrency cap | Soft cap at 2 concurrent dispatches per session; an explicit AskUserQuestion confirmation gates any 3rd+ concurrent dispatch. Matches this session's own actual pattern (2 concurrent, chosen deliberately) and guards against the review-queue-overload failure mode flagged earlier in this session (stacking unreviewed work faster than it can be verified). Not a hard block -- a deliberate larger fan-out is still possible, just confirmed. |
| 10 | Failure/hang detection | Cross-check the Agent tool's completion notification against the ORCHESTRATE file itself -- when notified, the dispatching session must verify checkboxes actually advanced (not just trust the agent's final chat summary). Notification fires but no checkboxes moved -> flag as suspected silent failure, do not offer merge. No notification within a reasonable window -> surface the crash/hang case explicitly, do not wait silently. Closes the gap where branches #5 (review gate) and #8 (resumability) both assume completion or death is already KNOWN -- neither covered detecting a hung agent, a crashed Agent call (tool docs: returns null on terminal API error after retries), or a false-positive success claim. Uses data the design already produces (checkboxes) plus the existing platform notification mechanism -- no new infrastructure. Rejected: trusting the notification alone (leaves exactly this gap open -- 'silence looks identical to still-running', per Monitor's own coverage principle). |

## Open Questions

- [ ] Exact wording/location of the GRILL-file precondition check in branch 6 -- warn-only (advisory, matches ADR-003 precedent elsewhere in this repo) or hard-block? Not resolved, needs a decision during /craft:plan.
- [ ] Whether `.STATUS` Active Worktrees entries get auto-written by the new mode or stay manual (Mode 1's existing step 7 already says 'Update .STATUS' -- likely just extends unchanged, but not explicitly confirmed in this grill).
- [ ] Not implemented yet -- this ledger is the handoff artifact for /craft:plan, no code/skill changes made this session for this topic.

## Research finding: sequential-thinking MCP (rejected for this design)

Investigated per explicit request. **Not adopted.** Sources: [Sequential Thinking MCP Server (official)](https://github.com/modelcontextprotocol/servers/tree/main/src/sequentialthinking), [MCP Servers directory](https://mcpservers.org/servers/modelcontextprotocol/sequentialthinking), [Sequential Thinking in Claude Code -- 2026 Blueprint](https://www.quantizelab.dev/articles/sequential-thinking-in-claude-code), [Optimising MCP Server Context Usage](https://scottspence.com/posts/optimising-mcp-server-context-usage-in-claude-code).

Mechanically: exposes one tool (`sequential_thinking`) the model calls repeatedly, each numbered 'thought' a full tool-call/tool-result round trip -- costs MORE tokens than Claude's native (internal) extended thinking, not less. Its real value (a human watching numbered thoughts says 'branch from thought #3') requires a human present mid-reasoning -- structurally unavailable in this design's unsupervised background-dispatch context. Also redundant with branch #6 (stuck-agent handling), which already resolves ambiguity BEFORE dispatch via the grill-gate rather than during an unsupervised run. Rejected on both token-cost and mechanism-fit grounds.
