# Craft Command Parameters Reference

Comprehensive parameter reference for all 97 Craft commands.

**Version**: v1.24.0 | **Last Updated**: 2026-01-17

---

## Quick Parameter Guide

### Parameter Types

| Type | Example | Description |
|------|---------|-------------|
| `string` | `"auth"`, `src/file.ts` | Text value |
| `enum` | `default` \| `debug` \| `optimize` | One of specific options |
| `number` | `8000`, `60` | Numeric value |
| `boolean` | `true` / `false` | True or false |
| `array` | `["a.ts", "b.ts"]` | List of values |

### Common Parameters

| Parameter | Type | Used In | Purpose |
|-----------|------|---------|---------|
| `mode` | enum | Most commands | Execution mode: `default`, `debug`, `optimize`, `release` |
| `--dry-run` / `-n` | boolean | Mutation commands | Preview changes without executing |
| `--fix` | boolean | Validation commands | Auto-fix detected issues |
| `--verbose` / `-v` | boolean | Most commands | Show detailed output |
| `--output` | string | Doc generation | Save output to file |
| `path` | string | File operations | Target file or directory |

---

## Root Commands Parameters

### /craft:do

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| task | string | Yes | - | - | Task description (natural language) |
| mode | enum | No | `default` | - | `default`, `debug`, `optimize`, `release` |
| complexity | enum | No | - | - | Override: `simple`, `moderate`, `complex` |
| dry-run | boolean | No | false | `-n` | Preview routing without executing |

**Environment Variables**:

- `CRAFT_MODE` - Default execution mode
- `CRAFT_COMPLEXITY_OVERRIDE` - Override complexity scoring

---

### /craft:check

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| scope | enum | No | `all` | - | `all`, `code`, `tests`, `git`, `docs` |
| mode | enum | No | `default` | - | Execution mode |
| fix | boolean | No | false | `--auto-fix` | Auto-fix fixable issues |
| dry-run | boolean | No | false | `-n` | Preview fixes |

**Output Scopes**:

- `code` - Linting, style, complexity
- `tests` - Test coverage, failures
- `git` - Branch status, commits
- `docs` - Broken links, completeness
- `all` - Everything (default)

---

### /craft:hub

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| query | string | No | - | - | Search commands by keyword |
| category | string | No | - | - | Filter by category |
| verbose | boolean | No | false | `-v` | Show full help text |

**Categories**:

- `arch` - Architecture commands
- `code` - Code development
- `docs` - Documentation
- `git` - Git workflows
- `test` - Testing
- `site` - Site generation
- `workflow` - Productivity workflows

---

### /craft:orchestrate

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| task | string | Yes | - | - | Task description |
| mode | enum | No | `default` | - | Execution mode |
| agents | number | No | 2 | `--agent-count` | Number of parallel agents |
| background | boolean | No | true | `-bg` | Run agents in background |

**Modes Impact on Agents**:

- `default` - 2 agents max
- `debug` - 1 agent (sequential)
- `optimize` - 4 agents max
- `release` - 4 agents max

---

### /craft:smart-help

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| command | string | No | - | - | Command to help with |
| examples | boolean | No | false | `-e` | Show usage examples |
| related | boolean | No | false | `--show-related` | Show related commands |

---

### /craft:discovery-usage

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| format | enum | No | `markdown` | - | `markdown`, `json`, `html` |

---

## Architecture Commands Parameters

### /craft:arch:analyze

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| path | string | No | `.` | - | Directory to analyze |
| mode | enum | No | `default` | - | Execution mode |
| output | string | No | stdout | `--save-to` | Save output to file |
| depth | number | No | 3 | - | Analysis depth (1-5) |
| metrics | boolean | No | true | - | Include metrics |

---

### /craft:arch:diagram

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| type | enum | No | `system` | - | `system`, `dataflow`, `class`, `sequence` |
| output | string | No | stdout | `--save-to` | Save diagram |
| format | enum | No | `mermaid` | - | `mermaid`, `svg`, `png` |
| title | string | No | - | - | Diagram title |
| detailed | boolean | No | false | `-d` | Include detailed info |

---

### /craft:arch:plan

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| scope | string | Yes | - | - | What to plan |
| timeline | enum | No | `flexible` | - | `urgent`, `normal`, `flexible` |
| estimate | boolean | No | true | - | Include estimates |
| risks | boolean | No | true | - | Include risk analysis |

