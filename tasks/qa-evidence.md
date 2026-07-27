# QA Evidence: Issue #316

## Candidate Artifact

- Commit: `906c4f31f8f172e5ee2cc1a60afac536a8a3cc32`
- Git archive SHA-256:
  `09e349d54ec675422db2ba1fc51f8dada91de8bc4f7b994df3523999ccf7d81b`
- `preflight-check` SHA-256:
  `5ad202e5de58f90f679e42e5b853631a4c53067029026bc182fe36712847e514`
- Claude Code: `2.1.220`
- Codex CLI: `0.146.0-alpha.3.1`

## Claude Code

Loaded the archived plugin with `--plugin-dir` from:

`/tmp/craft-qa-906c4f31f/marketplace/craft`

Observed:

- `preflight-check` resolved to
  `/tmp/craft-qa-906c4f31f/marketplace/craft/skills/preflight-check/SKILL.md`.
- Default, thorough, and PR dry-run routes passed.
- `/craft:check --context` resolved the project, branch, worktree, base, and testing phase.
- `brainstorm`, `grill`, and `release` loaded independently.
- No files changed.

The non-interactive permission mode blocked validator execution and direct reads outside the
worktree. Archive extraction plus matching hashes bind the staged path to the candidate commit.

## Codex

Installed `craft@data-wise-craft` into disposable `CODEX_HOME` from:

`/tmp/craft-qa-906c4f31f/marketplace`

`codex debug prompt-input` confirmed these model-visible identities:

| Identity | Resolved path |
|---|---|
| `craft:preflight-check` | `/private/tmp/craft-qa-906c4f31f/codex/plugins/cache/data-wise-craft/craft/4.4.1/skills/preflight-check/SKILL.md` |
| `craft:brainstorm` | `/private/tmp/craft-qa-906c4f31f/codex/plugins/cache/data-wise-craft/craft/4.4.1/skills/workflow/brainstorm/SKILL.md` |
| `craft:grill` | `/private/tmp/craft-qa-906c4f31f/codex/plugins/cache/data-wise-craft/craft/4.4.1/skills/workflow/grill/SKILL.md` |
| `craft:release` | `/private/tmp/craft-qa-906c4f31f/codex/plugins/cache/data-wise-craft/craft/4.4.1/skills/release/SKILL.md` |

Each cached `SKILL.md` hash matched its staged marketplace source. A model call from the
disposable home was unavailable because credentials were intentionally not copied; the offline
prompt renderer verifies the exact skill inventory and paths the model would receive.
