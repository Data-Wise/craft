---
description: "/craft:docs:generate - Unified Documentation Generator Router"
category: docs
arguments:
  - name: type
    description: "Which generator to run: api, guide, help, prompt, quickstart, site, tutorial, website, workflow"
    required: true
---

# /craft:docs:generate - Unified Documentation Generator Router

Thin router for the 9 documentation generator commands. Each generator has genuinely
distinct logic (different templates, different orchestration, different output
formats) — this command exists for discoverability (`/craft:docs:generate <type>`
instead of remembering 9 separate names), not to reimplement any of them.

## Usage

```bash
/craft:docs:generate api          # OpenAPI/Swagger spec generation
/craft:docs:generate guide        # Orchestrated feature guide + demo + refcard
/craft:docs:generate help         # Help page generator
/craft:docs:generate prompt       # Documentation prompt generator
/craft:docs:generate quickstart   # 5-minute quickstart guide
/craft:docs:generate site         # Website documentation focus
/craft:docs:generate tutorial     # Interactive tutorial generator
/craft:docs:generate website      # ADHD-friendly website enhancement
/craft:docs:generate workflow     # Workflow documentation generator
```

## When invoked

1. **Validate `type`.** Must be one of: `api`, `guide`, `help`, `prompt`,
   `quickstart`, `site`, `tutorial`, `website`, `workflow`. If missing or
   invalid, show this list and stop.
2. **Delegate to the canonical command file — do not reimplement.** Load and
   follow the matching file exactly, passing through any remaining arguments:

   | `type` | Canonical file |
   |--------|----------------|
   | `api` | [`commands/docs/api.md`](api.md) |
   | `guide` | [`commands/docs/guide.md`](guide.md) |
   | `help` | [`commands/docs/help.md`](help.md) |
   | `prompt` | [`commands/docs/prompt.md`](prompt.md) |
   | `quickstart` | [`commands/docs/quickstart.md`](quickstart.md) |
   | `site` | [`commands/docs/site.md`](site.md) |
   | `tutorial` | [`commands/docs/tutorial.md`](tutorial.md) |
   | `website` | [`commands/docs/website.md`](website.md) |
   | `workflow` | [`commands/docs/workflow.md`](workflow.md) |

3. **Any change to a generator's behavior** — templates, output format,
   flags — belongs in that generator's own file, never duplicated here.

## Why a router, not a merge

Each of the 9 generators was read in full during
`SPEC-command-namespace-reorganization-2026-07-05.md`'s grill: they have
genuinely different internal logic (orchestration-of-other-commands for
`guide`, template-fill for `quickstart`, OpenAPI-specific sub-actions for
`api`, etc.) — not the shared-core-with-a-filter shape that `code:test`'s
category argument has. Deleting the 9 direct entry points and inlining
their bodies into one dispatcher would risk losing behavior mid-merge for
no real simplification. This router adds the shorter/discoverable
`/craft:docs:generate <type>` path **alongside** the existing direct
commands (`/craft:docs:guide`, `/craft:docs:api`, etc.), which keep working
unchanged.

## See Also

- `/craft:docs:api`, `/craft:docs:guide`, `/craft:docs:help`, `/craft:docs:prompt`, `/craft:docs:quickstart`, `/craft:docs:site`, `/craft:docs:tutorial`, `/craft:docs:website`, `/craft:docs:workflow` — the 9 canonical generators, still directly invocable
- `/craft:docs:check` — validate what was generated
- `/craft:hub` — discover all commands
