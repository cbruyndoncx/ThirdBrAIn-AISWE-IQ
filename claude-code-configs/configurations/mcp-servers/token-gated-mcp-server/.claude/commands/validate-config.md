---
allowed-tools: Read, Bash, Grep
description: Validate token-gating configuration and environment setup
---

## Validate Token-Gating Configuration

Comprehensive validation of your token-gated MCP server configuration.

## Validation Checks

### 1. Environment Variables

```bash
# Check required variables
!echo "=== Environment Configuration ==="
!echo "Contract Address: ${EVMAUTH_CONTRACT_ADDRESS:-❌ NOT SET}"
!echo "Chain ID: ${EVMAUTH_CHAIN_ID:-❌ NOT SET}"
!echo "RPC URL: ${EVMAUTH_RPC_URL:-❌ NOT SET}"
!echo "Token ID: ${EVMAUTH_TOKEN_ID:-❌ NOT SET}"
!echo "Debug Mode: ${DEBUG:-✅ false (good for production)}"
!echo "Node Environment: ${NODE_ENV:-⚠️ NOT SET}"
```

### 2. Contract Address Validation

- Check format: 0x followed by 40 hexadecimal characters
- Verify it's a valid Ethereum address
- For testnet: Should be `0x5448Dc20ad9e0cDb5Dd0db25e814545d1aa08D96`

### 3. Chain ID Validation

- Should be numeric
- For Radius Testnet: 1223953
- Must match the network your contract is deployed on

### 4. RPC Connection Test

```bash
# Test RPC endpoint
!curl -s -X POST ${EVMAUTH_RPC_URL:-https://rpc.testnet.radiustech.xyz} \
  -H "Content-Type: application/json" \
  -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' | \
  jq -r 'if .result then "✅ RPC Connected - Chain: \(.result)" else "❌ RPC Connection Failed" end'
```

### 5. Dependencies Check

```bash
# Verify required packages
!echo "=== Required Dependencies ==="
!npm list fastmcp 2>/dev/null | grep fastmcp || echo "❌ fastmcp not installed"
!npm list @radiustechsystems/mcp-sdk 2>/dev/null | grep radius || echo "❌ Radius SDK not installed"
!npm list zod 2>/dev/null | grep zod || echo "❌ zod not installed"
!npm list viem 2>/dev/null | grep viem || echo "❌ viem not installed"
```

### 6. TypeScript Configuration

```bash
# Check TypeScript setup
![ -f "tsconfig.json" ] && echo "✅ tsconfig.json exists" || echo "❌ tsconfig.json missing"
!npx tsc --version 2>/dev/null || echo "❌ TypeScript not installed"
```

### 7. Server File Analysis

- Check for RadiusMcpSdk initialization
- Verify radius.protect() usage
- Ensure __evmauth parameter in schemas
- Validate error handling

### 8. Security Checks

```bash
# Security validation
!echo "=== Security Checks ==="
!grep -r "debug.*true" --include="*.ts" --include="*.js" . 2>/dev/null && echo "⚠️ Debug mode enabled in code" || echo "✅ No hardcoded debug mode"
!grep -r "0x[a-fA-F0-9]\{64\}" --include="*.ts" --include="*.js" . 2>/dev/null && echo "⚠️ Possible private key in code" || echo "✅ No private keys detected"
![ -f ".env" ] && [ ! -f ".gitignore" ] && echo "⚠️ .env exists but no .gitignore" || echo "✅ Environment files protected"
```

## Validation Report

Generate a comprehensive report with:

### ✅ Passed Checks

- List all successful validations

### ⚠️ Warnings

- Non-critical issues to address

### ❌ Failed Checks

- Critical issues that must be fixed

### 📋 Recommendations

1. Configuration improvements
2. Security enhancements
3. Performance optimizations
4. Best practices to follow

## Next Steps

Based on validation results, provide:

1. Immediate fixes required
2. Configuration commands to run
3. Files to update
4. Testing recommendations
