---
description: Claude Code marketplace distribution - init, validate, test, and publish
arguments:
  - name: subcommand
    description: "Subcommand: init|validate|test|publish"
    required: false
    default: validate
---

# /craft:dist:marketplace - Marketplace Distribution

Claude Code marketplace distribution management. Generate, validate, test, and publish marketplace listings.

## Subcommands

| Command | Purpose |
|---------|---------|
| `init` | Generate marketplace.json from plugin.json |
| `validate` | Validate marketplace config and plugin (default) |
| `test` | Local install/uninstall cycle |
| `publish` | Push to GitHub for marketplace availability |

## Quick Start

```bash
# Validate marketplace config (default)
/craft:dist:marketplace

# Initialize marketplace.json for first time
/craft:dist:marketplace init

# Test local install cycle
/craft:dist:marketplace test

# Publish to marketplace
/craft:dist:marketplace publish
```

---

## /craft:dist:marketplace init

Generate `.claude-plugin/marketplace.json` from existing `plugin.json`.

### Execution Steps

1. **Read plugin.json** - Load `.claude-plugin/plugin.json` for name, version, description, author
2. **Detect repository** - Run `git remote get-url origin` to extract owner and repo
3. **Prompt for marketplace name** - Suggest `{org}-{plugin}` format (e.g., `data-wise-craft`)
4. **Generate marketplace.json** - Write `.claude-plugin/marketplace.json` with the following structure:

```json
{
  "name": "{org}-{plugin}",
  "owner": {
    "name": "{author.name from plugin.json}",
    "email": "{author.email from plugin.json}"
  },
  "metadata": {
    "description": "{description from plugin.json, truncated to 1 line}",
    "version": "{version from plugin.json}"
  },
  "plugins": [
    {
      "name": "{name from plugin.json}",
      "source": { "source": "github", "repo": "{owner}/{repo}" },
      "description": "{description, single line}",
      "version": "{version}",
      "author": { "name": "...", "email": "..." },
      "homepage": "{docs site or repo URL}",
      "repository": "{git remote origin URL}",
      "license": "{from LICENSE file or plugin.json}",
      "category": "development",
      "keywords": []
    }
  ]
}
```

5. **Validate** - Run `claude plugin validate .` to verify the generated file
6. **Display install command** - Show how users will install

### Validation Checks

- `.claude-plugin/plugin.json` must exist
- If `.claude-plugin/marketplace.json` already exists, warn and confirm overwrite
- Git remote must be configured (needed for repository field)
- Author must have name and email in plugin.json

### Example Output

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace init                                │
├─────────────────────────────────────────────────────────────┤
│ Plugin: craft v2.18.0                                       │
│ Author: Data-Wise <dt@stat-wise.com>                        │
│ Marketplace: data-wise-craft                                │
│ Source: ./                                                   │
├─────────────────────────────────────────────────────────────┤
│ Created: .claude-plugin/marketplace.json                    │
│ Validated: claude plugin validate . ... PASSED              │
├─────────────────────────────────────────────────────────────┤
│ Install with:                                                │
│   /plugin marketplace add Data-Wise/craft                   │
│   /plugin install craft@data-wise-craft                     │
└─────────────────────────────────────────────────────────────┘
```

---

## /craft:dist:marketplace validate

Validate marketplace configuration and plugin structure.

### Execution Steps

1. **Check marketplace.json exists** - Verify `.claude-plugin/marketplace.json` is present

   ```
   ERROR: .claude-plugin/marketplace.json not found
   Run /craft:dist:marketplace init to create it
   ```

2. **Run plugin validation** - Execute `claude plugin validate .` and capture output
3. **Parse results** - Separate errors (blockers) from warnings (non-blocking)
4. **Check version consistency** - Compare versions across files:
   - `marketplace.json` `metadata.version` == `plugin.json` `version`
   - `marketplace.json` `plugins[0].version` == `plugin.json` `version` (if present)
5. **Report results** - Display in box-drawing format

### Validation Checks

| Check | Severity | Description |
|-------|----------|-------------|
| marketplace.json exists | Error | File must be present |
| `claude plugin validate .` | Error/Warning | Plugin structure validation |
| Version consistency | Error | marketplace.json version must match plugin.json |
| Owner fields present | Warning | name and email should be populated |
| Repository URL valid | Warning | Should match git remote |
| Description length | Warning | Should be concise (< 200 chars) |

### Example Output (Pass)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace validate                            │
├─────────────────────────────────────────────────────────────┤
│ marketplace.json .......................... FOUND            │
│ claude plugin validate . .................. PASSED           │
│ Version consistency ....................... OK (v2.18.0)     │
│ Owner fields .............................. OK               │
│ Repository URL ............................ OK               │
├─────────────────────────────────────────────────────────────┤
│ Result: ALL CHECKS PASSED                                   │
└─────────────────────────────────────────────────────────────┘
```

