# Brainstorm Question Bank Specification

> Full question text, options, and selection logic for the `/workflow:brainstorm` command

**Version:** 2.5.0 (v2.15.0 release)
**Source Command:** `commands/workflow/brainstorm.md`
**Categories:** 8 base + 6 project-type extensions

---

## Base Question Bank (16 Questions)

### requirements (2 questions)

**Q1:** "What are the key requirements for this feature?"

- Performance-critical
- User-facing functionality
- Internal tooling
- Data processing
- `multiSelect: false`

**Q2:** "Are there any hard constraints we must work within?"

- Technology stack
- Performance targets
- Security requirements
- Budget limits
- `multiSelect: true`

### users (2 questions)

**Q3:** "Who is the primary user for this feature?"

- End users
- Developers
- Administrators
- Automated systems
- `multiSelect: false`

**Q4:** "What problem does this solve for them?"

- Saves time
- Improves accuracy
- Enables new capability
- Simplifies workflow
- `multiSelect: false`

### scope (2 questions)

**Q5:** "What's definitely in scope for the first iteration?"

- Core functionality
- Basic error handling
- Essential UI/UX
- Documentation
- `multiSelect: true`

**Q6:** "What's explicitly out of scope (nice-to-have later)?"

- Advanced features
- Polish and refinement
- Integrations
- Scalability
- `multiSelect: true`

### technical (2 questions)

**Q7:** "Are there technical constraints or preferences?"

- Use existing stack
- New technology needed
- Architectural patterns
- No strong preferences
- `multiSelect: true`

**Q8:** "What existing systems does this need to integrate with?"

- Database
- Authentication
- APIs or services
- None (standalone)
- `multiSelect: true`

### timeline (2 questions)

**Q9:** "Are there any deadlines or milestones?"

- ASAP (urgent)
- Specific date
- Flexible timeline
- Unknown
- `multiSelect: false`

**Q10:** "Is there a target date for first working version?"

- Within a week
- 1-2 weeks
- 3-4 weeks
- Flexible
- `multiSelect: false`

### risks (2 questions)

**Q11:** "What could go wrong? What are the biggest risks?"

- Technical complexity
- Integration issues
- Performance concerns
- Unknown unknowns
- `multiSelect: true`

**Q12:** "Are there edge cases we should plan for upfront?"

- Empty/invalid input
- Concurrent access
- Failure scenarios
- None identified
- `multiSelect: true`

### existing (2 questions)

**Q13:** "What existing code or systems can we leverage?"

- Similar features
- Libraries or frameworks
- Infrastructure
- Start from scratch
- `multiSelect: true`

**Q14:** "What dependencies does this have?"

- Other features
- External services
- Data availability
- None (self-contained)
- `multiSelect: true`

### success (2 questions)

**Q15:** "How will we know this is successful?"

- User feedback
- Metrics
- Tests pass
- Requirements met
- `multiSelect: true`

**Q16:** "What are the acceptance criteria?"

- Feature works as described
- Tests validate behavior
- Documentation exists
- Performance acceptable
- `multiSelect: true`

---

## Default Categories by Focus

| Focus | Default Categories |
|-------|-------------------|
| `feat` | requirements, users, scope, success |
| `arch` | technical, risks, existing, scope |
| `api` | technical, requirements, success |
| `ux` | users, scope, success |
| `ops` | technical, risks, timeline |
| `auto` | requirements, users, technical, success |

---

## Custom Categories

Use `--categories` or `-C` flag:

```bash
/brainstorm d:5 "auth" -C req,tech,success
/brainstorm m:10 f "api" --categories req,usr,tech,exist
/brainstorm d:4 "caching" -C tech,risk
```

Category shortcuts: `req`, `usr`, `scp`, `tech`, `time`, `risk`, `exist`, `ok`, `all`

---

## Project-Type Question Extensions (v2.15.0)

Added via context-aware smart questions (`utils/brainstorm_context.py`).

