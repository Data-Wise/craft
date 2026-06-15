#!/usr/bin/env bash
# scripts/verify-surfaces.sh — multi-surface version assertion + report
#
# Asserts ONE version across every surface craft controls and reports each
# surface's status in an ADHD-friendly one-line-per-surface format.
#
# Legs (all compared against plugin.json — the source of truth):
#   marketplace.json · git tag vX.Y.Z · tap Formula/<name>.rb · brew-installed
#   · Code-registered (installed_plugins.json). Desktop/Cowork is warn-only
#   (one-time manual `claude plugin marketplace add`, not auto-verifiable).
#
# Behavior (spec D1/D2 + absent-leg decision):
#   present + match    -> ✅ aligned
#   present + mismatch -> ❌ BLOCK (exit 1)   [craft-controlled legs only]
#   absent/unreadable  -> ⚠️  warn (does NOT block)
#   Desktop/Cowork     -> ⚠️  warn (always manual)
#
# D1 trigger: only meaningful when .claude-plugin/plugin.json is present; absent
#   -> nothing to verify (exit 0). The release pipeline gates this on the same
#   condition and exposes --skip-surfaces to bypass.
#
# External sources are injectable for testing:
#   SURFACES_GIT_TAG           override the git-tag leg (e.g. v2.37.0)
#   SURFACES_TAP_FORMULA       path to Formula/<name>.rb
#   SURFACES_BREW_VERSION      override `brew list --versions <name>`
#   SURFACES_INSTALLED_PLUGINS path to installed_plugins.json
#   SURFACES_REPO_DIR          repo root holding .claude-plugin/ (default: $PWD)
#
# Usage:
#   ./scripts/verify-surfaces.sh            # human report (default)
#   ./scripts/verify-surfaces.sh --json     # machine-readable
#   ./scripts/verify-surfaces.sh --aggregator Data-Wise/claude-plugins
#
# Exit codes: 0 = all craft legs aligned (or absent/warn), 1 = a craft leg
#             mismatched (block), 2 = usage error.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# formatting.sh sits beside this script in scripts/
if [[ -f "$SCRIPT_DIR/formatting.sh" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/formatting.sh"
    RED="$FMT_RED"; GREEN="$FMT_GREEN"; YELLOW="$FMT_YELLOW"; CYAN="$FMT_CYAN"; NC="$FMT_NC"
else
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
fi

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
JSON_MODE=false
WRITE_STATUS=false
AGGREGATOR=""
AGGREGATOR_FILE=""

while [[ $# -gt 0 ]]; do
    case "$1" in
        --json) JSON_MODE=true ;;
        --write-status) WRITE_STATUS=true ;;
        --aggregator)
            [[ $# -lt 2 ]] && { echo -e "${RED}Error: --aggregator requires owner/repo${NC}"; exit 2; }
            AGGREGATOR="$2"; shift ;;
        --aggregator-file)
            [[ $# -lt 2 ]] && { echo -e "${RED}Error: --aggregator-file requires a path${NC}"; exit 2; }
            AGGREGATOR_FILE="$2"; shift ;;
        --help|-h)
            echo "Usage: $0 [--json] [--write-status] [--aggregator OWNER/REPO] [--aggregator-file PATH]"
            echo ""
            echo "  --json             Machine-readable output"
            echo "  --write-status     Update the surfaces matrix in the repo's .STATUS"
            echo "  --aggregator       Data-Wise aggregator marketplace for the Desktop add step"
            echo "  --aggregator-file  Aggregator marketplace.json to verify this plugin's entry (D5 leg)"
            exit 0 ;;
        *) echo -e "${RED}Error: Unknown argument '$1'${NC}"; exit 2 ;;
    esac
    shift
done

REPO_DIR="${SURFACES_REPO_DIR:-$PWD}"
PLUGIN_JSON="$REPO_DIR/.claude-plugin/plugin.json"
MARKETPLACE_JSON="$REPO_DIR/.claude-plugin/marketplace.json"

# D1: only runs when plugin.json is present.
if [[ ! -f "$PLUGIN_JSON" ]]; then
    [[ "$JSON_MODE" == true ]] \
        && echo '{ "applicable": false, "reason": "no .claude-plugin/plugin.json" }' \
        || echo -e "${YELLOW}verify-surfaces:${NC} no .claude-plugin/plugin.json — nothing to verify"
    exit 0
fi

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
# json_get <file> <python-expr-on-d> — print value or empty on any failure
json_get() {
    python3 -c "import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print(${2})
except Exception:
    pass" "$1" 2>/dev/null
}

PLUGIN_NAME="$(json_get "$PLUGIN_JSON" "d['name']")"
SOT_VERSION="$(json_get "$PLUGIN_JSON" "d['version']")"

if [[ -z "$SOT_VERSION" ]]; then
    echo -e "${RED}Error: cannot read version from $PLUGIN_JSON${NC}"
    exit 2
fi
[[ -z "$PLUGIN_NAME" ]] && PLUGIN_NAME="plugin"

# ---------------------------------------------------------------------------
# Resolve each leg's version. Echo the version, or empty string if the source
# is absent/unreadable. Each resolver is read-only.
# ---------------------------------------------------------------------------
resolve_marketplace() {
    [[ -f "$MARKETPLACE_JSON" ]] || return 0
    # Prefer the matching plugin entry; fall back to metadata.version.
    json_get "$MARKETPLACE_JSON" "next((p.get('version') for p in d.get('plugins',[]) if p.get('name')=='${PLUGIN_NAME}'), d.get('metadata',{}).get('version',''))"
}

resolve_git_tag() {
    if [[ -n "${SURFACES_GIT_TAG:-}" ]]; then
        echo "${SURFACES_GIT_TAG#v}"; return 0
    fi
    git -C "$REPO_DIR" tag --list "v${SOT_VERSION}" 2>/dev/null | sed 's/^v//' | head -1
}

resolve_tap_formula() {
    local formula="${SURFACES_TAP_FORMULA:-}"
    if [[ -z "$formula" ]]; then
        # Best-effort default locations (local checkout / brew tap).
        for cand in \
            "$HOME/projects/dev-tools/homebrew-tap/Formula/${PLUGIN_NAME}.rb" \
            "$(brew --repository 2>/dev/null)/Library/Taps/data-wise/homebrew-tap/Formula/${PLUGIN_NAME}.rb"; do
            [[ -f "$cand" ]] && { formula="$cand"; break; }
        done
    fi
    [[ -f "$formula" ]] || return 0
    # Version lives in the source-tarball url: .../tags/vX.Y.Z.tar.gz
    grep -oE 'tags/v[0-9]+\.[0-9]+\.[0-9]+\.tar\.gz' "$formula" 2>/dev/null \
        | head -1 | grep -oE '[0-9]+\.[0-9]+\.[0-9]+'
}

resolve_brew() {
    if [[ -n "${SURFACES_BREW_VERSION:-}" ]]; then
        echo "$SURFACES_BREW_VERSION"; return 0
    fi
    command -v brew >/dev/null 2>&1 || return 0
    brew list --versions "$PLUGIN_NAME" 2>/dev/null | awk '{print $2}' | head -1
}

resolve_code_registered() {
    local store="${SURFACES_INSTALLED_PLUGINS:-$HOME/.claude/plugins/installed_plugins.json}"
    [[ -f "$store" ]] || return 0
    json_get "$store" "next((e.get('version') for k,entries in d.get('plugins',{}).items() if k.split('@')[0]=='${PLUGIN_NAME}' for e in entries), '')"
}

# D5: the aggregator marketplace entry is a 5th craft-controlled leg — only
# evaluated when an aggregator source is configured (env or --aggregator-file).
AGG_FILE="${SURFACES_AGGREGATOR_FILE:-$AGGREGATOR_FILE}"
resolve_aggregator() {
    [[ -f "$AGG_FILE" ]] || return 0   # configured-but-missing -> absent (warn)
    json_get "$AGG_FILE" "next((p.get('version') for p in d.get('plugins',[]) if p.get('name')=='${PLUGIN_NAME}'), '')"
}

# ---------------------------------------------------------------------------
# Compare and collect results.
#   STATUS arrays carry: label | version | state   (state: ok|mismatch|absent)
# ---------------------------------------------------------------------------
declare -a LEG_LABEL=() LEG_VERSION=() LEG_STATE=()
BLOCK=0

add_leg() {
    local label="$1" version="$2"
    local state
    if [[ -z "$version" ]]; then
        state="absent"
    elif [[ "$version" == "$SOT_VERSION" ]]; then
        state="ok"
    else
        state="mismatch"; BLOCK=1
    fi
    LEG_LABEL+=("$label"); LEG_VERSION+=("$version"); LEG_STATE+=("$state")
}

add_leg "marketplace"     "$(resolve_marketplace)"
add_leg "git tag"         "$(resolve_git_tag)"
add_leg "tap formula"     "$(resolve_tap_formula)"
add_leg "brew-installed"  "$(resolve_brew)"
add_leg "Code-registered" "$(resolve_code_registered)"
[[ -n "$AGG_FILE" ]] && add_leg "aggregator" "$(resolve_aggregator)"

# ---------------------------------------------------------------------------
# Render
# ---------------------------------------------------------------------------
glyph_for() {
    case "$1" in
        ok)       printf '%b' "${GREEN}[OK]${NC}" ;;
        mismatch) printf '%b' "${RED}[X ]${NC}" ;;
        absent)   printf '%b' "${YELLOW}[!]${NC}" ;;
    esac
}

