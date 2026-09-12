# Simple MCP Server Development Assistant

You are an expert in building clean, well-structured MCP (Model Context Protocol) servers following best practices. You have deep expertise in the MCP SDK, TypeScript, and creating robust server implementations.

## Memory Integration

This CLAUDE.md follows official Claude Code patterns for MCP server development:

- **MCP protocol compliance** - Follows @modelcontextprotocol/sdk standards
- **Project memory** - Instructions shared with development team
- **Tool integration** - Works with Claude Code's MCP commands
- **Automated discovery** - Available when MCP server is configured

## MCP Configuration

To use this server with Claude Code:

```bash
# Add local MCP server
claude mcp add my-server -- node dist/index.js

# Add with npm/npx
claude mcp add my-server -- npx my-mcp-server

# Add with custom arguments
claude mcp add my-server -- node dist/index.js --port 3000

# Check server status
claude mcp list

# Remove server
claude mcp remove my-server
```

## Available MCP Tools

When connected, your server can provide these capabilities to Claude Code:

- **Tools** - Custom functions that Claude can invoke
- **Resources** - Data sources Claude can read
- **Prompts** - Reusable prompt templates
- **Sampling** - Custom completion behavior

## Project Context

This is a Simple MCP Server project focused on:

- **Clean architecture** with separation of concerns
- **Type safety** using TypeScript and Zod validation
- **Robust error handling** with proper error codes
- **Extensible design** for easy feature addition
- **MCP protocol compliance** using @modelcontextprotocol/sdk

## Technology Stack

### Core Technologies

- **TypeScript** - Type-safe development
- **Node.js** - Runtime environment
- **@modelcontextprotocol/sdk** - Official MCP implementation
- **Zod** - Runtime type validation

### Transport Options

- **stdio** - Standard input/output (default)
- **HTTP + SSE** - Server-sent events for web clients
- **WebSocket** - Bidirectional communication

## Architecture Patterns

### Basic MCP Server Structure

```typescript
import { Server } from '@modelcontextprotocol/sdk/server/index.js';
import { StdioServerTransport } from '@modelcontextprotocol/sdk/server/stdio.js';
import { CallToolRequestSchema, ListToolsRequestSchema } from '@modelcontextprotocol/sdk/types.js';
import { z } from 'zod';

// Create server instance
const server = new Server({
  name: 'my-mcp-server',
  version: '1.0.0',
}, {
  capabilities: {
    tools: {},
    resources: {},
    prompts: {},
  },
});

// Define tools
server.setRequestHandler(ListToolsRequestSchema, async () => {
  return {
    tools: [
      {
        name: 'example_tool',
        description: 'An example tool that processes input',
        inputSchema: {
          type: 'object',
          properties: {
            input: { type: 'string', description: 'Input to process' },
          },
          required: ['input'],
        },
      },
    ],
  };
});

// Handle tool calls
server.setRequestHandler(CallToolRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;

  switch (name) {
    case 'example_tool':
      const validated = z.object({
        input: z.string(),
      }).parse(args);
      
      return {
        content: [
          {
            type: 'text',
            text: `Processed: ${validated.input}`,
          },
        ],
      };
      
    default:
      throw new Error(`Unknown tool: ${name}`);
  }
});

// Start server
const transport = new StdioServerTransport();
await server.connect(transport);
```

### Resource Implementation

```typescript
import { ListResourcesRequestSchema, ReadResourceRequestSchema } from '@modelcontextprotocol/sdk/types.js';

// List available resources
server.setRequestHandler(ListResourcesRequestSchema, async () => {
  return {
    resources: [
      {
        uri: 'config://settings',
        name: 'Application Settings',
        description: 'Current configuration values',
        mimeType: 'application/json',
      },
    ],
  };
});

// Read resource content
server.setRequestHandler(ReadResourceRequestSchema, async (request) => {
  const { uri } = request.params;
  
  if (uri === 'config://settings') {
    return {
      contents: [
        {
          uri: 'config://settings',
          mimeType: 'application/json',
          text: JSON.stringify(getSettings(), null, 2),
        },
      ],
    };
  }
  
  throw new Error(`Unknown resource: ${uri}`);
});
```

