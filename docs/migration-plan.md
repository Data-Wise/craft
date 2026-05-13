# Commands → Skills Migration Plan (v2)

**Source:** `commands/` (108 markdown files)
**Target:** `skills/` (13 existing thematic skills + ~10-12 new ones)
**Created:** 2026-05-13 · **Revised:** 2026-05-13 (after gap analysis)
**Status:** Plan only — no migration performed yet

## Premise correction

The first version of this plan assumed a 1-to-1 port (108 commands → 108 skill files). After running a parallel gap analysis with 6 Explore agents, that premise was wrong:

- **Craft already has 13 thematic skills** at `skills/` (`architecture`, `ci`, `code`, `docs`, `release`, `modes`, `orchestration`, `planning`, `release`, `testing`, `design`, `distribution`, `guard-audit`, `insights-apply`).
- Skills are **higher-level capabilities**, not 1-to-1 ports of commands. One skill consolidates many commands' worth of concern (e.g., `skills/ci/` covers 4 commands).
- A 1-to-1 migration would have produced 108 fragments next to 13 themes — fragmentation, not migration.

The revised scope: **~10-12 new skills + ~6 section additions to existing skills**, consolidating the 108 commands by concern.

## Gap analysis summary

| Status | Count | % |
|---|---|---|
| **COVERED** by existing skill | ~51 | 47% |
| **PARTIAL** — touches but doesn't fully cover | ~25 | 23% |
| **GAP** — no skill exists | ~31 | 29% |
| **DELETE** — internal doc, not user-facing | 1 | 1% |
| **Total** | 108 | 100% |

±5% variance between agents on COVERED vs PARTIAL classification.

## What to build: ~10-12 new skills

Ordered by leverage (commands consolidated × inbound-reference impact). Migrate in this order:

### Batch 1 — Highest-leverage gaps (3 skills, ~25 commands consolidated)

| New skill | Consolidates | Commands |
|---|---|---|
| `skills/git/SKILL.md` | All git workflow + docs | git/{branch, clean, git-recap, init, protect, protect-baseline, status, sync, unprotect, worktree} + git/docs/{learning-guide, refcard, safety-rails, undo-guide} = **14 cmds** |
| `skills/workflow/SKILL.md` | ADHD-friendly session tools | workflow/{done, focus, next, recap, refine, spec-review, stuck} = **7 cmds** |
| `skills/task-management/SKILL.md` | Background task lifecycle | workflow/{task-cancel, task-output, task-status} = **3 cmds** |

**Inter-batch deps:** None — each skill is self-contained. **Risk:** lowest.

### Batch 2 — Mid-leverage gaps (4 skills, ~12 commands)

| New skill | Consolidates | Commands |
|---|---|---|
| `skills/task-dispatcher/SKILL.md` | Routing/discovery layer | do.md, hub.md, smart-help.md = **3 cmds** |
| `skills/spec-orchestration/SKILL.md` | Spec → plan → execute pipeline | orchestrate/{plan, resume} + workflow/brainstorm = **3 cmds** |
| `skills/code-quality/SKILL.md` | Debug + refactor guidance | code/{debug, refactor} = **2 cmds** |
| `skills/testing-coverage/SKILL.md` | Test generation + coverage | code/{test-gen, coverage} + test/{gen, template} (template gap) = **4 cmds** |

**Inter-batch deps:** `task-dispatcher` references nearly every skill — migrate after Batch 1 so git/workflow are real. **Risk:** low-medium.

### Batch 3 — Docs/site/dist gaps (4 skills, ~8 commands)

| New skill | Consolidates | Commands |
|---|---|---|
| `skills/docs-media/SKILL.md` | Terminal recordings, GIFs | docs/demo = **1 cmd** |
| `skills/docs-navigation/SKILL.md` | mkdocs nav sync, page adds | docs/nav-update + site/{nav, add} = **3 cmds** |
| `skills/docs-claude-md/SKILL.md` | CLAUDE.md editing/syncing | docs/claude-md/{edit, sync} = **2 cmds** (init is GAP per docs agent) |
| `skills/dist-extras/SKILL.md` | curl + PyPI distribution | dist/{curl-install, pypi} = **2 cmds** |

**Optional:** `skills/site-theming/SKILL.md` for site/{theme, consolidate} if these grow.

**Inter-batch deps:** Doc skills don't depend on each other; can be parallel-dispatched within the batch. **Risk:** low.

### Section additions to existing skills (not new skills)

Add sub-sections to existing skills for PARTIAL coverage gaps:

