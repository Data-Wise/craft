# Planning Commands

⏱️ **15 minutes** • 🟡 Intermediate • ✓ Project planning and roadmaps

> **TL;DR** (30 seconds)
>
> - **What:** `/craft:plan:feature` for feature breakdown; sprint planning and roadmap generation live in the `plan-orchestrator` skill (Modes 3–4), invoked via `/craft:plan`
> - **Why:** Break down features into tasks, organize team capacity, and visualize long-term project direction
> - **How:** Use `/craft:plan:feature` to plan individual features; ask `/craft:plan` for a sprint plan or roadmap and it routes to the right mode
> - **Next:** Try `/craft:plan:feature "your feature description"` to see a structured plan

Craft's planning commands help you organize work, estimate effort, identify dependencies, and communicate project direction with AI-powered task breakdown and timeline visualization.

---

## Commands Overview

| Command | Purpose | Time (default) | Focus |
|---------|---------|----------------|-------|
| `/craft:plan:feature` | Feature breakdown and scoping | < 60s | User stories, tasks, acceptance criteria |

Sprint planning and roadmap creation are Modes 3–4 of the `plan-orchestrator` skill (no
longer separate slash commands — see [`skills/orchestration/plan-orchestrator/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/orchestration/plan-orchestrator/SKILL.md)).
Invoke via `/craft:plan` and describe the sprint/roadmap need, or ask the skill directly.

All commands support flexible scoping (MVP/full/enterprise) and multiple output formats.

---

## `/craft:plan:feature` - Feature Planning

Break down features into actionable tasks with estimates, dependencies, and acceptance criteria.

> **Prompt refinement is on by default** — the `prompt-refiner` skill sharpens your prompt before acting. Use `--no-refine` to opt out. See [the --refine flag guide](../help/refine-flag.md).

### Quick Start

```bash
/craft:plan:feature "user profile page with avatar upload"
/craft:plan:feature "search functionality" --scope mvp
/craft:plan:feature "payment integration" --include-tests
/craft:plan:feature "notifications" --format github --output PLAN.md
```

### Options

| Option | Values | Default | Purpose |
|--------|--------|---------|---------|
| `--scope` | mvp, full, enterprise | full | Planning scope |
| `--format` | markdown, jira, github | markdown | Output format |
| `--output` | filename | stdout | Save to file |
| `--include-tests` | boolean | false | Include test planning |

### What It Does

1. **Analyzes feature request** and project context
2. **Creates user stories** in "who, what, why" format
3. **Breaks into tasks** with time estimates (hours)
4. **Identifies dependencies** and blocking items
5. **Lists risks** and mitigation strategies
6. **Defines acceptance criteria** for completion

### Example: MVP Scope

```bash
/craft:plan:feature "user authentication" --scope mvp
```

**Output:**

```
Feature Plan: User Authentication (MVP)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User Stories:
  1. As a user, I want to create an account so I can access the app
  2. As a user, I want to log in with email/password
  3. As a user, I want to reset my password if I forget it

Tasks:

  Backend (10 hours)
  ├── [ ] Create user model and database (2h)
  ├── [ ] Implement password hashing (1h)
  ├── [ ] Build sign-up API endpoint (2h)
  ├── [ ] Build login API endpoint (2h)
  ├── [ ] Implement session management (2h)
  └── [ ] Add password reset flow (1h)

  Frontend (8 hours)
  ├── [ ] Create sign-up form component (2h)
  ├── [ ] Create login form component (2h)
  ├── [ ] Add form validation (1h)
  ├── [ ] Implement error handling (1h)
  ├── [ ] Add password reset modal (2h)

  Testing (3 hours)
  ├── [ ] Write backend tests (2h)
  └── [ ] Write frontend tests (1h)

Dependencies:
  - Database must be set up first
  - Auth system is blocking social features

Risks:
  ⚠ Password reset email delivery might fail
  ⚠ Rate limiting needed for login attempts
  ⚠ Password complexity requirements TBD

Acceptance Criteria:
  ✓ User can sign up with valid email/password
  ✓ User can log in with correct credentials
  ✓ Session persists across page refresh
  ✓ User can reset password via email link
  ✓ Invalid credentials show clear error
  ✓ All tests pass (> 90% coverage)

Total Estimate: 21 hours (2.5-3 days)
Effort Level: ⚡ Low-Medium
```

### Example: Full Scope

```bash
/craft:plan:feature "user profile management" --scope full --include-tests
```

**Output:**

```
Feature Plan: User Profile Management (Full)
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

User Stories:
  1. As a user, I want to view my complete profile
  2. As a user, I want to upload and customize my avatar
  3. As a user, I want to edit my personal information
  4. As a user, I want to manage privacy settings
  5. As a user, I want to see my activity history
  6. As a user, I want to manage connected accounts

Tasks:

  Backend (18 hours)
  ├── [ ] Create profile schema with all fields (2h)
  ├── [ ] Build profile retrieval endpoint (1h)
  ├── [ ] Build profile update endpoint (2h)
  ├── [ ] Implement avatar upload handler (2h)
  ├── [ ] Add image optimization/resizing (2h)
  ├── [ ] Build activity logging system (3h)
  ├── [ ] Implement privacy settings (2h)
  ├── [ ] Add connected accounts management (2h)

  Frontend (14 hours)
  ├── [ ] Create profile view page (3h)
  ├── [ ] Build avatar upload widget (2h)
  ├── [ ] Create edit profile form (3h)
  ├── [ ] Implement privacy controls (2h)
  ├── [ ] Build activity history view (2h)
  ├── [ ] Create account connections UI (2h)

  Infrastructure (4 hours)
  ├── [ ] Set up S3 bucket for avatars (1h)
  ├── [ ] Configure CDN with cache invalidation (2h)
  ├── [ ] Set up image processing queue (1h)

  Testing (8 hours)
  ├── [ ] Write backend API tests (3h)
  ├── [ ] Write frontend component tests (2h)
  ├── [ ] Integration tests (2h)
  ├── [ ] Load test image uploads (1h)

Dependencies:
  - User authentication must be complete
  - S3 bucket setup needed before upload
  - Image processing library selection

Risks:
  ⚠ Image upload file size limits
  ⚠ CDN cache invalidation for avatar changes
  ⚠ Privacy settings complexity
  ⚠ Large file upload performance

Acceptance Criteria:
  ✓ User can view complete profile with all fields
  ✓ Avatar upload works (jpg, png, max 10MB)
  ✓ Images auto-resize and optimize
  ✓ Avatar displays in header, profile, comments
  ✓ User can edit all profile information
  ✓ Privacy settings control visibility
  ✓ Activity history shows recent actions
  ✓ Connected accounts can be added/removed
  ✓ All tests pass (> 85% coverage)
  ✓ Avatar CDN serves cached optimized images

Total Estimate: 44 hours (5-6 days)
Effort Level: 🔧 Medium
```

### Export Formats

**GitHub Format:**

```bash
/craft:plan:feature "search" --format github --output search-plan.md
# Creates GitHub issue template with task list
```

**Jira Format:**

```bash
/craft:plan:feature "search" --format jira
# Creates epic/story structure for Jira import
```

---

## Sprint Planning & Roadmaps

Sprint planning and roadmap generation are Modes 3–4 of the `plan-orchestrator` skill —
folded in during the v4 command consolidation (2026-07). They are no longer separate
`/craft:plan:sprint` / `/craft:plan:roadmap` slash commands. Invoke `/craft:plan`
and describe the sprint or roadmap need, or read
[`skills/orchestration/plan-orchestrator/SKILL.md`](https://github.com/Data-Wise/craft/blob/dev/skills/orchestration/plan-orchestrator/SKILL.md)
directly for the canonical procedure (options, output formats, examples).

## Common Workflows

### Workflow 1: Plan and Deliver a Feature

```bash
# Step 1: Plan the feature
/craft:plan:feature "search functionality" --scope mvp --include-tests

# Step 2: Create feature branch
/craft:git:branch feature/search

# Step 3: Assign to sprint (plan-orchestrator skill, Mode 3)
/craft:plan "sprint plan: add search to v0.2"

# Step 4: Work through tasks
# (implement, test, review)

# Step 5: Verify against acceptance criteria
/craft:test

# Step 6: Merge and celebrate
git merge feature/search
```

### Workflow 2: Enterprise Scoping (MVP → Full → Enterprise)

```bash
# Step 1: MVP scope - minimum viable
/craft:plan:feature "payment integration" --scope mvp

# Step 2: Full scope - production ready
/craft:plan:feature "payment integration" --scope full

# Step 3: Enterprise scope - advanced features
/craft:plan:feature "payment integration" --scope enterprise

# Step 4: Choose appropriate scope based on timeline
/craft:plan "sprint plan: deliver payment (full scope)"
```

---

## Integration with Other Commands

Planning commands work best with:

| Command | Use Case |
|---------|----------|
| `/craft:do` | AI routes planning tasks with task suggestions |
| `/craft:arch:plan` | Architecture needed before feature planning |
| `/craft:code:refactor` | Implement planned features |
| `/craft:test` | Validate task completion |
| `/folio:docs:sync` | Keep documentation aligned with roadmap |
| `/craft:git:branch` | Create feature branches from plans |
| `/craft:check` | Verify sprint goals before delivery |

---

## Tips

!!! tip "Start with MVP"
    Begin with `--scope mvp` to understand minimum viable scope, then expand to full/enterprise as needed.

!!! tip "Break It Down"
    Feature plans are most useful when tasks are < 4 hours each. Break down larger tasks further.

!!! tip "Link Dependencies"
    Identify blocking items early with `--include-tests` to account for testing time in estimates.

!!! tip "Regular Roadmap Updates"
    Update your roadmap monthly with `--update` as priorities change and dependencies shift.

!!! tip "Use Format Export"
    Export plans as GitHub issues (`--format github`) to integrate with your workflow.

!!! success "Capacity Planning"
    Always plan sprints at 80% capacity, leaving 20% for unexpected issues and interruptions.

!!! success "Track Metrics"
    Review velocity trends across sprints to improve estimation accuracy over time.

---

## Learn More

- [Architecture Commands](arch.md) - Plan architecture before features
- [Code & Testing Commands](code.md) - Implement planned tasks
- [Distribution Commands](dist.md) - Release planned milestones
- [Git Commands](git.md) - Manage feature branches
- [Visual Workflows](../workflows/index.md) - See planning workflows in action
