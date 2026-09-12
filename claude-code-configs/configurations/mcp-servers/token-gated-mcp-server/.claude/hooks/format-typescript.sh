#!/bin/bash

# Hook script to format TypeScript files after editing
# Used in PostToolUse hooks for Edit/Write operations

# Parse the input JSON
file_path=$(echo "$CLAUDE_HOOK_DATA" | jq -r '.tool_input.file_path // empty')

# Exit if no file path
if [ -z "$file_path" ]; then
  exit 0
fi

# Only process TypeScript/JavaScript files
if [[ "$file_path" =~ \.(ts|tsx|js|jsx)$ ]]; then
  # Check if prettier is available
  if command -v npx &> /dev/null && [ -f "package.json" ]; then
    # Check if prettier is installed
    if npm list prettier --depth=0 &>/dev/null || npm list -g prettier --depth=0 &>/dev/null; then
      echo "🎨 Formatting $file_path with Prettier..."
      npx prettier --write "$file_path" 2>/dev/null
      
      if [ $? -eq 0 ]; then
        echo "✅ Formatted successfully"
      else
        echo "⚠️  Prettier formatting failed (non-critical)"
      fi
    fi
  fi
  
  # Additional validation for server files
  if [[ "$file_path" =~ (server|index)\.(ts|js)$ ]]; then
    # Check for token protection
    if grep -q 'radius.protect' "$file_path" 2>/dev/null; then
      echo "✅ Token protection detected in $file_path"
      
      # Count protected tools
      tool_count=$(grep -c 'radius.protect' "$file_path" 2>/dev/null)
      echo "   Found $tool_count protected tool(s)"
    fi
    
    # Check for proper FastMCP setup
    if grep -q 'FastMCP' "$file_path" 2>/dev/null; then
      echo "✅ FastMCP server configured"
    fi
    
    # Warn about missing error handling
    if ! grep -q 'try\|catch\|throw' "$file_path" 2>/dev/null; then
      echo "⚠️  Consider adding error handling to $file_path"
    fi
  fi
fi

exit 0