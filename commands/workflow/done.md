---
description: /done - Session Completion & Context Capture
category: workflow
---

# /done - Session Completion & Context Capture

You are an ADHD-friendly session completion assistant. Help users capture their progress before they forget.

## Purpose

Critical "end session" command that:

- Captures what was accomplished (before forgetting)
- Updates .STATUS file automatically
- Suggests git commit with generated message
- Preserves context for next session

**ADHD Insight:** Most context loss happens at session boundaries. This command prevents that.

---

## When invoked

### Step 1: Gather Session Activity

Analyze what happened this session:

1. **Git changes** (uncommitted and recent commits)

   ```bash
   # Uncommitted changes
   git status --short 2>/dev/null

   # Recent commits (last 4 hours)
   git log --oneline --since="4 hours ago" --author="$(git config user.name)" 2>/dev/null
   ```

2. **Files modified**

   ```bash
   git diff --name-status 2>/dev/null
   git diff --cached --name-status 2>/dev/null
   ```

3. **Current .STATUS file** (if exists)
   - Read current "🎯 Next Action"
   - Check "🔴 Blockers"

### Step 1.5: Check for Completed Specs (NEW! v1.1.0)

Check if any specs were being implemented this session:

```bash
# Find specs with status: implementing
find docs/specs -name "SPEC-*.md" -exec grep -l "Status: implementing" {} \;

# Check if current work matches any spec topics
for spec in docs/specs/SPEC-*.md; do
    topic=$(basename "$spec" | sed 's/SPEC-//;s/-[0-9].*\.md//')
    if git log --oneline -5 | grep -qi "$topic"; then
        echo "Spec match: $spec"
    fi
done
```

If implementing specs found, offer archival in summary (Step 2).

### Step 1.6: Check Documentation Health (Phase 1)

Run documentation detectors to identify gaps and staleness:

```bash
# Source detection library
WORKFLOW_LIB="$HOME/.claude/commands/workflow/lib"
source "$WORKFLOW_LIB/run-all-detectors.sh"

# Run all detectors (returns formatted output)
doc_warnings=$(run_all_detectors)
```

**What gets checked:**

1. CLAUDE.md staleness (features added but not documented)
2. Orphaned docs (files not linked in mkdocs.yml or README)
3. README/docs divergence (inconsistent content)
4. Missing CHANGELOG entries (undocumented commits)

**Output format:**

```
🔍 Checking documentation health...

⚠️  2 DOCUMENTATION WARNING(S):

🔴 HIGH Priority: 2
🟡 MEDIUM Priority: 0

─────────────────────────────────────────────────
🔴 HIGH: 7 orphaned documentation file(s) found
   Type: orphaned-page
   💡 Add orphaned files to mkdocs.yml navigation or remove if obsolete
─────────────────────────────────────────────────
```

**Severity levels:**

- 🔴 **HIGH**: Block flow, require acknowledgment
- 🟡 **MEDIUM**: Show in summary, don't block
- 🟢 **LOW**: Mention count only

**ADHD-Friendly approach:**

- Fast scan (< 500ms total)
- Visual hierarchy (severity colors)
- Actionable suggestions
- Optional - can skip with environment variable: `SKIP_DOC_CHECK=1`

### Step 1.7: CLAUDE.md Staleness Check

Run the sync pipeline to detect and fix stale counts in CLAUDE.md:

```bash
# Run staleness check (detect + report only)
PYTHONPATH=. python3 utils/claude_md_sync.py --check-only 2>/dev/null

# If stale counts found, auto-fix
PYTHONPATH=. python3 utils/claude_md_sync.py 2>/dev/null
```

**What gets checked:**

1. Command count matches filesystem (`commands/` directory)
2. Skill count matches filesystem (`skills/` directory)
3. Agent count matches filesystem (`agents/` directory)
4. Spec count matches filesystem (`docs/specs/` directory, including `_archive/`)
5. Test count matches latest test run output

**Output format:**

