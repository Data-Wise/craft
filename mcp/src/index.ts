#!/usr/bin/env node
/**
 * craft-mcp — Claude Desktop MCP bridge for craft's read-only repo-hygiene checks.
 *
 * Exposes three craft scripts as MCP tools (design locked in GRILL-craft-mcp-2026-07-01):
 *   - craft_validate_counts   → scripts/validate-counts.sh
 *   - craft_governance_audit  → governance/run_rules.py --json
 *   - craft_docs_staleness    → scripts/docs-staleness-check.sh   (read-only; no --fix)
 *
 * Each tool runs a BUNDLED copy of the script (shipped inside the .mcpb) with the
 * working directory set to a caller-supplied `repo_path` (the craft-family repo to
 * inspect). All three are read-only — no writes, no network.
 */

import { Server } from "@modelcontextprotocol/sdk/server/index.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import {
  CallToolRequestSchema,
  ListToolsRequestSchema,
} from "@modelcontextprotocol/sdk/types.js";
import { spawn } from "node:child_process";
import { existsSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = dirname(fileURLToPath(import.meta.url));

// Scripts root — contains scripts/ and governance/ (same layout as the craft
// repo). Inside the .mcpb this is <ext>/bundled; for local dev (dist/ sits at
// mcp/dist) it falls back to the craft repo root two levels up.
const SCRIPTS_ROOT =
  process.env.CRAFT_MCP_SCRIPTS ??
  (existsSync(join(__dirname, "..", "bundled", "scripts", "validate-counts.sh"))
    ? join(__dirname, "..", "bundled")
    : join(__dirname, "..", ".."));

const MAX_OUTPUT = 60_000; // guard against a runaway script flooding the client

interface ToolSpec {
  name: string;
  title: string;
  description: string;
  /** argv to run, relative to SCRIPTS_ROOT; [0] is the interpreter target */
  build: (repoPath: string) => { cmd: string; args: string[] };
}

// All three tools are read-only, non-destructive, idempotent, and closed-world
// (they run bundled local scripts — no network). Shared per best-practices.
const READ_ONLY_ANNOTATIONS = {
  readOnlyHint: true,
  destructiveHint: false,
  idempotentHint: true,
  openWorldHint: false,
} as const;

const INPUT_SCHEMA = {
  type: "object",
  properties: {
    repo_path: {
      type: "string",
      description:
        "Absolute path to the craft-family repo to inspect (e.g. /Users/you/projects/craft).",
    },
  },
  required: ["repo_path"],
} as const;

// Structured result shape — returned as structuredContent alongside text.
const OUTPUT_SCHEMA = {
  type: "object",
  properties: {
    ok: { type: "boolean", description: "true if the check exited 0" },
    exit_code: {
      type: ["number", "null"],
      description: "the script's exit status, or null if it never ran (bad repo_path / missing script)",
    },
    output: { type: "string", description: "combined stdout/stderr report" },
  },
  required: ["ok", "exit_code", "output"],
} as const;

const TOOLS: ToolSpec[] = [
  {
    name: "craft_validate_counts",
    title: "Validate Craft Counts",
    description:
      "Validate a craft-family plugin's command/skill/agent counts against plugin.json and the tap manifest. Read-only. Requires repo_path (the plugin repo root).",
    build: (repo) => ({
      cmd: "bash",
      args: [join(SCRIPTS_ROOT, "scripts", "validate-counts.sh")],
    }),
  },
  {
    name: "craft_governance_audit",
    title: "Audit Skill Governance",
    description:
      "Run craft's skill-ecosystem governance rules (run_rules.py --json) and report RED/violations. Read-only. Requires repo_path (a repo containing governance/RULES.yaml).",
    build: (repo) => ({
      cmd: "python3",
      args: [join(SCRIPTS_ROOT, "governance", "run_rules.py"), "--json"],
    }),
  },
  {
    name: "craft_docs_staleness",
    title: "Check Docs Staleness",
    description:
      "Check a craft-family repo's docs for staleness (counts, versions, broken refs). Read-only — never applies --fix. Requires repo_path (the repo root).",
    build: (repo) => ({
      cmd: "bash",
      args: [join(SCRIPTS_ROOT, "scripts", "docs-staleness-check.sh"), "--non-interactive"],
    }),
  },
];

interface ToolResult {
  text: string;
  isError: boolean;
  exitCode: number | null;
}

function runTool(spec: ToolSpec, repoPath: string): Promise<ToolResult> {
  return new Promise((resolve) => {
    if (!repoPath || !existsSync(repoPath)) {
      resolve({
        text: `repo_path is required and must exist. Got: ${JSON.stringify(repoPath)}`,
        isError: true,
        exitCode: null,
      });
      return;
    }
    const { cmd, args } = spec.build(repoPath);
    if (!existsSync(args[0])) {
      resolve({
        text: `bundled script not found: ${args[0]} (SCRIPTS_ROOT=${SCRIPTS_ROOT})`,
        isError: true,
        exitCode: null,
      });
      return;
    }
    const child = spawn(cmd, args, { cwd: repoPath, env: process.env });
    let out = "";
    let err = "";
    child.stdout.on("data", (d) => (out += d.toString()));
    child.stderr.on("data", (d) => (err += d.toString()));
    child.on("error", (e) =>
      resolve({ text: `failed to run ${cmd}: ${e.message}`, isError: true, exitCode: null }),
    );
    child.on("close", (code) => {
      let body = out.trim() || err.trim() || "(no output)";
      if (body.length > MAX_OUTPUT) body = body.slice(0, MAX_OUTPUT) + "\n…(truncated)";
      const header = `$ ${cmd} (cwd=${repoPath}) → exit ${code}\n\n`;
      resolve({ text: header + body, isError: code !== 0, exitCode: code });
    });
  });
}

const server = new Server(
  { name: "craft-mcp", version: "0.1.0" },
  { capabilities: { tools: {} } },
);

server.setRequestHandler(ListToolsRequestSchema, async () => ({
  tools: TOOLS.map((t) => ({
    name: t.name,
    title: t.title,
    description: t.description,
    inputSchema: INPUT_SCHEMA,
    outputSchema: OUTPUT_SCHEMA,
    annotations: { title: t.title, ...READ_ONLY_ANNOTATIONS },
  })),
}));

server.setRequestHandler(CallToolRequestSchema, async (req) => {
  const spec = TOOLS.find((t) => t.name === req.params.name);
  if (!spec) {
    return {
      content: [{ type: "text", text: `unknown tool: ${req.params.name}` }],
      isError: true,
    };
  }
  const repoPath = String((req.params.arguments ?? {}).repo_path ?? "");
  const { text, isError, exitCode } = await runTool(spec, repoPath);
  return {
    content: [{ type: "text", text }],
    structuredContent: { ok: !isError, exit_code: exitCode, output: text },
    isError,
  };
});

const transport = new StdioServerTransport();
await server.connect(transport);
