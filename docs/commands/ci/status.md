# /craft:ci:status

> **Cross-repo CI status dashboard** — see all workflow statuses in one view.

---

## Synopsis

```bash
/craft:ci:status [--json] [--repo NAME]
```

**Quick examples:**

```bash
# Full dashboard for all repos
/craft:ci:status

# JSON output for scripting
/craft:ci:status --json

# Filter to a specific repo
/craft:ci:status --repo craft
/craft:ci:status --repo homebrew-tap
```

---

## What It Does

Queries GitHub Actions workflow runs across `Data-Wise/craft` and `Data-Wise/homebrew-tap`, deduplicates by workflow name (latest run only), and displays a color-coded dashboard.

---

## Output

### Dashboard View (Default)

```text
+-------------------------------------------------------------+
| CI Status Dashboard                                          |
+-------------------------------------------------------------+
|                                                              |
| Data-Wise/craft                                              |
|   [pass] Craft CI                    passed     (main)       |
|   [pass] Craft CI                    passed     (dev)        |
|   [pass] Deploy Documentation        passed     (main)       |
|   [pass] Homebrew Release            passed     (main)       |
|   [pass] Validate Dependencies       passed     (main)       |
|                                                              |
| Data-Wise/homebrew-tap                                       |
|   [pass] Update Formula              passed     (main)       |
|                                                              |
+-------------------------------------------------------------+
| Status: All workflows passing                                |
+-------------------------------------------------------------+
```

### Failure Summary

When failures exist, a summary section appears:

```text
+-------------------------------------------------------------+
| [FAIL] 1 failure:                                            |
|   Homebrew Release (main) -- failed 5 hours ago              |
|   -> Check: gh run view --repo Data-Wise/craft <run-id>     |
+-------------------------------------------------------------+
```

### JSON View (`--json`)

```json
{
  "repos": {
    "Data-Wise/craft": [
      {
        "workflow": "Craft CI",
        "status": "success",
        "branch": "main",
        "created": "2026-02-19T10:00:00Z"
      }
    ],
    "Data-Wise/homebrew-tap": [
      {
        "workflow": "Update Formula",
        "status": "success",
        "branch": "main",
        "created": "2026-02-19T09:00:00Z"
      }
    ]
  },
  "summary": {
    "total": 6,
    "passed": 6,
    "failed": 0
  }
}
```

---

## Arguments

| Argument | Description | Default |
|----------|-------------|---------|
| `--json` | Machine-readable JSON output | `false` |
| `--repo NAME` | Filter to specific repo (e.g., `craft`, `homebrew-tap`) | All repos |

---

## Repos Monitored

| Repo | Workflows |
|------|-----------|
| `Data-Wise/craft` | Craft CI, Deploy Documentation, Documentation Quality, Homebrew Release, Validate Dependencies |
| `Data-Wise/homebrew-tap` | Update Formula |

---

## When to Use

| Scenario | Command |
|----------|---------|
| Pre-release verification | `/craft:ci:status` |
| Post-release check | `/craft:ci:status --repo homebrew-tap` |
| CI debugging | `/craft:ci:status` (check for failures) |
| Scripting/automation | `/craft:ci:status --json` |

---

## Error Handling

| Error | Behavior |
|-------|----------|
| `gh` not authenticated | Shows: "Run `gh auth login` first" |
| Repo not accessible | Skips with warning, shows other repos |
| Network error | Shows error message |

---

## Prerequisites

- `gh` CLI installed and authenticated
- Access to `Data-Wise/craft` and `Data-Wise/homebrew-tap` repos

---

## See Also

- [CI Monitoring Architecture](../../architecture/ci-monitoring.md) — Automated CI monitoring loop
- [Release Pipeline Reference](../../reference/REFCARD-RELEASE.md) — CI verification in release flow
- [/craft:ci:generate](generate.md) — Generate CI workflows
