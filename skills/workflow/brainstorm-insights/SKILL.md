---
name: brainstorm-insights
description: This skill should be used when the user asks to "brainstorm", "explore ideas", "design a feature", "draft a spec", "capture a spec", "generate insights", "session insights", "friction report", "what patterns am I hitting", "analyze my sessions", or mentions ideation, requirements gathering, spec capture, brainstorming depth/focus modes, or aggregating session facets into a friction/goals report. Generates two kinds of artifacts from upstream signals — BRAINSTORM/SPEC documents (from project + conversation context) and INSIGHTS reports (from session facet history).
---

# Brainstorm & Insights Generation

Two generators bundled under one workflow skill. Both transform diffuse upstream signal — conversation, project state, session facets — into a concrete artifact the user (or downstream skill) can act on.

| Operation | Input | Output Artifact |
|-----------|-------|-----------------|
| **Brainstorm** | Topic + project/git context | `BRAINSTORM-<topic>-<date>.md` or `docs/specs/SPEC-<topic>-<date>.md` |
| **Insights** | `~/.claude/usage-data/facets/*.json` | Terminal report, `report.html`, or JSON; includes `claude_md_additions` |

## Boundary With Adjacent Skills

This skill is the **generation** end of an insights lifecycle. It does **not** mutate CLAUDE.md, settings, or specs.

| Skill | Role | Lifecycle Phase |
|-------|------|-----------------|
| **brainstorm-insights** (this) | Generates BRAINSTORM/SPEC and INSIGHTS report | **Produce** |
| `insights-apply` | Reads INSIGHTS report, writes suggestions into `~/.claude/CLAUDE.md` via sync pipeline | **Consume / apply** |
| `adhd-workflow` | Session boundary ops (done, recap, next, focus, stuck, spec-review, refine) | **Operate** on existing artifacts |
| `project-planner` | Project-scope planning, estimation, roadmaps | **Plan** after spec exists |

Typical chain: `brainstorm-insights` → SPEC → `project-planner` (breakdown) → `adhd-workflow` (spec-review/done). Independently: `brainstorm-insights` → INSIGHTS report → `insights-apply` → updated CLAUDE.md.

If the user wants to *apply* insight suggestions to CLAUDE.md, hand off to `insights-apply`. This skill stops at the report.

## When to Use

Activate when the prompt matches one of the two operations:

| User intent | Operation |
|-------------|-----------|
| "brainstorm X", "explore ideas for X", "design Y", "draft a spec for Z" | Brainstorm |
| "save this as a spec", "capture this as SPEC.md" | Brainstorm (save action) |
| "what's my friction", "session insights", "where am I getting stuck repeatedly", "patterns in my sessions" | Insights |
| "generate insights report", "aggregate facets", "show CLAUDE.md suggestions" | Insights |

If ambiguous, ask one clarifying question: "Brainstorm a new idea, or analyze your past sessions?"

---

## Operation 1: Brainstorm

ADHD-friendly ideation with depth budgets, focus modes, and optional spec capture.

### Inputs

- **Topic** — explicit argument, or inferred from conversation / `.STATUS` / git branch / recent commits.
- **Depth** (default | quick | deep | max) — controls question count and agent delegation.
- **Focus** (feat | arch | ux | api | ui | ops) — shapes output sections.
- **Action** (optional `save`) — capture as `SPEC-<topic>-<date>.md`.

### Depth Budgets

| Depth | Time | Expert Questions | Agents |
|-------|------|------------------|--------|
| quick | < 1 min | 0 + "ask more?" | None |
| default | < 5 min | 2 + "ask more?" | None |
| deep | < 10 min | 8 | None |
| max | < 30 min | 8 + milestones | 2 per focus |

### Flow

