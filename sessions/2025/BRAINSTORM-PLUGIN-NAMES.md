# Brainstorm: Dev-Tools Plugin Names

**Date:** 2025-12-26
**Decision:** Proposal 2 (Full Stack Dev - 42 commands)
**Note:** Proposal 3 (Smart Orchestrator) saved for workflow plugin enhancement

---

## Naming Criteria

| Criterion | Weight | Notes |
|-----------|--------|-------|
| **Memorable** | High | Easy to recall when needed |
| **Typeable** | High | Short prefix for `/name:command` |
| **Descriptive** | Medium | Hints at purpose |
| **Unique** | High | No collision with marketplace |
| **Professional** | Medium | Suitable for public release |
| **Fun/Personality** | Low | Optional but nice |

---

## Category 1: Literal/Descriptive Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `dev-tools` | `/dev:` | Clear, obvious | Generic, boring |
| `developer-toolkit` | `/dtk:` | Professional | Long |
| `fullstack-dev` | `/fs:` | Describes scope | Might exclude non-fullstack |
| `code-toolkit` | `/ct:` | Clear | Generic |
| `dev-essentials` | `/de:` | Implies core tools | Conflicts with developer-essentials |
| `dev-suite` | `/ds:` | Professional | Corporate-sounding |

**⭐ Best literal:** `dev-tools` → `/dev:` (short, clear, no conflicts)

---

## Category 2: Action/Verb-Based Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `forge` | `/forge:` | Creative, building | Taken (rforge exists) |
| `craft` | `/craft:` | Artisanal feel | Minecraft vibes |
| `build` | `/build:` | Action-oriented | Too specific |
| `ship` | `/ship:` | Outcome-focused | Might confuse with deployment |
| `make` | `/make:` | Unix heritage | Conflicts with make tool |
| `create` | `/create:` | Generative | Generic |

**⭐ Best action:** `craft` → `/craft:` (creative, memorable)

---

## Category 3: Metaphor/Creative Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `anvil` | `/anvil:` | Forge metaphor | Obscure |
| `workshop` | `/ws:` | Where work happens | Long |
| `workbench` | `/wb:` | Tool metaphor | Long |
| `garage` | `/garage:` | Maker space vibes | Too casual |
| `foundry` | `/foundry:` | Building things | Industry-specific |
| `atelier` | `/atelier:` | Creative workshop | Pretentious |
| `smithy` | `/smithy:` | Tool-making | Obscure |

**⭐ Best metaphor:** `workshop` → `/ws:` (intuitive)

---

## Category 4: Tech/Hacker Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `devkit` | `/dk:` | Game dev heritage | Short, good |
| `toolkit` | `/tk:` | Classic | Generic |
| `utils` | `/u:` | Unix-y | Too terse |
| `tools` | `/t:` | Minimal | Too generic |
| `kit` | `/kit:` | Modern, clean | Very generic |
| `sdk` | `/sdk:` | Familiar concept | Misleading (not an SDK) |
| `cli-tools` | `/cli:` | Accurate | Redundant in CLI context |

**⭐ Best tech:** `devkit` → `/dk:` (recognizable, short)

---

## Category 5: Personality/Fun Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `sidekick` | `/sk:` | Helpful assistant | Cutesy |
| `buddy` | `/buddy:` | Friendly | Too casual |
| `copilot` | `/cp:` | AI pair programming | GitHub trademark |
| `wingman` | `/wm:` | Support role | Gendered |
| `ally` | `/ally:` | Supportive | Generic |
| `assist` | `/assist:` | Helper | Generic |
| `partner` | `/partner:` | Collaborative | Business-y |

**⭐ Best personality:** `sidekick` → `/sk:` (fun but professional)

---

## Category 6: Power/Pro Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `pro-dev` | `/pro:` | Professional | Overused |
| `power-tools` | `/pt:` | Capability | Home Depot vibes |
| `turbo` | `/turbo:` | Speed/power | Dated |
| `ultra` | `/ultra:` | Premium | Overused |
| `plus` | `/plus:` | Enhanced | Implies paid tier |
| `prime` | `/prime:` | Top quality | Amazon conflict |
| `max` | `/max:` | Maximum | Apple conflict |

**⭐ Best power:** None stand out - avoid this category

---

## Category 7: DT-Specific/Personal Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `dt-dev` | `/dt:` | Personal brand | Limits public appeal |
| `datawise-dev` | `/dw:` | Brand aligned | Long |
| `wise-tools` | `/wise:` | Brand tie-in | Pretentious |
| `stat-dev` | `/sd:` | Stats focus | Too narrow |

**⭐ Best personal:** Skip - keep public-friendly

---

## Category 8: Compound/Portmanteau Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `devflow` | `/df:` | Dev + workflow | Nice combo |
| `codecraft` | `/cc:` | Code + craft | Alliterative |
| `buildbox` | `/bb:` | Building container | Product name conflicts |
| `codekit` | `/ck:` | Code + kit | Existing product |
| `devhub` | `/dh:` | Dev + hub | GitHub conflict |
| `codebase` | `/cb:` | Familiar term | Too literal |
| `stacktools` | `/st:` | Full-stack tools | Descriptive |

