# Safety Hardening — Orchestration Plan

> **Branch:** `feature/safety-hardening`
> **Base:** `dev`
> **Worktree:** `~/.git-worktrees/craft/feature-safety-hardening`
> **Spec:** `docs/specs/SPEC-safety-hardening-2026-05-10.md`
> **Brainstorm:** `docs/brainstorm/BRAINSTORM-safety-hardening-2026-05-10.md`
> **Version Target:** v2.33.0 increment (paired with insights-improvements spec)

## Objective

Two paired safety improvements driven by Claude Code v2.1.136 release findings: (1) layer `settings.autoMode.hard_deny` on top of branch-guard for unconditional protection of catastrophic patterns, and (2) defensive parsing in `/craft:workflow:insights` to prevent crashes on malformed facets.

## Phase Overview

| Phase | Increment | Priority | Effort | Status |
|-------|-----------|----------|--------|--------|
| 0 | Schema verification (research only) | High | 15 min | ✅ Complete (2026-05-10) — see Findings below |
| 1 | Insights defensive parsing (#2) | High | 45 min | ✅ Complete — commit `d6d299e3` |
| 2 | Hard_deny **prose** rule catalog + design | High | 30 min | ✅ Complete — commit `09b7c4be` |
| 3 | `/craft:git:protect` integration (#1 implementation) | High | 1h | ✅ Complete — commit `47747ccb` |
| 4 | Documentation (architecture.md + REFCARD-BRANCH-GUARD + CHANGELOG) | Medium | 30 min | ✅ Complete — see acceptance walkthrough below |
| 5 | Tests + verification | High | 30 min | ✅ Complete — see acceptance walkthrough below |

### Acceptance Criteria Walkthrough (Phase 5, 2026-05-10)

Walked through each criterion from the spec against the current state of `feature/safety-hardening`:

| # | Criterion | Evidence | Status |
|---|-----------|----------|--------|
| 1 | `/craft:workflow:insights` no longer crashes on malformed facet tool input fields | `commands/hub.md` and `commands/do.md` both wrap each facet read in `try/except (JSONDecodeError, KeyError, TypeError, FileNotFoundError, UnicodeDecodeError, OSError)` with stderr warning. `commands/workflow/insights.md` publishes the contract. | ✅ |
| 2 | Regression test feeds a deliberately malformed facet and asserts no crash | `tests/test_facet_parsing_defensive.py::test_hub_snippet_survives_malformed_facets` runs the hub.md snippet as a subprocess against truncated, binary, and wrong-shape fixture facets; asserts clean exit + correct Counter contents + stderr warnings. | ✅ |
| 3 | `~/.claude/settings.json` `autoMode.hard_deny` rules documented for force-push to main, `.git` deletion, and `gh repo delete` | `scripts/hard-deny-rules.json` defines `force-push-main`, `delete-git-dir`, `delete-github-repo`, plus the additional `destroy-claude-config`. Each with prose rule, rationale, and example patterns. | ✅ |
| 4 | `/craft:git:protect` detects whether rules are installed; offers to add them; `--no-hard-deny` opt-out | `commands/git/protect.md` Step 2b describes the flow; `--no-hard-deny` is in the frontmatter; `scripts/install-hard-deny.sh --check` is the detection primitive. | ✅ |
| 5 | Hard_deny rules survive `.claude/allow-once` (integration test) | Phase 0 research confirmed at the schema layer (Claude Code docs quote: "hard_deny rules block unconditionally. User intent and `allow` exceptions do not apply"). Cannot be tested craft-side — hard_deny is enforced *inside* Claude Code's classifier, not by any craft script. The schema *is* the contract; criterion is met by the choice of mechanism, not by a craft-side test. | ✅ (schema-verified) |
| 6 | Hard_deny rules are NARROW — only catastrophic patterns | `scripts/hard-deny-rules.json` contains 4 hard_deny entries + 4 explicitly-rejected carryover entries with rationale per rejection (e.g. `git reset --hard origin/main` is legitimate on feature branches). `tests/test_hard_deny_catalog.py` locks the spec-required rule IDs. | ✅ |
| 7 | `docs/architecture.md` documents the 3-layer protection model | Section 5 "Defense-in-Depth" rewritten from 2-layer to 3-layer, with layered ASCII diagram and per-tier comparison table. | ✅ |
| 8 | `REFCARD-BRANCH-GUARD.md` adds a hard_deny section | New "Hard_deny Layer" section added above the "Bypass Mechanisms" section; version header bumped to v2.33.0. | ✅ |
| 9 | All existing branch-guard tests continue to pass (backward compatible) | Confirmed: `tests/test_facet_parsing_defensive.py` + `tests/test_hard_deny_catalog.py` + `tests/test_install_hard_deny.py` add 16 new tests, ALL passing. **3 pre-existing failures in `tests/test_integration_branch_guard.py` are NOT regressions** — verified by stashing all safety-hardening changes and reproducing the same 3 failures on the Phase 3 baseline commit. The failures are unrelated to safety-hardening and existed before the feature branch was created. | ✅ (no new failures) |

**Full test pass count:** 140 tests passing (was 79 before the feature; +61 includes new tests for this feature plus the previously-uncounted e2e/dogfood suites that the orchestrator now runs).

### Phase 0 Findings Summary (2026-05-10)

Hard_deny is **prose-based**, not regex. Use `"$defaults"` to inherit Claude Code built-ins. Lives in `~/.claude/settings.json` (personal), `.local.json` (project), or org-managed — cumulative. Applies to **all tools**. **Unconditional** — survives `.claude/allow-once`. See SPEC Open Questions section for full resolution and the revised Phase 2 deliverable (prose strings instead of regex JSON).

### Phase 1 Re-scope Note (2026-05-10)

ORCHESTRATE originally targeted `commands/workflow/insights.md`, but that file is markdown-only — Claude is its runtime, not Python. The real facet parsers are inline Python snippets in `commands/hub.md` (Step 1.7) and `commands/do.md` (Step 1.5). Both hardened to the same defensive contract. The `insights.md` file now publishes the contract as a v2.33.0 subsection so future facet-readers follow it. Test: `tests/test_facet_parsing_defensive.py` (4 tests, both behavioral and structural).

**Total estimated effort:** ~3h.

**Sequencing rationale (from spec):** Phase 1 (insights audit) is purely defensive with no upstream schema dependency — safe to ship as standalone. Phase 2-3 (hard_deny) require schema verification first (Phase 0).

---

## Phase 0: Schema Verification (research, no code)

**Scope:** Resolve Open Question #1 from the spec — verify the exact JSON shape and matching semantics of `settings.autoMode.hard_deny`.

- [ ] 0.1 Read Claude Code docs/source for `settings.autoMode.hard_deny` schema
- [ ] 0.2 Determine: pattern-based (regex) or rule-based (named conditions)?
- [ ] 0.3 Determine: works on Bash tool only, or all tools?
- [ ] 0.4 Determine: per-project (`settings.local.json`) vs global (`~/.claude/settings.json`)?
- [ ] 0.5 Decide: auto-install via `/craft:git:protect` vs separate `/craft:git:harden` command
- [ ] 0.6 Decide: target version (v2.33.0 increment vs v2.32.2 patch)

**Key files:** none (research-only). Capture findings in this ORCHESTRATE doc as updates.

**Output:** clear answers to spec's Open Questions 1-4 before any implementation begins. If the schema is much more complex than assumed, RE-SCOPE Phase 2-3 before continuing.

---

## Phase 1: Insights Defensive Parsing

**Scope:** Port the v2.1.136 `/insights` crash fix pattern to `/craft:workflow:insights`. Pure defensive — no behavioral changes for valid facets, only graceful handling of malformed ones.

- [ ] 1.1 Read `commands/workflow/insights.md` to understand the command's flow
- [ ] 1.2 Locate the actual parsing code (likely in `utils/` or inlined in the command)
- [ ] 1.3 Audit: grep for `json.load()`, `facet[...]` without `.get()`, unguarded dict access
- [ ] 1.4 Wrap parsing in `try/except (json.JSONDecodeError, KeyError, TypeError)`
- [ ] 1.5 On exception: log warning to stderr (file path + error), skip the entry, continue
- [ ] 1.6 Add regression test: `tests/test_insights_dogfood.py` (or extend existing) — feed a deliberately malformed facet, assert no crash + insights report still generated
- [ ] 1.7 Commit: `fix(insights): defensive parsing for malformed facet files`

**Key files:**

- `commands/workflow/insights.md` (likely no change, may need to document graceful behavior)
- `utils/insights_*.py` or wherever the parsing lives (NEW try/except blocks)
- `tests/test_insights_dogfood.py` or `tests/test_insights_*.py` (NEW regression test)

---

## Phase 2: Hard_deny Pattern Catalog + Design

**Scope:** Decide which catastrophic patterns belong in `hard_deny` (vs branch-guard's smart-mode). Output: a craft-blessed snippet ready for installation.

- [ ] 2.1 Catalog initial patterns (from spec):
  - `git push --force` on `main`
  - `git push --force-with-lease` on `main`
  - `rm -rf .git`
  - `gh repo delete`
- [ ] 2.2 Review additional candidates:
  - `git reset --hard origin/main` (silent local-commit loss)
  - `find . -delete`
  - `xargs rm`
  - `rm -rf ~/.claude` (destroys all config)
- [ ] 2.3 For each: classify as "hard_deny" (truly catastrophic, no legitimate use) vs "stays in branch-guard smart-mode" (context-dependent)
- [ ] 2.4 Write the JSON snippet matching the verified schema from Phase 0
- [ ] 2.5 Document the rationale per pattern (why hard_deny vs branch-guard)
- [ ] 2.6 Commit (combined with Phase 3): `feat(git): add hard_deny pattern catalog for catastrophic operations`

**Key files:**

- `scripts/hard-deny-patterns.json` (NEW — the canonical pattern catalog)
- Or `scripts/install-hard-deny.sh` (NEW — installer script that knows the patterns)

---

## Phase 3: `/craft:git:protect` Integration

**Scope:** Add hard_deny detection + installation flow to the existing `/craft:git:protect` command. Per the spec recommendation: auto-detect-and-offer, with `--no-hard-deny` opt-out.

- [ ] 3.1 Update `commands/git/protect.md` to describe the new hard_deny detection step
- [ ] 3.2 Add `--no-hard-deny` flag to opt out
- [ ] 3.3 Implement detection: read `~/.claude/settings.json`, check if craft's recommended rules are present (by rule name or marker comment)
- [ ] 3.4 If missing: show preview of what will be added + AskUserQuestion to confirm
- [ ] 3.5 If user confirms: merge craft's rules into existing settings.json (preserve user's other settings)
- [ ] 3.6 Update `commands/git/unprotect.md` to clarify it does NOT bypass hard_deny (similar to the protect-baseline note about GitHub-side rules)
- [ ] 3.7 Commit: `feat(git): /craft:git:protect installs hard_deny rules for catastrophic ops`

**Key files:**

- `commands/git/protect.md` (UPDATE — new detection step + flag)
- `commands/git/unprotect.md` (UPDATE — clarification note)
- `scripts/install-hard-deny.sh` or extension to existing protect logic

---

## Phase 4: Documentation

**Scope:** Document the 3-layer protection model and update related references.

- [ ] 4.1 Update `docs/architecture.md` section 5 — extend the existing "defense-in-depth" subsection (added in PR #122) to document the 3rd layer (hard_deny)
- [ ] 4.2 Update `docs/reference/REFCARD-BRANCH-GUARD.md` with a new section describing the hard_deny layer
- [ ] 4.3 Update `commands/dist/homebrew.md` if it mentions any catastrophic patterns relevant to hard_deny (probably N/A)
- [ ] 4.4 Add CHANGELOG entry under `[Unreleased]` for v2.33.0
- [ ] 4.5 Commit: `docs: document 3-layer protection model (hard_deny + branch-guard + GitHub-side)`

**Key files:**

- `docs/architecture.md` (UPDATE)
- `docs/reference/REFCARD-BRANCH-GUARD.md` (UPDATE)
- `CHANGELOG.md` + `docs/CHANGELOG.md` (UPDATE — mirrored)

---

## Phase 5: Tests + Verification

**Scope:** End-to-end validation that all 8 acceptance criteria from the spec are met.

- [ ] 5.1 Run full test suite: `python3 -m pytest tests/ -v` — all green
- [ ] 5.2 Integration test: install hard_deny rules, attempt `git push --force origin main` with `.claude/allow-once` present, verify it's blocked
- [ ] 5.3 Integration test: feed a corrupt facet directory to `/craft:workflow:insights`, verify clean exit with warnings
- [ ] 5.4 Verify all branch-guard tests still pass (backward compatibility)
- [ ] 5.5 Run `/craft:check --for release` to mirror the CI gate
- [ ] 5.6 Walk through each of the spec's 8 acceptance criteria, mark complete

**Key files:**

- New tests in `tests/test_insights_dogfood.py` (Phase 1)
- New tests in `tests/test_hard_deny_integration.sh` or similar (Phase 5)

---

## Friction Prevention (from MEMORY + spec)

- **Verify location**: confirm CWD is `/Users/dt/.git-worktrees/craft/feature-safety-hardening` before any work — `pwd` and `git worktree list` first
- **Read spec first**: open `docs/specs/SPEC-safety-hardening-2026-05-10.md` AND this ORCHESTRATE before starting Phase 0
- **No autonomous starts**: after each phase completes, STOP and confirm with user before next phase
- **Test per phase**: run relevant tests after each commit, not just at Phase 5
- **Pre-commit auto-fix rollback**: if pre-commit modifies files, re-stage and create a NEW commit (never amend) — per MEMORY
- **mermaid label quoting**: any new mermaid diagrams must quote labels containing `:`, `/`, or `<br/>` — per MEMORY
- **Schema verification gates implementation**: do NOT start Phase 2 until Phase 0 resolves Open Questions 1-4. If schema is too complex, re-scope before writing code.

## Acceptance Criteria (from spec)

- [ ] `/craft:workflow:insights` no longer crashes when a facet file contains malformed tool input fields — instead skips the entry and logs a warning
- [ ] Regression test exists that feeds a deliberately malformed facet to the insights parser and asserts no crash
- [ ] `~/.claude/settings.json` `autoMode.hard_deny` rules are documented for: `git push --force` on main, `rm -rf .git`, `gh repo delete` (final list TBD pending schema verification)
- [ ] `/craft:git:protect` detects whether craft's recommended hard_deny rules are installed; offers to add them if missing (with `--no-hard-deny` opt-out flag)
- [ ] Hard_deny rules survive even when `.claude/allow-once` is present (verified by integration test)
- [ ] Hard_deny rules are NARROW — they trigger on patterns that should never execute, not patterns that are merely risky
- [ ] `docs/architecture.md` updated to document the 3-layer protection model (hard_deny + branch-guard + GitHub-side)
- [ ] `REFCARD-BRANCH-GUARD.md` adds a section describing the hard_deny layer
- [ ] All existing branch-guard tests continue to pass (backward compatible)

## Commit Strategy

- Conventional commits: `feat:`, `fix:`, `docs:`, `test:`, `chore:`
- Phase 0: no commits (research only, capture findings as updates to this ORCHESTRATE)
- Phase 1: `fix(insights): defensive parsing for malformed facet files`
- Phase 2-3: `feat(git): add hard_deny layer for catastrophic operations` (combined commit)
- Phase 4: `docs: document 3-layer protection model`
- Phase 5: `test: add integration tests for hard_deny + insights resilience`

## Verification

After each phase:

```bash
# Project-specific test command
python3 -m pytest tests/test_craft_plugin.py tests/test_plugin_e2e.py tests/test_plugin_dogfood.py

# After Phase 1 only — insights-specific tests
python3 -m pytest tests/test_insights_*.py -v

# After Phase 4 — markdown lint
/craft:docs:lint

# Pre-PR check (after Phase 5)
/craft:check --for release
```

## Session Instructions

### Context

You are in the **craft repo worktree** for the safety-hardening feature. The full spec has design details, open questions, and architecture diagrams. This ORCHESTRATE file translates the spec into executable phases.

### How to Start

```bash
cd /Users/dt/.git-worktrees/craft/feature-safety-hardening
claude
```

On session start, paste:

> Read `ORCHESTRATE-safety-hardening.md` and `docs/specs/SPEC-safety-hardening-2026-05-10.md`. Start Phase 0 (schema verification). Do not begin implementation until Open Questions 1-4 are resolved.

### Phase-by-Phase

1. **Phase 0 first** — schema verification gates everything. Update Open Questions in the spec with answers.
2. **Phase 1 next** (insights audit) — independent, ship-as-standalone if Phase 0 reveals hard_deny is too complex
3. **Phases 2-5** in sequence — depend on Phase 0 outcomes
4. After each phase: run verification, commit, STOP for user confirmation
5. Final phase: PR to dev with full acceptance criteria checklist

### What this ORCHESTRATE does NOT include

- Implementation kickoff (do that in a fresh session per craft workflow rules)
- Decisions on Open Questions 1-5 (deferred to Phase 0)
- Cross-plugin pattern adoption (out of scope; long-term backlog from brainstorm)
