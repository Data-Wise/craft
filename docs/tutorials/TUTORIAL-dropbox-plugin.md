# Dropbox Plugin Cheat Sheet

Run `claude plugin install dropbox@claude-plugins-official`, then ask
"who am I in Dropbox" to confirm the account link before doing anything
else.

## What it does

Browse, search, read, share, and manage Dropbox files/folders through MCP
tools — list folders, create share links, inspect file requests, move/copy/
delete with confirmation.

## Setup

```bash
claude plugin install dropbox@claude-plugins-official
```

Then authenticate — ask "check my Dropbox account" (calls `who_am_i`) to
confirm the link worked before relying on it.

## Gotchas

1. **Text extraction isn't guaranteed.** `read_file_content` works for
   supported files under 5 MiB; for anything else you get a usable Dropbox
   link instead of the text — don't assume every file is readable inline.
2. **No in-place edits.** This plugin can create new files and manage
   sharing/organization, but it cannot edit or overwrite existing file
   content — that's explicitly out of scope.
3. **"Delete" isn't permanent.** It moves items to Dropbox's own "Deleted
   files" area, not a true wipe — don't rely on it for sensitive-data
   removal.
