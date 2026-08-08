#!/bin/bash
# lib/hook-fallback.sh — Shared installed-hook fallback for branch-guard test suites
# Sourced by test_branch_guard.sh and test_branch_guard_e2e.sh.
#
# ~/.claude/hooks/branch-guard.sh is a shared install target: cc-config also
# ships a branch-guard.sh and symlinks it there, and deliberately relaxed the
# new-code-on-protected-branch tier from MEDIUM to LOW on 2026-07-28. When that
# is what is installed, this suite would assert craft's expectations against
# another repo's artifact and report a craft failure for a cc-config policy
# decision. Fall back to craft's own copy so a local run still exercises craft's
# logic. CI is unaffected: it runs install-guards.sh first, so the installed
# hook there IS this repo's copy and the integration path is still covered.
#
# Set HOOK_SCRIPT_EXPLICIT to any non-empty value to opt out of this fallback
# and force use of the installed hook even when it resolves to another repo.
#
# resolve_hook_fallback <hook_script_var_name> <script_dir>
# Reassigns the named variable in place if the installed hook is a symlink
# owned by another repo.
resolve_hook_fallback() {
  local _hook_var="$1"
  local _script_dir="$2"
  local _hook_script="${!_hook_var}"

  [[ -n "${HOOK_SCRIPT_EXPLICIT:-}" ]] && return
  [[ -L "$_hook_script" ]] || return

  local _link_target
  _link_target="$(readlink "$_hook_script")"

  local _installed_target
  if [[ "$_link_target" = /* ]]; then
    _installed_target="$_link_target"
  else
    # Relative symlink targets resolve relative to the symlink's OWN
    # directory, not the caller's cwd — resolving against cwd silently
    # produces a bogus path (e.g. "/branch-guard.sh") that never matches
    # the repo-root prefix check below, making the fallback fire
    # unconditionally regardless of which repo actually owns the hook.
    local _hook_dir
    _hook_dir="$(cd "$(dirname "$_hook_script")" && pwd)"
    _installed_target="$(cd "$_hook_dir/$(dirname "$_link_target")" 2>/dev/null && pwd)/$(basename "$_link_target")"
  fi

  local _repo_root
  _repo_root="$(cd "$_script_dir/.." && pwd)"

  if [[ "$_installed_target" != "$_repo_root"/* ]]; then
    echo "NOTE: installed hook is owned by another repo ($_installed_target)"
    echo "      falling back to this repo's scripts/branch-guard.sh"
    echo ""
    printf -v "$_hook_var" '%s' "$_repo_root/scripts/branch-guard.sh"
  fi
}
