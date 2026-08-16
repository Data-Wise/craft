#!/usr/bin/env bash
# scripts/docs-staleness-check.sh - Documentation staleness detection (Phases 6-9)
#
# Detects stale counts, missing nav entries, undocumented skills/agents,
# and cross-doc freshness issues. Integrates as Step 2d in release pipeline.
#
# Usage:
#   ./scripts/docs-staleness-check.sh                        # Dry-run report
#   ./scripts/docs-staleness-check.sh --fix                  # Auto-fix + interactive review
#   ./scripts/docs-staleness-check.sh --fix --non-interactive # Auto-fix only (CI mode)
#   ./scripts/docs-staleness-check.sh --json                 # JSON output
#   ./scripts/docs-staleness-check.sh --audit-exclusions     # Audit exclusion list
#
# Exit codes: 0 = GREEN, 1 = YELLOW/RED (issues found), 2 = usage error

set -uo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
# Resolve which repo to inspect. See the matching block in validate-counts.sh
# for the full rationale; order is:
#   1. $CRAFT_PLUGIN_DIR     — explicit override (craft-mcp sets the target repo)
#   2. the script's own repo — when this script sits inside a plugin repo, that
#                              repo is the subject. Preferring cwd here made a
#                              script invoked by absolute path against another
#                              tree silently inspect the caller's repo instead.
#   3. the caller's cwd      — packaged .mcpb, where bundled/ has no plugin.json
#   4. the script's parent   — last-resort fallback
if [[ -n "${CRAFT_PLUGIN_DIR:-}" && -f "${CRAFT_PLUGIN_DIR}/.claude-plugin/plugin.json" ]]; then
    PLUGIN_DIR="$CRAFT_PLUGIN_DIR"
elif [[ -f "$(dirname "$SCRIPT_DIR")/.claude-plugin/plugin.json" ]]; then
    PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
elif [[ -f "$(pwd)/.claude-plugin/plugin.json" ]]; then
    PLUGIN_DIR="$(pwd)"
else
    PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"
fi

source "$SCRIPT_DIR/formatting.sh"
RED="$FMT_RED"
GREEN="$FMT_GREEN"
YELLOW="$FMT_YELLOW"
CYAN="$FMT_CYAN"
NC="$FMT_NC"

# ---------------------------------------------------------------------------
# Argument parsing
# ---------------------------------------------------------------------------
FIX_MODE=false
NON_INTERACTIVE=false
JSON_MODE=false
AUDIT_EXCLUSIONS=false

while [[ $# -gt 0 ]]; do
    case "$1" in
        --fix)              FIX_MODE=true ;;
        --non-interactive)  NON_INTERACTIVE=true ;;
        --json)             JSON_MODE=true ;;
        --audit-exclusions) AUDIT_EXCLUSIONS=true ;;
        --help|-h)
            echo "Usage: $0 [--fix] [--non-interactive] [--json] [--audit-exclusions]"
            echo ""
            echo "  --fix              Auto-fix safe items, then interactive review"
            echo "  --non-interactive  Skip interactive review (CI mode, use with --fix)"
            echo "  --json             Output results as JSON"
            echo "  --audit-exclusions Audit exclusion list for stale entries"
            exit 0
            ;;
        *)
            echo -e "${RED}Error: unknown argument '$1'${NC}"
            echo "Run with --help for usage"
            exit 2
            ;;
    esac
    shift
done

cd "$PLUGIN_DIR"

# ---------------------------------------------------------------------------
# Exclusion config
# ---------------------------------------------------------------------------
EXCLUSIONS_FILE="$SCRIPT_DIR/config/exclusions.txt"

# Arrays for file exclusions and pattern exclusions
declare -a EXCLUDED_FILES=()
declare -a EXCLUDED_DIRS=()
declare -a EXCLUDED_PATTERNS=()  # "file:pattern" pairs

load_exclusions() {
    if [[ ! -f "$EXCLUSIONS_FILE" ]]; then
        return
    fi
    while IFS= read -r line; do
        # Skip comments and blank lines
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        # Trim whitespace
        line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -z "$line" ]] && continue

        if [[ "$line" == */ ]]; then
            # Directory exclusion (trailing slash)
            EXCLUDED_DIRS+=("$line")
        elif [[ "$line" == *:* ]]; then
            # Pattern exclusion (file:pattern)
            EXCLUDED_PATTERNS+=("$line")
        else
            # Whole-file exclusion
            EXCLUDED_FILES+=("$line")
        fi
    done < "$EXCLUSIONS_FILE"
}

# Check if a file is wholly excluded
is_file_excluded() {
    local file="$1"
    for excl in "${EXCLUDED_FILES[@]+"${EXCLUDED_FILES[@]}"}"; do
        [[ "$file" == "$excl" ]] && return 0
    done
    for dir in "${EXCLUDED_DIRS[@]+"${EXCLUDED_DIRS[@]}"}"; do
        [[ "$file" == "$dir"* ]] && return 0
    done
    return 1
}

# Check if a specific file:pattern match is excluded
is_pattern_excluded() {
    local file="$1"
    local pattern="$2"
    for excl in "${EXCLUDED_PATTERNS[@]+"${EXCLUDED_PATTERNS[@]}"}"; do
        local excl_file="${excl%%:*}"
        local excl_pattern="${excl#*:}"
        # Word-boundary match: excl_pattern must appear as a whole word/phrase in pattern
        # Prevents "97 commands" matching "197 commands" while allowing "18 skills" to match
        # inside a line like "**94 commands** · **18 skills** · **6 agents**"
        if [[ "$file" == "$excl_file" ]] && echo "$pattern" | grep -qE "(^|[^0-9])${excl_pattern}([^0-9]|$)"; then
            return 0
        fi
    done
    return 1
}

# ---------------------------------------------------------------------------
# Load authoritative counts
# ---------------------------------------------------------------------------
EXPECTED_CMDS=""
EXPECTED_SKILLS=""
EXPECTED_AGENTS=""
CURRENT_VERSION=""

# The CRAFT_EXPECTED_* overrides exist so the prose-staleness fixtures can declare
# their expected counts directly instead of materializing 48 command files and 41
# skill dirs per fixture case. Unset in every production path, so the derived
# values are what actually runs.
load_counts() {
    EXPECTED_CMDS="${CRAFT_EXPECTED_CMDS:-$(find commands -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')}"
    EXPECTED_SKILLS="${CRAFT_EXPECTED_SKILLS:-$(find skills -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')}"
    EXPECTED_AGENTS="${CRAFT_EXPECTED_AGENTS:-$(find agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')}"
    CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])")
}

# ---------------------------------------------------------------------------
# Prose staleness helpers (SPEC-doc-staleness-prose-gaps-2026-08-07)
# ---------------------------------------------------------------------------
# The boundary after a matched noun ("command", "agents", ...): whitespace,
# closing punctuation, or end of line. NOT `[^a-z]`, which also accepts `-` —
# that let "command-line" and "agent-facing" read as counts (F1), and let
# `[f]ix` then rewrite "30 command-line entry points" into
# "48 command-line entry points" (F2). One constant, shared by the awk
# pre-filter and the bash matcher below (and the strip in phase7 that trims it
# back off a matched span) — tuning them independently caused a 4x perf
# regression once already (see emit_shaped_lines' header note).
PROSE_COUNT_TRAILER='([])} .,;:!?*]|$)'