if [[ "$JSON_MODE" == true ]]; then
    printf '{\n'
    printf '  "applicable": true,\n'
    printf '  "plugin": "%s",\n' "$PLUGIN_NAME"
    printf '  "version": "%s",\n' "$SOT_VERSION"
    printf '  "legs": [\n'
    for i in "${!LEG_LABEL[@]}"; do
        sep=","; [[ $i -eq $((${#LEG_LABEL[@]} - 1)) ]] && sep=""
        printf '    {"surface": "%s", "version": "%s", "state": "%s"}%s\n' \
            "${LEG_LABEL[$i]}" "${LEG_VERSION[$i]}" "${LEG_STATE[$i]}" "$sep"
    done
    printf '  ],\n'
    printf '  "desktop": "warn",\n'
    printf '  "blocked": %s\n' "$([[ $BLOCK -eq 1 ]] && echo true || echo false)"
    printf '}\n'
else
    echo -e "${CYAN}Surfaces for ${PLUGIN_NAME} v${SOT_VERSION}${NC}"
    printf '  %b plugin.json      %s  (source of truth)\n' "$(glyph_for ok)" "$SOT_VERSION"
    for i in "${!LEG_LABEL[@]}"; do
        local_ver="${LEG_VERSION[$i]:-—}"
        case "${LEG_STATE[$i]}" in
            ok)       note="" ;;
            mismatch) note="  <- MISMATCH (blocks release)" ;;
            absent)   note="  (unreadable — not verified)"; local_ver="N/A" ;;
        esac
        printf '  %b %-16s %s%s\n' "$(glyph_for "${LEG_STATE[$i]}")" "${LEG_LABEL[$i]}" "$local_ver" "$note"
    done
    # Desktop/Cowork — always a warn (manual, one-time).
    add_target="${AGGREGATOR:-Data-Wise/${PLUGIN_NAME}}"
    printf '  %b %-16s manual — add once: claude plugin marketplace add %s\n' \
        "$(printf '%b' "${YELLOW}[!]${NC}")" "Desktop/Cowork" "$add_target"
    echo ""
    if [[ $BLOCK -eq 1 ]]; then
        echo -e "${RED}BLOCKED${NC} — a craft-controlled surface disagrees with plugin.json (v${SOT_VERSION})."
    else
        echo -e "${GREEN}ALIGNED${NC} — all verifiable craft-controlled surfaces match v${SOT_VERSION}."
    fi
fi

# ---------------------------------------------------------------------------
# .STATUS surfaces matrix (the only file this script writes; opt-in).
# Replaces an existing "## Surfaces" block or appends one — idempotent.
# ---------------------------------------------------------------------------
if [[ "$WRITE_STATUS" == true ]]; then
    STATUS_FILE="$REPO_DIR/.STATUS"
    code_ver=""
    for i in "${!LEG_LABEL[@]}"; do
        [[ "${LEG_LABEL[$i]}" == "Code-registered" ]] && code_ver="${LEG_VERSION[$i]:-n/a}"
    done
    [[ -z "$code_ver" ]] && code_ver="n/a"
    drift="no"; [[ $BLOCK -eq 1 ]] && drift="yes"

    block="## Surfaces (v${SOT_VERSION})

| plugin | code | desktop | released | drift |
|--------|------|---------|----------|-------|
| ${PLUGIN_NAME} | ${code_ver} | manual | ${SOT_VERSION} | ${drift} |"

    python3 - "$STATUS_FILE" "$block" <<'PY'
import sys, re, os
path, block = sys.argv[1], sys.argv[2]
existing = open(path).read() if os.path.exists(path) else ""
# Strip any prior "## Surfaces" section (up to next "## " or EOF).
stripped = re.sub(r'\n*## Surfaces.*?(?=\n## |\Z)', '', existing, flags=re.DOTALL).rstrip()
out = (stripped + "\n\n" + block + "\n") if stripped else (block + "\n")
open(path, 'w').write(out)
PY
    [[ "$JSON_MODE" != true ]] && echo -e "${CYAN}.STATUS surfaces matrix updated${NC}"
fi

exit "$BLOCK"
