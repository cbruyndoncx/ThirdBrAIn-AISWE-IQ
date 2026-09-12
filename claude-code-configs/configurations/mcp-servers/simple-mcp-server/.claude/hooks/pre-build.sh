#!/bin/bash

# Pre-Build Hook for Simple MCP Server
# Runs before building for production

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

echo -e "${BLUE}🔨 Pre-Build Hook${NC}"
echo "======================================"

# Check for uncommitted changes
if git diff --quiet && git diff --staged --quiet; then
    echo -e "${GREEN}✓ Working directory clean${NC}"
else
    echo -e "${YELLOW}⚠ Warning: Uncommitted changes detected${NC}"
    git status --short
fi

# Lint check
echo -e "\n${YELLOW}🔍 Running lint check...${NC}"
if npx eslint src --ext .ts 2>/dev/null; then
    echo -e "${GREEN}  ✓ Linting passed${NC}"
else
    echo -e "${RED}  ✗ Linting failed${NC}"
    echo "  Run 'npm run lint:fix' to fix issues"
    exit 1
fi

# Type validation
echo -e "\n${YELLOW}📝 Running type check...${NC}"
if npx tsc --noEmit; then
    echo -e "${GREEN}  ✓ Type checking passed${NC}"
else
    echo -e "${RED}  ✗ Type checking failed${NC}"
    exit 1
fi

# Test suite
echo -e "\n${YELLOW}🧪 Running tests...${NC}"
if npm test 2>/dev/null; then
    echo -e "${GREEN}  ✓ All tests passed${NC}"
else
    echo -e "${RED}  ✗ Tests failed${NC}"
    exit 1
fi

# Dependency audit
echo -e "\n${YELLOW}🔒 Checking dependencies...${NC}"
AUDIT_RESULT=$(npm audit --production 2>&1)
if echo "$AUDIT_RESULT" | grep -q "found 0 vulnerabilities"; then
    echo -e "${GREEN}  ✓ No vulnerabilities found${NC}"
else
    echo -e "${YELLOW}  ⚠ Security vulnerabilities detected${NC}"
    echo "  Run 'npm audit fix' to resolve"
fi

# Version validation
echo -e "\n${YELLOW}🏷️ Checking version...${NC}"
PACKAGE_VERSION=$(node -p "require('./package.json').version")
echo "  Current version: $PACKAGE_VERSION"

# Check if version tag exists
if git rev-parse "v$PACKAGE_VERSION" >/dev/null 2>&1; then
    echo -e "${GREEN}  ✓ Version tag exists${NC}"
else
    echo -e "${YELLOW}  ⚠ Version tag v$PACKAGE_VERSION not found${NC}"
    echo "  Create with: git tag v$PACKAGE_VERSION"
fi

# Check package.json required fields
echo -e "\n${YELLOW}📦 Validating package.json...${NC}"
NAME=$(node -p "require('./package.json').name" 2>/dev/null)
DESCRIPTION=$(node -p "require('./package.json').description" 2>/dev/null)
MAIN=$(node -p "require('./package.json').main" 2>/dev/null)

if [ -z "$NAME" ]; then
    echo -e "${RED}  ✗ Missing 'name' field${NC}"
    exit 1
fi

if [ -z "$DESCRIPTION" ]; then
    echo -e "${YELLOW}  ⚠ Missing 'description' field${NC}"
fi

if [ -z "$MAIN" ]; then
    echo -e "${YELLOW}  ⚠ Missing 'main' field${NC}"
fi

echo -e "${GREEN}  ✓ Package metadata valid${NC}"

# MCP specific checks
echo -e "\n${YELLOW}🔌 Checking MCP implementation...${NC}"

# Check for required MCP files
if [ -f "src/index.ts" ]; then
    echo -e "${GREEN}  ✓ Entry point exists${NC}"
else
    echo -e "${RED}  ✗ Missing src/index.ts${NC}"
    exit 1
fi

# Count capabilities
TOOL_COUNT=0
RESOURCE_COUNT=0
PROMPT_COUNT=0

if [ -d "src/tools" ]; then
    TOOL_COUNT=$(find src/tools -name "*.ts" -not -name "index.ts" | wc -l)
fi

if [ -d "src/resources" ]; then
    RESOURCE_COUNT=$(find src/resources -name "*.ts" -not -name "index.ts" | wc -l)
fi

if [ -d "src/prompts" ]; then
    PROMPT_COUNT=$(find src/prompts -name "*.ts" -not -name "index.ts" | wc -l)
fi

echo "  Capabilities:"
echo "    - Tools: $TOOL_COUNT"
echo "    - Resources: $RESOURCE_COUNT"
echo "    - Prompts: $PROMPT_COUNT"

if [ $TOOL_COUNT -eq 0 ] && [ $RESOURCE_COUNT -eq 0 ] && [ $PROMPT_COUNT -eq 0 ]; then
    echo -e "${YELLOW}  ⚠ No MCP capabilities implemented${NC}"
fi

# Final summary
echo ""
echo "======================================"
echo -e "${GREEN}✅ Pre-build checks complete${NC}"
echo "Ready to build for production!"
echo ""
echo "Next steps:"
echo "  1. npm run build"
echo "  2. npm test"
echo "  3. npm publish (if deploying to npm)"
