# BRAINSTORM: Delegating to Codex and OpenCode

**Date:** 2026-08-08 · **Depth:** deep · **Focus:** ops
**Branch:** dev · **Categories:** tech, risks, timeline

## Origin

Seed request (refined via `--refine`): research (web) best practices for
delegating coding tasks from Claude Code to OpenAI Codex (via the `codex`
plugin) and to OpenCode (via the `opencode`/`opencode-async` MCP bridges
just installed this session — both promoted to `user` scope, tested working
over stdio JSON-RPC: `opencode` exposes ~80 tiered tools, `opencode-async`
exposes 7 fire-and-forget tools). Not scoping a new feature — scoping how to
*use* three delegation surfaces craft's user now has installed:

| Surface | Style |
|---|---|
| `codex` plugin (`codex:codex-rescue` agent) | Synchronous hand-off — Claude drives `codex exec` as a subprocess, one broker per cwd |
| `opencode` MCP bridge | Synchronous-first, tiered (`opencode_setup` → `opencode_ask`/`opencode_run` → fine-grained session control) |
| `opencode-async` MCP bridge | Fire-and-forget — submit, poll `opencode_sessions`, `opencode_respond` on `input_required` |

## Context Scan

- **No existing craft spec covers delegation strategy.** `grep -ril
  "codex\|opencode" docs/specs/` (excluding `_archive/`) found nothing —
  this is genuinely new ground for craft's own docs, even though the tools
  themselves were just wired up this session.
- **`docs/tutorials/TUTORIAL-opencode-mcp-plugin.md`** (added this session)
  covers *setup and mechanics* of the two OpenCode bridges — scope, gotchas,
  smoke-test method. It does not cover *when/how to use them well*, which is
  this brainstorm's subject.
- **`agents/codex-rescue`** (via the `codex` plugin) already encodes one
  delegation trigger informally: "proactively use when Claude Code is
  stuck, wants a second implementation or diagnosis pass." No equivalent
  trigger doc exists for either OpenCode bridge yet.

## Research Findings (web)

**Task selection — when delegation is worth it at all.** The dominant
framing across sources: delegate when *describing* the task is cheaper than
*doing* it. A one-line rename isn't worth a delegation round-trip; a
codebase-wide migration is. Good delegation candidates: test generation,
boilerplate, documentation, simple refactors, well-scoped SWE tasks. Poor
candidates: security logic, architectural decisions, unfamiliar stacks,
anything the delegator can't verify afterward. Subagents/delegated calls
are "not free" — startup cost, coordination overhead, and failure modes
that don't exist when you just do the work yourself.

**Model/tier selection.** Not every delegated task needs the strongest
model. A repeated pattern: cheap/fast models for narrow workers (routing,
formatting, simple extraction), stronger reasoning models reserved for the
orchestrator or for genuinely hard sub-tasks. `opencode`'s own tool
description matches this — it explicitly warns against assuming a provider
is available and tells the caller to discover providers/models before
picking one per task.

**Structuring the delegated prompt.** Practical guidance converges on:
single-line messages (no embedded newlines — when driving an interactive
TUI, a newline can act as Enter and fragment the prompt; this does not
apply to `codex exec`, which takes the prompt as a plain argument/stdin
string, not keystrokes into a TUI), explicit scope statements, and — for
OpenCode specifically — picking the right agent mode (`explore` for
investigation, `plan` for structured analysis, `build` for direct
execution) rather than defaulting to one mode for everything.

**Orchestration pattern.** The Manager-Worker / hierarchical pattern shows
up repeatedly as the best fit for coding delegation: one agent plans and
assigns, worker agents execute narrow scoped pieces, the manager reviews.
Each worker gets a fresh context and a clean failure boundary, which
contains cascading failures rather than propagating them back through the
whole session.

**Token cost — directly answers the "token usage" risk flagged below.**
Every hop in a delegation chain that invokes an LLM is a billed API call —
a topology that looks cheap in-process can multiply spend once each
specialist is a real request. The mechanism to watch: the orchestrator's
own context grows with every round-trip result that flows back to it —
sources report a 5-10 sub-agent pipeline can push the orchestrator itself
to roughly 30-50k tokens by the end, independent of what the workers
spent (single-source estimate, not independently measured here). Two
mitigations, with tradeoffs reported the same way: (1) pass a small
structured context object instead of full conversation history (roughly
200-500 tokens vs. 5,000-20,000), or (2) summarize at the handoff (roughly
a 70-90% reduction) at the cost of ~500ms-1.5s added latency and some
information loss. Execution budgeting (max tokens, max steps, max time per
delegated call, with alerts on threshold breach) is the other lever named
repeatedly.

