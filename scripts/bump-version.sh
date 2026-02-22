#!/bin/bash
# bump-version.sh - Atomically bump version AND sync counts across all project files
#
# Usage:
#   ./scripts/bump-version.sh 2.23.0              # Full bump (version + counts)
#   ./scripts/bump-version.sh 2.23.0 --dry-run    # Preview changes without writing
#   ./scripts/bump-version.sh --counts-only        # Sync counts without version bump
#   ./scripts/bump-version.sh --verify             # Check consistency (exit 0/1)
#
# Exit codes: 0 = success, 1 = drift found (--verify), 2 = usage error
#
# Note: Uses BSD sed (macOS). For GNU/Linux, change `sed -i ''` to `sed -i`.

set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PLUGIN_DIR="$(dirname "$SCRIPT_DIR")"

source "$SCRIPT_DIR/formatting.sh"
RED="$FMT_RED"
GREEN="$FMT_GREEN"
YELLOW="$FMT_YELLOW"
CYAN="$FMT_CYAN"
NC="$FMT_NC"

DRY_RUN=false
COUNTS_ONLY=false
VERIFY_ONLY=false
NEW_VERSION=""

for arg in "$@"; do
    case "$arg" in
        --dry-run|-n)  DRY_RUN=true ;;
        --counts-only) COUNTS_ONLY=true ;;
        --verify)      VERIFY_ONLY=true ;;
        --help|-h)
            echo "Usage: $0 [VERSION] [--dry-run] [--counts-only] [--verify]"
            echo ""
            echo "  VERSION        Target version (e.g. 2.23.0)"
            echo "  --dry-run      Preview changes without writing"
            echo "  --counts-only  Sync counts only (no version bump)"
            echo "  --verify       Check consistency (exit 0 if ok, 1 if drift)"
            exit 0
            ;;
        *)
            if [[ "$arg" =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
                NEW_VERSION="$arg"
            else
                echo -e "${RED}Error: Unknown argument '$arg'${NC}"
                echo "Usage: $0 [VERSION] [--dry-run] [--counts-only] [--verify]"
                exit 2
            fi
            ;;
    esac
done

if [ "$COUNTS_ONLY" = true ] && [ -n "$NEW_VERSION" ]; then
    echo -e "${RED}Error: Cannot specify version with --counts-only${NC}"; exit 2
fi
if [ "$VERIFY_ONLY" = true ] && [ -n "$NEW_VERSION" ]; then
    echo -e "${RED}Error: Cannot specify version with --verify${NC}"; exit 2
fi
if [ "$COUNTS_ONLY" = false ] && [ "$VERIFY_ONLY" = false ] && [ -z "$NEW_VERSION" ]; then
    echo -e "${RED}Error: Version required (or use --counts-only / --verify)${NC}"
    echo "Usage: $0 [VERSION] [--dry-run] [--counts-only] [--verify]"
    exit 2
fi

cd "$PLUGIN_DIR"

CURRENT_VERSION=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['version'])" 2>/dev/null || echo "unknown")

CMD_COUNT=$(find commands -name "*.md" ! -name "index.md" ! -name "README.md" 2>/dev/null | wc -l | tr -d ' ')
SKILL_COUNT=$(find skills -name "*.md" -o -name "SKILL.md" 2>/dev/null | wc -l | tr -d ' ')
AGENT_COUNT=$(find agents -name "*.md" 2>/dev/null | wc -l | tr -d ' ')
SPEC_COUNT=$(find docs/specs -name "SPEC-*.md" ! -path "*/archive/*" ! -path "*/_archive/*" 2>/dev/null | wc -l | tr -d ' ')

# Count of files this script manages (3 JSON + 10 text = 13)
# Update this if you add new file handlers below
FILE_COUNT=13

# ---------------------------------------------------------------------------
# VERIFY mode
# ---------------------------------------------------------------------------
if [ "$VERIFY_ONLY" = true ]; then
    echo -e "${CYAN}Version & Count Verification${NC}"
    echo "=============================="
    echo ""
    echo -e "  Current version: ${CYAN}v${CURRENT_VERSION}${NC}"
    echo -e "  Counts: ${CMD_COUNT} commands, ${AGENT_COUNT} agents, ${SKILL_COUNT} skills"
    echo ""

    ERRORS=0

    for file in .claude-plugin/plugin.json .claude-plugin/marketplace.json package.json; do
        [ -f "$file" ] || continue
        FILE_VER=$(python3 -c "import json; d=json.load(open('$file')); print(d.get('version', d.get('metadata',{}).get('version','')))" 2>/dev/null)
        if [ -n "$FILE_VER" ] && [ "$FILE_VER" != "$CURRENT_VERSION" ]; then
            echo -e "  ${RED}✗${NC} $file version: $FILE_VER (expected $CURRENT_VERSION)"
            ERRORS=$((ERRORS + 1))
        fi
    done

    DESC=$(python3 -c "import json; print(json.load(open('.claude-plugin/plugin.json'))['description'])")
    DOC_CMDS=$(echo "$DESC" | grep -o '[0-9]* commands' | head -1 | grep -o '[0-9]*' || echo "?")
    DOC_AGENTS=$(echo "$DESC" | grep -o '[0-9]* agents' | grep -o '[0-9]*' || echo "?")
    DOC_SKILLS=$(echo "$DESC" | grep -o '[0-9]* skills' | grep -o '[0-9]*' || echo "?")

    if [ "$CMD_COUNT" != "$DOC_CMDS" ]; then echo -e "  ${RED}✗${NC} Commands: $CMD_COUNT actual vs $DOC_CMDS documented"; ERRORS=$((ERRORS + 1)); fi
    if [ "$AGENT_COUNT" != "$DOC_AGENTS" ]; then echo -e "  ${RED}✗${NC} Agents: $AGENT_COUNT actual vs $DOC_AGENTS documented"; ERRORS=$((ERRORS + 1)); fi
    if [ "$SKILL_COUNT" != "$DOC_SKILLS" ]; then echo -e "  ${RED}✗${NC} Skills: $SKILL_COUNT actual vs $DOC_SKILLS documented"; ERRORS=$((ERRORS + 1)); fi

    if [ -f "CLAUDE.md" ] && ! grep -q "v${CURRENT_VERSION}" CLAUDE.md; then
        echo -e "  ${RED}✗${NC} CLAUDE.md missing v${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    if [ -f "README.md" ] && ! grep -q "version-${CURRENT_VERSION}" README.md; then
        echo -e "  ${RED}✗${NC} README.md badge missing ${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    if [ -f "mkdocs.yml" ] && ! grep -q "v${CURRENT_VERSION}" mkdocs.yml; then
        echo -e "  ${RED}✗${NC} mkdocs.yml missing v${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    if [ -f ".STATUS" ] && ! grep -q "version: ${CURRENT_VERSION}" .STATUS; then
        echo -e "  ${RED}✗${NC} .STATUS version missing ${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    if [ -f "docs/DEPENDENCY-ARCHITECTURE.md" ] && ! grep -q "Version\*\*: ${CURRENT_VERSION}" docs/DEPENDENCY-ARCHITECTURE.md; then
        echo -e "  ${RED}✗${NC} docs/DEPENDENCY-ARCHITECTURE.md missing ${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    if [ -f "docs/reference/configuration.md" ] && ! grep -q "bump-version\.sh ${CURRENT_VERSION}" docs/reference/configuration.md; then
        echo -e "  ${RED}✗${NC} docs/reference/configuration.md example missing ${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    if [ -f "docs/REFCARD.md" ] && ! grep -q "Version: ${CURRENT_VERSION}" docs/REFCARD.md; then
        echo -e "  ${RED}✗${NC} docs/REFCARD.md box missing ${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    if [ -f "docs/index.md" ] && ! grep -q "Latest: v${CURRENT_VERSION}" docs/index.md; then
        echo -e "  ${RED}✗${NC} docs/index.md info box missing v${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
    fi
    for hub_file in commands/hub.md docs/commands/hub.md; do
        if [ -f "$hub_file" ] && ! grep -q "Toolkit v${CURRENT_VERSION}" "$hub_file"; then
            echo -e "  ${RED}✗${NC} $hub_file banner missing v${CURRENT_VERSION}"; ERRORS=$((ERRORS + 1))
        fi
    done

    echo ""
    if [ $ERRORS -gt 0 ]; then
        echo -e "${RED}DRIFT DETECTED: $ERRORS issue(s)${NC}"
        echo -e "  Fix: ./scripts/bump-version.sh ${CURRENT_VERSION}"
        exit 1
    else
        echo -e "${GREEN}ALL CONSISTENT${NC} — v${CURRENT_VERSION}, ${CMD_COUNT} commands, ${AGENT_COUNT} agents, ${SKILL_COUNT} skills"
        exit 0
    fi
fi

# ---------------------------------------------------------------------------
# Bump mode
# ---------------------------------------------------------------------------
if [ "$COUNTS_ONLY" = true ]; then
    TARGET_VERSION="$CURRENT_VERSION"
else
    TARGET_VERSION="$NEW_VERSION"
fi

if [ "$DRY_RUN" = true ]; then
    echo -e "${CYAN}bump-version.sh --dry-run${NC}"
else
    echo -e "${CYAN}bump-version.sh${NC}"
fi
echo "=============================="

if [ "$COUNTS_ONLY" = true ]; then
    echo -e "  Mode: ${YELLOW}counts-only${NC}"
else
    echo -e "  Version: ${CURRENT_VERSION} → ${GREEN}${TARGET_VERSION}${NC}"
fi
echo -e "  Counts:  ${CMD_COUNT} commands, ${AGENT_COUNT} agents, ${SKILL_COUNT} skills, ${SPEC_COUNT} specs"
echo ""

UPDATED=0

update_file() {
    local file="$1"
    local result mode

    [ -f "$file" ] || { echo -e "  ${YELLOW}skip${NC} $file (not found)"; return; }

    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} $file"; return
    fi

    mode="version"
    [ "$COUNTS_ONLY" = true ] && mode="counts"

    result=$(python3 "$SCRIPT_DIR/bump-version-helper.py" "$file" "$mode" "$TARGET_VERSION" "$CMD_COUNT" "$AGENT_COUNT" "$SKILL_COUNT")

    if [ "$result" = "updated" ]; then
        echo -e "  ${GREEN}✓${NC} $file"; UPDATED=$((UPDATED + 1))
    else
        echo -e "  ${YELLOW}—${NC} $file (unchanged)"
    fi
}

