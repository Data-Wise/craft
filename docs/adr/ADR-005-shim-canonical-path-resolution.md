# ADR-005: Command-Shim Canonical-Path Resolution

**Status:** Accepted
**Date:** 2026-07-05 (executed 2026-07-23)
**Context source:** Issue #261 (`Command shims don't document how to resolve their own canonical-reference path`)

> **Execution note (2026-07-23):** the 12-file list in Context below is now stale — several of
> those files were renamed or removed between this ADR's drafting (2026-07-05) and execution
> (2026-07-23): `commands/done.md` → `commands/finish.md` (ADR-006 rename), `commands/orch/plan.md`
> / `commands/plan/roadmap.md` / `commands/plan/sprint.md` / `commands/git/init.md` /
> `commands/git/sync.md` / `commands/git/docs/{learning-guide,safety-rails,undo-guide}.md` no
> longer exist (folded into `skills/dev/git/SKILL.md` per the git-consolidation work). The actual
> set of thin shims carrying a bare relative canonical-procedure link at execution time was **6
> files**: `commands/finish.md`, `commands/refine.md`, `commands/grill.md`,
> `commands/brainstorm.md`, `commands/code/skill-standards.md`, `commands/code/command-audit.md`
> (the last two didn't exist on 2026-07-05 and were added to this ADR's scope, since they carry the
> identical defect). `commands/restore.md` (also created since 2026-07-05) was checked and found
> to have no bare skill-file relative link — it cites skills by name only, not by path, so it
> needed no change. `${CLAUDE_PLUGIN_ROOT}` provenance (open question below) was verified via the
> official Claude Code plugins-reference docs: platform-provided, reliably set regardless of
> session cwd. The standing-pattern requirement (Decision item 2) still applies to any future
> shim conversion.

> **Note:** ADR-002's own numbering note (line 7) states ADR-001 was "reserved... not yet written" at the time it was drafted (2026-06-23). That is now stale: `docs/adr/ADR-001-workflow-branch-guard.md` exists, Accepted, dated 2026-06-24, issue #171. `docs/adr/` currently runs ADR-001 through ADR-004; this is ADR-005. (A one-line correction to ADR-002's note is included in Consequences below, since this ADR is the first to touch that file again.)

---

## Context

ADR-002 established the thin-shim pattern: a `commands/workflow/*.md` file reduces to a short pointer, and the full procedure lives in `skills/workflow/adhd-workflow/references/*.md` (or the equivalent skill tree for other consolidations, e.g. `prompt-refiner` for `/refine`). ADR-002's own Consequences section already flagged the follow-up risk in one sentence: `/recap`, `/next`, `/focus`, `/stuck`, `/spec-review` "have the same latent divergence if any grows rich detail," deferred as out of scope.

Issue #261 surfaced a *different*, narrower defect in the shims ADR-002's pattern has since produced: the pointer path is a **bare relative markdown link** —

```
commands/done.md:18    [...](../skills/workflow/adhd-workflow/references/done.md)
commands/refine.md:19  [...](../skills/workflow/prompt-refiner/SKILL.md)
```

This resolves correctly only when the reader (human or agent) is looking at the **source repo checkout**. When `/craft:done` is invoked from a session whose cwd is a *different* repo (craft installed as a plugin), the only copy of `references/done.md` that exists on disk is inside the installed plugin cache, e.g.:

```
~/.claude/plugins/cache/data-wise/craft/2.58.0/skills/workflow/adhd-workflow/references/done.md
```

