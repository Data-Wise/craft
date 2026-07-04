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

### Feature Planning

- User story creation
- Task breakdown (WBS)
- Dependency mapping
- Acceptance criteria definition
- MVP scoping

### Estimation

- Effort estimation techniques
- Complexity assessment
- Risk-adjusted timelines
- Capacity planning
- Velocity tracking

### Project Management

- Sprint planning
- Milestone definition
- Progress tracking
- Risk identification
- Stakeholder communication

### Agile Practices

- Scrum ceremonies
- Kanban workflows
- Backlog grooming
- Retrospective facilitation
- Continuous improvement

## Example Prompts

```
"What's a reasonable approach to breaking down this feature?"
"What should we prioritize for the next sprint?"
"What's a sound roadmap strategy for our Q1 goals?"
"What are the risks in this project plan?"
"How should we estimate this complex feature?"
```

## Outputs

- Feature plans with tasks
- Sprint plans with capacity
- Project roadmaps
- Risk assessments
- Milestone definitions

## ADHD-Friendly Features

- Clear task breakdowns
- Visual progress indicators
- Priority rankings
- Quick wins highlighted
- Next step recommendations

## Integration

Works with:

- `/craft:plan:feature` - Feature planning
- `/craft:plan:sprint` - Sprint planning
- `/craft:plan:roadmap` - Roadmap generation
- `/craft:git:branch` - Create feature branches
