# GRILL: Plugin Skill/Command Identity Hardening — Adversarial Review

**Date:** 2026-07-27  
**Target:** [`SPEC-plugin-skill-command-identity-hardening-2026-07-27.md`](SPEC-plugin-skill-command-identity-hardening-2026-07-27.md)  
**Source issue:** [#316](https://github.com/Data-Wise/craft/issues/316)  
**Review mode:** Fresh-context single-model adversarial review. Cross-model review skipped
after the user requested a brief, ADHD-friendly continuation.

## Claim Under Review

The draft claimed that renaming all nine mismatched skill directories to their frontmatter
names, split across two PRs, would align Claude Code and Codex while fixing the confirmed
`check` collision and preventing recurrence.

The claim did not survive review.

## Finding Reconciliation

| # | Severity | Finding | Classification | Resolution |
|---|---|---|---|---|
| 1 | Critical | Renaming `skills/code/` would also move three unrelated child skills | Valid + actionable | Cut the eight-directory normalization. Record `skills/code/SKILL.md` as a future file-only move constraint. |
| 2 | Critical | Collision inventory missed `commands/code/release.md` ↔ `skills/release/` | Valid + actionable | Inventory every command depth; baseline `release` with `brainstorm` and `grill`. |
| 3 | High | Nested skills may not be exposed by Claude Code even when names align | Valid + actionable | Split identity, discovery, auto-triggering, and explicit invocation into a measured client matrix. |
| 4 | High | Eight “normalization” moves were unclassified public API changes | Valid + actionable | Defer all eight moves to compatibility-design follow-ups; no rename in the hotfix PR. |
| 5 | High | Positive controls were temporary and tests were ordered after the fix | Valid + actionable | Require pure inventory helpers and committed fixture negatives before the production move. |
| 6 | High | Manual QA could inspect the globally installed plugin instead of the worktree | Valid + actionable | Require disposable Claude config and Codex marketplace staging, resolved paths, versions, and matching hashes. |
| 7 | High | `/craft:check` behavior preservation was not discriminatingly gated | Valid + actionable | Snapshot complete frontmatter and run a five-mode behavior matrix. |
| 8 | Medium | Broad zero-match gates cannot work for mixed category/skill paths such as `skills/code/` | Valid + actionable | Use exact retired-path mappings; only `skills/check` has a zero-match gate in this PR. |
| 9 | Medium | Collision exemptions lacked owner and terminal decision | Valid + actionable | Replace allowlist language with exact debt ledgers; require issue, owner, target release, and removal criterion. |
| 10 | Medium | The two-PR workflow left PR B's shape undecided | Valid + actionable | Lock one hotfix PR only. Defer compatibility migrations entirely instead of pretending PR B is ready. |

No finding was dismissed as noise. The review exposed a faulty implementation model, not merely
missing detail.

## Second-Cycle Reconciliation

A second fresh-context pass reviewed the re-scoped artifacts. It found eight remaining
contract defects; all were accepted and corrected.

| # | Severity | Finding | Resolution |
|---|---|---|---|
| 1 | Critical | A global zero-`skills/check` grep contradicted intentional SPEC/GRILL/fixture evidence | Scope the zero-reference gate to runtime/live docs with explicit evidence-file exclusions. |
| 2 | High | Basename-only collision ledger could not detect moved or duplicated collisions | Key by full command/skill paths and identity surfaces. |
| 3 | High | Directory-only comparison missed frontmatter-derived collisions | Compare command stems against both directory basename and frontmatter `name:`. |
| 4 | High | “Unchanged frontmatter” contradicted the required `replaced-by` edit | Snapshot the public argument contract; allow exactly the path-field change. |
| 5 | High | Mismatch ledger could not carry owner/target/removal metadata | Enrich every entry with ownership and closure fields. |
| 6 | High | #316 closure alternated between delegation and terminal decisions | Lock closure to terminal retain/rename/promote decisions. |
| 7 | Medium | Single-file hashes did not bind Codex QA to the complete artifact | Require clean committed `QA_SHA` plus whole-archive hash and staged SHA. |
| 8 | Medium | Five mode runs proved operability but not preservation | Add a normalized whole-command hash oracle to acceptance. |

The second cycle returned no reason to restore the rejected multi-directory normalization.

## Third-Cycle Reconciliation

The bounded final pass found three remaining contradictions:

1. Debt entries lacked explicit `owner`, `target_release`, and `decision` fields.
2. The GRILL closure gate still allowed delegation without a terminal decision.
3. Codex acceptance incorrectly called its archived disposable install the worktree.

All three are corrected. The ledger schema is now exact, issue closure requires terminal
retain/rename/promote decisions, and Codex QA resolves from a disposable staged installation
whose SHA and archive hash match the clean worktree commit.

## Locked Decisions

| # | Decision | Consequence |
|---|---|---|
| 1 | **Fix only `skills/check/` now:** move it to `skills/preflight-check/`; keep `/craft:check`. | The confirmed user-impacting ambiguity is removed without changing unrelated public identities. |
| 2 | **Do not rename the other eight mismatched skills in this implementation.** | They remain explicit debt, bounded by exact CI ledgers, until client compatibility is measured. |
| 3 | **Inventory all `commands/**/*.md`, not only flat commands.** | The existing nested `release` collision is visible and future nested collisions cannot bypass CI. |
| 4 | **Use permanent fixture tests and pure inventory helpers.** | New, stale, and nested inconsistencies are proven failure paths in CI rather than transcript-only planted defects. |
| 5 | **Treat identity, discovery, auto-triggering, and explicit invocation as separate client properties.** | A listing result cannot be used as proof of invocability, especially for nested skills. |
| 6 | **Preserve `/craft:check` with a full contract snapshot and five-mode QA matrix.** | The path migration cannot silently alter arguments, defaults, aliases, or representative behavior. |
| 7 | **Bind manual QA to the worktree artifact with versions, resolved paths, and hashes.** | Results from a stale globally installed craft version cannot satisfy acceptance. |
| 8 | **Keep #316 open until deferred debt has owner-bound terminal decisions.** | Merging the `preflight-check` hotfix alone cannot erase the remaining collision and mismatch work. |

## Final Implementation Scope

### In scope

1. Move `skills/check/` to `skills/preflight-check/`, including
   `references/gen-validator.md`.
2. Update every tracked `skills/check` reference.
3. Add pure inventory helpers and fixture-backed structural tests.
4. Baseline exactly eight remaining mismatches and three remaining collisions.
5. Snapshot `/craft:check` frontmatter and verify its representative behavior.
6. Probe the staged artifact in Claude Code and Codex with provenance evidence.
7. File owner-bound follow-ups for all deferred entries before PR handoff.

### Out of scope

1. Renaming the eight remaining mismatched skills.
2. Renaming `brainstorm`, `grill`, or `release`.
3. Removing slash-command shims.
4. Adding alias skill directories.
5. Changing command behavior, counts, or release version.

## Closure Gate

Issue #316 may close only when:

1. the `preflight-check` implementation PR is merged to `dev`;
2. staged-artifact QA passes in both clients;
3. the debt ledgers match repository state exactly;
4. every deferred collision and mismatch has an issue, owner, target release, terminal
   retain/rename/promote decision, and removal or retention criterion.

## Handoff

Implement from the revised SPEC only. The original nine-directory normalization is rejected
and must not be revived without a new compatibility review.
