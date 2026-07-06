# Verify-Gate Detection

Canonical auto-detection table for the "real verify gate" (D8): the step that
runs a project's **actual** verification command and treats its **exit
status** as the authoritative pass/fail. A green agent transcript is NOT
sufficient — the command must really run.

Shared by `drive-engine`, `workflow-engine`, and `plan-orchestrator` (D9b) —
all three skills point here instead of duplicating the table inline.

---

## Detection table

| Detection | Verify command |
|-----------|----------------|
| `tests/test_craft_plugin.py` | `python3 tests/test_craft_plugin.py` |
| `package.json` test script | `npm test` |
| `pyproject.toml` / `pytest.ini` | `pytest` |
| `Cargo.toml` | `cargo test` |
| `DESCRIPTION` (R) | `R CMD check` |

## How to use it

1. **Check for the marker file/config, top to bottom, first match wins.**
   A project can contain more than one marker (e.g. a `pyproject.toml`
   alongside a `package.json`) — pick the first row that matches rather than
   running every possible command.
2. **Run the resolved command and capture its real exit code.** Do not infer
   pass/fail from a subagent's narrative summary of "tests passed" — invoke
   the command yourself (or confirm a subagent actually invoked it) and read
   the exit status.
3. **Pair with a clean-tree check.** Always run `git status --short` alongside
   the verify command to confirm the working tree is clean and committed
   before treating the result as "done." A passing verify command against
   uncommitted changes is not a real green.
4. **No match found** — none of the marker files exist. Surface this
   explicitly rather than silently skipping the gate; the caller must specify
   a verify command manually or the run cannot claim verified-green.

## Consumers

| Skill | How it uses this table |
|-------|-------------------------|
| `drive-engine` | Runs the resolved command once the `/goal` condition clears; its exit status is the authoritative "done" signal for `/craft:orch:drive`. |
| `workflow-engine` | Executes it as a first-class `verify` stage (D8) inside a coded WORKFLOW definition — a strict superset of the drive-engine gate. |
| `plan-orchestrator` | Uses the table at plan-generation time to pre-fill the ORCHESTRATE template's `## Verification` section with the auto-detected command. |
