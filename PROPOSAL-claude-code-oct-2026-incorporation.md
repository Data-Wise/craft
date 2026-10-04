# PROPOSAL: Incorporate Claude Code changes (Aug–Oct 2026) into craft

Updated 2026-10-03 after verification. Source of the first draft was a subagent report;
items marked UNVERIFIED are not confirmed by an official source.

## Verified

- **v2.1.288 hook fix** (quoted from release notes): "Fixed PreToolUse and PermissionRequest hooks
  being skipped when matching them failed or the tool's input could not be serialized to JSON; the
  call is now blocked". Not in v2.1.289.
- **Hook audit (done):** branch-guard.sh, pretooluse.py, session-facet.sh, orchestrate-hooks.sh —
  12 runs (empty/garbage/valid stdin), all exit 0 with no stdout; positive control (branch-guard,
  `git commit` on main) exits 2. None emit JSON, so unaffected. Not covered: Write/Edit-shaped
  payloads for pretooluse.py, orchestrate-hooks.sh post-agent args.
- **plugin.json:** 4 keys (name, version, description, author). tests/test_plugin_dogfood.py:399-409
  allowlist rejects `metadata`/`userConfig`. Recommendation: do not add.

- **Docs + local CLI (2026-10-03):** `claude plugin eval` is stable, `--json` has `schemaVersion: 1`
  (confirmed in a real run). Manifest accepts `metadata`, `userConfig.options`, `experimental.evals`.
- **Eval spike (feature/plugin-eval-spike, commit 9845eeaff, local only):** 3 cases, 1 run each,
  ~$1.05 total. modes-lookup and preflight-check-scope discriminate (with 1 / without 0);
  release-skill-trigger does not (delta 0). Gotchas: default publishes the report to claude.ai
  (pass --no-publish); allowed_tools must be [Skill] or the baseline reads repo files; the
  `skill-invoked` grader reported 0 calls on two passing cases (meaning unclear).

## UNVERIFIED

- Mods `agent.spawn` stability.

## Remaining work

1. [x] Eval spike done (see above). [ ] Make release-skill-trigger discriminating; investigate `skill-invoked` 0x.
2. [x] Eval GA + manifest fields confirmed.
3. [ ] Optional: extend hook audit to Write/Edit payloads and post-agent args.

## Not applicable

MCP OAuth re-auth (craft MCP is stdio-only); managed-settings, auto-mode, allowedProviders; Mods (defer).

## Outcome (2026-10-03)

- Eval spike became PR [#356](https://github.com/Data-Wise/craft/pull/356) (merged, `86f218e89`): wrapper, 11 trigger evals,
  3 body cases, guide. Body-recall cases for nested skills cannot pass with `[Skill]` only; see `tasks/plan.md` in that PR.
- Hook audit and manifest findings above stand; `metadata`/`userConfig` still not added to `plugin.json`.
- Remaining: command-routing evals for the 30 nested skills; stabilize `trigger-hooks` (scored [0,1,1]).