echo -e "${CYAN}JSON files:${NC}"
update_file ".claude-plugin/plugin.json"
update_file ".claude-plugin/marketplace.json"
update_file "package.json"
echo ""

echo -e "${CYAN}Text files:${NC}"

# CLAUDE.md
if [ -f "CLAUDE.md" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} CLAUDE.md"
    else
        CHANGED=false
        if [ "$COUNTS_ONLY" = false ] && grep -q "Current Version:.*v[0-9]" CLAUDE.md; then
            sed -i '' "s|Current Version:\*\* v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*|Current Version:** v${TARGET_VERSION}|g" CLAUDE.md
            CHANGED=true
        fi
        if grep -q '\*\*[0-9]* commands\*\*' CLAUDE.md; then
            sed -i '' "s|\*\*[0-9]* commands\*\*|\*\*${CMD_COUNT} commands\*\*|g" CLAUDE.md
            sed -i '' "s|\*\*[0-9]* skills\*\*|\*\*${SKILL_COUNT} skills\*\*|g" CLAUDE.md
            sed -i '' "s|\*\*[0-9]* agents\*\*|\*\*${AGENT_COUNT} agents\*\*|g" CLAUDE.md
            sed -i '' "s|\*\*[0-9]* specs\*\*|\*\*${SPEC_COUNT} specs\*\*|g" CLAUDE.md
            CHANGED=true
        fi
        if [ "$CHANGED" = true ]; then
            echo -e "  ${GREEN}✓${NC} CLAUDE.md"; UPDATED=$((UPDATED + 1))
        else
            echo -e "  ${YELLOW}—${NC} CLAUDE.md (unchanged)"
        fi
    fi