# emit_shaped_lines prints "file:lineno:shape:content" for lines sitting in one
# of four structured shapes. Free prose is deliberately NOT emitted: an
# adversarial review of a blanket "N agents" search found 90+ false positives
# across docs/ — orchestration mode-limit prose ("2 agents max"), a tutorial
# using an intentionally fictional plugin, and a troubleshooting page that
# prints a wrong count on purpose to teach the bug. Scoping to line shapes is
# what makes checking the singular noun form safe here.
#
# Takes the whole file list at once and makes ONE awk pass over it. The first
# build called awk per file: ~640 markdown files x 2 scans is ~1300 process
# spawns, which took this script from 8s to 36s and blew the 30s timeout in
# test_pre_release_check_runs. FILENAME/FNR give the same per-file output from a
# single invocation.
emit_shaped_lines() {
    [[ $# -eq 0 ]] && return 0
    awk -v trailer="$PROSE_COUNT_TRAILER" '
        # Only lines that actually carry a count are worth emitting. Without this
        # filter every line of every box block is emitted (~3500 across docs/),
        # and the bash loop downstream spends ~6 grep subprocesses on each — the
        # other half of the 4x slowdown, alongside per-file awk spawns.
        function hascount(s) {
            return s ~ ("[0-9]+ (specialized )?(commands?|skills?|agents?)" trailer)
        }

        FNR == 1 { inbox = 0 }

        # "version-box": a quick-reference/version box drawn with box characters.
        # An unclosed box (no matching bottom border, e.g. truncated by a
        # missing fence) used to leak `inbox` mode into the rest of the file,
        # so a later structure-table row got measured as a version-box line
        # instead and lost its own type restriction (F8). Closed on the FIRST
        # line carrying no box-drawing character at all, not only on an
        # explicit `└` -- that line falls through to the shape checks below
        # instead of being consumed as part of the box.
        /┌/ { inbox = 1 }
        inbox {
            if ($0 !~ /[┌┐└┘│├┤─]/) {
                inbox = 0
            } else {
                if (hascount($0)) print FILENAME ":" FNR ":version-box:" $0
                if ($0 ~ /└/) inbox = 0
                next
            }
        }

        # "tldr": a line that OPENS with TL;DR (after optional blockquote or
        # emphasis markers), not merely one that mentions it. A doc describing a
        # TL;DR bug is not itself making a TL;DR claim: the context table in
        # ADR-007 quotes the "8 specialized agents" line the ADR exists to
        # explain, and a contains-match flagged it the moment it was written.
        # (No apostrophes in this awk program -- it is single-quoted in bash.)
        /^[[:space:]]*[>*_[:space:]]*TL;DR/ {
            if (hascount($0)) print FILENAME ":" FNR ":tldr:" $0
            next
        }

        # "count-summary": the bolded badge line, e.g. **48 commands** | **41 skills**.
        /\*\*[0-9]+ (commands|skills|agents)\*\*/ { print FILENAME ":" FNR ":count-summary:" $0; next }

        # "structure-table": a table row whose first cell names a counted
        # directory. Added 2026-08-15 after CLAUDE.md claimed "8 agent
        # definitions" (singular) for five minors while the plural-only scan
        # below read GREEN over it.
        /^\|[[:space:]]*`(commands|skills|agents)\/`[[:space:]]*\|/ {
            if (hascount($0)) print FILENAME ":" FNR ":structure-table:" $0
            next
        }
    ' "$@" 2>/dev/null || true
}

# emit_release_date_claims prints "file:lineno:YYYY-MM-DD" for release-date
# claims within 4 lines of a mention of the current version token — e.g.
# NEWS.md's "## v4.5.0 ..." heading followed by "**Released:** 2026-08-08".
# Windowed so historical entries further down the same file are not compared
# against the current version's date.
#
# The window opens ONLY when the version token sits in a markdown heading or a
# version-box content line (D6/F3). Proximity alone is not enough: an upgrade
# guide saying "Upgrading to v4.5.0 is a drop-in change" is prose, not a claim
# site, and used to open the window anyway, collecting whatever date happened
# to sit within 4 lines of it as though it were this version's release date.
#
# Single awk pass over the whole file list, for the same reason as above.
emit_release_date_claims() {
    [[ $# -eq 0 ]] && return 0
    awk -v ver="v${CURRENT_VERSION}" '
        FNR == 1 { win = 0 }
        function is_heading(s)  { return s ~ /^#+[[:space:]]/ }
        function is_box_line(s) { return s ~ /^[[:space:]]*│/ }
        # 5, not 4: the win-- below runs on the version line itself, so win=4
        # scanned that line plus only 3 more -- one short of the 4 following
        # lines this check documents, silently missing a layout as ordinary as
        # heading / blank / Type / blank / Released.
        (is_heading($0) || is_box_line($0)) && index($0, ver) { win = 5 }
        win > 0 {
            if (match($0, /[Rr]eleased[^0-9]{0,12}[0-9]{4}-[0-9]{2}-[0-9]{2}/)) {
                s = substr($0, RSTART, RLENGTH)
                if (match(s, /[0-9]{4}-[0-9]{2}-[0-9]{2}/))
                    print FILENAME ":" FNR ":" substr(s, RSTART, RLENGTH)
            }
            win--
        }
    ' "$@" 2>/dev/null || true
}

# D1: check 1 has no external authority. The git tag doesn't exist at either
# point this check actually runs -- the release pipeline writes NEWS/REFCARD
# dates in Step 3b, *before* Step 8 creates the tag, and CI's checkout has no
# fetch-tags -- so a tag-based check only ever fired on a developer machine
# that had already pulled it, which is not a gate (F7). Instead, every
# release-date claim for the current version is compared against every other
# one; the one-day tolerance survives as the agreement window between claims,
# absorbing the UTC-boundary case that motivated it (v4.5.0: NEWS.md says
# 2026-08-08, REFCARD.md says 2026-08-07 -- both are correct).
#
# Given N date strings, returns the one with the most occurrences. Ties break
# to the LATER date, not the earlier one: a stale-release-date bug is a
# forgotten update, so the wrong claim is normally older than the correct one,
# never newer. (With exactly two claims -- the common case, one NEWS.md entry
# and one REFCARD.md box -- every tie is 1-1, so this tie-break is what
# decides which claim is "authority" and which is "stale".) Plain nested
# loop, not an associative array -- this script supports bash 3.2.
majority_date() {
    local best="" best_count=0 d1 d2 count
    for d1 in "$@"; do
        count=0
        for d2 in "$@"; do
            [[ "$d2" == "$d1" ]] && count=$((count + 1))
        done
        if (( count > best_count )) || { (( count == best_count )) && [[ -n "$best" ]] && [[ "$d1" > "$best" ]]; }; then
            best="$d1"
            best_count="$count"
        fi
    done
    echo "$best"
}

# Applies one `s/PATTERN/REPLACEMENT/flags` substitution to one line of one file.
# Echoes "true" only when the file actually changed, "false" otherwise —
# including when fix_detail is not a substitution at all (Phase 8's doc-coverage
# findings carry a `doc-coverage:surface:cmd` marker instead).
#
# Uses python3 rather than `sed -i`: the patterns built in count_consistency use
# `\b` word boundaries, which GNU sed honors but BSD sed (macOS default) treats
# as a literal `b`. sed also exits 0 when nothing matched, so the script once
# reported "Fixed: N items" while no file was modified — a silent no-op on every
# macOS run. Shared by pass 1 and pass 2 so the two cannot drift apart again.
apply_line_fix() {
    python3 - "$1" "$2" "$3" <<'PYEOF' 2>/dev/null || echo "false"
import re, sys

file_path, lineno_str, sed_cmd = sys.argv[1], sys.argv[2], sys.argv[3]
# sed_cmd looks like: s/PATTERN/REPLACEMENT/g
# The delimiter is `/` — we never construct anything else.
if not sed_cmd.startswith("s/"):
    print("false")
    sys.exit(0)
parts = sed_cmd[2:].rsplit("/", 2)
if len(parts) != 3:
    print("false")
    sys.exit(0)
pattern, replacement, flags = parts
try:
    with open(file_path, encoding="utf-8") as f:
        lines = f.readlines()
except OSError:
    print("false")
    sys.exit(0)

idx = int(lineno_str) - 1
if idx < 0 or idx >= len(lines):
    print("false")
    sys.exit(0)
old = lines[idx]
try:
    new = re.sub(pattern, replacement, old)
except re.error:
    print("false")
    sys.exit(0)
if new == old:
    print("false")
    sys.exit(0)
lines[idx] = new
with open(file_path, "w", encoding="utf-8") as f:
    f.writelines(lines)
print("true")
PYEOF
}

# The acceptable window is three literal dates (authority-1, authority,
# authority+1), computed ONCE with a single python3 call rather than a python3
# spawn per claim. Callers then do a plain string comparison. python3 is
# already a hard dependency here (load_counts reads plugin.json with it) — no
# new dependency.
ACCEPTED_RELEASE_DATES=""
compute_release_date_window() {
    local authority_date="$1"
    ACCEPTED_RELEASE_DATES=$(python3 -c "
import sys, datetime
try:
    d = datetime.date.fromisoformat(sys.argv[1])
except ValueError:
    sys.exit(0)
print(' '.join(str(d + datetime.timedelta(days=n)) for n in (-1, 0, 1)))
" "$authority_date" 2>/dev/null)
}
release_date_accepted() {
    case " ${ACCEPTED_RELEASE_DATES} " in
        *" $1 "*) return 0 ;;
    esac
    return 1
}

# Dedup ledger shared by the broad count scan and the line-shape scan, so a
# stale count sitting inside a structured shape is reported once, not twice.
# A plain string, not an associative array — this script supports bash 3.2.
REPORTED_COUNT_KEYS=""
count_key_reported() {
    case "$REPORTED_COUNT_KEYS" in
        *"|$1|"*) return 0 ;;
    esac
    return 1
}
mark_count_key() {
    REPORTED_COUNT_KEYS="${REPORTED_COUNT_KEYS}|$1|"
}

# ---------------------------------------------------------------------------
# Result tracking
# ---------------------------------------------------------------------------
declare -a PHASE6_FINDINGS=()
declare -a PHASE7_FINDINGS=()
declare -a PHASE8_FINDINGS=()
declare -a PHASE9_FINDINGS=()

# Fixable items for pass 1 (auto-fix)
declare -a FIXABLE_ITEMS=()
# Uncertain items for pass 2 (interactive)
declare -a UNCERTAIN_ITEMS=()

TOTAL_WARNINGS=0
TOTAL_ERRORS=0
TOTAL_FIXED=0

# Renders a finding's location the way every consumer has always seen it —
# `path:lineno`, or the bare path when there is no locator. The split above is
# internal; this keeps the JSON contract unchanged.
finding_location() {
    local file="$1" locator="$2"
    if [[ -n "$locator" ]]; then
        echo "${file}:${locator}"
    else
        echo "$file"
    fi
}

# The finding record carries the file path and the location *within* it as two
# fields, never one glued string. They were glued (`path:lineno`) until
# 2026-08-15, which made pass 2's `[e]xclude` a silent no-op for every Phase 7
# and Phase 9 finding: `is_pattern_excluded` splits the exclusion entry on its
# first colon, so an entry of `docs/x.md:3:30 command` could never match. It
# printed "Excluded" and the finding returned on the next run.
#
# `locator` is a location, not necessarily a line number: Phase 9's
# site_description finding carries `site_description`, and coverage findings
# carry none at all. Nothing may assume it is numeric — pass 1 gets its line
# number from fix_detail, which is a separate payload.
add_finding() {
    local phase="$1"
    local severity="$2"  # error | warning
    local file="$3"
    local locator="$4"   # line number, named locator, or "" — never glued into file
    local message="$5"
    local fixable="${6:-false}"  # true if auto-fixable
    local fix_detail="${7:-}"    # sed command or description

    local entry="${severity}|${file}|${locator}|${message}|${fixable}|${fix_detail}"

    case "$phase" in
        6) PHASE6_FINDINGS+=("$entry") ;;
        7) PHASE7_FINDINGS+=("$entry") ;;
        8) PHASE8_FINDINGS+=("$entry") ;;
        9) PHASE9_FINDINGS+=("$entry") ;;
    esac

    if [[ "$severity" == "error" ]]; then
        TOTAL_ERRORS=$((TOTAL_ERRORS + 1))
    else
        TOTAL_WARNINGS=$((TOTAL_WARNINGS + 1))
    fi

    if [[ "$fixable" == "true" ]]; then
        FIXABLE_ITEMS+=("${phase}|${entry}")
    elif [[ "$fixable" == "uncertain" ]]; then
        UNCERTAIN_ITEMS+=("${phase}|${entry}")
    fi
}