---

### /craft:arch:review

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| path | string | No | `.` | - | File/directory to review |
| detailed | boolean | No | false | `-d` | Detailed analysis |
| focus | string | No | - | - | Focus area |

---

## Code Commands Parameters

### /craft:code:lint

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| mode | enum | No | `default` | - | `default`, `debug`, `optimize`, `release` |
| path | string | No | `.` | - | File or directory |
| fix | boolean | No | false | `--auto-fix` | Auto-fix issues |
| dry-run | boolean | No | false | `-n` | Preview fixes |
| rules | string | No | - | - | Specific rules to check |

**Mode Behaviors**:

- `default` - Quick style check (< 10s)
- `debug` - All rules + suggestions (< 120s)
- `optimize` - Performance focus (< 180s)
- `release` - Comprehensive + strict (< 300s)

---

### /craft:code:refactor

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| pattern | string | Yes | - | - | Refactoring pattern |
| path | string | No | `.` | - | Target directory |
| dry-run | boolean | No | false | `-n` | Preview changes |
| no-test | boolean | No | false | - | Skip test running |

**Common Patterns**:

- `rename <old> to <new>` - Rename identifier
- `extract method <name>` - Extract method
- `inline variable <name>` - Inline variable
- `move to <location>` - Move code

---

### /craft:code:test-gen

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| type | enum | No | `unit` | - | `unit`, `integration`, `e2e` |
| source | string | No | `.` | - | Source file/dir |
| output | string | No | auto | `--save-to` | Output directory |
| template | string | No | - | - | Test template |

---

### /craft:code:debug

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| command | string | Yes | - | - | Command to debug |
| verbose | boolean | No | false | `-v` | Verbose traces |
| breakpoint | string | No | - | - | Breakpoint location |
| port | number | No | 9229 | - | Debug server port |

---

### /craft:code:demo

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| script | string | Yes | - | - | Demo script file |
| format | enum | No | `gif` | - | `gif`, `asciinema`, `svg` |
| speed | number | No | 1.0 | - | Playback speed (0.5-2.0) |
| width | number | No | 80 | - | Terminal width |
| height | number | No | 24 | - | Terminal height |

---

### /craft:code:coverage

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| mode | enum | No | `default` | - | Execution mode |
| threshold | number | No | 80 | - | Minimum % required |
| report | enum | No | stdout | `--save-to` | `text`, `html`, `json`, `xml` |
| exclude | array | No | `[node_modules]` | - | Exclude patterns |

---

### /craft:code:deps-check

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| fix | boolean | No | false | `--auto-fix` | Auto-update |
| security | boolean | No | false | - | Security only |
| major | boolean | No | false | - | Check major versions |
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:code:deps-audit

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| licenses | boolean | No | false | `--check-licenses` | Include licenses |
| tree | boolean | No | false | `--show-tree` | Show dependency tree |
| json | boolean | No | false | `--json` | JSON output |

---

### /craft:code:ci-local

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| dry-run | boolean | No | false | `-n` | Preview |
| verbose | boolean | No | false | `-v` | Verbose output |

---

### /craft:code:ci-fix

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| issue | string | No | - | - | Specific issue |
| apply | boolean | No | false | - | Auto-apply |
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:code:docs-check

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| strict | boolean | No | false | - | Enforce all |
| fix | boolean | No | false | `--auto-fix` | Auto-add |
| language | string | No | `en` | - | Documentation language |

---

### /craft:code:release

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| version | string | No | auto | - | Version to release |
| dry-run | boolean | No | false | `-n` | Preview |
| skip-tests | boolean | No | false | - | Skip tests |
| skip-changelog | boolean | No | false | - | Skip changelog |

---

## CI/CD Commands Parameters

### /craft:ci:generate

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| platform | enum | No | `github` | - | `github`, `gitlab`, `circle`, `travis` |
| template | string | No | `default` | - | Workflow template |
| output | string | No | auto | `--save-to` | Output path |
| nodejs | boolean | No | false | - | Node.js workflow |
| python | boolean | No | false | - | Python workflow |

---

### /craft:ci:detect

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| recommended | boolean | No | false | `-r` | Show recommendation |

---

### /craft:ci:validate

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| file | string | No | auto | - | Workflow file |
| strict | boolean | No | false | - | Strict validation |
| fix | boolean | No | false | `--auto-fix` | Auto-fix |

