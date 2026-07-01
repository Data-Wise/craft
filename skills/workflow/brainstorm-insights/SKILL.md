---
name: brainstorm-insights
description: This skill should be used when the user asks "what's my friction", "session insights", "friction report", "what patterns am I hitting", "analyze my sessions", "generate insights report", "aggregate facets", or "show CLAUDE.md suggestions". Aggregates session facet history into a friction/goals report. Formerly bundled with the brainstorm skill (ideation); split out because the two operations share no input or output. Directory name kept as brainstorm-insights for path stability — tests and commands/workflow/insights.md reference it.
---

# Brainstorm Insights

Aggregate session facet data into a friction/goals report. Pure analysis —
reads `~/.claude/usage-data/facets/*.json`, writes a report. Never touches
CLAUDE.md (that's `insights-apply`'s job) and never generates BRAINSTORM/SPEC
documents (that's the `brainstorm` skill's job — see "Split history" below).

## Split history

This skill used to bundle two unrelated operations: ideation (topic +
project/git context → `BRAINSTORM-*.md` / `SPEC-*.md`) and session-facet
friction analysis (`~/.claude/usage-data/facets/*.json` → friction/goals
report). They shared no input and no output, so ideation moved to its own
`skills/workflow/brainstorm/`. This directory kept the `brainstorm-insights`
name rather than renaming to `session-insights`, to avoid a path break for
existing references (`commands/workflow/insights.md`, the dogfood/e2e
scaffold-default tests, `insights-apply`, and `references/scaffold-templates.md`
which is shared with `orchestrate`). Only the Insights operation remains here.

## Boundary With Adjacent Skills

| Skill | Role |
|-------|------|
| **brainstorm-insights** (this) | Aggregates session facet history into a friction/goals report |
| `insights-apply` | Reads INSIGHTS report, writes suggestions into `~/.claude/CLAUDE.md` via sync pipeline |
| `brainstorm` | Generates BRAINSTORM/SPEC documents from topic + context — unrelated input/output, was previously bundled here |
| `adhd-workflow` | Produces the facet data this skill consumes; also session boundary ops (done, recap, next, focus, stuck, spec-review) |

Chain: `adhd-workflow` (done) → facets → `brainstorm-insights` (this) → report → `insights-apply` → updated CLAUDE.md.

If the user wants to *apply* insight suggestions to CLAUDE.md, hand off to `insights-apply`. This skill stops at the report. If the user wants to brainstorm a new idea or capture a spec, hand off to `brainstorm`.

### Inputs

- `~/.claude/usage-data/facets/*.json` — written by `adhd-workflow` (session done operation).
- `--since N` (days, default 30).
- `--project NAME` (optional filter).
- `--format terminal|html|json`.

### Defensive Parsing Contract

Facet files can be malformed (interrupted writes, hand-edits, disk corruption). Every per-file read MUST wrap in `try / except` catching `(json.JSONDecodeError, KeyError, TypeError, FileNotFoundError, UnicodeDecodeError, OSError)`, log `warning: skipping malformed facet <path>: <ErrType>: <msg>` to stderr, and `continue`. Never abort the whole report on a single bad facet. This contract is shared with `/craft:hub` and `/craft:do` and is regression-tested in `tests/test_facet_parsing_defensive.py`.

### Aggregation

Across the time window, extract:

1. **Session count + outcome distribution** — success / partial / abandoned.
2. **Goal categories** — feature dev, bug fix, docs, refactoring, other.
3. **Friction patterns** by type: `wrong_approach`, `context_loss`, `tool_misuse`, `test_failure`, `dependency_issue`, `config_drift`.
4. **Top friction details** — specific recurring incidents ("Wrong CWD — 8 times").
5. **`claude_md_additions`** — structured suggestions for CLAUDE.md rules that would prevent the observed friction. Each has `title`, `content`, `priority` (high|medium|low), `source` (which events generated it).

### Friction Type → Guardrail Map

When an ORCHESTRATE plan downstream consumes insights, friction types map to guardrails:

| Friction | Guardrail Rule |
|----------|----------------|
| `wrong_approach` | "Verify CWD is the worktree before starting" |
| `context_loss` | "Read ORCHESTRATE file on session start" |
| `tool_misuse` | "Use /craft:do for routing, not manual commands" |
| `test_failure` | "Run tests after each phase, not just at the end" |
| `dependency_issue` | "Check package versions match before implementing" |
| `config_drift` | "Run validate-counts after structural changes" |

