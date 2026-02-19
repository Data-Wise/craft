#!/usr/bin/env bash
# scripts/ci-monitor.sh - CI monitoring loop with diagnosis and retry
# Polls GitHub Actions CI status for a PR, diagnoses failures, and reports.
#
# Usage:
#   ./scripts/ci-monitor.sh <pr-number>                    # Poll with defaults
#   ./scripts/ci-monitor.sh <pr-number> --timeout 300      # Custom timeout (seconds)
#   ./scripts/ci-monitor.sh <pr-number> --interval 15      # Custom poll interval
#   ./scripts/ci-monitor.sh <pr-number> --config path.json # Custom config file
#
# Exit codes:
#   0 = CI passed (all checks green)
#   1 = CI failed (after retries exhausted or timeout)
#   2 = usage error
#
# Output format:
#   JSON on stdout with status, diagnosis, and elapsed time.
#   Human-readable progress on stderr.

set -euo pipefail

# ============================================================================
# Configuration (defaults, overridden by config file or CLI args)
# ============================================================================

CI_TIMEOUT=600          # 10 minutes default
CI_MAX_RETRIES=3
CI_POLL_INTERVAL=30
CI_AUTO_FIX=("version_mismatch" "lint_failure" "changelog_format")
CI_ASK_BEFORE_FIX=("test_failure" "security_audit" "build_failure")

# ============================================================================
# Argument Parsing
# ============================================================================

PR_NUMBER=""
CONFIG_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --timeout) CI_TIMEOUT="$2"; shift 2 ;;
        --interval) CI_POLL_INTERVAL="$2"; shift 2 ;;
        --max-retries) CI_MAX_RETRIES="$2"; shift 2 ;;
        --config) CONFIG_FILE="$2"; shift 2 ;;
        --help|-h)
            echo "Usage: ci-monitor.sh <pr-number> [--timeout N] [--interval N] [--config file]"
            exit 0
            ;;
        *)
            if [[ -z "$PR_NUMBER" ]] && [[ "$1" =~ ^[0-9]+$ ]]; then
                PR_NUMBER="$1"
            fi
            shift
            ;;
    esac
done

if [[ -z "$PR_NUMBER" ]]; then
    echo "Error: PR number required" >&2
    echo "Usage: ci-monitor.sh <pr-number>" >&2
    exit 2
fi

# Load config file if provided (or auto-detect)
if [[ -z "$CONFIG_FILE" ]]; then
    for candidate in .claude/release-config.json release-config.json; do
        if [[ -f "$candidate" ]]; then
            CONFIG_FILE="$candidate"
            break
        fi
    done
fi

if [[ -n "$CONFIG_FILE" ]] && [[ -f "$CONFIG_FILE" ]]; then
    CI_TIMEOUT=$(jq -r '.ci_timeout // empty' "$CONFIG_FILE" 2>/dev/null || echo "$CI_TIMEOUT")
    CI_MAX_RETRIES=$(jq -r '.ci_max_retries // empty' "$CONFIG_FILE" 2>/dev/null || echo "$CI_MAX_RETRIES")
    CI_POLL_INTERVAL=$(jq -r '.ci_poll_interval // empty' "$CONFIG_FILE" 2>/dev/null || echo "$CI_POLL_INTERVAL")
    echo "Loaded config from $CONFIG_FILE" >&2
fi

# Colors for stderr output
if [[ -t 2 ]]; then
    GREEN='\033[0;32m' RED='\033[0;31m' YELLOW='\033[1;33m'
    CYAN='\033[1;36m' BOLD='\033[1m' NC='\033[0m'
else
    GREEN='' RED='' YELLOW='' CYAN='' BOLD='' NC=''
fi

# ============================================================================
# CI Status Functions
# ============================================================================

get_ci_status() {
    # Returns: success, failure, in_progress, pending, or unknown
    local status
    status=$(gh run list --branch "$(gh pr view "$PR_NUMBER" --json headRefName -q .headRefName 2>/dev/null)" \
        --limit 1 --json status,conclusion -q '.[0] | if .status == "completed" then .conclusion else .status end' 2>/dev/null || echo "unknown")

    # Normalize status values
    case "$status" in
        success|completed) echo "success" ;;
        failure|failed) echo "failure" ;;
        in_progress|queued|waiting|pending|requested) echo "in_progress" ;;
        *) echo "unknown" ;;
    esac
}

get_failed_logs() {
    # Get the failed run logs for diagnosis
    local run_id
    run_id=$(gh run list --branch "$(gh pr view "$PR_NUMBER" --json headRefName -q .headRefName 2>/dev/null)" \
        --limit 1 --json databaseId -q '.[0].databaseId' 2>/dev/null || echo "")

    if [[ -n "$run_id" ]]; then
        gh run view "$run_id" --log-failed 2>/dev/null | tail -100
    fi
}

# ============================================================================
# Failure Diagnosis
# ============================================================================

diagnose_failure() {
    local logs="$1"
    local category="unknown"
    local summary=""

    # Version mismatch
    if echo "$logs" | grep -qiE 'version.*mismatch|expected.*v[0-9]|version.*drift'; then
        category="version_mismatch"
        summary="Version string mismatch detected in CI"
    # Lint failure
    elif echo "$logs" | grep -qiE 'lint.*error|eslint.*error|ruff.*error|markdownlint'; then
        category="lint_failure"
        summary="Linting errors detected"
    # Changelog format
    elif echo "$logs" | grep -qiE 'changelog.*invalid|changelog.*missing|CHANGELOG'; then
        category="changelog_format"
        summary="Changelog format issue"
    # Test failure
    elif echo "$logs" | grep -qiE 'test.*fail|FAILED|AssertionError|expect.*to'; then
        category="test_failure"
        summary="Test failure detected"
    # Security audit
    elif echo "$logs" | grep -qiE 'vulnerabilit|security.*audit|CVE-'; then
        category="security_audit"
        summary="Security vulnerability detected"
    # Build failure
    elif echo "$logs" | grep -qiE 'build.*fail|compilation.*error|TypeError|SyntaxError'; then
        category="build_failure"
        summary="Build failure detected"
    else
        summary="Unknown CI failure — manual review needed"
    fi

    # Output as JSON
    printf '{"category": "%s", "summary": "%s"}' "$category" "$summary"
}

