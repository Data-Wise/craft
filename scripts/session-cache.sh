#!/bin/bash
# Session-Level Caching for Craft Demo Dependency Management
# Part of: feature/demo-dependency-management
# Phase: 1 (Core Dependency Checking)
#
# Provides session-scoped caching utilities for tool detection results.
# Cache location: /tmp/craft-deps-$SESSION_ID/
# Cache TTL: 60 seconds

# Cache configuration
CACHE_TTL=60
CRAFT_CACHE_DIR=""
SESSION_ID=""

#
# Initialize cache for this session
#
# Creates a unique cache directory using timestamp + random component
# Exports CRAFT_CACHE_DIR and SESSION_ID for use by other scripts
#
# Returns:
#   0 on success
#   1 on failure
#
# Output:
#   Prints cache directory path to stdout
#
init_cache() {
  # Generate unique session ID: timestamp_random
  local timestamp=$(date +%s)
  local random_part=$((RANDOM % 10000))
  SESSION_ID="${timestamp}_${random_part}"
  CRAFT_CACHE_DIR="/tmp/craft-deps-${SESSION_ID}"

  # Create cache directory
  if mkdir -p "$CRAFT_CACHE_DIR" 2>/dev/null; then
    # Export for use by other scripts
    export CRAFT_CACHE_DIR
    export SESSION_ID
    echo "$CRAFT_CACHE_DIR"
    return 0
  else
    return 1
  fi
}

#
# Retrieve cached status for a tool if valid
#
# Checks if cache file exists, validates age (< 60 seconds),
# and returns cached JSON data if valid. Returns empty/null if
# cache is missing or expired.
#
# Arguments:
#   $1 - tool_name (e.g., "asciinema")
#
# Returns:
#   0 if cache hit (valid data)
#   1 if cache miss or invalid
#
# Output:
#   Prints JSON object if valid cache found
#   Prints empty string if no valid cache
#
get_cached_status() {
  local tool_name="$1"

  if [ -z "$CRAFT_CACHE_DIR" ]; then
    return 1
  fi

  local cache_file="${CRAFT_CACHE_DIR}/${tool_name}.json"

  # Check if cache file exists
  if [ ! -f "$cache_file" ]; then
    return 1
  fi

  # Extract timestamp from cache file
  local cached_timestamp
  cached_timestamp=$(jq -r '.timestamp' "$cache_file" 2>/dev/null || echo "0")

  if [ "$cached_timestamp" = "0" ] || [ -z "$cached_timestamp" ]; then
    # Invalid JSON or no timestamp
    return 1
  fi

  # Calculate cache age
  local current_timestamp=$(date +%s)
  local age=$((current_timestamp - cached_timestamp))

  # Check if cache is still valid (< 60 seconds)
  if [ "$age" -lt "$CACHE_TTL" ]; then
    # Cache is valid, output the JSON
    cat "$cache_file"
    return 0
  else
    # Cache expired
    return 1
  fi
}

#
# Store tool status in cache
#
# Writes status JSON to cache file using atomic write pattern
# (write to temp file, then mv). Includes timestamp for age calculation.
#
# Arguments:
#   $1 - tool_name (e.g., "asciinema")
#   $2 - status_json (JSON object as string)
#
# Returns:
#   0 on success
#   1 on failure
#
# Example:
#   store_cache "asciinema" '{"installed": true, "version": "2.3.0"}'
#
store_cache() {
  local tool_name="$1"
  local status_json="$2"

  if [ -z "$CRAFT_CACHE_DIR" ]; then
    return 1
  fi

  # Ensure cache directory exists
  if ! mkdir -p "$CRAFT_CACHE_DIR" 2>/dev/null; then
    return 1
  fi

  local cache_file="${CRAFT_CACHE_DIR}/${tool_name}.json"
  local temp_file="${cache_file}.tmp.$$"

  # Add timestamp to JSON if not already present
  local json_with_timestamp
  if echo "$status_json" | jq -e '.timestamp' >/dev/null 2>&1; then
    # Timestamp already present
    json_with_timestamp="$status_json"
  else
    # Add timestamp to JSON object
    json_with_timestamp=$(echo "$status_json" | jq --arg ts "$(date +%s)" '. + {timestamp: ($ts | tonumber)}' 2>/dev/null)
    if [ -z "$json_with_timestamp" ]; then
      # Fallback: manual timestamp insertion if jq fails
      json_with_timestamp="$status_json"
    fi
  fi

  # Write to temp file
  if echo "$json_with_timestamp" > "$temp_file" 2>/dev/null; then
    # Atomic move
    if mv "$temp_file" "$cache_file" 2>/dev/null; then
      return 0
    else
      rm -f "$temp_file" 2>/dev/null
      return 1
    fi
  else
    rm -f "$temp_file" 2>/dev/null
    return 1
  fi
}

#
# Delete cache for a specific tool
#
# Removes the tool's cache file. Used after installation to force
# re-detection on next check. Silently succeeds if file doesn't exist.
#
# Arguments:
#   $1 - tool_name (e.g., "asciinema")
#
# Returns:
#   Always returns 0 (success)
#
clear_cache() {
  local tool_name="$1"

  if [ -z "$CRAFT_CACHE_DIR" ]; then
    return 0
  fi

  local cache_file="${CRAFT_CACHE_DIR}/${tool_name}.json"
  rm -f "$cache_file" 2>/dev/null
  return 0
}

#
# Clean up entire cache directory
#
# Removes the entire session cache directory. Called on session end.
# Gracefully handles cases where directory is already deleted or doesn't exist.
#
# Returns:
#   Always returns 0 (success)
#
cleanup_cache() {
  if [ -z "$CRAFT_CACHE_DIR" ]; then
    return 0
  fi

  if [ -d "$CRAFT_CACHE_DIR" ]; then
    rm -rf "$CRAFT_CACHE_DIR" 2>/dev/null || true
  fi

  return 0
}

# Note: Functions are available in current shell session
# To use in subshells, source this script: source scripts/session-cache.sh