### Output Formats

- **terminal** (default) — craft box-drawing report with bar charts, top friction list, and `claude_md_additions` summary. Footer points at `insights-apply` skill for next step.
- **html** — `~/.claude/usage-data/report.html` with interactive charts, filterable session table, copy-buttons on suggestions.
- **json** — stdout, structured for scripting (`period`, `sessions`, `goals`, `friction`, `claude_md_additions`).

### No Data Case

If `~/.claude/usage-data/facets/` is empty or missing, print a short note explaining facets are written automatically by session-done; do not error.

---

## Data Flow

```text
adhd-workflow (done) ──► facets/*.json ──► brainstorm-insights (this) ──► report + claude_md_additions
                                                                                  │
                                                                                  ▼
                                                                          insights-apply skill
                                                                                  │
                                                                                  ▼
                                                                          ~/.claude/CLAUDE.md
```

## Integration

Replaces during v2.34.0 → v3.0.0 migration: `/craft:insights` (formerly
`/craft:workflow:insights`). The command path continues to work during the
deprecation cycle.

## Test-plan scaffolding (default-on, shared template reference)

This skill's friction reports are not themselves BRAINSTORM/SPEC artifacts,
but it shares the test-plan and Documentation scaffolding contract with the
`brainstorm` skill and `orchestrate`, since downstream consumers
(`plan-orchestrator`) read both this skill's friction map and brainstorm's
scaffolded test plans together. When a SPEC consuming this skill's friction
data is generated (by `brainstorm`), a test-plan scaffold is emitted **by
default**. Pass `--no-tests` to suppress the section.

### Tier-inference rule

Infer tiers from the shape of the artifact/change being scoped:

| Change shape | Tiers to emit |
|---|---|
| Flag / frontmatter / prose only | `e2e` + `dogfood` |
| + new parser or script | + `unit` |
| + cross-command data flow | + `integration` |
| + external dependency change | + `dependency` |
| + new command / skill / agent | + `count-cascade` dogfood |

Unselected tiers print as `N/A — <reason>` (never empty stubs).

### Emission rules

- Emit test stubs **red-first** (failing placeholder, not passing no-op).
- Each stub carries `# TODO(author): delete if not contract-bearing` until the author confirms the contract.
- Scaffold templates live in `references/scaffold-templates.md` (this directory) — shared with `brainstorm` and `orchestrate`; point to that file, do not duplicate templates inline.

### `--yes` non-suppression

`--yes` auto-accepts prompts only; the test-plan and Documentation sections are CONTENT and are still emitted under `--yes`. Only `--no-tests`/`--no-docs` remove them.

### Opt-out

`--no-tests` suppresses the entire test-plan section. Default is **on**.

## Documentation scaffolding (default-on)

When this skill emits a BRAINSTORM or SPEC artifact, it also emits a Documentation section **by default**. Pass `--no-docs` to suppress the section.

### Which docs to emit

Derive which documentation artifacts are needed by running the existing doc-scorer rubric from `commands/docs/sync.md` (threshold ≥3). Do **not** invent a new rubric — reuse the scorer as the single source of truth.

For each doc type the scorer evaluates (guide, refcard, demo, mermaid), pre-check (`[x]`) boxes that meet the threshold, and mark the rest `N/A — score <N>`. The template for the Documentation section lives in `references/scaffold-templates.md`.

### Lifecycle split

| Phase | Action |
|-------|--------|
| **Spec-time** | Read-only emit + pre-derive: render the Documentation section with pre-checked boxes. No file edits. |
| **Impl/post-merge** | Real edits via `/craft:docs:update --post-merge`. Diff-confirm gated before applying. |

### Count-cascade exclusion

Auto-docs emission touches **only semantic docs** — CHANGELOG `[Unreleased]` ×2 mirror, guide/refcard/tutorial prose. It **never** touches version or count lines. Version/count updates stay in `bump-version.sh`.

### Opt-out

`--no-docs` suppresses the entire Documentation section. Default is **on**.

## Related Skills

- `insights-apply` — consumes this skill's report, writes suggestions to CLAUDE.md. **Do not duplicate that logic here.**
- `adhd-workflow` — produces the facet data this skill consumes.
- `brainstorm` — unrelated operation; was previously bundled with this skill, now separate at `skills/workflow/brainstorm/`.
- `plan-orchestrator` — consumes friction data from this skill alongside brainstorm-generated specs.
