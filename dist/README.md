# Data-Wise aggregator marketplace

`data-wise-marketplace.json` is **one** marketplace manifest listing every Data-Wise Claude Code
plugin (craft, scholar, rforge, himalaya-mcp). Add it **once** per surface and you receive all
current *and future* plugins — no per-repo `marketplace add` fan-out.

```bash
# Claude Code
claude plugin marketplace add Data-Wise/<aggregator-repo>

# Claude Desktop / Cowork — same engine, via the in-app "add marketplace" flow
# (one-time; see docs/guide/desktop-release.md for the click-path).
```

## Host (Open Question Q6 — not yet decided)

This manifest is the **source content**; it must be published to a Data-Wise GitHub repo whose
`.claude-plugin/marketplace.json` is this file. Two candidates:

| Option | Repo | Notes |
|--------|------|-------|
| **Reuse (recommended)** | `Data-Wise/claude-plugins` | Already exists ("Official Claude Code plugins"); no new repo to provision. |
| New dedicated | `Data-Wise/marketplace` | Cleaner naming, but one more repo + protection baseline to maintain. |

Until that decision lands, this file is committed in craft as the canonical content so the
aggregator repo can be seeded from it. **Provisioning the aggregator repo is a separate, reviewed
cross-repo change — not part of a craft release.**

## Keeping it in sync (no drift)

The aggregator entry is a **version leg**: once it exists, each plugin's release must update its own
entry, or the aggregator drifts from that plugin's per-repo `marketplace.json`.

- **Write:** `scripts/aggregator-sync.sh --file <aggregator> --plugin craft --version X.Y.Z`
  (updates an existing entry only — never silently adds a new plugin).
- **Verify:** `scripts/verify-surfaces.sh --aggregator-file <aggregator>` adds an `aggregator` leg
  that **blocks** the release if the entry disagrees with `plugin.json`.

Both are wired into the release pipeline at **Step 13.6** (see `skills/release/SKILL.md`).
