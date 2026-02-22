# Mermaid Validation Pipeline Architecture

How Mermaid diagram validation flows through the craft plugin, from authoring to deploy.

## Pipeline Overview

```mermaid
flowchart TD
    A["Author writes diagram"] --> B{"Trigger?"}
    B -->|"git commit"| C["Pre-commit Hook"]
    B -->|"/craft:docs:check"| D["Phase 5 Validation"]
    B -->|"/craft:site:deploy"| E["Release Gate"]
    B -->|"Manual"| F["CLI Validation"]

    C --> G["Regex Pre-checks"]
    D --> G
    E --> H["Health Score"]
    F --> G

    G -->|"Errors found"| I["Block + Report"]
    G -->|"Clean"| J["Pass"]
    H -->|"< threshold"| K["Deploy Blocked"]
    H -->|">= threshold"| L["Deploy OK"]

    G --> H
```

## Component Map

```mermaid
flowchart LR
    subgraph "Entry Points"
        CMD["/craft:docs:check"]
        HOOK["Pre-commit Hook"]
        CLI["mermaid-validate.py"]
        DEPLOY["/craft:site:deploy"]
    end

    subgraph "Validation Engine"
        EXT["Block Extraction"]
        REG["Regex Pre-checks"]
        MCP["mcp-mermaid MCP"]
        SCORE["Health Score"]
    end

    subgraph "Fix Engine"
        AUTO["mermaid-autofix.py"]
        SAFE["Safe Fixes"]
        REPORT["Report-Only"]
    end

    CMD --> CLI
    HOOK --> CLI
    DEPLOY --> CLI

    CLI --> EXT --> REG
    REG --> MCP
    REG --> SCORE
    MCP --> SCORE

    AUTO --> SAFE
    AUTO --> REPORT
```

## Data Flow

### Block Extraction

```text
*.md files
  → scan for ```mermaid fences
  → track indent level for closing fence
  → emit MermaidBlock(file, line_number, content)
```

### Regex Pre-checks (5 rules)

| Rule | Severity | Pattern | Catches |
|------|----------|---------|---------|
| `leading-slash` | Error | `[/text]` | Parallelogram misparse |
| `lowercase-end` | Error | `[end]` | Keyword conflict |
| `unquoted-colon` | Warning | `[a:b]` | Parsing ambiguity |
| `br-tag` | Warning | `<br/>` | Deprecated syntax |
| `deprecated-graph` | Warning | `graph TD` | Outdated keyword |

### Health Score Calculation

```text
health = syntax_validity × 0.5
       + best_practices  × 0.3
       + rendering       × 0.2

Where:
  syntax_validity  = % blocks with 0 errors
  best_practices   = % blocks with 0 warnings
  rendering        = % blocks passing MCP render (defaults to syntax_validity)

Deduplication: issues grouped by (file, block_start_line) to prevent
inflation from multiple warnings per block.
```

## Scripts

| Script | Purpose | Typical Use |
|--------|---------|-------------|
| `scripts/mermaid-validate.py` | Extract + validate + score | CI, pre-commit, manual |
| `scripts/mermaid-autofix.py` | Safe auto-fixes + report | Cleanup before PR |
| `scripts/hooks/pre-commit-mermaid.sh` | Hook wrapper | Automatic on commit |

### CLI Flags

```text
mermaid-validate.py <paths...>
  --errors-only     Only errors (fast, for pre-commit)
  --json            Machine-readable output
  --health-score    Show composite score
  --gate [N]        Exit non-zero if score < N (default 80)

mermaid-autofix.py <paths...>
  --fix             Apply safe fixes (default: dry-run)
  --test            Run 12 built-in self-tests
```

## Integration Points

```mermaid
flowchart TD
    subgraph "Authoring"
        NL["/craft:docs:mermaid NL"]
        TPL["/craft:docs:mermaid template"]
        EXPERT["mermaid-expert agent"]
    end

    subgraph "Validation"
        CHECK["/craft:docs:check Phase 5"]
        LINT["mermaid-linter skill"]
        HOOK["Pre-commit hook"]
    end

    subgraph "Deploy"
        GATE["Health score gate"]
        SITE["/craft:site:deploy"]
    end

    NL --> EXPERT
    EXPERT -->|"validates via"| MCP["mcp-mermaid"]
    TPL --> EXPERT

    CHECK --> LINT
    LINT -->|"calls"| SCRIPT["mermaid-validate.py"]
    HOOK -->|"calls"| SCRIPT

    SCRIPT --> GATE
    GATE --> SITE
```

## Severity Model

**Two tiers** prevent noise while catching real issues:

- **Errors** block commits and deploys. Only patterns that cause visible rendering failures.
- **Warnings** are reported but don't block. Patterns that work but have better alternatives.

This design keeps the pre-commit hook fast (<1s) and avoids false-positive fatigue.
