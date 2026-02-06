# Brainstorm Quick Reference Card

> At-a-glance reference for `/workflow:brainstorm`

---

## Syntax

```
/brainstorm [depth:count] [focus] [action] [-C|--categories "cats"] "topic"
```

## Depth Layer

| Full | Short | Count | Time |
|------|-------|-------|------|
| (default) | - | 2 | < 5 min |
| quick | q | 0 | < 1 min |
| deep | d | 8 | < 10 min |
| max | m | 8 | < 30 min |

Custom: `d:5`, `m:12`, `q:0`

## Focus Layer

| Full | Short | Single |
|------|-------|--------|
| feature | feat | f |
| architecture | arch | a |
| ux | ux | x |
| api | api | b |
| ui | ui | u |
| ops | ops | o |

## Action Layer

| Full | Short | Single |
|------|-------|--------|
| save | save | s |

## Category Shortcuts

| Short | Full |
|-------|------|
| req | requirements |
| usr | users |
| scp | scope |
| tech | technical |
| time | timeline |
| risk | risks |
| exist | existing |
| ok | success |
| all | all categories |

---

## Mode Selection Flowchart

```mermaid
flowchart TD
    Start["/brainstorm"] --> HasArgs{Arguments?}

    HasArgs -->|None| NewSession{New session?}
    HasArgs -->|Topic only| DepthQ["Q1: Depth?"]
    HasArgs -->|Topic + mode| Execute
    HasArgs -->|Full args| Execute

    NewSession -->|Yes| ResumeQ["Q-1: Resume session?"]
    NewSession -->|No| SmartDetect["Smart Context Detection"]

    ResumeQ --> ResumeChoice{User selects}
    ResumeChoice -->|Resume session| LoadSession["Load previous context"]
    ResumeChoice -->|Start fresh| SmartDetect

    LoadSession --> DepthQ

    SmartDetect --> HowMany{Topics found?}
    HowMany -->|1 topic| AutoTopic["Use detected topic"]
    HowMany -->|2-4 topics| TopicQ["Q0: Which topic?"]
    HowMany -->|0 or 5+| AskTopic["Ask: What to brainstorm?"]

    AutoTopic --> DepthQ
    TopicQ --> DepthQ
    AskTopic --> DepthQ

    DepthQ --> FocusQ["Q2: Focus?"]
    FocusQ --> ContextScan["Step 1.7: Context Scan"]
    ContextScan --> Questions["Ask Questions"]
    Questions --> AskMore["Ask More?"]
    AskMore --> Execute["Execute Brainstorm"]
    Execute --> Save["Save Output"]
    Save --> SpecQ{Spec capture?}
    SpecQ -->|save action| SpecCapture["Capture as spec"]
    SpecQ -->|feat/arch/api| SpecPrompt["Q: Capture as spec?"]
    SpecQ -->|quick/no| Done["Report + Next Steps"]
    SpecPrompt --> Done
    SpecCapture --> Done
```

## Milestone Flow (d:20 example)

```mermaid
graph TD
    A["Start: d:20"] --> B["Ask questions 1-8"]
    B --> C{"Milestone: Continue?"}
    C -->|Done| F["Generate brainstorm"]
    C -->|4 more| D["Ask 9-12"]
    C -->|8 more| E["Ask 9-16"]
    C -->|Keep going| G["Unlimited mode"]
    D --> C
    E --> C
    G --> H{"Every 4: Continue?"}
    H -->|Yes| G
    H -->|No| F
```

## v2.4.0 Colon Notation Flow

```
ColonArgs["d:5, m:12, q:3"] --> parse_depth_with_count()
  --> (depth_mode, question_count)
```

## v2.4.0 Categories Flag Flow

```
-C req,tech --> parse_categories()
  --> Filter question bank
  --> Selected questions
```

---

## Agent Delegation (Max Mode)

| Focus | Agents |
|-------|--------|
| feature | product-strategist |
| architecture | backend-architect, database-architect |
| design | ux-ui-designer |
| backend | backend-architect, security-specialist |
| frontend | frontend-specialist, performance-engineer |
| devops | devops-engineer |

---

## Common Patterns

```bash
# Fastest path
/brainstorm q "topic"

# Balanced (default)
/brainstorm "topic"

# Focused deep dive
/brainstorm d:5 f -C req,tech "topic"

# Full spec capture
/brainstorm d f s "topic"

# Maximum analysis
/brainstorm m a s "topic"

# Orchestrated
/brainstorm "topic" --orch=optimize
```

---

*See also: [Power User Tutorial](../tutorials/TUTORIAL-brainstorm-power-user.md) | [Question Bank](../specs/SPEC-brainstorm-question-bank.md)*
