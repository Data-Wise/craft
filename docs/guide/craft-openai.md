# Craft OpenAI Skills for Codex

The `craft-openai` package brings three Craft workflows to Codex as Agent
Skills. It is a skills-first local pilot, installed separately from the Claude
Craft plugin.

!!! info "Local pilot"
    Version 0.1.0 is not listed in a public Codex marketplace. Use a Craft
    checkout that contains `openai/craft-openai/`.

## Included skills

| Skill | Use it to | What it does |
|---|---|---|
| `craft-restore` | Resume work or request a repository recap | Reads project instructions, status, Git history, and available PR or issue context. It is read-only. |
| `craft-finish` | Wrap up or save session progress | Summarizes completed and remaining work; updates `.STATUS` only when explicitly asked. |
| `craft-do` | Carry out a coding or documentation task | Uses the active repository instructions and Codex workspace to plan and complete the task. |

These are skills, not `/craft:*` slash commands. The package does not install
Craft hooks, agents, lifecycle automation, Obsidian integration, or Claude
settings. In particular, `craft-finish` does not commit or push changes.

## Install from a local checkout

Use the `openai/` directory as the local marketplace root:

```sh
cd /path/to/craft/openai
codex plugin marketplace add "$PWD"
codex plugin add craft-openai@craft-openai-local
```

Restart Codex and start a new chat after installation. Confirm the plugin is
enabled with:

```sh
codex plugin list --marketplace craft-openai-local --json
```

The marketplace manifest is at `openai/.agents/plugins/marketplace.json`, and
the package instructions are in `openai/README.md` in the repository.

## Related integrations

- [Codex delegation plugin for Claude](../tutorials/TUTORIAL-codex-plugin.md)
  hands Claude Code tasks to Codex. It is a separate plugin with a different
  purpose and installation path.
- [Marketplace Distribution](marketplace-distribution.md) covers Craft's
  Claude Code marketplace release process.