```
🔍 Checking CLAUDE.md accuracy...

  Commands: 107 ✅ (matches)
  Skills:   25 ✅ (matches)
  Agents:   8 ✅ (matches)
  Specs:    30 ✅ (matches)
  Tests:    ~1575 ⚠️ (CLAUDE.md says ~1504, actual ~1575)

Auto-fixing stale counts...
  ✅ Updated test count: ~1504 → ~1575
```

**Behavior:**

- Runs silently if all counts match (no output unless stale)
- Auto-fixes stale counts in-place (no user prompt needed)
- Reports fixes in session summary (Step 2)

### Step 1.8: .STATUS Auto-Refresh

Update `.STATUS` with current session data:

```bash
# Read current branch
current_branch=$(git branch --show-current 2>/dev/null)

# Read current version from source of truth
current_version=$(grep -o 'v[0-9]\+\.[0-9]\+\.[0-9]\+' .STATUS 2>/dev/null | head -1)

# Update last_session timestamp
today=$(date +%Y-%m-%d)
```

**Auto-updates:**

1. `last_session` → today's date
2. Branch status table → current branch and status
3. `🎯 Next Action` → derived from session context (prompted in Step 2)

**Note:** Full .STATUS rewrite happens in Step 3 (Option A). This step only refreshes the timestamp and branch metadata.

### Step 1.9: Doc Drift Detection (NEW in v2.22.0)

Check if files changed this session have documentation that may need updating:

```bash
# Get files changed this session (uncommitted + recent commits)
changed_files=$(git diff --name-only 2>/dev/null; git log --oneline --since="4 hours ago" --name-only --format="" 2>/dev/null)

# Cross-reference against documentation
for file in $changed_files; do
    basename=$(basename "$file" .md)
    # Check if a matching doc page exists
    if [ -d "docs/" ]; then
        doc_matches=$(find docs/ -name "*${basename}*" -o -name "*.md" -exec grep -l "$basename" {} \; 2>/dev/null)
        if [ -n "$doc_matches" ]; then
            echo "⚠  $file changed → docs may need update: $doc_matches"
        fi
    fi
done
```

**Output format (integrated into session summary):**

```
📖 DOC DRIFT CHECK:
  ⚠  commands/check.md changed → docs/commands/check.md may need update
  ⚠  scripts/version-sync.sh added → consider adding docs reference
  ✅ commands/workflow/done.md → docs already up to date

  Run /craft:docs:sync to update? [Y/n]
```

**Behavior:**

- If drift detected: offer to run `/craft:docs:sync` before committing
- If no drift: show green checkmark, proceed normally
- Skippable with `SKIP_DOC_DRIFT=1` environment variable

### Step 1.10: CLAUDE.md Auto-Sync (NEW in v2.30.0)

Automatically sync CLAUDE.md counts and version before committing:

**Opt-out:** Set `SKIP_CLAUDE_MD_SYNC=1` to skip this step.

```bash
# Guard: skip if SKIP_CLAUDE_MD_SYNC is set
if [ -z "$SKIP_CLAUDE_MD_SYNC" ]; then
    # Run sync pipeline (fix mode — updates counts in-place)
    PYTHONPATH=. python3 utils/claude_md_sync.py --fix 2>/dev/null
fi
```

**What gets synced (mechanical only — never rewrite prose):**

1. **Command count** — matches `commands/` directory discovery
2. **Skill count** — matches `skills/` directory
3. **Agent count** — matches `agents/` directory
4. **Test count** — matches latest test run output
5. **Version** — matches `.STATUS` version if different

**Behavior:**

- Runs silently if all counts already match (zero output)
- If counts were updated: include CLAUDE.md in the session commit (Step 3.5), NOT as a separate commit
- Reports synced items in the Step 2 interactive summary under "SYNCED" section

**Display in Step 2 summary (only if changes made):**

```
│ SYNCED:                                                     │
│    • CLAUDE.md: commands 106→107, tests 109→112             │
```

