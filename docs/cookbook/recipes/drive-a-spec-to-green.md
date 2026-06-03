# Recipe: Drive a spec to green

1. `/craft:orchestrate:drive --dry-run`   # preview the /goal condition
2. Review the condition + preconditions.
3. `/craft:orchestrate:drive`             # confirm gate → enable auto mode → loop
4. Wait for the real verify gate to report green.
5. Copy the printed `gh pr create --base dev` and open the PR yourself.

> **drive vs `--swarm`:** use `drive` for a spec-anchored `/goal` turn-loop to autonomous completion; use `/craft:orchestrate --swarm` for free-form parallel independent tasks.
