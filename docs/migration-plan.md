# Commands → Skills Migration Plan

**Source:** `commands/` (108 markdown files)
**Target:** `skills/` (skill format with `SKILL.md` per skill)
**Created:** 2026-05-13
**Status:** Plan only — no migration performed yet

## Note on batch sizing

The request was "5 batches of ~10 commands each." There are **108 commands**, so 5 batches at ~10 covers fewer than half. This plan uses **5 batches of ~22 each** (total 108) so every command is accounted for. Adjust by splitting any batch further if a smaller working unit is preferred.

## Ordering principle

Dependencies were extracted by grepping `/craft:<name>` references inside command bodies (any reference counts — code-fence or prose). Each command is classified:

- **LEAF** — references no other craft commands (24 commands). Safest to migrate first.
- **BRANCH** — 1–3 light deps (10 commands).
- **HUB** — 4+ deps or high inbound-reference count (74 commands). Ordered by ascending **inbound** count so commands that many others depend on are migrated **last** (e.g. `check.md` has 30 inbound refs).

No external/dangling references — every `/craft:` reference resolves to a file in the tree.

---

## Batch 1 — Pure LEAVES, part 1 (22 commands)

Zero dependencies. Migrate first; no risk of breaking references.

| Command | Purpose |
|---|---|
| `code/debug.md` | Debug assistance |
| `code/demo.md` | Code demonstration |
| `code/docs-check.md` | Documentation & website pre-flight check |
| `code/refactor.md` | Refactoring guidance |
| `code/test-gen.md` | Generate tests |
| `discovery-usage.md` | Discovery engine usage guide |
| `git/docs/learning-guide.md` | Git commands learning guide |
| `git/docs/refcard.md` | Git commands quick reference |
| `git/docs/undo-guide.md` | Git undo guide |
| `git/git-recap.md` | Git activity summary |
| `site/docs/frameworks.md` | Documentation framework comparison |
| `site/init.md` | Initialize documentation site |
| `site/preview.md` | Preview documentation locally |
| `utils/readme-semester-progress.md` | Semester progress calculation utilities |
| `utils/readme-teach-config.md` | Teaching configuration parser |
| `workflow/adhd-guide.md` | ADHD-friendly workflow guide |
| `workflow/focus.md` | Single-task mode |
| `workflow/next.md` | Decision support |
| `workflow/recap.md` | Context restoration |
| `workflow/refine.md` | Prompt optimizer |
| `workflow/stuck.md` | Unblock helper |
| `workflow/task-cancel.md` | Cancel background task |

**Inter-batch deps:** none. **Risk:** lowest.

---

## Batch 2 — Remaining LEAVES + light BRANCHES + low-inbound utilities (22 commands)

Tail of the LEAF list, then commands with 1–3 narrow deps and minimal inbound exposure.

| Command | Class | Deps | Notes |
|---|---|---|---|
| `workflow/task-output.md` | LEAF | — | Background task results |
| `workflow/task-status.md` | LEAF | — | Background task status |
| `code/release-watch.md` | HUB | 4 deps, inbound 2 | Low inbound, isolated |
| `dist/pypi.md` | HUB | 4 deps, inbound 2 | Low inbound |
| `workflow/insights.md` | HUB | 5 deps, inbound 1 | Only `/done` references it |
| `smart-help.md` | HUB | 19 deps, inbound 1 | Only inbound from `do.md` |
| `code/release.md` | BRANCH | `/craft:check` | Single dep |
| `git/docs/safety-rails.md` | BRANCH | `/craft:git:protect`, `/craft:git:unprotect` | Docs-only |
| `ci/status.md` | BRANCH | `/craft:ci:status`, `/craft:ci:validate` | |
| `docs/mermaid.md` | BRANCH | `/craft:docs:check`, `/craft:docs:mermaid`, `/craft:site:status` | |
| `git/clean.md` | BRANCH | `/craft:git:clean`, `/craft:git:protect-baseline`, `/craft:git:worktree` | |
| `check/gen-validator.md` | BRANCH | `/craft:check`, `/craft:check:gen-validator` | Generates validators |
| `orchestrate/resume.md` | BRANCH | `/craft:orchestrate`, `/craft:orchestrate:plan` | |
| `workflow/done.md` | BRANCH | `/craft:docs:sync`, `/craft:workflow:insights` | |
| `workflow/spec-review.md` | BRANCH | `/craft:do`, `/craft:docs:update` | |
| `workflow/brainstorm.md` | BRANCH | `/craft:docs:workflow`, `/craft:orchestrate:plan` | |
| `plan/roadmap.md` | HUB | 3 deps, inbound 4 | Planning command |
| `plan/sprint.md` | HUB | 3 deps, inbound 4 | Planning command |
| `plan/feature.md` | HUB | 5 deps, inbound 5 | Planning command |
| `test/template.md` | HUB | 4 deps, inbound 3 | Jinja2 templates |
| `test/gen.md` | HUB | 4 deps, inbound 5 | Test generation |
| `docs/claude-md/init.md` | HUB | 4 deps, inbound 4 | CLAUDE.md scaffolding |