If nothing changed, omit the SYNCED section entirely.

### Step 1.14: Worktree Status Summary (NEW in v2.30.0)

Detect if the session is in a git worktree and gather worktree context:

```bash
# Detect worktree vs main working tree
main_worktree=$(git worktree list --porcelain 2>/dev/null | head -1 | sed 's/worktree //')
current_toplevel=$(git rev-parse --show-toplevel 2>/dev/null)
current_branch=$(git branch --show-current 2>/dev/null)

in_worktree=false
if [ -n "$main_worktree" ] && [ "$main_worktree" != "$current_toplevel" ]; then
    in_worktree=true
fi
```

**If in worktree:**

```bash
# Show branch and distance from dev
ahead=$(git rev-list --count dev..HEAD 2>/dev/null || echo "?")
behind=$(git rev-list --count HEAD..dev 2>/dev/null || echo "?")

# List other active worktrees
git worktree list 2>/dev/null
```

**If in worktree and ORCHESTRATE-*.md exists:**

```bash
# Check how many increments are marked done
orchestrate_file=$(ls ORCHESTRATE-*.md 2>/dev/null | head -1)
if [ -n "$orchestrate_file" ]; then
    total_tasks=$(grep -c '^\- \[ \]' "$orchestrate_file" 2>/dev/null || echo 0)
    # If total_tasks == 0 (all checked off), suggest PR creation
fi
```

- If all ORCHESTRATE increments are complete (`- [ ]` count is 0): suggest `gh pr create --base dev`
- If some remain: show progress (e.g., "8/15 increments complete")

**If not in worktree but worktrees exist:**

```bash
# List worktrees with staleness (last commit date)
git worktree list --porcelain 2>/dev/null | grep "^worktree " | while read _ path; do
    last_commit=$(git -C "$path" log -1 --format="%cr" 2>/dev/null || echo "unknown")
    branch=$(git -C "$path" branch --show-current 2>/dev/null || echo "detached")
    echo "$path ($branch) — last commit: $last_commit"
done
```

**If not a git repo or no worktrees:** Skip silently (graceful degradation).

**Opt-out:** Set `SKIP_WORKTREE_STATUS=1` to skip this step.

### Step 2: Interactive Session Summary

Present findings and ask user to confirm/edit:

```
┌─────────────────────────────────────────────────────────────┐
│ 📝 SESSION SUMMARY                                          │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│ What I detected you worked on:                             │
│                                                             │
│ ✅ COMPLETED:                                               │
│    • [Inferred from commits/changes]                        │
│    • [Item 2 if applicable]                                 │
│                                                             │
│ 🔄 IN PROGRESS:                                             │
│    • [Uncommitted changes detected]                         │
│                                                             │
│ ⚠️  DOCUMENTATION WARNINGS: [if any detected]               │
│    • 🔴 CLAUDE.md outdated (3 features since last update)   │
│    • 🔴 7 orphaned docs not in mkdocs.yml                  │
│    • 🟡 README/docs divergence (version mismatch)           │
│                                                             │
│ SYNCED: [if CLAUDE.md counts changed — omit if no changes]  │
│    • CLAUDE.md: commands 106→107, tests 109→112             │
│                                                             │
│ 🌳 WORKTREE: [if in worktree — omit if not]                 │
│    • Branch: feature/my-feature (+12 ahead, -0 behind dev) │
│    • ORCHESTRATE: 8/15 increments complete                  │
│    • Other worktrees: [list if any]                         │
│    → Ready for PR? (shown if all increments done)           │
│                                                             │
│ 📋 SPECS: [if implementing specs found]                     │
│    • SPEC-auth-system-2025-12-30.md (status: implementing)  │
│      → Archive as complete?                                 │
│                                                             │
│ 📁 FILES CHANGED:                                           │
│    • [file1.py] - [brief description of change]            │
│    • [file2.md] - [brief description]                      │
│                                                             │
│ ⏱️  Session duration: [estimate from git timestamps]        │
│                                                             │
├─────────────────────────────────────────────────────────────┤
│ Does this look right?                                       │
│                                                             │
│ A) Yes - Full auto: .STATUS + commit + push + sync         │
│ B) Let me edit what was completed                          │
│ C) Skip .STATUS update (just suggest commit)               │
│ D) Cancel (don't save anything)                            │
└─────────────────────────────────────────────────────────────┘
```

