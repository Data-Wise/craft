# Tutorial: code:fewer-prompts — One-Shot Bash Allowlist

By the end of this tutorial you will have:

- Installed a curated read-only Bash allowlist that eliminates common permission prompts
- Previewed changes before applying them
- Used `--reset` to undo

**Prerequisites:** craft installed.

---

## Step 1: Preview the Allowlist

See exactly what will be written before touching any files:

```
/craft:code:fewer-prompts --dry-run
```

The output shows every entry, its tier (Tier 1 = always safe, Tier 3 = craft-specific),
and whether it's already present.

---

## Step 2: Apply to This Project

```
/craft:code:fewer-prompts
```

Writes to `.claude/settings.json` in your project root (created if absent).
Restart Claude Code or open a new session for the allowlist to take effect.

**What gets added:**

- **Tier 1:** `git status/log/diff/branch/show`, `ls *`, `find . *`, `grep *`, `wc *`,
  `head *`, `tail *`, `pwd`, `echo *`, `which *`, version checks
- **Tier 3:** `gh pr list/view`, `gh issue list/view`, `gh run list`,
  `./scripts/validate-counts.sh`, `mkdocs build --dry-run`

**Excluded by design:** `cat` (the Read tool handles file reads safely),
`grep -r /`, `find /`, `gh secret list`.

---

## Step 3: Apply Globally (Optional)

To eliminate prompts across all projects:

```
/craft:code:fewer-prompts --global
```

Writes to `~/.claude/settings.json` instead of the project-local file.

---

## Step 4: Undo

```
/craft:code:fewer-prompts --reset
```

Removes only the entries craft installed. Any entries you added manually in
`permissions.allow` are untouched — craft tracks its own entries in a parallel
`craft_allowlist` key and removes only those.

---

## How Tracking Works

The command writes entries to two places:

- `permissions.allow` — the enforcement list Claude Code reads
- `craft_allowlist` — a parallel key that tracks which entries craft owns

This dual-write pattern means `--reset` can be surgical: it removes exactly what
it added and nothing more.