---

## Check Commands Parameters

### /craft:check:gen-validator

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| type | enum | Yes | - | - | `lint`, `test`, `link`, `custom` |
| output | string | No | auto | `--save-to` | Save validator |
| hooks | boolean | No | true | - | Install git hook |

---

## Distribution Commands Parameters

### /craft:dist:pypi

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| version | string | No | from manifest | - | Version to publish |
| dry-run | boolean | No | false | `-n` | Preview |
| test | boolean | No | false | `--testpypi` | Use TestPyPI |
| token | string | No | env var | `--token` | PyPI token |

---

### /craft:dist:homebrew

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| version | string | No | latest tag | - | Version to use |
| tap | string | No | auto | - | Homebrew tap |
| url | string | No | auto | - | Download URL |
| sha | string | No | auto | - | SHA256 hash |

---

### /craft:dist:curl-install

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| output | string | No | `install.sh` | `--save-to` | Output file |
| hosting | string | No | auto | - | Where script hosted |
| version | string | No | latest | - | Version to install |

---

## Documentation Commands Parameters

### /craft:docs:api

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| format | enum | No | `openapi` | - | `openapi`, `swagger`, `markdown` |
| output | string | No | auto | `--save-to` | Output file |
| title | string | No | auto | - | API title |
| version | string | No | from manifest | - | API version |

---

### /craft:docs:changelog

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| from | string | No | last tag | - | From commit/tag |
| to | string | No | HEAD | - | To commit/tag |
| format | enum | No | `markdown` | - | `markdown`, `html`, `json` |
| output | string | No | stdout | `--save-to` | Output file |

---

### /craft:docs:check-links

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| external | boolean | No | false | `--check-external` | Check external URLs |
| fix | boolean | No | false | `--auto-fix` | Auto-fix |
| timeout | number | No | 5000 | - | URL timeout (ms) |
| report | enum | No | stdout | `--save-to` | Report format |

---

### /craft:docs:check

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| strict | boolean | No | false | - | Strict requirements |

---

### /craft:docs:claude-md

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| sync | boolean | No | true | `--auto-sync` | Sync instructions |

---

### /craft:docs:demo

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| type | enum | No | `command` | - | `command`, `feature`, `workflow` |
| output | string | No | auto | `--save-to` | Output file |

---

### /craft:docs:guide

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| topic | string | Yes | - | - | Guide topic |
| level | enum | No | `beginner` | - | `beginner`, `intermediate`, `advanced` |
| output | string | No | auto | `--save-to` | Output file |

---

### /craft:docs:help

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| include-examples | boolean | No | true | `--no-examples` | Include examples |
| format | enum | No | markdown | - | `markdown`, `text`, `html` |

---

### /craft:docs:lint

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| fix | boolean | No | false | `--auto-fix` | Auto-fix |
| rules | string | No | - | - | Specific rules |

---

### /craft:docs:mermaid

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| type | enum | Yes | - | - | `flowchart`, `sequence`, `erd`, `gantt`, `class` |
| interactive | boolean | No | false | `-i` | Interactive |
| output | string | No | auto | `--save-to` | Output file |

---

### /craft:docs:nav-update

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| auto | boolean | No | true | `--manual` | Auto-detect |

---

### /craft:docs:prompt

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| task | string | Yes | - | - | Documentation task |

---

### /craft:docs:quickstart

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| topic | string | Yes | - | - | Quick-start topic |
| output | string | No | auto | `--save-to` | Output file |

---

### /craft:docs:site

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| action | enum | Yes | - | - | `build`, `deploy`, `preview`, `serve` |
| port | number | No | 8000 | - | Server port |
| production | boolean | No | false | - | Production build |

---

### /craft:docs:sync

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| fix | boolean | No | false | `--auto-fix` | Auto-fix |

---

### /craft:docs:tutorial

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| topic | string | Yes | - | - | Tutorial topic |
| interactive | boolean | No | false | `-i` | Interactive |
| output | string | No | auto | `--save-to` | Output file |

---

### /craft:docs:update

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| all | boolean | No | false | `-a` | Update all |
| field | string | No | - | - | Specific field |

---

### /craft:docs:workflow

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| workflow | string | Yes | - | - | Workflow name |
| output | string | No | auto | `--save-to` | Output file |

