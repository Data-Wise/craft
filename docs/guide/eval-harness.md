# Plugin Eval Harness

Craft ships a small eval suite for `claude plugin eval`, run through a safe wrapper. This guide
covers what the evals measure, how to run them, how to write a case, and what they cost.

## What the evals measure

| Kind | Case dir | Question it answers | Grader |
|---|---|---|---|
| **Trigger eval** (preferred) | `evals/trigger-<skill>/` | Given a natural request, does a matching craft skill or command fire? | `type: tool_used`, scored with `--single-arm` |
| **Command-routing trigger eval** | `evals/trigger-cmd-<slug>/` | Does a natural request fire the right craft *command* (11 commands that reach nested skills)? Not mapped to skills in `_coverage.json`. | `type: tool_used`, `--single-arm` |
| **Body case** | `evals/<name>/` | Does the with-plugin agent beat a no-plugin baseline on a fact reachable through the plugin? | `type: llm`, delta against the baseline |

Command-routing cases assert one exact command id, so a request meant for another command scores 0 (checked: a grill request graded against the check command scores 0).

A body-case pass means **plugin-level delta**, not proof that one skill's body was read. A trigger
pass means "something relevant fired", because each regex accepts the skill id or a related command id.

Only the 11 top-level skills (`skills/<name>/SKILL.md`) are exposed to the `Skill` tool. The 30
nested skills are files that commands read by path, so they are not trigger-testable and body
cases for them cannot pass with `[Skill]` only. Details and the traces behind this are in
`tasks/plan.md` ("Finding" and "Redesign").

## Running

```bash
./scripts/run-evals.sh --dry-run                               # print the command, run nothing
./scripts/run-evals.sh --single-arm --case 'trigger-*' --record # trigger evals, one run each
./scripts/run-evals.sh --tier full                              # 3 runs per case
```

The wrapper always passes `--no-publish` (the eval publishes its report to claude.ai by default),
a `--max-cost-usd` cap (default 5), and a private output directory outside the repo. It does not
pass `--trust-plugin` unless you give `--trust`. `--record` updates `evals/_coverage.json` from a
complete result and never from a partial one.

!!! warning "Every run bills your credential"
    Measured on 2026-10-03: about $0.13 per single-arm trigger run and about $0.22 per two-arm
    body-case run. The 11 trigger cases cost $1.41 for one run each. Runs share one rate limit.

## Writing a case

1. **Trigger case:** write a request a user would actually type, then a `tool_used` grader with
   `input_match: '"skill"\s*:\s*"craft:(<skill>|<related-command>)"'`.
2. **Body case:** ask about a fact that exists only where the plugin provides it, keep
   `allowed_tools: [Skill]`, and grade the primary claim. Avoid "must not name another X" clauses.
3. Run it once, then check the grader can fail (a negative control: an unrelated prompt should score 0).
4. `--record`, then run `tests/test_eval_suite_structure.py`.

## Tests and limits

- `tests/test_eval_suite_structure.py` checks case structure and `_coverage.json` (no cost).
- `tests/test_run_evals_wrapper.sh` checks the wrapper's safety flags with a stub `claude`.
- Live evals are run on demand, not in CI. Results are never committed (`evals/results/` is ignored).
- `evals/` ships with the plugin: the marketplace source is the whole repo and the Homebrew
  formula installs everything into `libexec`.
