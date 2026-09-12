# Token-Gated MCP Server Claude Code Configuration 🔐

A comprehensive Claude Code configuration for building token-gated MCP servers using FastMCP and the Radius MCP SDK. Enable decentralized, token-based access control for your AI tools with just 3 lines of code.

## ✨ Features

This configuration provides comprehensive support for:

- **Token-Gated Access** - ERC-1155 token-based authorization
- **FastMCP Integration** - Rapid MCP server development  
- **Radius MCP SDK** - Cryptographic proof verification
- **Web3 Authentication** - EIP-712 signature validation
- **Multi-Tier Pricing** - Different token requirements per tool
- **Complete Development Environment** - Agents, commands, hooks, and settings

## 📦 Installation

1. Copy the complete configuration to your token-gated MCP server project:

```bash
# Copy the entire configuration
cp -r token-gated-mcp-server/.claude your-mcp-project/
cp token-gated-mcp-server/CLAUDE.md your-mcp-project/

# Make hook scripts executable
chmod +x your-mcp-project/.claude/hooks/*.sh
```

2. The configuration will be automatically loaded when you start Claude Code.

## 📁 Configuration Structure

```text
.claude/
├── settings.json           # Main configuration with permissions, env vars, hooks
├── agents/                 # Specialized AI subagents
│   ├── radius-sdk-expert.md      # Radius MCP SDK implementation expert
│   ├── fastmcp-builder.md        # FastMCP server development specialist
│   ├── auth-flow-debugger.md     # Authentication debugging expert
│   ├── token-economics-designer.md # Token tier design specialist
│   └── web3-security-auditor.md  # Web3 security expert
├── commands/               # Custom slash commands
│   ├── setup-token-gate.md       # Set up complete token-gated server
│   ├── test-auth.md              # Test authentication flow
│   ├── create-tool.md            # Create new token-gated tool
│   ├── debug-proof.md            # Debug proof verification
│   ├── deploy-local.md           # Deploy locally with ngrok
│   └── validate-config.md        # Validate configuration
└── hooks/                  # Automation scripts
    ├── validate-token-config.sh  # Validate token configuration
    ├── format-typescript.sh      # Auto-format TypeScript files
    ├── log-mcp-commands.sh       # Log MCP commands for debugging
    └── production-safety.sh      # Production safety checks

## 🤖 Specialized Agents (5 Expert Agents)

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `radius-sdk-expert` | Radius MCP SDK implementation expert | Token protection, proof verification, multi-token patterns |
| `fastmcp-builder` | FastMCP server development specialist | Server setup, tool/resource/prompt creation, transport configuration |
| `auth-flow-debugger` | Authentication flow debugging expert | EVMAUTH errors, proof validation, token verification |
| `token-economics-designer` | Token economics and tier design specialist | Pricing models, access tiers, token distribution |
| `web3-security-auditor` | Web3 security expert | Smart contract safety, cryptographic operations, security audits |

## 🛠️ Commands (6 Powerful Commands)

| Command | Description | Usage |
|---------|-------------|-------|
| `/setup-token-gate` | Set up complete token-gated MCP server | `/setup-token-gate [basic\|full\|testnet]` |
| `/test-auth` | Test authentication flow end-to-end | `/test-auth [tool-name] [token-id]` |
| `/create-tool` | Create new token-gated tool | `/create-tool <tool-name> <token-id> [tier]` |
| `/debug-proof` | Debug proof verification issues | `/debug-proof` |
| `/deploy-local` | Deploy locally with ngrok | `/deploy-local` |
| `/validate-config` | Validate token-gating configuration | `/validate-config` |

## 🪝 Automation Hooks

### Pre-Tool Use Hooks
- **Token Configuration Validator** (`validate-token-config.sh`)
  - Validates contract address format (0x + 40 hex)
  - Checks for hardcoded private keys
  - Warns about debug mode in production
  - Verifies __evmauth parameter inclusion

- **MCP Command Logger** (`log-mcp-commands.sh`)
  - Logs FastMCP and ngrok commands
  - Tracks token configuration checks
  - Blocks dangerous commands (rm -rf, npm publish in dev)
  - Provides helpful tips for development

### Post-Tool Use Hooks
- **TypeScript Formatter** (`format-typescript.sh`)
  - Auto-formats with Prettier
  - Validates token protection implementation
  - Checks for proper error handling
  - Counts protected tools in server files

### Stop Hooks
- **Production Safety Check** (`production-safety.sh`)
  - Environment-specific warnings
  - Debug mode detection
  - Uncommitted changes reminder
  - Token configuration summary

## ⚙️ Configuration Details

### Security Permissions

The configuration includes comprehensive permissions for safe development:

**Allowed Operations:**
- All standard file operations (Read, Write, Edit, MultiEdit)
- Search and navigation tools (Grep, Glob, LS)
- Development commands (npm run dev/build/test/lint/typecheck)
- Package management (npm install, npm ci)
- FastMCP and ngrok for testing
- Git operations for version control
- Docker commands for containerization
- RPC endpoint testing

**Denied Operations:**
- Reading/writing private keys or secrets
- Destructive commands (rm -rf)
- Publishing to npm in development
- Modifying production environment files
- Unsafe curl operations (POST, PUT, DELETE)

### Environment Variables

Pre-configured for token-gated development:

- `EVMAUTH_CONTRACT_ADDRESS` - ERC-1155 contract (0x5448Dc20ad9e0cDb5Dd0db25e814545d1aa08D96)
- `EVMAUTH_CHAIN_ID` - Radius Testnet (1223953)
- `EVMAUTH_RPC_URL` - Blockchain RPC endpoint (https://rpc.testnet.radiustech.xyz)
- `EVMAUTH_TOKEN_ID` - Required token ID (default: 1)
- `NODE_ENV` - Environment mode (development/production)
- `DEBUG` - Debug mode (false by default, never enable in production!)
- `RADIUS_TESTNET` - Testnet indicator (true)

### Status Line

A custom status line displays real-time token-gating information:
```text