# ---------------------------------------------------------------------------
# Phase 6: Nav Completeness
# ---------------------------------------------------------------------------
phase6_nav_completeness() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 6: Nav Completeness ............ "
    fi

    local issues=0

    # Extract all .md paths from mkdocs.yml nav section only
    # Only match file paths (after ": " in nav entries), not label text
    local nav_files
    nav_files=$(sed -n '/^nav:/,$ p' mkdocs.yml \
        | grep -E ':\s*[a-zA-Z0-9/_.-]+\.md' \
        | sed 's/.*:[[:space:]]*//' \
        | sed 's/[[:space:]]*$//' \
        | sort -u)

    # Extract exclude_docs patterns from mkdocs.yml
    local exclude_patterns=()
    local in_exclude=false
    while IFS= read -r line; do
        if [[ "$line" =~ ^exclude_docs: ]]; then
            in_exclude=true
            continue
        fi
        if $in_exclude; then
            # Stop at next top-level key (no leading whitespace)
            if [[ "$line" =~ ^[a-z] && ! "$line" =~ ^[[:space:]] ]]; then
                break
            fi
            # Extract patterns (strip leading whitespace, comments, and quotes)
            local pattern
            pattern=$(echo "$line" | sed 's/^[[:space:]]*//;s/#.*//;s/[[:space:]]*$//')
            if [[ -n "$pattern" && "$pattern" != "|" ]]; then
                exclude_patterns+=("$pattern")
            fi
        fi
    done < mkdocs.yml

    # Find all docs files on disk
    while IFS= read -r file; do
        # Convert to relative path from docs/ (what mkdocs nav uses)
        local rel_path="${file#docs/}"

        # Skip excluded dirs/files from our config
        if is_file_excluded "$file"; then
            continue
        fi

        # Skip mkdocs exclude_docs patterns
        local mkdocs_excluded=false
        for pat in "${exclude_patterns[@]+"${exclude_patterns[@]}"}"; do
            # Simple glob match: pattern matches if file path contains it
            if [[ "$rel_path" == $pat* || "$rel_path" == *"$pat"* || "/$rel_path" == *"$pat"* ]]; then
                mkdocs_excluded=true
                break
            fi
        done
        $mkdocs_excluded && continue

        # Check if this file appears in nav
        if ! echo "$nav_files" | grep -qF "$rel_path"; then
            add_finding 6 "warning" "$file" "" "Not in mkdocs.yml nav"
            issues=$((issues + 1))
        fi
    done < <(find docs -name "*.md" -not -path "*/\.*" 2>/dev/null | sort)

    # Check for nav entries pointing to missing files
    while IFS= read -r nav_entry; do
        if [[ ! -f "docs/$nav_entry" ]]; then
            add_finding 6 "error" "mkdocs.yml" "" "Nav entry 'docs/$nav_entry' — file missing"
            issues=$((issues + 1))
        fi
    done < <(echo "$nav_files")

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Phase 7: Count Consistency
# ---------------------------------------------------------------------------
phase7_count_consistency() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 7: Count Consistency ........... "
    fi

    local issues=0

    # Scan docs for count patterns
    # Minimum thresholds: only match counts likely to be "total" references
    # (small numbers like "7 commands" in prose are not total counts)
    local count_types=("commands" "skills" "agents")
    local expected_values=("$EXPECTED_CMDS" "$EXPECTED_SKILLS" "$EXPECTED_AGENTS")
    # Minimum count to consider: ~40% of expected value (catches old totals,
    # skips prose), floored at 2. Agents' 40% is `2 * 40 / 100 == 0`, so
    # without the floor the guard this comment and ADR-007 describe does not
    # exist for the smallest count type — every "N agent(s)" mention, however
    # small, read as a stale-total candidate (F6).
    local min_thresholds=()
    for exp in "${expected_values[@]}"; do
        local floor=$((exp * 40 / 100))
        (( floor < 2 )) && floor=2
        min_thresholds+=("$floor")
    done

    for i in "${!count_types[@]}"; do
        local ctype="${count_types[$i]}"
        local expected="${expected_values[$i]}"
        local min_count="${min_thresholds[$i]}"

        # grep for "N commands/skills/agents" patterns in docs. One regex for
        # detection AND the fix anchor -- same reasoning as check 2's span-
        # anchored fix (D3): the trailing `\b` this scan used before accepted
        # `-` as a boundary the same way check 2's did, so "7 agents-only"
        # read as "7 agents" (expected 2). This scan's findings are
        # auto-fixable, unlike check 2's, so a boundary-unsafe substitution
        # here is worse than F2 -- it can silently corrupt a doc under
        # `--fix --non-interactive` with no human in the loop. PROSE_COUNT_TRAILER
        # is the same boundary class the shape-scoped check uses.
        while IFS= read -r match; do
            [[ -z "$match" ]] && continue
            local file="${match%%:*}"
            local rest="${match#*:}"
            local lineno="${rest%%:*}"
            local content="${rest#*:}"

            # Skip excluded files
            is_file_excluded "$file" && continue

            local full noun
            full=$(echo "$content" \
                | grep -oE "[0-9]+ ${ctype}${PROSE_COUNT_TRAILER}" | head -1)
            [[ -z "$full" ]] && continue
            local found_count
            found_count=$(echo "$full" | grep -oE '^[0-9]+')

            # Skip if count matches
            [[ "$found_count" == "$expected" ]] && continue

            # Skip counts below threshold (not total-count references)
            [[ "$found_count" -lt "$min_count" ]] && continue

            # Check pattern exclusions
            if is_pattern_excluded "$file" "${found_count} ${ctype}"; then
                continue
            fi

            # Already reported by the line-shape scan below? Report once.
            count_key_reported "${file}:${lineno}:${ctype}" && continue

            # Trim the trailing boundary char the trailer group consumed, so
            # the fix substitutes the exact matched text ("48 commands"), not
            # a re-derived \b-bounded pattern that could match elsewhere.
            noun=$(echo "$full" | sed -E 's/[])} .,;:!?*]$//')

            # Determine if auto-fixable (simple count swap)
            local fixable="true"
            local fix_detail="${file}:${lineno}:s/${noun}/${expected} ${ctype}/"

            add_finding 7 "warning" "$file" "$lineno" \
                "'${found_count} ${ctype}' (expected ${expected})" \
                "$fixable" "$fix_detail"
            mark_count_key "${file}:${lineno}:${ctype}"
            issues=$((issues + 1))
        done < <(grep -rnE "\b[0-9]+ ${ctype}${PROSE_COUNT_TRAILER}" docs/ CLAUDE.md README.md --include="*.md" 2>/dev/null || true)
    done

    # -----------------------------------------------------------------------
    # Check 2 — count prose inside structured line shapes, singular included.
    # The scan above is plural-only and unscoped; this one is shape-scoped and
    # therefore safe to run against the singular form too. Ordering matters:
    # the broad scan marks its keys first, so a line both scans can see is
    # reported by whichever reaches it first and skipped by the other.
    # -----------------------------------------------------------------------
    # Build the scannable file list once, then hand it to each scan in a single
    # awk invocation (see emit_shaped_lines' header note on why per-file awk
    # calls were a 4x slowdown).
    local prose_file shaped sfile srest slineno shape scontent singular found j
    local -a prose_files=()
    while IFS= read -r prose_file; do
        [[ -z "$prose_file" ]] && continue
        [[ -f "$prose_file" ]] || continue
        is_file_excluded "$prose_file" && continue
        prose_files+=("$prose_file")
    done < <(printf '%s\n' CLAUDE.md README.md; find docs -name '*.md' 2>/dev/null || true)

    while IFS= read -r shaped; do
            [[ -z "$shaped" ]] && continue
            sfile="${shaped%%:*}"; srest="${shaped#*:}"
            slineno="${srest%%:*}"; srest="${srest#*:}"
            shape="${srest%%:*}"; scontent="${srest#*:}"

            for j in "${!count_types[@]}"; do
                local ctype2="${count_types[$j]}"
                local expected2="${expected_values[$j]}"
                local min2="${min_thresholds[$j]}"
                singular="${ctype2%s}"

                # A structure-table row names its own type in the first cell, so
                # only compare against that type — a `commands/` row must not be
                # measured against the agent count.
                if [[ "$shape" == "structure-table" ]]; then
                    echo "$scontent" | grep -qE "^\|[[:space:]]*\`${ctype2}/\`" || continue
                fi

                # One regex for detection AND the fix anchor. F2 was a second,
                # looser regex used only to build `noun` (no trailer at all) —
                # it re-matched "command" inside "command-line" even after the
                # detection regex's own trailer would have rejected the line,
                # so [f]ix rewrote "30 command-line entry points" into
                # "48 command-line entry points". Capturing one span and
                # deriving both the report and the substitution from it makes
                # that drift impossible.
                local full
                full=$(echo "$scontent" \
                    | grep -oE "[0-9]+ (specialized )?(${ctype2}|${singular})${PROSE_COUNT_TRAILER}" \
                    | head -1)
                [[ -z "$full" ]] && continue
                found=$(echo "$full" | grep -oE '^[0-9]+')
                [[ "$found" == "$expected2" ]] && continue

                # Same 40%-of-expected floor the broad scan applies. Structured
                # shapes still carry non-total counts: category subtotals inside
                # a reference box ("SMART (4 commands)"), a bolded subset count
                # ("`--refine` is declared on **9 commands**"), and narrative
                # counts about other plugins ("kept shipping **0 skills**").
                # Without this floor all three read as stale totals.
                [[ "$found" -lt "$min2" ]] && continue

                count_key_reported "${sfile}:${slineno}:${ctype2}" && continue
                is_pattern_excluded "$sfile" "${found} ${ctype2}" && continue
                is_pattern_excluded "$sfile" "${found} ${singular}" && continue

                # Trim the single trailing boundary char the trailer group
                # consumed (space/closing punctuation) back off, so the
                # reported/substituted noun is "8 agent", not "8 agent ". `$`
                # in the trailer consumes nothing, so an end-of-line match is
                # already bare and this is a no-op for it.
                local noun
                noun=$(echo "$full" | sed -E 's/[])} .,;:!?*]$//')

                # Not auto-fixable: the surrounding prose ("8 agent definitions")
                # is hand-authored, so a blind count swap can produce grammatical
                # nonsense. Routed to the interactive pass instead.
                #
                # Routed to pass 2 (uncertain), not pass 1: the surrounding
                # prose is hand-authored, so a human should see the line before
                # the number changes under it. The fix_detail is still a real
                # substitution so that confirming it actually edits the file —
                # it swaps only the digits, leaving "agent definitions" intact.
                add_finding 7 "warning" "$sfile" "$slineno" \
                    "prose[${shape}]: '${noun}' (expected ${expected2})" \
                    "uncertain" "${sfile}:${slineno}:s/${noun}/${expected2}${noun#"$found"}/"
                mark_count_key "${sfile}:${slineno}:${ctype2}"
                issues=$((issues + 1))
            done
    done < <(emit_shaped_lines "${prose_files[@]+"${prose_files[@]}"}")

    # -----------------------------------------------------------------------
    # Check 1 — release-date claims agree with each other for the current
    # version. No external authority (D1): the tag doesn't exist at either
    # point this check runs (see the comment on majority_date). Vacuous
    # (skipped, not failed) with 0 or 1 claims -- there is nothing to compare
    # a lone claim against, which is the normal state on a feature branch
    # before release, or when only one doc in the repo names a release date at
    # all. Accepted cost: a date that is uniformly wrong in every file agrees
    # with itself and is never caught.
    # -----------------------------------------------------------------------
    local claim cfile crest clineno cdate
    local -a claim_files=() claim_lines=() claim_dates=()
    while IFS= read -r claim; do
        [[ -z "$claim" ]] && continue
        cfile="${claim%%:*}"; crest="${claim#*:}"
        clineno="${crest%%:*}"; cdate="${crest#*:}"
        is_file_excluded "$cfile" && continue
        claim_files+=("$cfile")
        claim_lines+=("$clineno")
        claim_dates+=("$cdate")
    done < <(emit_release_date_claims "${prose_files[@]+"${prose_files[@]}"}")

    if [[ "${#claim_dates[@]}" -ge 2 ]]; then
        local authority
        authority="$(majority_date "${claim_dates[@]}")"
        compute_release_date_window "$authority"
        # Empty window means the majority date itself failed to parse --
        # cannot happen in practice (it came from the [0-9]{4}-[0-9]{2}-[0-9]{2}
        # regex that fed emit_release_date_claims), but a broken authority must
        # make this vacuous, never universal, same posture as the old
        # missing-tag case: an empty accept-window would otherwise fail every
        # claim in the repo at once.
        if [[ -n "$ACCEPTED_RELEASE_DATES" ]]; then
            for i in "${!claim_dates[@]}"; do
                cdate="${claim_dates[$i]}"
                release_date_accepted "$cdate" && continue
                cfile="${claim_files[$i]}"; clineno="${claim_lines[$i]}"
                is_pattern_excluded "$cfile" "$cdate" && continue

                # error (D2, promoted per D11): shipped as "warning" while
                # the redesign (D1, D6) itself was unproven -- a passing
                # unit suite written by the same author in the same sitting
                # isn't evidence. Promoted once a live-repo run came back
                # clean (0 findings) across every tracked doc AND both real
                # claim sites (docs/NEWS.md, docs/REFCARD.md), plus a
                # transcript of the check actually firing: injecting
                # 2020-01-01 into docs/REFCARD.md:7 produced "release date
                # '2020-01-01' for v4.5.0 disagrees with other claims
                # (majority: 2026-08-07)", reverted after confirming.
                add_finding 7 "error" "$cfile" "$clineno" \
                    "release date '${cdate}' for v${CURRENT_VERSION} disagrees with other claims (majority: ${authority})" \
                    "uncertain" "${cfile}:${clineno}:s/${cdate}/${authority}/"
                issues=$((issues + 1))
            done
        fi
    fi

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Phase 8: Skill/Agent Coverage
# ---------------------------------------------------------------------------
phase8_skill_agent_coverage() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 8: Skill/Agent/Cmd Coverage .... "
    fi

    local issues=0

    # --- Commands coverage ---
    # Check that each command file appears in EITHER:
    #   1. docs/commands.md (A-Z reference)
    #   2. docs/commands/ help pages (category pages + individual)
    #   3. docs/commands/overview.md (overview page)
    # A command is "documented" if its name appears in any of these locations.
    local commands_az="docs/commands.md"
    local commands_dir="docs/commands"
    local commands_overview="docs/commands/overview.md"
    while IFS= read -r cmd_file; do
        [[ -z "$cmd_file" ]] && continue
        # Derive the craft command name from path:
        #   commands/docs/check.md -> docs:check -> /craft:docs:check
        #   commands/do.md -> do -> /craft:do
        local rel="${cmd_file#commands/}"
        rel="${rel%.md}"
        local cmd_name
        cmd_name=$(echo "$rel" | tr '/' ':')

        # Check across all command documentation locations
        local documented=false

        # Check A-Z reference
        if [[ -f "$commands_az" ]] && grep -qF "$cmd_name" "$commands_az" 2>/dev/null; then
            documented=true
        fi

        # Check docs/commands/ help pages (category + individual)
        if ! $documented && [[ -d "$commands_dir" ]]; then
            if grep -rqF "$cmd_name" "$commands_dir" --include="*.md" 2>/dev/null; then
                documented=true
            fi
        fi

        if ! $documented; then
            add_finding 8 "warning" "$cmd_file" "" \
                "Command '${cmd_name}' not in docs (commands.md, docs/commands/)" \
                "uncertain" "command:${cmd_file}"
            issues=$((issues + 1))
        fi
    done < <(find commands -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | sort)

    # --- Skills coverage ---
    local skills_doc="docs/skills-agents.md"

    if [[ -f "$skills_doc" ]]; then
        while IFS= read -r skill_file; do
            [[ -z "$skill_file" ]] && continue
            local skill_name
            skill_name=$(basename "$(dirname "$skill_file")")/$(basename "$skill_file" .md)
            # Check for skill reference in both docs
            if ! grep -q "$skill_file\|$skill_name" "$skills_doc" 2>/dev/null; then
                local desc=""
                # Try to extract description from frontmatter
                if [[ -f "$skill_file" ]]; then
                    desc=$(sed -n '/^---$/,/^---$/{ /^description:/s/^description:[[:space:]]*//p; }' "$skill_file" 2>/dev/null | head -1)
                fi
                add_finding 8 "warning" "$skill_file" "" \
                    "Not documented in $skills_doc" \
                    "uncertain" "skill:${skill_file}:${desc}"
                issues=$((issues + 1))
            fi
        done < <(find skills -name "*.md" -not -path "*/references/*" 2>/dev/null | sort)
    fi

    # --- Agents coverage ---
    if [[ -f "$skills_doc" ]]; then
        while IFS= read -r agent_file; do
            [[ -z "$agent_file" ]] && continue
            local agent_name
            agent_name=$(basename "$(dirname "$agent_file")")/$(basename "$agent_file" .md)
            if ! grep -q "$agent_file\|$agent_name" "$skills_doc" 2>/dev/null; then
                add_finding 8 "warning" "$agent_file" "" \
                    "Not documented in $skills_doc" \
                    "uncertain" "agent:${agent_file}"
                issues=$((issues + 1))
            fi
        done < <(find agents -name "*.md" 2>/dev/null | sort)
    fi

    # --- Doc surface coverage (REFCARD + nav) ---
    # Delegate to doc-coverage-check.sh for structured findings
    local cov_script="${SCRIPT_DIR}/doc-coverage-check.sh"
    if [[ -x "$cov_script" ]]; then
        local cov_json
        cov_json=$(bash "$cov_script" --json 2>/dev/null || true)
        # Parse each finding from JSON and add_finding
        while IFS= read -r line; do
            [[ -z "$line" ]] && continue
            local cmd surface severity_raw message
            cmd=$(echo "$line" | sed 's/.*"cmd":"\([^"]*\)".*/\1/')
            surface=$(echo "$line" | sed 's/.*"surface":"\([^"]*\)".*/\1/')
            severity_raw=$(echo "$line" | sed 's/.*"severity":"\([^"]*\)".*/\1/')
            message=$(echo "$line" | sed 's/.*"message":"\([^"]*\)".*/\1/')
            # Map block→error, warn→warning for staleness check convention
            local sev="warning"
            [[ "$severity_raw" == "block" ]] && sev="error"
            add_finding 8 "$sev" "commands/${cmd//:///}.md" "" \
                "$message" "uncertain" "doc-coverage:${surface}:${cmd}"
            issues=$((issues + 1))
        done < <(echo "$cov_json" | grep '"cmd"' || true)
    fi

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Phase 9: Cross-Doc Freshness
# ---------------------------------------------------------------------------
phase9_cross_doc_freshness() {
    if [[ "$JSON_MODE" != "true" ]]; then
        echo -ne "  Phase 9: Cross-Doc Freshness ......... "
    fi

    local issues=0

    # Check REFCARD version references
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        is_file_excluded "$file" && continue

        while IFS= read -r match; do
            [[ -z "$match" ]] && continue
            local lineno="${match%%:*}"
            local content="${match#*:}"

            # Extract version from content
            local found_ver
            found_ver=$(echo "$content" | grep -oE 'v?[0-9]+\.[0-9]+\.[0-9]+' | head -1)
            [[ -z "$found_ver" ]] && continue
            # Strip leading 'v'
            found_ver="${found_ver#v}"

            if [[ "$found_ver" != "$CURRENT_VERSION" ]]; then
                local fixable="true"
                local fix_detail="${file}:${lineno}:s/${found_ver}/${CURRENT_VERSION}/g"
                add_finding 9 "warning" "$file" "$lineno" \
                    "Version '${found_ver}' (current: ${CURRENT_VERSION})" \
                    "$fixable" "$fix_detail"
                issues=$((issues + 1))
            fi
        done < <(grep -nE '\*\*Version\*\*:?\s*v?[0-9]+\.[0-9]+\.[0-9]+|^Version:\s*v?[0-9]+\.[0-9]+\.[0-9]+' "$file" 2>/dev/null || true)
    done < <(find docs/reference -name "REFCARD*.md" 2>/dev/null | sort)

    # Check site_description vs CHANGELOG
    local site_desc
    site_desc=$(grep '^site_description:' mkdocs.yml 2>/dev/null | head -1 | sed 's/^site_description:[[:space:]]*//')
    if [[ -n "$site_desc" ]]; then
        # Extract version from site_description
        local site_ver
        site_ver=$(echo "$site_desc" | grep -oE 'v[0-9]+\.[0-9]+\.[0-9]+' | head -1)
        if [[ -n "$site_ver" ]]; then
            site_ver="${site_ver#v}"
            if [[ "$site_ver" != "$CURRENT_VERSION" ]]; then
                add_finding 9 "warning" "mkdocs.yml" "site_description" \
                    "References v${site_ver} (current: v${CURRENT_VERSION})" \
                    "uncertain" ""
                issues=$((issues + 1))
            fi
        fi
    fi

    # Check "See Also" sections for stale counts
    while IFS= read -r match; do
        [[ -z "$match" ]] && continue
        local file="${match%%:*}"
        is_file_excluded "$file" && continue

        local rest="${match#*:}"
        local lineno="${rest%%:*}"
        local content="${rest#*:}"

        # Check skill/agent counts in "See Also" or summary lines
        local see_skills see_agents
        see_skills=$(echo "$content" | grep -oE '[0-9]+ skills' | head -1 | grep -oE '[0-9]+')
        see_agents=$(echo "$content" | grep -oE '[0-9]+ agents' | head -1 | grep -oE '[0-9]+')

        local stale=false
        if [[ -n "$see_skills" && "$see_skills" != "$EXPECTED_SKILLS" ]]; then
            stale=true
        fi
        if [[ -n "$see_agents" && "$see_agents" != "$EXPECTED_AGENTS" ]]; then
            stale=true
        fi

        if $stale; then
            is_pattern_excluded "$file" "$content" && continue
            add_finding 9 "warning" "$file" "$lineno" \
                "Stale counts in summary (skills: ${see_skills:-?}/${EXPECTED_SKILLS}, agents: ${see_agents:-?}/${EXPECTED_AGENTS})" \
                "uncertain" ""
            issues=$((issues + 1))
        fi
    done < <(grep -rnE '[0-9]+ skills.*[0-9]+ agents|[0-9]+ agents.*[0-9]+ skills' docs/ --include="*.md" 2>/dev/null || true)

    # Architecture docs: flag stale metrics as warnings
    while IFS= read -r file; do
        [[ -z "$file" ]] && continue
        is_file_excluded "$file" && continue
        while IFS= read -r match; do
            [[ -z "$match" ]] && continue
            local lineno="${match%%:*}"
            local content="${match#*:}"
            local found_count
            found_count=$(echo "$content" | grep -oE '[0-9]+ commands' | head -1 | grep -oE '[0-9]+')
            [[ -z "$found_count" ]] && continue
            [[ "$found_count" == "$EXPECTED_CMDS" ]] && continue
            is_pattern_excluded "$file" "${found_count} commands" && continue
            add_finding 9 "warning" "$file" "$lineno" \
                "Architecture doc: '${found_count} commands' (current: ${EXPECTED_CMDS})" \
                "uncertain" ""
            issues=$((issues + 1))
        done < <(grep -nE '\b[0-9]+ commands\b' "$file" 2>/dev/null || true)
    done < <(find docs/architecture -name "*.md" 2>/dev/null | sort)

    print_phase_status "$issues"
}