### Prompt Templates

```typescript
import { ListPromptsRequestSchema, GetPromptRequestSchema } from '@modelcontextprotocol/sdk/types.js';

// List available prompts
server.setRequestHandler(ListPromptsRequestSchema, async () => {
  return {
    prompts: [
      {
        name: 'analyze_code',
        description: 'Analyze code for improvements',
        arguments: [
          {
            name: 'language',
            description: 'Programming language',
            required: true,
          },
        ],
      },
    ],
  };
});

// Get prompt content
server.setRequestHandler(GetPromptRequestSchema, async (request) => {
  const { name, arguments: args } = request.params;
  
  if (name === 'analyze_code') {
    return {
      messages: [
        {
          role: 'user',
          content: {
            type: 'text',
            text: `Analyze this ${args?.language || 'code'} for improvements...`,
          },
        },
      ],
    };
  }
  
  throw new Error(`Unknown prompt: ${name}`);
});
```

## Critical Implementation Details

### 1. Input Validation

```typescript
// Always validate inputs with Zod
const InputSchema = z.object({
  query: z.string().min(1).max(1000),
  options: z.object({
    format: z.enum(['json', 'text', 'markdown']).optional(),
    limit: z.number().int().min(1).max(100).optional(),
  }).optional(),
});

// Validate and handle errors
try {
  const validated = InputSchema.parse(args);
  return processQuery(validated);
} catch (error) {
  if (error instanceof z.ZodError) {
    return {
      error: {
        code: 'INVALID_PARAMS',
        message: 'Invalid parameters',
        data: error.errors,
      },
    };
  }
  throw error;
}
```

### 2. Error Handling

```typescript
// Comprehensive error handling
class MCPError extends Error {
  constructor(
    public code: string,
    message: string,
    public data?: unknown
  ) {
    super(message);
  }
}

// Use specific error codes
try {
  const result = await operation();
  return { content: [{ type: 'text', text: JSON.stringify(result) }] };
} catch (error) {
  if (error instanceof MCPError) {
    return {
      error: {
        code: error.code,
        message: error.message,
        data: error.data,
      },
    };
  }
  
  // Log unexpected errors
  console.error('Unexpected error:', error);
  return {
    error: {
      code: 'INTERNAL_ERROR',
      message: 'An unexpected error occurred',
    },
  };
}
```

### 3. Logging and Debugging

```typescript
// Structured logging
import pino from 'pino';

const logger = pino({
  level: process.env.LOG_LEVEL || 'info',
  transport: {
    target: 'pino-pretty',
    options: {
      colorize: true,
    },
  },
});

// Log server lifecycle
server.onerror = (error) => {
  logger.error({ error }, 'Server error');
};

// Log tool calls
logger.info({ tool: name, args }, 'Tool called');
```

### 4. Progress Notifications

```typescript
// Report progress for long-running operations
import { CreateMessageRequestSchema } from '@modelcontextprotocol/sdk/types.js';

async function longOperation(server: Server) {
  // Send progress updates
  await server.sendNotification({
    method: 'notifications/progress',
    params: {
      progress: 0.25,
      message: 'Processing step 1 of 4...',
    },
  });
  
  // Continue operation...
  
  await server.sendNotification({
    method: 'notifications/progress',
    params: {
      progress: 1.0,
      message: 'Operation complete!',
    },
  });
}
```

## Testing Strategy

### Unit Tests

```typescript
// Test tool handlers
describe('ToolHandlers', () => {
  it('should validate input parameters', async () => {
    const result = await handleTool('example_tool', { 
      input: 'test' 
    });
    expect(result.content[0].text).toContain('Processed');
  });
  
  it('should reject invalid parameters', async () => {
    const result = await handleTool('example_tool', {});
    expect(result.error?.code).toBe('INVALID_PARAMS');
  });
});
```

### Integration Tests

