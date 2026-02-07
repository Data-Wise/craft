# Teaching Workflow

> **TL;DR**: Three tools, one workflow. Flow-cli dispatches commands at shell speed, Scholar generates AI content, Craft manages your course site safely.

## Teaching Ecosystem

The teaching workflow spans three tools. Each has clear ownership:

<div class="grid cards" markdown>

- :zap:{ .lg .middle } **Flow-CLI** *(Shell Speed)*

    Config, deployment, semester tracking, shell aliases.
    `teach status`, `teach deploy`, `teach config`

- :brain:{ .lg .middle } **Scholar** *(AI Content)*

    Lectures, exams, quizzes, slides, assignments, rubrics.
    `teach lecture`, `teach exam`, `teach quiz`

- :shield:{ .lg .middle } **Craft** *(Site Safety)*

    Preview-before-publish, validation, progress tracking.
    `/craft:site:publish`, `/craft:site:progress`

</div>

## Which tool do I use?

| I want to... | Use | Command |
|---|---|---|
| Generate a lecture/exam/quiz | Scholar | `teach lecture`, `teach exam` |
| Deploy the course site | flow-cli | `teach deploy` |
| Check if content is ready | All three | `teach check` |
| See what week it is | flow-cli | `teach status` or `tst` |
| Publish with CI safety | Craft | `/craft:site:publish` |
| See all teaching commands | flow-cli | `teach map` |
| Track semester progress | Craft | `/craft:site:progress` |

## Getting Started

<div class="grid cards" markdown>

- :rocket:{ .lg .middle } **First-Time Setup**

    ---

    25-minute tutorial: create config, test detection, validate, publish.

    [:octicons-arrow-right-24: Setup Tutorial](../tutorials/teaching-mode-setup.md)

- :gear:{ .lg .middle } **Config Reference**

    ---

    Complete YAML schema for `.flow/teach-config.yml`. Flow-cli configs work too.

    [:octicons-arrow-right-24: Config Schema](../teaching-config-schema.md)

- :arrows_counterclockwise:{ .lg .middle } **Migration Guide**

    ---

    Moving from manual `git checkout && mkdocs build && git push` to one command.

    [:octicons-arrow-right-24: Migration Guide](../teaching-migration.md)

- :card_file_box:{ .lg .middle } **Quick Reference**

    ---

    Printable cheat sheet: commands, flags, branch strategy, troubleshooting.

    [:octicons-arrow-right-24: Quick Reference](../reference/REFCARD-TEACHING.md)

</div>

## Craft Commands

| Command | What it does |
|---------|-------------|
| `/craft:site:publish` | Preview → Validate → Switch branch → Build → Deploy (5-step safety) |
| `/craft:site:progress` | Semester dashboard with week tracking, break countdown, completion % |
| `/craft:site:build` | Build site with teaching-aware context (branch, week, course info) |
| `/craft:site:check` | Content validation (syllabus sections, schedule completeness, assignments) |
| `/craft:git:status` | Teaching-aware git status (shows deployment context, what students see) |

## Config Compatibility

Flow-cli is the canonical config owner. Craft normalizes flow-cli's schema silently:

| Flow-CLI writes | Craft reads as |
|---|---|
| `course.name` | `course.number` |
| `course.full_name` | `course.title` |
| `semester_info.start_date` | `dates.start` |
| `semester_info.end_date` | `dates.end` |
| `branches.production` | `deployment.production_branch` |
| `course.semester: "spring"` | `course.semester: "Spring"` |

No migration needed. Both schemas work transparently. See [Config Schema](../teaching-config-schema.md#flow-cli-config-compatibility) for details.

## Common Workflows

### Weekly Content Update

```bash
# 1. Edit content on draft branch
# 2. Preview changes
/craft:site:build
# 3. Validate and publish
/craft:site:publish
```

### Semester Check-In

```bash
# See where you are
/craft:site:progress

# Validate everything
/craft:site:publish --dry-run --validate-only
```

### Deploy Course Website

See the full [Deploy Course Website recipe](../cookbook/common/deploy-course-website.md) for step-by-step instructions.

## Documentation

| Resource | Purpose |
|----------|---------|
| [Ecosystem Overview](../guide/teaching-workflow.md) | Full guide with workflows, validation, troubleshooting |
| [Setup Tutorial](../tutorials/teaching-mode-setup.md) | First-time 25-minute walkthrough |
| [Config Schema](../teaching-config-schema.md) | YAML reference (flow-cli compatible) |
| [Migration Guide](../teaching-migration.md) | From manual workflows to Craft |
| [Quick Reference](../reference/REFCARD-TEACHING.md) | Printable cheat sheet |
| [Teaching Spec](../specs/_archive/SPEC-teaching-workflow-2026-01-16.md) | Original implementation spec |
| [Ecosystem Spec](../specs/_archive/SPEC-teaching-ecosystem-coordination-2026-02-06.md) | Cross-tool coordination spec |
