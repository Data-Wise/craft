# Craft plugin evals

Eval cases for `claude plugin eval`. Run them through the wrapper, never the raw command:

```bash
./scripts/run-evals.sh --dry-run          # print the command, run nothing
./scripts/run-evals.sh                    # smoke: 1 run per case (~$0.22 per case, both arms)
./scripts/run-evals.sh --tier full        # 3 runs per case
./scripts/run-evals.sh --case 'modes-*' --record   # one case, update evals/_coverage.json
```

The wrapper always passes `--no-publish` (the eval publishes its report to claude.ai by
default), a `--max-cost-usd` cap (default 5) and an `--output-dir` outside the repo.
Every run bills your own credential and shares one rate limit.

## What a pass means

A pass means the with-plugin arm beats the no-plugin baseline (**plugin-level delta**), not
that one specific skill fired. The `tool_used: Skill` grader is an unscored indicator and has
reported 0 calls on passing cases. A case that passes but ties the baseline (delta 0) proves
nothing and does **not** count as coverage.

## Trigger evals (preferred for skills)

`evals/trigger-<skill>/`: a natural user request plus a `type: tool_used` grader whose `input_match` accepts the skill
id or a related command id. Run with `--single-arm` (no baseline arm), because `tool_used` graders are only scored
then. Only the 11 top-level skills (`skills/<name>/SKILL.md`) are exposed to the `Skill` tool; the 30 nested skills are
read by commands via file paths, so body-recall cases for them cannot pass with `[Skill]` only (see `tasks/plan.md`).

```bash
./scripts/run-evals.sh --single-arm --case 'trigger-*' --record
```

## Layout

```text
evals/<case>/prompt.md            # frontmatter: max_turns (1-10), allowed_tools: [Skill]
evals/<case>/graders/criteria.md  # type: llm (scored) — plus optional tool_used indicator
evals/_coverage.json              # written by run-evals.sh --record; do not hand-edit deltas
```

## Writing a case

1. Ask about a fact that exists **only in the skill** (a table cell, a rule, a threshold).
   If the baseline can answer from general knowledge or repo files, delta will be 0.
2. Keep `allowed_tools: [Skill]`. Any file tool lets the baseline read the repo and score 1.
3. The prompt must not cause side effects; with `[Skill]` only, it can't.
4. Grade the primary claim. Do not write "must not name another X" clauses: a correct answer
   that mentions a secondary option then fails (seen on `modes-lookup`).
5. Run it once with the wrapper; keep it only if delta >= 1. Then `--record`.

`tests/test_eval_suite_structure.py` enforces the structure (no cost). Live scores are not run in CI.

## Packaging

`evals/` ships with the plugin: the marketplace source is the whole GitHub repo and the
Homebrew formula installs everything into `libexec`. The files are small text; there is no exclusion.