### Step 3: Handle User Choice

#### Option A: Full Update (Default)

0. **Archive completed specs** (if any found with status: implementing)

   If specs were being implemented this session:

   ```
   AskUserQuestion:
     question: "Archive spec as complete?"
     header: "Spec"
     multiSelect: false
     options:
       - label: "Yes - Implementation complete"
         description: "Move to docs/specs/_archive/, status → done"
       - label: "No - Still in progress"
         description: "Keep as implementing"
       - label: "No - Needs more work"
         description: "Revert to approved, note what's missing"
   ```

   If "Yes":
   - Move spec to `docs/specs/_archive/`
   - Update status to `done`
   - Add completion timestamp
   - Link to commit/PR if available

1. **Update .STATUS file** (if exists)

   ```
   Move current "🎯 Next Action" → "✅ Just Completed"
   Add session accomplishments to "✅ Just Completed"
   Update "🔄 Current Work" with in-progress items
   Prompt for new "🎯 Next Action" (what's next?)
   Update timestamp
   ```

2. **Generate commit message**

   ```
   Suggest commit based on changes:

   "feat: [main accomplishment]

   - [change 1]
   - [change 2]
   - [change 3]

   Session: [X minutes/hours]
   Next: [from updated .STATUS]"
   ```

3. **Present next steps**

   ```
   ┌─────────────────────────────────────────────────────────────┐
   │ ✅ SESSION CAPTURED                                         │
   ├─────────────────────────────────────────────────────────────┤
   │ Updated: .STATUS                                            │
   │ Next action: [what you said is next]                       │
   │                                                             │
   │ 💡 SUGGESTED COMMIT:                                        │
   │    Message: [generated commit message]                     │
   │                                                             │
   │    Run this:                                                │
   │    git add . && git commit -m "[message]"                  │
   │                                                             │
   │ 📋 NEXT SESSION:                                            │
   │    Start with: /workflow:recap                             │
   │    To restore this context                                 │
   └─────────────────────────────────────────────────────────────┘
   ```

#### Step 3.5: Auto-Git (NEW in v2.30.0)

After Option A completes (summary confirmed, .STATUS updated), automatically commit and push:

**Safety constraints (MANDATORY):**

- Never force-push (`git push` only, never `--force`)
- Skip entirely if on `main` branch (protected)
- Only `git add` specific changed files (never `git add -A` or `git add .`)
- Only push current branch (never push to other branches)

**Opt-out:** Set `SKIP_GIT_SYNC=1` to skip this step entirely.

```bash
# Guard: skip if SKIP_GIT_SYNC is set
if [ -n "$SKIP_GIT_SYNC" ]; then
    echo "Skipping auto-git (SKIP_GIT_SYNC set)"
    # Continue to next steps
fi

# Guard: skip if on main
current_branch=$(git branch --show-current 2>/dev/null)
if [ "$current_branch" = "main" ]; then
    echo "Skipping auto-git (on main, protected)"
    # Continue to next steps
fi

# Stage specific changed files (from Step 1 detection)
git add <list-of-changed-files> .STATUS

# If behind remote, attempt rebase first
behind=$(git rev-list --count HEAD..origin/$current_branch 2>/dev/null || echo 0)
if [ "$behind" -gt 0 ]; then
    git pull --rebase origin "$current_branch" || {
        echo "⚠️  Rebase conflicts detected. Skipping push."
        echo "   Resolve manually: git rebase --continue"
        # Continue without pushing
    }
fi

# Commit with generated session message
git commit -m "<generated-session-summary>"

# Push (set upstream if needed)
git push origin "$current_branch" -u 2>/dev/null || {
    echo "⚠️  Push failed. Changes are committed locally."
    echo "   Try: git push origin $current_branch"
    # Continue with .STATUS update regardless
}
```

