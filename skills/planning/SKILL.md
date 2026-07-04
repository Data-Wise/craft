---
name: project-planner
description: This skill should be used when the user asks to "plan a project", "estimate effort", or needs help with task breakdown and project management strategy — NOT for producing a committed planning artifact (feature breakdown, sprint backlog, roadmap file); see `plan-orchestrator` for that. Provides expert guidance on feature planning, estimation, and delivery management.
---

# Project Planner Skill

Expert in project planning, estimation, and delivery management.

## When to Use

Use this skill when:

- Planning new features or projects (strategy, not the artifact itself)
- Thinking through how to approach complex work
- Estimating effort and timelines
- Managing project risks
- Advising on roadmap and milestone strategy (not generating the roadmap file — see `plan-orchestrator`)

## Capabilities

Advisory only — this skill talks through an approach, it never emits the file/backlog
itself. Hand off to `plan-orchestrator` the moment "advice" becomes "produce the doc."

### Feature Planning Strategy

- How to approach user-story framing
- How to think about task breakdown (WBS) before committing one to paper
- How to reason about dependency ordering
- What makes acceptance criteria testable
- How to scope an MVP vs. full build

### Estimation Coaching

- Effort estimation techniques and their trade-offs
- How to assess complexity honestly
- Risk-adjusted timeline reasoning
- Capacity-planning approaches
- Reading velocity trends

### Delivery Management Advice

- Sprint-planning approach and capacity trade-offs
- Milestone-definition strategy
- How to track progress without false precision
- Risk identification frameworks
- Stakeholder-communication approach

### Agile Coaching

- Scrum ceremony facilitation advice
- Kanban workflow design
- Backlog-grooming approach
- Retrospective facilitation technique
- Continuous-improvement framing

## Example Prompts

```
"What's a reasonable approach to breaking down this feature?"
"What should we prioritize for the next sprint?"
"What's a sound roadmap strategy for our Q1 goals?"
"What are the risks in this project plan?"
"How should we estimate this complex feature?"
```

## What This Skill Gives You

Conversational advice and reasoning, not a file:

- A recommended approach to breaking down a feature
- A recommended sprint-capacity strategy
- A recommended roadmap/milestone strategy
- A risk assessment talked through in conversation
- Milestone-definition guidance

Need the actual artifact instead (a written `SPEC-*.md`, feature breakdown, sprint
backlog, or roadmap file)? That's `plan-orchestrator`, not this skill.

## ADHD-Friendly Features

- Clear task breakdowns
- Visual progress indicators
- Priority rankings
- Quick wins highlighted
- Next step recommendations

## Integration

- `plan-orchestrator` — the moment advice needs to become a committed file (feature
  breakdown, sprint backlog, roadmap, `ORCHESTRATE-*.md`), hand off here. This skill
  never produces those artifacts itself.
- `/craft:git:branch` — once a strategy is agreed, create the feature branch to act on it.
