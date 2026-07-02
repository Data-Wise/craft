// Local stdio smoke test for craft-mcp — validates the server lists 3 tools and
// can run craft_validate_counts against a real craft repo, WITHOUT Claude Desktop.
// Usage: node tests/smoke.mjs [repo_path]   (default: the craft repo two levels up)
import { Client } from "@modelcontextprotocol/sdk/client/index.js";
import { StdioClientTransport } from "@modelcontextprotocol/sdk/client/stdio.js";
import { dirname, join, resolve } from "node:path";
import { fileURLToPath } from "node:url";

const here = dirname(fileURLToPath(import.meta.url));
const mcpDir = join(here, "..");
const craftRoot = resolve(process.argv[2] ?? join(mcpDir, ".."));

const transport = new StdioClientTransport({
  command: "node",
  args: [join(mcpDir, "dist", "index.js")],
  // Dev: point SCRIPTS_ROOT at the craft repo root (has scripts/ + governance/)
  env: { ...process.env, CRAFT_MCP_SCRIPTS: craftRoot },
});
const client = new Client({ name: "smoke", version: "0" }, { capabilities: {} });

let failures = 0;
const check = (cond, msg) => {
  console.log(`${cond ? "PASS" : "FAIL"}: ${msg}`);
  if (!cond) failures++;
};

await client.connect(transport);

const { tools } = await client.listTools();
const names = tools.map((t) => t.name).sort();
check(tools.length === 3, `lists 3 tools (got ${tools.length}: ${names.join(", ")})`);
check(names.includes("craft_validate_counts"), "exposes craft_validate_counts");
check(names.includes("craft_governance_audit"), "exposes craft_governance_audit");
check(names.includes("craft_docs_staleness"), "exposes craft_docs_staleness");

// Best-practice fields (mcp-builder review): title, annotations, outputSchema
for (const t of tools) {
  check(!!t.title, `${t.name} has a title`);
  check(t.annotations?.readOnlyHint === true, `${t.name} is annotated readOnlyHint:true`);
  check(t.annotations?.destructiveHint === false, `${t.name} is annotated destructiveHint:false`);
  check(!!t.outputSchema, `${t.name} declares an outputSchema`);
}

// repo_path required
const missing = await client.callTool({ name: "craft_validate_counts", arguments: {} });
check(missing.isError === true, "craft_validate_counts errors without repo_path");

// real run against the craft repo
const res = await client.callTool({
  name: "craft_validate_counts",
  arguments: { repo_path: craftRoot },
});
const text = res.content?.[0]?.text ?? "";
check(text.includes("exit"), "validate_counts returns an exit-coded report");
check(/validated|commands|counts/i.test(text), "validate_counts output looks like a count report");
check(typeof res.structuredContent?.ok === "boolean", "returns structuredContent.ok");
check("exit_code" in (res.structuredContent ?? {}), "returns structuredContent.exit_code");

await client.close();
console.log(failures === 0 ? "\nSMOKE OK" : `\nSMOKE FAILED (${failures})`);
process.exit(failures === 0 ? 0 : 1);