# ---------------------------------------------------------------------------
# Pass 1: Auto-fix (non-interactive)
# ---------------------------------------------------------------------------
pass1_auto_fix() {
    if [[ ${#FIXABLE_ITEMS[@]} -eq 0 ]]; then
        if [[ "$JSON_MODE" != "true" ]]; then
            echo ""
            echo "  No auto-fixable items found."
        fi
        return
    fi

    if [[ "$JSON_MODE" != "true" ]]; then
        echo ""
        echo -e "${CYAN}=== Pass 1: Auto-fix ===${NC}"
    fi

    for item in "${FIXABLE_ITEMS[@]}"; do
        # Parse: phase|severity|file|locator|message|fixable|fix_detail
        # fix_detail is a separate payload (path:lineno:sed_cmd), not derived
        # from the record's own file/locator fields.
        local fix_detail="${item##*|}"
        local file="${fix_detail%%:*}"
        local rest="${fix_detail#*:}"
        local lineno="${rest%%:*}"
        local sed_cmd="${rest#*:}"

        if [[ -f "$file" ]]; then
            local fixed_one=false
            fixed_one="$(apply_line_fix "$file" "$lineno" "$sed_cmd")"
            if [[ "$fixed_one" == "true" ]]; then
                TOTAL_FIXED=$((TOTAL_FIXED + 1))
                if [[ "$JSON_MODE" != "true" ]]; then
                    echo -e "  ${GREEN}Fixed:${NC} ${file}:${lineno}"
                fi
            fi
        fi
    done

    if [[ "$JSON_MODE" != "true" ]]; then
        echo "  Auto-fixed: ${TOTAL_FIXED} items"
    fi
}

# ---------------------------------------------------------------------------
# Pass 2: Interactive review
# ---------------------------------------------------------------------------
pass2_interactive_review() {
    if [[ ${#UNCERTAIN_ITEMS[@]} -eq 0 ]]; then
        return
    fi

    if $NON_INTERACTIVE; then
        if [[ "$JSON_MODE" != "true" ]]; then
            echo ""
            echo "  ${#UNCERTAIN_ITEMS[@]} items need review (skipped: --non-interactive)"
        fi
        return
    fi

    # Check if we have a TTY
    if [[ ! -t 0 ]]; then
        if [[ "$JSON_MODE" != "true" ]]; then
            echo ""
            echo "  ${#UNCERTAIN_ITEMS[@]} items need review (skipped: no TTY)"
        fi
        return
    fi

    echo ""
    echo -e "${CYAN}=== Pass 2: Review remaining (${#UNCERTAIN_ITEMS[@]} items) ===${NC}"
    echo ""

    local idx=0
    for item in "${UNCERTAIN_ITEMS[@]}"; do
        idx=$((idx + 1))
        # Parse: phase|severity|file|locator|message|fixable|fix_detail
        IFS='|' read -r phase severity file locator message fixable fix_detail <<< "$item"
        local location
        location="$(finding_location "$file" "$locator")"

        echo -e "[${idx}/${#UNCERTAIN_ITEMS[@]}] ${YELLOW}${location}${NC}"
        echo "  ${message}"

        local response=""
        while [[ "$response" != "f" && "$response" != "s" && "$response" != "e" ]]; do
            echo -n "  [f]ix  [s]kip  [e]xclude permanently: "
            read -r response
        done

        case "$response" in
            f)
                # Actually apply it. This branch used to print "Fixed" and bump
                # TOTAL_FIXED without touching the file — the same
                # reports-success-changes-nothing bug pass 1 was fixed for
                # earlier, left behind in pass 2. Both now share apply_line_fix.
                local target_file="${fix_detail%%:*}"
                local fix_rest="${fix_detail#*:}"
                local target_line="${fix_rest%%:*}"
                local fix_cmd="${fix_rest#*:}"
                local applied="false"
                if [[ -n "$fix_detail" && -f "$target_file" ]]; then
                    applied="$(apply_line_fix "$target_file" "$target_line" "$fix_cmd")"
                fi
                if [[ "$applied" == "true" ]]; then
                    echo -e "  -> ${GREEN}Fixed${NC} ${target_file}:${target_line}"
                    TOTAL_FIXED=$((TOTAL_FIXED + 1))
                else
                    echo "  -> Cannot auto-fix (manual edit needed)"
                fi
                ;;
            s)
                echo "  -> Skipped"
                ;;
            e)
                # Add to exclusions file. $file is the bare path now that the
                # locator is a separate field (D4) — the written entry is
                # path:pattern, matching what is_pattern_excluded parses, not
                # path:lineno:pattern which could never match.
                local excl_entry="$file"
                # For pattern items, extract the pattern portion
                if [[ "$message" == *"'"*"'"* ]]; then
                    local pattern
                    pattern=$(echo "$message" | grep -oE "'[^']+'" | head -1 | tr -d "'")
                    if [[ -n "$pattern" ]]; then
                        excl_entry="${file}:${pattern}"
                    fi
                fi
                echo "" >> "$EXCLUSIONS_FILE"
                echo "# Excluded $(date +%Y-%m-%d) via interactive review" >> "$EXCLUSIONS_FILE"
                echo "$excl_entry" >> "$EXCLUSIONS_FILE"
                echo -e "  -> ${YELLOW}Excluded${NC} (added to exclusions.txt)"
                ;;
        esac
        echo ""
    done
}

# ---------------------------------------------------------------------------
# Audit exclusions
# ---------------------------------------------------------------------------
audit_exclusions() {
    if [[ ! -f "$EXCLUSIONS_FILE" ]]; then
        echo "No exclusions file found at $EXCLUSIONS_FILE"
        exit 0
    fi

    echo -e "${CYAN}Exclusion audit:${NC}"
    local stale_count=0

    while IFS= read -r line; do
        [[ -z "$line" || "$line" =~ ^[[:space:]]*# ]] && continue
        line="$(echo "$line" | sed 's/^[[:space:]]*//;s/[[:space:]]*$//')"
        [[ -z "$line" ]] && continue

        if [[ "$line" == */ ]]; then
            # Directory exclusion
            if [[ -d "$line" ]]; then
                echo -e "  ${GREEN}OK${NC}  $line -- directory exists"
            else
                echo -e "  ${RED}!!${NC}  $line -- DIRECTORY DELETED"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            fi
        elif [[ "$line" == *:* ]]; then
            # Pattern exclusion
            local file="${line%%:*}"
            local pattern="${line#*:}"
            if [[ ! -f "$file" ]]; then
                echo -e "  ${RED}!!${NC}  $line -- FILE DELETED"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            elif ! grep -qF "$pattern" "$file" 2>/dev/null; then
                echo -e "  ${RED}!!${NC}  $line -- PATTERN NOT FOUND"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            else
                local match_line
                match_line=$(grep -nF "$pattern" "$file" 2>/dev/null | head -1 | cut -d: -f1)
                echo -e "  ${GREEN}OK${NC}  $line -- pattern matches (line $match_line)"
            fi
        else
            # File exclusion
            if [[ -f "$line" ]]; then
                echo -e "  ${GREEN}OK${NC}  $line -- file exists"
            else
                echo -e "  ${RED}!!${NC}  $line -- FILE DELETED"
                stale_count=$((stale_count + 1))
                maybe_remove_exclusion "$line"
            fi
        fi
    done < "$EXCLUSIONS_FILE"

    echo ""
    if [[ $stale_count -gt 0 ]]; then
        echo "Found $stale_count stale exclusions."
    else
        echo -e "${GREEN}All exclusions valid.${NC}"
    fi
}

maybe_remove_exclusion() {
    local entry="$1"
    if $NON_INTERACTIVE || [[ ! -t 0 ]]; then
        echo "    (run interactively to remove)"
        return
    fi
    local response=""
    echo -n "    Remove exclusion? [y/n]: "
    read -r response
    if [[ "$response" == "y" ]]; then
        # Escape special chars for sed
        local escaped
        escaped=$(printf '%s\n' "$entry" | sed 's/[\/&]/\\&/g')
        if [[ "$(uname)" == "Darwin" ]]; then
            sed -i '' "/^${escaped}$/d" "$EXCLUSIONS_FILE"
        else
            sed -i "/^${escaped}$/d" "$EXCLUSIONS_FILE"
        fi
        echo "    -> Removed"
    fi
}

# ---------------------------------------------------------------------------
# Output helpers
# ---------------------------------------------------------------------------
print_phase_status() {
    local issues="$1"
    if [[ "$JSON_MODE" == "true" ]]; then
        return
    fi
    if [[ $issues -eq 0 ]]; then
        echo -e "${GREEN}GREEN${NC} (0 issues)"
    else
        echo -e "${YELLOW}YELLOW${NC} (${issues} warnings)"
    fi
}

phase_status_label() {
    # Indirect array access via eval rather than `local -n` (bash 4.3+):
    # the shebang is `env bash`, which on macOS resolves to bash 3.2, where
    # a nameref fails and the function silently emits nothing.
    # Callers always pass a literal internal array name, never user input.
    local _arr_name=$1
    local _count _i _f
    eval "_count=\${#${_arr_name}[@]}"
    if [[ $_count -eq 0 ]]; then
        echo "GREEN"
    else
        # Check if any are errors
        for (( _i=0; _i<_count; _i++ )); do
            eval "_f=\${${_arr_name}[$_i]}"
            if [[ "$_f" == error\|* ]]; then
                echo "RED"
                return
            fi
        done
        echo "YELLOW"
    fi
}

print_summary() {
    local total=$((TOTAL_WARNINGS + TOTAL_ERRORS))
    local overall="GREEN"
    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        overall="RED"
    elif [[ $TOTAL_WARNINGS -gt 0 ]]; then
        overall="YELLOW"
    fi

    echo ""
    case "$overall" in
        GREEN)  echo -e "Status: ${GREEN}GREEN${NC} (0 issues)" ;;
        YELLOW) echo -e "Status: ${YELLOW}YELLOW${NC} (${TOTAL_WARNINGS} warnings, ${TOTAL_ERRORS} errors)" ;;
        RED)    echo -e "Status: ${RED}RED${NC} (${TOTAL_WARNINGS} warnings, ${TOTAL_ERRORS} errors)" ;;
    esac

    if [[ $TOTAL_FIXED -gt 0 ]]; then
        echo -e "Fixed: ${GREEN}${TOTAL_FIXED} items${NC}"
    fi
}

print_json() {
    local p6_status p7_status p8_status p9_status overall
    p6_status=$(phase_status_label PHASE6_FINDINGS)
    p7_status=$(phase_status_label PHASE7_FINDINGS)
    p8_status=$(phase_status_label PHASE8_FINDINGS)
    p9_status=$(phase_status_label PHASE9_FINDINGS)

    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        overall="RED"
    elif [[ $TOTAL_WARNINGS -gt 0 ]]; then
        overall="YELLOW"
    else
        overall="GREEN"
    fi

    # Build JSON findings arrays
    local p6_json p7_json p8_json p9_json
    p6_json=$(findings_to_json PHASE6_FINDINGS)
    p7_json=$(findings_to_json PHASE7_FINDINGS)
    p8_json=$(findings_to_json PHASE8_FINDINGS)
    p9_json=$(findings_to_json PHASE9_FINDINGS)

    cat <<ENDJSON
{
  "version": "${CURRENT_VERSION}",
  "status": "${overall}",
  "phases": {
    "nav_completeness": {"status": "${p6_status}", "issues": ${#PHASE6_FINDINGS[@]}, "findings": ${p6_json}},
    "count_consistency": {"status": "${p7_status}", "issues": ${#PHASE7_FINDINGS[@]}, "findings": ${p7_json}},
    "skill_agent_coverage": {"status": "${p8_status}", "issues": ${#PHASE8_FINDINGS[@]}, "findings": ${p8_json}},
    "cross_doc_freshness": {"status": "${p9_status}", "issues": ${#PHASE9_FINDINGS[@]}, "findings": ${p9_json}}
  },
  "total_issues": $((TOTAL_WARNINGS + TOTAL_ERRORS)),
  "total_warnings": ${TOTAL_WARNINGS},
  "total_errors": ${TOTAL_ERRORS},
  "total_fixed": ${TOTAL_FIXED}
}
ENDJSON
}

findings_to_json() {
    # Indirect array access via eval rather than `local -n` — see the note on
    # phase_status_label above (bash 3.2 has no namerefs).
    local _arr_name=$1
    local _count _i entry
    eval "_count=\${#${_arr_name}[@]}"
    if [[ $_count -eq 0 ]]; then
        echo "[]"
        return
    fi
    local first=true
    echo -n "["
    for (( _i=0; _i<_count; _i++ )); do
        eval "entry=\${${_arr_name}[$_i]}"
        IFS='|' read -r severity file locator message fixable fix_detail <<< "$entry"
        # Render the location the way every consumer has always seen it —
        # path:locator, or the bare path — so the JSON contract is unchanged
        # even though the record now carries the two as separate fields.
        local location
        location="$(finding_location "$file" "$locator")"
        # Escape JSON strings
        location=$(echo "$location" | sed 's/\\/\\\\/g;s/"/\\"/g')
        message=$(echo "$message" | sed 's/\\/\\\\/g;s/"/\\"/g')
        if ! $first; then echo -n ","; fi
        first=false
        echo -n "{\"severity\":\"${severity}\",\"file\":\"${location}\",\"message\":\"${message}\"}"
    done
    echo -n "]"
}

# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
main() {
    # Handle audit mode separately
    if $AUDIT_EXCLUSIONS; then
        load_exclusions
        audit_exclusions
        exit 0
    fi

    load_exclusions
    load_counts

    if [[ "$JSON_MODE" != "true" ]]; then
        echo -e "${CYAN}=== Docs Staleness Check ===${NC}"
        echo "Version: ${CURRENT_VERSION} | Commands: ${EXPECTED_CMDS} | Skills: ${EXPECTED_SKILLS} | Agents: ${EXPECTED_AGENTS}"
        echo ""
    fi

    # Run all phases
    phase6_nav_completeness
    phase7_count_consistency
    phase8_skill_agent_coverage
    phase9_cross_doc_freshness

    # Fix mode
    if $FIX_MODE; then
        pass1_auto_fix
        pass2_interactive_review
    fi

    # Output
    if [[ "$JSON_MODE" == "true" ]]; then
        print_json
    else
        print_summary
    fi

    # Exit code
    if [[ $TOTAL_ERRORS -gt 0 ]]; then
        exit 1
    elif [[ $TOTAL_WARNINGS -gt 0 ]]; then
        exit 1
    fi
    exit 0
}

main "$@"
