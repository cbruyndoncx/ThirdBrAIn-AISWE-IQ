# Simple MCP Server Claude Code Configuration 🚀

A clean, focused Claude Code configuration for building standard MCP (Model Context Protocol) servers. Perfect for developers who want to create MCP servers without the complexity of specialized features like databases or authentication.

## ✨ Features

This configuration provides comprehensive support for:

- **MCP Protocol Implementation** - Complete server setup with tools, resources, and prompts
- **Type-Safe Development** - TypeScript with Zod validation
- **Multiple Transport Options** - stdio, HTTP+SSE, WebSocket
- **Testing & Debugging** - Integration with MCP Inspector
- **Production Ready** - Docker support, logging, error handling

## 📦 Installation

1. Copy the configuration to your MCP server project:

```bash
cp -r simple-mcp-server/.claude your-mcp-project/
cp simple-mcp-server/CLAUDE.md your-mcp-project/

# Make hook scripts executable
chmod +x your-mcp-project/.claude/hooks/*.sh
```

2. The configuration will be automatically loaded when you start Claude Code.

## 🤖 Specialized Agents (6 total)

### Core MCP Development

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `mcp-architect` | MCP server architecture expert | Server structure, capability design, protocol patterns |
| `tool-builder` | Tool implementation specialist | Creating tools, parameter schemas, response formats |
| `resource-manager` | Resource system expert | URI schemes, content types, dynamic resources |

### Development & Operations

| Agent | Description | Use Cases |
|-------|-------------|-----------|
| `error-handler` | Error handling and debugging | Error codes, validation, troubleshooting |
| `test-writer` | Testing strategy expert | Unit tests, integration tests, MCP Inspector |
| `deployment-expert` | Deployment and packaging | Docker, npm publishing, Claude integration |

## 🛠️ Commands (7 total)

### Setup & Initialization

```bash
/init basic         # Basic MCP server with one tool
/init standard      # Standard server with tools and resources
/init full          # Complete server with all capabilities
```

### Development Workflow

```bash
/add-tool           # Add a new tool to the server
/add-resource       # Add a new resource endpoint
/add-prompt         # Add a new prompt template
```

### Testing & Deployment

```bash
/test              # Run tests and validate protocol compliance
/debug             # Debug server issues with detailed logging
/build             # Build and prepare for deployment
/deploy            # Deploy to npm or Docker registry
```

## 🪝 Automation Hooks

### Development Hook (`dev-watch.sh`)

Automatically triggered on TypeScript file changes:

- ✅ Type checking with `tsc --noEmit`
- 🎨 Prettier formatting
- 🔍 ESLint linting
- 🧪 Test execution for changed files
- 📝 Update tool/resource counts

### Build Hook (`pre-build.sh`)

Runs before building:

- 🔍 Lint check
- ✅ Type validation
- 🧪 Test suite execution
- 📦 Dependency audit
- 🏷️ Version validation

### Test Hook (`test-runner.sh`)

Enhances test execution:

- 🧪 Run appropriate test suite
- 📊 Coverage reporting
- 🔍 MCP protocol validation
- 📝 Test results summary

## ⚙️ Configuration Details

### Security Permissions

```json
{
  "permissions": {
    "allow": [
      "Read", "Write", "Edit", "MultiEdit",
      "Grep", "Glob", "LS",
      "Bash(npm run:*)",
      "Bash(npx @modelcontextprotocol/inspector)",
      "Bash(node dist/*.js)",
      "Bash(tsx src/*.ts)"
    ],
    "deny": [
      "Bash(rm -rf)",
      "Bash(sudo:*)",
      "Read(**/*secret*)",
      "Write(**/*secret*)"
    ]
  }
}
```

### Environment Variables

Pre-configured for MCP development:

- `NODE_ENV` - Environment mode
- `LOG_LEVEL` - Logging verbosity
- `MCP_SERVER_NAME` - Server identifier
- `MCP_SERVER_VERSION` - Server version
- `DEBUG` - Debug mode flag

## 🚀 Usage Examples

### Creating a Basic MCP Server

```bash
# 1. Initialize the project
> /init standard

# 2. Add a custom tool
> /add-tool calculate "Performs calculations"

# 3. Add a resource
> /add-resource config "Server configuration"

# 4. Test the implementation
> /test

# 5. Build for production
> /build
```

### Quick Server Setup

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';

const server = new Server({
  name: 'my-server',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
    resources: {},
  },
});

