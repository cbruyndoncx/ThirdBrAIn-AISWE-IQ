#!/bin/bash
# Initialize state files for a new project

PROJECT_DIR=${1:-.}

# Resolve to absolute path and normalize (removes trailing slashes, resolves .)
PROJECT_DIR=$(cd "$PROJECT_DIR" && pwd)

STATE_DIR="$PROJECT_DIR/.claude/state"
PROJECT_NAME=$(basename "$PROJECT_DIR")

mkdir -p "$STATE_DIR"

for agent in chief-of-staff eng product design marketing sales content custdev qa devops; do
  if [ ! -f "$STATE_DIR/$agent.md" ]; then
    # Convert agent name to title case for display
    display_name=$(echo "$agent" | sed 's/-/ /g' | awk '{for(i=1;i<=NF;i++) $i=toupper(substr($i,1,1)) tolower(substr($i,2))}1')

    cat > "$STATE_DIR/$agent.md" << EOF
# ${display_name} State - ${PROJECT_NAME}

## Last Updated
$(date -u +"%Y-%m-%d %H:%M UTC")

## Current Focus
_Not yet initialized. First session should set objectives._

## Active Work
| Task | Status | Notes |
|------|--------|-------|
| - | - | - |

## Blockers
_None yet_

## Recent Decisions
_None yet_

## Context for Next Session
_First session—start by understanding project goals and current state._
EOF
    echo "Created $STATE_DIR/$agent.md"
  fi
done

# Ensure .last-sync-sha is gitignored
GITIGNORE="$PROJECT_DIR/.gitignore"
if [ -f "$GITIGNORE" ]; then
  if ! grep -q ".claude/state/.last-sync-sha" "$GITIGNORE"; then
    echo "" >> "$GITIGNORE"
    echo "# Session sync markers (auto-generated)" >> "$GITIGNORE"
    echo ".claude/state/.last-sync-sha" >> "$GITIGNORE"
    echo ".claude/state/.last-sync-fingerprint" >> "$GITIGNORE"
    echo "Added .last-sync-sha to .gitignore"
  fi
fi

echo "State initialized for $PROJECT_NAME"
