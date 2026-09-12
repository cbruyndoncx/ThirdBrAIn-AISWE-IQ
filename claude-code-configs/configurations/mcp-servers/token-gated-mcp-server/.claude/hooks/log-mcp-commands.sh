#!/bin/bash

# Hook script to log MCP-related commands for debugging
# Used in PreToolUse hooks for Bash tool

# Parse the command from input
command=$(echo "$CLAUDE_HOOK_DATA" | jq -r '.tool_input.command // empty')
description=$(echo "$CLAUDE_HOOK_DATA" | jq -r '.tool_input.description // "No description"')

# Exit if no command
if [ -z "$command" ]; then
  exit 0
fi

# Create log directory if it doesn't exist
LOG_DIR="$HOME/.claude/logs"
mkdir -p "$LOG_DIR"

# Log file with date
LOG_FILE="$LOG_DIR/token-gate-$(date +%Y%m%d).log"

# Timestamp for log entry
timestamp=$(date '+%Y-%m-%d %H:%M:%S')

# Log FastMCP commands
if [[ "$command" == *"fastmcp"* ]]; then
  echo "[$timestamp] FastMCP: $command - $description" >> "$LOG_FILE"
  echo "🚀 Running FastMCP command..."
  
  # Provide helpful hints
  if [[ "$command" == *"dev"* ]]; then
    echo "💡 Tip: Use 'npx fastmcp inspect' for visual debugging"
  fi
fi

# Log ngrok commands
if [[ "$command" == *"ngrok"* ]]; then
  echo "[$timestamp] ngrok: $command" >> "$LOG_FILE"
  echo "🌐 Setting up ngrok tunnel..."
  echo "💡 Remember to use the HTTPS URL with /mcp endpoint in claude.ai"
fi

# Log npm/node commands related to MCP
if [[ "$command" == *"npm"* ]] || [[ "$command" == *"node"* ]] || [[ "$command" == *"tsx"* ]]; then
  if [[ "$command" == *"radius"* ]] || [[ "$command" == *"mcp"* ]] || [[ "$command" == *"server"* ]]; then
    echo "[$timestamp] MCP Server: $command" >> "$LOG_FILE"
  fi
fi

# Log token configuration checks
if [[ "$command" == *"EVMAUTH"* ]] || [[ "$command" == *"echo"* ]]; then
  if [[ "$command" == *"CONTRACT"* ]] || [[ "$command" == *"CHAIN"* ]] || [[ "$command" == *"TOKEN"* ]]; then
    echo "[$timestamp] Config Check: $command" >> "$LOG_FILE"
    echo "🔍 Checking token configuration..."
  fi
fi

# Log RPC tests
if [[ "$command" == *"curl"* ]] && [[ "$command" == *"rpc"* ]]; then
  echo "[$timestamp] RPC Test: $command" >> "$LOG_FILE"
  echo "🔗 Testing RPC connection..."
fi

# Security check - warn about potentially dangerous commands
if [[ "$command" == *"rm -rf"* ]] || [[ "$command" == *"sudo rm"* ]]; then
  echo "⚠️  DANGER: Destructive command detected!"
  echo "[$timestamp] BLOCKED: $command" >> "$LOG_FILE"
  exit 2  # Block the command
fi

# Warn about npm publish in development
if [[ "$command" == *"npm publish"* ]]; then
  echo "⚠️  WARNING: About to publish to npm registry!"
  echo "   Ensure version is updated and changes are committed"
  echo "[$timestamp] NPM Publish: $command" >> "$LOG_FILE"
  
  if [ "$NODE_ENV" != "production" ]; then
    echo "❌ Blocking npm publish in non-production environment"
    exit 2
  fi
fi

exit 0