**Inter-batch deps:**

- `code/release.md` references `check.md` — still in original form until Batch 5; safe (still works).
- `workflow/done.md`, `workflow/spec-review.md`, `workflow/brainstorm.md` reference `docs/sync`, `docs/update`, `docs/workflow` — all still in `commands/` until Batch 3–4.
- Migration order **within** batch: do LEAVES first, then ascending-inbound BRANCHES.

**Risk:** low — references will continue resolving to `commands/` form during transition.

---

## Batch 3 — Architecture, dist, claude-md, plan (22 commands)

Mid-tier HUBs with 4–10 inbound references. Isolated functional areas.

| Command | Inbound | Deps |
|---|---|---|
| `arch/analyze.md` | 6 | 5 |
| `arch/diagram.md` | 6 | 5 |
| `arch/review.md` | 6 | 6 |
| `arch/plan.md` | 8 | 5 |
| `dist/curl-install.md` | 5 | 4 |
| `dist/marketplace.md` | 4 | 4 |
| `dist/homebrew.md` | 6 | 6 |
| `docs/claude-md/edit.md` | 4 | 8 |
| `docs/claude-md/sync.md` | 4 | 4 |
| `git/init.md` | 2 | 11 |
| `git/protect.md` | 5 | 4 |
| `git/protect-baseline.md` | 9 | 4 |
| `git/unprotect.md` | 10 | 8 |
| `git/status.md` | 10 | 7 |
| `git/branch.md` | 10 | 7 |
| `ci/detect.md` | 5 | 6 |
| `ci/generate.md` | 6 | 7 |
| `ci/validate.md` | 8 | 6 |
| `code/command-audit.md` | 6 | 8 |
| `code/desktop-watch.md` | 7 | 7 |
| `code/deps-audit.md` | 7 | 4 |
| `orchestrate/plan.md` | 7 | 4 |

**Inter-batch deps:**

- `arch/*` commands depend on `check.md` (Batch 5) and `docs/sync` (Batch 4). Safe during transition.
- `dist/*` commands depend on `code/release.md` (Batch 2 ✓) and `check.md` (still in commands/).
- `git/init.md` and `git/branch.md` depend on `git/worktree.md` (Batch 5) — still in commands/.

**Risk:** low–medium. Test cross-tree references after each migration.

---

## Batch 4 — Docs & site infrastructure (22 commands)

Documentation generators and site tooling. Many cross-reference each other.

| Command | Inbound | Deps |
|---|---|---|
| `docs/sync.md` | 12 | 4 |
| `docs/prompt.md` | 15 | 19 |
| `docs/help.md` | 15 | 19 |
| `docs/site.md` | 15 | 18 |
| `docs/website.md` | 15 | 17 |
| `docs/api.md` | 16 | 16 |
| `docs/quickstart.md` | 16 | 18 |
| `docs/workflow.md` | 16 | 18 |
| `docs/demo.md` | 17 | 20 |
| `docs/guide.md` | 17 | 16 |
| `docs/tutorial.md` | 17 | 17 |
| `docs/nav-update.md` | 17 | 19 |
| `docs/update.md` | 13 | 13 |
| `site/theme.md` | 12 | 13 |
| `site/add.md` | 12 | 13 |
| `site/audit.md` | 13 | 13 |
| `site/consolidate.md` | 13 | 13 |
| `site/nav.md` | 13 | 13 |
| `site/create.md` | 14 | 15 |
| `site/progress.md` | 14 | 14 |
| `site/publish.md` | 15 | 14 |
| `site/deploy.md` | 16 | 13 |

**Inter-batch deps:**

