---
allowed-tools: Bash, Read, Write
description: Deploy token-gated MCP server locally with ngrok for testing
---

## Deploy Locally with ngrok

Set up and deploy your token-gated MCP server locally with ngrok for testing with claude.ai.

## Deployment Steps

1. **Pre-deployment Checks**
   - Verify all dependencies installed: !`npm list fastmcp @radiustechsystems/mcp-sdk zod 2>/dev/null | grep -E "fastmcp|radius|zod"`
   - Check TypeScript compilation: !`npx tsc --noEmit`
   - Validate environment configuration

2. **Start the MCP Server**

   ```bash
   # Start server in development mode
   npm run dev
   ```

   Server should start on port 3000 (or configured PORT)

3. **Set Up ngrok Tunnel**

   ```bash
   # Install ngrok if needed
   # brew install ngrok (macOS)
   # or download from https://ngrok.com
   
   # Start ngrok tunnel
   ngrok http 3000
   ```

4. **Configure claude.ai**
   - Copy the HTTPS URL from ngrok (e.g., <https://abc123.ngrok.io>)
   - In claude.ai:
     1. Click the 🔌 connection icon
     2. Add MCP server
     3. Enter URL: `https://abc123.ngrok.io/mcp`
     4. Test connection

5. **Verify Token Protection**
   - Try calling a protected tool
   - Should receive EVMAUTH_PROOF_MISSING error
   - Error should guide to authenticate_and_purchase

## Testing Checklist

- [ ] Server starts without errors
- [ ] ngrok tunnel established
- [ ] claude.ai can connect
- [ ] Tools appear in claude.ai
- [ ] Token protection working
- [ ] Error messages are helpful
- [ ] Authentication flow completes

## Troubleshooting

### Server Won't Start

- Check port not already in use: !`lsof -i :3000`
- Verify dependencies installed
- Check for TypeScript errors

### ngrok Issues

- Ensure ngrok installed and authenticated
- Check firewall settings
- Try different port if 3000 blocked

### claude.ai Connection Failed

- Verify URL includes `/mcp` endpoint
- Check CORS settings in server
- Ensure server is running

### Authentication Errors

- Verify contract address configured
- Check chain ID matches (1223953)
- Ensure RPC URL accessible

## Generate Deployment Summary

Create a summary including:

1. Server URL for claude.ai
2. Available tools and their token requirements
3. Test commands to verify functionality
4. Any warnings or issues detected
