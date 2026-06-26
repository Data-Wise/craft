# Tutorial: Multi-Surface Release Propagation

**Audience:** craft plugin maintainers shipping a release to all registered surfaces.
**Time:** ~15 minutes
**Prerequisites:** craft release pipeline (`/release`), GitHub App configured.

---

## Overview

When you run `/release`, craft propagates the new version to a declarative surface registry:
three independent distribution surfaces (Code, Cowork, Desktop). This tutorial walks through the
surface model, the automated vs. manual steps, and how to verify full propagation.

---

## The 3-Surface Model

| Surface | Runtime | Gate | Automated? |
|---------|---------|------|------------|
| **Code** | Claude Code CLI | BLOCK | Yes (Homebrew + marketplace) |
| **Cowork** | Cowork platform | WARN | No (manual store update) |
| **Desktop** | Claude Desktop | INFO | No (DXT store; report only) |

A release is "fully shipped" when all BLOCK surfaces agree on the new version.

---

## Step 1: Pre-ship gate (one-time setup)

Before your first release using the aggregator CI action, verify the GitHub App is configured:

```bash
# Check App permissions on the aggregator repo
gh api repos/Data-Wise/claude-plugins/installation \
  --jq '.permissions | {contents, pull_requests}'
# Expected: { "contents": "write", "pull_requests": "write" }
```

If permissions are missing: navigate to the GitHub App settings and grant write access to
`Data-Wise/claude-plugins`.

---

## Step 2: Run the release pipeline

```bash
/release
```

The pipeline runs normally through Steps 1–13.5, then reaches Step 13.6 (Surface Registry Phase).

---

## Step 3: Surface registry phase (automated)

At Step 13.6, the pipeline:

1. **Waits for aggregator CI** — `aggregator-sync.yml` fires on `release: published` and
   auto-merges a version-bump PR in `Data-Wise/claude-plugins`. If the PR is not merged the
   action exits 1 and blocks the release.

2. **Emits advisory reminders** for WARN surfaces:

   ```
   ⚠️  Advisory: brew upgrade craft
   ⚠️  Advisory: claude plugin update craft@local-plugins
   ```

3. **Generates Cowork report** with a remind for manual store update.

4. **Runs verify-surfaces.sh** to assert every BLOCK surface has landed the new version.

---

## Step 4: Manual Cowork update (WARN — non-blocking)

The Cowork store requires a manual update after each release:

1. Open the Cowork app
2. Navigate to Plugins → craft → Update
3. Confirm the version matches the release

The Cowork WARN in the release report will clear once the store is updated and the next
`/craft:dist:surfaces` run detects alignment.

---

## Step 5: Verify full propagation

```bash
/craft:dist:surfaces
```

Expected output when all surfaces are aligned:

```
┌──────────────────────────────────────────────────────────────┐
│ /craft:dist:surfaces                                         │
├──────────────────────────────────────────────────────────────┤
│ Plugin: craft  Version: 2.53.0                               │
│ Surfaces checked: 3 (2 BLOCK, 1 WARN)                        │
├──────────────────────────────────────────────────────────────┤
│ Code    ............... 2.53.0  BLOCK  ✓ aligned             │
│ Cowork  ............... 2.53.0  WARN   ✓ aligned             │
│ Desktop ............... 2.53.0  WARN   ✓ aligned             │
├──────────────────────────────────────────────────────────────┤
│ Gate: PASSED — all BLOCK surfaces aligned                    │
└──────────────────────────────────────────────────────────────┘
```

---

## Troubleshooting

| Problem | Diagnosis | Fix |
|---------|-----------|-----|
| Aggregator CI fails | `gh run list --workflow=aggregator-sync.yml` | Check App permissions; re-run workflow |
| BLOCK surface mismatch | `scripts/verify-surfaces.sh` output | Fix lagging surface; re-run verify |
| Cowork WARN persistent | Manual update pending | Update Cowork store manually |
| `--skip-surfaces` used | Surfaces not verified | Re-run `scripts/verify-surfaces.sh` manually |

---

## Reference

- [`/craft:dist:surfaces`](../commands/dist/surfaces.md) — read-only surface registry view
- [`scripts/surfaces/registry.json`](../../scripts/surfaces/registry.json) — source of truth
- [`skills/release/references/downstream-verification.md`](../../skills/release/references/downstream-verification.md) — Step 13.6 implementation
- [`docs/adr/ADR-004-release-surface-registry.md`](../adr/ADR-004-release-surface-registry.md) — architecture decision
