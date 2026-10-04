# GRILL: eval-harness

Target: `tasks/plan.md` (feature/plugin-eval-spike). Date: 2026-10-03.

## Open Questions

- (none yet)

## Decision Ledger

| # | Branch | Decision |
|---|---|---|
| B1 | What does a pass claim? (Skill fired 0x in 2/3 passing cases; tool_used:Skill is an unscored indicator) | Plugin delta: pass = with-plugin beats baseline; Skill-fired is diagnostic only; first run per tier uses --keep-temp to confirm mechanism; docs say 'plugin-level', not 'per-skill'. Plan wording '41 skills covered' to be changed. |
| B2 | Do delta-0 passing cases count as coverage? (release-skill-trigger: green, baseline 1) | Delta>0 only: a skill leaves the coverage ledger only when its case has delta>=1 on a recorded run. Baseline arm stays on. Implication: the ledger needs a recorded-delta field and the structural test can only check the ledger's format, not live deltas. |
| B3 | Where does the recorded delta behind the coverage ledger live, and who writes it? | Wrapper writes JSON: `run-evals.sh --record` writes evals/_coverage.json (skill, case, delta, runs, claudeVersion, date) from the eval --json output; pytest validates schema + case dirs exist only. Replaces evals/_coverage-ledger.txt in T1/T2. |
| B4 | When do we learn whether a top-level evals/ dir breaks a validator or ships to users? | Add read-only T0 before T1: grep dogfood tests, validate-counts.sh, marketplace.json and the formula generator for top-level-dir/packaging assumptions; run the validators with the 3 spike cases present. |