**Update Option A label:**

```
A) Yes - Full auto: .STATUS + commit + push + sync
```

**Output in SESSION CAPTURED:**

```
┌─────────────────────────────────────────────────────────────┐
│ ✅ SESSION CAPTURED                                         │
├─────────────────────────────────────────────────────────────┤
│ Updated: .STATUS                                            │
│ Committed: feat: [session summary] (abc1234)               │
│ Pushed: origin/feature/my-feature                          │
│ Next action: [what you said is next]                       │
└─────────────────────────────────────────────────────────────┘
```

If push fails, show committed hash but note push status:

```
│ Committed: feat: [session summary] (abc1234)               │
│ Push: ⚠️  Failed (changes saved locally)                    │
```

#### Option B: Edit Accomplishments

Ask user to describe what they completed:

```
Tell me what you accomplished this session:
(I'll update .STATUS and generate commit message)

You can list multiple items:
• Item 1
• Item 2
```

Then proceed with update as in Option A.

#### Option C: Skip .STATUS, Just Commit

Only generate commit message suggestion, don't update .STATUS.

#### Option D: Cancel

Exit without changes.

---

## Special Cases

### No .STATUS file exists

```
📝 No .STATUS file found.

I can still help you commit your work!

Generated commit message:
[based on git changes]

💡 Want better session tracking?
   Create a .STATUS file: new.stat
   Or copy: ~/projects/.templates/.STATUS-template-enhanced
```

Then suggest commit only.

### No git changes detected

```
⚠️  No uncommitted changes or recent commits detected.

Did you:
• Forget to save files?
• Already commit everything?
• Just browse code without changes?

What did you accomplish? (I'll still update .STATUS)
```

### .STATUS file but no git repo

```
✅ Updated .STATUS with your session progress

📝 Note: No git repository detected
   Consider initializing: git init
```

---

## ADHD-Optimized Behaviors

### 1. **Fast Default Path**

- Pressing Enter accepts auto-detected summary
- Generates everything automatically
- No decision paralysis

### 2. **Prevent "I'll Remember"**

- Always captures, even if user thinks they'll remember
- Makes it harder to skip than to do
- 30-second max interaction time

### 3. **Momentum Preservation**

- Asks "what's next?" while context is fresh
- Updates .STATUS immediately
- Makes it easy to resume later

### 4. **Forgiveness Mode**

```
If user says "I don't remember what I did":

No problem! Let me check git...

[Show detected changes]

These changes suggest you worked on:
• [Inference 1]
• [Inference 2]

Sound right? (Y/n)
```

---

## Integration with Other Commands

**Typical Session:**

```
START:  /workflow:recap      # "Where was I?"
        [work happens]
END:    /workflow:done       # "Save context"
        git commit           # Save code
        /git:sync           # Push to remote
```

**Quick Capture Pattern:**

```
DURING: [idea pops up]
        /workflow:brain-dump # Quick save
        [continue work]
END:    /workflow:done       # Captures brain-dumps too
```

**Emergency Exit:**

```
Must stop NOW:
  /workflow:done
  → A (accept auto-summary)
  → [30 seconds total]
```

---

## Output Formats

### For .STATUS Update

Add to "✅ Just Completed" section:

```
✅ Just Completed:
- [Session date/time]: [Accomplishment 1]
- [Accomplishment 2]
- [Accomplishment 3]
```

Update "🔄 Current Work":

```
🔄 Current Work:
- [In-progress item from uncommitted changes]
```

Update "🎯 Next Action":

```
🎯 Next Action:
A) [User's stated next task] ⚡ (recommended)
B) [Alternative if provided]
```

### For Commit Message

