---
name: plugin-audit
description: This skill should be used when the user asks to "audit my plugins", "check for plugin duplicates", "plugin collision check", "find duplicate skills across plugins", "which plugins overlap", or wants to know if an installed Claude Code plugin duplicates or shadows another plugin's commands/skills. Diffs enabled plugins' actual command/skill surface against each other and flags cross-namespace name collisions — e.g. a bare `workflow:brainstorm` skill in one plugin vs. `craft:workflow:brainstorm` in another. Read-only — reports findings, never disables or uninstalls a plugin itself. Do not confuse with guard-audit (branch-guard.sh rule tuning) or command-skill-token-efficiency (command-vs-skill placement within a single plugin) — this skill compares surfaces ACROSS installed plugins.
---

# Plugin Audit

Finds duplicate or colliding plugins in the current Claude Code installation — the class of finding that a one-off manual sweep is prone to miss. Grew out of a 2026-07-01 session in which a manual 60-plugin review (2026-06-29) had missed `workflow@local-plugins`, a standalone plugin whose `commands/workflow/*` fully duplicated craft's own `commands/workflow/*` namespace (1131 legacy lines vs. craft's 112-line thin shim, same command names). See `docs/specs/SPEC-token-efficiency-and-context-tooling-2026-07-01.md` Part D #3.

## Why this matters

Two plugins registering the same command or skill name — or near-duplicate content under different namespaces (`workflow:brainstorm` vs. `craft:workflow:brainstorm`) — is both a token-cost problem (duplicate content loads twice) and a correctness problem (routing ambiguity: which one fires?). Manual plugin audits are infrequent and don't scale past a handful of plugins; this skill makes the surface-diff repeatable and cheap enough to run any time plugin state changes.

## What this skill does NOT do

