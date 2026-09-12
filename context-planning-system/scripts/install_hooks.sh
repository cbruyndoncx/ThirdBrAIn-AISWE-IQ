#!/usr/bin/env bash
# Install git hooks for automatic project context updates

set -e

CONTEXT_ROOT="$(git rev-parse --show-toplevel)"
cd "$CONTEXT_ROOT"

echo "🔧 Installing git hooks..."

# Copy hooks from .githooks to .git/hooks
for hook in .githooks/post-*; do
    if [ -f "$hook" ]; then
        hook_name=$(basename "$hook")
        cp "$hook" ".git/hooks/$hook_name"
        chmod +x ".git/hooks/$hook_name"
        echo "  ✅ Installed: $hook_name"
    fi
done

echo ""
echo "✅ Git hooks installed successfully!"
echo ""
echo "Hooks will now run automatically on:"
echo "  - git commit   (updates changed projects)"
echo "  - git pull     (updates changed projects)"
echo "  - git checkout (updates when switching branches)"