```
[type]: [brief description]

Changes:
- [file1]: [what changed]
- [file2]: [what changed]

Session: [duration]
Status: [link to .STATUS if exists]
Next: [next action from .STATUS]
```

---

## Error Handling

### User interrupts mid-command

```
⚠️  Looks like you stopped partway through.

What I captured before interruption:
[show partial data]

Options:
A) Continue where we left off
B) Start over
C) Cancel (lose progress)
```

### .STATUS file is malformed

```
⚠️  .STATUS file exists but format unclear.

I'll backup current .STATUS and help you fix it.

Backed up to: .STATUS.backup.[timestamp]

Create new .STATUS? (Y/n)
```

### Git operations fail

```
⚠️  Git command failed

Still updating .STATUS (that worked fine)

Git error: [error message]
Fix: [suggestion based on error]
```

---

## Examples

### Example 1: Successful Session Capture

**Input:** User runs `/workflow:done` after 2 hours of work

**Detected:**

- 3 git commits
- 2 uncommitted files
- Modified test file
- Updated documentation

**Interaction:**

```
📝 SESSION SUMMARY

✅ COMPLETED:
   • Implemented user authentication (commit: abc123)
   • Added password validation (commit: def456)
   • Fixed login button styling (commit: ghi789)

🔄 IN PROGRESS:
   • Writing tests for auth module (uncommitted)

📁 FILES CHANGED:
   • auth.py - Added login/logout functions
   • test_auth.py - Started test coverage
   • README.md - Updated installation section

⏱️  Session: ~2 hours

Does this look right?
A) Yes ←  [ENTER]
B) Let me edit
C) Skip .STATUS
D) Cancel

> [User presses Enter]

✅ SESSION CAPTURED

Updated: .STATUS
Next action: Complete auth module tests

💡 SUGGESTED COMMIT:

git add . && git commit -m "feat: implement user authentication

- Add login/logout functions (auth.py)
- Add password validation with bcrypt
- Fix login button styling
- Start test coverage for auth module

Session: 2 hours
Next: Complete test coverage"

📋 NEXT SESSION: Start with /workflow:recap
```

### Example 2: Quick Exit (Forgot to Save)

**Input:** User runs `/workflow:done`, no changes detected

**Interaction:**

```
⚠️  No git changes detected

Did you:
• Forget to save files? ←
• Already commit everything?
• Just browse code without changes?

What did you accomplish? (or type 'nothing')

> I added the login function but forgot to save

Got it! Please save your files, then run /workflow:done again.

💡 Quick tip: Enable auto-save in your editor to prevent this
```

### Example 3: User Edits Summary

**Input:** User chooses option B (edit)

**Interaction:**

```
Tell me what you accomplished:

> Fixed the bug with email validation
> Added dark mode toggle
> Updated dependencies

✅ Captured!

Generated commit:
"fix: email validation and dark mode

- Fix email validation regex bug
- Add dark mode toggle to settings
- Update dependencies to latest versions

Session: [detected from git]"

Update .STATUS? (Y/n)
> y

✅ All set! Run /workflow:recap next time to restore context.
```

---

## Related Commands

- **`/workflow:recap`** - Start session (restore context)
- **`/workflow:next`** - Decide what to do next
- **`/git:commit`** - Actually run the suggested commit
- **`/git:sync`** - Push changes to remote

---

## Shell Integration

Works with your shell aliases:

```bash
# DT's shell workflow
work <project>     # Start session → auto-runs /workflow:recap
finish [message]   # End session → runs /workflow:done + commits
```

The `finish` alias can delegate to this command for the capture part.

---

## Success Criteria

✅ **Fast** - 30 seconds max for default path
✅ **Smart** - Auto-detects accomplishments from git
✅ **Forgiving** - Works even if user forgot what they did
✅ **Preserving** - Updates .STATUS for next session
✅ **Actionable** - Generates ready-to-use commit message

**ADHD Win:** Never lose context at session boundaries again!
