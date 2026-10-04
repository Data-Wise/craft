# TODO: Craft Eval Harness

Plan: [`plan.md`](plan.md). Branch `feature/plugin-eval-spike`. Sizes: XS/S/M (no task >5 files; a "case" is one `evals/<name>/` dir).
Every task: run the wrapper (once it exists) with `--runs 1` to confirm each new case passes with-plugin; a case that also passes the baseline is marked `non-discriminating` in the ledger.

## Phase 0 — Decisions (human)
- [x] D1: Approve plan, tiers and cost model; answer plan.md Open Questions 1-4.
  - Acceptance: budget, results location, packaging stance and spec-first decision recorded in plan.md (done: defaults applied 2026-10-03).

## Phase 1 — Harness foundation
- [x] T0 (XS, read-only, from GRILL B4): check validators and packaging against a top-level `evals/` dir.
  - Acceptance: finding recorded in plan.md for `test_plugin_dogfood.py`, `validate-counts.sh`, `marketplace.json`, formula generator; validators run with the 3 spike cases present.
  - Verify: `./scripts/validate-counts.sh` and the dogfood tests, results quoted.
- [ ] T1 (S): `scripts/run-evals.sh` wrapper (adds `--record`, GRILL B3).
  - Acceptance: always passes `--no-publish`; does not pass `--trust-plugin` unless the caller sets `--trust` (trust prompt is a user decision), `--max-cost-usd` (default 5), `--output-dir` outside the tree; flags `--tier`, `--case`, `--runs`; refuses to run without `claude` on PATH; `--dry-run` prints the command.
  - Verify: `bash scripts/run-evals.sh --dry-run --tier smoke` shows all safety flags; bash test asserts `--no-publish` present.
  - Files: `scripts/run-evals.sh`, `tests/test_run_evals_wrapper.sh`.
- [ ] T2 (M): structural test + coverage ledger.
  - Acceptance: pytest checks every `evals/*/prompt.md` has frontmatter `allowed_tools: [Skill]`, ≥1 grader with `type: llm`, valid grader frontmatter; coverage file `evals/_coverage.json` (GRILL B3, written by `run-evals.sh --record`: skill, case, delta, runs, claudeVersion, date) is schema-validated and every referenced case dir exists; a skill counts as covered only with delta >= 1 (GRILL B2).
  - Verify: `python3 -m pytest tests/test_eval_suite_structure.py`; planted defect (case with `Read` tool) is caught.
  - Files: `tests/test_eval_suite_structure.py`, `evals/_coverage.json`.
- [ ] T3 (XS): ignore results; conventions.
  - Acceptance: `evals/results/` gitignored; `evals/README.md` states layout, `[Skill]`-only rule, grader checklist (no negative clauses that reject correct secondary mentions), cost table.
  - Files: `.gitignore`, `evals/README.md`.
- [ ] T4 (S): resolve the spike's open defects.
  - Acceptance: `release-skill-trigger` rewritten so baseline scores 0 and with-plugin 1; root cause of `skill-invoked` "0x" explained (read the run trace at the `tracePath` in the JSON) and either fixed or the `tool_used` graders removed.
  - Verify: one wrapper run on the 3 spike cases, delta ≥1 on each.
  - Files: `evals/release-skill-trigger/*`, `evals/*/graders/skill-invoked.md`, `tasks/plan.md` (finding).
- [ ] T5 (XS): document that `evals/` ships (T0: marketplace = whole repo; Homebrew installs `Dir["*"]`).
  - Acceptance: stated in `evals/README.md` and the guide page; no packaging change.
  - Files: `evals/README.md`.

### Checkpoint 1 — foundation
- [ ] `python3 -m pytest tests/` green (report counts); wrapper dry-run OK; 3 spike cases discriminate; human review.

## Phase 2 — Tier 1 (blast-radius skills)
- [ ] T6 (M): cases for guard-audit, hooks, dev/git.
- [ ] T7 (S): cases for ci, insights-apply.
  - Acceptance (both): each case's prompt needs a skill-only fact; grader checks that fact; no case can cause side effects (tools are `[Skill]` only).
  - Verify: wrapper `--case <name> --runs 1`; ledger shrinks.
### Checkpoint 2
- [ ] Tier 1 at `--runs 3`, pass rate ≥ 2/3 per case; cost recorded in plan.md against the estimate.

## Phase 3 — Tier 2 (orchestration + workflow)
- [ ] T8 (M): drive-engine, plan-orchestrator, repo-triage.
- [ ] T9 (M): session-state, task-analyzer, workflow-engine.
- [ ] T10 (M): adhd-workflow, brainstorm, brainstorm-insights.
- [ ] T11 (M): grill, prompt-refiner, task-management.
- [ ] T12 (S): orchestrator-resilience, planning.
### Checkpoint 3
- [ ] Structural test + ledger green; smoke run over tiers 1-2 within budget.

## Phase 4 — Tier 3 (remaining)
- [ ] T13 (M): architecture, code, audit-router.
- [ ] T14 (M): command-skill-token-efficiency, plugin-audit, backend-designer.
- [ ] T15 (M): devops-helper, frontend-designer, dist-extras.
- [ ] T16 (M): distribution-strategist, homebrew-formula-expert, homebrew-multi-formula.
- [ ] T17 (M): homebrew-setup-wizard, homebrew-workflow-expert, architecture-decision-records.
- [ ] T18 (M): changelog-automation, claude-md, test-generator.
- [ ] T19 (XS): test-strategist.
### Checkpoint 4
- [ ] Ledger empty (41/41 skills have a case); full smoke run recorded (cost, pass rate, non-discriminating list).

## Phase 5 — Documentation + release prep
- [ ] T20 (S): `docs/guide/eval-harness.md` + `mkdocs.yml` nav; `mkdocs build` clean.
- [ ] T21 (S): CLAUDE.md Quick Commands row; `/craft:test` docs mention; run `/folio:docs:lint` and `./scripts/validate-counts.sh`.
- [ ] T22 (S): CHANGELOG (root + `docs/CHANGELOG.md` mirror, diff both), `.STATUS`, memory note on eval gotchas (publishing default, `[Skill]`-only, strict graders).
- [ ] T23 (S): pre-PR gate: full `python3 -m pytest tests/` in the worktree with counts; E2E transcript of one live wrapper run quoted in the PR body (per `e2e-before-pr`).
### Checkpoint 5
- [ ] All acceptance criteria met; human review before any push or PR.
