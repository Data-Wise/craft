# Mermaid Troubleshooting Guide

Common Mermaid diagram issues and how to fix them.

## Diagram Shows as Raw Code

**Symptom:** `flowchart TD` text appears instead of a rendered diagram.

| Cause | Fix |
|-------|-----|
| Missing `custom_fences` in mkdocs.yml | Add the superfences config (see below) |
| Extra CDN script conflicting | Remove `extra_javascript` mermaid CDN entry |
| Syntax error in diagram | Run `python3 scripts/mermaid-validate.py <file>` |

**Required mkdocs.yml config:**

```yaml
markdown_extensions:
  - pymdownx.superfences:
      custom_fences:
        - name: mermaid
          class: mermaid
          format: !!python/name:pymdownx.superfences.fence_code_format
```

## Pre-commit Hook Blocks Commit

**Symptom:** `Mermaid validation failed` on `git commit`.

1. Check which rule fired — the hook prints the file, line, and rule name
2. Fix the pattern:

| Rule | What You Wrote | Fix |
|------|---------------|-----|
| `leading-slash` | `A[/api/v1]` | `A["/api/v1"]` |
| `lowercase-end` | `B[end]` | `B[End]` |

3. If the error is in a **code example** (intentional bad syntax), change the fence from `` ```mermaid `` to `` ```text ``

## Health Score Below Threshold

**Symptom:** `Release gate FAILED: 75 < 80`

```bash
# See full breakdown
python3 scripts/mermaid-validate.py docs/ --health-score

# See all warnings
python3 scripts/mermaid-validate.py docs/

# Auto-fix safe patterns
python3 scripts/mermaid-autofix.py docs/ --fix
```

**Score components:**

| Component | Weight | How to Improve |
|-----------|--------|---------------|
| Syntax validity | 50% | Fix all errors (leading-slash, lowercase-end) |
| Best practices | 30% | Fix warnings (quote colons, replace `graph` with `flowchart`) |
| Rendering success | 20% | Currently mirrors syntax validity |

## Auto-fix Didn't Fix Everything

**Symptom:** Warnings remain after `--fix`.

The auto-fix engine has two modes:

- **Safe fixes** (applied by `--fix`): leading-slash, lowercase-end, unquoted-colon, br-tag, deprecated-graph
- **Report-only** (needs human review): long text (>20 chars), orphaned nodes, complex horizontal layouts

Report-only items require judgment — the tool tells you what to look at, but you decide the fix.

## MCP Server Not Available

**Symptom:** MCP validation skipped or errors about mcp-mermaid.

1. Check `.mcp.json` exists in project root with:

   ```json
   {
     "mcpServers": {
       "mcp-mermaid": {
         "command": "npx",
         "args": ["-y", "mcp-mermaid"]
       }
     }
   }
   ```

2. Test manually: `npx -y mcp-mermaid` (should start without errors)

3. If npx fails, check Node.js is installed: `node --version` (requires 18+)

**Fallback:** All regex pre-checks work without MCP. Only full syntax validation and SVG rendering require the MCP server.

## Common Syntax Errors

| Error | Cause | Fix |
|-------|-------|-----|
| `Parse error on line N` | Invalid Mermaid syntax | Check node labels for special chars |
| `Lexical error on line N` | Unescaped characters | Quote labels containing `/`, `:`, `<`, `>` |
| Diagram cuts off | Unclosed subgraph | Ensure every `subgraph` has matching `end` |
| Nodes overlap | Horizontal layout too wide | Switch from `LR` to `TD` for >5 nodes |

## Quick Diagnostic Commands

```bash
# Validate specific file
python3 scripts/mermaid-validate.py docs/guide/my-file.md

# Errors only (fast)
python3 scripts/mermaid-validate.py docs/ --errors-only

# Full health check
python3 scripts/mermaid-validate.py docs/ --health-score

# Preview auto-fixes (dry-run)
python3 scripts/mermaid-autofix.py docs/

# Apply safe fixes
python3 scripts/mermaid-autofix.py docs/ --fix

# Run autofix self-tests
python3 scripts/mermaid-autofix.py --test
```
