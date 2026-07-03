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
2. **`~/.claude/plugins/installed_plugins.json`** (if present) — richer per-plugin metadata (source path, marketplace, version) than `settings.json` alone provides. Treat as supplementary, not required — some installations only have `settings.json`. **Schema:** `{"version": 2, "plugins": {"<name>@<marketplace>": [{"installPath": "...", "version": "...", ...}]}}` — `.plugins` is an object keyed by `<name>@<marketplace>`, each value an ARRAY of install records (usually one). The on-disk path field is `installPath`, not `path`.
3. **Each enabled plugin's own directory** — resolve via `installed_plugins.json`'s recorded path, or `~/.claude/plugins/marketplaces/<marketplace>/<plugin>/` / `~/.claude/plugins/repos/...` (layout varies by install method: local marketplace vs. GitHub marketplace vs. Desktop). Within that directory, the actual surface is:
   - `commands/**/*.md` — each file's path (minus the `.md`) becomes a command name, namespaced as `<plugin>:<relative-path-without-ext>` (e.g. `commands/workflow/brainstorm.md` → `<plugin>:workflow:brainstorm`).
   - `skills/**/SKILL.md` — each `SKILL.md`'s parent directory name is the skill name, namespaced the same way.

## Audit procedure

Execute these steps in order.

### Step 1: Enumerate enabled plugins

```bash
jq -r '.enabledPlugins | to_entries[] | select(.value == true) | .key' ~/.claude/settings.json
```

Cross-reference against `installed_plugins.json` if present, to resolve each plugin's on-disk path. `.plugins` is keyed by `<name>@<marketplace>` with an array of install records per key — take the first record's `installPath`:

```bash
jq -r '.plugins | to_entries[] | "\(.key) -> \(.value[0].installPath // "unknown")"' ~/.claude/plugins/installed_plugins.json 2>/dev/null \
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

Compare every pair of enabled plugins' base-name lists. A raw basename intersection produces a false-positive firehose in practice — generic names (`status`, `init`, `check`, `sync`, `list`) legitimately recur across many unrelated plugins without being duplicates. Apply BOTH of the following filters; report a pair only if at least one fires:

1. **Breadth threshold (weak signals, need volume):** the pair shares **3 or more** basenames. A single coincidental shared word (e.g. two unrelated plugins both happen to have a `status` command) is NOT reported on its own — it's noise, not signal.
2. **Structural namespace containment (strong signal, 1 match is enough):** one plugin's own name/namespace (e.g. `workflow`) exactly matches a subdirectory name under another plugin's `commands/` or `skills/` tree (e.g. `craft`'s `commands/workflow/`). This is the actual `workflow@local-plugins` vs. `craft:workflow:*` bug pattern — one plugin's entire top-level surface duplicates a subtree of another — and it's reportable even with just one shared basename, because the containment itself is the finding, not the name overlap.

A single shared basename with NO structural containment relationship is a coincidence, not a collision — do not report it.

```bash
# Given two newline-separated basename lists, list1.txt and list2.txt:
comm -12 <(sort -u list1.txt) <(sort -u list2.txt)
# Apply the breadth threshold (>=3) OR the structural containment check above
# before treating the comm -12 output as a reportable finding.
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

Both have base name `brainstorm` — Step 3's `comm -12` on their basename lists finds one shared basename, and `fixture-plugin-b`'s command lives under a `workflow/` subdirectory matching `fixture-plugin-a`'s own name → structural containment fires → **reportable**, even though there's only one shared basename. This mirrors the real `workflow@local-plugins` vs. `craft` finding from 2026-07-01 without requiring a live plugin install to reproduce.

**Negative control (must NOT be flagged):** create two more throwaway directories that each define an unrelated `status` command with no structural relationship:

```text
/tmp/fixture-plugin-c/commands/status.md
/tmp/fixture-plugin-d/commands/status.md
```

One shared basename (`status`), no breadth (<3 shared names), no namespace containment (`status` isn't a subdirectory name in either plugin) → Step 3 must report **zero** collisions for this pair. If a run of this skill flags `fixture-plugin-c` vs. `fixture-plugin-d`, the breadth/containment filters have regressed back to the false-positive firehose this section exists to prevent.

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
