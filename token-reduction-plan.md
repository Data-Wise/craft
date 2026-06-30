# Claude Code Token Reduction — Research & Plan

**For:** Stat-Wise (Davood Tofighi) · **Date:** 2026-06-30 · **Scope:** craft plugin + dev-tools workflow

---

## TL;DR

🔴 **Verdict: Keep craft. Don't migrate to bare native skills/dynamic workflows.** The mechanism that's burning your tokens is well-documented, narrowly located, and fixable in under an hour — not a reason to rebuild your toolchain.

**Root cause, confirmed against official docs + community data:**
1. Subagent calls open a **fresh, isolated context window** every time — no inheritance from your main session, full re-bill. Community `/usage` reports: **85% of heavy-session spend is subagent fan-out**.
2. craft's `agents/orchestrator-v2.md` is **1,473 lines** — that *entire* file re-enters context on every spawn, with no lazy-loading (unlike commands/skills, which only cost ~100–200 tokens until invoked).
3. "Ultra code" (dynamic workflows) is the **opposite** of a fix — Anthropic's own docs warn it can use *substantially more* tokens than normal sessions.

**Fix priority:** (1) model-route the orchestrator agents, (2) audit the env var that silently breaks routing, (3) trim orchestrator-v2 into a lazy-loaded skill + thin agent shell, (4) tighten subagent task scoping, (5) measure with `/usage` and `/context` before/after.

**Est. effort:** 60–90 min total. **Est. impact:** 30–50% drop on the subagent line item (community-reported range for model routing alone).

---

## Part 1 — What I Researched

### Official Anthropic / Claude Code docs (primary source)

