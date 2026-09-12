#!/bin/bash
# Sync agents between source repo and deployed location
# Usage: sync-agents.sh [status|diff|pull|push]

set -e

# Paths
SOURCE_DIR="$HOME/.claude/plugins/solo-founder-fleet/agents"
DEPLOYED_DIR="$HOME/.claude/agents"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get list of agent files from source
get_source_agents() {
  ls "$SOURCE_DIR"/*.md 2>/dev/null | xargs -n1 basename
}

# Get list of agent files from deployed
get_deployed_agents() {
  ls "$DEPLOYED_DIR"/*.md 2>/dev/null | xargs -n1 basename
}

# Compare two files, return 0 if identical
files_identical() {
  local file="$1"
  local source="$SOURCE_DIR/$file"
  local deployed="$DEPLOYED_DIR/$file"

  if [ ! -f "$source" ] || [ ! -f "$deployed" ]; then
    return 1
  fi

  diff -q "$source" "$deployed" > /dev/null 2>&1
}

# Get modification time (cross-platform)
get_mtime() {
  local file="$1"
  if [[ "$OSTYPE" == "darwin"* ]]; then
    stat -f %m "$file"
  else
    stat -c %Y "$file"
  fi
}

# Show status of all agents
cmd_status() {
  echo -e "${BLUE}Agent Sync Status${NC}"
  echo "Source:   $SOURCE_DIR"
  echo "Deployed: $DEPLOYED_DIR"
  echo ""

  # Check if directories exist
  if [ ! -d "$SOURCE_DIR" ]; then
    echo -e "${RED}Error: Source directory not found${NC}"
    exit 1
  fi

  if [ ! -d "$DEPLOYED_DIR" ]; then
    echo -e "${YELLOW}Warning: Deployed directory not found. Run 'push' to deploy.${NC}"
    return
  fi

  local has_drift=false

  printf "%-25s %s\n" "AGENT" "STATUS"
  printf "%-25s %s\n" "-----" "------"

  # Check all source agents
  for agent in $(get_source_agents); do
    local source="$SOURCE_DIR/$agent"
    local deployed="$DEPLOYED_DIR/$agent"

    if [ ! -f "$deployed" ]; then
      printf "%-25s ${YELLOW}%s${NC}\n" "$agent" "NOT DEPLOYED"
      has_drift=true
    elif files_identical "$agent"; then
      printf "%-25s ${GREEN}%s${NC}\n" "$agent" "IN SYNC"
    else
      # Compare timestamps
      local source_time=$(get_mtime "$source")
      local deployed_time=$(get_mtime "$deployed")

      if [ "$source_time" -gt "$deployed_time" ]; then
        printf "%-25s ${YELLOW}%s${NC}\n" "$agent" "SOURCE NEWER"
      else
        printf "%-25s ${RED}%s${NC}\n" "$agent" "DEPLOYED NEWER"
      fi
      has_drift=true
    fi
  done

  # Check for deployed-only agents (not in source)
  for agent in $(get_deployed_agents); do
    if [ ! -f "$SOURCE_DIR/$agent" ]; then
      printf "%-25s ${RED}%s${NC}\n" "$agent" "DEPLOYED ONLY"
      has_drift=true
    fi
  done

  echo ""
  if $has_drift; then
    echo -e "${YELLOW}Drift detected. Use 'diff' to see changes, 'pull' or 'push' to sync.${NC}"
  else
    echo -e "${GREEN}All agents in sync.${NC}"
  fi
}

# Show diff of changed files
cmd_diff() {
  local specific_agent="$1"

  if [ -n "$specific_agent" ]; then
    # Diff specific agent
    local source="$SOURCE_DIR/$specific_agent"
    local deployed="$DEPLOYED_DIR/$specific_agent"

    if [ ! -f "$source" ] && [ ! -f "$deployed" ]; then
      echo -e "${RED}Agent not found: $specific_agent${NC}"
      exit 1
    fi

    echo -e "${BLUE}Diff for $specific_agent${NC}"
    echo "--- source (repo)"
    echo "+++ deployed (~/.claude/agents)"
    echo ""
    diff -u "$source" "$deployed" 2>/dev/null || true
  else
    # Diff all changed agents
    for agent in $(get_source_agents); do
      if ! files_identical "$agent"; then
        echo -e "${BLUE}=== $agent ===${NC}"
        echo "--- source (repo)"
        echo "+++ deployed (~/.claude/agents)"
        diff -u "$SOURCE_DIR/$agent" "$DEPLOYED_DIR/$agent" 2>/dev/null || true
        echo ""
      fi
    done

    # Check for deployed-only
    for agent in $(get_deployed_agents); do
      if [ ! -f "$SOURCE_DIR/$agent" ]; then
        echo -e "${RED}=== $agent (deployed only, not in source) ===${NC}"
        echo "This agent exists only in ~/.claude/agents/"
        echo ""
      fi
    done
  fi
}

# Pull changes from deployed back to source
cmd_pull() {
  local force="$1"

  echo -e "${BLUE}Pulling changes from deployed to source...${NC}"
  echo ""

  local pulled=0

  for agent in $(get_deployed_agents); do
    local source="$SOURCE_DIR/$agent"
    local deployed="$DEPLOYED_DIR/$agent"

    # Skip if files are identical
    if files_identical "$agent"; then
      continue
    fi

    # Check if deployed is newer or source doesn't exist
    if [ ! -f "$source" ]; then
      echo -e "${GREEN}New agent: $agent${NC}"
      if [ "$force" != "-f" ]; then
        read -p "  Pull this new agent? [y/N] " -n 1 -r
        echo
        if [[ ! $REPLY =~ ^[Yy]$ ]]; then
          continue
        fi
      fi
      cp "$deployed" "$source"
      pulled=$((pulled + 1))
    else
      local source_time=$(get_mtime "$source")
      local deployed_time=$(get_mtime "$deployed")

      if [ "$deployed_time" -gt "$source_time" ]; then
        echo -e "${YELLOW}Modified: $agent${NC}"
        if [ "$force" != "-f" ]; then
          read -p "  Pull changes? [y/N] " -n 1 -r
          echo
          if [[ ! $REPLY =~ ^[Yy]$ ]]; then
            continue
          fi
        fi
        cp "$deployed" "$source"
        pulled=$((pulled + 1))
      fi
    fi
  done

  if [ $pulled -eq 0 ]; then
    echo "No changes to pull."
  else
    echo ""
    echo -e "${GREEN}Pulled $pulled agent(s).${NC}"
    echo "Don't forget to commit: cd $SOURCE_DIR && git add . && git commit -m 'Sync agent changes'"
  fi
}

# Push changes from source to deployed
cmd_push() {
  local force="$1"

  echo -e "${BLUE}Pushing changes from source to deployed...${NC}"
  echo ""

  # Create deployed dir if it doesn't exist
  mkdir -p "$DEPLOYED_DIR"

  local pushed=0

  for agent in $(get_source_agents); do
    local source="$SOURCE_DIR/$agent"
    local deployed="$DEPLOYED_DIR/$agent"

    # Skip if files are identical
    if files_identical "$agent"; then
      continue
    fi

    if [ ! -f "$deployed" ]; then
      echo -e "${GREEN}New agent: $agent${NC}"
    else
      echo -e "${YELLOW}Modified: $agent${NC}"
    fi

    if [ "$force" != "-f" ]; then
      read -p "  Push this agent? [y/N] " -n 1 -r
      echo
      if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        continue
      fi
    fi

    cp "$source" "$deployed"
    pushed=$((pushed + 1))
  done

  if [ $pushed -eq 0 ]; then
    echo "No changes to push."
  else
    echo ""
    echo -e "${GREEN}Pushed $pushed agent(s).${NC}"
    echo "Restart Claude Code to load updated agents."
  fi
}

# Show help
cmd_help() {
  echo "Solo Founder Fleet Agent Sync"
  echo ""
  echo "Usage: sync-agents.sh <command> [options]"
  echo ""
  echo "Commands:"
  echo "  status          Show sync status of all agents"
  echo "  diff [agent]    Show diff of changed agents (or specific agent)"
  echo "  pull [-f]       Pull changes from deployed back to source repo"
  echo "  push [-f]       Push changes from source repo to deployed"
  echo ""
  echo "Options:"
  echo "  -f              Force (skip confirmation prompts)"
  echo ""
  echo "Paths:"
  echo "  Source:   $SOURCE_DIR"
  echo "  Deployed: $DEPLOYED_DIR"
}

# Main
case "${1:-status}" in
  status)
    cmd_status
    ;;
  diff)
    cmd_diff "$2"
    ;;
  pull)
    cmd_pull "$2"
    ;;
  push)
    cmd_push "$2"
    ;;
  help|--help|-h)
    cmd_help
    ;;
  *)
    echo -e "${RED}Unknown command: $1${NC}"
    echo ""
    cmd_help
    exit 1
    ;;
esac
