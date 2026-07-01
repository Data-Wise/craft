# Research Report: Token Efficiency in Claude Code Plugins (Craft Case Study)

**Status:** COMPLETE (research) / branch IMPLEMENTED, PR #232 open · **Date:** 2026-06-30 · **Driver:** Cowork session, originally triggered by observing subagent calls dominating token usage
**Companion docs:** [`docs/internal/TOKEN-EFFICIENCY-craft.md`](../internal/TOKEN-EFFICIENCY-craft.md) (what we did, implementation record) · [`SPEC-craft-audit-and-next-steps-2026-06-30.md`](SPEC-craft-audit-and-next-steps-2026-06-30.md) (broader audit + roadmap)

---

## 1. The question this started from

Token usage in this Cowork session was visibly dominated by subagent (orchestrator) calls. The standing question was binary: **abandon the craft plugin architecture for native skills/dynamic workflows, or keep craft and fix the token cost within it?**

This report documents the research that answered that question, the methodology applied to fix what was fixable, and what's quantifiably true now versus what's still a hypothesis pending production validation.

## 2. Research sources and findings

### 2.1 How Claude Code loads context (official + community)

Three structural facts drove every decision in this work:

1. **Command/agent files load in full, unconditionally, whenever invoked.** There is no partial-loading or lazy-evaluation of a command's markdown body — a 1473-line agent file costs the same context whether the turn exercises 50 lines of its logic or all of it. This is a property of how Claude Code resolves `commands/*.md` and `agents/*.md`, not a craft-specific behavior.
2. **Skills load conditionally, on trigger-phrase match.** This is the structural lever the thin-command/fat-skill pattern exploits: content inside a `SKILL.md` only enters context when the skill's description matches the conversation, not on every invocation of a command that might delegate to it.
3. **Subagent spawns inherit the caller's model tier unless overridden.** A `model:` frontmatter field on an agent definition pins it; without one, cost scales with whatever tier the parent context is running at — which in an interactive session is often the most capable (most expensive) tier available, even for agents doing comparatively mechanical work (dispatch, status aggregation, string matching).

None of these three are unique to craft — they're true of any Claude Code plugin or command/agent/skill structure. This is why the recommendation (below) was "fix craft," not "abandon craft for something structurally different" — the same three facts would apply to a hand-rolled native-skill replacement too.

### 2.2 Extended thinking / "ultrathink" cost

Investigated as a candidate token sink. Finding: extended-thinking tokens are a separate, bounded budget from the visible-prompt budget the rest of this work addressed — relevant to a different optimization (how much an agent reasons before acting) rather than the one this branch targeted (how much always-loaded prompt text exists regardless of whether the agent reasons at all). Not pursued further in this branch; flagged as a separate lever if subagent reasoning depth becomes the binding constraint after this branch's fixes land.

### 2.3 Plugin architecture vs. native dynamic workflows

The original framing question. Researched both the official Claude Code plugin documentation and community discussion of plugin-vs-native tradeoffs. Finding, in short: a plugin's command/skill/agent files are not inherently more expensive than the equivalent logic expressed as inline session instructions or native dynamic workflows — the cost is a property of *how much gets loaded unconditionally*, which is a design choice within the plugin (command-file bulk, missing model pins), not an inherent property of "being a plugin." **Recommendation at the time: do not abandon craft.** This branch is the follow-through on that recommendation — proving it by fixing the actual cost drivers rather than re-architecting around them.

## 3. Methodology applied

Four-phase approach, applied to each token-cost candidate found:

1. **Locate the always-loaded bulk.** Audited every command and agent file craft loads in a typical orchestrate-heavy session for size, independent of whether the content inside is conditionally relevant. `/refine` (630 lines), `/brainstorm` (528 lines), and `orchestrator-v2.md` (1473 lines) were the three largest unconditionally-loaded files in the orchestration path.
2. **Classify content as procedure (move-able) vs. invocation-specific (must stay).** Procedure — the actual step-by-step logic of what `/refine` or `/brainstorm` does — can move to a skill, which loads conditionally. Invocation-specific content — flag parsing, the literal `--refine`/`--no-refine` block four sibling commands need verbatim regardless of skill-routing — has to stay in the command file, because the command always runs even when the skill it delegates to might not yet have triggered.
3. **Extract, don't delete.** Every line removed from a command/agent file was moved into a skill (`skills/orchestrator-resilience/SKILL.md`, the split `skills/workflow/brainstorm/SKILL.md`), never just cut. This is a deliberate methodological choice: token-reduction work that silently drops capability isn't a win, it's a regression wearing a smaller line count.
4. **Verify against the full test suite, not a sampled subset.** The first verification pass checked the 2 files most directly touched and called it done. A later, explicitly-requested full run of the ~2056-test suite caught three real regressions the sampled check had missed entirely (`test_skill_trigger_phrases_unique`, `test_refine_flag_documented`, `test_behavior_9_timeline` — see §4 below). **This is the single most important methodological finding in this report**: a token-reduction edit that touches always-loaded prompt text is exactly the kind of change a sampled test pass will under-cover, because the regressions it introduces are about *missing* documented behavior (a dropped section, a dropped string a test checks for), not about logic errors a targeted test would naturally hit.