### Example Output (Fail)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace validate                            │
├─────────────────────────────────────────────────────────────┤
│ marketplace.json .......................... FOUND            │
│ claude plugin validate . .................. 2 ERRORS         │
│   - Missing required field: plugins[0].source               │
│   - Invalid schema reference                                │
│ Version consistency ....................... MISMATCH         │
│   marketplace.json: 2.17.0                                  │
│   plugin.json:      2.18.0                                  │
├─────────────────────────────────────────────────────────────┤
│ Result: 3 ERRORS, 0 WARNINGS                               │
│ Fix errors before publishing.                               │
└─────────────────────────────────────────────────────────────┘
```

---

## /craft:dist:marketplace test

Run a local install/uninstall cycle to verify the plugin works via marketplace.

### Execution Steps

1. **Run validate** - Execute the validate subcommand first (fail fast on errors)

   ```
   Running /craft:dist:marketplace validate ...
   ```

   If validate fails, stop and report errors. Do not proceed to install.

2. **Install locally** - Run `/plugin marketplace add ./` using the local path

   ```bash
   claude plugin marketplace add ./
   ```

3. **Verify installation** - Check plugin appears in the installed list

   ```bash
   claude plugin list
   ```

   Confirm the plugin name appears in output.

4. **Verify command discovery** - Check that key commands are accessible

   Check that representative command files exist in the plugin cache. For craft, verify
   at least 3 commands are discoverable (e.g., `do`, `check`, `code/lint`).

5. **Uninstall** - Remove the test installation

   ```bash
   claude plugin uninstall {name}@{marketplace-name}
   ```

6. **Verify cleanup** - Confirm plugin no longer appears in installed list
7. **Report results** - Display pass/fail for each step

### Example Output (Pass)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace test                                │
├─────────────────────────────────────────────────────────────┤
│ Step 1: Validate ......................... PASSED            │
│ Step 2: Install (local) .................. PASSED            │
│ Step 3: Plugin visible ................... PASSED            │
│ Step 4: Commands discoverable ............ PASSED (108 cmds) │
│ Step 5: Uninstall ........................ PASSED            │
│ Step 6: Cleanup verified ................. PASSED            │
├─────────────────────────────────────────────────────────────┤
│ Result: ALL 6 STEPS PASSED                                  │
│ Plugin is ready for marketplace distribution.               │
└─────────────────────────────────────────────────────────────┘
```

