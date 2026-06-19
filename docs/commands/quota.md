# /craft:quota

> **Pre-flight token quota gate — checks available capacity before an orchestrated run.**

---

## Synopsis

```bash
/craft:quota [engine] [--json]
```

**Quick examples:**

```bash
/craft:quota                # Estimate for workflow engine (default)
/craft:quota fanout         # Estimate for fanout engine
/craft:quota --json         # Machine-readable JSON output
```

---

## What It Does

Reads `~/.claude/quota-cache.json` (written by Claude Code's native rate-limit
status line), estimates cost-weighted tokens for the planned orchestrate run, and
maps to a **SAFE / TIGHT / DEFER** advisory before committing to an expensive run.

Silently skips when the cache is absent or stale (>900 s), so it never blocks
in cold or offline environments.

---

## Arguments

| Argument | Values | Default | Description |
|----------|--------|---------|-------------|
| `engine` | `workflow` \| `fanout` | `workflow` | Engine type to estimate tokens for |
| `--json` | flag | `false` | Output as JSON instead of human-readable |

---

## Advisories

| Status | `five_hour_pct` | Meaning |
|--------|-----------------|---------|
| **SAFE** | < 60 % | Proceed — plenty of quota remaining |
| **TIGHT** | 60 – 84 % | Consider deferring large runs |
| **DEFER** | ≥ 85 % | Quota critically low — defer if possible |

---

## Thresholds

- SAFE: `five_hour_pct < 60`
- TIGHT: `60 ≤ five_hour_pct < 85`
- DEFER: `five_hour_pct ≥ 85`

---

## Integration

`/craft:check` integrates `/craft:quota` as an opt-in advisory step (silently
skips when cache absent). The advisory is informational only — it never blocks
the check from completing.

---

## Related

- [`/craft:check`](check.md) — pre-flight validation (includes quota advisory)
- [`/craft:orchestrate`](orchestrate.md) — token-consuming orchestration engine
