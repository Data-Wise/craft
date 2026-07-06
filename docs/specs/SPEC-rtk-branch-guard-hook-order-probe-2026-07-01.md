# RTK / branch-guard Hook-Ordering Probe — Verification Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use `superpowers:subagent-driven-development` (recommended) or `superpowers:executing-plans` to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Answer, with an actual reproduced test (not inference from documentation), whether installing `rtk-ai/rtk`'s Claude Code hook silently defeats `scripts/branch-guard.sh`'s catastrophic-command protection — then record a go/no-go verdict on RTK adoption. This plan does not install RTK permanently, does not modify `branch-guard.sh`, and does not touch any real craft/research repo's protected branches.

**Background:** `docs/internal/TUTORIAL-rtk-cli-token-proxy.md` §4.2 flags this as an unverified risk: RTK's `PreToolUse`/`Bash` hook rewrites commands before execution (`git commit -m "x"` → `rtk git commit -m "x"`); `branch-guard.sh` is a `PreToolUse`/`Bash` hook on the same registration point whose catastrophic-command regexes are anchored to the start of the command (e.g. `(^|;|&&|\|\|)\s*git\s+(commit|push)`). If RTK's rewrite runs first, the inserted `rtk` token could sit between the anchor and `git`, breaking the match. Neither Claude Code's multi-hook ordering semantics nor RTK's exact rewrite mechanism (mutates `tool_input.command` vs. some other approach) have been confirmed — this plan closes that gap empirically.

**Architecture:** A disposable throwaway git repo (not craft, not any research repo) with `branch-guard.sh` installed at `smart` or `block-all` protection level, RTK installed and initialized globally, and a sequence of deliberately-triggered catastrophic commands run through Claude Code to observe whether branch-guard still blocks them. No permanent changes to the user's real `~/.claude/settings.json` beyond what a normal RTK install makes (reversible via `rtk init -g --uninstall`).

**Tech stack:** Bash, git, RTK (installed via Homebrew), Claude Code CLI. No new code written to craft itself — this is a verification exercise, output is a written verdict.

## Global Constraints