---

### /craft:docs:website

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| action | enum | Yes | - | - | `init`, `add`, `remove`, `restructure` |
| name | string | No | - | - | Section name |

---

## Git Commands Parameters

### /craft:git:init

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| template | enum | No | `default` | - | `default`, `monorepo`, `minimal` |
| hooks | boolean | No | true | `--no-hooks` | Install hooks |

---

### /craft:git:status

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| detailed | boolean | No | false | `-d` | Detailed info |
| suggest | boolean | No | true | `--no-suggest` | Show suggestions |

---

### /craft:git:sync

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| force | boolean | No | false | `--dangerous-force` | Force sync |
| rebase | boolean | No | true | `--merge` | Rebase vs merge |
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:git:branch

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| action | enum | Yes | - | - | `create`, `list`, `delete`, `rename` |
| name | string | No | - | - | Branch name |
| type | enum | No | `feature` | - | `feature`, `hotfix`, `release` |

---

### /craft:git:worktree

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| action | enum | Yes | - | - | `setup`, `create`, `move`, `list`, `clean`, `install`, `finish` |
| branch | string | No | - | - | Branch name |
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:git:clean

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| dry-run | boolean | No | false | `-n` | Preview |
| remote | boolean | No | false | `--clean-remote` | Clean remote |

---

### /craft:git:git-recap

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| topic | enum | No | - | - | `basics`, `branching`, `merging`, `rebasing` |
| interactive | boolean | No | true | `--no-interactive` | Interactive |

---

## Plan Commands Parameters

### /craft:plan:feature

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| feature | string | Yes | - | - | Feature name |
| timeline | enum | No | `flexible` | - | `urgent`, `normal`, `flexible` |
| scope | enum | No | `medium` | - | `small`, `medium`, `large` |

---

### /craft:plan:sprint

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| duration | string | No | `1w` | - | Sprint duration |
| capacity | number | No | 40 | - | Team capacity (hours) |

---

### /craft:plan:roadmap

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| horizon | enum | No | `1y` | - | `6m`, `1y`, `2y` |
| format | enum | No | `timeline` | - | `timeline`, `kanban`, `swimlanes` |

---

## Site Commands Parameters

### /craft:site:init

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| template | enum | No | `mkdocs` | - | `mkdocs`, `hugo`, `jekyll`, `vuepress` |
| theme | string | No | `default` | - | Theme name |

---

### /craft:site:build

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| production | boolean | No | false | `--prod` | Production build |
| minify | boolean | No | false | `--compress` | Minify assets |

---

### /craft:site:preview

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| port | number | No | 8000 | `-p` | Server port |
| watch | boolean | No | true | `--no-watch` | Watch files |

---

### /craft:site:deploy

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| platform | enum | No | `github-pages` | - | `github-pages`, `netlify`, `vercel`, `s3` |
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:site:publish

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| skip-build | boolean | No | false | - | Skip build |

---

### /craft:site:add

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| path | string | Yes | - | - | Page path |
| template | string | No | - | - | Template name |

---

### /craft:site:check

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| strict | boolean | No | false | - | Strict validation |

---

### /craft:site:update

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:site:status

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| details | boolean | No | false | `-d` | Detailed info |

---

### /craft:site:progress

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| breakdown | boolean | No | false | `--by-section` | Show breakdown |

---

### /craft:site:audit

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| external | boolean | No | false | `--check-external` | Check external |
| performance | boolean | No | true | `--no-perf` | Performance metrics |

---

### /craft:site:consolidate

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:site:nav

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| auto | boolean | No | true | `--manual` | Auto-generate |

---

### /craft:site:theme

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| theme | string | No | - | - | Theme name |
| custom | boolean | No | false | - | Use custom theme |

---

### /craft:site:create

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| name | string | Yes | - | - | Site name |
| template | string | No | `default` | - | Template name |

---

## Test Commands Parameters

### /craft:test:run

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| mode | enum | No | `default` | - | `default`, `debug`, `optimize`, `release` |
| path | string | No | `.` | - | Test file/dir |
| filter | string | No | - | `--match` | Filter pattern |
| dry-run | boolean | No | false | `-n` | Preview |

---

### /craft:test:generate

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| source | string | No | `.` | - | Source file |
| type | enum | No | `unit` | - | `unit`, `integration`, `e2e` |

---

