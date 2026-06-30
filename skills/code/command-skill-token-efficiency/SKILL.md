---
name: command-skill-token-efficiency
description: This skill should be used when the user is writing, editing, resizing, or reviewing a craft command (commands/**/*.md), skill (skills/**/SKILL.md), or agent (agents/*.md) file — including "add a new command for X", "this command is getting long", "should this be a skill instead", "make /craft:do leaner", "reduce token usage in this command", "audit command body size", or "is this skill too big". Also use it before finalizing any deprecated-true/replaced-by thin-shim split (the ADR-002 pattern). Checks whether content belongs in a command (invocation-specific — flags, frontmatter) versus a skill (procedure — the actual logic, which loads conditionally instead of every invocation), and runs a quantitative line-ratio check via scripts/audit-deprecated-commands.py --pair. Do not confuse with skill-standards' format/frontmatter compliance check (a different concern — that audits style rules, this audits token-cost structure) or guard-audit (tunes branch-guard rules, doesn't touch command/skill content).
---

# Command/Skill Token Efficiency

Helps decide where content belongs when authoring or resizing a craft command, skill, or agent file, and runs the quantitative check that backs the decision up. Grew out of `feature/token-usage-reduction` ([PR #232](https://github.com/Data-Wise/craft/pull/232)), which found and fixed real, measured token cost in `/refine` (630→42 lines), `/brainstorm` (528→112 lines), and `orchestrator-v2.md` (1473→1212 lines) — a 48% reduction in the always-loaded orchestration path. Full research and methodology: `docs/specs/SPEC-token-efficiency-research-2026-06-30.md`.

## Why this matters

Command and agent files load into context in full, every time they're invoked — regardless of which part of the file is actually relevant that turn. Skills load conditionally, only when their description matches the conversation. That single structural fact is the entire lever this skill exists to apply: content that's genuinely procedure (the step-by-step logic of what a command *does*) costs less if it lives in a skill instead of the command file, because then it only loads when needed rather than every time.

This isn't a rule to apply mechanically everywhere — a short, focused command file is already fine. The skill matters most when a command file has grown large, or when a new command is being designed and there's a real choice about where its logic should live.

## The classification: command vs. skill

When writing or reviewing a command/skill/agent file, sort its content into two buckets:

**Stays in the command file (invocation-specific):**

- Flag parsing and the documentation of those flags
- Frontmatter (`deprecated:`, `replaced-by:`, argument hints)
- Anything that has to be present even if skill-routing hasn't fired yet — the command always runs; the skill it might delegate to is conditional

**Belongs in a skill (procedure):**

- The actual step-by-step logic of what happens
- Detailed reference material, examples, edge-case handling
- Anything that's the same regardless of which command or context triggered it (shared logic worth a `references/*.md`)

A useful test: if you deleted the skill, would the command still make sense as a "this does X, see SKILL.md for how" pointer? If yes, the split is probably right. If the command can't be described without re-explaining the procedure, the procedure hasn't actually moved.

## Extract, don't delete

When moving content from a command/agent file into a skill, move it — don't summarize it away. A token-reduction edit that silently drops capability isn't a win, it's a regression wearing a smaller line count. If you're unsure whether something is safe to compress rather than relocate, relocate it; compression can happen later once it's confirmed nothing depends on the exact wording.

## The quantitative check

`scripts/audit-deprecated-commands.py` has two modes. Use `--pair` at authoring time, on the specific file(s) you just touched:

```bash
python3 scripts/audit-deprecated-commands.py --pair commands/workflow/your-command.md skills/your-area/your-skill/SKILL.md
```

This reports the line-count ratio between the two files (larger ÷ smaller) and flags it if it exceeds the threshold (default 2.0 — a command file more than twice the size of the skill it's supposed to defer to is worth a second look). It works on any two files, not just ones with `deprecated: true`/`replaced-by:` frontmatter already set, so it's useful while a split is still in progress, not just as a final gate.

The repo-wide sweep (no `--pair` flag) scans every `deprecated: true` command against its `replaced-by:` skill — useful for periodic audits, not authoring-time, since it depends on that frontmatter already being correct:

```bash
python3 scripts/audit-deprecated-commands.py --threshold 2.0
```

Both modes are WARN-only (exit 1 on a flag, never blocking) — see ADR-003's advisory-not-hard-gate precedent. A high ratio is a prompt to look closer, not an automatic failure.

## Before calling a split done: verify with the full suite, not a sample

This is the most important thing this skill exists to enforce, because it's the lesson that cost real time on `feature/token-usage-reduction`. A thin-command/fat-skill extraction shipped with three real regressions that a scoped check (the 2 files most obviously touched) completely missed:

- A new skill's description quoted a phrase already claimed as a trigger by a sibling skill (`test_skill_trigger_phrases_unique`)
- The redesign dropped a literal documentation section that sibling commands all carry verbatim (`test_refine_flag_documented`)
- Extracting a section out of an agent file dropped a literal string a test asserts must exist in the agent file itself (`test_behavior_9_timeline`)

None of these are logic bugs a targeted test would catch — they're about *missing* documented behavior, which only shows up when something checks for its absence. That's specifically what a full-suite run catches and a scoped one doesn't. Before treating a command/skill split as finished:

1. Run `python3 -m pytest tests/` (the full suite, not a file subset) — chunk it if the environment has a short tool timeout, but run all of it.
2. Check for trigger-phrase collisions: does the new or edited skill's description quote a phrase another skill already claims? (`grep` both descriptions for shared quoted strings is a fast manual check; the test suite's skill-trigger-uniqueness test is the authoritative one.)
3. If the split touches one command in a family of similarly-structured commands (e.g., several commands that all share a `--refine`/`--no-refine` block), check the siblings weren't supposed to keep something this one dropped.
4. Run `python3 scripts/audit-deprecated-commands.py --pair <command> <skill>` as the final quantitative sanity check.

## Model routing (a separate, smaller lever)

Distinct from the prompt-bulk question above: agent files (`agents/*.md`) can carry a `model:` frontmatter field to pin which model tier a subagent spawns at. Without one, a spawned agent inherits whatever tier the calling context is running at — which for a lightweight coordination agent (dispatch, status aggregation) is often more expensive than necessary. If you're authoring or reviewing an agent file, check whether it has an explicit `model:` pin and whether the tier matches the agent's actual workload (heavier synthesis work warrants a stronger model; mechanical dispatch usually doesn't).

## Further reading

- `docs/specs/SPEC-token-efficiency-research-2026-06-30.md` — full research report: the structural facts behind this skill, the methodology, and quantified results
- `docs/internal/TOKEN-EFFICIENCY-craft.md` — implementation record of what changed on `feature/token-usage-reduction`
- `docs/adr/ADR-002-done-command-skill-consolidation.md` — the original instance of this pattern (`/done`)
- `docs/specs/SPEC-craft-audit-and-next-steps-2026-06-30.md` §4.1 — the case for promoting the repo-wide sweep into a standing governance check
