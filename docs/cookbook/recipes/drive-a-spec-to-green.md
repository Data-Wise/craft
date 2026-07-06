# Recipe: Drive a spec to green

1. `/craft:orch:drive --dry-run`   # preview the /goal condition
2. Review the condition + preconditions.
3. `/craft:orch:drive`             # confirm gate → enable auto mode → loop
4. Wait for the real verify gate to report green.
5. Copy the printed `gh pr create --base dev` and open the PR yourself.

> **drive vs `--swarm`:** use `drive` for a spec-anchored `/goal` turn-loop to autonomous completion; use `/craft:orch --swarm` for free-form parallel independent tasks.
