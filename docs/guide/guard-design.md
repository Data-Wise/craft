# Guard Suite Design

Architecture notes for the two-hook safety system. See [Guard Suite Guide](guard-suite.md) for user-facing documentation.

---

## Why Two Separate Hooks

The Guard Suite uses two PreToolUse hooks (`branch-guard.sh` and `no-switch-guard.sh`) rather than one monolithic guard. The reason is rooted in the Claude Code hook output contract.

### Two distinct emission mechanisms

**`branch-guard.sh` — model-mediated confirm pattern**

Branch-guard protects commit/push operations. When it fires, it writes a `[CONFIRM]` block to stderr and exits with a non-zero status code. The Claude Code runtime sees the non-zero exit and surfaces the stderr content to the model. The model then presents the confirmation to the user in natural language.

```bash
# branch-guard emission (stderr + exit 1)
echo "[CONFIRM] Direct commit to main is blocked." >&2
exit 1
```

This pattern is correct for commit/push because the model needs to synthesize context (what branch, what files, why blocked) before presenting the decision.

**`no-switch-guard.sh` — platform-native permission decision**

No-switch-guard protects branch-switch, checkout, restore, and worktree operations. When it fires, it emits a `permissionDecision` JSON object on stdout. The Claude Code runtime reads this JSON directly and renders a native permission prompt — bypassing the model entirely.

```bash
# no-switch-guard emission (stdout JSON)
jq -n '{
  "decision": "ask",
  "message": "git switch main with dirty tree — allow?"
}'
```

This pattern is correct for switch/restore operations because they need a low-latency yes/no without model round-trip overhead. Dirty-tree switches and destructive restores are time-sensitive: the user needs to respond before the operation has a chance to proceed.

**Why merging them would break things**

If both guards were merged into one script, the script would need to choose one emission contract. Choosing stderr+exit-1 would make switch/restore confirmations go through the model (slower, wordy). Choosing stdout JSON would make commit/push confirmations bypass model context (less informative). Keeping them separate preserves the right contract for each operation class.

---

## Hook Precedence

Both hooks are registered as PreToolUse hooks in Claude Code settings. The registration order determines which fires first.

**Order:** `branch-guard.sh` fires BEFORE `no-switch-guard.sh`.

The reason: branch-guard covers the broader class of "any dangerous git operation" and has been in production longer. If branch-guard blocks an operation, no-switch-guard never runs — the operation is already stopped. Firing branch-guard first avoids redundant permission prompts when an operation would be blocked by both guards.

For operations that only no-switch-guard covers (branch switches, restores), branch-guard runs first and exits 0 (GREEN), then no-switch-guard fires and makes the actual decision.

---

## The jq Quirk: `false // true → true`

The registry is read with `jq`. A subtle trap exists with the `enabled` field.

In jq, the `//` operator is an "alternative" that returns the right side when the left side is `false` or `null`. This is different from most languages where `false || true` returns `true` only when the left side is falsy but not when it is literally `false` — in jq, `false` is falsy for `//`.

```
$ echo '{"enabled": false}' | jq '.enabled // true'
true   # WRONG — this would ignore an explicit false
```

**Consequence:** if the guards read `enabled` with a `// true` fallback to handle missing fields, `"enabled": false` in the registry would be silently ignored and the guard would activate anyway. Disabling a guard would have no effect.

**The fix:** guards read `enabled` without any fallback:

```bash
enabled=$(jq -r '.guards["no-switch-guard"].enabled // empty' ~/.claude/guards.json 2>/dev/null)
```

`// empty` causes jq to output nothing (rather than `null`) when the field is missing, which the shell treats as an unset variable. The guard then falls through to the fail-open path.

Missing field → fail-open (allow). Explicit `false` → disabled. Explicit `true` → active. The three cases are distinguishable.

---

## The `--staged` Exclusion on `git restore`

`git restore` has two very different behaviors:

| Invocation | What it does | Harm tier |
|------------|--------------|-----------|
| `git restore --staged <file>` | Moves file from staging area back to working tree (un-stages). Does NOT touch working-tree content. | GREEN |
| `git restore <file>` | Discards working-tree changes from `<file>` (restores to HEAD). Irreversible without stash. | RED |

