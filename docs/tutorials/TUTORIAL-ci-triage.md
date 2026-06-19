# Tutorial: ci:triage — Diagnose a Failing CI Check

By the end of this tutorial you will have:

- Triaged a failing CI run to determine if it's PR-caused or pre-existing
- Received a recommended action (re-run / `--admin` merge / fix)
- Used JSON output to script triage decisions

**Prerequisites:** craft installed, `gh` CLI authenticated, a PR with a failing check.

---

## Step 1: Triage the Current PR

```
/craft:ci:triage
```

The command fetches the failing check logs, analyzes them, and classifies the failure:

```
CI Triage — PR #176 (dev → main)
──────────────────────────────────
Failing check: Craft CI / test (ubuntu-latest)

Classification: PRE-EXISTING / INFRASTRUCTURE
  Evidence:
    • Failure is in `validate-plugin-structure` step
    • This step was also failing on the prior green run (#1229)
    • No files in the PR diff touch plugin structure
    • Runner queue timeout pattern detected

Recommendation: ✅ Safe to merge with --admin
  Rationale: Failure is unrelated to PR diff; infrastructure queue issue.
  Command:    gh pr merge 176 --merge --admin
```

---

## Step 2: Triage a Specific PR

```
/craft:ci:triage --pr 176
```

Or specify a different repo:

```
/craft:ci:triage --pr 176 --repo Data-Wise/craft
```

---

## Step 3: Understand Classification

| Classification | Meaning | Recommended Action |
|----------------|---------|-------------------|
| `DIFF-CAUSED` | Failure introduced by this PR's changes | Fix the code |
| `PRE-EXISTING` | Failure existed before this PR | Re-run or `--admin` |
| `INFRASTRUCTURE` | Runner timeout, cache miss, flaky network | Re-run |
| `UNKNOWN` | Cannot determine | Review logs manually |

---

## Step 4: JSON Output

```
/craft:ci:triage --json
```

Returns:

```json
{
  "pr": 176,
  "classification": "PRE-EXISTING",
  "recommendation": "admin_merge",
  "evidence": ["..."],
  "safe_to_merge": true
}
```

---

## What's Next

- If `DIFF-CAUSED`, fix the failing code and push a new commit
- If `PRE-EXISTING` or `INFRASTRUCTURE`, use `gh pr merge --admin` after confirming
- Use `/craft:ci:watch` to monitor a re-triggered run
