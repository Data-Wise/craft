# OpenCode Plugins: Tutorial & Cheat Sheet

Three plugins configured for your OpenCode setup:

| Plugin | Type | npm Package | Source |
|--------|------|-------------|--------|
| **opencode-shell-strategy** | Instructions file | N/A (local clone) | [GitHub](https://github.com/JRedeker/opencode-shell-strategy) |
| **opencode-pty** | npm plugin | `opencode-pty@0.3.6` | [GitHub](https://github.com/shekohex/opencode-pty) |
| **@zenobius/opencode-skillful** | npm plugin | `@zenobius/opencode-skillful@1.2.5` | [GitHub](https://github.com/zenobi-us/opencode-skillful) (archived) |

---

## 1. opencode-shell-strategy

### What it does

Injects a rules file into every OpenCode session that teaches the LLM to always use non-interactive shell flags. It prevents the single most common failure mode in headless agents: commands that hang waiting for user input.

### How it works

Loaded as an **instructions** entry (not a plugin). At session start, OpenCode reads `shell_strategy.md` and feeds it to the LLM as system context. The LLM then internalizes rules like "always use `npm init -y` instead of `npm init`", "never launch `vim` or `less`", and "pipe `yes |` when no flag exists".

### What you'll notice

- Fewer timeout errors from the Bash tool
- The agent auto-adds `--no-edit`, `-y`, `--non-interactive` flags without being told
- No more `git log` hanging the session (it uses `--no-pager` or `git log -n 10`)

### You don't do anything — it's automatic

This plugin has no tools, no commands, no configuration. It works silently in the background. You just stop seeing hangs.

### Cheat sheet: problematic commands and their safe equivalents

#### Package managers

| Tool | Hangs (avoid) | Safe (use instead) |
|------|--------------|-------------------|
| npm | `npm init` | `npm init -y` |
| npm | `npm install` | `npm install --yes` |
| pip | `pip install pkg` | `pip install --no-input pkg` |
| apt | `apt-get install pkg` | `apt-get install -y pkg` |
| brew | `brew install pkg` | `HOMEBREW_NO_AUTO_UPDATE=1 brew install pkg` |

#### Git

| Action | Hangs (avoid) | Safe (use instead) |
|--------|--------------|-------------------|
| Commit | `git commit` | `git commit -m "msg"` |
| Merge | `git merge branch` | `git merge --no-edit branch` |
| Add | `git add -p` | `git add .` |
| Log | `git log` (pager) | `git log --no-pager -n 20` |

#### System

| Tool | Hangs (avoid) | Safe (use instead) |
|------|--------------|-------------------|
| rm | `rm file` (prompts on some systems) | `rm -f file` |
| unzip | `unzip file.zip` | `unzip -o file.zip` |
| ssh | `ssh host` | `ssh -o BatchMode=yes host` |
| curl | `curl url` | `curl -fsSL url` |

#### Always-banned commands (will hang indefinitely)

`vim` `nano` `less` `more` `man` `git add -p` `git rebase -i` `python` (REPL) `node` (REPL)

#### When no flag exists: pipe `yes`

```bash
yes | ./install_script.sh
```

Or use a timeout as last resort:

```bash
timeout 30 ./potentially_hanging_script.sh
```

---

## 2. opencode-pty

### What it does

Gives the AI agent five new tools for managing background PTY sessions — real terminal processes that persist and can be interacted with. This is the counterpart to shell-strategy: where shell-strategy *avoids* interactivity, opencode-pty *enables* it safely.

### Tools provided

| Tool | Purpose | Key params |
|------|---------|------------|
| `pty_spawn` | Start a background process | `command`, `args`, `workdir`, `title`, `notifyOnExit`, `timeoutSeconds` |
| `pty_write` | Send input to a running session | `id`, `data` (text or escape sequences) |
| `pty_read` | Read output with pagination | `id`, `offset`, `limit`, `pattern` (regex filter) |
| `pty_list` | Show all sessions | (none) |
| `pty_kill` | Terminate a session | `id`, `cleanup` (bool) |

### Slash commands

| Command | Description |
|---------|-------------|
| `/pty-open-background-spy` | Open the web UI (React dashboard with live output) |
| `/pty-show-server-url` | Show the web server URL |

### Tutorial: common workflows

#### Start a dev server in the background

Ask the agent:

> "Start the vite dev server as a background session"

The agent calls `pty_spawn` with `command="npm"`, `args=["run", "dev"]`, `title="Dev Server"` and returns a session ID like `pty_a1b2c3d4`.

#### Read the output later

> "Show me the last 50 lines from the dev server"

The agent calls `pty_read` with `id="pty_a1b2c3d4"`, `limit=50`.

#### Filter for errors

> "Show me any errors from the build session"

The agent calls `pty_read` with `pattern="error|ERROR"`, `ignoreCase=true` to filter lines.

#### Send interactive input

> "Type 'rs' and Enter into the vite session to restart it"

The agent calls `pty_write` with `data="rs\n"`.

#### Send Ctrl+C to stop

> "Stop the dev server"

The agent calls `pty_write` with `data="\x03"` (Ctrl+C escape sequence).

#### Long-running build with exit notification

> "Run the build in the background and tell me when it finishes"

The agent calls `pty_spawn` with `notifyOnExit=true`. When the build exits, you get a `<pty_exited>` message with exit code and last line of output. No polling needed.

### Cheat sheet: escape sequences

| Key | Sequence | Use case |
|-----|----------|----------|
| Ctrl+C | `\x03` | Interrupt/kill process |
| Ctrl+D | `\x04` | Send EOF |
| Ctrl+Z | `\x1a` | Suspend process |
| Enter | `\n` or `\r` | Submit input |
| Tab | `\t` | Autocomplete |
| Arrow Up | `\x1b[A` | Command history |
| Arrow Down | `\x1b[B` | Command history |

### Cheat sheet: session lifecycle

```
pty_spawn → running → [exited | killed]
                          ↓
              stays in list until cleanup=true
```

- Sessions persist after exit so you can read final output
- Use `pty_kill` with `cleanup=true` to fully remove
- Buffer holds up to 50,000 lines per session (configurable via `PTY_MAX_BUFFER_LINES`)

### Web UI

Run `/pty-open-background-spy` to open a browser dashboard with:

- Live session list with status indicators
- Real-time output streaming via WebSocket
- Interactive input field per session
- Kill button per session

### Permission note

PTY commands are checked against your `permission.bash` config. `"ask"` permissions are treated as `"deny"` (plugins can't show a prompt UI), so use explicit `"allow"` for commands you want to run via PTY.

---

## 3. @zenobius/opencode-skillful

### What it does

Provides lazy-loading skill discovery. Instead of dumping all skills into context at session start (consuming tokens), skills are indexed in the background and injected only when you explicitly request them.

### Tools provided

| Tool | Purpose | Example |
|------|---------|---------|
| `skill_find` | Search skills by keyword | `skill_find "git commit"` |
| `skill_use` | Load a skill into context | `skill_use "experts_writing_git_commits"` |
| `skill_resource` | Read a specific file from a skill | `skill_resource skill_name="..." relative_path="references/guide.md"` |

### How it differs from OpenCode's built-in skills

| Aspect | Built-in | opencode-skillful |
|--------|----------|-------------------|
| Loading | All skills pre-loaded | On-demand only |
| Token cost | All skills consume tokens every session | Only loaded skills cost tokens |
| Discovery | Limited | Natural-language query with negation |
| Resource access | Direct filesystem | Pre-indexed (security: no path traversal) |

### Tutorial: common workflows

#### Find skills by keyword

Ask the agent:

> "Find skills related to testing"

The agent calls `skill_find` with `query="testing"` and returns matching skills with names and descriptions.

#### Find with exclusions

> "Find testing skills but exclude performance ones"

The agent calls `skill_find` with `query="testing -performance"`.

#### List all skills

> "What skills are available?"

The agent calls `skill_find` with `query="*"`.

#### Load a skill into context

> "Load the git commits skill"

The agent calls `skill_use` with the skill's fully-qualified identifier (e.g., `experts_writing_git_commits`). The skill content is silently injected into the conversation. You won't see it, but the AI now has access to its instructions.

#### Read a specific reference document

> "Show me the commit style guide from the git skill"

The agent calls `skill_resource` with `skill_name="..."` and `relative_path="references/style-guide.md"`.

### Cheat sheet: query syntax

| Syntax | Meaning | Example |
|--------|---------|---------|
| `*` or empty | List all skills | `skill_find "*"` |
| `word1 word2` | AND logic (both must match) | `skill_find "git commit"` |
| `-term` | Exclude results | `skill_find "testing -performance"` |
| `"exact phrase"` | Phrase match | `skill_find "git commit"` |
| `path/prefix` | Path prefix matching | `skill_find "experts/writing"` |

### Skill identifier convention

Directory paths become identifiers by replacing separators and hyphens with underscores:

```
skills/
  experts/
    writing/
      git-commits/          → experts_writing_git_commits
  superpowers/
    code-review/            → superpowers_code_review
```

### Configuration (optional)

Create `.opencode-skillful.json` in your project root:

```json
{
  "debug": false,
  "basePaths": ["~/.config/opencode/skills", ".opencode/skills"],
  "promptRenderer": "xml",
  "modelRenderers": {
    "claude-3-5-sonnet": "xml",
    "gpt-4": "json"
  }
}
```

| Field | Default | Description |
|-------|---------|-------------|
| `debug` | `false` | Show skill discovery stats in results |
| `basePaths` | `["~/.config/opencode/skills", ".opencode/skills"]` | Where to scan for SKILL.md files |
| `promptRenderer` | `"xml"` | Default format: `xml`, `json`, or `md` |
| `modelRenderers` | `{}` | Per-model format overrides |

---

## Quick reference: all three at a glance

| Plugin | Install type | What you do | What the agent gets |
|--------|-------------|-------------|---------------------|
| shell-strategy | Instructions file | Nothing — automatic | LLM knows to use non-interactive flags |
| opencode-pty | npm plugin | Ask for background sessions | 5 tools: spawn, write, read, list, kill |
| opencode-skillful | npm plugin | Ask to find/load skills | 3 tools: find, use, resource |

## Installation summary

Your `~/.config/opencode/config.json` has:

```json
{
  "plugin": ["opencode-pty", "@zenobius/opencode-skillful"],
  "instructions": [
    "CLAUDE.md",
    ".claude/rules/*.md",
    "~/.config/opencode/plugin/shell-strategy/shell_strategy.md"
  ]
}
```

- `opencode-pty` and `@zenobius/opencode-skillful` install automatically via Bun on startup (cached in `~/.cache/opencode/packages/`).
- `shell-strategy` was cloned to `~/.config/opencode/plugin/shell-strategy/` and loaded as an instructions file.
