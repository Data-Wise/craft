#!/usr/bin/env bash
#
# lib/guards-lock.sh — mkdir-based lock for guards.json mutations.
#
# mkdir is atomic on both macOS and Linux, so it is used as the lock
# primitive here (flock has no CLI on macOS — only the syscall exists,
# confirmed on this machine). A staleness timeout ensures a crashed
# holder can't wedge the lock permanently.
#
# Invoked as a STANDALONE script (bash lib/guards-lock.sh ...), not
# sourced — guards.json has two independent mutation paths that don't
# share a shell process: skills/dev/git/SKILL.md Operation 12 issues
# inline bash from an LLM turn, and scripts/install-guards.sh runs as
# its own process. A sourced function can't coordinate across those.
#
# Usage:
#   bash lib/guards-lock.sh acquire [lockdir] [timeout_sec]
#   bash lib/guards-lock.sh release [lockdir]
#
# Exit codes (acquire): 0 = lock held, 1 = timed out waiting for lock.
# release is always best-effort (never fails the caller's script).

set -euo pipefail

DEFAULT_LOCKDIR="${HOME}/.claude/guards.json.lock"
DEFAULT_TIMEOUT=10     # seconds a lock dir can be held before it's considered stale
POLL_INTERVAL=0.1      # seconds between acquire retries
MAX_POLLS=200           # ~20s hard cap on total wait, independent of staleness timeout

action="${1:-}"
lockdir="${2:-$DEFAULT_LOCKDIR}"
timeout="${3:-$DEFAULT_TIMEOUT}"

# Portable mtime-in-epoch-seconds (BSD `stat -f %m` vs GNU `stat -c %Y`).
_lock_mtime() {
  stat -f %m "$1" 2>/dev/null || stat -c %Y "$1" 2>/dev/null
}

_acquire() {
  local polls=0
  while true; do
    if mkdir "$lockdir" 2>/dev/null; then
      return 0
    fi

    # Lock is held by someone — check whether it's stale (crashed holder).
    if [[ -d "$lockdir" ]]; then
      local mt now age
      mt="$(_lock_mtime "$lockdir" 2>/dev/null || echo 0)"
      now="$(date +%s)"
      age=$(( now - mt ))
      if (( age >= timeout )); then
        echo "guards-lock: breaking stale lock at $lockdir (age ${age}s >= ${timeout}s)" >&2
        rmdir "$lockdir" 2>/dev/null || true
        continue
      fi
    fi

    polls=$(( polls + 1 ))
    if (( polls > MAX_POLLS )); then
      echo "guards-lock: timed out waiting for lock at $lockdir" >&2
      return 1
    fi
    sleep "$POLL_INTERVAL"
  done
}

_release() {
  rmdir "$lockdir" 2>/dev/null || true
}

case "$action" in
  acquire) _acquire ;;
  release) _release ;;
  *)
    echo "Usage: $0 {acquire|release} [lockdir] [timeout_sec]" >&2
    exit 2
    ;;
esac
