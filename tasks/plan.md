# Implementation Plan: Craft Eval Harness (`claude plugin eval`)

Branch: `feature/plugin-eval-spike` (worktree `~/.git-worktrees/craft/feature-plugin-eval-spike`).
Task list: `tasks/todo-eval-harness.md` (the existing `tasks/todo.md` is the finished #316 list and was left untouched).
Status: APPROVED 2026-10-03 (user: "approve the plan"). Open-question defaults below were applied, not separately answered. No spec exists; this plan is the spec of record until one is written.

## Overview
Scale the 3-case spike (`evals/modes-lookup`, `preflight-check-scope`, `release-skill-trigger`, commit
`9845eeaff`) into a repeatable eval harness covering all 41 skills (`find skills -name SKILL.md` = 41),
with safe-by-default tooling (a pass means plugin-level delta, not per-skill proof — GRILL B1), a structural test that stops coverage from regressing, and documentation.

## What the spike established (evidence, 2026-10-03)
- Case layout: `evals/<case>/prompt.md` + `evals/<case>/graders/*.md` (`type: llm` | `type: tool_used`).
- Cost: ~$0.22 per case-run (both arms) from 3 runs / $0.67 — a single sample, treat as ±50%.
- `allowed_tools: [Skill]` is needed so the no-plugin baseline cannot read repo files
  (with `[Read, Glob, Grep, Skill]` the baseline scored 1, delta 0). 2 of 3 cases then discriminated.
- `release-skill-trigger` still does not discriminate (baseline 1) — needs a prompt about a fact only the skill holds.
- `skill-invoked` (`tool_used: Skill`) reported "called 0x" on two passing cases; meaning unresolved.
- `claude plugin eval` publishes its report to claude.ai by default; the harness must pass `--no-publish`.
- Results default to `<plugin>/evals/results/` — must not be committed.
- `plugin.json` allowlist (`tests/test_plugin_dogfood.py:399-409`) rejects `experimental`; keep the default `evals/` dir.

## Architecture Decisions
1. **Default `evals/` directory, no manifest change** — avoids touching the strict `plugin.json` allowlist.
2. **One wrapper script (`scripts/run-evals.sh`) owns safety flags**: `--no-publish`, `--max-cost-usd`, `--runs`,
   `--output-dir` outside the tree. Humans and docs call the wrapper, never the raw command.
3. **Local-only runs, not CI.** Account is in zero-CI mode and each run bills the user's credential on one shared
   rate limit. A *static* structural test runs in pytest/CI; live evals run on demand.
4. **Tag tiers** so cost is controllable: `smoke` (1 run, every skill) vs `full` (3 runs, tier 1 only).
5. **Coverage ratchet** (GRILL B2/B3): `evals/_coverage.json`, written by the wrapper from eval `--json`; a skill is covered only at delta >= 1; pytest validates schema and case dirs only.
6. **Tiering by blast radius, not by usage** (no usage data exists): skills that gate irreversible or
   safety-critical actions first.

## Skill tiers (41 = 7 + 14 + 20; spike already covers modes, preflight-check, release)
- **Tier 1 — gates irreversible/safety actions (7):** release, preflight-check, guard-audit, hooks, dev/git, ci, insights-apply
- **Tier 2 — orchestration + workflow (14):** drive-engine, plan-orchestrator, repo-triage, session-state, task-analyzer,
  workflow-engine, adhd-workflow, brainstorm, brainstorm-insights, grill, prompt-refiner, task-management,
  orchestrator-resilience, planning
- **Tier 3 — everything else (20):** architecture, code, audit-router, command-skill-token-efficiency, plugin-audit,
  backend-designer, devops-helper, frontend-designer, dist-extras, distribution-strategist, homebrew-formula-expert,
  homebrew-multi-formula, homebrew-setup-wizard, homebrew-workflow-expert, architecture-decision-records,
  changelog-automation, claude-md, modes, test-generator, test-strategist

## Grill decisions
See `docs/specs/GRILL-eval-harness-2026-10-03.md` (B1 pass meaning, B2 delta>0 coverage, B3 wrapper-written record, B4 T0 pre-check).

## Phases
- **Phase 0 — Decisions** (human): budget, tiers, where results are kept.
- **Phase 1 — Harness foundation:** wrapper script, structural test + ledger, gitignore + conventions, fix spike cases.
- **Phase 2 — Tier 1 cases** (7 skills; 3 already exist).
- **Phase 3 — Tier 2 cases** (14 skills).
- **Phase 4 — Tier 3 cases** (20 skills).
- **Phase 5 — Documentation + release prep.**

## Cost model (estimate, derived from one sample)
| Scope | Case-runs | ≈ Cost |
|---|---|---|
| Smoke: 1 case × 1 run × 41 skills | 41 | ~$9 |
| Full tier 1: 7 skills × 2 cases × 3 runs | 42 | ~$9 |
| Everything at 3 runs, 1 case/skill | 123 | ~$27 |
Wrapper enforces `--max-cost-usd`; default $5 per invocation.

## Risks and Mitigations
| Risk | Impact | Mitigation |
|---|---|---|
| LLM-judge flakiness (1 run is noise) | High | `full` tier uses 3 runs; grade on pass rate, not a single score |
| Over-strict graders fail correct answers (seen in spike) | Med | Grader-authoring checklist in docs; review each new grader against a real transcript |
| Baseline contamination via repo files | High | Lint: every `prompt.md` must set `allowed_tools: [Skill]` (structural test) |
| Report auto-published to claude.ai | Med | Wrapper always passes `--no-publish`; test greps the wrapper for it |
| Eval suite ships inside the plugin / Homebrew formula | Med | T-check packaging (`marketplace.json`, formula generator) before PR |
| `skill-invoked` grader unreliable | Med | Investigate (T4) before relying on it; otherwise drop `tool_used` graders |
| Spend runs away | Med | `--max-cost-usd` default in wrapper; docs state cost table |

## Open Questions (need a human)
1. Monthly eval budget? (drives `full` vs `smoke` scope)
2. Keep results anywhere durable, or scratch only? (default here: scratch, not committed)
3. Should `evals/` ship to users in the plugin package, or be excluded?
4. Write a SPEC first, or is this plan sufficient? (Repo convention: grill new specs before building.)

## Decisions applied on approval (defaults — override any)
1. Budget: ~$30 total across the project; wrapper cap $5 per invocation.
2. Results: scratch only, never committed.
3. Packaging: T0 found exclusion infeasible (see T0 finding); `evals/` ships. Default now: accept it (small text files), document it.
4. Spec: this plan serves as the spec; no separate SPEC/grill. (Your standing preference is to grill new specs — say "grill it" to run one before Phase 1.)

## Documentation deliverables
`evals/README.md` (conventions + grader checklist), `docs/guide/eval-harness.md` (+ `mkdocs.yml` nav),
CLAUDE.md Quick Commands row, CHANGELOG (root + `docs/CHANGELOG.md` mirror), `/craft:test` docs mention,
count/doc validators green, `.STATUS` update, memory note on the eval gotchas.

## T0 finding (2026-10-03, read-only)
- No test or script enumerates top-level dirs (grep found none). With the 3 spike cases present:
  `./scripts/validate-counts.sh` rc=0; `uv run --no-project --with pytest --with pyyaml --with jinja2 pytest tests/test_plugin_dogfood.py tests/test_craft_plugin.py` = 83 passed.
- Packaging: `marketplace.json` source is the whole GitHub repo, so `evals/` ships to marketplace installs; the
  Homebrew formula (`homebrew-tap/Formula/craft.rb:16`) installs `Dir["*", ".*"]` into libexec, so it ships there too.
  Excluding it would need a cross-repo tap change and has no marketplace mechanism. T5 becomes "document that evals/ ships".
- Not checked: full `tests/` suite and the bash CI suites (only the two files above).
- Note: plain `uv run` fails on this repo's `pyproject.toml` (no `project.name`); use `--no-project`.

## Finding: skill-body cases cannot pass with [Skill]-only tools (2026-10-03, Phase 2)
- 38 agent-authored cases (facts quoted from SKILL.md bodies) were authored; first 13 recorded runs: every new case
  scored 0 in BOTH arms (delta 0). Spend: $3.79 on batches a-c, plus ~$0.44 on two diagnostics.
- Trace (`--keep-temp`): with no cue, the with-plugin agent used Grep/Glob/Read on its sandbox cwd (denied) and never
  called `Skill`. With a "use the Skill tool" cue, `Skill craft:grill` resolved to the `/craft:grill` COMMAND shim
  (commands/grill.md), which only points at `${CLAUDE_PLUGIN_ROOT}/skills/workflow/grill/SKILL.md`; the body was unreachable.
- Why the 3 spike cases passed: their facts appear in text reachable without the body (descriptions/commands), not the SKILL.md body.
- Consequence: B1 holds, but per-skill *body recall* is the wrong thing to eval. Candidate redesign: trigger evals
  ("given this user request, does the right craft skill/command fire?") with `tool_used` graders, which is what the tool is built for.
- Open: batches d..w were stopped before running (no spend). 38 case dirs are uncommitted; coverage ledger holds 10 honest delta-0 records.

## Redesign (2026-10-03, user chose option 1)
- Only 11 of 41 skills (`skills/<name>/SKILL.md`) are exposed to the `Skill` tool; the 30 nested ones are files that
  commands read by path. Verified: `ls skills/*/SKILL.md` = 11, `find skills -mindepth 3 -name SKILL.md` = 30, and this
  session's skill listing shows exactly the 11 `craft:*` ids. (Inference about the loader, consistent with all traces.)
- New design: **trigger evals** = a natural user request + a scored `tool_used: Skill` grader whose `input_match` accepts the
  skill id or a related command id. Run single-arm (`--single-arm` = `--ablation none`), since with ablation `tool_used`
  is an unscored indicator. Cost ~$0.13 per case.
- Result: 11 trigger cases, 11/11 pass, $1.41, 1 run each. Negative control (capital-of-France prompt vs the release
  grader) scores 0, so the grader can fail.
- Kept: 3 body cases whose facts are reachable (modes-lookup, preflight-check-thresholds, release-autonomous-mode).
- Coverage ledger rule is now: body cases need delta >= 1; trigger cases need score 1.
- Known limits: single run each; a regex accepting a skill OR a command measures "something relevant fired", not which one.
