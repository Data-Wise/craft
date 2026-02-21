# /craft:code:sync-features

> **Interactive wizard to sync craft with latest Claude capabilities**

---

## Synopsis

```bash
/craft:code:sync-features
```

---

## Description

Chains command-audit, release-watch, and desktop-watch into a prioritized action plan. Audits craft's current health, checks for upstream Claude Code/Desktop changes, and presents an interactive selection of actions to keep the plugin current.

---

## Workflow Steps

| Step | Tool | What Happens |
|------|------|-------------|
| 1 | command-audit | Assess current craft health (frontmatter, deprecated patterns) |
| 2 | release-watch | Fetch latest Claude Code releases, find plugin-relevant changes |
| 3 | desktop-watch | (Optional) Search for Claude Desktop updates |
| 4 | Merge | Combine findings into prioritized action list |
| 5 | Select | Interactive multi-select of items to act on |
| 6 | Execute | Apply selected fixes and improvements |
| 7 | Summary | Report actions taken and health score change |

---

## Priority Levels

| Priority | Criteria |
|----------|----------|
| P0 (Critical) | BREAKING changes, errors in audit |
| P1 (High) | NEW features to adopt, deprecated patterns to remove |
| P2 (Medium) | Warnings from audit, FIXED items to verify |
| P3 (Low) | Desktop integration opportunities, suggestions |

---

## When to Use

- After a Claude Code release to assess impact on craft
- Periodic maintenance to ensure craft uses latest capabilities
- Before a craft release to verify compatibility
- When the user asks "what's new in Claude Code?"

---

## Prerequisites

- `gh` CLI installed and authenticated (for release-watch)
- Internet access (for desktop-watch web search)

---

## Integration

- [/craft:code:command-audit](command-audit.md) -- Step 1: Frontmatter validation
- [/craft:code:release-watch](release-watch.md) -- Step 2: Release tracking
- [/craft:code:desktop-watch](desktop-watch.md) -- Step 3: Desktop monitoring
- [/craft:check](../check.md) -- General pre-flight checks