| Doc | Key finding relevant to you |
|---|---|
| [Manage costs effectively](https://code.claude.com/docs/en/costs) | Subagent tasks billed independently; "agent teams" (multi-instance) use **~7x** more tokens than standard sessions when teammates run in plan mode. Extended thinking billed as *output* tokens — can be tens of thousands per request. Official reduction levers: model selection, `/compact` proactively, reduce MCP overhead, move CLAUDE.md detail into skills, delegate verbose ops to subagents *deliberately scoped*. |
| [Create custom subagents](https://code.claude.com/docs/en/sub-agents) | Subagents exist specifically to keep exploration/logs *out* of main context — but each one pays its own re-read cost. You can pin `model:` per subagent in frontmatter. |
| [Orchestrate subagents at scale with dynamic workflows](https://code.claude.com/docs/en/workflows) | Explicit warning: dynamic workflows "**can consume substantially more tokens** than a typical Claude Code session" — recommended only for small, well-scoped tasks first. This directly contradicts the idea that "ultra code" saves tokens. |
| [Explore the context window](https://code.claude.com/docs/en/context-window) | Startup breakdown (illustrative): system prompt ~4,200 tok, auto-memory ~680 tok, env info ~280 tok, **MCP tool names ~120 tok (deferred — full schemas load only on first use)**. Confirms tool *definitions* are cheap until used; what's expensive is large always-loaded text (CLAUDE.md, agent system prompts). |
| [Extend Claude with skills](https://code.claude.com/docs/en/skills) | **Custom commands have been merged into skills.** `.claude/commands/*.md` and `skills/*/SKILL.md` both work the same way: only name+description load at startup; the body loads only when invoked. This means craft's 117 commands and 42 skills are *not* the primary startup cost — they're already lazy. |
| [How Claude remembers your project (CLAUDE.md)](https://code.claude.com/docs/en/memory) | CLAUDE.md is loaded **in full, every session, regardless of length** — no lazy loading, no eviction. Target <200 lines. Auto-memory `MEMORY.md` caps at 200 lines/25KB. This is a second, independent lever from the agent issue. |

### Community sources (cross-checked against official docs, not taken at face value)

| Source | Claim | My assessment |
|---|---|---|
| [youcanbuildthings.com — Why Subagents Burn So Many Tokens](https://youcanbuildthings.com/articles/claude-code-subagents-token-usage/) | 85% of heavy-session spend from subagents; `CLAUDE_CODE_SUBAGENT_MODEL` env var silently overrides per-agent `model:` frontmatter | **Verified-consistent** with official subagent docs. The env var gotcha is the single highest-leverage check — costs 2 minutes, can invalidate your entire routing setup silently. |
| [KDnuggets — 7 Practical Ways](https://www.kdnuggets.com/7-practical-ways-to-reduce-claude-code-token-usage) | "Subagents are not automatically cheaper" — for *small* tasks, subagent overhead (prompt + tool defs + round trips) can exceed just doing it inline | **Important correction** to a naive "always delegate" heuristic. Confirms: scope matters more than the delegate/don't-delegate binary. |
| [systemprompt.io — Reduce Costs 60%](https://systemprompt.io/guides/claude-code-cost-optimisation) | Four-habit framework: model selection, context management, thinking-token caps, prompt caching | Consistent with official `/costs` doc; no new mechanism, just packaging. |
| [MindStudio — Skills vs Plugins](https://www.mindstudio.ai/blog/claude-code-skills-vs-plugins-difference) | MCP servers (not skills/commands) load full tool defs into context regardless of plugin bundling | Now superseded by the official docs above — Claude Code has since moved to **deferred tool schemas by default** (you're seeing this directly in this very session, where most tools show as "deferred" until searched). This community claim is partially stale; verify your CC version supports tool search before assuming the old behavior. |
| GitHub issue #55051 (cited secondhand) | A vague prompt ("deep security review, use multiple subagents") burned 50% of a weekly Max 20 limit in ~30 seconds | Anecdotal but mechanistically plausible given fan-out math (3 subagents ≈ 4x one thread). Matches the "tight briefs" guidance in both official docs and community pieces. |

### Correction to my prior recommendation

In my first pass I said "dump dynamic workflows" without sourcing it directly — confirmed now: it's explicitly Anthropic's own warning, not just my inference. I also softened the blanket "always delegate to subagents" framing — KDnuggets' point that small tasks can lose money to subagent overhead is correct and now folded into the plan below.

---

## Part 2 — Where Your Tokens Are Actually Going (craft-specific)

Inspected `/Users/dt/projects/dev-tools/craft` directly:

- `.claude-plugin/plugin.json`: 117 commands + 42 skills + **8 agents** bundled as one plugin.
- `agents/orchestrator.md`: 298 lines.
- `agents/orchestrator-v2.md`: **1,473 lines** — this is the structural problem. Per the skills doc, commands/skills lazy-load; agent *system prompts* do not have an equivalent on-demand mechanism documented — the full file is the subagent's system prompt every time it's spawned.
- 6 commands directly reference `subagent`/`Task(` spawning — these are your fan-out entry points.
- Total commands+skills markdown: ~50K lines, but per the official skills doc this is mostly inert (frontmatter-only) until invoked, so it is **not** the main lever here.

**Bottom line:** the leak isn't "craft has too much stuff." It's "craft's orchestrator agent is a 1,473-line system prompt that gets fully re-billed on every delegation, likely at your main session's model tier."

---

## Part 3 — The Plan

### Phase 0 — Measure before touching anything [5 min]
1. Run `/usage` (press `d`/`w` to toggle 24h/7d) — get the actual % breakdown by skill/subagent/plugin/MCP server. **Do this first.** Don't assume orchestrator-v2 is the culprit until this confirms it.
2. Run `/context` to see current session's live breakdown.
3. Note today's baseline numbers somewhere (Apple Notes or `.STATUS`) so Phase 4 has something to compare against.

### Phase 1 — Close the silent-override gap [2 min]
```bash
echo "CLAUDE_CODE_SUBAGENT_MODEL: ${CLAUDE_CODE_SUBAGENT_MODEL:-(unset)}"
```
If set, it overrides every subagent's frontmatter `model:` field with **no warning in the transcript**. Unset it (or in `~/.zshrc`/`~/.bashrc` if it's set there) before doing any routing work below — otherwise Phase 2 will appear to do nothing.

### Phase 2 — Model-route craft's agents [15 min]
Edit `agents/orchestrator.md` and `agents/orchestrator-v2.md` frontmatter:
```yaml
---
name: orchestrator-v2
model: sonnet   # down from inherited Opus/main-session tier, unless it does real architectural judgment
---
```
Reserve `model: opus` only for sub-steps that need deep reasoning (e.g., CRAN-blocker triage); route mechanical sub-tasks (status aggregation, doc-staleness checks, count validation) to `model: haiku`. This is the single highest-leverage, lowest-effort change — community-reported 30–50% drop on the subagent line from routing alone.

Also lock a sane session default in `~/.claude/settings.json`:
```json
{
  "model": "sonnet",
  "availableModels": ["opus", "sonnet", "haiku"]
}
```

### Phase 3 — Shrink orchestrator-v2's always-loaded footprint [30 min]
1,473 lines is the real structural problem since it has no lazy-load path. Two options, pick one:

- **Option A (recommended, lower risk):** Extract the bulkiest reference sections (e.g., the "BEHAVIOR 0: Forked Context Execution" block and similar large procedural sections) out of the agent file and into a companion **skill** (`skills/orchestrator-behaviors/SKILL.md`). Leave a thin pointer in the agent's system prompt ("see skill X for forked-context execution rules") so it loads on-demand instead of every spawn. Skills cost ~100–200 tokens until invoked vs. the full body cost every time for an agent file.
- **Option B (more invasive):** Split orchestrator-v2 into 2–3 narrower agents with smaller individual system prompts, each scoped to one job (e.g., `release-orchestrator`, `health-orchestrator`), so any single spawn only pays for the relevant slice.

Start with A — it's reversible and matches the documented skills lazy-load mechanism exactly.

### Phase 4 — Tighten how subagents get invoked [ongoing habit]
- Replace open-ended prompts ("audit the ecosystem," "do a deep review, use multiple subagents") with scoped briefs ("check only `medfit/DESCRIPTION` and `NAMESPACE` for CRAN compliance").
- For genuinely small tasks (single file check, quick git status), **don't delegate** — KDnuggets' point holds: subagent startup overhead (prompt + tool defs + round trip) can exceed the cost of doing it inline.
- Use **plan mode** (`Shift+Tab`) before any multi-step craft command that might fan out, so you see the plan before tokens are spent on execution.

### Phase 5 — Independent CLAUDE.md lever [10 min, separate from the agent issue]
Your global CLAUDE.md (this file) and `craft/CLAUDE.md` both load in full every session, uncompressed, every turn. Check line counts:
```bash
wc -l ~/.claude/CLAUDE.md /Users/dt/projects/dev-tools/craft/CLAUDE.md
```
Target <200 lines each per official guidance. If either is bloated with procedural detail (multi-step workflows, not just facts/rules), move that detail into a skill — same lazy-load benefit as Phase 3, applied to your memory files instead of agents.

### Phase 6 — Re-measure [5 min]
Re-run `/usage` after a week of normal use under the new routing. Compare against the Phase 0 baseline. Target: 30–50% drop on the subagent percentage, per community-reported ranges — treat this as a hypothesis to confirm, not a guarantee.

---

## Part 4 — Explicit Answer to "Should I switch to native skills + dynamic workflows + ultra code?"

| Option | Verdict | Why |
|---|---|---|
| **Drop craft, rebuild on bare native skills** | 🔴 No | craft's commands/skills already use the lazy-load mechanism natively (commands merged into skills as of recent Claude Code versions) — you'd be rebuilding something structurally similar at high migration cost, for a problem that's actually in 2 agent files, not the skill/command layer. |
| **Dynamic workflows / "ultra code"** | 🔴 No, not for cost reasons | Anthropic explicitly documents these as **higher** token consumers, intended for throughput/autonomy on large tasks, not cost control. Using it to *reduce* spend is solving for the wrong variable. |
| **Model-route + trim the 2 orchestrator agents** | 🟢 Yes — do this | Directly targets the confirmed mechanism (large always-loaded agent system prompts at expensive model tiers), with official-doc-backed levers, reversible, ~1 hour of work. |

---

## Next Step

Want me to draft the actual frontmatter diffs for `orchestrator.md` / `orchestrator-v2.md` (Phase 2) and scaffold the extracted skill file (Phase 3, Option A) directly in `/Users/dt/projects/dev-tools/craft/agents/` and `/Users/dt/projects/dev-tools/craft/skills/`? I can do that as the next concrete step once you confirm Phase 0's `/usage` numbers actually point at the orchestrator agents.

---

## Sources

- [Manage costs effectively — Claude Code Docs](https://code.claude.com/docs/en/costs)
- [Create custom subagents — Claude Code Docs](https://code.claude.com/docs/en/sub-agents)
- [Orchestrate subagents at scale with dynamic workflows — Claude Code Docs](https://code.claude.com/docs/en/workflows)
- [Explore the context window — Claude Code Docs](https://code.claude.com/docs/en/context-window)
- [Extend Claude with skills — Claude Code Docs](https://code.claude.com/docs/en/skills)
- [How Claude remembers your project — Claude Code Docs](https://code.claude.com/docs/en/memory)
- [Why Claude Code Subagents Burn So Many Tokens — youcanbuildthings.com](https://youcanbuildthings.com/articles/claude-code-subagents-token-usage/)
- [7 Practical Ways to Reduce Claude Code Token Usage — KDnuggets](https://www.kdnuggets.com/7-practical-ways-to-reduce-claude-code-token-usage)
- [Reduce Claude Code Costs 60% — systemprompt.io](https://systemprompt.io/guides/claude-code-cost-optimisation)
- [Claude Code Skills vs Plugins — MindStudio](https://www.mindstudio.ai/blog/claude-code-skills-vs-plugins-difference)
