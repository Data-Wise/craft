# /craft:restore Architecture

How `/craft:restore` combines git-activity and session-state recap into one
read-only output, and where each piece of logic actually lives.

## Pipeline Overview

```mermaid
flowchart TD
    A["User: /craft:restore [mode]"] --> B["commands/restore.md (thin shim)"]
    B --> C["adhd-workflow skill: Context Restoration (Sec 2)"]
    B --> D["dev/git skill: Operation 7 (mode-aware)"]

    C --> E[".STATUS state: Next Action / Blockers"]
    C --> F["Planning files: TODO/PLAN/ROADMAP"]
    C --> G["Obsidian flow status: obs doctor --layer flow"]

    D --> H["Git commits: today/this week"]
    D --> I["Branch ahead/behind, unpushed work"]

    C -.->|"also surfaces"| J["Recent git activity (48h), open PRs/issues"]
    D -.->|"also surfaces"| K["Open PRs: gh pr list"]

    J -.->|"de-duped against"| H
    K -.->|"de-duped against"| I

    E --> L["Combined Output"]
    F --> L
    G --> L
    H --> L
    I --> L

    L --> M["GIT ACTIVITY block, mode-aware"]
    L --> N["SESSION STATE block, single-verbosity"]
    L --> O["WHAT'S NEXT, one line"]
```

The dotted edges mark the one deliberate overlap: both source skills independently
fetch recent commits and open PRs. The shim resolves this at presentation time —
one combined git-activity block sourced from `dev/git` (mode-aware), not two
separate printouts of the same commits.

## Component Map

```mermaid
flowchart LR
    subgraph "Entry Point"
        CMD["commands/restore.md"]
    end

    subgraph "Session-State Source"
        ADHD["adhd-workflow/SKILL.md: Sec 2 Context Restoration"]
    end

    subgraph "Git-Activity Source"
        GITSKILL["dev/git/SKILL.md: Operation 7"]
    end

    subgraph "Sibling Commands"
        DONE["/craft:done, produces .STATUS"]
        NEXT["/craft:next, consumes .STATUS"]
    end

    CMD --> ADHD
    CMD --> GITSKILL
    DONE -.->|"writes"| ADHD
    ADHD -.->|"read by"| NEXT
```

## Why a Shim, Not a Reimplementation

`commands/restore.md` contains no recap logic of its own — every fact it
reports is computed by one of the two source skills. This mirrors the
`commands/done.md` convention already used across the plugin: the slash
command is a routing/discovery entry point; behavior changes happen in the
skill, never duplicated into the shim. See
[`SPEC-craft-restore-2026-07-17.md`](../specs/SPEC-craft-restore-2026-07-17.md)
for the decision record (combined output, no `--sync`, git-side-only modes).

## Boundaries (unchanged from the spec)

- **Read-only.** No `.STATUS` writes, no commits, no `--sync` flag.
- **No cross-plugin dispatch.** A `/restore` router forwarding to
  `savant:restore` for research projects was proposed alongside this command
  and confirmed structurally blocked — craft's `/do`/`/hub` routers cannot
  reach another plugin's namespace. Out of scope for this architecture.
- **Modes are git-side only.** `adhd-workflow`'s recap has no
  `default`/`detailed`/`summary` support today (verified before implementation,
  not assumed) — adding it is an open question in the spec, not shipped here.