🔐 Token-Gated MCP | Chain: 1223953 | Token: 1 | dev

```

## 🚀 Usage Examples

### Building a Token-Gated MCP Server

```bash
# 1. Set up the project
> /setup full

# 2. Create a token-gated tool
> /create-tool premium_analytics 101

# 3. Test authentication flow
> /test-auth

# 4. Deploy locally with ngrok
> /deploy-local

# 5. Connect in claude.ai
# Use the ngrok URL + /mcp endpoint
```

### The 3-Line Integration

```typescript
// That's all you need!
const radius = new RadiusMcpSdk({ 
  contractAddress: '0x5448Dc20ad9e0cDb5Dd0db25e814545d1aa08D96' 
});

server.addTool({
  name: 'premium_tool',
  handler: radius.protect(101, yourHandler)  // Token-gated!
});
```

### Testing Authentication Flow

```bash
# Debug authentication issues
> /debug-proof

# The debugger will:
# - Validate proof structure
# - Check signature verification
# - Test token ownership
# - Identify configuration issues
```

## 📊 Technology Stack

Optimized for:

- **TypeScript** & Node.js
- **FastMCP v3.0+** for MCP servers
- **Radius MCP SDK** for token-gating
- **Viem** for Ethereum interactions
- **Zod** for schema validation
- **EIP-712** for cryptographic signatures
- **Radius Network Testnet** (Chain ID: 1223953)

## 🎯 Key Features

### Token-Based Access Control

- ERC-1155 multi-token support
- ANY token logic (user needs one of many)
- Tiered access patterns
- Dynamic token requirements

### Authentication Flow

- Cryptographic proof verification
- EIP-712 signature validation
- 30-second proof expiry
- Replay attack prevention

### Developer Experience

- 3-line integration
- AI-friendly error messages
- Automatic retry guidance
- Built-in caching

### Production Ready

- Docker containerization
- Health check endpoints
- Structured logging
- Performance monitoring

## 🔧 Customization

Edit `.claude/settings.json` to customize:

- Token contract addresses
- Chain ID for different networks
- Token tier configurations
- Cache settings
- Debug options

## 📝 Best Practices

This configuration enforces:

1. **Security First** - Cryptographic verification, fail-closed design
2. **Simple Integration** - Minimal code for maximum protection
3. **AI-Friendly Errors** - Clear guidance for authentication
4. **Performance** - Caching, batch checks, optimization
5. **Testing** - Comprehensive auth flow validation
6. **Production Ready** - Monitoring, health checks, logging

## 🐛 Troubleshooting

### Common Issues

**EVMAUTH_PROOF_MISSING errors:**

```bash
# Check Radius MCP Server connection
# Ensure __evmauth parameter is included
# Verify proof hasn't expired (30 seconds)
```

**Token verification failures:**

```bash
# Check contract address configuration
echo $EVMAUTH_CONTRACT_ADDRESS