## 4. What broke, and why it matters methodologically

Three real regressions shipped silently in the redesign commit, invisible until the full suite ran:

| Regression | Root cause | Generalizable lesson |
|---|---|---|
| `test_skill_trigger_phrases_unique` | New skill's description quoted a phrase already claimed as a trigger by a sibling skill | Extracting content into a new skill can accidentally create trigger-phrase collisions with existing skills — not visible without running the full skill-description test sweep |
| `test_refine_flag_documented` | Thin-shim redesign dropped a literal section 4 sibling commands all carry verbatim | Bulk-reduction work that touches one command in a family of similarly-structured commands needs a cross-command consistency check, not just a self-check |
| `test_behavior_9_timeline` | Extracting a BEHAVIOR section out of an agent file into a skill dropped a literal string a test asserts must exist in the *agent file itself* | Extraction can violate an implicit "this string must exist in file X" contract that isn't documented anywhere except a test assertion |

All three are now fixed (commit `81750e05`). The methodological takeaway, generalized beyond this branch: **any thin-command/fat-skill extraction needs a full-suite verification pass before merge, not a scoped one** — the failure modes are specifically the kind that scoped testing misses (missing documented strings, cross-file consistency, trigger-phrase collisions), not the kind scoped testing is good at catching (logic bugs in the touched function).

## 5. Quantified results

| Metric | Before | After | Change |
|---|---:|---:|---:|
| `/refine` command file | 630 lines | 42 lines | −93% |
| `/brainstorm` command file | 528 lines | 112 lines | −79% |
| `orchestrator-v2.md` agent file | 1473 lines | 1212 lines | −18% |
| Combined always-loaded total (3 files above) | 2631 lines | 1366 lines | **−48%** |
| Orchestrator agents with explicit model pin | 0 | 2 (`sonnet`, `haiku`) | new lever, not yet in the line-count number |

**What this number does and doesn't mean:** a 48% reduction in always-loaded line count for the orchestration path is a structural, measured fact — it's a `wc -l` diff, not an estimate. It is **not** the same claim as "session token usage will drop 48%." Line count and token count correlate but aren't identical (markdown formatting, repeated phrases, and code blocks tokenize differently), and the always-loaded path is only part of total session cost — subagent dispatch volume and reasoning depth (extended thinking) are separate, unaddressed levers. **The honest claim this report supports: a measured 48% reduction in unconditionally-loaded prompt bulk for the three largest files in the orchestration path, plus model-tier routing now in place for both orchestrator agents.** The token-usage hypothesis this branch was built to test should be validated against real `/usage` data over the next week or two of actual sessions post-merge — that validation has not yet happened, because the branch isn't merged yet.

## 6. Generalizing beyond this branch: the deprecated-command audit

This branch's methodology — find always-loaded bulk that should be a skill instead — generalizes to a repo-wide question: are there other commands that *claim* to be thin shims (`deprecated: true` + a `replaced-by:` skill pointer) but have actually grown back into something bulkier than the skill they're supposed to defer to? `scripts/audit-deprecated-commands.py` (committed this branch) answers this mechanically:

```bash
python3 scripts/audit-deprecated-commands.py --threshold 2.0
```

Full results are in `SPEC-craft-audit-and-next-steps-2026-06-30.md`. Headline: 18 of 56 deprecated commands exceed a 2:1 body-to-skill ratio; `commands/check.md` is worst at 8.9:1 (1132 lines vs. a 127-line skill); `skills/dev/git/` is the consolidation target for six commands totaling 4185 source lines. None of these 18 have been fixed yet — flagged, tracked in issue #233, not executed this round.

## 7. Should we build a dedicated token-saving skill?

Asked directly: should there be a separate skill (or two — one for general devops token-saving, one specifically for writing commands/skills/designs with token efficiency in mind)?

**Recommendation: build one skill, scoped to command/skill/agent authoring — not two, and not a general "devops token-saving" skill.**

Reasoning:

**Why not a general devops token-saving skill.** "Token saving" as a general devops concern is too broad and too context-dependent to productize as a single skill. The actual levers — extended-thinking budget, subagent dispatch count, model selection per task, context-window management across a long session — are different problems with different fixes, most of which are already owned by existing craft surfaces (`/craft:orchestrate`'s `--swarm` level control, the existing model-routing convention now established on `agents/orchestrator-v2.md`/`agents/orchestrator.md`, governance's drift-prevention checks). Bundling all of that under one "save tokens" skill would either be too shallow to be useful (generic advice) or would duplicate logic that already lives closer to where it's actually enforced. There's also no clear trigger phrase for "help me save tokens in devops" that wouldn't just be a worse front-end to tools that already exist.