- Does not uninstall, disable, or edit any plugin, marketplace entry, or `~/.claude/settings.json` key. It reports; the user (or a follow-up command) acts.
- Does not evaluate whether a plugin's *content quality* is good — only whether its surface (command/skill names) collides with another installed plugin's surface.
- Does not require network access — everything it reads is local (`~/.claude/settings.json`, `~/.claude/plugins/`, each plugin's own repo/cache directory).

## Inputs

1. **`~/.claude/settings.json`** — `enabledPlugins` object. Keys are `<plugin-name>@<marketplace-name>`; only plugins with a truthy value are actually active.
2. **`~/.claude/plugins/installed_plugins.json`** (if present) — richer per-plugin metadata (source path, marketplace, version) than `settings.json` alone provides. Treat as supplementary, not required — some installations only have `settings.json`.
3. **Each enabled plugin's own directory** — resolve via `installed_plugins.json`'s recorded path, or `~/.claude/plugins/marketplaces/<marketplace>/<plugin>/` / `~/.claude/plugins/repos/...` (layout varies by install method: local marketplace vs. GitHub marketplace vs. Desktop). Within that directory, the actual surface is:
   - `commands/**/*.md` — each file's path (minus the `.md`) becomes a command name, namespaced as `<plugin>:<relative-path-without-ext>` (e.g. `commands/workflow/brainstorm.md` → `<plugin>:workflow:brainstorm`).
   - `skills/**/SKILL.md` — each `SKILL.md`'s parent directory name is the skill name, namespaced the same way.

## Audit procedure

Execute these steps in order.

### Step 1: Enumerate enabled plugins

```bash
jq -r '.enabledPlugins | to_entries[] | select(.value == true) | .key' ~/.claude/settings.json
```

Cross-reference against `installed_plugins.json` if present, to resolve each plugin's on-disk path:

```bash
jq -r '.plugins[]? | "\(.name)@\(.marketplace) -> \(.path // "unknown")"' ~/.claude/plugins/installed_plugins.json 2>/dev/null \
  || echo "(installed_plugins.json not found — resolve paths manually per plugin)"
```

**Progress indicator:** `[1/4] Enumerate plugins .......... DONE (N enabled)`

### Step 2: Extract each plugin's command/skill surface

For each enabled plugin, list its command and skill basenames:

```bash
# Commands: strip .md, keep path structure as the namespaced name
find "<plugin-dir>/commands" -name '*.md' 2>/dev/null | sed -E "s#^.*/commands/##; s#\.md\$##"

# Skills: each SKILL.md's parent directory name
find "<plugin-dir>/skills" -name 'SKILL.md' 2>/dev/null | sed -E 's#/SKILL\.md$##; s#^.*/skills/##'
```

Build one flat list per plugin of `<base-name>` entries (the part after the last `/` — this is what actually collides, since users invoke by base name or via fuzzy match, not full namespaced path).

**Progress indicator:** `[2/4] Extract surfaces ........... DONE (N plugins, M total commands+skills)`

### Step 3: Cross-plugin collision detection

Compare every pair of enabled plugins' base-name lists. Flag two classes of finding:

1. **Exact base-name collision** — the same command or skill base name (e.g. `brainstorm`) appears in two or more different plugins. This is the `workflow` vs. `craft:workflow` class: a bare-namespace plugin (`workflow@local-plugins`) and a prefixed one (`craft`) both define `brainstorm`, `refine`, `done`, etc.
2. **Substring/near-duplicate namespace** — one plugin's namespace is a suffix or prefix of another's own command namespace (e.g. plugin `workflow` vs. plugin `craft`'s `commands/workflow/*` subdirectory) — this is a structural signal even before checking individual command names, since it means an entire plugin may be redundant with a subset of another.

```bash
# Given two newline-separated basename lists, list1.txt and list2.txt:
comm -12 <(sort -u list1.txt) <(sort -u list2.txt)
```

Run this pairwise across all `C(N, 2)` plugin pairs. For N enabled plugins this is cheap (N is typically under 100).

**Progress indicator:** `[3/4] Collision detection ........ DONE (N collisions found)`

### Step 4: Report

```text
┌───────────────────────────────────────────────────────────────┐
│ PLUGIN AUDIT REPORT                                           │
├───────────────────────────────────────────────────────────────┤
│ Plugins enabled: N                                            │
│ Total commands+skills surfaced: M                             │
│ Collisions found: K                                           │
│                                                                │
│ [COLLISION] "brainstorm"                                      │
│   - workflow@local-plugins  commands/brainstorm.md            │
│   - craft@local-plugins     commands/workflow/brainstorm.md   │
│   Same base name, likely duplicate/redundant plugin.           │
│   Recommendation: review workflow@local-plugins for removal    │
│   (this skill does not remove it — human judgment call).       │
│                                                                │
│ [NAMESPACE OVERLAP] plugin "workflow" vs. craft's              │
│   commands/workflow/* subtree (14 shared base names)          │
│   Recommendation: confirm which is canonical before either     │
│   plugin's commands drift further apart.                       │
└───────────────────────────────────────────────────────────────┘
```

If zero collisions: report a clean audit explicitly (don't stay silent — silence reads as "didn't run" not "found nothing").

**Progress indicator:** `[4/4] Report ...................... SHOWN (K collisions)`

## Detecting the target class on a synthetic fixture

To sanity-check this skill's logic without touching real installed plugins, create two throwaway directories:

```text
/tmp/fixture-plugin-a/commands/brainstorm.md
/tmp/fixture-plugin-b/commands/workflow/brainstorm.md
```

Both have base name `brainstorm` — Step 3's `comm -12` on their basename lists should report exactly one collision. This mirrors the real `workflow@local-plugins` vs. `craft` finding from 2026-07-01 without requiring a live plugin install to reproduce.

## Error Recovery

| Situation | Recovery |
|-----------|----------|
| `~/.claude/settings.json` missing or unreadable | Report the path checked, stop — cannot proceed without it |
| `installed_plugins.json` absent | Fall back to manual/documented plugin paths; note the limitation in the report |
| A plugin's directory can't be resolved | List it as "surface unknown — skipped" rather than silently omitting it from the plugin count |
| Zero enabled plugins found | Report "no enabled plugins" rather than an empty table |

## See Also

- `skills/code/command-skill-token-efficiency/SKILL.md` — command-vs-skill placement *within* one plugin (a different axis: this skill compares *across* plugins)
- `skills/guard-audit/SKILL.md` — branch-guard rule tuning, a different config surface entirely
- `docs/specs/SPEC-token-efficiency-and-context-tooling-2026-07-01.md` Part D #3 — the finding and backlog item this skill implements
