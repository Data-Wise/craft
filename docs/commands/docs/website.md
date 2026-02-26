# /craft:docs:website

> **ADHD-friendly website enhancement with scoring and phased improvements**

---

## Synopsis

```bash
/craft:docs:website [options]
```

**Quick examples:**

```bash
# Full enhancement (all 3 phases)
/craft:docs:website

# Analyze ADHD-friendliness score only
/craft:docs:website --analyze

# Run quick wins phase only
/craft:docs:website --phase 1

# Preview changes without writing files
/craft:docs:website --dry-run
```

---

## Description

Analyzes and improves documentation sites for ADHD accessibility. Calculates an ADHD-friendliness score (0-100) across five categories, then generates and executes a phased enhancement plan to raise that score.

Supports MkDocs Material (primary), Quarto (partial), and Sphinx (basic). The command auto-detects the site framework from project configuration files.

Philosophy: "One command to make any documentation site ADHD-friendly."

---

## Options

| Option | Description | Default |
|--------|-------------|---------|
| `--analyze` | Show ADHD score without making changes | `false` |
| `--phase` | Run a specific phase: `1`, `2`, or `3` | All phases |
| `--dry-run` | Preview changes without writing files | `false` |
| `--validate` | Validate current ADHD-friendliness state | `false` |

---

## Scoring Categories

The ADHD score is a weighted average of five categories:

| Category | Weight | What It Measures |
|----------|--------|------------------|
| Visual Hierarchy | 25% | TL;DR boxes, emoji headings, heading structure |
| Time Estimates | 20% | Duration labels on tutorials and guides |
| Workflow Diagrams | 20% | Mermaid diagrams, syntax validity, workflow page |
| Mobile Responsive | 15% | Responsive CSS, overflow fixes, touch targets |
| Content Density | 20% | Paragraph length, callout boxes, visual breaks |

Grades: A (90-100), B (80-89), C (70-79), D (60-69), F (<60).

---

## Enhancement Phases

| Phase | Focus | Time Budget | Key Actions |
|-------|-------|-------------|-------------|
| **1: Quick Wins** | Highest impact, lowest effort | < 2 hours | Fix mermaid errors, add TL;DR boxes, add time estimates, create ADHD Quick Start page |
| **2: Structure** | Navigation and layout | < 4 hours | Create Visual Workflows page, flatten navigation, add callout boxes, homepage restructure |
| **3: Polish** | Mobile and interactivity | < 8 hours | Mobile responsive CSS, interactive diagrams, progress indicators |

After each phase, the command rebuilds the site with `mkdocs build --strict`, recalculates the ADHD score, and reports the improvement.

---

## See Also

- [/craft:docs:check](check.md) -- Documentation health check
- [/craft:docs:mermaid](mermaid.md) -- Mermaid diagram generation
- [/craft:docs:update](update.md) -- Update documentation