The relative link gives no way to derive that path. In practice this required a blind `find ~/.claude -iname "*adhd-workflow*"` sweep to locate the file (see issue #261 for the full incident).

**Re-auditing the whole `commands/` tree for this session's amendment found the actual scope is far wider than ADR-002 implied would eventually matter.** A search for the "thin shim" marker phrase (`grep -rl "thin shim" commands/`) currently returns 12 files, all already converted and all sharing the identical relative-link defect:

```
commands/done.md
commands/refine.md
commands/brainstorm.md
commands/grill.md
commands/orch/plan.md
commands/plan/roadmap.md
commands/plan/sprint.md
commands/git/init.md
commands/git/sync.md
commands/git/docs/learning-guide.md
commands/git/docs/safety-rails.md
commands/git/docs/undo-guide.md
```

`recap.md`, `next.md`, `focus.md`, and `stuck.md` are still full inline bodies with `deprecated: true` frontmatter — they are not yet thin shims and carry no canonical-path reference at all (`spec-review.md` likewise remains a full inline body, not yet converted). The "revisit if one accrues detail" deferral from ADR-002 covers those four remaining commands; this ADR's decision must be treated as the standing rule for every future shim conversion, not a one-off fix to two files — and must be applied now to all 12 already-converted shims above, not just `done.md` and `refine.md`.

**Precedent already exists in the repo for the alternative.** `${CLAUDE_PLUGIN_ROOT}` is already used, with a safe default, in two places:

```
commands/git/status.md:116            os.environ.get('CLAUDE_PLUGIN_ROOT', '.')
commands/git/status.md:288            PLUGIN_ROOT="${CLAUDE_PLUGIN_ROOT:-.}"
commands/git/protect-baseline.md:75   SCRIPT="${CLAUDE_PLUGIN_ROOT}/scripts/protect-baseline.sh"
```

**Provenance gap found while researching this ADR:** no file in the repo documents whether `CLAUDE_PLUGIN_ROOT` is a Claude Code platform-provided env var or something craft provisions itself. The only in-repo trace is a comment in `scripts/docs-lint.sh:12` — `# CLAUDE_PLUGIN_ROOT: Root of craft plugin (auto-detected)` — which asserts auto-detection without saying by what. `.claude-plugin/plugin.json` says nothing about it. This ADR does not resolve that gap; it flags it explicitly (see Consequences) so the next person doesn't rediscover it from scratch.

## Decision

**Adopt `${CLAUDE_PLUGIN_ROOT}` (with a `:-.`-style fallback to the current-repo-relative path) as the sanctioned resolution mechanism for every shim's canonical-reference pointer, and apply it retroactively to all 12 already-converted thin shims listed in Context.**

This is Option (b) from issue #261, chosen over (a) (spell out the plugin-cache path pattern inline — brittle, breaks on every version bump since the cache path is version-namespaced) and (c) (a one-line disclaimer note — doesn't actually fix resolution, just documents the friction).

1. Each of the 12 files (`commands/done.md`, `commands/refine.md`, `commands/brainstorm.md`, `commands/grill.md`, `commands/orch/plan.md`, `commands/plan/roadmap.md`, `commands/plan/sprint.md`, `commands/git/init.md`, `commands/git/sync.md`, `commands/git/docs/learning-guide.md`, `commands/git/docs/safety-rails.md`, `commands/git/docs/undo-guide.md`) changes its reference-path line from a bare relative link to a resolved path using the existing repo pattern, e.g.:

   ```
   ${CLAUDE_PLUGIN_ROOT:-.}/skills/workflow/adhd-workflow/references/done.md
   ${CLAUDE_PLUGIN_ROOT:-.}/skills/workflow/prompt-refiner/SKILL.md
   ```

   applied analogously to each remaining file's own reference target (each shim's own `../` or `../../` or `../../../`-relative link, per its depth in `commands/`).

   The `:-.` fallback preserves current behavior for anyone working directly in the source checkout (mirrors `commands/git/status.md:288`'s pattern exactly, rather than `protect-baseline.md:75`'s no-fallback version, since the shim must still degrade gracefully for source-repo contributors).

