# Tutorial: arch:analyze — Codebase Architecture Analysis

By the end of this tutorial you will have:

- Run a full architecture analysis on your project
- Reviewed a scoped analysis on a subdirectory
- Understood the output format and how to act on findings

**Prerequisites:** craft installed, project with code to analyze.

---

## Step 1: Run a Full Analysis

```
/craft:arch:analyze
```

The command scans your codebase, identifies layers (controllers, services, models, utilities), and reports dependency patterns, coupling hotspots, and structural concerns.

Example output:

```
Architecture Analysis — my-project
────────────────────────────────────
Layers detected:
  • src/api/      → Controllers (12 files)
  • src/services/ → Business logic (8 files)
  • src/models/   → Data layer (5 files)
  • src/utils/    → Utilities (14 files)

Coupling concerns:
  ⚠️  src/api/auth.ts imports from src/models/ directly (bypass service layer)
  ⚠️  src/utils/ has 3 circular dependencies

Recommendations:
  1. Route auth.ts through AuthService to preserve layer boundaries
  2. Extract shared constants to break circular dep in utils/
```

---

## Step 2: Analyze a Subdirectory

Focus on a specific area:

```
/craft:arch:analyze --path src/api
```

Useful for scoping analysis to a module you're about to refactor.

---

## Step 3: Choose an Analysis Mode

```
/craft:arch:analyze --mode deep
/craft:arch:analyze --mode quick
/craft:arch:analyze --mode diagram
```

- `quick` — coupling summary only, fast
- `deep` — full dependency graph with recommendations (default)
- `diagram` — outputs a Mermaid architecture diagram

---

## What's Next

- Use `/craft:arch:plan` to turn analysis findings into an implementation plan
- Use `/craft:docs:mermaid` to render the diagram output
- Run after large refactors to verify architectural integrity is maintained
