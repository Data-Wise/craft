# Recipe: Triage a red PR

A check just went red on your PR. Don't guess — classify it, then act.

1. `/craft:ci:triage` — triage the current branch's open PR (or `/craft:ci:triage <pr>`).
2. Read the verdict:
   - **DIFF-CAUSED** → the failure is in your changes. `/craft:code:ci-fix`, re-push.
   - **PRE-EXISTING** → error sites are outside your diff. An `--admin` merge may be
     justified — confirm it's unrelated first (the evidence `file:line` list tells you).
   - **INFRA-FLAKE** → rate-limit / runner / timeout. `gh run rerun <run-id> --failed`.
   - **PARTIAL** → fix the diff-owned failures, then re-run triage on the rest.
3. After a fix or re-run, `/craft:ci:watch <pr>` to poll the new run to completion —
   it'll suggest the merge when it goes green.

> **watch vs triage:** use `watch` to *wait* on a run and route the easy calls
> (green → merge, stuck check → `--admin`); use `triage` to *analyze* a red run
> with `file:line` evidence when the cause isn't obvious. Watch forwards the hard
> cases to triage, so you never reach for `--admin` on a hunch.
