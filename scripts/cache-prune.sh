#!/usr/bin/env bash
# scripts/cache-prune.sh — GC stale local-plugins version-cache directories
#
# Claude Code keeps every installed version under
#   ~/.claude/plugins/cache/local-plugins/<name>/<version>/
# and never garbage-collects them, so old versions accumulate (scholar alone
# had 2.17.0–2.24.0). This prunes them, keeping CURRENT + 2 MOST RECENT per
# plugin (D7), and ALWAYS reports what it removes — never a silent delete.
#
# Distinct from `claude plugin prune` (that GCs unused *dependency* plugins,
# not the per-version cache).
#
# Usage:
#   ./scripts/cache-prune.sh            # dry-run: report what WOULD be removed
#   ./scripts/cache-prune.sh --prune    # actually delete old version dirs
#   ./scripts/cache-prune.sh --json     # machine-readable
#
# Env:
#   CACHE_DIR   local-plugins cache root
#               (default: ~/.claude/plugins/cache/local-plugins)
#
# Exit codes: 0 = success (maintenance, never a release gate), 2 = usage error.

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
if [[ -f "$SCRIPT_DIR/formatting.sh" ]]; then
    # shellcheck disable=SC1091
    source "$SCRIPT_DIR/formatting.sh"
    RED="$FMT_RED"; GREEN="$FMT_GREEN"; YELLOW="$FMT_YELLOW"; CYAN="$FMT_CYAN"; NC="$FMT_NC"
else
    RED='\033[0;31m'; GREEN='\033[0;32m'; YELLOW='\033[1;33m'; CYAN='\033[0;36m'; NC='\033[0m'
fi

RETENTION=3   # current + 2 most recent
PRUNE=false
JSON_MODE=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --prune|--fix) PRUNE=true ;;
        --dry-run|-n)  PRUNE=false ;;
        --json)        JSON_MODE=true ;;
        --help|-h)
            echo "Usage: $0 [--prune] [--json]"
            echo ""
            echo "  --prune   Delete old version dirs (default: dry-run report)"
            echo "  --json    Machine-readable output"
            echo "  Keeps current + 2 most recent per plugin; always reports removals."
            exit 0 ;;
        *) echo -e "${RED}Error: Unknown argument '$1'${NC}"; exit 2 ;;
    esac
    shift
done

CACHE_DIR="${CACHE_DIR:-$HOME/.claude/plugins/cache/local-plugins}"
INSTALLED_PLUGINS="${INSTALLED_PLUGINS:-$HOME/.claude/plugins/installed_plugins.json}"

# installed_version <plugin> — the version Code actually has registered, or
# empty. Used to NEVER prune the running version even if it's not in the newest
# RETENTION (a pinned/downgraded install must survive).
installed_version() {
    [[ -f "$INSTALLED_PLUGINS" ]] || return 0
    python3 -c "import json,sys
try:
    d=json.load(open(sys.argv[1]))
    print(next((e.get('version') for k,entries in d.get('plugins',{}).items() if k.split('@')[0]==sys.argv[2] for e in entries), ''))
except Exception:
    pass" "$INSTALLED_PLUGINS" "$1" 2>/dev/null
}

if [[ ! -d "$CACHE_DIR" ]]; then
    [[ "$JSON_MODE" == true ]] \
        && echo "{ \"cache_dir\": \"${CACHE_DIR}\", \"retention\": ${RETENTION}, \"plugins\": [], \"pruned\": false }" \
        || echo -e "${YELLOW}cache-prune:${NC} no cache dir at ${CACHE_DIR} — nothing to do"
    exit 0
fi

# Collect per-plugin kept/prunable version lists.
declare -a J_PLUGIN=() J_KEPT=() J_PRUNABLE=()
TOTAL_PRUNABLE=0
TOTAL_FREED=0

if [[ "$JSON_MODE" != true ]]; then
    echo -e "${CYAN}Cache prune${NC} (keep current + $((RETENTION - 1)) most recent)"
    echo "  Cache: ${CACHE_DIR}"
    echo ""
fi

