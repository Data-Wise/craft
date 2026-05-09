#!/bin/bash
# protect-baseline.sh - Apply craft's baseline branch protection to a GitHub repo
#
# Baseline: PR required (0 reviews) + no force-push + no delete + no enforce-admins.
# Optional: required status checks, strict (require up-to-date) mode, dry-run.
#
# Usage:
#   ./protect-baseline.sh                                    # current repo, default branch
#   ./protect-baseline.sh --repo OWNER/REPO                  # explicit repo
#   ./protect-baseline.sh --branch BRANCH                    # explicit branch
#   ./protect-baseline.sh --check "test" --check "lint"      # add status checks (repeatable)
#   ./protect-baseline.sh --strict                           # require up-to-date branches
#   ./protect-baseline.sh --dry-run                          # show what would be applied
#   ./protect-baseline.sh --remove                           # remove protection
#   ./protect-baseline.sh --show                             # show current protection

set -euo pipefail

REPO=""
BRANCH=""
CHECKS=()
STRICT="false"
DRY_RUN="false"
REMOVE="false"
SHOW="false"

while [[ $# -gt 0 ]]; do
  case "$1" in
    --repo)         REPO="$2"; shift 2 ;;
    --branch)       BRANCH="$2"; shift 2 ;;
    --check)        CHECKS+=("$2"); shift 2 ;;
    --strict)       STRICT="true"; shift ;;
    --dry-run)      DRY_RUN="true"; shift ;;
    --remove)       REMOVE="true"; shift ;;
    --show)         SHOW="true"; shift ;;
    -h|--help)
      awk 'NR==1{next} /^set -euo/{exit} {sub(/^# ?/,""); print}' "$0"
      exit 0 ;;
    *) echo "Unknown arg: $1" >&2; exit 2 ;;
  esac
done

if ! command -v gh >/dev/null 2>&1; then
  echo "ERROR: gh CLI not found. Install: brew install gh" >&2
  exit 1
fi

if [[ -z "$REPO" ]]; then
  if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "ERROR: Not in a git repo. Pass --repo OWNER/REPO." >&2
    exit 1
  fi
  REMOTE_URL=$(git remote get-url origin 2>/dev/null || true)
  if [[ -z "$REMOTE_URL" ]]; then
    echo "ERROR: No 'origin' remote. Pass --repo OWNER/REPO." >&2
    exit 1
  fi
  REPO=$(echo "$REMOTE_URL" | sed -E 's#.*[/:]([^/]+/[^/.]+)(\.git)?$#\1#')
fi

if [[ -z "$BRANCH" ]]; then
  default_err=$(mktemp -t protect-baseline-err.XXXXXX)
  BRANCH=$(gh api "repos/$REPO" --jq '.default_branch' 2>"$default_err" || true)
  if [[ -z "$BRANCH" ]]; then
    echo "ERROR: Could not detect default branch for $REPO. Pass --branch NAME." >&2
    if [[ -s "$default_err" ]]; then
      sed 's/^/  gh: /' "$default_err" >&2
    fi
    rm -f "$default_err"
    exit 1
  fi
  rm -f "$default_err"
fi

echo "Repo:   $REPO" >&2
echo "Branch: $BRANCH" >&2

if [[ "$SHOW" == "true" ]]; then
  result=$(gh api "repos/$REPO/branches/$BRANCH/protection" 2>&1 || true)
  if echo "$result" | grep -q "Branch not protected"; then
    echo "Status: NONE (unprotected)" >&2
    exit 0
  fi
  echo "$result" | python3 -m json.tool
  exit 0
fi

if [[ "$REMOVE" == "true" ]]; then
  if [[ "$DRY_RUN" == "true" ]]; then
    echo "Action: REMOVE protection (dry-run, no API call)"
    exit 0
  fi
  echo "Action: REMOVE protection"
  if ! gh api -X DELETE "repos/$REPO/branches/$BRANCH/protection"; then
    echo "FAILED to remove protection on $REPO@$BRANCH" >&2
    exit 1
  fi
  echo "Removed protection on $REPO@$BRANCH"
  exit 0
fi

if [[ ${#CHECKS[@]} -gt 0 ]]; then
  CHECKS_JSON=$(printf '%s\n' "${CHECKS[@]}" | python3 -c "
import sys, json
items = [s.rstrip('\n') for s in sys.stdin.readlines() if s.strip()]
print(json.dumps(items))
")
  STATUS_CHECKS_BLOCK=$(cat <<EOF
"required_status_checks": {
    "strict": $STRICT,
    "contexts": $CHECKS_JSON
  }
EOF
)
else
  STATUS_CHECKS_BLOCK='"required_status_checks": null'
fi

PAYLOAD=$(cat <<EOF
{
  $STATUS_CHECKS_BLOCK,
  "enforce_admins": false,
  "required_pull_request_reviews": {
    "dismiss_stale_reviews": false,
    "require_code_owner_reviews": false,
    "required_approving_review_count": 0
  },
  "restrictions": null,
  "allow_force_pushes": false,
  "allow_deletions": false,
  "required_conversation_resolution": false,
  "lock_branch": false,
  "allow_fork_syncing": false
}
EOF
)

echo "Action: APPLY baseline protection"
echo "  PR required:    yes (0 reviews)"
echo "  Force push:     blocked"
echo "  Delete:         blocked"
if [[ ${#CHECKS[@]} -gt 0 ]]; then
  echo "  Status checks:  ${#CHECKS[@]} (strict=$STRICT)"
  for c in "${CHECKS[@]}"; do echo "                    - $c"; done
else
  echo "  Status checks:  none"
fi

if [[ "$DRY_RUN" == "true" ]]; then
  echo ""
  echo "--- Payload (dry-run, no API call) ---"
  echo "$PAYLOAD" | python3 -m json.tool
  exit 0
fi

PAYLOAD_FILE=$(mktemp -t protect-baseline.XXXXXX.json)
trap 'rm -f "$PAYLOAD_FILE"' EXIT
echo "$PAYLOAD" > "$PAYLOAD_FILE"

if ! gh api -X PUT "repos/$REPO/branches/$BRANCH/protection" --input "$PAYLOAD_FILE" >/dev/null; then
  echo "FAILED to apply protection on $REPO@$BRANCH" >&2
  exit 1
fi
echo "Applied successfully."