**Why a command/skill/design-authoring skill makes sense.** This is genuinely a recurring, well-scoped pattern with a concrete trigger condition: *someone is about to write or edit a command, skill, or agent file, and should be prompted to think about always-loaded bulk before committing to a structure.* That's:

- A clear trigger: command/skill/agent authoring or editing — easy to describe, easy to distinguish from other work.
- A concrete, transferable checklist this branch already produced: classify content as procedure (→ skill) vs. invocation-specific (→ stays in command); extract, don't delete; verify with the full test suite, not a sampled one; check for trigger-phrase collisions and cross-file string-contract dependencies before calling extraction done.
- A natural relationship to ADR-002 and the new audit script — the skill would essentially be "the methodology in §3-4 of this report, made reusable," with `scripts/audit-deprecated-commands.py` as a built-in verification step the skill can invoke.
- A real, demonstrated failure mode it would prevent: the three regressions in §4 happened specifically because there was no standing checklist forcing a full-suite verification pass before calling a thin-command extraction done.

**What I'd scope out of it, deliberately:** model-routing decisions (that's a narrower, separate concern — arguably a few sentences in `docs/internal/COMMAND-SPEC-CONVENTIONS.md` rather than a whole skill) and the count-of-record drift problem (that's a tooling/CI gap, not an authoring-time judgment call — better solved by SPEC §4.2's consolidation than by a skill nudging a human to remember to check 14 files by hand).

**Net recommendation:** one skill, scoped narrowly to "you're about to write or resize a command/skill/agent file, here's the checklist." **Built**: `skills/code/command-skill-token-efficiency/SKILL.md` — auto-triggers on command/skill/agent authoring, documents the procedure-vs-invocation-specific classification from §3, and wraps the extended `scripts/audit-deprecated-commands.py --pair <file_a> <file_b>` mode (added alongside the skill) as its quantitative check. No existing skill overlapped (checked first), so this is new, not a fold-in.

## 8. Open questions

- Does the recommended authoring-efficiency skill get built as new, or folded into an existing skill? **Checked:** no existing craft skill covers this — `find skills -iname '*standard*' -o -iname '*creat*' -o -iname '*author*'` against the repo turned up nothing that overlaps (the closest concept, skill-standards validation, audits format/frontmatter compliance, not token-cost structure). Build new if pursued — no consolidation candidate exists.
- The §6 audit (18 flagged commands) is unscheduled work — same open question as `SPEC-craft-audit-and-next-steps-2026-06-30.md` §4.4/4.5: dedicated session before v3.0.0, or folded into general maintenance?
- Real `/usage` validation of the §5 hypothesis hasn't started — recommend tracking it as a follow-up once PR #232 merges, not closing this report's loop until that data exists.

## 9. Addendum (2026-06-30): checkpoint tooling, replacing the broken trigger

The original plan for validating §5's hypothesis was to schedule an automated reminder
(`send_later`/`create_trigger`) for `.STATUS` item D (~2026-07-14). All three scheduling calls
returned HTTP 404 — confirmed via research as a known, currently-open platform issue
(`anthropics/claude-code` [#43438](https://github.com/anthropics/claude-code/issues/43438),
[#40460](https://github.com/anthropics/claude-code/issues/40460),
[#53581](https://github.com/anthropics/claude-code/issues/53581)), not session-specific — retrying
wouldn't have helped.

**Grilled before writing:** `docs/specs/GRILL-usage-checkpoint-tooling-2026-06-30.md` (5 branches).
Two real gaps caught before shipping: (1) an earlier draft proposed extending
`docs/internal/TOKEN-EFFICIENCY-craft.md` instead of this SPEC — reversed in favor of what
`.STATUS` item D already committed to; (2) the researched tool name
("Claude-Code-Usage-Monitor") is the GitHub repo name, not the installable PyPI package
(`claude-monitor`) — caught before it could ship as a broken install command.

**Replacement mechanism** — run verified commands against data that already exists, instead of
waiting for a trigger:

```
npx ccusage daily --since 2026-06-25 --until 2026-06-30   # pre-merge baseline (already exists)
npx ccusage daily --since 2026-07-01                       # post-merge (PR #232 merged 2026-07-01; run at checkpoint time)
```

`ccusage` needs no install (`npx` runs it on demand); flags (`--since`/`--until`, `YYYY-MM-DD`)
verified live against this machine's real Claude Code usage logs, which already cover the
pre-merge period — no separate baseline-capture step needed. `claude-monitor` (`uv tool install
claude-monitor`) is a separate, standing install for ongoing live-session awareness, independent
of this one checkpoint.

**`.STATUS` item D** now references these commands directly instead of an automated reminder.
Target date (~2026-07-14) and destination (this section) are unchanged — only the mechanism
changed, from "wait for a trigger to fire" to "run this command when you next pick this repo back
up."
