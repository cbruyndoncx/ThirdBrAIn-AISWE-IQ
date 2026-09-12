---
allowed-tools: "Write, Edit, Bash(npm install*), Bash(npm init*), Read"
description: Set up a complete token-gated MCP server with FastMCP and Radius SDK
argument-hint: "[basic|full|testnet]"
---

## Setup Token-Gated MCP Server

Create a complete token-gated MCP server project with the specified configuration level:

- **basic**: Minimal setup with one protected tool
- **full**: Complete setup with multiple tiers and examples
- **testnet**: Configured for Radius Testnet deployment

Configuration: $ARGUMENTS

## Tasks

1. **Initialize Project**
   - Create package.json with required dependencies
   - Set up TypeScript configuration
   - Create directory structure

2. **Install Dependencies**

   ```json
   {
     "dependencies": {
       "fastmcp": "^3.0.0",
       "@radiustechsystems/mcp-sdk": "^1.0.0",
       "zod": "^3.22.0",
       "viem": "^2.31.0"
     },
     "devDependencies": {
       "@types/node": "^20.0.0",
       "tsx": "^4.0.0",
       "typescript": "^5.0.0",
       "prettier": "^3.0.0"
     }
   }
   ```

3. **Create Server Implementation**
   - Main server file with token protection
   - Example tools with different token requirements
   - Proper error handling and responses

4. **Environment Configuration**
   - Create .env.example with required variables
   - Set up for Radius Testnet (Chain ID: 1223953)
   - Configure debug settings

5. **Create Helper Scripts**
   - Development script with hot reload
   - Build script for production
   - Test script for auth flow validation

6. **Documentation**
   - README with setup instructions
   - Token tier documentation
   - Testing guide with ngrok

## Implementation Structure

```text
project/
├── src/
│   ├── index.ts          # Main server file
│   ├── tools/            # Tool implementations
│   ├── config/           # Configuration
│   └── types/            # Type definitions
├── .env.example          # Environment template
├── package.json          # Dependencies
├── tsconfig.json         # TypeScript config
├── README.md             # Documentation
└── .claude/              # Claude Code config
    └── CLAUDE.md         # Project context
```

Based on the configuration level ($ARGUMENTS), create the appropriate setup with working examples and clear documentation.
