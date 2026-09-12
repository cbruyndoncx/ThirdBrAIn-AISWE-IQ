#!/bin/bash

# Test Runner Hook for Simple MCP Server
# Enhanced test execution with coverage and protocol validation

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
MAGENTA='\033[0;35m'
NC='\033[0m' # No Color

echo -e "${BLUE}🧪 Test Runner Hook${NC}"
echo "======================================"

# Parse test type from arguments
TEST_TYPE="${1:-all}"
WATCH_MODE="${2:-false}"

# Function to run tests
run_tests() {
    local type=$1
    local title=$2
    
    echo -e "\n${YELLOW}Running $title...${NC}"
    
    if [ "$type" = "unit" ]; then
        TEST_CMD="npx vitest run tests/unit"
    elif [ "$type" = "integration" ]; then
        TEST_CMD="npx vitest run tests/integration"
    else
        TEST_CMD="npx vitest run"
    fi
    
    if [ "$WATCH_MODE" = "true" ]; then
        TEST_CMD="${TEST_CMD/run/}"
    fi
    
    if $TEST_CMD; then
        echo -e "${GREEN}  ✓ $title passed${NC}"
        return 0
    else
        echo -e "${RED}  ✗ $title failed${NC}"
        return 1
    fi
}

# Function to check MCP protocol compliance
check_protocol_compliance() {
    echo -e "\n${YELLOW}🔌 Checking MCP Protocol Compliance...${NC}"
    
    # Check server initialization
    echo "  Checking server initialization..."
    if node -e "require('./dist/index.js')" 2>/dev/null; then
        echo -e "${GREEN}    ✓ Server module loads${NC}"
    else
        echo -e "${YELLOW}    ⚠ Server not built (run 'npm run build')${NC}"
    fi
    
    # Check for required handlers
    echo "  Checking protocol handlers..."
    
    # This would normally check the actual implementation
    # For now, we'll check if the files exist
    if [ -f "src/index.ts" ]; then
        if grep -q "ListToolsRequestSchema\|ListResourcesRequestSchema\|ListPromptsRequestSchema" src/index.ts 2>/dev/null; then
            echo -e "${GREEN}    ✓ Protocol handlers found${NC}"
        else
            echo -e "${YELLOW}    ⚠ Some protocol handlers may be missing${NC}"
        fi
    fi
    
    # Check capabilities
    echo "  Checking capabilities..."
    local has_capability=false
    
    if [ -d "src/tools" ] && [ "$(ls -A src/tools 2>/dev/null)" ]; then
        echo -e "${GREEN}    ✓ Tools capability${NC}"
        has_capability=true
    fi
    
    if [ -d "src/resources" ] && [ "$(ls -A src/resources 2>/dev/null)" ]; then
        echo -e "${GREEN}    ✓ Resources capability${NC}"
        has_capability=true
    fi
    
    if [ -d "src/prompts" ] && [ "$(ls -A src/prompts 2>/dev/null)" ]; then
        echo -e "${GREEN}    ✓ Prompts capability${NC}"
        has_capability=true
    fi
    
    if [ "$has_capability" = false ]; then
        echo -e "${YELLOW}    ⚠ No capabilities implemented yet${NC}"
    fi
}

# Function to generate coverage report
generate_coverage() {
    echo -e "\n${YELLOW}📊 Generating Coverage Report...${NC}"
    
    if npx vitest run --coverage 2>/dev/null; then
        echo -e "${GREEN}  ✓ Coverage report generated${NC}"
        
        # Parse coverage summary if available
        if [ -f "coverage/coverage-summary.json" ]; then
            echo "  Coverage Summary:"
            node -e "
                const coverage = require('./coverage/coverage-summary.json');
                const total = coverage.total;
                const metrics = ['statements', 'branches', 'functions', 'lines'];
                metrics.forEach(metric => {
                    const pct = total[metric].pct;
                    const color = pct >= 80 ? '\\033[0;32m' : pct >= 60 ? '\\033[1;33m' : '\\033[0;31m';
                    console.log('    ' + metric + ': ' + color + pct.toFixed(1) + '%\\033[0m');
                });
            " 2>/dev/null || echo "    (Could not parse coverage summary)"
        fi
        
        echo "  View detailed report: coverage/index.html"
    else
        echo -e "${YELLOW}  ⚠ Coverage generation failed${NC}"
    fi
}

# Main execution
echo "Test configuration:"
echo "  Type: $TEST_TYPE"
echo "  Watch: $WATCH_MODE"

# Pre-test checks
echo -e "\n${YELLOW}📋 Pre-test checks...${NC}"

# Check if test framework is installed
if ! command -v vitest &> /dev/null && ! npx vitest --version &> /dev/null; then
    echo -e "${RED}  ✗ Vitest not installed${NC}"
    echo "  Install with: npm install -D vitest"
    exit 1
fi

# Check if test directory exists
if [ ! -d "tests" ] && [ ! -d "src/__tests__" ]; then
    echo -e "${YELLOW}  ⚠ No test directory found${NC}"
    echo "  Create tests in 'tests/' directory"
fi

# Run appropriate tests
case $TEST_TYPE in
    unit)
        run_tests "unit" "Unit Tests"
        ;;
    integration)
        run_tests "integration" "Integration Tests"
        ;;
    coverage)
        generate_coverage
        ;;
    protocol)
        check_protocol_compliance
        ;;
    all)
        FAILED=false
        
        run_tests "unit" "Unit Tests" || FAILED=true
        run_tests "integration" "Integration Tests" || FAILED=true
        check_protocol_compliance
        
        if [ "$FAILED" = true ]; then
            echo -e "\n${RED}❌ Some tests failed${NC}"
            exit 1
        fi
        ;;
    *)
        echo -e "${RED}Unknown test type: $TEST_TYPE${NC}"
        echo "Valid options: unit, integration, coverage, protocol, all"
        exit 1
        ;;
esac

# Test summary
echo ""
echo "======================================"

if [ "$WATCH_MODE" = "true" ]; then
    echo -e "${BLUE}👁️ Watching for changes...${NC}"
    echo "Press Ctrl+C to stop"
else
    echo -e "${GREEN}✅ Test run complete${NC}"
    
    # Provide helpful next steps
    echo ""
    echo "Next steps:"
    echo "  • Fix any failing tests"
    echo "  • Run with coverage: npm test -- coverage"
    echo "  • Test with MCP Inspector: npx @modelcontextprotocol/inspector"
fi
