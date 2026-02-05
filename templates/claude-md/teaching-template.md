# CLAUDE.md - {course_name}

> **TL;DR**: {course_description}

**Course:** {course_code} | **Semester:** {semester} | **Instructor:** {instructor}
**Weeks:** {week_count} | **Assignments:** {assignment_count} | **Exams:** {exam_count}

## Quick Reference

**Course Type**: {course_type}
**Main Branch**: `main` | **Dev Branch**: `dev`

### Essential Commands

```bash
# Preview locally
quarto preview

# Render full site
quarto render

# Publish to GitHub Pages
quarto publish gh-pages
```

## Course Structure

```text
{course_name}/
├── _quarto.yml          # Site configuration
├── course.yml           # Course metadata
├── index.qmd            # Landing page
├── syllabus.qmd         # Course syllabus
├── schedule.qmd         # Week-by-week schedule
├── weeks/
{week_dirs}
├── assignments/
{assignment_dirs}
├── exams/
{exam_dirs}
└── resources/
{resource_dirs}
```

## Development Workflow

1. Create content in weeks/ or assignments/
2. Add to schedule.qmd if needed
3. Preview: `quarto preview`
4. Render: `quarto render`
5. Publish: `quarto publish gh-pages`

## Week Structure

{week_structure}

## Assignment Workflow

| Task | Command |
|------|---------|
| Create assignment | Create .qmd in assignments/ |
| Preview | `quarto preview assignments/hw1.qmd` |
| Publish | Update schedule.qmd, then publish |
| Grade tracking | Update in course.yml |

## Publishing Workflow

**Safe publish pattern:**

1. Preview locally first: `quarto preview`
2. Check all links work
3. Render: `quarto render`
4. Validate _site/ output
5. Publish: `quarto publish gh-pages`

**IMPORTANT:** Always preview before publishing to avoid broken student links.

## Semester Progress

**Current:** {current_week}
**Progress:** {progress}%
**Next:** {next_task}

## Key Files

| File | Purpose |
|------|---------|
| _quarto.yml | Site configuration, theme, navigation |
| course.yml | Course metadata, grading, calendar |
| syllabus.qmd | Course policies, objectives |
| schedule.qmd | Week-by-week topics and due dates |

## Related Commands

{related_commands}

## Common Issues

| Issue | Fix |
|-------|-----|
| Build fails | `quarto render` |
| Broken links | Check schedule.qmd references |
| Preview issues | `quarto preview` |

## References

-> Course site: [{course_name}]({course_url})
-> GitHub: [{course_name}]({repo_url})
-> Canvas: [{course_name}]({canvas_url})
