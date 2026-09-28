# Craft OpenAI package

This directory contains a portable skills-first package for Codex and ChatGPT. The package is intentionally separate from Craft's Claude plugin runtime.

## Imported workflows

| Craft source | OpenAI skill | Disposition |
|---|---|---|
| commands/restore.md, skills/workflow/adhd-workflow/SKILL.md, skills/dev/git/SKILL.md | craft-restore | Adapted as a read-only recap; Craft-specific Obsidian behavior is omitted. |
| commands/finish.md, skills/workflow/adhd-workflow/references/done.md | craft-finish | Adapted for status capture; Claude settings, memory, sync, and detector integrations are omitted. |
| commands/do.md and its router dependencies | craft-do | Redesigned around Codex and repository instructions; Claude slash dispatch and orchestrator-v2 are not portable. |

Skills are the user-facing workflows. The Craft command files remain the Claude entry points and are not duplicated as OpenAI commands.

## Local test marketplace

`.agents/plugins/marketplace.json` exposes craft-openai for local installation. Add this `openai/` directory as the local marketplace root, then install and enable the plugin from Codex. After changing the package, refresh the marketplace and restart Codex before testing in a new chat.

## Limitations

The package has no automatic lifecycle hooks. It does not reproduce Craft's Claude command namespace, orchestrator-v2 agent behavior, Obsidian integration, or machine-local settings and memory operations.
