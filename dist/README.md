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

## Host (Open Question Q6 — RESOLVED 2026-06-15)

**Decision: reuse `Data-Wise/claude-plugins`.** A root `.claude-plugin/marketplace.json` (this file's
content) is added there, so the aggregator is addable as `Data-Wise/claude-plugins` with no new repo
to provision. Published via **[Data-Wise/claude-plugins#3](https://github.com/Data-Wise/claude-plugins/pull/3)**
(branch + PR, no direct push to main).

This file remains the **canonical source content** in craft; the aggregator repo is seeded from it.
Keep the two in sync — a future plugin's version bump updates its entry here *and* in the aggregator
repo (see "Keeping it in sync" below).

## Keeping it in sync (no drift)

The aggregator entry is a **version leg**: once it exists, each plugin's release must update its own
entry, or the aggregator drifts from that plugin's per-repo `marketplace.json`.

- **Write:** `scripts/aggregator-sync.sh --file <aggregator> --plugin craft --version X.Y.Z`
  (updates an existing entry only — never silently adds a new plugin).
- **Verify:** `scripts/verify-surfaces.sh --aggregator-file <aggregator>` adds an `aggregator` leg
  that **blocks** the release if the entry disagrees with `plugin.json`.

Both are wired into the release pipeline at **Step 13.6** (see `skills/release/SKILL.md`).
