# Tutorial: RTK (rtk-ai/rtk) — CLI Token Proxy for Claude Code

**Status:** Reference tutorial — not a proposal, not implemented
**Date:** 2026-07-01
**Source:** [github.com/rtk-ai/rtk](https://github.com/rtk-ai/rtk) (README, v0.28.2 at time of writing)
**Scope:** Installation, setup, usage, compatibility with craft, caveats, suggested workflows. No adoption decision is made here — this is background for you to decide.

---

## 0. What it is, in one paragraph

RTK is a single Rust binary that sits between Claude Code and your shell. It installs a Claude Code hook that transparently rewrites Bash commands you run (`git status` → `rtk git status`) so the *output* Claude sees is filtered, grouped, truncated, and deduplicated before it ever reaches context — claimed 60-90% token reduction on common dev commands (git, test runners, linters, package managers, Docker/K8s, AWS CLI). It only touches the `Bash` tool; Claude Code's native `Read`, `Grep`, and `Glob` tools bypass it entirely.

---

## 1. Installation

Pick one:

```bash
# Homebrew (recommended on macOS)
brew install rtk

# Quick install script (installs to ~/.local/bin)
curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh

# From source via cargo
cargo install --git https://github.com/rtk-ai/rtk

# Pre-built binary from GitHub Releases (macOS arm64/x86_64, Linux, Windows)
```

Verify:

```bash
rtk --version   # should print "rtk 0.28.2" (or later)
rtk gain        # should show token savings stats (empty on first run)
```

**Naming collision warning:** a *different* project called "rtk" (Rust Type Kit) exists on crates.io. If `rtk gain` fails after a `cargo install rtk` (without `--git`), you installed the wrong package — use the `--git` form above.

---

## 2. Setting it up for Claude Code

```bash
rtk init -g                 # installs the PreToolUse hook + RTK.md, global scope
rtk init --show              # verify what got installed
```

Then **restart Claude Code** (a fresh session) for the hook to take effect.

What `rtk init -g` actually does:

- Registers a `PreToolUse` hook matched on the `Bash` tool in `~/.claude/settings.json`.
- Drops an `RTK.md` file (instructions Claude reads) somewhere in the global config so the model is aware RTK-prefixed commands exist and are expected.
- The hook rewrites your Bash command before the shell executes it — Claude issues `git status`, the hook substitutes `rtk git status`, and Claude only ever sees the compact output.

To remove it later:

```bash
rtk init -g --uninstall     # removes hook, RTK.md, settings.json entry
```

---

## 3. How to use it day to day

**If the hook is installed, you mostly don't "use" RTK directly** — it rewrites eligible Bash commands automatically. You'll notice it via short outputs (`ok main` instead of a full `git push` transcript) and via `rtk gain` reporting cumulative savings.

**Where you do call it directly** (because Claude's built-in `Read`/`Grep`/`Glob` tools never pass through the Bash hook):

```bash
rtk read some_file.R                 # smart file reading
rtk read some_file.R -l aggressive   # signatures only, strips function bodies
rtk grep "pattern" .                 # grouped search results
rtk find "*.R" .                     # compact find results
```

These only help if the calling code path uses `Bash` to invoke `cat`/`grep`/`find` rather than Claude's native `Read`/`Grep`/`Glob` tools — in an interactive Claude Code session, the native tools are what actually get used most of the time, so this path matters more for scripted/headless invocations than for your normal interactive sessions.

**Checking what it's saving you:**

```bash
rtk gain                    # summary stats
rtk gain --graph             # ASCII graph, last 30 days
rtk discover                 # finds commands you're running that RTK *could* filter but currently doesn't
rtk session                  # RTK adoption rate across recent sessions
```

**Per-command opt-out** (`~/.config/rtk/config.toml`, or `~/Library/Application Support/rtk/config.toml` on macOS):

```toml
[hooks]
exclude_commands = ["curl", "playwright"]
```

**Failure recovery:** RTK saves the full unfiltered output to a local log file whenever a wrapped command fails, so the compact "FAILED: 2/15 tests" summary Claude sees comes with a pointer (`[full output: ~/.local/share/rtk/tee/....log]`) it can read on demand instead of forcing a full re-run.

---

## 4. Compatibility with craft and your other Claude tooling

### 4.1 No MCP namespace clash

RTK is **not** an MCP server — it's a CLI binary plus a Claude Code hook. Craft's `.mcp.json` registers only `mcp-mermaid`; savant registers no MCP servers at all. There's nothing for RTK to collide with at the MCP layer.

### 4.2 Real risk: hook ordering against `branch-guard.sh`

This is the one finding worth pausing on before you install RTK globally in a craft-managed environment.

Craft's `scripts/branch-guard.sh` is itself a `PreToolUse` hook registered on the `Bash` matcher (installed via `scripts/install-branch-guard.sh` into `~/.claude/settings.json`, same registration point RTK uses). It inspects the **raw command text** Claude submitted and blocks catastrophic operations with anchored regexes, e.g.:

```
(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+(commit|push)
(^|;|&&|\|\|)[[:space:]]*git[[:space:]]+reset[[:space:]]+--hard
rm[[:space:]]+-[rfRF]*...\.git([[:space:]]|/|$)
```

These patterns require `git` (or `rm`) to appear right after the start of the command or a shell separator (`;`, `&&`, `||`). If RTK's hook runs **first** in the `PreToolUse` chain and rewrites `git commit -m "msg"` into `rtk git commit -m "msg"` before branch-guard's hook evaluates the same event, branch-guard's anchored regex no longer matches — the `rtk` prefix sits between the anchor and `git`, so the catastrophic-command check would silently fail to fire.

**What I don't know, and you should verify before relying on this:** exactly how Claude Code sequences multiple `PreToolUse` hooks registered on the same matcher (registration order in the `settings.json` array is the most likely mechanism, but this isn't something I've confirmed against current Claude Code hook documentation), and exactly how RTK's hook performs the rewrite (whether it mutates `tool_input.command` directly via hook output, or uses a different mechanism). The README states the rewrite is transparent and silent for Claude Code specifically — that's the claim, not something I've independently verified against the hook wire format.

**Practical takeaway:** if you install RTK globally, check `~/.claude/settings.json` afterward and confirm `branch-guard.sh`'s hook entry still fires and still blocks a deliberately-triggered test case (e.g., attempt a `git push --force` on a protected branch in a throwaway repo) *after* RTK is installed. Don't assume the two coexist safely without that check, given they share a registration point and one of them rewrites the exact text the other pattern-matches against.

### 4.3 No clash with craft's other hooks

Craft's `skills/hooks` (the hooks skill, e.g. the MkDocs `--strict` `PostToolUse` template mentioned in `.STATUS`) operates on `PostToolUse`, a different event than RTK's `PreToolUse` — no overlap there.

### 4.4 Limited value for your R/statistics workflows

RTK's filter catalog (per its README) covers: git, GitHub CLI, JS/TS test runners (Jest, Vitest, Playwright), pytest, `go test`, `cargo test`, Ruby (`rake test`, RSpec), ESLint/Biome/tsc/Prettier, cargo build/clippy, `ruff`, `golangci-lint`, `rubocop`, npm/pnpm/pip/bundler/Prisma, AWS CLI, Docker/Kubernetes. **There is no R-specific filter** — no `R CMD check`, `devtools::test()`, `testthat`, `roxygen2`, or `Rscript` support listed. For MediationVerse package work (`rforge:r:check`, `rforge:r:test`, etc.), RTK would currently provide no measurable benefit unless you write a custom filter yourself (the config supports per-project custom TOML filters per its telemetry docs, though the README doesn't show a worked example).

Where it *would* apply inside your workflow: general git operations across any repo (craft, R packages, manuscripts), and craft's own dev-tooling work (npm/cargo/pytest if craft or its sibling tools ever use those runners directly).

### 4.5 Telemetry

Disabled by default, opt-in only, and explicitly excludes source code, file paths, command arguments, and repository contents — worth knowing given the codebases involved (unpublished manuscripts, CRAN-bound packages) but not a blocker since it's off unless you turn it on.

---

## 5. Caveats summary

| Caveat | Detail |
|---|---|
| **Hook-ordering risk with branch-guard.sh** | Unverified whether RTK's rewrite happens before or after branch-guard sees the command; anchored regexes in branch-guard could silently stop matching if RTK's `rtk` prefix lands between the anchor and the guarded verb |
| **Only covers `Bash` tool calls** | Claude's native `Read`/`Grep`/`Glob` bypass RTK entirely; benefit is scoped to shell-invoked commands |
| **No R/statistics tooling filters** | Nothing for `R CMD check`, testthat, devtools, roxygen2 out of the box — limited direct value for MediationVerse/rforge work without custom filters |
| **Windows native support is degraded** | Falls back to CLAUDE.md-injection mode (no auto-rewrite) outside WSL |
| **Third-party, unaudited by you** | MIT-licensed, active project (core team named in README), but you haven't independently reviewed the source — normal due diligence for any tool with shell-level hook access applies |
| **Savings figures are vendor-reported** | The 60-90%/table-of-percentages numbers come from RTK's own README, not an independent benchmark |

---

## 6. Suggested workflow (if you decide to try it)

1. **Pilot in a disposable repo first**, not craft or any active manuscript/package repo — clone something throwaway, `rtk init -g`, and deliberately test a `git push --force` against a protected-branch setup to confirm hook-ordering behavior before touching real work.
2. **Check `~/.claude/settings.json` after install** — confirm both `branch-guard.sh` and RTK's hook entries are present, note their array order, and re-test a branch-guard-triggering command in the craft repo specifically (not just the disposable repo) since that's where the guard's regexes actually protect something.
3. **If ordering checks out clean**, install globally (`rtk init -g`) and let it run passively for a few sessions — check `rtk gain` and `rtk discover` after a week of normal craft/general dev work to see actual (not vendor-claimed) savings on your real usage pattern.
4. **Leave R-package/manuscript sessions alone for now** — no filter coverage there, so no expected benefit, and no reason to add hook-chain complexity to those repos until/unless you write a custom filter.
5. **Re-evaluate against the token-probe script** (if built — see the consolidated craft SPEC, `docs/specs/SPEC-token-efficiency-and-context-tooling-2026-07-01.md`) once that tooling exists, for an apples-to-apples measured comparison rather than RTK's self-reported percentages.

## 7. Sample workflows

**A. Normal craft dev session (git-heavy):**

```bash
git status          # rewritten to `rtk git status` — compact output
git diff             # rewritten, condensed diff
git add . && git commit -m "fix: ..." && git push   # each leg rewritten + shortened
```

Expected effect: shorter tool-result blocks in context for routine git chatter, per RTK's own table (~80-92% reduction on these specific operations, vendor-reported).

**B. Debugging a failing test suite (JS/Python/Go/Rust project only — not R):**

```bash
pytest               # rewritten to `rtk pytest` — failures only, ~90% reduction claimed
cargo test           # same pattern for Rust
```

On a failure, RTK keeps the full raw log on disk and gives Claude a path to it — so a failure investigation isn't blocked by the compact summary, it just starts compact and expands on demand.

**C. R package work (MediationVerse) — no direct RTK involvement:**
Continue using `rforge:r:test`, `rforge:r:check`, etc. as-is. RTK's Bash-level rewriting won't engage unless the underlying `rforge` commands shell out to something RTK recognizes (git operations inside those flows would still get filtered; the R-specific parts would not).

**D. Manuscript/research sessions:**
Minimal RTK involvement expected — these sessions are dominated by `Read`/file-editing rather than Bash-heavy dev-tool invocation, and RTK doesn't touch the native `Read` tool.