```typescript
// Test MCP protocol compliance
describe('MCP Server', () => {
  let server: Server;
  let transport: TestTransport;
  
  beforeEach(() => {
    transport = new TestTransport();
    server = createServer();
    server.connect(transport);
  });
  
  it('should handle initialize request', async () => {
    const response = await transport.request({
      method: 'initialize',
      params: {
        protocolVersion: '2024-11-05',
        capabilities: {},
        clientInfo: {
          name: 'test-client',
          version: '1.0.0',
        },
      },
    });
    
    expect(response.protocolVersion).toBe('2024-11-05');
    expect(response.capabilities).toBeDefined();
  });
});
```

## Deployment Configuration

### Package Scripts

```json
{
  "scripts": {
    "dev": "tsx watch src/index.ts",
    "build": "tsc",
    "start": "node dist/index.js",
    "test": "vitest",
    "lint": "eslint src",
    "typecheck": "tsc --noEmit",
    "format": "prettier --write src"
  }
}
```

### Docker Setup

```dockerfile
FROM node:20-alpine
WORKDIR /app
COPY package*.json ./
RUN npm ci --production
COPY dist ./dist
CMD ["node", "dist/index.js"]
```

### Environment Variables

```env
NODE_ENV=production
LOG_LEVEL=info
MCP_SERVER_NAME=my-mcp-server
MCP_SERVER_VERSION=1.0.0
```

## Performance Optimization

### Connection Management

```typescript
// Reuse connections and handle cleanup
class ConnectionManager {
  private connections = new Map();
  
  async getConnection(id: string) {
    if (!this.connections.has(id)) {
      this.connections.set(id, await createConnection());
    }
    return this.connections.get(id);
  }
  
  async cleanup() {
    for (const conn of this.connections.values()) {
      await conn.close();
    }
    this.connections.clear();
  }
}
```

### Response Caching

```typescript
// Cache frequently requested data
const cache = new Map();
const CACHE_TTL = 60000; // 1 minute

function getCached(key: string) {
  const cached = cache.get(key);
  if (cached && Date.now() - cached.timestamp < CACHE_TTL) {
    return cached.data;
  }
  return null;
}

function setCached(key: string, data: unknown) {
  cache.set(key, {
    data,
    timestamp: Date.now(),
  });
}
```

## Security Best Practices

### Input Sanitization

```typescript
// Sanitize user inputs
import { sanitize } from 'dompurify';

function sanitizeInput(input: string): string {
  // Remove potential script tags and dangerous content
  return sanitize(input, {
    ALLOWED_TAGS: [],
    ALLOWED_ATTR: [],
  });
}
```

### Rate Limiting

```typescript
// Implement rate limiting
const rateLimiter = new Map();
const MAX_REQUESTS = 100;
const TIME_WINDOW = 60000; // 1 minute

function checkRateLimit(clientId: string): boolean {
  const now = Date.now();
  const client = rateLimiter.get(clientId) || { count: 0, resetTime: now + TIME_WINDOW };
  
  if (now > client.resetTime) {
    client.count = 0;
    client.resetTime = now + TIME_WINDOW;
  }
  
  if (client.count >= MAX_REQUESTS) {
    return false;
  }
  
  client.count++;
  rateLimiter.set(clientId, client);
  return true;
}
```

## Common Commands

```bash
# Development
npm run dev           # Start development server with hot reload
npm run build         # Build for production
npm run test          # Run tests
npm run lint          # Lint code
npm run typecheck     # Type check without building

# Testing MCP
npx @modelcontextprotocol/inspector  # Interactive testing UI
npm run test:integration              # Run integration tests

# Production
npm start             # Start production server
npm run docker:build  # Build Docker image
npm run docker:run    # Run in container
```

## Resources

- [MCP Documentation](https://modelcontextprotocol.io)
- [MCP SDK Reference](https://github.com/modelcontextprotocol/typescript-sdk)
- [MCP Inspector](https://github.com/modelcontextprotocol/inspector)
- [MCP Examples](https://github.com/modelcontextprotocol/servers)

Remember: **Simplicity, Reliability, and Standards Compliance** are key to building great MCP servers!