### /craft:test:coverage

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| threshold | number | No | 80 | - | Minimum % |
| report | enum | No | `text` | - | `text`, `html`, `json`, `xml` |

---

### /craft:test:debug

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| test | string | No | - | - | Test name |
| breakpoint | boolean | No | false | `-b` | Enable breakpoint |

---

### /craft:test:watch

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| filter | string | No | - | - | Filter pattern |
| coverage | boolean | No | false | `-c` | Show coverage |

---

### /craft:test:cli-gen

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| command | string | Yes | - | - | Command to test |

---

### /craft:test:cli-run

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| verbose | boolean | No | false | `-v` | Verbose |

---

## Workflow Commands Parameters

### /craft:workflow:brainstorm

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| topic | string | Yes | - | - | Topic to brainstorm |
| duration | number | No | 20 | `--time` | Duration (minutes) |
| save | boolean | No | true | `--no-save` | Save to file |

---

### /craft:workflow:focus

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| duration | number | Yes | - | - | Duration (minutes) |
| task | string | No | - | - | Task name |

---

### /craft:workflow:next

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| context | string | No | auto | - | Current context |

---

### /craft:workflow:stuck

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| problem | string | No | - | - | Problem description |

---

### /craft:workflow:done

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| message | string | No | - | - | Completion message |
| commit | boolean | No | true | `--no-commit` | Commit |

---

### /craft:workflow:recap

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| detail | boolean | No | false | `-d` | Detailed |

---

### /craft:workflow:refine

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| task | string | Yes | - | - | Task to refine |

---

### /craft:workflow:spec-review

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| spec | string | No | - | - | Spec file |
| detailed | boolean | No | false | `-d` | Detailed |

---

### /craft:workflow:adhd-guide

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| topic | string | No | - | - | Specific topic |

---

### /craft:workflow:task-status

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| format | enum | No | `summary` | - | `summary`, `detailed`, `json` |

---

### /craft:workflow:task-output

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| task | string | No | - | - | Task ID |
| tail | number | No | 50 | - | Last N lines |

---

### /craft:workflow:task-cancel

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| task | string | Yes | - | - | Task ID |

---

## Utility Commands Parameters

### /craft:utils:readme-teach-config

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| examples | boolean | No | false | `-e` | Show examples |

---

### /craft:utils:readme-semester-progress

| Parameter | Type | Required | Default | Aliases | Description |
|-----------|------|----------|---------|---------|-------------|
| template | boolean | No | false | `-t` | Show template |

---

## Parameter Validation Rules

### String Parameters

- Minimum length: 1 character
- Maximum length: 1000 characters (unless noted)
- Special characters: Generally allowed, be quoted if containing spaces

### Numeric Parameters

- Port numbers: 1024-65535 (privileged: 1-1023 not recommended)
- Percentages: 0-100
- Timeouts: milliseconds, 0 for infinite
- Durations: minutes, seconds, hours (parse intelligently)

### Enum Parameters

- Case-insensitive in most commands
- Whitespace trimmed automatically
- Invalid values show available options

### Path Parameters

- Absolute paths accepted
- Relative paths (`.`, `..` supported)
- Glob patterns in some commands (`*.ts`, `src/**/*.js`)
- Tilde expansion (`~` → home directory)

### Boolean Parameters

- Accepts: `true`, `false`, `1`, `0`, `yes`, `no`
- Long form: `--flag-name`
- Short form: `-n` or `-f`
- Negation: `--no-flag-name`

---

## Environment Variables

### Global

| Variable | Purpose | Example |
|----------|---------|---------|
| `CRAFT_MODE` | Default execution mode | `export CRAFT_MODE=optimize` |
| `CRAFT_HOME` | Craft config directory | `~/.craft` |
| `CRAFT_QUIET` | Suppress output | `export CRAFT_QUIET=1` |

### Command-Specific

| Command | Variable | Purpose |
|---------|----------|---------|
| `/craft:code:release` | `CRAFT_RELEASE_TOKEN` | Release token |
| `/craft:dist:pypi` | `PYPI_TOKEN` | PyPI authentication |
| `/craft:site:deploy` | `NETLIFY_TOKEN` | Netlify deployment |
| `/craft:git:*` | `GIT_AUTHOR_NAME` | Git author |

---

**Last Updated**: January 17, 2026 | **Version**: v1.24.0