for plugin_dir in "$CACHE_DIR"/*/; do
    [[ -d "$plugin_dir" ]] || continue
    plugin="$(basename "$plugin_dir")"

    # Semver version dirs only, sorted newest-first. Filtering to a version
    # pattern means non-version dirs (e.g. 'dev', 'backup', a symlink) are
    # IGNORED entirely — never counted toward retention, never pruned. Without
    # this, `sort -rV` ranked such junk above real releases, so the newest real
    # versions fell into the prunable tail and `--prune` deleted them.
    mapfile -t versions < <(find "$plugin_dir" -mindepth 1 -maxdepth 1 -type d -exec basename {} \; 2>/dev/null \
        | grep -E '^[0-9]+\.[0-9]+\.[0-9]+' | sort -rV)
    [[ ${#versions[@]} -eq 0 ]] && continue

    # The installed version must never be pruned even if it's older than the
    # newest RETENTION (a pinned/downgraded install).
    cur="$(installed_version "$plugin")"

    kept=("${versions[@]:0:RETENTION}")
    prunable=()
    for v in "${versions[@]:RETENTION}"; do
        if [[ -n "$cur" && "$v" == "$cur" ]]; then
            kept+=("$v")
        else
            prunable+=("$v")
        fi
    done

    J_PLUGIN+=("$plugin")
    J_KEPT+=("$(IFS=,; echo "${kept[*]}")")
    J_PRUNABLE+=("$(IFS=,; echo "${prunable[*]:-}")")

    if [[ ${#prunable[@]} -eq 0 ]]; then
        [[ "$JSON_MODE" != true ]] && echo -e "  ${GREEN}[keep]${NC} ${plugin}: ${#versions[@]} version(s), within retention"
        continue
    fi

    TOTAL_PRUNABLE=$((TOTAL_PRUNABLE + ${#prunable[@]}))
    if [[ "$JSON_MODE" != true ]]; then
        echo -e "  ${CYAN}${plugin}${NC}: keep [${kept[*]}]"
    fi

    for v in "${prunable[@]}"; do
        target="${plugin_dir}${v}"
        if [[ "$PRUNE" == true ]]; then
            rm -rf "$target"
            [[ "$JSON_MODE" != true ]] && echo -e "    ${RED}[removed]${NC} ${plugin}/${v}"
        else
            [[ "$JSON_MODE" != true ]] && echo -e "    ${YELLOW}[prunable]${NC} ${plugin}/${v}"
        fi
        TOTAL_FREED=$((TOTAL_FREED + 1))
    done
done

if [[ "$JSON_MODE" == true ]]; then
    printf '{\n'
    printf '  "cache_dir": "%s",\n' "$CACHE_DIR"
    printf '  "retention": %s,\n' "$RETENTION"
    printf '  "pruned": %s,\n' "$([[ "$PRUNE" == true ]] && echo true || echo false)"
    printf '  "total_prunable": %s,\n' "$TOTAL_PRUNABLE"
    printf '  "plugins": [\n'
    for i in "${!J_PLUGIN[@]}"; do
        sep=","; [[ $i -eq $((${#J_PLUGIN[@]} - 1)) ]] && sep=""
        kept_json=$(python3 -c "import json,sys; print(json.dumps([x for x in sys.argv[1].split(',') if x]))" "${J_KEPT[$i]}")
        prun_json=$(python3 -c "import json,sys; print(json.dumps([x for x in sys.argv[1].split(',') if x]))" "${J_PRUNABLE[$i]}")
        printf '    {"plugin": "%s", "kept": %s, "prunable": %s}%s\n' "${J_PLUGIN[$i]}" "$kept_json" "$prun_json" "$sep"
    done
    printf '  ]\n'
    printf '}\n'
else
    echo ""
    if [[ $TOTAL_PRUNABLE -eq 0 ]]; then
        echo -e "${GREEN}Nothing to prune${NC} — every plugin is within retention."
    elif [[ "$PRUNE" == true ]]; then
        echo -e "${GREEN}Pruned ${TOTAL_FREED} old version dir(s).${NC}"
    else
        echo -e "${YELLOW}${TOTAL_PRUNABLE} prunable version dir(s).${NC} Re-run with ${CYAN}--prune${NC} to remove."
    fi
fi

exit 0
