# /craft:restore

> **Restore git and session context in one read-only command.**

---

## Synopsis

```bash
/craft:restore
/craft:restore detailed
/craft:restore summary
```

---

## Description

Combines two existing recap sources into one output, so returning to a project
after a break answers "where did I leave off" without asking twice:

1. **Session state** — the `adhd-workflow` skill's "Context Restoration" operation:
   `.STATUS` state (Just Completed / Next Action / Blockers), git activity (last
   48h), open PRs/issues, planning files, Obsidian flow status.
2. **Git activity** — the `dev/git` skill's Operation 7: today's/this week's
   commits, branch ahead/behind, unpushed work, open PRs. This portion is
   mode-aware (`default` | `detailed` | `summary`).

The two sources overlap on recent commits and open PRs — the command
de-duplicates on presentation (one combined git-activity block, mode-aware from
source 2) rather than printing the same commits twice.

**Read-only.** No `.STATUS` writes, no commits, no sync — this command only
reads and reports. There is no `--sync` flag.

---

## Modes

| Mode | Applies to | Behavior |
|------|-----------|----------|
| `default` | git-activity portion | Standard verbosity |
| `detailed` | git-activity portion | Full commit list, diff stats |
| `summary` | git-activity portion | One-line git state |

The session-state portion (`.STATUS`/adhd-workflow side) has no mode support —
its output is single-verbosity regardless of the mode argument. This was
verified against `skills/workflow/adhd-workflow/SKILL.md` before implementation
(see [`SPEC-craft-restore-2026-07-17.md`](../specs/SPEC-craft-restore-2026-07-17.md));
adding modes there is an explicit open question, not shipped today.

---

## Output

```
GIT ACTIVITY (last 48h, mode: default)
   <commits> · branch ahead/behind · unpushed work · open PRs

SESSION STATE (.STATUS)
   Just Completed / Next Action / Blockers · planning files · Obsidian flow status

WHAT'S NEXT
   → single suggested next step
```

---

## Relationship to Other Commands

| Command | Role |
|---------|------|
| `/craft:finish` | **Produces** the `.STATUS` state this command consumes |
| `/craft:next` | Suggests the next task from the same `.STATUS` state |
| `/craft:restore` | Read-only opener — run first when returning after a break |

---

## Why This Exists

Replaces the deleted `git-recap` and `recap` root commands (removed 2026-07-09).
Those covered git activity and session recap as two separate asks; `/craft:restore`
combines them into one, mirroring the framing of `savant:restore` ("restore
context on a research project") — minus its optional `--sync` write path, which
this command deliberately does not implement.

A cross-plugin `/restore` dispatcher (routing to `savant:restore` for research
projects, `craft:restore` for dev-tools projects) was proposed and investigated
alongside this command, but confirmed structurally blocked: craft's `/do`/`/hub`
routers cannot dispatch into another plugin's namespace. That idea is out of
scope here — see the spec's Open Questions.

---

## See Also

- **Session completion:** `/craft:finish` - Save context, produces the `.STATUS` this reads
- **Decision support:** `/craft:next` - What to do next
- **Spec:** [`docs/specs/SPEC-craft-restore-2026-07-17.md`](../specs/SPEC-craft-restore-2026-07-17.md)