// Add your tools
server.addTool({
  name: 'hello',
  description: 'Say hello',
  inputSchema: {
    type: 'object',
    properties: {
      name: { type: 'string' },
    },
  },
  handler: async (args) => ({
    content: [{
      type: 'text',
      text: `Hello, ${args.name}!`,
    }],
  }),
});

// Connect transport
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Testing with MCP Inspector

```bash
# Launch the MCP Inspector
> npx @modelcontextprotocol/inspector

# The inspector will:
# - Connect to your server
# - Display available tools/resources
# - Allow interactive testing
# - Show protocol messages
```

## 📊 Technology Stack

Optimized for:

- **TypeScript** - Type-safe development
- **Node.js** - JavaScript runtime
- **@modelcontextprotocol/sdk** - Official MCP SDK
- **Zod** - Runtime validation
- **Vitest** - Fast unit testing
- **Docker** - Containerization

## 🎯 Key Features

### MCP Protocol Support

- Tools, Resources, and Prompts
- Multiple transport options
- Progress notifications
- Error handling with proper codes

### Developer Experience

- Type-safe with TypeScript
- Automatic validation with Zod
- Hot reload in development
- Comprehensive testing

### Production Ready

- Docker containerization
- Structured logging
- Error monitoring
- Rate limiting support

## 🔧 Customization

Edit `.claude/settings.json` to customize:

- Tool and resource definitions
- Environment variables
- Hook configurations
- Permission settings

## 📝 Best Practices

This configuration enforces:

1. **Protocol Compliance** - Strict MCP specification adherence
2. **Type Safety** - Full TypeScript with runtime validation
3. **Error Handling** - Proper error codes and messages
4. **Testing** - Comprehensive test coverage
5. **Documentation** - Clear code comments and API docs
6. **Security** - Input validation and sanitization

## 🐛 Troubleshooting

### Common Issues

**Server not starting:**

```bash
# Check TypeScript compilation
npm run typecheck

# Check for missing dependencies
npm install

# Verify Node.js version
node --version  # Should be >= 18
```

**Tools not appearing:**

```bash
# Validate tool registration
/debug

# Check MCP Inspector
npx @modelcontextprotocol/inspector
```

**Transport issues:**

```bash
# Test with stdio transport first
node dist/index.js

# For HTTP transport, check port
lsof -i :3000
```

## 🌟 Example Projects

### Weather Tool Server

```typescript
server.addTool({
  name: 'get_weather',
  description: 'Get weather for a location',
  inputSchema: {
    type: 'object',
    properties: {
      location: { type: 'string' },
    },
    required: ['location'],
  },
  handler: async ({ location }) => {
    const weather = await fetchWeather(location);
    return {
      content: [{
        type: 'text',
        text: `Weather in ${location}: ${weather}`,
      }],
    };
  },
});
```

### File System Resource Server

```typescript
server.addResource({
  uri: 'file:///{path}',
  name: 'File System',
  handler: async ({ path }) => {
    const content = await fs.readFile(path, 'utf-8');
    return {
      contents: [{
        uri: `file:///${path}`,
        mimeType: 'text/plain',
        text: content,
      }],
    };
  },
});
```

## 📚 Resources

- [MCP Specification](https://spec.modelcontextprotocol.io)
- [MCP SDK Documentation](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [Example MCP Servers](https://github.com/modelcontextprotocol/servers)
- [Claude Code MCP Guide](https://docs.anthropic.com/claude-code/mcp)

## 🎉 Quick Start

```bash
# 1. Create a new MCP server project
mkdir my-mcp-server && cd my-mcp-server
npm init -y

# 2. Install dependencies
npm install @modelcontextprotocol/sdk zod
npm install -D typescript tsx @types/node vitest

# 3. Copy this configuration
cp -r path/to/simple-mcp-server/.claude .
cp path/to/simple-mcp-server/CLAUDE.md .

# 4. Initialize TypeScript
npx tsc --init

# 5. Create your server
touch src/index.ts

# 6. Start development
npm run dev
```

## 🎯 What Makes This Configuration Special

### Focused on Fundamentals

- **No complexity** - Just pure MCP server development
- **No dependencies** - No databases, no authentication, no external services
- **Clean architecture** - Clear separation of concerns
- **Best practices** - Industry-standard patterns and conventions

### Perfect For

- Building your first MCP server
- Creating utility servers for Claude Code
- Learning MCP protocol implementation
- Prototyping new MCP capabilities
- Building production-ready MCP servers

---

**Built for clean, simple MCP server development** 🚀

*Create robust MCP servers with best practices and minimal complexity.*

**Configuration Version:** 1.0.0 | **Compatible with:** @modelcontextprotocol/sdk >=1.0.0
