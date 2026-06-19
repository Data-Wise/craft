# Tutorial: arch:plan — Architecture Planning

By the end of this tutorial you will have:

- Created an architecture plan for a new feature
- Refined it with the `--refine` flag
- Understood how the plan output feeds into implementation

**Prerequisites:** craft installed, a feature or refactor in mind.

---

## Step 1: Generate an Architecture Plan

Describe what you want to build:

```
/craft:arch:plan "add OAuth2 authentication with Google and GitHub providers"
```

The command analyzes your existing codebase patterns, then produces a structured plan:

```
Architecture Plan — OAuth2 Authentication
─────────────────────────────────────────
Phase 1: Foundation
  • Add OAuthProvider interface (src/auth/providers/base.ts)
  • Implement GoogleProvider (src/auth/providers/google.ts)
  • Implement GitHubProvider (src/auth/providers/github.ts)

Phase 2: Integration
  • Update AuthService to delegate to providers
  • Add /auth/callback/:provider route
  • Store tokens in session (not localStorage)

Phase 3: UI
  • Add "Sign in with Google" button to login page
  • Add "Sign in with GitHub" button to login page

Files to create: 4
Files to modify: 3
Estimated scope: Medium (3–5 hours)
```

---

## Step 2: Refine the Plan

Use `--refine` to pre-process the request through prompt refinement before planning:

```
/craft:arch:plan --refine "add auth"
```

The refiner expands the brief request into a precise specification, then generates the plan. This produces better-scoped output for vague prompts.

---

## Step 3: Act on the Plan

The architecture plan is designed to feed directly into orchestration:

```
/craft:orchestrate "implement the OAuth2 plan from arch:plan"
```

Or use it as a reference while implementing manually — the phase breakdown maps cleanly to feature branches.

---

## What's Next

- Run `/craft:arch:analyze` first on existing code to understand current patterns
- Use `/craft:orchestrate:drive` with a SPEC derived from the plan for fully-automated implementation
- Architecture plans are good inputs for `/craft:workflow:brainstorm` when exploring trade-offs
