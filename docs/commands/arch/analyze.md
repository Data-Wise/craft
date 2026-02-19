# /craft:arch:analyze

> **Architecture analysis and pattern detection**

---

## Synopsis

```bash
/craft:arch:analyze [mode] [path]
```

**Quick examples:**

```bash
# Quick overview of architecture
/craft:arch:analyze

# Deep dive with verbose tracing
/craft:arch:analyze debug

# Full audit for release validation
/craft:arch:analyze release src/
```

---

## Description

Analyzes codebase architecture patterns, dependencies, and structure. Detects architectural anti-patterns, circular dependencies, and structural issues. Supports multiple analysis modes with different time budgets and depth levels.

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `mode` | Analysis mode: `default\|debug\|optimize\|release` | `default` |
| `path` | Directory to analyze | `.` (current directory) |

---

## Execution Modes

| Mode | Budget | Use Case | Output |
|------|--------|----------|--------|
| **default** | <15s | Quick overview | High-level patterns |
| **debug** | <120s | Troubleshooting | Verbose traces |
| **optimize** | <180s | Performance analysis | Hotspots + metrics |
| **release** | <300s | Pre-release audit | Comprehensive report |

---

## What It Analyzes

- **Structure**: Directory organization, file placement
- **Dependencies**: Module relationships, circular deps
- **Patterns**: Design patterns, anti-patterns
- **Complexity**: Cyclomatic complexity, nesting depth
- **Coupling**: Module coupling, cohesion metrics
- **Documentation**: Code-to-docs alignment

---

## Example Output

```text
Architecture Analysis (default mode)
====================================

Structure:
  • Commands:       106 files
  • Skills:         21 files
  • Agents:         8 files
  • Utils:          12 Python modules

Patterns Detected:
  ✓ Command routing: Hub-based discovery
  ✓ Agent delegation: Complexity scoring
  ✓ Error handling: Consistent patterns

Issues Found:
  ⚠ Circular dependency: utils/a.py → utils/b.py
  ⚠ High complexity: complexity_scorer.py (score: 8)

Recommendations:
  → Break circular dependency with interface
  → Refactor complexity_scorer into smaller modules
```

---

## See Also

- [/craft:check](../check.md) — Pre-flight validation
- [/craft:code:lint](../code/lint.md) — Code quality checks
- [/craft:test](../test.md) — Run test suite