| Project Type | Detection | Extra Questions |
|-------------|-----------|-----------------|
| R package | `DESCRIPTION` file | "CRAN submission planned?" / "Package dependencies to consider?" |
| Python | `pyproject.toml` | "PyPI distribution needed?" / "Python version constraints?" |
| Node.js | `package.json` | "npm publish target?" / "Bundle size concerns?" |
| Quarto | `_quarto.yml` | "Publication format?" / "Cross-references needed?" |
| Claude Plugin | `.claude-plugin/` | "Command count impact?" / "Backward compatibility?" |
| Teaching | `.flow/teach-config.yml` | "Student-facing?" / "Assessment integration?" |

### R Package Questions

**Q-R1:** "Is CRAN submission planned for this feature?"

- Yes, targeting CRAN
- No, internal/GitHub only
- Eventually, not this iteration
- Unsure
- `multiSelect: false`

**Q-R2:** "Are there R package dependencies to consider?"

- Tidyverse packages
- Base R only
- System libraries needed
- No new dependencies
- `multiSelect: true`

### Python Questions

**Q-PY1:** "Is PyPI distribution needed?"

- Yes, publish to PyPI
- No, internal only
- GitHub releases only
- Unsure
- `multiSelect: false`

**Q-PY2:** "Are there Python version constraints?"

- Python 3.9+ minimum
- Python 3.11+ (latest features)
- Must support 3.8+
- No constraints
- `multiSelect: false`

### Node.js Questions

**Q-NODE1:** "What's the npm publish target?"

- Public npm registry
- Private registry
- No npm publish needed
- GitHub packages
- `multiSelect: false`

**Q-NODE2:** "Are bundle size concerns relevant?"

- Yes, client-side bundle
- No, server-side only
- Moderate concern
- Not applicable
- `multiSelect: false`

### Quarto Questions

**Q-QMD1:** "What publication format is primary?"

- HTML website
- PDF document
- Reveal.js slides
- Multiple formats
- `multiSelect: false`

**Q-QMD2:** "Are cross-references needed?"

- Figure/table references
- Section references
- Citation references
- No cross-references
- `multiSelect: true`

### Claude Plugin Questions

**Q-PLUG1:** "How does this impact command count?"

- Adds new commands
- Modifies existing commands
- No command changes
- Deprecates commands
- `multiSelect: false`

**Q-PLUG2:** "Are there backward compatibility concerns?"

- Must maintain existing syntax
- Breaking changes acceptable
- Deprecation period needed
- No compatibility issues
- `multiSelect: false`

### Teaching Questions

**Q-TEACH1:** "Is this student-facing content?"

- Yes, students will see it
- No, instructor-only
- Both student and instructor
- Administrative tool
- `multiSelect: false`

**Q-TEACH2:** "Does this integrate with assessment?"

- Graded assignment
- Practice exercise
- No assessment link
- Rubric component
- `multiSelect: false`

---

## Dynamic Questions (v2.15.0)

Generated at runtime based on project state:

| Trigger | Question |
|---------|----------|
| Matching spec found | "Found SPEC-[name].md — load as context?" |
| Prior brainstorm exists | "Found prior brainstorm — resume or start fresh?" |
| Recent test failures | "Recent tests failing — address first?" |
| `.STATUS` has active task | "Current task: [task] — brainstorm related?" |

---

## Question Selection Algorithm

```python
def select_questions(topic, depth_count, categories, context):
    questions = load_question_bank()  # 16 base questions

    # 1. Filter by requested categories
    if categories != 'all':
        questions = [q for q in questions if q.category in categories]

    # 2. Add project-type questions
    project_type = detect_project_type()
    if project_type:
        questions += get_project_type_questions(project_type)

    # 3. Pre-fill from context
    for q in questions:
        if q.category in context.answers:
            q.pre_filled = context.answers[q.category]
            q.skippable = True

    # 4. Add dynamic questions based on state
    if context.has_failing_tests:
        questions.insert(0, DYNAMIC_Q_FAILING_TESTS)
    if context.matching_spec:
        questions.insert(0, DYNAMIC_Q_LOAD_SPEC)
    if context.prior_brainstorm:
        questions.insert(0, DYNAMIC_Q_RESUME)

    # 5. Trim to requested count
    return questions[:depth_count]
```

---

*Extracted from commands/workflow/brainstorm.md v2.4.0 + new v2.15.0 additions*