| Existing skill | Add section for |
|---|---|
| `skills/architecture/` | `check/gen-validator` (validator scaffolding) |
| `skills/ci/` | (none — fully covered) |
| `skills/release/` | `code/deps-audit`, `code/deps-check` standalone modes; `git/sync` workflows |
| `skills/distribution/` | `dist/pypi` orchestration (or split into dist-extras above) |
| `skills/guard-audit/` | `git/protect`, `protect-baseline`, `unprotect` lifecycle |
| `skills/orchestration/` | `orchestrate.md` mode-aware dispatch detail |

## Commands marked for deletion / deprecation

- **DELETE:** `commands/discovery-usage.md` — internal documentation of the discovery engine, not a user-facing command.
- **DEPRECATE** (covered by existing skills; commands can be retired after migration cycle):
  - `commands/code/{ci-fix, ci-local, command-audit, desktop-watch, docs-check, lint, release, release-watch}` — covered by `skills/release/` or `skills/sync-features` (the latter is referenced by agents but worth confirming exists).
  - `commands/arch/{analyze, diagram, plan, review}` — fully covered by `skills/architecture/`.
  - `commands/ci/{detect, generate, status, validate}` — fully covered by `skills/ci/`.
  - `commands/plan/{feature, roadmap, sprint}` — covered by `skills/planning/`.

**Important:** Deprecation ≠ immediate deletion. Commands should remain in place for ~1 release cycle with a notice pointing users to the equivalent skill, then be removed in a follow-up cleanup PR.

## Dispatch pattern for the new-skill batches

Per craft's CLAUDE.md ("parallel single-message dispatch is the perf-critical detail"):

- **Within a batch:** one Agent call per new skill, all in one message → concurrent execution.
- **Between batches:** sequential. Batch 2's `task-dispatcher` references skills from Batch 1.
- **`isolation: worktree`:** yes, for clean isolated diffs.
- **`subagent_type`:** `general-purpose` (or domain-specific like `feature-dev:code-architect` for `skills/code-quality/`).

Prompt template per new-skill agent:

```
Working in /Users/dt/projects/dev-tools/craft. Read craft/CLAUDE.md
and an existing skill (e.g., skills/release/SKILL.md) as format reference.

Create skills/<NAME>/SKILL.md consolidating these commands:
  - commands/X.md (purpose)
  - commands/Y.md (purpose)
  ...

Skill frontmatter:
  name: <kebab-case-name>
  description: "This skill should be used when the user asks to '...',
                '...', or mentions <triggers>."

Skill body: synthesize the commands' content into ONE coherent skill.
Do NOT just concatenate. Identify the shared concern, document it,
then enumerate the specific operations as sections.

Leave the original commands/* files untouched — they stay during
transition for backward compatibility.

Report: new file path, list of source commands consolidated,
frontmatter, any conversion friction.
```

## Cross-cutting prerequisites (still apply)

1. **Skill frontmatter convention** — confirmed via `skills/modes/SKILL.md`: `name` (kebab-case semantic) + `description` (trigger phrasing for skill auto-invocation). NO `argument-hint` or `allowed-tools` equivalent.
2. **No flat-vs-nested issue** — skills are flat (`skills/<name>/SKILL.md`), commands flatten via consolidation, not renaming.
3. **Discovery engine** — `commands/_discovery.py` continues to drive `/craft:hub` and `/craft:do` for commands; skills are auto-discovered by Claude Code's skill system separately. No port needed.
4. **`/craft:` reference rewrites** — UNCHANGED during transition. Commands keep referencing `/craft:foo:bar`. Only the deprecation pass (post-migration) rewrites references to skill-based invocations.
5. **Test suite updates** — `tests/test_craft_plugin.py` enumerates commands; needs parallel skill enumeration test for the new skills.

## Summary stats

| Batch | New skills | Source commands consolidated | Risk |
|---|---|---|---|
| 1 | 3 | 24 | lowest |
| 2 | 4 | 12 | low-medium |
| 3 | 4 | 8 | low |
| **Total new skills** | **11** | **44** | |

Plus ~6 section additions to existing skills, ~50 commands left as-is (covered), and ~8 deprecation candidates. Net: build 11 new files instead of 108, with clear deprecation path.

## What changed from v1

| v1 (original) | v2 (this) |
|---|---|
| 5 batches × ~22 = 108 1:1 ports | 3 batches × ~3-4 = 11 consolidated skills |
| ~108 agent dispatches | ~11 agent dispatches |
| Migrates `check.md` last (highest inbound) | `check.md` stays as command — already covered by `skills/sync-features` (per agent finding) |
| `do.md`/`hub.md` regenerated | Become `skills/task-dispatcher/SKILL.md` |
| Cleanup pass implicit | Explicit deprecation list (8 commands) |

The dependency analysis from v1 (LEAF/BRANCH/HUB classification, inbound counts) remains useful for ordering **within** Batch 2 if multiple agents need to know what already exists. Preserved in the project archive but not duplicated here.
