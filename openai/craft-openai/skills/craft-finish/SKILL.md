---
name: craft-finish
description: Capture progress when wrapping up a coding session. Use when the user asks to finish, wrap up, save progress, or end the session.
---

Summarize the current work and preserve enough context to resume.

1. Read the repository instructions, current .STATUS, working-tree changes, and recent commits. Do not infer completed work from filenames alone.
2. Summarize completed work in 3–5 plain-language bullets. Identify remaining work and blockers from the observed state.
3. When the user explicitly asks to finish or save progress, update the existing .STATUS sections for completed work, next action, and blockers. Preserve its format and unrelated content. If there is no .STATUS, draft a concise file with those sections.
4. Suggest a conventional commit message based on the actual changes. Do not commit, push, or discard changes as part of this skill.
5. Report verification that was actually run and any remaining unverified item. End with the next action.

Keep the update scoped to session state. Do not run Claude-specific CLAUDE.md or settings synchronization, Obsidian sync, memory tooling, or Craft detectors. Ask before writing .STATUS when the user's intent to save progress is not explicit.
