# SPEC: Documentation Gap-Fill

> **Date:** 2026-02-05
> **Branch:** `feature/docs-gap-fill`
> **Status:** Draft
> **Milestone:** v2.13.0

## Summary

Fill documentation gaps identified in the v2.12.0 gap analysis: 17 missing cookbook recipes, 15 missing troubleshooting pages, 10 missing tutorials, and 16 missing individual command pages.

## Requirements

### Must Have (Phase 1-2)

- 5 beginner cookbook recipes covering most common tasks
- 8 troubleshooting recipes for critical failure scenarios
- "Your First 10 Minutes" beginner tutorial

### Should Have (Phase 3-4)

- Individual documentation pages for top 15 most-used commands
- Enhanced category pages with "when to use X vs Y" scenarios

### Nice to Have (Phase 5+)

- Intermediate cookbook recipes (CI setup, badge management, CLAUDE.md lifecycle)
- Advanced tutorials (custom skills, custom agents)
- Interactive troubleshooting flowcharts

## Design

### Cookbook Recipe Template

```markdown
# [Recipe Title]

> **Time:** X minutes | **Level:** Beginner/Intermediate/Advanced

## TL;DR

One-line summary of what this recipe does.

## Prerequisites

- [ ] Craft installed
- [ ] [Any other requirements]

## Steps

### Step 1: [Action]

[Description with code block]

### Step 2: [Action]

[Description with code block]

## Expected Output

[What the user should see]

## Troubleshooting

[Common issues with this recipe]

## What's Next

- [Related recipe or guide]
```

### Troubleshooting Template

```markdown
# [Problem Title]

## Symptom

What the user sees or experiences.

## Cause

Why this happens.

## Fix

Step-by-step resolution.

## Prevention

How to avoid this in the future.
```

## Implementation Plan

| Step | Description | Files | Est. Time |
| ---- | ----------- | ----- | --------- |
| 1 | Create 5 beginner cookbook recipes | docs/cookbook/common/*.md | 2h |
| 2 | Create 8 troubleshooting recipes | docs/cookbook/troubleshooting/*.md | 2h |
| 3 | Create "First 10 Minutes" tutorial | docs/tutorials/TUTORIAL-first-10-minutes.md | 1h |
| 4 | Update mkdocs.yml nav for new pages | mkdocs.yml | 30m |
| 5 | Validate build + links | - | 30m |
| 6 | Create top 15 command pages | docs/commands/**/*.md | 4h |
| 7 | Enhance category pages | docs/commands/*.md | 2h |
| 8 | Final validation + commit | - | 30m |

## Metrics

| Metric | Before | Target |
|--------|--------|--------|
| Cookbook recipes | 8 | 21+ |
| Troubleshooting pages | 1 | 9+ |
| Tutorials | 14 | 15+ |
| Individual command pages | 19 | 34+ |
| Documentation completeness | 98% | 99% |
