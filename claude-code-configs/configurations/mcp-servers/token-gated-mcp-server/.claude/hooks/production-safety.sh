#!/bin/bash

# Hook script for production safety checks
# Used in Stop hooks to provide reminders and warnings

# Check environment
env_mode="${NODE_ENV:-development}"
debug_mode="${DEBUG:-false}"
chain_id="${EVMAUTH_CHAIN_ID:-not_set}"

# Production safety checks
if [ "$env_mode" = "production" ]; then
  echo "🚨 PRODUCTION ENVIRONMENT DETECTED"
  
  # Check debug mode
  if [ "$debug_mode" = "true" ]; then
    echo "❌ CRITICAL: Debug mode is enabled in production!"
    echo "   Set DEBUG=false immediately"
  fi
  
  # Verify mainnet configuration
  if [ "$chain_id" = "1223953" ]; then
    echo "⚠️  Using Radius Testnet in production environment"
    echo "   Switch to mainnet configuration if deploying to production"
  fi
  
  # Check for .env file
  if [ -f ".env" ] && [ ! -f ".env.production" ]; then
    echo "⚠️  Using .env file - ensure production values are set"
  fi
else
  # Development environment reminders
  echo "ℹ️  Environment: $env_mode"
  
  if [ "$debug_mode" = "true" ]; then
    echo "🔍 Debug mode enabled (OK for development)"
  fi
  
  if [ "$chain_id" = "1223953" ]; then
    echo "🔗 Using Radius Testnet (Chain ID: 1223953)"
  fi
fi

# Check for uncommitted changes
if command -v git &> /dev/null; then
  if [ -d ".git" ]; then
    uncommitted=$(git status --porcelain 2>/dev/null | wc -l)
    if [ "$uncommitted" -gt 0 ]; then
      echo "📝 You have $uncommitted uncommitted change(s)"
      
      # Check for changes to sensitive files
      if git status --porcelain 2>/dev/null | grep -qE '\.env|private|secret|key'; then
        echo "⚠️  Sensitive files may have been modified - review before committing"
      fi
    fi
  fi
fi

# Token configuration summary
if [ "$EVMAUTH_CONTRACT_ADDRESS" ]; then
  echo "🔐 Token Gate Active:"
  echo "   Contract: ${EVMAUTH_CONTRACT_ADDRESS:0:10}...${EVMAUTH_CONTRACT_ADDRESS: -8}"
  echo "   Token ID: ${EVMAUTH_TOKEN_ID:-1}"
fi

# Server status check
if lsof -i :3000 &>/dev/null; then
  echo "✅ MCP Server running on port 3000"
elif lsof -i :${PORT:-3000} &>/dev/null; then
  echo "✅ MCP Server running on port ${PORT}"
fi

# Final reminders based on recent activity
if [ -f "$HOME/.claude/logs/token-gate-$(date +%Y%m%d).log" ]; then
  recent_fastmcp=$(grep -c "FastMCP" "$HOME/.claude/logs/token-gate-$(date +%Y%m%d).log" 2>/dev/null || echo 0)
  recent_ngrok=$(grep -c "ngrok" "$HOME/.claude/logs/token-gate-$(date +%Y%m%d).log" 2>/dev/null || echo 0)
  
  if [ "$recent_fastmcp" -gt 0 ] || [ "$recent_ngrok" -gt 0 ]; then
    echo "📊 Today's activity: $recent_fastmcp FastMCP commands, $recent_ngrok ngrok sessions"
  fi
fi

# Success message if everything looks good
all_good=true
[ "$env_mode" = "production" ] && [ "$debug_mode" = "true" ] && all_good=false
[ "$uncommitted" -gt 0 ] && all_good=false

if [ "$all_good" = true ] && [ "$env_mode" != "production" ]; then
  echo "✨ Development environment properly configured!"
fi

exit 0