1. **Parse args / detect topic.** If no topic, scan conversation, `.STATUS`, git branch, recent commits. 1 topic → use it; 2–4 → AskUserQuestion; 0 or 5+ → ask free-form.
2. **Pick depth + focus.** If not provided, present AskUserQuestion menus. Never skip these silently.
3. **Context scan.** Check for existing SPEC or prior brainstorm on the topic, project type, `.STATUS` version, recent test failures. Pre-fill answers where the project state already answers a question; insert dynamic questions where state suggests one (e.g., "Tests failing — address first?").
4. **Insights pre-load.** If `~/.claude/usage-data/facets/` has sessions matching the project/topic, surface top friction patterns inline ("Previous sessions: 8x wrong CWD") so they become input to the brainstorm. This is the only place this skill *reads* insights data — it does not regenerate the report here.
5. **Expert questions.** Per-depth count. Use AskUserQuestion. Always offer "ask more?" / "switch depth" escape hatches after the planned count, even at quick (0 questions).
6. **Generate output.** Focus-specific sections (user stories for `feat`, Mermaid diagram for `arch`, API endpoints for `api`, etc.). Save to `BRAINSTORM-<topic>-<date>.md`.
7. **Spec capture (action=save, or prompted for feat/arch/api).** Ask user-story + acceptance criteria, render full SPEC template, write to `docs/specs/SPEC-<topic>-<date>.md`. If insights had friction patterns, auto-add a "Known Risks" section sourced from them.
8. **Orchestration handoff (optional, post-spec).** Offer to generate ORCHESTRATE file + worktree via `plan-orchestrator` skill / `/craft:orchestrate:plan`.

### Mandatory Interactive Steps

Even when all arguments are provided, the following are **never skipped**:

- The expert-question count for the selected depth (0 / 2 / 8).
- The "ask more?" escape-hatch prompt after questions.

Skipping these is a known regression pattern — the depth/focus *menus* may be skipped when args provide them, but interactive expert questions cannot be.

### Outputs

- `BRAINSTORM-<topic>-<date>.md` (always — even when also saving spec).
- `docs/specs/SPEC-<topic>-<date>.md` (when `save` action selected).
- Terminal summary with paths and suggested next commands.

---

## Operation 2: Insights

Aggregate session facet data into a friction/goals report.

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

## Cross-Operation Data Flow

```text
adhd-workflow (done) ──► facets/*.json ──► [Insights op] ──► report + claude_md_additions
                                                                    │
                                                                    ▼
                                                            insights-apply skill
                                                                    │
                                                                    ▼
                                                            ~/.claude/CLAUDE.md

conversation + .STATUS + git ──► [Brainstorm op] ──► BRAINSTORM.md + (optional) SPEC.md
                                          ▲                              │
                                          │                              ▼
                                  insights pre-load              plan-orchestrator skill
```

Brainstorm *reads* facets only as inline context (Step 4); it does not generate the report. The Insights operation is the dedicated generator.

---

## Integration

Replaces during v2.34.0 → v3.0.0 migration:

- `/craft:workflow:brainstorm` → Operation 1
- `/craft:insights` (formerly `/craft:workflow:insights`) → Operation 2

Both command paths continue to work during the deprecation cycle.

## Test-plan scaffolding (default-on)

When this skill emits a BRAINSTORM or SPEC artifact, it also emits a test-plan scaffold **by default**. Pass `--no-tests` to suppress the section.

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
- Scaffold templates live in `references/scaffold-templates.md`; point to that file — do not duplicate templates inline.
- For the **grill operation**: emit a test-plan scaffold only when called with a TOPIC arg; skip on a PATH arg (path targets existing code that already has tests).

### Opt-out

`--no-tests` suppresses the entire test-plan section. Default is **on**.

## Related Skills

- `insights-apply` — Consume Insights output; write suggestions to CLAUDE.md. **Do not duplicate that logic here.**
- `adhd-workflow` — Produces the facet data this skill consumes; also handles `spec-review` after spec capture.
- `project-planner` — Project-scope breakdown after a SPEC is captured.
- `plan-orchestrator` (Batch 2 sibling) — Generates ORCHESTRATE file + worktree from a SPEC.
