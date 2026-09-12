---
allowed-tools: Read, Bash, Grep, WebFetch
description: Debug proof verification issues and authentication errors
---

## Debug Proof Verification

Analyze and debug authentication proof issues in your token-gated MCP server.

## Debugging Process

1. **Check Recent Errors**
   - Search for EVMAUTH errors: !`grep -r "EVMAUTH" . --include="*.log" --include="*.ts" | tail -20`
   - Find proof-related issues: !`grep -r "proof\|PROOF" . --include="*.log" | tail -20`

2. **Validate Configuration**

   ```bash
   # Check all required environment variables
   !echo "=== Token Gate Configuration ==="
   !echo "Contract Address: ${EVMAUTH_CONTRACT_ADDRESS:-NOT SET}"
   !echo "Chain ID: ${EVMAUTH_CHAIN_ID:-NOT SET}"
   !echo "RPC URL: ${EVMAUTH_RPC_URL:-NOT SET}"
   !echo "Token ID: ${EVMAUTH_TOKEN_ID:-NOT SET}"
   !echo "Debug Mode: ${DEBUG:-false}"
   !echo "Environment: ${NODE_ENV:-development}"
   ```

3. **Test RPC Connection**

   ```bash
   # Verify RPC endpoint is accessible
   !curl -s -X POST ${EVMAUTH_RPC_URL:-https://rpc.testnet.radiustech.xyz} \
     -H "Content-Type: application/json" \
     -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' | jq '.'
   ```

4. **Analyze Proof Structure**
   Check for common proof issues:
   - Missing __evmauth parameter
   - Expired timestamp (> 30 seconds)
   - Invalid signature format (not 0x + 130 hex chars)
   - Chain ID mismatch
   - Contract address mismatch
   - Invalid nonce format

5. **Debug Token Verification**
   - Check if RPC calls are succeeding
   - Verify token balance queries
   - Test cache behavior
   - Validate multi-token logic

## Common Issues and Solutions

### EVMAUTH_PROOF_MISSING

- **Cause**: No __evmauth in request
- **Fix**: Ensure parameter is included in tool schema

### PROOF_EXPIRED

- **Cause**: Proof older than 30 seconds
- **Fix**: Request fresh proof from Radius MCP Server

### CHAIN_MISMATCH

- **Cause**: Proof for different chain
- **Fix**: Ensure SDK and proof use same chain ID (1223953 for testnet)

### SIGNER_MISMATCH

- **Cause**: Signature doesn't match wallet
- **Fix**: Verify signature recovery process

### PAYMENT_REQUIRED

- **Cause**: User lacks required tokens
- **Fix**: Use authenticate_and_purchase to obtain tokens

## Generate Debug Report

Create a comprehensive debug report including:

1. Current configuration status
2. Recent error patterns
3. Proof validation results
4. Token verification status
5. Recommended fixes

Enable debug mode temporarily if needed:

```typescript
const radius = new RadiusMcpSdk({
  contractAddress: process.env.EVMAUTH_CONTRACT_ADDRESS,
  debug: true // Temporary for debugging
});
```
