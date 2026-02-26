---
description: Cross-repo CI status dashboard showing all workflow runs
arguments:
  - name: json
    description: Output as JSON for scripting
    required: false
    default: false
  - name: repo
    description: Filter to a specific repo (e.g. craft, homebrew-tap)
    required: false
  - name: post-release
    description: Run post-release verification (downstream workflows, live site, formula)
    required: false
    default: false
---

# /craft:ci:status - CI Status Dashboard

Show all CI workflow statuses across craft and related repos in one view.

## When to Use

- Before releasing, to verify all workflows are green
- After a release, to check homebrew-release succeeded
- When debugging CI failures across repos

## Implementation

Run `gh run list` for each configured repo and display results.

### Step 1: Gather Workflow Runs

```bash
# Primary repo
CRAFT_REPO="Data-Wise/craft"
gh run list --repo "$CRAFT_REPO" --limit 10 --json name,status,conclusion,headBranch,createdAt,event

# Homebrew tap
TAP_REPO="Data-Wise/homebrew-tap"
gh run list --repo "$TAP_REPO" --limit 5 --json name,status,conclusion,headBranch,createdAt,event
```

### Step 2: Parse and Deduplicate

For each workflow, show only the most recent run:

```bash
# Group by workflow name, take latest per workflow
# Use jq or python3 to deduplicate
python3 -c "
import json, sys
runs = json.load(sys.stdin)
seen = {}
for run in runs:
    name = run['name']
    if name not in seen:
        seen[name] = run
for name, run in sorted(seen.items()):
    status = run['conclusion'] or run['status']
    icon = '✅' if status == 'success' else '❌' if status == 'failure' else '🔄' if status == 'in_progress' else '⏭️'
    branch = run['headBranch']
    print(f'  {icon} {name:30s} {status:10s} ({branch})')
"
```

### Step 3: Format Output

Display using box-drawing characters:

```
┌─────────────────────────────────────────────────────────────┐
│ CI Status Dashboard                                          │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│ Data-Wise/craft                                              │
│   ✅ Craft CI                    passed     (main)           │
│   ✅ Craft CI                    passed     (dev)            │
│   ✅ Deploy Documentation        passed     (main)           │
│   ✅ Documentation Quality       passed     (main)           │
│   ✅ Homebrew Release            passed     (main)           │
│   ✅ Validate Dependencies       passed     (main)           │
│                                                              │
│ Data-Wise/homebrew-tap                                       │
│   ✅ Update Formula              passed     (main)           │
│                                                              │
├─────────────────────────────────────────────────────────────┤
│ Status: All workflows passing                                │
└─────────────────────────────────────────────────────────────┘
```

### Step 4: Failure Summary

If any workflows failed, add a summary section:

```
├─────────────────────────────────────────────────────────────┤
│ ❌ 1 failure:                                                │
│   Homebrew Release (main) — failed 5 hours ago               │
│   → Check: gh run view --repo Data-Wise/craft <run-id>      │
└─────────────────────────────────────────────────────────────┘
```

### JSON Output (--json)

When `--json` is passed, output machine-readable format:

```json
{
  "repos": {
    "Data-Wise/craft": [
      {"workflow": "Craft CI", "status": "success", "branch": "main", "created": "2026-02-19T10:00:00Z"}
    ],
    "Data-Wise/homebrew-tap": [
      {"workflow": "Update Formula", "status": "success", "branch": "main", "created": "2026-02-19T09:00:00Z"}
    ]
  },
  "summary": {"total": 7, "passed": 7, "failed": 0}
}
```

## Post-Release Mode

When invoked with `--post-release`, runs extended downstream verification:

1. **Release-triggered workflows** — checks ci.yml, docs.yml, homebrew-release.yml ran successfully on latest main push
2. **Homebrew tap workflows** — checks Data-Wise/homebrew-tap CI for successful formula update
3. **Live site version** — curls the docs site to confirm new version string appears
4. **Badge URL validation** — confirms main and dev CI badges resolve and show "passing"
5. **Brew info** — runs `brew info data-wise/tap/craft` to verify version

### Output Format

Uses standard box-drawing output:

```text
┌─────────────────────────────────────────────────────────────┐
│  POST-RELEASE VERIFICATION                                   │
├─────────────────────────────────────────────────────────────┤
│  [1/5] ci.yml on main ..................... PASSED            │
│  [2/5] docs.yml deployment ............... PASSED             │
│  [3/5] homebrew-release.yml .............. PASSED             │
│  [4/5] Live site version ................. v2.28.0            │
│  [5/5] Badge validation .................. ALL PASSING        │
├─────────────────────────────────────────────────────────────┤
│  Result: ALL GREEN                                           │
└─────────────────────────────────────────────────────────────┘
```

## Repos Monitored

| Repo | Workflows |
|------|-----------|
| `Data-Wise/craft` | Craft CI, Deploy Documentation, Documentation Quality, Homebrew Release, Validate Dependencies |
| `Data-Wise/homebrew-tap` | Update Formula |

## Error Handling

- If `gh` CLI is not authenticated, show: "Run `gh auth login` first"
- If a repo is not accessible, skip it with a warning
- Network errors: show cached data if available, or error message
