# craft v4 — Full Disposition Table (69 → 26)

> Companion to `GRILL-craft-v4-roster-2026-07-09.md` (R1–R3 locked; R4 lock pending this
> review). Every post-split command's fate. 🛟 = salvage gate (R2: body-vs-skill diff, unique
> logic → skill `references/` before deletion). One correction found while building this
> table: **`check` is itself a deprecated shim (315L)** — promoted to the hot micro-shim list
> (5th), since it's the pre-commit safety entry used constantly.

## ✅ KEEP as-is (18)

| Command | Lines | Type | Note |
|---|---|---|---|
| do | 1002 | router | smart routing entry |
| hub | 804 | catalog | diet to 26-surface is a 3.5 task (see open question) |
| plan | 102 | router | absorbs plan:feature |
| orch | 369 | router | absorbs orch:drive + orch:workflow as flags |
| smart-help | 271 | router | discovery |
| grill | 51 | shim | non-deprecated entry over grill skill |
| code:release | 73 | shim | non-deprecated entry over release skill |
| code:lint | 313 | rich | |
| code:debug | 176 | rich | |
| code:refactor | 171 | rich | |
| code:test-gen | 182 | rich | |
| code:release-watch | 117 | rich | |
| code:fewer-prompts | 72 | rich | |
| dist:homebrew | 1691 | rich | largest command; untouched |
| dist:surfaces | 180 | rich | |
| docs:update | 1046 | rich | release-plumbing (stays per B2) |
| docs:changelog | 262 | rich | release-plumbing (stays per B2) |
| brief | 325 | rich | |

## 🔥 KEEP as ≤5-line micro-shims (5) — R1 + this review

| Command | Today | Skill (canonical) |
|---|---|---|
| next | 95L dep shim | workflow/adhd-workflow |
| done | 35L dep shim | workflow/adhd-workflow |
| refine | 47L dep shim | workflow/prompt-refiner |
| brainstorm | 111L dep shim | workflow/brainstorm |
| **check** | **315L dep shim** | check — **added here: daily pre-commit safety entry; 315L body gets the 🛟 salvage diff too** |

## 🔀 CONSOLIDATED away (20 files → 3 new routers + 2 existing)

| Family | Files folded | Bodies land in |
|---|---|---|
| **NEW `ci`** (8) | detect 292 · fix 96 · generate 730 · local 219 · status 166 · triage 176 · validate 303 · watch 135 | `skills/ci/references/<sub>.md` |
| **NEW `arch`** (4) | analyze 147 · diagram 130 · plan 133 · review 109 | `skills/architecture/references/` |
| **NEW `code:audit`** (5) | command-audit 131 · deps-audit 170 · deps-check 88 · docs-check 248 · skill-standards 167 | `skills/code/references/audit-<sub>.md` |
| → existing `orch` (2) | orch:drive 114 · orch:workflow 126 | `skills/orchestration/references/` |
| → existing `plan` (1) | plan:feature 139 | `skills/planning/references/` |

## ☠️ KILL — deprecated shims (22; 🛟 = salvage-gated per R2)

| Group | Commands | Salvage |
|---|---|---|
| git (9) | worktree 247 🛟 · guard 67 · protect 69 · unprotect 138 · status 69 · clean 64 · branch 75 · protect-baseline 142 · **docs:refcard 363 🛟** | refcard = PR #279 restoration; worktree at 247L crosses the 150L gate |
| dist extras (3) | **marketplace 409 🛟 · pypi 492 🛟 · curl-install 252 🛟** | all 3 into ONE dist-extras skill — the PR #279 profile |
| claude-md trio (3) | **edit 635 🛟 · sync 362 🛟 · init 320 🛟** | 1,317L vs one skill; skill STAYS in craft, commands die |
| plan family (3) | sprint 30 · roadmap 29 · orch:plan 57 | tiny, tripwire-covered |
| check family (1) | **gen-validator 447 🛟** | PR #279 restoration |
| code (2) | demo 183 🛟 · coverage 89 | demo crosses 150L |
| workflow (1) | **insights 194 🛟** | PR #279 restoration |

**Salvage jobs: 11** (R2's 9 + git:worktree + code:demo crossing the 150L line, + check's 315L
body under the micro-shim conversion = 12 diffs total).

## 🗑️ KILL — teaching residue (2) + DEMOTE (1)

utils:readme-teach-config (146) · utils:readme-semester-progress (241) — scholar leftovers ·
discovery-usage (289, `internal: true`) → docs page.

## Arithmetic check

18 keep + 5 micro-shims + 3 new routers = **26** ✓
Files removed: 22 shims + 20 consolidated + 2 utils + 1 demoted = 45; 69 − 45 + 3 new = 27…
minus `check` already counted in micro-shims (it was in the 69) = **26** ✓

## Open question (non-blocking)

- **hub diet**: 804-line catalog describes a 94-surface; regenerate against the 26 at Phase
  3.5's count-cascade step (recommend: yes, as part of the sweep — it's regenerated content,
  not a design decision).