- **Do not run this against `craft`, any R-packages repo, or any research repo.** Use a fresh disposable directory (e.g. `~/scratch/rtk-hook-probe/`) with its own throwaway git history — a corrupted or bypassed branch-guard during testing must never risk real repo state.
- **Do not leave RTK installed globally afterward** unless Task 5's verdict is a clean pass and the user explicitly decides to keep it — default to `rtk init -g --uninstall` as the last step regardless of outcome, then let the user re-install deliberately if they choose to adopt.
- **Record the actual `~/.claude/settings.json` hook array contents** at each stage (before RTK, after RTK) — this is the primary evidence, not a paraphrase of it.
- If `branch-guard.sh` is not already installed on this machine (check via `install-branch-guard.sh`'s idempotent registration check), install it fresh as part of Task 1 rather than assuming it's present.

---

### Task 1: Set up the disposable test repo with branch-guard only (baseline)

**Files:**

- Create: `~/scratch/rtk-hook-probe/` (throwaway git repo, outside all real project directories)

**Steps:**

- [ ] **Step 1:** Create `~/scratch/rtk-hook-probe/`, `git init`, create a `main` branch with one commit, and a `dev` branch.
- [ ] **Step 2:** Confirm `branch-guard.sh` is registered in `~/.claude/settings.json` (via `scripts/install-branch-guard.sh` from the craft repo, or confirm existing registration). Record the full `hooks.PreToolUse` array contents to a file, e.g. `~/scratch/rtk-hook-probe/settings-before-rtk.json`.
- [ ] **Step 3:** Confirm RTK is **not** currently installed (`which rtk` should fail, or if installed, run `rtk init -g --uninstall` first so this baseline is clean).
- [ ] **Step 4:** From a Claude Code session with cwd set to `~/scratch/rtk-hook-probe/` on the `main` branch, attempt a deliberately catastrophic command: `git commit -m "test" && git push`. **Expected (baseline):** branch-guard blocks this on `main` (block-all level) — confirm the block message appears and the command did not execute.
- [ ] **Step 5:** Repeat on `dev` at `smart`/`confirm` level with `git reset --hard` — confirm the MEDIUM/HIGH-tier confirm-or-block behavior fires as documented in `docs/guide/branch-guard-smart-mode.md`.

**Done when:** Two reproduced baseline blocks are confirmed and logged, with the pre-RTK `settings.json` hook array saved to disk.

---

### Task 2: Install RTK and capture the post-install hook state

**Files:**

- Create: `~/scratch/rtk-hook-probe/settings-after-rtk.json`

**Steps:**

- [ ] **Step 1:** `brew install rtk` (or the curl install script), verify with `rtk --version` and `rtk gain`.
- [ ] **Step 2:** `rtk init -g`, then `rtk init --show` to confirm what was installed.
- [ ] **Step 3:** Read `~/.claude/settings.json` and save the full `hooks.PreToolUse` array to `settings-after-rtk.json`. Diff it against `settings-before-rtk.json` from Task 1 — specifically note: (a) whether RTK's hook entry appears before or after `branch-guard.sh`'s entry in the array, (b) whether RTK modified branch-guard's entry at all (it shouldn't, but confirm), (c) the exact `matcher` value RTK registered under (should be `Bash`, confirm it's not a broader or narrower pattern that changes evaluation order).
- [ ] **Step 4:** Restart Claude Code (required for the hook to take effect per RTK's own setup instructions).

**Done when:** Both hook-array snapshots exist on disk and the diff is documented in prose (not just the raw diff), specifically calling out array order.

---

### Task 3: Reproduce the catastrophic commands with RTK active

**Steps:**

- [ ] **Step 1:** From the same disposable repo, on `main`, re-run the exact command from Task 1 Step 4: `git commit -m "test" && git push`. Observe:
  - Does Claude's Bash tool call show the command as rewritten (`rtk git commit ...`) in the transcript, or does it stay as the original text?
  - Does branch-guard's block message still appear?
  - Does the command actually execute (i.e., did the push go through despite `main` being block-all)?
- [ ] **Step 2:** Repeat the `dev`-branch `git reset --hard` case from Task 1 Step 5 under the same RTK-active conditions.
- [ ] **Step 3:** Test at least one command RTK is documented to rewrite via a *different* verb than `git` — e.g. `rm -rf .git` (branch-guard's other catastrophic pattern) — to check whether RTK's filter catalog touches `rm` at all (its README's command list doesn't show an `rm` filter, so this may pass through unrewritten regardless; confirm rather than assume).
- [ ] **Step 4:** For each case, record: the literal command Claude attempted (from the tool-call transcript), whether it was rewritten, and whether branch-guard's block fired.

**Done when:** All three cases have a recorded pass/fail on "did branch-guard still block this," with the literal transcript evidence saved (not paraphrased).

---

### Task 4: Determine the mechanism, if the risk is confirmed

**Only do this task if Task 3 shows branch-guard's protection was bypassed for at least one case.**

- [ ] **Step 1:** Determine whether the bypass happened because (a) RTK's hook ran first and mutated `tool_input.command` before branch-guard saw it, (b) RTK's hook ran first and short-circuited the `PreToolUse` chain entirely (some hook systems stop processing on a specific return value), or (c) some other mechanism — inspect Claude Code's hook execution documentation/changelog for `PreToolUse` chaining behavior if available, or infer from the settings.json array order plus the observed transcript.
- [ ] **Step 2:** Check whether `~/.claude/settings.json` hook array order is deterministic (does re-running `rtk init -g` always insert at the same position — start, end, or where `branch-guard.sh`'s entry happens to be) — this determines whether a fix is "reorder the array" or something deeper.

**Done when:** The mechanism is understood well enough to state a specific, actionable fix (e.g., "re-order the hooks array so branch-guard's entry precedes RTK's" or "this isn't fixable by ordering alone, RTK would need an exclude_commands entry for git").

---

### Task 5: Verdict and cleanup

**Files:**

- Update: `docs/internal/TUTORIAL-rtk-cli-token-proxy.md` §4.2 — replace "unverified" framing with the actual confirmed/refuted result and evidence.
- Update: `docs/specs/SPEC-token-efficiency-and-context-tooling-2026-07-01.md` if RTK adoption is referenced there (check first).

**Steps:**

- [ ] **Step 1:** Write the verdict: CONFIRMED BROKEN (branch-guard bypassed under at least one tested case), CONFIRMED SAFE (branch-guard held in all tested cases), or INCONCLUSIVE (state exactly why, e.g. hook didn't register as expected).
- [ ] **Step 2:** If CONFIRMED BROKEN: state the specific mitigation from Task 4 (reordering, `exclude_commands = ["git"]` in RTK's config, or "do not co-install these two on any repo with protected branches until upstream fixes it").
- [ ] **Step 3:** Update `TUTORIAL-rtk-cli-token-proxy.md` §4.2 with the dated result and a link/reference to this probe's evidence files.
- [ ] **Step 4:** `rtk init -g --uninstall` to remove the hook, RTK.md, and settings.json entry from this test machine (per Global Constraints — don't leave it installed post-probe by default).
- [ ] **Step 5:** Confirm via a fresh `~/.claude/settings.json` read that only `branch-guard.sh`'s entry remains and RTK's is gone.
- [ ] **Step 6:** Delete `~/scratch/rtk-hook-probe/` (the disposable repo) unless the user wants to keep it as a regression-test fixture for re-checking after a future RTK version bump.

**Done when:** The tutorial reflects a confirmed result (not "unverified"), the test machine's real Claude Code hook config is back to its pre-probe state, and the disposable repo is cleaned up or explicitly kept by user request.

---

## Recommended execution order

Tasks 1 → 2 → 3 → 4 (conditional) → 5, strictly in sequence — each task's evidence is the input to the next. Do not skip Task 1's baseline; without it, a bypass observed in Task 3 can't be distinguished from branch-guard simply not being installed/working correctly in the first place.