2. **This becomes the standing pattern for every future ADR-002-style shim conversion**, not just these twelve files. When `/recap`, `/next`, `/focus`, `/stuck`, or `/spec-review` are eventually converted to thin shims (per ADR-002's own deferred follow-up), the conversion checklist must include a `${CLAUDE_PLUGIN_ROOT}`-resolved pointer from the start — this ADR removes the need to rediscover the defect for each new conversion.
3. The `CLAUDE_PLUGIN_ROOT` provenance gap is recorded as an open question (see Consequences) rather than guessed at. If it turns out to be a Claude Code platform variable, this ADR's decision holds as-is. If craft turns out to provision it itself via some setup step, that provisioning must be confirmed reliable *before* shims depend on it — this should be checked as part of executing this ADR, not assumed.

## Alternatives Considered

1. **State the plugin-cache path pattern explicitly in each shim** (Option a from #261). Rejected — the plugin-cache path is version-namespaced (`.../craft/2.58.0/...`); hardcoding or even templating it invites drift on every release and doesn't help a reader who doesn't already know their installed version.
2. **One-line disclaimer note only** (Option c from #261). Rejected — resolves nothing; leaves the actual `find ~/.claude -iname ...` sweep as the only mechanism, just now an expected one instead of a surprising one.
3. **Do nothing until all remaining commands are converted, then fix once.** Rejected — all 12 already-converted shims are live now and the defect is live now; deferring a mechanical fix to bundle it with unrelated future conversions has no benefit and issue #261 is already filed against the current state.

## Consequences

- **Positive:** a single, already-precedented resolution pattern (`${CLAUDE_PLUGIN_ROOT:-.}`) replaces a broken relative-link assumption, fixing all 12 already-converted thin shims for any session invoking them from outside the craft repo.
- **Positive:** the pattern is now a documented requirement for any future ADR-002-style conversion, closing the gap before it recurs across `/recap`, `/next`, `/focus`, `/stuck`, `/spec-review`.
- **Cost / open question:** `CLAUDE_PLUGIN_ROOT`'s provenance (platform-provided vs. craft-provisioned) is undocumented anywhere in the repo. This ADR's fix depends on the variable being reliably set at invocation time in exactly the cross-repo scenario issue #261 describes. **This must be confirmed as part of executing this ADR** — if `CLAUDE_PLUGIN_ROOT` turns out to be unset or unreliable in a plugin-installed (non-source-checkout) session, the `:-.` fallback would silently resolve to the wrong path (the invoking repo's own root, not craft's), which is arguably worse than the current explicit failure. Verification (below) is written to catch this before it ships.
- **Correction to ADR-002:** its numbering note (line 7) says ADR-001 is "reserved... not yet written" — `ADR-001-workflow-branch-guard.md` now exists (Accepted, 2026-06-24). Recommend a one-line strikethrough/update to ADR-002 alongside this ADR's merge, since this is the first PR to touch that file again.

## Verification

- [x] Confirm `CLAUDE_PLUGIN_ROOT`'s actual provenance — verified 2026-07-23 via the official Claude Code plugins-reference docs (`https://code.claude.com/docs/en/plugins-reference.md`, "Environment variables" section): platform-provided, absolute path to the plugin's installation directory, reliably set regardless of session cwd for hooks/MCP/LSP subprocesses.
- [x] Update the reference-path line in each already-converted thin shim to the `${CLAUDE_PLUGIN_ROOT:-.}`-resolved path — the actual current set (see Execution note above) was 6 files, not the original 12: `commands/finish.md`, `commands/refine.md`, `commands/grill.md`, `commands/brainstorm.md`, `commands/code/skill-standards.md`, `commands/code/command-audit.md`. `commands/restore.md` checked, needed no change (no bare skill-file path link).
- [x] Standing-pattern requirement recorded in this ADR's Decision (item 2) — applies to any future ADR-002-style shim conversion.
- [x] One-line correction to ADR-002's stale ADR-001 numbering note (see below).
- [ ] `validate-counts.sh` and `docs-staleness-check.sh` clean after edits — run as part of this PR's pre-merge check.
