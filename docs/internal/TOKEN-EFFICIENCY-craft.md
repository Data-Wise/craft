# Token Efficiency: What We Did to Craft

What changed on `feature/token-usage-reduction` ([PR #232](https://github.com/Data-Wise/craft/pull/232)), why, and the measured before/after. This is the implementation record; the methodology and decision framework behind it live in
`docs/specs/SPEC-token-efficiency-research-2026-06-30.md` (in the repo; specs aren't published to this site, see `mkdocs.yml`'s `exclude_docs`).

## The problem

Subagent calls (orchestrator agents, brainstorm's old delegation path) were burning a disproportionate share of session tokens relative to their value. Two root causes, both structural rather than one-off:

1. **Always-loaded prompt bulk.** Command and agent files are loaded into context whenever the command runs or the agent spawns — regardless of which branch of the prompt actually executes that turn. A 1473-line agent file costs the same whether 50 lines or 1400 lines of it were relevant this turn.
2. **No model routing.** Every orchestrator agent spawned at the caller's model tier by default. A lightweight coordination agent doing string-matching and dispatch doesn't need the same model as one doing synthesis.

## What changed, file by file

| File | Before | After | Δ |
|---|---:|---:|---:|
| `commands/workflow/refine.md` | 630 lines | 42 lines | **−93%** |
| `commands/workflow/brainstorm.md` | 528 lines | 112 lines | **−79%** |
| `agents/orchestrator-v2.md` | 1473 lines | 1212 lines | −18% |
| `skills/workflow/brainstorm-insights/SKILL.md` | 236 lines | 170 lines | −28% |

New files added (content moved here, not duplicated):

| File | Lines | What moved here |
|---|---:|---|
| `skills/orchestrator-resilience/SKILL.md` | 278 | BEHAVIOR 5 (error handling) + BEHAVIOR 9 (timeline) templates, extracted from `orchestrator-v2.md` |
| `skills/workflow/brainstorm/SKILL.md` | 160 | Ideation logic, split out of the old combined `brainstorm-insights` skill |
| `scripts/audit-deprecated-commands.py` | 104 | New tooling (see "Generalizing the pattern" below) |

**Net effect on the always-loaded path** (`/refine` + `/brainstorm` + `orchestrator-v2`, the three files a typical orchestrate-heavy session loads regardless of which skill ends up triggering): **2631 → 1366 lines, a 48% reduction.** The line count didn't vanish — most of it moved into skills, which load on-demand instead of unconditionally.

## The pattern: thin command, fat skill

This is **ADR-002's pattern, generalized.** ADR-002 originally fixed `/done` (consolidated into the `adhd-workflow` skill, command reduced to a thin shim with a `replaced-by:` pointer). This branch applies the same shape to `/refine` and `/brainstorm`:

- The **command file** becomes a thin shim: frontmatter, a one-paragraph "what this does," and a pointer to the skill that owns the actual procedure.
- The **skill** (`SKILL.md` + `references/*.md`) owns the canonical, detailed logic. Skills load into context only when their trigger conditions match the conversation — not on every command invocation.
- Anything genuinely command-specific (flag parsing, the literal `--refine`/`--no-refine` documentation block that 4 sibling commands all need verbatim) stays in the command file, because skill-routing can't be assumed to fire before the command itself runs.

The risk this pattern creates — a thin command silently drifting out of sync with the skill it points to — is exactly what generated two of the three real test regressions caught during this branch's verification pass (see the SPEC for the regression details). The fix isn't "don't use the pattern," it's "verify it with the full test suite before merging," which is now a standing recommendation, not a one-off.

## Model routing

`agents/orchestrator-v2.md` and `agents/orchestrator.md` had no `model:` frontmatter before this branch — both ran at whatever model the calling context used. Added:

```yaml
# agents/orchestrator-v2.md
model: sonnet

# agents/orchestrator.md
model: haiku
```

`orchestrator.md` is the lighter-weight coordination agent (dispatch, status aggregation); `orchestrator-v2.md` does heavier synthesis work and stays on sonnet. This is a per-agent cost lever independent of the prompt-size reduction above — it doesn't shrink what's loaded, it changes what tier processes it.

## Why extraction, not deletion

Every line removed from a command or agent file in this branch is still in the repo — moved to a skill, not cut. This matters for two reasons:

1. **Nothing was silently lost.** The full pytest suite (~2056 tests) was run against the branch specifically to catch content that the move dropped by accident (it caught three: see the SPEC).
2. **The content still loads when it's actually needed** — skills activate on trigger-phrase match, so a session that genuinely needs BEHAVIOR 9's timeline template still gets it, just not on every orchestrator invocation.

## Generalizing the pattern: the deprecated-command audit

While fixing `/refine` and `/brainstorm`, a broader question came up: how many other commands have this same shape — a `deprecated: true` command with a `replaced-by:` skill pointer, where the command's body has silently grown larger than the skill it's supposed to defer to? `scripts/audit-deprecated-commands.py` answers this for the whole repo:

```bash
python3 scripts/audit-deprecated-commands.py --threshold 2.0
```

It scans every `commands/**/*.md` with `deprecated: true`, finds its `replaced-by:` skill, and computes `command_lines / skill_lines`. Top of the list at threshold 2.0 (18 commands flagged):

| Command | Lines | Skill lines | Ratio |
|---|---:|---:|---:|
| `commands/check.md` | 1132 | 127 | **8.9** |
| `commands/workflow/task-cancel.md` | 508 | 90 | 5.6 |
| `commands/git/worktree.md` | 1010 | 250 | 4.0 |

`skills/dev/git/` (250 lines) is the `replaced-by:` target for six commands totaling 4185 source lines — the single highest-leverage consolidation target in the repo, not yet executed (tracked in [issue #233](https://github.com/Data-Wise/craft/issues/233)).

## What this doesn't fix

This branch addresses always-loaded prompt bulk and model routing. It does **not** address:

- **Per-call subagent dispatch volume** — how many subagent calls a given orchestrate run makes is a separate lever from how big each one's prompt is.
- **The 18 other oversized deprecated commands** the audit found — flagged, not fixed, this round.
- **Count-of-record drift tooling** — the skill-count drift this branch found (40 documented vs. 42 actual) was fixed by hand across 14+ files; there's still no single check that would have caught it automatically before this session ran the full doc-staleness sweep.

See the SPEC's §4 (Candidate next steps) for the prioritized list.

## Standing tooling: the authoring-time skill

The methodology in this doc — classify content as command-specific vs. skill-procedure, extract rather than delete, verify with the full suite — is now codified as a craft skill: `skills/code/command-skill-token-efficiency/SKILL.md`. It auto-triggers when writing or resizing a command/skill/agent file, and wraps `scripts/audit-deprecated-commands.py --pair <file_a> <file_b>` as its quantitative check. See `docs/specs/SPEC-token-efficiency-research-2026-06-30.md` §7 for the reasoning behind scoping it this narrowly (and why a broader "devops token-saving" skill wasn't built).
