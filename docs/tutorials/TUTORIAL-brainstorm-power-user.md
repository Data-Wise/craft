# Brainstorm Power User Tutorial

> Advanced patterns and detailed examples for `/workflow:brainstorm`

**Prerequisites:** Basic familiarity with `/brainstorm` (see `/craft:hub workflow:brainstorm`)

---

## Quick Reference

```bash
# Minimal
/brainstorm "auth"                           # depth+focus menu, then 2 decision points

# Skip the menu — supply depth + focus as arguments
/brainstorm quick feat "auth"                # Quick depth, feature focus
/brainstorm deep arch "auth"                 # Deep depth, architecture focus

# Save as spec
/brainstorm deep feat save "auth"            # Deep + feature focus + spec capture

# Category override — limit expert questions regardless of focus defaults
/brainstorm deep "caching" -C tech,risks     # Only technical + risk questions
/brainstorm deep "auth" --categories req,users,success

# Orchestrated hand-off (post-spec, not in-skill delegation)
/brainstorm deep arch save "multi-tenant SaaS" --orch=optimize
```

There is no `max`/`m` depth tier, no colon notation (`d:5`, `m:12`), and no
`--format json`/`--format markdown` flag — these were part of the
pre-redesign 4-decision-point system and were intentionally removed. See
[Two Decision Points](#two-decision-points-not-four) below for why.

---

## Two Decision Points, Not Four

The current design has exactly two decision points per session:

1. **Depth + focus**, asked together in one `AskUserQuestion` call when not
   supplied as arguments.
2. **One optional follow-up** — "anything else before I generate this?" —
   offered once, after the expert questions, regardless of depth.

There is no per-depth escape-hatch menu, no "switch depth mid-flow," and no
milestone re-prompting every N questions. If a topic genuinely needs more
than the deep-tier's 6 expert questions, use the follow-up offer to add
more — don't look for a count-override flag; there isn't one.

| Depth | Time | Expert Questions |
|-------|------|-------------------|
| quick | < 1 min | 0 |
| default | < 5 min | 2 |
| deep | < 10 min | 6 |

| Focus | Shapes output |
|-------|---------------|
| `feat` | User stories, requirements-first |
| `arch` | Mermaid diagram, technical approach |
| `ux` | User-facing scope, success criteria |
| `api` | API endpoints, technical + requirements |
| `ui` | Visual/interaction scope |
| `ops` | Technical approach, risks, timeline |

---

## Example Scenarios

### Scenario 1: Interactive Mode Selection

```
User: /workflow:brainstorm "user authentication"

Claude: Single AskUserQuestion combining depth + focus...
User: Selects "default" depth, "feat" focus

-> Asks 2 expert questions (requirements + success, focus-driven default)
-> One follow-up offer: "anything else, or ready to generate?"
-> Saves to BRAINSTORM-user-authentication-<date>.md
```

### Scenario 2: Direct Invocation (Skip the Menu)

```
User: /workflow:brainstorm quick feat "auth"

-> Skips the depth+focus menu (both supplied as arguments)
-> Quick depth = 0 expert questions, straight to generation
-> Saves to BRAINSTORM-auth-<date>.md
```

### Scenario 3: Deep Architecture + Spec Capture

```
User: /workflow:brainstorm deep arch save "multi-tenant SaaS"

-> Deep depth: 6 expert questions (tech, risks, existing, scope defaults for arch focus)
-> One follow-up offer
-> Generates BRAINSTORM with a Mermaid architecture diagram
-> Spec capture: user-story + acceptance criteria prompts
-> Saves docs/specs/SPEC-multi-tenant-saas-<date>.md
```

### Scenario 4: Category Override

```
User: /workflow:brainstorm deep "caching" -C tech,risks

-> Deep depth, but expert questions limited to technical + risk categories
   (instead of the focus-driven default set)
-> Skips users, scope, timeline, existing, success entirely
-> More focused context gathering for a narrow topic
```

### Scenario 5: Orchestrated Hand-off

```
User: /workflow:brainstorm deep arch save "payment api" --orch=optimize

-> Runs the normal 2-decision-point brainstorm flow, generates + saves the spec
-> Post-spec: offers hand-off to orchestrator-v2 via --orch=optimize
   (plan-orchestrator skill / /craft:orchestrate:plan <spec-path>)
-> This is the ONLY delegation mechanism — brainstorm does not spawn
   subagents itself (see "Going Deeper" below)
```

### Scenario 6: Context-Aware Smart Questions

```
User: /workflow:brainstorm deep "dependency management"

-> Context scan finds an existing SPEC-dependency-management.md
-> Pre-fills requirements + technical from the existing spec
-> Only asks the remaining expert questions the spec doesn't already answer
```

---

## Going Deeper: No In-Skill Agent Delegation

The pre-redesign version had a "max" depth that launched background agents
directly from inside brainstorm — duplicating what `orchestrator-v2` already
does (wave checkpoints, file-based results, explicit model routing,
`AskUserQuestion` confirmation before spawning) but without those
safeguards, and referencing agent type names that didn't exist.

The current design does not spawn subagents itself. After a spec is
captured, it offers a hand-off to the orchestrator via the existing
`--orch` flag / `plan-orchestrator` skill / `/craft:orchestrate:plan
<spec-path>` — one delegation mechanism, already hardened, instead of two.

---

## Output

- `BRAINSTORM-<topic>-<date>.md` — always generated, even when also saving a spec.
- `docs/specs/SPEC-<topic>-<date>.md` — when the `save` action is selected.
- Terminal summary with paths and a suggested next command.
- Test-plan + Documentation scaffolds are emitted by default (`--no-tests`/`--no-docs` to suppress).

---

## Tips

1. **Skip the menu when you know what you want** — supply depth + focus as
   arguments (`/brainstorm deep arch "topic"`) to go straight to the expert
   questions.
2. **Use `-C`/`--categories` to narrow a broad topic** — overrides the
   focus-driven default category set.
3. **`deep` is the ceiling** — 6 expert questions max per invocation; use the
   follow-up offer to add more instead of looking for a count override.
4. **`save` for anything implementation-bound** — auto-generates the spec
   with user-story + acceptance criteria.
5. **`--orch=<mode>` for complex topics** — hands off to the orchestrator
   after spec capture, not before.
6. **Context-aware saves repetition** — an existing SPEC on the same topic
   pre-fills answers the skill can already infer.

---

*See also: [Brainstorm Reference Card](../reference/REFCARD-BRAINSTORM.md)*
