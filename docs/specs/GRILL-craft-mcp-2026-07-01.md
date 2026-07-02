# GRILL: craft-mcp Desktop bridge (Cluster C)

- **Date:** 2026-07-01
- **Target:** [`SPEC-dist-surface-hardening-2026-07-01.md`](SPEC-dist-surface-hardening-2026-07-01.md) — Cluster C
- **Mode:** grill (convergent) — 5 branches resolved
- **Precedent:** `~/projects/dev-tools/himalaya-mcp` (TS MCP server → `.mcpb` + plugin variant)

## Locked decisions

| # | Branch | Decision | Why |
|---|--------|----------|-----|
| C-1 | **Tool surface** | Expose **3 clean read-only tools**: `validate-counts`, governance `run_rules.py --json`, `docs-staleness-check`. **Drop** `branch-guard.sh` (a PreToolUse hook reading stdin JSON — not a callable CLI) and `pre-release-check.sh` (needs a version arg, release-only). | Smallest correct surface; every tool is read-only with clean JSON I/O, no adapters. |
| C-2 | **Server language** | **Node/TypeScript**, shelling out to the bash/Python scripts. | Mirrors himalaya-mcp exactly (`@modelcontextprotocol/sdk` + Node-based `.mcpb`/DXT packaging). |
| C-3 | **Package location** | **Subdir in the craft repo** (`craft/mcp/`), bundling the wrapped scripts at build. | The tools ARE craft's own in-repo scripts — co-location bundles them into the `.mcpb` with **no vendoring / no version skew** (a separate repo would re-create the D1 frozen-mirror class). |
| C-4 | **Distribution** | Built **`.mcpb` as a GitHub release asset** on craft releases + install docs; build wired into craft's release pipeline. | Desktop installs DXT via its own app UI, not brew (himalaya-mcp ships exactly this). |
| C-5 | **Rollout / justification** | **Build (3 tools) + `.mcpb` + docs → validate on a real Claude Desktop install (tools actually invoke) → THEN wire release automation.** | Narrow audience (Desktop user wanting craft repo-hygiene) — prove the bridge works end-to-end before paying pipeline cost. |

## Open questions (resolve at implementation)

1. **Tool output contracts** — the JSON schema each of the 3 tools returns to Desktop (wrap the scripts' stdout, or define a typed result?).
2. **`docs-staleness-check` mode** — expose read-only only, or also its `--fix` (a write action on Desktop)? Lean read-only for a Desktop tool.
3. **Exact `.mcpb` build step location** in craft's release pipeline (deferred by C-5 until post-validation).
4. **Script invocation from the bundled `.mcpb`** — paths must resolve inside the extension sandbox; confirm the bundled scripts are found at runtime (not assuming a craft checkout).

## Handoff

Design is settled enough to implement C-5's first increment (build + validate, defer automation).
Next: `/craft:plan` (tier 4) → `ORCHESTRATE-craft-mcp.md`, or implement the `craft/mcp/` scaffold
directly in a worktree. Feeds the same dist-surface effort (D1 ✅ · A ✅ · B ✅ · **C** here).