**Failure handling.** Consistent theme: isolate the blast radius. A failed
worker should fail cleanly within its own context rather than corrupting
the manager's state. The two OpenCode bridges use *different* status
vocabularies, not a shared one: `opencode-async`'s task status is
`working` / `input_required` / `completed` / `failed` / `cancelled`
(`opencode_cancel` reaches the last one); the npm `opencode` bridge's
`opencode_check` reports `running` / `completed` / `error` instead — do
not assume interchangeability between the two when writing status-handling
code against either.

Sources:

- [GitHub - eddiearc/codex-delegator](https://github.com/eddiearc/codex-delegator)
- [Codex Task Dispatcher - Claude Code Skill for OpenAI](https://mcpmarket.com/tools/skills/codex-task-dispatcher)
- [Claude codex-cli skill: 10 ways to bridge Claude Code and OpenAI Codex CLI](https://mcp.directory/blog/claude-codex-cli-skill-guide)
- [GitHub - Traves-Theberge/opencode-mcp](https://github.com/Traves-Theberge/opencode-mcp)
- [Best practices for Mastering AI Agents, Subagents, Skills & MCP](https://foojay.io/today/best-practices-for-working-with-ai-agents-subagents-skills-and-mcp/)
- [Cost Management for LLM Agents](https://apxml.com/courses/multi-agent-llm-systems-design-implementation/chapter-6-system-evaluation-debugging-tuning/managing-llm-agent-costs)
- [Multi-Agent Orchestration Patterns: A Practical Guide](https://www.glukhov.org/ai-systems/architecture/multi-agent-orchestration-patterns/)
- [AI Agent Subagent Orchestration: When to Spawn vs When to Do It Yourself](https://dev.to/bobrenze/ai-agent-subagent-orchestration-when-to-spawn-vs-when-to-do-it-yourself-4opg)
- [The Delegation Decision: When to Use an Agent vs Do It Yourself](https://agentpatterns.ai/agent-design/delegation-decision/)

## Expert Questions & Answers

**Technical constraints/preferences** (multi-select): Use existing stack
(research the 3 tools already installed, don't evaluate new ones) + New
tooling needed (stay open to surfacing other options if research turns them
up) + Architectural pattern (define routing rules for which task type goes
where). → Net: research the installed stack deeply, but the output should
still propose a routing rule, and flag credible alternatives if the
research surfaces them unprompted.

**Integration target** (multi-select): craft's own commands/skills +
Ad-hoc manual use only. → Net: findings should be usable standalone today
(manual delegation decisions), but written so a future craft skill/command
could consume the routing rule directly without a rewrite.

**Timeline:** Flexible. **First usable outcome:** Flexible. No deadline
pressure — quality over speed on this one.

**Biggest risks** (multi-select): Technical complexity (routing logic) +
Integration issues (auth/model availability) + Performance concerns
(latency/cost) + **token usage for codex and opencode models** (user
addition, not from the question bank — see Token Cost research above,
directly responsive).

**Edge cases** (multi-select): Failure scenarios (delegated agent
hangs/errors/garbage output) + Concurrent access (codex's per-cwd broker +
opencode-async's session model, both need to survive multiple in-flight
delegations) + Empty/invalid input (vague delegated prompts producing
useless output).

## Proposed Routing Rule (ops output)

Based on research + the answers above, a first-cut decision rule — not yet
adopted as policy, offered for the follow-up spec if this gets built out:

1. **Do it yourself** when: the task is smaller to describe than to do, it
   touches security/architecture/unfamiliar-stack decisions, or you can't
   independently verify the result.
2. **Delegate to `codex`** when: it's a genuinely hard, well-scoped SWE
   task (complex refactor, deep debugging) and you want a second
   implementation/diagnosis pass — matches the existing `codex-rescue`
   agent's own trigger condition, no new logic needed there.
3. **Delegate to `opencode` (sync)** when: the task is a one-shot
   question/lookup that benefits from a different model's perspective, and
   you want the answer inline, in this turn — `opencode_ask` after
   `opencode_setup`/`opencode_provider_models` discovery.
4. **Delegate to `opencode-async` (fire-and-forget)** when: the task is
   long-running and you don't want to block this session on it — submit,
   keep working, poll `opencode_sessions` later.
5. **Always budget before firing:** state an explicit stop condition (max
   turns/time) in the delegated prompt itself where the target tool
   supports it: uncontrolled delegation chains are the direct cause of the
   token-cost risk flagged above.

## Risks & Edge Cases (recorded, not yet mitigated in code)

- Token spend compounding across delegation hops — no craft-side budget
  enforcement exists yet for either bridge.
- No craft-side timeout/hang detection wired to either `opencode` bridge
  today (craft's own `orchestrate-dispatch` mode has this for its own
  subagents — worth reusing the pattern rather than inventing a new one,
  per the "reuse, don't duplicate" instinct that shaped the `codex` plugin
  integration).
- Concurrent delegation to the same cwd via `codex` (single broker per
  directory) vs. multiple parallel `opencode-async` sessions — not
  stress-tested.

## Test Plan

| Tier | Status |
|---|---|
| unit | N/A — no new parser/script proposed by this brainstorm |
| integration | N/A — no cross-command data flow proposed yet |
| e2e / dogfood | N/A — no craft command/skill change proposed yet; this is a research artifact, not an implementation |
| dependency | N/A — no external dependency change |
| count-cascade | N/A — no new command/skill/agent |

Nothing here is code-shaped yet — the routing rule above is a candidate for
a future skill, not a shipped one. Re-run test-plan inference once/if this
becomes a `/craft:plan` implementation.

## Documentation

Doc-impact scorer (threshold ≥3) applied against the routing rule above,
should it ship as a skill later:

- [ ] Guide — N/A, no implementation yet
- [ ] REFCARD entry — N/A, no implementation yet
- [ ] Demo — N/A, no implementation yet
- [ ] Mermaid diagram — N/A, no implementation yet

This BRAINSTORM itself is the documentation artifact for now.

## Adversarial Review (dogfooding the routing rule on itself)

Both delegation surfaces this brainstorm is about were used to review the
uncommitted diff that produced it (this file + the tutorial + the mkdocs
nav line) — the routing rule ate its own dog food same-session.

| Reviewer | Model | Cost | Tokens | Findings |
|---|---|---|---|---|
| `codex` (`codex exec review --uncommitted`) | GPT-5-based (Codex default) | not reported by this CLI | 1,010,356 total (1,002,654 in @ 91% cache hit, 7,702 out) | 2 (both real: markdownlint gap, wrong tool count) |
| `opencode` (`opencode_run`, provider `opencode-go`) | `deepseek-v4-pro` | $0.0003 | 1,555 total (267 in, 1,288 out) | 6 (see below) |

**Cost delta is ~650× by token count** for this task — not a general claim
about the models' relative capability, just this one review of a
~250-line diff. Codex's number is inflated by a large, mostly-cached
system-prompt/tool context (skills + instructions bundle), not by doing
more review work; `opencode`'s dispatch had no comparable fixed overhead
in this setup. **Not a dollar comparison** (added on adversarial
re-review, GRILL Branch 4): codex ran on a flat subscription (sunk cost,
no marginal $ per call), while `opencode-go` bills per call — token count
is still a real signal (context-window pressure, rate limits apply under
a subscription too), just don't read "650×" as a cash-cost claim.

**opencode/deepseek-v4-pro findings** (both fixed in this doc + the
tutorial as part of this same session):

1. **F1 (High):** this brainstorm's own Origin section still said "6
   fire-and-forget tools" after the tutorial's copy had already been fixed
   to 7 — the two docs contradicted each other. Real bug: codex's review
   never caught this because it only reviewed the diff, and this line
   hadn't changed in the diff it saw (it was wrong from the first version).
2. **F2 (High):** the Failure Handling section asserted `opencode` and
   `opencode-async` share one status vocabulary
   (`working`/`input_required`/`completed`/`failed`). False — that set is
   `opencode-async`-only; `opencode`'s `opencode_check` reports
   `running`/`completed`/`error`. Also caught a missing `cancelled` status.
3. **F3 (Medium):** tutorial said the usage guide lives at
   `serverInfo.instructions` — it's actually a top-level `instructions`
   field, sibling to `serverInfo`, not nested in it.
4. **F4 (Medium):** the newline-as-Enter caveat (from web research) was
   misattributed to `codex exec` specifically — that mode takes the prompt
   as a plain argument, not TUI keystrokes, so the hazard doesn't apply
   there. Softened to the general interactive-TUI case.
5. **F5 (Low):** missing caveats — `OPENCODE_AUTO_SERVE=false` disables
   auto-start; `cancelled` status wasn't surfaced (see F2); the two docs
   should cross-link each other. Not individually actioned (low value,
   noted here for completeness).
6. **F6 (Low):** several web-research numbers (30-50k token orchestrator
   growth, 70-90% summarization reduction, etc.) were stated as fact
   without a confidence hedge or citation in the Sources list — corrected
   to "sources report" / "roughly" framing.

**codex/GPT-5 findings** (both fixed earlier in this session, see the
commit history): missing blank line before the Sources markdown list
(markdownlint), and the same wrong tool-count bug F1 re-caught in a
different file.

**Takeaway for the routing rule:** two independent reviewers with
different strengths caught non-overlapping bugs — codex caught a lint gate
failure (mechanical, would have failed CI); opencode caught two factual
inconsistencies a lint gate can't see (contradicting docs, a misattributed
technical claim). Neither was redundant with the other. This is itself
evidence for the "use both, not just one" instinct in the routing rule
below rather than a full head-to-head model comparison (n=1 diff, not a
benchmark).

## Next

- **Now spec'd.** See `docs/specs/SPEC-codex-opencode-delegation-2026-08-08.md`.