fi

# README.md
if [ -f "README.md" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} README.md"
    else
        CHANGED=false
        if [ "$COUNTS_ONLY" = false ] && grep -q "version-[0-9]" README.md; then
            sed -i '' "s|version-[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*|version-${TARGET_VERSION}|g" README.md
            CHANGED=true
        fi
        if grep -q '\*\*[0-9]* commands\*\*' README.md; then
            sed -i '' "s|\*\*[0-9]* commands\*\*|\*\*${CMD_COUNT} commands\*\*|g" README.md
            sed -i '' "s|\*\*[0-9]* skills\*\*|\*\*${SKILL_COUNT} skills\*\*|g" README.md
            sed -i '' "s|\*\*[0-9]* agents\*\*|\*\*${AGENT_COUNT} agents\*\*|g" README.md
            CHANGED=true
        fi
        sed -i '' "s|[0-9][0-9]* commands, [0-9][0-9]* agents, [0-9][0-9]* skills|${CMD_COUNT} commands, ${AGENT_COUNT} agents, ${SKILL_COUNT} skills|g" README.md
        if [ "$CHANGED" = true ]; then
            echo -e "  ${GREEN}✓${NC} README.md"; UPDATED=$((UPDATED + 1))
        else
            echo -e "  ${YELLOW}—${NC} README.md (unchanged)"
        fi
    fi
