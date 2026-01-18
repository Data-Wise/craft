#!/bin/bash
#
# Agent-scoped hooks for orchestrator-v2
#
# These hooks run during orchestration lifecycle events:
# - PreToolUse: Before each agent/subagent starts
# - PostToolUse: After each agent/subagent completes
# - Stop: When orchestration is stopped/completed
#
# Environment variables available:
# - HOOK_EVENT: The current hook event (PreToolUse, PostToolUse, Stop)
# - TOOL_NAME: Name of the tool being used (for PreToolUse/PostToolUse)
# - DURATION: Tool execution duration in seconds (for PostToolUse)
# - AGENT_COUNT: Total number of agents spawned (for Stop)
#

set -eo pipefail

# Create necessary directories
mkdir -p .craft/logs .craft/cache

# Log file location
LOG_FILE=".craft/logs/orchestration.log"
CACHE_DIR=".craft/cache"

# Get timestamp in ISO format
timestamp() {
    date -Iseconds
}

# Log with timestamp
log() {
    echo "[$(timestamp)] $*" >> "$LOG_FILE"
}

# Main hook logic
case "${HOOK_EVENT:-}" in
    PreToolUse)
        # ========================================
        # BEFORE AGENT LAUNCH
        # ========================================

        # Count currently active agents (background Claude processes)
        ACTIVE_AGENTS=$(pgrep -f "claude.*agent" 2>/dev/null | wc -l | xargs)
        ACTIVE_AGENTS="${ACTIVE_AGENTS:-0}"

        # Get resource limit from mode (default: 2)
        MODE="${CRAFT_MODE:-default}"
        case "$MODE" in
            debug)
                MAX_AGENTS=1
                ;;
            optimize|release)
                MAX_AGENTS=4
                ;;
            *)
                MAX_AGENTS=2
                ;;
        esac

        # Check if we're at capacity
        if [ "$ACTIVE_AGENTS" -ge "$MAX_AGENTS" ]; then
            log "⚠️  Resource limit: $ACTIVE_AGENTS/$MAX_AGENTS agents running"
            echo "⚠ Resource limit: $ACTIVE_AGENTS/$MAX_AGENTS agents already running"
            echo "action: queue"  # Signal to orchestrator to queue this agent
            exit 0
        fi

        # Log agent start
        log "🚀 Starting agent: ${TOOL_NAME:-unknown}"
        log "   Active agents: $ACTIVE_AGENTS/$MAX_AGENTS"
        log "   Mode: $MODE"

        # Create agent status entry in cache
        cat > "$CACHE_DIR/agent-${TOOL_NAME:-unknown}.status" <<EOF
{
  "agent": "${TOOL_NAME:-unknown}",
  "status": "starting",
  "start_time": "$(timestamp)",
  "mode": "$MODE"
}
EOF
        ;;

    PostToolUse)
        # ========================================
        # AFTER AGENT COMPLETION
        # ========================================

        # Get duration (in seconds)
        DURATION_SEC="${DURATION:-0}"

        # Log agent completion
        log "✅ Completed agent: ${TOOL_NAME:-unknown}"
        log "   Duration: ${DURATION_SEC}s"

        # Update agent status cache
        cat > "$CACHE_DIR/agent-${TOOL_NAME:-unknown}.status" <<EOF
{
  "agent": "${TOOL_NAME:-unknown}",
  "status": "completed",
  "start_time": "$(cat "$CACHE_DIR/agent-${TOOL_NAME:-unknown}.status" 2>/dev/null | jq -r .start_time || echo "$(timestamp)")",
  "end_time": "$(timestamp)",
  "duration_seconds": $DURATION_SEC,
  "mode": "${CRAFT_MODE:-default}"
}
EOF

        # Append to agent results cache (for result reuse)
        echo "${TOOL_NAME:-unknown}:success:$(date +%s):${DURATION_SEC}" >> "$CACHE_DIR/agent-results.cache"

        # Check if this was the last agent (optional cleanup trigger)
        ACTIVE_AGENTS=$(pgrep -f "claude.*agent" 2>/dev/null | wc -l | xargs)
        ACTIVE_AGENTS="${ACTIVE_AGENTS:-0}"
        if [ "$ACTIVE_AGENTS" -eq 0 ]; then
            log "📊 All agents completed"
        fi
        ;;

    Stop)
        # ========================================
        # ORCHESTRATION STOP/CLEANUP
        # ========================================

        log "🛑 Orchestration stopped"
        log "   Total agents: ${AGENT_COUNT:-0}"

        # Save final session state to JSON
        SESSION_FILE="$CACHE_DIR/last-orchestration.json"

        # Collect agent statuses
        AGENT_STATUSES="[]"
        for status_file in "$CACHE_DIR"/agent-*.status; do
            if [ -f "$status_file" ]; then
                AGENT_STATUSES=$(echo "$AGENT_STATUSES" | jq ". + [$(cat "$status_file")]")
            fi
        done

        # Create session summary
        cat > "$SESSION_FILE" <<EOF
{
  "timestamp": "$(timestamp)",
  "total_agents": ${AGENT_COUNT:-0},
  "mode": "${CRAFT_MODE:-default}",
  "agents": $AGENT_STATUSES,
  "log_file": "$LOG_FILE"
}
EOF

        log "💾 Session saved: $SESSION_FILE"

        # Optional: Archive old logs (keep last 10 sessions)
        LOG_COUNT=$(ls -1 .craft/logs/orchestration-*.log 2>/dev/null | wc -l | tr -d ' ')
        if [ "$LOG_COUNT" -gt 10 ]; then
            log "🗑️  Archiving old logs (keeping last 10)"
            ls -1t .craft/logs/orchestration-*.log | tail -n +11 | xargs rm -f
        fi
        ;;

    *)
        # Unknown event
        log "⚠️  Unknown hook event: ${HOOK_EVENT:-none}"
        exit 0
        ;;
esac

# Exit successfully
exit 0