- All commands here depend heavily on each other AND on `docs/lint.md`, `docs/check.md`, `docs/check-links.md`, `docs/changelog.md`, `site/build.md`, `site/check.md`, `site/status.md` — those are deferred to Batch 5 because of their very high inbound counts (18–21).
- **Migrate intra-batch in inbound order** (lowest first: `docs/sync`, then `docs/prompt/help/site/website`, …, ending with `site/deploy`).

**Risk:** medium. Big tangle of cross-refs. Recommend smoke-testing `/craft:docs:update` and `/craft:site:create` after the batch lands.

---

## Batch 5 — High-inbound hubs and entrypoints (20 commands)

The most-referenced commands. Migrate **last** so earlier batches keep working against the unchanged hubs during transition.

| Command | Inbound | Deps | Notes |
|---|---|---|---|
| `code/coverage.md` | 8 | 9 | |
| `code/ci-fix.md` | 9 | 8 | |
| `code/deps-check.md` | 9 | 8 | |
| `code/ci-local.md` | 12 | 7 | |
| `site/update.md` | 9 | 7 | |
| `test.md` | 12 | 5 | Test runner entrypoint |
| `git/sync.md` | 12 | 6 | |
| `code/lint.md` | 13 | 9 | |
| `git/worktree.md` | 16 | 8 | Widely referenced by git/* |
| `docs/check.md` | 19 | 21 | |
| `docs/check-links.md` | 19 | 18 | |
| `docs/changelog.md` | 20 | 18 | |
| `docs/lint.md` | 21 | 19 | |
| `site/build.md` | 18 | 13 | |
| `site/check.md` | 18 | 14 | |
| `site/status.md` | 16 | 15 | |
| `do.md` | 9 (also a HUB) | 17 | Universal router; references nearly every other command |
| `hub.md` | 4 | 53 | Discovery index; **regenerate from new skills/ tree** |
| `orchestrate.md` | 8 | 6 | Orchestrator entrypoint |
| `check.md` | **30** | 8 | Highest inbound — migrate **dead last** |

**Inter-batch deps:**

- `do.md` and `hub.md` reference virtually all other commands; after migration their reference table must be regenerated (likely via the same discovery mechanism, just pointed at `skills/`).
- `check.md` is the single most-referenced command (30 inbound). Migrating it last means every earlier batch can keep referencing the unchanged version.
- `git/worktree.md` is referenced by Batch 3's `git/branch.md`, `git/init.md`, `git/clean.md` — keep until last in the git subtree.

**Risk:** highest. Plan to:

1. Run `/craft:code:command-audit` against the new `skills/` tree to confirm all references resolve.
2. Regenerate `commands/_cache.json` → `skills/_cache.json` equivalent.
3. Update `_discovery.py` to target the new layout.
4. Smoke-test `/craft:do`, `/craft:hub`, `/craft:check` end-to-end.

---

## Cross-cutting prerequisites (before Batch 1)

Not commands, but **must be decided before migrating anything**:

1. **Skill format mapping** — how does YAML frontmatter (`description`, `argument-hint`, `allowed-tools`) map to skill `SKILL.md` frontmatter (`name`, `description`)? Several craft fields have no direct skill equivalent.
2. **Subdirectory flattening** — skills are typically flat (`skills/<name>/SKILL.md`), but craft has nested dirs (`docs/claude-md/init.md`, `git/docs/safety-rails.md`). Decide on naming convention (e.g., `docs-claude-md-init` vs colon-separated).
3. **Discovery engine port** — `commands/_discovery.py` and `commands/_cache.json` need a skills/ equivalent or retirement.
4. **`/craft:` reference rewrites** — all 108 files reference each other with `/craft:foo:bar` syntax. Decide whether skills retain the same invocation prefix or change.
5. **Test suite updates** — `tests/test_craft_plugin.py` and `test_plugin_dogfood.py` enumerate commands; will need parallel skill enumeration.

---

## Summary stats

| Batch | Count | Class mix | Inbound range | Risk |
|---|---|---|---|---|
| 1 | 22 | All LEAF | 0 | lowest |
| 2 | 22 | LEAF + BRANCH + low-inbound HUB | 1–5 | low |
| 3 | 22 | Mid HUB (arch/dist/git mid/plan) | 2–10 | low–medium |
| 4 | 22 | Docs + site HUBs | 12–17 | medium |
| 5 | 20 | Highest-inbound + entrypoints | 4–30 | highest |
| **Total** | **108** | | | |

No commands reference non-existent targets. All deps internal to the tree.
