#!/bin/bash

# Development Watch Hook for Simple MCP Server
# Automatically triggered on TypeScript file changes

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}🔄 Development Watch Hook Triggered${NC}"

# Get the modified file
MODIFIED_FILE="$1"

# Skip if not a TypeScript file
if [[ ! "$MODIFIED_FILE" =~ \.ts$ ]]; then
    exit 0
fi

# Skip node_modules and dist
if [[ "$MODIFIED_FILE" =~ node_modules|dist|coverage ]]; then
    exit 0
fi

echo "📝 File changed: $MODIFIED_FILE"

# Type checking
echo -e "${YELLOW}✅ Running type check...${NC}"
if npx tsc --noEmit 2>/dev/null; then
    echo -e "${GREEN}  ✓ Type checking passed${NC}"
else
    echo -e "${RED}  ✗ Type checking failed${NC}"
    exit 1
fi

# Format with prettier
if command -v prettier &> /dev/null; then
    echo -e "${YELLOW}🎨 Formatting with Prettier...${NC}"
    npx prettier --write "$MODIFIED_FILE" 2>/dev/null || true
    echo -e "${GREEN}  ✓ Formatted${NC}"
fi

# Lint with ESLint
if [ -f .eslintrc.json ] || [ -f .eslintrc.js ]; then
    echo -e "${YELLOW}🔍 Linting with ESLint...${NC}"
    if npx eslint "$MODIFIED_FILE" --fix 2>/dev/null; then
        echo -e "${GREEN}  ✓ Linting passed${NC}"
    else
        echo -e "${YELLOW}  ⚠ Linting warnings${NC}"
    fi
fi

# Run tests if it's a test file or if the corresponding test exists
if [[ "$MODIFIED_FILE" =~ \.test\.ts$ ]] || [[ "$MODIFIED_FILE" =~ \.spec\.ts$ ]]; then
    echo -e "${YELLOW}🧪 Running tests for $MODIFIED_FILE...${NC}"
    if npx vitest run "$MODIFIED_FILE" 2>/dev/null; then
        echo -e "${GREEN}  ✓ Tests passed${NC}"
    else
        echo -e "${RED}  ✗ Tests failed${NC}"
        exit 1
    fi
else
    # Check if corresponding test file exists
    TEST_FILE="${MODIFIED_FILE%.ts}.test.ts"
    TEST_FILE_SPEC="${MODIFIED_FILE%.ts}.spec.ts"
    
    if [ -f "$TEST_FILE" ]; then
        echo -e "${YELLOW}🧪 Running related tests...${NC}"
        npx vitest run "$TEST_FILE" 2>/dev/null || true
    elif [ -f "$TEST_FILE_SPEC" ]; then
        echo -e "${YELLOW}🧪 Running related tests...${NC}"
        npx vitest run "$TEST_FILE_SPEC" 2>/dev/null || true
    fi
fi

# Update tool/resource counts if applicable
if [[ "$MODIFIED_FILE" =~ src/tools/ ]] || [[ "$MODIFIED_FILE" =~ src/resources/ ]] || [[ "$MODIFIED_FILE" =~ src/prompts/ ]]; then
    echo -e "${YELLOW}📊 Updating capability counts...${NC}"
    
    TOOL_COUNT=$(find src/tools -name "*.ts" -not -name "index.ts" 2>/dev/null | wc -l || echo 0)
    RESOURCE_COUNT=$(find src/resources -name "*.ts" -not -name "index.ts" 2>/dev/null | wc -l || echo 0)
    PROMPT_COUNT=$(find src/prompts -name "*.ts" -not -name "index.ts" 2>/dev/null | wc -l || echo 0)
    
    echo "  Tools: $TOOL_COUNT"
    echo "  Resources: $RESOURCE_COUNT"
    echo "  Prompts: $PROMPT_COUNT"
fi

echo -e "${GREEN}✅ Development checks complete${NC}"