**⭐ Best compound:** `devflow` → `/df:` (flows nicely)

---

## Category 9: Short/Punchy Names

| Name | Prefix | Pros | Cons |
|------|--------|------|------|
| `flux` | `/flux:` | Change/flow | Abstract |
| `pulse` | `/pulse:` | Alive/active | Abstract |
| `core` | `/core:` | Essential | Generic |
| `base` | `/base:` | Foundation | Generic |
| `apex` | `/apex:` | Peak/best | Gaming connotation |
| `nova` | `/nova:` | Bright/new | Overused |
| `zen` | `/zen:` | Calm/focused | ADHD-friendly? |

**⭐ Best short:** `zen` → `/zen:` (calm, focused - ADHD angle)

---

## Top 10 Finalists

| Rank | Name | Prefix | Why |
|------|------|--------|-----|
| 1 | ⭐ **devkit** | `/dk:` | Short, familiar, professional |
| 2 | ⭐ **craft** | `/craft:` | Creative, memorable, artisanal |
| 3 | ⭐ **devflow** | `/df:` | Flows well, dev + workflow |
| 4 | **dev-tools** | `/dev:` | Clear, obvious, no confusion |
| 5 | **workshop** | `/ws:` | Metaphor works, intuitive |
| 6 | **codecraft** | `/cc:` | Alliterative, creative |
| 7 | **zen** | `/zen:` | ADHD-friendly, calm |
| 8 | **sidekick** | `/sk:` | Fun personality |
| 9 | **forge** | `/forge:` | Creative (but rforge exists) |
| 10 | **toolkit** | `/tk:` | Classic, clear |

---

## Prefix Collision Check

Checking against existing plugins/commands:

| Prefix | Status | Conflict? |
|--------|--------|-----------|
| `/dk:` | ✅ Available | No |
| `/craft:` | ✅ Available | No |
| `/df:` | ✅ Available | No |
| `/dev:` | ✅ Available | No |
| `/ws:` | ✅ Available | No |
| `/cc:` | ⚠️ Might conflict | cc-marketplace? |
| `/zen:` | ✅ Available | No |
| `/sk:` | ✅ Available | No |
| `/forge:` | ❌ Conflict | rforge uses this |
| `/tk:` | ✅ Available | No |

---

## Recommendation Tiers

### Tier 1: Top Recommendations (Pick One)

| Name | Command Example | Why |
|------|-----------------|-----|
| **devkit** | `/dk:code:debug` | Professional, familiar, short |
| **craft** | `/craft:code:debug` | Creative, memorable |
| **devflow** | `/df:code:debug` | Modern, flows well |

### Tier 2: Solid Alternatives

| Name | Command Example | Why |
|------|-----------------|-----|
| **dev-tools** | `/dev:code:debug` | Clear, no surprises |
| **workshop** | `/ws:code:debug` | Good metaphor |
| **zen** | `/zen:code:debug` | ADHD-focused angle |

### Tier 3: If Nothing Else Works

| Name | Command Example | Why |
|------|-----------------|-----|
| **toolkit** | `/tk:code:debug` | Safe, boring |
| **sidekick** | `/sk:code:debug` | Fun but might not age well |

---

## Command Preview with Top Names

### Option 1: `devkit`
```
/dk:hub                    # Command discovery
/dk:code:debug             # Debug assistance
/dk:site:deploy            # Deploy docs
/dk:git:sync               # Smart git sync
/dk:docs:changelog         # Update changelog
/dk:test:run               # Run tests
/dk:arch:plan              # Architecture planning
```

### Option 2: `craft`
```
/craft:hub
/craft:code:debug
/craft:site:deploy
/craft:git:sync
/craft:docs:changelog
/craft:test:run
/craft:arch:plan
```

### Option 3: `devflow`
```
/df:hub
/df:code:debug
/df:site:deploy
/df:git:sync
/df:docs:changelog
/df:test:run
/df:arch:plan
```

---

## Decision Framework

**If you want professional/familiar:** → `devkit`
**If you want creative/memorable:** → `craft`
**If you want modern/flowing:** → `devflow`
**If you want obvious/safe:** → `dev-tools`
**If you want ADHD-angle:** → `zen`
**If you want personality:** → `sidekick`

---

## Wild Card Ideas

Just for fun, some unconventional options:

| Name | Vibe |
|------|------|
| `grok` | Deep understanding |
| `mojo` | Power/magic |
| `dojo` | Practice/mastery |
| `nexus` | Connection point |
| `prism` | Multiple perspectives |
| `spark` | Ignition/creativity |

---

## Next Steps

1. **Pick top 3 favorites** from finalists
2. **Test command feel** - type them out, see what flows
3. **Check npm/pypi** - ensure name available if public release
4. **Sleep on it** - names that feel good tomorrow win

---

**Last Updated:** 2025-12-26
**Status:** Ready for decision