No-switch-guard detects the `--staged` flag explicitly:

```bash
if echo "$args" | grep -q -- '--staged'; then
  # Safe unstage — GREEN, allow silently
  exit 0
fi
# Otherwise RED — ask
```

This distinction is important for daily use. The model frequently runs `git restore --staged` to un-stage files before a commit (a benign, reversible operation). Without the `--staged` exclusion, every un-stage would trigger a RED confirmation prompt, making the guard annoying in normal workflows.

---

## Phase A vs Phase B

The Guard Suite shipped in two phases. Phase A is what is currently in the codebase. Phase B is deferred work.

### Phase A (shipped)

- `no-switch-guard.sh` — new hook, full harm taxonomy, registry reads
- `branch-guard.sh` — duplicate restore/checkout checks removed (now owned by no-switch-guard)
- `~/.claude/guards.json` — registry schema and defaults
- `commands/git/guard.md` — `/craft:git:guard` command (7 actions)
- `skills/guard-audit/SKILL.md` — extended with guard-suite checks
- `.claude-plugin/skills/validation/guard-consistency.md` — new validation skill

### Phase B (deferred)

- `scripts/harm-classify.sh` — shared classification core that both guards call. Currently each guard has its own inline harm-tier logic. Extracting to a shared script would reduce duplication but adds a dependency between two hooks that currently have no shared state. Deferred until there is a third guard that would benefit from the shared classifier.
- Harm taxonomy unit tests — isolated test harness for the classifier logic, separate from the dogfood suite.
- Per-repo registry overrides — allow a repo's `.claude/guards.json` to merge with the global `~/.claude/guards.json` (precedence: repo wins).

---

## The `muted_until` Timestamp Format

The `muted_until` field uses ISO 8601 UTC format, specifically the subset that BSD `date` and GNU `date` both parse without flags:

```
YYYY-MM-DDTHH:MM:SSZ
```

Example: `"2026-06-19T14:30:00Z"`

**Why not Unix epoch?** Epoch integers are harder to inspect in the raw JSON. The ISO format lets you open `~/.claude/guards.json` and immediately see when the mute expires.

**Comparison logic:**

```bash
now=$(date -u +%Y-%m-%dT%H:%M:%SZ)
muted_until=$(jq -r '.guards["no-switch-guard"].muted_until' ~/.claude/guards.json)

if [[ "$muted_until" != "null" && "$now" < "$muted_until" ]]; then
  # Still muted — string comparison works for ISO 8601 UTC
  exit 0
fi
```

ISO 8601 UTC strings sort lexicographically in the same order as their temporal order, so string comparison (`<`) is valid for both BSD and GNU environments. No `date -d` (GNU-only) required.

---

## Registry File Location

`~/.claude/guards.json` is a user-level file, not a repo-level file. This is intentional:

- Guard preferences are personal (one developer's `yolo` profile should not affect a teammate)
- The registry persists across worktrees and repos without needing to be committed
- The fail-open guarantee means a missing registry is safe — it does not need to be tracked

If a future Phase B adds per-repo overrides, the merge order will be: global `~/.claude/guards.json` → repo `.claude/guards.json` → CLI flags.

---

## Relationship to `branch-guard.sh` Smart Mode

`branch-guard.sh` has a "smart mode" that activates when the repo has a `dev` or `draft` branch. In smart mode, the guard blocks new file creation on `dev`/`draft` (forcing work to feature branches) while allowing edits to existing files.

Smart mode is entirely within `branch-guard.sh` and is unaffected by the Guard Suite split. No-switch-guard does not participate in smart-mode decisions. The two guards have orthogonal scopes:

- `branch-guard.sh` — what you commit and where
- `no-switch-guard.sh` — where you move and what you restore

---

## See Also

- [Guard Suite Guide](guard-suite.md) — user-facing documentation
- [Guard Suite Tutorial](../tutorials/TUTORIAL-guard-suite.md) — hands-on walkthrough
- [Branch Guard Smart Mode](branch-guard-smart-mode.md) — smart-mode details
