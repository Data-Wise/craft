# Headless Recipes

`claude -p` runs Claude Code non-interactively — stdin gets the prompt, stdout gets the result.
Combine with `--allowedTools` to control which tools fire. Useful for CI, cron jobs, and release pipelines.

## Recipe 1 — Version reconcile

Finds and fixes stale version strings across docs and config after a release:

```bash
claude -p "Grep for version 2.53.0 across all docs and config files, update to 2.54.0" \
  --allowedTools "Edit,Read,Bash"
```

Run this after `bump-version.sh` to catch the long tail of version references the script misses.

## Recipe 2 — Count audit

Detects skill/command count drift between docs and the live plugin manifest:

```bash
claude -p "Run ./scripts/validate-counts.sh and fix any count mismatches in docs/" \
  --allowedTools "Read,Bash,Edit"
```

Safe to run anytime — `validate-counts.sh` is read-only; the Edit tool only fires if drift is found.

## Recipe 3 — Post-release doc sweep

Verifies all doc version references match `package.json` after a release:

```bash
claude -p "Verify all doc version references match the version in package.json; fix any that don't" \
  --allowedTools "Read,Edit,Bash"
```

Equivalent to running `./scripts/post-release-sweep.sh --fix` but with judgment — handles edge cases the script's regex misses.

## GitHub Actions example

Wire recipe 3 into a post-release workflow:

```yaml
- name: Post-release doc sweep
  env:
    ANTHROPIC_API_KEY: ${{ secrets.ANTHROPIC_API_KEY }}
  run: |
    claude -p "Verify all doc version references match ${{ env.VERSION }}; fix any that don't" \
      --allowedTools "Read,Edit,Bash" \
      --output-format text
```

Add this step after the GitHub Release creation step. Set `env.VERSION` from your version bump output.

## Useful flags

| Flag | Effect |
|------|--------|
| `--allowedTools "Read,Bash"` | Read-only mode — no file writes |
| `--allowedTools "Read,Edit,Bash"` | Allow edits but not new file creation |
| `--output-format text` | Plain text output (vs JSON) — better for CI logs |
| `--max-turns 5` | Cap the number of agentic turns (default: unlimited) |
| `--no-interactive-auth` | Fail if auth prompt would appear (CI-safe) |

## See also

- [`/release`](../commands/code/release.md) — full interactive release pipeline
- [`/craft:docs:update`](../commands/docs/update.md) — smart doc update with `--post-merge` mode
- [CI Triage & Watch](ci-triage-and-watch.md) — monitoring CI from Claude sessions