### Example Output (Fail)

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace test                                │
├─────────────────────────────────────────────────────────────┤
│ Step 1: Validate ......................... PASSED            │
│ Step 2: Install (local) .................. PASSED            │
│ Step 3: Plugin visible ................... PASSED            │
│ Step 4: Commands discoverable ............ FAILED            │
│   Expected 107 commands, found 0                            │
│   Check plugin.json and command file paths                  │
├─────────────────────────────────────────────────────────────┤
│ Step 5: Uninstall ........................ PASSED            │
│ Step 6: Cleanup verified ................. PASSED            │
├─────────────────────────────────────────────────────────────┤
│ Result: 1 FAILURE (Step 4)                                  │
│ Fix issues before publishing.                               │
└─────────────────────────────────────────────────────────────┘
```

### Notes

- The test always attempts cleanup (Steps 5-6) even if earlier steps fail
- Local install uses `./` path, not the remote GitHub URL
- If `claude` CLI is not available, report and skip Steps 2-6

---

## /craft:dist:marketplace publish

Push to GitHub to make the plugin available via marketplace.

### Execution Steps

1. **Run validate** - Execute the validate subcommand first (fail fast)

   ```
   Running /craft:dist:marketplace validate ...
   ```

   If validate fails, stop and report errors.

2. **Check git working tree** - Verify no uncommitted changes

   ```bash
   git status --porcelain
   ```

   If dirty, display changed files and ask user to commit or stash first.

   ```
   ERROR: Working tree is not clean
   Uncommitted changes:
     M .claude-plugin/marketplace.json
     M commands/dist/marketplace.md
   Commit changes before publishing.
   ```

3. **Check branch** - Verify current branch is `dev` or `main`

   ```bash
   git branch --show-current
   ```

   If on a feature branch, warn:

   ```
   WARNING: Currently on feature/marketplace-distribution
   Marketplace installs use the default branch (main).
   Consider merging to dev/main first.
   ```

4. **Show install preview** - Display what users will run after publish

   ```
   After publishing, users install with:
     /plugin marketplace add {owner}/{repo}
     /plugin install {name}@{marketplace-name}
   ```

5. **Confirm with user** - Ask for explicit confirmation before pushing

   ```
   Push to origin/{branch}? (y/n)
   ```

6. **Push** - Execute git push

   ```bash
   git push
   ```

7. **Display success** - Show final install instructions

### Example Output

```
┌─────────────────────────────────────────────────────────────┐
│ /craft:dist:marketplace publish                             │
├─────────────────────────────────────────────────────────────┤
│ Validate ............................... PASSED              │
│ Working tree ........................... CLEAN               │
│ Branch ................................. main                 │
├─────────────────────────────────────────────────────────────┤
│ Ready to publish craft v2.18.0                              │
│                                                              │
│ After push, users install with:                             │
│   /plugin marketplace add Data-Wise/craft                   │
│   /plugin install craft@data-wise-craft                     │
├─────────────────────────────────────────────────────────────┤
│ Push to origin/main? (y/n)                                  │
└─────────────────────────────────────────────────────────────┘
```

After confirmation:

```
┌─────────────────────────────────────────────────────────────┐
│ Published!                                                   │
├─────────────────────────────────────────────────────────────┤
│ Users can now install with:                                 │
│   /plugin marketplace add Data-Wise/craft                   │
│   /plugin install craft@data-wise-craft                     │
└─────────────────────────────────────────────────────────────┘
```

---

## Integration

| Command | Relationship |
|---------|-------------|
| `/craft:dist:homebrew` | Homebrew distribution (complementary channel) |
| `/craft:check --for release` | Pre-release validation includes marketplace checks |
| `/release` | Release pipeline auto-bumps marketplace.json version |

### Release Pipeline Integration

The `/release` skill handles marketplace automatically:

- **Step 2 (Pre-Flight):** Runs `claude plugin validate .` if marketplace.json exists
- **Step 3 (Version Bump):** Updates `metadata.version` and `plugins[0].version` in marketplace.json
- **Step 10 (Tap Update):** Updates Homebrew tap formula with new version and SHA256

### Recommended Distribution Strategy

| Audience | Channel | Command |
|----------|---------|---------|
| New users (all platforms) | Marketplace | `/plugin marketplace add {owner}/{repo}` |
| Power users (macOS) | Homebrew | `brew install {tap}/{formula}` |
| Contributors | Manual clone | `git clone ... && ln -sf ...` |

---

## Dependencies

- `claude` CLI - Required for `claude plugin validate .` and plugin management
- `git` - Required for publish subcommand and repository detection
- `jq` - Optional, used for JSON parsing when available

## See Also

- `/craft:dist:homebrew` - Homebrew formula automation
- `/craft:check` - Pre-flight validation
- `/release` - End-to-end release pipeline