fi

# docs/index.md — only update header/badge version, not historical "NEW in vX.Y.Z" refs
if [ -f "docs/index.md" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} docs/index.md"
    else
        if [ "$COUNTS_ONLY" = false ]; then
            # Target specific version patterns (badges, headers), not prose mentions
            sed -i '' "s|version-${CURRENT_VERSION}|version-${TARGET_VERSION}|g" docs/index.md
            sed -i '' "s|Current version: v${CURRENT_VERSION}|Current version: v${TARGET_VERSION}|g" docs/index.md
            # Info box: !!! info "Latest: vX.Y.Z — ..."
            sed -i '' "s|Latest: v${CURRENT_VERSION}|Latest: v${TARGET_VERSION}|g" docs/index.md
        fi
        sed -i '' "s|[0-9][0-9]* commands, [0-9][0-9]* AI agents, and [0-9][0-9]* auto-triggered skills|${CMD_COUNT} commands, ${AGENT_COUNT} AI agents, and ${SKILL_COUNT} auto-triggered skills|g" docs/index.md
        sed -i '' "s|[0-9][0-9]* commands, [0-9][0-9]* agents, [0-9][0-9]* skills|${CMD_COUNT} commands, ${AGENT_COUNT} agents, ${SKILL_COUNT} skills|g" docs/index.md
        echo -e "  ${GREEN}✓${NC} docs/index.md"; UPDATED=$((UPDATED + 1))
    fi
fi

# docs/REFCARD.md — update header + box interior version lines
if [ -f "docs/REFCARD.md" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} docs/REFCARD.md"
    else
        if [ "$COUNTS_ONLY" = false ]; then
            # Target the version badge/header line
            sed -i '' "s|version-${CURRENT_VERSION}|version-${TARGET_VERSION}|g" docs/REFCARD.md
            sed -i '' "1,5s|v${CURRENT_VERSION}|v${TARGET_VERSION}|g" docs/REFCARD.md
            # Box interior: line ~7 "Version: X.Y.Z" and line ~11 "vX.Y.Z: ..."
            sed -i '' "s|Version: ${CURRENT_VERSION}|Version: ${TARGET_VERSION}|g" docs/REFCARD.md
            sed -i '' "s|v${CURRENT_VERSION}:|v${TARGET_VERSION}:|g" docs/REFCARD.md
        fi
        echo -e "  ${GREEN}✓${NC} docs/REFCARD.md"; UPDATED=$((UPDATED + 1))
    fi
fi

