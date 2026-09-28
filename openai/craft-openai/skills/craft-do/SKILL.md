---
name: craft-do
description: Carry out a coding or documentation task in the current repository. Use when the user asks to implement, fix, update, or otherwise do project work.
---

Carry out the user's task using the current Codex workspace and repository instructions.

1. Inspect the current branch, working tree, and relevant project instructions before editing. Identify existing specs or plans that cover the task.
2. If the user asks for a preview, provide a concise plan and stop before making changes. Otherwise proceed with the requested work.
3. For small tasks, make the smallest complete change. For multi-step work, state the sequence briefly and work through it in reviewable increments.
4. Use available skills and tools only when they directly match the task. Do not dispatch to Craft or Claude slash-command names. Do not create subagents or goals unless the user or active repository instructions call for them.
5. Follow the repository's branch and safety rules. If the correct branch or a required authorization is unclear, inspect the local instructions and state; ask only if those sources do not resolve it.
6. Verify changed behavior with the repository's relevant checks when requested or required by project instructions. Report what changed, checks run, and any remaining uncertainty.

Do not claim work is complete until the requested result and required verification are complete. Do not add automatic prompt rewriting, complexity scores, or a fixed command sequence; choose the workflow from the task and repository evidence.
