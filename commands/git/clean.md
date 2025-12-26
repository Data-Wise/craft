---
description: Clean up merged branches safely
category: git
---

# Git Clean - Remove merged branches

This command safely removes branches that have been merged.

## What I'll do

1. **List merged branches** - Show which branches are merged
2. **Confirm deletion** - Ask before deleting
3. **Delete local branches** - Remove merged branches locally
4. **Optional**: Delete remote branches

## Safety

- Never deletes current branch
- Never deletes main/master/dev
- Always confirms before deletion
- Shows what will be deleted first

## Usage

Run `/git:clean` and I'll show you merged branches!