# Verify chain ID
echo $EVMAUTH_CHAIN_ID

# Test RPC connection
curl $EVMAUTH_RPC_URL
```

**Debug authentication flow:**

```bash
/debug-proof
```

## 🌟 Example Projects

### Simple Token-Gated Timestamp

```typescript
server.addTool({
  name: 'get_timestamp',
  description: `Get current time (requires token ${TOKEN_ID})`,
  parameters: z.object({
    format: z.enum(['unix', 'iso', 'readable'])
  }),
  handler: radius.protect(TOKEN_ID, async (args) => {
    return new Date().toISOString();
  })
});
```

### Multi-Tier Analytics

```typescript
const TOKENS = {
  BASIC: 101,
  PREMIUM: 102,
  ENTERPRISE: [201, 202, 203]
};

// Different tools for different tiers
server.addTool({
  name: 'basic_analytics',
  handler: radius.protect(TOKENS.BASIC, basicHandler)
});

server.addTool({
  name: 'enterprise_analytics',
  handler: radius.protect(TOKENS.ENTERPRISE, enterpriseHandler)
});
```

## 🔗 Integration with Radius MCP Server

This SDK works with the **Radius MCP Server** for complete token-gating:

1. **Radius MCP Server** (one per AI client)
   - OAuth authentication
   - Wallet management via Privy
   - Proof generation
   - Token purchases

2. **Your MCP Server** (using this config)
   - Proof verification
   - Token ownership checks
   - Tool execution
   - Error guidance

## 📚 Resources

- [FastMCP Documentation](https://github.com/punkpeye/fastmcp)
- [Radius MCP SDK](https://github.com/radiustechsystems/mcp-sdk)
- [Model Context Protocol](https://modelcontextprotocol.io)
- [Radius Network Testnet](https://docs.radiustech.xyz)
- [EIP-712 Specification](https://eips.ethereum.org/EIPS/eip-712)

## 🎉 Quick Start Example

```bash
# 1. Install dependencies
npm install fastmcp @radiustechsystems/mcp-sdk zod

# 2. Create server.ts
cat > server.ts << 'EOF'
import { FastMCP } from 'fastmcp';
import { RadiusMcpSdk } from '@radiustechsystems/mcp-sdk';
import { z } from 'zod';

const radius = new RadiusMcpSdk({
  contractAddress: '0x5448Dc20ad9e0cDb5Dd0db25e814545d1aa08D96'
});

const server = new FastMCP({ name: 'My Token Server' });

server.addTool({
  name: 'premium_tool',
  description: 'Premium feature (token required)',
  parameters: z.object({ input: z.string() }),
  handler: radius.protect(1, async (args) => {
    return `Premium result for: ${args.input}`;
  })
});

server.start({ 
  transportType: 'httpStream',
  httpStream: { port: 3000 }
});
EOF

# 3. Run the server
npx tsx server.ts

# 4. Test with ngrok
ngrok http 3000

# 5. Connect in claude.ai with the ngrok URL + /mcp
```

## 🎯 What Makes This Configuration Special

### Complete Development Environment

- **5 Expert Agents** - Specialized AI assistants for every aspect of token-gating
- **6 Power Commands** - From setup to deployment, all automated
- **4 Smart Hooks** - Automatic validation, formatting, and safety checks
- **Comprehensive Settings** - Pre-configured for Radius Testnet with security best practices

### Key Capabilities

1. **3-Line Integration** - Token-gate any tool with minimal code
2. **AI-Friendly Errors** - Guide Claude through authentication automatically
3. **Production Ready** - Built-in safety checks and deployment tools
4. **Security First** - Automatic detection of private keys and unsafe patterns
5. **Developer Experience** - Auto-formatting, logging, and debugging tools

### Perfect For

- Building token-gated MCP servers with FastMCP
- Implementing ERC-1155 token access control
- Creating tiered access models for AI tools
- Deploying to Radius Network (testnet and mainnet)
- Learning Web3 authentication patterns

---

**Built for the decentralized AI tool marketplace** 🚀

*Enable token-gated access to your MCP tools with minimal code and maximum security.*

**Configuration Version:** 1.0.0 | **Compatible with:** FastMCP 3.0+, Radius MCP SDK 1.0+
