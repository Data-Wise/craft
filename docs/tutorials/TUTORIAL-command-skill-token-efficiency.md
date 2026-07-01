# Tutorial: command-skill-token-efficiency — Keep Commands Lean

By the end of this tutorial you will have:

- Understood why command/agent file size matters for token cost, and why skill content doesn't
- Walked through a real before/after split (`/refine`, 630 → 42 lines) as a worked example
- Run the quantitative `--pair` check on your own command/skill split
- Verified a split is safe with the full test suite, not a sampled one

**Prerequisites:** craft installed, working inside the `craft` repo (this skill's quantitative check and further-reading links are craft-specific — see the note at the end for using it elsewhere).

This skill has no backing command — it auto-triggers when you're writing, editing, resizing, or reviewing a `commands/**/*.md`, `skills/**/SKILL.md`, or `agents/*.md` file. This tutorial walks the same steps the skill prompts for, by hand, so you can see what it's checking and why.

---

## Step 1: Recognize when it applies

The trigger isn't "any command file" — it's specifically when a command or agent file has grown large, or you're deciding where new logic should live. A short, focused command is already fine; this matters when:

- A command file has crept past a few hundred lines
- You're about to add a `deprecated: true` / `replaced-by:` pair (the ADR-002 thin-shim pattern)
- You're unsure whether new logic belongs in the command itself or in a skill it could delegate to

## Step 2: Classify the content

Sort what's in (or going into) the command file into two buckets:

**Stays in the command** — invocation-specific content that has to be present even before any skill-routing fires: flag parsing, `deprecated:`/`replaced-by:` frontmatter, argument hints.

**Belongs in a skill** — procedure: the actual step-by-step logic, detailed reference material, edge-case handling. This is the content that costs nothing when it's *not* relevant, because skills load conditionally on trigger-match, while commands load in full every time they're invoked.

**Worked example — `commands/workflow/refine.md`:** before `feature/token-usage-reduction` ([PR #232](https://github.com/Data-Wise/craft/pull/232)), this command was 630 lines — the full `--refine` procedure lived directly in the command file. The procedure (how to sharpen a prompt, the before/after/accept-edit-use-original flow) is the same regardless of which command invokes `--refine`, so it moved to `skills/workflow/prompt-refiner/SKILL.md`. What stayed: the flag documentation itself, since the command always runs whether or not the skill's routing has fired yet. Result: 630 → 42 lines, a thin shim pointing at the skill.

A quick test for whether a split is right: if you deleted the skill, would the command still read sensibly as "this does X, see SKILL.md for how"? If the command can't be described without re-explaining the procedure, the procedure hasn't actually moved.

## Step 3: Extract, don't delete

When moving content out of a command/agent file, move it verbatim into the skill (or a `references/*.md` under it) — don't compress or summarize on the way. A token-reduction edit that silently drops capability is a regression wearing a smaller line count. If you're unsure whether something is safe to shorten, relocate it as-is first; compress later once you've confirmed nothing depended on the exact wording.

## Step 4: Run the quantitative check

```bash
python3 scripts/audit-deprecated-commands.py --pair commands/workflow/refine.md skills/workflow/prompt-refiner/SKILL.md
```

```text
skills/workflow/prompt-refiner/SKILL.md: 60 lines
commands/workflow/refine.md: 42 lines
ratio: 1.4  [OK, threshold=2.0]
```

`--pair` takes any two files and reports the line-count ratio (larger ÷ smaller), flagging it above the threshold (default 2.0). It doesn't require `deprecated: true`/`replaced-by:` frontmatter to already be set, so it's usable mid-split — run it against your draft skill before the frontmatter is even finalized.

There's also a repo-wide sweep for periodic audits (not authoring-time, since it depends on `replaced-by:` already pointing at the right place):

```bash
python3 scripts/audit-deprecated-commands.py --threshold 2.0
```

Both modes are WARN-only — exit 1 on a flag, never a hard block (ADR-003's advisory-not-hard-gate precedent). A high ratio is a prompt to look closer, not an automatic failure.

## Step 5: Verify with the full suite — the step that's easy to skip

This is the step the skill exists to enforce, because skipping it is exactly what went wrong the first time. The `/brainstorm` redesign on this same branch shipped with three real regressions that a scoped check — the 2 files most obviously touched — completely missed:

- A new skill's description quoted a phrase another skill already claimed as a trigger (`test_skill_trigger_phrases_unique`)
- The redesign dropped a documentation section that sibling commands all carry verbatim (`test_refine_flag_documented`)
- Extracting a section out of an agent file dropped a literal string a test asserts must exist in that agent file (`test_behavior_9_timeline`)

None of these are logic bugs a targeted test would catch — they're about *missing* documented behavior, which only surfaces when something checks for its absence. Before calling a split done:

```bash
python3 -m pytest tests/          # full suite, not a file subset
```

Chunk it if your environment has a short tool timeout, but run all of it — not the handful of tests nearest your edit.

## Step 6: Check trigger-phrase collisions

If you wrote or edited a skill description, grep both descriptions for shared quoted strings — a fast manual check before trusting the test suite's authoritative `test_skill_trigger_phrases_unique`:

```bash
grep -o '"[^"]*"' skills/your-area/your-skill/SKILL.md
grep -o '"[^"]*"' skills/your-area/sibling-skill/SKILL.md
```

If both lists share a phrase, one skill's description is probably quoting an example that the other has already claimed as a real trigger — rephrase to paraphrase instead of quoting.

---

## Using this skill outside craft

The classification logic in Steps 2–3 and the full-suite-verification discipline in Step 5 generalize to any Claude Code plugin with a commands/skills split. The quantitative check in Step 4 (`scripts/audit-deprecated-commands.py`) and the cross-references in the skill's "Further reading" section are craft-specific — they assume this repo's file layout. Outside craft, apply the same `bigger_file_lines / smaller_file_lines` ratio by hand, or port the script.

## See also

- [Token Efficiency](../internal/TOKEN-EFFICIENCY-craft.md) — the full implementation record this tutorial draws its worked example from
- `docs/specs/SPEC-token-efficiency-research-2026-06-30.md` (in the repo, not published to this site) — the research report behind the methodology
- [ADR-002](../adr/ADR-002-done-command-skill-consolidation.md) — the original instance of the thin-shim pattern (`/done`)
