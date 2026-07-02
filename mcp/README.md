# craft-mcp — Claude Desktop bridge for craft repo-hygiene

A small MCP server that exposes craft's **read-only** repo-hygiene checks as tools
Claude Desktop can call. Design: [`docs/specs/GRILL-craft-mcp-2026-07-01.md`](../docs/specs/GRILL-craft-mcp-2026-07-01.md).

Claude Code (the CLI) loads craft as a *plugin* (commands/skills/agents). Claude
**Desktop** can't load plugins — it loads DXT/MCPB *extensions* that wrap a runnable
MCP server. This is that server, packaged as a `.mcpb`.

## Tools (all read-only, no writes, no network)

| Tool | Wraps | Needs |
|------|-------|-------|
| `craft_validate_counts` | `scripts/validate-counts.sh` | `repo_path` |
| `craft_governance_audit` | `governance/run_rules.py --json` | `repo_path` |
| `craft_docs_staleness` | `scripts/docs-staleness-check.sh` | `repo_path` |

Each takes `repo_path` — the absolute path to the craft-family repo to inspect —
and runs a **bundled** copy of the script there. `docs-staleness` never applies `--fix`.

## Develop

```bash
npm install
npm run build      # esbuild → dist/index.js
npm run smoke      # local stdio test against the craft repo (no Desktop needed)
```

## Package for Desktop

```bash
npm run build:mcpb   # → craft-mcp-v<version>.mcpb
```

Install the `.mcpb` from Claude Desktop's extension manager (Settings → Extensions →
install from file). The bundle ships the wrapped scripts under `bundled/`
(`CRAFT_MCP_SCRIPTS=${__dirname}/bundled`), so it's self-contained — no craft
checkout required at runtime, but you still point each tool at a `repo_path` to inspect.

## Status

MVP (Cluster C of `SPEC-dist-surface-hardening-2026-07-01`). Rollout per grill C-5:
build + local smoke → validate the `.mcpb` on a real Desktop → then wire the `.mcpb`
build into craft's release pipeline. Not yet auto-released.
