---
allowed-tools: Bash, Read, Write, TodoWrite
description: Test the complete authentication flow end-to-end
argument-hint: "[tool-name] [token-id]"
---

## Test Authentication Flow

Test the complete token-gated authentication flow for the specified tool.

Tool: $ARGUMENTS

## Testing Steps

1. **Check Current Configuration**
   - Verify environment variables: !`echo "Contract: $EVMAUTH_CONTRACT_ADDRESS, Chain: $EVMAUTH_CHAIN_ID"`
   - Check RPC connection: !`curl -s -X POST $EVMAUTH_RPC_URL -H "Content-Type: application/json" -d '{"jsonrpc":"2.0","method":"eth_chainId","params":[],"id":1}' | jq -r '.result'`

2. **Start MCP Server**
   - Run the server if not already running
   - Note the port and endpoint

3. **Simulate Tool Call Without Auth**
   - Call the protected tool without __evmauth
   - Verify EVMAUTH_PROOF_MISSING error
   - Check error includes requiredTokens

4. **Simulate Authentication**
   - Mock authenticate_and_purchase response
   - Generate sample proof structure
   - Verify proof format is correct

5. **Test With Valid Proof**
   - Call tool with __evmauth parameter
   - Verify successful execution or PAYMENT_REQUIRED

6. **Test Error Scenarios**
   - Expired proof (> 30 seconds old)
   - Wrong chain ID
   - Invalid signature format
   - Missing required fields

## Create Test Script

Generate a test script that validates:

- Token protection is properly configured
- Error messages are AI-friendly
- Authentication flow works end-to-end
- Caching behaves correctly

## Expected Results

✅ **Success Criteria:**

- Tool rejects calls without auth
- Error messages guide to authenticate_and_purchase
- Valid proofs are accepted
- Token ownership is properly verified

❌ **Common Failures:**

- Chain ID mismatch
- Contract address not configured
- RPC connection issues
- Debug mode enabled in production

Generate comprehensive test results and recommendations.
