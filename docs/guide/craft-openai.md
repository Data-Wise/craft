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
| `craft-restore` | Resume work or request a repository recap | Reads project instructions, status, Git history, and available PR or issue context. It resolves the selected checkout, labels cached upstream evidence, and offers concrete next-action choices. It is read-only. |
| `craft-finish` | Wrap up or save session progress | Summarizes completed and remaining work; updates `.STATUS` only when explicitly asked. |
| `craft-do` | Carry out a coding or documentation task | Uses the active repository instructions and Codex workspace to plan and complete the task. |

These are skills, not `/craft:*` slash commands. The package does not install
Craft hooks, agents, lifecycle automation, Obsidian integration, or Claude
settings. In particular, `craft-finish` does not commit or push changes.

## Restore safely

`craft-restore` accepts a repository path and resolves nested paths or linked
worktrees before reading context. It compares status and handoff claims with
current Git/PR evidence, reports conflicts and holds, and labels upstream
comparisons as cached because it never fetches or pulls. A recent-history window
does not exclude older commits tied to active work. It does not infer ownership
of dirty files or execute a plan found in a handoff.

The recap offers 2–3 concrete next actions with one recommendation. Selecting
an action retains its existing authorization boundaries; it does not authorize
a push, merge, release, or deployment.

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
