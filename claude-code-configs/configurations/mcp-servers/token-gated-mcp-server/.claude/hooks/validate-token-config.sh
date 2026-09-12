#!/bin/bash

# Hook script to validate token configuration in TypeScript files
# Used in PreToolUse hooks for Edit/Write operations

# Parse the input JSON from CLAUDE_HOOK_DATA
file_path=$(echo "$CLAUDE_HOOK_DATA" | jq -r '.tool_input.file_path // empty')
content=$(echo "$CLAUDE_HOOK_DATA" | jq -r '.tool_input.content // .tool_input.new_string // ""')

# Only process TypeScript files
if [[ ! "$file_path" =~ \.(ts|tsx)$ ]]; then
  exit 0
fi

# Check if content contains token configuration
if echo "$content" | grep -qE 'contractAddress|chainId|tokenId|RadiusMcpSdk'; then
  echo "🔐 Token configuration detected in $file_path"
  
  # Validate contract address format (0x + 40 hex chars)
  if echo "$content" | grep -qE '0x[a-fA-F0-9]{40}'; then
    echo "✅ Valid contract address format"
  else
    if echo "$content" | grep -qE 'contractAddress.*0x'; then
      echo "⚠️  Warning: Invalid contract address format detected"
      echo "   Contract addresses must be 0x followed by 40 hexadecimal characters"
    fi
  fi
  
  # Check for Radius Testnet configuration
  if echo "$content" | grep -q '1223953'; then
    echo "✅ Configured for Radius Testnet (Chain ID: 1223953)"
  fi
  
  # Warn about debug mode
  if echo "$content" | grep -qE 'debug:\s*true'; then
    if [ "$NODE_ENV" = "production" ]; then
      echo "❌ ERROR: Debug mode cannot be enabled in production!"
      echo "   Set debug: false or use process.env.NODE_ENV check"
      exit 2  # Block the operation
    else
      echo "⚠️  Warning: Debug mode is enabled - disable before production"
    fi
  fi
  
  # Check for hardcoded private keys (security check)
  if echo "$content" | grep -qE '0x[a-fA-F0-9]{64}'; then
    echo "🚨 SECURITY WARNING: Possible private key detected!"
    echo "   Never commit private keys to source control"
    echo "   Use environment variables instead"
    # exit 2  # Uncomment to block operation if private key detected
  fi
  
  # Validate token protection pattern
  if echo "$content" | grep -q 'radius.protect'; then
    echo "✅ Token protection implemented"
    
    # Check if __evmauth is in parameters
    if echo "$content" | grep -q '__evmauth.*z\.any'; then
      echo "✅ __evmauth parameter included in schema"
    else
      echo "⚠️  Reminder: Include __evmauth in tool parameters:"
      echo "   __evmauth: z.any().optional()"
    fi
  fi
fi

exit 0