# docs/DEPENDENCY-ARCHITECTURE.md — **Version**: X.Y.Z footer
if [ -f "docs/DEPENDENCY-ARCHITECTURE.md" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} docs/DEPENDENCY-ARCHITECTURE.md"
    else
        if [ "$COUNTS_ONLY" = false ]; then
            sed -i '' "s|\*\*Version\*\*: [0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*|\*\*Version\*\*: ${TARGET_VERSION}|g" docs/DEPENDENCY-ARCHITECTURE.md
        fi
        echo -e "  ${GREEN}✓${NC} docs/DEPENDENCY-ARCHITECTURE.md"; UPDATED=$((UPDATED + 1))
    fi
fi

# docs/reference/configuration.md — bump-version.sh example + file count
if [ -f "docs/reference/configuration.md" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} docs/reference/configuration.md"
    else
        if [ "$COUNTS_ONLY" = false ]; then
            sed -i '' "s|bump-version\.sh [0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*|bump-version.sh ${TARGET_VERSION}|g" docs/reference/configuration.md
        fi
        sed -i '' "s|across [0-9][0-9]* files|across ${FILE_COUNT} files|g" docs/reference/configuration.md
        echo -e "  ${GREEN}✓${NC} docs/reference/configuration.md"; UPDATED=$((UPDATED + 1))
    fi
fi

# mkdocs.yml
if [ -f "mkdocs.yml" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} mkdocs.yml"
    else
        sed -i '' "s|[0-9][0-9]* commands, [0-9][0-9]* agents, [0-9][0-9]* skills|${CMD_COUNT} commands, ${AGENT_COUNT} agents, ${SKILL_COUNT} skills|g" mkdocs.yml
        [ "$COUNTS_ONLY" = false ] && sed -i '' "s|v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]* adds|v${TARGET_VERSION} adds|" mkdocs.yml
        echo -e "  ${GREEN}✓${NC} mkdocs.yml"; UPDATED=$((UPDATED + 1))
    fi
fi

# .STATUS
if [ -f ".STATUS" ]; then
    if [ "$DRY_RUN" = true ]; then
        echo -e "  ${CYAN}would update${NC} .STATUS"
    else
        [ "$COUNTS_ONLY" = false ] && sed -i '' "s|^version: [0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*|version: ${TARGET_VERSION}|" .STATUS
        sed -i '' "s|[0-9][0-9]* commands, [0-9][0-9]* skills, [0-9][0-9]* agents|${CMD_COUNT} commands, ${SKILL_COUNT} skills, ${AGENT_COUNT} agents|g" .STATUS
        echo -e "  ${GREEN}✓${NC} .STATUS"; UPDATED=$((UPDATED + 1))
    fi
fi

# commands/hub.md + docs/commands/hub.md — version in banner, test/skill counts
for hub_file in commands/hub.md docs/commands/hub.md; do
    if [ -f "$hub_file" ]; then
        if [ "$DRY_RUN" = true ]; then
            echo -e "  ${CYAN}would update${NC} $hub_file"
        else
            if [ "$COUNTS_ONLY" = false ]; then
                # Banner version: "Toolkit v2.23.1"
                sed -i '' "s|Toolkit v[0-9][0-9]*\.[0-9][0-9]*\.[0-9][0-9]*|Toolkit v${TARGET_VERSION}|g" "$hub_file"
            fi
            # Counts in banner and quick reference: "N commands | N skills | N agents"
            sed -i '' "s|[0-9][0-9]* commands | [0-9][0-9]* skills | [0-9][0-9]* agents|${CMD_COUNT} commands | ${SKILL_COUNT} skills | ${AGENT_COUNT} agents|g" "$hub_file"
            echo -e "  ${GREEN}✓${NC} $hub_file"; UPDATED=$((UPDATED + 1))
        fi
    fi
done

echo ""

if [ "$DRY_RUN" = true ]; then
    echo -e "${YELLOW}DRY RUN — no files were modified${NC}"
    echo "  Run without --dry-run to apply changes"
else
    echo -e "${GREEN}Done!${NC} Updated $UPDATED file(s)"
    [ "$COUNTS_ONLY" = false ] && echo -e "  Version: v${TARGET_VERSION}"
    echo -e "  Counts:  ${CMD_COUNT} commands, ${AGENT_COUNT} agents, ${SKILL_COUNT} skills"
fi