is_auto_fixable() {
    local category="$1"
    for auto in "${CI_AUTO_FIX[@]}"; do
        [[ "$category" == "$auto" ]] && return 0
    done
    return 1
}

# ============================================================================
# Main Polling Loop
# ============================================================================

echo -e "${BOLD}CI Monitor${NC} — PR #${PR_NUMBER}" >&2
echo -e "Timeout: ${CI_TIMEOUT}s | Interval: ${CI_POLL_INTERVAL}s | Max retries: ${CI_MAX_RETRIES}" >&2
echo "" >&2

RETRIES=0
TOTAL_ELAPSED=0

while [[ $RETRIES -le $CI_MAX_RETRIES ]]; do
    ELAPSED=0
    POLL_COUNT=0

    while [[ $ELAPSED -lt $CI_TIMEOUT ]]; do
        POLL_COUNT=$((POLL_COUNT + 1))
        STATUS=$(get_ci_status)

        case "$STATUS" in
            success)
                echo -e "[Poll ${POLL_COUNT}] ${GREEN}✅ All checks passed${NC} (${ELAPSED}s elapsed)" >&2
                TOTAL_ELAPSED=$((TOTAL_ELAPSED + ELAPSED))
                # Output final result as JSON
                printf '{"status": "success", "elapsed": %d, "retries": %d, "pr": %d}\n' \
                    "$TOTAL_ELAPSED" "$RETRIES" "$PR_NUMBER"
                exit 0
                ;;
            failure)
                echo -e "[Poll ${POLL_COUNT}] ${RED}❌ Failed${NC} (${ELAPSED}s elapsed)" >&2
                break
                ;;
            in_progress)
                echo -e "[Poll ${POLL_COUNT}] ${YELLOW}⏳ In progress${NC} (${ELAPSED}s elapsed)" >&2
                sleep "$CI_POLL_INTERVAL"
                ELAPSED=$((ELAPSED + CI_POLL_INTERVAL))
                ;;
            unknown)
                echo -e "[Poll ${POLL_COUNT}] ${CYAN}? Unknown status${NC} (${ELAPSED}s elapsed)" >&2
                sleep "$CI_POLL_INTERVAL"
                ELAPSED=$((ELAPSED + CI_POLL_INTERVAL))
                ;;
        esac
    done

    TOTAL_ELAPSED=$((TOTAL_ELAPSED + ELAPSED))

    # Handle timeout
    if [[ "$STATUS" != "failure" ]]; then
        echo -e "${RED}Timeout after ${CI_TIMEOUT}s${NC}" >&2
        printf '{"status": "timeout", "elapsed": %d, "retries": %d, "pr": %d}\n' \
            "$TOTAL_ELAPSED" "$RETRIES" "$PR_NUMBER"
        exit 1
    fi

    # Handle failure — diagnose and report
    echo "" >&2
    echo -e "${BOLD}Diagnosing failure...${NC}" >&2

    LOGS=$(get_failed_logs)
    DIAGNOSIS=$(diagnose_failure "$LOGS")
    CATEGORY=$(echo "$DIAGNOSIS" | jq -r '.category')
    SUMMARY=$(echo "$DIAGNOSIS" | jq -r '.summary')

    echo -e "  Category: ${BOLD}${CATEGORY}${NC}" >&2
    echo -e "  Summary: ${SUMMARY}" >&2

    if is_auto_fixable "$CATEGORY"; then
        echo -e "  Fix type: ${GREEN}auto-fixable${NC}" >&2
    else
        echo -e "  Fix type: ${YELLOW}requires user approval${NC}" >&2
    fi

    # Check if we've exhausted retries
    if [[ $RETRIES -ge $CI_MAX_RETRIES ]]; then
        echo "" >&2
        echo -e "${RED}Max retries ($CI_MAX_RETRIES) exhausted${NC}" >&2
        printf '{"status": "failed_after_retries", "elapsed": %d, "retries": %d, "pr": %d, "diagnosis": %s}\n' \
            "$TOTAL_ELAPSED" "$RETRIES" "$PR_NUMBER" "$DIAGNOSIS"
        exit 1
    fi

    RETRIES=$((RETRIES + 1))

    # Output diagnosis for the caller to handle (fix + push + re-poll)
    printf '{"status": "needs_fix", "retry": %d, "elapsed": %d, "pr": %d, "diagnosis": %s}\n' \
        "$RETRIES" "$TOTAL_ELAPSED" "$PR_NUMBER" "$DIAGNOSIS"

    echo "" >&2
    echo -e "Waiting for new CI run after fix (retry ${RETRIES}/${CI_MAX_RETRIES})..." >&2
    echo -e "Re-polling in ${CI_POLL_INTERVAL}s..." >&2
    sleep "$CI_POLL_INTERVAL"
done

# Should not reach here
printf '{"status": "error", "elapsed": %d, "retries": %d, "pr": %d}\n' \
    "$TOTAL_ELAPSED" "$RETRIES" "$PR_NUMBER"
exit 1
