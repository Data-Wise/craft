# /craft:docs:sync

> **Smart documentation detection from code changes**

---

## Synopsis

```bash
/craft:docs:sync [options]
```

**Quick examples:**

```bash
# Detect doc needs from recent changes
/craft:docs:sync

# Check changes since specific commit
/craft:docs:sync --since HEAD~5

# Use orchestration mode for complex updates
/craft:docs:sync --orch
```

---

## Description

Analyzes code changes and intelligently classifies documentation needs: guides for concepts, refcards for quick reference, demos for workflows. Supports orchestration mode for coordinating multi-file documentation updates.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--verbose` | Show detailed detection logic | `false` |
| `--json` | Output results as JSON | `false` |
| `--since` | Commit range to analyze (e.g., `HEAD~5`, `v2.11.0`) | `HEAD~10` |
| `--dry-run`, `-n` | Preview detection without creating files | `false` |
| `--orch` | Enable orchestration mode | `false` |
| `--orch-mode` | Orchestration mode: `default\|debug\|optimize\|release` | `default` |

---

## Detection Rules

| Change Type | Suggested Documentation |
|-------------|------------------------|
| New command | Command page + usage examples |
| New agent | Agent guide + trigger scenarios |
| API changes | API reference update |
| Workflow changes | Tutorial or guide update |
| Config changes | Reference card update |

---

## Orchestration Mode

When `--orch` is enabled, coordinates multi-agent documentation updates:

- **default** (<10s): Quick sync for minor changes
- **debug** (<120s): Verbose tracing for troubleshooting
- **optimize** (<180s): Performance-focused analysis
- **release** (<300s): Comprehensive audit for releases

---

## See Also

- [/craft:docs:check](check.md) — Documentation health check
- [/craft:docs:changelog](changelog.md) — Auto-update changelog
- [/craft:orchestrate](../orchestrate.md) — Multi-agent coordination
